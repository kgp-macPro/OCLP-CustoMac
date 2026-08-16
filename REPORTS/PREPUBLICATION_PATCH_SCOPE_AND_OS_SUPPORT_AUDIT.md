# Pre-publication patch-scope, genuine-Mac, and OS-support audit

Audit date: 2026-08-15
Repository: `/Users/kgp/Developer/OCLP-amfipassbeta-v2.0-development`
Audited documentation HEAD: `cf77e6f7e4307154aafe856f81b174f9bee6466f`
Canonical Phase-5 implementation: `13a8aeaaaa877b197b54cf6f8452a5801d7e36ff`

## Executive conclusion

The frozen Phase-5 source is already configured to produce only the intended two top-level root-patch families:

- `Networking: Modern Wireless`;
- `Miscellaneous: Modern Audio`.

This is enforced by the existing `HardwarePatchsetDetection._hardware_variants` registration list in `opencore_legacy_patcher/sys_patch/patchsets/detect.py:118-149`. All other inherited detectors are retained in source but commented out of that list; `AMDNavi` is not imported or registered. No new allowlist, planner, or genuine-Mac branch is needed. In fact, changing the registry now would be a regression: the desired public configuration is the current configuration.

That conclusion is stronger than the GUI alone. The Phase-3 selection model preserves unknown/nonselectable families by design. If an inherited detector were re-registered, it could pass through without either Modern Wi-Fi or Modern Audio checkbox controlling it. The registry is therefore the operative product-scope switch, and it must remain frozen with exactly the two active entries.

The source is not globally Tahoe-only. Ordinary root-patch validation permits Darwin 20 through Darwin 25. The active families behave as follows:

- Darwin 20-22: neither active family needs a patch;
- Darwin 23/Sonoma: Modern Wireless can patch supported Broadcom or Intel hardware using the complete `13.7.2-23` payload set; Modern Audio is native;
- Darwin 24/Sequoia: Modern Wireless can patch supported Broadcom or Intel hardware using the complete `13.7.2-24` payload set; Modern Audio is native;
- Darwin 25/Tahoe: Modern Wireless uses `13.7.2-25`; Modern Audio uses `26.0 Beta 1/AppleHDA.kext` and requires a permitted KDK; this is the runtime-validated release target;
- Darwin 26/Golden Gate: the root patcher is globally rejected by the unsupported-host-OS validation before either the no-KDK or KDK path can be authorized. The separate Darwin-26 KDK prohibition is defense in depth, not the sole global gate.

Recommendation: publish the first OCLP-CustoMac release as Tahoe-only. Sonoma and Sequoia have coherent source/resource Modern Wireless paths, but KGP has not runtime-validated those OS paths in the frozen project. Do not advertise them until controlled hardware testing is complete.

## 1. How the current patch plan is formed

The authoritative flow is:

1. `HardwarePatchsetDetection.__init__()` constructs the fixed `_hardware_variants` registry.
2. `_detect()` instantiates only registered classes, then excludes an item when `present()` is false or `native_os()` is true.
3. `applicable_patchsets` records those surviving hardware family names.
4. `RootPatchSelection` selects applicable Modern Wi-Fi/Audio families and defaults all applicable choices on for a clean operation.
5. The detector's second pass aggregates SIP, AMFI, KDK, Metallib, network, and other requirements only from selected hardware.
6. The third pass calls `patches()` only for the selected registered hardware and builds the final patch dictionary.
7. GUI display, click-time validation, pre-download validation, and `PatchSysVolume.start_patch()` recompute this result. `PatchSysVolume` compares the semantic patch names with the expected selection before mounting or mutation.
8. `PatchSysVolume._patch_root_vol()` passes that dictionary to `_execute_patchset()`, which reads payloads from `constants.payload_local_binaries_root_path` and ultimately performs the existing KC/snapshot workflow.

Important call sites are `detect.py:118-149, 462-557`, `root_selection.py:26-128`, `gui_sys_patch_display.py:142-177, 345-426`, `gui_sys_patch_start.py:76-132, 430-489`, and `sys_patch.py:119-153, 690-776`.

Every production entry found—GUI, CLI, auto-patcher, update caching, and `PatchSysVolume`—uses `HardwarePatchsetDetection`. No alternate detector or direct dormant-family route was found. The fallback at `sys_patch.py:490` also creates a new `HardwarePatchsetDetection`, so it is subject to the same two-entry registry.

`ModernWireless.present()` itself has one consumer: the first pass in `HardwarePatchsetDetection._detect()`. All higher-level consumers receive the detector result. The detector construction sites are `support/validation.py:130`, `sys_patch/auto_patcher/start.py:148`, `sys_patch/sys_patch.py:122,132,490,702,790`, `wx_gui/gui_cache_os_update.py:46`, `wx_gui/gui_entry.py:68`, `wx_gui/gui_sys_patch_display.py:146,350`, and `wx_gui/gui_sys_patch_start.py:76,87,104`. None calls Modern Wireless or a dormant detector directly.

### Critical Phase-3 pass-through detail

`RootPatchSelection.is_hardware_patchset_selected()` returns `True` for an unrecognized hardware-family name, and `filter_patch_dictionary()` preserves patch names not mapped to Modern Wi-Fi or Modern Audio. This is intentional compatibility for direct/internal paths and for other KDK-requiring patches. It also means the GUI selectors are not a general patch-family allowlist.

Therefore:

- today, dormant families cannot bypass the selectors because they never enter detection;
- re-registering a dormant family would make it reachable and would let it pass through the Phase-3 selector layer;
- publication must preserve the current detector registry, not rely only on the two-checkbox UI.

## 2. Complete current patch-family configuration matrix

“Registered” below means present in `_hardware_variants`, the existing OCLP detector-registration configuration. “Dormant” means the implementation remains in source but the registry entry is commented out. Native/KDK descriptions summarize each class's existing `present()`, `native_os()`, and resource requirements; they are not active product behavior while the class is dormant.

Source paths in the table are relative to `opencore_legacy_patcher/sys_patch/patchsets/`.

| Public family / class | Source | Existing applicability and OS condition | KDK / Metallib | Payload source and frozen-resource observation | Current final-plan reachability | Phase-3 selectors |
|---|---|---|---|---|---|---|
| Graphics: Intel Iron Lake / `IntelIronLake` | `hardware/graphics/intel_iron_lake.py` | Iron Lake GPU; non-native Mojave+ | KDK Ventura+ | inherited 10.13.6/non-Metal/WebKit branches; referenced files present in the audited local PSP tree for Darwin 20-24 | Dormant | Would bypass both |
| Graphics: Intel Sandy Bridge / `IntelSandyBridge` | `hardware/graphics/intel_sandy_bridge.py` | Sandy Bridge GPU; non-native Mojave+ | KDK Ventura+ | inherited 10.13.6/non-Metal/GVA/OpenCL/WebKit; audited references present for 20-24 | Dormant | Would bypass both |
| Graphics: Intel Ivy Bridge / `IntelIvyBridge` | `hardware/graphics/intel_ivy_bridge.py` | Ivy Bridge GPU; non-native Monterey+ | no KDK; Metallib Sequoia+ | 11.7.10, Metal 3802, GVA/OpenCL/WebKit branches; audited references present through 24 | Dormant | Would bypass both |
| Graphics: Intel Haswell / `IntelHaswell` | `hardware/graphics/intel_haswell.py` | Haswell GPU; non-native Ventura+ | no KDK; Metallib Sequoia+ | 12.5, Metal 3802, GVA/OpenCL branches; audited references present through 24 | Dormant | Would bypass both |
| Graphics: Intel Broadwell / `IntelBroadwell` | `hardware/graphics/intel_broadwell.py` | Broadwell GPU; non-native Ventura+ | no KDK/Metallib flag | 12.5/RenderBox branches; `12.5-25` and `RenderBox-25` references required by the dormant Tahoe path are absent from the audited PSP tree | Dormant | Would bypass both |
| Graphics: Intel Skylake / `IntelSkylake` | `hardware/graphics/intel_skylake.py` | Skylake GPU; non-native Ventura+ | no KDK/Metallib flag | 12.5/RenderBox branches; `12.5-25` and `RenderBox-25` references required by the dormant Tahoe path are absent | Dormant | Would bypass both |
| Graphics: Nvidia Tesla / `NvidiaTesla` | `hardware/graphics/nvidia_tesla.py` | Tesla GPU; non-native Mojave+ | KDK Ventura+ | inherited non-Metal/WebKit and Tesla resources; audited references present through 24 | Dormant | Would bypass both |
| Graphics: Nvidia Kepler / `NvidiaKepler` | `hardware/graphics/nvidia_kepler.py` | Kepler GPU; nuanced Monterey boundary, non-native after support removal | no KDK; Metallib Sequoia+ | Kepler/Metal 3802 branches; audited references present through 24 | Dormant | Would bypass both |
| Graphics: Nvidia Web Drivers / `NvidiaWebDriver` | `hardware/graphics/nvidia_webdriver.py` | Fermi/Maxwell/Pascal; non-native Mojave+ plus WebDriver prerequisites | KDK Ventura+ | WebDriver, non-Metal, enforcement, CoreDisplay and framework branches; audited references present through 24 | Dormant | Would bypass both |
| Graphics: AMD TeraScale 1 / `AMDTeraScale1` | `hardware/graphics/amd_terascale_1.py` | TeraScale 1 GPU; non-native Mojave+ | KDK Ventura+ | TS1/non-Metal inherited branches; audited references present through 24 | Dormant | Would bypass both |
| Graphics: AMD TeraScale 2 / `AMDTeraScale2` | `hardware/graphics/amd_terascale_2.py` | TeraScale 2 GPU; non-native Mojave+ | KDK Ventura+ | TS2/non-Metal inherited branches; audited references present through 24 | Dormant | Would bypass both |
| Graphics: AMD Legacy GCN / `AMDLegacyGCN` | `hardware/graphics/amd_legacy_gcn.py` | GCN 7000/8000/9000 with CPU/model conditions; non-native Ventura+ | KDK Ventura+ | 12.5/GCN/RenderBox branches; `RenderBox-25` is absent for dormant Tahoe path | Dormant | Would bypass both |
| Graphics: AMD Polaris / `AMDPolaris` | `hardware/graphics/amd_polaris.py` | Polaris with AVX2/model conditions; non-native Ventura+ | KDK Ventura+ | 12.5/GCN/RenderBox; Tahoe `12.5-25` driver and `RenderBox-25` references are absent | Dormant | Would bypass both |
| Graphics: AMD Vega / `AMDVega` | `hardware/graphics/amd_vega.py` | Vega with non-AVX2 conditions; non-native Ventura+ | KDK Ventura+ | 12.5/RenderBox; Tahoe `12.5-25` driver and `RenderBox-25` references are absent | Dormant | Would bypass both |
| Graphics: AMD Navi / `AMDNavi` | `hardware/graphics/amd_navi.py` | Navi/non-AVX2 and Dortania-internal check; non-native Ventura+ | KDK Ventura+ | 12.5/RenderBox; Tahoe roots absent as above | Not imported or registered | Would bypass both |
| Networking: Legacy Wireless / `LegacyWireless` | `hardware/networking/legacy_wireless.py` | Broadcom 4331/43224 or Atheros40; non-native Monterey+ | no KDK | 11.7.10 and 12.7.2 variants; dormant Tahoe `12.7.2-25` resource branch is absent | Dormant | Would bypass both |
| **Networking: Modern Wireless / `ModernWireless`** | `hardware/networking/modern_wireless.py` | supported Broadcom chipset or Phase-5 Intel `AirportItlwm` identity; non-native Sonoma+ | **no KDK** | `13.7.2-23/-24/-25`; exact required resources present; no `-26` resource | **Registered and reachable** | **Modern Wi-Fi** |
| Miscellaneous: Legacy Audio / `LegacyAudio` | `hardware/misc/legacy_audio.py` | old specified Apple models/AppleALC condition; non-native from Sierra or Mojave depending model | no KDK | 10.11.6/10.13.6 audio resources present | Dormant | Would bypass both |
| **Miscellaneous: Modern Audio / `ModernAudio`** | `hardware/misc/modern_audio.py` | always physically present, but native before Tahoe and on build 25A5279m | **KDK required when applicable** | `26.0 Beta 1/AppleHDA.kext`, present | **Registered and reachable** | **Modern Audio** |
| Miscellaneous: Legacy Backlight Control / `DisplayBacklight` | `hardware/misc/display_backlight.py` | explicit old-model list; non-native High Sierra+ | KDK Ventura+ | 10.12.6 resources present | Dormant | Would bypass both |
| Miscellaneous: Legacy GMUX / `GraphicsMultiplexer` | `hardware/misc/gmux.py` | MacBookPro8,2/8,3 plus demux evidence; non-native Sierra+ | KDK Ventura+ | 10.12.6 resources present | Dormant | Would bypass both |
| Miscellaneous: Legacy Keyboard Backlight / `KeyboardBacklight` | `hardware/misc/keyboard_backlight.py` | MacBook plus legacy GPU architecture; non-native Big Sur+ | KDK Ventura+ | execute-only defaults command; no payload file | Dormant | Would bypass both |
| Miscellaneous: PCIe FaceTime Camera / `PCIeFaceTimeCamera` | `hardware/misc/pcie_webcam.py` | probed PCIe camera; non-native Sonoma+ except 23A5257q | no KDK | 14.0 Beta 1 camera resources present | Dormant | Would bypass both |
| Miscellaneous: T1 Security Chip / `T1SecurityChip` | `hardware/misc/t1_security.py` | probed T1; non-native Sonoma+ | no KDK | 13.6/13.7.1/14.7.2/15.x branches; dormant `13.7.1-25` SharedUtils branch is absent | Dormant | Would bypass both |
| Miscellaneous: Legacy USB 1.1 / `USB11Controller` | `hardware/misc/usb11.py` | UHCI/OHCI; Hackintosh or specified old Apple models; non-native Ventura+ | no KDK | 12.6.2/14.5/14.6.1 resources present | Dormant | Would bypass both |
| Miscellaneous: Legacy CPUs (Lacking AVX) / `CPUMissingAVX` | `hardware/misc/cpu_missing_avx.py` | no AVX, Ventura only, and no legacy/modern wireless family already present | no KDK | `13.7.2-22/IO80211.framework`, present | Dormant | Would bypass both |

The local payload check above evaluated patch-source references produced across Darwin 20-26 and all bundled example hardware against the available extracted `PatcherSupportPkg-lzhoang2801/Universal-Binaries` reference. It is useful evidence about inherited resource retention, but only registered classes are covered by the frozen application's built-in `validation=True` sweep. Therefore dormant payloads are not a supported/certified frozen-product contract. The concrete Tahoe omissions make this distinction important.

### Shared/subordinate patch modules are not top-level families

`patchsets/shared_patches/` contains these reusable modules/classes: `AMDOpenCL`, `AMDTeraScale`, `BigSurGVA`, `BigSurOpenCL`, `HighSierraGVA`, `LegacyMetal31001`, `LegacyMetal3802`, `MontereyGVA`, `MontereyOpenCL`, `MontereyWebKit`, `NonMetal`, `NonMetalCoreDisplay`, `NonMetalEnforcement`, and `NonMetalIOAccelerator`. They have no independent detector entry. They enter a final plan only when a top-level graphics class merges them into `patches()`. Since every graphics detector is dormant, none is independently reachable.

## 3. Current versus desired configuration

| Patch family | Current registry | Desired OCLP-CustoMac | Existing switch/condition and proposed value |
|---|---:|---:|---|
| Modern Wireless | Enabled | Enabled when applicable | `detect.py:_hardware_variants` contains `modern_wireless.ModernWireless`; **no change** |
| Modern Audio / AppleHDA | Enabled | Enabled when applicable | registry contains `modern_audio.ModernAudio`; **no change** |
| Intel graphics (Iron Lake through Skylake) | Disabled | Disabled | entries commented out; **no change** |
| Nvidia graphics (Tesla, Kepler, Web Drivers) | Disabled | Disabled | entries commented out; **no change** |
| AMD graphics (TeraScale, GCN, Polaris, Vega) | Disabled | Disabled | entries commented out; **no change** |
| AMD Navi | Disabled/not registered | Disabled | not imported/registered; **no change** |
| Non-Metal/Metal compatibility/shared graphics | Indirectly disabled | Disabled | no registered parent detector can request them; **no change** |
| Legacy Wireless | Disabled | Disabled | registry entry commented out; **no change** |
| Legacy Audio | Disabled | Disabled | registry entry commented out; **no change** |
| Backlight, GMUX, keyboard backlight | Disabled | Disabled | registry entries commented out; **no change** |
| PCIe camera, T1, USB 1.1, missing-AVX | Disabled | Disabled | registry entries commented out; **no change** |

There is no per-family global preference or declarative boolean separate from detector registration. The fixed registration list is the existing architecture's configuration gate. The exact list already has the desired value. The minimal configuration-only implementation plan is therefore **zero functional changes**: preserve and test the existing list. A useful publication regression test would assert the exact registered class tuple and assert that every final dictionary key belongs to the Modern Wireless or Modern Audio closure; that is a test hardening proposal, not a new planner.

## 4. Genuine Apple hardware behavior

### Detection and gating

- `application_entry.py:83-85` sets `host_is_hackintosh=True` only when the probed firmware vendor exists and is not `Apple`. Apple firmware remains on the genuine path.
- There is no genuine-Mac prohibition in `HardwarePatchsetDetection`, the Root Patch Selection GUI, `PatchSysVolume.start_patch()`, or the state classifier.
- `CheckProperties.host_can_build()` in `gui_support.py:141-154` governs **OpenCore configuration building**, not root patching. Its model list and `allow_oc_everywhere` setting do not gate root-patch detection.
- `gui_main_menu.py:183-187` independently disables “Build and Install OpenCore” when the host cannot build and disables “Post-Install Root Patch” only below Big Sur.
- Model, board-ID, GPU, USB, T1, and legacy hardware predicates remain in dormant classes but are never instantiated by the current root detector.
- Active Modern Wireless detection is hardware-probe based. Active Modern Audio is OS/build based and deliberately applies on Tahoe regardless of model.
- The automatic patcher skips Hackintosh hosts at `auto_patcher/start.py:266-267`; this is not a genuine-Mac rejection and does not affect manual root patching.

Consequently, genuine Intel Macs remain technically unblocked. They receive exactly the same two-family scope as a Custom Mac because both use the same registry and final-plan pipeline. This supports the intended policy: public positioning may remain Custom-Mac focused without adding an artificial Apple-hardware block.

### Representative Tahoe simulations

These are source/model simulations, not runtime support claims. Results assume a clean root and the normal Phase-3 default-on selection.

| Representative genuine Mac | Probed/source facts | Current applicable and final patch dictionary on Darwin 25 | KDK | Unrelated inherited patches |
|---|---|---|---|---|
| MacPro7,1 | Model alone does not determine active Wi-Fi. A stock modern Apple wireless device classified outside the supported Modern Wireless chipsets does not match; a supported replacement would match. | Stock-like unmatched Wi-Fi: `Modern Audio` only. Supported replacement: `Modern Wireless` + `Modern Audio`. | Yes whenever Audio is selected | None; model/GPU families are unregistered |
| iMac20,1 (modern genuine control) | Bundled fixture has Broadcom 0x4464 classified `AppleBCMWLANBusInterfacePCIe`, not a ModernWireless-supported enum | `Modern Audio` only | Yes | None, despite inherited graphics source |
| MacBookPro9,2 (older Ivy/non-Metal candidate in upstream OCLP) | Bundled fixture has Ivy Bridge GPU and Broadcom 0x4331 classified `AirPortBrcm4360` | `Modern Wireless` + `Modern Audio` | Yes due only to Audio | Ivy graphics, keyboard/backlight, USB and other inherited candidates do not run |
| MacBookPro11,1 (supported-wireless genuine example) | Bundled fixture has Broadcom 0x43a0 classified `AirportBrcmNIC` | `Modern Wireless` + `Modern Audio` | Yes due only to Audio | Haswell graphics remains dormant |
| Genuine Intel Mac with no supported Modern Wireless device | ModernAudio `present()` is unconditional and non-native on normal Tahoe builds | `Modern Audio` | Yes | None |

On Tahoe Beta 1 build `25A5279m`, Modern Audio is intentionally treated as native. A supported Modern Wireless device would therefore produce Wi-Fi only and no KDK requirement from these families.

No representative genuine Mac can currently cause an unrelated graphics/legacy patch to reach `PatchSysVolume`. Some dormant Tahoe dictionaries refer to absent resource branches, but those classes are not instantiated. This is precisely why the current registration list must remain frozen.

## 5. Modern Wireless and Modern Audio dependency closure

### Modern Wireless

Top-level detector: `ModernWireless`.

Hardware applicability is supported Broadcom **or** a Phase-5 Intel card whose authentic vendor/device identity maps to `IntelWirelessCard.Chipsets.AirportItlwm`. Intel runtime binding remains external EFI/AirportItlwm behavior; it is not a root-patch dependency installed by OCLP.

Patch closure:

- all non-native supported OSes: `Modern Wireless`
  - `/usr/libexec/wifip2pd`;
  - `/System/Library/PrivateFrameworks/IO80211.framework`;
  - `/System/Library/PrivateFrameworks/WiFiPeerToPeer.framework`;
- Sonoma only: `Modern Wireless Extended`
  - `/usr/libexec/airportd`;
  - `/System/Library/Frameworks/CoreWLAN.framework`;
  - `/System/Library/PrivateFrameworks/CoreWiFi.framework`.

There is no top-level graphics, Legacy Wireless, IOSkywalkFamily, IO80211FamilyLegacy, EFI, spoof, ACPI, DMAR, or DeviceProperties dependency in this dictionary. The generic root engine still supplies ordinary support-image mounting, root-volume copying, AMFI/SIP preflight, AuxiliaryKC handling when appropriate, and snapshot creation. Those are shared operations, not extra patch families.

Modern Wireless returns `requires_kernel_debug_kit=False`; Wi-Fi-only remains no-KDK on Sonoma, Sequoia, and Tahoe.

### Modern Audio

Top-level detector: `ModernAudio`.

Patch closure on normal Tahoe builds:

- `Modern Audio`;
- overwrite `/System/Library/Extensions/AppleHDA.kext` from `26.0 Beta 1`;
- KDK discovery/install/reuse and KDK merge via the existing shared KDK path;
- Boot/System KC rebuild and normal snapshot workflow.

It does not depend on Modern Wireless or any dormant audio/graphics family. KDK merge and KC rebuild are required operations, not patch families. Audio deselection therefore removes AppleHDA and removes a KDK requirement caused solely by Audio, while any independently selected future KDK-requiring registered family would still aggregate normally.

## 6. Source-derived OS support boundaries

### Global gates

- The PyInstaller specification declares `LSMinimumSystemVersion=10.10.0` and there is no application-level maximum-OS startup gate.
- The main-menu Root Patch button is disabled below Darwin 20/Big Sur.
- `HardwarePatchsetDetection._validation_check_unsupported_host_os()` authorizes ordinary root patching only for Darwin 20 through Darwin 25. A hidden Dortania developer marker bypass exists for internal development; it is not public behavior.
- Thus “the application can launch” and “root patching is authorized” are separate questions. The locked packaged runtime was not tested on older releases merely because the bundle declaration permits launch.
- Compatible loaded AMFIPass (`>=1.2.1`; frozen component `1.4.1`) overrides the patch families' AMFI requirement to `NO_CHECK`. The EFI builder's `-amfipassbeta` coupling is not Darwin-specific. This mechanism was runtime validated on Tahoe only.
- Root snapshot/KC code has inherited Big Sur+ branches. For the active no-kext Modern Wireless path on Ventura+, `skip_root_kmutil_requirement` follows the selected KDK requirement; Audio on Tahoe takes the full KDK/KC path.

### Complete matrix

| Darwin | macOS | App source gate | Root patch global gate | Modern Wireless | Modern Audio | Resources / KDK / KC | Unrelated families | Assessment | Runtime proven | Public recommendation |
|---:|---|---|---|---|---|---|---|---|---|---|
| <20 | Catalina and older | Bundle declares launch down to 10.10; actual frozen binary not validated | Blocked; main-menu button below Big Sur disabled | Native/not requested | Native/not requested | no active plan | Registry still only two | Not reachable for root patch | No | Do not claim |
| 20 | Big Sur | No source upper block | Allowed | `native_os=True`; none | `native_os=True`; none | empty plan; no KDK | None | No active OCLP-CustoMac patch needed | No | Do not claim as a patch target |
| 21 | Monterey | No source upper block | Allowed | native; none | native; none | empty plan; no KDK | None | No active patch needed | No | Do not claim as a patch target |
| 22 | Ventura | No source upper block | Allowed | native; none | native; none | empty plan; no KDK | None | No active patch needed | No | Do not claim as a patch target |
| 23 | Sonoma | Yes | Allowed | Base + Extended; `13.7.2-23` | native; none | complete six-resource Wi-Fi set; no KDK; shared root/AuxKC/snapshot flow | None | **Complete existing Modern Wireless path** | No KGP runtime proof | Technically plausible; do not advertise yet |
| 24 | Sequoia | Yes | Allowed | Base only; `13.7.2-24` | native; none | complete three-resource Wi-Fi set; no KDK; shared root/AuxKC/snapshot flow | None | **Complete existing Modern Wireless path** | No KGP runtime proof recorded | Strong candidate after testing; do not advertise yet |
| 25 | Tahoe | Yes | Allowed | Base only; `13.7.2-25` | `26.0 Beta 1/AppleHDA.kext` except 25A5279m | Wi-Fi no KDK; Audio requires permitted Darwin-25 KDK; both resource sets complete; full runtime path proven | None | Complete | **Yes, Broadcom and Intel** | **Claim in first release** |
| 26 | Golden Gate | App has no startup max | **Blocked as unsupported host OS** | Class could construct `13.7.2-26`, but operation cannot be authorized and resource branch is absent | Class would request AppleHDA/KDK, but operation blocked | Darwin-26 KDKs independently prohibited; no `13.7.2-26` Wi-Fi payload | None active beyond two | Explicitly unsupported/incomplete | No | Do not claim |

For Darwin 20-25, the source accepts a loaded compatible AMFIPass through `_override_amfi_level()`; the frozen AMFIPass version is 1.4.1 and the minimum accepted version is 1.2.1. The EFI builder's exact-token `-amfipassbeta` coupling is not restricted to a Darwin generation. On Darwin 26, neither AMFIPass nor a no-KDK selection bypasses the unsupported-host-OS root-patch gate. This is source reachability only; the AMFIPass/root/KC combination is runtime proven here only on Tahoe.

The active KC/snapshot paths also remain within existing version-aware infrastructure. There is no active patch on Darwin 20-22. Sonoma/Sequoia Modern Wireless has no kext and no KDK requirement, so Ventura+ `skip_root_kmutil_requirement` selects the existing no-primary-KC/Auxiliary handling while the shared APFS snapshot flow remains in use. Tahoe Audio requires the permitted KDK merge and Boot/System KC rebuild; Tahoe Wi-Fi-only retains the validated no-KDK behavior.

### Sequoia deep assessment

Modern Wireless on Darwin 24 is complete in source/resources without new patch logic:

- `native_os()` becomes false from Sonoma onward;
- `_base_patch()` deterministically selects `13.7.2-24`;
- the required `wifip2pd`, `IO80211.framework`, and `WiFiPeerToPeer.framework` paths exist in the audited PSP resource source;
- `_extended_patch()` deliberately returns empty after Sonoma;
- Broadcom and the Phase-5 Intel detector share the same dictionary;
- Intel detection itself has no Darwin restriction beyond `ModernWireless.native_os()` and the global root gate;
- no KDK is required, so Wi-Fi-only remains no-KDK;
- no Tahoe-only selection/KDK assumption is present in the Modern Wireless path.

This is a coherent source-supported path, but it is not KGP runtime validated on Sequoia. Resource presence plus inherited code reachability is not enough for a public support claim.

Modern Audio is intentionally native on Darwin 24. There is no Sequoia AppleHDA root patch to enable, and none is missing: `ModernAudio.native_os()` returns true below Darwin 25. Therefore:

- if “complete Modern Audio path” means a root-patch dictionary, **no**—none is applicable;
- if it means the intended OCLP-CustoMac audio behavior, **yes via native macOS audio**, with no OCLP Audio patch or KDK.

### Sonoma and older assessment

- Sonoma/Darwin 23: category **A, complete existing Modern Wireless path**. It includes the Extended userland/framework set and needs no KDK. Audio is native.
- Ventura/Darwin 22: category **D, no Modern Wireless/Audio patch is relevant** because both classes report native.
- Monterey/Darwin 21: category **D**, same.
- Big Sur/Darwin 20: category **D**, same.
- Catalina and older: category **C, not root-patch reachable** under the current global/main-menu gates.

The lowest generation with a coherent **active Modern Wireless root-patch** architecture is Sonoma/Darwin 23. The first generation on which **both** public controls can represent non-native root-patch families is Tahoe/Darwin 25.

### Golden Gate boundary

Darwin 26 is globally blocked by `UNSUPPORTED_HOST_OS`; it is not merely an Audio/KDK limitation. Even a selected Modern Wireless-only plan that would otherwise need no KDK fails `can_patch` at display, click, and operation revalidation. Separately:

- the dynamic Wi-Fi dictionary would ask for absent `13.7.2-26` resources if the global developer bypass were used;
- a KDK-requiring Audio plan cannot use a build-family-26 KDK due to the canonical KDK eligibility policy.

Therefore Golden Gate is not a hidden no-KDK Wi-Fi target today.

## 7. Phase-2 state and Phase-3 GUI interaction

The current two-entry registry naturally feeds all frozen Phase-2/3 behavior:

- applicable controls default on in `CLEAN`;
- Wi-Fi-only and Audio-only filter only their respective dictionaries;
- both off yields an empty final dictionary, disables Start, and is rejected again at the operation boundary;
- KDK aggregation uses only selected detector objects;
- installed metadata stores `semantic_patch_selection(self.patch_set_dictionary)`, i.e. only executed dictionary keys;
- the state classifier compares installed names with the newly requested final dictionary, independent of which detector classes exist;
- selection changes remain Revert -> reboot -> repatch;
- lifecycle states and recovery authorization consume operation metadata/final dictionaries and assume no particular dormant family;
- Revert authorization is root-state based and unaffected by narrowing detection.

If the detector registry were narrowed from a broader build, valid metadata containing a now-disabled family would naturally become a different/foreign installed selection and require recovery before new patching. In the frozen build no transition is needed because the registry is already narrow.

## 8. Minimal publication implementation plan

No functional patch-scope change is warranted.

1. Preserve `_hardware_variants` with exactly `ModernWireless` and `ModernAudio` registered.
2. Do not uncomment or add any dormant detector.
3. Add a source-level regression assertion for the exact registered class tuple if publication hardening is desired.
4. Add representative genuine-Mac fixture tests showing old GPUs do not add graphics families while active Wi-Fi/Audio still work.
5. Keep the Phase-3 pass-through semantics unchanged; it is compatibility behavior, not the scope boundary.
6. Continue to claim Tahoe only until Sonoma/Sequoia receive controlled runtime validation.

This uses the existing OCLP configuration mechanism and introduces no allowlist, planner, hardware branch, or OS compatibility engine.

## 9. Direct answers

1. **Which root-patch families are currently enabled/reachable?** Only `Networking: Modern Wireless` and `Miscellaneous: Modern Audio`. Their emitted patch names are `Modern Wireless`, Sonoma-only `Modern Wireless Extended`, and `Modern Audio`.
2. **Can all unrelated inherited patches be disabled solely through existing switches/configuration?** Yes. The existing detector-registration list already disables them; they remain in source.
3. **Which exact existing switches must change?** None. Preserve `detect.py:118-149` exactly with only `modern_wireless.ModernWireless` and `modern_audio.ModernAudio` active. There is no separate per-family preference boolean.
4. **Will that leave only Modern Wireless + Modern Audio as possible final families?** Yes—this is already the frozen result. Production paths all use the same detector registry.
5. **Will the same restriction naturally apply to genuine Apple Intel Macs?** Yes. Root detection does not branch by Apple-versus-Hackintosh ownership.
6. **Can genuine Macs remain technically unblocked without claiming support?** Yes. Keep technical execution available, state the product target as Custom Macs, and make no genuine-hardware support promise.
7. **Could a genuine Mac receive unrelated graphics/legacy patches after the proposed configuration?** No, provided the existing registry remains unchanged. Those classes are never instantiated.
8. **Which Darwin generations are currently permitted by source?** Root-patch authorization permits Darwin 20 through 25 inclusive. The bundle declares launch down to macOS 10.10 and has no upper startup gate, but root patching is separately gated. Darwin 26 is rejected.
9. **Is the frozen build Tahoe-only?** No at source level. It permits root-patch evaluation on Big Sur through Tahoe and contains complete Modern Wireless paths for Sonoma and Sequoia. Tahoe alone is runtime validated for this product.
10. **Does Sequoia have a complete Modern Wireless path without new logic?** Yes: supported Broadcom/Intel detection plus `13.7.2-24` base resources, no KDK.
11. **Does Sequoia have a complete Modern Audio path without new logic?** No Modern Audio root patch is applicable because audio is classified native below Tahoe. That is intentional and complete native behavior, not a missing payload path.
12. **What is the lowest macOS generation with a coherent Modern Wireless/Audio architecture?** Sonoma/Darwin 23 for an active Modern Wireless root patch with native audio. Tahoe/Darwin 25 is the first where both selectable patch families can be non-native.
13. **Which OS generations should the first public release claim?** Tahoe/Darwin 25 only.
14. **Which may technically work but should not yet be advertised?** Sonoma/Darwin 23 and Sequoia/Darwin 24 for Modern Wireless; they need controlled runtime validation. Big Sur through Ventura need neither active family and should not be marketed as patch targets.
15. **Smallest safe OCLP-CustoMac branding change?** Change user-visible application/window/menu/About/installer text and `CFBundleName` to `OCLP-CustoMac`, while retaining `OpenCore-Patcher.app`, its executable/package filenames, bundle/package/helper/launch-service identifiers, install paths, preferences, metadata/lifecycle names, and compatibility identities. Repository/update URLs require a separate coordinated publication decision. See `PREPUBLICATION_BRANDING_INVENTORY.md`.

## Audit integrity

No functional source, configuration, README, branding, build artifact, EFI, or runtime state was changed during this audit. No package was built and no root patch/revert operation was invoked.
