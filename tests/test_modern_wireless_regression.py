"""Modern Wireless detection/payload and hardware-agnostic selection regression gates."""

import inspect
import types
import unittest

from opencore_legacy_patcher.detections import device_probe
from opencore_legacy_patcher.sys_patch.patchsets.hardware.networking import modern_wireless
from opencore_legacy_patcher.sys_patch.root_selection import RootPatchSelection, SelectableRootPatch


class ModernWirelessRegressionTests(unittest.TestCase):
    def _patchset(self, wifi) -> modern_wireless.ModernWireless:
        constants = types.SimpleNamespace(computer=types.SimpleNamespace(wifi=wifi))
        return modern_wireless.ModernWireless(25, 0, "25G82", constants)

    def test_supported_broadcom_modern_wireless_is_unchanged(self) -> None:
        wifi = device_probe.Broadcom(vendor_id=0x14E4, device_id=0x43A0, class_code=0x028000)
        wifi.chipset = device_probe.Broadcom.Chipsets.AirPortBrcm4360
        patchset = self._patchset(wifi)
        self.assertTrue(patchset.present())
        self.assertEqual(
            set(patchset.patches()["Modern Wireless"].keys()),
            {"Overwrite System Volume", "Merge System Volume"},
        )

    def test_externally_spoofed_intel_path_remains_the_same_broadcom_input(self) -> None:
        # KGP's current Intel contract remains external identity preparation;
        # the root-selection layer consumes applicability without inspecting PCI IDs.
        selection = RootPatchSelection.initialize(("Networking: Modern Wireless",))
        self.assertTrue(selection.is_selected(SelectableRootPatch.MODERN_WIFI))
        self.assertEqual(selection.filter_patch_dictionary({"Modern Wireless": {"payload": "unchanged"}}), {
            "Modern Wireless": {"payload": "unchanged"},
        })
        selection_source = inspect.getsource(RootPatchSelection)
        for forbidden in ("Broadcom", "Intel", "vendor_id", "device_id", "8086"):
            self.assertNotIn(forbidden, selection_source)

    def test_direct_intel_detection_adds_no_spoofing_logic(self) -> None:
        source = inspect.getsource(modern_wireless.ModernWireless.present)
        self.assertIn("device_probe.Broadcom", source)
        self.assertIn("device_probe.IntelWirelessCard", source)
        for forbidden in ("DeviceProperties", "fake_id", "compatible", "IOName"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
