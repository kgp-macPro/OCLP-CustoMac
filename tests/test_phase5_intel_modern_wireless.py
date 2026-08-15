"""Generic Intel Modern Wireless applicability and frozen Broadcom regressions."""

from __future__ import annotations

import inspect
import types
import unittest

from pathlib import Path
from unittest import mock

from opencore_legacy_patcher.datasets import pci_data
from opencore_legacy_patcher.detections import device_probe
from opencore_legacy_patcher.sys_patch.patchsets.hardware.networking import modern_wireless
from opencore_legacy_patcher.sys_patch.root_selection import RootPatchSelection, SelectableRootPatch


AIRPORT_ITLWM_SUPPORTED_IDS = frozenset(
    int(device_id, 16)
    for device_id in """
        2723 43F0 A0F0 34F0 4DF0 02F0 3DF0 06F0 2720
        08B1 08B2 08B3 08B4 095A 095B 3165 3166 24F3 24F4 24F5 24F6
        24FB 24FD 2526 9DF0 A370 31DC 30DC 271C 271B 42A4 00A0 00A4
        02A0 40A4 0060 0064 0260 0264
        4229 422B 422C 4230 4232 4235 4236 4237 4238 4239 423A 423B
        423C 423D 0082 0083 0084 0085 0087 0089 008A 008B 0090 0091
        0892 0893 0894 0895 0896 0897 08AE 08AF 088E 088F 0890 0891
        0887 0888
        2725 2726 7A70 7AF0 51F0 54F0 2729 7E40 7F70 51F1
    """.split()
)


def _intel(device_id: int) -> device_probe.IntelWirelessCard:
    return device_probe.IntelWirelessCard(
        vendor_id=0x8086,
        device_id=device_id,
        class_code=0x028000,
    )


def _broadcom(
    device_id: int = 0x43A0,
    chipset: device_probe.Broadcom.Chipsets = device_probe.Broadcom.Chipsets.AirPortBrcm4360,
) -> device_probe.Broadcom:
    device = device_probe.Broadcom(
        vendor_id=0x14E4,
        device_id=device_id,
        class_code=0x028000,
    )
    device.chipset = chipset
    return device


def _patchset(wifi=None, wifi_devices=None) -> modern_wireless.ModernWireless:
    computer = types.SimpleNamespace(wifi=wifi)
    if wifi_devices is not None:
        computer.wifi_devices = wifi_devices
    constants = types.SimpleNamespace(computer=computer)
    return modern_wireless.ModernWireless(25, 0, "25G82", constants)


class Phase5IntelModernWirelessTests(unittest.TestCase):
    def test_dataset_exactly_matches_audited_airportitlwm_personality(self) -> None:
        self.assertEqual(len(AIRPORT_ITLWM_SUPPORTED_IDS), 87)
        self.assertEqual(pci_data.intel_wireless_ids.AirportItlwm, AIRPORT_ITLWM_SUPPORTED_IDS)

    def test_every_airportitlwm_supported_intel_id_is_applicable(self) -> None:
        for device_id in sorted(AIRPORT_ITLWM_SUPPORTED_IDS):
            with self.subTest(device_id=f"{device_id:04X}"):
                wifi = _intel(device_id)
                self.assertEqual(wifi.chipset, device_probe.IntelWirelessCard.Chipsets.AirportItlwm)
                self.assertTrue(_patchset(wifi).present())

    def test_representative_generations_and_ax210_are_applicable(self) -> None:
        representatives = {
            "WiFi Link 4965": 0x4229,
            "Wireless-AC 7260": 0x08B1,
            "Wireless-AC 8265": 0x24FD,
            "Wireless-AC 9560 CNVi": 0x9DF0,
            "AX200": 0x2723,
            "AX201/CNVi": 0x2720,
            "AX210": 0x2725,
            "newer MA family": 0x2729,
        }
        for family, device_id in representatives.items():
            with self.subTest(family=family, device_id=f"{device_id:04X}"):
                self.assertTrue(_patchset(_intel(device_id)).present())

    def test_unsupported_intel_ids_are_not_applicable(self) -> None:
        for device_id in (0x0885, 0x0886, 0x272B, 0xFFFF):
            with self.subTest(device_id=f"{device_id:04X}"):
                wifi = _intel(device_id)
                self.assertEqual(wifi.chipset, device_probe.IntelWirelessCard.Chipsets.Unknown)
                self.assertFalse(_patchset(wifi).present())

    def test_non_intel_device_with_overlapping_id_is_not_intel(self) -> None:
        wifi = _broadcom(device_id=0x2725, chipset=device_probe.Broadcom.Chipsets.Unknown)
        self.assertFalse(_patchset(wifi).present())

    def test_raw_vendor_detection_requires_intel_vendor(self) -> None:
        intel = device_probe.PCIDevice(0x8086, 0x2725, 0x028000)
        overlapping = device_probe.PCIDevice(0x14E4, 0x2725, 0x028000)
        self.assertIs(intel.vendor_detect(inherits=device_probe.WirelessCard), device_probe.IntelWirelessCard)
        self.assertIsNot(overlapping.vendor_detect(inherits=device_probe.WirelessCard), device_probe.IntelWirelessCard)

    def test_probe_retains_complete_inventory_and_logs_supported_intel_identity(self) -> None:
        intel_entry = object()
        broadcom_entry = object()
        intel_raw = device_probe.PCIDevice(0x8086, 0x2725, 0x028000)
        broadcom_raw = device_probe.PCIDevice(0x14E4, 0x43A0, 0x028000)
        intel = _intel(0x2725)
        broadcom = _broadcom()
        computer = device_probe.Computer()

        with mock.patch.object(
            device_probe.ioreg,
            "IOServiceGetMatchingServices",
            return_value=(None, object()),
        ), mock.patch.object(
            device_probe.ioreg,
            "ioiterator_to_list",
            return_value=[intel_entry, broadcom_entry],
        ), mock.patch.object(
            device_probe.PCIDevice,
            "from_ioregistry",
            side_effect=[intel_raw, broadcom_raw],
        ), mock.patch.object(
            device_probe.IntelWirelessCard,
            "from_ioregistry",
            return_value=intel,
        ), mock.patch.object(
            device_probe.Broadcom,
            "from_ioregistry",
            return_value=broadcom,
        ), mock.patch.object(
            device_probe.ioreg,
            "IOObjectRelease",
        ) as release, mock.patch.object(device_probe.logging, "info") as log:
            computer.wifi_probe()

        self.assertEqual(computer.wifi_devices, [intel, broadcom])
        self.assertIs(computer.wifi, broadcom)
        self.assertEqual(release.call_count, 2)
        log.assert_called_once_with("- Detected supported Intel Modern Wireless device: 8086:2725")

    def test_broadcom_intel_inventory_matrix_uses_one_shared_patchset(self) -> None:
        broadcom = _broadcom()
        intel = _intel(0x2725)
        cases = {
            "Broadcom only": ([broadcom], True),
            "Intel only": ([intel], True),
            "Broadcom and Intel": ([broadcom, intel], True),
            "neither": ([], False),
        }
        for case, (inventory, expected) in cases.items():
            with self.subTest(case=case):
                patchset = _patchset(wifi=None, wifi_devices=inventory)
                self.assertEqual(patchset.present(), expected)
                if expected:
                    self.assertEqual(tuple(patchset.patches()), ("Modern Wireless",))

    def test_intel_and_broadcom_share_identical_payload_dictionary(self) -> None:
        self.assertEqual(_patchset(_intel(0x2725)).patches(), _patchset(_broadcom()).patches())

    def test_intel_wifi_only_does_not_require_a_kdk(self) -> None:
        patchset = _patchset(_intel(0x2725))
        self.assertTrue(patchset.present())
        self.assertFalse(patchset.requires_kernel_debug_kit())

    def test_intel_applicability_defaults_existing_modern_wifi_selection_on(self) -> None:
        patchset = _patchset(_intel(0x2725))
        selection = RootPatchSelection.initialize((patchset.name(),))
        self.assertTrue(selection.is_applicable(SelectableRootPatch.MODERN_WIFI))
        self.assertTrue(selection.is_selected(SelectableRootPatch.MODERN_WIFI))

    def test_intel_detection_does_not_enter_the_efi_wireless_builder(self) -> None:
        source_path = Path("opencore_legacy_patcher/efi_builder/networking/wireless.py")
        source = source_path.read_text(encoding="utf-8")
        self.assertNotIn("IntelWirelessCard", source)
        self.assertNotIn("AirportItlwm", source)

    def test_detector_contains_no_spoof_or_efi_mutation(self) -> None:
        source = inspect.getsource(modern_wireless.ModernWireless.present)
        for forbidden in ("DeviceProperties", "compatible", "IOName", "fake_id", "config.plist"):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
