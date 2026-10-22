<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-199/README.md | author: watchthelight </wtl> -->
# N-199: NMIntelFB 0.3 in Hybrid with -nvoff (2026-10-20 20:23) and N-200 (20:25)

- **N-199:** OpenCore log `opencore-2026-10-21-002333.txt`: 9 GOP modes, `Current FB at 0x70800000` (Hybrid), handover
  to Tahoe at 00:23:35 UTC. The next OpenCore start (N-200) was at 00:25:32 UTC, under two minutes later. The unified
  log has no entry from N-199, so the boot never persisted anything (the auxiliary collection, which carries NMIntelFB,
  loads only at ~60 s on this machine).
- **NVRAM markers lost:** on N-200 `nmintelfb-step-prev` was absent, so the N-198 value "1 probe" was already gone
  when N-200 started; `nullmoth-nv-ok` survived. Whether NMIntelFB 0.3 ran on N-199 is unknown from the machine.
  What Bash saw on screen is the missing piece.
- **N-200** (dGPU, still -nvoff): NVRMBootFB / IONDRV desktop without acceleration, NMIntelFB 0.3 declined (no lit pipe).
  `-nvoff` removed from OCEFI afterwards (backup `config.n200-pre.plist.bak`), so the next boot is the normal NVIDIA one.
