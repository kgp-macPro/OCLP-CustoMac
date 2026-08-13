"""Validated source identity for reproducible KGP application builds."""

from __future__ import annotations

import re
import subprocess

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


CANONICAL_REPOSITORY_URL = "https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta"
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _git(repository: Path, *arguments: str, check: bool = True) -> str:
    result = subprocess.run(
        ["/usr/bin/git", "-C", str(repository), *arguments],
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Git metadata query failed")
    return result.stdout.strip()


def _normalize_repository_url(url: str) -> str:
    return url.removesuffix(".git").rstrip("/")


@dataclass(frozen=True)
class SourceBuildMetadata:
    ref: str
    commit_sha: str
    commit_url: str
    commit_date: str
    repository_url: str = CANONICAL_REPOSITORY_URL

    @classmethod
    def from_repository(
        cls,
        repository: Path,
        *,
        ref: str | None = None,
        commit_url: str | None = None,
        commit_date: str | None = None,
    ) -> "SourceBuildMetadata":
        repository = repository.resolve()
        if _git(repository, "status", "--porcelain=v1", "--untracked-files=all"):
            raise RuntimeError("Refusing to build from a dirty source tree")

        head = _git(repository, "rev-parse", "HEAD")
        actual_date = _git(repository, "show", "-s", "--format=%cI", "HEAD")
        actual_ref = cls._resolve_ref(repository, ref)
        canonical_url = f"{CANONICAL_REPOSITORY_URL}/commit/{head}"

        metadata = cls(
            ref=actual_ref,
            commit_sha=head,
            commit_url=commit_url or canonical_url,
            commit_date=commit_date or actual_date,
        )
        metadata.validate(repository)
        return metadata

    @staticmethod
    def _resolve_ref(repository: Path, supplied_ref: str | None) -> str:
        branch = _git(repository, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
        exact_tag = _git(repository, "describe", "--exact-match", "--tags", "HEAD", check=False)

        if supplied_ref:
            if branch and supplied_ref not in {branch, f"refs/heads/{branch}"}:
                raise RuntimeError(f"Supplied ref {supplied_ref!r} does not match branch {branch!r}")
            if exact_tag and supplied_ref.startswith("refs/tags/") and supplied_ref != f"refs/tags/{exact_tag}":
                raise RuntimeError(f"Supplied ref {supplied_ref!r} does not match tag {exact_tag!r}")
            return supplied_ref
        if exact_tag:
            return f"refs/tags/{exact_tag}"
        if branch:
            return f"refs/heads/{branch}"
        raise RuntimeError("Cannot establish a non-empty source ref for detached HEAD")

    def validate(self, repository: Path) -> None:
        repository = repository.resolve()
        if not self.ref or not self.ref.strip():
            raise RuntimeError("Source ref is missing")
        if not FULL_SHA_PATTERN.fullmatch(self.commit_sha):
            raise RuntimeError("Commit SHA must be the full 40-character lowercase Git SHA")
        if not self.commit_url:
            raise RuntimeError("Commit URL is missing")
        if not self.commit_date:
            raise RuntimeError("Commit date is missing")

        parsed = urlparse(self.commit_url)
        expected_repository = _normalize_repository_url(self.repository_url)
        expected_url = f"{expected_repository}/commit/{self.commit_sha}"
        if parsed.scheme != "https" or self.commit_url != expected_url:
            raise RuntimeError(f"Commit URL must be exactly {expected_url}")
        if expected_repository != CANONICAL_REPOSITORY_URL:
            raise RuntimeError("Build metadata does not identify the canonical KGP repository")

        actual_head = _git(repository, "rev-parse", "HEAD")
        if self.commit_sha != actual_head:
            raise RuntimeError(f"Commit SHA {self.commit_sha} does not match HEAD {actual_head}")
        actual_date = _git(repository, "show", "-s", "--format=%cI", "HEAD")
        if self.commit_date != actual_date:
            raise RuntimeError(f"Commit date {self.commit_date!r} does not match HEAD date {actual_date!r}")
