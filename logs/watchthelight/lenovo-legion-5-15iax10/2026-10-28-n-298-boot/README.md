# N-298: Hybrid xe-guard run, 4 h under disk and GPU load (PASS)

Date: 2026-10-27, OpenCore start 20:28 EDT. BIOS GPU mode Hybrid, OC log FB at 0x70800000 (Intel iGPU), OCEFI config with
XeGfxBlock off. XeGfx 0.0.45 with `xegfx.nvram_trace=0` (as N-296 and N-297), plugin 7495d761 (xe-2.6.2 d54b9d9, the
I-120 fix).

## What changed from N-297
Settle 14400 s instead of 7200 s, and the plugin with the I-120 buffer-texture fix is the one WindowServer loads. Same
`xe-load`: every ~22 s it writes 256 MB plus 200 small files and runs 50 mtlbench draws.

## Result
xe-guard verdict `pass`: stages 1-7 passed, post rc 0, AGDC 1, WindowServer pid 2254 (12 accelerator clients) stable from
20:31:44 to 00:31:47, no new panic report. The load ran 642 cycles (about 160 GB written). Files: `guard/` (verdict,
post, ws, ws-progress, xegfx logs, sysctl, ioreg, `load.txt`) and `opencore-2026-10-28-002835.txt` (redacted).

mtlbench draw average 4.21 ms for the first three hours, flat. At 23:31:03 the average stepped to 6.2 ms and stayed
there: the screen saver (idle time 10800 s, Aerials) started at that second with a VideoToolbox decoder, so the bench
shared the GPU with the aerial video from then on. One cycle at the switch averaged 13.9 ms (worst draw 100 ms). Not a
regression; the aerial video played on the Intel desktop for an hour without trouble.

Three clean passes in a row with the NVRAM trace off (N-296 1 h, N-297 2 h loaded, N-298 4 h loaded) against N-290
dying at 88 min with it on: I-116 is now most likely the SMI/NVRAM trace.

## I-120 on the desktop
The new WindowServer loaded d54b9d9. The System Settings icon draws correctly; one Dock icon is still a flat yellow
square because its icon was cached before the fix. Clearing `/Library/Caches/com.apple.iconservices.store` waits for
Bash's OK.
