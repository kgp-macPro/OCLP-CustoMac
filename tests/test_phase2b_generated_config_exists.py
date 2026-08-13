"""Regression tests for generated config existence validation."""

import plistlib
import tempfile
import types
import unittest

from pathlib import Path

from opencore_legacy_patcher.efi_builder.support import BuildSupport


class GeneratedConfigExistsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.release = Path(self.temporary_directory.name)
        for directory in ("EFI/OC/ACPI", "EFI/OC/Kexts", "EFI/OC/Tools", "EFI/OC/Drivers"):
            (self.release / directory).mkdir(parents=True, exist_ok=True)
        self.constants = types.SimpleNamespace(opencore_release_folder=self.release)
        self.support = BuildSupport("KGP-Tahoe-Fixture", self.constants, {})

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_absent_config_uses_missing_config_branch(self) -> None:
        with self.assertRaisesRegex(Exception, "OpenCore config file missing"):
            self.support.validate_pathing()

    def test_existing_minimal_config_uses_validation_branch(self) -> None:
        config = {
            "ACPI": {"Add": []},
            "Kernel": {"Add": []},
            "Misc": {"Tools": []},
            "UEFI": {"Drivers": []},
        }
        config_path = self.release / "EFI/OC/config.plist"
        with config_path.open("wb") as config_file:
            plistlib.dump(config, config_file)
        self.support.validate_pathing()


if __name__ == "__main__":
    unittest.main()
