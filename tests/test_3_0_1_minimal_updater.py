"""Minimal regression coverage for OCLP-CustoMac's stable update comparator."""

from __future__ import annotations

import types
import unittest

from packaging import version

from opencore_legacy_patcher.support import updates


class MinimalUpdaterComparatorTests(unittest.TestCase):
    @staticmethod
    def _checker(local_version: str, local_ref: str) -> updates.CheckBinaryUpdates:
        return updates.CheckBinaryUpdates(
            types.SimpleNamespace(
                patcher_version=local_version,
                special_build=False,
                commit_info=(local_ref, "", ""),
            )
        )

    def _remote_is_newer(self, local_version: str, remote_version: str, local_ref: str) -> bool:
        checker = self._checker(local_version, local_ref)
        return checker._check_if_build_newer(remote_version, checker.binary_version)

    def test_equal_branch_build_is_not_an_update(self) -> None:
        self.assertFalse(self._remote_is_newer("3.0.0", "v3.0.0", "refs/heads/main"))

    def test_equal_tagged_build_is_not_an_update(self) -> None:
        self.assertFalse(self._remote_is_newer("3.0.0", "v3.0.0", "refs/tags/v3.0.0"))

    def test_newer_remote_release_is_an_update(self) -> None:
        self.assertTrue(self._remote_is_newer("3.0.0", "v3.0.1", "refs/heads/main"))

    def test_equal_current_release_is_not_an_update(self) -> None:
        self.assertFalse(self._remote_is_newer("3.0.1", "v3.0.1", "refs/tags/v3.0.1"))

    def test_older_remote_release_is_not_an_update(self) -> None:
        self.assertFalse(self._remote_is_newer("3.0.2", "v3.0.1", "refs/tags/v3.0.2"))

    def test_v_prefix_normalizes_with_existing_version_parser(self) -> None:
        self.assertEqual(version.parse("v3.0.1"), version.parse("3.0.1"))
        self.assertTrue(self._remote_is_newer("v3.0.0", "v3.0.1", "refs/heads/main"))


if __name__ == "__main__":
    unittest.main()
