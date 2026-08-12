# OCLP amfipassbeta v2.0 Development Baseline

Creation timestamp: `2026-08-12T16:36:51+02:00`

## Scope

- Primary purpose: KGP Tahoe Hackintosh root patching.
- Secondary maintenance work: controlled modernization of already-carried inherited Universal OCLP EFI-builder components.
- Production source is read-only. All implementation occurs in this isolated development copy.

## Source and copy identity

| Item | Value |
|---|---|
| Production source | `/Users/kgp/OCLP-Github-KGP/lzhoang2801/OCLP-amfipassbeta` |
| Development path | `/Users/kgp/Developer/OCLP-amfipassbeta-v2.0-development` |
| Production branch | `main` |
| Production HEAD | `ec5e591e0f46e948b0258ef1c8ed5d17d6a2c865` |
| Production status before copy | clean |
| Development initial HEAD | `ec5e591e0f46e948b0258ef1c8ed5d17d6a2c865` |
| Development status immediately after copy | clean |
| Development branch | `experiment/amfipassbeta-v2.0` |
| Nested Git repositories | none |

The pre-edit non-`.git` file-content manifest aggregate is SHA-256 `950e0ce58181cdae18956e37866cde7fcf0ffa602c4f2fbe85d30fffae92f2be` in both production and the initial development copy. It is the SHA-256 of the deterministically sorted per-file SHA-256 records. Git also reported the development copy clean at the same HEAD before branch creation.

`ditto` reported that it could not restore creation-time metadata on five `.DS_Store` files and `README.md`. Static verification found the same file count, exact byte hashes, file sizes, modification times, flags, modes, symlink targets, tracked state, and aggregate content hash. The differing creation-time metadata is disclosed and has no source/content effect.

## Production Git configuration before copy

Production remotes:

```text
origin  https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta.git (fetch)
origin  https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta.git (push)
```

Production local configuration:

```text
core.repositoryformatversion=0
core.filemode=true
core.bare=false
core.logallrefupdates=true
core.ignorecase=true
core.precomposeunicode=true
remote.origin.url=https://github.com/kgp-macPro/OCLP-lzhoang2801-amfipassbeta.git
remote.origin.fetch=+refs/heads/*:refs/remotes/origin/*
branch.main.remote=origin
branch.main.merge=refs/heads/main
```

## Development remote removal

The copied `origin` above was removed only from the development repository. `git remote -v` in the development root produces no output. No nested Git repository was found. The local experiment branch was created only after remote removal.

## Immutable boundaries

The production repository, completed audit workspaces, KGP FeatureUnlock-Tahoe, EFI, NVRAM, root volume, KDK installations, and macOS installation are outside this development tree and are not modification targets.
