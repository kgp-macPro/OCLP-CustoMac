"""PATCH_PENDING_REBOOT lifecycle, restart reconstruction, and safe revert gating."""

import plistlib
import tempfile
import types
import unittest

from pathlib import Path
from unittest import mock

from opencore_legacy_patcher.support.kdk_selection import KDKSelectionMode
from opencore_legacy_patcher.sys_patch import sys_patch
from opencore_legacy_patcher.sys_patch.lifecycle import (
    LifecycleDiscovery,
    ROOT_PATCH_LIFECYCLE_FILENAME,
    RootPatchLifecycleState,
    RootPatchLifecycleStore,
)
from opencore_legacy_patcher.sys_patch.root_state import (
    KDK_IDENTITY_METADATA_KEY,
    KDK_SELECTION_MODE_METADATA_KEY,
    ROOT_PATCH_METADATA_FILENAME,
    ROOT_PATCH_METADATA_SCHEMA,
    RootPatchState,
    RootPatchStateEvaluator,
    RootStateEvidence,
)
from opencore_legacy_patcher.wx_gui import gui_sys_patch_start


SHA = "a" * 40
REPOSITORY = "https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta"
PROJECT = "OCLP 3.0.0 Nightly - amfipassbeta Edition v2.0"
PATCHES = {"Modern Audio": {}, "Modern Wireless": {}}


class PatchPendingRebootTests(unittest.TestCase):
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
        self.metadata = {
            "Metadata Schema": ROOT_PATCH_METADATA_SCHEMA,
            "Project Identity": PROJECT,
            "OpenCore Legacy Patcher": "v3.0.0",
            "Commit Ref": self.constants.commit_info[0],
            "Commit Date": self.constants.commit_info[1],
            "Commit SHA": SHA,
            "Commit URL": f"{REPOSITORY}/commit/{SHA}",
            "Repository": REPOSITORY,
            "Installed Patches": ["Modern Audio", "Modern Wireless"],
            KDK_SELECTION_MODE_METADATA_KEY: "MANUAL",
            KDK_IDENTITY_METADATA_KEY: {
                "Version": "26.6.2",
                "Build": "25G82",
                "Path": "/Library/Developer/KDKs/KDK_26.6.2_25G82.kdk",
            },
        }

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _writer(self, path: Path, payload: bytes) -> bool:
        path.write_bytes(payload)
        return True

    def _store(self, boot: str = "boot-a") -> RootPatchLifecycleStore:
        return RootPatchLifecycleStore(
            self.constants,
            path=self.lifecycle_path,
            boot_session_reader=lambda: boot,
            writer=self._writer,
        )

    def _evaluator(
        self,
        store: RootPatchLifecycleStore,
        evidence: RootStateEvidence = RootStateEvidence(True, "Yes"),
    ) -> RootPatchStateEvaluator:
        return RootPatchStateEvaluator(
            self.constants,
            metadata_path=self.metadata_path,
            evidence_reader=lambda: evidence,
            lifecycle_store=store,
        )

    def test_successful_patch_before_reboot_is_patch_pending(self) -> None:
        store = self._store()
        self.assertTrue(store.write(RootPatchLifecycleState.PATCH_PENDING_REBOOT, self.metadata))
        result = self._evaluator(store).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.PATCH_PENDING_REBOOT)
        self.assertFalse(result.patch_allowed)
        self.assertTrue(result.revert_allowed(True))
        self.assertEqual(result.installed_selection, ("Modern Audio", "Modern Wireless"))
        self.assertEqual(result.installed_kdk_selection_mode, KDKSelectionMode.MANUAL)
        self.assertEqual(result.installed_kdk_identity.build, "25G82")

    def test_patch_pending_revert_respects_existing_can_unpatch_gate(self) -> None:
        store = self._store()
        store.write(RootPatchLifecycleState.PATCH_PENDING_REBOOT, self.metadata)
        result = self._evaluator(store).evaluate(PATCHES)
        self.assertTrue(result.revert_allowed(True))
        self.assertFalse(result.revert_allowed(False))

    def test_automatic_kdk_patch_is_pending_with_safe_revert(self) -> None:
        metadata = dict(self.metadata)
        metadata[KDK_SELECTION_MODE_METADATA_KEY] = "AUTO"
        store = self._store()
        self.assertTrue(store.write(RootPatchLifecycleState.PATCH_PENDING_REBOOT, metadata))
        result = self._evaluator(store).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.PATCH_PENDING_REBOOT)
        self.assertEqual(result.installed_kdk_selection_mode, KDKSelectionMode.AUTO)
        self.assertFalse(result.patch_allowed)
        self.assertTrue(result.revert_allowed(True))

    def test_manual_kdk_patch_is_pending_with_safe_revert(self) -> None:
        store = self._store()
        self.assertTrue(store.write(RootPatchLifecycleState.PATCH_PENDING_REBOOT, self.metadata))
        result = self._evaluator(store).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.PATCH_PENDING_REBOOT)
        self.assertEqual(result.installed_kdk_selection_mode, KDKSelectionMode.MANUAL)
        self.assertFalse(result.patch_allowed)
        self.assertTrue(result.revert_allowed(True))

    def test_no_kdk_wifi_only_patch_is_pending_with_safe_revert(self) -> None:
        metadata = dict(self.metadata)
        metadata["Installed Patches"] = ["Modern Wireless"]
        metadata.pop(KDK_SELECTION_MODE_METADATA_KEY)
        metadata.pop(KDK_IDENTITY_METADATA_KEY)
        store = self._store()
        self.assertTrue(store.write(RootPatchLifecycleState.PATCH_PENDING_REBOOT, metadata))
        result = self._evaluator(store).evaluate({"Modern Wireless": {}})
        self.assertEqual(result.state, RootPatchState.PATCH_PENDING_REBOOT)
        self.assertIsNone(result.installed_kdk_selection_mode)
        self.assertIsNone(result.installed_kdk_identity)
        self.assertFalse(result.patch_allowed)
        self.assertTrue(result.revert_allowed(True))

    def test_cancelled_reboot_prompt_does_not_cancel_completed_patch_state(self) -> None:
        constants = types.SimpleNamespace(
            root_patcher_succeeded=True,
            root_patcher_patch_pending=True,
            needs_to_open_preferences=False,
        )
        frame = types.SimpleNamespace(constants=constants, frame_modal=mock.Mock())
        restart = mock.Mock()
        with mock.patch.object(gui_sys_patch_start.gui_support, "RestartHost", return_value=restart):
            gui_sys_patch_start.SysPatchStartFrame._post_patch(frame)
        restart.restart.assert_called_once()
        self.assertTrue(constants.root_patcher_patch_pending)

    def test_app_reopen_same_boot_reconstructs_pending_and_safe_revert(self) -> None:
        store = self._store()
        store.write(RootPatchLifecycleState.PATCH_PENDING_REBOOT, self.metadata)
        reopened_constants = types.SimpleNamespace(
            commit_info=self.constants.commit_info,
            root_patcher_patch_pending=False,
            root_patcher_revert_pending=False,
            root_patcher_pending_metadata=None,
        )
        reopened_store = RootPatchLifecycleStore(
            reopened_constants,
            path=self.lifecycle_path,
            boot_session_reader=lambda: "boot-a",
            writer=self._writer,
        )
        result = RootPatchStateEvaluator(
            reopened_constants,
            metadata_path=self.metadata_path,
            evidence_reader=lambda: RootStateEvidence(True, "Yes"),
            lifecycle_store=reopened_store,
        ).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.PATCH_PENDING_REBOOT)
        self.assertFalse(result.patch_allowed)
        self.assertTrue(result.revert_allowed(True))

    def test_normal_reboot_ignores_old_boot_record_and_classifies_installed_same(self) -> None:
        self._store().write(RootPatchLifecycleState.PATCH_PENDING_REBOOT, self.metadata)
        with self.metadata_path.open("wb") as metadata_file:
            plistlib.dump(self.metadata, metadata_file)
        new_boot_store = self._store("boot-b")
        self.assertEqual(new_boot_store.read().discovery, LifecycleDiscovery.STALE)
        result = self._evaluator(new_boot_store, RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INSTALLED_SAME)

    def test_patch_pending_revert_transitions_to_revert_pending(self) -> None:
        store = self._store()
        store.write(RootPatchLifecycleState.PATCH_PENDING_REBOOT, self.metadata)
        store.write(RootPatchLifecycleState.REVERT_PENDING, self.metadata)
        result = self._evaluator(store).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.REVERT_PENDING)
        self.assertFalse(result.patch_allowed)
        self.assertFalse(result.revert_applicable)
        self.assertEqual(result.installed_kdk_selection_mode, KDKSelectionMode.MANUAL)

    def test_reboot_after_revert_is_clean(self) -> None:
        self._store().write(RootPatchLifecycleState.REVERT_PENDING, self.metadata)
        result = self._evaluator(self._store("boot-b"), RootStateEvidence(True, "Yes")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.CLEAN)
        self.assertTrue(result.patch_allowed)

    def test_lifecycle_hash_corruption_never_becomes_clean(self) -> None:
        store = self._store()
        store.write(RootPatchLifecycleState.PATCH_PENDING_REBOOT, self.metadata)
        with self.lifecycle_path.open("rb") as lifecycle_file:
            data = plistlib.load(lifecycle_file)
        data["Installed Metadata"]["Installed Patches"] = ["Modern Wireless"]
        with self.lifecycle_path.open("wb") as lifecycle_file:
            plistlib.dump(data, lifecycle_file)
        result = self._evaluator(store).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INVALID_UNKNOWN)
        self.assertFalse(result.patch_allowed)

    def test_operation_layer_cannot_patch_from_patch_pending(self) -> None:
        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.constants = types.SimpleNamespace(detected_os=25)
        patcher.patch_selection = mock.Mock(is_empty=mock.Mock(return_value=False))
        patcher.expected_patch_selection = tuple(sorted(PATCHES))
        detection = types.SimpleNamespace(
            patches=PATCHES,
            can_patch=True,
            device_properties={},
        )
        pending = types.SimpleNamespace(patch_allowed=False, reason="Reboot required")
        with mock.patch.object(sys_patch, "HardwarePatchsetDetection", return_value=detection), \
             mock.patch.object(sys_patch, "RootPatchStateEvaluator") as evaluator, \
             mock.patch.object(sys_patch, "PatcherSupportPkgMount") as support:
            evaluator.return_value.evaluate.return_value = pending
            patcher.start_patch()
        support.assert_not_called()

    def test_success_recording_sets_session_state_and_persists_exact_metadata(self) -> None:
        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.constants = types.SimpleNamespace(
            root_patcher_patch_pending=False,
            root_patcher_revert_pending=False,
            root_patcher_pending_metadata=None,
        )
        patcher.installed_patch_metadata = self.metadata
        lifecycle_store = mock.Mock()
        lifecycle_store.write.return_value = True
        with mock.patch.object(sys_patch, "RootPatchLifecycleStore", return_value=lifecycle_store):
            patcher._record_patch_pending()
        self.assertTrue(patcher.constants.root_patcher_patch_pending)
        self.assertFalse(patcher.constants.root_patcher_revert_pending)
        self.assertEqual(patcher.constants.root_patcher_pending_metadata, self.metadata)
        lifecycle_store.write.assert_called_once_with(
            RootPatchLifecycleState.PATCH_PENDING_REBOOT,
            self.metadata,
        )

    def test_revert_recording_preserves_pending_metadata_and_changes_state(self) -> None:
        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.constants = types.SimpleNamespace(
            root_patcher_patch_pending=True,
            root_patcher_revert_pending=False,
            root_patcher_pending_metadata=self.metadata,
        )
        lifecycle_store = mock.Mock()
        lifecycle_store.write.return_value = True
        with mock.patch.object(sys_patch, "RootPatchLifecycleStore", return_value=lifecycle_store):
            patcher._record_revert_pending()
        self.assertFalse(patcher.constants.root_patcher_patch_pending)
        self.assertTrue(patcher.constants.root_patcher_revert_pending)
        lifecycle_store.write.assert_called_once_with(RootPatchLifecycleState.REVERT_PENDING, self.metadata)


if __name__ == "__main__":
    unittest.main()
