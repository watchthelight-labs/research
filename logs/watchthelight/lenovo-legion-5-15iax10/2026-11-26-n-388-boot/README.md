# N-388: third WindowServer run on the Intel GPU on 25G416, in one boot with the Wi-Fi attempt N-387

Queued 2026-11-26 about 23:50 EST. Hybrid, 25G416. Same set as N-384 and N-386 (XeGfx 0.0.48, XeGfxAccel 0.9,
XeGfxAGDC 0.1.1, XeGfxIntelFB 0.10, barrier snapshot plugin 42034b3d11b6, Intel userland from
`/Library/XeGfx/pkg-n384`). Nothing in it changed.

## Why

- Repetition: two passes in a row so far on this build. A third with a different Wi-Fi driver under it.
- The accelerated desktop keeps the laptop cool (N-386: 59.7 C at 25.1 W quiet, against 93.5 C at 50.6 W composited
  in software), which the weak cooler needs (I-138).

## Entry

```
xe-queue add N-388 7 env="compat.linuxkpi.i915_disable_display=1 compat.linuxkpi.i915_xegfx_no_display=1 compat.linuxkpi.i915_enable_guc=3 xegfx.nvram_trace=0 xegfx.gtawake=2" wdog=180 settle=300 post=/usr/local/bin/xe-post post_timeout=400 ws=1 reboot_on_fail=1 reboot_after=0 fbcapex=1 ws_wait=120 wait="/usr/local/bin/xe-pre-after-wifi N-387 /usr/bin/true" wait_timeout=900
```

## Pass

1. `N-388: wait rc=0` after the wifi-guard's pass of N-387, stages 1 to 7, xe-post rc 0.
2. ws step: new WindowServer pid, accelerator clients, pid kept for the 300 s settle.
3. Wi-Fi still joined after the WindowServer restart.

## Risks and the way back

- A failed Wi-Fi attempt: the wait step exits 3, XeGfx is not loaded, the wifi-guard rolls back and restarts.
- A ws failure restarts the Mac (`reboot_on_fail=1`); the next boot is the software desktop.
- The XeGfx-built Metal plugin stays installed. Before any Discrete boot:
  `MODE=restore /Library/XeGfx/pkg-n384/install.sh` as root.

## Result (2026-11-26, same start as N-387, kernel boot 23:45:54)

Pass. xe-guard: `wait` on N-387 passed, stages 1 to 7 result 1 each (stage 7 at 23:48:01), xe-post rc 0, WindowServer
restarted at 23:48:48 onto the Intel GPU: new pid 2359, 12 accelerator clients, 603 frames to head 4, stable for 300 s
(verdict 23:54:43, `ws_fails_in_a_row` 0). Third ws run on 25G416 after N-384 and N-386.

Idle afterwards: 49 C at 16 W package (23:57). During the build of the I-147 fix it reached 91 C at 125 W for a moment.
