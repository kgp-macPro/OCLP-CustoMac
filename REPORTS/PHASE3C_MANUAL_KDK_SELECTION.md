# Phase 3C Manual KDK Selection

Artifact source implementation HEAD: `5e2c95f2897783b53ecdd84400550364a0c34ee5`

## Result

Phase 3C adds an operation-scoped **Manually select Kernel Debug Kit** control directly below the Modern Wi-Fi and Modern Audio controls on the main Root Patching screen. It is OFF by default and is enabled only when the requirements aggregated from the final selected patchsets say a KDK is required.

The corrected Phase-3B selection contract is unchanged:

| Wi-Fi | Audio | KDK required by these patchsets | Manual control |
|---:|---:|---:|---|
| ON | ON | yes, from Modern Audio | enabled, OFF by default |
| OFF | ON | yes, from Modern Audio | enabled, OFF by default |
| ON | OFF | no | disabled and cleared |
| OFF | OFF | no operation | disabled and cleared |

If the KDK requirement disappears, manual mode and its pending candidate are immediately cleared. Restoring the requirement makes the control available again but leaves it OFF. No manual state is written to global preferences, EFI, NVRAM, config.plist, or installed patch-selection metadata.

## Selection-only modal flow

The manual dialog and confirmation dialog only select one exact catalog candidate. They contain no downloader, installer, validation, merge, root-patching, KC or snapshot implementation.

1. The Root Patching page revalidates patch selection, Phase-2 root state, patch permission and KDK requirement.
2. The dialog lists eligible official Tahoe candidates and previews the existing OCLP automatic choice.
3. **Use This KDK** closes the native confirmation modal and the selection modal.
4. Catalog identity is revalidated before the Root Selection page is dismissed.
5. The existing Root Patching progress frame revalidates again before support-payload or KDK activity.
6. An installed exact candidate is reused. A non-installed exact candidate enters the existing standard OCLP KDK download GUI, checksum validation, installation and merge workflow.

Cancel from confirmation returns to the candidate list. Cancel from the candidate list returns to Root Patch Selection. Neither path starts KDK or root-patch work, and neither silently changes to AUTO mode.

## Trusted provenance and filtering

The candidate source is the existing OCLP `KernelDebugKitObject` catalog provider:

`https://dortania.github.io/KdkSupportPkg/manifest.json`

No second database, hard-coded KDK list, arbitrary URL entry, mirror, or user package path was added. Eligible candidates must declare macOS 26 and Darwin-build major 25. Product version is displayed only from catalog metadata.

## Automatic-choice preview

The dialog calls the existing `KernelDebugKitObject._get_latest_kdk()` resolver in passive, installed-ignoring preview mode against the same cached trusted catalog. It displays version, build, Exact Match or Closest Match, and Installed or Not Installed, and marks the same list row **OCLP Automatic Choice**. Previewing calls no `retrieve_download`, KDK install, mount, authentication, or patch operation.

The automatic choice is informational. A user may choose another eligible official Tahoe KDK. Once confirmed, the manual candidate wins and no fallback to the displayed automatic choice is permitted.

## Build artifact

- Clean implementation HEAD: `5e2c95f2897783b53ecdd84400550364a0c34ee5`
- Package SHA-256: `7b7539a14200af369237de5787c47531b2ac583f75afe5cf15103e6fd3d3bbec`
- Embedded Python: CPython 3.14.3, x86_64
- Dependency lock SHA-256: `be3082246b9d559c766dbda3eac4bb5bc1766bd85cc76756953d06b042d152a0`
- Built app strict/deep ad-hoc verification: PASS
- Package-expanded app strict/deep ad-hoc verification: PASS
- Built/package-expanded app content: identical 110 regular files and 33 symlink targets; package expansion changes directory mtimes only

The package is a test artifact and was not installed or runtime tested by Codex.
