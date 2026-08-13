# Phase 2B Root State Test Matrix

Date: 2026-08-13

Focused suites:

- `tests/test_phase2b_build_metadata.py`
- `tests/test_phase2b_identical_state_blocking.py`
- `tests/test_phase2b_generated_config_exists.py`
- `tests/test_phase2b_root_state_protection.py`

## Required behavior

| Fixture | Expected classification/result | Covered |
|---|---|---|
| clean sealed snapshot, no metadata | CLEAN; Start enabled; Revert disabled | yes |
| exact build and exact patch selection | INSTALLED_SAME; Start disabled; Revert follows `can_unpatch` | yes |
| same build, different patch selection | INSTALLED_DIFFERENT_PATCH_SET; revert/reboot required | yes |
| different full commit, same selection | INSTALLED_DIFFERENT_BUILD; revert/reboot required | yes |
| same displayed version, different commit | not SAME | yes |
| legacy KGP/OCLP metadata | LEGACY_FOREIGN; never SAME | yes |
| foreign-fork filename or current-schema repository | LEGACY_FOREIGN; Start blocked | yes |
| malformed metadata | INVALID_UNKNOWN; fail closed | yes |
| missing metadata, broken/non-clean root | INVALID_UNKNOWN; no guessed revert | yes |
| metadata contradicts root/seal evidence | INVALID_UNKNOWN | yes |
| wrong metadata filename capitalization | INVALID_UNKNOWN; never clean | yes |
| duplicate case-folded metadata candidates | INVALID_UNKNOWN; ambiguous | yes, simulated independently of host filesystem case behavior |
| display SAME, click DIFFERENT | click-time revalidation blocks | yes |
| display CLEAN, click installed | click-time revalidation blocks | yes |
| operation layer receives blocked result | exits before support/root mounting | yes |
| successful revert before reboot | REVERT_PENDING; not CLEAN | yes |
| simulated reboot into clean sealed snapshot | CLEAN | yes |
| reversed dictionary order | same semantic patch selection | yes |
| existing generated config path | validation branch executes | yes |
| absent generated config path | missing-config branch executes | yes |

## Build-provenance negative fixtures

The metadata suite fails closed for missing commit URL, abbreviated SHA, wrong SHA, wrong canonical repository, wrong Git commit date, missing ref, and dirty source. A valid clean exact metadata fixture passes.

## Evidence boundary

The live evaluator binds both `APFSSnapshot` and `Sealed` to the active root object returned by `diskutil info -plist /`. If the command fails or the active-root seal field is absent, the state is UNKNOWN and patching is blocked. It does not infer the active state from another snapshot listed elsewhere in the APFS container. A missing metadata file is CLEAN only when the active root is positively a sealed APFS snapshot.

No test mutates the live root, snapshots, EFI, NVRAM, SIP, KDKs, or payloads.
