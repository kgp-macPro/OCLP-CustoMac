# Root Patch Recovery and Darwin 26 KDK Implementation

## Scope and baseline

Implementation started from clean source commit:

`4fe8f1326b4f293537f989479675b9588bbfabf3`

The only pre-existing working-tree item was the completed, untracked audit report:

`REPORTS/ROOT_PATCH_REVERT_SAFETY_AUDIT.md`

No production, upstream, OCLP-Plus, OCLP-Mod, EFI, NVRAM, hardware, package, or installed root-patch state was modified.

The clean implementation HEAD after the two source commits is:

`53c44be749e77d830b4ee5ba733321f40d31ec02`

## Implementation commits

1. `8351c95de20810390bf192d391c3707b2b7f9723` — `state: preserve evidence-backed root recovery`
2. `53c44be749e77d830b4ee5ba733321f40d31ec02` — `kdk: prohibit Darwin 26 root patch kits`

A documentation-only checkpoint commits this report and the completed audit separately from implementation. Its SHA is reported in the final handoff.

## Exact files changed

Runtime source:

- `opencore_legacy_patcher/support/kdk_handler.py`
- `opencore_legacy_patcher/support/kdk_selection.py`
- `opencore_legacy_patcher/sys_patch/root_state.py`
- `opencore_legacy_patcher/sys_patch/sys_patch.py`
- `opencore_legacy_patcher/sys_patch/utilities/kdk_merge.py`
- `opencore_legacy_patcher/wx_gui/gui_sys_patch_display.py`

Tests:

- `tests/test_darwin26_kdk_policy.py`
- `tests/test_modern_wireless_regression.py`
- `tests/test_root_patch_recovery_authorization.py`
- `tests/test_phase3b_empty_selection_guard.py`
- `tests/test_phase3c_installed_selection_readonly.py`
- `tests/test_phase3c_manual_kdk_gui.py`
- `tests/test_phase3c_manual_kdk_resolver.py`

Reports:

- `REPORTS/ROOT_PATCH_REVERT_SAFETY_AUDIT.md`
- `REPORTS/ROOT_PATCH_RECOVERY_AND_DARWIN26_KDK_IMPLEMENTATION.md`

## Root-state authorization model

### Before

The state classifier already computed strict `patch_allowed` and evidence-sensitive `revert_applicable`, but the GUI collapsed recovery authorization and SIP executability into one result:

`Revert enabled = revert_applicable AND can_unpatch`

A positively identified installed or pending patched state could therefore show both Start and Revert disabled when SIP did not currently permit the rollback operation. The operation layer also checked `can_unpatch` before explaining whether the current root state authorized recovery.

### After

`RootPatchStateResult` now exposes the meanings explicitly:

- `patch_authorized`: root-state authorization to start patching;
- `recovery_authorized`: positive root-state evidence authorizing recovery;
- `revert_allowed(can_unpatch)`: recovery is authorized and the SIP-derived execution prerequisite currently passes.

The compatibility fields `patch_allowed` and `revert_applicable` remain intact. Existing state-classification semantics were not removed.

The UI applies the layers independently:

1. Root state decides which operation is authorized.
2. Patch selection and other runtime requirements may disable Start without creating recovery authorization.
3. An evidence-backed recovery state keeps Revert visible/enabled even if SIP currently blocks execution.
4. Clicking Revert revalidates state and then refuses execution with a concrete SIP prerequisite message when `can_unpatch` is false.
5. `PatchSysVolume.start_unpatch()` independently reevaluates root state first, then enforces `can_unpatch`, then mounts and uses the unchanged rollback engine.

This prevents a silent Patch-off/Revert-off deadlock for positively identified installed or pending patch states without enabling Revert on a clean system merely because both patch-selection toggles are off.

### State behavior

| Root state/evidence | Patch authorized | Recovery authorized | Notes |
|---|---:|---:|---|
| `CLEAN` | Yes | No | Empty user selection may disable the Start button, but does not enable Revert. |
| `PATCH_PENDING_REBOOT` | No | Yes | Applies equally to AUTO-KDK, MANUAL-KDK, and no-KDK patch operations. |
| `INSTALLED_SAME` | No | Yes | Installed current build/selection is read-only and revertable. |
| `INSTALLED_DIFFERENT_PATCH_SET` | No | Yes | Revert, reboot, then repatch remains required. |
| `INSTALLED_DIFFERENT_BUILD` | No | Yes | Exact SHA mismatch still blocks patching but not evidence-backed rollback. |
| recognized OCLP-family metadata + active patched root | No | Yes | Recovery only; never treated as current/equal KGP metadata. |
| `REVERT_PENDING` | No | No | Reboot is required; another patch or revert is not authorized. |
| malformed/ambiguous/unknown without independent recovery evidence | No | No | Fail closed; no snapshot scanning or guessing. |

Valid boot-scoped lifecycle evidence remains authoritative before the first reboot and remains consumable by another same-lineage KGP build without exact SHA equality. The lifecycle mechanism remains independent of AUTO/MANUAL/no-KDK provenance.

## SIP and `can_unpatch`

SIP enforcement was not weakened.

For a recovery-authorized state with `can_unpatch == False`:

- Start remains disabled;
- Revert remains visibly identifiable as the required recovery path;
- the state text explains that current System Integrity Protection settings prevent execution;
- clicking Revert starts no mount or rollback and displays the prerequisite;
- direct/internal operation entry revalidates the root state, logs the SIP block, emits existing detailed requirement errors, and stops before mounting.

Mount, `bless --last-sealed-snapshot`, cleanup, and snapshot semantics are unchanged.

## OCLP-family metadata compatibility

The recognized source-backed registry now includes both:

- `OCLP-Mod.plist` → required identity key `OCLP-Mod`;
- `oclp-mod.plist` → required identity key `OCLP-Mod`.

Existing `OCLP-Plus.plist`/`OCLP-Plus` and `OCLP-R.plist`/`OCLP-R` recognition is preserved.

Foreign metadata is no longer accepted by filename alone. The plist must be a dictionary and contain the expected nonempty family identity. Multiple family files, malformed plists, missing identity keys, and ambiguous capitalization remain invalid. Canonical legacy metadata must contain a valid `OpenCore Legacy Patcher` identity unless it declares the current KGP schema.

Recognized foreign metadata plus active patched-root evidence authorizes recovery only. It never authorizes patching and is never classified as current KGP metadata.

## Global Darwin 26 KDK policy

One central build policy in `support/kdk_selection.py` parses the leading Darwin major from the Apple KDK build identifier. Darwin major `26` is prohibited for root patching. A missing or unparsable build identity also fails closed at acceptance/use boundaries.

The policy is applied at every relevant path:

1. **Trusted catalog exposure:** prohibited candidates are omitted from `available_candidates()`, so they cannot appear as eligible manual rows.
2. **Automatic exact/closest resolution:** the existing resolver applies its unchanged exact/closest algorithm only to permitted catalog entries.
3. **Manual exact resolution:** a selected candidate must pass Tahoe eligibility, the central build policy, and exact trusted-catalog identity matching; no substitution is introduced.
4. **Resolved-candidate exposure:** a prohibited resolved build cannot be returned to UI or operation callers.
5. **Local installed lookup:** exact, version-based fallback, dialog status, and backup restoration paths reject Darwin 26 builds. Installed KDK validation reads `ProductBuildVersion` and refuses Darwin 26 without deleting it as corrupt.
6. **Download resolution:** `retrieve_download()` rechecks the selected build before either installed reuse or creating a download object. A Darwin 26 URL is never returned for download.
7. **Predownload installation:** the root merge path reads `KDKInfo.plist`, requires an established build identity, and rejects Darwin 26 before installing the DMG.
8. **Operation-time/manual revalidation:** existing GUI and patch-operation resolver construction now consumes the guarded resolver, so a stale or programmatic Darwin 26 manual candidate fails before support-package/root-patch work.
9. **Merge-time final validation:** the merge path checks the resolver build repeatedly and reads the actual installed KDK `SystemVersion.plist` before any KDK merge. A Darwin 26 installed identity cannot be merged or used.

If a prohibited catalog entry precedes a valid supported candidate, the existing closest-match resolver continues over the filtered candidate set and uses the valid candidate. No new cross-major fallback algorithm was invented. If no permitted candidate satisfies existing policy, resolution fails rather than using Darwin 26.

Darwin 24 and Darwin 25 candidate behavior remains valid in regression fixtures. AUTO mode retains the prior exact/closest semantics for permitted candidates. KDK download/install UI, KDK merge commands, kernel-cache rebuild commands, and manual no-substitution semantics are unchanged.

## Phase 3B and wireless preservation

The full Phase 3B/3C selection suites remain green:

- BOTH, Wi-Fi-only, Audio-only, and neither retain their established selection behavior.
- Wi-Fi-only remains no-KDK when no other selected patch requires a KDK.
- Audio OFF still excludes Modern Audio/Beta-1 AppleHDA and its sole KDK requirement.
- other selected KDK-requiring patches still require a permitted KDK.
- empty selection still blocks before KDK/root operations.
- state, click-time, pre-KDK, and operation-time revalidation remains active.
- installed metadata still records only patches actually applied.

`modern_wireless.py`, `modern_audio.py`, and `device_probe.py` are byte-identical to baseline commit `4fe8f132...`. No Modern Wireless/Audio dictionary, payload, PCI ID, spoof, or hardware-detection code changed.

The supported Broadcom detector path is covered directly. KGP's present Intel workflow remains the previously documented external Broadcom-identity/applicability path; no direct Intel PCI detection was added. A hardware-agnostic applicability fixture confirms the selection layer continues to consume Modern Wireless applicability without inspecting Broadcom/Intel IDs, so the existing external Intel path is not coupled to the new KDK policy.

## Validation results

- New recovery/KDK/wireless tests: **24 passed, 0 failed**.
- Complete repository unit-test discovery: **166 passed, 0 failed**.
- `python3 -m compileall -q opencore_legacy_patcher tests`: passed.
- `git diff --check`: passed.
- Frozen-source differential for Modern Wireless, Modern Audio, device probing, EFI builder, and datasets: no differences from `4fe8f132...`.

The full suite emitted one pre-existing `ResourceWarning` for an unclosed config plist in `efi_builder/support.py:130`; it did not fail a test and is unrelated to this change. Error/warning log lines from negative-path fixtures are expected assertions of fail-closed behavior.

## Known limitations

- A pre-lifecycle, pre-first-reboot patch prepared by an older build cannot be inferred safely from a still-clean active root. This remains fail-closed; no unrelated APFS snapshot scan or guessing was added.
- Malformed, duplicate, ambiguous, or unknown metadata does not receive broad recovery authorization. A valid pending lifecycle is independent positive evidence; otherwise active patched-root evidence must be paired with structurally recognized OCLP-family metadata.
- Recovery authorization does not guarantee execution: SIP, root-volume mount, or `bless --last-sealed-snapshot` can still fail. These existing execution prerequisites remain enforced and are now surfaced without hiding the recovery path.
- No new Darwin-generation fallback policy was added. The existing resolver selects among permitted candidates; it fails if none meets its established compatibility rules.

## Integrity statement

No changes were made to:

- Modern Wireless or Modern Audio detection/dictionaries/payloads;
- Intel PCI support or Broadcom spoofing;
- EFI, DeviceProperties, ACPI, DMAR, AppleVTD, or hardware state;
- KDK merge commands or kernel-cache rebuild commands;
- SIP requirements;
- APFS snapshot creation or `bless` rollback implementation;
- component versions or payload identities.

Production remained at `ec5e591e0f46e948b0258ef1c8ed5d17d6a2c865`, clean, with its original `origin` remote. The development repository remains remote-free. No package was built or installed, no root patch or revert was performed, and no network dependency resolution was used.

After the documentation-only checkpoint containing the two reports, the development working tree is clean. The documentation commit changes history only; the implementation source remains exactly `53c44be749e77d830b4ee5ba733321f40d31ec02`.
