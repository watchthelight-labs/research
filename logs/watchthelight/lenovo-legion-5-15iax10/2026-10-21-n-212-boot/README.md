<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-212/README.md | author: watchthelight </wtl> -->
# N-212: XeGfx b53b58b (IOResources personality only), idle (staged 2026-10-21 05:55 EDT)

Same as N-211 plus XeGfx in the aux collection (tools/install.sh, other seven third-party kexts verified). The kext has
no PCI personality (I-094): its only personality attaches to IOResources so the kext stays loaded, and nothing touches
any device until `sudo sysctl debug.xegfx_start=1`. Uninstall: `XEGFX_MODE=uninstall sudo tools/install.sh`.
Expected: normal boot, `sysctl debug.xegfx_state` = 0.

## Result (read from Windows 2026-10-21 ~06:05 EDT): FAIL
- Bash (Claude Code, no photo): "Failed".
- OC log: BIOS Hybrid (FB 0x70800000), EXITBS 09:53:49 UTC. Windows started from F12 (no OpenCore log) at 09:54:32,
  so the boot ran at most ~40 s.
- No legion-diag boot dump, no DiagnosticReports entry, no `aapl,panic-info`. Persist 1e8 (created 09:53:54) holds no
  flushed chunks. Same signature as N-208.
- So loading XeGfx kills the boot even with no PCI personality. In N-210 XeGfx was in the aux collection too but no
  personality matched (the iGPU vendor-id was spoofed), so it was never loaded and the boot passed. The fault is in
  XeGfx's load path (`_start`, C++ static initialisers, or XeGfxResident::start), not in iGPU matching; I-094 revised.

## Change for N-213 (applied from Windows, no typing for Bash)
OCEFI: codeless `XeGfxBlock.kext` (native/kexts/XeGfxBlock.kext; backup config.n213-pre.plist.bak) claims XeGfx's only
match category (`XeGfxResident` on IOResources) with a plain IOService at probe score 10000, so IOKit never loads XeGfx.
Assumption (Medium): IOKit skips the lower-scored candidate of a satisfied category before loading its kext.
