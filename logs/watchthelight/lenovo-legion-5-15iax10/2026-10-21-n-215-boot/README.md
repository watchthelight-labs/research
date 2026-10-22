<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-215/README.md | author: watchthelight </wtl> -->
# N-215: XeGfx 0.0.3, why i915 does not bind (staged 2026-10-21 11:10 EDT), BIOS Hybrid

Change since N-214: XeGfx 0.0.3 (NvGfx xe e934514) in the aux collection. Stage 3 and stage 4 write the newbus tree and
every devclass's drivers into `debug.xegfx_log`; stage 4 fails with ENODEV (-19) unless an i915/xe driver is attached.
xe-guard queue: N-215 (stages 1-4, display disabled, wdog 180 s, no reboot on failure because of I-098).
Boot: needs a manual pick of Tahoe at the OpenCore picker until I-098 is fixed.

## I-098 fix applied before this boot (Bash's OK, 11:15)
BootOrder was Boot0005, Boot0004, Boot0080, Boot0001, Boot0003, Boot0002, Boot0000; Boot0004 and Boot0005 are both
"OpenCore (macOS)" entries pointing at `HD(5,...)/\EFI\OC\OpenCore.efi` (OCEFI), added during the Windows visits at
about 05:44 and 10:45 EDT. Rewritten to Boot0080, Boot0001, Boot0003, Boot0002, Boot0000, Boot0004, Boot0005
(`BootOrder-before.xml`, `BootOrder-after.txt`). Check in this boot's OpenCore log: `Should boot from 0. Tahoe` and
no `Showing menu`.

## Result (checked live 2026-10-21 11:12 EDT): boot PASS, I-098 fixed, i915 has no device to bind (cause found)
- OpenCore: `0 -> Boot0080`, `Should boot from 0. Tahoe`, no picker, EXITBS 2.8 s after OpenCore started. I-098 fixed.
- xe-guard N-215: stages 1-3 pass, stage 4 result -19 (ENODEV, the new 0.0.3 check), verdict fail; WindowServer fine.
- The newbus dump (`xegfx-log.txt`) shows the tree stops at `root0 -> pcib0`: no `pci0` bus, no devices. i915 did
  register (`devclass vgapci: drmn`), but there was no vgapci device for it to probe.
- Cause: the PCI scan (`xg_pci_scan`, every IOPCIDevice into newbus) and the claim of the display function
  (`xg_pci_bus_claim`, vgapci onto the GPU) only ran from `xg_pci_xnu_start()`, which the PCI personality called.
  That personality was removed in b53b58b (I-094 precaution), so nothing triggered them.
- Fix: XeGfx 0.0.4 runs the scan and the claim at the end of stage 3 and dumps the tree there.
