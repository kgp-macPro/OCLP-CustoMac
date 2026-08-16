# Phase 5 — Intel Modern Wi-Fi Device Support Audit

Date: 2026-08-16 (pre-publication development-hardware addendum)

Audit boundary: local, read-only source reconciliation performed before the Phase-5 implementation.

Phase-4 functional baseline: `a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0`

Phase-4 documentation baseline: `d0d0aaf26057d1e8faa31773f6edef20098e14d6`

## Decision

KGP should directly recognize two explicit classes of Intel wireless hardware:

1. the **87 unique Intel PCI device IDs exposed by the audited current AirportItlwm IOKit personality**; and
2. **9 additional Intel BZ/SC PCI transport IDs** positively identified by current upstream Intel `iwlwifi` source for Wi-Fi 7/development hardware.

A qualifying device must have PCI vendor `8086`, wireless class `028000`, and one of those 96 exact device IDs. The second class grants only OCLP Modern Wi-Fi root-patch applicability. It does not claim that stock AirportItlwm can bind the device.

AX210 (`8086:2725`) remains an ordinary member of the 87-ID regular set, not a special case. BE200-class device `8086:272B` is now deliberately included in the development set.

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

## Regular Intel device set

Every ID below uses vendor `8086`.

| Source family | Exact device IDs included |
|---|---|
| `iwx` — Wi-Fi 6 / 6E PCI and CNVi families | `2723, 43F0, A0F0, 34F0, 4DF0, 02F0, 3DF0, 06F0, 2720, 2725, 2726, 7A70, 7AF0, 51F0, 54F0, 2729, 7E40, 7F70, 51F1` |
| `iwm` — AC 3160/3165/3168, 7260/7265, 8260/8265, 9260, 9461/9462, 9560 families | `08B1, 08B2, 08B3, 08B4, 095A, 095B, 3165, 3166, 24F3, 24F4, 24F5, 24F6, 24FB, 24FD, 2526, 9DF0, A370, 31DC, 30DC, 271C, 271B, 42A4, 00A0, 00A4, 02A0, 40A4, 0060, 0064, 0260, 0264` |
| `iwn` — WiFi Link and Centrino Wireless-N families exposed by AirportItlwm | `4229, 422B, 422C, 4230, 4232, 4235, 4236, 4237, 4238, 4239, 423A, 423B, 423C, 423D, 0082, 0083, 0084, 0085, 0087, 0089, 008A, 008B, 0090, 0091, 0892, 0893, 0894, 0895, 0896, 0897, 08AE, 08AF, 088E, 088F, 0890, 0891, 0887, 0888` |

Regular count: **87 unique device IDs**.

Reliable source labels include older WiFi Link/Centrino generations, the Wireless-AC families listed above, AX200 (`2723`), AX210 (`2725`), and AX201/AX211/AX411-class PCI/CNVi families represented in the `iwx` tables. The source sometimes resolves a precise product name from subsystem identity, so KGP does not fabricate a more specific marketing name from the PCI device ID alone.

## Experimental/development Intel device set

The development set is derived from the current upstream Linux Intel wireless PCI matcher, retrieved on 2026-08-16:

- [`drivers/net/wireless/intel/iwlwifi/pcie/drv.c`](https://github.com/torvalds/linux/blob/master/drivers/net/wireless/intel/iwlwifi/pcie/drv.c), `iwl_hw_card_ids` BZ/SC entries;
- the same file's `iwl_dev_info_table`, which maps FM RF to BE200/BE201/BE202 and WH RF to BE211/BE213;
- [Intel BE200 specifications](https://www.intel.com/content/www/us/en/products/sku/230078/intel-wifi-7-be200/specifications.html) and [BE202 specifications](https://www.intel.com/content/www/us/en/products/sku/234444/intel-wifi-7-be202/specifications.html), which identify PCIe/USB modules;
- [Intel's BE201/BE211/BE213 comparison](https://www.intel.com/content/www/us/en/products/compare.html?productIds=240284%2C240287%2C230079%2C230078.html), which identifies those integrated products as CNVio3;
- the current [`pci.ids`](https://github.com/pciutils/pciids/blob/master/pci.ids) database for discrete 272B subsystem labels and the E440/0114 BE211 example.

| Upstream family | Exact PCI device IDs included | What can be stated safely |
|---|---|---|
| BZ/GL | `272B` | discrete PCIe BE200/BE202 and Killer/OEM derivatives; subsystem identity distinguishes the marketed product |
| BZ integrated hosts | `A840, 7740, 4D40` | CNVio-family Intel wireless hosts; FM RF identifies BE201/BE202-class configurations and WH RF may identify BE211/BE213-class configurations |
| SC integrated hosts | `E440, E340, D340, 6E70, D240` | newer integrated Intel wireless hosts; WH RF identifies BE211/BE213-class configurations |

Experimental count: **9 unique device IDs**. Final detector count: **96 unique device IDs**.

### BE-family identity qualification

Marketing SKU is not always a function of the 16-bit PCI device ID alone:

| Family | Interface | Positively identified PCI evidence used by KGP |
|---|---|---|
| BE200 | PCIe | device `272B`; known Intel subsystem IDs include `00F0`, `00F4`, `40F0`, and `E0F4` |
| BE202 | PCIe | device `272B`; known Intel subsystem IDs include `02F4` and `42F4` |
| BE201 | CNVio3 | FM RF on a BZ integrated host (`A840`, `7740`, or `4D40`); the base PCI ID alone is not a unique BE201 name |
| BE211 | CNVio3 | WH RF on a compatible BZ/SC host; `E440` with Intel subsystem `0114` is one positively labelled BE211 example |
| BE213 | CNVio3 | bandwidth-limited WH RF on a compatible BZ/SC host; the base PCI ID alone is not a unique BE213 name |

KGP therefore detects the exact upstream PCI host/transport set but does not fabricate BE201/BE211/BE213 labels from a base ID. The detector also does not inspect or reject by interface generation. Regular AirportItlwm IDs already cover PCIe, CNVi, and CNVio2 hardware such as AX201; the development set adds CNVio3 hosts. Interface type is informational only.

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
| AirportItlwm ∩ Mod | 85 | Include in the regular set |
| AirportItlwm only | `2720, 2729` | Include in the regular set; exposed by AirportItlwm and present in `iwx_devices` |
| Mod and KGP development set | `272B` | Include as positively identified discrete BZ Wi-Fi 7 development hardware, without claiming stock AirportItlwm support |
| Mod only | `0885, 0886` | Exclude; these are legacy Centrino Wireless-N/WiMAX 6150 identities, are absent from AirportItlwm `IOPCIMatch`, and are not current Modern Wireless development hardware |
| KGP development-only relative to Mod | `A840, 7740, 4D40, E440, E340, D340, 6E70, D240` | Include from the current upstream Intel BZ/SC PCI matcher |

Final comparison: Mod has 88 IDs; KGP has 96; the common set is 86; KGP-only is 10; Mod-only is `0885, 0886`. This resolves the earlier discrepancy without copying Mod's table wholesale.

## Device-by-device three-way cross-check

Exact set algebra:

- AirportItlwm matcher (A): 87 IDs;
- upstream BZ/SC development transports (B): 9 IDs;
- OCLP-Mod (M): 88 IDs;
- A ∩ B: empty;
- A ∩ M: 85 IDs;
- B ∩ M: `272B`;
- A ∩ B ∩ M: empty, because the current AirportItlwm personality has no BZ/SC ID;
- A − M: `2720, 2729`;
- B − M: `A840, 7740, 4D40, E440, E340, D340, 6E70, D240`;
- M − (A ∪ B): `0885, 0886`;
- final OCLP-CustoMac set: A ∪ B, 96 IDs.

The absence of a three-way intersection is not disagreement: A and B are intentionally non-overlapping generations. The 85 regular IDs are the AirportItlwm/Mod agreement class, and `272B` is the BZ/SC/Mod agreement class.

| PCI ID | AirportItlwm matcher | Upstream BZ/SC | OCLP-Mod | Final OCLP-CustoMac | Classification | Rationale |
|---|---:|---:|---:|---:|---|---|
| `0060` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0064` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0082` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0083` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0084` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0085` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0087` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0089` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `008A` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `008B` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0090` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0091` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `00A0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `00A4` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0260` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0264` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `02A0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `02F0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `06F0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0885` | no | no | yes | exclude | legacy Intel Wi-Fi | Wireless-N/WiMAX 6150; not current matcher/development transport |
| `0886` | no | no | yes | exclude | legacy Intel Wi-Fi | Wireless-N/WiMAX 6150; not current matcher/development transport |
| `0887` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0888` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `088E` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `088F` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0890` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0891` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0892` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0893` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0894` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0895` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0896` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `0897` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `08AE` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `08AF` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `08B1` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `08B2` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `08B3` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `08B4` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `095A` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `095B` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `24F3` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `24F4` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `24F5` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `24F6` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `24FB` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `24FD` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `2526` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `271B` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `271C` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `2720` | yes | no | no | include | regular current Intel Wi-Fi transport | current AirportItlwm personality; Mod omits it |
| `2723` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `2725` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `2726` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `2729` | yes | no | no | include | regular current Intel Wi-Fi transport | current AirportItlwm personality; Mod omits it |
| `272B` | no | yes | yes | include | current BZ/SC development transport | upstream BZ matcher and Mod agree |
| `30DC` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `3165` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `3166` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `31DC` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `34F0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `3DF0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `40A4` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `4229` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `422B` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `422C` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `4230` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `4232` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `4235` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `4236` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `4237` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `4238` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `4239` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `423A` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `423B` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `423C` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `423D` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `42A4` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `43F0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `4D40` | no | yes | no | include | current BZ/SC development transport | upstream BZ/SC matcher; KGP extension beyond Mod |
| `4DF0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `51F0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `51F1` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `54F0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `6E70` | no | yes | no | include | current BZ/SC development transport | upstream BZ/SC matcher; KGP extension beyond Mod |
| `7740` | no | yes | no | include | current BZ/SC development transport | upstream BZ/SC matcher; KGP extension beyond Mod |
| `7A70` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `7AF0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `7E40` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `7F70` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `9DF0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `A0F0` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `A370` | yes | no | yes | include | regular current Intel Wi-Fi transport | current AirportItlwm personality and Mod agree |
| `A840` | no | yes | no | include | current BZ/SC development transport | upstream BZ/SC matcher; KGP extension beyond Mod |
| `D240` | no | yes | no | include | current BZ/SC development transport | upstream BZ/SC matcher; KGP extension beyond Mod |
| `D340` | no | yes | no | include | current BZ/SC development transport | upstream BZ/SC matcher; KGP extension beyond Mod |
| `E340` | no | yes | no | include | current BZ/SC development transport | upstream BZ/SC matcher; KGP extension beyond Mod |
| `E440` | no | yes | no | include | current BZ/SC development transport | upstream BZ/SC matcher; KGP extension beyond Mod |

For the nine BZ/SC IDs specifically:

| ID | In Mod? | Final treatment |
|---|---:|---|
| `272B` | yes | include; discrete BZ transport with BE200/BE202/Killer/OEM associations resolved through subsystem/RF evidence |
| `A840` | no | include as upstream integrated BZ host |
| `7740` | no | include as upstream integrated BZ host |
| `4D40` | no | include as upstream integrated BZ host |
| `E440` | no | include as upstream integrated SC host; E440/0114 is a source-backed BE211 example |
| `E340` | no | include as upstream integrated SC host |
| `D340` | no | include as upstream integrated SC host |
| `6E70` | no | include as upstream integrated SC host |
| `D240` | no | include as upstream integrated SC host |

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

Phase 5 has two independent validation layers for both regular and development IDs:

1. **OCLP detection/applicability:** real `8086:<recognized-ID>` hardware makes the existing Modern Wi-Fi root patch applicable.
2. **Intel runtime binding:** the user's external EFI must load a compatible AirportItlwm, which binds the adapter at boot and consumes the restored Apple wireless/P2P frameworks.

OCLP does not download, install, enable, configure, or validate runtime attachment of AirportItlwm. Detection success is not proof of driver binding, and working AirportItlwm is not proof that the OCLP detector was exercised. Development IDs may require an experimental or modified external AirportItlwm build.

## Physical validation design

### Test A — shared payload independence

With a Modern Wireless root patch installed while Broadcom hardware was present, KGP powered off, replaced Broadcom with AX210, booted the known Intel EFI, and did not repatch solely because the card changed. Successful Intel runtime operation proved the root payload is hardware-independent; it did not by itself prove direct Intel detection.

### Test B — direct Intel detection and patching

KGP returned safely to the appropriate clean state, left AX210 installed, launched the Phase-5 build, observed direct Intel recognition and Modern Wi-Fi applicability, then patched and rebooted. Working Intel Wi-Fi and AirPlay after reboot separately confirmed external AirportItlwm binding and runtime behavior.

An optional reverse test may later boot Broadcom against an Intel-originated shared root patch without repatching. It was not required for Phase-5 closure.

## Audit integrity

No reference source was modified. No internet list or marketing-name list was used. No EFI, DeviceProperties, ACPI, DMAR, NVRAM, KDK, root volume, or live hardware state was changed during this audit.

## Runtime confirmation and addendum boundary

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

The 87-ID regular set remains unchanged and its AX210/Broadcom runtime evidence remains authoritative. The pre-publication addendum adds the separate 9-ID development set. `272B` is included; `0885` and `0886` remain excluded.

The development set is statically validated for OCLP detection and shared root-patch applicability. It is not a statement of stock AirportItlwm support and has not inherited AX210's runtime-validation result. A later BE200 test needs to prove only that physical `8086:272B` is detected and makes Modern Wi-Fi applicable; actual Wi-Fi binding remains a separate external-driver result.

## Publication wording prepared

> OCLP-CustoMac directly detects the current Intel device set supported by AirportItlwm and additionally recognizes selected experimental Intel Wi-Fi hardware, including current Wi-Fi 7 / BE-series devices, so ongoing driver development is not blocked by the root patcher. Runtime support for experimental devices depends on the external AirportItlwm build and is not guaranteed by OCLP-CustoMac. No Broadcom IOName spoof is required for Intel detection.

## Public support contract

The complete public-facing list is [Documentation/Intel-WiFi-Device-Support.md](../Documentation/Intel-WiFi-Device-Support.md). It contains separately marked Regular, Experimental / Development, and Explicitly Excluded tables.

`tests/test_phase5_intel_wifi_documentation.py` extracts only the marked table regions and asserts exact equality with `intel_wireless_ids.AirportItlwm` and `intel_wireless_ids.Experimental`. It also freezes the `0885/0886` exclusion and every row's classification. The implementation remains the source of truth; a deliberate detector update must update the public table and parity test in the same change.
