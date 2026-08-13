# Phase 3A — OCLP-Mod 3.1.9 Intel Wi-Fi / Automatic Broadcom-Spoof Audit

Date: 2026-08-13

Audit type: read-only source and Git-history comparison

KGP golden runtime baseline: `51b1910a30e80fbe964459231b3e2ae1a813258e`

OCLP-Mod target: `3b15c88820a6f99d1974532b9a722925da8b2897`

OCLP-Plus secondary target: `afc5021e0c27df30c2d249fce709566220f76273`

## Decision

**C. ADOPT DETECTION ONLY** — later, inside the physical AX210 validation block.

OCLP-Mod 3.1.9 does directly recognize selected Intel PCI wireless IDs and makes its Modern Wireless root-patch detector Intel-aware. It does **not** automatically convert Intel hardware into a Broadcom identity, inject an Intel-targeted Broadcom `DeviceProperties` block, modify an independently maintained EFI, or bundle/enable AirportItlwm. The apparent “automatic spoof” is therefore not present in the audited source.

The useful concept is the small detection-layer change: recognize explicitly supported Intel hardware and allow the existing shared Tahoe user-space Modern Wireless patch to become applicable. KGP should not adopt silent EFI mutation. KGP can eventually remove the external Broadcom-spoof prerequisite for validated Intel cards, but only while retaining a separate prerequisite that the user's EFI loads a compatible AirportItlwm and only after AX210 runtime validation.

## Evidence boundary and method

Read-only sources inspected:

- `OCLP-Plus-Mod-evaluation-audit/SOURCES/OCLP-Mod-3.1.9/oclp_mod/detections/device_probe.py`
- `OCLP-Plus-Mod-evaluation-audit/SOURCES/OCLP-Mod-3.1.9/oclp_mod/datasets/pci_data.py`
- `OCLP-Plus-Mod-evaluation-audit/SOURCES/OCLP-Mod-3.1.9/oclp_mod/sys_patch/patchsets/detect.py`
- `OCLP-Plus-Mod-evaluation-audit/SOURCES/OCLP-Mod-3.1.9/oclp_mod/sys_patch/patchsets/hardware/networking/modern_wireless.py`
- `OCLP-Plus-Mod-evaluation-audit/SOURCES/OCLP-Mod-3.1.9/oclp_mod/efi_builder/networking/wireless.py`
- `OCLP-Plus-Mod-evaluation-audit/SOURCES/OCLP-Mod-3.1.9/oclp_mod/efi_builder/build.py`
- `OCLP-Plus-Mod-evaluation-audit/SOURCES/OCLP-Mod-3.1.9/oclp_mod/wx_gui/gui_sys_patch_start.py`
- corresponding KGP Phase-2 files under `opencore_legacy_patcher/`
- corresponding OCLP-Plus 3.2.2 files under `oclp_plus/`
- already-local AirportItlwm/itlwm source at `/Users/kgp/Developer/OpenIntelWireless/itlwm-dexter-awdl`, HEAD `0b17225dfbe1b7810b114f8fa9148b09f56d4efd`
- local OCLP-Mod Git history and the exact relevant diffs described below

No source was imported or executed. No network access, package download, build, EFI write, DeviceProperties write, root patch, hardware swap, or elevated operation was performed.

## 1. What Mod actually detects

### Detection mechanics

The hardware probe is real, direct Intel detection:

1. `Computer.probe()` calls `wifi_probe()` in `oclp_mod/detections/device_probe.py:731-753`.
2. `wifi_probe()` enumerates `IOPCIDevice` objects with PCI class code `0x028000` using `WirelessCard.class_code_matching_dict()` at `device_probe.py:806-820`; the class definition is at `device_probe.py:268-295`.
3. `PCIDevice.from_ioregistry(..., anti_spoof=True)` reads `IOName` in the form `pciVVVV,DDDD` when available and otherwise reads `vendor-id`/`device-id` (`device_probe.py:155-197`). This is a read-only probe, not a property writer.
4. `vendor_detect(inherits=WirelessCard)` selects a subclass by vendor/class (`device_probe.py:199-203`). `IntelWirelessCard.VENDOR_ID` is `0x8086` (`device_probe.py:559-573`).
5. `IntelWirelessCard.detect_chipset()` marks the card supported only if the device ID is in `pci_data.intelwl_ids.IntelWirelessIDs` (`device_probe.py:569-573`; `pci_data.py:1238-1379`).

This is a two-level rule:

- any `8086` class-`028000` device can be instantiated as `IntelWirelessCard`;
- only the explicit device-ID list becomes `IntelWirelessIDs` and is eligible for Modern Wireless.

Actual Intel hardware is sufficient if it is visible as an `IOPCIDevice` with wireless class `0x028000` and its real Intel identity is available through `IOName` or the ordinary vendor/device properties. No pre-existing Broadcom property is required. A user-injected `IOName` spoof can, however, influence Mod's supposedly “anti-spoof” read because Mod treats `IOName` as the preferred identity.

### Exact source-backed device table

Every row below has vendor `8086`. “AirportItlwm match” refers only to the already-local AirportItlwm `IOPCIMatch` at `AirportItlwm/Info.plist:31-36`; it is not runtime proof. For every recognized ID, Mod selects Modern Wireless on Sequoia and Tahoe through `ModernWireless.present()`.

| Intel family/source label | Exact Mod IDs | Recognized by Mod | Auto-spoofed | AirportItlwm match | Modern Wireless on Tahoe | Evidence |
|---|---|---:|---:|---:|---:|---|
| AC 7260 | `08B1, 08B2` | yes | no | yes | yes | `pci_data.py:1240-1242` |
| AC 3160 | `08B3, 08B4` | yes | no | yes | yes | `pci_data.py:1243-1245` |
| AC 7265 | `095A, 095B` | yes | no | yes | yes | `pci_data.py:1246-1248` |
| AC 3165 | `3165, 3166` | yes | no | yes | yes | `pci_data.py:1249-1251` |
| AC 8260 | `24F3, 24F4` | yes | no | yes | yes | `pci_data.py:1252-1254` |
| Source-labeled AC 4165 | `24F5, 24F6` | yes | no | yes | yes | `pci_data.py:1255-1257` |
| AC 3168 | `24FB` | yes | no | yes | yes | `pci_data.py:1258-1259` |
| AC 8265 | `24FD` | yes | no | yes | yes | `pci_data.py:1260-1261` |
| AC 9260 | `2526` | yes | no | yes | yes | `pci_data.py:1262-1263` |
| AC 9560 | `9DF0, A370, 31DC, 30DC, 271C, 271B` | yes | no | yes | yes | `pci_data.py:1264-1270` |
| AC 9462 | `42A4, 00A0, 00A4, 02A0, 40A4` | yes | no | yes | yes | `pci_data.py:1271-1276` |
| AC 9461 | `0060, 0064, 0260, 0264` | yes | no | yes | yes | `pci_data.py:1277-1281` |
| WiFi Link 4965 | `4229, 4230` | yes | no | yes | yes | `pci_data.py:1282-1289` |
| Ultimate-N 6300 | `422B, 4238` | yes | no | yes | yes | `pci_data.py:1284-1298` |
| Advanced-N 6200 | `422C, 4239` | yes | no | yes | yes | `pci_data.py:1286-1300` |
| WiFi Link 5100 | `4232, 4237` | yes | no | yes | yes | `pci_data.py:1290-1296` |
| WiFi Link 5300 | `4235, 4236` | yes | no | yes | yes | `pci_data.py:1292-1294` |
| WiFi Link 5350 | `423A, 423B` | yes | no | yes | yes | `pci_data.py:1301-1303` |
| WiFi Link 5150 | `423C, 423D` | yes | no | yes | yes | `pci_data.py:1304-1306` |
| Advanced-N 6205 | `0082, 0085` | yes | no | yes | yes | `pci_data.py:1307-1313` |
| WiFi Link 1000 | `0083, 0084` | yes | no | yes | yes | `pci_data.py:1309-1312` |
| Advanced-N 6250 | `0087, 0089` | yes | no | yes | yes | `pci_data.py:1314-1316` |
| WiFi Link 1030 | `008A, 008B` | yes | no | yes | yes | `pci_data.py:1317-1319` |
| Advanced-N 6030 | `0090, 0091` | yes | no | yes | yes | `pci_data.py:1320-1322` |
| Wireless-N 135 | `0892, 0893` | yes | no | yes | yes | `pci_data.py:1323-1325` |
| Wireless-N 105 | `0894, 0895` | yes | no | yes | yes | `pci_data.py:1326-1328` |
| Wireless-N 130 | `0896, 0897` | yes | no | yes | yes | `pci_data.py:1329-1331` |
| Wireless-N 100 | `08AE, 08AF` | yes | no | yes | yes | `pci_data.py:1332-1334` |
| Advanced-N 6235 | `088E, 088F` | yes | no | yes | yes | `pci_data.py:1335-1337` |
| Wireless-N 2200 | `0890, 0891` | yes | no | yes | yes | `pci_data.py:1338-1340` |
| Wireless-N 6150 | `0885, 0886` | yes | no | **no in inspected matcher** | yes | `pci_data.py:1341-1343` |
| Wireless-N 2230 | `0887, 0888` | yes | no | yes | yes | `pci_data.py:1344-1346` |
| Killer 1650x / AX200-class ID | `2723` | yes | no | yes | yes | `pci_data.py:1347-1348` |
| Killer 1690i | `51F0` | yes | no | yes | yes | `pci_data.py:1349-1350` |
| Killer 1690s | `54F0` | yes | no | yes | yes | `pci_data.py:1351-1352` |
| Killer 1650s | `7A70` | yes | no | yes | yes | `pci_data.py:1353-1354` |
| Killer 1650i | `7AF0` | yes | no | yes | yes | `pci_data.py:1355-1356` |
| AX201 group | `43F0, A0F0, 02F0, 06F0, 34F0, 3DF0, 4DF0, 2726` | yes | no | yes | yes | `pci_data.py:1357-1364,1369-1370` |
| Killer 1550i duplicate | `06F0` | yes | no | yes | yes | `pci_data.py:1365-1366` |
| AX210 | `2725` | yes | no | yes | yes | `pci_data.py:1367-1368` |
| AX411 | `7F70` | yes | no | yes | yes | `pci_data.py:1371-1372` |
| AX211 | `7E40` | yes | no | yes | yes | `pci_data.py:1373-1374` |
| AX211 CNVi | `51F1` | yes | no | yes | yes | `pci_data.py:1375-1376` |
| Source-comment Wi-Fi 7 group (`AX1775*/AX1790*/BE20*/BE401/BE1750*`) | `272B` only | yes | no | **no in inspected matcher** | yes | `pci_data.py:1377-1378` |

The list contains 89 entries but 88 unique IDs because `06F0` appears twice. The exact set comparison found:

- Mod-only relative to the inspected AirportItlwm matcher: `0885`, `0886`, `272B`.
- AirportItlwm-only relative to Mod: `2720`, `2729`.

Consequently, Mod's list must not be treated as an end-to-end AirportItlwm support list. The source does not contain the literal model name `BE200`; it contains one exact ID (`272B`) under a broad source comment. This audit does not infer support for any other Wi-Fi 7 or BE200 ID.

## 2. The alleged Broadcom spoof

### Finding: no Intel Broadcom spoof exists

No Intel branch exists in `oclp_mod/efi_builder/networking/wireless.py:_on_model()` (`lines 45-85`). The builder handles `Broadcom` and `Atheros`; an `IntelWirelessCard` falls through without enabling a Wi-Fi kext or writing DeviceProperties. Repository-wide searches found no Intel-targeted write of `vendor-id`, `device-id`, `compatible`, `IOName`, `built-in`, any other DeviceProperties entry, ACPI/SSDT, Kernel Patch, or AirportBrcmFixup property.

Normalized Mod output for a real Intel device is therefore:

```text
DeviceProperties:
  Add:
    <Intel Wi-Fi PCI path>:
      # no OCLP-Mod-generated entry
```

For the Intel path:

| Mechanism/property | Mod result |
|---|---|
| fake vendor ID | absent |
| fake device ID | absent |
| `compatible` | absent |
| `IOName` | absent |
| `built-in` | absent |
| `brcmfx-country` | absent |
| AirportBrcmFixup enablement/options | absent |
| Wi-Fi boot argument | absent |
| ACPI/SSDT | absent |
| Kernel/Patch | absent |

Mod does contain inherited Broadcom-only logic:

- a real supported Broadcom card can receive `brcmfx-country`, optionally `-brcmfxwowl`, and AirportBrcmFixup (`wireless.py:53-73`);
- old `AirPortBrcm4360` hardware can enable `AirPortBrcmNIC_Injector.kext`; `_wifi_fake_id()` ultimately writes only `brcmfx-country` when it has a detected country code (`wireless.py:142-177`).

That inherited method name and its comments do not prove an Intel-to-Broadcom spoof. A direct semantic diff of Mod's wireless EFI builder against the KGP Phase-2 builder showed only translated logging/comments; there is no Mod-specific Intel builder implementation.

## 3. Where the behavior acts

| Boundary | Intel-specific Mod effect |
|---|---|
| A. OCLP-generated EFI | Records the detected ID in `#Revision/Hardware-Wifi`; no Intel Wi-Fi kext, Broadcom identity, or spoof is generated. |
| B. User's existing external EFI | **No modification.** |
| C. Runtime IORegistry | Read-only probing; no property write. |
| D. Root-patch hardware detection | **Yes.** Intel eligibility is added here. |

Running OCLP-Mod only as a root patcher against an independently maintained Hackintosh EFI does **not** modify that EFI. `gui_sys_patch_start.py:309-344` passes the selected patch dictionary to `PatchSysVolume.start_patch()`; it never calls `BuildOpenCore` or writes `config.plist`. EFI generation is a separate `BuildOpenCore` path (`efi_builder/build.py:41-85,93-119`).

Users can perceive that Mod “automatically handles Intel Wi-Fi” because it recognizes Intel in the root-patch detector and applies the user-space Tahoe compatibility payload while the user's already-maintained EFI loads AirportItlwm. No Broadcom conversion is necessary for Mod's detector.

## 4. Exact Intel-to-root-patch flow

```text
Intel PCI device (8086, class 028000, explicitly listed device ID)
  -> Computer.probe()/wifi_probe()
     oclp_mod/detections/device_probe.py:731-753,806-820
  -> PCIDevice.from_ioregistry(..., anti_spoof=True) + vendor_detect()
     device_probe.py:155-203
  -> IntelWirelessCard.detect_chipset() -> IntelWirelessIDs
     device_probe.py:559-573; datasets/pci_data.py:1238-1379
  -> HardwarePatchsetDetection instantiates ModernWireless
     sys_patch/patchsets/detect.py:113-145,488-528
  -> ModernWireless.present() directly accepts IntelWirelessCard on Sequoia/Tahoe
     modern_wireless.py:54-79
  -> HardwarePatchsetDetection merges ModernWireless.patches()
     detect.py:580-598
  -> Tahoe common payload selected:
       /usr/libexec/wifip2pd
       /System/Library/PrivateFrameworks/IO80211.framework
       /System/Library/PrivateFrameworks/WiFiPeerToPeer.framework
     modern_wireless.py:129-159
```

Modern Wireless itself gains Intel awareness. Intel is **not** converted into the Broadcom class or fed through the Broadcom EFI-builder branch.

An important correction to the hypothesized flow: Mod's Intel root-patch path does not select `IOSkywalkFamily.kext`, `IO80211FamilyLegacy.kext`, or `AirPort_BrcmNIC`. Those are EFI kexts enabled by Mod's builder only inside its Broadcom branch (`efi_builder/networking/wireless.py:53-58,118-122`). They are not entries in Mod's Tahoe Modern Wireless root-patch dictionary. The Intel driver path is external AirportItlwm plus the shared user-space framework patch.

For Tahoe, the “extended” patch function returns an empty dictionary (`modern_wireless.py:103-126`), so `airportd`, CoreWLAN, and CoreWiFi are not part of the actual Tahoe path shown above.

The `name()` function contains an unreachable dual-card label: it tests whether the single `computer.wifi` object is simultaneously an `IntelWirelessCard` and `Broadcom` (`modern_wireless.py:26-48`), while `wifi_probe()` stores the first recognized card and breaks. This should not be copied.

## 5. Comparison with KGP's current external-spoof model

Current KGP Phase-2 source has no `IntelWirelessCard` class or Intel ID dataset, and `ModernWireless.present()` is Broadcom-only (`opencore_legacy_patcher/sys_patch/patchsets/hardware/networking/modern_wireless.py:28-39`). KGP therefore presently relies on the externally established working configuration described by KGP.

OCLP-Mod's actual flow is:

```text
real Intel hardware
  -> direct Intel detection
  -> direct Intel Modern Wireless applicability
  -> shared Tahoe user-space root patches
  + separately maintained AirportItlwm in the user's EFI
```

It is not a subset/superset of a Broadcom spoof; it contains no spoof at all. The exact KGP external-spoof property bytes were not found in the development or audited source evidence, so no exact key/value equivalence claim is possible. No live EFI was inspected.

## 6. AirportItlwm compatibility

Classification: **PROVEN SAFE at the static interaction boundary; runtime not yet proven.**

Mod's detection code only reads IORegistry and writes no identity property, so it cannot itself prevent AirportItlwm from attaching. The inspected AirportItlwm source matches an `IOPCIDevice` through explicit Intel `IOPCIMatch` values (`AirportItlwm/Info.plist:31-36`), casts the provider to `IOPCIDevice`, and enables PCI bus-master/IO/memory access (`AirportItlwm.cpp:1105-1135`). Its lower-level Intel matchers read the actual PCI configuration-space device ID and require `PCI_VENDOR_INTEL` (`itlwm/hal_iwx/ItlIwx.cpp:19705-19710`; `itlwm/hal_iwm/mac80211.cpp:4355-4361`).

Mod does not bundle or enable AirportItlwm: no `AirportItlwm`/`itlwm` payload or builder reference exists in the exact 3.1.9 source. The user must supply a compatible driver in the maintained EFI.

This static safety conclusion is limited to Mod's no-write detector. It is not AX210 runtime proof. It also does not validate an unknown external spoof. The current KGP external spoof is known operationally to coexist with KGP's current Intel setup, but its exact properties were not locally available for this comparison.

## 7. Existing external-spoof collision and migration

Because Mod does not generate a spoof, there is no Mod-generated duplicate DeviceProperties dictionary, key overwrite, or builder merge collision.

There is one detection nuance: Mod prefers `IOName` when `anti_spoof=True`. If an external configuration replaces `IOName` with a Broadcom string, Mod can classify the device as Broadcom instead of Intel. That can still make Modern Wireless applicable when the emulated Broadcom ID is supported, but it means the new Intel-aware path is not actually being exercised. Exact behavior depends on the external properties, which were not present in local evidence.

Safest future KGP strategy:

1. implement direct Intel recognition and root-patch applicability only;
2. do not write or merge into the user's EFI;
3. retain the current working external-spoof instructions until the AX210 direct/no-spoof test passes;
4. then publish explicit migration instructions to remove the external spoof for the validated Intel configuration;
5. warn when a Broadcom-looking `IOName` obscures otherwise known Intel hardware rather than silently rewriting it.

Existing users do not need to remove their spoof to avoid a new automatic-spoof collision, because no new spoof is recommended. They would remove it only to migrate to and validate the new direct-detection contract.

## 8. Architectural fit

Best fit: **root-patcher hardware-detection enhancement only**.

- Universal EFI Builder behavior only: insufficient for KGP's root-patcher-first users and unnecessary for AirportItlwm matching.
- Root-patcher hardware detection: correct layer.
- Automatic mutation of a user's EFI: rejected.
- Detection plus opt-in EFI modification: no source-backed need; unnecessary complexity.
- Permanent external spoof: workable but no longer technically necessary after direct detection is validated.

Detection and user selection remain separate:

```text
hardware detection
  -> patch applicability
  -> [Modern Wi-Fi] user selection
  -> requested patch set
```

The future Modern Wi-Fi/Modern Audio GUI can remain hardware-agnostic and independent of the Intel work.

## 9. Can KGP remove the external-spoof requirement?

**Yes, for explicitly validated Intel IDs, after implementation and AX210 testing.** The truthful documentation would be: “No external Broadcom spoof is required for supported Intel Wi-Fi; a compatible AirportItlwm in the user's EFI remains required.”

Minimum required implementation:

- add an Intel wireless device class to `opencore_legacy_patcher/detections/device_probe.py`;
- add a deliberately scoped, tested Intel PCI-ID dataset to `opencore_legacy_patcher/datasets/pci_data.py`;
- make `ModernWireless.present()` in `opencore_legacy_patcher/sys_patch/patchsets/hardware/networking/modern_wireless.py` accept those Intel devices on Tahoe;
- retain the stable patch identity `Modern Wireless`; do not port Mod's translated/dynamic patch names;
- add fixtures for AX210/AX200/AX201/7260/3165, unknown Intel, Broadcom, spoof-obscured identity, and selection-toggle independence;
- validate that the exact intended AirportItlwm build matches each KGP-supported ID.

No `efi_builder/networking/wireless.py` change is required for detection-only adoption, and KGP should not bundle or silently install AirportItlwm as part of this change.

## 10. Documentation and distribution impact after later adoption

| Item | Classification | Required change |
|---|---|---|
| KGP EFI-Folder distribution | **MUST CHANGE if its Intel config carries the old spoof** | Ship/describe the validated no-spoof Intel config; retain AirportItlwm. No Broadcom EFI change. |
| Intel EFI `config.plist` | **MUST CHANGE if spoof is present** | Remove only the documented spoof after validation; do not add a replacement spoof. |
| README | **MUST CHANGE** | State direct supported-ID detection and the remaining AirportItlwm prerequisite. |
| Experimental Fork thread | **MUST CHANGE** | Explain scope, migration, and AX210 evidence. |
| EFI thread | **MUST CHANGE** | Publish no-spoof Intel EFI prerequisites and rollback. |
| prerequisites | **MUST CHANGE** | Remove Broadcom-spoof requirement only for validated IDs; retain exact AirportItlwm requirement. |
| Intel setup instructions | **MUST CHANGE** | Add supported ID table and migration procedure. |
| Broadcom-spoof instructions | **MUST CHANGE** | Mark legacy/transition-only after the direct path is proven. |
| migration instructions | **MUST CHANGE** | Remove external spoof, reboot with verified Intel EFI, detect, patch, reboot, verify Wi-Fi/AWDL; document rollback. |
| Broadcom user documentation | **NO CHANGE** | Direct Intel detection does not alter Broadcom behavior. |

The current distribution's exact spoof bytes were not found in the local source evidence, so the first two classifications are conditional on the stated premise that its Intel configuration includes them.

## 11. Focus hardware coverage

| Hardware | Mod detection result | AirportItlwm source overlap | Auto-spoof | Expected root-patch result |
|---|---|---|---|---|
| AX200 | `8086:2723` is recognized (Mod labels it Killer 1650x) | yes | no | Modern Wireless selected on Tahoe |
| AX210 | `8086:2725` recognized | yes | no | Modern Wireless selected on Tahoe |
| AX201 | eight listed IDs, including `2726` | yes | no | Modern Wireless selected on Tahoe |
| 7260 | `8086:08B1`, `8086:08B2` | yes | no | Modern Wireless selected on Tahoe |
| 3165 | `8086:3165`, `8086:3166` | yes | no | Modern Wireless selected on Tahoe |
| BE200 | no generic claim | `272B` is accepted under a broad Mod source comment but absent from the inspected AirportItlwm matcher | no | root patch would be selected for `272B`, but end-to-end driver support is not established |

CNVi/CNVio is not matched generically. Only the explicit IDs in the full table are recognized.

## 12. OCLP-Plus comparison

OCLP-Plus 3.2.2 does **not** contain `IntelWirelessCard`, `intelwl_ids`, or an Intel-aware Modern Wireless detector. Its README explicitly says AirportItlwm is not supported and points Intel users to OCLP-Mod (`README.md:40-42`).

Plus contains a different Broadcom `IOName = "pci14e4,43a0"` injection for a fixed list of genuine Mac models (`oclp_plus/efi_builder/networking/wireless.py:82-95,155-166`). It runs within a Broadcom/model path and is not the Mod Intel mechanism.

Therefore Plus does not share Mod's direct Intel detection and does not provide an Intel automatic-spoof implementation. The feature is Mod-specific in the exact audited sources.

## 13. Git history and provenance

The Mod repository is complete (`--is-shallow-repository=false`), but its root commit is a bulk initial import. Direct Intel detection, the Intel ID dataset, and the Intel-aware Modern Wireless predicate are already present in that root:

- `970ceeb04cef757b9b8a3834a49216d01d37b124`
- author: laobamac `<wxcznb@qq.com>`
- date: 2024-11-24 14:32:12 +0800
- subject: `V2.3.3,Update kexts,add auto-update handle add support for AR9xxx`

The exact pre-import introducing commit is therefore unavailable in this local ancestry. Commit `52691c4de7f1d6a2e1e043417af81d149fca0158` (2024-11-30, `Push version to 2.4.3`) renamed `opencore_legacy_patcher` to `oclp_mod`; it did not introduce the already-present Intel mechanism.

Relevant subsequent changes:

| Commit | Author/date | Subject | Relevant change / entanglement |
|---|---|---|---|
| `0fc6039adae7f8b95fcdcd9cacd69e6192c95105` | laobamac, 2024-12-06 | `Add support for AX1775*/AX1790*/BE20*/BE401/BE1750* on Sequoia` | Added exact ID `272B`; small ID change plus changelog. |
| `67dbd916503bd7db61c75d51cd812f0c8f178d9a` | laobamac, 2025-02-02 | `Fix wrong patchset report on Sonoma` | Limited Intel eligibility to Sequoia and later; included unrelated generated bytecode. |
| `1a7c49dc1e131ba2618a37827fcf328b90619e77` | laobamac, 2025-04-07 | `Add support for CNVi AX211 2x2` | Added `51F1` and changed version metadata. |
| `9c715c68748ee0e0dbb0b2584b01be13beea68a1` | laobamac, 2025-06-15 | `Remove Modern WiFi patches on Tahoe,fix memory detect of WebDrivers on Tahoe` | Temporarily disabled the Tahoe path; entangled graphics behavior. |
| `c0a2bf70ae3cb388e1ee4857d910cd4da5fb5d96` | laobamac, 2025-12-25 | `Support for modern wireless patches on Tahoe` | Restored Intel/Broadcom Tahoe applicability and changed Tahoe payload mapping; touched workflows, constants, detector and GUI, so not an isolated transplant. |
| `07b17025c04173b694285bf043fa36a655fcfbb9` | laobamac, 2025-12-26 | `Improve ioreg detection stablity.` | Changed PCI-path parsing only; did not create an Intel spoof. |
| `cee97fca47ba1856769e5f44a39758c2f35fd6cb` | laobamac, 2026-01-15 | `Fix wrong setting about KDK downloading in modern wireless patchset` | Changed Modern Wireless KDK requirement to false; no identity/spoof change. |

No inspected commit adds an Intel-to-Broadcom DeviceProperties writer.

## 14. KGP implementation feasibility

Change surface: **SMALL**.

Likely implementation files:

- `opencore_legacy_patcher/detections/device_probe.py`
- `opencore_legacy_patcher/datasets/pci_data.py`
- `opencore_legacy_patcher/sys_patch/patchsets/hardware/networking/modern_wireless.py`
- focused new/extended test fixtures only

`HardwarePatchsetDetection` already consumes `ModernWireless`, so it should not need a semantic change. The EFI builder should remain unchanged. No payload, PatcherSupportPkg, ACPI, DeviceProperties, KDK, SIP, root-state, or GUI-toggle change is required.

It can be one isolated, revertible commit: **YES**.

- implementation confidence: **HIGH**;
- runtime confidence before the AX210 test: **MEDIUM**.

Confidence is not VERY HIGH because the direct no-spoof path has not been run on KGP's AX210, the exact KGP AirportItlwm build must be verified at implementation time, and Mod's ID list is not identical to the inspected AirportItlwm matcher.

## 15. Final direct answers

1. **Does Mod detect Intel directly?** Yes—real `8086` class-`028000` PCI devices are probed directly; patch eligibility is explicit-ID based.
2. **Which IDs/families?** The exact 88 unique IDs are listed in the source-backed table. AX210 `2725`, AX200-class `2723`, AX201, 7260, and 3165 are included; support is not generic for every Intel device.
3. **Does it auto-generate a Broadcom spoof?** No.
4. **What exact spoof properties are injected for Intel?** None.
5. **Where are they injected?** Nowhere. Intel affects root-patch detection only.
6. **Does it alter an existing EFI?** No. Root patching invokes `PatchSysVolume`, not the EFI builder.
7. **Does Modern Wireless gain Intel awareness?** Yes, directly in `ModernWireless.present()`.
8. **Is Intel converted into the Broadcom path?** No.
9. **Is AirportItlwm compatibility statically safe?** **PROVEN SAFE** for Mod's read-only detector/no-write interaction boundary; end-to-end AX210 runtime remains unverified.
10. **Can it coexist with KGP's external spoof?** There is no new property collision, but an external `IOName` spoof can obscure direct Intel classification. Exact KGP properties were unavailable locally.
11. **Must existing users remove their spoof?** Not to avoid a duplicate Mod/KGP write. They should remove it only when migrating to and validating the future direct-detection path.
12. **Can KGP eliminate the external-spoof requirement?** Yes for explicitly validated Intel IDs, after adding direct detection/applicability and AX210 testing; AirportItlwm remains an external EFI prerequisite.
13. **Must KGP's EFI distribution change?** Yes if the distributed Intel config currently carries the spoof; Broadcom configurations need no change.
14. **Must README/thread documentation change?** Yes, after adoption.
15. **Does Plus use the same mechanism?** No. Plus expressly excludes AirportItlwm and has no Intel detector.
16. **Where did it originate?** It is already present in Mod's 2024-11-24 root import; its earlier introducing commit cannot be established from this local history.
17. **How large is the KGP change?** Small: three source files plus tests.
18. **Can it be isolated/revertible?** Yes, one commit.
19. **Implementation confidence?** High.
20. **Runtime confidence before AX210 testing?** Medium.
21. **Can future Wi-Fi/Audio toggles remain independent?** Yes; detection precedes applicability and user selection.
22. **Final recommendation:** **C. ADOPT DETECTION ONLY**, later with the AX210 installed; do not implement an automatic Broadcom spoof or silently modify EFI.

## Integrity record

Final verification passed:

- development branch remains `experiment/amfipassbeta-v2.0` at `51b1910a30e80fbe964459231b3e2ae1a813258e`, tree `c9cccdcfa90eca7fc6a8e5e02de1d65a00d203cb`, with no remotes;
- no tracked development file differs from HEAD; this untracked report is the sole working-tree change;
- frozen identities still match the Phase-1 manifest:
  - `Universal-Binaries.dmg`: `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4`;
  - AMFIPass 1.4.1 archive: `07b266145906db41f4b13a7938fbb173ea28888cc1fa65f84417f8820adc961e`;
  - IO80211FamilyLegacy archive: `e681dcc76a2cd2cea4b0ad5f27a3c816055fde3cdccd890dd10a3e2c84e96d93`;
  - IOSkywalkFamily archive: `1e12b7ef42f55b39ea54ada97b46331220668b2c48a28656e9875c5145fe2479`;
  - KGP Modern Wireless source: `fa0dad681239c2268d17d81a9d8f422dc359d5d2b8b9fe670f2f12d4f3485f97`;
  - KGP Modern Audio source: `a24581ef94b304d2252bc9db9d181a20332fe6621801dadf9bd5cb3339d2615d`;
- production remains clean on `main` at `ec5e591e0f46e948b0258ef1c8ed5d17d6a2c865`, tree `a57963cc7cb6911617ad11edf65f80648d28a93e`, with its original `origin` unchanged;
- Mod remains clean at `3b15c88820a6f99d1974532b9a722925da8b2897`, tree `a7d71b8809e9630579f2263fd4684ea02cda0b92`, and remote-free;
- Plus remains clean at `afc5021e0c27df30c2d249fce709566220f76273`, tree `efbd57b0d0c237f2f8f9bcad60754a9dd7927ebe`, and remote-free;
- the AirportItlwm reference remains clean at `0b17225dfbe1b7810b114f8fa9148b09f56d4efd`;
- no Phase-2 source/build/state file, EFI, DeviceProperties, root volume, or hardware state changed; no package was installed, no elevated operation was used, and no Intel hardware swap occurred.
