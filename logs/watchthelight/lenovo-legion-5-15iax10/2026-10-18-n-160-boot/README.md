# N-160 (prepared, not yet installed): stock 2.3.6 + our fork plugin only

Package `~/src/NvGfx-build/pkg/2.3.6-stock-plugin` (package.sh, REF = stock 2.3.6 pkgroot copy, NVGFX_PLUGIN = the
fork plugin from 2.3.6-nvgfx.2 (879f9fe: submit-ahead at commit, per-module caches, fetch set per pass, sampler
maxLod, spvcache fallback, icon deferral fix); plugin in the package 11194136aa86 after re-signing). Stock NVRM
122b3994729c, NVRMFB 61574b21b8cb, NVAccel, translator 454a84d57bc8. CHECK PASS 13:15. Install and reboot wait for
Bash's word (13:15: "Also wait to reboot"). Questions: does the fork plugin freeze the panel on 2.3.6 (I-069), and
does it bring the glass and the Dock icons back (I-070)?

Installed 13:24 after the Bluetooth session finished (backup of the N-159 set: /Library/NullMoth/backup-20261018-132420.Nqiu97).

## Result (boot 13:25, checked 13:27 to 13:30)

Kexts 2.3.6 (stock NVRM 122b3994729c), fork plugin 11194136aa86, NVRMNVDAFramebuffer, mode 1280x800 HiDPI (2560x1600
pixels) at 165 Hz with 87 modes (no PR 273 in the stock NVRM, so the 1680x1050 looks-like mode of N-159 is gone from
the default), 0 crashes. The compositor output (`desktop.png`) is right: translucent Terminal windows, Dock glass,
the Terminal Dock icon drawn, the guard dialog visible. So the fork plugin's icon deferral and fetch work cover the
2.3.6 glass regression (I-070) at least in the composite; Bash's eyes decide the panel.

I-069 reproduced in a milder form: the flip path does not stop, but window drags nearly do. Finder title-bar drags
(`drag.txt`): run1 147 flips/s, then 4, 4, 14, 12, 6, 4, 4 flips/s. A pure Core Animation pass still flips at
143/s (caanim: 1002 flips in 7 s) and present stats report 0 latch timeouts, so the display path is fine and the
WindowServer drag path is what stalls. CPU is idle (WindowServer 10 %, load from the other Claude session only).
Counters (`sysctl-0/1/2.txt`): `nvaccel_surface_gpu_marks` 33410 and `nvaccel_surface_gpu_waits` 3736 after three
minutes, against the N-159 values on the stock plugin listed below in the tracker. N-151 (fork plugin + fork
NVRMFB/NVAccel builds) had 0 flips: the same stall, complete. Cause to find in the fork plugin on 2.3.6: the
submit-ahead-at-commit pass (2840553, I-061) and the per-pass fetch set (80e6f53) are the candidates that touch the
drag path; 2.3.6 changed the surface-dirty path on the kext side (nvAccelRestoreParkedForDirty, PR 245).

## In-process bisect without a reboot (13:45 to 14:00, on the N-161 boot: 2.3.5 kexts installed)

Four plugin builds loaded in a test process beside the installed one (NM_TEST_PLUGIN): the fork plugin on 2.3.6
(879f9fe rebuilt with RELEASE=1, text identical to the N-160 binary), the same without submit-ahead at commit
(bisect-no-submit-ahead), without the per-pass fetch set (bisect-no-fetch-set), and the stock 2.3.6 plugin.
- `sched3` (commit A busy, commit B, wait until B is scheduled): the fork plugin and the no-fetch build schedule B
  in 0.05 ms, the no-submit-ahead build and the stock plugin only after A completes (105 to 115 ms): the I-061 fix
  works on the 2.3.6 base and the harness tells the builds apart.
- `wsdrag` (native/tools/display/wsdrag.m: a window render into an IOSurface texture, a composite into an
  IOSurface framebuffer, commit, wait until scheduled, two frames in flight), plain and with a colour-attachment
  read in the composite, and run under the process name WindowServer so the kernel takes the surface marks
  (478k marks taken) and the plugin's WindowServer-only paths run: every build between 1900 and 3500 frames/s,
  no degradation over 5 s, no build slower than the stock plugin. The stall does not reproduce in a process.
So the N-160 stall needs what a test process cannot give: the 2.3.6 kexts (NVAccel's parked-VRAM restore, NVRMFB's
cursor thread) together with the fork plugin, or the real present path. The remaining bisect needs boots, two
packages are ready (2.3.6-stock-plugin-nosub, -nofetch), and the next such boot should run
`evidence/native/i-069-bisect/check-drag-spindump.sh` (spindump of WindowServer during a stalled drag) before any more
variants: one spindump says which thread waits where.
