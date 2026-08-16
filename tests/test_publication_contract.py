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

        gui_entry = (root / "opencore_legacy_patcher/wx_gui/gui_entry.py").read_text()
        gui_main = (root / "opencore_legacy_patcher/wx_gui/gui_main_menu.py").read_text()
        gui_about = (root / "opencore_legacy_patcher/wx_gui/gui_about.py").read_text()
        self.assertIn("title=self.constants.patcher_name", gui_entry)
        self.assertIn('label=f"Version {self.constants.patcher_version}"', gui_main)
        self.assertIn('label=f"Version {self.constants.patcher_version}"', gui_about)
        self.assertIn("Focused Modern Wi-Fi and AppleHDA Root Patching for macOS", gui_about)
        for source in (gui_entry, gui_main, gui_about):
            self.assertNotIn("(Nightly)", source)

    def test_user_visible_gui_strings_have_no_development_branding(self) -> None:
        root = Path(__file__).resolve().parents[1]
        user_visible_sources = [
            *sorted((root / "opencore_legacy_patcher/wx_gui").glob("*.py")),
            root / "opencore_legacy_patcher/sys_patch/auto_patcher/start.py",
            root / "opencore_legacy_patcher/sys_patch/root_state.py",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in user_visible_sources)

        for forbidden in (
            "KGP v2.0",
            "KGP v2",
            "amfipassbeta-v2.0",
            "OCLP-amfipassbeta-v2.0-development",
            "Phase 2",
            "Phase 3",
            "Phase 4",
            "Phase 5",
            "OpenCore Legacy Patcher 3.0.0 (Nightly)",
            "(Nightly)",
            "latest nightly build",
            "nightly update",
            "falling back to Nightly",
            'version_label="Nightly"',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined)

        self.assertIn(
            "Installed metadata predates or is incompatible with the current OCLP-CustoMac metadata format",
            combined,
        )
        self.assertIn('"Install branch build 🧪"', combined)
        self.assertIn('version_label="Branch Build"', combined)

    def test_operational_update_endpoints_target_the_production_repository(self) -> None:
        root = Path(__file__).resolve().parents[1]
        current = constants.Constants()
        expected_repo = "https://github.com/kgp-macPro/OCLP-CustoMac"
        self.assertEqual(current.repo_link, expected_repo)
        self.assertEqual(
            current.installer_pkg_url,
            f"{expected_repo}/releases/download/v3.0.0/AutoPkg-Assets.pkg",
        )

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
            self.assertNotIn("kgp-macPro/OCLP-lzhoang2801-amfipassbeta", text)

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

    def test_normal_ci_is_fail_closed_and_cannot_publish(self) -> None:
        root = Path(__file__).resolve().parents[1]
        workflows = root / ".github/workflows"
        build = (workflows / "build-app-wxpython.yml").read_text()
        validation = (workflows / "validate.yml").read_text()
        site = (workflows / "build-site.yml").read_text()
        combined = "\n".join(path.read_text() for path in workflows.glob("*.yml"))

        self.assertIn("github.repository == 'kgp-macPro/OCLP-CustoMac'", build)
        self.assertIn("python -m unittest discover -s tests", build)
        self.assertIn("codesign --verify --deep --strict", build)
        self.assertIn("OpenCore-Patcher.pkg", build)
        self.assertIn("OpenCore-Patcher-Uninstaller.pkg", build)
        self.assertIn("https://www.python.org/ftp/python/3.14.3/python-3.14.3-macos11.pkg", build)
        self.assertIn("50b709f72cb5ed87d5882901923face981dd657569717761832c36db3bf08238", build)
        self.assertIn("131f5211d7a7ec6279abcc2e4b0b97f8559d8eb77d5a28c22771f9ced084360f", build)
        self.assertIn("pkgutil --expand-full", build)
        self.assertIn("DYLD_FRAMEWORK_PATH", build)
        self.assertIn("arch -x86_64", build)
        self.assertIn("-m venv --without-pip", build)
        self.assertIn("-m ensurepip --upgrade --default-pip", build)
        self.assertIn('= "25.3"', build)
        self.assertIn('PYTHON_FRAMEWORK_PARENT="$RUNNER_TEMP/python-3.14.3"', build)
        self.assertIn('>> "$GITHUB_ENV"', build)
        self.assertNotIn("${{ runner.temp }}", build)
        self.assertNotIn("actions/setup-python", build)
        self.assertNotIn("PYTHON_BIN: /Library/Frameworks/Python.framework", build)
        self.assertIn("python -m unittest discover -s tests", validation)
        self.assertNotIn("continue-on-error: true", validation)
        self.assertNotIn("actions/deploy-pages", site)
        for forbidden in (
            "upload-release-action",
            "softprops/action-gh-release",
            "actions/create-release",
            "gh release create",
            "git push",
        ):
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
