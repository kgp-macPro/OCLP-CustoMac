"""Operation-scoped Manual KDK Selection GUI and preview contracts."""

import types
import unittest

from pathlib import Path
from unittest import mock

from opencore_legacy_patcher.support import kdk_handler
from opencore_legacy_patcher.support.kdk_selection import (
    KDKCandidateStatus,
    KDKSelectionContext,
    KernelDebugKitCandidate,
    ManualKDKSelectionState,
)
from opencore_legacy_patcher.wx_gui import gui_kdk_selection
from opencore_legacy_patcher.wx_gui import gui_sys_patch_display
from opencore_legacy_patcher.sys_patch.patchsets import HardwarePatchsetSettings
from opencore_legacy_patcher.sys_patch.root_selection import RootPatchSelection
from opencore_legacy_patcher.sys_patch.root_state import RootPatchState


EXACT = KernelDebugKitCandidate("26.6.2", "25G82", "https://example/25G82.dmg", 82)
CLOSEST = KernelDebugKitCandidate("26.6", "25G72", "https://example/25G72.dmg", 72)


class Phase3CManualKDKGUIStateTests(unittest.TestCase):
    def _refresh_display(self, *, kdk_required: bool, manual_state=None, patch_allowed=True):
        checkbox = mock.Mock()
        display = types.SimpleNamespace(
            constants=types.SimpleNamespace(),
            selection=RootPatchSelection(frozenset(), frozenset()),
            selection_checkboxes={},
            selection_summary=mock.Mock(),
            selection_state_label=mock.Mock(),
            start_button=mock.Mock(),
            revert_button=mock.Mock(),
            manual_kdk_checkbox=checkbox,
            manual_kdk_state=manual_state or ManualKDKSelectionState(),
            _applicable_patchsets=lambda detection: detection.applicable_patchsets,
        )
        detection = types.SimpleNamespace(
            applicable_patchsets=(),
            patches={"Future KDK Patch": {}},
            device_properties={HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED: kdk_required},
            can_patch=True,
            can_unpatch=True,
        )
        root_state = types.SimpleNamespace(
            state=RootPatchState.CLEAN if patch_allowed else RootPatchState.INSTALLED_SAME,
            reason="Already installed",
            patch_allowed=patch_allowed,
            revert_allowed=lambda can_unpatch: not patch_allowed,
        )
        with mock.patch.object(gui_sys_patch_display, "HardwarePatchsetDetection", return_value=detection), \
             mock.patch.object(gui_sys_patch_display, "RootPatchStateEvaluator") as evaluator:
            evaluator.return_value.evaluate.return_value = root_state
            gui_sys_patch_display.SysPatchDisplayFrame._refresh_selection_state(display)
        return display, checkbox

    def test_manual_mode_defaults_off_and_requires_a_kdk(self) -> None:
        state = ManualKDKSelectionState()
        self.assertFalse(state.enabled)
        self.assertEqual(state, state.for_requirement(True))
        self.assertEqual(state, state.with_enabled(True, False))
        self.assertTrue(state.with_enabled(True, True).enabled)

    def test_requirement_loss_clears_mode_and_candidate_without_restoring_it(self) -> None:
        state = ManualKDKSelectionState().with_enabled(True, True).with_candidate(EXACT)
        self.assertEqual(state.candidate, EXACT)
        state = state.for_requirement(False)
        self.assertEqual(state, ManualKDKSelectionState())
        self.assertEqual(state.for_requirement(True), ManualKDKSelectionState())

    def test_gui_toggle_is_available_but_off_when_selected_patches_require_kdk(self) -> None:
        display, checkbox = self._refresh_display(kdk_required=True)
        checkbox.Enable.assert_called_once_with(True)
        checkbox.SetValue.assert_called_once_with(False)
        self.assertFalse(display.manual_kdk_state.enabled)

    def test_gui_disables_and_clears_manual_mode_when_requirement_disappears(self) -> None:
        selected = ManualKDKSelectionState(True, EXACT)
        display, checkbox = self._refresh_display(kdk_required=False, manual_state=selected)
        checkbox.Enable.assert_called_once_with(False)
        checkbox.SetValue.assert_called_once_with(False)
        self.assertEqual(display.manual_kdk_state, ManualKDKSelectionState())

    def test_manual_mode_does_not_bypass_installed_same_start_block(self) -> None:
        selected = ManualKDKSelectionState(True, EXACT)
        display, _ = self._refresh_display(kdk_required=True, manual_state=selected, patch_allowed=False)
        display.start_button.Enable.assert_called_once_with(False)

    def test_automatic_preview_uses_existing_resolver_and_has_no_package_side_effect(self) -> None:
        resolver = mock.Mock()
        resolver.success = True
        resolver.kdk_url_is_exactly_match = True
        resolver.available_candidates.return_value = (EXACT, CLOSEST)
        resolver.resolved_candidate.return_value = EXACT
        resolver.installed_path_for_build.side_effect = lambda build: Path("/Library/Developer/KDKs/KDK_26.6.2_25G82.kdk") if build == "25G82" else None
        constants = types.SimpleNamespace(detected_os_build="25G82", detected_os_version="26.6.2")

        with mock.patch.object(kdk_handler, "KernelDebugKitObject", return_value=resolver) as constructor, \
             mock.patch.object(resolver, "retrieve_download") as download, \
             mock.patch.object(kdk_handler.KernelDebugKitUtilities, "install_kdk_dmg") as install:
            context = KDKSelectionContext.from_system(constants)

        constructor.assert_called_once_with(constants, "25G82", "26.6.2", ignore_installed=True, passive=True)
        download.assert_not_called()
        install.assert_not_called()
        self.assertEqual(context.automatic_candidate, EXACT)
        self.assertTrue(context.automatic_exact_match)
        self.assertTrue(context.candidates[0].automatic_choice)
        self.assertTrue(context.candidates[0].installed)
        self.assertIn("Exact Match", gui_kdk_selection.automatic_choice_text(context))
        self.assertNotIn("Automatic Choice", gui_kdk_selection.automatic_choice_text(context))
        row = gui_kdk_selection.candidate_display_text(context.candidates[0])
        self.assertIn("Automatic Choice", row)
        self.assertNotIn("OCLP Automatic Choice", row)

    def test_closest_automatic_choice_is_displayed_from_existing_resolver(self) -> None:
        context = KDKSelectionContext(
            candidates=(KDKCandidateStatus(CLOSEST, None, True, False),),
            automatic_candidate=CLOSEST,
            automatic_exact_match=False,
        )
        preview = gui_kdk_selection.automatic_choice_text(context)
        self.assertIn("Closest Match", preview)
        self.assertIn("Not Installed", preview)

    def test_confirmation_closes_selection_dialog_and_returns_exact_candidate(self) -> None:
        context = KDKSelectionContext(
            candidates=(KDKCandidateStatus(EXACT, Path("/installed"), True, True),),
            automatic_candidate=EXACT,
            automatic_exact_match=True,
        )
        dialog = types.SimpleNamespace(
            candidate_list=mock.Mock(GetSelection=mock.Mock(return_value=0)),
            context=context,
            selected_candidate=None,
            EndModal=mock.Mock(),
        )
        confirmation = mock.Mock()
        confirmation.ShowModal.return_value = gui_kdk_selection.wx.ID_YES

        with mock.patch.object(gui_kdk_selection.wx, "MessageDialog", return_value=confirmation):
            gui_kdk_selection.ManualKDKSelectionDialog._on_confirm(dialog, mock.Mock())

        confirmation.ShowModal.assert_called_once_with()
        confirmation.SetYesNoLabels.assert_called_once_with("Use This KDK", "Cancel")
        self.assertEqual(dialog.selected_candidate, EXACT)
        dialog.EndModal.assert_called_once_with(gui_kdk_selection.wx.ID_OK)

    def test_confirmation_cancel_keeps_selector_open_and_starts_nothing(self) -> None:
        context = KDKSelectionContext(
            candidates=(KDKCandidateStatus(CLOSEST, None, False, False),),
            automatic_candidate=None,
            automatic_exact_match=False,
        )
        dialog = types.SimpleNamespace(
            candidate_list=mock.Mock(GetSelection=mock.Mock(return_value=0)),
            context=context,
            selected_candidate=None,
            EndModal=mock.Mock(),
        )
        confirmation = mock.Mock()
        confirmation.ShowModal.return_value = gui_kdk_selection.wx.ID_NO

        with mock.patch.object(gui_kdk_selection.wx, "MessageDialog", return_value=confirmation):
            gui_kdk_selection.ManualKDKSelectionDialog._on_confirm(dialog, mock.Mock())

        self.assertIsNone(dialog.selected_candidate)
        dialog.EndModal.assert_not_called()

    def test_user_can_choose_a_nonautomatic_candidate_and_manual_choice_wins(self) -> None:
        context = KDKSelectionContext(
            candidates=(
                KDKCandidateStatus(EXACT, Path("/installed"), True, True),
                KDKCandidateStatus(CLOSEST, None, False, False),
            ),
            automatic_candidate=EXACT,
            automatic_exact_match=True,
        )
        dialog = types.SimpleNamespace(
            candidate_list=mock.Mock(GetSelection=mock.Mock(return_value=1)),
            context=context,
            selected_candidate=None,
            EndModal=mock.Mock(),
        )
        confirmation = mock.Mock()
        confirmation.ShowModal.return_value = gui_kdk_selection.wx.ID_YES

        with mock.patch.object(gui_kdk_selection.wx, "MessageDialog", return_value=confirmation):
            gui_kdk_selection.ManualKDKSelectionDialog._on_confirm(dialog, mock.Mock())

        self.assertEqual(dialog.selected_candidate, CLOSEST)
        dialog.EndModal.assert_called_once_with(gui_kdk_selection.wx.ID_OK)

    def test_dialog_width_accommodates_the_normal_automatic_choice_row(self) -> None:
        longest_normal = KDKCandidateStatus(
            KernelDebugKitCandidate("26.6.2", "25G5065a", "https://example/25G5065a.dmg", 1),
            Path("/installed"),
            True,
            True,
        )
        row = gui_kdk_selection.candidate_display_text(longest_normal)
        self.assertEqual(gui_kdk_selection.KDK_SELECTION_DIALOG_SIZE, (610, 430))
        self.assertEqual(gui_kdk_selection.KDK_SELECTION_LIST_SIZE, (570, 210))
        self.assertIn("Exact Match · Installed · Automatic Choice", row)
        self.assertNotIn("OCLP Automatic Choice", row)


if __name__ == "__main__":
    unittest.main()
