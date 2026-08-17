### OCLP-CustoMac 3.0.1

Maintenance hotfix for OCLP-CustoMac 3.0.0.

### Fixed

- Fixes the inherited application updater loop that could repeatedly offer the already installed 3.0.0 release.
- Automatic application updates are now offered only when the available stable semantic version is strictly newer than the installed version.

### Unchanged

No intended functional changes were made to:

- Modern Wireless Root Patching
- Modern Audio / AppleHDA Root Patching
- Broadcom detection/support
- Intel detection / PCI IDs
- AirportItlwm handling
- Root Patch selection/application
- KDK handling
- AUTO / Manual KDK selection
- Darwin-26 KDK protection
- APFS patch resources
- EFI / ACPI / DMAR / DeviceProperties behavior

The Tahoe patch payloads are byte-identical to v3.0.0.

### Runtime validation

The minimal 3.0.1 hotfix was extensively A/B tested against public v3.0.0.

Reference system:

- macOS Tahoe 26.6.2
- Broadcom BCM943602CDP

Successfully verified:

- AppleHDA
- Wi-Fi
- native Bluetooth
- AirDrop
- AirPlay
- Screen Mirroring
- Continuity Camera
- Personal Hotspot
- Handoff
- Sleep/Wake

No reproducible functional regression attributable to the 3.0.1 hotfix was identified.

### Root Patch note

OCLP-CustoMac 3.0.1 deliberately retains the existing exact-build Root Patch state semantics.

Updating the application does not itself modify the installed Root Patches.

If a future Root Patch operation or selection change is required and the existing snapshot belongs to another exact build, use the established:

Revert Root Patches  
→ reboot  
→ apply Root Patches  
→ reboot

workflow.

### Upgrade

OCLP-CustoMac 3.0.0 users are recommended to update to 3.0.1 to eliminate the same-version application-update loop.
