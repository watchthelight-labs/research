# N-367: wifi-guard takes its kext names from one table (MT792x phase 2, step 1)

Staged 2026-11-10 after the N-366 pass with `--no-kexts`. Kexts and boot-args do not change (MtkWlan 0.13.0,
MtkWlanNative 0.4.17, "mtkfe=native mtknativeif=1"). What changes is the guard itself, installed as
`/usr/local/bin/wifi-guard` before the restart.

## Why

Phase 2 replaces the three MT7925 kexts with one WTLWireless bundle. The guard named `MtkWlan.kext` and
`MtkWlanNative.kext` in five places and matched their bundle IDs in `kextstat`, so it would have failed the first
bundle boot for the wrong reason and could not have rolled it back. It gets proven with the old kexts first.

## Change

- `guard.sh`: four lists at the top (kext folders, core and menu bundle ID patterns, ioreg classes) cover the old set
  and the bundle. One `restore_lastgood` function for both places that put the known-good set back. After a pass,
  `wifi-lastgood` keeps only the kexts the passing config.plist loads (all that exist when the config cannot be
  read), each replaced only after its new copy is complete.
- `guard.sh` `same_boot()`: the boot the attempt started in is recognised within 10 s. `kern.boottime` read
  1794358377 at the reinstall and 1794358378 at boot (it moves when the clock is corrected), and the script compared
  for equality. With a result already recorded nothing happened, but a rerun before the result would have rolled a
  good boot back. Dry runs: one second off goes on to the criteria, 600 s off rolls back.
- `stage.sh`: the kexts to stage are one list (`WIFI_STAGE_KEXTS` replaces it), and it strips `mtknativeops=`.

## Checked before the boot

- The helper functions on a scratch copy of the EFI tree: `in_config` says yes for the two loaded kexts and no for
  a WTLWireless folder the config does not name; the refresh drops that folder from the known-good set; a restore
  puts kexts and config back; an unreadable config keeps every kext.
- Whole guard in dry mode: an attempt on a missing interface fails and restores both kexts and the config into the
  dry folder; an attempt on en1 passes and captures `ioreg-mtkwlan.txt` and `ioreg-mtkwlannative.txt` as before.
- The bundle ID patterns match the live `kextstat`; the core pattern does not match the menu kext alone.

## Pass criteria

1. wifi-guard stage E pass with the new script (log line "lastgood refreshed from the passing set: MtkWlan.kext
   MtkWlanNative.kext" in /Users/Shared/legion-diag/wifi-guard.log).
2. `wifi-lastgood/Kexts` on OCEFI holds exactly those two kexts at 0.13.0 and 0.4.17, and its config.plist equals
   the live one.
3. The capture folder has the same eleven files as N-366. `MtkNativeCoreOps` 6, link as before.

## Result

**Pass** (boot 2026-11-10 20:02:08 EST, 25G416, Hybrid: "Current FB at 0x70800000").

1. The new guard judged the boot: start 20:02:12, pass at 20:02:45, capture at 20:03:03, then
   "lastgood refreshed from the passing set: MtkWlan.kext MtkWlanNative.kext".
2. `wifi-lastgood/Kexts` on OCEFI holds exactly those two, 0.13.0 and 0.4.17, binaries equal to the live ones; its
   config.plist equals the live one; no half-copied folder left behind.
3. The capture folder has the same eleven files as N-366. `MtkNativeCoreOps` 6, channel list and name identical to
   `../N-364/baseline-n363.txt`, link 5g44/80, 11ac, MCS 9, 2 streams, 866 Mbit/s. No panic.

Not exercised on the machine: a real rollback with the new script (dry runs only), and the bundle side of the
lists, which has nothing to match until WTLWireless.kext exists.

The restart dialog was answered with Reboot this time.

Files: `state.txt`, `opencore-2026-11-11-010159.txt` (redacted).
