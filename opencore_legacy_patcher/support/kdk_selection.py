"""Operation-scoped manual Kernel Debug Kit selection models."""

from __future__ import annotations

import re
import packaging.version

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KernelDebugKitCandidate:
    """One immutable official KdkSupportPkg catalog entry."""

    version: str
    build: str
    url: str
    file_size: int

    @classmethod
    def from_catalog_entry(cls, entry: dict) -> KernelDebugKitCandidate:
        return cls(
            version=str(entry["version"]),
            build=str(entry["build"]),
            url=str(entry["url"]),
            file_size=int(entry["fileSize"]),
        )

    def catalog_identity(self) -> tuple[str, str, str, int]:
        return (self.version, self.build, self.url, self.file_size)

    def is_tahoe(self) -> bool:
        try:
            version = packaging.version.parse(self.version)
        except Exception:
            return False
        build_match = re.match(r"^(\d+)", self.build)
        return version.major == 26 and build_match is not None and int(build_match.group(1)) == 25


@dataclass(frozen=True)
class ManualKDKSelectionState:
    """Non-persistent manual mode for one root-patch operation."""

    enabled: bool = False
    candidate: KernelDebugKitCandidate | None = None

    def for_requirement(self, kdk_required: bool) -> ManualKDKSelectionState:
        if kdk_required is False:
            return ManualKDKSelectionState()
        if self.enabled is False:
            return ManualKDKSelectionState()
        return self

    def with_enabled(self, enabled: bool, kdk_required: bool) -> ManualKDKSelectionState:
        if kdk_required is False or enabled is False:
            return ManualKDKSelectionState()
        return ManualKDKSelectionState(enabled=True)

    def with_candidate(self, candidate: KernelDebugKitCandidate) -> ManualKDKSelectionState:
        if self.enabled is False:
            raise ValueError("Manual KDK mode is not enabled")
        return ManualKDKSelectionState(enabled=True, candidate=candidate)


@dataclass(frozen=True)
class KDKCandidateStatus:
    candidate: KernelDebugKitCandidate
    installed_path: Path | None
    automatic_choice: bool
    automatic_exact_match: bool

    @property
    def installed(self) -> bool:
        return self.installed_path is not None


@dataclass(frozen=True)
class KDKSelectionContext:
    """Side-effect-free catalog and existing-resolver preview for the dialog."""

    candidates: tuple[KDKCandidateStatus, ...]
    automatic_candidate: KernelDebugKitCandidate | None
    automatic_exact_match: bool

    @classmethod
    def from_system(cls, global_constants) -> KDKSelectionContext:
        # Local import avoids a model/handler import cycle.
        from . import kdk_handler

        resolver = kdk_handler.KernelDebugKitObject(
            global_constants,
            global_constants.detected_os_build,
            global_constants.detected_os_version,
            ignore_installed=True,
            passive=True,
        )
        catalog = tuple(candidate for candidate in resolver.available_candidates() if candidate.is_tahoe())
        automatic = resolver.resolved_candidate() if resolver.success else None
        if automatic not in catalog:
            automatic = None

        statuses = tuple(
            KDKCandidateStatus(
                candidate=candidate,
                installed_path=resolver.installed_path_for_build(candidate.build),
                automatic_choice=candidate == automatic,
                automatic_exact_match=(candidate == automatic and resolver.kdk_url_is_exactly_match),
            )
            for candidate in catalog
        )

        # KdkSupportPkg already provides canonical version/date ordering. Promote
        # only the existing resolver's choice; preserve every other relative row.
        statuses = tuple(sorted(statuses, key=lambda item: not item.automatic_choice))
        return cls(
            candidates=statuses,
            automatic_candidate=automatic,
            automatic_exact_match=bool(automatic and resolver.kdk_url_is_exactly_match),
        )

    def status_for(self, candidate: KernelDebugKitCandidate) -> KDKCandidateStatus | None:
        return next((status for status in self.candidates if status.candidate == candidate), None)
