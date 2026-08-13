# HFS+ vs APFS — Practical Engineering Decision

Audit date: 2026-08-13

KGP branch: `experiment/amfipassbeta-v2.0`

Golden runtime baseline: `454bd1b867a40c301240928085eb0fa4b04452ba`

Phase-1 baseline: `6fcf12f0bd4d4717ab9e7ad50db1926ea4537a57`

## Decision

**APFS-OPTIONAL / LOW-PRIORITY**

KGP should retain the current HFS+ `payloads.dmg` for the v2.0 golden line unless there is a later maintenance reason to reopen this boundary. APFS is technically reasonable, very easy to implement, and probably more future-proof, but it supplies no demonstrated current-Tahoe reliability, security, payload, or root-patching advantage over the runtime-validated baseline.

The decisive fact is that the KGP application is already a mixed-filesystem design:

- `payloads.dmg` is HFS+ and works on current Tahoe;
- the frozen `Universal-Binaries.dmg` is already APFS and also works through KGP's existing, non-elevated mount code;
- the live macOS System volume and its root-patch snapshots are APFS independently of both resource images.

Changing `payloads.dmg` to APFS would therefore be an outer resource-container modernization, not a patcher modernization. It would reopen image creation, application/package hashes, attach/detach behavior, and runtime patch/revert validation without changing logical payload content.

No implementation source, DMG, EFI, NVRAM, root volume, or production repository was modified during this assessment. Existing images were inspected statically and were not mounted or regenerated.

### KGP project decision

KGP has accepted the following sequencing decision for v2.0:

- HFS+ remains the working development baseline while functional v2.0 work is completed.
- Conversion of `payloads.dmg` to APFS is intentionally postponed until all functional v2.0 work is complete.
- The intended final resource-image state is `payloads.dmg` on APFS and `Universal-Binaries.dmg` on APFS; the latter is already APFS.
- The later `payloads.dmg` conversion must be one isolated, easily revertible maintenance commit and receive separate runtime validation against the golden HFS+ baseline.

## Evidence baseline

Exact local source states inspected:

| Target | Path | Commit/tag |
|---|---|---|
| KGP v2.0 | `/Users/kgp/Developer/OCLP-amfipassbeta-v2.0-development` | `454bd1b867a40c301240928085eb0fa4b04452ba` |
| OCLP-Plus | `/Users/kgp/Developer/OCLP-Plus-Mod-evaluation-audit/SOURCES/OCLP-Plus-3.2.2` | `afc5021e0c27df30c2d249fce709566220f76273`, tag `3.2.2` |
| OCLP-Mod | `/Users/kgp/Developer/OCLP-Plus-Mod-evaluation-audit/SOURCES/OCLP-Mod-3.1.9` | `3b15c88820a6f99d1974532b9a722925da8b2897`, tag `3.1.9` |

All three repositories were clean and remote-free when inspected. KGP's authoritative production repository remained clean on `main` at `ec5e591e0f46e948b0258ef1c8ed5d17d6a2c865`.

Read-only `hdiutil imageinfo`, file-size, and SHA-256 inspection established:

| Exact release/build image | Filesystem and container | Size | SHA-256 |
|---|---|---:|---|
| KGP `payloads.dmg` | whole-disk HFS+; encrypted, zlib-compressed UDZO; 32,000 MiB virtual size; layout `NONE` | 51,643,392 | `22581d0a9981f583d1921ca447bb0d578b3c39b20a805c5c6bac4ab5678d6f98` |
| KGP `Universal-Binaries.dmg` | GPT/APFS; encrypted, LZMA-compressed ULMO; 4,096 MiB virtual size | 664,348,160 | `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4` |
| Plus 3.2.2 packaged `payloads.dmg` | whole-disk APFS; encrypted, zlib-compressed UDZO; 32,000 MiB virtual size; layout `NONE` | 50,688,000 | `ed15685a56871656dd592e8ebd89822d4aa180aec2b51d598d129724c3e67fa0` |
| Mod 3.1.9 packaged `payloads.dmg` | whole-disk APFS; encrypted, zlib-compressed UDZO; 32,000 MiB virtual size; layout `NONE` | 52,411,392 | `7ade9aac53f0f1b18ca1ad479f6a3f432385e8aebe04f83b9b5d983032da06f2` |

The different Plus/Mod sizes and hashes cannot be used as a filesystem-efficiency comparison because their payload trees differ from KGP and from each other.

## 1. Exact KGP boundary

### A. Build-time disk-image generation

`Build-Project.command` invokes `GenerateDiskImages.generate()` before application and package creation. The relevant implementation is `ci_tooling/build_modules/disk_images.py`:

- `_delete_extra_binaries()` limits the source `payloads/` tree to `ACPI`, `Config`, `Drivers`, `Icon`, `Kexts`, `OpenCore`, `Tools`, and `Launch Services`.
- `_generate_payloads_dmg()` creates `payloads.dmg` with `hdiutil create`, `UDZO`, a 32,000 MiB virtual size, `-layout NONE`, password encryption, and `-fs HFS+` at line 80.
- There is no resize command. The large virtual size exists so the runtime shadow image has sufficient capacity.
- `_download_resources()` acquires `Universal-Binaries.dmg`; it does not create or transform it.
- Both DMGs are cache inputs: without `--reset-dmg-cache`, existing images are reused.

`OpenCore-Patcher-GUI.spec` lines 29–31 embeds both files unchanged in the application bundle. Package creation then packages the resulting application; it does not reinterpret their filesystems.

The current KGP PatcherSupportPkg's active `Generate-DMG.command` creates `Universal-Binaries.dmg` as APFS and converts it to encrypted ULMO. Its older `build-dmg.sh` still contains an HFS+ command, but that does not describe the exact frozen release image: static inspection proves the released KGP image is APFS. The separate `Generate-Internal-Overlay.command` still uses HFS+ for an optional developer overlay.

### B. Runtime resource-image mounting and consumption

`opencore_legacy_patcher/constants.py` lines 270–275 maps the bundle-root images; line 827 maps the mounted PatcherSupportPkg tree.

`opencore_legacy_patcher/application_entry.py` line 104 starts `RoutePayloadDiskImage` during application initialization. `opencore_legacy_patcher/support/reroute_payloads.py`:

- acts only for the compiled wxPython application, not source execution;
- creates a private temporary `payloads` mountpoint;
- attaches `payloads.dmg` with `-noverify`, `-nobrowse`, the fixed passphrase, and a private `payloads_overlay` shadow;
- uses ordinary `subprocess.run`, not the privileged helper;
- redirects `constants.current_path` and `constants.payload_path` to the mounted tree;
- records an `atexit` cleanup and force-detaches only the image associated with its own shadow path.

The mounted `payloads.dmg` supplies the EFI-builder archives/config template, icons, launch-service resources, tools, and other packaged application resources.

`opencore_legacy_patcher/sys_patch/utilities/dmg_mount.py` lines 23–47 then attaches the already-APFS `Universal-Binaries.dmg` at `payloads/Universal-Binaries`, also using `-noverify`, `-nobrowse`, a shadow file, the fixed passphrase, and ordinary `subprocess.run`. `PatcherSupportPkgMount.mount()` is called by `opencore_legacy_patcher/sys_patch/sys_patch.py` line 568 before the root volume is mounted. Root-patch file copies use `constants.payload_local_binaries_root_path` as their source at line 372.

`opencore_legacy_patcher/support/validation.py` lines 199–267 independently mounts, validates, detaches, and removes the PatcherSupportPkg shadow during developer validation. It is not the live patch workflow.

No `DortaniaInternalResources.dmg` is present in the golden development tree. The runtime can optionally mount one for developer use, but it is not part of the v2.0 primary path.

### C. macOS System-volume APFS root-patch handling — separate subsystem

The following code is already APFS-specific and is unrelated to the resource-image filesystem:

- `opencore_legacy_patcher/sys_patch/mount/mount.py` identifies and mounts the macOS System volume as APFS;
- `opencore_legacy_patcher/sys_patch/mount/snapshot.py` creates and reverts boot snapshots;
- `opencore_legacy_patcher/sys_patch/sys_patch.py` invokes those snapshot operations around patch/revert.

Changing `payloads.dmg` from HFS+ to APFS does not change the live root filesystem, seal, kernel cache, snapshot, or revert implementation.

Other occurrences are also outside this decision: Apple KDK/installer DMG attachment, macOS installer-media HFS+ formatting, OpenCore's EFI APFS driver/configuration, and FileVault/APFS-seal logic.

## 2. What Plus and Mod changed

### OCLP-Plus 3.2.2

The filesystem conversion is commit `bcb4b1391248174b47b8b772e8d0da14bfd29c08`, “Change filesystem format from HFS+ to APFS.” It changes exactly one line in `ci_tooling/build_modules/disk_images.py::_generate_payloads_dmg()`:

```text
- '-fs', 'HFS+',
+ '-fs', 'APFS',
```

Plus separately changed the compiled `payloads.dmg` attach in `oclp_plus/support/reroute_payloads.py::_setup_tmp_disk_image()` from `subprocess.run` to `subprocess_wrapper.run_as_root` in commit `59119350c40507a3341d0778d024625756daedbd`. It separately made the same elevation change for `Universal-Binaries.dmg` in `oclp_plus/sys_patch/utilities/dmg_mount.py::_mount_universal_binaries_dmg()` in commit `b841a3316b2197d8b5b5e11fb4e411e2c7616935`.

### OCLP-Mod 3.1.9

The filesystem conversion is commit `a9d2fcf61226f7243c34a3b97f7b2bcc38fee03d`, “macOS 26.4B1 removed HFS+ support, change to APFS.” It makes the same one-line change in the same function.

Mod's two elevation changes are in separate commit `2862c2e35202a3ed288e58b3ca69e6b08c0307a5`, affecting `oclp_mod/support/reroute_payloads.py::_setup_tmp_disk_image()` and `oclp_mod/sys_patch/utilities/dmg_mount.py::_mount_universal_binaries_dmg()`.

### Semantic comparison

Plus and Mod use essentially the same APFS implementation:

| Area | Plus 3.2.2 | Mod 3.1.9 | Material difference? |
|---|---|---|---|
| `payloads.dmg` creation | `-fs APFS` | `-fs APFS` | No |
| Image type | 32,000 MiB, UDZO, encrypted, layout `NONE` | same | No |
| Mount flags | `-noverify`, fixed mountpoint, `-nobrowse`, shadow, passphrase | same | No |
| Attach execution | privileged wrapper in compiled/runtime paths | same | No |
| Detach | existing force-detach logic | same | No |
| Shadow/cleanup | existing temporary shadow and `atexit` logic | same | No |
| Resize | none | none | No |
| Permissions | elevation added independently of filesystem-line change | same result | No |
| Validation mount | ordinary `subprocess.run` | ordinary `subprocess.run` | No |
| Extra handling | ordinary logging | localized logging; unrelated four-second validation delay | No APFS benefit |

Their namespaces, download URLs, localized strings, and internal-overlay names differ, but these are unrelated to HFS+/APFS.

The elevation changes should not be copied automatically. KGP's golden build already mounts its APFS `Universal-Binaries.dmg` through the same unprivileged `hdiutil attach` pattern during successful root patching. Plus/Mod's own validation paths also retain unprivileged APFS attachment. APFS therefore does not intrinsically require adopting their broader privileged-helper boundary.

## 3. Practical scorecard

| Category | Result | Concrete basis |
|---:|---|---|
| 1. Current Tahoe 26.x compatibility | **EQUAL** | KGP's HFS+ outer payload image and APFS inner support image both work in the golden runtime; the stated current-Tahoe HFS+ defect no longer exists. |
| 2. Mount reliability | **EQUAL** | Both formats are already mounted successfully by KGP; Plus/Mod leave mount flags and cleanup semantics unchanged. |
| 3. Image creation reliability | **EQUAL** | Both use the same `hdiutil create` flow with only `-fs` changed; no current failure is established for either. |
| 4. Attach/detach cleanup | **EQUAL** | Shadow naming, `atexit`, image enumeration, and force-detach logic are unchanged. |
| 5. Permissions/ownership preservation | **EQUAL** | Both Apple filesystems preserve the relevant POSIX metadata; no fork code supplies evidence of an APFS-specific gain. The current `payloads/` tree contains no symlinks. |
| 6. Symlink/xattr preservation | **EQUAL** | Both formats support them, and the conversion does not change the source-copy operation. Canonical metadata comparison would still be required in a prototype. |
| 7. Corruption/error recovery | **EQUAL** | These are encrypted, compressed, read-only distribution images with disposable shadows. Operational recovery is verification/reacquisition, not in-place filesystem repair. |
| 8. Security | **EQUAL** | The same UDIF encryption and static passphrase are used. APFS supplies no meaningful new trust boundary here. Copying fork elevation would instead enlarge privileged execution. |
| 9. Maintenance complexity | **EQUAL** | A KGP-native implementation is one literal change; runtime code can remain format-agnostic. The one-time migration validation is covered under regression risk. |
| 10. Code simplicity | **EQUAL** | Minimal HFS+ and APFS creators differ by one token. Plus/Mod's elevation is independent and unnecessary absent a demonstrated failure. |
| 11. Future macOS compatibility | **APFS BETTER** | APFS is Apple's current native filesystem and the path used by both maintained forks; HFS+ remains legacy despite current support. This is prospective, not a present requirement. |
| 12. Build reproducibility | **HFS+ BETTER** | For regeneration, APFS adds container/volume UUIDs and transaction/checkpoint metadata. HFS+ also has UUID/timestamp/catalog metadata, and encryption adds fresh cryptographic metadata, so neither current create command is proven byte-deterministic; APFS is not easier. With a fixed, hash-pinned DMG input, application reproducibility is equal. |
| 13. Package/image size | **UNKNOWN** | Existing fork images contain different logical payloads; a same-tree controlled generation is required. |
| 14. Build speed | **UNKNOWN** | No same-source controlled measurement was performed. |
| 15. Runtime speed | **EQUAL** | The workload is a short attach followed by ordinary reads; no source or runtime evidence shows a material difference. |
| 16. Ease of debugging | **HFS+ BETTER** | The current whole-disk HFS+ image has a simpler device/filesystem topology than an APFS container plus volume. KGP's exact path is already understood and validated. |
| 17. Regression risk | **HFS+ BETTER** | HFS+ is the installed, successful golden baseline. APFS would require new image, app, package, mount, patch, reboot, and revert validation. |
| 18. Alignment with current Plus/Mod | **APFS BETTER** | Both exact forks use APFS for `payloads.dmg`. |

APFS wins future alignment; HFS+ wins the immediate reproducibility/debugging/regression boundary. Neither wins current functionality.

## 4. Reproducibility impact

Phase 2A established byte-reproducible application builds under an explicit boundary: both builds reused the exact same verified `payloads.dmg` and `Universal-Binaries.dmg`. `REPORTS/PHASE2A_BUILD_ENVIRONMENT_AUDIT.md` already records DMG regeneration as a separate supply-chain boundary.

An APFS migration would have two distinct effects:

1. **Fixed-input application builds:** neutral. Once one APFS `payloads.dmg` is selected and SHA-256-pinned, the PyInstaller build embeds those bytes exactly as it does today. The application can remain byte-reproducible from that fixed input.
2. **Recreating the DMG from `payloads/`:** harder, or at best unproven. APFS normally creates fresh container and volume UUIDs plus creation/checkpoint metadata. HFS+ also creates fresh volume/timestamp/catalog metadata. The current command additionally encrypts the image, introducing fresh cryptographic metadata. No claim should be made that either freshly generated image will hash identically across runs.

Therefore APFS does not improve Phase 2A reproducibility. It adds APFS-specific nondeterministic metadata to an already separately nondeterministic image-generation boundary. If adopted later, KGP should either pin one authenticated generated image as an input or first design a controlled image-normalization/reproducibility policy; it should not fold DMG regeneration into the existing application reproducibility claim.

## 5. Patcher behavior boundary

The minimum conversion touches only the filesystem literal used when creating `payloads.dmg`. The mounted relative paths are identical. Accordingly:

| System | Effect of minimal HFS+ → APFS conversion |
|---|---|
| Modern Wireless detection and patch dictionary | None |
| Modern Audio detection and patch dictionary | None |
| Beta-1 AppleHDA | None |
| PatcherSupportPkg identity/content | None; frozen APFS `Universal-Binaries.dmg` remains byte-identical |
| IO80211FamilyLegacy / IOSkywalkFamily | None |
| AMFIPass 1.4.1 | None |
| `-amfipassbeta` and retired automatic `-lilubetaall` policies | None |
| KDK selection, download, validation, installation | None |
| Root-patch dictionaries and destinations | None |
| Kernel-cache rebuild | None |
| System-volume mount, snapshot creation, seal, and revert | None |
| SIP validation | None |
| ACPI, DMAR, DeviceProperties, PCI/IOMapper, AppleVTD | None |

This conclusion follows from the exact fork history: each filesystem conversion changed only `ci_tooling/build_modules/disk_images.py`. No root-patch or EFI-builder decision code was part of either conversion. The image bytes and filesystem metadata would differ, but a canonical file-tree comparison should show the same logical payload files and hashes.

## 6. Port feasibility

### Minimum KGP-native implementation

Required functional source change:

- `ci_tooling/build_modules/disk_images.py::_generate_payloads_dmg()`, line 80: change `HFS+` to `APFS`.

Required generated/output changes:

- regenerate `payloads.dmg` from the exact same pruned `payloads/` tree;
- update its pinned hash wherever the build/release process records it;
- rebuild the application and package because the embedded DMG bytes change;
- update resulting application/package artifact manifests.

Not required:

- no `Universal-Binaries.dmg` regeneration—it is already APFS and must remain frozen;
- no spec, package-builder, constants, root-patch, KDK, EFI-builder, or snapshot change;
- no new helper, class, dependency, or mount option;
- no root privilege for image creation;
- no demonstrated need to change runtime attachment to `run_as_root`.

Approximate implementation size is one functional source line, plus test/report/manifest updates. If a disposable test unexpectedly proved unprivileged attachment impossible for the outer APFS image, two additional call-site lines would reproduce the fork elevation in `opencore_legacy_patcher/support/reroute_payloads.py` and `opencore_legacy_patcher/sys_patch/utilities/dmg_mount.py`. That should be treated as a reason to reconsider adoption, not assumed as part of the port, because HFS+ already works and KGP already mounts APFS support payloads without elevation.

The Plus/Mod filesystem line can be adapted directly and has no unrelated dependencies. Their privileged-wrapper changes should not be copied without evidence.

**Implementation confidence: VERY HIGH** for an isolated source conversion; **runtime adoption confidence remains HIGH** until the regenerated image completes the controlled validation below.

**Can this APFS conversion be implemented as one isolated, easily revertible commit on top of `454bd1b...`? YES.** The commit should contain the one source change and its tests/reports/manifests; ignored generated DMGs and build outputs should remain separately hash-pinned artifacts.

## 7. Smallest controlled validation plan

Overall difficulty: **MODERATE**. The code change is simple; the required runtime patch/reboot/revert proof makes the full acceptance test more than a simple static check.

1. Start an isolated disposable branch/worktree exactly at `454bd1b867a40c301240928085eb0fa4b04452ba` and preserve the golden HFS+ image/hash.
2. Change only the `-fs` literal. Do not copy Plus/Mod elevation, URLs, or other fork code.
3. Generate only a new APFS `payloads.dmg` from the exact same source tree. Keep `Universal-Binaries.dmg` at `3659ae0e...`.
4. Verify the new image with `hdiutil verify` and `imageinfo`. Attach it without sudo using the actual shadow/mount arguments, repeat attach/detach cycles, and prove no stale mounts or shadows remain.
5. Compare canonical source and mounted manifests: relative path, object type, mode, uid/gid, symlink target, xattrs, file size, and SHA-256. Filesystem housekeeping metadata is excluded; every logical payload must match.
6. Run two image generations only if DMG-level reproducibility is being evaluated. Expect and explain UUID/timestamp/encryption differences rather than assuming equal hashes.
7. Select and hash-pin one APFS image, then repeat the locked Phase 2A application build twice with that identical input. Require the existing application reproducibility boundary to hold.
8. Expand the application/package and verify the same component versions, payload hashes, PatcherSupportPkg hash, AMFIPass 1.4.1, AppleHDA, IO80211FamilyLegacy, and IOSkywalkFamily.
9. Re-run synthetic EFI fixtures and require identical generated config semantics, Modern Wireless/Audio selection, KDK behavior, exactly one `-amfipassbeta` when AMFIPass is selected, and no automatically generated `-lilubetaall`.
10. Perform one isolated KGP runtime cycle: root patch, reboot, confirm Modern Wireless and Modern Audio, revert, reboot, and confirm clean revert. No Intel hardware swap is required.

## Direct answers

1. **Is KGP's HFS+ implementation working correctly on current Tahoe?** Yes. KGP reports the exact `454bd1b...` package works perfectly on the real Tahoe Hackintosh.
2. **Is APFS required for current Tahoe?** No.
3. **Does APFS provide a concrete advantage today?** Only a prospective maintenance advantage: alignment with Apple's active filesystem and both current forks. No present functional/reliability gain is demonstrated.
4. **Does HFS+ provide a concrete advantage today?** Yes: it is the golden runtime baseline, has simpler on-image metadata/topology, and avoids reopening image-generation and runtime acceptance testing.
5. **Which is simpler in KGP's current tree?** The implementations are one-token equivalents, but retaining HFS+ is operationally simpler because it requires no migration.
6. **Which is likely more future-proof?** APFS.
7. **Which is more reproducible?** HFS+ is marginally easier at the regeneration boundary; neither current encrypted creation flow is proven deterministic. With a fixed DMG input, they are equal for application reproducibility.
8. **Do Plus and Mod implement APFS essentially the same way?** Yes. Their one-line filesystem conversions and runtime mount models are substantively the same.
9. **Would APFS alter logical payload content?** No, provided the same source tree is used and canonical manifests are verified; it changes container/filesystem bytes and metadata.
10. **Would APFS alter root-patch behavior?** No.
11. **What exact files would KGP need to change?** Functionally, only `ci_tooling/build_modules/disk_images.py`. Tests, reports, and artifact manifests would also change. Runtime mount files should remain untouched unless a controlled prototype proves otherwise.
12. **Would DMGs need regeneration?** `payloads.dmg`: yes. `Universal-Binaries.dmg`: no—it is already APFS and frozen.
13. **Can the conversion be implemented cleanly?** Yes.
14. **Confidence level?** VERY HIGH for isolation/implementation; HIGH for adoption pending runtime acceptance.
15. **Can it be one isolated/revertible commit?** Yes.
16. **How difficult is validation?** MODERATE.
17. **Is there a compelling reason to switch now?** No.
18. **Final recommendation:** **APFS-OPTIONAL / LOW-PRIORITY**.
