<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-194/README.md | author: watchthelight </wtl> -->
# N-194: dGPU mode after the N-193 stop, no -nvoff (2026-10-20 19:14)

Read on the Mac afterwards (unified log of that boot, which ends 19:16:59 when Bash powered off), correcting the Windows
reading in `00-info.txt` and the first I-091 text:

- The auxiliary kext collection **did** load: `kernelmanagerd ... loaded collection: auxiliary kext collection` at
  19:15:30, about 60 s after boot. That is the normal time here (N-195: 63 s). The bootdump snapshots at 20 s and 60 s
  were simply earlier, which is why they showed no third-party kext.
- NMIntelFB 0.1 started at 19:15:52 and declined as designed ("no pipe is scanning out": dGPU mode).
- NVRM: boot guard start 1, `go(2) took 12115 ms -> 0x0`, then `heads published mask 0x0 (0 of nvfbheads 4) after 20 s`,
  `accelerator level 1 NEVER took after 11 tries`, boot hold `display PARTIAL` at 19:16:41. So NVIDIA's display code found
  no display on this boot; WindowServer had nothing to show.
- The next boot (N-195, same config) was fully normal, so this was a one-off on the first boot after the unclean N-193 stop.
