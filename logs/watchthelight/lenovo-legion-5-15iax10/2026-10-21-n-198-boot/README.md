<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-198/README.md | author: watchthelight </wtl> -->
# N-196 to N-198 (2026-10-20 evening)

- **N-196** (Hybrid, -nvoff, NMIntelFB 0.2) and **N-197** (Hybrid by mistake, no -nvoff): no display on either. The
  NVRAM breadcrumb read from Windows was `nmintelfb-step = 8 map surface wc` both times: stages 1 to 7 (BAR0 map, plane
  and timing registers, frame counter, boot console check, `IOFramebuffer::start`) passed, and the machine stopped in
  `IODeviceMemory::withRange(0x70800000, 16 MB)->map(kIOMapWriteCombineCache)`, the kernel map of the DSM framebuffer
  for the NVIDIA copy path. The guard counted both (`nmintelfb-starts` 2). The Windows boot after N-197 froze once
  (Kernel-Power 41 at 20:06:54) and was fine after a reset.
- **N-198** (20:14, BIOS dGPU, no -nvoff): normal NVIDIA desktop. NMIntelFB 0.2 wrote `1 probe` (guard tripped).
  OpenCore log `opencore-2026-10-21-001411.txt`.
- Fix for N-199: NMIntelFB 0.3 (fork intel-xe) makes that map only when NVAccel asks for the scanout, which never
  happens with -nvoff, so N-199 tests the plain framebuffer under WindowServer. Cache mode for the later copy-path test:
  boot-arg `nmintelfbcache=1` (WC), `2` (UC), default IOKit's device default.
