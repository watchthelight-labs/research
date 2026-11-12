# N-372: XeGfx 0.0.48 (WTLIntelGfx PR 16), stages 1 to 7, first XeGfx run on 25G416

Queued on 2026-11-11 at 19:14 EST. Runs on the boot after N-371, judged by the xe-guard, no Good needed.

## What is tested
WTLIntelGfx PR 16 by samwu07 ("stage 4 moves the boot framebuffer out of the GuC area"), merged locally onto main
with the version set to 0.0.48 (`~/src/XeGfx` branch `pr16-test`: cf24103 merge, b1d5cd9 version). Before stage 4
starts, `xg_fbmove_stage4()` reads where the firmware's boot surface sits in the GGTT. A surface that reaches into
the area above 0xFEE00000, which the GuC needs, is moved to a free target (0x80000000, 0x40000000 or 0xC0000000).

On the Legion the boot surface does not cross that line, so the expected result is **status 0 (not needed)**: BAR0
reads only, nothing written. The move itself is proven on the author's ThinkBook and in our host test
(scratch `fbr_test.c`, 9 cases, all pass: no move at and above the top and at GGTT 0, the crossing case moves to
0x80000000, a missing latch restores and gives -6, foreign targets -5, pipe off -1, hole -3).

This is also the first XeGfx run on 25G416 (the last full run was N-355 on 26.7.2).

## Queue entry
```
xe-queue add N-372 7 env="compat.linuxkpi.i915_disable_display=1 compat.linuxkpi.i915_xegfx_no_display=1
  compat.linuxkpi.i915_enable_guc=3 xegfx.nvram_trace=0 xegfx.gtawake=2" wdog=180 settle=120
  post="/usr/local/bin/xe-post" post_timeout=400 reboot_on_fail=1 reboot_after=1
  pre="/usr/local/bin/xe-pre-after-wifi N-371 /Library/XeGfx/pkg-0.0.48/install.sh" pre_timeout=1500
```
Same environment as N-355. No `ws=1`: the PR needs stages 1 to 7 only, and a WindowServer switch adds the I-116
risk for nothing. `reboot_after=1` ends on a clean boot without XeGfx loaded.

## Pass
- `/Users/Shared/legion-diag/xe-guard/results/N-372.json`: result pass, stages 1 to 7.
- Stage 4 log line "XeGfx: stage 4 boot framebuffer move: status 0, ..." and the `xegfx-fbmove` property on the GPU.
- xe-post: xgprobe, ANV `vkCreateDevice` and the compute pipeline, vkdraw, the Metal checks of a 7-stage run.

## After a pass
- Push `pr16-test` to WTLIntelGfx main (GitHub then shows PR 16 as merged), CHANGELOG heading "0.0.48 (booted:
  N-372)", release zip, `git subtree pull` into the NvGfx xe mirror, thank samwu07 on the PR.

## After a fail
- A stage 4 status below 0 is the PR's finding on this hardware: post the line on the PR, do not merge.
- A fail in another stage or in xe-post is 25G416 against XeGfx, not the PR: compare with N-355's capture.
- The machine sits frozen: `debug=0x100` halts on a panic. Power cycle, read `Kernel-*.panic`.

## Result

**Pass** (boot 2026-11-11 19:19:53 EST, 25G416, Hybrid; judged by the xe-guard at 19:24:06, then its restart).

1. `kmutil load` rc 0 at 19:21:03, so XeGfx 0.0.48 loads on the 25G416 kernel.
2. Stages 1 to 7 each rc 0, result 1, in 17 s (19:21:03 to 19:21:20).
3. Stage 4, the PR's code: "XeGfx: stage 4 boot framebuffer move: status 0, surf 0xff000000 -> 0x0, size 0xfa0000,
   pages 4000". The boot surface sits at 0xFF000000, above the 0xFEE00000 line, so nothing had to move, as expected.
   The GuC came up after it (`guc-fw-status` 10, `guc-submission` 1, three engines, exec and store tests result 1).
4. xe-post rc 0 in 44 s: xgprobe, ANV `vkCreateDevice` and compute pipeline, vkdraw, the three Metal probes, vkhost
   and the Metal bench all OK.
5. 120 s settle with no panic and no WindowServer restart. `results/N-372.json`: pass.

Files here: `xe-guard.log` (the guard's lines), `stage4.txt` (kernel line, registry state, sysctl), `post-summary.txt`.

One fault outside the driver: after the guard's restart the session got no prompt and sat idle until the morning.
The guard's folder was mode 0744 owned by root, so the login script (`claude-autostart.command`) could not list
`results/` as the user. Fixed on 2026-11-12: the guard sets the folder to 0777 and `results/` to 0755 at every start.
