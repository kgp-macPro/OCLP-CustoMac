# Phase 1 Synthetic Regression Results

Date: 2026-08-12

## Result

**PASS for all applicable static, archive, generated-configuration, and synthetic EFI-builder checks.** No installation, root patch, KDK operation, NVRAM write, EFI write, or live-system mutation occurred.

## OpenCore and schema checks

| Check | Result |
|---|---|
| Official 1.0.5 vs 1.0.7 `Docs/Sample.plist` recursive key/type schema | identical; no added, removed, or type-changed key |
| 1.0.7 slim archive member set vs baseline slim archive | identical after ignoring regenerated `__MACOSX` metadata |
| 1.0.7 ordinary member hashes vs matching official parent | all exact matches |
| RELEASE full synthetic build vs official 1.0.7 `ocvalidate` | PASS, no issues |
| DEBUG full synthetic build vs official 1.0.7 `ocvalidate` | PASS, no issues |
| OpenLegacyBoot in generated outputs | absent, as before |
| normal KGP fixture NvmExpressDxe/XhciDxe activation | absent, as before |
| explicit conditional-driver fixture | both selected exactly when their existing flags are set, as before |

The raw template deliberately has all UEFI drivers disabled and is not a final generated configuration; validating it directly reports that `RequestBootVarRouting` needs OpenRuntime. The builder's unchanged `BuildMiscellaneous._general_oc_handling()` enables OpenRuntime. Both the minimally completed template fixture and all full generated configurations pass 1.0.7 `ocvalidate`.

## Before/after full-build fixtures

An immutable baseline source tree was generated from original HEAD `ec5e591e0f46e948b0258ef1c8ed5d17d6a2c865` inside `WORK/`. Baseline and refreshed builders wrote only to separate fixture folders inside the development repository. Matching 1.0.5 and 1.0.7 `ocvalidate` binaries validated their respective outputs.

| Fixture | Main paths exercised | Before/after result |
|---|---|---|
| MacPro5,1 Broadcom default | normal RELEASE suite, Lilu order, WEG, RestrictEvents, NVMeFix, BlueToolFixup, CryptexFixup, Modern Wireless EFI resources, AMFIPass | semantic config identical except declared OpenCore version |
| BCM4360 + BRCM20702 | AirportBrcmFixup injector/fake-ID path and BlueToolFixup legacy-Bluetooth gate | identical selection, order, arguments, properties |
| BrcmNIC + `US` + WOWL | country property and WOWL path | identical selection, order, properties and arguments |
| RestrictEvents empty | `allow_oc_everywhere` path; RestrictEvents off; EFICheckDisabler on | identical mutual exclusion |
| debug + FeatureUnlock + CPUFriend | DEBUG OpenCore/kext archives, DebugEnhancer, stock FeatureUnlock, CPUFriend/DataProvider | identical selection/order; both configs pass matching `ocvalidate` |
| MacPro audio RELEASE + DEBUG | existing AppleALC model/layout gate and both payload variants | unchanged selection/layout/order; official 1.9.7 executable selected; both configs pass matching `ocvalidate` |
| conditional drivers | explicit existing `nvme_boot` and `xhci_boot` flags | NvmExpressDxe, XhciDxe and existing UsbBusDxe selected before and after; predicates identical |

For every matrix row, the complete configuration is semantically equal after removing only `#Revision/OpenCore-Version`, generated serial identity fields, and applying the two approved boot-argument transformations to the baseline: remove the automatically generated `-lilubetaall` token and add `-amfipassbeta` only if AMFIPass is enabled. `Kernel/Add`, `Kernel/Block`, `UEFI/Drivers`, `Misc/Tools`, ACPI, DeviceProperties, quirks, and all other NVRAM selections compare equal.

The country+WOWL fixture exposes a pre-existing behavior: `-brcmfxwowl` appears twice because both the country-code branch and `_wowl_handling()` append it. It is identical before and after and was not changed under the Phase-1 no-logic-change rule.

## Boot-argument policy fixtures

| Required case | Result |
|---|---|
| AMFIPass enabled | AMFIPass entry count 1; `-amfipassbeta` count 1; `-lilubetaall` count 0 |
| multiple AMFIPass enable requests | `enable_kext()` remains idempotent; AMFIPass entry count 1; argument count 1 |
| no AMFIPass | both automatic argument counts 0 |
| unrelated arguments | existing `keepsyms`, `debug`, graphics, Bluetooth, and fixture marker tokens preserved in order |
| pre-existing `-amfipassbeta` | count remains 1; no duplicate |
| pre-existing `-lilubetaall` | explicitly supplied token remains present once; it is not stripped |

All five generated policy configurations pass official OpenCore 1.0.7 `ocvalidate`. The full seven-case component matrix also retains semantic equality under only the approved policy delta. Six ordinary outputs pass `ocvalidate`; the intentionally `validate=False` country/WOWL fixture retains its pre-existing redundant `bootmgfw.efi` BlessOverride diagnostic and is not presented as an ocvalidate-clean release output.

The committed standard-library fixture suite `tests/test_phase1_boot_argument_policy.py` independently exercises enabled, disabled, repeated, pre-existing AMFIPass, pre-existing Lilu beta, unrelated-token, and exact-token/sub-string cases. All six unit tests pass.

## Component selection assertions

- Lilu is entry 0 and precedes every plugin.
- Stock WEG changes only its selected artifact version; disabled cases remain disabled.
- The locally patched Navi WEG archive and version remain byte-identical.
- RestrictEvents keeps `revblock`, `revpatch`, `none`, and EFICheckDisabler exclusion behavior.
- AirportBrcmFixup preserves chipset detection, fake-ID injector, country property, WOWL argument, DeviceProperties, and order. It remains absent for non-Broadcom input.
- Only BlueToolFixup was imported from BrcmPatchRAM 2.7.2. Its existing BRCM2070/BRCM2046/BRCM20702/third-party gates and template position are unchanged.
- NVMeFix remains conditional on the existing non-Apple NVMe path.
- CPUFriend retains its model/SMBIOS gate and CPUFriendDataProvider generation path.
- CryptexFixup retains its legacy/pre-Ivy CPU gate and does not become active in a modern/default fixture.
- DebugEnhancer remains debug-only.
- Stock FeatureUnlock retains `fu_status` and model/OS gates; no FeatureUnlock-Tahoe file, source, entry, or binary is present.
- AppleALC retains the same inherited model/layout selection and Lilu ordering while selecting official 1.9.7. The RELEASE fixture executable is `5b67211797985272949b352eff0bb797504903a2ea4598e2d75d0ceca0ed5aa4`; the DEBUG fixture executable is `38a57eda103d7aaf4bf27b64f61e3e972388bf7517ae8da013d86d6512ec1434`. KGP's production Hackintosh already loads 1.9.7 successfully. This does not validate the historical unsupported-Mac Intel-HDEF case.
- AMFIPass remains 1.4.1 in the same `Kernel/Add` position.

## Root-patch and wireless/audio assertions

The following source files compare byte-identically to baseline:

| File | SHA-256 |
|---|---|
| `sys_patch/patchsets/hardware/networking/modern_wireless.py` | `fa0dad681239c2268d17d81a9d8f422dc359d5d2b8b9fe670f2f12d4f3485f97` |
| `sys_patch/patchsets/hardware/misc/modern_audio.py` | `a24581ef94b304d2252bc9db9d181a20332fe6621801dadf9bd5cb3339d2615d` |

On Darwin 25, the Broadcom fixture returns the same Modern Wireless patch dictionary before and after: `wifip2pd`, `IO80211.framework`, and `WiFiPeerToPeer.framework` from `13.7.2-25`. The Modern Audio fixture returns the same Beta-1 AppleHDA patch and KDK requirement.

An Intel-like wireless fixture remains unselected by `ModernWireless.present()` because this preserved source class is explicitly Broadcom-typed. Phase 1 therefore proves the current Intel behavior is unchanged; it does not invent or broaden an Intel detector. Shared KGP PSP resources and all previously established Intel payload evidence remain frozen.

## Static change-boundary checks

- `git diff --check`: PASS.
- No patch dictionary, root-patch engine, PatcherSupportPkg, KDK, APFS/snapshot, ACPI, DMAR, DeviceProperties, PCI, AppleVTD, NVRAM-policy, hardware-detection, model-gating, or GUI source file changed.
- Every changed payload is an explicitly approved component or approved OpenCore-provided conditional driver.
- No fork binary entered the tree.
- No new hardware or patch family was enabled.
- Automatic/global `-lilubetaall` injection is removed from both the core builder and the inherited AppleALC path. An explicitly supplied token is retained.
- `BuildOpenCore._apply_amfipass_boot_arg_policy()` runs once after every component builder and adds the exact `-amfipassbeta` token only when final AMFIPass state is enabled. Token-aware checking prevents duplicates.
- AMFIPass enablement criteria and its exact 1.4.1 archive/executable are unchanged.

## Build-environment boundary

The existing Python environment was sufficient for all synthetic EFI builds; no dependency was installed or upgraded. A full application/package release build was intentionally not attempted because requirements and hashes are not pinned and the packaged/CI Python mismatch remains unresolved.

`BUILD_ENVIRONMENT_REPRODUCIBILITY = SEPARATE_V2_PHASE`
