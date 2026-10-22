<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-209/README.md | author: watchthelight </wtl> -->
# N-209: -x safe boot to get past XeGfx (2026-10-21 05:31 EDT), BIOS Hybrid

Screen (Bash via Claude web, note ae0b2fd5): prohibited sign and support.apple.com/mac/startup, no verbose text.

## OpenCore log (opencore-2026-10-21-093113.txt)
boot.efi ran twice (Bash retried from the picker), both times:
- `EB.LD.LKC` loaded the Boot KC fine (`Ok(0)`, OpenCore kernel patches applied),
- then `EB.MM.AKM|! Err(0xE) <- EB.MM.MKP` and `EB.BST.FBS|RT! 0 <- EB.MM.AKMr2 0x1240d000`: boot.efi could not allocate
  ~292 MB of kernel memory,
- `EB|STOP 0x16`, boot failure graphic, exit back to OpenCore. Bash then chose Windows.
OpenCore reports `Only 128/256 slide values are usable` on this machine. Normal boots fit; a safe-mode boot needs a
larger allocation and does not. The kernel never started, so this says nothing about XeGfx.

## Cause (High)
Safe mode (-x) cannot boot on this machine with the current Booter quirks (boot.efi kernel memory allocation fails).
Not worth fixing for a rescue path.

## Change for N-210
- OCEFI: `-x` removed (backup `config.n210-pre.plist.bak`); make_config mirrored.
- (superseded, see below) XeGfx removed from macOS Recovery (Windows can only read APFS): restore the pre-XeGfx auxiliary collection from
  /Library/XeGfx/backup-20261021-032158 (19,349,504 bytes; all six backups are that size, the current collection with
  XeGfx is 23,576,576) and move /Library/Extensions/XeGfx.kext aside. That is the N-207 state, which booted in both BIOS
  modes.

Recovery Terminal commands (Bash):
```
diskutil mount "Tahoe - Data"
D="/Volumes/Tahoe - Data"
cp -p "$D/Library/XeGfx/backup-20261021-032158/AuxiliaryKernelExtensions.kc" "$D/Library/KernelCollections/AuxiliaryKernelExtensions.kc"
mv "$D/Library/Extensions/XeGfx.kext" "$D/Library/XeGfx/XeGfx.kext.off"
ls -l "$D/Library/KernelCollections/AuxiliaryKernelExtensions.kc"
reboot
```
The size printed must be 19349504.

## Revised N-210 (Bash: "make it automatic, I don't want to type anything")
Instead of Recovery: OCEFI DeviceProperties sets the iGPU `vendor-id` to 0x1234, so XeGfx's personality (vendor 0x8086)
cannot match it, and IGPUConsoleRange's Info.plist on OCEFI matches 0x1234 as well so the Hybrid IONDRV desktop keeps
working (IONDRV matches by class). The Mac session uninstalls XeGfx on that boot and removes the spoof. Writing APFS
from Windows (Paragon, MacDrive) was offered and declined.

## N-210 result (Mac, 2026-10-21 05:45 EDT): PASS
Booted normally in Hybrid with the vendor-id spoof (IONDRV desktop). XeGfx was in the aux collection but could not
match the iGPU, then the kext was unloaded for lack of an instance. On this boot the Mac session uninstalled XeGfx
(`XEGFX_MODE=uninstall tools/install.sh`, backup /Library/XeGfx/backup-20261021-054931; the seven other third-party
kexts verified in the new collection), removed the spoof from OCEFI DeviceProperties (backup `config.n211-pre.plist.bak`)
and restored IGPUConsoleRange's Info.plist on OCEFI to vendor 0x8086 only (identical to the fork's). make_config
mirrored. N-211 = the N-207 state.

## I-094, a likely mechanism (Medium, IOPCIFamily source)
`IOPCIDevice::getResources()` runs on every match of a nub. When the nub is resourced and has no child in the service
plane it calls `resetNubState()`, which the source calls "effectively a no-op on the first match". XeGfx's personality
was a late, second match on IGPU (IONDRV had matched at boot in its own category), so IOKit reset the live iGPU nub's
software state; the boot stopping right after the aux collection loaded fits that. XeGfx no longer has a PCI
personality (it finds the iGPU by registry path when started).

## N-211 result (2026-10-21 05:51 EDT): PASS
Normal Hybrid boot (FB 0x70800000), IONDRV desktop, no XeGfx loaded, no crash reports. The machine is back in the
N-207 state.
