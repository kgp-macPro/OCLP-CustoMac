# Phase 1 Full Official Component / Universal EFI-Builder Refresh

Date: 2026-08-12

## Outcome

Phase 1 is complete in the isolated, remote-free development repository. The **primary purpose** remains Tahoe root patching on KGP Hackintosh systems. The broader changes are **secondary maintenance work** for component paths already carried by the inherited Universal OCLP EFI Builder; no newly supported hardware, root-patch family, or feature was enabled.

Every adopted binary is from an exact published official upstream release. No OCLP-Plus, OCLP-Mod, OCLP-R, SimpleHac, mirror, proxy, nightly, or third-party rebuilt artifact entered the tree.

## Acquisition discipline

Before any download, the completed Plus/Mod audit, `/private/tmp`, and the active macOS temporary directory were searched. Existing exact RELEASE assets were reused only after their SHA-256 values matched the immutable audit records:

- `OCLP-Plus-Mod-evaluation-audit/RELEASE_ASSETS/Acidanthera/`: OpenCore, Lilu, WhateverGreen, RestrictEvents, AirportBrcmFixup;
- `OCLP-Plus-Mod-evaluation-audit/WORK/COMPONENT_MODERNIZATION/OFFICIAL/`: BrcmPatchRAM, NVMeFix, CPUFriend, CryptexFixup, DebugEnhancer, FeatureUnlock, AppleALC.

The corresponding official DEBUG assets were not present in the searched completed-audit or temporary trees. They were downloaded once from the exact official GitHub release URLs and immediately verified. Parent hashes and local paths are recorded in `MANIFESTS/PHASE1_COMPONENT_SHA256.md`. No mutable-main or fork artifact was used.

## A. Primary KGP root-patcher-relevant updates

| Component | Official identity | Result |
|---|---|---|
| OpenCorePkg | 1.0.7, `6651fc36a8c3dca36a3231ba00679611100dbe85`, RELEASE `2ffab6ebf58c7aefb0bcb3a1a385d207746823d6dd87d44bd666e1286939943e` | Updated as one coherent DEBUG/RELEASE suite; slim member set preserved |
| Lilu | 1.7.2, `e4748cc081bf060302c7d3c44a643ce1d11b7e1d`, RELEASE `53967d7dcfaab01023a33df2e969a89522f13d6654a6a56ac4711b62dabf3ab8` | Updated; remains first |
| WhateverGreen stock | 1.7.0, `32514961df000100aa1c8aebd5479cabd4ca3070`, RELEASE `6d6ffe8334ad60f784a662794e67b2560b79d757d506841dc8ca9994ab39979b` | Updated; local Navi variant untouched |
| RestrictEvents | 1.1.6, `3ff8491859606f95957c0cc1dcdf2233a0e1a459`, RELEASE `98170dfae195ddd28b5d95e3f040125a13ca783bcb9bd1e5b8c588e217b14ee6` | Updated; no unreleased 1.1.7 used |
| AirportBrcmFixup | 2.2.0, `d7696451addb696030e785a02fb27992b981285e`, RELEASE `4543a097c120e19f848a8f60e0dbb2d42359f368feb3c217d725b6fe8cd384e1` | Updated as Broadcom-only Tahoe maintenance; not an AppleVTD fix |
| BlueToolFixup | BrcmPatchRAM 2.7.2, `aef376bb1e7e27cabc61da7edfb1a88fac7f7acc`, RELEASE `e1c1c55347526d031a8ae2fdd1f52efa3019161e497fb38e1cfa809752f8af21` | Only BlueToolFixup imported; all other archive members excluded |

The official OpenCore parent supplied `boot.efi`, `OpenCore.efi`, OpenRuntime, OpenCanopy, OpenLinuxBoot, OpenLegacyBoot, ResetNvramEntry, BootKicker, OpenShell, macserial, and ocvalidate. DEBUG and RELEASE members were not mixed. The previous slim-package member set is exact; OpenLegacyBoot remains removed from generated output by unchanged logic. A recursive type/key comparison of official 1.0.5 and 1.0.7 `Sample.plist` found no schema migration, and generated configurations pass matching official 1.0.7 `ocvalidate`.

## B. Universal EFI-builder maintenance updates

| Component | Before → after | Official tag / commit | Existing behavior |
|---|---|---|---|
| NVMeFix | 1.1.2 → 1.1.3 | 1.1.3 / `6358326a01a051f888fc38ab80efea86d64574a5` | storage predicate unchanged |
| CPUFriend | 1.2.9 → 1.3.0 | 1.3.0 / `6a2d0124f8a102212cccdd4cfc89b7369126b627` | model/SMBIOS and DataProvider behavior unchanged |
| CryptexFixup | 1.0.4 → 1.0.5 | 1.0.5 / `cd1cb635ec63c2091720560dae2bc6efd1ac7686` | legacy/pre-Ivy gate unchanged |
| DebugEnhancer | 1.1.0 → 1.1.1 | 1.1.1 / `8792fba2b28e51599e45e1293de868a179563d3a` | debug-only gate unchanged |
| stock FeatureUnlock | 1.1.7 → 1.1.8 | 1.1.8 / `a7496bacee9545978658938f64668121a9b9bd04` | stock gate unchanged; no FeatureUnlock-Tahoe source/binary used |
| AppleALC | 1.6.3 → 1.9.7 | 1.9.7 / `a822e7c7e8f301bbedd60cca631789acd437ba24` | inherited EFI-audio gate/layout/order unchanged |
| NvmExpressDxe | inherited 2020 member → official OpenCore 1.0.7 X64 | OpenCore identity above | `nvme_boot` predicate unchanged |
| XhciDxe | inherited 2022 member → official OpenCore 1.0.7 X64 | OpenCore identity above | `xhci_boot` predicate unchanged |

NvmExpressDxe and XhciDxe were ordinary inherited upstream OpenCore members: repository history showed no KGP/local patch, and no source/build evidence of customization. Their existing consumers and predicates are unchanged, so they were updated coherently from OpenCore 1.0.7. They remain absent from the normal fixture and appear only when the pre-existing flags select them.

AppleALC's inherited pin was traced to Dortania OCLP commit `c707047530db29f88d1fc5e7ffcedfa0b1ebf180`, which reverted 1.7.6 to 1.6.3 for audio failures on certain unsupported-Mac Intel HDEF devices. No upstream change was found that proves that unspecified legacy case resolved. It does not block KGP's supported Hackintosh scope: KGP's production Hackintosh EFI already successfully loads official 1.9.7. Plus 3.2.2 carries 1.6.3 and Mod 3.1.9 carries 1.9.5; neither supplies 1.9.7. The official Acidanthera 1.9.7 release was adopted, while unsupported-Mac compatibility remains explicitly **not validated**. See `PHASE1_APPLEALC_REVIEW.md`.

## C. Kept/frozen components

- AMFIPass remains exact 1.4.1 (archive `07b266145906db41f4b13a7938fbb173ea28888cc1fa65f84417f8820adc961e`, executable `4c35bc196d35c69b5f9dca83fe733801211c7828716f51585c7f5450039ca884`).
- PatcherSupportPkg remains `2.0.0-tahoe-restored.1`; `Universal-Binaries.dmg` remains `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4`.
- IO80211FamilyLegacy, IOSkywalkFamily, every Modern Wireless framework/service payload, and all wireless patch dictionaries remain unchanged.
- Beta-1 AppleHDA and the Modern Audio patch/KDK logic remain unchanged.
- local Navi WhateverGreen remains exact 1.6.9-Navi.
- RSRHelper, Innie, SimpleMSR, AutoPkgInstaller, CSLVFixup, EFICheckDisabler, RSRRepair, AMDGPUWakeHandler, KDKlessWorkaround, CreateVault tooling, and opaque/legacy resources remain unchanged.

## D. Blocked or excluded work

- No fork binary was eligible.
- No other BrcmPatchRAM member was eligible; only BlueToolFixup was imported.
- AMFIPass had no authenticated newer official public artifact and was kept.
- The historical unsupported-Mac Intel-HDEF behavior is not represented as validated for AppleALC 1.9.7.
- No driver, kext, sample configuration entry, or hardware family was added merely because an official archive contained it.

## E. Deferred build-environment reproducibility

`BUILD_ENVIRONMENT_REPRODUCIBILITY = SEPARATE_V2_PHASE`

The existing Python environment was sufficient for isolated baseline/refreshed EFI fixture builds. No dependency was installed or upgraded. A full application/package release build was not attempted because requirements are mutable/unhashed and packaged/CI Python versions remain incoherent. Phase 1 did not create a lockfile or alter Python policy.

## Final KGP boot-argument policy

KGP intentionally adopts neither audited fork verbatim:

- `-lilubetaall` is no longer automatically/global injected. The builder does not strip a deliberately supplied instance.
- `-amfipassbeta` is centrally coupled to the final generated AMFIPass state: when AMFIPass is enabled, the exact argument token is present once; when KGP does not enable AMFIPass, KGP does not add the argument.
- Plus 3.2.2 likewise has no automatic `-lilubetaall`, but uses several partial/conditional `-amfipassbeta` injection sites. Mod 3.1.9 globally injects `-lilubetaall`, never injects `-amfipassbeta`, and manages AMFIPass independently.

The implementation is centralized in `BuildOpenCore._apply_amfipass_boot_arg_policy()`, called after all component builders. It reads the final `AMFIPass.kext` `Enabled` field, uses token-aware detection for idempotence, and leaves all pre-existing boot arguments unchanged. It does not alter AMFIPass enablement criteria or the 1.4.1 artifact.

## Preserved invariants

- No component enablement or hardware/model selection branch changed. Source changes outside constants are limited to the approved centralized boot-argument policy and removal of the obsolete AppleALC beta-override block.
- Lilu remains first. `-lilubetaall` is not automatically injected; an explicitly supplied token is preserved.
- `-amfipassbeta` is automatically present exactly once whenever the final generated configuration enables AMFIPass.
- AirportBrcmFixup retains its existing Broadcom chipset, country, fake-ID, WOWL, property, and ordering logic and remains disabled for Intel input.
- BlueToolFixup retains every existing gate and order. No Brcm firmware/injector kext was added.
- Stock FeatureUnlock is distinct from `/Users/kgp/OCLP-Github-KGP/kgp/FeatureUnlock-Tahoe`; the latter was neither read as an artifact source nor modified.
- No root-patch payload, PSP file, wireless/audio patch dictionary, KDK path, APFS/snapshot path, ACPI, DMAR, DeviceProperties, PCI, IOMapper, or AppleVTD behavior changed.

## Verification result

All applicable static, archive, selection, fixture, and generated-config checks pass. Full baseline/refreshed RELEASE and DEBUG EFI fixtures pass their matching official `ocvalidate`. The detailed cases and limitations are recorded in `PHASE1_SYNTHETIC_REGRESSION.md`.

Final pre-commit integrity checks passed: `git diff --check` is clean; the production branch, HEAD, clean status, remotes, local configuration, and deterministic non-`.git` content aggregate all match the development baseline; the root-patch, security, and OCLP-R audits match their saved final metadata records; and all 52 existing files authenticated by the Plus/Mod audit's final SHA-256 manifest still match. IntelLucy-DMA-Research retains an exact non-`.git` metadata match, with only its previously disclosed Git-index timestamp refresh. The local Phase-1 commit identity is recorded in the final handoff because a commit cannot contain its own object ID.

This component baseline is suitable as the foundation for the separately authorized Phase-2 patch/state implementation. Phase 2 has not started.
