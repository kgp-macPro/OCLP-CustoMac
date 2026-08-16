# Pre-publication OCLP-CustoMac branding inventory

Audit date: 2026-08-15
Repository: `/Users/kgp/Developer/OCLP-amfipassbeta-v2.0-development`
Audited HEAD: `cf77e6f7e4307154aafe856f81b174f9bee6466f`
Proposed user-facing brand: **OCLP-CustoMac**

## Executive recommendation

Use a deliberately split identity:

- **user-visible product/UI name:** `OCLP-CustoMac`;
- **technical application/package identity:** retain `OpenCore-Patcher.app`, `OpenCore-Patcher`, existing bundle/package/helper/launch-service identifiers, install paths, preference domains, and root-patch metadata/lifecycle filenames.

The smallest safe branding boundary is therefore text and display metadata, not a filesystem/identifier migration. `constants.patcher_name`, the hard-coded GUI strings, package titles/welcome text, and the app's `CFBundleName` can present OCLP-CustoMac. Renaming the executable, app bundle path, bundle ID, helper, package IDs, launch services, settings domains, root metadata, lifecycle records, or build identity would create compatibility and recovery risks without improving the visible brand.

Repository/update/support URLs are a separate publication decision. They must point to the final public infrastructure before enabling updates, but they should not be changed as a casual string-replacement exercise.

## Classification legend

- **A — safe user-visible branding:** expected to become OCLP-CustoMac.
- **B — technical identity / historical compatibility:** retain unchanged.
- **C — further coordinated decision:** may need a change for publication, but it affects distribution, provenance, licensing, update behavior, support, or migration.

## 1. User-visible application strings — A

| Surface | Current source | Recommended presentation |
|---|---|---|
| Central application display name | `constants.py:19`, `patcher_name = "OpenCore Legacy Patcher"` | `OCLP-CustoMac`; use this central constant wherever practical |
| wx application name and top-level frame title | `wx_gui/gui_entry.py:51,81` | Naturally follows `patcher_name`; retain version formatting; decide separately whether public builds still say Nightly |
| Main-menu heading | `wx_gui/gui_main_menu.py:80` | Replace hard-coded text with the central display name |
| About menu item | `wx_gui/gui_support.py:66` | `About OCLP-CustoMac` |
| About window heading | `wx_gui/gui_about.py:34` | `OCLP-CustoMac`; retain upstream credits/licensing |
| Error/log dialog titles and banner | `support/logging_handler.py:169,205,214` | Use the public display name; log filename can remain technical |
| Auto-patcher windows/dialog prose | `sys_patch/auto_patcher/start.py:73,95-96,167,172,231,306` | User-visible product name can change; do not alter behavior |
| OS-update caching dialog | `wx_gui/gui_cache_os_update.py:207,247,249` | User-visible product name can change |
| Main-menu update notices | `wx_gui/gui_main_menu.py:231,344-345` | User-visible name can change after updater source is resolved |
| Update failure prose | `wx_gui/gui_update.py:119,233` | User-visible name can change; package filename reference remains `OpenCore-Patcher.pkg` |
| PyInstaller display metadata | `OpenCore-Patcher-GUI.spec:85`, `CFBundleName` | Set display name to `OCLP-CustoMac`; keep bundle file/executable/identifier unchanged |
| Installer package title | `ci_tooling/build_modules/package.py:100,123` | `OCLP-CustoMac Uninstaller` / `OCLP-CustoMac` are safe display titles |
| Installer welcome/uninstaller prose | `ci_tooling/build_modules/package.py:39-43,61-65,78-79` | Present OCLP-CustoMac while retaining exact technical paths/package names where shown |
| Generated package-script comments | `ci_tooling/build_modules/package_scripts.py:360,415,480,482` | Cosmetic; may follow public brand, with no path/logic change |
| Build CLI description | `Build-Project.command:27` | Safe developer-facing rename if desired |
| Analytics application label | `support/analytics_handler.py:53` | Currently no endpoint/key is configured. If analytics remains disabled, cosmetic; if enabled later, coordinate schema/privacy first (otherwise category C) |

The app's generic page/dialog titles are mostly inherited from `gui_entry.py` through `self.title`; changing the central display name covers those without renaming technical files.

### Current hard-coded user-visible locations

The tracked runtime source locations containing the literal `OpenCore Legacy Patcher`, outside historical reports/docs, are:

- `opencore_legacy_patcher/constants.py`;
- `opencore_legacy_patcher/wx_gui/gui_entry.py` through `patcher_name`;
- `opencore_legacy_patcher/wx_gui/gui_main_menu.py`;
- `opencore_legacy_patcher/wx_gui/gui_about.py`;
- `opencore_legacy_patcher/wx_gui/gui_support.py`;
- `opencore_legacy_patcher/wx_gui/gui_cache_os_update.py`;
- `opencore_legacy_patcher/wx_gui/gui_update.py`;
- `opencore_legacy_patcher/sys_patch/auto_patcher/start.py`;
- `opencore_legacy_patcher/support/logging_handler.py`;
- `opencore_legacy_patcher/support/analytics_handler.py`;
- `ci_tooling/build_modules/package.py` and `package_scripts.py`;
- `OpenCore-Patcher-GUI.spec`;
- `Build-Project.command`.

Other hits in module docstrings/comments are source attribution rather than product UI and do not need mechanical replacement.

## 2. Technical identities to preserve — B

### Application and executable

| Identity | Locations | Reason to retain |
|---|---|---|
| `OpenCore-Patcher.app` | `OpenCore-Patcher-GUI.spec`, `ci_tooling/build_modules/application.py`, `package.py`, `package_scripts.py`, launch-service plists, updater, docs/workflows | Installed path, shim, launch services, updater, helper interaction, and packaging all assume this filename |
| `Contents/MacOS/OpenCore-Patcher` | PyInstaller spec, `application.py`, package scripts, launch plists, updater | Executable/path compatibility |
| `OpenCore-Patcher-GUI.command` | PyInstaller analysis, validation workflows, source instructions, application source-mode logic | Build/CLI entry-point compatibility |
| `OpenCore-Patcher.pkg`, `OpenCore-Patcher-Uninstaller.pkg`, `AutoPkg-Assets.pkg` | workflows, package builder, updater, manifests | Update asset discovery and established artifact compatibility |
| `OpenCore-Patcher` log prefix | `support/logging_handler.py:50,103` | Existing log discovery/cleanup; visible banner can still use new brand |

### Bundle, package, helper, and launch-service identifiers

Retain:

- main app bundle ID `com.dortania.opencore-legacy-patcher` (`OpenCore-Patcher-GUI.spec:83`);
- package IDs `com.dortania.opencore-legacy-patcher`, `com.dortania.opencore-legacy-patcher-uninstaller`, and `com.dortania.pkg.AutoPkg-Assets` (`package.py`);
- privileged helper name/path `com.dortania.opencore-legacy-patcher.privileged-helper` (`subprocess_wrapper.py`, helper Makefile/install script, package scripts);
- helper shim bundle ID `com.dortania.opencore-legacy-patcher-helper` (`payloads/Tools/OpenCore-Patcher.app/Contents/Info.plist`);
- launch labels and filenames:
  - `com.dortania.opencore-legacy-patcher.auto-patch`;
  - `com.dortania.opencore-legacy-patcher.macos-update`;
  - `com.dortania.opencore-legacy-patcher.os-caching`;
  - `com.dortania.opencore-legacy-patcher.rsr-monitor`;
- installed main path `/Library/Application Support/Dortania/OpenCore-Patcher.app`;
- shim path `/Applications/OpenCore-Patcher.app`;
- helper path `/Library/PrivilegedHelperTools/com.dortania.opencore-legacy-patcher.privileged-helper`.

These strings form a coupled install/update/uninstall/service graph. A broad rename would require a migration/uninstall strategy and would risk leaving duplicate helpers, launch jobs, or stale apps. It is outside a minimal branding phase.

### Preferences and persistent state

Retain:

- `/Users/Shared/.com.dortania.opencore-legacy-patcher.plist` and legacy `~/Library/Preferences/com.dortania.opencore-legacy-patcher.plist` (`support/global_settings.py`, package scripts, settings messages);
- root metadata `/System/Library/CoreServices/OpenCore-Legacy-Patcher.plist` (`sys_patch/root_state.py`);
- lifecycle `/Library/Application Support/Dortania/OpenCore-Legacy-Patcher-Lifecycle.plist` (`sys_patch/lifecycle.py`);
- metadata schemas `KGP-Root-Patch-State-v1` and `KGP-Root-Patch-Lifecycle-v1`;
- legacy metadata key `OpenCore Legacy Patcher` written/read by `sys_patch_helpers.py`, `root_state.py`, and `device_probe.py`;
- recognized foreign filenames (`OCLP-R.plist`, `OCLP-Plus.plist`, both Mod spellings) and compatibility logic.

These are data-format and recovery identities, not display branding. Renaming them would impair installed-state discovery and safe recovery from existing builds.

### Embedded OpenCore/payload labels and attributions

Occurrences inside `payloads/Config/config.plist`, the helper shim, existing kext/plist bundle identifiers, generated EFI comments, upstream source comments, LICENSE, and payload-source attribution are technical or legal provenance. They should not be globally replaced. In particular, never rewrite third-party `CFBundleIdentifier` values in payloads.

## 3. Items requiring a coordinated decision — C

### Project identity in installed metadata

`constants.project_identity` is currently:

`OCLP 3.0.0 Nightly - amfipassbeta Edition v2.0`

It is embedded in build metadata (`ci_tooling/build_modules/application.py:172`) and installed root-patch metadata (`sys_patch_helpers.py:116`). `root_state.py` uses it, together with repository identity and commit provenance, for strict **new-patch** classification and display history. Recovery no longer depends on matching ownership, but changing this value would intentionally classify prior installed operations as another project/build and force Revert -> reboot -> repatch.

Recommendation: do not change `project_identity` in the minimal UI-branding commit. If the first public branded build needs a new identity, treat that as an explicit one-time state migration decision with tests; do not conflate it with the visible name.

### Public repository, provenance, and updater

Current values are internally inconsistent for a public fork:

- canonical build provenance: `ci_tooling/build_metadata.py` points to `https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta`;
- current Git remote recorded in `DEVELOPMENT_BASELINE.md` is the same KGP repository;
- `constants.repo_link`, `support/updates.py`, main-menu update checks, auto-patcher update checks, and Settings nightly lookup still target Dortania upstream;
- `constants.installer_pkg_url_nightly`, `SOURCE.md`, and Settings target Dortania's nightly.link workflow;
- `constants.guide_link` targets Dortania upstream documentation;
- `constants.url_patcher_support_pkg` and `disk_images.py` target KGP's `PatcherSupportPkg-laobamac` releases.

Before publication, decide the authoritative OCLP-CustoMac repository, release asset names, update policy, documentation site, and whether automatic upstream update checks must be disabled or redirected. Redirect all operational update call sites together. Leaving an updater pointed at upstream could replace the branded/frozen build with an incompatible upstream package.

Operational updater locations:

- `opencore_legacy_patcher/constants.py:23-28`;
- `opencore_legacy_patcher/support/updates.py:18,98-124`;
- `opencore_legacy_patcher/wx_gui/gui_main_menu.py:327`;
- `opencore_legacy_patcher/sys_patch/auto_patcher/start.py:78,166`;
- `opencore_legacy_patcher/wx_gui/gui_settings.py:1342,1364`;
- `opencore_legacy_patcher/application_entry.py:107-113`;
- `opencore_legacy_patcher/wx_gui/gui_macos_installer_flash.py:417-423`.

PSP/KDK/Metallib catalog URLs are functional supply-chain sources, not branding:

- KGP `PatcherSupportPkg-laobamac` release URL;
- Dortania `KdkSupportPkg/manifest.json`;
- Dortania `MetallibSupportPkg/manifest.json`.

Retain them unless a separately audited supply-chain migration is approved.

### Support, privacy, and community links

`constants.discord_link`, `constants.guide_link`, `gui_help.py`, `PRIVACY.md`, README forum links, and upstream issue links need editorial review. Some upstream issue links are technical citations and should remain; product support links should point to the chosen OCLP-CustoMac support venue. Analytics is currently inert because its server and site key are empty, but privacy text still needs to accurately describe the public build.

### Nightly and edition labels

`Nightly` is currently generated whenever commit provenance is not a tag in `gui_entry.py`, `gui_main_menu.py`, auto-patcher update UI, and updater logic. The exact development identity `OCLP 3.0.0 Nightly - amfipassbeta Edition v2.0` also occurs in constants, build metadata, and state tests.

For a public release:

- user-visible `Nightly` treatment depends on release/tag policy;
- the historical/project identity must not be silently rewritten;
- test fixtures must continue describing the schema/identity they validate unless a deliberate migration is implemented.

### Icons and package backgrounds

The following binary/design assets may contain visual upstream branding and require visual/editorial review rather than string replacement:

- `payloads/Icon/AppIcons/OC-Patcher.icns` and related app icons/`Assets.car`;
- `ci_tooling/pkg_assets/PkgBackground-Installer.png`;
- `PkgBackground-Uninstaller.png`;
- `PkgBackground-AutoPkg.png`;
- `PkgBackground-Source-File.afdesign`.

Changing the icon is optional for the smallest safe text-branding boundary. If changed, preserve bundle filename and technical icon-resource wiring.

## 4. Documentation and repository occurrence inventory

### Product-facing documents to rewrite for publication — A/C

- `README.md`: current title is “OCLP 3.0.0 Nightly – amfipassbeta Edition for macOS Tahoe”; contains old repository history, forum links, KGP PSP link, contributor credits, and upstream attribution. Rewrite editorially, not mechanically; preserve credits and technical limitations.
- `SOURCE.md`: upstream project name, Dortania clone URL, nightly download link, and technical filenames. Brand prose may change; command/artifact filenames should remain.
- `PRIVACY.md`: upstream product name, preferences domain, Discord contact. Brand prose/support contact may change; preference domain remains technical.
- `.github/ISSUE_TEMPLATE/bug_report.yml`: upstream issue URL and support expectations need publication-repository review.
- `docs/.vuepress/config.js`, `docs/package.json`, and user-facing files under `docs/`: upstream title, repository, issue, guide, and project strings need an editorial decision if this documentation is published as OCLP-CustoMac.

### Historical/provenance documents to preserve — B

- `CHANGELOG.md` is inherited history. Add branded entries prospectively; do not rewrite historical release names/paths.
- `LICENSE.txt` and `docs/LICENSE.md` must retain upstream attribution and license wording.
- `DEVELOPMENT_BASELINE.md`, `MANIFESTS/**`, `REPORTS/**`, and previous build evidence intentionally record historical names, repositories, filenames, package hashes, and project identities. Do not mass-rename them.
- Existing tests whose fixtures contain the KGP project/repository identity validate state compatibility. Update only if a separately designed identity migration changes the contract.

### Complete tracked-file groups containing the key names

At this audit HEAD, excluding historical `REPORTS/**`, the literal terms occur in these groups:

- `OpenCore Legacy Patcher`: root `Build-Project.command`, `CHANGELOG.md`, `LICENSE.txt`, `PRIVACY.md`, `README.md`, `SOURCE.md`; build/package/helper sources; user documentation under `docs/`; runtime files `application_entry.py`, `constants.py`, `device_probe.py`, `analytics_handler.py`, `logging_handler.py`, `updates.py`, `utilities.py`, auto-patcher, `detect.py`, `root_state.py`, `sys_patch_helpers.py`, `dmg_mount.py`, and the listed GUI files; historical/source comments and tests.
- `OpenCore-Patcher`: workflows, `.gitignore`, build command/spec, source/changelog/manifests, application/package scripts, helper docs, install/update/log/commit-info code, launch-service plists, helper shim Info.plist, and `payloads/Config/config.plist`.
- `OCLP`: README/development/manifests/changelog, build metadata, broad inherited source comments and symbols, docs, patch-state/KDK/GUI code, config, and tests. Most are technical abbreviations or historical provenance, not UI labels.
- `Nightly`: README/SOURCE/changelog, issue template, constants/build metadata, application/update GUI, settings, auto-patcher, and identity tests.
- `amfipassbeta`: README/development baseline, canonical build metadata, constants/project identity, the required EFI boot-argument code/test, build Info.plist metadata, and state fixture tests. The boot argument `-amfipassbeta` is functional and must never be renamed as branding.

This grouped inventory covers all tracked hits found by exact case-insensitive searches at the audited HEAD. Occurrences in generated `WORK/**`, prior artifacts, reports, manifests, and Git history are evidence and must remain untouched.

## 5. Smallest safe implementation boundary for a later branding phase

The future minimal branding change should:

1. Change `constants.patcher_name` to `OCLP-CustoMac`.
2. Replace the few runtime GUI hard-codes with `patcher_name` (main menu, About/menu, error/auto-update/cache dialogs) without changing control flow.
3. Set PyInstaller `CFBundleName` to `OCLP-CustoMac` while retaining the bundle filename and ID.
4. Change Installer/Uninstaller **display titles and prose** while retaining output filenames, package IDs, payload paths, helper IDs, and script logic.
5. Decide updater/repository/guide/support targets as a separate, explicit publication configuration and regression-test that the app cannot install upstream OCLP accidentally.
6. Rewrite README/public docs prospectively while preserving licenses, credits, technical filenames, frozen evidence, and historical reports.
7. Leave `project_identity`, preferences, root metadata, lifecycle, bundle/package/helper/launch identifiers, and `-amfipassbeta` unchanged unless a separate migration is designed.

This produces a visible OCLP-CustoMac application without destabilizing installation, updates, state classification, Revert recovery, launch services, or existing user data.

## 6. Direct branding answer

The smallest safe branding change is a **display-name overlay**: show `OCLP-CustoMac` in wx application/window/menu/About/installer text and `CFBundleName`, but continue shipping the technical `OpenCore-Patcher.app` / `OpenCore-Patcher.pkg` identity and all existing IDs/paths/state filenames. Repository and update endpoints must be decided and changed coherently before publication; they are not safe blind-renaming targets.

## Audit integrity

No branding, source, identifiers, paths, URLs, documentation outside these audit reports, build artifacts, or installed system state were changed during this audit.
