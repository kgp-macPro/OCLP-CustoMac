# Phase 3C KDK Resolver Parity

Artifact source implementation HEAD: `5e2c95f2897783b53ecdd84400550364a0c34ee5`

## AUTO mode

When no manual candidate is supplied, `KernelDebugKitObject` invokes the inherited `_get_latest_kdk()` path exactly as before. Exact host-build matching, existing closest-match ordering/range rules, installed-KDK discovery, download validation, installation, KDK merge, Boot/System KC and AuxiliaryKC behavior are unchanged.

Synthetic parity fixtures prove:

- exact catalog match selects the same exact KDK;
- an unavailable exact build selects the same inherited closest match;
- an installed exact KDK is reused;
- a missing catalog result retains existing AUTO failure behavior.

## MANUAL mode

A manual candidate is an immutable identity tuple of catalog version, build, URL and file size. The resolver requires an exact tuple match in the trusted catalog and does not call the exact/closest substitution algorithm.

- If the exact candidate is installed and valid, precisely that path is reused.
- If it is not installed, precisely that URL is handed to the existing `DownloadObject` and standard OCLP download GUI.
- The generated `KDKInfo.plist` records the selected version/build; merge preflight rejects a stale predownload whose identity differs.
- The selected identity is re-resolved at the Root Selection page, normal progress frame, operation layer and KDK merge boundary.
- If catalog lookup, download, checksum validation, installation or later identity validation fails, the operation stops. Another exact/closest/installed KDK is never substituted.
- If an installed selected KDK disappears and no already-validated exact predownload exists, the merge path fails instead of starting an invisible download or choosing another KDK.

The same existing downloader, checksum validator, package installer and KDK merge implementation remain downstream of both AUTO and MANUAL. No second acquisition or merge engine exists.

## Side-effect boundary

Catalog/automatic-choice preview is passive. The 24 focused Phase-3C tests explicitly verify no preview download/install call, no custom selector acquisition UI, standard download-GUI use for a non-installed candidate, no GUI for an installed candidate, and revalidation before support/root activity.

All 105 Phase-1/2/3 tests pass. Targeted `iMac19,1` EFI generation and official OpenCore 1.0.7 validation pass. The inherited full universal sweep was not needed because Phase 3C does not touch EFI-builder code; its previously established post-`iMac18,3` `iMac19,1` sweep boundary remains unchanged.

## Frozen boundaries

Relative to corrected Phase-3B HEAD `f29f4bf97b260b91fd007e69a6976dc16cc0d264`, only manual KDK model/GUI/resolver plumbing and tests changed. Modern Wireless/Audio detection and dictionaries, KDK match/fallback semantics in AUTO, KC commands, SIP, ACPI, DMAR, DeviceProperties, AppleVTD, DisableIoMapper, Intel detection, boot arguments and component payloads are outside the diff.

- `payloads.dmg`: `22581d0a9981f583d1921ca447bb0d578b3c39b20a805c5c6bac4ab5678d6f98`
- `Universal-Binaries.dmg`: `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4`
- Modern Wireless dictionary source: `fa0dad681239c2268d17d81a9d8f422dc359d5d2b8b9fe670f2f12d4f3485f97`
- Modern Audio dictionary source: `a24581ef94b304d2252bc9db9d181a20332fe6621801dadf9bd5cb3339d2615d`
