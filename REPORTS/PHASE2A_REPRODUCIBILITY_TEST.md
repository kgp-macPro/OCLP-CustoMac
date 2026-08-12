# Phase 2A Reproducibility Test

## Environment reconstruction

Two venvs were independently created under ignored `WORK/PHASE2A_ENV`. Pass 1 acquired the exact official PyPI wheels and installed the hash lock. Pass 2 was destroyed/recreated and installed with `--no-index --find-links ... --require-hashes --only-binary=:all:` from the verified wheelhouse. No global site-packages were inherited.

Both normalized manifests are byte-identical, SHA-256 `5249b8738a259625bb1be52ba6f728e892acb4fc8d10b1a3c1d42fb0d9841d31`. Each reports CPython 3.14.3, x86_64, the official framework-binary hash, pip 25.3, `PYTHONHASHSEED=0`, lock SHA-256 `be308224...52a0`, and the same 22 distributions. `pip check` passed twice.

## Clean application builds

Both builds used:

```text
PYTHONHASHSEED=0
SOURCE_DATE_EPOCH=1786553026
fresh venv
fresh PyInstaller cache
same verified payloads.dmg and Universal-Binaries.dmg inputs
python Build-Project.command --run-as-individual-steps --reset-pyinstaller-cache --prepare-application
```

Each run completed all post-PyInstaller mutations and then performed the outer-only, timestamp-free ad-hoc seal. File hashes, modes and symlink targets were separately normalized and compared.

## Result

Classification: **A — byte-identical** within the declared build boundary.

| Comparison | Pass 1 | Pass 2 | Result |
|---|---|---|---|
| Canonical file-manifest SHA-256 | `7466eb4039bd698ba2aff5f3f9f12c29359eb7b9535c404b9666594345e98985` | same | identical |
| Symlink manifest | identical | identical | identical |
| Mode manifest | identical | identical | identical |
| Main executable SHA-256 | `12b87a8558384fd06a24a97b8f5ab00562425c7e8a5acbc4f70bc0a1b2a38db1` | same | identical |
| Embedded Python binary | `c0ac658c1f1f024b3019509e2af50c0eda69b311d5f8d511160a0e4110b42a71` | same | identical |
| `base_library.zip` | `c0664ce2530851fb0ca10a429dfb001ab050d3022d3004707cb633e704bdb9f5` | same | identical |
| Info.plist | `5a2c2feffc633552e85803de7520d56d1997aad7171a893ad8957e0b2c1eca3b` | same | identical |
| Outer CodeResources | `feadfdf6cad9f5c05dc643d205055d0e1dfc5fea37aeefb14df55c7141e8ac80` | same | identical |
| strict/deep codesign | pass | pass | identical validity |

An exploratory pair before enforcing `PYTHONHASHSEED` differed only in the order of otherwise byte-identical `.pyc` members in `base_library.zip`; all 155 member contents and their fixed timestamps matched. Rebuilding with `PYTHONHASHSEED=0` removed the difference at source. No archive post-processing is part of the committed solution.

## Outer signature experiment

Before outer refresh, strict/deep verification failed because later Info.plist/resource mutations invalidated PyInstaller's early ad-hoc seal. The raw outer CodeDirectory had SHA-256 CDHash `f9e22fec...fc888` and did not bind the final Info.plist. After outer-only sealing, the experiment CDHash became `81928424...840d5` and bound the final 18-entry Info.plist/135 resources.

Raw versus sealed comparison changed exactly:

- `Contents/MacOS/OpenCore-Patcher` (outer signature blob);
- `Contents/_CodeSignature/CodeResources` (outer resource envelope).

Unchanged: Info.plist, full Resources manifest, all nested Mach-Os/signatures, executable code before the signature region, bundle identifier, lack of entitlements, lack of Team ID and lack of timestamp. The two final clean builds then produced the same outer signature bytes.

## Universal validation disclosure

The focused Phase-1 boot-argument suite passes 6/6. A targeted `iMac19,1` EFI build succeeds and validates under both Phase 1 and Phase 2A. The inherited full `--validate` sweep exits at the same pre-existing `KeyError: 'iMac19,1'` after succeeding through `iMac18,3` in both the exact Phase-1 baseline copy and Phase 2A. The relevant builder source is byte-identical. This is a parity-confirmed inherited universal-validator defect, not a Phase-2A regression; fixing it is outside this phase.
