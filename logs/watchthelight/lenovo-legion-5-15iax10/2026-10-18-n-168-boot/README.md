<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-168/README.md | author: watchthelight </wtl> -->
# N-168: shipped NullMoth 2.3.7, unchanged (baseline for the PR 289 follow-up)

Package `~/src/NvGfx-build/pkg/2.3.7-stock` = the release pkgroot as shipped (audit:
research/repository-audits/nullmoth-release-2.3.7.md). Plugin 4744ffd12959 contains PR 289 as merged (f326ab5:
submit-ahead pass on the committing thread). Stock NVRM, so the GPU runs at the VBIOS 50 W (no nvrmtgp glue). Firmware
moved to /Library/NullMoth/nvfw by the installer.

Question: does the shipped 2.3.7 show the slow drags after login that N-160 / N-167 showed?

After the boot (Bash's Good first): `evidence/native/i-069-bisect/timed-drag.sh n168 5` started as soon as the session
is up; `caanim`; log lines. Then, still on this boot, the System Settings A/B for the dcc4ab4 PR (in-process, plugin
swapped as the system plugin for fresh processes only): DisplaysExt CPU while opening the Displays pane, stock 2.3.7 plugin
against 2.3.7 + dcc4ab4 (`~/src/NvGfx-wt-prsettings`). N-169 = 2.3.7 + 530c07f only (package 2.3.7-pr289fix).
Rollback of this install: `sudo ./uninstall.sh /Library/NullMoth/backup-20261018-181741.9ZKP8l`; recovery package 2.3.5-nvgfx.5.

## Result (2026-10-18 18:21-18:28, PASS; Bash clicked Good at 18:24:48)

- Stock 2.3.7 (kexts 2.3.7, plugin 4744ffd12959), panel on NVIDIA, 0 crashes.
- Gotcha: the timed series started during the guard window and drove the mouse, so Bash could not click Good until
  it was stopped (Good 8 s before the deadline). timed-drag.sh now waits for the guard's pass.
- Finder drag from login (`timed-drag-part1.txt`, part2): +42 s 46, +51 s 50, +63 s 146, then +72 s to +180 s
  11-26 flips/s (load 13 -> 5); from +225 s 75-77 flips/s steady (load 3.6 -> 2).
- Same shape as N-167 (2.3.6 kexts + fork 530c07f: 11-28 early, 74-78 steady). So the slow early phase is in the
  shipped 2.3.7 too, and moving the commit-time pass to its own queue (530c07f) changes neither phase on this machine.
  N-160's "stall" (4-14 flips/s) was most likely this early phase, measured before it ended.
- Consequence for the PR 289 follow-up: no performance case. What is left is the race on `_parts` (I-073), which has
  no reproduction yet.
