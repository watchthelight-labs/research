<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-217/README.md | author: watchthelight </wtl> -->
# N-217: XeGfx 0.0.5, minimal PCI scan, then the first real i915 probe (staged 2026-10-21 11:25 EDT)

Change since N-216: stage 3 adds only bus 0's display function, host bridge and ISA bridge to newbus and resolves
interrupts for the GPU only (I-099). xe-guard queue: N-217a (stages 1-3, 300 s settle to catch a delayed freeze),
N-217b (stage 4: i915 with display disabled, GuC from Resources, display check, reboot_on_fail).
A hard freeze needs a power press (TCO locked); the guard records it as a crash on the next boot and holds the queue.

## Result (2026-10-21 11:35 EDT): stage 3 held 5 min; stage 4 reached i915_pci_probe and panicked (cause found)
- Stages 1-3 passed at 11:24:36 with the minimal scan (host bridge, vgapci0 on 7D67, ISA bridge): no freeze during
  the 5-minute settle, which supports I-099 (the full scan was the trigger).
- At about 11:29:41 (uptime 385 s) stage 4 started and the kernel panicked (`Kernel-2026-10-21-113531.panic`, saved
  here): page fault at CR2 0x222a22 in `device_id_in_list` <- `i915_pci_probe` <- `linux_pci_attach_device` <-
  `bus_generic_driver_added` <- `devclass_add_driver` <- `lkpi_pci_register_driver` <- `i915kms_evh`. **i915 reached
  the GPU for the first time.** The machine rebooted by itself at 11:35 (debug=0x100 is in the boot-args, so the
  panic waited a few minutes first).
- Cause (I-100): drm-kmod's kconfig.mk writes `DRM_I915_FORCE_PROBE='"*"'` as a shell word. The harness passed it to
  clang without a shell, so the single quotes survived and `CONFIG_DRM_I915_FORCE_PROBE` became the multi-character
  constant `'"*"'` = 0x222A22, which i915 used as its `char *force_probe`. Fixed in XeGfx 0.0.6 (shlex-unquote every
  kconfig value; also fixes DRM_PANIC_SCREEN and DRM_CLIENT_DEFAULT).
- xe-guard lost its last lines (N-217a pass, N-217b start) to the panic and labelled the crash "stage 3": macOS fsync
  does not flush the drive cache. The guard now uses F_FULLFSYNC.
