# N-384: accelerated Intel desktop on 25G416 (ws=1) with the barrier snapshot plugin

Staged 2026-11-26 about 14:25 EST, Hybrid, macOS 26.7.3 beta 25G416. One restart, no kext or kernel collection change.

## Why
- Every Hybrid boot today has WindowServer at 70 to 200 % CPU: without XeGfxAccel the Intel desktop is composited in
  software. On this cooler (I-138) that alone keeps the package near 100 C (150 s sample at idle: average 93.5 C,
  35 % of seconds at 100 C or more, 50.6 W).
- The WindowServer step (`ws=1`) has never run on 25G416. N-372 passed stages 1 to 7 and xe-post there, N-355 was the
  last ws pass (25G241).
- The plugin with the barrier fix (WTLIntelGfx branch `xe-barrier-snapshot` 02ca433, sha256 starts `42034b3d11b6`)
  is built and untested. The fault it fixes was a tester's (I-116 tester notes); here it is a regression run.

## What is in place
- Kexts unchanged: XeGfx 0.0.48, XeGfxAccel 0.9 (in the auxiliary collection, not loaded: `kmutil showloaded
  --show unloaded` lists it with the package's UUID 235450C8), XeGfxAGDC 0.1.1, XeGfxIntelFB 0.10.
- Userland, installed 14:22 by `native/tools/xe-guard/xe-userland-install.sh` from `/Library/XeGfx/pkg-n384`
  (build folder `~/src/XeGfx-build/n384-userland`): Mesa ANV `libvulkan_intel.dylib` and `libdrm.2.dylib` (the
  2026-10-22 build from `~/src/xe-userland/prefix/lib`), `intel_icd.json`, `xe-live` 0 in
  `/Library/GPUBundles/nvmtl`, and the plugin in `/Library/GPUBundles/NVMTLDriver.bundle/Contents/MacOS/NVMTLDriver`.
- The NVIDIA 2.9 plugin it replaced (sha256 starts `2f185ed8b545`) is kept at
  `/Library/XeGfx/NVMTLDriver.pre-xe-userland`. `libnvmtl_translate.dylib` is still 2.9's: all 17 translator
  functions the plugin source loads by name exist in it; whether their arguments still match is what xe-post's Metal
  probes show.
- Queue entry (model N-355, without the disk load and with a 300 s settle):
  `stages=7 env="compat.linuxkpi.i915_disable_display=1 compat.linuxkpi.i915_xegfx_no_display=1
  compat.linuxkpi.i915_enable_guc=3 xegfx.nvram_trace=0 xegfx.gtawake=2" wdog=180 settle=300
  post=/usr/local/bin/xe-post post_timeout=400 ws=1 reboot_on_fail=1 reboot_after=0 fbcapex=1 ws_wait=120`

## Pass
1. Stages 1 to 7 report 1, xe-post exits 0 (`mtlprobe` and `mtlprobews rc=0` with this plugin and 2.9's translator).
2. The ws step: AGDC armed, the new WindowServer has NMXAccel clients and frames above 0, and keeps its pid for 300 s.
3. WindowServer CPU and package temperature against the software desktop (same 150 s sample).
4. No new picture faults in the Terminal (Bash's eyes when he is there; a screenshot otherwise).

## Risks and the way back
- I-116: a freeze under XeGfx with LegionCpuPower loaded is possible; `debug=0x100` is in the boot-args, so a panic
  halts and looks like a freeze. Power button, then read `Kernel-*.panic` first.
- A failed entry restarts by itself (`reboot_on_fail=1`); two failures in a row hold the queue.
- After the run, pass or fail: `MODE=restore /Library/XeGfx/pkg-n384/install.sh` as root puts the NVIDIA plugin back
  so that a Discrete boot runs what it ran before. The ANV files can stay.
- If the panel comes up on the NVIDIA GPU, the guard refuses the ws step; restore the plugin first thing.

## Result: pass (2026-11-26, boot at 14:24:43 EST, Hybrid, `Current FB at 0x70800000`)

Timeline (xe-guard.log): entry started 14:25:52, stages 1 to 7 done 14:26:07, xe-post rc=0 at 14:26:51, WindowServer
restarted 14:26:51, sampled 14:27:47 (new pid 2031, 12 accelerator clients, 289 frames to head 4), pass at 14:32:51
("stages 1-7 passed, WindowServer stable 300 s"). AGDC read 1.

1. Stages 1 to 7 all report 1. xe-post: vkprobe, vkdraw, `mtlprobe rc=0`, the WindowServer sandbox probe, vkhost,
   mtlbench (2560x1600 frames: clear 3.97 ms, blit 0.82 ms, draw 4.38 ms average), compute. The barrier snapshot
   plugin works with the shader translator of the NVIDIA 2.9 package (`post-summary.txt`).
2. The ws step passed on 25G416 for the first time: WindowServer pid 2031 kept through the 300 s settle and is still
   the same pid at 14:35. Loaded: XeGfx 0.0.48, XeGfxAccel 0.9, XeGfxAGDC 0.1.1, XeGfxIntelFB 0.10,
   LegionCpuPower 0.4.2. No panic, no WindowServer crash report, no freeze.
3. Heat and power at idle, 150 s each (`post-boot.txt`):

   | Desktop | Package temp avg (min to max) | Package power avg | Seconds at 100 C or more | WindowServer CPU |
   |---|---|---|---|---|
   | software (boot of 14:10, sampled 14:17) | 93.5 C (71 to 104) | 50.6 W | 35 % | 70 to 220 % |
   | accelerated (this boot, 14:28:30 to 14:31) | 56.4 C (49 to 87) | 17.0 W | 0 % | about 2 % (one 14.6 % sample) |

   Most of the idle heat on this unit was WindowServer compositing in software. The cooler is still weak (I-138), but
   an accelerated Intel desktop takes 34 W and 37 C off the idle state.
4. Picture: a screenshot at 14:33 (kept outside git, `~/.cache/legion/xe/N-384-desktop.jpg`) shows the Terminal with
   its translucent background, the menu bar and the Dock without a fault. Bash has not looked at it live.

Seen, not caused by this attempt: the bluetoothd fault report again at 14:25:17 (I-145), a shutdown stall report from
the restart at 14:24:23.

Not done in this boot: the research repo filing (its privacy check reads 1,600 files; no heavy I/O while WindowServer
runs on XeGfx, I-116). The NVIDIA plugin goes back with `MODE=restore` right before the next restart, not while this
desktop runs on the XeGfx plugin.

Autostart: the session after the WindowServer restart was told to check N-383 (an old verdict nobody had marked as
told came before the "still judging" case). Fixed in `claude-autostart.command`: a running attempt wins, and a
prompt that already leads to a check marks the newest verdict as told.
