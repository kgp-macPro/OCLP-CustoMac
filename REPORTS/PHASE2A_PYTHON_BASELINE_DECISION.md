# Phase 2A Python Baseline Decision

## Decision

The v2.0 application artifact baseline is **CPython 3.14.3, official Python.org macOS universal2 framework, built as x86_64**.

| Identity | Pinned value |
|---|---|
| Python | CPython 3.14.3 |
| Build architecture | x86_64 |
| Framework | `Python` |
| Interpreter path used locally | `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` |
| Official installer | `python-3.14.3-macos11.pkg` |
| Official installer SHA-256 | `50b709f72cb5ed87d5882901923face981dd657569717761832c36db3bf08238` |
| Installed universal2 framework binary SHA-256 | `131f5211d7a7ec6279abcc2e4b0b97f8559d8eb77d5a28c22771f9ced084360f` |
| Python publisher identifier | `org.python.python`, Team ID `BMM5U3QVKW` |
| venv bootstrap pip | 25.3 |
| `PYTHONHASHSEED` | `0` |

The release page is `https://www.python.org/downloads/release/python-3143/`. Python.org records a 2026-02-03 release date and the installer digest above.

## Available local interpreters

| Executable | Version | Process architecture | Framework | pip | Clean venv |
|---|---:|---|---|---:|---|
| `/usr/bin/python3` (Xcode shim target) | 3.9.6 | x86_64 | `Python3` | 21.2.4 | yes |
| `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` | 3.13.12 | x86_64 | `Python` | 25.3 | yes |
| `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` | 3.14.3 | x86_64 | `Python` | 26.0.1 globally; 25.3 from a fresh venv | yes |

No interpreter was installed or altered. The selected interpreter was already present. The project venv did not inherit global site-packages.

## Evidence-based selection

The previous workflow's Python 3.11 reference was not selected because it was an unverified historical path and did not match the committed application evidence. Python 3.13.12 was compatible with much of the source but would introduce an unnecessary ABI change from the known application build. Python 3.9.6 cannot consume the selected current wxPython/PyObjC stack.

The committed Phase-1 application was inspected as evidence and embeds Python.framework 3.14.3 with an x86_64 runtime. Its PyInstaller TOCs also identify PyInstaller 6.18.0. Fresh official PyPI wheels exist for every selected dependency on CPython 3.14/x86_64, including wxPython 4.2.5 and PyObjC 12.1. Two clean locked builds reproduced the same x86_64 application and embedded Python 3.14.3 bytes.

The choice is therefore source-line compatibility driven, not a generic choice of the newest Python. Python 3.14.3 has since been superseded upstream, but v2.0 deliberately pins the demonstrated patch release.

## Enforcement and residual boundary

Artifact builds fail closed unless the exact version, implementation, architecture, framework identity, framework-binary SHA-256, pip version, hash seed and locked distribution set all match. Non-artifact validation workflows use exact Python 3.14.3/x64 from `actions/setup-python` and the same dependency lock, but intentionally use `--validation-only` because those workflows do not create release artifacts.

The build runner remains an external machine dependency: `x86_64_monterey` must already carry the authenticated official framework at the pinned path. No CI provisioning or global Python installation is performed by this phase.
