"""Synthetic fixtures for KGP's v2.0 AMFIPass boot-argument invariant."""

import types
import unittest

from opencore_legacy_patcher.efi_builder.build import BuildOpenCore


APPLE_BOOT_GUID = "7C436110-AB2A-4BBB-A880-FE41995C9F82"


class AMFIPassBootArgumentPolicyTests(unittest.TestCase):
    def _builder(self, *, enabled: bool, boot_args: str = "keepsyms=1 debug=0x100") -> BuildOpenCore:
        builder = object.__new__(BuildOpenCore)
        builder.model = "KGP-Tahoe-Fixture"
        builder.constants = types.SimpleNamespace()
        builder.config = {
            "Kernel": {
                "Add": [
                    {
                        "BundlePath": "AMFIPass.kext",
                        "Enabled": enabled,
                    }
                ]
            },
            "NVRAM": {
                "Add": {
                    APPLE_BOOT_GUID: {
                        "boot-args": boot_args,
                    }
                }
            },
        }
        return builder

    def _tokens(self, builder: BuildOpenCore) -> list[str]:
        return builder.config["NVRAM"]["Add"][APPLE_BOOT_GUID]["boot-args"].split()

    def test_enabled_adds_amfipassbeta_once_without_lilubetaall(self) -> None:
        builder = self._builder(enabled=True)
        builder._apply_amfipass_boot_arg_policy()
        self.assertEqual(self._tokens(builder).count("-amfipassbeta"), 1)
        self.assertNotIn("-lilubetaall", self._tokens(builder))

    def test_repeated_requests_are_idempotent(self) -> None:
        builder = self._builder(enabled=True)
        builder._apply_amfipass_boot_arg_policy()
        builder._apply_amfipass_boot_arg_policy()
        self.assertEqual(self._tokens(builder).count("-amfipassbeta"), 1)

    def test_disabled_adds_nothing_and_preserves_unrelated_arguments(self) -> None:
        original = "keepsyms=1 debug=0x100 kgpfixture=preserve"
        builder = self._builder(enabled=False, boot_args=original)
        builder._apply_amfipass_boot_arg_policy()
        self.assertEqual(builder.config["NVRAM"]["Add"][APPLE_BOOT_GUID]["boot-args"], original)

    def test_existing_amfipassbeta_is_not_duplicated(self) -> None:
        original = "keepsyms=1 -amfipassbeta kgpfixture=preserve"
        builder = self._builder(enabled=True, boot_args=original)
        builder._apply_amfipass_boot_arg_policy()
        self.assertEqual(builder.config["NVRAM"]["Add"][APPLE_BOOT_GUID]["boot-args"], original)

    def test_explicit_lilubetaall_is_not_removed(self) -> None:
        builder = self._builder(enabled=True, boot_args="keepsyms=1 -lilubetaall")
        builder._apply_amfipass_boot_arg_policy()
        self.assertEqual(self._tokens(builder).count("-lilubetaall"), 1)
        self.assertEqual(self._tokens(builder).count("-amfipassbeta"), 1)

    def test_exact_token_match_does_not_accept_substrings(self) -> None:
        builder = self._builder(enabled=True, boot_args="keepsyms=1 marker=-amfipassbeta")
        builder._apply_amfipass_boot_arg_policy()
        self.assertEqual(self._tokens(builder).count("-amfipassbeta"), 1)
        self.assertIn("marker=-amfipassbeta", self._tokens(builder))


if __name__ == "__main__":
    unittest.main()
