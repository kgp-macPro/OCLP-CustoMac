"""Required root-patch state protection matrix."""

import plistlib
import tempfile
import types
import unittest

from pathlib import Path
from unittest import mock

from opencore_legacy_patcher.sys_patch.root_state import (
    ROOT_PATCH_METADATA_FILENAME,
    ROOT_PATCH_METADATA_SCHEMA,
    RootPatchState,
    RootPatchStateEvaluator,
    RootStateEvidence,
    read_root_state_evidence,
    semantic_patch_selection,
)


SHA = "a" * 40
OTHER_SHA = "b" * 40
REPOSITORY = "https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta"
PROJECT = "OCLP 3.0.0 Nightly - amfipassbeta Edition v2.0"
PATCHES = {"Modern Wireless": {}, "Modern Audio": {}}


class RootPatchStateProtectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.metadata_path = self.directory / ROOT_PATCH_METADATA_FILENAME
        self.constants = types.SimpleNamespace(
            project_identity=PROJECT,
            root_patcher_revert_pending=False,
            commit_info=(
                "refs/heads/experiment/amfipassbeta-v2.0",
                "2026-08-13T04:00:00+02:00",
                f"{REPOSITORY}/commit/{SHA}",
                SHA,
                REPOSITORY,
                PROJECT,
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
            "Project Identity": PROJECT,
            "OpenCore Legacy Patcher": "v3.0.0",
            "Commit Ref": self.constants.commit_info[0],
            "Commit Date": self.constants.commit_info[1],
            "Commit SHA": sha,
            "Commit URL": f"{REPOSITORY}/commit/{sha}",
            "Repository": REPOSITORY,
            "Installed Patches": list(patches),
        }

    def _write(self, data: dict, path: Path | None = None) -> None:
        with (path or self.metadata_path).open("wb") as metadata_file:
            plistlib.dump(data, metadata_file)

    def test_clean_enables_start_and_disables_revert(self) -> None:
        result = self._evaluator(RootStateEvidence(True, "Yes")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.CLEAN)
        self.assertTrue(result.patch_allowed)
        self.assertFalse(result.revert_allowed(True))

    def test_same_build_same_selection_blocks_start_and_allows_revert(self) -> None:
        self._write(self._metadata())
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INSTALLED_SAME)
        self.assertEqual(result.installed_selection, ("Modern Audio", "Modern Wireless"))
        self.assertFalse(result.patch_allowed)
        self.assertTrue(result.revert_allowed(True))
        self.assertFalse(result.revert_allowed(False))

    def test_same_build_different_selection_requires_revert(self) -> None:
        self._write(self._metadata(patches=("Modern Wireless",)))
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INSTALLED_DIFFERENT_PATCH_SET)
        self.assertFalse(result.patch_allowed)
        self.assertTrue(result.revert_applicable)

    def test_different_full_commit_same_selection_requires_revert(self) -> None:
        self._write(self._metadata(sha=OTHER_SHA))
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INSTALLED_DIFFERENT_BUILD)
        self.assertEqual(result.installed_selection, ("Modern Audio", "Modern Wireless"))
        self.assertFalse(result.patch_allowed)

    def test_same_human_version_different_commit_is_not_same(self) -> None:
        metadata = self._metadata(sha=OTHER_SHA)
        metadata["OpenCore Legacy Patcher"] = "v3.0.0"
        self._write(metadata)
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INSTALLED_DIFFERENT_BUILD)

    def test_legacy_metadata_never_classifies_same(self) -> None:
        self._write({
            "OpenCore Legacy Patcher": "v3.0.0",
            "Commit URL": "",
            "Modern Wireless": {},
            "Modern Audio": {},
        })
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.LEGACY_FOREIGN)
        self.assertIsNone(result.installed_selection)
        self.assertFalse(result.patch_allowed)
        self.assertTrue(result.revert_applicable)

    def test_foreign_fork_metadata_blocks(self) -> None:
        self._write({"OCLP-R": "v3.1.7"}, self.directory / "OCLP-R.plist")
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.LEGACY_FOREIGN)
        self.assertFalse(result.patch_allowed)

    def test_current_schema_from_foreign_repository_blocks_as_foreign(self) -> None:
        metadata = self._metadata()
        metadata["Project Identity"] = "Foreign Patcher"
        metadata["Repository"] = "https://github.com/example/foreign"
        metadata["Commit URL"] = f"https://github.com/example/foreign/commit/{SHA}"
        self._write(metadata)
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.LEGACY_FOREIGN)

    def test_malformed_metadata_fails_closed(self) -> None:
        self.metadata_path.write_bytes(b"not a plist")
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INVALID_UNKNOWN)
        self.assertFalse(result.patch_allowed)

    def test_missing_metadata_with_broken_root_blocks_patch_but_allows_common_revert(self) -> None:
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INVALID_UNKNOWN)
        self.assertFalse(result.patch_allowed)
        self.assertTrue(result.revert_applicable)

    def test_clean_root_without_metadata_is_patchable(self) -> None:
        result = self._evaluator(RootStateEvidence(True, "Yes")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.CLEAN)
        self.assertTrue(result.patch_allowed)

    def test_metadata_filename_case_mismatch_is_invalid_not_clean(self) -> None:
        wrong_case = self.directory / "opencore-legacy-patcher.plist"
        self._write(self._metadata(), wrong_case)
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INVALID_UNKNOWN)
        self.assertIn("capitalization", result.reason)

    def test_duplicate_case_candidates_are_ambiguous(self) -> None:
        entries = (
            types.SimpleNamespace(name=ROOT_PATCH_METADATA_FILENAME, is_file=lambda: True),
            types.SimpleNamespace(name="opencore-legacy-patcher.plist", is_file=lambda: True),
        )
        with mock.patch.object(Path, "iterdir", return_value=iter(entries)):
            result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.INVALID_UNKNOWN)
        self.assertIn("Ambiguous", result.reason)

    def test_display_same_then_click_different_is_blocked_after_revalidation(self) -> None:
        self._write(self._metadata())
        evaluator = self._evaluator(RootStateEvidence(True, "Broken"))
        self.assertEqual(evaluator.evaluate(PATCHES).state, RootPatchState.INSTALLED_SAME)
        self._write(self._metadata(sha=OTHER_SHA))
        clicked = evaluator.evaluate(PATCHES)
        self.assertEqual(clicked.state, RootPatchState.INSTALLED_DIFFERENT_BUILD)
        self.assertFalse(clicked.patch_allowed)

    def test_display_clean_then_click_installed_is_blocked_after_revalidation(self) -> None:
        evidence = RootStateEvidence(True, "Yes")
        evaluator = self._evaluator(evidence)
        self.assertTrue(evaluator.evaluate(PATCHES).patch_allowed)
        self._write(self._metadata())
        evaluator.evidence_reader = lambda: RootStateEvidence(True, "Broken")
        self.assertFalse(evaluator.evaluate(PATCHES).patch_allowed)

    def test_successful_revert_is_pending_until_reboot(self) -> None:
        self._write(self._metadata())
        self.constants.root_patcher_revert_pending = True
        result = self._evaluator(RootStateEvidence(True, "Broken")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.REVERT_PENDING)
        self.assertFalse(result.patch_allowed)
        self.assertFalse(result.revert_applicable)

    def test_simulated_reboot_into_clean_sealed_snapshot_is_clean(self) -> None:
        self.constants.root_patcher_revert_pending = False
        result = self._evaluator(RootStateEvidence(True, "Yes")).evaluate(PATCHES)
        self.assertEqual(result.state, RootPatchState.CLEAN)

    def test_patch_selection_comparison_ignores_dictionary_order(self) -> None:
        self.assertEqual(
            semantic_patch_selection({"Modern Audio": {}, "Modern Wireless": {}}),
            semantic_patch_selection({"Modern Wireless": {}, "Modern Audio": {}}),
        )

    def test_live_evidence_uses_existing_snapshot_seal_signal(self) -> None:
        root_result = types.SimpleNamespace(
            returncode=0,
            stdout=plistlib.dumps({"APFSSnapshot": True, "Sealed": "Broken"}),
        )
        with mock.patch(
            "opencore_legacy_patcher.sys_patch.root_state.subprocess.run",
            return_value=root_result,
        ):
            evidence = read_root_state_evidence()
        self.assertEqual(evidence, RootStateEvidence(True, "Broken"))

    def test_missing_active_root_seal_field_fails_closed(self) -> None:
        root_result = types.SimpleNamespace(
            returncode=0,
            stdout=plistlib.dumps({"APFSSnapshot": True}),
        )
        with mock.patch(
            "opencore_legacy_patcher.sys_patch.root_state.subprocess.run",
            return_value=root_result,
        ):
            self.assertIsNone(read_root_state_evidence())


if __name__ == "__main__":
    unittest.main()
