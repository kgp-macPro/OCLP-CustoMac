# Phase 5 — Intel Modern Wi-Fi Device Support Audit

Date: 2026-08-15

Audit boundary: local, read-only source reconciliation performed before the Phase-5 implementation.

Phase-4 functional baseline: `a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0`

Phase-4 documentation baseline: `d0d0aaf26057d1e8faa31773f6edef20098e14d6`

## Decision

KGP should directly recognize the **87 unique Intel PCI device IDs exposed by the audited AirportItlwm IOKit personality**, and no others. A qualifying device must have PCI vendor `8086`, wireless class `028000`, and one of those exact device IDs.

This is a generic AirportItlwm-source-backed detector. AX210 (`8086:2725`) is one member of the set, not a special case.

## Authoritative AirportItlwm source

The local source used for this decision is:

- repository: `/Users/kgp/Developer/OpenIntelWireless/itlwm-dexter-awdl`
- exact HEAD: `0b17225dfbe1b7810b114f8fa9148b09f56d4efd`
- `AirportItlwm/Info.plist:31-32`
- `AirportItlwm/AirportItlwm-Sonoma-Info.plist:46-47`
- `AirportItlwm/AirportItlwm-Monterey-Info.plist:31-32`

All three AirportItlwm personalities expose the same 87-entry `IOPCIMatch` set. The personality is the first binding gate; an ID present only in a lower driver table but absent from `IOPCIMatch` is not treated as supported by the audited AirportItlwm configuration.

The lower driver matchers corroborate the exposed families:

- `itlwm/hal_iwn/ItlIwn.cpp:244-333`: Intel vendor check and `iwn_devices`
- `itlwm/hal_iwm/mac80211.cpp:4290-4361`: Intel vendor check and `iwm_devices`
- `itlwm/hal_iwx/ItlIwx.cpp:18513-18517,18742-18773,19705-19711`: Intel vendor check and `iwx_devices`

## Final Intel device set

Every ID below uses vendor `8086`.

| Source family | Exact device IDs included |
|---|---|
| `iwx` — Wi-Fi 6 / 6E PCI and CNVi families | `2723, 43F0, A0F0, 34F0, 4DF0, 02F0, 3DF0, 06F0, 2720, 2725, 2726, 7A70, 7AF0, 51F0, 54F0, 2729, 7E40, 7F70, 51F1` |
| `iwm` — AC 3160/3165/3168, 7260/7265, 8260/8265, 9260, 9461/9462, 9560 families | `08B1, 08B2, 08B3, 08B4, 095A, 095B, 3165, 3166, 24F3, 24F4, 24F5, 24F6, 24FB, 24FD, 2526, 9DF0, A370, 31DC, 30DC, 271C, 271B, 42A4, 00A0, 00A4, 02A0, 40A4, 0060, 0064, 0260, 0264` |
| `iwn` — WiFi Link and Centrino Wireless-N families exposed by AirportItlwm | `4229, 422B, 422C, 4230, 4232, 4235, 4236, 4237, 4238, 4239, 423A, 423B, 423C, 423D, 0082, 0083, 0084, 0085, 0087, 0089, 008A, 008B, 0090, 0091, 0892, 0893, 0894, 0895, 0896, 0897, 08AE, 08AF, 088E, 088F, 0890, 0891, 0887, 0888` |

Count: **87 unique device IDs**.

Reliable source labels include older WiFi Link/Centrino generations, the Wireless-AC families listed above, AX200 (`2723`), AX210 (`2725`), and AX201/AX211/AX411-class PCI/CNVi families represented in the `iwx` tables. The source sometimes resolves a precise product name from subsystem identity, so KGP does not fabricate a more specific marketing name from the PCI device ID alone.

## OCLP-Mod 3.1.9 comparison

Read-only reference:

- `/Users/kgp/Developer/OCLP-Plus-Mod-evaluation-audit/SOURCES/OCLP-Mod-3.1.9`
- exact HEAD: `3b15c88820a6f99d1974532b9a722925da8b2897`
- `oclp_mod/datasets/pci_data.py:1238-1379`
- `oclp_mod/detections/device_probe.py:559-573`
- `oclp_mod/sys_patch/patchsets/hardware/networking/modern_wireless.py:25-79`

Mod contains 88 unique Intel IDs. It creates `IntelWirelessCard`, maps its explicit list to one supported chipset enum, and ORs that class into `ModernWireless.present()`. It does not add an Intel EFI-builder branch or automatically create a Broadcom spoof.

| Comparison | Count / IDs | KGP decision |
|---|---|---|
| AirportItlwm ∩ Mod | 85 | Include |
| AirportItlwm only | `2720, 2729` | Include; exposed by AirportItlwm and present in `iwx_devices` |
| Mod only | `0885, 0886` | Exclude; lower `iwn` matcher exists, but AirportItlwm `IOPCIMatch` does not expose either ID |
| Mod only | `272B` | Exclude; absent from the audited AirportItlwm personalities and lower matchers |
| KGP Phase-4 direct Intel set | 0 | Replaced by the 87-ID audited set in Phase 5 |

This resolves the earlier Phase-3A discrepancy without copying Mod's table wholesale.

## KGP Phase-4 Broadcom baseline

Before Phase 5, `ModernWireless.present()` accepted only a `device_probe.Broadcom` whose detected chipset was one of:

- `AirPortBrcm4360`
- `AirportBrcmNIC`
- `AirPortBrcmNICThirdParty`

The underlying Broadcom device tables and all three applicability choices remain unchanged. `AppleBCMWLANBusInterfacePCIe` remains outside this root patch because it is not one of those dropped-support chipsets.

Hardware discovery uses `Computer.wifi_probe()` and `WirelessCard.class_code_matching_dict()` to enumerate PCI class `028000`. `PCIDevice.from_ioregistry(..., anti_spoof=True)` prefers a parseable `IOName` of the form `pciVVVV,DDDD`, otherwise it reads `vendor-id` and `device-id`. Matching does not depend on a chipset marketing name, loaded driver/service identity, `compatible`, or a Broadcom identity.

Consumers of `ModernWireless.present()` are:

- `HardwarePatchsetDetection._detect()` through the registered `ModernWireless` hardware class;
- `CPUMissingAVX.native_os()` for its inherited Ventura compatibility decision.

## Direct identity and spoof boundary

The Phase-5 rule consumes the PCI vendor/device identity already produced by the existing anti-spoof probe. A normal injected `vendor-id`/`device-id` does not hide physical identity when the original `IOName` remains `pci8086,<device>`.

There is one explicit limitation: if an external configuration also replaces `IOName` itself with a false PCI identity, the current hardware model has no separate, trustworthy PCI-configuration-space reader from which to reconstruct the original identity. Phase 5 does not guess and does not mutate EFI to remove that spoof. The user must expose the real Intel identity for the direct detector to prove Intel hardware.

## Detection is not runtime binding

Phase 5 has two independent validation layers:

1. **OCLP detection/applicability:** real `8086:<supported-ID>` hardware makes the existing Modern Wi-Fi root patch applicable.
2. **Intel runtime binding:** the user's external EFI must load a compatible AirportItlwm, which binds the adapter at boot and consumes the restored Apple wireless/P2P frameworks.

OCLP does not download, install, enable, configure, or validate runtime attachment of AirportItlwm. Detection success is not proof of driver binding, and working AirportItlwm is not proof that the new OCLP detector was exercised.

## Physical validation design

### Test A — shared payload independence

With a Modern Wireless root patch installed while Broadcom hardware was present, KGP powered off, replaced Broadcom with AX210, booted the known Intel EFI, and did not repatch solely because the card changed. Successful Intel runtime operation proved the root payload is hardware-independent; it did not by itself prove direct Intel detection.

### Test B — direct Intel detection and patching

KGP returned safely to the appropriate clean state, left AX210 installed, launched the Phase-5 build, observed direct Intel recognition and Modern Wi-Fi applicability, then patched and rebooted. Working Intel Wi-Fi and AirPlay after reboot separately confirmed external AirportItlwm binding and runtime behavior.

An optional reverse test may later boot Broadcom against an Intel-originated shared root patch without repatching. It was not required for Phase-5 closure.

## Audit integrity

No reference source was modified. No internet list or marketing-name list was used. No EFI, DeviceProperties, ACPI, DMAR, NVRAM, KDK, root volume, or live hardware state was changed during this audit.

## Runtime confirmation and frozen decision

KGP subsequently runtime-validated the generic detector with an Intel AX210. The captured IORegistry/device properties exposed:

| Property | Captured value | Decoded identity |
|---|---|---|
| `vendor-id` | `<86 80 00 00>` | `0x8086` |
| `device-id` | `<25 27 00 00>` | `0x2725` |
| `IOName` | `pci8086,2725` | corroborates `8086:2725` |
| `class-code` | `0x028000` | network controller / wireless class used by the probe |
| model | `Intel AX210 Wi-Fi 6E 802.11ax + Bluetooth 5.3` | observed hardware description |

The runtime node also used Apple-style wireless naming, including `AirPort Extreme` and `ARPT` where applicable. Those service/display names did not obscure the authentic numeric Intel PCI identity: `8086:2725` remained directly visible in the PCI properties and was corroborated by `IOName`.

The eligibility decision therefore remains a numeric vendor/device decision. It is not an `AirPort` name, compatible-string, marketing-name, loaded-service, or fabricated Broadcom-identity predicate. The existing probe may use a parseable PCI `IOName` as one source of the resolved identity, but Phase 5 does not treat the string or Apple-style service naming itself as proof of supported Intel hardware.

The final support decision is frozen at 87 AirportItlwm-personality-backed IDs. AX210 remains a generic member of that set; `0885`, `0886`, and `272B` remain excluded. Runtime success on AX210 does not narrow or expand the source-backed table.
