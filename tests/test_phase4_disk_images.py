"""Phase 4 disk-image creation contract tests."""

import subprocess
import unittest

from pathlib import Path
from unittest import mock

from ci_tooling.build_modules import disk_images


class Phase4DiskImageTests(unittest.TestCase):
    def test_payload_image_uses_apfs_without_changing_container_contract(self) -> None:
        generator = disk_images.GenerateDiskImages(reset_dmg_cache=False)

        with mock.patch.object(Path, "exists", return_value=False), \
             mock.patch.object(disk_images.subprocess_wrapper, "run_and_verify") as run_and_verify:
            generator._generate_payloads_dmg()

        run_and_verify.assert_called_once_with(
            [
                "/usr/bin/hdiutil", "create", "./payloads.dmg",
                "-megabytes", "32000",
                "-format", "UDZO", "-ov",
                "-volname", "OpenCore Patcher Resources (Base)",
                "-fs", "APFS",
                "-layout", "NONE",
                "-srcfolder", "./payloads",
                "-passphrase", "password", "-encryption",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


if __name__ == "__main__":
    unittest.main()
