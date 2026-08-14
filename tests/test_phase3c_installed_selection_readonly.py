"""Installed/revert-required root-patch selections are evidence-backed read-only views."""

import types
import unittest

from unittest import mock

from opencore_legacy_patcher.support.kdk_selection import (
    KDKSelectionMode,
    KernelDebugKitCandidate,
    KernelDebugKitIdentity,
    ManualKDKSelectionState,
)
from opencore_legacy_patcher.sys_patch.patchsets import HardwarePatchsetSettings
from opencore_legacy_patcher.sys_patch.root_selection import (
    RootPatchSelection,
    SelectableRootPatch,
)
from opencore_legacy_patcher.sys_patch.root_state import RootPatchState
from opencore_legacy_patcher.wx_gui import gui_sys_patch_display


APPLICABLE = ("Networking: Modern Wireless", "Miscellaneous: Modern Audio")
CANDIDATE = KernelDebugKitCandidate("26.6.2", "25G82", "https://example/25G82.dmg", 82)
KDK_IDENTITY = KernelDebugKitIdentity("26.6.2", "25G82", "/Library/Developer/KDKs/KDK_26.6.2_25G82.kdk")


class InstalledSelectionReadOnlyTests(unittest.TestCase):
    def _state(self, state: RootPatchState, installed_selection=None, kdk_mode=None, kdk_identity=None):
        return types.SimpleNamespace(
            state=state,
            installed_selection=installed_selection,
            installed_kdk_selection_mode=kdk_mode,
            installed_kdk_identity=kdk_identity,
            reason=f"State: {state.value}",
            patch_allowed=state == RootPatchState.CLEAN,
            revert_allowed=lambda can_unpatch: state in {
                RootPatchState.INSTALLED_SAME,
                RootPatchState.INSTALLED_DIFFERENT_PATCH_SET,
                RootPatchState.INSTALLED_DIFFERENT_BUILD,
            } and can_unpatch,
        )

    def _display(self, selection=None, manual_state=None):
        wifi = mock.Mock()
        audio = mock.Mock()
        manual = mock.Mock()
        manual_history = mock.Mock()
        display = types.SimpleNamespace(
            constants=types.SimpleNamespace(),
            selection=selection or RootPatchSelection.initialize(APPLICABLE),
            selection_checkboxes={
                SelectableRootPatch.MODERN_WIFI: wifi,
                SelectableRootPatch.MODERN_AUDIO: audio,
            },
            selection_summary=mock.Mock(),
            selection_state_label=mock.Mock(),
            start_button=mock.Mock(),
            revert_button=mock.Mock(),
            manual_kdk_checkbox=manual,
            manual_kdk_history_label=manual_history,
            manual_kdk_state=manual_state or ManualKDKSelectionState(),
            _applicable_patchsets=lambda detection: detection.applicable_patchsets,
        )
        return display, wifi, audio, manual, manual_history

    def _refresh(self, root_state, *, selection=None, manual_state=None, kdk_required=True):
        display, wifi, audio, manual, manual_history = self._display(selection, manual_state)
        detection = types.SimpleNamespace(
            applicable_patchsets=APPLICABLE,
            patches={"Modern Wireless": {}, "Modern Audio": {}},
            device_properties={HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED: kdk_required},
            can_patch=True,
            can_unpatch=True,
        )
        with mock.patch.object(gui_sys_patch_display, "HardwarePatchsetDetection", return_value=detection), \
             mock.patch.object(gui_sys_patch_display, "RootPatchStateEvaluator") as evaluator:
            evaluator.return_value.evaluate.return_value = root_state
            gui_sys_patch_display.SysPatchDisplayFrame._refresh_selection_state(display)
        return display, wifi, audio, manual, manual_history

    def test_clean_controls_are_editable(self) -> None:
        _, wifi, audio, manual, manual_history = self._refresh(self._state(RootPatchState.CLEAN))
        wifi.Enable.assert_called_once_with(True)
        audio.Enable.assert_called_once_with(True)
        manual.Enable.assert_called_once_with(True)
        manual_history.SetLabel.assert_called_once_with("")
        manual_history.Show.assert_called_once_with(False)

    def test_installed_both_is_displayed_read_only(self) -> None:
        state = self._state(RootPatchState.INSTALLED_SAME, ("Modern Audio", "Modern Wireless"))
        display, wifi, audio, manual, _ = self._refresh(state)
        wifi.SetValue.assert_called_once_with(True)
        audio.SetValue.assert_called_once_with(True)
        wifi.Enable.assert_called_once_with(False)
        audio.Enable.assert_called_once_with(False)
        manual.Enable.assert_called_once_with(False)
        display.start_button.Enable.assert_called_once_with(False)
        display.revert_button.Enable.assert_called_once_with(True)
        display.selection_summary.SetLabel.assert_called_once_with("Installed: Modern Wi-Fi + Modern Audio")

    def test_installed_wifi_only_is_displayed_read_only(self) -> None:
        state = self._state(RootPatchState.INSTALLED_SAME, ("Modern Wireless",))
        _, wifi, audio, _, _ = self._refresh(state, kdk_required=False)
        wifi.SetValue.assert_called_once_with(True)
        audio.SetValue.assert_called_once_with(False)
        wifi.Enable.assert_called_once_with(False)
        audio.Enable.assert_called_once_with(False)

    def test_installed_audio_only_is_displayed_read_only(self) -> None:
        state = self._state(RootPatchState.INSTALLED_SAME, ("Modern Audio",))
        _, wifi, audio, _, _ = self._refresh(state)
        wifi.SetValue.assert_called_once_with(False)
        audio.SetValue.assert_called_once_with(True)

    def test_installed_manual_kdk_mode_is_checked_and_read_only(self) -> None:
        state = self._state(
            RootPatchState.INSTALLED_SAME,
            ("Modern Audio", "Modern Wireless"),
            KDKSelectionMode.MANUAL,
            KDK_IDENTITY,
        )
        _, _, _, manual, manual_history = self._refresh(state)
        manual.SetValue.assert_called_once_with(True)
        manual.Enable.assert_called_once_with(False)
        manual_history.SetLabel.assert_called_once_with("macOS 26.6.2 — Build 25G82")
        manual_history.Show.assert_called_once_with(True)

    def test_installed_auto_kdk_mode_is_unchecked_and_read_only(self) -> None:
        state = self._state(
            RootPatchState.INSTALLED_SAME,
            ("Modern Audio", "Modern Wireless"),
            KDKSelectionMode.AUTO,
            KDK_IDENTITY,
        )
        _, _, _, manual, manual_history = self._refresh(state)
        manual.SetValue.assert_called_once_with(False)
        manual.Enable.assert_called_once_with(False)
        manual_history.SetLabel.assert_called_once_with("")
        manual_history.Show.assert_called_once_with(False)

    def test_legacy_kdk_history_is_not_guessed(self) -> None:
        state = self._state(
            RootPatchState.INSTALLED_SAME,
            ("Modern Audio", "Modern Wireless"),
        )
        _, _, _, manual, manual_history = self._refresh(state)
        manual.SetValue.assert_called_once_with(False)
        manual.Enable.assert_called_once_with(False)
        manual_history.Show.assert_called_once_with(False)

    def test_revert_pending_remains_read_only_and_does_not_claim_installed_selection(self) -> None:
        state = self._state(RootPatchState.REVERT_PENDING)
        display, wifi, audio, manual, manual_history = self._refresh(state)
        wifi.Enable.assert_called_once_with(False)
        audio.Enable.assert_called_once_with(False)
        manual.Enable.assert_called_once_with(False)
        display.selection_summary.SetLabel.assert_called_once_with("Installed selection: Unknown")
        manual_history.Show.assert_called_once_with(False)

    def test_revert_pending_preserves_trustworthy_manual_kdk_display(self) -> None:
        state = self._state(
            RootPatchState.REVERT_PENDING,
            ("Modern Audio", "Modern Wireless"),
            KDKSelectionMode.MANUAL,
            KDK_IDENTITY,
        )
        display, wifi, audio, manual, manual_history = self._refresh(state)
        wifi.SetValue.assert_called_once_with(True)
        audio.SetValue.assert_called_once_with(True)
        manual.SetValue.assert_called_once_with(True)
        manual.Enable.assert_called_once_with(False)
        display.selection_summary.SetLabel.assert_called_once_with("Installed: Modern Wi-Fi + Modern Audio")
        manual_history.SetLabel.assert_called_once_with("macOS 26.6.2 — Build 25G82")
        manual_history.Show.assert_called_once_with(True)

    def test_simulated_reboot_to_clean_makes_controls_editable_again(self) -> None:
        display, wifi, audio, manual, manual_history = self._display(
            manual_state=ManualKDKSelectionState(True, CANDIDATE),
        )
        detection = types.SimpleNamespace(
            applicable_patchsets=APPLICABLE,
            patches={"Modern Wireless": {}, "Modern Audio": {}},
            device_properties={HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED: True},
            can_patch=True,
            can_unpatch=True,
        )
        pending = self._state(
            RootPatchState.REVERT_PENDING,
            ("Modern Audio", "Modern Wireless"),
            KDKSelectionMode.MANUAL,
            KDK_IDENTITY,
        )
        clean = self._state(RootPatchState.CLEAN)
        with mock.patch.object(gui_sys_patch_display, "HardwarePatchsetDetection", return_value=detection), \
             mock.patch.object(gui_sys_patch_display, "RootPatchStateEvaluator") as evaluator:
            evaluator.return_value.evaluate.side_effect = (pending, clean)
            gui_sys_patch_display.SysPatchDisplayFrame._refresh_selection_state(display)
            gui_sys_patch_display.SysPatchDisplayFrame._refresh_selection_state(display)
        self.assertEqual(wifi.Enable.call_args_list, [mock.call(False), mock.call(True)])
        self.assertEqual(audio.Enable.call_args_list, [mock.call(False), mock.call(True)])
        self.assertEqual(manual.Enable.call_args_list, [mock.call(False), mock.call(True)])
        self.assertEqual(manual.SetValue.call_args_list, [mock.call(True), mock.call(False)])
        self.assertEqual(
            manual_history.SetLabel.call_args_list,
            [mock.call("macOS 26.6.2 — Build 25G82"), mock.call("")],
        )
        self.assertEqual(manual_history.Show.call_args_list, [mock.call(True), mock.call(False)])
        self.assertEqual(display.manual_kdk_state, ManualKDKSelectionState())

    def test_nonclean_transition_clears_pending_manual_candidate(self) -> None:
        manual_state = ManualKDKSelectionState(True, CANDIDATE)
        state = self._state(RootPatchState.INSTALLED_DIFFERENT_BUILD, ("Modern Wireless",))
        display, _, _, manual, _ = self._refresh(state, manual_state=manual_state)
        self.assertEqual(display.manual_kdk_state, ManualKDKSelectionState())
        manual.SetValue.assert_called_once_with(False)

    def test_untrusted_states_are_disabled_without_authoritative_selection(self) -> None:
        for state_name in (RootPatchState.LEGACY_FOREIGN, RootPatchState.INVALID_UNKNOWN):
            with self.subTest(state=state_name):
                state = self._state(state_name)
                display, wifi, audio, manual, manual_history = self._refresh(state)
                wifi.SetValue.assert_called_once_with(False)
                audio.SetValue.assert_called_once_with(False)
                wifi.Enable.assert_called_once_with(False)
                audio.Enable.assert_called_once_with(False)
                manual.Enable.assert_called_once_with(False)
                display.selection_summary.SetLabel.assert_called_once_with("Installed selection: Unknown")
                manual_history.Show.assert_called_once_with(False)

    def test_manual_kdk_history_falls_back_to_build_when_version_is_unknown(self) -> None:
        state = self._state(
            RootPatchState.INSTALLED_SAME,
            ("Modern Audio",),
            KDKSelectionMode.MANUAL,
            KernelDebugKitIdentity(None, "25G82", "/Library/Developer/KDKs/example.kdk"),
        )
        _, _, _, _, manual_history = self._refresh(state)
        manual_history.SetLabel.assert_called_once_with("Build 25G82")
        manual_history.Show.assert_called_once_with(True)

    def test_blocked_programmatic_toggle_does_not_change_canonical_selection(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE)
        display = types.SimpleNamespace(
            selection=selection,
            root_state=self._state(RootPatchState.INSTALLED_SAME, ("Modern Audio", "Modern Wireless")),
            _refresh_selection_state=mock.Mock(),
            frame_modal=mock.Mock(),
        )
        gui_sys_patch_display.SysPatchDisplayFrame.on_patch_selection_changed(
            display,
            SelectableRootPatch.MODERN_AUDIO,
            False,
        )
        self.assertEqual(display.selection, selection)


if __name__ == "__main__":
    unittest.main()
