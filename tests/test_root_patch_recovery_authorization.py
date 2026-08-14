"""Root-state recovery authorization, SIP visibility, and OCLP-family evidence."""

import plistlib
import tempfile
import types
import unittest

from pathlib import Path
from unittest import mock

from opencore_legacy_patcher.sys_patch import sys_patch
from opencore_legacy_patcher.sys_patch.lifecycle import (
    ROOT_PATCH_LIFECYCLE_FILENAME,
    RootPatchLifecycleState,
    RootPatchLifecycleStore,
)
from opencore_legacy_patcher.sys_patch.root_selection import RootPatchSelection
from opencore_legacy_patcher.sys_patch.root_state import (
    ROOT_PATCH_METADATA_FILENAME,
    ROOT_PATCH_METADATA_SCHEMA,
    RootPatchState,
    RootPatchStateEvaluator,
    RootStateEvidence,
)
from opencore_legacy_patcher.wx_gui import gui_sys_patch_display, gui_sys_patch_start


SHA = "a" * 40
OTHER_SHA = "b" * 40
REPOSITORY = "https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta"
PROJECT = "OCLP 3.0.0 Nightly - amfipassbeta Edition v2.0"
PATCHES = {"Modern Wireless": {}, "Modern Audio": {}}


class RootPatchRecoveryAuthorizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.metadata_path = self.directory / ROOT_PATCH_METADATA_FILENAME
        self.lifecycle_path = self.directory / ROOT_PATCH_LIFECYCLE_FILENAME
        self.constants = types.SimpleNamespace(
            commit_info=(
                "refs/heads/experiment/amfipassbeta-v2.0",
                "2026-08-14T04:45:22+02:00",
                f"{REPOSITORY}/commit/{SHA}",
                SHA,
                REPOSITORY,
                PROJECT,
            ),
            root_patcher_patch_pending=False,
            root_patcher_revert_pending=False,
            root_patcher_pending_metadata=None,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _metadata(self, sha: str = SHA) -> dict:
        return {
            "Metadata Schema": ROOT_PATCH_METADATA_SCHEMA,
            "Project Identity": PROJECT,
            "OpenCore Legacy Patcher": "v3.0.0",
            "Commit Ref": self.constants.commit_info[0],
            "Commit Date": self.constants.commit_info[1],
            "Commit SHA": sha,
            "Commit URL": f"{REPOSITORY}/commit/{sha}",
            "Repository": REPOSITORY,
            "Installed Patches": sorted(PATCHES),
        }

    def _write(self, data: dict, path: Path | None = None) -> None:
        with (path or self.metadata_path).open("wb") as metadata_file:
            plistlib.dump(data, metadata_file)

    def _store(self, boot: str = "boot-a") -> RootPatchLifecycleStore:
        return RootPatchLifecycleStore(
            self.constants,
            path=self.lifecycle_path,
            boot_session_reader=lambda: boot,
            writer=lambda path, payload: (path.write_bytes(payload) or True),
        )

    def _evaluate(self, evidence: RootStateEvidence, requested: dict = PATCHES):
        return RootPatchStateEvaluator(
            self.constants,
            metadata_path=self.metadata_path,
            evidence_reader=lambda: evidence,
            lifecycle_store=self._store(),
        ).evaluate(requested)

    def test_clean_authorizes_patch_not_recovery_even_with_empty_selection(self) -> None:
        for requested in (PATCHES, {}):
            with self.subTest(requested=bool(requested)):
                result = self._evaluate(RootStateEvidence(True, "Yes"), requested)
                self.assertEqual(result.state, RootPatchState.CLEAN)
                self.assertTrue(result.patch_authorized)
                self.assertFalse(result.recovery_authorized)

    def test_installed_current_and_different_build_authorize_only_recovery(self) -> None:
        for sha, expected in (
            (SHA, RootPatchState.INSTALLED_SAME),
            (OTHER_SHA, RootPatchState.INSTALLED_DIFFERENT_BUILD),
        ):
            with self.subTest(state=expected):
                self._write(self._metadata(sha))
                result = self._evaluate(RootStateEvidence(True, "Broken"))
                self.assertEqual(result.state, expected)
                self.assertFalse(result.patch_authorized)
                self.assertTrue(result.recovery_authorized)

    def test_same_lineage_pending_lifecycle_accepts_another_full_sha_for_recovery(self) -> None:
        metadata = self._metadata(OTHER_SHA)
        self.assertTrue(self._store().write(RootPatchLifecycleState.PATCH_PENDING_REBOOT, metadata))
        result = self._evaluate(RootStateEvidence(True, "Yes"))
        self.assertEqual(result.state, RootPatchState.PATCH_PENDING_REBOOT)
        self.assertFalse(result.patch_authorized)
        self.assertTrue(result.recovery_authorized)

    def test_lowercase_oclp_mod_metadata_is_source_backed_recovery_evidence(self) -> None:
        self._write({"OCLP-Mod": "v3.1.9"}, self.directory / "oclp-mod.plist")
        result = self._evaluate(RootStateEvidence(True, "Broken"))
        self.assertEqual(result.state, RootPatchState.LEGACY_FOREIGN)
        self.assertFalse(result.patch_authorized)
        self.assertTrue(result.recovery_authorized)
        self.assertIn("oclp-mod.plist", result.reason)

    def test_existing_uppercase_oclp_mod_spelling_remains_recognized(self) -> None:
        self._write({"OCLP-Mod": "v3.1.9"}, self.directory / "OCLP-Mod.plist")
        result = self._evaluate(RootStateEvidence(True, "Broken"))
        self.assertEqual(result.state, RootPatchState.LEGACY_FOREIGN)
        self.assertTrue(result.recovery_authorized)

    def test_malformed_or_ambiguous_foreign_metadata_remains_fail_closed(self) -> None:
        malformed = self.directory / "oclp-mod.plist"
        malformed.write_bytes(b"not a plist")
        result = self._evaluate(RootStateEvidence(True, "Broken"))
        self.assertEqual(result.state, RootPatchState.INVALID_UNKNOWN)
        self.assertFalse(result.patch_authorized)
        self.assertFalse(result.recovery_authorized)

        malformed.unlink()
        self._write({"OCLP-Mod": "v3.1.9"}, self.directory / "oclp-mod.plist")
        self._write({"OCLP-Plus": "v3.2.2"}, self.directory / "OCLP-Plus.plist")
        ambiguous = self._evaluate(RootStateEvidence(True, "Broken"))
        self.assertEqual(ambiguous.state, RootPatchState.INVALID_UNKNOWN)
        self.assertFalse(ambiguous.recovery_authorized)

    def test_empty_canonical_metadata_is_not_treated_as_legacy_recovery_evidence(self) -> None:
        self._write({})
        result = self._evaluate(RootStateEvidence(True, "Broken"))
        self.assertEqual(result.state, RootPatchState.INVALID_UNKNOWN)
        self.assertFalse(result.patch_authorized)
        self.assertFalse(result.recovery_authorized)

    def test_pre_lifecycle_clean_root_with_foreign_metadata_is_not_guessed(self) -> None:
        self._write({"OCLP-Mod": "v3.1.9"}, self.directory / "oclp-mod.plist")
        result = self._evaluate(RootStateEvidence(True, "Yes"))
        self.assertEqual(result.state, RootPatchState.LEGACY_FOREIGN)
        self.assertFalse(result.patch_authorized)
        self.assertFalse(result.recovery_authorized)

    def test_sip_blocked_recovery_stays_visible_and_explains_prerequisite(self) -> None:
        self._write(self._metadata())
        root_state = self._evaluate(RootStateEvidence(True, "Broken"))
        display = types.SimpleNamespace(
            constants=types.SimpleNamespace(),
            selection=RootPatchSelection(frozenset(), frozenset()),
            selection_checkboxes={},
            selection_summary=mock.Mock(),
            selection_state_label=mock.Mock(),
            start_button=mock.Mock(),
            revert_button=mock.Mock(),
            manual_kdk_checkbox=None,
            manual_kdk_history_label=None,
            _applicable_patchsets=lambda detection: (),
        )
        detection = types.SimpleNamespace(
            applicable_patchsets=(),
            patches=PATCHES,
            device_properties={},
            can_patch=False,
            can_unpatch=False,
        )
        with mock.patch.object(gui_sys_patch_display, "HardwarePatchsetDetection", return_value=detection), \
             mock.patch.object(gui_sys_patch_display, "RootPatchStateEvaluator") as evaluator:
            evaluator.return_value.evaluate.return_value = root_state
            gui_sys_patch_display.SysPatchDisplayFrame._refresh_selection_state(display)
        display.start_button.Enable.assert_called_once_with(False)
        display.revert_button.Enable.assert_called_once_with(True)
        status = display.selection_state_label.SetLabel.call_args.args[0]
        self.assertIn("System Integrity Protection", status)
        self.assertIn("Revert Root Patches is required", status)

    def test_sip_blocked_click_and_operation_refuse_before_mount(self) -> None:
        root_state = types.SimpleNamespace(
            recovery_authorized=True,
            reason="Existing root patches require recovery",
        )
        display = types.SimpleNamespace(
            _refresh_selection_state=mock.Mock(),
            root_state=root_state,
            current_detection=types.SimpleNamespace(can_unpatch=False),
        )
        with mock.patch.object(gui_sys_patch_display.wx, "MessageBox") as message, \
             mock.patch.object(gui_sys_patch_start, "SysPatchStartFrame") as start_frame:
            gui_sys_patch_display.SysPatchDisplayFrame.on_revert_root_patching(display)
        start_frame.assert_not_called()
        self.assertIn("System Integrity Protection", message.call_args.args[0])

        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.constants = types.SimpleNamespace()
        patcher.patch_selection = None
        detection = types.SimpleNamespace(
            patches=PATCHES,
            can_unpatch=False,
            detailed_errors=mock.Mock(),
        )
        patcher._mount_root_vol = mock.Mock()
        with mock.patch.object(sys_patch, "HardwarePatchsetDetection", return_value=detection), \
             mock.patch.object(sys_patch, "RootPatchStateEvaluator") as evaluator:
            evaluator.return_value.evaluate.return_value = root_state
            patcher.start_unpatch()
        detection.detailed_errors.assert_called_once_with()
        patcher._mount_root_vol.assert_not_called()


if __name__ == "__main__":
    unittest.main()
