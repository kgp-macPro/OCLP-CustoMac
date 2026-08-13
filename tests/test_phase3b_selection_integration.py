"""Phase-3B selection/state/operation integration fixtures."""

import plistlib
import tempfile
import types
import unittest

from pathlib import Path
from unittest import mock

from opencore_legacy_patcher.sys_patch import sys_patch, sys_patch_helpers
from opencore_legacy_patcher.sys_patch.root_selection import (
    RootPatchSelection,
    SelectableRootPatch,
)
from opencore_legacy_patcher.sys_patch.root_state import (
    ROOT_PATCH_METADATA_SCHEMA,
    RootPatchState,
    RootPatchStateEvaluator,
    RootStateEvidence,
    semantic_patch_selection,
)


SHA = "c" * 40
OTHER_SHA = "d" * 40
REPOSITORY = "https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta"
PROJECT = "OCLP 3.0.0 Nightly - amfipassbeta Edition v2.0"
APPLICABLE = ("Networking: Modern Wireless", "Miscellaneous: Modern Audio")
PATCHES = {"Modern Wireless": {}, "Modern Audio": {}}


class Phase3BSelectionStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.metadata_path = self.directory / "OpenCore-Legacy-Patcher.plist"
        self.constants = types.SimpleNamespace(
            project_identity=PROJECT,
            root_patcher_revert_pending=False,
            commit_info=(
                "refs/heads/experiment/amfipassbeta-v2.0",
                "2026-08-13T19:00:00+02:00",
                f"{REPOSITORY}/commit/{SHA}",
                SHA,
                REPOSITORY,
                PROJECT,
            ),
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _metadata(self, patches: tuple[str, ...], sha: str = SHA) -> dict:
        return {
            "Metadata Schema": ROOT_PATCH_METADATA_SCHEMA,
            "Project Identity": PROJECT,
            "OpenCore Legacy Patcher": "v3.0.0",
            "Commit Ref": self.constants.commit_info[0],
            "Commit Date": self.constants.commit_info[1],
            "Commit SHA": sha,
            "Commit URL": f"{REPOSITORY}/commit/{sha}",
            "Repository": REPOSITORY,
            "Installed Patches": list(patches),
        }

    def _write(self, data: dict) -> None:
        with self.metadata_path.open("wb") as metadata_file:
            plistlib.dump(data, metadata_file)

    def _evaluator(self) -> RootPatchStateEvaluator:
        return RootPatchStateEvaluator(
            self.constants,
            metadata_path=self.metadata_path,
            evidence_reader=lambda: RootStateEvidence(True, "Broken"),
        )

    def _initialize_from_installed(self) -> tuple[RootPatchSelection, RootPatchState]:
        bootstrap = self._evaluator().evaluate(PATCHES)
        selection = RootPatchSelection.initialize(APPLICABLE, bootstrap.installed_selection)
        state = self._evaluator().evaluate(selection.filter_patch_dictionary(PATCHES)).state
        return selection, state

    def test_installed_both_initializes_both_and_returns_same(self) -> None:
        self._write(self._metadata(("Modern Audio", "Modern Wireless")))
        selection, state = self._initialize_from_installed()
        self.assertEqual(selection.selected, selection.applicable)
        self.assertEqual(state, RootPatchState.INSTALLED_SAME)

    def test_installed_wifi_only_initializes_wifi_only_and_returns_same(self) -> None:
        self._write(self._metadata(("Modern Wireless",)))
        selection, state = self._initialize_from_installed()
        self.assertTrue(selection.is_selected(SelectableRootPatch.MODERN_WIFI))
        self.assertFalse(selection.is_selected(SelectableRootPatch.MODERN_AUDIO))
        self.assertEqual(state, RootPatchState.INSTALLED_SAME)

    def test_installed_audio_only_initializes_audio_only_and_returns_same(self) -> None:
        self._write(self._metadata(("Modern Audio",)))
        selection, state = self._initialize_from_installed()
        self.assertFalse(selection.is_selected(SelectableRootPatch.MODERN_WIFI))
        self.assertTrue(selection.is_selected(SelectableRootPatch.MODERN_AUDIO))
        self.assertEqual(state, RootPatchState.INSTALLED_SAME)

    def test_installed_both_disabling_audio_requires_revert(self) -> None:
        self._write(self._metadata(("Modern Audio", "Modern Wireless")))
        selection, _ = self._initialize_from_installed()
        selection = selection.with_selection(SelectableRootPatch.MODERN_AUDIO, False)
        result = self._evaluator().evaluate(selection.filter_patch_dictionary(PATCHES))
        self.assertEqual(result.state, RootPatchState.INSTALLED_DIFFERENT_PATCH_SET)
        self.assertTrue(result.revert_applicable)

    def test_installed_both_disabling_wifi_requires_revert(self) -> None:
        self._write(self._metadata(("Modern Audio", "Modern Wireless")))
        selection, _ = self._initialize_from_installed()
        selection = selection.with_selection(SelectableRootPatch.MODERN_WIFI, False)
        result = self._evaluator().evaluate(selection.filter_patch_dictionary(PATCHES))
        self.assertEqual(result.state, RootPatchState.INSTALLED_DIFFERENT_PATCH_SET)

    def test_installed_wifi_only_enabling_audio_requires_revert(self) -> None:
        self._write(self._metadata(("Modern Wireless",)))
        selection, _ = self._initialize_from_installed()
        selection = selection.with_selection(SelectableRootPatch.MODERN_AUDIO, True)
        result = self._evaluator().evaluate(selection.filter_patch_dictionary(PATCHES))
        self.assertEqual(result.state, RootPatchState.INSTALLED_DIFFERENT_PATCH_SET)

    def test_changing_away_then_back_returns_to_same(self) -> None:
        self._write(self._metadata(("Modern Audio", "Modern Wireless")))
        selection, _ = self._initialize_from_installed()
        selection = selection.with_selection(SelectableRootPatch.MODERN_AUDIO, False)
        selection = selection.with_selection(SelectableRootPatch.MODERN_AUDIO, True)
        result = self._evaluator().evaluate(selection.filter_patch_dictionary(PATCHES))
        self.assertEqual(result.state, RootPatchState.INSTALLED_SAME)

    def test_different_build_cannot_be_bypassed_by_selection(self) -> None:
        self._write(self._metadata(("Modern Wireless",), sha=OTHER_SHA))
        selection, state = self._initialize_from_installed()
        self.assertTrue(selection.is_selected(SelectableRootPatch.MODERN_WIFI))
        self.assertEqual(state, RootPatchState.INSTALLED_DIFFERENT_BUILD)

    def test_legacy_state_cannot_be_bypassed_by_selection(self) -> None:
        self._write({"OpenCore Legacy Patcher": "v3.0.0", "Modern Wireless": {}})
        bootstrap = self._evaluator().evaluate(PATCHES)
        selection = RootPatchSelection.initialize(APPLICABLE, bootstrap.installed_selection)
        result = self._evaluator().evaluate(selection.filter_patch_dictionary(PATCHES))
        self.assertEqual(result.state, RootPatchState.LEGACY_FOREIGN)
        self.assertFalse(result.patch_allowed)

    def test_invalid_state_cannot_be_bypassed_by_selection(self) -> None:
        self.metadata_path.write_bytes(b"invalid")
        selection = RootPatchSelection.initialize(APPLICABLE)
        selection = selection.with_selection(SelectableRootPatch.MODERN_AUDIO, False)
        result = self._evaluator().evaluate(selection.filter_patch_dictionary(PATCHES))
        self.assertEqual(result.state, RootPatchState.INVALID_UNKNOWN)

    def test_revert_pending_cannot_be_bypassed_by_selection(self) -> None:
        self.constants.root_patcher_revert_pending = True
        selection = RootPatchSelection.initialize(APPLICABLE)
        result = self._evaluator().evaluate(selection.filter_patch_dictionary(PATCHES))
        self.assertEqual(result.state, RootPatchState.REVERT_PENDING)
        self.assertFalse(result.patch_allowed)


class Phase3BOperationTests(unittest.TestCase):
    def test_operation_refuses_changed_selection_before_mounting(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE)
        patcher = object.__new__(sys_patch.PatchSysVolume)
        patcher.constants = types.SimpleNamespace(detected_os=25)
        patcher.patch_selection = selection
        patcher.expected_patch_selection = ("Modern Wireless",)
        patcher.patch_set_dictionary = {}
        changed_detection = types.SimpleNamespace(
            patches={"Modern Audio": {}},
            device_properties={},
            can_patch=True,
        )
        with mock.patch.object(sys_patch, "HardwarePatchsetDetection", return_value=changed_detection), \
             mock.patch.object(sys_patch, "PatcherSupportPkgMount") as support_mount:
            patcher.start_patch()
        support_mount.assert_not_called()

    def test_successful_metadata_records_only_executed_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            payload_path = Path(temporary_directory)
            constants = types.SimpleNamespace(
                payload_path=payload_path,
                payload_local_binaries_root_path=payload_path / "payload-root",
                project_identity=PROJECT,
                patcher_version="3.0.0",
                patcher_support_pkg_version="2.0.0-tahoe-restored.1",
                commit_info=(
                    "refs/heads/experiment/amfipassbeta-v2.0",
                    "2026-08-13T19:00:00+02:00",
                    f"{REPOSITORY}/commit/{SHA}",
                    SHA,
                    REPOSITORY,
                    PROJECT,
                ),
                detected_os=25,
                detected_os_minor=0,
                detected_os_build="25A123",
            )
            file_name = "selection.plist"
            patchset = {"Modern Wireless": {}}
            self.assertTrue(
                sys_patch_helpers.SysPatchHelpers(constants).generate_patchset_plist(
                    patchset,
                    file_name,
                    None,
                    None,
                )
            )
            with (payload_path / file_name).open("rb") as metadata_file:
                metadata = plistlib.load(metadata_file)
            self.assertEqual(metadata["Installed Patches"], ["Modern Wireless"])
            self.assertNotIn("Modern Audio", metadata)

    def test_expected_selection_uses_semantic_patch_names(self) -> None:
        self.assertEqual(
            semantic_patch_selection({"Modern Wireless": {}, "Modern Audio": {}}),
            ("Modern Audio", "Modern Wireless"),
        )


if __name__ == "__main__":
    unittest.main()
