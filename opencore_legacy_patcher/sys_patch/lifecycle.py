"""Boot-session-bound lifecycle evidence for root-patch transactions."""

from __future__ import annotations

import hashlib
import logging
import plistlib
import subprocess

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Callable

from ..support import subprocess_wrapper


ROOT_PATCH_LIFECYCLE_FILENAME = "OpenCore-Legacy-Patcher-Lifecycle.plist"
ROOT_PATCH_LIFECYCLE_PATH = Path("/Library/Application Support/Dortania") / ROOT_PATCH_LIFECYCLE_FILENAME
ROOT_PATCH_LIFECYCLE_SCHEMA = "KGP-Root-Patch-Lifecycle-v1"


class RootPatchLifecycleState(StrEnum):
    PATCH_IN_PROGRESS = "PATCH_IN_PROGRESS"
    PATCH_FAILED_RECOVERY_REQUIRED = "PATCH_FAILED_RECOVERY_REQUIRED"
    PATCH_PENDING_REBOOT = "PATCH_PENDING_REBOOT"
    REVERT_PENDING = "REVERT_PENDING"


class LifecycleDiscovery(StrEnum):
    MISSING = "missing"
    STALE = "stale-after-reboot"
    VALID = "valid"
    INVALID = "invalid"


@dataclass(frozen=True)
class RootPatchLifecycleRecord:
    state: RootPatchLifecycleState
    boot_session_uuid: str
    installed_metadata: dict


@dataclass(frozen=True)
class LifecycleReadResult:
    discovery: LifecycleDiscovery
    record: RootPatchLifecycleRecord | None
    reason: str


def read_boot_session_uuid() -> str | None:
    """Return the current kernel boot-session UUID without mutating system state."""
    result = subprocess.run(
        ["/usr/sbin/sysctl", "-n", "kern.bootsessionuuid"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    boot_session_uuid = result.stdout.strip().lower()
    return boot_session_uuid or None


def _metadata_sha256(metadata: dict) -> str:
    normalized = plistlib.dumps(metadata, fmt=plistlib.FMT_XML, sort_keys=True)
    return hashlib.sha256(normalized).hexdigest()


class RootPatchLifecycleStore:
    """Read and atomically write root-owned, boot-scoped lifecycle evidence."""

    def __init__(
        self,
        global_constants,
        *,
        path: Path = ROOT_PATCH_LIFECYCLE_PATH,
        boot_session_reader: Callable[[], str | None] = read_boot_session_uuid,
        writer: Callable[[Path, bytes], bool] | None = None,
    ) -> None:
        self.constants = global_constants
        self.path = path
        self.boot_session_reader = boot_session_reader
        self.writer = writer

    def read(self) -> LifecycleReadResult:
        try:
            with self.path.open("rb") as lifecycle_file:
                data = plistlib.load(lifecycle_file)
        except FileNotFoundError:
            return LifecycleReadResult(LifecycleDiscovery.MISSING, None, "No pending root-patch lifecycle record")
        except (OSError, plistlib.InvalidFileException, TypeError, ValueError) as error:
            return LifecycleReadResult(LifecycleDiscovery.INVALID, None, f"Pending lifecycle record is unreadable: {error}")

        if not isinstance(data, dict) or data.get("Lifecycle Schema") != ROOT_PATCH_LIFECYCLE_SCHEMA:
            return LifecycleReadResult(LifecycleDiscovery.INVALID, None, "Pending lifecycle schema is invalid")
        recorded_boot = data.get("Boot Session UUID")
        if not isinstance(recorded_boot, str) or not recorded_boot:
            return LifecycleReadResult(LifecycleDiscovery.INVALID, None, "Pending lifecycle boot identity is missing")
        current_boot = self.boot_session_reader()
        if not isinstance(current_boot, str) or not current_boot:
            return LifecycleReadResult(LifecycleDiscovery.INVALID, None, "Current boot-session identity cannot be established")
        if recorded_boot.lower() != current_boot.lower():
            return LifecycleReadResult(LifecycleDiscovery.STALE, None, "Pending lifecycle record belongs to an earlier boot")

        try:
            state = RootPatchLifecycleState(data.get("State"))
        except (TypeError, ValueError):
            return LifecycleReadResult(LifecycleDiscovery.INVALID, None, "Pending lifecycle state is invalid")
        metadata = data.get("Installed Metadata")
        metadata_hash = data.get("Installed Metadata SHA-256")
        if not isinstance(metadata, dict) or not isinstance(metadata_hash, str):
            return LifecycleReadResult(LifecycleDiscovery.INVALID, None, "Pending lifecycle metadata is missing")
        if _metadata_sha256(metadata) != metadata_hash:
            return LifecycleReadResult(LifecycleDiscovery.INVALID, None, "Pending lifecycle metadata hash is invalid")

        return LifecycleReadResult(
            LifecycleDiscovery.VALID,
            RootPatchLifecycleRecord(state, recorded_boot.lower(), metadata),
            "Trusted pending root-patch lifecycle record found",
        )

    def write(self, state: RootPatchLifecycleState, installed_metadata: dict) -> bool:
        boot_session_uuid = self.boot_session_reader()
        if not isinstance(boot_session_uuid, str) or not boot_session_uuid:
            logging.error("- Cannot record pending root-patch lifecycle without a boot-session identity")
            return False
        if not isinstance(installed_metadata, dict):
            logging.error("- Cannot record pending root-patch lifecycle without installed operation metadata")
            return False

        data = {
            "Lifecycle Schema": ROOT_PATCH_LIFECYCLE_SCHEMA,
            "State": state.value,
            "Boot Session UUID": boot_session_uuid.lower(),
            "Installed Metadata SHA-256": _metadata_sha256(installed_metadata),
            "Installed Metadata": installed_metadata,
        }
        payload = plistlib.dumps(data, fmt=plistlib.FMT_XML, sort_keys=False)
        if self.writer is not None:
            return bool(self.writer(self.path, payload))

        local_path = Path(self.constants.payload_path) / ROOT_PATCH_LIFECYCLE_FILENAME
        destination_temporary = self.path.with_name(f".{self.path.name}.tmp")
        try:
            local_path.write_bytes(payload)
            subprocess_wrapper.run_as_root_and_verify(["/bin/mkdir", "-p", str(self.path.parent)])
            subprocess_wrapper.run_as_root_and_verify(["/bin/cp", "-f", str(local_path), str(destination_temporary)])
            subprocess_wrapper.run_as_root_and_verify(["/bin/chmod", "0644", str(destination_temporary)])
            subprocess_wrapper.run_as_root_and_verify(["/bin/mv", "-f", str(destination_temporary), str(self.path)])
        except Exception as error:
            logging.error(f"- Failed to record pending root-patch lifecycle: {error}")
            return False
        finally:
            try:
                local_path.unlink()
            except FileNotFoundError:
                pass
        return self.read().discovery == LifecycleDiscovery.VALID
