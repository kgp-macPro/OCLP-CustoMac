# Pre-publication AppleVTD / IOMMU Feasibility Audit

Date: 2026-08-15

Audit type: read-only feasibility gate; no implementation, build, EFI change, or runtime mutation.

Repository state audited:

- Phase-5 implementation: `13a8aeaaaa877b197b54cf6f8452a5801d7e36ff`
- Phase-5 documentation closure / audit HEAD: `cf77e6f7e4307154aafe856f81b174f9bee6466f`
- AirportItlwm reference: `/Users/kgp/Developer/OpenIntelWireless/itlwm-dexter-awdl`
- AirportItlwm reference HEAD: `0b17225dfbe1b7810b114f8fa9148b09f56d4efd`

## Executive decision

**PUBLISH PHASE-5 GOLDEN STATE FIRST AND CONTINUE APPLEVTD AFTER RELEASE.**

No small, localized OCLP-side change is supported by the inspected source.

- **Broadcom: D — CURRENTLY UNSOLVED / RESEARCH.** The failure boundary is below the Tahoe Modern Wireless root payload, in the Apple PCI/DMA driver and platform IOMMU/DMAR relationship. The closed Apple driver does contain DMA and PCI-resource handling, but the audit found no OCLP-controlled AppleVTD property, entitlement, patch requirement, metadata field, or kernel-collection switch that can be changed with a bounded and justified fix.
- **Intel: C — LARGE / CROSS-PROJECT.** OCLP only restores the shared wireless frameworks. AirportItlwm owns Intel PCI attachment, BAR mapping, interrupts, firmware/ring DMA, and packet DMA addresses. Its source contains a mixed DMA implementation that needs a dedicated active-IOMMU driver audit and physical validation. An OCLP-only change cannot establish Intel AppleVTD compatibility.

AppleVTD support is an additional enhancement, not a missing part of the already runtime-validated Phase-2 through Phase-5 feature contract. Attempting it before publication would put the frozen root-patching, KDK, APFS-image, Broadcom, Intel, audio, and recovery paths at disproportionate risk.

## Runtime facts accepted as the audit boundary

The following KGP observations are treated as established runtime evidence; this audit did not alter or repeat them:

- AppleVTD/IOMMU is enabled at platform level.
- The validated wireless configuration requires `DisableIoMapper=true`.
- With `DisableIoMapper=false`, wireless activation fails in the tested configuration while other major functionality remains operational.
- Phase 2, Phase 3B, Phase 3C, Phase 4, and Phase 5 are runtime validated and frozen.

These observations establish a real IOMMU-sensitive wireless boundary on the KGP platform. They do not, by themselves, identify whether its first cause is an Apple wireless driver, AirportItlwm, a DMAR scope/reserved-region issue, PCI topology, or an interaction among them.

## OCLP Modern Wireless trace

### Detection and root payload

`opencore_legacy_patcher/sys_patch/patchsets/hardware/networking/modern_wireless.py` contains the complete Phase-5 applicability and Tahoe root-patch definition:

- `ModernWireless.present()` (`:28-51`) accepts the frozen Broadcom chipset classes or the AirportItlwm-source-backed Intel class.
- `_base_patch()` (`:67-85`) restores only:
  - `/usr/libexec/wifip2pd`
  - `/System/Library/PrivateFrameworks/IO80211.framework`
  - `/System/Library/PrivateFrameworks/WiFiPeerToPeer.framework`
- `_extended_patch()` (`:87-110`) returns an empty dictionary after Sonoma. On Tahoe, it therefore adds no kernel extension or other driver payload.
- `ModernWireless` inherits `requires_primary_kernel_cache() == False` and `requires_kernel_debug_kit() == False` from `sys_patch/patchsets/hardware/base.py:95-107`.

The Tahoe Modern Wireless root patch is consequently a user-space/service/framework restoration. It does not replace the PCI Wi-Fi driver that allocates or programs DMA.

The class is registered with the normal hardware detector at `sys_patch/patchsets/detect.py:137`; `_detect()` evaluates `present()` while building applicable hardware at `:462-490`. The only other production use of the same predicate is `sys_patch/patchsets/hardware/misc/cpu_missing_avx.py:58`, where it contributes to that patchset's existing OS-support decision. Neither caller adds an AppleVTD condition or changes PCI/DMA state.

### Broadcom boot driver relationship

The distinct EFI-builder path is in `opencore_legacy_patcher/efi_builder/networking/wireless.py`:

- `_on_model()` (`:45-85`) enables `IOSkywalkFamily.kext`, `IO80211FamilyLegacy.kext`, and its `AirPortBrcmNIC.kext` plugin for the applicable Broadcom chipset classes, and blocks the native IOSkywalkFamily bundle.
- `_prebuilt_assumption()` repeats the equivalent legacy-family configuration at `:118-122`.
- Country-code handling and historical fake-ID handling exist for specific Broadcom cases at `:59-81` and `_wifi_fake_id()` beginning at `:142`; they are not part of the Tahoe root payload and contain no IOMMU policy.

This builder code prepares an OpenCore configuration. It is not executed as a hidden EFI mutation by the Phase-5 root-patch selection path, and this audit did not run it. KGP's existing EFI remains a frozen external input.

The shipped Broadcom boot payloads were inspected read-only:

- `payloads/Kexts/Wifi/IOSkywalkFamily-v1.2.0.zip`
- `payloads/Kexts/Wifi/IO80211FamilyLegacy-v1.0.0.zip`
- `payloads/Kexts/Acidanthera/AirportBrcmFixup-v2.2.0-RELEASE.zip`

The `AirPortBrcmNIC` personality is an `IOPCIDevice` client and depends on IOPCIFamily, IOSkywalkFamily, and IO80211FamilyLegacy. Its executable contains PCI BAR, MSI/interrupt, DMA-ring, physical-address, `IOBufferMemoryDescriptor`, and `IODMACommand` machinery. IOSkywalkFamily contains `IOMapper`/`IODMACommand` interfaces. None of the inspected bundle metadata or searchable executable symbols exposes an `AppleVTD`, `DisableIoMapper`, `IOMMU`, or `DMAR` setting that OCLP can safely supply or toggle. The driver implementation itself is Apple binary code in the frozen payload.

### Requirements, kernel collections, and metadata

`HardwarePatchsetDetection._detect()` in `sys_patch/patchsets/detect.py:445-564` aggregates patch presence, SIP, AMFI, KDK, MetallibSupportPkg, networking, and related patch prerequisites. It has no AppleVTD/IOMMU requirement or decision.

`generate_patchset_plist()` in `sys_patch/sys_patch_helpers.py:82-153` records patch selection, build provenance, KDK/Metallib provenance, OS identity, and the actual patch dictionary. It records no IOMMU mode and does not affect DMA operation.

The kernel-collection support code only places the patch dictionary's kernel extensions in the required collection and rebuilds the selected collection. Because the Tahoe Modern Wireless root dictionary contains no kext, changing Boot/System versus Auxiliary KC policy would not alter the wireless driver's DMA mapper relationship. No IOMMU policy exists in the KDK merge, KC, snapshot, or root-state paths.

### OpenCore template and source assumptions

The repository OpenCore template has:

- `payloads/Config/config.plist:2468-2471`: `DisableIoMapper=false` and `DisableIoMapperMapping=false`
- `payloads/Config/config.plist:3254-3255`: an empty `ReservedMemory` array

A repository-wide source search found no builder assignment that silently changes either IOMMU quirk and no wireless code referencing AppleVTD, IOMMU, DMAR, `DisableIoMapper`, or `DisableIoMapperMapping`. The only nearby source comments concern unrelated legacy Ethernet/storage fallbacks whose Apple drivers require VT-d; they are not a wireless workaround (`efi_builder/networking/wired.py:89-103`).

Therefore OCLP neither deliberately disables AppleVTD for Modern Wireless nor omits a known local IOMMU patch contract. It presently has no meaningful root-patch control over the observed failure.

## Broadcom assessment — BCM943602CDP

### What is controlled by OCLP

- Broadcom applicability detection.
- The frozen shared Tahoe `wifip2pd` and private-framework root payload.
- In an explicitly requested EFI build, selection of the legacy IOSkywalk/IO80211/AirPortBrcmNIC boot kext stack.

### What is not controlled by the root patch

- AppleVTD domain creation and device attachment.
- DMA address translation used by the Apple AirPortBrcmNIC binary.
- PCI BAR/MSI behavior inside the Apple driver.
- Firmware DMA descriptors inside that driver.
- Firmware/platform DMAR scopes, reserved regions, PCI topology, or OpenCore's live `DisableIoMapper` choice.

The user-space root payload can make the Tahoe wireless API/service surface compatible, but it does not change how BCM943602CDP performs PCI DMA. There is no evidence of a missing root-patch entitlement or plist property. Root-patch metadata and KC selection are descriptive/build mechanisms and do not mediate the IOMMU.

### Feasibility result

**D — CURRENTLY UNSOLVED / RESEARCH.**

An eventual solution might be found in the Apple legacy driver choice, a platform DMAR/topology issue, or their interaction. The current evidence does not distinguish them well enough to name a safe source change. Because the Apple DMA implementation is closed and the required KGP DMAR/XHC14 configuration is frozen, there is no grounded, localized OCLP patch to implement before publication.

This is not a finding that Broadcom AppleVTD is impossible. It is a finding that the present source and runtime evidence do not justify an OCLP-local implementation.

## Intel assessment — AirportItlwm

OCLP's Intel contribution ends at detection/applicability and the same frozen shared Tahoe root payload. Runtime PCI binding is provided by the external AirportItlwm in the user's EFI.

### PCI attachment and resources

In the audited AirportItlwm source:

- `AirportItlwm/AirportItlwm.cpp:1105-1177` starts against an `IOPCIDevice`, initializes the HAL, attaches it to that PCI provider, and attaches the network interface.
- `AirportItlwm/AirportItlwm.cpp:1229-1251` enables PCI bus mastering and memory space and configures PCI power management.
- `AirportItlwm/IOPCIEDeviceWrapper.cpp:60-100` selects the iwx/iwm/iwn HAL and configures MSI/MSI-X capability state.
- `itl80211/compat.cpp:53-69` maps a PCI BAR with `IOPCIDevice::mapDeviceMemoryWithRegister()`.

These are driver-owned operations. The OCLP framework payload does not participate in them.

### DMA implementation

The source demonstrates two materially different paths:

1. Contiguous firmware/ring allocations use mapped I/O virtual addresses:
   - `itlwm/hal_iwx/ItlIwx.cpp:3636-3680` allocates and prepares an `IOBufferMemoryDescriptor`, creates an `IODMACommand` with `kMapped`, calls `gen64IOVMSegments()`, and stores `Segment64.fIOVMAddr` for hardware use.
   - Corresponding implementations exist for iwm (`itlwm/hal_iwm/io.cpp:294-334`) and iwn (`itlwm/hal_iwn/ItlIwn.cpp:1077-1117`).

2. Packet/mbuf paths obtain and program physical-segment cursor addresses:
   - `itl80211/compat.h:200-205` stores an `IOMbufNaturalMemoryCursor` and `IOPhysicalSegment` array in `bus_dmamap`.
   - `itl80211/compat.cpp:175-184,293-300` creates that cursor and uses `getPhysicalSegmentsWithCoalesce()`.
   - `itl80211/compat.cpp:257-266` exposes `getPhysicalAddress()` for a memory descriptor and implements `bus_dmamap_sync()` as a no-op.
   - The AX210-capable iwx RX path obtains mbuf segments and writes their locations into RX descriptors at `ItlIwx.cpp:10435-10504`.
   - The iwx firmware-command mbuf path does the same at `:12470-12502`.
   - The iwx TX path obtains coalesced physical segments and writes their locations to device transfer buffers at `:13032-13085`.
   - Numerous DMA sync/unload calls in the iwx/iwm/iwn ports remain commented or collapse to the no-op compatibility implementation.

This is not proof that any one line causes KGP's `DisableIoMapper=false` failure. It is positive evidence that AirportItlwm itself owns the address-generation and descriptor-programming behavior that must be made correct under AppleVTD. A reliable fix requires checking whether every hardware-visible address is a valid translated IOVA for the device, and verifying descriptor lifetime, preparation/completion, coherency, and teardown across RX, TX, firmware, and ring paths.

A repository-wide search of the AirportItlwm reference found no explicit AppleVTD, VT-d, IOMMU, DMAR, RMRR, or `DisableIoMapper` handling. Absence of those names is not itself a defect, because correct IOKit DMA APIs can abstract the mapper. In combination with the mixed mapped-command/physical-cursor implementation, however, it rules out claiming a known AppleVTD compatibility layer without driver work and tests.

### Feasibility result

**C — LARGE / CROSS-PROJECT.**

Intel support cannot plausibly be completed by changing OCLP's detector, patch dictionary, KDK policy, or restored frameworks. It requires a separate AirportItlwm DMA/IOMMU engineering track and may also require platform/EFI/DMAR validation. AX210 exercises iwx; the complete Phase-5 supported set spans iwx, iwm, and iwn, so a generic claim has a much larger regression matrix than one physical adapter.

## EFI / ACPI / DMAR boundary

No change in this area is authorized or recommended as a publication hotfix.

Potential causes outside OCLP's root payload include:

- incorrect or incomplete DMAR device scopes;
- reserved-memory-region representation;
- PCI bridges/topology not represented as expected by AppleVTD;
- platform ACPI relationships, including the frozen XHC14 configuration;
- OpenCore IOMMU quirks;
- driver use of untranslated physical addresses or mapper-incompatible DMA lifetimes.

The audit does not select among these possibilities. It did not inspect or mutate the live tables, enumerate snapshots, change `DisableIoMapper`, or propose DMAR surgery. Any future platform work must start with read-only evidence tied to the exact root volume and PCI device path, not speculative table deletion or broad quirk changes.

## Regression surface and publication impact

| Area | Minimum affected surface if pursued now | Risk to frozen work |
|---|---|---|
| Broadcom | Apple legacy Wi-Fi driver choice/payload, BCM PCI DMA, IOSkywalk/IO80211 coupling, IOMMU domain assignment, DMAR/topology, interrupts, sleep/wake, Wi-Fi and AWDL | High; no identified local fix and the working BCM943602CDP path is frozen |
| Intel | AirportItlwm iwx/iwm/iwn DMA allocation and packet maps, firmware/rings, BAR/MSI, external EFI, DMAR/topology, shared Apple frameworks, sleep/wake and network features | Very high; crosses OCLP and AirportItlwm and spans many supported generations |
| Platform | Other DMA devices sharing AppleVTD/DMAR policy, including storage, USB, audio, graphics, and bridges | Potentially system-wide if EFI/DMAR is changed |

A responsible pre-publication validation would require multiple bootable recovery configurations and physical permutations. That is not commensurate with a narrow release gate when the frozen feature set already has a tested configuration.

## Release-blocker decision

**PUBLISH PHASE-5 GOLDEN STATE FIRST AND CONTINUE APPLEVTD AFTER RELEASE.**

Reasons:

1. No specific OCLP root-patch omission was found.
2. Broadcom's first actionable cause remains unresolved and reaches closed Apple driver/platform behavior.
3. Intel positively reaches AirportItlwm's PCI and DMA implementation, making it cross-project work.
4. EFI/DMAR experimentation would have system-wide regression potential and is explicitly outside the frozen configuration.
5. Broadcom and Intel require separate physical validation; a result for one cannot validate the other.
6. The current Phase-5 feature set is already runtime validated with `DisableIoMapper=true`; AppleVTD is an additional compatibility enhancement rather than a prerequisite for publication.
7. Reopening Phase 2 through Phase 5 for an ungrounded mapper change has a substantially greater chance of destabilization than of producing a safe release improvement.

Because neither assessment is category A, this report intentionally provides no Phase-6 implementation plan.

## Post-release research boundaries

### Track A — Broadcom / OCLP and platform

Goal: isolate whether the BCM943602CDP failure arises in the selected Apple driver stack, the platform's AppleVTD/DMAR representation, or their interaction before proposing any patch.

Required evidence:

- exact PCI path, bridge path, BARs, interrupt mode, loaded wireless kext versions, and mapper/domain attachment with `DisableIoMapper=true` versus `false`;
- kernel/IOKit logs from boot through Wi-Fi activation, including any AppleVTD faults;
- read-only native and patched IORegistry captures for the Wi-Fi device and its parents;
- read-only DMAR table, device scopes, and reserved-region evidence tied to that same PCI path;
- proof of which IOSkywalkFamily/IO80211FamilyLegacy/AirPortBrcmNIC binaries are active;
- an A/B test that holds the root payload, EFI, OS build, and hardware constant while changing only the mapper mode;
- preferably a second Broadcom/platform control known to operate with AppleVTD so a KGP-specific platform condition can be separated from a general legacy-driver limitation.

Hardware/runtime matrix:

- BCM943602CDP on the KGP platform;
- one comparable Broadcom adapter/platform control if available;
- cold boot, association, sustained bidirectional traffic, AirPlay/AWDL cases already validated, sleep/wake, reboot, and recovery;
- monitoring of other DMA devices so a wireless improvement cannot mask platform regressions.

No DMAR, XHC14, DeviceProperties, or OpenCore quirk change should be attempted until the evidence identifies a specific incorrect relationship.

### Track B — Intel / AirportItlwm

Goal: make AirportItlwm's hardware-visible DMA addresses and lifetimes demonstrably correct under AppleVTD, independently of OCLP's already-complete detector and shared root payload.

Required evidence and engineering:

- instrument the exact iwx RX, TX, firmware-command, firmware-page, context, and ring allocation paths;
- distinguish physical addresses from device-valid IOVAs returned through a mapper-aware `IODMACommand`;
- verify descriptor preparation/completion, synchronization/coherency, segmentation limits, reuse, teardown, and error paths;
- capture AppleVTD faults and correlate each address to the corresponding AirportItlwm descriptor;
- verify BAR mapping and MSI/MSI-X behavior under active AppleVTD;
- develop and review any driver changes in the AirportItlwm repository rather than hiding them in OCLP;
- keep the OCLP shared framework payload constant while testing driver revisions.

Hardware/runtime matrix:

- AX210/`iwx` as the first physical device;
- at least one earlier iwx or iwm family device (for example AX200 or a supported 826x/9260-class device);
- iwn only if generic AppleVTD compatibility is to be claimed for the full authoritative Phase-5 set;
- cold boot, scan/association, sustained RX/TX, large transfers, sleep/wake, firmware recovery, AirPlay, and whichever AWDL functions the driver claims;
- a Broadcom control to prove AirportItlwm work did not alter the frozen OCLP root payload.

An Intel result must continue to report OCLP detection/applicability separately from AirportItlwm runtime binding.

## First-public-release limitation

Recommended concise release note:

> AppleVTD/IOMMU wireless operation is not yet validated. On the KGP reference platform, the validated Broadcom and Intel wireless configuration requires OpenCore `DisableIoMapper=true`; setting it to `false` can prevent wireless activation. OCLP does not modify EFI/DMAR and does not install or configure AirportItlwm.

This is intentionally scoped to the tested configuration and does not claim that every Hackintosh or every supported adapter requires the quirk.

## Audit integrity

- No OCLP functional source changed.
- No AirportItlwm source changed.
- No build or package was produced.
- No EFI, ACPI, DMAR, XHC14, DeviceProperties, OpenCore quirk, KDK, root volume, snapshot, NVRAM, or live hardware state was changed.
- No root patch, revert, install, reboot, mount, or runtime test was performed.
- Phase 2, Phase 3B, Phase 3C, Phase 4, and Phase 5 remain frozen.
