# Phase 2A Dependency Selection

## Policy

`requirements.txt` now documents the ten intentional direct dependencies. `requirements-lock.txt` is the release input and contains all 22 direct and transitive distributions at exact versions, with exactly one accepted official PyPI wheel hash per distribution. Release installation uses `--only-binary=:all:` and `--require-hashes`; no sdist, alternate index, mirror, proxy, fork or unbounded hash set is accepted.

The previously inherited effective environment was not reproducibly recoverable: its requirements named packages without versions or hashes. The only authoritative artifact-level recoveries were Python 3.14.3 and PyInstaller 6.18.0. Other old global-site versions were treated as non-authoritative and were not frozen.

## Direct dependencies

| Distribution | Selected | Role / source consumer | Runtime or build | Selection rationale |
|---|---:|---|---|---|
| requests | 2.32.5 | network handler, KDK/Metallib/update/catalog paths | runtime | current compatible stable API; exact universal wheel |
| pyobjc-framework-Cocoa | 12.1 | Cocoa/AppKit GUI and Foundation/IOKit bridging | runtime | minimum required framework surface, not the broad mutable `pyobjc` meta-package; CPython 3.14 wheel |
| wxPython | 4.2.5 | all wx GUI modules and auto-patcher UI | runtime | official CPython 3.14 macOS 14 x86_64 wheel; avoids a source build |
| PyInstaller | 6.18.0 | application bundle generator | build | matches the known built-app TOC and supports Python 3.14 |
| packaging | 26.0 | OS/KDK/Metallib/update version comparison | runtime | compatible public API used by this tree |
| py-sip-xnu | 1.0.4 | SIP inspection and patchset validation | runtime | exact compatible release used by source imports |
| py-applescript | 1.0.3 | logging, GUI support and DMG mount AppleScript bridge | runtime | supplies the required `applescript.AppleScript` API; the unrelated `applescript` package is excluded |
| markdown2 | 2.5.4 | changelog rendering in GUI/auto patcher | runtime | compatible public API |
| macos-pkg-builder | 2.3.0 | unsigned/local package generation and formal package signing wrapper | build | current compatible package API |
| mac-signing-buddy | 1.0.0 | configured Developer-ID signing/notarization path | build | exact authenticated release; formal signing behavior unchanged |

## Transitive dependencies

| Distribution | Selected | Introduced by / purpose |
|---|---:|---|
| altgraph | 0.17.5 | PyInstaller graph analysis |
| certifi | 2026.1.4 | requests trust store |
| charset-normalizer | 3.4.4 | requests decoding; CPython 3.14 universal2 wheel |
| idna | 3.11 | requests URL handling |
| Markdown | 3.10.2 | macos-pkg-builder rendering dependency |
| macholib | 1.16.4 | PyInstaller/macOS Mach-O analysis |
| pyinstaller-hooks-contrib | 2026.0 | PyInstaller hooks |
| pyobjc-core | 12.1 | PyObjC runtime core |
| pyobjc-framework-AppleScriptKit | 12.1 | py-applescript bridge dependency |
| pyobjc-framework-AppleScriptObjC | 12.1 | py-applescript bridge dependency |
| setuptools | 82.0.0 | PyInstaller runtime/build dependency |
| urllib3 | 2.6.3 | requests HTTP transport |

Dependency resolution under CPython 3.14 does not select numpy or typing-extensions for wxPython. `pip check` passed in both fresh environments. Imports of requests, wx, Cocoa/Foundation/objc, packaging, py_sip_xnu, applescript, markdown2, PyInstaller, macos_pkg_builder and mac_signing_buddy all passed.

## Packaging inclusion boundary

Runtime dependencies found in the PyInstaller archive/bundle match the lock. Build-only PyInstaller, macos-pkg-builder, mac-signing-buddy and Markdown are not shipped as ordinary application modules. Setuptools material appears only where PyInstaller intentionally collects a runtime hook/vendor subset. That is an expected inclusion, not an undeclared environment.
