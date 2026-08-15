# Phase 5 — Generic Intel Modern Wi-Fi Implementation

Date: 2026-08-15

Frozen Phase-4 functional baseline: `a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0`

Frozen Phase-4 documentation baseline: `d0d0aaf26057d1e8faa31773f6edef20098e14d6`

Phase-5 implementation commit: `13a8aeaaaa877b197b54cf6f8452a5801d7e36ff` (`wireless: detect supported Intel modern Wi-Fi hardware`)

## Implementation

Phase 5 is a narrow hardware-applicability extension.

| File | Final responsibility |
|---|---|
| `opencore_legacy_patcher/datasets/pci_data.py` | Defines the frozen 87-ID `intel_wireless_ids.AirportItlwm` set derived from the local AirportItlwm personality. |
| `opencore_legacy_patcher/detections/device_probe.py` | Adds vendor-`8086` `IntelWirelessCard`, classifies only audited IDs as AirportItlwm-supported, retains all discovered Wi-Fi devices, and logs supported Intel identity once during the initial probe. |
| `opencore_legacy_patcher/sys_patch/patchsets/hardware/networking/modern_wireless.py` | Extends applicability to supported Intel or the existing supported Broadcom chipsets. Patch construction is unchanged. |
| `tests/test_phase5_intel_modern_wireless.py` | Protects the authoritative set, vendor boundary, every supported ID, excluded discrepancies, multi-device inventory, shared payload, no-KDK behavior, GUI-selection default, and no EFI integration. |
| `tests/test_modern_wireless_regression.py` | Preserves the Broadcom and hardware-agnostic selection regressions while allowing the intended direct Intel predicate. |

The probe continues to expose `computer.wifi` as a backwards-compatible primary shortcut. It additionally records `computer.wifi_devices` so a synthetic Broadcom+Intel inventory remains one Modern Wireless applicability result. If both Intel and a historical Broadcom/Atheros device exist, the historical non-Intel device remains the primary shortcut; existing EFI-builder behavior is not displaced.

## Applicability flow

```text
IOPCIDevice class 028000
  -> physical PCI identity from the existing anti-spoof probe
  -> vendor 8086 + one of 87 AirportItlwm IDs
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

## Shared payload and KDK behavior

Intel and Broadcom return the same existing Tahoe patch dictionary:

- `/usr/libexec/wifip2pd`
- `/System/Library/PrivateFrameworks/IO80211.framework`
- `/System/Library/PrivateFrameworks/WiFiPeerToPeer.framework`

The `_base_patch`, `_extended_patch`, and `patches` method text is byte-for-byte unchanged after normalized line termination. Its SHA-256 remains:

`f71883e711d7eadaa45fb23799024db1d38c1da82b57c55044687cd430f880fe`

Intel Modern Wi-Fi alone inherits `requires_kernel_debug_kit() == False`. Modern Audio and every other independent KDK requirement remain authoritative.

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

## Broadcom regression

The existing supported Broadcom chipset enums and PCI tables were not edited. Tests show:

- Broadcom-only: applicable;
- Intel-only: applicable;
- Broadcom+Intel: applicable once, with one shared patch dictionary;
- neither: not applicable;
- Broadcom and Intel produce identical Modern Wireless payload dictionaries.

BCM943602CDP remains the Phase-5A physical control device.

## Validation results

Pre-commit focused run:

- 47 Phase-3B/Modern Wireless/Phase-5 tests: PASS
- 16 direct Phase-5 plus Broadcom regression tests: PASS

Pre-documentation complete suite:

- 199 tests: PASS
- inherited `ResourceWarning` at `efi_builder/support.py:130`: unchanged and non-failing

Final validation from a clean source clone at the exact implementation commit:

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

## Runtime status

Phase-5A artifacts:

- directory: `/Users/kgp/Desktop/OCLP/OCLP-v2.0-phase5-intel-modern-wifi`
- primary package: `OpenCore-Patcher.pkg`
- SHA-256: `dbd3bbd56e97dfd5f9edec4b5f662ae8750326e4901698c1b13d771083f458e1`
- uninstaller SHA-256: `88420b7ed293fb84ed8d1e6ff0f0cf1056541ae91252f0770a612f022218242d`
- AutoPkg assets SHA-256: `8bf175f2ff495a9177536a7800bfa631ca91f93ac487b8a91f9e35c5a559f213`
- status: statically validated; not installed or runtime-tested by Codex

The first physical validation is the BCM943602CDP Phase-5A control. It must establish that adding the Intel predicate caused no Broadcom or GUI/KDK side effect. Phase-5B then records Test A (shared root payload across a Broadcom-to-Intel hardware swap without repatching) separately from Test B (direct Intel detection/applicability, Intel-originated root patching, and subsequent external-AirportItlwm runtime binding).

Phase-5B AX210 direct-detection and AirportItlwm runtime validation: **not performed by Codex**.
