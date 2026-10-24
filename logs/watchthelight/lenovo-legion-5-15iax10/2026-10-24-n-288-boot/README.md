<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-288/README.md | author: watchthelight </wtl> -->
# N-288 (2026-10-24 11:35 EDT): XeGfx 0.0.41 (interrupt counters), XeGfxIntelFB 0.5, ws=1 with 900 s settle

Panel: Intel iGPU (Hybrid). About This Mac now names the GPU: System Profiler shows "Chipset Model: Intel Xe Graphics"
(XeGfxIntelFB 0.5 sets the iGPU's `model`).

Result: **crash**, the same panic type as N-287 (I-116), about 40 s into the Intel desktop.

- 11:38:13 WindowServer 1973 on the Intel GPU. Last progress line 11:38:52 (1013 IOPresentment transactions).
- Interrupts kept flowing and every one was handled up to the end: 7002 -> 11881 in 40 s (about 120-240 a second,
  rising with the load), `irqs == handled` on every line. So the GPU interrupt path neither stopped nor stormed.
- Panic (`panic-string.txt`): `mp_rv_action() entry: 23 of 24 responses`, then 23 CPUs not answering the NMI. The
  panicking CPU this time was idle (kernel_task, processor_idle), so the CPU that never entered the rendezvous, the
  one sitting with interrupts off, is not in the report.

## What points at 0.0.40

| run   | XeGfx  | crash after             |
|-------|--------|-------------------------|
| N-285 | 0.0.39 | ~4 min                  |
| N-286 | 0.0.39 | ~4.5 min, rwlock panic  |
| N-287 | 0.0.40 | ~45 s, rendezvous panic |
| N-288 | 0.0.41 | ~40 s, rendezvous panic |

0.0.40 made every rwlock spin, instead of sleep, inside any critical section. A spinner can keep a CPU (or one that
waits on it with interrupts off) from answering the rendezvous IPI. Confidence Medium: the timing fits and no other
change between 0.0.39 and 0.0.40 touches locking, but the stuck CPU is not in either report.

## Next (N-289): XeGfx 0.0.42

Reverts the general rwlock spin and fixes the one site I-115 hit instead: `xg_map_mmap` now takes the vma-offset
lookup lock before `rcu_read_lock()` (and drops them in reverse order), so a contended reader sleeps outside the RCU
section. The interrupt counters stay. If N-289 runs well past a minute, 0.0.40's spin was I-116.

XeGfxBlock back on after this run (config.n288-post.plist.bak), off again for N-289 (config.n289-pre.plist.bak).
