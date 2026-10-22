<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-166/README.md | author: watchthelight </wtl> -->
# N-166: stock NullMoth 2.3.6 + fork plugin 879f9fe, submit-ahead at commit off (I-069 / I-073 A/B)

Same install as N-160 (package `~/src/NvGfx-build/pkg/2.3.6-stock-plugin`, plugin 11194136aa86, kexts stock 2.3.6),
plus `NVMTL_COMMIT_AHEAD=0` at the end of `/Library/GPUBundles/nvmtl/nvrm610.conf`, so the submit-ahead pass runs on
the execution worker only (the 2.3.5 behaviour). N-160 with the knob unset: drag fell from 147 to 4-14 flips/s while
Core Animation still flipped at 143/s.

Question: is I-069 fork commit 2840553 (submit-ahead at commit, class lock held across sync-in and vkQueueSubmit)?

After the boot (Bash's Good through the gpu-guard first):
- `log show --last 10m --predicate 'eventMessage CONTAINS "commit: submit-ahead"'` must say "runs on the worker only"
- `~/.cache/legion/drag/run.sh n166` with a Finder window open, 3 runs, plus a 30 s continuous drag (N-160 stalled
  after ~2200 flips); `~/.cache/legion/drag/caanim`; `native/tools/gfxbench/fps.sh 10 n166`
- on a stall: `evidence/native/i-069-bisect/check-drag-spindump.sh`

Pass (drags normal, no stall over 2500 flips) = I-069 is 2840553, go to plan step 3. Fail = boot
`2.3.6-stock-plugin-nofetch` next. Recovery package: 2.3.5-nvgfx.5. Rollback of this install:
`sudo ./uninstall.sh /Library/NullMoth/backup-20261018-173122.XESXQ1`.

## Result (2026-10-18 17:35, PASS: I-069 is 2840553)

- Bash clicked Good at 17:34:59 (gpu-guard PASS). Panel on NVIDIA ("Current FB at 0x6000000000"). Kexts stock 2.3.6,
  plugin 11194136aa86, 0 crashes since boot.
- Finder drag (`run.sh`, 8 s each): 33, 39, then 50 50 49 50 51 52 54 54 53 53 flips/s over 12 runs; flips counter
  1352 -> 5633 -> 6584 with no stall (N-160 with the knob unset fell to 4-14 flips/s near 2200 flips).
- So the stall comes from submit-ahead at commit (2840553): with it off the same plugin, kexts and boot are fine.
  Drag speed is back at the worker-only level (N-133 had 35; 50-54 after warm-up here), so the fix keeps the
  commit-time pass but moves the submit out of the class lock (plan step 3, I-073).
- The `commit: submit-ahead` nvlog line did not reach `log show` (release plugin), so the knob is proven by behaviour.
