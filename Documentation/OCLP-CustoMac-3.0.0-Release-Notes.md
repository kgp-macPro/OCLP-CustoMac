# OCLP-CustoMac 3.0.0 — macOS Tahoe

Future tag: `v3.0.0`

> Pre-publication release-candidate draft. No tag or GitHub Release exists yet. SHA-256 placeholders below are finalized only after the local RC build passes validation.

## What OCLP-CustoMac Is

OCLP-CustoMac is an independent, focused OpenCore Legacy Patcher derivative for advanced Custom Mac and Hackintosh systems. The first supported public target is **macOS Tahoe 26.x / Darwin 25**.

It grew out of long-term maintenance and real-system validation of the preserved OCLP 3.0.0 Nightly Tahoe environment and the amfipassbeta Edition. Independent Wi-Fi/audio selection, stronger recovery, manual KDK control, KDK safeguards, direct Intel detection, APFS resources, and reproducible builds eventually required a further-developed branch rather than preservation-only changes.

OCLP-Mod and OCLP-Plus were important comparative references. OCLP-CustoMac is not a copy-and-paste combination of them: concepts were audited against the preserved Nightly baseline and independently reimplemented, adapted, refined, or rejected. Intel IDs were reconstructed from AirportItlwm and current Intel BZ/SC definitions; the APFS privileged nested-mount approach used by comparative forks was deliberately rejected in favor of an unprivileged host-side sibling mount; recovery and manual KDK behavior were designed from OCLP-CustoMac's own runtime findings.

## Intentionally Narrow Patch Scope

Only two root-patch families are registered:

- Modern Wireless
- Modern Audio / AppleHDA

No graphics, Non-Metal, or unrelated inherited OCLP family can enter the final patch plan. Intel and Broadcom share the same established Modern Wireless root payload.

## Highlights

- independent Modern Wi-Fi and Modern Audio selection;
- Wi-Fi + Audio, Wi-Fi-only, and Audio-only operation;
- both-OFF Start guard and read-only installed selection;
- direct Broadcom and authentic-PCI Intel detection;
- 87 Regular AirportItlwm IDs plus 9 Experimental / Development BZ/SC transport IDs—96 total;
- no Broadcom `IOName` spoof required for OCLP-CustoMac Intel detection;
- automatic exact/closest KDK choice among eligible candidates;
- optional operation-scoped manual KDK selection with Automatic Choice preview;
- ProductBuildVersion/build-family-26 KDK exclusion (`25G82` allowed, `26A...` rejected);
- recovery retained for patched, pending, failed, and non-clean root states;
- APFS `payloads.dmg` and `Universal-Binaries.dmg`;
- unprivileged APFS sibling-mount/logical-path compatibility;
- locked CPython 3.14.3 x86_64 / 22-wheel reproducible builds.

[Complete Intel Wi-Fi Device Support List](Intel-WiFi-Device-Support.md)

Experimental detection only authorizes the shared Modern Wi-Fi root patch. It does not promise stock AirportItlwm runtime support, and BZ/SC transport IDs do not necessarily identify one marketing SKU without subsystem/RF information.

## Runtime Validation

### Broadcom control

BCM943602CDP retained working AppleHDA, Wi-Fi, and tested AWDL/Continuity behavior with the Intel detector present.

### Intel AX210

With AX210 `8086:2725` physically installed, OCLP-CustoMac directly detected Intel hardware, made Modern Wi-Fi applicable, completed root patching, and subsequently delivered working:

- Wi-Fi;
- AppleHDA;
- AirPlay;
- normal Apple Screen Mirroring.

AirportItlwm remains an external EFI/runtime dependency. Its current incomplete native AWDL control/data path means reliable bidirectional AirDrop, Personal Hotspot, and Continuity Camera are not supported claims for Intel. These are driver limitations, not OCLP-CustoMac PCI-detection or root-patch failures.

Some systems independently reproduce an outgoing Hackintosh-to-Apple-receiver Screen Mirroring black screen. FeatureUnlock-Tahoe is a validated fallback for affected Broadcom setups; Intel plus FeatureUnlock-Tahoe remains less reliable and separate development. Users with normally working Screen Mirroring do not need it.

## KDK and Recovery Safety

Wi-Fi-only does not require a KDK solely because Wi-Fi is selected. Modern Audio uses a KDK when its applicable AppleHDA path requires one.

Manual KDK selection locks the confirmed exact catalog identity into the normal OCLP acquisition/patch workflow. Cancellation starts nothing, and a failed manual candidate never silently falls back into AUTO.

Recovery authorization is separate from authorization to apply another patch. Patched, pending, failed, and non-clean roots retain Revert without artificial project/build/SHA/patchset/KDK ownership restrictions. SIP/`can_unpatch`, target-root validation, operation-time revalidation, and the normal last-sealed-snapshot rollback remain enforced.

## Three Available Tahoe Approaches

OCLP-CustoMac does not obsolete the earlier KGP configurations:

1. **[OCLP 3.0.0 Nightly – Preserved Reference Edition](https://github.com/kgp-macPro/OCLP-lzhoang2801)** — conservative reference closest to the earlier working lzhoang2801 state, complete earlier PatcherSupportPkg, historical `amfi=0x80` / `ipc_control_port_options=0` path.
2. **[OCLP 3.0.0 Nightly – amfipassbeta Edition](https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta)** — conservative and extensively real-system tested, `AMFIPass.kext + -amfipassbeta`, historically documented Intel Broadcom-`IOName` spoof path; existing users do not need to migrate.
3. **[OCLP-CustoMac](https://github.com/kgp-macPro/OCLP-CustoMac)** — direct Intel detection, selection controls, AUTO/Manual KDK, strengthened recovery, APFS resources, and reproducible builds.

Migration from the amfipassbeta Edition is optional. A controlled migration is Revert -> reboot CLEAN/sealed -> install OCLP-CustoMac -> retain `AMFIPass.kext + -amfipassbeta` -> select patches -> patch -> reboot. Do not remove historical EFI DeviceProperties without reviewing whether they serve another purpose.

## Support Boundaries

- Tahoe/Darwin 25 on Custom Mac/Hackintosh hardware is the fully runtime-validated first-release target.
- Sonoma/Darwin 23 and Sequoia/Darwin 24 have coherent inherited Modern Wireless paths but are not runtime validated or advertised as supported.
- Genuine Apple Intel Macs are not artificially blocked but remain unverified.
- Darwin 26/Golden Gate is outside the root-patch support scope.
- The validated configuration uses `DisableIoMapper=true`; AppleVTD with `DisableIoMapper=false` remains post-release research.

## Installation and Integrity

OCLP-CustoMac is ad-hoc signed and not Apple-notarized. Verify the official published SHA-256 before removing package quarantine:

```sh
shasum -a 256 OpenCore-Patcher.pkg
xattr -cr ./OpenCore-Patcher.pkg
```

For the uninstaller:

```sh
xattr -cr ./OpenCore-Patcher-Uninstaller.pkg
```

This does not disable Gatekeeper system-wide. It removes quarantine metadata only from the selected package. Use it only on official, hash-verified artifacts.

## Release Candidate SHA-256

```text
OpenCore-Patcher.pkg:             TO-BE-FILLED-AFTER-RC-BUILD
OpenCore-Patcher-Uninstaller.pkg: TO-BE-FILLED-AFTER-RC-BUILD
OpenCore-Patcher.app:             TO-BE-FILLED-AFTER-RC-BUILD
payloads.dmg:                     082de073e0d103d7bd4b47852007f2b6ab360eda5b4737a089cf3b34a3910f91
Universal-Binaries.dmg:           3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4
```

## Credits

**KGP / kgp-macPro** led the project concept, architecture, experimental design, patch-environment development, Broadcom/Intel integration, physical and multi-build validation, evidence collection, review, and publication.

**ChatGPT by OpenAI** assisted with research, reasoning, evidence analysis, hypothesis refinement, architecture/experiment planning, runtime interpretation, safety boundaries, review, and documentation.

**OpenAI Codex CLI** performed repository/source analysis, implementation, static validation, testing, reproducible-build verification, packaging, Git-history construction, auditing, and publication preparation.

All AI assistance occurred under continuous human direction, hardware testing, review, validation, and final editorial control. No OpenAI endorsement is implied.

Upstream and community credit remains with the Dortania OCLP Team, crystall1nedev, lzhoang2801, laobamac, YBronst, zxystd/OpenIntelWireless, lshbluesky, Vinhts, Z3c0ld, badbrain, InsanelyMac, and tonymacx86. OCLP-Mod/laobamac and OCLP-Plus/YBronst were important comparative reference implementations during the audits.

OCLP-CustoMac is an unofficial independent project and is not endorsed or supported by Dortania, Apple, Intel, Broadcom, or OpenAI.
