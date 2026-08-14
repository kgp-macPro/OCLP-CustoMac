# Phase 2 + Phase 3 Runtime Validation Final

Date: 2026-08-15

## Closure status

| Phase | Status |
|---|---|
| **PHASE 2** | **COMPLETE — RUNTIME VALIDATED** |
| **PHASE 3B** | **COMPLETE — RUNTIME VALIDATED** |
| **PHASE 3C** | **COMPLETE — RUNTIME VALIDATED** |

The canonical runtime-validated implementation is:

`62e0b1c0413eb900bda69955030dd5bee28219b6`

The documentation-only checkpoint present when the validated artifact was finalized is:

`26130e65333288bc8b4723a89dfb1195e90125e6`

The exact runtime-tested package is:

`/Users/kgp/Desktop/OCLP/OCLP-v2.0-phase3C-recovery-hotfix/OpenCore-Patcher.pkg`

SHA-256:

`66fb1ef601ad5df57a4cf4cb3906f2c72ef82134cac1d6bd238bcd59f34ec074`

This package was validated by KGP on the real Tahoe test system. It is not rebuilt or replaced by this documentation checkpoint.

## Phase 2 runtime result

Phase 2's patch-state protection and full migration cycle are runtime validated:

1. legacy/different state blocked Start;
2. Revert was available and succeeded;
3. reboot returned the system to `CLEAN`;
4. patching from CLEAN succeeded;
5. reboot classified the active installation as the matching installed state;
6. Start was blocked for the already-installed same build/selection.

The final recovery hardening is also runtime validated:

- CLEAN authorizes the patch path and does not expose unnecessary recovery;
- CLEAN with no selected patches does not falsely expose Revert;
- existing, failed, pending, and non-clean states block new patching and expose the common Revert path;
- build/SHA/project/fork, patch-set, KDK, installed-selection, and lifecycle ownership restrictions no longer block recovery;
- SIP/`can_unpatch`, target-volume mounting, and the unchanged last-sealed-snapshot operation remain true click/operation-time prerequisites;
- KGP recovered the previously deadlocked failed/non-clean root through Revert;
- the Revert succeeded and reboot returned the system to CLEAN.

## Final root authorization architecture

Root-state authorization is deliberately separate from GUI selection prerequisites:

```text
clean / patch-authorized root
    -> Revert not authorized

non-clean / existing / failed / pending root that blocks new patching
    -> Revert authorized
```

This is not a literal inversion of the visual Start button. For example:

```text
CLEAN + Modern Wi-Fi OFF + Modern Audio OFF
    -> Start disabled because selection is empty
    -> Revert disabled because the root is CLEAN
```

True execution prerequisites remain enforced after recovery authorization. If SIP prevents execution, Revert remains the visible recovery action, the user receives the concrete prerequisite, and no mount or rollback begins.

`REVERT_PENDING` remains the deliberate exception to repeated Revert: rollback already completed and reboot is required.

## Phase 3B runtime result

The main Root Patching page's Modern Wireless and Modern Audio selection model is runtime validated:

- both applicable controls default ON in CLEAN;
- Modern Wireless selection works;
- Modern Audio/Beta-1 AppleHDA selection works;
- BOTH works;
- Wi-Fi-only works;
- Audio-only works;
- both OFF disables Start and the operation-level guard remains active;
- Wi-Fi OFF filters only root patches and does not change EFI or hardware;
- Audio OFF excludes Modern Audio and AppleHDA;
- Audio OFF removes the KDK requirement caused solely by Modern Audio;
- an independently selected KDK-requiring patch still requires a KDK;
- trustworthy installed metadata restores the exact installed selection read-only;
- changing installed selection requires Revert, reboot, and repatch;
- successful metadata records only the patch dictionary actually applied.

Runtime results include working AppleHDA, Broadcom Wi-Fi, and all tested AWDL/Continuity functions. No regression was observed in the validated Broadcom path.

## Phase 3C runtime result

Manual KDK selection and KDK safety policy are runtime validated:

- the manual selection UI works;
- the existing OCLP automatic-choice preview works without package side effects;
- AUTO KDK root patching works;
- MANUAL exact KDK root patching works;
- installed and non-installed candidate handling remains in the normal OCLP flow;
- allowed Darwin-25 KDKs work;
- build-family 26 KDKs are excluded from AUTO and MANUAL root-patching paths;
- macOS 26.6.2 with KDK `ProductBuildVersion` `25G82` is correctly permitted;
- the trusted catalog is filtered before inherited AUTO exact/closest ranking;
- the same canonical build-identity policy protects manual, local, download, operation-time, and merge-time paths.

The KDK rule is:

```text
KDK ProductBuildVersion/build family 26...
    -> prohibited for root patching

Darwin 25 and older build families
    -> remain available to existing eligible-candidate selection logic
```

Marketing product version and build family are not interchangeable:

```text
macOS 26.6.2 / KDK build 25G82
    -> permitted

KDK 26.7 / build 26A5368g
    -> prohibited
```

Inherited exact/closest ranking among permitted candidates is unchanged.

## Final invariants

The validated Phase-2/3 implementation did not intentionally change:

- Modern Wireless PCI IDs during the Phase-3B/3C Broadcom work;
- EFI hardware configuration or automatic spoofing;
- DeviceProperties, ACPI, DMAR, or AppleVTD policy;
- Modern Wireless patch dictionaries or payloads;
- Modern Audio patch dictionaries or payloads except their selection/filtering boundary;
- the Wi-Fi-only no-KDK architecture;
- inherited OCLP exact/closest KDK ranking among eligible candidates.

Broadcom and future Intel Modern Wireless integrations remain independent regression targets. Later Intel detection/integration must not retroactively reopen or redefine the runtime-validated Broadcom Phase-3 result.

## Development-history boundary

The development branch intentionally retains useful experimental history. Production promotion must use the final implementation state, not replay all commits one-for-one. In particular, do not reintroduce:

- the abandoned KDK-backed Wi-Fi-only experiment;
- superseded build/SHA/project/fork/metadata/lifecycle ownership gates on Revert;
- intermediate Darwin-26 parsing that confused macOS product version with KDK build identity;
- temporary recovery/snapshot evidence experiments removed by the final simple policy.

The companion `PHASE2_PHASE3_FINAL_PROMOTION_MANIFEST.md` is the authoritative source-and-test map for deterministic promotion.

## Next phase boundary

HFS+ to APFS payload conversion was not part of Phase 3.

It is reserved for:

**PHASE 4 — Build / Packaging Finalization**

Phase 4 has not begun at this checkpoint.

Future physical Intel Modern Wireless integration/testing also remains a separate later integration block.

## Checkpoint integrity

This is a documentation/freeze checkpoint only. No functional source, application, package, payload, KDK, live root, EFI, NVRAM, hardware, or runtime state was changed. The tested package remains the exact artifact identified above.
