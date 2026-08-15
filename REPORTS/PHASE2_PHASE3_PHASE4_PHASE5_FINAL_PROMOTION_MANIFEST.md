# Phase 2 + Phase 3 + Phase 4 + Phase 5 Final Promotion Manifest

Date: 2026-08-15

## Promotion authority

The canonical final functional source through Phase 5 is:

`13a8aeaaaa877b197b54cf6f8452a5801d7e36ff`

Its frozen predecessor boundaries are:

- Phase-2/3 implementation: `62e0b1c0413eb900bda69955030dd5bee28219b6`
- Phase-4 implementation: `a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0`
- Phase-4 documentation: `d0d0aaf26057d1e8faa31773f6edef20098e14d6`
- Phase-5 pre-runtime documentation: `83c90cd65dc9903b49657886af1f687ddad2f954`

All phases listed here are **COMPLETE — RUNTIME VALIDATED — FROZEN**. Promotion must reconstruct the final source behavior and regression coverage. It must not blindly replay intermediate development commits or reintroduce superseded experiments.

Detailed supporting authorities remain:

- `REPORTS/PHASE2_PHASE3_FINAL_PROMOTION_MANIFEST.md`
- `REPORTS/PHASE2_PHASE3_PHASE4_FINAL_PROMOTION_MANIFEST.md`
- `REPORTS/PHASE4_RUNTIME_VALIDATION_FINAL.md`
- `REPORTS/PHASE5_INTEL_MODERN_WIFI_DEVICE_SUPPORT_AUDIT.md`
- `REPORTS/PHASE5_INTEL_MODERN_WIFI_IMPLEMENTATION.md`
- `REPORTS/PHASE5_RUNTIME_VALIDATION_FINAL.md`

## Phase 2 and Phase 3 — mandatory promoted behavior

| Area | Frozen contract |
|---|---|
| Reproducible build | CPython 3.14.3 x86_64, exact 22-wheel lock, fixed provenance, deterministic ad-hoc finalization, strict/deep verification, packaged-app parity |
| Patch authorization | CLEAN authorizes new root patching; installed, differing, pending, failed, legacy, and unknown non-clean states remain fail-closed for new patching |
| Recovery authorization | Existing/non-clean roots expose common last-sealed-snapshot recovery without artificial build/SHA/fork/patch/KDK ownership restrictions; SIP and real execution prerequisites remain enforced |
| Lifecycle | Boot-scoped, integrity-checked in-progress, failed-recovery-required, pending-reboot, and revert-pending evidence remains authoritative for state/provenance, not ownership gating |
| Selection model | Modern Wi-Fi and Modern Audio are independent, applicability-constrained selections; trusted installed metadata is truthful and read-only until Revert/reboot |
| Modern Wireless | The complete shared root-patch family is independently selectable; selection does not mutate EFI or hardware |
| Modern Audio | Beta-1 AppleHDA and its KDK requirement are present only when selected |
| Wi-Fi-only | Modern Wi-Fi with Audio off remains a no-KDK path unless another selected patch independently requires a KDK |
| Empty selection | Start is disabled; a forced explicit empty operation aborts before KDK, mount, mutation, KC, snapshot, or metadata work |
| Manual KDK | Trusted-catalog, operation-scoped exact choice; AUTO preview; confirmation; standard download/install/progress flow; no substitution after manual choice |
| KDK provenance | Successful installed metadata records AUTO/MANUAL and exact used identity as historical provenance, never as a future preference |
| Darwin-26 KDK policy | Build/ProductBuildVersion family 26 is excluded; marketing version 26.x does not trigger exclusion; inherited exact/closest ranking remains unchanged among eligible KDKs |
| Metadata compatibility | Supported OCLP-family metadata, including both `OCLP-Mod.plist` and `oclp-mod.plist`, remains recognized without falsely becoming current KGP ownership |

Every regression named in the detailed Phase-2/3 manifest remains mandatory.

## Phase 4 — mandatory promoted behavior

### APFS payload image

- `ci_tooling/build_modules/disk_images.py` creates `payloads.dmg` as APFS while preserving filename, volume identity, source tree, protected-image contract, and logical contents.
- `Universal-Binaries.dmg` remains APFS and functionally unchanged.
- pinned `payloads.dmg`: `082de073e0d103d7bd4b47852007f2b6ab360eda5b4737a089cf3b34a3910f91`
- pinned `Universal-Binaries.dmg`: `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4`
- logical payload aggregate: `789687b7ac93dd0eb686e56f5b869636e93d535c36107bef817d2906294db9da` across 351 files, 133 directories, and 0 symlinks
- native APFS UUID/container nondeterminism is accepted at the container level; the proven logical-equivalent image is pinned.

### Runtime mount and authentication

- the APFS outer image uses the existing unprivileged writable-shadow workflow;
- `Universal-Binaries.dmg` mounts at a host-sibling temporary location with its own shadow;
- a writable-shadow-layer symlink preserves the historical logical nested path;
- cleanup detaches inner before outer and leaves no stale operation mount;
- protected images use `hdiutil -stdinpass` with the repository passphrase through stdin;
- no deprecated `-passphrase`, interactive DiskImages/Keychain path, named signing identity, or privileged/general-purpose fork helper is promoted.

### Revert UX cleanup

Revert-specific detection does not perform irrelevant KDK availability/resolver probing. Normal patching retains full KDK behavior and useful status. Recovery authorization, SIP checks, root mounting, and `bless --last-sealed-snapshot` semantics remain unchanged.

Mandatory Phase-4 tests include `test_phase4_disk_images.py`, `test_phase4_runtime_disk_images.py`, `test_revert_kdk_logging.py`, frozen hashes, signatures, packaged-app parity, and the inherited Phase-2/3 suite.

## Phase 5 — generic Intel Modern Wi-Fi integration

**Promotion:** MUST PROMOTE.

**Canonical implementation:** `13a8aeaaaa877b197b54cf6f8452a5801d7e36ff`.

### Authoritative device support

- source authority: the 87-entry `IOPCIMatch` exposed identically by the audited local AirportItlwm personalities at itlwm HEAD `0b17225dfbe1b7810b114f8fa9148b09f56d4efd`;
- qualifying identity: PCI class `028000`, Intel vendor `8086`, and one of the exact 87 device IDs;
- final KGP count: 87;
- AX210 `8086:2725`: included generically, with no special-case branch;
- include AirportItlwm-backed `2720` and `2729` even though OCLP-Mod omitted them;
- exclude Mod-only `0885`, `0886`, and `272B` because the authoritative AirportItlwm personality does not expose them.

**Final source:**

- `opencore_legacy_patcher/datasets/pci_data.py` — `intel_wireless_ids.AirportItlwm`;
- `opencore_legacy_patcher/detections/device_probe.py` — `IntelWirelessCard`, complete `wifi_devices` inventory, physical-identity classification, concise initial detection log;
- `opencore_legacy_patcher/sys_patch/patchsets/hardware/networking/modern_wireless.py` — `ModernWireless.present()` accepts supported Broadcom or Intel inventory;
- `tests/test_phase5_intel_modern_wireless.py`;
- `tests/test_modern_wireless_regression.py`.

### Shared patchset and KDK invariant

Intel and Broadcom activate one existing Modern Wireless root patchset. No Intel-specific payload or duplicate patch operation is introduced. The frozen patch-method hash is `f71883e711d7eadaa45fb23799024db1d38c1da82b57c55044687cd430f880fe`.

Intel detection itself does not request a KDK. Modern Wi-Fi alone remains no-KDK; independent KDK-requiring patches retain normal aggregation.

### Detection versus runtime binding

Promotion must preserve two independent layers:

1. OCLP resolves real PCI vendor/device identity and authorizes Modern Wi-Fi applicability.
2. The user's external EFI/AirportItlwm binds Intel hardware at boot and consumes the shared restored Apple frameworks.

OCLP must not install/download AirportItlwm or mutate `config.plist`, `Kernel/Add`, boot arguments, EFI, DeviceProperties, ACPI, DMAR, or NVRAM. Neither Broadcom nor Intel spoofing is part of the feature.

### Required regressions

- every authoritative Intel ID applicable;
- unsupported Intel ID rejected;
- non-Intel vendor with overlapping device ID rejected;
- AX210 and multiple supported generations detected generically;
- Broadcom-only, Intel-only, both, and neither inventories independently tested;
- one shared Modern Wireless dictionary with no duplicated payload work;
- existing Broadcom result unchanged;
- Wi-Fi-only no-KDK behavior preserved;
- no Intel EFI-builder path, spoofing, or hardware mutation.

The final implementation suite passed 199 tests. The tested package is `/Users/kgp/Desktop/OCLP/OCLP-v2.0-phase5-intel-modern-wifi/OpenCore-Patcher.pkg`, SHA-256 `dbd3bbd56e97dfd5f9edec4b5f662ae8750326e4901698c1b13d771083f458e1`.

## Phase-5 runtime evidence boundary

Keep the evidence classes separate:

- **Broadcom control:** BCM943602CDP root patch/reboot retained AppleHDA, Broadcom Wi-Fi, and tested AWDL/Continuity functionality.
- **Intel Test A:** a Broadcom-originated shared root patch supported AX210 runtime after a powered-off hardware swap without repatching; this proves payload independence, not detector execution.
- **Intel Test B:** OCLP directly detected physical `8086:2725`, made Modern Wi-Fi applicable, patched with AX210 installed, and subsequently delivered working AppleHDA, Intel Wi-Fi, and AirPlay; this proves detection/applicability and external runtime binding separately.
- **Screen Mirroring:** unreliable except for one successful attempt; remains a FeatureUnlock/Tahoe research observation, not Phase-5 acceptance or promoted work.

Captured AX210 properties included `vendor-id <86 80 00 00>`, `device-id <25 27 00 00>`, `IOName pci8086,2725`, and class code `0x028000`. Apple-style `AirPort Extreme`/`ARPT` naming coexisted with the directly visible Intel identity. Eligibility remains a numeric vendor/device decision, not a service/display-name predicate.

## Approaches explicitly not for promotion

- OCLP-Mod-only IDs `0885`, `0886`, and `272B`;
- copying the OCLP-Mod table without AirportItlwm reconciliation;
- AX210-only logic or marketing-name matching;
- automatic Broadcom or Intel spoofing;
- any Intel-specific EFI mutation, AirportItlwm downloader/installer/injector, or `Kernel/Add` change;
- treating working AirportItlwm as proof of OCLP detection, or detection as proof of runtime binding;
- FeatureUnlock or Screen Mirroring experiments;
- temporary Phase-5 audit/debug instrumentation;
- any Phase-2/3/4 superseded experiment listed in the earlier manifests.

## Final phase status

| Phase | Status |
|---|---|
| Phase 2 | COMPLETE — RUNTIME VALIDATED — FROZEN |
| Phase 3B | COMPLETE — RUNTIME VALIDATED — FROZEN |
| Phase 3C | COMPLETE — RUNTIME VALIDATED — FROZEN |
| Phase 4 | COMPLETE — RUNTIME VALIDATED — FROZEN |
| Phase 5 — Generic Intel Modern Wi-Fi Integration | COMPLETE — RUNTIME VALIDATED — FROZEN |

The final online-repository promotion must reproduce this combined validated state, not blindly cherry-pick all development history.
