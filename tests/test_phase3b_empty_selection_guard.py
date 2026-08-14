"""Empty root-patch selections must fail before any patch-operation side effect."""

import types
import unittest

from unittest import mock

from opencore_legacy_patcher.sys_patch import sys_patch
from opencore_legacy_patcher.sys_patch.root_selection import (
    EMPTY_SELECTION_MESSAGE,
    RootPatchSelection,
    SelectableRootPatch,
)
from opencore_legacy_patcher.sys_patch.root_state import RootPatchState
from opencore_legacy_patcher.wx_gui import gui_sys_patch_display, gui_sys_patch_start


APPLICABLE = ("Networking: Modern Wireless", "Miscellaneous: Modern Audio")


def empty_selection() -> RootPatchSelection:
    selection = RootPatchSelection.initialize(APPLICABLE)
    selection = selection.with_selection(SelectableRootPatch.MODERN_WIFI, False)
    return selection.with_selection(SelectableRootPatch.MODERN_AUDIO, False)


class Phase3BEmptySelectionGuardTests(unittest.TestCase):
    def test_display_disables_start_for_empty_and_reenables_after_wifi_selection(self) -> None:
        display = types.SimpleNamespace(
            constants=types.SimpleNamespace(),
            selection=empty_selection(),
            selection_checkboxes={},
            selection_summary=mock.Mock(),
            selection_state_label=mock.Mock(),
            start_button=mock.Mock(),
            revert_button=mock.Mock(),
            _applicable_patchsets=lambda detection: detection.applicable_patchsets,
        )
        root_state = types.SimpleNamespace(
            state=RootPatchState.CLEAN,
            reason="",
            patch_allowed=True,
            revert_allowed=lambda can_unpatch: False,
        )
        empty_detection = types.SimpleNamespace(
            applicable_patchsets=APPLICABLE,
            patches={},
            can_patch=True,
            can_unpatch=True,
        )

        with mock.patch.object(gui_sys_patch_display, "HardwarePatchsetDetection", return_value=empty_detection), \
             mock.patch.object(gui_sys_patch_display, "RootPatchStateEvaluator") as evaluator:
            evaluator.return_value.evaluate.return_value = root_state
            gui_sys_patch_display.SysPatchDisplayFrame._refresh_selection_state(display)

        display.start_button.Enable.assert_called_with(False)

        display.selection = display.selection.with_selection(SelectableRootPatch.MODERN_WIFI, True)
        wifi_detection = types.SimpleNamespace(
            applicable_patchsets=APPLICABLE,
            patches={"Modern Wireless": {}},
            can_patch=True,
            can_unpatch=True,
        )
        display.start_button.Enable.reset_mock()

        with mock.patch.object(gui_sys_patch_display, "HardwarePatchsetDetection", return_value=wifi_detection), \
             mock.patch.object(gui_sys_patch_display, "RootPatchStateEvaluator") as evaluator:
            evaluator.return_value.evaluate.return_value = root_state
            gui_sys_patch_display.SysPatchDisplayFrame._refresh_selection_state(display)

        display.start_button.Enable.assert_called_with(True)

    def test_display_guard_uses_exact_message_and_does_not_leave_selection_page(self) -> None:
        display = types.SimpleNamespace(
            requested_patchset={},
            _refresh_selection_state=mock.Mock(),
        )

        with mock.patch.object(gui_sys_patch_display.wx, "MessageBox") as message_box, \
             mock.patch.object(gui_sys_patch_display.gui_sys_patch_start, "SysPatchStartFrame") as start_frame:
            gui_sys_patch_display.SysPatchDisplayFrame.on_start_root_patching(display)

        message_box.assert_called_once_with(
            EMPTY_SELECTION_MESSAGE,
            "Root Patching Blocked",
            gui_sys_patch_display.wx.OK | gui_sys_patch_display.wx.ICON_WARNING,
        )
        start_frame.assert_not_called()

    def test_start_frame_rejects_empty_before_detection_or_kdk_handling(self) -> None:
        start = types.SimpleNamespace(
            patch_selection=empty_selection(),
            constants=types.SimpleNamespace(),
        )

        with mock.patch.object(gui_sys_patch_start, "HardwarePatchsetDetection") as detection, \
             mock.patch.object(gui_sys_patch_start.wx, "MessageBox") as message_box, \
             mock.patch.object(gui_sys_patch_start.SysPatchStartFrame, "_kdk_download") as kdk_download:
            result = gui_sys_patch_start.SysPatchStartFrame._revalidate_patch_selection(start)

        self.assertIsNone(result)
        detection.assert_not_called()
        kdk_download.assert_not_called()
        message_box.assert_called_once_with(
            EMPTY_SELECTION_MESSAGE,
            "Root Patching Blocked",
            gui_sys_patch_start.wx.OK | gui_sys_patch_start.wx.ICON_WARNING,
        )

    def test_operation_rejects_empty_before_detection_mount_patch_kc_snapshot_or_metadata(self) -> None:
        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.patch_selection = empty_selection()
        patcher.constants = types.SimpleNamespace(detected_os=25)
        patcher._mount_root_vol = mock.Mock()
        patcher._patch_root_vol = mock.Mock()
        patcher._merge_kdk_with_root = mock.Mock()
        patcher._rebuild_kernel_cache = mock.Mock()
        patcher._create_new_apfs_snapshot = mock.Mock()
        patcher._write_patchset = mock.Mock()

        with mock.patch.object(sys_patch, "HardwarePatchsetDetection") as detection, \
             mock.patch.object(sys_patch, "PatcherSupportPkgMount") as support_mount, \
             self.assertLogs(level="ERROR") as captured:
            patcher.start_patch()

        self.assertIn(EMPTY_SELECTION_MESSAGE, "\n".join(captured.output))
        detection.assert_not_called()
        support_mount.assert_not_called()
        patcher._mount_root_vol.assert_not_called()
        patcher._patch_root_vol.assert_not_called()
        patcher._merge_kdk_with_root.assert_not_called()
        patcher._rebuild_kernel_cache.assert_not_called()
        patcher._create_new_apfs_snapshot.assert_not_called()
        patcher._write_patchset.assert_not_called()

    def test_operation_rejects_recomputed_empty_before_support_package_and_mount(self) -> None:
        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.patch_selection = RootPatchSelection.initialize(("Networking: Modern Wireless",))
        patcher.expected_patch_selection = ("Modern Wireless",)
        patcher.constants = types.SimpleNamespace(detected_os=25)
        patcher._mount_root_vol = mock.Mock()
        empty_detection = types.SimpleNamespace(patches={})

        with mock.patch.object(sys_patch, "HardwarePatchsetDetection", return_value=empty_detection), \
             mock.patch.object(sys_patch, "PatcherSupportPkgMount") as support_mount, \
             self.assertLogs(level="ERROR") as captured:
            patcher.start_patch()

        self.assertIn(EMPTY_SELECTION_MESSAGE, "\n".join(captured.output))
        support_mount.assert_not_called()
        patcher._mount_root_vol.assert_not_called()

    def test_direct_entry_without_explicit_selection_uses_detected_patches(self) -> None:
        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.constants = types.SimpleNamespace(detected_os=25)
        patcher._apply_hardware_details = mock.Mock()
        patcher._mount_root_vol = mock.Mock()
        detection = types.SimpleNamespace(
            patches={"Modern Wireless": {}},
            can_patch=True,
            device_properties={},
        )
        root_state = types.SimpleNamespace(patch_allowed=True)
        support_mount = mock.Mock()
        support_mount.mount.return_value = False

        with mock.patch.object(sys_patch, "HardwarePatchsetDetection", return_value=detection), \
             mock.patch.object(sys_patch, "RootPatchStateEvaluator") as evaluator, \
             mock.patch.object(sys_patch, "PatcherSupportPkgMount", return_value=support_mount):
            evaluator.return_value.evaluate.return_value = root_state
            patcher.start_patch()

        support_mount.mount.assert_called_once_with()
        patcher._mount_root_vol.assert_not_called()


if __name__ == "__main__":
    unittest.main()
