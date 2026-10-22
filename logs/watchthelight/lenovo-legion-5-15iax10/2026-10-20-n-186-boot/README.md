<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-186/README.md | author: watchthelight </wtl> -->
# N-186: 2.4.3-nvgfx.1, slow bring-up (35 s) survived the new hold cap, Bash Good

Booted 2026-10-20 10:24:16 EDT through `boot-next.sh` (package `~/src/NvGfx-build/pkg/2.4.3-nvgfx.1` installed as root,
staged under the gpu-guard with recovery 2.3.7-nvgfx.1 and a 21600 s window). OpenCore log
`opencore-2026-10-20-142358.txt` (UTC), panel on the NVIDIA GPU. Installed: NVRM c7467dcf0092 (hold cap waits for the
bring-up, TGP power-source refresh), NVRMFB f2e415e5136f (upstream 2.4.3's ONCE callbacks plus the fork's present
path), NVAccel 881569a85c9a, plugin fb7983353d66 (byte-identical to the 2.4.1-nvgfx.1 plugin: upstream's merged PR 294 is
the same code as the fork's digest half). `driver-sums.txt`, `nvrm-props.txt`, `sysctl.txt` from the guard's login capture.

Result: **Pass.** The bring-up was one of the slow ones: go(2) at 10:25:52, again a 26 s gap after `NBCI _DSM 0x10`
(`rm-bringup-35s.txt`), RmInitAdapter succeeded at 10:26:27, "auto-go: go(2) took 35280 ms (hold cap settle + 120 s)",
"boot hold RELEASED (display armed)" at 10:26:28. On N-183 and the N-184 rollback boot the same 35 to 48 s bring-up lost
the desktop to the 40 s cap; this time the cap waited and WindowServer got an armed display. Metal 3 on the desktop,
`nvrm-boot-hold = display armed`, no crash report on this boot. The guard recorded "confirmed by Bash (dialog)" at
10:27:43, 18 s after the login capture.

Bring-up series (go(2) to RmInitAdapter succeeded): 4, 48, 4, >40, 2.6, 40, 15, 35 s. Four of eight boots over 30 s;
the time sits between the NBCI `_DSM` call and RM's first allocations every time. Still unexplained, now harmless.

The staged gpubench boot set did not run by itself: the label carried a comma, which the runner refuses, and the state
file stayed at "running" (both fixed in after-good.command); the set was then run by hand as label
`2.4.3-nvgfx.1 boot` (see `evidence/native/gpubench/`).

## Boot set result (label `2.4.3-nvgfx.1 boot`, 145 rows, `gpubench/README-gpubench.md`)

On mains (10:31 to 10:57): early drags 3 to 9 flips/s for the first two minutes after login, then 99 (the N-167 slow
phase, now measured: 12 rows); caanim 177 flips/s with 0 misses; Finder drag 148 flips/s and 148 presents/s;
draw.encode 1.6 us/draw; fakews 8920 frames/s; feature test gpu/display/desktop 19 probes, 0 fail (the per-run
counts in the CSV triple because ft.sh counted the growing results file; fixed); log rate 653 NVRM lines/min at idle
(all "other": the trace chatter, upstream #242 / our nvrmdiag); gpu at rest 66.7 C, 17.4 W, limit 115000 mW.
Bash unplugged the charger at 10:57:50, so paneab (1.70 s DisplaysExt CPU per 12 s), pipeline (0.4 ms each, 7.3x),
sampbench (397k draws/s), sched3 (0.085 ms), selftest (16/16) and surfin (539 frames/s) ran on battery at the 50 W
limit; they are not comparable with mains rows. present.sh failed: no "present stats" line in the dmesg buffer, which
the Wi-Fi driver's debug lines flood (it should read the unified log instead).

## Pileup set (12:21, label `2.4.3-nvgfx.1 pileup`)

Upstream #295 regression check on 2.4.3's ONCE thread_calls: three runs, each with two display mode switches
(`setDisplayMode 0x8000101f` and back, 12:21:03 to 12:21:29) under 100 Hz synthetic mouse bursts. kernel_task threads
245 base, 247 peak, delta 2, no abort, recovery 0 s (`evidence/native/gpubench/pileup/pileup-17925132*.csv`, summary
`evidence/native/gpubench/summary-N-186-2.4.3-nvgfx.1 pileup.md`). The first attempt at 12:20 wrote three
`pileup.failed` rows: the script probed sudo with `-n`, which defeats its own GB_PW fallback (fixed in pileup.sh).
I-082 closes on this result.

## Three text-app freezes on this boot (I-085)

Terminal 11:46:12, iTerm2 12:08:41 and 12:23:37: the plugin logged "completion witness missing; disabling backend"
inside each process and the app hung in CoreAnimation's CG queue. Not a WindowServer or kernel event; the display and
every other app kept running. Record: `evidence/native/I-085-completion-witness-hang/README.md`.
