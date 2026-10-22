<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-201/README.md | author: watchthelight </wtl> -->
# N-201: first desktop on the Intel iGPU (2026-10-20 20:52)

Config: BIOS Hybrid, boot-args `-nvoff gfxrst=4`, IGPUConsoleRange 0.1 injected by OpenCore (fork intel-xe 4e5bedb),
NMIntelFB not installed. OpenCore: 9 GOP modes, `Current FB at 0x70800000` (Intel).

Result: **desktop on the built-in panel, driven by Apple's IONDRVFramebuffer on the iGPU** (Bash: "I can see the
display"). The framebuffer is `.Display_boot` (IOBootNDRV renames it when it accepts the boot console), the iGPU's
IODeviceMemory now lists the console range (0x70800000, 16,384,000 B) next to BAR0 and BAR2, system_profiler shows
Intel 7D67 2560x1600, Main Display, Online. WindowServer: first a virtual framebuffer at session creation, then
`Creating FB 1 of 1` and `Software compositor activated`: unaccelerated (CPU compositing).

So I-088 is fixed: Apple's IOBootNDRV only accepts a boot console inside a device memory range; adding the stolen-memory
range lets Apple's own driver drive the panel. The WC mapping IOFramebuffer makes of that range is fine: the earlier
NMIntelFB hangs were not caused by a write-combined mapping of DSM as such (gfxrst=4, WhateverGreen's initFB console
copy, is the remaining suspect there).

Files: `displays.txt`, `ioreg-framebuffers.txt`, `ioreg-igpu.txt`, `windowserver-and-kernel.log`, OpenCore log.
Next: acceleration. The NVIDIA card renders and NVAccel copies frames onto this framebuffer (#16 on the fork).
