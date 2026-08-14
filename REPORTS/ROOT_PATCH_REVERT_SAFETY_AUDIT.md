# Root Patch Revert Safety Audit

## Scope and source baselines

This is a read-only source audit. No patch, revert, snapshot, EFI, KDK, or implementation operation was performed.

| Source | Exact local revision |
|---|---|
| Current KGP v2.0 | `4fe8f1326b4f293537f989479675b9588bbfabf3` |
| Original production OCLP-amfipassbeta | `ec5e591e0f46e948b0258ef1c8ed5d17d6a2c865` |
| Local Dortania/OCLP reference | `b9df76ebdf3e768b37c1cc980e8444aa837c623e` |
| OCLP-Plus 3.2.2 | `afc5021e0c27df30c2d249fce709566220f76273` |
| OCLP-Mod 3.1.9 | `3b15c88820a6f99d1974532b9a722925da8b2897` |

## Executive finding

The actual APFS rollback engine does **not** require the reverting application to have the same Git commit, project identity, patch selection, KDK selection mode, or metadata schema as the application that patched the root. Those identities are consumed by the KGP v2.0 state policy before the rollback engine is reached; the rollback itself mounts the current System volume and invokes `bless --last-sealed-snapshot`.

The correct design principle is therefore:

> Patch authorization and recovery authorization are separate decisions.

Strict build/selection equality is appropriate before modifying an existing patched state. It is not, by itself, a technical prerequisite for selecting a positively identified last sealed snapshot.

There are four important qualifications:

1. Current `INSTALLED_DIFFERENT_BUILD` already permits Revert. It does not cause the reported dead end by itself.
2. Current `PATCH_PENDING_REBOOT` permits Revert for AUTO-KDK, MANUAL-KDK, and no-KDK operations, including same-boot application relaunch, when its lifecycle record is valid and `can_unpatch` is true.
3. A patch made by an older build that did not write the new lifecycle record cannot be reconstructed reliably before first reboot from the currently active root alone. The active root may still look clean/sealed even though another snapshot has been prepared for the next boot.
4. The foreign-family recognizer lists `OCLP-Mod.plist`, but Mod 3.1.9 actually writes `oclp-mod.plist`. On a case-sensitive source comparison this is a real recognition gap. Current KGP can consequently classify an active Mod-patched root as metadata-missing/unknown and withhold Revert.

The observed “another program or previous version” label is therefore not enough to identify the blocking gate. Under current HEAD, a valid different-build state and a valid pending lifecycle both allow Revert. The disabled outcome requires one of the following additional conditions:

- `can_unpatch == False` (the selected/current hardware requirements report SIP as insufficient);
- the patching build predated `PATCH_PENDING_REBOOT` lifecycle recording;
- the lifecycle record was absent, stale, unreadable, or invalid;
- the active pre-reboot root still appeared clean/sealed, so no active patched-root evidence existed;
- the foreign metadata filename was not recognized, notably Mod's lowercase `oclp-mod.plist`;
- root evidence or metadata was contradictory/unknown and did not satisfy the classifier's conditional recovery rule.

## 1. Complete current revert gating chain

### Gate 1: GUI state calculation

**File:** `opencore_legacy_patcher/wx_gui/gui_sys_patch_display.py`
**Function:** `SysPatchDisplayFrame._refresh_selection_state()`
**Relevant lines:** 338-412

The GUI performs fresh hardware detection, constrains the current selection, produces the final requested patch dictionary, and evaluates `RootPatchStateEvaluator`. It enables Revert only when:

```text
root_state.revert_applicable AND detection.can_unpatch
```

This is implemented through `RootPatchStateResult.revert_allowed(can_unpatch)` in `root_state.py:79-80` and consumed at `gui_sys_patch_display.py:411`.

- `can_unpatch` is consulted.
- state, metadata, lifecycle, and active-root evidence are consulted indirectly through `RootPatchStateEvaluator`.
- exact patch/build ownership does not appear in the GUI conditional itself.

### Gate 2: click-time GUI revalidation

**File:** `opencore_legacy_patcher/wx_gui/gui_sys_patch_display.py`
**Function:** `SysPatchDisplayFrame.on_revert_root_patching()`
**Relevant lines:** 527-544

The click handler calls `_refresh_selection_state()` again and repeats the same combined test. A stale enabled button cannot bypass a changed state or changed `can_unpatch` result.

If the condition fails, the handler shows the classifier reason and never creates the revert progress operation.

### Gate 3: progress-UI handoff

**File:** `opencore_legacy_patcher/wx_gui/gui_sys_patch_start.py`
**Functions:** `revert_root_patching()` and `_revert_root_patching()`
**Relevant lines:** 489-512

This layer displays the existing progress UI and calls `PatchSysVolume(...).start_unpatch()`. It does not make a separate ownership or snapshot decision.

### Gate 4: operation-time `can_unpatch`

**File:** `opencore_legacy_patcher/sys_patch/sys_patch.py`
**Function:** `PatchSysVolume.start_unpatch()`
**Relevant lines:** 713-726

The operation creates a new `HardwarePatchsetDetection` and aborts if `patchset_obj.can_unpatch` is false. This is independent of the GUI and also protects direct/internal/CLI entry.

The current detector calculates:

```text
_cant_unpatch = requirements[SIP_ENABLED]
can_unpatch = not _cant_unpatch
```

at `sys_patch/patchsets/detect.py:527-549`. The SIP result comes from `utilities.csr_decode(required_sip_configs)` at `detect.py:196-200`.

At this gate:

- SIP/`can_unpatch` is consulted.
- metadata ownership and build identity are not consulted.
- lifecycle and active snapshot state are not consulted.
- other patching validation failures such as missing KDK, network, FileVault, AMFI, or Secure Boot do not directly define `_cant_unpatch` in the inspected code.

### Gate 5: operation-time state revalidation

**File:** `opencore_legacy_patcher/sys_patch/sys_patch.py`
**Function:** `PatchSysVolume.start_unpatch()`
**Relevant lines:** 728-731

The operation creates a new `RootPatchStateEvaluator`, evaluates the current requested patch dictionary, and aborts unless `root_state.revert_applicable` is true.

This gate is distinct from `can_unpatch`. It is the Phase-2/Phase-3 policy addition that can make current KGP more restrictive than inherited OCLP, Plus, and Mod.

### Gate 6: root-volume mount

**Files:**

- `opencore_legacy_patcher/sys_patch/sys_patch.py:733-735`
- `opencore_legacy_patcher/sys_patch/mount/mount.py:26-75`

The active root's APFS volume identifier is resolved with `diskutil info -plist /`; a snapshot suffix is removed; the underlying System volume is mounted at `/System/Volumes/Update/mnt1`. Mount failure aborts.

No installed patch metadata, Git identity, or KDK identity is required by this mount path.

### Gate 7: actual snapshot rollback

**Files:**

- `opencore_legacy_patcher/sys_patch/sys_patch.py:219-225`
- `opencore_legacy_patcher/sys_patch/mount/snapshot.py:56-69`

For Big Sur and later, rollback executes:

```text
/usr/sbin/bless --mount <mounted-system-volume> --bootefi --last-sealed-snapshot
```

If `bless` returns nonzero, reversion stops. This is the first point at which the engine itself proves that the requested last-sealed-snapshot operation can actually be performed.

The command does not receive or inspect:

- current application Git identity;
- patching application Git identity;
- patch selection;
- metadata filename or schema;
- KDK version, build, or selection mode.

### Gate 8: post-bless cleanup and lifecycle transition

**File:** `opencore_legacy_patcher/sys_patch/sys_patch.py`
**Function:** `_unpatch_root_vol()`
**Relevant lines:** 227-239

After `bless` succeeds, current OCLP cleanup removes its shared Data-volume state (`SkyLightPlugins`, CoreDisplay enforcement preferences, and AuxiliaryKC policy/cache state), marks success, and records `REVERT_PENDING`.

This cleanup is not selected from installed metadata. Cross-build/fork recovery therefore uses shared inherited cleanup semantics; it does not reconstruct the exact inverse of every patch dictionary.

### Direct/CLI path

`support/arguments.py:106-111` calls `PatchSysVolume.start_unpatch()` directly. It bypasses GUI gates but not operation-time `can_unpatch`, state revalidation, mount, or `bless` failure handling.

## 2. Current state matrix

The table assumes a nonempty applicable patch selection for Start. Every “Revert yes” is additionally conditional on `can_unpatch == True`.

| State | Start Root Patching | Revert Root Patches | Current reason |
|---|---:|---:|---|
| `CLEAN` | Yes, if `detection.can_patch` | No | `_result()` grants patch permission only to `CLEAN`; no installed/pending recovery evidence is present. |
| `PATCH_PENDING_REBOOT` | No | Yes | Successful patch lifecycle is positively recorded for this boot; user may reboot or roll back first. |
| `INSTALLED_SAME` | No | Yes | Exact build and requested selection are already installed. |
| `INSTALLED_DIFFERENT_PATCH_SET` | No | Yes | Live add/remove is forbidden; revert/reboot/repatch is required. |
| `INSTALLED_DIFFERENT_BUILD` | No | Yes | Exact-build mismatch blocks patching, but code explicitly sets `revert_applicable=True`. |
| `LEGACY_FOREIGN` | No | Conditional | Canonical legacy metadata after a patched-root reading gives Yes. A recognized foreign filename gives Yes only when active-root evidence is patched. A still-clean pre-reboot active root gives No. |
| `INVALID_UNKNOWN` | No | Conditional | Some invalid states have positive patched-root/known-file evidence and get Yes; missing metadata, unreadable root evidence, active-root contradiction, or clean pre-reboot evidence normally get No. State name alone does not determine Revert. |
| `REVERT_PENDING` | No | No | Rollback has already selected the sealed snapshot; another patch/revert is blocked until reboot. |

The common state constructor at `root_state.py:224-242` defines `patch_allowed` solely as `state == CLEAN`. Revert is an independently supplied boolean.

### Important `INVALID_UNKNOWN` distinctions

Current code allows Revert for some invalid states:

- valid pending lifecycle envelope whose installed display metadata is not trusted (`root_state.py:291-297`);
- invalid lifecycle record when the active root is patched and a known metadata filename is present (`root_state.py:345-352`);
- malformed canonical metadata on an actively patched root (`root_state.py:362-369`);
- malformed exact-build fields after canonical metadata and patched-root evidence have already been established (`root_state.py:399-446`).

Current code refuses Revert for other invalid states:

- active-root evidence cannot be read (`root_state.py:359-360`);
- metadata is missing while the root is broken (`root_state.py:376-382`);
- metadata exists but active root appears clean/sealed, contradicting an installed state (`root_state.py:384-390`);
- a lifecycle record is invalid while the active pre-reboot root is still clean.

Consequently, `INVALID_UNKNOWN` must not be globally enabled or disabled without preserving evidence subtypes.

## 3. Same-build `PATCH_PENDING_REBOOT`

### Successful operation to state transition

`PatchSysVolume.start_patch()` calls `_record_patch_pending()` whenever the existing patch engine has set `root_patcher_succeeded=True` (`sys_patch.py:708-710`). That call is outside all KDK-selection branches.

`_record_patch_pending()` (`sys_patch.py:389-401`):

1. sets the in-process `root_patcher_patch_pending` flag;
2. clears `root_patcher_revert_pending`;
3. retains the exact installed-operation metadata for read-only selection/KDK history;
4. writes the boot-scoped lifecycle record.

There is no condition on:

- AUTO versus MANUAL KDK mode;
- the exact KDK identity;
- whether any KDK was required;
- the Wi-Fi/Audio selection.

Therefore current code supports the required sequence for all three paths:

```text
AUTO KDK patch        -> PATCH_PENDING_REBOOT -> Revert eligible
MANUAL KDK patch      -> PATCH_PENDING_REBOOT -> Revert eligible
no-KDK Wi-Fi-only     -> PATCH_PENDING_REBOOT -> Revert eligible
```

The three cases are explicitly covered in `tests/test_phase3c_patch_pending_reboot.py:119-151`.

### Cancel and Return to Main Menu

The reboot prompt does not clear the pending flag or lifecycle record. Cancel means only “do not reboot now.” The same `Constants` object survives return to the main UI, and `RootPatchStateEvaluator.evaluate()` checks the in-memory pending flag before active-root evidence (`root_state.py:332-343`).

Result:

- Start is disabled.
- Revert is enabled if `can_unpatch` remains true.
- installed selection and trustworthy MANUAL/AUTO provenance are display-only and do not determine eligibility.

### Quit and reopen the same build, same boot

`lifecycle.py` writes:

- schema `KGP-Root-Patch-Lifecycle-v1`;
- `PATCH_PENDING_REBOOT`/`REVERT_PENDING`;
- the current `kern.bootsessionuuid`;
- the installed operation metadata;
- SHA-256 of normalized metadata.

The record is root-owned at:

```text
/Library/Application Support/Dortania/OpenCore-Legacy-Patcher-Lifecycle.plist
```

On reopen, a same-boot valid record is read before normal active-root classification (`root_state.py:345-357`) and reconstructs `PATCH_PENDING_REBOOT`.

This guarantee is conditional on:

- the lifecycle write having succeeded;
- the record remaining readable and hash-valid;
- `kern.bootsessionuuid` still matching;
- the embedded installed metadata satisfying the current trusted-history structure;
- `can_unpatch` being true at GUI and operation time;
- root mount and `bless --last-sealed-snapshot` succeeding.

If the lifecycle file is missing/invalid after app restart and the active root still describes the old clean snapshot, active-root evidence cannot recover the pending state.

## 4. Previous-build pending patch behavior

### Build A and Build B both understand the new lifecycle schema

Build B reads the same root-owned lifecycle path. The lifecycle reader does not compare the record to B's commit. `_trusted_installed_history()` validates:

- KGP metadata schema;
- project identity;
- repository;
- full installed SHA;
- installed commit URL consistent with that installed SHA;
- structurally valid installed selection.

It deliberately does **not** require the installed SHA/ref/date to equal B's own SHA/ref/date (`root_state.py:244-278`).

Therefore, for two builds in the same KGP v2.0 lineage:

```text
build A patches -> no reboot -> build B opens
    => build B sees A's lifecycle record
    => PATCH_PENDING_REBOOT
    => Start disabled
    => Revert eligible when can_unpatch
```

Normal `INSTALLED_DIFFERENT_BUILD` classification is bypassed because valid lifecycle evidence is handled first.

Even when the record's project/repository is not accepted for authoritative display, `_pending_lifecycle_result()` currently returns `INVALID_UNKNOWN` with `revert_applicable=True`. Thus metadata-display rejection does not itself destroy the safe recovery path.

### Build A predates lifecycle recording, or the lifecycle write failed

Build B has no pending record to consume. Before reboot, `/` still represents the previously booted snapshot. It may therefore look clean/sealed even though a patched snapshot has been prepared for the next boot.

Current outcomes can be:

- no active metadata + clean/sealed root -> `CLEAN`, Revert disabled;
- recognized foreign filename + clean/sealed root -> `LEGACY_FOREIGN`, but Revert disabled because `safe_known_revert` requires a patched active root;
- canonical installed metadata contradicting clean/sealed evidence -> `INVALID_UNKNOWN`, Revert disabled;
- unrecognized fork metadata -> treated as missing, with no recovery authorization.

This is the precise compatibility hole for older pre-lifecycle packages. Current active-root-only evidence cannot prove the prepared-but-not-booted snapshot state. Enabling Revert solely because the user reports that patching just occurred would be guessing.

## 5. `INSTALLED_DIFFERENT_BUILD`

### Applying another patch

Unsafe under current policy. Full installed identity differs, so Start remains disabled and the user must revert/reboot before applying another patch. This prevents mixed snapshots and preserves Phase-2's core invariant.

### Reverting

Already permitted by current code. At `root_state.py:450-458`, `INSTALLED_DIFFERENT_BUILD` is returned with `revert_applicable=True`.

The unpatch engine never reads the installed commit, current commit, requested selection, or KDK identity. The exact-build restriction is therefore not an engine prerequisite.

If Revert is disabled while the UI says the patch is from a different build, the additional blocker is `can_unpatch` or the state was not actually the structurally valid `INSTALLED_DIFFERENT_BUILD` branch. It may instead be legacy/foreign/invalid evidence shown with similar user wording.

Recommendation: keep the present split:

```text
INSTALLED_DIFFERENT_BUILD
    Start = disabled
    Revert = enabled when can_unpatch and positive rollback evidence exist
```

Add an explicit regression test for `revert_allowed(True)`; the existing Phase-2 test asserts classification and Start blocking but does not directly assert Revert for this state.

## 6. Legacy and foreign metadata taxonomy

Current `LEGACY_FOREIGN` conflates several distinguishable classes:

| Class | Current recognition |
|---|---|
| Old KGP/OCLP-amfipassbeta | Canonical `OpenCore-Legacy-Patcher.plist`; old schema becomes `LEGACY_FOREIGN` only after patched-root evidence. |
| Upstream/inherited OCLP | Same canonical filename and similar legacy fields; current classifier does not distinguish it from old KGP. |
| OCLP-Plus | Exact `OCLP-Plus.plist` filename is listed and recognized; contents are not parsed. |
| OCLP-Mod | Mod writes lowercase `oclp-mod.plist`; current list contains `OCLP-Mod.plist`, so the actual file is not recognized by exact comparison. |
| OCLP-R | Current list contains `OCLP-R.plist`; any lowercase-writing implementation would reproduce the same case mismatch class. |
| Current schema from another project/repository | Parsed as canonical, then classified `LEGACY_FOREIGN`. |
| Malformed canonical metadata | `INVALID_UNKNOWN`, not `LEGACY_FOREIGN`. |
| Unknown patcher with no recognized metadata | Missing metadata; a broken root becomes `INVALID_UNKNOWN` without Revert. |

The relevant current definitions are `root_state.py:23-34` and discovery logic at `root_state.py:168-222`.

Reliable source-backed family signatures exist:

- original/upstream/KGP legacy: `OpenCore-Legacy-Patcher.plist` and key `OpenCore Legacy Patcher`;
- Plus 3.2.2: `OCLP-Plus.plist` and key `OCLP-Plus`;
- Mod 3.1.9: `oclp-mod.plist` and key `OCLP-Mod`.

These signatures can support a future **recognized OCLP-family recovery** classification without treating them as current/equal for patch authorization. Malformed content, ambiguous duplicates, canonical KGP case mismatch, and genuinely unknown metadata should remain fail-closed.

## 7. What the revert engine technically requires

### Required by current code

1. `can_unpatch == True`, presently derived from the required SIP configuration.
2. The current System APFS volume can be resolved and mounted.
3. `bless --last-sealed-snapshot` succeeds for that mounted volume.
4. Existing privileged-helper authorization is available.
5. Post-bless shared Data-volume cleanup can execute sufficiently to complete the inherited workflow.

### Not required by the actual engine

- exact current application identity;
- exact patching application identity;
- equal Git commit;
- equal human-readable version;
- equal patch dictionary;
- installed metadata schema;
- installed metadata at all;
- KDK selection mode or KDK identity;
- active root being `Sealed: Broken`.

Those inputs affect policy/UI provenance, not the arguments passed to the rollback engine.

### Evidence limitation

Current code has no side-effect-free preflight that proves a last sealed rollback target exists. The proof is the actual `bless --last-sealed-snapshot` call after mounting. Active `Sealed: Broken` plus recognized metadata is used as a policy proxy, while a valid pending lifecycle is stronger operation-time evidence because it is written only after successful patch/KC/snapshot completion.

A future broadening for pre-lifecycle, pre-first-reboot recovery should not merely scan unrelated APFS snapshots or infer safety from any metadata file. It should use an active-System-volume-specific, read-only prepared-target/rollback-evidence probe. If no reliable probe is available, that legacy corner remains unprovable and should not be guessed clean or safe.

## 8. Upstream / Mod / Plus comparison

| Implementation | GUI Revert gate | Operation Revert gate | Metadata/build ownership consulted? | Actual rollback |
|---|---|---|---|---|
| Original OCLP-amfipassbeta | Disable only when `can_unpatch` false (`gui_sys_patch_display.py:107,238-239`) | `can_unpatch`, mount (`sys_patch.py:585-601`) | No | `bless --last-sealed-snapshot` |
| Local upstream reference | Same inherited GUI behavior | Same inherited operation behavior | No | Same |
| OCLP-Plus 3.2.2 | Same inherited GUI behavior | Same inherited operation behavior | No | Same |
| OCLP-Mod 3.1.9 | Same, with `.get(..., False)` for the validation key (`gui_sys_patch_display.py:107-108,239-240`) | Same inherited operation behavior | No | Same |
| Current KGP v2.0 | `revert_applicable AND can_unpatch` | independently rechecks both | Yes, in `revert_applicable` policy | Same |

Upstream, Plus, and Mod may impose dirty-root/different-commit restrictions on **patching/repatching**, but `_cant_unpatch` remains the SIP result. Plus makes this separation especially explicit: dirty/repatch requirements are added at `oclp_plus/sys_patch/patchsets/detect.py:539-547`, while `_cant_unpatch` is still only `SIP_ENABLED` at lines 549-571.

This source structure supports KGP's report that the older/fork applications can generally revert each other's root patches: they do not inspect ownership before invoking the common rollback. It does not constitute runtime proof for every fork/OS combination, and their broad “Revert even on clean/unknown state” GUI policy should not be copied.

Phase 2 added the state-level `revert_applicable` gate and operation-time classifier recheck. That correctly removed misleading Revert on `CLEAN`, but also made recognized-family and pre-reboot recovery dependent on the completeness of KGP's metadata/lifecycle classifier.

## 9. Recommended authorization model

The proposed separation is technically sound:

### Patch authorization

Remain strict and unchanged in principle:

- only `CLEAN` permits patching;
- exact same/different build/different selection remain blocked;
- legacy, foreign, invalid, pending-patch, and pending-revert states remain blocked;
- no live additive/subtractive overwrite of an existing patched snapshot.

### Recovery authorization

Derive independently from positive recovery evidence:

1. **Valid same-boot completed-patch lifecycle:** allow Revert regardless of AUTO/MANUAL/no-KDK and regardless of current exact commit.
2. **Active patched root + structurally valid current KGP metadata:** allow Revert, including `INSTALLED_DIFFERENT_BUILD` and different selection.
3. **Active patched root + structurally recognized OCLP-family metadata:** allow Revert, but never classify it current/equal.
4. **`REVERT_PENDING`:** do not offer another Revert; reboot is required.
5. **Clean root with no pending evidence:** do not offer Revert.
6. **Malformed/ambiguous/unknown state:** remain fail-closed unless an independent, active-System-volume-specific safe rollback target is positively established.

Manual/AUTO KDK provenance remains display-only for this decision.

### Minimum future change set

No patch, KDK, KC, snapshot, or bless implementation needs to change. The smallest coherent future change is:

1. Introduce a small typed recovery-evidence result separate from `RootPatchState`, or compute `revert_applicable` through one centralized recovery function rather than incidental classifier branches.
2. Preserve strict `patch_allowed` semantics exactly.
3. Preserve `can_unpatch` as a second independent gate at GUI and operation time.
4. Preserve current valid lifecycle recovery across different KGP commits.
5. Canonicalize a source-backed registry of recognized OCLP-family metadata identities, including the actual lowercase `oclp-mod.plist`, and validate the expected family key. Do not make foreign metadata current/equal.
6. Keep malformed, duplicate, ambiguous, and unknown metadata distinct from recognized family metadata.
7. Add a dedicated read-only prepared-target/last-sealed recovery probe only if pre-lifecycle pre-reboot compatibility is required and can be proven active-volume-specific. Do not restore the inherited “Revert everywhere SIP permits” policy.
8. Add operation-level tests proving the exact same recovery result as the GUI.

## 10. Critical scenario matrix

Every proposed Revert result below remains conditional on existing `can_unpatch`, mount success, and `bless --last-sealed-snapshot` success.

| Scenario | Current classification / behavior | Current Start | Current Revert | Technical prerequisites | Recommended safe policy |
|---|---|---:|---:|---|---|
| **A. Same build patches; no reboot; same build reverts** | `PATCH_PENDING_REBOOT` through in-memory flag and valid lifecycle | No | Yes | Completed patch lifecycle, `can_unpatch`, mount, last sealed snapshot | Keep current behavior. |
| **B. Build A patches; no reboot; build B same lineage reverts** | If A wrote valid current lifecycle: `PATCH_PENDING_REBOOT`, Yes. If A predates lifecycle/record failed: active root may look `CLEAN`, `LEGACY_FOREIGN`, or `INVALID_UNKNOWN`, usually Revert No. | No for valid pending; otherwise state-dependent and may incorrectly be Yes if classified CLEAN | Conditional | Valid shared lifecycle, or a future positive prepared-target recovery probe | Preserve cross-commit lifecycle recovery. Do not infer legacy pending state solely from active clean root. Add a proven active-volume recovery probe if legacy pre-marker support is mandatory. |
| **C. Build A patches; reboot; build B same lineage reverts** | Current schema/project/repository with different identity -> `INSTALLED_DIFFERENT_BUILD` | No | Yes | Active patched root, valid KGP metadata, `can_unpatch`, mount, sealed rollback | Keep current behavior and add direct Revert regression assertion. |
| **D. Old amfipassbeta patches; current build reverts** | After reboot: canonical legacy metadata + broken root -> `LEGACY_FOREIGN`, Revert Yes. Before first reboot: no KGP lifecycle, often Revert No. | No after reboot | Yes after reboot; pre-reboot conditional/no | Recognized canonical OCLP-family metadata and active patched root, or positive pending evidence | Treat old KGP as recognized family for recovery only; do not treat it current for patching. Legacy pre-reboot still needs positive prepared-target evidence. |
| **E. Current build patches; old amfipassbeta reverts** | Old app has no KGP state enum and gates Revert only on `can_unpatch` | Old app's own policy | Generally Yes | SIP, mount, last sealed snapshot | Source supports compatibility, but current KGP cannot enforce safety in the old app. Do not depend on this as the preferred workflow. |
| **F. Plus/Mod patches; current build reverts** | Plus after reboot: recognized `LEGACY_FOREIGN`, Yes. Mod after reboot: lowercase filename missed -> metadata missing + broken root -> `INVALID_UNKNOWN`, No. Before first reboot neither fork writes KGP lifecycle, so generally No. | No | Plus Yes after reboot; Mod No under exact current filename logic | Recognized family metadata, active patched root, `can_unpatch`, mount, sealed rollback | Fix source-backed family recognition (especially `oclp-mod.plist`) for recovery only. Pre-reboot recovery still needs positive prepared-target evidence. |
| **G. Current build patches; Plus/Mod reverts** | Forks have no KGP state enum; Revert is gated only by their SIP-derived `can_unpatch` | Fork policy | Generally Yes | SIP, mount, last sealed snapshot | Technically supported by shared engine; KGP should still prefer its evidence-backed recovery UI. |
| **H. Malformed/unknown metadata; current build attempts revert** | `INVALID_UNKNOWN`. Malformed known canonical file + active broken root may currently allow Revert; missing/unknown metadata generally does not. | No | Conditional | Current policy proxy or an independent proven rollback target | Do not globally enable. Require positive active-volume rollback evidence; otherwise fail closed. |
| **I. `PATCH_PENDING_REBOOT` with safe rollback target; revert before first reboot** | Dedicated pending state | No | Yes | Valid session/lifecycle evidence, `can_unpatch`, mount, last sealed snapshot | Keep and treat as highest-confidence pre-reboot recovery evidence across KGP commits and all KDK modes. |

## Direct answers

1. **What currently gates Revert?** State-derived `revert_applicable`, hardware-derived `can_unpatch`/SIP, operation-time repetition of both, root mount success, and `bless --last-sealed-snapshot` success.
2. **Does exact build mismatch technically prevent rollback?** No. `INSTALLED_DIFFERENT_BUILD` already permits Revert; the engine never consumes the build identity.
3. **Does current same-build pending recovery work?** Yes for AUTO KDK, MANUAL KDK, and no-KDK operations, subject to `can_unpatch` and normal mount/bless success.
4. **Does same-boot app reopen work?** Yes when the new lifecycle record was written successfully and remains valid for the same boot session.
5. **Does a later KGP commit lose a valid pending record from an earlier KGP commit?** No. Exact SHA equality is not required for pending lifecycle recovery.
6. **What remains broken?** Pre-lifecycle/failed-record pre-first-reboot recovery cannot be proven from active-root evidence alone; actual Mod metadata is also missed due filename capitalization.
7. **Do Plus/Mod/upstream require matching patch ownership to revert?** No. Their inspected source gates Revert only through SIP-derived `can_unpatch`, then uses the same mount/bless engine.
8. **Is `patch authorization != revert authorization` safe?** Yes when Revert is tied to positive pending or active patched-root/recognized-family rollback evidence and retains `can_unpatch` plus operation-time revalidation.
9. **Should malformed/unknown states be broadly allowed to revert?** No. Preserve fail-closed behavior unless independent safe rollback evidence is positively established.
10. **Recommended next implementation direction:** keep strict patch blocking; centralize separate recovery evidence; preserve current pending/different-build Revert; recognize actual OCLP-family metadata identities; and add a proven active-volume prepared-target probe only if backward recovery before first reboot is required.
