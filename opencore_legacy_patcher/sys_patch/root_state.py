"""Minimal, testable root-patch state checks shared by UI and patch execution."""

from __future__ import annotations

import plistlib
import re
import subprocess

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable


ROOT_PATCH_METADATA_FILENAME = "OpenCore-Legacy-Patcher.plist"
ROOT_PATCH_METADATA_PATH = Path("/System/Library/CoreServices") / ROOT_PATCH_METADATA_FILENAME
ROOT_PATCH_METADATA_SCHEMA = "KGP-Root-Patch-State-v1"
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class RootPatchState(StrEnum):
    CLEAN = "clean"
    INSTALLED_SAME = "installed-same"
    NOT_SAME = "not-same"


@dataclass(frozen=True)
class RootStateEvidence:
    apfs_snapshot: bool
    seal: str

    @property
    def clean(self) -> bool:
        return self.apfs_snapshot and self.seal.lower() in {"yes", "sealed"}

    @property
    def patched(self) -> bool:
        return self.apfs_snapshot and self.seal.lower() == "broken"


@dataclass(frozen=True)
class RootPatchStateResult:
    state: RootPatchState
    patch_allowed: bool
    reason: str


def semantic_patch_selection(patches: dict) -> tuple[str, ...]:
    """Return stable patch identifiers independent of dictionary insertion order."""
    return tuple(sorted(str(key) for key in patches))


def current_build_identity(global_constants) -> dict | None:
    commit_info = global_constants.commit_info
    if not isinstance(commit_info, tuple) or len(commit_info) < 6:
        return None
    ref, date, url, sha, repository, project = commit_info[:6]
    if not all(isinstance(value, str) and value for value in (ref, date, url, sha, repository, project)):
        return None
    if not FULL_SHA_PATTERN.fullmatch(sha):
        return None
    if url != f"{repository.rstrip('/')}/commit/{sha}":
        return None
    return {
        "Commit Ref": ref,
        "Commit SHA": sha,
        "Commit URL": url,
        "Repository": repository,
        "Project Identity": project,
    }


def read_root_state_evidence() -> RootStateEvidence | None:
    result = subprocess.run(
        ["/usr/sbin/diskutil", "info", "-plist", "/"],
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    try:
        content = plistlib.loads(result.stdout)
        return RootStateEvidence(
            apfs_snapshot=content.get("APFSSnapshot") is True,
            seal=str(content.get("Sealed", "")),
        )
    except (plistlib.InvalidFileException, TypeError, ValueError):
        return None


class RootPatchStateEvaluator:
    def __init__(
        self,
        global_constants,
        *,
        metadata_path: Path = ROOT_PATCH_METADATA_PATH,
        evidence_reader: Callable[[], RootStateEvidence | None] = read_root_state_evidence,
    ) -> None:
        self.constants = global_constants
        self.metadata_path = metadata_path
        self.evidence_reader = evidence_reader

    def evaluate(self, requested_patches: dict) -> RootPatchStateResult:
        evidence = self.evidence_reader()
        if not self.metadata_path.exists():
            if evidence is not None and evidence.clean:
                return RootPatchStateResult(RootPatchState.CLEAN, True, "Root volume is clean and sealed")
            return RootPatchStateResult(RootPatchState.NOT_SAME, True, "No identical installed patch state was proven")

        try:
            with self.metadata_path.open("rb") as metadata_file:
                metadata = plistlib.load(metadata_file)
        except (OSError, plistlib.InvalidFileException, ValueError, TypeError):
            return RootPatchStateResult(RootPatchState.NOT_SAME, True, "Installed metadata is not structurally valid")

        identity = current_build_identity(self.constants)
        expected_selection = semantic_patch_selection(requested_patches)
        installed_selection = metadata.get("Installed Patches")
        if not isinstance(installed_selection, list) or not all(isinstance(item, str) for item in installed_selection):
            return RootPatchStateResult(RootPatchState.NOT_SAME, True, "Installed patch selection is incomplete")

        identity_matches = identity is not None and all(metadata.get(key) == value for key, value in identity.items())
        schema_matches = metadata.get("Metadata Schema") == ROOT_PATCH_METADATA_SCHEMA
        selection_matches = tuple(sorted(installed_selection)) == expected_selection
        root_matches = evidence is not None and evidence.patched
        if identity_matches and schema_matches and selection_matches and root_matches:
            return RootPatchStateResult(
                RootPatchState.INSTALLED_SAME,
                False,
                "The requested root patches from this exact build are already installed",
            )
        return RootPatchStateResult(RootPatchState.NOT_SAME, True, "Installed state does not exactly match this build and selection")
