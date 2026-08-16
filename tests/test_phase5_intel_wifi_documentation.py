"""Keep the public Intel Wi-Fi support contract synchronized with detection."""

from __future__ import annotations

import re
import unittest

from pathlib import Path

from opencore_legacy_patcher.datasets import pci_data


DOCUMENT = Path(__file__).resolve().parents[1] / "Documentation" / "Intel-WiFi-Device-Support.md"
EXCLUDED_IDS = frozenset({0x0885, 0x0886})


def _documented_ids(section: str) -> tuple[frozenset[int], list[str]]:
    text = DOCUMENT.read_text(encoding="utf-8")
    start = f"<!-- INTEL_WIFI_{section}_IDS_START -->"
    end = f"<!-- INTEL_WIFI_{section}_IDS_END -->"
    assert text.count(start) == 1
    assert text.count(end) == 1
    body = text.split(start, 1)[1].split(end, 1)[0]
    matches = re.findall(r"`8086:([0-9A-F]{4})`", body)
    assert len(matches) == len(set(matches)), f"Duplicate {section} PCI ID in public documentation"
    return frozenset(int(device_id, 16) for device_id in matches), body.splitlines()


class Phase5IntelWiFiDocumentationTests(unittest.TestCase):
    def test_documented_regular_ids_match_implementation(self) -> None:
        documented, _ = _documented_ids("REGULAR")
        self.assertEqual(documented, pci_data.intel_wireless_ids.AirportItlwm)
        self.assertEqual(len(documented), 87)

    def test_documented_experimental_ids_match_implementation(self) -> None:
        documented, _ = _documented_ids("EXPERIMENTAL")
        self.assertEqual(documented, pci_data.intel_wireless_ids.Experimental)
        self.assertEqual(len(documented), 9)

    def test_documented_exclusions_remain_outside_detector(self) -> None:
        documented, _ = _documented_ids("EXCLUDED")
        implemented = (
            pci_data.intel_wireless_ids.AirportItlwm
            | pci_data.intel_wireless_ids.Experimental
        )
        self.assertEqual(documented, EXCLUDED_IDS)
        self.assertTrue(documented.isdisjoint(implemented))

    def test_public_table_classifications_and_final_count_are_frozen(self) -> None:
        regular, regular_lines = _documented_ids("REGULAR")
        experimental, experimental_lines = _documented_ids("EXPERIMENTAL")
        excluded, excluded_lines = _documented_ids("EXCLUDED")

        self.assertEqual(len(regular | experimental), 96)
        self.assertTrue(regular.isdisjoint(experimental))
        for line in regular_lines:
            if line.startswith("| `8086:"):
                self.assertIn("| Regular |", line)
        for line in experimental_lines:
            if line.startswith("| `8086:"):
                self.assertIn("| Experimental / Development |", line)
        for line in excluded_lines:
            if line.startswith("| `8086:"):
                self.assertIn("| Excluded |", line)


if __name__ == "__main__":
    unittest.main()
