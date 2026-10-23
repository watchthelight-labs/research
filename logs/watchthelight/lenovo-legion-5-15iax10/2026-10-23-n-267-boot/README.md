<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-267/README.md | author: watchthelight </wtl> -->
# N-267: first macOS boot through the graphical OpenCore picker

Booted 2026-10-23 15:23 EDT from OCEFI after the Windows sessions of the afternoon. Reported in Claude Code with no screen note; the record below comes from the OpenCore log and the running system.

## What changed since N-266
- OCEFI: OpenCanopy (OC 1.0.8) with GoldenGate resources, PickerMode External, PickerAttributes 145, ShowPicker true, Timeout 5, UIScale 2.
- Icons: blackosx BsxM1 Apple, Windows 11, Ubuntu and Linux icns in GoldenGate (source native/themes/goldengate-windows).
- Tools entry "Ubuntu probe" (LegionProbeBoot.efi, flavour Ubuntu:Linux).
- XeGfxBlock still on (as N-264).

## Result: pass
- OpenCanopy loaded at driver slot 5; panel on the Intel iGPU (`Current FB at 0x70800000`, 2560x1600, Hybrid).
- Picker entries: 1. Tahoe [Apple26:Apple], 2. Windows, 3. Ubuntu probe [Ubuntu:Linux]. OpenShell, Reset NVRAM and Toggle SIP hidden as auxiliary.
- The menu ran 5.0 s (`OCHK: FreeHotKeys` 05:025 after the menu opened), then the default Tahoe booted. `Get volume icon for Tahoe - Not Found` only means there is no `.VolumeIcon.icns`; the flavour icon Apple.icns is in GoldenGate.
- Kernel patches OK (kext dump, CPUID, power state, AppleIoMapper x2), EXITBS 19:23:57.
- Desktop on IONDRV, MtkWlan 0.12.1 + MtkWlanNative 0.4.13 joined (lease IP-185, wifi-guard pass), MtkBt 0.2.4 loaded, AppleALC 1.9.8. XeGfx not loaded, xe-guard queue empty.
- The three earlier OCEFI logs of the afternoon (18:01, 18:20, 18:40 UTC) are the Windows sessions' own picker boots (Tahoe once, Windows twice).

## Open
- How the picker looks on screen (icons, scale) is Bash's call; no photo yet.
- The Ubuntu probe tool entry is still untested on hardware.

Evidence: opencore-2026-10-23-192349.txt (redacted).
