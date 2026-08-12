# Phase 1 Boot-Argument Policy Evidence

Date: 2026-08-12

Status: **final KGP v2.0 policy implemented and fixture-verified.**

Exact local release copies inspected read-only:

- OCLP-Plus 3.2.2, commit `afc5021e0c27df30c2d249fce709566220f76273`;
- OCLP-Mod 3.1.9, commit `3b15c88820a6f99d1974532b9a722925da8b2897`.

Both audit copies remained Git-clean after inspection.

## Concise comparison

| Policy | OCLP-Plus 3.2.2 | OCLP-Mod 3.1.9 |
|---|---|---|
| `-lilubetaall` | **No automatic injection.** Explicitly removed. | **Yes, unconditional** in every generated configuration; the AppleALC path also contains a redundant conditional guard. |
| `-amfipassbeta` | **Yes, conditional.** Added by security paths and Modern-Broadcom/Skywalk builder paths. | **No automatic injection anywhere in `oclp_mod`.** Changelog tells the user to add it manually if needed. |
| AMFIPass version | 1.4.1 | 1.4.1 |
| AMFIPass artifact | `AMFIPass-v1.4.1-RELEASE.zip` | same |
| AMFIPass auto-enabled? | Yes: generic pre-Tahoe model security path; also the fork's Modern-Broadcom/Skywalk paths. | Yes: generic model security path only when model `Max OS Supported < Sonoma`; wireless builder does not enable it. |
| Kext/argument coupling | Coupled in Modern-Broadcom/Skywalk paths; otherwise managed independently in `BuildSecurity`. | Independent: kext can be enabled, but `-amfipassbeta` is never added. |
| Source locations | `oclp_plus/efi_builder/security.py`; `oclp_plus/efi_builder/networking/wireless.py`; removal in `oclp_plus/efi_builder/build.py` history | `oclp_mod/efi_builder/build.py`; `oclp_mod/efi_builder/graphics_audio.py`; `oclp_mod/efi_builder/security.py` |

Both exact AMFIPass archives are byte-identical to KGP's retained artifact: archive SHA-256 `07b266145906db41f4b13a7938fbb173ea28888cc1fa65f84417f8820adc961e`, `CFBundleVersion` 1.4.1, principal executable SHA-256 `4c35bc196d35c69b5f9dca83fe733801211c7828716f51585c7f5450039ca884`.

## KGP pre-implementation enumeration

There was exactly one KGP builder call that could change AMFIPass from disabled to enabled:

| Source | Function | Exact condition | Tahoe relevance | Resulting boot arguments before change |
|---|---|---|---|---|
| `opencore_legacy_patcher/efi_builder/security.py` | `BuildSecurity._build()` | `smbios_data.smbios_dictionary[model]["Max OS Supported"] < os_data.os_data.sonoma` | inherited older-model Universal Builder path; not KGP's claimed Hackintosh compatibility surface | AMFIPass enabled, global `-lilubetaall` already present, no automatically generated `-amfipassbeta` |

`payloads/Config/config.plist` contains the disabled AMFIPass template entry; it is not an enabler. No KGP networking, audio, GUI, or root-patch path calls `enable_kext()` for AMFIPass. Root-patch detection only checks whether `com.dhinakg.AMFIPass` is loaded and does not generate EFI state.

## OCLP-Plus 3.2.2

### `-lilubetaall`

The exact current source contains no automatic `-lilubetaall` injection. `BuildOpenCore._build_efi()` enables Lilu at `oclp_plus/efi_builder/build.py:66-68`, then directly dispatches builders at lines 70-82.

This is an explicit fork change, not merely absent code. Plus commit `92778db877539fbe771aec0fae753a65b1ccb0ca` (“Cleanup config.plist and update AMFI boot arguments,” 2026-04-13) deletes the unconditional `-lilubetaall` append from `BuildOpenCore._build_efi()` and deletes the inherited AppleALC-conditional append from `BuildGraphicsAudio._audio_handling()`. The commit message calls the argument redundant.

Result: **no Plus source path auto-adds `-lilubetaall`.** A user could still place it manually in a pre-existing/custom configuration, but the generator does not add it.

### `-amfipassbeta`

Plus automatically adds `-amfipassbeta`, with a duplicate guard, in these exact paths:

1. `oclp_plus/efi_builder/security.py`, `BuildSecurity._build()`, lines 42-47: when `sip_status is False` **or** `custom_sip_value` is non-empty.
2. Same function, lines 74-80: when `disable_cs_lv is True` **and** `disable_amfi is True`.
3. `oclp_plus/efi_builder/networking/wireless.py`, `BuildWirelessNetworking._on_model()`, lines 54-81: when detected Wi-Fi is Broadcom and its chipset is `AirportBrcmNIC`, `AirPortBrcm4360`, or `AppleBCMWLANBusInterfacePCIe`. The same block enables AMFIPass, assigns MinKernel 23 for the first two or 25 for the T2-modern class, then adds the argument.
4. Same file, `BuildWirelessNetworking._prebuilt_assumption()`, lines 168-189: when model metadata has one of those three Modern-Broadcom classes. This also enables AMFIPass and adds the argument.

AMFIPass itself is also enabled independently by `BuildSecurity._build()` at `security.py:95-97` for any model whose `Max OS Supported` is earlier than Tahoe. Consequently, Plus's kext and argument are tightly coupled in its Modern-Broadcom path but are not represented by one global invariant across all security/model paths.

### Deterministic generated result

The exact base template boot arguments are `keepsyms=1 debug=0x100`. No current-tag generated-config fixture is present in the local Plus audit copy. Static traversal of a Modern-Broadcom path deterministically yields at least:

`keepsyms=1 debug=0x100 -amfipassbeta`

with no automatic `-lilubetaall`; unrelated model/debug/country/WOWL conditions may append additional arguments. For Plus's MacPro7,1 metadata, `Max OS Supported = Sequoia` and `Wireless Model = AppleBCMWLANBusInterfacePCIe`, so both the security and wireless criteria apply, while the duplicate guard keeps one `-amfipassbeta` token.

## OCLP-Mod 3.1.9

### `-lilubetaall`

`oclp_mod/efi_builder/build.py`, `BuildOpenCore._build_efi()`, lines 66-71, enables Lilu then unconditionally appends ` -lilubetaall` before any component-specific builder runs. There is no model, OS, hardware, plugin, debug, or root-patch condition around it.

`oclp_mod/efi_builder/graphics_audio.py`, `BuildGraphicsAudio._audio_handling()`, lines 354-357, additionally says that if AppleALC is enabled and the argument is absent, it should append it. Because the unconditional builder append runs first, this path normally makes no second change. The inherited code has **not** been removed or disabled in Mod.

### `-amfipassbeta`

There is no `-amfipassbeta` string anywhere in the exact `oclp_mod` source or Config template. `BuildSecurity._build()` retains different legacy behavior:

- at `oclp_mod/efi_builder/security.py:42-46`, lowered/custom SIP appends `ipc_control_port_options=0`;
- at lines 72-77, `disable_cs_lv and disable_amfi` appends `amfi=0x80`;
- at lines 91-93, AMFIPass is enabled only when model `Max OS Supported < Sonoma`.

The Mod wireless builder enables IOSkywalkFamily/IO80211FamilyLegacy for `AirportBrcmNIC` and `AirPortBrcm4360`, but does not enable AMFIPass and does not add `-amfipassbeta`. Mod's changelog says AMFIPass should load normally and tells users to add `-lilubetaall` or `-amfipassbeta` if they cannot boot. That is manual/operational guidance, not automatic injection.

Thus Mod supports and may auto-enable AMFIPass 1.4.1, but the kext and `-amfipassbeta` are managed independently; automatic kext enablement does not imply automatic argument injection.

### Deterministic generated result

The exact base template is also `keepsyms=1 debug=0x100`. No current-tag generated-config fixture is present in the local Mod audit copy. Every Mod builder execution deterministically first yields at least:

`keepsyms=1 debug=0x100 -lilubetaall`

and never automatically appends `-amfipassbeta`; unrelated conditions may append other arguments. For Mod's MacPro7,1 metadata, `Max OS Supported = max_os`, so the generic pre-Sonoma AMFIPass condition is false; its wireless builder also lacks Plus's T2-modern AMFIPass path.

## Final KGP v2.0 policy

KGP intentionally adopts neither fork verbatim:

- automatic/global `-lilubetaall` injection was removed from `BuildOpenCore._build_efi()`;
- the inherited AppleALC-specific beta-override append was also removed;
- `BuildOpenCore._apply_amfipass_boot_arg_policy()` runs after every component builder and observes the final `AMFIPass.kext` state;
- if AMFIPass is enabled and the exact `-amfipassbeta` token is absent, it appends the token once;
- if AMFIPass is disabled, it adds nothing;
- it never strips user-supplied `-lilubetaall` or `-amfipassbeta`.

This is smaller and more complete than Plus's dispersed partial coupling, while avoiding Mod's global Lilu override and independent AMFIPass state.

## KGP Phase-1 preservation check

The following checks pass against original HEAD `ec5e591e0f46e948b0258ef1c8ed5d17d6a2c865`:

| Required invariant | Evidence/result |
|---|---|
| Modern Wireless detection and dictionaries | complete `opencore_legacy_patcher/sys_patch` diff is empty; Modern Wireless source remains `fa0dad681239c2268d17d81a9d8f422dc359d5d2b8b9fe670f2f12d4f3485f97` |
| Modern Audio dictionary | complete `sys_patch` diff is empty; Modern Audio source remains `a24581ef94b304d2252bc9db9d181a20332fe6621801dadf9bd5cb3339d2615d` |
| PatcherSupportPkg identity/content | version remains `2.0.0-tahoe-restored.1`; `Universal-Binaries.dmg` remains `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4` |
| IO80211FamilyLegacy | archive remains `e681dcc76a2cd2cea4b0ad5f27a3c816055fde3cdccd890dd10a3e2c84e96d93` |
| IOSkywalkFamily | archive remains `1e12b7ef42f55b39ea54ada97b46331220668b2c48a28656e9875c5145fe2479` |
| Beta-1 AppleHDA | retained executable `6bf19c385a1212160be8a01fd7903aaa0416407e0b52e949f49d04cee4c65de7`; `__text` `135b98fbccd0c8cd742b50f01a563054eef506f81bcc7799b5fb6429df063096` |
| KDK requirements/selection | complete `opencore_legacy_patcher/support` diff is empty; root-patch sources are unchanged |
| AMFIPass handling | enablement criteria in `efi_builder/security.py`, networking builder, detection, and patch detection are unchanged; only the centralized final-state argument invariant was added; version/archive/executable remain exact 1.4.1 identities above |
| SIP requirements | security builder, AMFI/SIP detection, patch validation, and all `sys_patch` logic are unchanged |
| Root-patch destinations | all patch dictionaries and root-patch code are under the unchanged `sys_patch` tree |

The component refresh therefore does not alter KGP's primary Tahoe Hackintosh root-patching detection, payload, or application workflow. The boot-argument policy affects only newly generated Universal Builder configurations.

## Policy fixtures

| Case | AMFIPass entries enabled | `-amfipassbeta` count | `-lilubetaall` count | Result |
|---|---:|---:|---:|---|
| ordinary inherited AMFIPass path | 1 | 1 | 0 | PASS |
| repeated AMFIPass requests | 1 | 1 | 0 | PASS |
| no AMFIPass (`MacPro7,1` external model fixture) | 0 | 0 | 0 | PASS |
| pre-existing `-amfipassbeta` plus unrelated marker | 1 | 1 | 0 | PASS; no duplicate, marker preserved |
| pre-existing `-lilubetaall` plus unrelated marker | 1 | 1 | 1 | PASS; explicit beta token preserved |

Every policy fixture passes official OpenCore 1.0.7 `ocvalidate`. A seven-case before/after component matrix is identical after applying only the two approved argument transformations to baseline. No component enablement predicate changed.

Final policy:

- Plus 3.2.2: no automatic `-lilubetaall`; conditional/partial `-amfipassbeta` coupling.
- Mod 3.1.9: automatic global `-lilubetaall`; no automatic `-amfipassbeta`; AMFIPass independent.
- KGP v2.0: no automatic `-lilubetaall`; centralized exact-token `-amfipassbeta` coupling to final AMFIPass state.
