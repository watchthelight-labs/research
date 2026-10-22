<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-204/README.md | author: watchthelight </wtl> -->
# N-204: dGPU attach on, NvGfx off (-nvoff), BIOS Hybrid (2026-10-20 21:36 EDT)

Result: FAIL, the laptop lost power again (Bash). Read from Windows: OC log (FB 0x70800000 = Hybrid, -nvoff set) and
the unified log (Persist 1cc/1ce, Special 1db/1dd parsed with unifiedlog_iterator).

## What the log shows
- The log ends at 01:36:39.057, mid-activity (user session running), about 32 s after the kernel started.
- 01:36:32.507 `IOPCIFamily [getResources()] Performing FLR on nub IGPU`, then AGPM starts on IGPU. That is 24 s after
  IGPUConsoleRange started: with `nvfbigpu=1` the kext holds the iGPU's framebuffer slot, and when no NVIDIA GPU has
  appeared after 24 s it gives the slot back to IONDRVFramebuffer. Matching IONDRV makes IOPCIFamily reset (FLR) the
  iGPU that is scanning out the panel.
- Same on the last N-203 boot: FLR on IGPU at 01:15:16.985, log ends 01:15:25.437.
- No 10de device and no new PXSX under RP01 after the attach: DGON did not bring the RTX 5070 up. The kext's own lines
  (DGON result, EC IGPS/HPFF, PXP status) are stored as absolute references into the kernel's string table, which the
  Windows parser cannot resolve; `log show` on the Mac can.

## Cause (I-093, High for the trigger)
The iGPU FLR on the slot hand-back; the power loss follows it by 7-8 s on both boots read. The NVIDIA driver is not
involved (N-204 had -nvoff). The attach failing is a separate problem.

## Change for N-205 (safe config, applied from Windows)
OCEFI: SSDT-DGPU-ON disabled, `-nvoff` and `nvfbigpu=1` removed (backup `config.n205-pre.plist.bak` = N-204 config).
IGPUConsoleRange then behaves like 0.1 (IONDRV takes the panel at boot, as in N-201/N-202). Hybrid: unaccelerated
desktop; Discrete: normal NVIDIA desktop.

## For the Mac session (path to Hybrid + accelerated)
1. `log show --last boot` is not enough (power-cut boots); use
   `log show --start "2026-10-21 01:36:00" --end "2026-10-21 01:36:40" --predicate 'sender == "IGPUConsoleRange"'`
   (times UTC) for the DGON line: result and EC IGPS/HPFF/PXP status.
2. IGPUConsoleRange: never give the slot back late. Attach first, then decide; if the dGPU is not there, let IONDRV
   take the slot at once (before anything has used the iGPU), or keep it and stop the FLR.
3. Fix DGON using step 1's EC values (Lenovo's `_ON` skips power-on while HPFF is 1; HTPE needs EC GSTA 1).
