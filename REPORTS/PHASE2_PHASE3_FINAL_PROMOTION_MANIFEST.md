# Phase 2 + Phase 3 Final Promotion Manifest

Date: 2026-08-15

## Promotion authority

The authoritative runtime-validated implementation is the complete tracked source state at:

`62e0b1c0413eb900bda69955030dd5bee28219b6`

The validated package is:

`/Users/kgp/Desktop/OCLP/OCLP-v2.0-phase3C-recovery-hotfix/OpenCore-Patcher.pkg`

SHA-256:

`66fb1ef601ad5df57a4cf4cb3906f2c72ef82134cac1d6bd238bcd59f34ec074`

Promotion into the future online repository must reproduce the final source behavior and tests at the authoritative implementation commit. Development commits are provenance, not a requirement to replay every intermediate state. Each item marked **MUST PROMOTE** below is part of the final validated behavior.

## 1. Reproducible environment and deterministic application build

**Promotion:** MUST PROMOTE.

**Final source:** `.python-version`; `requirements.txt`; `requirements-lock.txt`; `Build-Project.command`; `OpenCore-Patcher-GUI.spec`; `ci_tooling/build_environment.py`; `ci_tooling/build_modules/application.py`; applicable `.github/workflows/*.yml`; Phase-2A manifests.

**Key code:** `build_environment.locked_distributions()`, `normalized_manifest()`, `verify()`; `GenerateApplication._refresh_ad_hoc_signature()` and `generate()`; the spec's `SOURCE_DATE_EPOCH` enforcement.

**Final behavior:** CPython 3.14.3 x86_64; exact 22-distribution hash lock; verified offline wheelhouse; `PYTHONHASHSEED=0`; required deterministic timestamp; clean PyInstaller cache; deterministic outer-only, timestamp-free ad-hoc signature finalization; strict/deep validation; package-expanded application parity. No signing identity is required.

**Protection/evidence:** `REPORTS/PHASE2A_*`; `MANIFESTS/PHASE2A_*`; build-environment verifier; final artifact validation recorded in `ROOT_PATCH_RECOVERY_AND_DARWIN26_KDK_IMPLEMENTATION.md`.

**Origin:** `454bd1b867a40c301240928085eb0fa4b04452ba`.

**Do not promote:** exploratory non-fixed Python hash-seed builds; archive post-processing; dependency upgrades outside the lock; mutable network resolution; inner-signature rewrites; any package produced from a dirty tree.

## 2. Exact build provenance and generated-config check

**Promotion:** MUST PROMOTE.

**Final source:** `ci_tooling/build_metadata.py`; `ci_tooling/build_modules/application.py`; `opencore_legacy_patcher/support/commit_info.py`; `opencore_legacy_patcher/constants.py`; `opencore_legacy_patcher/efi_builder/support.py`.

**Key code:** `SourceBuildMetadata.from_repository()`, `validate()`; `GenerateApplication._embed_git_data()`; `ParseCommitInfo.generate_commit_info()`; generated-config `Path.exists()` branch.

**Final behavior:** a clean source tree, exact full 40-character SHA, canonical repository and commit URL, exact Git commit date, and a real ref are mandatory. The application embeds and runtime code consumes the same identity. Missing, abbreviated, inconsistent, foreign, or dirty provenance fails the build. Generated EFI config detection uses `Path.exists()` correctly.

**Tests:** `tests/test_phase2b_build_metadata.py`; `tests/test_phase2b_generated_config_exists.py`.

**Origin:** `b1289b8e9f0afd209396a2ad4d9253f2c41a03f2`; `977a728f0c49057223d85ac5e70e7cfdf52bb15f`.

**Do not promote:** human-readable version equality as build identity; abbreviated SHA acceptance; build-time dates substituted for commit dates; provenance added after packaging.

## 3. Root-state classification and strict patch authorization

**Promotion:** MUST PROMOTE.

**Final source:** `opencore_legacy_patcher/sys_patch/root_state.py`; `opencore_legacy_patcher/sys_patch/sys_patch.py`; `opencore_legacy_patcher/sys_patch/patchsets/detect.py`; `opencore_legacy_patcher/wx_gui/gui_sys_patch_display.py`; `opencore_legacy_patcher/wx_gui/gui_sys_patch_start.py`; active-root evidence providers in `detections/device_probe.py` and kernel-cache support.

**Key code:** `RootPatchState`, `RootStateEvidence`, `RootPatchStateResult`; `RootPatchStateEvaluator._discover_metadata()`, `_pending_lifecycle_result()`, `evaluate()`, `_result()`; `PatchSysVolume.start_patch()`.

**Final behavior:** only `CLEAN` is root-state-authorized for a new patch. `INSTALLED_SAME`, `INSTALLED_DIFFERENT_PATCH_SET`, `INSTALLED_DIFFERENT_BUILD`, `LEGACY_FOREIGN`, `INVALID_UNKNOWN`, `PATCH_IN_PROGRESS`, `PATCH_FAILED_RECOVERY_REQUIRED`, `PATCH_PENDING_REBOOT`, and `REVERT_PENDING` all block new patching. Exact build and semantic requested-patch selection remain strict for classifying an installed state. Only the active root supplies seal/snapshot evidence; no broad system-wide snapshot fallback exists.

**Tests:** `tests/test_phase2b_identical_state_blocking.py`; `tests/test_phase2b_root_state_protection.py`; relevant integration cases in `tests/test_phase3b_selection_integration.py`; `tests/test_phase3c_patch_pending_reboot.py`.

**Origin/finalization:** `b1289b8e9f0afd209396a2ad4d9253f2c41a03f2`; `51b1910a30e80fbe964459231b3e2ae1a813258e`; `4fe8f1326b4f293537f989479675b9588bbfabf3`; `448d652d20d081856dcfc564b286b3887e52f127`; final authorization at `62e0b1c0413eb900bda69955030dd5bee28219b6`.

**Do not promote:** any rule that permits a new patch merely because metadata is missing; unrelated snapshot scanning; state inference from the GUI button; selective live mutation of an installed patched snapshot.

## 4. Simplified common Revert authorization

**Promotion:** MUST PROMOTE.

**Final source:** `opencore_legacy_patcher/sys_patch/root_state.py`; `opencore_legacy_patcher/wx_gui/gui_sys_patch_display.py`; `opencore_legacy_patcher/wx_gui/gui_sys_patch_start.py`; `opencore_legacy_patcher/sys_patch/sys_patch.py`.

**Key code:** `RootPatchStateResult.recovery_authorized`, `revert_allowed()`; `RootPatchStateEvaluator._result()`; `SysPatchDisplayFrame._refresh_selection_state()`, `on_revert_root_patching()`; `SysPatchStartFrame.revert_root_patching()`; `PatchSysVolume.start_unpatch()`.

**Final behavior:** root-state authorization, not ownership, controls recovery. `CLEAN` does not authorize Revert. Every non-clean/blocking state authorizes the common Revert path except `REVERT_PENDING`, where Revert already succeeded and reboot is required. Revert does not require matching SHA, application/fork identity, patch dictionary, KDK identity, trusted installed selection, or lifecycle evidence. An unknown installed selection may remain displayed as unknown while Revert is offered.

The policy is not literal inversion of the Start button. `CLEAN` plus an empty user selection has Start disabled by selection but Revert disabled because the root is clean.

**Tests:** `tests/test_root_patch_recovery_authorization.py`; final expectations in `tests/test_phase2b_root_state_protection.py`; `tests/test_phase3c_patch_pending_reboot.py`; read-only display cases in `tests/test_phase3c_installed_selection_readonly.py`.

**Final commit:** `62e0b1c0413eb900bda69955030dd5bee28219b6`.

**Do not promote:** superseded evidence-owned recovery from `8351c95de20810390bf192d391c3707b2b7f9723`; build/SHA/project/fork/metadata/lifecycle ownership gates; snapshot-enumeration heuristics; enabling a second destructive Revert in `REVERT_PENDING`.

## 5. SIP and operation-time recovery prerequisites

**Promotion:** MUST PROMOTE.

**Final source:** `opencore_legacy_patcher/sys_patch/root_state.py`; `opencore_legacy_patcher/wx_gui/gui_sys_patch_display.py`; `opencore_legacy_patcher/wx_gui/gui_sys_patch_start.py`; `opencore_legacy_patcher/sys_patch/sys_patch.py`; existing mount/snapshot implementation.

**Key code:** `RootPatchStateResult.revert_allowed()`; `recovery_status_text()`; `SysPatchDisplayFrame.on_revert_root_patching()`; `PatchSysVolume.start_unpatch()`, `_mount_root_vol()`, `_unpatch_root_vol()`.

**Final behavior:** recovery authorization and immediate executability are separate. SIP-derived `can_unpatch` never hides the appropriate recovery action. A click and direct operation entry revalidate root state and SIP. If SIP blocks execution, the user receives the concrete prerequisite and no root mount or rollback occurs. If allowed, the unchanged common OCLP rollback restores the last sealed snapshot via the existing `bless --last-sealed-snapshot` path.

**Tests:** SIP visibility/click/direct-entry and mount-failure cases in `tests/test_root_patch_recovery_authorization.py`; pending-reboot gate in `tests/test_phase3c_patch_pending_reboot.py`.

**Origin/finalization:** `8351c95de20810390bf192d391c3707b2b7f9723`, as simplified and made ownership-independent by `62e0b1c0413eb900bda69955030dd5bee28219b6`.

**Do not promote:** `Revert enabled = recovery evidence AND can_unpatch` as a display rule; weakened SIP enforcement; automatic rollback; a new APFS snapshot engine.

## 6. Canonical root-patch selection and installed metadata

**Promotion:** MUST PROMOTE.

**Final source:** `opencore_legacy_patcher/sys_patch/root_selection.py`; `opencore_legacy_patcher/sys_patch/patchsets/detect.py`; `opencore_legacy_patcher/sys_patch/sys_patch.py`; `opencore_legacy_patcher/sys_patch/sys_patch_helpers.py`; `opencore_legacy_patcher/sys_patch/root_state.py`; both root-patching GUI frames.

**Key code:** `SelectableRootPatch`, `SelectableRootPatchDefinition`, `RootPatchSelection.initialize()`, `with_selection()`, `constrained_to()`, `filter_patch_dictionary()`; `HardwarePatchsetDetection._detect()`; `SysPatchHelpers.generate_patchset_plist()`; `semantic_patch_selection()`.

**Final behavior:** hardware detection determines applicability; one immutable operation selection determines the final requested patch dictionary. CLEAN defaults applicable selections ON. Trustworthy installed metadata restores the installed selection read-only. The final dictionary is revalidated at display, click, pre-KDK, and patch-engine entry. Successful metadata records only the dictionary actually applied. Changing an installed selection requires Revert, reboot, and repatch.

**Tests:** `tests/test_phase3b_root_selection.py`; `tests/test_phase3b_selection_integration.py`; `tests/test_phase3c_installed_selection_readonly.py`; installed provenance tests.

**Origin:** `3631d4c66882b8999fab2d8932091ac5cdf8c230`; `249473cab6850633ae55eaae7a0ceef6c58f6c75`.

**Do not promote:** independent Settings/GUI/engine copies of selection; selection as hardware detection; recording deselected applicable patches; changing selection on an installed snapshot.

## 7. Modern Wireless selection

**Promotion:** MUST PROMOTE.

**Final source:** selection/filtering files above; unchanged detector/dictionary in `opencore_legacy_patcher/sys_patch/patchsets/hardware/networking/modern_wireless.py`.

**Key code:** `SelectableRootPatch.MODERN_WIFI`; `RootPatchSelection.filter_patch_dictionary()`; selection-aware `HardwarePatchsetDetection._detect()`.

**Final behavior:** the main Root Patching UI selects or excludes the already-applicable complete Modern Wireless root-patch family. OFF affects only root patches: it does not alter hardware, EFI, DeviceProperties, ACPI, or AirportItlwm/Broadcom configuration. Selection code contains no Broadcom/Intel PCI logic.

**Tests:** Modern Wireless cases in `tests/test_phase3b_root_selection.py`, `tests/test_phase3b_selection_integration.py`, and `tests/test_modern_wireless_regression.py`.

**Origin:** `3631d4c66882b8999fab2d8932091ac5cdf8c230`; `249473cab6850633ae55eaae7a0ceef6c58f6c75`.

**Do not promote:** Phase-3A Intel-ID experiments; Broadcom spoofing; any Modern Wireless dictionary/payload rewrite as part of this selection feature.

## 8. Modern Audio selection

**Promotion:** MUST PROMOTE.

**Final source:** selection/filtering files above; unchanged patch definition in `opencore_legacy_patcher/sys_patch/patchsets/hardware/misc/modern_audio.py`.

**Key code:** `SelectableRootPatch.MODERN_AUDIO`; `RootPatchSelection.filter_patch_dictionary()`; selection-aware requirement aggregation in `HardwarePatchsetDetection._detect()`.

**Final behavior:** Audio ON includes the existing Modern Audio/Beta-1 AppleHDA patch and its KDK requirement. Audio OFF excludes that dictionary and does not manage AppleHDA, HDAUniversal, VoodooHDA, or audio EFI configuration.

**Tests:** `tests/test_phase3b_kdk_selection.py`; Audio combinations in the Phase-3B selection modules.

**Origin/finalization:** `3631d4c66882b8999fab2d8932091ac5cdf8c230`; `249473cab6850633ae55eaae7a0ceef6c58f6c75`; `f451fd49f0500363022d92b25f0d382523818fa6`.

**Do not promote:** coupling Audio OFF to live AppleHDA removal; changing the AppleHDA payload; making Audio selection a global preference.

## 9. Wi-Fi-only no-KDK architecture

**Promotion:** MUST PROMOTE.

**Final source:** `root_selection.py`; `patchsets/detect.py`; `sys_patch.py`; GUI selection frames.

**Key code:** selection filtering before requirement aggregation in `HardwarePatchsetDetection._detect()`.

**Final behavior:** Wi-Fi ON plus Audio OFF applies Modern Wireless only and creates no KDK requirement solely from those two families. Another independently selected KDK-requiring patch continues to require a KDK.

**Tests:** `tests/test_phase3b_kdk_selection.py`; `tests/test_phase3c_manual_kdk_gui.py`; no-KDK lifecycle case in `tests/test_phase3c_patch_pending_reboot.py`.

**Final origin:** `f451fd49f0500363022d92b25f0d382523818fa6`.

**Do not promote:** the abandoned experiment that forced selected Modern Wi-Fi onto a KDK-backed full-KC path; AppleHDA/KDK conflict checks introduced solely for that experiment; use of `requires_primary_kernel_cache()` for an unvalidated no-KDK Primary KC path.

## 10. Explicit empty-selection guard

**Promotion:** MUST PROMOTE.

**Final source:** `opencore_legacy_patcher/sys_patch/root_selection.py`; `sys_patch.py`; `gui_sys_patch_display.py`; `gui_sys_patch_start.py`.

**Key code:** `EMPTY_SELECTION_MESSAGE`; display refresh/start handlers; `SysPatchStartFrame._revalidate_patch_selection()`; `PatchSysVolume.start_patch()`.

**Final behavior:** explicit Wi-Fi OFF plus Audio OFF disables Start. A forced/stale/programmatic explicit-empty invocation aborts with exactly `Please select at least one patching option.` before KDK, support package, authentication, root mount, mutation, KC, snapshot, or metadata work. Legacy/direct callers without an explicit Phase-3 selection retain their detected-patch semantics.

**Tests:** `tests/test_phase3b_empty_selection_guard.py`; re-enable cases in `tests/test_phase3b_root_selection.py`; clean-empty recovery invariant in `tests/test_root_patch_recovery_authorization.py`.

**Origin:** `f29f4bf97b260b91fd007e69a6976dc16cc0d264`.

**Do not promote:** treating every missing selection object as explicit-empty; enabling Revert merely because Start is selection-disabled.

## 11. Manual KDK selector and operation-scoped GUI state

**Promotion:** MUST PROMOTE.

**Final source:** `opencore_legacy_patcher/support/kdk_selection.py`; `opencore_legacy_patcher/wx_gui/gui_kdk_selection.py`; `gui_sys_patch_display.py`; `gui_sys_patch_start.py`.

**Key code:** `ManualKDKSelectionState`, `KDKSelectionContext`, `KDKCandidateStatus`; `ManualKDKSelectionDialog`; `automatic_choice_text()`; `candidate_status_text()`; GUI `_select_manual_kdk()` and `_revalidate_manual_kdk()`.

**Final behavior:** the main Root Patching page exposes an OFF-by-default manual control only when final selected requirements need a KDK. Candidate and confirmation dialogs are selection-only. They list eligible trusted-catalog Tahoe KDKs, show installed status and the side-effect-free existing AUTO choice, and return exactly one confirmed candidate to the normal OCLP progress/download flow. Cancel starts nothing. State is operation-scoped and cleared when the requirement disappears or a new CLEAN operation begins.

**Tests:** `tests/test_phase3c_manual_kdk_gui.py`; relevant read-only/transition cases in `tests/test_phase3c_installed_selection_readonly.py`.

**Origin/polish:** `7377cc054fba3c6e7893fd1c2b2e98a6ba6bab12`; `fbc2633e5c9bee412bb9bc7ee3971f3d92cfa258`.

**Do not promote:** a second download/install/progress implementation; persistent global manual preference; arbitrary package path or URL; silent AUTO fallback after Cancel or failure; old long row marker `OCLP Automatic Choice` in place of final `Automatic Choice`.

## 12. AUTO/manual KDK resolver integration and provenance

**Promotion:** MUST PROMOTE.

**Final source:** `opencore_legacy_patcher/support/kdk_handler.py`; `support/kdk_selection.py`; `sys_patch/utilities/kdk_merge.py`; `sys_patch/sys_patch.py`; `sys_patch/sys_patch_helpers.py`; `root_state.py`; KDK and root-patching GUI frames.

**Key code:** `KernelDebugKitObject.available_candidates()`, `_get_selected_kdk()`, `_get_latest_kdk()`, `resolved_candidate()`, `retrieve_download()`; `KernelDebugKitIdentity`; `KDKSelectionMode`; manual revalidation in both GUI and `PatchSysVolume`; `KernelDebugKitMerge._kdk_object()`; `SysPatchHelpers.generate_patchset_plist()`.

**Final behavior:** AUTO retains inherited exact/closest selection among eligible candidates. MANUAL locks the exact trusted-catalog identity, reuses that exact installed KDK or passes that exact candidate into the existing standard download/install flow, and fails closed without substitution. Successful installed-operation metadata records AUTO or MANUAL and the actual KDK identity as historical provenance, not a future preference. Installed/revert-state GUI displays trustworthy MANUAL history read-only.

**Tests:** `tests/test_phase3c_manual_kdk_resolver.py`; `tests/test_phase3c_installed_kdk_provenance.py`; `tests/test_phase3c_installed_selection_readonly.py`; AUTO-preview tests in `tests/test_phase3c_manual_kdk_gui.py`.

**Origin:** `5e2c95f2897783b53ecdd84400550364a0c34ee5`; `d06c950b911a4a8a20114ef6fa6ec336e186bf6d`.

**Do not promote:** a duplicate resolver; ranking changes in AUTO mode; fallback after manual confirmation; inferring MANUAL/AUTO from whether the chosen KDK matches AUTO.

## 13. Darwin-26 KDK exclusion

**Promotion:** MUST PROMOTE.

**Final source:** `opencore_legacy_patcher/support/kdk_selection.py`; `support/kdk_handler.py`; `sys_patch/utilities/kdk_merge.py`; existing manual/operation revalidation consumers.

**Key code:** `kdk_darwin_major()`, `root_patch_kdk_build_allowed()`; `KernelDebugKitCandidate.allowed_for_root_patching()`; `KernelDebugKitObject._permitted_catalog_entries()`; guarded candidate/download/local methods; `KernelDebugKitMerge._require_permitted_build()` and `_require_permitted_kdk()`.

**Final behavior:** Apple `ProductBuildVersion` is the only build-family identity. Build family 26 is excluded globally. The trusted catalog is filtered before unchanged inherited AUTO ranking; manual, local, download, pre-install, operation-time, and merge-time defenses use the same canonical policy. `25G82`, `25G76`, Darwin 24, and older are permitted. `26A5368g` and `26A5406e` are prohibited. macOS marketing version `26.6.2` is not a build identifier. Rejected logging is concise.

**Tests:** all cases in `tests/test_darwin26_kdk_policy.py`; manual integration suites.

**Final commit:** `c1d5e05c3cad7de12af738725136a53030183088` on top of the initial boundary introduced at `53c44be749e77d830b4ee5ba733321f40d31ec02`.

**Do not promote:** the intermediate parser that accepted a leading numeric marketing version as a Darwin build; treating an empty installed fast-path catalog build as Darwin 26; dumping full catalog dictionaries; teaching exact/closest ranking a second eligibility policy.

## 14. Boot-scoped lifecycle and installed-operation provenance

**Promotion:** MUST PROMOTE.

**Final source:** `opencore_legacy_patcher/sys_patch/lifecycle.py`; `sys_patch/sys_patch.py`; `sys_patch/root_state.py`; `sys_patch/sys_patch_helpers.py`; installed-state GUI.

**Key code:** `RootPatchLifecycleState`; `RootPatchLifecycleStore.read()`, `write()`; `PatchSysVolume._record_patch_in_progress()`, `_record_patch_failed()`, `_record_patch_pending()`, `_record_revert_pending()`; `RootPatchStateEvaluator._pending_lifecycle_result()`; KDK provenance metadata helpers.

**Final behavior:** integrity-checked, root-owned, boot-session-bound records distinguish `PATCH_IN_PROGRESS`, `PATCH_FAILED_RECOVERY_REQUIRED`, and `PATCH_PENDING_REBOOT`. Recording occurs before the first root-patch mutation boundary. Failure after that boundary preserves recovery state without writing false success metadata. Success records the exact applied patch/KDK provenance. Records survive app reopen on the same boot and go stale across reboot as designed. They improve state/provenance but never gate Revert permission.

**Tests:** `tests/test_phase3c_patch_pending_reboot.py`; `tests/test_phase3c_installed_kdk_provenance.py`; installed-state GUI tests.

**Origin/finalization:** `4fe8f1326b4f293537f989479675b9588bbfabf3`; `448d652d20d081856dcfc564b286b3887e52f127`; authorization decoupled at `62e0b1c0413eb900bda69955030dd5bee28219b6`.

**Do not promote:** making lifecycle presence a Revert prerequisite; tying lifecycle to manual KDK mode; claiming failed patch metadata as a successful installation.

## 15. Lowercase OCLP-Mod metadata compatibility

**Promotion:** MUST PROMOTE.

**Final source:** `opencore_legacy_patcher/sys_patch/root_state.py`.

**Key code:** `FOREIGN_METADATA_IDENTITIES`; `RootPatchStateEvaluator._discover_metadata()`.

**Final behavior:** both `OCLP-Mod.plist` and the actual Mod spelling `oclp-mod.plist` are recognized as source-backed OCLP-family metadata with identity `OCLP-Mod`. Recognition never classifies it as current/equal KGP metadata and never authorizes new patching. Under the final common-recovery rule, spelling/ownership does not gate Revert.

**Tests:** lowercase and uppercase cases in `tests/test_root_patch_recovery_authorization.py`; foreign/ambiguous metadata cases in `tests/test_phase2b_root_state_protection.py`.

**Origin:** `8351c95de20810390bf192d391c3707b2b7f9723`; final recovery semantics `62e0b1c0413eb900bda69955030dd5bee28219b6`.

**Do not promote:** filename-only trust as current KGP metadata; case-insensitive ambiguity acceptance; using recognized family identity as a Revert ownership restriction.

## Final regression suite to promote

All current test modules are part of the promotion gate:

| Test module | Protected behavior |
|---|---|
| `test_phase2b_build_metadata.py` | exact/clean build provenance |
| `test_phase2b_generated_config_exists.py` | `Path.exists()` regression |
| `test_phase2b_identical_state_blocking.py` | identical/different build and selection gating, TOCTOU |
| `test_phase2b_root_state_protection.py` | complete root-state classifier, active-root evidence, metadata cases |
| `test_phase3b_root_selection.py` | canonical selection/default/applicability/filter model |
| `test_phase3b_selection_integration.py` | final dictionary, state integration, installed metadata |
| `test_phase3b_kdk_selection.py` | selection-derived KDK requirements and AppleHDA exclusion |
| `test_phase3b_empty_selection_guard.py` | GUI and operation-level empty guard/direct-entry compatibility |
| `test_phase3c_manual_kdk_gui.py` | manual-control state, selector, AUTO preview, confirmation/cancel |
| `test_phase3c_manual_kdk_resolver.py` | exact manual lock, no substitution, standard download flow, TOCTOU |
| `test_phase3c_installed_kdk_provenance.py` | AUTO/MANUAL historical metadata and exact identity |
| `test_phase3c_installed_selection_readonly.py` | installed/revert read-only UI and CLEAN reset |
| `test_phase3c_patch_pending_reboot.py` | lifecycle, mutation boundary, pending/failed recovery across reopen/reboot |
| `test_root_patch_recovery_authorization.py` | final common Revert policy, SIP separation, unknown-root recovery |
| `test_darwin26_kdk_policy.py` | canonical build-family filter at all KDK boundaries |
| `test_modern_wireless_regression.py` | Broadcom path, existing external Intel path, no detector/spoof change |
| `test_phase1_boot_argument_policy.py` | frozen inherited Phase-1 boot-argument policy |

The final runtime-hotfix validation result was 178 passed, 0 failed. The inherited non-failing `ResourceWarning` in `efi_builder/support.py:130` remains disclosed.

## Frozen boundaries and future work

The runtime-validated Phase-2/3 promotion must not introduce changes to Modern Wireless PCI IDs, EFI hardware configuration, automatic spoofing, DeviceProperties, ACPI, DMAR, AppleVTD, Modern Wireless payloads/dictionaries, Modern Audio payloads/dictionaries, Wi-Fi-only no-KDK behavior, or inherited AUTO exact/closest ranking among eligible KDKs.

Broadcom and future direct Intel Modern Wireless paths must be tested independently. The validated Broadcom Phase-3 result is closed; future Intel integration is a separate block.

HFS+ to APFS payload conversion is not Phase 3 and is reserved for **Phase 4 — Build / Packaging Finalization**.
