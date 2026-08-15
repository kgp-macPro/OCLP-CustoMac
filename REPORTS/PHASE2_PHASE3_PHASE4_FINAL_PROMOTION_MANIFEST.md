# Phase 2 + Phase 3 + Phase 4 Final Promotion Manifest

Date: 2026-08-15

## Promotion authority

The authoritative final tracked source is the complete implementation state at:

`a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0`

The Phase-2/3 runtime-validated implementation beneath it remains:

`62e0b1c0413eb900bda69955030dd5bee28219b6`

All four completed phases are **COMPLETE — RUNTIME VALIDATED — FROZEN**. Promotion must reproduce final source behavior and its regression tests. Development commits are provenance; they are not instructions to replay superseded experiments.

`PHASE2_PHASE3_FINAL_PROMOTION_MANIFEST.md` remains the detailed source/function/test map for Phase 2, Phase 3B, and Phase 3C. This combined manifest incorporates that entire validated scope and adds the authoritative Phase-4 promotion requirements below.

## Phase-2/3 functionality that must remain promoted

| Validated area | Final contract | Detailed authority |
|---|---|---|
| Locked reproducible build | CPython 3.14.3 x86_64, exact 22-wheel lock, fixed build metadata, deterministic ad-hoc finalization and packaged-app parity | Phase-2/3 manifest sections 1–2 |
| Root-state and patch authorization | Only CLEAN authorizes new patching; existing, differing, pending, failed, legacy, and unknown non-clean states block it | sections 3–4 |
| Common recovery authorization | Recovery is not gated by build/SHA/fork/patch/KDK ownership; SIP and actual execution checks remain | sections 4–5 |
| Root-patch selection | One applicability-constrained operation model; truthful installed selection and metadata; installed selection is read-only until Revert/reboot | sections 6–10 |
| Modern Wireless | Complete applicable root-patch family can be selected independently; no selection-layer hardware/EFI mutation | section 7 |
| Modern Audio | Beta-1 AppleHDA family and KDK requirement are included only when selected | section 8 |
| Wi-Fi-only | Modern Wireless works without a KDK requirement caused solely by deselected Audio | section 9 |
| Empty selection | Start disabled and forced explicit empty operation rejected before any KDK/root work | section 10 |
| Manual KDK | Trusted-catalog, operation-scoped exact choice with AUTO preview, confirmation, standard progress path, and no substitution | sections 11–12 |
| KDK provenance | Successful metadata records AUTO/MANUAL and exact used identity as history, not future preference | section 12 |
| Darwin-26 exclusion | Canonical ProductBuildVersion-family filter excludes build family 26 while permitting `25G82`; AUTO ranking among permitted candidates is unchanged | section 13 |
| Lifecycle/recovery provenance | Boot-scoped integrity-checked in-progress, failed-recovery-required, pending-reboot, and revert-pending evidence | section 14 |
| OCLP-Mod metadata compatibility | Both `OCLP-Mod.plist` and `oclp-mod.plist` are recognized without becoming current KGP ownership | section 15 |

All Phase-2/3 tests named in the earlier manifest remain mandatory. Phase 4 must not weaken or reinterpret any of those contracts.

## Phase 4.1 — APFS `payloads.dmg` creation and frozen input

**Promotion:** MUST PROMOTE.

**Final source:** `ci_tooling/build_modules/disk_images.py`; fixed build input `payloads.dmg`; `tests/test_phase4_disk_images.py`.

**Key code:** `GenerateDiskImages._generate_payloads_dmg()`.

**Final behavior:** the builder creates `payloads.dmg` with APFS while preserving its filename, volume identity, source tree, capacity, UDZO/encryption contract, and logical payload content. `Universal-Binaries.dmg` remains APFS and functionally unchanged.

**Pinned images:**

- `payloads.dmg`: `082de073e0d103d7bd4b47852007f2b6ab360eda5b4737a089cf3b34a3910f91`;
- `Universal-Binaries.dmg`: `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4`.

**Logical evidence:** 351 files, 133 directories, 0 symlinks, and canonical per-file aggregate `789687b7ac93dd0eb686e56f5b869636e93d535c36107bef817d2906294db9da` match the HFS+ baseline. Native APFS UUID/container variation is expected; the selected logical-equivalent image is pinned rather than regenerated for each reproducible application build.

**Origin:** `b269e61b6c3e88c2b24c85eb09ddd884ca980580`.

**Do not promote:** a regenerated image with refreshed payload bytes; any payload/kext/framework/version update hidden inside the filesystem conversion; a claim of byte determinism across independent native APFS generations.

## Phase 4.2 — APFS-compatible runtime mount topology

**Promotion:** MUST PROMOTE.

**Final source:** `opencore_legacy_patcher/support/disk_image.py`; `support/reroute_payloads.py`; `sys_patch/utilities/dmg_mount.py`; `support/validation.py`.

**Key code:** the shared protected-image attach helper; outer payload setup; `PatcherSupportPkgMount._mount_universal_binaries_dmg()`; scoped detach/cleanup.

**Final behavior:** `payloads.dmg` mounts unprivileged with a writable shadow at the existing operation payload root. `Universal-Binaries.dmg` mounts at a sibling host temporary path with its own shadow. A symlink created in the writable outer shadow preserves the historical `payloads/Universal-Binaries` logical path. Cleanup detaches the inner Universal image before the outer payload image and leaves no stale operation mount.

**Runtime proof:** implementation `0b6b25161936c672d21a7af82796ff9b80c9d22e`, package `OCLP-v2.0-phase4-apfs-runtime-fix/OpenCore-Patcher.pkg`, SHA-256 `3c3a01bbaacfb3a65ba02650ee1e23a771bc8dfe29afe3bee3f7288f439205c9`.

**Origin:** `0b6b25161936c672d21a7af82796ff9b80c9d22e`.

**Do not promote:** the failed direct nested unprivileged APFS mount; mounting the inner image inside the already-mounted APFS volume; suppression of the mount failure; any new APFS snapshot or cleanup engine.

## Phase 4.3 — Noninteractive protected-image authentication

**Promotion:** MUST PROMOTE.

**Final source:** shared `support/disk_image.py` and all runtime/validation consumers above.

**Final behavior:** protected-image attachment uses `hdiutil -stdinpass` with the repository image password supplied through stdin, never process argv or interactive DiskImages authentication. Application signing remains timestamp-free ad hoc with no named identity, private key, Keychain authorization, or Team ID. Verification remains strict/deep and read-only.

**Tests:** `tests/test_phase4_runtime_disk_images.py` protects both images, `-stdinpass`, absence of deprecated `-passphrase`, sibling mount topology, and logical symlink behavior.

**Do not promote:** deprecated runtime `-passphrase`; unqualified protected-image `hdiutil imageinfo`/`verify`; Keychain lookup; named signing identity; silent background credential acquisition.

## Phase 4.4 — Security boundary versus Mod/Plus

**Promotion:** MUST PROMOTE the decision, not the fork helper.

The final KGP design remains unprivileged. Do not promote the OCLP-Mod/OCLP-Plus general-purpose privileged-helper approach for nested APFS `hdiutil`. KGP's ad-hoc signature has no Team ID with which to satisfy their release signer boundary; weakening that boundary would create unnecessary privileged command execution. No setuid/root helper is part of Phase 4.

## Phase 4.5 — Revert-specific KDK probe/log cleanup

**Promotion:** MUST PROMOTE.

**Final source:** `support/kdk_handler.py`; `sys_patch/patchsets/detect.py`; `sys_patch/sys_patch.py`; `support/arguments.py`; `wx_gui/gui_entry.py`; `wx_gui/gui_sys_patch_display.py`; `wx_gui/gui_sys_patch_start.py`.

**Key code:** quiet installed-KDK status support; selection detection's Revert-only KDK-status boundary; `revert_mode`/`unpatching` propagation; `PatchSysVolume.start_unpatch()`.

**Final behavior:** Revert-specific detection does not perform KDK availability/resolver probing because rollback does not need KDK selection, download, install, or merge. Shared display calculations suppress irrelevant installed-KDK status. Normal Root Patching retains its full KDK checks and useful logging. Recovery authorization, SIP/`can_unpatch`, click/operation-time validation, mount, and last-sealed-snapshot rollback are unchanged.

**Tests:** `tests/test_revert_kdk_logging.py` plus all existing recovery/state tests. Final complete suite at the implementation commit: 186 passed, 0 failed.

**Runtime proof:** implementation `a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0`, package `OCLP-v2.0-phase4-revert-log-cleanup/OpenCore-Patcher.pkg`, SHA-256 `9beaa5378e92b3fed4a62615d5801a7d9ed48dee905a25a29ceb09bf0fe20ac4`; KGP confirmed Revert 100% verified with no redundant KDK messages.

**Do not promote:** global KDK logging suppression; removal of normal patch KDK status; relaxed Revert authorization/SIP validation; any KDK resolver/ranking change.

## Final Phase-4 regression gate

Promotion must include and pass:

- `tests/test_phase4_disk_images.py`;
- `tests/test_phase4_runtime_disk_images.py`;
- `tests/test_revert_kdk_logging.py`;
- the complete Phase-2/3 suite from the earlier manifest;
- frozen Modern Wireless/Audio source hashes;
- frozen logical payload aggregate and both pinned image hashes;
- strict/deep built-app and package-expanded-app signature verification;
- checksum/tree parity between the built and packaged application.

## Superseded Phase-4 approaches — not for promotion

- failed direct inner mount at a nested location inside the outer APFS shadow;
- deprecated `-passphrase` runtime attachment;
- protected-image inspection or verification without `-stdinpass`;
- interactive DiskImages/Keychain authentication;
- Mod/Plus privileged/general-purpose helper architecture;
- temporary audit, mount-probe, Keychain-diagnostic, or image-generation workspaces/scripts;
- any payload refresh or `Universal-Binaries.dmg` regeneration;
- global removal of normal Root Patching KDK status.

## Final runtime-evidence boundary

The runtime evidence is intentionally split:

- `0b6b251...` / package SHA `3c3a01...` proves APFS resource mounting and the successful BOTH root-patch/reboot result;
- `a2b6e60...` / package SHA `9beaa537...` proves the final Revert cleanup and successful real Revert.

Do not claim that the latter package performed the preceding root-patch operation. The canonical source to promote is nevertheless the final complete state `a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0`.

## Next-phase boundary

Phase 5 — Intel Modern Wi-Fi Integration — has not begun. It must start later from the frozen Phase-4 state and independently test Broadcom and Intel paths. It must not add automatic Broadcom spoofing, automatic EFI mutation, or ACPI/DMAR/DeviceProperties changes without separate authorization and evidence.
