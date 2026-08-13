# Phase 2B Golden Baseline Differential

Date: 2026-08-13

Golden runtime baseline: `454bd1b867a40c301240928085eb0fa4b04452ba`

## Intentional changes

- strict build provenance derivation, validation, embedding, and consumption;
- exact-build fields in metadata written after a new successful patch;
- shared root-patch state classification and GUI/operation enforcement;
- state-aware Revert availability and explicit in-process reboot-pending state;
- canonical root-patch metadata path used by existing consumers;
- generated-config `Path.exists()` semantic correction;
- focused synthetic tests and Phase 2B documentation.

No root-patch payload, component archive, patch dictionary, patch destination, SIP requirement, KDK selection algorithm, or generated EFI policy was intentionally changed.

## Frozen identity recheck

| Boundary | Golden SHA-256 | Phase 2B pre-commit SHA-256 | Result |
|---|---|---|---|
| `Universal-Binaries.dmg` / PatcherSupportPkg | `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4` | same | unchanged |
| AMFIPass 1.4.1 archive | `07b266145906db41f4b13a7938fbb173ea28888cc1fa65f84417f8820adc961e` | same | unchanged |
| IO80211FamilyLegacy archive | `e681dcc76a2cd2cea4b0ad5f27a3c816055fde3cdccd890dd10a3e2c84e96d93` | same | unchanged |
| IOSkywalkFamily archive | `1e12b7ef42f55b39ea54ada97b46331220668b2c48a28656e9875c5145fe2479` | same | unchanged |
| local Navi WhateverGreen archive | `c7c841f1776f40009eeb0a1d23c697a49fb76be772ee14863d30abad78a91474` | same | unchanged |
| Modern Wireless patch dictionary source | `fa0dad681239c2268d17d81a9d8f422dc359d5d2b8b9fe670f2f12d4f3485f97` | same | unchanged |
| Modern Audio patch dictionary source | `a24581ef94b304d2252bc9db9d181a20332fe6621801dadf9bd5cb3339d2615d` | same | unchanged |
| centralized EFI/boot-argument builder | `65380814d0c6f5fff52377a0c81a3eab9f257016868214dc93e491a263b51098` | same | unchanged |
| Wireless EFI builder | `1551de078fe38633f555702c6055ffe01719e4ba98ad4881dc5ad1b7ce2b46d7` | same | unchanged |
| Security/AMFIPass EFI builder | `c0929ea54c0890ec74923d54b8b5a26ecabf0c176b6cbcf9681c762042134336` | same | unchanged |

`Universal-Binaries.dmg` identity also preserves the audited Beta-1 AppleHDA executable and `__text` hashes recorded in `MANIFESTS/PHASE1_COMPONENT_SHA256.md`.

## Phase 1 and Phase 2A boundaries

The Phase 1 component versions remain OpenCorePkg 1.0.7, Lilu 1.7.2, WhateverGreen 1.7.0, RestrictEvents 1.1.6, AirportBrcmFixup 2.2.0, BlueToolFixup 2.7.2, NVMeFix 1.1.3, CPUFriend 1.3.0, CryptexFixup 1.0.5, DebugEnhancer 1.1.1, FeatureUnlock 1.1.8, AppleALC 1.9.7, and AMFIPass 1.4.1.

The Phase 1 boot policy is unchanged: KGP does not automatically inject global `-lilubetaall`, deliberately supplied `-lilubetaall` is preserved, and enabled AMFIPass receives exactly one `-amfipassbeta`.

The locked CPython 3.14.3 x86_64 dependency environment and Phase 2A build/signature-finalization infrastructure are unchanged. Phase 2B adds no Python dependency and downloads no package.

## Source-boundary review

The only KDK-related source edit replaces a duplicated literal metadata path with the canonical constant; matching, selection, installation, and fallback behavior are unchanged. The same path-only consolidation applies to existing patch detection, kernel-collection auxiliary checks, device-probe metadata parsing, and GUI support readers.

No files implementing Modern Wireless or Modern Audio dictionaries, SIP validation, ACPI, DMAR, DeviceProperties, AppleVTD, DisableIoMapper, patch destinations, or payload data are changed relative to the golden baseline.
