# N-370: OCEFI without the three old MT7925 kexts

Staged from Windows on 2026-11-11 ~07:45 EST. Bash: "examine the latest work done from macOS and do everything you can here". This is item 1 of the "Not done" list in the 2026-11-10 20:53 handoff entry.

## Change
- `EFI/OC/config.plist`: the three disabled `Kernel > Add` entries removed (`MtkWlan.kext`, `MtkBt.kext`, `MtkWlanNative.kext`). 33 entries before, 30 after. Written with `plistlib.dump(sort_keys=False)` like `entries.py`; a round trip of the old file is byte-identical, so the diff is only those entries.
- Folders removed from `EFI/OC/Kexts`: `MtkWlan.kext`, `MtkBt.kext`, `MtkWlanNative.kext`, and `MtkWlanNative.kext.0.4.15.bak` (the I-132 backup from 2026-11-10, obsolete since 0.4.16).
- Not touched: `WTLWireless.kext` 0.14.0 and its three entries, boot-args, `wifi-lastgood` (already the bundle), `MtkBt.kext.0.2.0.bak`, `MtkWlanNative.kext.0.4.13.bak`.
- No wifi-guard attempt is pending (no `stage.sh` run), so the guard will log "no pending attempt" and not judge this boot. `ocvalidate` was not run (no Windows build here).

## Undo
- `EFI/OC/config.n-370-pre.plist.bak` is the config from before.
- The removed folders and that config are in `private/ocefi-old-kexts-2026-11-11/` on the Windows side (not in git), hashes checked against OCEFI before removal.

## Pass
- `kmutil showloaded | grep -i watchthelight`: WTLWireless, WTLWireless.Native and WTLWireless.Bt at 0.14.0, nothing named Mtk*.
- en1 has a lease, the Wi-Fi menu lists networks, Bluetooth is on.
- `/Users/Shared/legion-diag/wifi-guard.log`: "no pending attempt".

## After a pass
- Refresh the public EFI repo's `config.plist` from the live config (item 3 of the list).
- Stick sync when it is plugged in (item 2).

## Result

**Pass** (boot 2026-11-11 18:25:12 EST, 25G416, Hybrid: "Current FB at 0x70800000"; checked on the Mac at 18:30). It was
the first macOS boot after the staging; the 07:36 boot of the same day came before it.

1. OpenCore injected `WTLWireless.kext` v0.14.0, the Bluetooth plugin v0.14.0 and the native plugin v0.14.0, each
   "Success". `kmutil showloaded`: org.watchthelight.WTLWireless, .WTLWireless.Native and .WTLWireless.Bt at 0.14.0,
   nothing named Mtk*. On OCEFI: 30 `Kernel > Add` entries, none for the three old kexts; of the MT7925 folders only
   `WTLWireless.kext` and the two `.bak` folders named above are left.
2. Wi-Fi: en1 active with a lease, default route on en1, gateway answers 3 of 3. "W6 pass: en1 passing traffic", core
   ops 6, native join 1 of 1, no `MtkConflict`. Link 5g157/80, 11ac, MCS 9, 2 streams, 866 Mbit/s, WPA2 Personal.
   System Information lists 37 other networks; card type, PHY modes and channel list equal to
   `../N-364/baseline-n363.txt`.
3. Bluetooth: `MtkBtState` ready, `MtkBtStep` done, one pass, 1522 ms, chip ID 31013, firmware version 16896, same
   loader log as N-369 (sections 0 and 1 already loaded, section 2 sent). State On, chipset THIRD_PARTY_DONGLE,
   transport UART, both known devices listed, none connected.
4. Guard log: "attempt already finished (pass); nothing to do" for N-369 (the README above expected the words "no
   pending attempt"; the meaning is the same, the guard did not judge this boot). No kernel panic; the usual
   `bluetoothd` user-fault report 33 s after boot.

Seen, not a fault of this change: System Information shows the controller firmware as v9480 c277 on this boot. N-369
showed v9736 c4881; v9480 c277 was also the value in N-357 and in the feature test of 2026-10-18. The loader's own
numbers (firmware version 16896, build 20260813113236) are the same on all of them. Why the line differs between boots
is not known. Also as before (since N-141): System Information says "Network Service Inactive" for Wi-Fi while the
link carries traffic.

Not exercised: pairing, a device connection, audio over Bluetooth.

Files: `state.txt`, `opencore-2026-11-11-232504.txt` (redacted).
