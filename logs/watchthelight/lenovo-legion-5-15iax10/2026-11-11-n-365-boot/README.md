# N-365: MtkWlanNative 0.4.17 held to core API v5 (fallback path of MT792x phase 1)

Staged 2026-11-10 after the N-364 pass. Same kexts as N-364 (MtkWlan 0.13.0 sha256 ca49b5f4..., MtkWlanNative 0.4.17
sha256 8113c3a8...), nothing rebuilt. The only change is one boot-arg: `mtknativeops=5`.

## Why

0.4.17 asks the core for API v6 and falls back to v5, v4 and v3. On N-364 it got v6, so the fallback code (chip
defaults for an MT7925, the band taken from the channel number, `get_link_info` in place of `get_link_chan`) has
never run on the machine. The release notes say so. The boot-arg stops the kext at v5 with a core that offers v6,
which is the same code path a 0.12.x core would give.

## Pass criteria

1. wifi-guard stage E pass, no panic.
2. `MtkNativeCoreOps` 5 and `MtkNativeChip` ends in "core ops v5".
3. `IO80211HardwareVersion` and the Supported Channels lines identical to `../N-364/baseline-n363.txt`.
4. Link as before: 5 GHz, 80 MHz, 11ac MCS 9, 2 streams, 866 Mbit/s.

## After the boot

Whatever the result, the token comes out again: stage the next attempt with "mtkfe=native mtknativeif=1" and
`--no-kexts` (stage.sh strips `mtknativeops=` since this attempt). The guard copies the passing config into
`wifi-lastgood`, so that copy also carries the token until the next pass.

## Result

**Pass** (boot 2026-11-10 19:43:53 EST, 25G416, Hybrid: "Current FB at 0x70800000").

1. wifi-guard stage E: pass, lease on en1, gateway answers. No panic. Capture in `~/.cache/legion/wifi/N-365-pass/`.
2. The kernel's boot-args carry `mtknativeops=5`. `MtkNativeCoreOps` 5, `MtkNativeChip` "MT7925, bands 3, 2 streams,
   width 2, core ops v5". Kexts as N-364: MtkWlan 0.13.0, MtkWlanNative 0.4.17.
3. `IO80211HardwareVersion` "MediaTek MT7925"; the Supported Channels lines of `system_profiler` and `wdutil info`
   and the PHY modes line are identical to `../N-364/baseline-n363.txt` (diff empty, 5 lines).
4. Link: 5g44/80, 11ac, MCS 9, 2 streams, 866 Mbit/s, WPA2 Personal, country US. Handshake counters m1 to m4 once
   each, no bad MIC.

So the v5 path of 0.4.17 gives macOS the same as the v6 path on an MT7925. What this does not show: a real 0.12.x
core under 0.4.17 (the core here was 0.13.0 with the front end told to stop at v5), and the v4 and v3 paths.

The restart was asked for with the on-screen dialog first; it ran out with nobody answering and the restart went
ahead under the standing authorization.

Files: `state.txt`, `opencore-2026-11-11-004340.txt` (redacted).
