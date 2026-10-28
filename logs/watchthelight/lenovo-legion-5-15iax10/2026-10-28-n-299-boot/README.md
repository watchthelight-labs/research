# N-299: Hybrid xe-guard run, 8 h soak under load (stopped at 5.6 h by a manual restart; shutdown panic I-121)

Date: 2026-10-28, OpenCore start 00:38 EDT. BIOS GPU mode Hybrid, OC log FB at 0x70800000 (Intel iGPU), OCEFI config with
XeGfxBlock off. XeGfx 0.0.45 with `xegfx.nvram_trace=0`, plugin 7495d761 (xe-2.6.2 d54b9d9). Same as N-298 with
settle 28800 s.

## Result
Stages 1-7 passed, post rc 0, Intel WindowServer pid 2074 from 00:41:11. The load ran 897 cycles (about 225 GB written)
until 06:18:04 with no stall. Bash restarted the Mac at about 06:19 when he woke up, before the 8 h settle ended.
xe-guard recorded it as `crash` because the restart panicked (below); the soak itself had no failure.

mtlbench draw average 4.20-4.24 ms for the first three hours, then 6.25 ms after the screen saver started at the 3 h
idle mark (03:41), as in N-298.

With N-296, N-297 and N-298 this is 1 h + 2 h + 4 h + 5.6 h of Intel desktop without the I-116 stall since
`xegfx.nvram_trace=0`.

## The shutdown panic (I-121)
`Kernel-2026-10-28-061910.panic`: `xegfx: vm: freeing wired page (ref 0x1)` from `xg_bsd_vm_page_free` <-
`linux_release_pages` <- `i915_gem_userptr_put_pages` <- `__i915_gem_free_objects` on the GEM free worker.

Cause: `vm_page_unwire` drops a userptr page's last wiring before `vm_page_free` takes its run out of the run table.
A new userptr hold on the same physical page (`vm_fault_quick_hold_pages`) could find the run in that window and add
a wiring with a plain atomic add, 0 to 1, so `vm_page_free` found the page wired again. Processes freeing and
registering host-memory buffers at shutdown make the window likely.

Fix: XeGfx 0.0.46 (NvGfx xe-2.6.2 6cf9b86). The hold takes its wiring under the table lock and only while the count is
above zero (compare and swap), and waits for a dying run to leave the table before creating a new one. Built and
link-checked; not booted yet.

Files: `guard/` (verdict, post, ws, ws-progress, xegfx logs, sysctl, ioreg, `load.txt`), the panic report and
`opencore-2026-10-28-043804.txt` (redacted).
