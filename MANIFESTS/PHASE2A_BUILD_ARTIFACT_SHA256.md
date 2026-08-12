# Phase 2A Build Artifact SHA-256

All paths are relative to the development repository. WORK artifacts are deliberately ignored and are not committed.

## Reproducible application builds

| Artifact / identity | Pass 1 | Pass 2 |
|---|---|---|
| App path | `WORK/PHASE2A_FINAL_BUILD/ARTIFACTS/PASS1/OpenCore-Patcher.app` | `WORK/PHASE2A_FINAL_BUILD/ARTIFACTS/PASS2/OpenCore-Patcher.app` |
| Canonical file-manifest SHA-256 | `7466eb4039bd698ba2aff5f3f9f12c29359eb7b9535c404b9666594345e98985` | `7466eb4039bd698ba2aff5f3f9f12c29359eb7b9535c404b9666594345e98985` |
| `Contents/MacOS/OpenCore-Patcher` | `12b87a8558384fd06a24a97b8f5ab00562425c7e8a5acbc4f70bc0a1b2a38db1` | same |
| `Contents/Info.plist` | `5a2c2feffc633552e85803de7520d56d1997aad7171a893ad8957e0b2c1eca3b` | same |
| Embedded `Python.framework/.../Python` | `c0ac658c1f1f024b3019509e2af50c0eda69b311d5f8d511160a0e4110b42a71` | same |
| `Contents/Resources/base_library.zip` | `c0664ce2530851fb0ca10a429dfb001ab050d3022d3004707cb633e704bdb9f5` | same |
| Outer `CodeResources` | `feadfdf6cad9f5c05dc643d205055d0e1dfc5fea37aeefb14df55c7141e8ac80` | same |
| `Contents/Resources/payloads.dmg` | `22581d0a9981f583d1921ca447bb0d578b3c39b20a805c5c6bac4ab5678d6f98` | same |
| `Contents/Resources/Universal-Binaries.dmg` | `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4` | same |

The canonical file manifests, mode manifests and symlink manifests compare byte-for-byte. Both bundles pass `codesign --verify --strict --deep`.

## Static local packages

| Path | SHA-256 |
|---|---|
| `WORK/PHASE2A_FINAL_BUILD/SOURCE/dist/OpenCore-Patcher.pkg` | `734e3d2443d2d206a0d08dcf787c7875cf426183907a4d76a442491d67a382d4` |
| `WORK/PHASE2A_FINAL_BUILD/SOURCE/dist/OpenCore-Patcher-Uninstaller.pkg` | `72c1f77d22cbccdddfc35f7478f7edc7e676b220f0e8f07a88a9d27f637a0e97` |
| `WORK/PHASE2A_FINAL_BUILD/SOURCE/dist/AutoPkg-Assets.pkg` | `991e4e9ab90e767d9abde1b071e0a113c3b8b9e0a1850e1abed4bc90a4ac34a8` |

These are unsigned local package containers. They were generated and expanded for static inspection only and were not installed. Container-level reproducibility was not claimed.
