"""Permanent publication invariants for OCLP-CustoMac."""

from __future__ import annotations

import unittest

from pathlib import Path
from unittest import mock

from opencore_legacy_patcher import constants
from opencore_legacy_patcher.sys_patch.patchsets import detect
from opencore_legacy_patcher.sys_patch.patchsets.hardware.misc import modern_audio
from opencore_legacy_patcher.sys_patch.patchsets.hardware.networking import modern_wireless


class PublicationContractTests(unittest.TestCase):
    def test_root_patch_registry_is_exactly_modern_wireless_and_audio(self) -> None:
        with mock.patch.object(detect.HardwarePatchsetDetection, "_detect"):
            detector = detect.HardwarePatchsetDetection(
                mock.MagicMock(),
                xnu_major=25,
                xnu_minor=0,
                os_build="25G82",
                os_version="26.6.2",
            )

        self.assertEqual(
            tuple(detector._hardware_variants),
            (modern_wireless.ModernWireless, modern_audio.ModernAudio),
        )

    def test_public_brand_and_technical_identity_boundary(self) -> None:
        root = Path(__file__).resolve().parents[1]
        current = constants.Constants()
        self.assertEqual(current.patcher_name, "OCLP-CustoMac")
        self.assertEqual(current.project_identity, "OCLP 3.0.0 Nightly - amfipassbeta Edition v2.0")

        spec = (root / "OpenCore-Patcher-GUI.spec").read_text()
        self.assertIn('name=\'OpenCore-Patcher.app\'', spec)
        self.assertIn('bundle_identifier="com.dortania.opencore-legacy-patcher"', spec)
        self.assertIn('"CFBundleName": "OCLP-CustoMac"', spec)

        readme = (root / "README.md").read_text(encoding="utf-8")
        expected_header = """<div align="center">
  <img src="docs/images/OC-Patcher.png" alt="OpenCore Patcher Logo" width="256" />
</div>

# OCLP-CustoMac

### Focused Modern Wi-Fi and AppleHDA root patching for macOS"""
        self.assertTrue(readme.startswith(expected_header))
        self.assertTrue((root / "docs/images/OC-Patcher.png").is_file())

    def test_operational_update_endpoints_target_the_production_repository(self) -> None:
        root = Path(__file__).resolve().parents[1]
        current = constants.Constants()
        expected_repo = "https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta"
        self.assertEqual(current.repo_link, expected_repo)

        operational_sources = [
            root / "opencore_legacy_patcher/constants.py",
            root / "opencore_legacy_patcher/support/updates.py",
            root / "opencore_legacy_patcher/sys_patch/auto_patcher/start.py",
            root / "opencore_legacy_patcher/wx_gui/gui_main_menu.py",
            root / "opencore_legacy_patcher/wx_gui/gui_settings.py",
        ]
        for source in operational_sources:
            text = source.read_text(encoding="utf-8")
            self.assertNotIn("api.github.com/repos/dortania/OpenCore-Legacy-Patcher", text)
            self.assertNotIn("nightly.link/dortania/OpenCore-Legacy-Patcher", text)

    def test_component_baseline_is_frozen(self) -> None:
        current = constants.Constants()
        expected = {
            "opencore_version": "1.0.7",
            "lilu_version": "1.7.2",
            "whatevergreen_version": "1.7.0",
            "restrictevents_version": "1.1.6",
            "airportbcrmfixup_version": "2.2.0",
            "bluetool_version": "2.7.2",
            "nvmefix_version": "1.1.3",
            "cpufriend_version": "1.3.0",
            "cryptexfixup_version": "1.0.5",
            "debugenhancer_version": "1.1.1",
            "applealc_version": "1.9.7",
            "featureunlock_version": "1.1.8",
            "amfipass_version": "1.4.1",
        }
        self.assertEqual({name: getattr(current, name) for name in expected}, expected)


if __name__ == "__main__":
    unittest.main()
