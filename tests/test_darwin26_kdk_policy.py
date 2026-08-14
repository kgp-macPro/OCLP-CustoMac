"""Global Darwin 26 KDK rejection across root-patching resolution paths."""

import plistlib
import tempfile
import types
import unittest

from pathlib import Path
from unittest import mock

from opencore_legacy_patcher.support import kdk_handler
from opencore_legacy_patcher.support.kdk_selection import (
    KernelDebugKitCandidate,
    kdk_darwin_major,
    root_patch_kdk_build_allowed,
)
from opencore_legacy_patcher.sys_patch import sys_patch
from opencore_legacy_patcher.sys_patch.patchsets import HardwarePatchsetSettings
from opencore_legacy_patcher.sys_patch.utilities import kdk_merge


DARWIN_25 = {"version": "26.6.2", "build": "25G82", "url": "https://example/25G82.dmg", "fileSize": 82}
DARWIN_24 = {"version": "15.6", "build": "24G90", "url": "https://example/24G90.dmg", "fileSize": 90}
DARWIN_26 = {"version": "27.0", "build": "26A5368g", "url": "https://example/26A5368g.dmg", "fileSize": 101}
MISMATCHED_DARWIN_26 = {"version": "26.6.3", "build": "26Z99", "url": "https://example/26Z99.dmg", "fileSize": 99}


def constants(download_path: Path | None = None):
    return types.SimpleNamespace(
        detected_os=25,
        detected_os_build="25G99",
        detected_os_version="26.6.3",
        kdk_download_path=download_path or Path("/private/tmp/KDK.dmg"),
        patcher_version="3.0.0",
    )


class Darwin26KDKResolverPolicyTests(unittest.TestCase):
    def _resolver(self, catalog, *, build="25G99", version="26.6.3", selected=None):
        with mock.patch.object(kdk_handler.KernelDebugKitObject, "_get_remote_kdks", return_value=catalog), \
             mock.patch.object(kdk_handler.KernelDebugKitObject, "_local_kdk_installed", return_value=None):
            return kdk_handler.KernelDebugKitObject(constants(), build, version, selected_candidate=selected)

    def test_build_policy_blocks_only_darwin_26(self) -> None:
        self.assertEqual(kdk_darwin_major("26A5368g"), 26)
        self.assertFalse(root_patch_kdk_build_allowed("26A5368g"))
        self.assertFalse(root_patch_kdk_build_allowed("26A5406e"))
        self.assertTrue(root_patch_kdk_build_allowed("25G82"))
        self.assertTrue(root_patch_kdk_build_allowed("25G76"))
        self.assertTrue(root_patch_kdk_build_allowed("24G90"))

    def test_marketing_product_version_is_not_a_build_family(self) -> None:
        self.assertIsNone(kdk_darwin_major("26.6.2"))
        self.assertFalse(root_patch_kdk_build_allowed("26.6.2"))
        with self.assertRaisesRegex(Exception, "ProductBuildVersion could not be established"):
            kdk_merge.KernelDebugKitMerge._require_permitted_build("26.6.2")

    def test_automatic_and_available_catalog_selection_reject_darwin_26(self) -> None:
        resolver = self._resolver([DARWIN_26], build="26A101", version="27.0")
        self.assertFalse(resolver.success)
        self.assertIsNone(resolver.resolved_candidate())
        with mock.patch.object(resolver, "_get_remote_kdks", return_value=[DARWIN_26]):
            self.assertEqual(resolver.available_candidates(), ())

    def test_closest_match_skips_darwin_26_and_uses_permitted_fallback(self) -> None:
        resolver = self._resolver([MISMATCHED_DARWIN_26, DARWIN_25])
        self.assertTrue(resolver.success)
        self.assertEqual(resolver.kdk_url_build, "25G82")
        self.assertEqual(resolver.resolved_candidate(), KernelDebugKitCandidate.from_catalog_entry(DARWIN_25))

    def test_auto_26_6_2_selects_permitted_exact_25g82(self) -> None:
        resolver = self._resolver([DARWIN_26, DARWIN_25], build="25G82", version="26.6.2")
        self.assertTrue(resolver.success)
        self.assertTrue(resolver.kdk_url_is_exactly_match)
        self.assertEqual(resolver.kdk_url_build, "25G82")
        self.assertEqual(resolver.resolved_candidate(), KernelDebugKitCandidate.from_catalog_entry(DARWIN_25))

    def test_other_darwin_generation_auto_selection_is_preserved(self) -> None:
        resolver = self._resolver([DARWIN_24], build="24G90", version="15.6")
        self.assertTrue(resolver.success)
        self.assertEqual(resolver.resolved_candidate(), KernelDebugKitCandidate.from_catalog_entry(DARWIN_24))

    def test_manual_darwin_26_candidate_is_rejected_without_fallback(self) -> None:
        selected = KernelDebugKitCandidate.from_catalog_entry(DARWIN_26)
        resolver = self._resolver([DARWIN_25, DARWIN_26], selected=selected)
        self.assertFalse(resolver.success)
        self.assertIsNone(resolver.resolved_candidate())

    def test_download_resolver_cannot_return_a_darwin_26_download(self) -> None:
        resolver = kdk_handler.KernelDebugKitObject.__new__(kdk_handler.KernelDebugKitObject)
        resolver.constants = constants()
        resolver.kdk_already_installed = False
        resolver.kdk_url = DARWIN_26["url"]
        resolver.kdk_url_build = DARWIN_26["build"]
        resolver.kdk_url_version = DARWIN_26["version"]
        resolver.success = True
        resolver.error_msg = ""
        with mock.patch.object(kdk_handler.network_handler, "DownloadObject") as download:
            self.assertIsNone(resolver.retrieve_download())
        download.assert_not_called()
        self.assertFalse(resolver.success)
        self.assertIn("Darwin 26", resolver.error_msg)

    def test_locally_installed_darwin_26_kdk_is_not_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            kdk_path = root / "KDK_27.0_26A5368g.kdk"
            plist_path = kdk_path / "System/Library/CoreServices/SystemVersion.plist"
            plist_path.parent.mkdir(parents=True)
            with plist_path.open("wb") as plist_file:
                plistlib.dump({"ProductVersion": "27.0", "ProductBuildVersion": "26A5368g"}, plist_file)
            resolver = kdk_handler.KernelDebugKitObject.__new__(kdk_handler.KernelDebugKitObject)
            resolver.ignore_installed = False
            resolver.check_backups_only = False
            resolver.passive = True
            with mock.patch.object(kdk_handler, "KDK_INSTALL_PATH", str(root)):
                self.assertIsNone(resolver._local_kdk_installed(match="26A5368g"))
                self.assertIsNone(resolver.installed_path_for_build("26A5368g"))

    def test_operation_time_manual_revalidation_rejects_before_support_mount(self) -> None:
        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.constants = constants()
        patcher.patch_selection = mock.Mock(is_empty=mock.Mock(return_value=False))
        patcher.expected_patch_selection = ("Modern Audio",)
        patcher.manual_kdk_candidate = KernelDebugKitCandidate.from_catalog_entry(DARWIN_26)
        detection = types.SimpleNamespace(
            patches={"Modern Audio": {}},
            can_patch=True,
            device_properties={HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED: True},
        )
        root_state = types.SimpleNamespace(patch_allowed=True)
        with mock.patch.object(sys_patch, "HardwarePatchsetDetection", return_value=detection), \
             mock.patch.object(sys_patch, "RootPatchStateEvaluator") as evaluator, \
             mock.patch.object(kdk_handler.KernelDebugKitObject, "_get_remote_kdks", return_value=[DARWIN_25, DARWIN_26]), \
             mock.patch.object(kdk_handler.KernelDebugKitObject, "_local_kdk_installed", return_value=None), \
             mock.patch.object(sys_patch, "PatcherSupportPkgMount") as support:
            evaluator.return_value.evaluate.return_value = root_state
            patcher.start_patch()
        support.assert_not_called()


class Darwin26KDKMergePolicyTests(unittest.TestCase):
    def test_installed_25g82_with_empty_catalog_build_is_accepted(self) -> None:
        """Regression: installed AUTO resolution leaves kdk_url_build empty."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            installed = root / "KDK_26.6.2_25G82.kdk"
            version_plist = installed / "System/Library/CoreServices/SystemVersion.plist"
            version_plist.parent.mkdir(parents=True)
            with version_plist.open("wb") as plist_file:
                plistlib.dump({"ProductVersion": "26.6.2", "ProductBuildVersion": "25G82"}, plist_file)

            merger = kdk_merge.KernelDebugKitMerge(constants(root / "missing.dmg"), "/mount", False)
            resolver = mock.Mock(
                success=True,
                kdk_already_installed=True,
                kdk_installed_path=str(installed),
                kdk_url_build="",
            )
            merger._kdk_object = mock.Mock(return_value=resolver)
            merger._matching_kdk_already_merged = mock.Mock(return_value=True)
            self.assertEqual(merger.merge(), installed)

    def test_permitted_predownload_retains_existing_install_and_merge_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            download = root / "KDK.dmg"
            download.touch()
            with (root / kdk_handler.KDK_INFO_PLIST).open("wb") as info_file:
                plistlib.dump({"build": "25G82", "version": "26.6.2"}, info_file)
            installed = root / "KDK_26.6.2_25G82.kdk"
            version_plist = installed / "System/Library/CoreServices/SystemVersion.plist"
            version_plist.parent.mkdir(parents=True)
            with version_plist.open("wb") as plist_file:
                plistlib.dump({"ProductVersion": "26.6.2", "ProductBuildVersion": "25G82"}, plist_file)

            merger = kdk_merge.KernelDebugKitMerge(constants(download), "/mount", False)
            resolver = mock.Mock(
                success=True,
                kdk_already_installed=True,
                kdk_installed_path=str(installed),
                kdk_url_build="25G82",
            )
            merger._kdk_object = mock.Mock(return_value=resolver)
            merger._matching_kdk_already_merged = mock.Mock(return_value=True)
            with mock.patch.object(kdk_handler.KernelDebugKitUtilities, "install_kdk_dmg", return_value=True) as install:
                result = merger.merge()
            install.assert_called_once_with(download)
            self.assertEqual(result, installed)

    def test_predownloaded_darwin_26_kdk_is_rejected_before_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            download = Path(temporary) / "KDK.dmg"
            download.touch()
            with (download.parent / kdk_handler.KDK_INFO_PLIST).open("wb") as info_file:
                plistlib.dump({"build": "26A5406e", "version": "27.0"}, info_file)
            merger = kdk_merge.KernelDebugKitMerge(constants(download), "/mount", False)
            with mock.patch.object(kdk_handler.KernelDebugKitUtilities, "install_kdk_dmg") as install:
                with self.assertRaisesRegex(Exception, "Darwin 26"):
                    merger.merge()
            install.assert_not_called()

    def test_installed_kdk_identity_is_revalidated_before_merge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            kdk_path = Path(temporary) / "KDK_27.0_26A5368g.kdk"
            plist_path = kdk_path / "System/Library/CoreServices/SystemVersion.plist"
            plist_path.parent.mkdir(parents=True)
            with plist_path.open("wb") as plist_file:
                plistlib.dump({"ProductVersion": "27.0", "ProductBuildVersion": "26A5368g"}, plist_file)
            merger = kdk_merge.KernelDebugKitMerge(constants(), "/mount", False)
            resolver = mock.Mock(
                success=True,
                kdk_already_installed=True,
                kdk_installed_path=str(kdk_path),
                kdk_url_build="25G82",
            )
            merger._kdk_object = mock.Mock(return_value=resolver)
            merger._merge_kdk = mock.Mock()
            with self.assertRaisesRegex(Exception, "Darwin 26"):
                merger.merge()
            merger._merge_kdk.assert_not_called()


if __name__ == "__main__":
    unittest.main()
