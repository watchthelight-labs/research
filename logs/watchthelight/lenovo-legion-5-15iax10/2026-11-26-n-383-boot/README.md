# N-383: XeGfxIntelFB 0.10 (hardware cursor at any firmware framebuffer base, boot guard clear fixed)

Staged 2026-11-26 about 14:05 EST under Bash's standing order of the same day ("automate/loop testing until further
notice"). Hybrid expected. Two restarts: the first boot only installs, the second one runs the new kext.

## What changes
One kext: XeGfxIntelFB 0.9 -> 0.10 (WTLIntelGfx branch `cursor-guard-fw-base`, 816a235). Nothing else: OCEFI config,
WTLWireless 0.15.4 and LegionCpuPower 0.4.2 stay. The two Wi-Fi diagnostic boot-args of N-382 stay in.

- 7f15059, 8691e37: the hardware cursor takes the firmware framebuffer at any GGTT base instead of only 0xff000000, and
  the refusal line prints PLANE_CTL. Review and arithmetic in `evidence/native/xe-cursor-guard/README.md`.
- 816a235 (new today, I-141): `xifbGuardClear()` lost its once-per-boot flag. Every `start()` counts in NVRAM
  `xeintelfb-starts` and arms a clear 120 s later, but only the first clear of a boot ran, so a second start in the
  same boot stayed counted. One line removed, one comment added.

Build: `OUTROOT=~/src/XeGfx-build/cursor-guard build/build_xegfxintelfb.sh` (one file, no kernel collection read).
Binary sha256 14d0bf860e0d, 68096 B, 441 undefined symbols, the same list as the installed 0.9. Package
`/Library/XeGfx/pkg-xeintelfb-0.10` (root owned, SHA256SUMS checked after the copy).

## How it runs
```
xe-queue add N-383 1 pre="/Library/XeGfx/pkg-xeintelfb-0.10/install.sh" pre_timeout=1500
```
- Boot A (the legion-reboot): about a minute after the Dock the xe-guard runs the install as root. It copies the kext to
  /Library/Extensions, deletes `xeintelfb-starts`, builds a new auxiliary kernel collection beside the old one and
  swaps it in only when XeGfxIntelFB and the NVIDIA kexts are in it. Then the guard restarts the Mac itself.
  A session that starts in boot A waits for that restart and does nothing heavy (the collection build is running).
- Boot B: 0.10 loads at boot. The guard runs the entry (XeGfx stage 1 only: shim state, nothing outside the kext) and
  writes `/Users/Shared/legion-diag/xe-guard/results/N-383.json`.

## Pass (checked in boot B)
1. `kextstat` shows org.watchthelight.XeGfxIntelFB (0.10) and `.Display_boot` is class XeGfxIntelFramebuffer.
2. `/usr/bin/log show --last 10m | grep "hw cursor"` has
   `XeGfxIntelFB: hw cursor ready: 256x256 ARGB at GGTT fffa0000, firmware framebuffer ff000000-fffa0000`.
   A "hw cursor off" line is the finding instead (it prints cur, surf, end, buf, ctl).
3. `nvram 7C436110-AB2A-4BBB-A880-FE41995C9F82:xeintelfb-starts` is 1 in the first two minutes and 0 after.
4. xe-guard result N-383 pass (stage 1).
5. Wi-Fi joined, Bluetooth ready, LegionCpuPower passes counting, no panic file.
6. `Current FB at 0x70800000` in the OpenCore log.

## Rollback
- Install fails in boot A: the old collection is kept, the guard holds its queue, nothing changed.
- Black or frozen panel in boot B: two such starts trip the boot guard and the third boot comes up on Apple's
  IONDRVFramebuffer. Or boot-arg `-xeintelfboff`.
- Back to 0.9: package `~/src/XeGfx-build/cursor-guard/xeintelfb-0.9` installed the same way; the replaced collection
  is in `/Library/XeGfx/backup-xeintelfb-<time>`.
- No USB stick: if OCEFI itself does not boot, F12 -> Windows Boot Manager.

## Result: pass (2026-11-26, boot B at 14:10:09 EST)
Hybrid, `Current FB at 0x70800000` in all three OpenCore logs. No panic file, no rollback.

Timeline: legion-reboot at 14:04:22. OpenCore start 14:04:36 handed over at 14:04:41 and macOS never logged a line
(see below). OpenCore start 14:08:30 = boot A: the xe-guard ran the install at 14:09:45 (`pre rc=0`, backup
`/Library/XeGfx/backup-xeintelfb-20261126-140945`) and restarted. OpenCore start 14:10:03 = boot B.

1. `kextstat`: org.watchthelight.XeGfxIntelFB (0.10); `.Display_boot` is class XeGfxIntelFramebuffer.
2. Kernel log 14:10:13: `XeGfxIntelFB: hw cursor ready: 256x256 ARGB at GGTT fffa0000, firmware framebuffer
   ff000000-fffa0000`, then cursor images and states "ok". Boot A (0.9) printed the old line without the range.
3. Boot guard: `boot guard: start 1` at 14:10:12, `boot guard cleared: still up 120 s after start` at 14:12:14;
   NVRAM `xeintelfb-starts` read 1 at 14:11:53 and 0 at 14:12:28. The second-start case that 816a235 fixes did not
   occur in this boot, so that path is covered by the source change only.
4. xe-guard: stage 1 `rc=0 result=1` (XeGfx 0.0.48 loaded for it). Verdict file: see post-boot.txt.
5. Wi-Fi "W6 pass", joins 1 fails 0, ping without loss; Bluetooth ready; LegionCpuPower passes 12 at 3 min.
6. Intel iGPU drives the panel.

The XIFBLOG lines ARE readable here with `/usr/bin/log show --predicate 'eventMessage CONTAINS "XeGfxIntelFB:"'`.

Seen, not caused by 0.10:
- The restart at 14:04 did not come up: handover at `EXITBS:START` 14:04:41, no macOS log, next OpenCore start
  3 min 49 s later, which booted normally with the unchanged config (0.9 still installed then). Filed under I-118.
  The boot guard count was 0 at 14:08, so the kext's start() was never reached in that attempt.
- WindowServer `cpu_resource` report at 14:12:19 (71 % average over 126 s; 113 to 210 % sampled at 14:13). The same
  report exists for the earlier Hybrid boots today (12:46, 13:36, 13:57 = N-380, N-381, N-382): the Intel desktop is
  composited in software without XeGfxAccel. It explains much of the 96 to 99 C at 44 to 60 W at idle.
- `ExcUserFault_bluetoothd` in both boots (I-145).

Files: `post-boot.txt`, three redacted OpenCore logs.
