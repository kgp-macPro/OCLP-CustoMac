# Phase 2A Application Build Validation

## Application

The statically validated disposable artifact is:

`WORK/PHASE2A_FINAL_BUILD/ARTIFACTS/PASS2/OpenCore-Patcher.app`

It was not launched or installed.

| Property | Result |
|---|---|
| Bundle identifier | `com.dortania.opencore-legacy-patcher` |
| Bundle version | 3.0.0 |
| Main architecture | x86_64 |
| Embedded Python | Python.framework 3.14.3, x86_64 |
| Embedded Python SHA-256 | `c0ac658c1f1f024b3019509e2af50c0eda69b311d5f8d511160a0e4110b42a71` |
| Build Date | `2026-08-12 16:43:46 UTC` (SOURCE_DATE_EPOCH) |
| Git metadata | `Built from source`, empty Commit URL; BuildIdentity is explicitly deferred |
| Outer signature | ad hoc, timestamp-free, no Team ID, no entitlements |
| Strict/deep verification | pass |
| App canonical tree digest | `7466eb4039bd698ba2aff5f3f9f12c29359eb7b9535c404b9666594345e98985` |

PyInstaller recursive-archive inspection found the expected runtime package set. Expected build-only exclusions are documented in the dependency report. No unexpected library family was found.

## Phase-1 payload identities

The application carries the unchanged Phase-1 inputs:

| Input | SHA-256 / status |
|---|---|
| `payloads.dmg` | `22581d0a9981f583d1921ca447bb0d578b3c39b20a805c5c6bac4ab5678d6f98` |
| `Universal-Binaries.dmg` | `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4` |
| AMFIPass 1.4.1 slim archive | `07b266145906db41f4b13a7938fbb173ea28888cc1fa65f84417f8820adc961e` |
| AppleALC 1.9.7 slim archive | `79680e6dba45c6866d6b32c8821fad584542e4414122cc440a48bfe561aaad4a` |
| IO80211FamilyLegacy archive | `e681dcc76a2cd2cea4b0ad5f27a3c816055fde3cdccd890dd10a3e2c84e96d93` |
| IOSkywalkFamily archive | `1e12b7ef42f55b39ea54ada97b46331220668b2c48a28656e9875c5145fe2479` |

No Phase-1 component archive/version changed. No patch dictionary, KDK, SIP, ACPI, DMAR, DeviceProperties, AppleVTD or root-patch destination source changed. The only application-source change is build finalization; the only other changes are dependency/build infrastructure.

The Phase-1 boot-argument suite confirms no automatic global `-lilubetaall`, preservation of explicitly supplied `-lilubetaall`, and exactly one `-amfipassbeta` when AMFIPass is enabled. AMFIPass remains 1.4.1.

## Static local packages

Package generation used the locked venv and required no privilege. Packages were not installed and package scripts were not executed. Read-only expansion proved that the packaged application file manifest exactly matches the validated Pass-2 application.

| Package | SHA-256 | Signature |
|---|---|---|
| `OpenCore-Patcher.pkg` | `734e3d2443d2d206a0d08dcf787c7875cf426183907a4d76a442491d67a382d4` | unsigned local |
| `OpenCore-Patcher-Uninstaller.pkg` | `72c1f77d22cbccdddfc35f7478f7edc7e676b220f0e8f07a88a9d27f637a0e97` | unsigned local |
| `AutoPkg-Assets.pkg` | `991e4e9ab90e767d9abde1b071e0a113c3b8b9e0a1850e1abed4bc90a4ac34a8` | unsigned local |

The package containers were generated once and are not claimed byte-reproducible. Formal signing/notarization remains unchanged and untested because it requires external credentials/services.
