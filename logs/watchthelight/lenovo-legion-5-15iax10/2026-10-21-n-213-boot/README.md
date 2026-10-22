<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-213/README.md | author: watchthelight </wtl> -->
# N-213: XeGfxBlock (codeless) keeps XeGfx from loading (2026-10-21 06:04 EDT), BIOS Hybrid

Read from Windows 2026-10-21 ~07:05 EDT: OC log, Tahoe Data volume (legion-diag, DiagnosticReports, unified log
Persist 1ee/1ef/1f0, Special 1ff).

## Boot: PASS
Boot dump 20261021-100457Z written, macOS ran 10:04 to 10:54 UTC (shutdown_stall 10:54:25, then Windows). No new
panic. XeGfxBlock did its job: XeGfx (still in the aux collection) was not loaded. The Mac session made no commits in
that time (Bash reports Claude Code API errors, see below), so XeGfx is still installed.

## The N-212 panic, finally (saved at this boot: ../N-212/panic-2026-10-21-060500.txt)
```
page fault, CR2 0x0
org.watchthelight.XeGfx : _sysctl_register_oid_locked + 0x29
org.watchthelight.XeGfx : _sysctl_register_oid + 0x3a
org.watchthelight.XeGfx : __start + 0x10
OSKext::start <- OSKext::load <- IOCatalogue::isModuleLoaded <- IOService::probeCandidates
```
XeGfx links FreeBSD's kern_sysctl (sysctl_register_oid / sysctl_register_oid_locked) into the kext, and those
definitions shadow XNU's exported `sysctl_register_oid` inside the kext. `_start` registers `debug.xegfx_start` with
the FreeBSD copy, whose OID tree is not initialised, and it dereferences NULL. N-208 died at the same time in boot
(XeGfx loaded when its PCI personality matched), so I-094 is this symbol clash, not the iGPU FLR.
Fix for XeGfx: rename the FreeBSD sysctl implementation (prefix it, e.g. `-Dsysctl_register_oid=bsd_sysctl_register_oid`)
or make `_start` call XNU's function through a separately compiled unit that cannot see the FreeBSD symbols; add a
link check that no XNU KPI symbol is defined inside the kext.

## Wi-Fi: silent data stall at ~10:42:40 (I-096)
Bash: "WiFi disconnected on macOS", "or like API errors with Claude Code".
- From 10:42:40 every outbound connection fails (Tailscale control: "no route" / all attempts failed every minute,
  apsd "Connected on 0 interfaces" at 10:45:34, Python TCP drop 10:42:09).
- The association stays up: no "Link down event", no DISASSOC, DHCP lease (Boingo, 100.70.x) kept, RSSI -56, until the
  shutdown at 10:54:08 ("en1 link INACTIVE", DISASSOC reason 3 = leaving).
- IO80211 LQM shows zero TX counts per 5 s window and "packet counts: I0 Q0 O0" around the stall.
So the native data path (MtkWlan 0.11.x core + MtkWlanNative) stopped moving frames while associated, about 38 min
into the session. Different from I-067 (scan teardown, closed at N-150) and I-081 (warm restart).
The kext's own log lines are absolute references the Windows parser cannot decode; on the Mac:
`log show --start "2026-10-21 06:40:00" --end "2026-10-21 06:45:00" --predicate 'sender BEGINSWITH "MtkWlan"'` (EDT).

## Next
No OpenCore change for N-214 (the boot is fine). For the Mac session: read the MtkWlan/MtkWlanNative lines for 06:40 to
06:45 EDT (TX ring, RX ring, firmware, MCU events), uninstall XeGfx and drop XeGfxBlock, fix the XeGfx sysctl clash.
Workaround for Bash: Wi-Fi off and on in the menu bar; if it stays dead, Shut Down (not Restart, I-081).

## Mac session check (2026-10-21 06:12 and 07:16 EDT)
- Live on the 06:04 boot: `kmutil showloaded` had no `org.watchthelight.XeGfx`; the registry showed
  `IOMatchCategory = XeGfxResident`, `IOPersonalityPublisher = org.watchthelight.XeGfxBlock`; displays: Intel 0x7D67,
  no kext loaded (IONDRV), 2560x1600.
- Static confirmation of the panic: in the linked kext `__start` calls `_sysctl_register_oid`, which `nm` lists as a
  local `T` symbol (0x85d00, from `shim/src/fbsd/xg_misc.c:292`). A new `tools/shadow_check.py` (kcabi exports vs the
  kext's defined symbols) finds 41 such kernel names redefined in the kext: the sysctl family, `sysctl__children`,
  sbuf, eventhandler, `wakeup`/`wakeup_one`, `hz`, `log`, `knote`, `kmem_free`, `zfree`, `vm_page_*`, `pmap_*_page`,
  `suword64`, `bsearch`. Every one is a trap for XNU-side code. Fix: rename them on the FreeBSD side with a forced
  include header and run the check in `link.sh`.
- Second boot at 07:14:57 (after the Windows read): same config, XeGfxBlock in the registry again, XeGfx not loaded.
- I-097 (new): `harness/score.py:143` compiles against drm-kmod's GPL-only `linuxkpi/gplv2/include`.
- I-096 read on the Mac (07:20): no MtkWlan core lines in the unified log between attach (06:05) and shutdown. The
  IO80211 LQM TX counters and "packet counts: I0 Q0 O0" read 0 already at 06:38, before the stall, so the native front
  end never feeds them and they say nothing about when traffic stopped. Next stall: `sudo mtkwifi status` while it is
  stalled, to capture the ring and MCU counters.
