"""Fail-closed root-patch state classification shared by UI and operations."""

from __future__ import annotations

import plistlib
import re
import subprocess

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable


ROOT_PATCH_METADATA_FILENAME = "OpenCore-Legacy-Patcher.plist"
ROOT_PATCH_METADATA_DIRECTORY = Path("/System/Library/CoreServices")
ROOT_PATCH_METADATA_PATH = ROOT_PATCH_METADATA_DIRECTORY / ROOT_PATCH_METADATA_FILENAME
ROOT_PATCH_METADATA_SCHEMA = "KGP-Root-Patch-State-v1"
FOREIGN_METADATA_FILENAMES = frozenset({
    "OCLP-R.plist",
    "OCLP-Plus.plist",
    "OCLP-Mod.plist",
})
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class RootPatchState(StrEnum):
    CLEAN = "clean"
    INSTALLED_SAME = "installed-same"
    INSTALLED_DIFFERENT_PATCH_SET = "installed-different-patch-set"
    INSTALLED_DIFFERENT_BUILD = "installed-different-build"
    LEGACY_FOREIGN = "legacy-or-foreign"
    INVALID_UNKNOWN = "invalid-or-unknown"
    REVERT_PENDING = "revert-pending-reboot-required"


class MetadataDiscovery(StrEnum):
    MISSING = "missing"
    CANONICAL = "canonical"
    LEGACY_FOREIGN = "legacy-or-foreign"
    INVALID = "invalid"


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
    revert_applicable: bool
    reason: str
    installed_selection: tuple[str, ...] | None = None

    def revert_allowed(self, can_unpatch: bool) -> bool:
        return self.revert_applicable and can_unpatch


@dataclass(frozen=True)
class MetadataResult:
    discovery: MetadataDiscovery
    data: dict | None
    reason: str
    known_patch_metadata_present: bool


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
        "Commit Date": date,
        "Commit SHA": sha,
        "Commit URL": url,
        "Repository": repository,
        "Project Identity": project,
    }


def read_root_state_evidence() -> RootStateEvidence | None:
    root_result = subprocess.run(
        ["/usr/sbin/diskutil", "info", "-plist", "/"],
        capture_output=True,
    )
    if root_result.returncode != 0:
        return None
    try:
        content = plistlib.loads(root_result.stdout)
        if "Sealed" not in content:
            return None
        return RootStateEvidence(
            apfs_snapshot=content.get("APFSSnapshot") is True,
            seal=str(content["Sealed"]),
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

    def _discover_metadata(self) -> MetadataResult:
        directory = self.metadata_path.parent
        try:
            entries = {entry.name: entry for entry in directory.iterdir() if entry.is_file()}
        except FileNotFoundError:
            return MetadataResult(MetadataDiscovery.MISSING, None, "Metadata directory is missing", False)
        except OSError as error:
            return MetadataResult(MetadataDiscovery.INVALID, None, f"Cannot inspect metadata directory: {error}", False)

        case_candidates = [name for name in entries if name.casefold() == ROOT_PATCH_METADATA_FILENAME.casefold()]
        foreign_candidates = sorted(name for name in entries if name in FOREIGN_METADATA_FILENAMES)
        if len(case_candidates) > 1:
            return MetadataResult(
                MetadataDiscovery.INVALID,
                None,
                f"Ambiguous metadata filenames: {', '.join(sorted(case_candidates))}",
                True,
            )
        if case_candidates and case_candidates[0] != ROOT_PATCH_METADATA_FILENAME:
            return MetadataResult(
                MetadataDiscovery.INVALID,
                None,
                f"Metadata filename capitalization is invalid: {case_candidates[0]}",
                True,
            )
        if case_candidates and foreign_candidates:
            return MetadataResult(
                MetadataDiscovery.INVALID,
                None,
                f"Multiple patch metadata families are present: {', '.join([*case_candidates, *foreign_candidates])}",
                True,
            )
        if not case_candidates:
            if foreign_candidates:
                return MetadataResult(
                    MetadataDiscovery.LEGACY_FOREIGN,
                    None,
                    f"Foreign patch metadata is present: {', '.join(foreign_candidates)}",
                    True,
                )
            return MetadataResult(MetadataDiscovery.MISSING, None, "No root-patch metadata is installed", False)

        try:
            with entries[ROOT_PATCH_METADATA_FILENAME].open("rb") as metadata_file:
                metadata = plistlib.load(metadata_file)
        except (OSError, plistlib.InvalidFileException, ValueError, TypeError) as error:
            return MetadataResult(
                MetadataDiscovery.INVALID,
                None,
                f"Root-patch metadata is unreadable or malformed: {error}",
                True,
            )
        if not isinstance(metadata, dict):
            return MetadataResult(MetadataDiscovery.INVALID, None, "Root-patch metadata is not a dictionary", True)
        return MetadataResult(MetadataDiscovery.CANONICAL, metadata, "Canonical metadata found", True)

    def _result(
        self,
        state: RootPatchState,
        reason: str,
        *,
        revert_applicable: bool = False,
        installed_selection: tuple[str, ...] | None = None,
    ) -> RootPatchStateResult:
        return RootPatchStateResult(
            state=state,
            patch_allowed=state == RootPatchState.CLEAN,
            revert_applicable=revert_applicable,
            reason=reason,
            installed_selection=installed_selection,
        )

    def evaluate(self, requested_patches: dict) -> RootPatchStateResult:
        evidence = self.evidence_reader()
        metadata = self._discover_metadata()

        if getattr(self.constants, "root_patcher_revert_pending", False) is True:
            return self._result(
                RootPatchState.REVERT_PENDING,
                "Root patch reversion succeeded; reboot into the restored sealed snapshot before patching again",
            )

        if evidence is None:
            return self._result(RootPatchState.INVALID_UNKNOWN, "Root snapshot and seal state could not be read")

        safe_known_revert = evidence.patched and metadata.known_patch_metadata_present

        if metadata.discovery == MetadataDiscovery.INVALID:
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                metadata.reason,
                revert_applicable=safe_known_revert,
            )
        if metadata.discovery == MetadataDiscovery.LEGACY_FOREIGN:
            return self._result(
                RootPatchState.LEGACY_FOREIGN,
                f"{metadata.reason}; revert existing patches, reboot, then patch with this build",
                revert_applicable=safe_known_revert,
            )
        if metadata.discovery == MetadataDiscovery.MISSING:
            if evidence.clean:
                return self._result(RootPatchState.CLEAN, "Root volume is clean and sealed")
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "No trusted patch metadata exists, but the active root is not a clean sealed snapshot",
            )

        installed = metadata.data
        if evidence.patched is False:
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "Installed patch metadata contradicts the active root snapshot/seal state",
                revert_applicable=False,
            )

        if installed.get("Metadata Schema") != ROOT_PATCH_METADATA_SCHEMA:
            return self._result(
                RootPatchState.LEGACY_FOREIGN,
                "Installed metadata predates or does not implement the KGP v2.0 exact-build schema; revert, reboot, then repatch",
                revert_applicable=True,
            )

        identity = current_build_identity(self.constants)
        if identity is None:
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "The running application has no trustworthy exact build identity",
                revert_applicable=True,
            )

        installed_selection = installed.get("Installed Patches")
        if not isinstance(installed_selection, list) or not all(isinstance(item, str) for item in installed_selection):
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "Installed metadata has no structurally valid patch selection",
                revert_applicable=True,
            )
        if len(installed_selection) != len(set(installed_selection)):
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "Installed metadata contains duplicate patch identifiers",
                revert_applicable=True,
            )

        required_identity_keys = set(identity)
        if any(key not in installed or not isinstance(installed[key], str) or not installed[key] for key in required_identity_keys):
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "Installed exact-build metadata is incomplete",
                revert_applicable=True,
            )
        if installed["Project Identity"] != identity["Project Identity"] or installed["Repository"] != identity["Repository"]:
            return self._result(
                RootPatchState.LEGACY_FOREIGN,
                "Installed metadata belongs to a different project or repository; revert, reboot, then patch with KGP v2.0",
                revert_applicable=True,
            )
        installed_sha = installed["Commit SHA"]
        if not FULL_SHA_PATTERN.fullmatch(installed_sha):
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "Installed metadata does not contain a full 40-character commit SHA",
                revert_applicable=True,
            )
        if installed["Commit URL"] != f"{installed['Repository'].rstrip('/')}/commit/{installed_sha}":
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "Installed commit URL and SHA are contradictory",
                revert_applicable=True,
            )

        if any(installed[key] != value for key, value in identity.items()):
            return self._result(
                RootPatchState.INSTALLED_DIFFERENT_BUILD,
                "Installed root patches were produced by a different exact build; revert, reboot, then repatch",
                revert_applicable=True,
                installed_selection=tuple(sorted(installed_selection)),
            )

        expected_selection = semantic_patch_selection(requested_patches)
        if tuple(sorted(installed_selection)) != expected_selection:
            return self._result(
                RootPatchState.INSTALLED_DIFFERENT_PATCH_SET,
                "Installed and requested patch selections differ; revert, reboot, then apply the requested selection",
                revert_applicable=True,
                installed_selection=tuple(sorted(installed_selection)),
            )

        return self._result(
            RootPatchState.INSTALLED_SAME,
            "The requested root patches from this exact build are already installed",
            revert_applicable=True,
            installed_selection=tuple(sorted(installed_selection)),
        )
