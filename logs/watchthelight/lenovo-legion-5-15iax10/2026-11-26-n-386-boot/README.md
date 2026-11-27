# N-386: WindowServer on the Intel GPU again, in one boot with a Wi-Fi attempt

Queued 2026-11-26 about 14:50 EST for the boot that carries the Wi-Fi attempt N-385. Hybrid, 25G416.

## Why

- A second WindowServer run on 25G416 with the set that passed N-384 (XeGfx 0.0.48, XeGfxAccel 0.9, barrier snapshot
  plugin 42034b3d11b6, Intel userland from `/Library/XeGfx/pkg-n384`). Nothing in that set changed.
- N-384 showed what the accelerated desktop is worth at idle on this unit: 56 C at 17 W against 93.5 C at 50.6 W
  composited in software. With the weak cooler (I-138) the laptop should not sit in the software state for hours.
- New in the guard: `wait="/usr/local/bin/xe-pre-after-wifi N-385 /usr/bin/true"`. The entry starts only after the
  wifi-guard has passed N-385, and no restart sits between the two. Before, a batch of a Wi-Fi attempt and an XeGfx
  run needed the `pre=` path and a second restart.

## Entry

```
xe-queue add N-386 7 env="compat.linuxkpi.i915_disable_display=1 compat.linuxkpi.i915_xegfx_no_display=1 compat.linuxkpi.i915_enable_guc=3 xegfx.nvram_trace=0 xegfx.gtawake=2" wdog=180 settle=300 post=/usr/local/bin/xe-post post_timeout=400 ws=1 reboot_on_fail=1 reboot_after=0 fbcapex=1 ws_wait=120 wait="/usr/local/bin/xe-pre-after-wifi N-385 /usr/bin/true" wait_timeout=900
```

## Pass

1. xe-guard.log shows `N-386: wait rc=0` after the wifi-guard's pass, then stages 1 to 7 and xe-post rc 0.
2. ws step: new WindowServer pid, accelerator clients, pid kept for the 300 s settle.
3. Wi-Fi still joined after the WindowServer restart (the logout must not drop the link).
4. Idle package temperature and power in the range of N-384.

## Risks and the way back

- If the Wi-Fi attempt fails, the wait step exits 3, the entry is recorded as failed without loading XeGfx, and the
  wifi-guard rolls back and restarts.
- A ws failure restarts the Mac (`reboot_on_fail=1`); the next boot is the software desktop.
- The XeGfx-built Metal plugin stays in the NVMTLDriver bundle for this boot. Before any Discrete boot:
  `MODE=restore /Library/XeGfx/pkg-n384/install.sh` as root.

## Result: pass (2026-11-26, boot at 23:10:33 EST, Hybrid, `Current FB at 0x70800000`)

The restart of 14:46 never reached macOS (I-118, see `../N-385/README.md`); this is the start at 23:10.

Timeline (`xe-guard.log`): wifi-guard pass at 23:11, `wait rc=0` and entry start 23:12:30, stages 1 to 7 done
23:12:42, xe-post rc=0 at 23:13:28, WindowServer restarted 23:13:31, sampled 23:14:23 (new pid 2345, 12 accelerator
clients, 506 frames to head 4), pass at 23:19:26 ("stages 1-7 passed, WindowServer stable 300 s"). AGDC read 1.

Against the pass list:

1. `N-386: wait rc=0 xe-pre-after-wifi: wifi N-385 pass after 0 s`, then all seven stages report 1 and xe-post
   ends with rc 0 (`post-summary.txt`; mtlbench 2560x1600: clear 3.95 ms, blit 0.90 ms, draw 6.12 ms average). The
   `wait=` option did what it was written for: one restart carried a Wi-Fi attempt and a WindowServer run.
2. ws step: new pid 2345 at 23:13:31, kept through the 300 s settle. Second pass in a row on 25G416 with the same
   set (XeGfx 0.0.48, XeGfxAccel 0.9, XeGfxAGDC 0.1.1, XeGfxIntelFB 0.10, barrier snapshot plugin 42034b3d11b6).
   No panic and no WindowServer crash report. A `WindowServer ... cpu_resource.diag` was written at 23:12:54, before
   the switch at 23:13:31, so it is about the software desktop of the first minutes, not the accelerated one.
3. Wi-Fi stayed joined through the logout and login of the ws step: `MtkW1Join` still "joins 1 ... rejoins 0",
   gateway answers 3 of 3 at 23:15.
4. Package temperature and power, 150 s each:

   | When | Package temp avg (min to max) | Package power avg | Seconds at 100 C or more | WindowServer CPU |
   |---|---|---|---|---|
   | 23:15:40 to 23:18:10, session busy (export, tracker edits, GitHub calls) | 65.2 C (52 to 105) | 30.4 W | 1 % | 5.6 % |
   | 23:19:49 to 23:22:21, session quiet (file edits only) | 59.7 C (50 to 87) | 25.1 W | 0 % | 3.7 % |

   N-384 measured 56.4 C at 17.0 W at idle. The quiet row is in that range (a Claude Code session was open and
   editing, so it is not a bare idle). The busy row shows that light work on the accelerated desktop stays far below
   the 93.5 C and 50.6 W that the software desktop needs for doing nothing.

Seen, not caused by this attempt: the bluetoothd fault report again at 23:11:09 (I-145).

The XeGfx-built Metal plugin is still installed. Before any Discrete boot:
`MODE=restore /Library/XeGfx/pkg-n384/install.sh` as root.
