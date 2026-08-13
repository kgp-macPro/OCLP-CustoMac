"""Fail-closed tests for exact KGP source metadata."""

import os
import subprocess
import tempfile
import unittest

from dataclasses import replace
from pathlib import Path

from ci_tooling.build_metadata import CANONICAL_REPOSITORY_URL, SourceBuildMetadata


class SourceBuildMetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.repository = Path(self.temporary_directory.name)
        self._git("init", "-b", "fixture")
        self._git("config", "user.name", "KGP Fixture")
        self._git("config", "user.email", "fixture@example.invalid")
        (self.repository / "source.txt").write_text("fixture\n", encoding="utf-8")
        self._git("add", "source.txt")
        environment = os.environ.copy()
        environment.update({
            "GIT_AUTHOR_DATE": "2026-08-13T00:00:00+02:00",
            "GIT_COMMITTER_DATE": "2026-08-13T00:00:00+02:00",
        })
        subprocess.run(
            ["/usr/bin/git", "-C", str(self.repository), "commit", "-m", "fixture"],
            check=True,
            capture_output=True,
            env=environment,
        )
        self.valid = SourceBuildMetadata.from_repository(self.repository)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _git(self, *arguments: str) -> str:
        return subprocess.run(
            ["/usr/bin/git", "-C", str(self.repository), *arguments],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _assert_invalid(self, metadata: SourceBuildMetadata) -> None:
        with self.assertRaises(RuntimeError):
            metadata.validate(self.repository)

    def test_valid_exact_metadata_passes(self) -> None:
        self.valid.validate(self.repository)
        self.assertEqual(self.valid.commit_url, f"{CANONICAL_REPOSITORY_URL}/commit/{self.valid.commit_sha}")
        self.assertEqual(len(self.valid.commit_sha), 40)

    def test_missing_commit_url_fails(self) -> None:
        self._assert_invalid(replace(self.valid, commit_url=""))

    def test_abbreviated_sha_fails(self) -> None:
        short_sha = self.valid.commit_sha[:12]
        self._assert_invalid(replace(self.valid, commit_sha=short_sha, commit_url=f"{CANONICAL_REPOSITORY_URL}/commit/{short_sha}"))

    def test_wrong_sha_fails(self) -> None:
        wrong_sha = "0" * 40
        self._assert_invalid(replace(self.valid, commit_sha=wrong_sha, commit_url=f"{CANONICAL_REPOSITORY_URL}/commit/{wrong_sha}"))

    def test_wrong_repository_fails(self) -> None:
        self._assert_invalid(replace(
            self.valid,
            repository_url="https://github.com/example/foreign",
            commit_url=f"https://github.com/example/foreign/commit/{self.valid.commit_sha}",
        ))

    def test_wrong_commit_date_fails(self) -> None:
        self._assert_invalid(replace(self.valid, commit_date="2026-08-13T01:00:00+02:00"))

    def test_missing_ref_fails(self) -> None:
        self._assert_invalid(replace(self.valid, ref=""))

    def test_dirty_source_fails(self) -> None:
        (self.repository / "untracked.txt").write_text("dirty\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "dirty source tree"):
            SourceBuildMetadata.from_repository(self.repository)


if __name__ == "__main__":
    unittest.main()
