# Phase 5 — Generic Intel Modern Wi-Fi Implementation

Date: 2026-08-16 (pre-publication development-hardware addendum)

Frozen Phase-4 functional baseline: `a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0`

Frozen Phase-4 documentation baseline: `d0d0aaf26057d1e8faa31773f6edef20098e14d6`

Phase-5 implementation commit: `13a8aeaaaa877b197b54cf6f8452a5801d7e36ff` (`wireless: detect supported Intel modern Wi-Fi hardware`)

Phase-5 development-hardware addendum: `555db89d3ed21285e1b84beded91932762b79ef9` (`wireless: extend experimental Intel Wi-Fi detection`)

Public support/parity checkpoint: `f8ce3acbfe08de7923d8022411aa64a665a14d52` (`test: enforce public Intel Wi-Fi support parity`)

## Implementation

Phase 5 is a narrow hardware-applicability extension.

| File | Final responsibility |
|---|---|
| `opencore_legacy_patcher/datasets/pci_data.py` | Preserves the 87-ID `intel_wireless_ids.AirportItlwm` set and separately defines the nine-ID `Experimental` BZ/SC development set. |
| `opencore_legacy_patcher/detections/device_probe.py` | Classifies vendor-`8086` Intel devices into current-AirportItlwm or experimental/development detection classes, maps both to the existing applicability path, retains the complete Wi-Fi inventory, and logs the resolved identity once. |
| `opencore_legacy_patcher/sys_patch/patchsets/hardware/networking/modern_wireless.py` | Extends applicability to supported Intel or the existing supported Broadcom chipsets. Patch construction is unchanged. |
| `tests/test_phase5_intel_modern_wireless.py` | Protects all 87 regular IDs, all nine development IDs, vendor/interface boundaries, excluded legacy IDs, multi-device inventory, shared payload, no-KDK behavior, GUI-selection default, concise logging, and no EFI integration. |
| `tests/test_modern_wireless_regression.py` | Preserves the Broadcom and hardware-agnostic selection regressions while allowing the intended direct Intel predicate. |
| `Documentation/Intel-WiFi-Device-Support.md` | Public Regular/Experimental/Excluded transport table and runtime caveats. |
| `tests/test_phase5_intel_wifi_documentation.py` | Enforces exact source/public-document parity and classification. |

The probe continues to expose `computer.wifi` as a backwards-compatible primary shortcut. It additionally records `computer.wifi_devices` so a synthetic Broadcom+Intel inventory remains one Modern Wireless applicability result. If both Intel and a historical Broadcom/Atheros device exist, the historical non-Intel device remains the primary shortcut; existing EFI-builder behavior is not displaced.

## Applicability flow

```text
IOPCIDevice class 028000
  -> physical PCI identity from the existing anti-spoof probe
  -> vendor 8086 + one of 87 AirportItlwm IDs
                    OR one of 9 audited BZ/SC development IDs
  -> IntelWirelessCard.Chipsets.AirportItlwm
  -> ModernWireless.present() == true
  -> "Networking: Modern Wireless" applicable
  -> existing Modern Wi-Fi selection/defaults/filtering
  -> existing shared Modern Wireless patch dictionary
```

Supported Intel discovery emits one concise initial-probe message, for example:

```text
- Detected supported Intel Modern Wireless device: 8086:2725
```

Repeated GUI/state revalidation does not log the message again.

Development discovery is explicitly distinguishable without adding GUI controls:

```text
- Detected experimental Intel Modern Wireless device: 8086:272B
```

`IntelWirelessCard.DetectionClass` records whether the identity came from the current AirportItlwm personality or the experimental/development set. Both classes intentionally reuse the same `Chipsets.AirportItlwm` applicability token so `ModernWireless.present()` and the frozen patch source do not need another branch. This token means the external AirportItlwm architecture is expected; it is not a stock-driver support claim for a development ID.

## Shared payload and KDK behavior

Intel and Broadcom return the same existing Tahoe patch dictionary:

- `/usr/libexec/wifip2pd`
- `/System/Library/PrivateFrameworks/IO80211.framework`
- `/System/Library/PrivateFrameworks/WiFiPeerToPeer.framework`

The `_base_patch`, `_extended_patch`, and `patches` method text is byte-for-byte unchanged after normalized line termination. Its SHA-256 remains:

`f71883e711d7eadaa45fb23799024db1d38c1da82b57c55044687cd430f880fe`

Intel Modern Wi-Fi alone inherits `requires_kernel_debug_kit() == False` for both detection classes. Modern Audio and every other independent KDK requirement remain authoritative.

## No-spoof / no-EFI invariant

Phase 5 does not add any Intel branch to `efi_builder/networking/wireless.py`. It does not:

- install or configure AirportItlwm;
- modify `config.plist`, `Kernel/Add`, boot arguments, DeviceProperties, ACPI, DMAR, NVRAM, or hardware state;
- create Intel or Broadcom spoofing;
- add AirportBrcmFixup properties or Broadcom kexts for Intel hardware.

AirportItlwm remains an external user-EFI prerequisite.

## Detection/applicability versus runtime binding

The implementation deliberately proves only the OCLP layer:

```text
supported Intel PCI identity
  -> Modern Wi-Fi applicable
  -> shared root patch selectable/applicable
```

Runtime is separate:

```text
Intel hardware
  -> external EFI
  -> AirportItlwm binds
  -> restored Apple wireless/P2P frameworks are consumed
```

Neither result substitutes for the other. Physical Phase-5 validation must record the shared-payload cross-hardware test and direct Intel-detection/patch test independently.

For the nine development IDs, the first required physical result is likewise detection/applicability only. Runtime binding may require a compatible experimental or modified AirportItlwm build and is not guaranteed by this addendum.

## Broadcom regression

The existing supported Broadcom chipset enums and PCI tables were not edited. Tests show:

- Broadcom-only: applicable;
- Intel-only: applicable;
- Broadcom+Intel: applicable once, with one shared patch dictionary;
- neither: not applicable;
- Broadcom and Intel produce identical Modern Wireless payload dictionaries.

BCM943602CDP was the independent Broadcom runtime-control device.

## Addendum validation results

Final source/public-document review through `f8ce3acbfe08de7923d8022411aa64a665a14d52`:

- 22 direct Phase-5 detector/document parity tests: PASS
- 63 Phase-3B/Modern Wireless/Phase-5 focused tests: PASS
- 208 complete-suite tests: PASS
- inherited `ResourceWarning` at `efi_builder/support.py:130`: unchanged and non-failing
- `compileall`: PASS
- `git diff --check`: PASS

The direct matrix loops over every regular and every development ID. It also proves `2725` remains regular, `272B` is experimental, `0885/0886` remain rejected, AX201/CNVio remains accepted, all development IDs share the Broadcom payload dictionary, none adds a KDK requirement, and the public classification tables match source exactly.

## Original Phase-5 package validation

The previously runtime-tested regular Phase-5 build at `13a8ae...` retained these results:

- 199 tests: PASS
- `compileall`: PASS
- `git diff --check`: PASS
- locked CPython 3.14.3 x86_64 / 22-wheel offline environment: VERIFIED
- built-app strict/deep ad-hoc signature: PASS
- packaged-app strict/deep ad-hoc signature: PASS
- `TeamIdentifier`: not set
- packaged app versus validated built app: identical by `rsync --dry-run --checksum`
- built and packaged app inventories: 110 regular files and 33 symlinks each
- exact packaged runtime DMG helper: both images mounted with writable shadows, the inner image used the Phase-4 host-sibling mount plus logical symlink, expected payloads were readable, and cleanup detached both images without a stale project mount
- no interactive authentication prompt, Keychain operation, signing identity, package installation, root patch, revert, KDK operation, or EFI/NVRAM mutation occurred

## Frozen Phase-4 invariants

At implementation review:

- Modern Audio source: `a24581ef94b304d2252bc9db9d181a20332fe6621801dadf9bd5cb3339d2615d`
- APFS `payloads.dmg`: `082de073e0d103d7bd4b47852007f2b6ab360eda5b4737a089cf3b34a3910f91`
- `Universal-Binaries.dmg`: `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4`
- Modern Wireless patch-method source: `f71883e711d7eadaa45fb23799024db1d38c1da82b57c55044687cd430f880fe`

No Phase-2/3/4 root state, recovery, KDK, GUI, payload-image, nested-mount, audio, or Revert behavior was changed.

## Runtime validation status

Runtime-tested Phase-5 artifact:

- directory: `/Users/kgp/Desktop/OCLP/OCLP-v2.0-phase5-intel-modern-wifi`
- primary package: `OpenCore-Patcher.pkg`
- SHA-256: `dbd3bbd56e97dfd5f9edec4b5f662ae8750326e4901698c1b13d771083f458e1`
- uninstaller SHA-256: `88420b7ed293fb84ed8d1e6ff0f0cf1056541ae91252f0770a612f022218242d`
- AutoPkg assets SHA-256: `8bf175f2ff495a9177536a7800bfa631ca91f93ac487b8a91f9e35c5a559f213`
- status: statically validated by Codex and runtime validated by KGP

The physical validation used three deliberately separate evidence steps:

1. **Broadcom regression control:** BCM943602CDP root patching succeeded with the Intel detector present. After reboot, AppleHDA, Broadcom Wi-Fi, and the tested AWDL/Continuity functions worked flawlessly. Sidecar is excluded from that result.
2. **Intel Test A — shared root-payload independence:** KGP powered off, replaced the Broadcom adapter with AX210, booted the external Intel EFI/AirportItlwm, and did not repatch. Intel Wi-Fi and AppleHDA worked immediately, proving that the existing root payload is shared across the two hardware paths.
3. **Intel Test B — direct detection and patching:** with physical `8086:2725` AX210 installed and a clean root-patch state, OCLP directly recognized Intel Modern Wireless, made Modern Wi-Fi applicable, and completed root patching. After reboot, AppleHDA, Intel Wi-Fi, and AirPlay worked flawlessly. This separately proves the detector/applicability layer and the external AirportItlwm runtime-binding layer.

The captured AX210 properties were `vendor-id <86 80 00 00>`, `device-id <25 27 00 00>`, `IOName pci8086,2725`, and class code `0x028000`. Apple-style `AirPort Extreme`/`ARPT` naming coexisted with the authentic Intel PCI identity.

Hack-to-MBP-M1 Screen Mirroring worked once but was otherwise unreliable. It is not classified as a Phase-5 detection failure or as validated Intel functionality. FeatureUnlock/Tahoe Screen Mirroring is a separate research area and Phase 5 did not modify it. Other Continuity/AWDL services not positively exercised in this session are not claimed.

The 87-ID regular detector, AX210 path, Broadcom control, and shared payload remain **RUNTIME VALIDATED**. The nine-ID pre-publication addendum is **STATICALLY VALIDATED; PHYSICAL DEVELOPMENT-HARDWARE DETECTION PENDING**. It does not invalidate or overstate the earlier runtime results.

## Prepared README link

The later publication README should include this wording without changing the current development README during this addendum:

> ### Intel Wi-Fi Device Support
>
> OCLP-CustoMac directly detects the current regular AirportItlwm-supported Intel device set and additionally selected experimental Intel BZ/SC Wi-Fi 7 transport IDs used for ongoing driver development.
>
> Runtime support for experimental devices depends on the external AirportItlwm implementation used. No Broadcom IOName spoof is required for OCLP-CustoMac Intel detection.
>
> [Complete Intel Wi-Fi Device Support List](Documentation/Intel-WiFi-Device-Support.md)
