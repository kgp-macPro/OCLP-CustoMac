# Phase 5 — Runtime Validation Final

Date: 2026-08-15

Official phase: **Phase 5 — Generic Intel Modern Wi-Fi Integration**

Status: **COMPLETE — RUNTIME VALIDATED — FROZEN**

## Authority and tested artifact

- frozen Phase-4 implementation baseline: `a2b6e60ded9d9cbcc849ab8102de9d58a73f37b0`
- frozen Phase-4 documentation baseline: `d0d0aaf26057d1e8faa31773f6edef20098e14d6`
- canonical Phase-5 implementation: `13a8aeaaaa877b197b54cf6f8452a5801d7e36ff`
- pre-runtime Phase-5 documentation checkpoint: `83c90cd65dc9903b49657886af1f687ddad2f954`
- tested package: `/Users/kgp/Desktop/OCLP/OCLP-v2.0-phase5-intel-modern-wifi/OpenCore-Patcher.pkg`
- package SHA-256: `dbd3bbd56e97dfd5f9edec4b5f662ae8750326e4901698c1b13d771083f458e1`

The implementation is generic, not AX210-specific. Its 87 Intel PCI device IDs are the exact audited AirportItlwm IOKit-personality set. AX210 `8086:2725` is one ordinary member.

## Two independent validation layers

### Layer 1 — OCLP detection and applicability

```text
real Intel PCI hardware
  -> vendor 8086 + an authoritative supported device ID
  -> Intel Modern Wireless detected
  -> existing Modern Wi-Fi root patch applicable
```

### Layer 2 — runtime binding

```text
physical Intel adapter
  -> user's external Intel EFI
  -> AirportItlwm binds at boot
  -> OCLP-restored shared Apple wireless/P2P frameworks
  -> runtime wireless functionality
```

These are independent proofs. OCLP does not install, download, inject, enable, or configure AirportItlwm and does not modify the user's EFI.

## Broadcom regression control

Hardware: BCM943602CDP.

KGP successfully root patched with the Phase-5 Intel detection code present. After reboot:

- AppleHDA: **WORKING**
- Broadcom Wi-Fi: **WORKING**
- tested AWDL/Continuity functionality: **WORKING FLAWLESSLY**
- Sidecar: excluded from this result; it remains a separate research area

Conclusion: adding generic Intel detection caused no observed Broadcom regression. The Broadcom path remains independently runtime validated.

## Intel Test A — shared root-patch/runtime independence

Starting state: the shared Modern Wireless root patch had been applied while Broadcom hardware was present.

KGP powered off, replaced BCM943602CDP with AX210, booted the known external Intel EFI/AirportItlwm configuration, and did not reapply root patches merely because the physical adapter changed.

Result:

- AppleHDA: **WORKING**
- Intel AX210 Wi-Fi: **WORKING FLAWLESSLY**

This proves that the existing Modern Wireless root payload is hardware-independent between the validated Broadcom and Intel runtime paths. It does not, by itself, prove the new OCLP Intel detector; that is Test B.

## Intel Test B — direct OCLP detection and root patching

Hardware: Intel AX210, PCI identity `8086:2725`.

With AX210 physically installed and the appropriate clean root-patch state established, KGP launched the Phase-5 build. OCLP directly recognized the Intel adapter through the generic supported-ID detector, made the existing Modern Wi-Fi selection applicable, and successfully completed root patching with AX210 present.

After reboot:

- AppleHDA: **WORKING FLAWLESSLY**
- Intel Wi-Fi: **WORKING FLAWLESSLY**
- AirPlay: **WORKING FLAWLESSLY**

Test B proves Layer 1. The successful AirportItlwm-backed runtime after reboot independently proves Layer 2.

## Captured AX210 PCI evidence

KGP captured these real-system properties after successful Intel validation:

| Property | Captured value | Meaning |
|---|---|---|
| `vendor-id` | `<86 80 00 00>` | little-endian `0x8086` |
| `device-id` | `<25 27 00 00>` | little-endian `0x2725` |
| `IOName` | `pci8086,2725` | corroborates the numeric identity |
| `class-code` | `0x028000` | wireless/network controller class used by probing |
| model | `Intel AX210 Wi-Fi 6E 802.11ax + Bluetooth 5.3` | observed device description |

The same runtime node exposed Apple-style names such as `AirPort Extreme` and `ARPT`. The authentic Intel vendor/device identity remained directly visible despite that service naming. Phase-5 eligibility is based on resolved numeric PCI vendor/device identity, not an AirPort label, compatible string, loaded-service name, marketing name, or Broadcom-style spoof identity.

## Shared root-patch result

Intel and Broadcom use the same frozen Modern Wireless dictionary. Phase 5 introduced no Intel-specific payload. The shared payload includes the existing Tahoe components such as:

- `/usr/libexec/wifip2pd`
- `/System/Library/PrivateFrameworks/IO80211.framework`
- `/System/Library/PrivateFrameworks/WiFiPeerToPeer.framework`

Intel detection adds no KDK requirement. Modern Wi-Fi alone, with Modern Audio off and no other KDK-requiring patch, remains the validated no-KDK path.

## Screen Mirroring observation and acceptance boundary

Hack-to-MBP-M1 Screen Mirroring worked once and was otherwise unreliable/non-working during AX210 testing. It is not claimed as validated Intel functionality and is not classified as a failure of Intel hardware detection. The behavior belongs to the separate FeatureUnlock/Tahoe Screen Mirroring research area; Phase 5 changed no FeatureUnlock code.

AirPlay was independently confirmed working flawlessly. No broader claim is made for Intel Continuity/AWDL services that were not positively exercised in this runtime session.

## Phase-5 success criteria satisfied

1. The generic Intel set is derived from authoritative AirportItlwm source.
2. AX210 is detected through the generic rule, not a special case.
3. OCLP directly recognizes supported Intel hardware.
4. Modern Wi-Fi becomes applicable for that hardware.
5. Intel and Broadcom reuse the shared frozen Modern Wireless patchset.
6. No Intel-specific root payload, Broadcom spoof, or EFI mutation was introduced.
7. AirportItlwm remains external.
8. The Broadcom control remained fully functional with the Intel detector present.
9. A Broadcom-originated shared root patch worked after changing to AX210 without repatching.
10. Root patching with AX210 physically installed succeeded.
11. AppleHDA, Intel Wi-Fi, and AirPlay worked after reboot.
12. Screen Mirroring remains outside Phase-5 acceptance.

## Frozen invariants

- Modern Wireless patch methods: `f71883e711d7eadaa45fb23799024db1d38c1da82b57c55044687cd430f880fe`
- Modern Audio: `a24581ef94b304d2252bc9db9d181a20332fe6621801dadf9bd5cb3339d2615d`
- `payloads.dmg`: `082de073e0d103d7bd4b47852007f2b6ab360eda5b4737a089cf3b34a3910f91`
- `Universal-Binaries.dmg`: `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4`

Phase-2/3/4 functionality remained frozen.

## Final project status

| Phase | Status |
|---|---|
| Phase 2 | COMPLETE — RUNTIME VALIDATED — FROZEN |
| Phase 3B | COMPLETE — RUNTIME VALIDATED — FROZEN |
| Phase 3C | COMPLETE — RUNTIME VALIDATED — FROZEN |
| Phase 4 | COMPLETE — RUNTIME VALIDATED — FROZEN |
| Phase 5 — Generic Intel Modern Wi-Fi Integration | COMPLETE — RUNTIME VALIDATED — FROZEN |

The terms Phase-5A and Phase-5B describe runtime-test ordering only. They are not official product phases.
