# N-371: WTLWireless 0.15.0 on the MT7925, and the XeGfx 0.0.48 install

Staged on the Mac on 2026-11-11 at 19:14 EST. One boot carries two things, so that the evening needs three restarts
instead of five (Bash: "tackle multiple things at once with minimal reboots").

## Change
1. **Wi-Fi (wifi-guard stage E).** `EFI/OC/Kexts/WTLWireless.kext` on OCEFI is now 0.15.0 (core sha256 8c8eb1e46fa0...,
   native plugin 1a8b2c0f3408..., Bluetooth plugin 839bf76821dc...), built from 089eed44 with `NO_KMUTIL=1
   NO_LINKCHECK=1` (I-116: XeGfxAGDC and LegionCpuPower were loaded). 0.15.0 is phase 3 of docs/mt792x-unified.md:
   an MT7927 row in the chip table that is matched but runs only with boot-arg `mtk7927=1`. Nothing else in the
   config changed: same three entries, same boot-args.
2. **XeGfx install (xe-guard pre step).** The queue entry N-372 has
   `pre="/usr/local/bin/xe-pre-after-wifi N-371 /Library/XeGfx/pkg-0.0.48/install.sh"`. About a minute after the Dock
   the guard runs it: the wrapper waits for the wifi-guard verdict of N-371, and only on a pass the package installs
   XeGfx.kext 0.0.48 (WTLIntelGfx main b3eee07 plus PR 16, branch `pr16-test` b1d5cd9, binary sha256 1228886d79d3...)
   into `/Library/Extensions` and rebuilds the auxiliary collection beside the old one. Then the guard restarts the
   machine and N-372 runs.

## Host proof before the boot
- `tests/hwtrace/compare.sh 1d2c41d5`: the MT7925 hardware trace is identical before and after the MT7927 commit
  (3589 events). `tests/hwtrace/run.sh` and `tests/run.sh` pass.
- `nm -u` of all three binaries is the same list as the 0.14.0 bundle that boots today, so no new kernel symbol can
  fail to link. The native plugin's `MtkNativeAbi` allows 25G241, 25G332 and 25G416.
- XeGfx 0.0.48: `nm -u` (442 symbols) and the exported set are identical to 0.0.47; the collection build in the
  install script is the link check, and a failed build moves the old kext back.

## Undo
- Wi-Fi: the wifi-guard does it. No lease on en1 within 240 s restores `EFI/OC/wifi-lastgood` (the 0.14.0 bundle and
  the N-370 config, refreshed to the live config before staging; the config from before is
  `wifi-lastgood/config.n369.plist.bak`) and restarts once. `config.n-371.plist.bak` is the live config from before.
- XeGfx: `/Library/XeGfx/backup-xegfx-<stamp>/` holds the 0.0.47 kext and the old collection.

## Pass
- wifi-guard: `~/.cache/legion/wifi/N-371-pass`, lease on en1, gateway answers, the saved network joined.
- `kmutil showloaded`: org.watchthelight.WTLWireless, .Native and .Bt at 0.15.0.
- `ioreg -c WTLWireless`: `MtkChipName` MT7925, status "W1 pass: drv_own ok, chip 7925", no `MtkChipMatched`, no
  `MtkChipUnsupported`. Link as in N-370 (5 GHz, 80 MHz). Bluetooth ready, on.
- xe-guard log: "N-372: pre rc=0 ... XeGfx 0.0.48 installed", then the restart.

## If it does not go that way
- Wi-Fi rolled back: the wrapper exits 3, nothing is installed, the guard holds its queue and records N-372 as
  "pre failed". Read `~/.cache/legion/wifi/`, fix, queue N-372 again.
- The machine sits frozen: `debug=0x100` is set, a panic halts it. Power cycle, then read
  `/Library/Logs/DiagnosticReports/Kernel-*.panic` first.

## Result

**Wi-Fi part: pass** (boot 2026-11-11 19:17:36 EST, 25G416, Hybrid). The wifi-guard passed 34 s after it started
(19:18:14: lease on en1, gateway answers) and refreshed `wifi-lastgood` with the 0.15.0 bundle.

1. `kmutil showloaded`: org.watchthelight.WTLWireless, .Native and .Bt at 0.15.0.
2. Core: `MtkChipName` MT7925, `MtkState` "W6 pass: en1 passing traffic", `MtkBadAccess` 0, no `MtkChipMatched`,
   no `MtkChipUnsupported`, no `MtkChipOptIn`. Native front end on core ops 6.
3. Link as in N-370: 5g157/80, 11ac, MCS 9, 2 streams, 866 Mbit/s, RSSI -43 dBm, WPA2 Personal.
4. Bluetooth: `MtkBtState` ready, version 0.15.0.
5. The guard's one join request was answered "Could not find network" at 19:18:01 (the scan list was not in yet);
   macOS joined the saved network itself 13 s later. Same as earlier stage E boots, no fault.

Captures: `boot-state.txt` here (no addresses, no network name), the guard's set in `~/.cache/legion/wifi/N-371-pass`.

**XeGfx install part: pass.** xe-guard log, 19:19:33: "N-372: pre rc=0 xe-pre-after-wifi: wifi N-371 pass after 0 s,
installing" and "xegfx-pkg: XeGfx 0.0.48 installed (backup /Library/XeGfx/backup-xegfx-20261111-191930, kept: 12
kexts); restart to apply". So the collection build linked 0.0.48 against the 25G416 kernel and all 12 third-party
kexts of the old collection are in the new one. The guard restarted at once; the next boot (19:19:53) is N-372.
`/Library/Extensions/XeGfx.kext` reads 0.0.48 there.
