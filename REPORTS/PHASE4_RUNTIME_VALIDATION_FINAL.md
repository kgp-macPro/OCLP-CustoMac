# Phase 4 Runtime Validation Final

Date: 2026-08-15

## Closure status

| Phase | Final status |
|---|---|
| Phase 2 | **COMPLETE — RUNTIME VALIDATED — FROZEN** |
| Phase 3B | **COMPLETE — RUNTIME VALIDATED — FROZEN** |
| Phase 3C | **COMPLETE — RUNTIME VALIDATED — FROZEN** |
| Phase 4 | **COMPLETE — RUNTIME VALIDATED — FROZEN** |

The canonical Phase-2/3 implementation remains `62e0b1c0413eb900bda69955030dd5bee28219b6`. The canonical final Phase-4 source implementation is `a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0`.

This report records real-system evidence supplied by KGP. It does not rebuild, replace, install, patch with, or revert with either tested artifact.

## Final implementation history

| Scope | Commit |
|---|---|
| Convert `payloads.dmg` from HFS+ to APFS | `b269e61b6c3e88c2b24c85eb09ddd884ca980580` |
| Fix APFS runtime resource mounting | `0b6b25161936c672d21a7af82796ff9b80c9d22e` |
| Remove redundant KDK status/probing from Revert | `a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0` |

Intermediate development history is diagnostic provenance. Future promotion must reproduce the final behavior, not replay superseded approaches.

## Final disk-image state

| Image | Filesystem | Frozen SHA-256 |
|---|---|---|
| `payloads.dmg` | APFS | `082de073e0d103d7bd4b47852007f2b6ab360eda5b4737a089cf3b34a3910f91` |
| `Universal-Binaries.dmg` | APFS | `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4` |

The APFS `payloads.dmg` is logically equivalent to the Phase-2/3 HFS+ payload baseline:

- 351 regular files;
- 133 directories;
- 0 symlinks;
- unchanged relative paths, file bytes, modes, executable bits, bundle/plist content, and archives;
- unchanged canonical per-file SHA-256 aggregate `789687b7ac93dd0eb686e56f5b869636e93d535c36107bef817d2906294db9da`.

Native encrypted APFS creation generates fresh container and volume UUIDs, so independently generated image containers are not byte-identical. This expected container-level nondeterminism does not change logical payload content. Reproducible application builds therefore use the selected APFS image pinned by the hash above rather than regenerating it.

## APFS nested-mount failure and final architecture

The first installed Phase-4 candidate proved that the unchanged unprivileged helper could mount the inner resource image under an HFS+ outer shadow but failed when the outer shadow was APFS:

```text
hdiutil: attach failed - Permission denied
```

The failure was specific to mounting `Universal-Binaries.dmg` at a nested path inside the already-mounted APFS `payloads.dmg`. The frozen inner image itself mounted successfully at a normal host temporary path. Replacing deprecated `-passphrase` with `-stdinpass` corrected authentication but did not remove the APFS nested-mount restriction.

The final unprivileged topology is:

```text
payloads.dmg
    -> APFS shadow mount at the operation payload root

Universal-Binaries.dmg
    -> sibling host temporary mountpoint with its own shadow

historical payloads/Universal-Binaries path
    -> symlink created in the writable outer shadow
```

Existing consumers retain the historical logical path. Cleanup detects and detaches the inner Universal image before the outer payload image and removes the operation-scoped temporary hierarchy. No new snapshot, filesystem, or privilege mechanism was introduced.

## Cross-fork security decision

The exact local OCLP-Mod/laobamac and OCLP-Plus/YBronst sources also use APFS resource images. Their implementations preserve the nested hierarchy by running `hdiutil attach` through a privileged, general-purpose helper.

KGP deliberately did not adopt that architecture. The reproducible KGP application is ad-hoc signed and has no Team ID. Adopting the fork helper would require weakening or redesigning its signer/authorization boundary and would add unnecessary privileged command execution. The final design instead uses unprivileged `hdiutil`, a sibling host mount, and a logical symlink in the writable shadow. No setuid/root helper was added.

## Noninteractive image authentication and signing

Early read-only validation commands ran protected-image `hdiutil imageinfo` and `hdiutil verify` without the known image passphrase. DiskImages consequently attempted interactive authentication/Keychain lookup. These were validation-command mistakes, not code-signing failures.

The final implementation and validation supply the repository image passphrase noninteractively. Runtime protected-image attachment uses `-stdinpass`; the password is supplied via process stdin and is absent from argv. Final validation confirmed:

- no GUI authentication prompt;
- no Keychain import, unlock, authorization, or modification workflow;
- no Apple Development or Developer ID identity;
- no private key;
- ad-hoc application signatures;
- `TeamIdentifier=not set`;
- strict/deep verification for built and package-expanded applications.

## Root-patch runtime validation

The APFS/root-patch proof uses implementation `0b6b25161936c672d21a7af82796ff9b80c9d22e` and this immutable package:

```text
/Users/kgp/Desktop/OCLP/OCLP-v2.0-phase4-apfs-runtime-fix/OpenCore-Patcher.pkg
SHA-256: 3c3a01bbaacfb3a65ba02650ee1e23a771bc8dfe29afe3bee3f7288f439205c9
```

KGP performed a complete BOTH operation with Modern Wireless ON, Modern Audio ON, and AUTO KDK. The real workflow successfully completed:

- APFS-compatible `Universal-Binaries.dmg` mounting;
- KDK `26.6.2` / build `25G82` detection and root-volume merge;
- Modern Wireless installation, including `wifip2pd`, `IO80211.framework`, and `WiFiPeerToPeer.framework`;
- Modern Audio/Beta-1 `AppleHDA.kext` installation;
- installed patch metadata write;
- Boot/System Kernel Collection rebuild;
- root unmount and snapshot completion;
- successful reboot.

After reboot KGP confirmed AppleHDA working, Broadcom Wi-Fi working, and tested AWDL functionality working flawlessly. No Phase-2/3 regression was observed.

## Final Revert runtime validation

The later Revert-cleanup proof uses canonical final implementation `a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0` and this immutable package:

```text
/Users/kgp/Desktop/OCLP/OCLP-v2.0-phase4-revert-log-cleanup/OpenCore-Patcher.pkg
SHA-256: 9beaa5378e92b3fed4a62615d5801a7d9ed48dee905a25a29ceb09bf0fe20ac4
```

The preceding audit proved that Revert did not download, install, or merge a KDK. Repeated installed-KDK messages came from unnecessary read-only availability/resolver probing during shared detection. The final commit removes that probing from Revert-specific detection and makes shared display calculations quiet while retaining normal Root Patching KDK behavior.

KGP used the final package on the successfully Phase-4-patched system. The real output was:

```text
- Starting Unpatch Process
- Found SkylightPlugins folder, removing old plugins
- Cleaning Auxiliary Kernel Collection
- Unpatching complete

Please reboot the machine for patches to take effect
```

The redundant KDK messages were absent. KGP confirmed the Revert Root Patches fix as **100% VERIFIED**.

The evidence is intentionally split: the `0b6b251...` artifact performed and validates the root-patch/APFS workflow; the subsequent `a2b6e60...` artifact validates the final Revert cleanup. This report does not claim that the latter artifact performed the preceding root-patch operation.

## Frozen functional boundaries

Phase 4 did not reopen or change Phase-2/3 root-state policy, Patch/Revert authorization, SIP enforcement, lifecycle state, root-patch selection, AUTO/MANUAL KDK semantics, Darwin-26 exclusion, KDK merge, KC/snapshot behavior, Modern Wireless/Audio dictionaries or payloads, PCI IDs, EFI, DeviceProperties, ACPI, DMAR, or AppleVTD.

Phase 4 is closed. No further Phase-4 functional development is required. Phase 5 — Intel Modern Wi-Fi Integration — has not begun and must start later from the frozen final Phase-4 state.
