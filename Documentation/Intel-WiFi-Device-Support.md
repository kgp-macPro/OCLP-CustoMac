# Intel Wi-Fi Device Support

OCLP-CustoMac recognizes the Intel PCI transport identities listed here for the single existing **Modern Wi-Fi** root-patch option. Detection is based on authentic PCI class `028000`, vendor `8086`, and device ID. It does not require a Broadcom `IOName` spoof.

This list controls root-patch applicability only:

```text
Intel hardware detection / Modern Wi-Fi applicability
    !=
AirportItlwm runtime driver binding
```

OCLP-CustoMac does not provide or install AirportItlwm, modify EFI or `Kernel/Add`, inject DeviceProperties, create Intel/Broadcom spoofing, or guarantee runtime support for Experimental devices. AirportItlwm remains external.

The implementation source is authoritative:

- regular IDs: `opencore_legacy_patcher.datasets.pci_data.intel_wireless_ids.AirportItlwm`;
- experimental/development IDs: `opencore_legacy_patcher.datasets.pci_data.intel_wireless_ids.Experimental`.

Automated tests require the two marked tables below to match those sets exactly.

## Regular

**Regular** means present in the current authoritative AirportItlwm IOKit matcher and recognized normally by OCLP-CustoMac. A transport ID may represent multiple subsystem variants, so broad family language is used where the ID alone does not prove a marketing SKU.

<!-- INTEL_WIFI_REGULAR_IDS_START -->
| PCI ID | Family / association | Interface | Classification | Notes |
|---|---|---|---|---|
| `8086:2723` | AX200 family | PCIe | Regular | Current AirportItlwm matcher entry. |
| `8086:43F0` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:A0F0` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:34F0` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:4DF0` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:02F0` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:3DF0` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:06F0` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:2720` | AX201-class integrated transport | CNVi family | Regular | Current AirportItlwm matcher entry; exact adapter depends on platform/subsystem identity. |
| `8086:2725` | AX210 family | PCIe | Regular | Current AirportItlwm matcher entry; physical 8086:2725 path runtime validated. |
| `8086:2726` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:7A70` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:7AF0` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:51F0` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:54F0` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:2729` | newer MA integrated transport | CNVi family | Regular | Current AirportItlwm matcher entry; exact adapter depends on RF/subsystem identity. |
| `8086:7E40` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:7F70` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:51F1` | iwx — Wi-Fi 6 / 6E transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:08B1` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:08B2` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:08B3` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:08B4` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:095A` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:095B` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:3165` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:3166` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:24F3` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:24F4` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:24F5` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:24F6` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:24FB` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:24FD` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:2526` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:9DF0` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:A370` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:31DC` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:30DC` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:271C` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:271B` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:42A4` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:00A0` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:00A4` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:02A0` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:40A4` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0060` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0064` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0260` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0264` | iwm — Wireless-AC transport family | PCIe/CNVi family | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:4229` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:422B` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:422C` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:4230` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:4232` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:4235` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:4236` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:4237` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:4238` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:4239` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:423A` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:423B` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:423C` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:423D` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0082` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0083` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0084` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0085` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0087` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0089` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:008A` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:008B` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0090` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0091` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0892` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0893` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0894` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0895` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0896` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0897` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:08AE` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:08AF` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:088E` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:088F` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0890` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0891` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0887` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
| `8086:0888` | iwn — WiFi Link / Centrino Wireless-N transport family | PCI transport | Regular | Current AirportItlwm matcher entry; exact marketing SKU is not inferred from this ID. |
<!-- INTEL_WIFI_REGULAR_IDS_END -->

Regular count: **87**.

## Experimental / Development

**Experimental / Development** means an additional current Intel wireless transport intentionally recognized so active Intel/AirportItlwm work is not blocked by the root patcher. Detection means only that Modern Wi-Fi root patching is applicable. Stock AirportItlwm runtime support is not guaranteed; a compatible experimental or modified AirportItlwm build may be required.

A base PCI ID is not always a one-to-one product name. In particular, `272B` covers discrete BE200 and BE202 variants through further subsystem identity. Integrated BE201, BE211, and BE213 differentiation can require RF/subdevice information that the OCLP-CustoMac PCI detector intentionally does not claim to know.

<!-- INTEL_WIFI_EXPERIMENTAL_IDS_START -->
| PCI ID | Transport / family association | Interface | Classification | Runtime-support caveat |
|---|---|---|---|---|
| `8086:272B` | Discrete BZ/GL transport; source-backed BE200/BE202 and Killer/OEM associations vary by subsystem | PCIe | Experimental / Development | Applicability only; a compatible experimental/modified AirportItlwm may be required. |
| `8086:A840` | Integrated BZ host; BE201/BE-series association requires RF/subdevice evidence | CNVio-family host | Experimental / Development | Applicability only; a compatible experimental/modified AirportItlwm may be required. |
| `8086:7740` | Integrated BZ host; exact adapter requires RF/subdevice evidence | CNVio-family host | Experimental / Development | Applicability only; a compatible experimental/modified AirportItlwm may be required. |
| `8086:4D40` | Integrated BZ host; BE201/BE211/BE213-class differentiation requires RF/subdevice evidence | CNVio-family host | Experimental / Development | Applicability only; a compatible experimental/modified AirportItlwm may be required. |
| `8086:E440` | Integrated SC host; E440/0114 is a source-backed BE211 example | CNVio3-family host | Experimental / Development | Applicability only; a compatible experimental/modified AirportItlwm may be required. |
| `8086:E340` | Integrated SC host; exact adapter requires RF/subdevice evidence | CNVio-family host | Experimental / Development | Applicability only; a compatible experimental/modified AirportItlwm may be required. |
| `8086:D340` | Integrated SC host; exact adapter requires RF/subdevice evidence | CNVio-family host | Experimental / Development | Applicability only; a compatible experimental/modified AirportItlwm may be required. |
| `8086:6E70` | Integrated SC host; exact adapter requires RF/subdevice evidence | CNVio-family host | Experimental / Development | Applicability only; a compatible experimental/modified AirportItlwm may be required. |
| `8086:D240` | Integrated SC host; exact adapter requires RF/subdevice evidence | CNVio-family host | Experimental / Development | Applicability only; a compatible experimental/modified AirportItlwm may be required. |
<!-- INTEL_WIFI_EXPERIMENTAL_IDS_END -->

Experimental / Development count: **9**.

## Explicitly Excluded

**Excluded** means a known Intel identity deliberately outside the current detector policy.

<!-- INTEL_WIFI_EXCLUDED_IDS_START -->
| PCI ID | Association | Classification | Rationale |
|---|---|---|---|
| `8086:0885` | Centrino Wireless-N / WiMAX 6150-era hardware | Excluded | Legacy identity absent from the current AirportItlwm personality and outside the current Modern Wireless development scope. |
| `8086:0886` | Centrino Wireless-N / WiMAX 6150-era hardware | Excluded | Legacy identity absent from the current AirportItlwm personality and outside the current Modern Wireless development scope. |
<!-- INTEL_WIFI_EXCLUDED_IDS_END -->

OCLP-Mod contains both legacy IDs. OCLP-CustoMac does not include an ID merely for fork-list parity.

## Differences from OCLP-Mod

The final result comes from a three-way audit of the current AirportItlwm matcher, current upstream Intel BZ/SC definitions, and the local OCLP-Mod list:

- **85 regular IDs** are shared by AirportItlwm and OCLP-Mod.
- `2720` and `2729` are current AirportItlwm IDs absent from OCLP-Mod; OCLP-CustoMac includes them.
- `272B` is the current BZ development ID also present in OCLP-Mod; OCLP-CustoMac includes it as Experimental / Development.
- `A840, 7740, 4D40, E440, E340, D340, 6E70, D240` are current upstream BZ/SC transports absent from OCLP-Mod; OCLP-CustoMac includes them as Experimental / Development.
- `0885` and `0886` are OCLP-Mod-only relative to the final KGP policy and remain explicitly excluded.

For the evidence, source links, subsystem qualifications, and complete device-by-device matrix, see [the Phase-5 device support audit](../REPORTS/PHASE5_INTEL_MODERN_WIFI_DEVICE_SUPPORT_AUDIT.md).

## Updating This List

A deliberate detector update must change the implementation set, this public table, and the source/documentation parity test together. The test rejects undocumented additions, stale documented IDs, silent classification changes, dropped BZ/SC IDs, and reintroduction of excluded legacy IDs.

