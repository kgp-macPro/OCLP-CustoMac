"""Shared noninteractive mounting for OCLP's protected resource images."""

import subprocess

from pathlib import Path

from . import subprocess_wrapper


PROTECTED_DISK_IMAGE_PASSWORD = b"password"


def attach_protected_disk_image(
    image_path: Path,
    mountpoint: Path,
    shadow_path: Path,
) -> subprocess.CompletedProcess:
    """Attach a protected resource image without DiskImages authentication UI."""
    return subprocess_wrapper.run(
        [
            "/usr/bin/hdiutil", "attach", "-noverify", str(image_path),
            "-mountpoint", mountpoint,
            "-nobrowse",
            "-shadow", shadow_path,
            "-stdinpass",
        ],
        input=PROTECTED_DISK_IMAGE_PASSWORD,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
