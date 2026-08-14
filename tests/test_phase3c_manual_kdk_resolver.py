"""Fail-closed manual KDK resolution and AUTO parity tests."""

import plistlib
import tempfile
import types
import unittest

from pathlib import Path
from unittest import mock

from opencore_legacy_patcher.support import kdk_handler
from opencore_legacy_patcher.support.kdk_selection import KernelDebugKitCandidate
from opencore_legacy_patcher.sys_patch import sys_patch
from opencore_legacy_patcher.sys_patch.patchsets import HardwarePatchsetSettings
from opencore_legacy_patcher.sys_patch.utilities import kdk_merge
from opencore_legacy_patcher.wx_gui import gui_kdk_selection, gui_sys_patch_start


CATALOG = [
    {"version": "26.6.2", "build": "25G82", "url": "https://example/25G82.dmg", "fileSize": 82},
    {"version": "26.6", "build": "25G72", "url": "https://example/25G72.dmg", "fileSize": 72},
    {"version": "26.5", "build": "25F90", "url": "https://example/25F90.dmg", "fileSize": 90},
]
EXACT = KernelDebugKitCandidate.from_catalog_entry(CATALOG[0])
OTHER = KernelDebugKitCandidate.from_catalog_entry(CATALOG[1])


def constants(download_path: Path | None = None):
    return types.SimpleNamespace(
        detected_os=25,
        detected_os_build="25G82",
        detected_os_version="26.6.2",
        kdk_download_path=download_path or Path("/private/tmp/KDK.dmg"),
    )


class Phase3CManualResolverTests(unittest.TestCase):
    def _resolver(self, *, build="25G82", version="26.6.2", selected=None, installed=None):
        with mock.patch.object(kdk_handler.KernelDebugKitObject, "_get_remote_kdks", return_value=CATALOG), \
             mock.patch.object(kdk_handler.KernelDebugKitObject, "_local_kdk_installed", return_value=installed):
            return kdk_handler.KernelDebugKitObject(
                constants(),
                build,
                version,
                selected_candidate=selected,
            )

    def test_auto_exact_and_closest_results_are_unchanged(self) -> None:
        exact = self._resolver()
        closest = self._resolver(build="25G99", version="26.6.3")
        self.assertEqual(exact.resolved_candidate(), EXACT)
        self.assertTrue(exact.kdk_url_is_exactly_match)
        self.assertEqual(closest.resolved_candidate(), EXACT)
        self.assertFalse(closest.kdk_url_is_exactly_match)

    def test_manual_choice_wins_over_automatic_exact_and_closest(self) -> None:
        manual = self._resolver(selected=OTHER)
        self.assertTrue(manual.success)
        self.assertEqual(manual.resolved_candidate(), OTHER)
        self.assertNotEqual(manual.resolved_candidate(), EXACT)

    def test_manual_candidate_missing_or_changed_fails_without_fallback(self) -> None:
        changed = KernelDebugKitCandidate(OTHER.version, OTHER.build, "https://changed/25G72.dmg", OTHER.file_size)
        resolver = self._resolver(selected=changed)
        self.assertFalse(resolver.success)
        self.assertIsNone(resolver.resolved_candidate())
        self.assertIn("No substitute", resolver.error_msg)

    def test_exact_installed_manual_candidate_is_reused(self) -> None:
        installed = "/Library/Developer/KDKs/KDK_26.6_25G72.kdk"
        resolver = self._resolver(selected=OTHER, installed=installed)
        self.assertTrue(resolver.kdk_already_installed)
        self.assertEqual(resolver.kdk_installed_path, installed)
        with mock.patch.object(kdk_handler.network_handler, "DownloadObject") as download:
            self.assertIsNone(resolver.retrieve_download())
        download.assert_not_called()

    def test_not_installed_manual_candidate_uses_exact_existing_download_object(self) -> None:
        resolver = self._resolver(selected=OTHER)
        with tempfile.TemporaryDirectory() as temporary:
            download_path = Path(temporary) / "KDK.dmg"
            resolver.constants.kdk_download_path = download_path
            with mock.patch.object(kdk_handler.network_handler, "DownloadObject") as download:
                resolver.retrieve_download()
            download.assert_called_once_with(OTHER.url, download_path)
            with (download_path.parent / kdk_handler.KDK_INFO_PLIST).open("rb") as info_file:
                info = plistlib.load(info_file)
            self.assertEqual(info, {"build": OTHER.build, "version": OTHER.version})

    def test_manual_dialog_contains_no_download_install_or_patch_progress_code(self) -> None:
        source = Path(gui_kdk_selection.__file__).read_text()
        for forbidden in ("DownloadFrame", "retrieve_download", "install_kdk", "KernelDebugKitMerge", "start_patch"):
            self.assertNotIn(forbidden, source)


class _Widget:
    def SetFont(self, *args): pass
    def Centre(self, *args): pass
    def SetLabel(self, *args): pass
    def SetValue(self, *args): pass
    def GetPosition(self): return (0, 0)
    def GetSize(self): return (100, 20)
    def Destroy(self): pass


class _Pulse:
    def start_pulse(self): pass
    def stop_pulse(self): pass


class _Frame:
    def SetSize(self, *args): pass
    def Show(self): pass
    def GetChildren(self): return ()


class Phase3CStandardDownloadGUIFlowTests(unittest.TestCase):
    def _run_download(self, download_object):
        candidate_resolver = mock.Mock()
        candidate_resolver.success = True
        candidate_resolver.kdk_url_build = OTHER.build
        candidate_resolver.retrieve_download.return_value = download_object
        candidate_resolver.validate_kdk_checksum.return_value = True
        start = types.SimpleNamespace(
            constants=types.SimpleNamespace(
                detected_os_build="25G82",
                detected_os_version="26.6.2",
            ),
            manual_kdk_candidate=OTHER,
            title="OCLP",
            kdk_obj=None,
        )
        with mock.patch.object(gui_sys_patch_start.kdk_handler, "KernelDebugKitObject", return_value=candidate_resolver) as resolver, \
             mock.patch.object(gui_sys_patch_start.wx, "StaticText", side_effect=lambda *a, **k: _Widget()), \
             mock.patch.object(gui_sys_patch_start.wx, "Gauge", side_effect=lambda *a, **k: _Widget()), \
             mock.patch.object(gui_sys_patch_start.gui_support, "font_factory"), \
             mock.patch.object(gui_sys_patch_start.gui_support, "GaugePulseCallback", return_value=_Pulse()), \
             mock.patch.object(gui_sys_patch_start.gui_support, "wait_for_thread", side_effect=lambda thread: thread.join()), \
             mock.patch.object(gui_sys_patch_start.gui_download, "DownloadFrame") as download_frame:
            result = gui_sys_patch_start.SysPatchStartFrame._kdk_download(start, _Frame())
        resolver.assert_called_once_with(
            start.constants,
            "25G82",
            "26.6.2",
            selected_candidate=OTHER,
        )
        return result, download_frame

    def test_installed_exact_candidate_skips_download_gui_and_continues(self) -> None:
        result, download_frame = self._run_download(None)
        self.assertTrue(result)
        download_frame.assert_not_called()

    def test_not_installed_exact_candidate_uses_standard_download_gui(self) -> None:
        download = types.SimpleNamespace(download_complete=True)
        result, download_frame = self._run_download(download)
        self.assertTrue(result)
        download_frame.assert_called_once()

    def test_manual_download_failure_does_not_invoke_an_automatic_substitute(self) -> None:
        download = types.SimpleNamespace(download_complete=False)
        result, download_frame = self._run_download(download)
        self.assertFalse(result)
        download_frame.assert_called_once()

    def test_manual_preflight_failure_occurs_before_payload_or_kdk_activity(self) -> None:
        start = types.SimpleNamespace(
            manual_kdk_candidate=OTHER,
            _revalidate_patch_selection=mock.Mock(return_value=types.SimpleNamespace()),
            _revalidate_manual_kdk=mock.Mock(return_value=False),
            _return_to_root_patch_selection=mock.Mock(),
        )
        with mock.patch.object(gui_sys_patch_start.gui_support, "PayloadMount") as payload, \
             mock.patch.object(gui_sys_patch_start.SysPatchStartFrame, "_kdk_download") as download:
            gui_sys_patch_start.SysPatchStartFrame.start_root_patching(start)
        payload.assert_not_called()
        download.assert_not_called()
        start._return_to_root_patch_selection.assert_called_once_with()


class Phase3CManualMergeTests(unittest.TestCase):
    def test_installed_manual_candidate_ignores_stale_download_and_reuses_exact_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            download = Path(temporary) / "stale.dmg"
            download.touch()
            constants_obj = constants(download)
            resolver = mock.Mock(
                success=True,
                kdk_already_installed=True,
                kdk_installed_path="/exact/25G72.kdk",
                kdk_url_build=OTHER.build,
            )
            merger = kdk_merge.KernelDebugKitMerge(constants_obj, "/mount", False, manual_kdk_candidate=OTHER)
            merger._kdk_object = mock.Mock(return_value=resolver)
            merger._matching_kdk_already_merged = mock.Mock(return_value=True)
            with mock.patch.object(kdk_handler.KernelDebugKitUtilities, "install_kdk_dmg") as install, \
                 mock.patch.object(kdk_merge.KernelDebugKitIdentity, "from_installed_path", return_value=mock.Mock(build=OTHER.build)):
                result = merger.merge()
            install.assert_not_called()
            self.assertEqual(result, Path("/exact/25G72.kdk"))

    def test_stale_download_identity_fails_before_install_without_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            download = Path(temporary) / "KDK.dmg"
            download.touch()
            with (download.parent / kdk_handler.KDK_INFO_PLIST).open("wb") as info_file:
                plistlib.dump({"build": EXACT.build, "version": EXACT.version}, info_file)
            merger = kdk_merge.KernelDebugKitMerge(constants(download), "/mount", False, manual_kdk_candidate=OTHER)
            merger._kdk_object = mock.Mock(return_value=mock.Mock(
                success=True,
                kdk_already_installed=False,
                kdk_url_build=OTHER.build,
            ))
            with mock.patch.object(kdk_handler.KernelDebugKitUtilities, "install_kdk_dmg") as install:
                with self.assertRaisesRegex(Exception, "does not match"):
                    merger.merge()
            install.assert_not_called()

    def test_selected_installed_kdk_disappearing_never_causes_silent_download_or_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            download = Path(temporary) / "missing.dmg"
            merger = kdk_merge.KernelDebugKitMerge(constants(download), "/mount", False, manual_kdk_candidate=OTHER)
            resolver = mock.Mock(success=True, kdk_already_installed=False, kdk_url_build=OTHER.build)
            merger._kdk_object = mock.Mock(return_value=resolver)
            with self.assertRaisesRegex(Exception, "no substitute or silent download"):
                merger.merge()
            resolver.retrieve_download.assert_not_called()

    def test_operation_layer_revalidates_manual_identity_before_support_mount(self) -> None:
        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.constants = constants()
        patcher.patch_selection = mock.Mock()
        patcher.patch_selection.is_empty.return_value = False
        patcher.expected_patch_selection = ("Modern Audio",)
        patcher.manual_kdk_candidate = OTHER
        detection = types.SimpleNamespace(
            patches={"Modern Audio": {}},
            can_patch=True,
            device_properties={HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED: True},
        )
        root_state = types.SimpleNamespace(patch_allowed=True)
        resolver = mock.Mock(success=False, resolved_candidate=mock.Mock(return_value=None))
        with mock.patch.object(sys_patch, "HardwarePatchsetDetection", return_value=detection), \
             mock.patch.object(sys_patch, "RootPatchStateEvaluator") as evaluator, \
             mock.patch.object(sys_patch.kdk_handler, "KernelDebugKitObject", return_value=resolver), \
             mock.patch.object(sys_patch, "PatcherSupportPkgMount") as support:
            evaluator.return_value.evaluate.return_value = root_state
            patcher.start_patch()
        support.assert_not_called()


if __name__ == "__main__":
    unittest.main()
