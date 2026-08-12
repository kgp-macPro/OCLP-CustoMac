# Phase 1 AppleALC Review

Date: 2026-08-12

## Decision

**UPDATE AppleALC 1.6.3 to exact official AppleALC 1.9.7 for the inherited Hackintosh/Universal EFI-builder maintenance path.**

This decision uses the clarified supported scope and direct KGP runtime evidence. KGP amfipassbeta v2.0 supports Tahoe root patching on Hackintosh systems; it does not claim unsupported-Mac compatibility. KGP's real production Hackintosh EFI already uses and successfully loads official AppleALC 1.9.7. That is stronger in-scope evidence than the inherited unsupported-Mac pin.

Unsupported-Mac compatibility with 1.9.7 remains **NOT VALIDATED** and is not claimed.

## Exact pin and historical regression

KGP's current source pins `applealc_version = "1.6.3"` in `opencore_legacy_patcher/constants.py`. `BuildGraphicsAudio._audio_handling()` in `opencore_legacy_patcher/efi_builder/graphics_audio.py` states:

> Due to regression in AppleALC 1.6.4+, temporarily use 1.6.3 and set override

The upstream Dortania OCLP history supplies the concrete provenance:

- commit `c707047530db29f88d1fc5e7ffcedfa0b1ebf180` (2022-12-10), “Revert AppleALC 1.7.6 update back to 1.6.3,” says the revert “resolves audio issues on certain Intel HDEF devices” and that the regression was being investigated in AppleALC;
- commit `d3878e34a2ee04d525f8d426f61830ca11cba1aa` then scoped `-lilubetaall` to the path where AppleALC is actually enabled.

That is the most exact documented failure available: AppleALC 1.6.4-or-newer behavior caused loss/breakage of audio on an unspecified subset of Intel HDEF devices. Neither OCLP nor AppleALC history identifies a narrower controller ID or one upstream AppleALC function as the sole cause. This remains a valid warning for unsupported Macs, but is not by itself a blocking compatibility requirement for KGP's stated Hackintosh support scope.

## Upstream source review

The official AppleALC repository was inspected read-only at these tags:

| Version | Tag commit |
|---|---|
| 1.6.3 | `2516cfe1a40cf7d470c20d885cd0299c49adb5d3` |
| 1.6.4 | `66949d7c336b4997d5cd087b5ea385b936c466da` |
| 1.7.6 | `e1ad27fc553ced42466f2b74a4aadeae49f6296e` |
| 1.9.7 | `a822e7c7e8f301bbedd60cca631789acd437ba24` |

The 1.6.3-to-1.6.4 range is not a single audio-controller fix. It combines extensive resource/controller additions, 32-bit/Tiger support work, pin-configuration routing changes, and other implementation changes. Later history through 1.9.7 adds many controllers/layouts and Darwin 25 constants, but no commit, changelog item, revert, or source note was found that explicitly maps to and resolves OCLP's “certain Intel HDEF devices” regression.

Current official Dortania OCLP and OCLP-Plus retain the protective 1.6.3 choice for their broader hardware scopes. OCLP-Mod 3.1.9 has already moved beyond the pin to 1.9.5. None of those facts proves unsupported-Mac safety at 1.9.7; they establish only that the historical pin is scope-specific rather than a universal Hackintosh prohibition.

## Exact Plus and Mod payload inspection

These values were read from the exact local audit copies, not inferred from ancestry:

| Fork / variant | Declared version | Payload archive | Archive SHA-256 | Kext `CFBundleVersion` | Principal executable SHA-256 |
|---|---:|---|---|---:|---|
| OCLP-Plus 3.2.2 DEBUG | 1.6.3 | `AppleALC-v1.6.3-DEBUG.zip` | `167c896d26f29fe67e84675193579f63c817cc00b4a5d87504bb81fed813961c` | 1.6.3 | `04a4e35a1ae4d21bec15c0565536245d35dc3a7d37231bf25f650f5f7e990a86` |
| OCLP-Plus 3.2.2 RELEASE | 1.6.3 | `AppleALC-v1.6.3-RELEASE.zip` | `f0179f00351fcd630164478673cbccb84098122a47cea9afe1e2ecfbc56924ed` | 1.6.3 | `2dd9eb5d040ff0a552baa9ef2a5b17c7357bb437a30297ce84f503d0012b79c2` |
| OCLP-Mod 3.1.9 DEBUG | 1.9.5 | `AppleALC-v1.9.5-DEBUG.zip` | `49a74205e7c1ace8069f886eeedc455a787b8ebf2f22dea08b942be5e279e746` | 1.9.5 | `7f7caf64498d48fb5a41e540498837951e54af0d2ca132f75d19789a95fba3cc` |
| OCLP-Mod 3.1.9 RELEASE | 1.9.5 | `AppleALC-v1.9.5-RELEASE.zip` | `a1d5cb2f7cef6ff19d5dae530a1a8d06727caf8f8456a1b5d9f58d3fe9f7ba92` | 1.9.5 | `0b086d72c7437b97ecace392340584085c8be8e030cf75702e9e46ca0b526c02` |

Neither fork carries 1.9.7. Plus is corroboration for the broad unsupported-Mac caution; Mod is evidence that a later AppleALC is used by a fork. The decisive in-scope evidence for 1.9.7 is KGP's own validated production Hackintosh EFI.

## Artifact identities

| Item | SHA-256 |
|---|---|
| KGP AppleALC 1.6.3 RELEASE slim archive | `f0179f00351fcd630164478673cbccb84098122a47cea9afe1e2ecfbc56924ed` |
| KGP AppleALC 1.6.3 RELEASE executable | `2dd9eb5d040ff0a552baa9ef2a5b17c7357bb437a30297ce84f503d0012b79c2` |
| KGP AppleALC 1.6.3 DEBUG slim archive | `167c896d26f29fe67e84675193579f63c817cc00b4a5d87504bb81fed813961c` |
| Official AppleALC 1.9.7 RELEASE parent archive | `81a8ba79986130e8c845fff595950226cbc30e588f8d37089e467f776469c29d` |
| Official AppleALC 1.9.7 DEBUG parent archive | `6769c7c833e3692cf5d08c4d472d59f80dfbdb8646754a8a685be8e33164b78b` |
| Generated 1.9.7 RELEASE slim archive | `79680e6dba45c6866d6b32c8821fad584542e4414122cc440a48bfe561aaad4a` |
| Generated 1.9.7 RELEASE executable | `5b67211797985272949b352eff0bb797504903a2ea4598e2d75d0ceca0ed5aa4` |
| Generated 1.9.7 DEBUG slim archive | `f84864d80c5dcb5a0321ec97fd7ff9fadf8945baaff33fb971cd86fb41f25a59` |
| Generated 1.9.7 DEBUG executable | `38a57eda103d7aaf4bf27b64f61e3e972388bf7517ae8da013d86d6512ec1434` |

The 1.9.7 RELEASE parent was reused from the completed audit. The DEBUG parent was absent from all searched completed-audit and temporary paths and was downloaded once from the exact official Acidanthera 1.9.7 release, then verified against its authoritative SHA-256 before use.

## Boundaries

- The AppleALC constant and DEBUG/RELEASE payloads changed to official 1.9.7; no AppleALC gate, layout-selection logic, property, or order changed.
- AppleALC remains a conditional EFI Lilu plugin.
- Modern Audio remains the separate Beta-1 AppleHDA root patch and is unaffected.
- HDAUniversal and VoodooHDA scenarios are not altered in Phase 1.
- RELEASE and DEBUG AppleALC-selected fixtures pass matching `ocvalidate`; the selected executable hashes equal their official-parent members.
- Unsupported-Mac Intel-HDEF runtime testing remains necessary before anyone represents that hardware class as compatible.
