# Phase 3C Recovery Hotfix and Darwin 26 KDK Eligibility

## Baseline and result

The hotfix was developed in the remote-free primary repository from the documentation checkpoint:

`aecdd7e0c87ab53d76286c5d39bf27da3cb396c6`

Its validated implementation parent was:

`53c44be749e77d830b4ee5ba733321f40d31ec02`

The clean implementation HEAD used to build the runtime artifact is:

`62e0b1c0413eb900bda69955030dd5bee28219b6`

The implementation commits are:

1. `c1d5e05c3cad7de12af738725136a53030183088` — `kdk: validate root patch eligibility by build family`
2. `448d652d20d081856dcfc564b286b3887e52f127` — `state: preserve recovery after partial root patching`
3. `62e0b1c0413eb900bda69955030dd5bee28219b6` — `state: authorize common revert for blocked roots`

The third commit deliberately supersedes the more restrictive recovery-evidence policy initially implemented in the second commit. Lifecycle records remain useful state/provenance information, but are not Revert authorization prerequisites.

## Exact tracked implementation changes

Runtime source:

- `opencore_legacy_patcher/support/kdk_handler.py`
- `opencore_legacy_patcher/support/kdk_selection.py`
- `opencore_legacy_patcher/sys_patch/lifecycle.py`
- `opencore_legacy_patcher/sys_patch/root_state.py`
- `opencore_legacy_patcher/sys_patch/sys_patch.py`
- `opencore_legacy_patcher/sys_patch/utilities/kdk_merge.py`

Tests:

- `tests/test_darwin26_kdk_policy.py`
- `tests/test_phase2b_root_state_protection.py`
- `tests/test_phase3c_patch_pending_reboot.py`
- `tests/test_root_patch_recovery_authorization.py`

No other tracked implementation file changed.

## Darwin 26 KDK false-positive: cause and correction

The installed-KDK fast path can reach `kdk_merge.py` with `kdk_url_build` empty. The former merge guard treated that absent catalog field as a prohibited Darwin 26 identity and raised the misleading exception even though the installed KDK was `KDK_26.6.2_25G82.kdk`. It thereby conflated missing catalog identity and the KDK's marketing/product version with the Apple `ProductBuildVersion` family.

The correction uses one canonical eligibility rule based on the real Apple build identifier:

- `26A...` and all build identifiers whose parsed Darwin major is 26 are prohibited;
- `25...`, `24...`, and older build families remain permitted;
- a macOS product version such as `26.6.2` is not accepted as a build identity and cannot itself trigger the Darwin 26 prohibition.

The trusted KdkSupportPkg manifest is filtered once before the inherited AUTO exact/closest resolver. The resolver's ranking semantics are unchanged. Manual candidates, installed/local candidates, download selection, pre-install/operation validation, and the merge-time defense all reuse the same canonical rule.

For an already installed KDK, the merge guard reads `System/Library/CoreServices/SystemVersion.plist` and validates its actual `ProductBuildVersion`. Thus `KDK_26.6.2_25G82.kdk` resolves to `25G82` and is permitted, while `KDK_26.7_26A5368g.kdk` resolves to `26A5368g` and is rejected. A missing or malformed build identity fails closed with a distinct identity error rather than a false Darwin 26 diagnosis.

Rejected catalog logging is intentionally concise, for example:

`Ignoring prohibited Darwin 26 KDK: 26A5368g (26.7)`

The complete catalog record and its large `kernel_versions` structure are not logged.

## Root recovery deadlock: cause and final policy

The deadlock was policy-created rather than required by the rollback engine. Recovery authorization had become conditional on positive metadata ownership, recognized patch provenance, or a boot-session lifecycle record. A partial operation with no trusted installed selection could therefore be classified `INVALID_UNKNOWN`, block new patching, and also hide Revert even though the common OCLP rollback operation remained the appropriate recovery action.

The final model separates root-state authorization from GUI selection prerequisites:

- `patch_authorized` is true only for `CLEAN`;
- `recovery_authorized` is true for every non-clean/blocking root state except `REVERT_PENDING`, where the revert has already completed and reboot is required;
- Wi-Fi/Audio selection may independently disable Start on a clean root and never creates recovery authorization.

Accordingly, Revert is no longer gated by:

- matching Git commit or application build;
- matching project, fork, or OCLP-family identity;
- matching installed patch dictionary or requested patch set;
- KDK identity or AUTO/MANUAL/no-KDK provenance;
- trusted installed-selection metadata;
- lifecycle-record presence.

The resulting root-state policy is:

| Root state | Patch authorized | Recovery authorized |
|---|---:|---:|
| `CLEAN` | Yes | No |
| `PATCH_PENDING_REBOOT` | No | Yes |
| `PATCH_IN_PROGRESS` | No | Yes |
| `PATCH_FAILED_RECOVERY_REQUIRED` | No | Yes |
| `INSTALLED_SAME` | No | Yes |
| `INSTALLED_DIFFERENT_PATCH_SET` | No | Yes |
| `INSTALLED_DIFFERENT_BUILD` | No | Yes |
| `LEGACY_FOREIGN` | No | Yes |
| `INVALID_UNKNOWN` | No | Yes |
| `REVERT_PENDING` | No | No; reboot is required |

This means the already-existing pre-lifecycle failed state is recoverable without fabricating installed metadata. The GUI may continue to show `Installed selection: Unknown`, keeps Start disabled, and exposes Revert. There is no requirement to know which patch set, build, fork, or KDK produced the state.

No APFS snapshot discovery engine was added. The code does not enumerate arbitrary snapshots, inspect unrelated volumes, guess snapshot names, delete snapshots, or change APFS structures.

## True Revert execution prerequisites

Authorization to offer recovery is distinct from permission and ability to execute it. The following existing technical checks remain:

1. Display-, click-, and operation-time root-state revalidation.
2. SIP-derived `can_unpatch` validation.
3. Mounting the intended System/root volume through the existing patcher path.
4. The existing common rollback implementation using `bless --mount <volume> --bootefi --last-sealed-snapshot`.
5. Existing command-result/error handling.

SIP enforcement was not weakened. If recovery is the root-state action but SIP prevents execution, Revert remains visible. Clicking it reports the concrete SIP prerequisite and stops before mount or rollback. A mount or `bless` failure likewise fails the operation; authorization does not imply silent or automatic recovery.

`REVERT_PENDING` remains protected from a second destructive revert. It communicates that the existing revert completed and a reboot is required.

## Future partial-operation protection

The existing integrity-checked, root-owned, boot-session-bound lifecycle store now also represents:

- `PATCH_IN_PROGRESS`;
- `PATCH_FAILED_RECOVERY_REQUIRED`.

Immediately before crossing the first root-patch mutation boundary, the patcher records `PATCH_IN_PROGRESS`. A successful operation replaces it with the existing `PATCH_PENDING_REBOOT` record and truthful installed-operation metadata. An exception or unsuccessful result after that boundary records `PATCH_FAILED_RECOVERY_REQUIRED`, unmounts through the existing cleanup path, and does not claim a successful installation.

These records survive application quit/reopen on the same boot and become stale after a boot-session change as designed. They improve state presentation and provenance for AUTO-KDK, MANUAL-KDK, and no-KDK operations equally. They are not required to authorize the common Revert action.

## Preserved Phase 3B/3C behavior

- BOTH, Wi-Fi-only, Audio-only, and neither retain their established selection behavior.
- Wi-Fi-only remains no-KDK when no other selected patch requires one.
- Audio OFF excludes Modern Audio/Beta-1 AppleHDA and the KDK requirement caused solely by Modern Audio.
- Other selected KDK-requiring patches still require a permitted KDK.
- Empty explicit selection still aborts before KDK/root operations.
- Installed selection metadata still records only patches actually applied.
- AUTO exact/closest ranking among permitted KDK candidates is unchanged.
- Manual KDK selection remains exact, operation-scoped, and fail-closed without substitution.
- KDK download/install GUI, merge contents, KC commands, snapshot creation, and common rollback command are unchanged.
- Existing recognition of both `OCLP-Mod.plist` and lowercase `oclp-mod.plist` remains intact; metadata spelling no longer controls Revert authorization.

Modern Wireless detection and selection remain hardware-agnostic at the selection layer. Supported Broadcom fixtures and the existing supported Intel Modern Wireless fixture pass. No PCI identifiers, spoofing, EFI, DeviceProperties, ACPI, DMAR, AppleVTD, or hardware behavior changed.

## Validation

The exact clean implementation source was tested twice: once in the primary tree and once in the isolated build-source clone.

- Focused recovery/KDK suite: **67 passed, 0 failed**.
- Complete repository suite: **178 passed, 0 failed**.
- Exact build-source clone complete suite: **178 passed, 0 failed**.
- `python -m compileall`: passed.
- `git diff --check`: passed.
- One inherited non-failing `ResourceWarning` remains in `efi_builder/support.py:130`.

Locked build environment:

- CPython `3.14.3` x86_64;
- exactly 22 locked distributions;
- dependency lock SHA-256 `be3082246b9d559c766dbda3eac4bb5bc1766bd85cc76756953d06b042d152a0`;
- Python framework SHA-256 `131f5211d7a7ec6279abcc2e4b0b97f8559d8eb77d5a28c22771f9ced084360f`.

Frozen parity:

- payload aggregate: `13dc609fe5029df046c85c54693b48816f713a0c61220a955a3eb6677976a9a1`;
- Modern Wireless dictionary/source: `fa0dad681239c2268d17d81a9d8f422dc359d5d2b8b9fe670f2f12d4f3485f97`;
- Modern Audio dictionary/source: `a24581ef94b304d2252bc9db9d181a20332fe6621801dadf9bd5cb3339d2615d`;
- `payloads.dmg`: `22581d0a9981f583d1921ca447bb0d578b3c39b20a805c5c6bac4ab5678d6f98`;
- `Universal-Binaries.dmg`: `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4`.

Both the built app and package-expanded app pass `codesign --verify --strict --deep`. Their trees are byte/mode/symlink identical, excluding directory timestamps.

Final artifacts:

- `OpenCore-Patcher.pkg`: `66fb1ef601ad5df57a4cf4cb3906f2c72ef82134cac1d6bd238bcd59f34ec074`
- `OpenCore-Patcher-Uninstaller.pkg`: `f3b00eb527b99613e94190d4ed38ea33146ba4df23b73d69f8215d0d7ac1ee00`
- `AutoPkg-Assets.pkg`: `5ec814b2f5902c04026cbff71e7a3b0428996fd74a474326ddbcb9abfc0d8dc5`

Delivery directory:

`/Users/kgp/Desktop/OCLP/OCLP-v2.0-phase3C-recovery-hotfix`

The package embeds implementation HEAD `62e0b1c0413eb900bda69955030dd5bee28219b6`, its canonical commit URL, and exact commit date. It is a runtime-test artifact and has not been installed or executed by Codex.

## Integrity and limitations

No live-system operation was performed: no package installation, root patch, root revert, reboot, `bless`, KDK installation/removal, writable System mount, sudo mutation, EFI/NVRAM write, or hardware change. No dependency network resolution occurred.

The common Revert action is deliberately available for blocked/unknown non-clean states without metadata ownership proof, but it remains an explicit user action and may still fail safely at SIP, root mount, or `bless --last-sealed-snapshot`. The patcher does not attempt another new patch in those states.

Production, the Phase-2-only diagnostic repository, and the local upstream/Plus/Mod audit copies were not modified. This report is committed after the artifact build as a documentation-only checkpoint; it does not change the embedded implementation identity and does not require a rebuild.
