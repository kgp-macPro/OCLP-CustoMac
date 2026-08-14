# Phase 3C GUI State Matrix

Artifact source implementation HEAD: `5e2c95f2897783b53ecdd84400550364a0c34ee5`

## Selection and requirement state

| Patch selection/state | Manual KDK control | Candidate | Start behavior |
|---|---|---|---|
| CLEAN, Wi-Fi + Audio | enabled, OFF by default | none | enabled if normal requirements pass |
| CLEAN, Audio only | enabled, OFF by default | none | enabled if normal requirements pass |
| CLEAN, Wi-Fi only | disabled | cleared | unchanged no-KDK Wi-Fi-only path |
| CLEAN, neither | disabled | cleared | disabled by Phase-3B empty guard |
| KDK-required -> manual ON -> requirement removed | disabled/OFF | cleared immediately | recomputed from final selection |
| requirement restored | enabled, OFF | none | recomputed normally |
| INSTALLED_SAME | may be enabled if KDK required | operation-only | Start remains blocked |
| DIFFERENT_BUILD / DIFFERENT_PATCH_SET | no bypass | irrelevant | blocked; revert/reboot/repatch policy unchanged |
| LEGACY_FOREIGN / INVALID_UNKNOWN / REVERT_PENDING | no bypass | irrelevant | fail-closed Phase-2 behavior unchanged |

Manual mode does not change semantic patch selection and therefore cannot manufacture a Phase-2 state transition.

## Dialog state

| Event | Result |
|---|---|
| Open selector | existing AUTO choice previewed; no package side effect |
| No row + confirm | confirmation blocked |
| Choose one row | exactly one candidate selected |
| Confirmation Cancel | selector remains open; no operation |
| Selector Cancel | returns to Root Patch Selection; no AUTO fallback |
| Use This KDK | confirmation and selector close; exact candidate enters normal progress workflow |
| Installed candidate | no download GUI; normal patch progress continues |
| Not-installed candidate | standard OCLP KDK download GUI appears, then normal validation/install/patch progress |
| Catalog identity changes after confirmation | fail closed before KDK/root operation |
| Manual candidate fails later | fail closed; no automatic-choice substitution |

The Root Patching progress UI remains the sole progress surface for download, validation, installation, merge, root patching, KC rebuild, snapshot and completion/failure reporting.

## Validation summary

- Phase-3C focused tests: 24 PASS
- Complete Phase-1/2/3 discovery: 105 PASS
- Locked CPython 3.14.3 x86_64 / 22-distribution environment verification: PASS
- `git diff --check`: PASS
- Targeted `iMac19,1` build and `ocvalidate`: PASS
- Built/package-expanded app signatures: PASS
- Package SHA-256: `7b7539a14200af369237de5787c47531b2ac583f75afe5cf15103e6fd3d3bbec`
