"""Synthetic tests for exact installed-state blocking and revalidation."""

import plistlib
import tempfile
import types
import unittest

from pathlib import Path
from unittest import mock

from opencore_legacy_patcher.sys_patch import sys_patch
from opencore_legacy_patcher.sys_patch.root_state import (
    ROOT_PATCH_METADATA_SCHEMA,
    RootPatchState,
    RootPatchStateEvaluator,
    RootPatchStateResult,
    RootStateEvidence,
)


SHA = "1" * 40
REPOSITORY = "https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta"
PATCHES = {"Modern Wireless": {}, "Modern Audio": {}}


class IdenticalStateBlockingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.metadata_path = Path(self.temporary_directory.name) / "OpenCore-Legacy-Patcher.plist"
        self.constants = types.SimpleNamespace(
            detected_os=25,
            project_identity="OCLP 3.0.0 Nightly - amfipassbeta Edition v2.0",
            commit_info=(
                "refs/heads/experiment/amfipassbeta-v2.0",
                "2026-08-13T03:00:00+02:00",
                f"{REPOSITORY}/commit/{SHA}",
                SHA,
                REPOSITORY,
                "OCLP 3.0.0 Nightly - amfipassbeta Edition v2.0",
            ),
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _evaluator(self, evidence: RootStateEvidence) -> RootPatchStateEvaluator:
        return RootPatchStateEvaluator(
            self.constants,
            metadata_path=self.metadata_path,
            evidence_reader=lambda: evidence,
        )

    def _metadata(self, *, sha: str = SHA, patches: tuple[str, ...] = tuple(sorted(PATCHES))) -> dict:
        return {
            "Metadata Schema": ROOT_PATCH_METADATA_SCHEMA,
            "Project Identity": self.constants.project_identity,
            "Commit Ref": self.constants.commit_info[0],
            "Commit Date": self.constants.commit_info[1],
            "Commit SHA": sha,
            "Commit URL": f"{REPOSITORY}/commit/{sha}",
            "Repository": REPOSITORY,
            "Installed Patches": list(patches),
            "OpenCore Legacy Patcher": "v3.0.0",
        }

    def _write(self, metadata: dict) -> None:
        with self.metadata_path.open("wb") as metadata_file:
            plistlib.dump(metadata, metadata_file)

    def test_clean_root_is_enabled(self) -> None:
        result = self._evaluator(RootStateEvidence(True, "Yes")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.CLEAN)
        self.assertTrue(result.patch_allowed)

    def test_exact_same_build_and_selection_is_disabled(self) -> None:
        self._write(self._metadata())
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INSTALLED_SAME)
        self.assertFalse(result.patch_allowed)

    def test_same_version_different_full_sha_is_not_same(self) -> None:
        self._write(self._metadata(sha="2" * 40))
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INSTALLED_DIFFERENT_BUILD)

    def test_same_sha_different_selection_is_not_same(self) -> None:
        self._write(self._metadata(patches=("Modern Wireless",)))
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INSTALLED_DIFFERENT_PATCH_SET)

    def test_malformed_metadata_is_not_same(self) -> None:
        self.metadata_path.write_bytes(b"not a plist")
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INVALID_UNKNOWN)

    def test_click_time_revalidation_observes_changed_state(self) -> None:
        evaluator = self._evaluator(RootStateEvidence(True, "Yes"))
        displayed = evaluator.evaluate(PATCHES)
        self.assertTrue(displayed.patch_allowed)
        self._write(self._metadata())
        evaluator.evidence_reader = lambda: RootStateEvidence(True, "Broken")
        clicked = evaluator.evaluate(PATCHES)
        self.assertFalse(clicked.patch_allowed)

    def test_operation_layer_refuses_a_blocked_state(self) -> None:
        patcher = object.__new__(sys_patch.PatchSysVolume)
        patcher.constants = self.constants
        patcher.patch_set_dictionary = {}
        detection = types.SimpleNamespace(patches=PATCHES, can_patch=True)
        blocked = RootPatchStateResult(RootPatchState.INSTALLED_SAME, False, True, "already installed")
        with mock.patch.object(sys_patch, "HardwarePatchsetDetection", return_value=detection), \
             mock.patch.object(sys_patch, "RootPatchStateEvaluator") as evaluator, \
             mock.patch.object(sys_patch, "PatcherSupportPkgMount") as support_mount:
            evaluator.return_value.evaluate.return_value = blocked
            patcher.start_patch()
            support_mount.assert_not_called()


if __name__ == "__main__":
    unittest.main()
