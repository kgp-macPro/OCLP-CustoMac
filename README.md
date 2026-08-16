<div align="center">
  <img src="docs/images/OC-Patcher.png" alt="OpenCore Patcher Logo" width="256" />
</div>

# OCLP-CustoMac

### Focused Modern Wi-Fi and AppleHDA root patching for macOS

---

OCLP-CustoMac is an independent, focused OpenCore Legacy Patcher derivative developed primarily for advanced Custom Mac and Hackintosh systems. Its first public release is fully runtime validated on **macOS Tahoe 26.x / Darwin 25**.

The registered root-patch families are deliberately limited to:

- **Modern Wireless**
- **Modern Audio / AppleHDA**

No graphics, Non-Metal, or unrelated inherited OCLP root-patch family is registered. The inherited OCLP source infrastructure remains present, but those other detector families cannot enter OCLP-CustoMac's final root-patch plan. The same narrow registry applies if OCLP-CustoMac is executed on genuine Apple Intel hardware.

## Why OCLP-CustoMac Exists

OCLP-CustoMac was not created merely to place another OCLP patcher on the market, and it is not intended to replace original Dortania OCLP, OCLP-Mod, or OCLP-Plus.

The project grew from long-term maintenance and real-system validation of the preserved OCLP 3.0.0 Nightly Tahoe environment and its amfipassbeta Edition. Continued Tahoe development exposed requirements that no longer fit cleanly within preservation-only changes:

- independent Modern Wi-Fi and Modern Audio selection;
- safer recovery from installed, pending, and failed root-patch states;
- optional manual KDK selection and KDK eligibility safeguards;
- direct Intel hardware detection;
- APFS patch-resource packaging;
- locked, reproducible, and independently validated builds.

OCLP-Mod and OCLP-Plus were important comparative reference implementations during the audits. OCLP-CustoMac is **not** a copy-and-paste combination of those forks. Comparable concepts were audited against the preserved OCLP 3.0.0 Nightly baseline, then independently reimplemented, adapted, refined, or deliberately rejected according to this project's narrower scope and security boundaries.

Concrete examples include:

- **Intel detection:** reconstructed from the current AirportItlwm matcher and current Intel BZ/SC transport definitions, then cross-checked against OCLP-Mod rather than copied from its table.
- **APFS resources:** the APFS container concept was adopted, but the privileged nested-mount model found in comparative forks was rejected. OCLP-CustoMac uses an unprivileged host-side sibling mount with logical-path compatibility.
- **Root-patch recovery:** independently redesigned following real failed/pending root-state testing.
- **Manual KDK and patch selection:** designed for OCLP-CustoMac's operation-scoped selection and fail-closed resolver architecture.

The result has a different scope, different implementation decisions, and its own static and physical runtime validation record. This is not a claim that it is superior to other OCLP derivatives.

## Three Established Tahoe Approaches

OCLP-CustoMac does not obsolete or withdraw the two earlier KGP Tahoe configurations. All three approaches remain intentionally available.

### 1. OCLP 3.0.0 Nightly – Preserved Reference Edition

Repository: [kgp-macPro/OCLP-lzhoang2801](https://github.com/kgp-macPro/OCLP-lzhoang2801)

- conservative reference environment closest to the earlier working lzhoang2801 OCLP 3.0.0 Nightly Tahoe state;
- uses the earlier working lzhoang2801 PatcherSupportPkg containing Modern Wireless resources and AppleHDA;
- retains the historical `amfi=0x80` and `ipc_control_port_options=0` AMFI path;
- preserved for users who value maximum proximity to the original Nightly architecture.

### 2. OCLP 3.0.0 Nightly – amfipassbeta Edition

Repository: [kgp-macPro/OCLP-lzhoang2801-amfipassbeta](https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta)

- conservative and extensively tested on real systems over many months;
- remains close to the preserved Nightly architecture;
- uses `AMFIPass.kext + -amfipassbeta`;
- its documented Intel configuration uses a Broadcom `IOName` spoof with AirportItlwm;
- remains fully available, and satisfied users do not need to migrate.

### 3. OCLP-CustoMac

Repository: [kgp-macPro/OCLP-CustoMac](https://github.com/kgp-macPro/OCLP-CustoMac)

- further-developed focused branch with direct Intel detection;
- does not require a Broadcom `IOName` spoof for Intel detection;
- selectable Modern Wi-Fi and Modern Audio;
- automatic and optional manual KDK selection;
- strengthened root-patch recovery;
- APFS internal resources;
- reproducible, validated builds.

## Public Support Scope

| Environment | Status |
|---|---|
| Custom Mac / Hackintosh, macOS Tahoe 26.x / Darwin 25 | **Fully runtime validated public target** |
| macOS Sequoia / Darwin 24 Modern Wireless | Coherent inherited path and complete resources; not runtime validated or advertised as supported |
| macOS Sonoma / Darwin 23 Modern Wireless | Coherent inherited path and complete resources; not runtime validated or advertised as supported |
| Genuine Apple Intel hardware | Not artificially blocked; unverified and not advertised as supported |
| Darwin 26 / Golden Gate | Outside the current root-patch support scope |

Modern Audio is native/not applicable on Sequoia. Source reachability is not a support promise: Tahoe/Darwin 25 is the first-release support claim.

## Root Patch Selection

The Root Patch Selection screen presents applicable controls for:

```text
[✓] Modern Wi-Fi
[✓] Modern Audio
[ ] Manually select Kernel Debug Kit
```

Applicable Modern Wi-Fi and Modern Audio options default ON on a CLEAN root. Supported selections are:

- Wi-Fi + Audio;
- Wi-Fi only;
- Audio only.

With both patch options OFF, **Start Root Patching** is disabled and an explicitly forced empty operation is rejected before KDK, root, kernel-cache, snapshot, or metadata work.

When a known root patch is installed, its applied selection is shown read-only. To change it:

```text
Revert Root Patches
    -> reboot into a CLEAN/sealed root
    -> choose the new configuration
    -> root patch again
```

Selection affects root payloads only. OCLP-CustoMac does not mutate EFI, DeviceProperties, ACPI, DMAR, NVRAM, or hardware identity as a side effect of Modern Wi-Fi selection.

## Intel Wi-Fi Device Support

OCLP-CustoMac directly recognizes:

- **87 Regular** Intel PCI IDs from the current authoritative AirportItlwm matcher;
- **9 Experimental / Development** Intel BZ/SC transport IDs;
- **96 total** Intel transport IDs.

[Complete Intel Wi-Fi Device Support List](Documentation/Intel-WiFi-Device-Support.md)

Experimental detection makes the shared Modern Wi-Fi root-patch path applicable. It does **not** guarantee stock AirportItlwm runtime support, and a compatible experimental or modified driver may be required. BZ/SC PCI transport IDs do not necessarily identify a one-to-one marketing SKU: `272B` covers discrete BE200/BE202-family variants differentiated through further subsystem/RF identity, while integrated BE201/BE211/BE213 differentiation may likewise require information beyond the base PCI transport ID.

CNVio, CNVio2, and CNVio3 are not exclusion criteria. The known legacy Centrino Wireless-N/WiMAX 6150 IDs `0885` and `0886` remain deliberately excluded.

### Direct Intel detection—no Broadcom IOName spoof required

Unlike the amfipassbeta Edition, OCLP-CustoMac detects supported Intel hardware from its authentic PCI vendor/device identity and does not require a Broadcom `IOName` spoof for detection.

Intel detection and runtime binding are separate layers:

1. OCLP-CustoMac detects the Intel transport and makes Modern Wi-Fi applicable.
2. The user's external EFI and AirportItlwm bind the physical device at boot.

OCLP-CustoMac does **not**:

- provide, install, or download AirportItlwm;
- modify the user's EFI or `Kernel/Add`;
- inject Broadcom `IOName` or Intel spoofing;
- modify DeviceProperties, ACPI, DMAR, or NVRAM.

Do not blindly remove an existing historical EFI property merely because OCLP-CustoMac no longer needs it for detection. It may serve another system-specific purpose; review the migration context first.

### Validated Intel runtime status

With Intel AX210 (`8086:2725`) and an external AirportItlwm EFI, KGP validated the final pre-publication RC after the GUI-branding cleanup:

- Wi-Fi — working;
- AppleHDA — working;
- AirPlay — working bidirectionally;
- normal Apple Screen Mirroring path — working bidirectionally.

This is **Gate 1 — PASS**.

Current AirportItlwm does not provide a complete native AWDL control/data path. OCLP-CustoMac therefore does not claim reliable Intel support for bidirectional AirDrop, Personal Hotspot, or Continuity Camera. Those limitations belong to the external runtime driver, not to OCLP-CustoMac's PCI detection or shared Modern Wireless root patch.

Normal Screen Mirroring works on the validated Broadcom and Intel paths. Some Hackintosh systems independently reproduce an outgoing Hackintosh-to-Apple-receiver black-screen issue; it is separate from OCLP-CustoMac. [FeatureUnlock-Tahoe](https://github.com/kgp-macPro/FeatureUnlock-Tahoe) is a validated fallback for affected Broadcom setups, while Intel plus [FeatureUnlock-Tahoe](https://github.com/kgp-macPro/FeatureUnlock-Tahoe) remains less reliable and under separate development. Systems with normally working Screen Mirroring do not need [FeatureUnlock-Tahoe](https://github.com/kgp-macPro/FeatureUnlock-Tahoe).

### Final Broadcom runtime gate

After Gate 1, KGP physically replaced AX210 with BCM943602CDP and retained the already-installed final-RC Modern Wireless / Modern Audio root-patch snapshot. Root patches were not reverted or reapplied for the adapter change. AppleHDA, Broadcom Wi-Fi, bidirectional AirDrop, bidirectional AirPlay, bidirectional normal Apple Screen Mirroring, Continuity Camera, and Personal Hotspot all worked immediately after boot.

This **Gate 2 — PASS** result confirms that the shared Modern Wireless root-patch environment is hardware-neutral between the validated Intel and Broadcom paths. It does not represent a new Broadcom Revert -> CLEAN -> Root Patch cycle; Broadcom detection and patch application were separately runtime validated during development, and the final GUI-branding cleanup changed no related functional code.

**Publication runtime gates: COMPLETE.**

## Kernel Debug Kit Handling

Modern Wi-Fi alone does not require a KDK solely because Wi-Fi is selected. Modern Audio / AppleHDA uses a KDK where its applicable path requires one. Requirement aggregation remains authoritative for any future selected patch that independently requires a KDK.

### Automatic mode

Automatic mode preserves inherited OCLP behavior: exact match when available, otherwise the existing closest-match choice among permitted candidates.

### Manual mode

When the final selected patch plan requires a KDK, the optional **Manually select Kernel Debug Kit** control becomes available. The dialog shows eligible official candidates, version/build, installed status, exact/closest status where applicable, and the candidate OCLP would choose automatically.

The manual selection is operation-scoped and confirmed before use. The exact chosen identity is handed to the normal OCLP download/install/merge/patch workflow. Cancellation starts no KDK or root operation, and a failed manual choice never falls back silently into AUTO.

### Darwin-26 KDK protection

KDK eligibility uses ProductBuildVersion/build family—not the macOS marketing version:

```text
macOS 26.6.2 / KDK build 25G82  -> permitted
KDK build 26A5368g              -> rejected
```

All KDK candidates whose build identity begins with `26` are excluded. Darwin 25 and older permitted candidates retain inherited exact/closest ranking. Darwin 26 itself is outside the current root-patch scope.

## Root Patch Recovery

OCLP-CustoMac separates authorization to apply a new patch from authorization to recover a root:

- a clean, patch-authorized root does not need Revert;
- a patched, pending, failed, or otherwise non-clean root that blocks new patching exposes **Revert Root Patches** as the recovery path.

Recovery is not artificially restricted by Git commit, application build, project/fork identity, patchset identity, KDK identity, trusted installed-selection metadata, or lifecycle-record presence.

True safeguards remain enforced at click and operation time, including SIP/`can_unpatch`, target-root validation, state revalidation, and the standard last-sealed-snapshot rollback. Failed and pending patch operations retain a recovery path instead of creating a Patch-off/Revert-off dead end.

## Validated Tahoe Configuration

The KGP runtime-validation baseline used:

```text
AMFIPass                1.4.1
boot argument           -amfipassbeta
SecureBootModel         Disabled
csr-active-config       03080000
DisableIoMapper         true
```

`amfi=0x80` is not required for this configuration. `-amfipassbeta` is **not deprecated**.

This is the validated project baseline, not an instruction to rewrite an existing EFI without reviewing the complete hardware and security context.

## Component / Build Baseline

| Component | Version |
|---|---:|
| OpenCorePkg | 1.0.7 |
| Lilu | 1.7.2 |
| WhateverGreen | 1.7.0 |
| RestrictEvents | 1.1.6 |
| AirportBrcmFixup | 2.2.0 |
| BlueToolFixup | 2.7.2 |
| NVMeFix | 1.1.3 |
| CPUFriend | 1.3.0 |
| CryptexFixup | 1.0.5 |
| DebugEnhancer | 1.1.1 |
| AppleALC | 1.9.7 |
| FeatureUnlock | 1.1.8 (stock baseline) |
| AMFIPass | **1.4.1 (intentionally pinned)** |

These versions describe the OCLP-CustoMac build/component baseline. OCLP-CustoMac does not automatically update or rewrite the user's EFI.

## Installation and Package Security

OCLP-CustoMac packages are ad-hoc signed and are not distributed with Apple Developer ID signing or Apple notarization.

First verify the package against the SHA-256 published with the official release:

```sh
shasum -a 256 OpenCore-Patcher.pkg
```

If macOS quarantine blocks that verified package, remove quarantine metadata only from the selected artifact:

```sh
xattr -cr ./OpenCore-Patcher.pkg
```

For the uninstaller:

```sh
xattr -cr ./OpenCore-Patcher-Uninstaller.pkg
```

OCLP-CustoMac does **not** require Gatekeeper to be disabled system-wide. `xattr -cr` removes quarantine metadata from the named package; use it only on an official, hash-verified artifact. A targeted GUI quarantine-removal utility may be used as an optional alternative, but it does not replace checksum verification.

Technical compatibility filenames remain `OpenCore-Patcher.app`, `OpenCore-Patcher.pkg`, and `OpenCore-Patcher-Uninstaller.pkg`.

## APFS Patch Resources

Both protected resource images use APFS:

```text
payloads.dmg            = APFS
Universal-Binaries.dmg = APFS
```

The HFS+-to-APFS conversion preserved the logical payload tree. Complete root patching and Revert were runtime validated with the APFS resources. The runtime mount architecture remains unprivileged: the inner resource image mounts at a host-side sibling location and is exposed through the expected logical path without adding a general-purpose privileged nested-mount helper. Protected-image authentication uses the noninteractive stdin-passphrase path.

## Tahoe Payload Provenance

Two complete PatcherSupportPkg lines are intentionally preserved for the three Tahoe approaches.

### Why complete working resources are required

The final publicly released lzhoang2801 OCLP 3.0.0 Nightly configuration references a newer PatcherSupportPkg that no longer contains the Tahoe `AppleHDA.kext` expected by its included Modern Audio patch definition. When Modern Audio is applicable, that final published configuration cannot complete the expected Tahoe root patch because the required payload is absent.

The preserved working configurations therefore use complete resource sources instead.

### Preserved Reference Edition

The Preserved Reference Edition uses an earlier working lzhoang2801 PatcherSupportPkg containing both the required Modern Wireless payloads and `AppleHDA.kext`. Its relevant Modern Wireless framework variants are the earlier ad-hoc-signed payloads, paired with the historical `amfi=0x80` and `ipc_control_port_options=0` configuration.

### amfipassbeta Edition and OCLP-CustoMac

These use a KGP-maintained derivative of the PatcherSupportPkg preserved by laobamac:

https://github.com/kgp-macPro/PatcherSupportPkg-laobamac

The laobamac-preserved line provides the non-ad-hoc-signed Modern Wireless framework variants used with `AMFIPass.kext + -amfipassbeta`. Because `AppleHDA.kext` was also absent from that preserved package, KGP restored it **unchanged** from the earlier working lzhoang2801 PatcherSupportPkg.

### Verified relationship of consumed payloads

The audit did **not** establish that the two complete PatcherSupportPkg repositories are globally byte-identical. It established equivalence only for resources consumed by the enabled Modern Wireless and Modern Audio patchsets:

- `wifip2pd` is byte-identical between the compared working package variants;
- the restored `AppleHDA.kext` is byte-identical to the earlier working lzhoang2801 Tahoe payload;
- five relevant framework executables retain identical architectures, paths, permissions, and executable `__text` sections:
  - `IO80211`;
  - `IO80211Old.dylib`;
  - `LibSystemShim.dylib`;
  - `WiFiPeerToPeer`;
  - `WiFiPeerToPeerOld.dylib`;
- relevant differences in those framework binaries are confined to embedded code-signature and associated link-edit metadata;
- the earlier lzhoang2801 variants are ad-hoc signed;
- the laobamac-derived variants contain non-ad-hoc embedded signatures.

The payload definitions and consumed functional content remain preserved. OCLP-CustoMac's control logic has been substantially improved; the historical statement that no patcher logic changed no longer describes this project.

## AppleVTD / IOMMU

The fully validated configuration uses `DisableIoMapper=true`. AppleVTD operation with `DisableIoMapper=false` remains post-release research and is not a release requirement.

The pre-publication audit found no grounded localized OCLP-only fix for Broadcom. Intel investigation additionally reaches AirportItlwm's PCI, DMA, and IOMMU behavior. This release does not modify DMAR, the XHC14 Reserved Memory Region, DeviceProperties, ACPI, IOMMU settings, or the user's EFI.

## Existing amfipassbeta Edition Users

Migration is optional. The amfipassbeta Edition remains available, and `AMFIPass.kext + -amfipassbeta` remains valid.

Recommended controlled migration:

```text
Revert existing root patches
    -> reboot CLEAN/sealed
    -> install OCLP-CustoMac
    -> retain AMFIPass.kext + -amfipassbeta
    -> choose Modern Wi-Fi / Modern Audio
    -> root patch
    -> reboot
```

For Intel, an old Broadcom `IOName` spoof used solely for predecessor detection is no longer required by OCLP-CustoMac. Review the complete EFI migration guidance before removing historical DeviceProperties that may have other purposes.

## Community and Discussion

- [InsanelyMac primary discussion](https://www.insanelymac.com/forum/topic/362042-experimental-fork-of-oclp-300-nightly-%E2%80%93-modern-wi-fi-awdl-and-applehda-fully-working-under-tahoe/)
- [tonymacx86 mirror discussion](https://www.tonymacx86.com/threads/experimental-fork-of-oclp-3-0-0-nightly-modern-wi-fi-awdl-and-applehda-fully-working-under-tahoe-26-x.332849/)

Repository, release, updater, and support URLs will be updated together during the separately authorized online-promotion step. This local release-candidate task does not create or guess a future GitHub release URL.

## Project Development & Research

**[KGP / kgp-macPro](https://github.com/kgp-macPro)** — Project lead; OCLP-CustoMac concept and architecture; experimental design; Tahoe patch-environment preservation and development; Broadcom and Intel hardware integration; hardware, operating-system, and multi-build runtime validation; evidence collection; technical review; and publication.

**ChatGPT by OpenAI** — Technical research and reasoning partner for evidence analysis, hypothesis refinement, architecture and experiment planning, runtime-result interpretation, safety-boundary development, technical review, and documentation development.

**OpenAI Codex CLI** — Repository and source analysis, implementation, static validation, automated testing, reproducible-build verification, release packaging, Git-history construction, source auditing, and publication preparation.

**AI attribution:** All AI assistance occurred under continuous human direction, hardware testing, review, validation, and final editorial control. No OpenAI endorsement is implied.

## Upstream & Community Credits

- [Dortania OpenCore Legacy Patcher Team](https://github.com/dortania/OpenCore-Legacy-Patcher)
- [crystall1nedev](https://github.com/crystall1nedev)
- [lzhoang2801](https://github.com/lzhoang2801)
- [laobamac](https://github.com/laobamac) — OCLP-Mod and PatcherSupportPkg preservation; important comparative/reference implementation during the audits
- [YBronst](https://github.com/YBronst) — OCLP-Plus; important comparative/reference implementation during the audits
- [zxystd](https://github.com/zxystd) / [OpenIntelWireless](https://github.com/OpenIntelWireless)
- [lshbluesky](https://github.com/lshbluesky)
- [Vinhts](https://github.com/Vinhts)
- [Z3c0ld](https://github.com/Z3c0ld)
- badbrain
- [InsanelyMac community](https://www.insanelymac.com/)
- [tonymacx86 community](https://www.tonymacx86.com/)

For the complete upstream contributor history, see the original [Dortania OpenCore Legacy Patcher repository](https://github.com/dortania/OpenCore-Legacy-Patcher).

OCLP-CustoMac is an unofficial independent project. It is not supported or endorsed by the Dortania OCLP Team, Apple, Intel, Broadcom, or OpenAI. Attribution above does not imply authorship by KGP of upstream work.

## Disclaimer

Root patching modifies the macOS system snapshot and carries risk. Keep verified backups and a known-good recovery path. OCLP-CustoMac is intended for experienced users who understand OpenCore, EFI configuration, SIP requirements, KDK handling, and APFS snapshot recovery.

Use at your own risk.
