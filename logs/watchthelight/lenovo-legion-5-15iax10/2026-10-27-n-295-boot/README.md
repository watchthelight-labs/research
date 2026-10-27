# N-295: Hybrid xe-guard run, gtawake=2 and FBCAPEX (2026-10-27)

BIOS Hybrid (OC log: Current FB at 0x70800000). OCEFI with XeGfxBlock off. XeGfx 0.0.45, XeGfxAccel from xe-2.6.2,
XeGfxAGDC 0.1.1, NMIntelFB 0.3. Queue entry: stages 1-7, ws step, `gtawake=2`, `fbcapex=1`, settle 900 s.

## Timeline (EDT)
- 16:08:36 boot. Stages 1-7 rc=0 result=1, xe-post rc=0.
- 16:10:53 ws step: WindowServer restart, new pid 2052, 12 accelerator clients, 253 frames to head 4.
- 16:26:50 guard verdict "pass" (WindowServer stable 900 s), guard exits.
- about 16:27:00 (panic uptime 1103 s) whole-machine stall and rendezvous panic. debug=0x100 halts, so it looked
  frozen to Bash. He powered off and booted Discrete; that boot (16:46) wrote `panic-2026-10-27-164757.txt`.

## Result: fail (I-116 recurred), not the pass the guard recorded
- Panic: `mp_rv_action() entry: 23 of 24 responses`, `mp_kdp_enter() timed-out ... expected 24 acks but received 1`.
  Same shape as N-287 to N-290: all other CPUs stopped answering, even the NMI.
- `gtawake 2 held on 1 GTs`, registry `gtawake-gts=1`: holding GT forcewake did not stop the stall.
- FBCAPEX: `fbcapex=1`, asked 65814, served 278. No harm seen in 16 min; no evidence it matters for I-116 either.
- XeGfx spin monitor to the end: max_us 306, long 0, irqs handled 20685 of 20685. No CPU sat with interrupts off
  past 100 ms before the stall, as in N-290.
- The guard judges only inside its settle window, so a stall 10 s after the window counts as a pass. Results file
  kept as written in `guard/N-295.json`.

## Files
- `opencore-2026-10-27-200828.txt` redacted OC log of the Hybrid boot.
- `panic-2026-10-27-164757.txt` panic string.
- `guard/` xe-guard result and evidence (post, ws, progress samples, xegfx log rings, sysctl, ioreg).

## Next
- I-116: gtawake=2 ruled out. Next candidates from the dossier: yields in the long ggtt_pin/shmem_get_pages loops
  and the TLB-flush timeout path (zep245 list), each behind its own knob.
- xe-guard: recheck a ws pass on the next boot (a panic report dated before the boot and after the verdict turns it
  into a crash) and a longer settle for I-116 runs (3600 s).
- OCEFI: XeGfxBlock back on (backup config.n295-post.plist.bak). BIOS back to Discrete, done by Bash at 16:46.
