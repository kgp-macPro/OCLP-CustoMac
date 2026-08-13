# Phase 3B — Modern Wi-Fi / Modern Audio Root-Patch Selection

Date: 2026-08-13  
Artifact source implementation HEAD: `f451fd49f0500363022d92b25f0d382523818fa6`  
Baseline: `68adea563b425678f9c27e874be1a6e00f992981`

## Result

Phase 3B adds one canonical, immutable current-operation selection for the two already-applicable KGP root-patch families. Native checkboxes are displayed directly on the main **Post-Install Menu / Root Patching** dialog under **Root Patch Selection**. No Settings duplicate was added.

The architecture is:

```text
unchanged hardware detection
    -> applicable hardware patchsets
    -> RootPatchSelection
    -> selected hardware patchsets
    -> final patch dictionary and requirements
    -> Phase-2 root-state classifier
    -> GUI/click/operation gates
    -> existing patch engine
```

The selection model contains no PCI vendor/device, Broadcom, Intel, EFI, ACPI or DeviceProperties logic. A later Intel-aware `ModernWireless.present()` implementation can make Modern Wi-Fi applicable before this layer without changing the GUI/selection design.

## Implementation commits

| Commit | Purpose |
|---|---|
| `3631d4c66882b8999fab2d8932091ac5cdf8c230` | `ui: add root patch selection controls` |
| `249473cab6850633ae55eaae7a0ceef6c58f6c75` | `patch: apply selected modern wifi and audio patchsets` |
| `f451fd49f0500363022d92b25f0d382523818fa6` | `patch: derive KDK requirement from selected patchsets` |

## Canonical model and defaults

`sys_patch/root_selection.py` defines stable identifiers `modern-wifi` and `modern-audio`, maps them to existing hardware patchset names and actual patch dictionary keys, constrains selection to applicability, and preserves all nonselectable patch families.

- CLEAN with no trustworthy installed selection: all applicable selectable families default ON.
- Valid current-format installed metadata: controls initialize from `Installed Patches`.
- Legacy, foreign, invalid or revert-pending states never supply a trusted installed selection and remain fail-closed under Phase 2.
- Inapplicable families are not rendered and cannot be selected.
- Both OFF yields an empty requested patch dictionary in KGP's deliberately narrow two-family patcher, so Start is disabled.

## Main UI behavior

The main root-patching dialog renders **Modern Wi-Fi** and **Modern Audio** checkboxes only when their unchanged detectors report applicability. It shows the normalized selected-family summary and the Phase-2 state reason. Button state is recomputed whenever a checkbox changes.

Start requires all of:

1. a non-empty final patch dictionary;
2. selected-patch validation (`can_patch`);
3. Phase-2 `patch_allowed`.

Revert continues to require both an evidence-backed revertable state and existing `can_unpatch`; CLEAN does not expose Revert merely because SIP permits unpatching.

## State protection integration

Phase 2 now compares installed metadata against the **final user-requested patch dictionary**, not the full automatically applicable dictionary.

- Same exact build + same selection: `INSTALLED_SAME`, Start disabled.
- Same build + changed selection: `INSTALLED_DIFFERENT_PATCH_SET`, Revert -> reboot -> repatch required.
- Different build, legacy/foreign, invalid/unknown and revert-pending remain blocked regardless of checkbox state.
- Changing away from and back to the exact installed selection returns to `INSTALLED_SAME`; it does not make Start available.

Valid current-schema metadata exposes only its normalized `Installed Patches` selection to initialization. Legacy/foreign metadata is never promoted or rewritten.

## Operation and metadata integrity

The immutable selection and its expected semantic patch-key tuple are passed from display to start frame to `PatchSysVolume`. Detection and state are recomputed:

- when the main UI refreshes;
- immediately on Start;
- again after payload mounting and before KDK handling;
- again at patch-engine entry before support payload mounting.

If applicability or selection differs from the expected semantic tuple, operation entry returns before the support image or root volume is mounted. The engine receives the same selected dictionary that was state-classified. Existing metadata generation records `Installed Patches` from that executed dictionary, so deselected applicable families are not recorded.

## Default compatibility

With both applicable controls left ON, the selection filter returns the complete original Modern Wireless + Modern Audio dictionaries. Those dictionary source files and payloads are byte-identical to the runtime-validated Phase-2 baseline. Patch destinations and Modern Audio's KDK behavior are unchanged in this default case.

## Validation

| Check | Result |
|---|---|
| Phase 1/2/3 focused test discovery | PASS, 72 tests |
| Six Phase-1 boot-policy fixtures | PASS (included above) |
| Selection defaults/four combinations/applicability | PASS |
| Installed-selection initialization/state transitions | PASS |
| Different build/legacy/invalid/revert-pending non-bypass | PASS |
| Click/operation stale-selection rejection | PASS |
| Actual metadata contains executed selection only | PASS |
| KDK requirement selection tests | PASS, 5 focused cases |
| Targeted `iMac19,1` build + official OpenCore 1.0.7 `ocvalidate` | PASS |
| Inherited full universal validator | baseline-parity: validates through `iMac18,3`, then pre-existing `KeyError: 'iMac19,1'` |
| `git diff --check` | PASS |
| strict/deep app signature before packaging | PASS |
| strict/deep packaged-app signature | PASS |
| app/package file content | PASS, identical 110-file SHA-256 manifest |
| app/package symlink topology | PASS, identical 33-target manifest |

The universal-validator `iMac19,1` result is the already-established inherited sweep defect. Targeted generation remains valid; Phase 3 did not touch EFI-builder code.

## Frozen boundaries

There is no diff from the Phase-3 starting baseline in `payloads/`, EFI-builder source, Modern Wireless/Audio patch dictionary files, KDK matching/handler code, SIP requirements, ACPI, DMAR, DeviceProperties or AppleVTD-related paths. The ignored fixed images remain:

- `payloads.dmg`: `22581d0a9981f583d1921ca447bb0d578b3c39b20a805c5c6bac4ab5678d6f98`
- `Universal-Binaries.dmg`: `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4`

Dictionary sources remain:

- Modern Wireless: `fa0dad681239c2268d17d81a9d8f422dc359d5d2b8b9fe670f2f12d4f3485f97`
- Modern Audio: `a24581ef94b304d2252bc9db9d181a20332fe6621801dadf9bd5cb3339d2615d`

The Phase-1 boot policy remains unchanged: no automatic global `-lilubetaall`, explicit user-supplied `-lilubetaall` preserved, and exactly one `-amfipassbeta` when AMFIPass is enabled.

## Disposable artifact

Built from clean implementation HEAD `f451fd49f0500363022d92b25f0d382523818fa6` with the existing locked CPython 3.14.3 x86_64 environment and 22-distribution hash lock. No dependency download occurred.

- Package: `/Users/kgp/Desktop/OCLP/OCLP-v2.0-phase3/OpenCore-Patcher.pkg`
- SHA-256: `585e75d3709f19498c432f599b983d3a7f7e6fd0b0c72822dd98e15e98c4ce2d`
- Embedded commit/ref/date/repository metadata exactly matches the clean implementation commit.
- Package is unsigned; the contained application has the deterministic outer ad-hoc seal and passes strict/deep verification.

Nothing was installed, no installer script was executed, and no root/EFI/NVRAM/runtime operation was performed.

