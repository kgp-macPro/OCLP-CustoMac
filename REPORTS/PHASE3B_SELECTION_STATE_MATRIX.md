# Phase 3B Selection / State Matrix

Artifact source implementation HEAD: `f451fd49f0500363022d92b25f0d382523818fa6`

## Selection matrix

| Applicable / selected | Final requested dictionary | Start on CLEAN | KDK from Modern Audio |
|---|---|---:|---:|
| Wi-Fi ON, Audio ON | `Modern Wireless` (+ Extended when applicable), `Modern Audio` | enabled | yes |
| Wi-Fi ON, Audio OFF | Modern Wireless family only | enabled | no |
| Wi-Fi OFF, Audio ON | `Modern Audio` only | enabled | yes |
| Wi-Fi OFF, Audio OFF | empty in current narrow KGP scope | disabled | no |
| Wi-Fi inapplicable | Wi-Fi cannot be selected | depends on other selected patches | none from Wi-Fi |
| Audio inapplicable | Audio cannot be selected | depends on other selected patches | none from Audio |

The selection layer sees only hardware patchset applicability names. It contains no Broadcom/Intel hardware identity branch.

## Installed-state matrix

| Installed state | Initial controls | User request | Phase-2 result | Start | Revert |
|---|---|---|---|---:|---:|
| CLEAN, both applicable | both ON | both | CLEAN | enabled | disabled |
| CLEAN | user selects Wi-Fi only | Wi-Fi only | CLEAN | enabled | disabled |
| CLEAN | user selects Audio only | Audio only | CLEAN | enabled | disabled |
| CLEAN | both OFF | empty | CLEAN, empty request gate | disabled | disabled |
| Installed both, same build | both ON | both | INSTALLED_SAME | disabled | if `can_unpatch` |
| Installed Wi-Fi only, same build | Wi-Fi ON, Audio OFF | Wi-Fi only | INSTALLED_SAME | disabled | if `can_unpatch` |
| Installed Audio only, same build | Wi-Fi OFF, Audio ON | Audio only | INSTALLED_SAME | disabled | if `can_unpatch` |
| Installed both | both -> Audio OFF | Wi-Fi only | INSTALLED_DIFFERENT_PATCH_SET | blocked | required/if `can_unpatch` |
| Installed both | both -> Wi-Fi OFF | Audio only | INSTALLED_DIFFERENT_PATCH_SET | blocked | required/if `can_unpatch` |
| Installed Wi-Fi only | Audio enabled | Wi-Fi + Audio | INSTALLED_DIFFERENT_PATCH_SET | blocked | required/if `can_unpatch` |
| Installed any valid selection | change away, then exactly back | installed selection | INSTALLED_SAME | disabled | if `can_unpatch` |
| Different exact build | any controls | any | INSTALLED_DIFFERENT_BUILD | blocked | required/if `can_unpatch` |
| Legacy/foreign metadata | defaults are not trusted as installed state | any | LEGACY_FOREIGN | blocked | only safe normal revert path |
| Malformed/contradictory state | no trusted installed selection | any | INVALID_UNKNOWN | blocked | fail closed |
| Revert selected, pre-reboot | no trusted active installed selection | any | REVERT_PENDING | blocked | reboot required |

## TOCTOU matrix

| Display-time state | Operation-time state | Result |
|---|---|---|
| CLEAN, expected selection | applicability/selection unchanged | operation may proceed subject to existing validation |
| CLEAN, expected selection | patch keys changed | blocked before support payload mounting |
| CLEAN | installed state appears before click/engine | Phase-2 reclassification blocks |
| INSTALLED_SAME | controls changed | `INSTALLED_DIFFERENT_PATCH_SET`; no patch execution |
| Any | empty final request | blocked; patch engine is not invoked |

## Metadata

The installed selection is the normalized `Installed Patches` list from successful current-schema metadata. New metadata is still emitted only by the existing successful patch path and is derived from the actual filtered patch dictionary. The Phase-2 build identity schema is unchanged.

## Test coverage

The committed fixtures cover all required combinations, valid installed initialization for both/Wi-Fi-only/Audio-only, selection mismatch/recovery, non-bypass of different/legacy/invalid/revert-pending states, empty requests, inapplicability, semantic order normalization, stale-operation rejection, and actual installed-metadata content.

