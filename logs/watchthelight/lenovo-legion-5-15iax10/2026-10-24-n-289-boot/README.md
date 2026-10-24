<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-289/README.md | author: watchthelight </wtl> -->
# N-289 (2026-10-24 11:48 EDT): XeGfx 0.0.42 (rwlock spin reverted, I-115 lock order fix), ws=1 with 900 s settle

Panel: Intel iGPU (OC log `Current FB at 0x70800000`, Hybrid). Stack: XeGfx 0.0.42, XeGfxAccel, XeGfxIntelFB 0.5,
plugin NvGfx-xe e60f462.

Result: **crash**, I-116 again, and sooner than ever: about 15-20 s into the Intel desktop.

- WindowServer 1973 on the Intel GPU (12 accelerator clients, 341 frames to head 4 during the arm step).
- Progress lines 11:51:58 to 11:52:09: 368 -> 573 IOPresentment transactions, interrupts 4942 -> 6368, `irqs ==
  handled` on every line, shim spins max 1729 us, no long spins. Then nothing.
- Panic 11:53:12 report (`panic-string.txt`): `mp_rv_action() entry: 23 of 24 responses`, 23 CPUs not answering the
  NMI. The panicking CPU 3 was kernel_task in `pmap_remove_range` (a TLB shootdown) from
  `IOBufferMemoryDescriptor::free <- xg_vm_x_release <- __i915_gem_free_objects`, the i915 object free worker.
  Like N-287 and N-288, it is a CPU that waited on the stuck one, not the stuck one itself.

## What this rules out

| run   | XeGfx  | crash after             |
|-------|--------|-------------------------|
| N-285 | 0.0.39 | ~4 min                  |
| N-286 | 0.0.39 | ~4.5 min, rwlock panic  |
| N-287 | 0.0.40 | ~45 s, rendezvous panic |
| N-288 | 0.0.41 | ~40 s, rendezvous panic |
| N-289 | 0.0.42 | ~15-20 s, rendezvous    |

0.0.42 has none of 0.0.40's rwlock spin, so that suspect (N-288 README) is cleared. The crash time is not a property
of the build; N-285 and N-286 likely lived longer by chance (or died of I-115 first). GPU interrupts never stopped or
went unhandled. What is left: one CPU sits with interrupts off for over half a second, and no report shows which.

## Next (N-290): XeGfx 0.0.43, an interrupts-off watchdog

Every shim spin section (`spinlock_enter`, interrupts off at nesting 0 -> 1) and every run of the interrupt filter
records, per CPU, the time and the caller. A thread call on a CPU that still answers checks the slots every 20 ms
and panics past 100 ms with the CPU, the time, the kind of section and the caller's offset in XeGfx, well before
XNU's rendezvous timeout. If N-290 still dies in `mp_rv_action` without that panic, the stuck CPU is outside XeGfx's
own interrupts-off sections (an MMIO read stalled on the GPU, or an XNU path), which narrows it the other way.

OpenCore: `opencore-2026-10-24-154829.txt` is this boot; `155253` is the restart after the panic.
XeGfxBlock stays off from N-289 straight into N-290 (config.n290-pre.plist.bak); it goes back on after N-290.
