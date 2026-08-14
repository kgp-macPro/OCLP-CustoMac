"""KDK requirements must be derived from the final root-patch selection."""

import types
import unittest

from unittest import mock

from opencore_legacy_patcher.detections.amfi_detect import AmfiConfigDetectLevel
from opencore_legacy_patcher.sys_patch.patchsets.base import PatchType
from opencore_legacy_patcher.sys_patch.patchsets import detect
from opencore_legacy_patcher.sys_patch.patchsets.hardware.base import BaseHardware
from opencore_legacy_patcher.sys_patch.patchsets.hardware.misc.modern_audio import ModernAudio
from opencore_legacy_patcher.sys_patch.root_selection import (
    RootPatchSelection,
    SelectableRootPatch,
)


APPLICABLE = ("Networking: Modern Wireless", "Miscellaneous: Modern Audio")


class _FakeHardware(BaseHardware):
    patchset_name = ""
    patch_name = ""
    kdk_required = False

    def name(self) -> str:
        return self.patchset_name

    def present(self) -> bool:
        return True

    def native_os(self) -> bool:
        return False

    def required_system_integrity_protection_configurations(self) -> list[str]:
        return []

    def required_amfi_level(self) -> AmfiConfigDetectLevel:
        return AmfiConfigDetectLevel.NO_CHECK

    def requires_kernel_debug_kit(self) -> bool:
        return self.kdk_required

    def patches(self) -> dict:
        return {self.patch_name: {}}


class _FakeWireless(_FakeHardware):
    patchset_name = "Networking: Modern Wireless"
    patch_name = "Modern Wireless"


class _FakeAudio(_FakeHardware):
    patchset_name = "Miscellaneous: Modern Audio"
    patch_name = "Modern Audio"
    kdk_required = True


class _FakeOtherKDKPatch(_FakeHardware):
    patchset_name = "Graphics: Future KDK Patch"
    patch_name = "Future KDK Patch"
    kdk_required = True


class _DeterministicDetection(detect.HardwarePatchsetDetection):
    def _validation_check_unsupported_host_os(self) -> bool:
        return False

    def _validation_check_filevault_is_enabled(self) -> bool:
        return False

    def _validation_check_system_integrity_protection_enabled(self, configs: list[str]) -> bool:
        return False

    def _validation_check_secure_boot_model_enabled(self) -> bool:
        return False

    def _validation_check_amfi_enabled(self, level: AmfiConfigDetectLevel) -> bool:
        return False

    def _validation_check_whatevergreen_missing(self) -> bool:
        return False

    def _validation_check_force_opengl_missing(self) -> bool:
        return False

    def _validation_check_force_compat_missing(self) -> bool:
        return False

    def _validation_check_nvda_drv_missing(self) -> bool:
        return False


class Phase3BKDKSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.constants = types.SimpleNamespace(
            detected_os=25,
            detected_os_minor=0,
            detected_os_build="25A123",
            detected_os_version="26.0",
            computer=types.SimpleNamespace(),
        )

    def _detect(
        self,
        selection: RootPatchSelection,
        wireless_class: type[BaseHardware] = _FakeWireless,
    ) -> _DeterministicDetection:
        with mock.patch.object(detect.modern_wireless, "ModernWireless", wireless_class), \
             mock.patch.object(detect.modern_audio, "ModernAudio", _FakeAudio):
            return _DeterministicDetection(
                self.constants,
                validation=True,
                patch_selection=selection,
            )

    def test_wifi_only_excludes_audio_patch_and_audio_kdk_requirement(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE).with_selection(
            SelectableRootPatch.MODERN_AUDIO,
            False,
        )
        result = self._detect(selection)
        self.assertEqual(set(result.patches), {"Modern Wireless"})
        self.assertFalse(result.device_properties[detect.HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED])

    def test_wifi_only_excludes_the_beta_applehda_payload(self) -> None:
        audio_patches = ModernAudio(25, 0, "25A123", self.constants).patches()
        self.assertIn(
            "AppleHDA.kext",
            audio_patches["Modern Audio"][PatchType.OVERWRITE_SYSTEM_VOLUME]["/System/Library/Extensions"],
        )
        selection = RootPatchSelection.initialize(APPLICABLE).with_selection(
            SelectableRootPatch.MODERN_AUDIO,
            False,
        )
        filtered = selection.filter_patch_dictionary({"Modern Wireless": {}, **audio_patches})
        self.assertEqual(set(filtered), {"Modern Wireless"})
        self.assertNotIn("Modern Audio", filtered)

    def test_audio_only_retains_audio_kdk_requirement(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE).with_selection(
            SelectableRootPatch.MODERN_WIFI,
            False,
        )
        result = self._detect(selection)
        self.assertEqual(set(result.patches), {"Modern Audio"})
        self.assertTrue(result.device_properties[detect.HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED])

    def test_both_selected_retains_audio_kdk_requirement(self) -> None:
        result = self._detect(RootPatchSelection.initialize(APPLICABLE))
        self.assertEqual(set(result.patches), {"Modern Wireless", "Modern Audio"})
        self.assertTrue(result.device_properties[detect.HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED])

    def test_both_off_has_no_patch_and_no_audio_kdk_requirement(self) -> None:
        selection = RootPatchSelection.initialize(APPLICABLE)
        selection = selection.with_selection(SelectableRootPatch.MODERN_WIFI, False)
        selection = selection.with_selection(SelectableRootPatch.MODERN_AUDIO, False)
        result = self._detect(selection)
        self.assertEqual(result.patches, {})
        self.assertFalse(result.device_properties[detect.HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED])

    def test_nonselectable_kdk_patch_still_requires_a_kdk(self) -> None:
        selection = RootPatchSelection.initialize(("Miscellaneous: Modern Audio",)).with_selection(
            SelectableRootPatch.MODERN_AUDIO,
            False,
        )
        result = self._detect(selection, wireless_class=_FakeOtherKDKPatch)
        self.assertEqual(set(result.patches), {"Future KDK Patch"})
        self.assertTrue(result.device_properties[detect.HardwarePatchsetSettings.KERNEL_DEBUG_KIT_REQUIRED])


if __name__ == "__main__":
    unittest.main()
