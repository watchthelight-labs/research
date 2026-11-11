# N-366: back on core API v6 after the fallback check

Staged 2026-11-10 after the N-365 pass with `--no-kexts`: the `mtknativeops=5` token is out of the OCEFI boot-args
again, nothing else changes (MtkWlan 0.13.0, MtkWlanNative 0.4.17). It puts the daily config and the guard's
`wifi-lastgood` copy back on the v6 path.

## Pass criteria

1. wifi-guard stage E pass, no panic.
2. No `mtknativeops` in the kernel's boot-args; `MtkNativeCoreOps` 6.
3. Channel list, hardware name and link as N-364 (`../N-364/baseline-n363.txt`).

## Result

**Pass** (boot 2026-11-10 19:52:58 EST, 25G416, Hybrid: "Current FB at 0x70800000").

1. wifi-guard stage E: pass, lease on en1, gateway answers. No panic. Capture in `~/.cache/legion/wifi/N-366-pass/`.
2. The kernel's boot-args have no `mtknativeops`. `MtkNativeCoreOps` 6, `MtkNativeChip` "MT7925, bands 3,
   2 streams, width 2, core ops v6".
3. Channel list, PHY modes and hardware name identical to `../N-364/baseline-n363.txt`; link 5g44/80, 11ac, MCS 9,
   2 streams, 866 Mbit/s, WPA2 Personal.

The guard refreshed `wifi-lastgood` from this boot: MtkWlan 0.13.0, MtkWlanNative 0.4.17, config without the token.
Phase 1 of the MT792x plan is closed with N-364 (v6), N-365 (v5 path) and this boot.

The restart was asked for with the on-screen dialog first; it ran out with nobody answering and the restart went
ahead under the standing authorization.

Files: `state.txt`, `opencore-2026-11-11-005249.txt` (redacted).
