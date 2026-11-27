# N-387: WTLWireless 0.15.6 candidate (group replay counters per key id, channel switch with `mtkcsa=1`)

Staged 2026-11-26 about 23:50 EST through the wifi-guard, stage E, Hybrid, macOS 26.7.3 beta 25G416. Same boot as the
XeGfx run N-388, which waits for this attempt's verdict.

## What changed against 0.15.5 (booted N-385, released)

1. Group replay counters per key id (`MtkPn.h`, the case of mt76 339bbc19). Before, all group keys shared one set of
   eight counters, so one late frame of the old GTK after a rekey could raise the counter and make frames of the new
   key read as replays until the new key's PN caught up. mt76 answers that by skipping the PN check for group frames.
   Here each group key id has its own eight counters, and the id comes from what the card reports in RXD1 bits 22:21.
   An id that is neither the current nor the previous group key is filed under the current key, which is what the
   driver did before, so a card that reports nothing useful behaves as 0.15.5. New property `MtkW2Gkey`:
   "id N prev N frames cur N old N odd N (last odd id N)".
2. Channel switch (I-139), only with boot-arg `mtkcsa=1` (branch `wifi-csa` rebased, write-up in
   `../i-139-csa/README.md`): the joined AP's beacons, probe responses and CSA / ECSA action frames are parsed
   (`MtkCsa.c`); a switch on the same band is followed with ROC plus RLM at the announced count; a beacon-loss event of
   the firmware (0x0c) ends the link at once, as a deauth does, unless a switch is pending. Counters `MtkW6Csa*`,
   new in this build `MtkW6CsaBeacons` (beacons of the joined AP checked) and `MtkW6CsaOther` (announcements of other
   BSSs on our channel, counted and never followed).
3. Always on, refactors that came with 2: the width rule of a join moved to `mtk_chan_width` (compared with the old
   inline rule over 16128 inputs, 0 differ), a shared `rlmFill`, `roc(acquire, ch, ms)`.

## Why `mtkcsa=1` in the first boot of this build

The boot of N-385 / N-386 showed the case on the air. The joined AP is a repeater. At 23:20 it moved from channel 44
to 157. What the driver saw (0.15.5, no channel switch code):

- the firmware sent beacon-loss events (`MtkW6EventIds` "0c:4"), which 0.15.5 ignores;
- the stall supervisor noticed ("tx tokens or tx status stopped"), reloaded the firmware in 1477 ms
  (`MtkStall` "probes 1 ... reloads 1"), and macOS joined again on channel 157 (`MtkW1Join` "joins 2");
- macOS had the link down from 23:20:29 to 23:20:51;
- the drop ring held two CSA and two ECSA action frames (new channel 157, count 15) from two other BSSIDs, most likely
  the repeater's uplink AP. None from the joined BSSID got to the host as an action frame; whether its beacons carried
  the element is what `MtkW6CsaBeacons` and the `MtkW6CsaSeen` counter will tell.

So this place repeats the test without anybody's help, and every restart of the loop carries the I-118 risk, which
speaks for one boot instead of two. `mtkrxdrop=1` and `mtknativelqmsnr=1` stay for this boot (the ring shows which
frames came); they come out with the release.

## Checks before the boot

- `tests/run.sh`: mtk_rxdrop_test, mtk_pn_test, mtk_csa_test, supervisor, 75 WPA checks, oracle: all pass.
- `tests/hwtrace/compare.sh b9a1e4a8`: identical (3604 events), so the hardware init sequence is that of 0.15.5.
- Build rc 0 (`NO_KMUTIL=1 NO_LINKCHECK=1`, XeGfx is loaded), 22 warnings as before. sha256 starts: core
  1ff844878e4aa2a7, native b9387bb0d766401a, bt 8203d83a7d099047. Undefined symbols of all three binaries are the
  same lists as 0.15.5 (510, 750, 310).
- Not checked on a host: whether RXD1 carries a usable key id for group frames on this card. `MtkW2Gkey` answers it.

## Staging

`WIFI_STAGE_KEXTS="WTLWireless.kext=native/drivers/WTLWireless/out" native/tools/wifi-guard/stage.sh N-387 E "mtkfe=native mtknativeif=1 mtkcsa=1"`
(`stage.sh` now replaces every key it is given and takes `WIFI_STAGE_DROP="key key"` for tokens to remove).

## Pass

1. wifi-guard: lease and gateway, `N-387 pass`.
2. `MtkW2Gkey`: "cur" counts up with group traffic, "odd" stays 0 (then the card reports the key id). If "odd" counts
   instead, the fix is inert on this card and the fallback keeps the 0.15.5 behaviour: still a pass, the finding is
   recorded.
3. `MtkW2Sec` "pnreplay 0", `MtkW2Cmd` "refused 0", `MtkW6RxDropped` 0.
4. `MtkW6CsaBeacons` counts up; `MtkW6CsaFail` 0. A channel move of the repeater, if one happens: `MtkW6CsaDone`
   up and no second join (followed), or `MtkW6CsaBcnLoss` up and a second join within a few seconds (not announced
   in a way we parse; then the frames in the ring say why).
5. Bluetooth ready, Wi-Fi menu lists networks.

## Risks and the way back

- No join: the guard puts the last good set back (0.15.5 with the N-385 boot-args) and restarts. By hand from
  Windows: restore `config.n-387.plist.bak` and the `wifi-lastgood` kexts on disk0s5.
- With `mtkcsa=1` a firmware beacon-loss event ends the link. This boot had four such events and all belong to the one
  channel move (the count did not grow in the 17 minutes after it). If the firmware sends them without cause, the
  link would drop and rejoin: `MtkW6CsaBcnLoss` against `MtkW1Join` shows it, and the next stage drops the boot-arg
  (`WIFI_STAGE_DROP=mtkcsa`).
- Wi-Fi is this laptop's only network link (en0 has no cable), so a Wi-Fi fault after the guard's pass also takes
  Remote Control down until the next restart.
- The restart itself: I-118 (two lost warm restarts on 2026-11-26).

## Result (2026-11-26 23:45 EST start, Hybrid, 25G416)

Pass for the join and the group key part, fail for `mtkcsa=1`.

- Kernel boot 23:45:54. OpenCore log `opencore-2026-11-27-044546.txt` (redacted): "Current FB at 0x70800000", so Intel panel.
- wifi-guard: pass at 23:46:53 (lease, gateway answers). It refreshed `wifi-lastgood` on OCEFI at 23:47, so the last good
  set is now 0.15.6 with `mtkcsa=1`.
- Loaded: WTLWireless, its Native and Bt plugins, all 0.15.6 (`kexts-loaded.txt`).
- Group key id: `MtkW2Gkey` = "id 1 prev -1 frames cur 23 old 0 odd 0" at 23:48. The card reports the key id in RXD1
  bits 22:21 and every group frame matched the installed key. `pnreplay 0`, `MtkW2Cmd` refused 0, `MtkW6RxDropped` 0,
  `MtkW9Power` "sku 2g failed 0, sku 5g failed 0".
- Channel switch: no announcement from the joined AP in 11 minutes (`MtkW6CsaSeen` 0, `MtkW6CsaOther` frames 0), so the
  switch path itself is still unproven on the Legion.

### I-147: the beacon-loss event ends the link without cause

Counters (`ioreg-core-early.txt` at 23:47, `ioreg-core-late.txt` at 23:56:49):

| time | joins | 0x0c events | native leaves |
|---|---|---|---|
| 23:48:25 | 3 | 2 | 2 |
| 23:49:12 | 4 | 3 | 3 |
| 23:51:24 | 7 | 6 | - |
| 23:55:22 | 12 | 11 | - |
| 23:56:49 | 14 | 13 | 13 |

One drop about every 50 s, each followed by a clean rejoin (fails 0, `MtkW6Deauths` 0, 28 key installs). Every drop is
one unsolicited firmware event 0x0c with reason 10. The AP did not go away: `MtkW6CsaBeacons` (beacons of the joined
BSSID that reached the host) kept counting between the events, 348 at 23:48:25, 480 at 23:49:12, 1798 at 23:56:49.

Cause: the 0.15.6 handler in `MtkScan.cpp` called `linkLost()` on every such event. mt76 does not: in
`mt7925_mcu_connection_loss_iter` (v6.18, `mt7925/mcu.c:274`) the event is ignored unless the interface has
`IEEE80211_VIF_BEACON_FILTER`, and then mac80211 probes the AP before it gives up. Why this firmware reports loss while
beacons arrive is open; reason 10 is not decoded. In the 0.15.5 boot before it the same event came four times in one
real channel move (I-139), so it is not always wrong.

Fix (same version 0.15.6, core sha256 starts f572ed742284ecb6, Native and Bt binaries unchanged): the handler only
notes the time. Three seconds later `tick()` ends the link only if no beacon of the joined AP arrived since the event,
otherwise it counts `MtkW6CsaBcnLossHeld`. Host tests pass, `tests/hwtrace/compare.sh` identical (3604 events), build
rc 0 with 22 warnings. Planned as N-389 with `mtkcsa=1` kept. It was built but not staged, see the check below.

### Check from Windows, 2026-11-27 12:30 EST: N-389 is not staged

Read-only, from the Windows side of the same laptop:

- `EFI/OC/Kexts/WTLWireless.kext` and `EFI/OC/wifi-lastgood` on OCEFI both hold the N-387 build (core sha256 starts
  1ff844878e4aa2a7, written 23:36). The boot-args end in `mtkfe=native mtknativeif=1 mtkcsa=1`.
- There is no `config.n-389.plist.bak` on OCEFI (the newest backup is `config.n-387.plist.bak`, 23:40:14), and the
  guard's `pending.json` still names N-387 with result pass.
- The fixed build exists: `native/drivers/WTLWireless/out/WTLWireless.kext` on the macOS volume, version 0.15.6, core
  sha256 starts f572ed742284ecb6 (hashed from Windows through `scripts/diag/apfs-read.py`).
- The xe-guard queue is empty, so N-390 is not queued either.
- No OpenCore log is newer than `opencore-2026-11-27-044546.txt`: macOS has not been started since this boot.

So the last commit of the Mac session (23:57) recorded the plan, and the session ended before the stage step. Until
N-389 is staged, every macOS start runs the N-387 build with `mtkcsa=1` and drops the link about every 50 s. First
thing at the next macOS start: stage the fixed build
(`WIFI_STAGE_KEXTS="WTLWireless.kext=native/drivers/WTLWireless/out" native/tools/wifi-guard/stage.sh N-389 E "mtkfe=native mtknativeif=1 mtkcsa=1"`),
queue N-390 behind it, restart. Windows was on the same network at 12:30, so the place for the test is unchanged.

Way back if N-389 still drops: `WIFI_STAGE_DROP=mtkcsa` with `--no-kexts`.
