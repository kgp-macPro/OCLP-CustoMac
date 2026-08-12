# Phase 2A Build Environment Audit

## Result

Phase 2A resolves the Python dependency mutability defect for the v2.0 application source line. The build now requires an authenticated CPython 3.14.3 framework artifact, a fresh isolated venv, pip 25.3, `PYTHONHASHSEED=0`, exact direct/transitive versions, and one SHA-256-pinned official PyPI wheel per package. Two independent offline reconstructions and two clean application builds passed.

No global Python, Homebrew/MacPorts environment, user site-packages, Keychain, certificate store or shell startup file was changed. No sudo or installation was used.

## Inventory of the inherited build path

Inspected inputs included `requirements.txt`, all workflows, `Build-Project.command`, `OpenCore-Patcher-GUI.spec`, `ci_tooling/build_modules/`, package/signing modules, the committed `dist/OpenCore-Patcher.app`, its Info.plist, framework/runtime Mach-Os, PyInstaller TOCs and package resources. No `pyproject.toml` or separate constraints/lock file existed.

The inherited defect was concrete:

- ten unversioned direct names in `requirements.txt`;
- Python 3.11 hard-coded in workflows;
- a committed app containing Python.framework 3.14.3 and PyInstaller 6.18.0 evidence;
- no transitive lock or artifact hashes;
- mutable package-index resolution;
- a wall-clock local Build Date;
- an outer application signature invalidated after PyInstaller by later Info.plist/resource mutations.

## Implemented build policy

- `.python-version` pins 3.14.3.
- `requirements.txt` is an exact, human-maintained direct declaration.
- `requirements-lock.txt` pins all 22 distributions and one wheel hash each.
- `ci_tooling.build_environment` validates interpreter, framework binary, architecture, isolated venv, pip, hash seed, lock integrity, exact installed set and absence of extra distributions.
- `Build-Project.command` invokes the verifier before any build action.
- release workflow uses the pinned official framework path and a local venv; validation workflows use exact 3.14.3/x64 plus the same lock.
- all pip installs use the official PyPI simple endpoint, only wheels and hash checking.
- `SOURCE_DATE_EPOCH` replaces the wall clock in application Build Date generation and the local “Built from source” Commit Date fallback. Explicit release metadata still takes precedence.
- `PYTHONHASHSEED=0` removes nondeterministic `base_library.zip` member ordering.
- the final application-generation step refreshes only the outer ad-hoc seal after all local mutations.

## Supply-chain identities

| Layer | Identity |
|---|---|
| Interpreter | official Python.org CPython 3.14.3 macOS universal2; installed framework SHA-256 `131f5211...4360f` |
| Interpreter installer | `python-3.14.3-macos11.pkg`, SHA-256 `50b709f7...8238` |
| Bootstrap | CPython ensurepip pip 25.3; no global upgrade |
| Direct dependencies | ten exact versions in `requirements.txt` |
| Transitive dependencies | twelve exact versions in `requirements-lock.txt` |
| Package artifacts | 22 official PyPI wheels, one accepted SHA-256 each |
| Local cache | ignored `WORK/PHASE2A_ENV/WHEELHOUSE`; verified against the committed lock/manifest |
| Source base | Phase-1 HEAD `6fcf12f0bd4d4717ab9e7ad50db1926ea4537a57` plus the Phase-2A tree; final local commit recorded in handoff |
| App tree identity | canonical file-manifest SHA-256 `7466eb4039bd698ba2aff5f3f9f12c29359eb7b9535c404b9666594345e98985` for both builds |
| Package identity | three unsigned local packages recorded in the artifact manifest |

## PRE-EXISTING LOCAL-BUILD SIGNATURE-FINALIZATION DEFECT

PyInstaller ad-hoc signed the app before `GenerateApplication` mutated Info.plist and resources. The disposable raw bundle therefore failed strict/deep verification with a modified/invalid Info.plist seal. This predates Phase 1 and was not caused by component refreshes.

The approved remediation is the smallest finalization step:

```text
/usr/bin/codesign --force --sign - --timestamp=none OpenCore-Patcher.app
```

No `--deep` repair is used. The test proved that only the outer main executable's signature bytes and outer `_CodeSignature/CodeResources` changed. Info.plist, every Resources file and all 79 nested Mach-O hashes/signatures remained identical. The identifier remained `com.dortania.opencore-legacy-patcher`; both before and after were ad hoc, had no Team ID, no entitlements and no timestamp. The final bundle passes `codesign --verify --strict --deep`.

Formal Developer-ID/release signing remains the subsequent, separately configured existing step. It was not invoked or redesigned.

## Remaining external/non-deterministic boundaries

- GitHub Action implementation tags (`checkout@v4`, `setup-python@v5`, upload actions) remain mutable major tags.
- GitHub-hosted runner patch images and the self-hosted `x86_64_monterey` machine remain external. Artifact builds fail if the pinned Python framework is not provisioned exactly.
- `BuildMachineOSBuild` intentionally records the runner OS build; identical bytes across different macOS patch builds are not claimed.
- the two application builds reused identical, previously verified `payloads.dmg` and `Universal-Binaries.dmg` inputs. Regenerating HFS/DMG containers and reacquiring PSP assets is a separate supply-chain boundary.
- formal Developer-ID signing/notarization and package container timestamps are credential/service-dependent and were not claimed reproducible.

Within the declared boundary—same source tree/epoch, exact interpreter, locked wheelhouse, runner OS build and fixed DMG inputs—the unsigned/ad-hoc application is byte-identical.

## Phase-1 and immutable-workspace gate

The production repository remains on `main` at `ec5e591e0f46e948b0258ef1c8ed5d17d6a2c865`, clean, with its original `origin` and exact baseline non-`.git` content aggregate `950e0ce58181cdae18956e37866cde7fcf0ffa602c4f2fbe85d30fffae92f2be`. The development repository remained remote-free throughout.

All 52 existing files authenticated by the Plus/Mod final SHA-256 manifest still verify. No completed-audit content has a post-Phase-1 modification time. One Git read caused only the directory mtime of `OCLP-Plus-Mod-evaluation-audit/REFERENCES/Dortania-OCLP/.git` to refresh at 19:11:36; no child file, Git object, index content, report, manifest or source content changed. It is disclosed as a read-side metadata effect and was not “repaired,” because changing prior-audit metadata is prohibited.

Phase-1 component hashes, the six boot-argument tests and the prohibited-path diff gate all pass. The Phase-2A diff contains no EFI builder, root-patch, detection, constants, payload, KDK, SIP, ACPI, DMAR, DeviceProperties or AppleVTD change.
