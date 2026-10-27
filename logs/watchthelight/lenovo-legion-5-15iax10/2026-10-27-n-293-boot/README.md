# N-293: cold boot after three days off, fast-boot config proven

2026-10-27 13:45 EDT. OCEFI, BIOS Discrete NVIDIA (Current FB at 0x6000000000). Desktop with NvGfx 2.5.3-nvgfx.1
(Metal 3), MtkWlan 0.12.1 + MtkWlanNative 0.4.13 (wifi-guard pass), MtkBt 0.2.4, LegionCpuPower 0.4.1.

boot-timeline.txt: kernel 13:46:02, BSD root 13:46:21 (19 s), APFS free-space scan 0 s with no trims
(SetApfsTrimTimeout 0 works), Login Window started 13:47:02, 41 s after root (58 s on 2026-10-24, 20 s of it TRIM).
