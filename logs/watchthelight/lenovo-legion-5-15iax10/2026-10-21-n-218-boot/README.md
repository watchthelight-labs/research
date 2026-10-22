<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-218/README.md | author: watchthelight </wtl> -->
# N-218: XeGfx 0.0.6, i915 probe with force_probe fixed (staged 2026-10-21 11:41 EDT), BIOS Hybrid

Change since N-217: kconfig values shell-unquoted (I-100); xe-guard writes with F_FULLFSYNC. Queue: N-218 (stages 1-4
in one entry, display disabled, wdog 180 s, settle 120 s, reboot_on_fail). Expected next failure points: GuC firmware
load (`mtl_guc_70.bin` from Resources), stolen memory (base read as 0 by the quirk), GGTT init.

## Result (2026-10-21 11:50 EDT): i915_driver_probe reached, panic in the shim's free() (cause found)
- Stages 1-3 passed (11:41:36-11:41:43). Stage 4 started 11:41:43; the kernel panicked
  (`Kernel-2026-10-21-114820.panic`): page fault at CR2 = pointer - 8 in `free` <- (tail call from
  `__devm_drm_dev_alloc`) <- `i915_driver_probe` + 0xbf <- `linux_pci_attach_device`. force_probe (I-100) is fixed:
  i915 got past the ID check into the driver probe.
- The machine rebooted by itself at 11:48 after the panic; that boot's restart stalled (shutdown_stall 11:49:58) and
  Bash held the power button ("I had to hard reboot"). The guard recorded "crash during stage 4" correctly this time
  (F_FULLFSYNC).
- Cause (I-101): LinuxKPI's kmalloc sends every request above a page to contigmalloc but frees with plain free().
  FreeBSD's free() finds such blocks through its slab lookup; the shim's free() assumed its 16-byte header and read
  the magic word below a page-aligned contiguous block. The drm device (0x3520 bytes) is the first such block freed.
- Fix: XeGfx 0.0.7 records contigmalloc blocks (address hash table); free, zfree, realloc and malloc_usable_size
  check it for page-aligned pointers.
