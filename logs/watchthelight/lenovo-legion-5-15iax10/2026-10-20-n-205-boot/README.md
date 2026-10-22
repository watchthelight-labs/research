<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-205/README.md | author: watchthelight </wtl> -->
# N-205: safe config after I-093, BIOS Hybrid (2026-10-20 21:47 EDT)

Result: PASS. OC log `opencore-2026-10-21-014750.txt`: Current FB at 0x70800000 (Hybrid). IONDRVFramebuffer drives
the panel at 2560x1600 through IGPUConsoleRange's console range (as N-201), unaccelerated. No `Performing FLR on nub
IGPU` line in this boot's log, no power cut (up 9+ min when checked). No NVIDIA device on PCI.

## I-093, mechanism from the IOPCIFamily source (apple-oss-distributions/IOPCIFamily, checked 2026-10-20)
- `IOPCIDevice::detachFromChild` (IOPCIDevice.cpp ~417-433): when a child service of a live nub detaches while it is
  inactive (a terminated driver, not a crash and not a match-time detach), the nub is marked `hardwareResetNeeded`.
- `IOPCIDevice::getResources` (~1080-1090): the next time drivers match on that nub, it runs an FLR (or a hot reset)
  first and logs `[getResources()] Performing FLR on nub <name>`.
- IGPUConsoleRange 0.3 terminated its own claim on IGPU 24 s after start and re-registered the nub, so IONDRV's match
  reset the iGPU while it was scanning out the panel. The laptop lost power 7-8 s later on every such boot.
- Rule from this: never start a driver on the iGPU and terminate it later. Decide the framebuffer slot once, in probe.

## Why the DGON result was missing
The kext logged with IOLog only. On this machine third-party IOLog lines reach neither the unified log nor a usable
dmesg (the Wi-Fi debug output wraps the message buffer within seconds), so N-203/N-204 left no trace of DGON.
0.4 keeps its own trace (sysctl `debug.wtlacpi_log`, property `watchthelight-trace` on IGPU, last line in NVRAM
`wtl-igpurange`).
