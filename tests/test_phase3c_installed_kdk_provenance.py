"""Historical AUTO/MANUAL KDK provenance in installed root-patch metadata."""

import plistlib
import tempfile
import types
import unittest

from pathlib import Path
from unittest import mock

from opencore_legacy_patcher.support.kdk_selection import (
    KDKSelectionMode,
    KernelDebugKitCandidate,
)
from opencore_legacy_patcher.sys_patch import sys_patch, sys_patch_helpers
from opencore_legacy_patcher.sys_patch.root_state import (
    KDK_IDENTITY_METADATA_KEY,
    KDK_SELECTION_MODE_METADATA_KEY,
    ROOT_PATCH_METADATA_FILENAME,
    ROOT_PATCH_METADATA_SCHEMA,
    RootPatchState,
    RootPatchStateEvaluator,
    RootStateEvidence,
)


SHA = "a" * 40
REPOSITORY = "https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta"
PROJECT = "OCLP 3.0.0 Nightly - amfipassbeta Edition v2.0"
CANDIDATE = KernelDebugKitCandidate("26.6.2", "25G82", "https://example/25G82.dmg", 82)


class InstalledKDKProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.payload = self.directory / "payload"
        self.payload.mkdir()
        self.kdk = self.directory / "KDK_26.6.2_25G82.kdk"
        version_directory = self.kdk / "System/Library/CoreServices"
        version_directory.mkdir(parents=True)
        with (version_directory / "SystemVersion.plist").open("wb") as version_file:
            plistlib.dump(
                {
                    "ProductVersion": CANDIDATE.version,
                    "ProductBuildVersion": CANDIDATE.build,
                },
                version_file,
            )
        self.constants = types.SimpleNamespace(
            payload_path=self.payload,
            payload_local_binaries_root_path=self.payload / "payload-root",
            project_identity=PROJECT,
            patcher_version="3.0.0",
            patcher_support_pkg_version="2.0.0-tahoe-restored.1",
            commit_info=(
                "refs/heads/experiment/amfipassbeta-v2.0",
                "2026-08-14T04:24:51+02:00",
                f"{REPOSITORY}/commit/{SHA}",
                SHA,
                REPOSITORY,
                PROJECT,
            ),
            detected_os=25,
            detected_os_minor=0,
            detected_os_build="25G82",
            root_patcher_revert_pending=False,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _write_operation_metadata(self, mode: KDKSelectionMode, file_name: str = "operation.plist") -> dict:
        result = sys_patch_helpers.SysPatchHelpers(self.constants).generate_patchset_plist(
            {"Modern Audio": {}, "Modern Wireless": {}},
            file_name,
            self.kdk,
            None,
            mode,
        )
        self.assertTrue(result)
        with (self.payload / file_name).open("rb") as metadata_file:
            return plistlib.load(metadata_file)

    def test_successful_manual_kdk_metadata_records_manual_and_exact_identity(self) -> None:
        metadata = self._write_operation_metadata(KDKSelectionMode.MANUAL)
        self.assertEqual(metadata[KDK_SELECTION_MODE_METADATA_KEY], "MANUAL")
        self.assertEqual(
            metadata[KDK_IDENTITY_METADATA_KEY],
            {
                "Version": CANDIDATE.version,
                "Build": CANDIDATE.build,
                "Path": str(self.kdk),
            },
        )

    def test_successful_auto_kdk_metadata_records_auto(self) -> None:
        metadata = self._write_operation_metadata(KDKSelectionMode.AUTO)
        self.assertEqual(metadata[KDK_SELECTION_MODE_METADATA_KEY], "AUTO")
        self.assertEqual(metadata[KDK_IDENTITY_METADATA_KEY]["Build"], CANDIDATE.build)

    def test_manual_choice_equal_to_automatic_choice_is_still_manual(self) -> None:
        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.constants = self.constants
        patcher.mount_location = str(self.directory / "mounted-root")
        patcher.kdk_path = self.kdk
        patcher.metallib_path = None
        patcher.manual_kdk_candidate = CANDIDATE
        helper = mock.Mock()
        helper.generate_patchset_plist.return_value = False
        with mock.patch.object(sys_patch.sys_patch_helpers, "SysPatchHelpers", return_value=helper):
            patcher._write_patchset({"Modern Audio": {}, "Modern Wireless": {}})
        self.assertEqual(helper.generate_patchset_plist.call_args.args[-1], KDKSelectionMode.MANUAL)

    def test_auto_operation_without_manual_candidate_is_recorded_auto(self) -> None:
        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.constants = self.constants
        patcher.mount_location = str(self.directory / "mounted-root")
        patcher.kdk_path = self.kdk
        patcher.metallib_path = None
        patcher.manual_kdk_candidate = None
        helper = mock.Mock()
        helper.generate_patchset_plist.return_value = False
        with mock.patch.object(sys_patch.sys_patch_helpers, "SysPatchHelpers", return_value=helper):
            patcher._write_patchset({"Modern Audio": {}})
        self.assertEqual(helper.generate_patchset_plist.call_args.args[-1], KDKSelectionMode.AUTO)

    def test_installed_evaluator_exposes_historical_mode_and_identity(self) -> None:
        metadata = self._write_operation_metadata(KDKSelectionMode.MANUAL)
        metadata_path = self.directory / ROOT_PATCH_METADATA_FILENAME
        with metadata_path.open("wb") as metadata_file:
            plistlib.dump(metadata, metadata_file)
        result = RootPatchStateEvaluator(
            self.constants,
            metadata_path=metadata_path,
            evidence_reader=lambda: RootStateEvidence(True, "Broken"),
        ).evaluate({"Modern Audio": {}, "Modern Wireless": {}})
        self.assertEqual(result.state, RootPatchState.INSTALLED_SAME)
        self.assertEqual(result.installed_kdk_selection_mode, KDKSelectionMode.MANUAL)
        self.assertEqual(result.installed_kdk_identity.version, CANDIDATE.version)
        self.assertEqual(result.installed_kdk_identity.build, CANDIDATE.build)
        self.assertEqual(result.installed_kdk_identity.path, str(self.kdk))

    def test_revert_pending_preserves_trustworthy_manual_history(self) -> None:
        metadata = self._write_operation_metadata(KDKSelectionMode.MANUAL)
        metadata_path = self.directory / ROOT_PATCH_METADATA_FILENAME
        with metadata_path.open("wb") as metadata_file:
            plistlib.dump(metadata, metadata_file)
        self.constants.root_patcher_revert_pending = True
        result = RootPatchStateEvaluator(
            self.constants,
            metadata_path=metadata_path,
            evidence_reader=lambda: RootStateEvidence(True, "Broken"),
        ).evaluate({"Modern Audio": {}, "Modern Wireless": {}})
        self.assertEqual(result.state, RootPatchState.REVERT_PENDING)
        self.assertEqual(result.installed_selection, ("Modern Audio", "Modern Wireless"))
        self.assertEqual(result.installed_kdk_selection_mode, KDKSelectionMode.MANUAL)

    def test_legacy_metadata_does_not_guess_kdk_mode(self) -> None:
        metadata = {
            "Metadata Schema": ROOT_PATCH_METADATA_SCHEMA,
            "Project Identity": PROJECT,
            "Repository": REPOSITORY,
            "Commit Ref": self.constants.commit_info[0],
            "Commit Date": self.constants.commit_info[1],
            "Commit SHA": SHA,
            "Commit URL": f"{REPOSITORY}/commit/{SHA}",
            "Installed Patches": ["Modern Audio", "Modern Wireless"],
            "Kernel Debug Kit Used": str(self.kdk),
        }
        metadata_path = self.directory / ROOT_PATCH_METADATA_FILENAME
        with metadata_path.open("wb") as metadata_file:
            plistlib.dump(metadata, metadata_file)
        result = RootPatchStateEvaluator(
            self.constants,
            metadata_path=metadata_path,
            evidence_reader=lambda: RootStateEvidence(True, "Broken"),
        ).evaluate({"Modern Audio": {}, "Modern Wireless": {}})
        self.assertEqual(result.state, RootPatchState.INSTALLED_SAME)
        self.assertIsNone(result.installed_kdk_selection_mode)
        self.assertIsNone(result.installed_kdk_identity)


if __name__ == "__main__":
    unittest.main()
