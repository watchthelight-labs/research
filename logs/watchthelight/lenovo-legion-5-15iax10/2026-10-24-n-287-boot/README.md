<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-287/README.md | author: watchthelight </wtl> -->
# N-287 (2026-10-24 11:15 EDT): XeGfx 0.0.40 (rwlock fix), ws=1 with a 900 s settle

Panel: Intel iGPU (OC log `Current FB at 0x70800000`, Hybrid). Stack: XeGfx 0.0.40, XeGfxAccel, XeGfxIntelFB 0.4,
plugin NvGfx-xe e60f462.

Result: **crash**, a different panic from N-286 and much sooner (under a minute into the Intel desktop).

Bash, during this run: the Dock's glass rendered on the Intel desktop, a visual sign that compositing is accelerated.
About This Mac showed no GPU name (the iGPU PCI device has no `model` property; fixed in XeGfxIntelFB 0.5).

Timeline:
- 11:18:54 WindowServer 1952 on the Intel GPU, 12 accelerator clients, IOPresentment counting up.
- 11:19:00 to 11:19:27 the guard's 5 s progress loop did not run at all (a 27 s gap), and the unified log stops at
  11:19:06: the whole machine stalled.
- 11:19:15 Core Animation in WindowServer: `synchronize timed out` over and over (GPU work stopped completing).
- 11:19:38 last progress line (1740 transactions; shim spins max 1188 us, no long spins).
- ~11:19:41 panic, the off-box stream ends.

    mp_kdp_enter() timed-out during locked wait after NMI; expected 24 acks but received 1
    panic(cpu 3): mp_rv_action() entry: 23 of 24 responses
    Panicked task: pid 1952: WindowServer
      interrupted in XeGfx fwtable_write32 <- intel_guc_ct_send <- guc_add_request <- guc_submit_request
      <- submit_notify <- __i915_request_queue <- eb_requests_add <- i915_gem_execbuffer2_ioctl

(`panic-string.txt`). A CPU rendezvous timed out, and none of the other 23 CPUs answered even an NMI, which is what
cores stuck on a bus access to a hung device look like. The XeGfx log ring (snapshot 11:19:37) has no i915 message
at all after GuC load: no hang report, no engine reset, no CT timeout. So the GPU stopped completing work without
i915 noticing, while the CPUs stalled.

New issue I-116. Not the rwlock fix itself: no long spins were recorded. Cause unknown; candidates: completion
interrupts stopped (or stormed), the GT or GuC hung in a way that stalls MMIO.

Next (N-288): XeGfx 0.0.41 adds the interrupt count and handler-run count to `debug.xegfx_spin`, which the guard
logs every 5 s, so the progress lines show whether interrupts stop, storm, or pile up unhandled before the stall.
XeGfxIntelFB 0.5 sets the iGPU's `model` ("Intel Xe Graphics") for About This Mac.

XeGfxBlock back on after this run (config.n287-post.plist.bak), off again for N-288 (config.n288-pre.plist.bak).
