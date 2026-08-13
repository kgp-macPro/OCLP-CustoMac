# Phase 2B Build Metadata and Root Patch State Protection

Date: 2026-08-13

Golden runtime baseline: `454bd1b867a40c301240928085eb0fa4b04452ba`

This phase does not repair a demonstrated dirty root. The prior forensic evidence remains controlling: KGP amfipassbeta did not introduce edition-specific snapshot or revert damage. Phase 2B prevents a future patch operation from overwriting an incompatible, foreign, legacy, or untrustworthy active root-patch state.

## Exact build provenance

Application construction now derives and validates immutable provenance from the clean local Git repository before packaging:

- non-empty exact branch, tag, or ref;
- full 40-character lowercase commit SHA;
- canonical repository `https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta`;
- canonical full commit URL formed from that repository and exact SHA;
- Git commit date read from the exact HEAD commit, not build time;
- project identity `OCLP 3.0.0 Nightly - amfipassbeta Edition v2.0`;
- application version `3.0.0`.

The canonical repository was established read-only from the production repository remote. No remote was added to the isolated development copy. Missing, abbreviated, inconsistent, foreign-repository, wrong-date, missing-ref, or dirty-tree provenance fails closed before application packaging. Ignored build output remains outside the source-cleanliness decision.

The built application's `Info.plist` `Github` dictionary records Branch/ref, Commit SHA, Commit URL, Commit Date, Repository, and Project. Runtime `commit_info` preserves all six values. New successful root patches write schema `KGP-Root-Patch-State-v1` and record those exact identity fields plus a deterministic `Installed Patches` list. Existing metadata is not silently upgraded.

## Enforcement boundary

The shared root-state evaluator is consumed by both the GUI and operation layer. The GUI genuinely disables Start for an installed identical state and all other blocked states. Immediately before work begins, `PatchSysVolume.start_patch()` detects the requested patch selection again and re-evaluates the active root; no support image is mounted and no root volume is mounted if the result is blocked. This closes the display-to-click TOCTOU gap.

Revert is no longer offered merely because SIP permits unpatching. It requires both an evidence-backed revertable state and the existing `can_unpatch` result. SIP requirements themselves were not changed.

## Root Patch State Protection

The minimum explicit states are:

| State | Start | Revert |
|---|---|---|
| clean sealed root, no metadata | allowed | unavailable |
| same exact build and semantic patch set | blocked: already installed | available when `can_unpatch` |
| same build, different patch set | blocked: revert/reboot/repatch | available when `can_unpatch` |
| different exact build/commit | blocked: revert/reboot/repatch | available when `can_unpatch` |
| legacy or foreign metadata | blocked; never treated as current | available only when the normal snapshot rollback is positively applicable and `can_unpatch` |
| invalid, contradictory, ambiguous, or unknown | fail closed | unavailable unless a known metadata-bearing broken snapshot provides a positively identified normal rollback path |
| successful revert, before reboot | blocked: reboot required | unavailable |

Patch selection comparison uses sorted stable patch identifiers, so dictionary order is cosmetic. Modern Wireless and Modern Audio definitions are unchanged.

## Canonical metadata path

The single canonical definition is:

`/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist`

All runtime readers and the writer use that definition. Wrong capitalization, duplicate case-folded candidates, multiple metadata families, and known foreign metadata names are detected rather than interpreted as a clean root. This directly prevents the `OCLP-R.plist` versus `oclp-r.plist` failure class found in the OCLP-R audit.

## Migration from the golden runtime baseline

The currently installed golden package can legitimately have legacy metadata without the new full identity schema. Phase 2B does not rewrite it. The first migration is deliberately:

1. revert existing root patches using the established snapshot rollback;
2. reboot into the restored sealed snapshot;
3. patch with the new exact-build Phase 2B artifact.

That is safer than inferring identity from a shared human-readable version.

## Out-of-scope systems

No Modern Audio selection, KDK strategy, result-propagation redesign, APFS payload conversion, FileVault, GPU, ACPI, DMAR, DeviceProperties, AppleVTD, DisableIoMapper, payload, or component update is part of this phase.
