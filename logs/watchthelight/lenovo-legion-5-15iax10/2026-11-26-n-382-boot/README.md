<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-382/README.md | author: watchthelight </wtl> -->
# N-382: XeGfxIntelFB boot guard cleared (I-141) + two Wi-Fi diagnostic boot-args

Date 2026-11-26. Staged on Bash's word (he chose "Clear I-141 + Wi-Fi args" when asked what the next boot carries).
macOS 26.7.3 beta (25G416), firmware in Hybrid, no USB stick (Bash no longer has it: OCEFI is the only OpenCore).

## What changed since N-381
1. NVRAM `7C436110-AB2A-4BBB-A880-FE41995C9F82:xeintelfb-starts` deleted (`sudo nvram -d`). It read 2 in N-381, so
   XeGfxIntelFB 0.9 was loaded but declined and Apple's IONDRVFramebuffer (`.Display_boot`) drove the panel (I-141).
   With the count gone, XeGfxIntelFB 0.9 should take the panel again. No kext changed.
2. boot-args through wifi-guard stage E, kexts untouched (`--no-kexts`, WTLWireless 0.15.4 stays): added
   `mtknativelqmsnr=1` (noise floor, SNR and per-chain RSSI in the link quality event; never run) and `mtkrxdrop=1`
   (counts received frames the driver drops, by reason; AWDL phase 0 instrumentation; never run).

## Rollback
- Wi-Fi: the guard puts the last good set back (0.15.4 with the N-381 boot-args) when there is no lease. By hand:
  `config.n-382.plist.bak` on OCEFI is the config before this staging.
- XeGfxIntelFB: its own guard counts starts and declines from the third start that did not survive 120 s, which hands
  the panel back to Apple's driver. By hand: boot-arg `-xeintelfboff`.
- No stick: if OCEFI does not boot at all, F12 -> Windows Boot Manager and restore the `.bak` config from Windows.

## Pass list
1. wifi-guard: `N-382 pass`.
2. `ioreg`: the panel's framebuffer is XeGfxIntelFB's, not `.Display_boot` of class IONDRVFramebuffer.
3. More than 2 minutes after boot `nvram ...:xeintelfb-starts` is gone or 0 (the 120 s timer cleared it). If it stays
   at 1 in Hybrid as well, I-141's cause is the clear, not Discrete mode.
4. `wdutil info` (or the Wi-Fi menu with Option) shows a noise value and an SNR; the link holds as in N-381.
5. The drop counters of `mtkrxdrop=1` are published and readable in `ioreg -rc WTLWireless`.
6. LegionCpuPower 0.4.2 as in N-381 (`passes` about 10 plus one a minute), no panic file.
7. Which GPU drives the panel (OpenCore log).

## Result: pass (2026-11-26, booted 13:55:12 EST)
Hybrid boot, `Current FB at 0x70800000`. No panic file, no rollback.

1. wifi-guard: `N-382 pass` (lease, gateway answers); last good set now carries the four boot-args.
2. The panel's framebuffer `.Display_boot` is class XeGfxIntelFramebuffer (it was IONDRVFramebuffer in N-381).
   System Information: Intel Arrow Lake Xe-LPG, 2560 x 1600, VRAM (Dynamic, Max) 24576 MB.
3. `xeintelfb-starts` read 1 at 1 min and at 2 min after boot, 0 at about 2 min 15 s: in Hybrid the 120 s clear
   reaches NVRAM. So the count of I-141 did not come from a clear that never works. Reading the source gives two
   ways it stays up: a power-off inside 120 s of start, and the static `done` flag in `xifbGuardClear()`, which lets
   only the first clear of a boot run, so a second `start()` later in the same boot counts and stays. Not proven
   for the Discrete boots (no kernel log of them).
4. `mtknativelqmsnr=1`: `wdutil info` shows `Noise : -95 dBm` with RSSI -41 dBm, 11ac, MCS 9, 2 streams,
   866 Mbps, 5g44/80. wdutil has no SNR line; the value was not looked for elsewhere.
5. `mtkrxdrop=1`: the counters are published: `MtkW6RxDropMgmtUnused` 1, the other four 0, `MtkW6RxDropped` 0,
   two minutes after boot. `MtkW6RxTransInfo` "ok 138 undecrypted 0", ping without loss.
6. LegionCpuPower 0.4.2: `passes 11` at 2 min, `sched 1 (ok`. Package 96 to 98 C at 44 to 60 W in the first minutes.
7. Panel: Intel iGPU.

Seen again: `ExcUserFault_bluetoothd` at 13:55:44 (I-145), Bluetooth ready.

Not exercised: the hardware cursor state of XeGfxIntelFB (its log lines are not readable here), a longer run, anything
that needs XeGfxAccel.

Files: `post-boot.txt`, `opencore-2026-11-26-185502.txt` (redacted). The guard's capture stays in
`~/.cache/legion/wifi/N-382-pass`.
