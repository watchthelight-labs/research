<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-286/README.md | author: watchthelight </wtl> -->
# N-286 (2026-10-24 10:34 EDT): ws=1 with a 900 s settle to catch the I-115 freeze

Panel: Intel iGPU (OC log `Current FB at 0x70800000`, Hybrid). Stack as N-285: XeGfx 0.0.39, XeGfxAccel,
XeGfxIntelFB 0.4, plugin NvGfx-xe e60f462.

Result: **crash**, and this time a kernel panic report names the cause of I-115.

WindowServer 1944 came up on the Intel GPU at 10:37:09 and ran until 10:41:42 (`guard/ws-progress.txt`, 3993
IOPresentment transactions, no copy or spin problems). The off-box stream ends at 10:41:48. Then:

    panic(cpu 1): thread_invoke: preemption_level 1
     possible cause: blocking while holding a spinlock or within interrupt context @sched_prim.c:3033
    Panicked task: pid 1944: WindowServer
      thread_block_reason <- XeGfx __rw_rlock <- xg_map_ioctl <- xg_fd_dev_ioctl <- xg_fd_remote_ioctl
      <- XeGfxResident::callPlatformFunction <- IOAccelXeGfxDRMClient::externalMethod

(`panic-string.txt`). The boot-args carry `debug=0x100`, so the panicked Mac stayed halted (it looks frozen) until
it was restarted at 11:04. N-285's silent freeze about 4 minutes in was very likely the same panic; its report was
not saved.

## Cause (High)

`xg_map_mmap` (gpu/xkpi/src/i915/xg_i915_map.c, the XG_DRM_IOCTL_MMAP path WindowServer uses to map a GEM object)
does what i915 does: `rcu_read_lock()`, then `drm_vma_offset_lock_lookup()`, which is `read_lock()` on the offset
manager's `rwlock_t`. In the shim:
- `rcu_read_lock` pins the thread, and `sched_pin` is a critical section (preemption off), on the premise that RCU
  readers never sleep;
- LinuxKPI's `rwlock_t` is the shim's `struct rwlock`, whose contended slow path blocks with `thread_block`.

On Linux `rwlock_t` spins, so taking it inside an RCU read section is legal. Here, when another WindowServer
thread held the lock for writing (adding or removing an mmap offset) at the same moment, the reader blocked with
preemption off and XNU panicked. Contention is rare, hence minutes of normal running first.

The shim's mutex slow path already spins inside critical sections (N-239); the rwlock paths did not.

## Fix (XeGfx 0.0.40, installed, not booted)

`__rw_rlock` and `_rw_wlock_cookie` (gpu/xegfx/shim/src/fbsd/xg_lock.c) spin instead of blocking when
`td_critnest != 0`, with the same bounded `xg_spin_note` as the mutex path (panics past 2 s with interrupts on,
150 ms with them off, so a real deadlock still shows up). AuxKC rebuilt (backup /Library/XeGfx/backup-20261024-110856).

Next: N-287, the same 900 s ws run on 0.0.40.

XeGfxBlock was put back on after this run (config.n286-post.plist.bak) and off again for N-287 (config.n287-pre.plist.bak).
