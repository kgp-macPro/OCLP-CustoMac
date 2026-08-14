
import logging
import subprocess
import plistlib

from pathlib import Path

from ... import constants

from ...datasets import os_data
from ...support import subprocess_wrapper, kdk_handler
from ...support.kdk_selection import KernelDebugKitCandidate
from ...volume import generate_copy_arguments
from ..root_state import ROOT_PATCH_METADATA_PATH


class KernelDebugKitMerge:

    def __init__(
        self,
        global_constants: constants.Constants,
        mount_location: str,
        skip_root_kmutil_requirement: bool,
        manual_kdk_candidate: KernelDebugKitCandidate = None,
    ) -> None:
        self.constants: constants.Constants = global_constants
        self.mount_location = mount_location
        self.skip_root_kmutil_requirement = skip_root_kmutil_requirement
        self.manual_kdk_candidate = manual_kdk_candidate


    def _kdk_object(self) -> kdk_handler.KernelDebugKitObject:
        return kdk_handler.KernelDebugKitObject(
            self.constants,
            self.constants.detected_os_build,
            self.constants.detected_os_version,
            selected_candidate=self.manual_kdk_candidate,
        )


    def _manual_download_matches_selection(self) -> bool:
        if self.manual_kdk_candidate is None:
            return True
        info_path = self.constants.kdk_download_path.parent / kdk_handler.KDK_INFO_PLIST
        try:
            with info_path.open("rb") as info_file:
                info = plistlib.load(info_file)
        except (FileNotFoundError, OSError, plistlib.InvalidFileException):
            return False
        return (
            info.get("build") == self.manual_kdk_candidate.build
            and info.get("version") == self.manual_kdk_candidate.version
        )


    def _matching_kdk_already_merged(self, kdk_path: str) -> bool:
        """
        Check whether the KDK is already merged with the root volume
        """
        oclp_plist = ROOT_PATCH_METADATA_PATH
        if not oclp_plist.exists():
            return False

        if not (Path(self.mount_location) / Path("System/Library/Extensions/System.kext/PlugIns/Libkern.kext/Libkern")).exists():
            return False

        try:
            oclp_plist_data = plistlib.load(open(oclp_plist, "rb"))
            if "Kernel Debug Kit Used" not in oclp_plist_data:
                return False
            if oclp_plist_data["Kernel Debug Kit Used"] == str(kdk_path):
                logging.info("- Matching KDK determined to already be merged, skipping")
                return True
        except:
            pass

        return False


    def _backup_hid_cs(self) -> None:
        """
        Due to some IOHIDFamily oddities, we need to ensure their CodeSignature is retained
        """
        cs_path = Path(self.mount_location) / Path("System/Library/Extensions/IOHIDFamily.kext/Contents/PlugIns/IOHIDEventDriver.kext/Contents/_CodeSignature")
        if not cs_path.exists():
            return

        logging.info("- Backing up IOHIDEventDriver CodeSignature")
        subprocess_wrapper.run_as_root(generate_copy_arguments(cs_path, f"{self.constants.payload_path}/IOHIDEventDriver_CodeSignature.bak"), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


    def _restore_hid_cs(self) -> None:
        """
        Restore IOHIDEventDriver CodeSignature
        """
        if not Path(f"{self.constants.payload_path}/IOHIDEventDriver_CodeSignature.bak").exists():
            return

        logging.info("- Restoring IOHIDEventDriver CodeSignature")
        cs_path = Path(self.mount_location) / Path("System/Library/Extensions/IOHIDFamily.kext/Contents/PlugIns/IOHIDEventDriver.kext/Contents/_CodeSignature")
        if not cs_path.exists():
            logging.info("  - CodeSignature folder missing, creating")
            subprocess_wrapper.run_as_root(["/bin/mkdir", "-p", cs_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        subprocess_wrapper.run_as_root(generate_copy_arguments(f"{self.constants.payload_path}/IOHIDEventDriver_CodeSignature.bak", cs_path), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        subprocess_wrapper.run_as_root(["/bin/rm", "-rf", f"{self.constants.payload_path}/IOHIDEventDriver_CodeSignature.bak"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


    def _merge_kdk(self, kdk_path: str) -> None:
        """
        Merge Kernel Debug Kit (KDK) with the root volume
        """
        logging.info(f"- Merging KDK with Root Volume: {Path(kdk_path).name}")
        subprocess_wrapper.run_as_root(
            # Only merge '/System/Library/Extensions'
            # 'Kernels' and 'KernelSupport' is wasted space for root patching (we don't care above dev kernels)
            ["/usr/bin/rsync", "-r", "-i", "-a", f"{kdk_path}/System/Library/Extensions/", f"{self.mount_location}/System/Library/Extensions"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        if not (Path(self.mount_location) / Path("System/Library/Extensions/System.kext/PlugIns/Libkern.kext/Libkern")).exists():
            logging.info("- Failed to merge KDK with Root Volume")
            raise Exception("Failed to merge KDK with Root Volume")
        logging.info("- Successfully merged KDK with Root Volume")


    def merge(self, save_hid_cs: bool = False) -> str:
        """
        Merge the Kernel Debug Kit (KDK) with the root volume

        Returns KDK used
        """
        if self.skip_root_kmutil_requirement is True:
            return None
        if self.constants.detected_os < os_data.os_data.ventura:
            return None

        # Manual mode resolves the exact catalog identity before considering a
        # predownloaded asset, so stale assets can never substitute another KDK.
        kdk_obj = self._kdk_object() if self.manual_kdk_candidate is not None else None
        if kdk_obj is not None and kdk_obj.success is False:
            raise Exception(f"Unable to get selected KDK info: {kdk_obj.error_msg}")

        # If a KDK was pre-downloaded, install it. An already-installed manual
        # selection deliberately ignores unrelated stale download artifacts.
        if self.constants.kdk_download_path.exists() and not (
            kdk_obj is not None and kdk_obj.kdk_already_installed
        ):
            if self._manual_download_matches_selection() is False:
                raise Exception("Predownloaded KDK does not match the manual selection; no substitute KDK will be used")
            if kdk_handler.KernelDebugKitUtilities().install_kdk_dmg(self.constants.kdk_download_path) is False:
                logging.info("Failed to install KDK")
                raise Exception("Failed to install KDK")

        # AUTO follows the inherited resolver. MANUAL resolves only the exact
        # trusted-catalog identity selected for this operation.
        kdk_obj = self._kdk_object()
        if kdk_obj.success is False:
            logging.info(f"Unable to get KDK info: {kdk_obj.error_msg}")
            raise Exception(f"Unable to get KDK info: {kdk_obj.error_msg}")

        # If no KDK is installed, download and install it
        if kdk_obj.kdk_already_installed is False:
            if self.manual_kdk_candidate is not None:
                raise Exception(
                    "The manually selected KDK is not installed and its validated predownload is unavailable; "
                    "no substitute or silent download will be used"
                )
            kdk_download_obj = kdk_obj.retrieve_download()
            if not kdk_download_obj:
                logging.info(f"Could not retrieve KDK: {kdk_obj.error_msg}")
                raise Exception(f"Could not retrieve KDK: {kdk_obj.error_msg}")

            # Hold thread until download is complete
            kdk_download_obj.download(spawn_thread=False)

            if kdk_download_obj.download_complete is False:
                error_msg = kdk_download_obj.error_msg
                logging.info(f"Could not download KDK: {error_msg}")
                raise Exception(f"Could not download KDK: {error_msg}")

            if kdk_obj.validate_kdk_checksum() is False:
                logging.info(f"KDK checksum validation failed: {kdk_obj.error_msg}")
                raise Exception(f"KDK checksum validation failed: {kdk_obj.error_msg}")

            kdk_handler.KernelDebugKitUtilities().install_kdk_dmg(self.constants.kdk_download_path)
            # re-init kdk_obj to get the new kdk_installed_path
            kdk_obj = self._kdk_object()
            if kdk_obj.success is False:
                logging.info(f"Unable to get KDK info: {kdk_obj.error_msg}")
                raise Exception(f"Unable to get KDK info: {kdk_obj.error_msg}")

            if kdk_obj.kdk_already_installed is False:
                # We shouldn't get here, but just in case
                logging.warning(f"KDK was not installed, but should have been: {kdk_obj.error_msg}")
                raise Exception(f"KDK was not installed, but should have been: {kdk_obj.error_msg}")


        kdk_path = Path(kdk_obj.kdk_installed_path) if kdk_obj.kdk_installed_path != "" else None
        if kdk_path is None:
            logging.info(f"- Unable to find Kernel Debug Kit")
            raise Exception("Unable to find Kernel Debug Kit")

        logging.info(f"- Found KDK at: {kdk_path}")

        if self._matching_kdk_already_merged(kdk_path):
            return kdk_path

        if save_hid_cs is True:
            self._backup_hid_cs()

        self._merge_kdk(kdk_path)

        if save_hid_cs is True:
            self._restore_hid_cs()

        return kdk_path
