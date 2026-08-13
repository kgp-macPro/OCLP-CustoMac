# Phase 3B KDK Selection Boundary

Artifact source implementation HEAD: `f451fd49f0500363022d92b25f0d382523818fa6`

## Result

KDK requirements are now aggregated from the final **selected applicable hardware patchsets**, rather than every applicable patchset. This makes the Modern Audio control authoritative without changing KDK discovery, matching, fallback, download, validation, installation or merge behavior.

Detection retains two separate collections:

1. `applicable_patchsets`: every patchset reported present/non-native by unchanged hardware detection; this controls which UI choices can exist.
2. `selected_hardware`: applicability intersected with the immutable current user selection; only this collection contributes requirements and patch dictionaries.

Unknown/nonselectable patch families remain selected by default. Therefore a different selected patch that requires a KDK still requires one.

## Required behavior

| Final selection | Modern Audio included | KDK required due to Audio | Existing KDK machinery |
|---|---:|---:|---|
| Wi-Fi + Audio | yes | yes | unchanged |
| Wi-Fi only | no | no | unchanged/not entered solely for Audio |
| Audio only | yes | yes | unchanged |
| Neither | no | no | unchanged/not entered |
| Other selected KDK patch | as selected | independent | remains required |

The patch-start frame revalidates the selected detection before payload mounting and again immediately before KDK handling. `PatchSysVolume` repeats detection at engine entry and refreshes its KDK flags from that same selected result. This prevents a stale all-applicable requirements dictionary from reaching KDK handling.

## What did not change

- Modern Audio's detector still returns `requires_kernel_debug_kit() == True`.
- Beta-1 AppleHDA and its patch destination are unchanged.
- KDK exact/closest matching and fallback policies are unchanged.
- KDK cache/download/install/merge code is unchanged.
- Other selected KDK-requiring patchsets are not globally suppressed.
- Modern Wireless detection, root dictionary and payload are unchanged.

## Focused validation

Five synthetic requirement-aggregation fixtures pass:

1. Wi-Fi only -> Wireless dictionary only; KDK false.
2. Audio only -> Audio dictionary only; KDK true.
3. Both -> both dictionaries; KDK true.
4. Both OFF -> empty dictionary; KDK false.
5. A nonselectable selected KDK patch with Audio OFF -> other patch retained; KDK true.

These are included in the 72-test Phase 1/2/3 discovery pass.
