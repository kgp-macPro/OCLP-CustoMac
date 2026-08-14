"""Fail-closed root-patch state classification shared by UI and operations."""

from __future__ import annotations

import plistlib
import re
import subprocess

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable

from ..support.kdk_selection import KDKSelectionMode, KernelDebugKitIdentity
from .lifecycle import (
    LifecycleDiscovery,
    ROOT_PATCH_LIFECYCLE_FILENAME,
    RootPatchLifecycleState,
    RootPatchLifecycleStore,
)


ROOT_PATCH_METADATA_FILENAME = "OpenCore-Legacy-Patcher.plist"
ROOT_PATCH_METADATA_DIRECTORY = Path("/System/Library/CoreServices")
ROOT_PATCH_METADATA_PATH = ROOT_PATCH_METADATA_DIRECTORY / ROOT_PATCH_METADATA_FILENAME
ROOT_PATCH_METADATA_SCHEMA = "KGP-Root-Patch-State-v1"
KDK_SELECTION_MODE_METADATA_KEY = "Kernel Debug Kit Selection Mode"
KDK_IDENTITY_METADATA_KEY = "Kernel Debug Kit Identity"
FOREIGN_METADATA_IDENTITIES = {
    "OCLP-R.plist": "OCLP-R",
    "OCLP-Plus.plist": "OCLP-Plus",
    "OCLP-Mod.plist": "OCLP-Mod",
    "oclp-mod.plist": "OCLP-Mod",
}
FOREIGN_METADATA_FILENAMES = frozenset(FOREIGN_METADATA_IDENTITIES)
FULL_SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class RootPatchState(StrEnum):
    CLEAN = "clean"
    PATCH_IN_PROGRESS = "patch-in-progress"
    PATCH_FAILED_RECOVERY_REQUIRED = "patch-failed-recovery-required"
    PATCH_PENDING_REBOOT = "patch-pending-reboot-required"
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
        return self.apfs_snapshot and self.seal.lower() in {"yes", "sealed", "true"}

    @property
    def patched(self) -> bool:
        return self.apfs_snapshot and self.seal.lower() in {"broken", "no", "unsealed", "false"}

@dataclass(frozen=True)
class RootPatchStateResult:
    state: RootPatchState
    patch_allowed: bool
    revert_applicable: bool
    reason: str
    installed_selection: tuple[str, ...] | None = None
    installed_kdk_selection_mode: KDKSelectionMode | None = None
    installed_kdk_identity: KernelDebugKitIdentity | None = None

    @property
    def patch_authorized(self) -> bool:
        """Root-state authorization, independent of GUI selection prerequisites."""
        return self.patch_allowed

    @property
    def recovery_authorized(self) -> bool:
        """Evidence-backed recovery authorization, independent of SIP execution prerequisites."""
        return self.revert_applicable

    def revert_allowed(self, can_unpatch: bool) -> bool:
        """Whether recovery is both authorized by state and currently executable."""
        return self.recovery_authorized and can_unpatch


@dataclass(frozen=True)
class MetadataResult:
    discovery: MetadataDiscovery
    data: dict | None
    reason: str
    recovery_evidence_present: bool


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


def installed_kdk_provenance(metadata: dict) -> tuple[KDKSelectionMode | None, KernelDebugKitIdentity | None]:
    """Read optional historical KDK provenance without guessing for older metadata."""
    try:
        mode = KDKSelectionMode(metadata.get(KDK_SELECTION_MODE_METADATA_KEY))
    except (TypeError, ValueError):
        return None, None
    identity = KernelDebugKitIdentity.from_metadata(metadata.get(KDK_IDENTITY_METADATA_KEY))
    if identity is None:
        return None, None
    return mode, identity


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
        lifecycle_store: RootPatchLifecycleStore | None = None,
    ) -> None:
        self.constants = global_constants
        self.metadata_path = metadata_path
        self.evidence_reader = evidence_reader
        lifecycle_path = None
        if metadata_path != ROOT_PATCH_METADATA_PATH:
            lifecycle_path = metadata_path.parent / ROOT_PATCH_LIFECYCLE_FILENAME
        self.lifecycle_store = lifecycle_store or RootPatchLifecycleStore(
            global_constants,
            **({"path": lifecycle_path} if lifecycle_path is not None else {}),
        )

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
                False,
            )
        if case_candidates and case_candidates[0] != ROOT_PATCH_METADATA_FILENAME:
            return MetadataResult(
                MetadataDiscovery.INVALID,
                None,
                f"Metadata filename capitalization is invalid: {case_candidates[0]}",
                False,
            )
        if case_candidates and foreign_candidates:
            return MetadataResult(
                MetadataDiscovery.INVALID,
                None,
                f"Multiple patch metadata families are present: {', '.join([*case_candidates, *foreign_candidates])}",
                False,
            )
        if not case_candidates:
            if foreign_candidates:
                if len(foreign_candidates) > 1:
                    return MetadataResult(
                        MetadataDiscovery.INVALID,
                        None,
                        f"Multiple foreign patch metadata families are present: {', '.join(foreign_candidates)}",
                        False,
                    )
                foreign_name = foreign_candidates[0]
                try:
                    with entries[foreign_name].open("rb") as metadata_file:
                        foreign_metadata = plistlib.load(metadata_file)
                except (OSError, plistlib.InvalidFileException, ValueError, TypeError) as error:
                    return MetadataResult(
                        MetadataDiscovery.INVALID,
                        None,
                        f"Recognized foreign patch metadata is unreadable or malformed: {error}",
                        False,
                    )
                expected_identity = FOREIGN_METADATA_IDENTITIES[foreign_name]
                if not isinstance(foreign_metadata, dict) or not isinstance(
                    foreign_metadata.get(expected_identity),
                    str,
                ) or not foreign_metadata[expected_identity].strip():
                    return MetadataResult(
                        MetadataDiscovery.INVALID,
                        None,
                        f"Recognized foreign patch metadata does not contain a valid {expected_identity} identity",
                        False,
                    )
                return MetadataResult(
                    MetadataDiscovery.LEGACY_FOREIGN,
                    foreign_metadata,
                    f"Recognized OCLP-family patch metadata is present: {foreign_name}",
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
                False,
            )
        if not isinstance(metadata, dict):
            return MetadataResult(MetadataDiscovery.INVALID, None, "Root-patch metadata is not a dictionary", False)
        is_current_schema = metadata.get("Metadata Schema") == ROOT_PATCH_METADATA_SCHEMA
        legacy_identity = metadata.get("OpenCore Legacy Patcher")
        if is_current_schema is False and (
            not isinstance(legacy_identity, str) or not legacy_identity.strip()
        ):
            return MetadataResult(
                MetadataDiscovery.INVALID,
                None,
                "Canonical metadata does not contain a recognized OCLP-family identity",
                False,
            )
        return MetadataResult(MetadataDiscovery.CANONICAL, metadata, "Canonical metadata found", True)

    def _result(
        self,
        state: RootPatchState,
        reason: str,
        *,
        installed_selection: tuple[str, ...] | None = None,
        installed_kdk_selection_mode: KDKSelectionMode | None = None,
        installed_kdk_identity: KernelDebugKitIdentity | None = None,
    ) -> RootPatchStateResult:
        return RootPatchStateResult(
            state=state,
            patch_allowed=state == RootPatchState.CLEAN,
            # Recovery authorization follows root state, never patch/KDK/build
            # ownership.  REVERT_PENDING has already completed the destructive
            # operation and only permits reboot, so a second revert is blocked.
            revert_applicable=state not in {RootPatchState.CLEAN, RootPatchState.REVERT_PENDING},
            reason=reason,
            installed_selection=installed_selection,
            installed_kdk_selection_mode=installed_kdk_selection_mode,
            installed_kdk_identity=installed_kdk_identity,
        )

    def _trusted_installed_history(
        self,
        metadata: MetadataResult,
    ) -> tuple[tuple[str, ...] | None, KDKSelectionMode | None, KernelDebugKitIdentity | None]:
        """Return display-only history from structurally valid KGP metadata."""
        if metadata.discovery != MetadataDiscovery.CANONICAL or not isinstance(metadata.data, dict):
            return None, None, None
        installed = metadata.data
        if installed.get("Metadata Schema") != ROOT_PATCH_METADATA_SCHEMA:
            return None, None, None
        identity = current_build_identity(self.constants)
        if identity is None:
            return None, None, None
        if any(
            key not in installed or not isinstance(installed[key], str) or not installed[key]
            for key in identity
        ):
            return None, None, None
        if installed.get("Project Identity") != identity["Project Identity"]:
            return None, None, None
        if installed.get("Repository") != identity["Repository"]:
            return None, None, None
        selection = installed.get("Installed Patches")
        if not isinstance(selection, list) or not all(isinstance(item, str) for item in selection):
            return None, None, None
        if len(selection) != len(set(selection)):
            return None, None, None
        installed_sha = installed.get("Commit SHA")
        installed_url = installed.get("Commit URL")
        if not isinstance(installed_sha, str) or not FULL_SHA_PATTERN.fullmatch(installed_sha):
            return None, None, None
        if installed_url != f"{identity['Repository'].rstrip('/')}/commit/{installed_sha}":
            return None, None, None
        mode, kdk_identity = installed_kdk_provenance(installed)
        return tuple(sorted(selection)), mode, kdk_identity

    def _pending_lifecycle_result(
        self,
        lifecycle_state: RootPatchLifecycleState,
        installed_metadata: dict | None,
    ) -> RootPatchStateResult:
        metadata = MetadataResult(
            MetadataDiscovery.CANONICAL,
            installed_metadata if isinstance(installed_metadata, dict) else None,
            "Pending operation metadata",
            True,
        )
        installed_selection, kdk_mode, kdk_identity = self._trusted_installed_history(metadata)
        if lifecycle_state == RootPatchLifecycleState.REVERT_PENDING:
            return self._result(
                RootPatchState.REVERT_PENDING,
                "Root patch reversion succeeded; reboot into the restored sealed snapshot before patching again",
                installed_selection=installed_selection,
                installed_kdk_selection_mode=kdk_mode,
                installed_kdk_identity=kdk_identity,
            )
        if lifecycle_state == RootPatchLifecycleState.PATCH_IN_PROGRESS:
            return self._result(
                RootPatchState.PATCH_IN_PROGRESS,
                "Root patching crossed the root-mutation boundary and did not complete; revert to the last sealed snapshot before patching again",
                installed_selection=installed_selection,
                installed_kdk_selection_mode=kdk_mode,
                installed_kdk_identity=kdk_identity,
            )
        if lifecycle_state == RootPatchLifecycleState.PATCH_FAILED_RECOVERY_REQUIRED:
            return self._result(
                RootPatchState.PATCH_FAILED_RECOVERY_REQUIRED,
                "Root patching failed after root mutation began; revert to the last sealed snapshot before patching again",
                installed_selection=installed_selection,
                installed_kdk_selection_mode=kdk_mode,
                installed_kdk_identity=kdk_identity,
            )
        if installed_selection is None:
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "A completed root-patch lifecycle is pending reboot, but its installed operation metadata is not trustworthy",
            )
        return self._result(
            RootPatchState.PATCH_PENDING_REBOOT,
            "Root patching completed successfully; reboot to use the new patched snapshot, or revert before rebooting",
            installed_selection=installed_selection,
            installed_kdk_selection_mode=kdk_mode,
            installed_kdk_identity=kdk_identity,
        )

    def evaluate(self, requested_patches: dict) -> RootPatchStateResult:
        evidence = self.evidence_reader()
        metadata = self._discover_metadata()

        if getattr(self.constants, "root_patcher_revert_pending", False) is True:
            pending_metadata = getattr(self.constants, "root_patcher_pending_metadata", None)
            if not isinstance(pending_metadata, dict) and metadata.discovery == MetadataDiscovery.CANONICAL:
                pending_metadata = metadata.data
            if not isinstance(pending_metadata, dict):
                return self._result(
                    RootPatchState.REVERT_PENDING,
                    "Root patch reversion succeeded; reboot into the restored sealed snapshot before patching again",
                )
            return self._pending_lifecycle_result(
                RootPatchLifecycleState.REVERT_PENDING,
                pending_metadata,
            )
        if getattr(self.constants, "root_patcher_patch_pending", False) is True:
            pending_metadata = getattr(self.constants, "root_patcher_pending_metadata", None)
            if not isinstance(pending_metadata, dict):
                return self._result(
                    RootPatchState.PATCH_PENDING_REBOOT,
                    "Root patching completed successfully; reboot to use the new patched snapshot, or revert before rebooting",
                )
            return self._pending_lifecycle_result(
                RootPatchLifecycleState.PATCH_PENDING_REBOOT,
                pending_metadata,
            )

        lifecycle = self.lifecycle_store.read()
        if lifecycle.discovery == LifecycleDiscovery.INVALID:
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                lifecycle.reason,
            )
        if lifecycle.discovery == LifecycleDiscovery.VALID:
            return self._pending_lifecycle_result(
                lifecycle.record.state,
                lifecycle.record.installed_metadata,
            )

        if evidence is None:
            return self._result(RootPatchState.INVALID_UNKNOWN, "Root snapshot and seal state could not be read")

        if metadata.discovery == MetadataDiscovery.INVALID:
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                metadata.reason,
            )
        if metadata.discovery == MetadataDiscovery.LEGACY_FOREIGN:
            return self._result(
                RootPatchState.LEGACY_FOREIGN,
                f"{metadata.reason}; revert existing patches, reboot, then patch with this build",
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
            )

        if installed.get("Metadata Schema") != ROOT_PATCH_METADATA_SCHEMA:
            return self._result(
                RootPatchState.LEGACY_FOREIGN,
                "Installed metadata predates or does not implement the KGP v2.0 exact-build schema; revert, reboot, then repatch",
            )

        identity = current_build_identity(self.constants)
        if identity is None:
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "The running application has no trustworthy exact build identity",
            )

        installed_selection = installed.get("Installed Patches")
        if not isinstance(installed_selection, list) or not all(isinstance(item, str) for item in installed_selection):
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "Installed metadata has no structurally valid patch selection",
            )
        if len(installed_selection) != len(set(installed_selection)):
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "Installed metadata contains duplicate patch identifiers",
            )

        required_identity_keys = set(identity)
        if any(key not in installed or not isinstance(installed[key], str) or not installed[key] for key in required_identity_keys):
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "Installed exact-build metadata is incomplete",
            )
        if installed["Project Identity"] != identity["Project Identity"] or installed["Repository"] != identity["Repository"]:
            return self._result(
                RootPatchState.LEGACY_FOREIGN,
                "Installed metadata belongs to a different project or repository; revert, reboot, then patch with KGP v2.0",
            )
        installed_sha = installed["Commit SHA"]
        if not FULL_SHA_PATTERN.fullmatch(installed_sha):
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "Installed metadata does not contain a full 40-character commit SHA",
            )
        if installed["Commit URL"] != f"{installed['Repository'].rstrip('/')}/commit/{installed_sha}":
            return self._result(
                RootPatchState.INVALID_UNKNOWN,
                "Installed commit URL and SHA are contradictory",
            )

        installed_kdk_mode, installed_kdk_identity = installed_kdk_provenance(installed)

        if any(installed[key] != value for key, value in identity.items()):
            return self._result(
                RootPatchState.INSTALLED_DIFFERENT_BUILD,
                "Installed root patches were produced by a different exact build; revert, reboot, then repatch",
                installed_selection=tuple(sorted(installed_selection)),
                installed_kdk_selection_mode=installed_kdk_mode,
                installed_kdk_identity=installed_kdk_identity,
            )

        expected_selection = semantic_patch_selection(requested_patches)
        if tuple(sorted(installed_selection)) != expected_selection:
            return self._result(
                RootPatchState.INSTALLED_DIFFERENT_PATCH_SET,
                "Installed and requested patch selections differ; revert, reboot, then apply the requested selection",
                installed_selection=tuple(sorted(installed_selection)),
                installed_kdk_selection_mode=installed_kdk_mode,
                installed_kdk_identity=installed_kdk_identity,
            )

        return self._result(
            RootPatchState.INSTALLED_SAME,
            "The requested root patches from this exact build are already installed",
            installed_selection=tuple(sorted(installed_selection)),
            installed_kdk_selection_mode=installed_kdk_mode,
            installed_kdk_identity=installed_kdk_identity,
        )
