"""Revert must not expose or perform root-patching KDK preparation."""

import types
import unittest

from unittest import mock

from opencore_legacy_patcher.support import kdk_handler
from opencore_legacy_patcher.sys_patch import sys_patch
from opencore_legacy_patcher.sys_patch.patchsets import HardwarePatchsetSettings
from opencore_legacy_patcher.sys_patch.root_selection import RootPatchSelection
from opencore_legacy_patcher.wx_gui import gui_sys_patch_display, gui_sys_patch_start


INSTALLED_KDK = "/Library/Developer/KDKs/KDK_26.6.2_25G82.kdk"


def _kdk_constants():
    return types.SimpleNamespace(patcher_version="3.0.0")


class RevertKDKLoggingTests(unittest.TestCase):
    def test_quiet_lookup_suppresses_installed_status_but_normal_lookup_logs_it(self) -> None:
        with mock.patch.object(
            kdk_handler.KernelDebugKitObject,
            "_local_kdk_installed",
            return_value=INSTALLED_KDK,
        ), mock.patch.object(kdk_handler.logging, "info") as log:
            normal = kdk_handler.KernelDebugKitObject(_kdk_constants(), "25G82", "26.6.2")
        self.assertTrue(normal.kdk_already_installed)
        log.assert_any_call("KDK already installed (KDK_26.6.2_25G82.kdk), skipping")

        with mock.patch.object(
            kdk_handler.KernelDebugKitObject,
            "_local_kdk_installed",
            return_value=INSTALLED_KDK,
        ), mock.patch.object(kdk_handler.logging, "info") as log:
            quiet = kdk_handler.KernelDebugKitObject(
                _kdk_constants(),
                "25G82",
                "26.6.2",
                quiet_installed_status=True,
            )
        self.assertTrue(quiet.kdk_already_installed)
        log.assert_not_called()

    def test_revert_operation_skips_kdk_resolution_download_install_and_merge(self) -> None:
        patcher = sys_patch.PatchSysVolume.__new__(sys_patch.PatchSysVolume)
        patcher.constants = types.SimpleNamespace()
        patcher.patch_selection = RootPatchSelection(frozenset(), frozenset())
        patcher._mount_root_vol = mock.Mock(return_value=True)
        patcher._unpatch_root_vol = mock.Mock()
        detection = types.SimpleNamespace(
            patches={"Modern Audio": {}},
            can_unpatch=True,
        )
        root_state = types.SimpleNamespace(recovery_authorized=True)

        with mock.patch.object(sys_patch, "HardwarePatchsetDetection", return_value=detection) as detector, \
             mock.patch.object(sys_patch, "RootPatchStateEvaluator") as evaluator, \
             mock.patch.object(sys_patch.kdk_handler, "KernelDebugKitObject") as resolver, \
             mock.patch.object(sys_patch, "KernelDebugKitMerge") as merger:
            evaluator.return_value.evaluate.return_value = root_state
            patcher.start_unpatch()

        detector.assert_called_once_with(
            patcher.constants,
            patch_selection=patcher.patch_selection,
            check_kdk_status=False,
            quiet_kdk_status=True,
        )
        resolver.assert_not_called()
        merger.assert_not_called()
        patcher._mount_root_vol.assert_called_once_with()
        patcher._unpatch_root_vol.assert_called_once_with()

    def test_revert_construction_skips_kdk_status_while_patch_construction_does_not(self) -> None:
        constants = types.SimpleNamespace(
            computer=types.SimpleNamespace(),
            detected_os=25,
        )
        detection = types.SimpleNamespace(
            applicable_patchsets=("Miscellaneous: Modern Audio",),
            patches={"Modern Audio": {}},
            device_properties={
                HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED: True,
                HardwarePatchsetSettings.METALLIB_SUPPORT_PKG_REQUIRED: False,
            },
        )
        state = types.SimpleNamespace(installed_selection=None)

        def construct(unpatching: bool):
            with mock.patch.object(sys_patch.utilities, "check_if_root_is_apfs_snapshot", return_value=True), \
                 mock.patch.object(sys_patch, "HardwarePatchsetDetection", return_value=detection) as detector, \
                 mock.patch.object(sys_patch, "RootPatchStateEvaluator") as evaluator, \
                 mock.patch.object(sys_patch.PatchSysVolume, "_init_pathing"), \
                 mock.patch.object(sys_patch, "RootVolumeMount"):
                evaluator.return_value.evaluate.return_value = state
                sys_patch.PatchSysVolume("MacPro7,1", constants, unpatching=unpatching)
            return detector.call_args_list

        revert_calls = construct(True)
        self.assertEqual(len(revert_calls), 2)
        for call in revert_calls:
            self.assertFalse(call.kwargs["check_kdk_status"])
            self.assertTrue(call.kwargs["quiet_kdk_status"])

        patch_calls = construct(False)
        self.assertEqual(len(patch_calls), 2)
        for call in patch_calls:
            self.assertTrue(call.kwargs["check_kdk_status"])
            self.assertFalse(call.kwargs["quiet_kdk_status"])

    def test_revert_click_revalidates_state_and_marks_following_frame_as_revert(self) -> None:
        frame = mock.Mock()
        display = types.SimpleNamespace(
            _refresh_selection_state=mock.Mock(),
            root_state=types.SimpleNamespace(recovery_authorized=True),
            current_detection=types.SimpleNamespace(can_unpatch=True, device_properties={}),
            selection=RootPatchSelection(frozenset(), frozenset()),
            title="Root Patching",
            constants=types.SimpleNamespace(),
            frame_modal=mock.Mock(),
            frame=mock.Mock(),
        )
        with mock.patch.object(gui_sys_patch_start, "SysPatchStartFrame", return_value=frame) as start_frame:
            gui_sys_patch_display.SysPatchDisplayFrame.on_revert_root_patching(display)

        display._refresh_selection_state.assert_called_once_with(check_kdk_status=False)
        start_frame.assert_called_once_with(
            parent=None,
            title=display.title,
            global_constants=display.constants,
            patches=display.current_detection.device_properties,
            patch_selection=display.selection,
            revert_mode=True,
        )
        frame.revert_root_patching.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
