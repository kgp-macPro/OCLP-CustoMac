# OCLP-CustoMac 3.0.0 RC — Runtime Validation

Date: 2026-08-16

Status: **GATE 1 PASS — GATE 2 PENDING**

## Release-candidate identity

- source commit: `6ef78041577bd00ef4d7b5aabe215ff969e4c8de`
- source description: final user-visible GUI-branding cleanup
- package: `/Users/kgp/Desktop/OCLP/OCLP-CustoMac-3.0.0-RC/OpenCore-Patcher.pkg`
- package SHA-256: `69a745c4dbb92a493c1562c717a0b426364a624dbcc19f54ee0aa92d67595fda`

This is the current final pre-publication RC. The evidence below was produced from that RC after the GUI-branding cleanup; it is separate from the earlier Phase-5 package evidence.

## Gate 1 — Intel AX210

Hardware: Intel AX210 (`8086:2725`)

Result: **PASS**

KGP performed the following real-system sequence:

1. Existing root patches were successfully reverted.
2. The system returned to the clean/reverted state.
3. OCLP-CustoMac Root Patching completed successfully.
4. After reboot:
   - AppleHDA: **PASS**
   - Intel Wi-Fi: **PASS**
   - AirPlay: **PASS — bidirectional**
   - normal Apple Screen Mirroring: **PASS — bidirectional**

This validates the final RC's Intel AX210 patch/recovery path after the user-visible GUI-branding cleanup.

### Intel runtime claim boundary

This result does not broaden the AirportItlwm AWDL support claim. OCLP-CustoMac still does not claim reliable Intel support for:

- bidirectional AirDrop;
- Personal Hotspot;
- Continuity Camera.

Those remain external AirportItlwm runtime/driver limitations, distinct from OCLP-CustoMac PCI detection, Modern Wi-Fi applicability, and the shared Modern Wireless root patch.

## Gate 2 — Broadcom BCM943602CDP

Status: **PENDING**

Publication remains blocked until KGP completes the final physical BCM943602CDP runtime gate. No GitHub push, tag, or release is authorized by the Gate-1 result alone.

## Artifact integrity

This documentation update did not rebuild or alter the RC. Its recorded identities remain:

- `OpenCore-Patcher.pkg`: `69a745c4dbb92a493c1562c717a0b426364a624dbcc19f54ee0aa92d67595fda`
- `OpenCore-Patcher-Uninstaller.pkg`: `3e37647e8bab1602eb129bb7651dd88ab28afeb0302cc03c9e15a7258b122ed1`
- `payloads.dmg`: `082de073e0d103d7bd4b47852007f2b6ab360eda5b4737a089cf3b34a3910f91`
- `Universal-Binaries.dmg`: `3659ae0ebadc1062252bbeeb7fe75dce292b5b9d599681c6dfa3dc4430bbc6a4`
