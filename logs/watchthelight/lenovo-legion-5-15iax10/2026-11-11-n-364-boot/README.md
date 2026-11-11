# N-364: core ops v6, the native front end reads chip facts from the core (MT792x phase 1)

Staged 2026-11-10 on OCEFI through wifi-guard, stage E, boot-args `mtkfe=native mtknativeif=1`.

## Change

- **MtkWlan 0.12.2 -> 0.13.0.** Core API version 6 (`MtkCoreApi.h`): `get_chip_info` (name, chip ID, firmware
  string, what the silicon can do next to what the driver uses today), `get_channels2` (the country's channels with
  band and passive / DFS flags), `get_link_chan` (the association's channel with its band). Versions 1 to 5 are
  untouched. Nothing in bring-up, scan, join or the data path changed.
- **MtkWlanNative 0.4.16 -> 0.4.17.** Asks for v6 first, then v5, v4, v3. The hardware name, the stream count in the
  HT and VHT maps, the band of each supported channel and the band of the current channel now come from the core.
  On a core without v6 it assumes what it assumed before (MT7925, two streams, 2.4 and 5 GHz, 80 MHz).
  New: `MtkNativeCoreOps`, `MtkNativeChip`, boot-arg `mtknativeops=N` to stop at an older version.

Not in this step, on purpose:
- Scan results keep `mtk_bss_info` with a plain channel number. The core scans 2.4 and 5 GHz only; a band there comes
  with the 6 GHz scan.
- 6 GHz channels and a 160 MHz link are not reported to macOS even if a core offered them: Apple's channel flags for
  both are not read from `ChanSpecConvToApple80211Channel` yet (that needs a kernel collection read, which waits for a
  boot without XeGfx, I-116). A 6 GHz entry is left out, 160 MHz shows as 80.
- `getCARD_CAPABILITIES` is unchanged: none of its bits is derived from chip facts today.

## Proof before the boot

- `tests/hwtrace/compare.sh HEAD~1` style run against 0.12.2: `hwtrace: identical (3589 events)`. The core's register
  accesses and firmware commands did not change.
- `tests/hwtrace/run.sh` now also runs the v6 calls against the older ones while joined:
  `OPS6 chip rc 0 MT7925 id 7925 pci 7925 bands 3/7 nss 2/2 bw 2/3 he 0/1 eht 0/1`,
  `OPS6 channels rc 0 36 (old 36) agree 36 5g 25 dfs 16 passive 16`,
  `OPS6 link rc 0 up 1 band 1 chan 36 bw 2 center 42 flags 0`. A caller with a shorter struct gets only its own bytes.
- Core build: same warning count as 0.12.2 (16), 506 undefined symbols as before. Native build: slot check 23 and 225
  overrides right, 0 wrong, for 25G416. Both built with NO_KMUTIL / NO_LINKCHECK (I-116).
- For MT7925 the bytes macOS gets are meant to be the same as in N-363: same name string, same HT bytes
  (two streams), same VHT mask (0xfffa), same channel list and flags.

## Pass criteria

1. wifi-guard stage E pass (lease, gateway answers), no panic.
2. MtkWlan 0.13.0 and MtkWlanNative 0.4.17 loaded; `MtkNativeCoreOps` 6;
   `MtkNativeChip` "MT7925, bands 3, 2 streams, width 2, core ops v6".
3. `IO80211HardwareVersion` "MediaTek MT7925", and the Supported Channels lines of `system_profiler` and `wdutil info`
   equal to `baseline-n363.txt`.
4. Link as N-363: 5 GHz, 80 MHz, 11ac, MCS 9, 2 streams, 866 Mbit/s (channel flags 5 GHz + 80 MHz from
   `get_link_chan`).

Rollback: the guard restores `EFI/OC/wifi-lastgood/` (0.12.2 + 0.4.16) on a fail.

## Result

**Pass** (boot 2026-11-10 19:32:28 EST, 25G416, Hybrid: "Current FB at 0x70800000").

1. wifi-guard stage E: pass, lease on en1, gateway answers. No panic. Capture in `~/.cache/legion/wifi/N-364-pass/`.
2. MtkWlan 0.13.0 and MtkWlanNative 0.4.17 loaded. `MtkNativeCoreOps` 6,
   `MtkNativeChip` "MT7925, bands 3, 2 streams, width 2, core ops v6".
3. `IO80211HardwareVersion` "MediaTek MT7925"; the Supported Channels lines of `system_profiler` and `wdutil info`
   and the PHY modes line are identical to `baseline-n363.txt` (diff empty, 5 lines).
4. Link: 5g44/80, 11ac, MCS 9, 2 streams, 866 Mbit/s, WPA2 Personal, country US, as N-363. The channel and its
   5 GHz + 80 MHz flags now come from `get_link_chan`.

Bluetooth ready. The per-boot bluetoothd ExcUserFault report is the known one.

Not tested on hardware: the new native kext on a core without v6 (`mtknativeops=5`).

The restart was asked for with the on-screen dialog first; it ran out with nobody answering and the restart went
ahead under the standing authorization.

Files: `state.txt`, `opencore-2026-11-11-003221.txt` (redacted), `baseline-n363.txt`.
