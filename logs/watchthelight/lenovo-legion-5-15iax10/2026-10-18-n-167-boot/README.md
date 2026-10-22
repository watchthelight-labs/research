<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-167/README.md | author: watchthelight </wtl> -->
# N-167: stock NullMoth 2.3.6 + fork plugin 530c07f (commit-time ahead pass on its own queue), commit-ahead ON

Package `~/src/NvGfx-build/pkg/2.3.6-stock-plugin-aheadq` (REF stock 2.3.6 pkgroot, plugin b81e4ec27348 after
re-signing, built RELEASE from nvgfx-2.3.6-next 530c07f). No `NVMTL_COMMIT_AHEAD` line in nvrm610.conf, so the
commit-time pass is on (the N-160 setting that stalled drags; N-166 had it off and did not stall).

Fix under test (I-073): a commit only asks for an ahead pass and returns; one pass at a time runs on the
`nvmtl.ahead` queue. The worker retires parts and the finish path empties `_parts` under the class lock, and the finish
path closes the parts to the pass before walking them.

In-process before the boot (system plugin swapped, fresh processes, conf without the knob):
- sched3: B scheduled 0.10-0.13 ms after commit in every round (worker-only: 65-85 ms in 3 of 5 rounds)
- order: 0/400 wrong on one queue, 0/400 on two queues with a shared event
- wsdrag (as WindowServer): 6410 frames/s over 20 s, no degradation; a8rt 17 ok (unchanged)

Gotcha found on the way: a RELEASE plugin unsets every `NVMTL_*`/`NVK_*`/`NAK_*`/`NVRM_*` variable at load
(`nvmtl_conf_knobs`), so only nvrm610.conf knobs reach a release build. The in-process runs earlier today with
`NVMTL_COMMIT_AHEAD=1` in the environment really ran with the conf's 0.

After the boot (Bash's Good first): `~/.cache/legion/drag/run.sh n167` x12 (Finder window open; N-166: 50-54 after
warm-up, no stall over 5200 flips), `caanim`, `fps.sh 10 n167`; a stall -> `evidence/native/i-069-bisect/check-drag-spindump.sh`.
Pass = no stall over 5000 flips and drag at or above N-166.
Rollback of this install: `sudo ./uninstall.sh /Library/NullMoth/backup-20261018-174536.3yNKID`; recovery package 2.3.5-nvgfx.5.

## Result (2026-10-18 17:49-17:55, PASS in steady state; slow first two minutes after login)

- Bash clicked Good at 17:51:41. Panel on NVIDIA ("Current FB at 0x6000000000"), kexts stock 2.3.6, plugin
  b81e4ec27348, 0 crashes.
- Finder drag right after login (17:49:45, load ~2.5): 140, then 11 11 11 25 11 11 12 13 26 28 26 flips/s.
- From ~17:51:50 on: 76 75 76 (the spindump script's drags), then 74 74 76 74 74 75 75 76 75 77 75 flips/s, and 77-78
  right after 20 s idle periods. Flips counter 832 -> 12877 with no stall. One run (n167-13) read 11, while the
  spindump's dmesg/chown tail was still running.
- Steady-state drag is 74-78 flips/s against 50-54 on N-166 (commit-time pass off): the commit-time pass is worth
  about 45 % on window drags once it runs off the committing thread.
- The spindump (`ws-drag-spindump.txt.gz`, taken during a 75 flips/s drag, not a slow one) shows the execution worker
  in `vkWaitForFences` from `nvmtlAdvancePart` -> `nvmtl_gsub_finish` (264 of 269 samples), which is the expected
  worker wait. It shows no wait in the commit path.
- Open: the slow first ~2 minutes after login. N-166 (pass off) also started at 33/39 before 50-54, so part of it is
  login load (Spotlight, WindowManager). With the pass on it is deeper (11-28). N-160's "stall" (4-14 for about a
  minute) was measured in the same window, so I-069 may have been this early phase, not a permanent stall. Next: one
  timed series from login to +5 min with the pass on, and a spindump during a slow early drag.
