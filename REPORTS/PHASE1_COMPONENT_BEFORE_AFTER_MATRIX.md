# Phase 1 Component Before/After Matrix

Date: 2026-08-12

The **primary purpose** remains Tahoe Hackintosh root patching. Updates marked “Universal maintenance” modernize already-carried inherited EFI-builder paths without enabling them for new hardware. All adopted binaries came from exact official upstream releases; no Plus, Mod, OCLP-R, SimpleHac, mirror, nightly, or rebuilt-fork binary was used.

## Adopted updates

| Component | Before | After | Official tag / commit | Official RELEASE parent SHA-256 | Existing consumer/gate | Scope |
|---|---:|---:|---|---|---|---|
| OpenCorePkg suite | 1.0.5 | 1.0.7 | `1.0.7` / `6651fc36a8c3dca36a3231ba00679611100dbe85` | `2ffab6ebf58c7aefb0bcb3a1a385d207746823d6dd87d44bd666e1286939943e` | universal builder; same slim-member set | Primary validated EFI refresh |
| Lilu | 1.7.0 | 1.7.2 | `1.7.2` / `e4748cc081bf060302c7d3c44a643ce1d11b7e1d` | `53967d7dcfaab01023a33df2e969a89522f13d6654a6a56ac4711b62dabf3ab8` | always first in `Kernel/Add` | Primary validated EFI refresh |
| WhateverGreen stock | 1.6.9 | 1.7.0 | `1.7.0` / `32514961df000100aa1c8aebd5479cabd4ca3070` | `6d6ffe8334ad60f784a662794e67b2560b79d757d506841dc8ca9994ab39979b` | existing graphics/audio conditions | Primary validated EFI refresh |
| RestrictEvents | 1.1.5 | 1.1.6 | `1.1.6` / `3ff8491859606f95957c0cc1dcdf2233a0e1a459` | `98170dfae195ddd28b5d95e3f040125a13ca783bcb9bd1e5b8c588e217b14ee6` | existing `revblock`/`revpatch`; EFICheck exclusion | Primary validated EFI refresh |
| AirportBrcmFixup | 2.1.9 | 2.2.0 | `2.2.0` / `d7696451addb696030e785a02fb27992b981285e` | `4543a097c120e19f848a8f60e0dbb2d42359f368feb3c217d725b6fe8cd384e1` | unchanged Broadcom-only chipset/country/fake-ID/WOWL gates | Primary Tahoe maintenance |
| BlueToolFixup | 2.6.9 | 2.7.2 | BrcmPatchRAM `2.7.2` / `aef376bb1e7e27cabc61da7edfb1a88fac7f7acc` | `e1c1c55347526d031a8ae2fdd1f52efa3019161e497fb38e1cfa809752f8af21` | unchanged legacy/third-party Bluetooth gates | Primary Bluetooth/Tahoe maintenance |
| NVMeFix | 1.1.2 | 1.1.3 | `1.1.3` / `6358326a01a051f888fc38ab80efea86d64574a5` | `e1d5657ab7ac31f69771708f7b80bf218ab9aa0b8e4c4fe6ff943983037e3dfb` | unchanged non-Apple NVMe predicate | Universal maintenance |
| CPUFriend | 1.2.9 | 1.3.0 | `1.3.0` / `6a2d0124f8a102212cccdd4cfc89b7369126b627` | `37645d960f0b3c958cfd0a8a041160532267ec535c4979897123df89c7dbdcde` | unchanged model/SMBIOS/spoof predicate | Universal maintenance |
| CryptexFixup | 1.0.4 | 1.0.5 | `1.0.5` / `cd1cb635ec63c2091720560dae2bc6efd1ac7686` | `25041d94a0fe9a0261caf0ba89b36dfcb21682bf3c697a34bcaddc839576ab30` | unchanged pre-Ivy/legacy CPU predicate | Universal maintenance |
| DebugEnhancer | 1.1.0 | 1.1.1 | `1.1.1` / `8792fba2b28e51599e45e1293de868a179563d3a` | `2c0978c43fb6179fd5195ddec14c4dd9ab2eb46262021a33fcab78b5568ef67f` | unchanged `kext_debug` predicate | Universal maintenance |
| FeatureUnlock stock | 1.1.7 | 1.1.8 | `1.1.8` / `a7496bacee9545978658938f64668121a9b9bd04` | `b1b85c31fe48fc899ac838b013c9b64a842f6f33265200b5ace3ecec5caa045c` | unchanged `fu_status` and model/OS predicate | Universal maintenance |
| AppleALC | 1.6.3 | 1.9.7 | `1.9.7` / `a822e7c7e8f301bbedd60cca631789acd437ba24` | `81a8ba79986130e8c845fff595950226cbc30e588f8d37089e467f776469c29d` | unchanged inherited EFI-audio model/layout predicate | Universal maintenance; validated KGP Hackintosh use, not an unsupported-Mac claim |
| NvmExpressDxe | inherited 2020 binary | OpenCore 1.0.7 X64 member | OpenCore tag/commit above | member `7b560cf9d1682761419669a5dcd4c0a1e674546be9ae2016335d9146b825796b` | unchanged `nvme_boot` predicate | Universal conditional-driver maintenance |
| XhciDxe | inherited 2022 binary | OpenCore 1.0.7 X64 member | OpenCore tag/commit above | member `315a295b3e992ae22223dca16783daa425e12ede77d0449e3f98851282e88d3f` | unchanged `xhci_boot` predicate; existing UsbBusDxe companion | Universal conditional-driver maintenance |

For BlueToolFixup, only `BlueToolFixup.kext` was extracted. No BrcmFirmwareData, BrcmFirmwareRepo, BrcmPatchRAM variant, BrcmNonPatchRAM, or BrcmBluetoothInjector member was added.

## OpenCore coherence

The DEBUG and RELEASE slim archives preserve exactly the previous repository member set. Every ordinary member below came from its matching official 1.0.7 parent variant:

- renamed X64 `BOOTx64.efi` as the existing `System/Library/CoreServices/boot.efi`;
- `OpenCore.efi`;
- `OpenRuntime.efi`, `OpenCanopy.efi`, `OpenLinuxBoot.efi`, `OpenLegacyBoot.efi`, and `ResetNvramEntry.efi`;
- `BootKicker.efi` and `OpenShell.efi`;
- standalone `macserial` and `ocvalidate` from the official 1.0.7 DEBUG parent, following the repository's established packaging model.

OpenLegacyBoot remains packaged but the unchanged builder removes/disables it. No other official driver, tool, sample entry, or sample configuration was imported. RELEASE and DEBUG members were never mixed.

## Kept/frozen components

| Component | Exact retained identity | Decision/reason |
|---|---|---|
| AMFIPass | 1.4.1 archive `07b266145906db41f4b13a7938fbb173ea28888cc1fa65f84417f8820adc961e`; executable `4c35bc196d35c69b5f9dca83fe733801211c7828716f51585c7f5450039ca884` | KEEP exactly |
| PatcherSupportPkg | `2.0.0-tahoe-restored.1`; `Universal-Binaries.dmg` `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4` | FREEZE |
| IO80211FamilyLegacy | archive `e681dcc76a2cd2cea4b0ad5f27a3c816055fde3cdccd890dd10a3e2c84e96d93` | FREEZE |
| IOSkywalkFamily | archive `1e12b7ef42f55b39ea54ada97b46331220668b2c48a28656e9875c5145fe2479` | FREEZE |
| Beta-1 AppleHDA | executable `6bf19c385a1212160be8a01fd7903aaa0416407e0b52e949f49d04cee4c65de7`; `__text` `135b98fbccd0c8cd742b50f01a563054eef506f81bcc7799b5fb6429df063096` | FREEZE |
| local Navi WhateverGreen | 1.6.9-Navi RELEASE archive `c7c841f1776f40009eeb0a1d23c697a49fb76be772ee14863d30abad78a91474` | KEEP; local implementation untouched |
| RSRHelper / Innie / SimpleMSR | current principal identities | KEEP; already latest established identities |
| AutoPkgInstaller, CSLVFixup, EFICheckDisabler, RSRRepair, AMDGPUWakeHandler, KDKlessWorkaround, CreateVault suite | current carried bytes | KEEP; no separately authenticated safe update or local/custom boundary |
| all Apple-derived/legacy opaque resources | current carried bytes | KEEP |

## Behavioral boundaries

- No hardware/model/SMBIOS predicate changed.
- No ACPI, Booter quirk, Kernel quirk, UEFI quirk, DeviceProperties, PCI, DMA, DMAR, or AppleVTD logic changed.
- No Modern Wireless or Modern Audio root-patch source changed.
- `-lilubetaall` is no longer automatically/global injected. The finalizer never strips a deliberately pre-existing token.
- `-amfipassbeta` is centrally and idempotently coupled to final `AMFIPass.kext` enablement; it is added once only when AMFIPass is enabled.
- Plus 3.2.2 has no automatic `-lilubetaall` and partial conditional `-amfipassbeta` coupling. Mod 3.1.9 globally adds `-lilubetaall`, never auto-adds `-amfipassbeta`, and handles AMFIPass independently. KGP adopts neither policy verbatim.
- `BUILD_ENVIRONMENT_REPRODUCIBILITY = SEPARATE_V2_PHASE`.
