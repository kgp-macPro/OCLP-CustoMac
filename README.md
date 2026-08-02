<div align="center">
<img src="docs/images/OC-Patcher.png" alt="OpenCore Patcher Logo" width="256" />
<h1>OCLP 3.0.0 Nightly – amfipassbeta Edition for macOS Tahoe</h1>
</div>

---

## Recommended Setup

This repository provides the **recommended way** to run the preserved OCLP 3.0.0 Tahoe patchset using:

**AMFIPass.kext + boot argument `-amfipassbeta`**

Unlike the original setup, this variant **does not require `amfi=0x80`**, avoiding application compatibility issues.

For full documentation, compatibility details, proper setup and EFI configuration, see:

**InsanelyMac thread (primary reference):**  
https://www.insanelymac.com/forum/topic/362042-experimental-fork-of-oclp-300-nightly-%E2%80%93-modern-wi-fi-awdl-and-applehda-fully-working-under-tahoe/

---

## Overview

This repository provides a reproducible and adapted version of the final OCLP 3.0.0 Nightly snapshot (Dec 24, 2025) by lzhoang2801, configured for macOS Tahoe 26.x.

The original snapshot is no longer directly usable on Tahoe due to incomplete PatcherSupportPkg resources.

This repository restores the functionality required for modern AppleHDA, Wi-Fi and AWDL support by using a compatible PatcherSupportPkg providing complete Universal-Binaries and enabling compatibility with AMFIPass.kext and `-amfipassbeta`.

No original Tahoe root patch logic has been modified.

---

## Scope Clarification

This repository is intended exclusively for advanced Hackintosh systems running macOS Tahoe 26.x.

It is NOT a general unsupported-Mac patching project.

No additional graphics acceleration patches or unsupported-Mac root patch frameworks are included.

This repository intentionally remains as close as possible to the original OCLP 3.0.0 Nightly Tahoe baseline released by the OCLP developers and later preserved by lzhoang2801.

The fork only enables and preserves the original Tahoe patch functionality already implemented by the OCLP developers.

---

## Functionality

The following components are currently confirmed working with this setup:

- modern audio (AppleHDA)
- modern Wi-Fi (Broadcom and supported Intel chipsets)

AWDL stack:
- AirDrop (bidirectional)
- AirPlay (bidirectional)
- Screen Mirroring (bidirectional)
- Personal Hotspot
- Continuity Camera

Continuity:
- Handoff (e.g. Mail, Notes, Safari)

Sidecar:
- currently not functional

---

## Requirements

- Boot argument:  
  `-amfipassbeta`

- A suitable **Kernel Debug Kit (KDK)** is required for OCLP root patching

For compatibility details (macOS versions and KDK handling), see the InsanelyMac thread or its mirror on tonymacx86.

---

## PatcherSupportPkg Dependency

This repository relies on:

https://github.com/kgp-macPro/PatcherSupportPkg-laobamac

This PatcherSupportPkg provides complete Universal-Binaries and enables compatibility with AMFIPass.kext and `-amfipassbeta`.

### Verified Payload Relationship

The PatcherSupportPkg history requires an important distinction.

The final published OCLP 3.0.0 Nightly release by lzhoang2801 references a newer PatcherSupportPkg that no longer contains the required Tahoe `AppleHDA.kext`. As a result, root patching with that currently published configuration fails because the expected AppleHDA payload cannot be found.

The separately preserved edition corrects this by redirecting OCLP to an earlier lzhoang2801 PatcherSupportPkg that still contains the required `AppleHDA.kext`.

This amfipassbeta edition instead uses a KGP-maintained derivative of laobamac's PatcherSupportPkg. Because laobamac's original package also did not contain the required Tahoe `AppleHDA.kext`, that payload was restored unchanged by KGP from the earlier working lzhoang2801 PatcherSupportPkg.

An offline comparison of all resources actually consumed by the enabled `Modern Wireless` and `Modern Audio` patchsets confirmed:

- `wifip2pd` is byte-identical in the earlier lzhoang2801 package and the KGP-maintained laobamac derivative.
- The restored `AppleHDA.kext` is byte-identical to the payload from the earlier working lzhoang2801 PatcherSupportPkg.
- Five Modern Wireless framework executables have identical architectures, paths, permissions and executable `__text` sections:
  - `IO80211`
  - `IO80211Old.dylib`
  - `LibSystemShim.dylib`
  - `WiFiPeerToPeer`
  - `WiFiPeerToPeerOld.dylib`
- The relevant difference in these five files is their embedded code-signature and associated link-edit metadata.
- The earlier lzhoang2801 variants are ad-hoc signed.
- The laobamac variants contain non-ad-hoc embedded signatures.

The PatcherSupportPkg redirect does not modify OCLP's Modern Wireless or Modern Audio patch definitions, destination paths, APFS snapshot handling, kernel-cache rebuilding, root-patch application logic or root-patch reversion logic.

This comparison refers specifically to the earlier working lzhoang2801 PatcherSupportPkg deliberately used by the preserved edition. It does not describe or make assumptions about the newer incomplete PatcherSupportPkg referenced by lzhoang2801's final published release.

---

## Repository Scope

This repository:

- provides a reproducible working reference of the original OCLP 3.0.0 Nightly snapshot
- restores the missing Tahoe `AppleHDA.kext` and preserves the resources required for modern Wi-Fi and AWDL functionality
- uses a PatcherSupportPkg compatible with AMFIPass.kext and `-amfipassbeta`, including AppleHDA
- does **not introduce any new patch logic**

---

## Important Notes

- this fork only enables and preserves the original Tahoe patch functionality already implemented by the OCLP developers
- this fork is **not supported by the OCLP developers**
- intended for **advanced Hackintosh configurations only**
- only modern audio (AppleHDA) and modern Wi-Fi + AWDL are expected to work reliably
- no additional graphics acceleration or unsupported-Mac root patch frameworks are included
- always keep a bootable backup before applying root patches

---

## Community & Discussion

Additional discussion:

**tonymacx86 (mirror thread):**  
https://www.tonymacx86.com/threads/experimental-fork-of-oclp-3-0-0-nightly-modern-wi-fi-awdl-and-applehda-fully-working-under-tahoe-26-x.332849/

---

## Credits

- Dortania OCLP Team (original OCLP authors and developers)
- [crystall1nedev](https://github.com/crystall1nedev) (Eva Isabella Luna) (original OCLP 3.0.0 Nightly release)
- [lzhoang2801](https://github.com/lzhoang2801) (original OCLP 3.0.0 Nightly fork)
- [kgp-macPro](https://github.com/kgp-macPro) (preservation, maintenance, AMFIPass integration, AppleHDA restoration, testing and documentation)
- [laobamac](https://github.com/laobamac) (amfipassbeta PatcherSupportPkg)
- [YBronst](https://github.com/YBronst) (OCLP Nightly development)
- badbrain (boot-arg ipc_control_port_options=0 support)
- [zxystd](https://github.com/zxystd) (itlwm/AirportItlwm project)
- [lshbluesky](https://github.com/lshbluesky) (IntelBluetoothFirmware maintenance and releases)
- [Vinhts](https://github.com/Vinhts) (IntelBTPatcher Tahoe 26.5 Bluetooth LE fixes)
- [Z3c0ld](https://github.com/Z3c0ld) (IntelBTPatcher Tahoe 26.5 Bluetooth LE fixes)
- InsanelyMac community
- tonymacx86 community (mirror thread)

For a complete list of OpenCore Legacy Patcher contributors, please refer to the original Dortania repository:

https://github.com/dortania/OpenCore-Legacy-Patcher

---

## Maintainer

Maintained by **kgp**

- GitHub: https://github.com/kgp-macPro
- InsanelyMac: kgp (formerly KGP-iMacPro)
- tonymacx86: kgp

---

## Disclaimer

This repository provides a preserved and maintained Tahoe patch environment intended for advanced Hackintosh systems.

Not intended for unsupported Macs requiring graphics acceleration root patches.

Use at your own risk.

---

If this repository was useful to you:

A coffee is always appreciated ☕  
https://buymeacoffee.com/kgp.macpro