<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-208/README.md | author: watchthelight </wtl> -->
# N-208: XeGfx 0.0.1 in the auxiliary collection, idle; shim start by sysctl (staged 2026-10-21 ~03:25 EDT)

XeGfx (github.com/watchthelight-labs/WTLIntelGfx a36e0b4): FreeBSD drm-kmod (Linux i915 6.14 level) + LinuxKPI + the
XeGfx shim, 423 objects, 4.0 MB, every symbol resolved from declared public KPI libraries (tools/kpi_check.py), no
kpi.private, no direct map. Installed with tools/install.sh into /Library/KernelCollections/AuxiliaryKernelExtensions.kc
(backup /Library/XeGfx/backup-20261021-032158; NVRM, NVRMFB, NVRMAGDC, NVAccel still in it). BIOS Hybrid, OCEFI config
unchanged from N-207 (SSDT-DGPU-ON off, no nvfbigpu). No boot-arg: the kext loads idle and only its PCI personality
probes (logs, never claims the iGPU).

After the boot:
1. `kmutil showloaded | grep XeGfx`, `sysctl debug.xegfx_state` (0), the "XeGfx: loaded, idle" and "saw 8086:7d67" lines.
2. `sudo sysctl debug.xegfx_start=1`: runs the shim init and every SYSINIT (drm, ttm, dma-buf, i915 module init). No
   device is handed to the Linux PCI driver yet, so i915 does not probe. A panic reboots into the idle kext.

## Result (read from Windows 2026-10-21 ~05:20 EDT): FAIL, both boots died early
- Boots at 07:23:46 and 09:07:57 UTC, both BIOS Hybrid (FB 0x70800000), Windows at 09:12. Bash: "last two boots failed".
- Neither boot reached the legion-diag boot dump (newest dump 20261021-021006Z = N-207), no DiagnosticReports entry after
  the 07:23:32 shutdown_stall (end of the staging session), no `aapl,panic-info` in NVRAM.
- Unified log: Persist 1e2 (07:23 boot) is empty; 1e3 (09:07 boot) is 361 KB of preallocated space with no flushed
  chunks. So both stopped within seconds of userland, before logd flushed: a hard stop, not a panic.
- Likely cause (Medium, I-094): XeGfx's PCI personality (`IOPCIMatch 0x00008086&0x0000ffff`, class 0x03, own
  IOMatchCategory) matches the live iGPU when the aux collection loads (~5 s after userland in Hybrid). Late matching on
  IGPU is what made IOPCIFamily FLR the iGPU in N-203/N-204 (I-093), followed by power loss. The probe itself only
  reads config space, so the reset would come from IOKit's matching (`getResources()`), not XeGfx code. Not proven:
  no log survived.
- The iGPU is on PCI in Discrete mode too (N-188 CoreDisplay log: IGPU@2 with IONDRVFramebuffer), so Discrete does not
  avoid the probe.

## Change for N-209 (rescue, applied from Windows)
OCEFI boot-args + `-x` (safe boot; backup `config.n209-pre.plist.bak`), mirrored in make_config. Safe mode does not
load the auxiliary collection (XeGfx, NVRM, NVRMFB, NVAccel); OpenCore-injected kexts (IGPUConsoleRange) still load.
Either BIOS mode should reach a slow, unaccelerated desktop. Then on the Mac: `XEGFX_MODE=uninstall sudo
tools/install.sh` in ~/src/XeGfx, remove `-x` from OCEFI, restart.

## For XeGfx
Do not match IOPCIDevice from a personality while the iGPU is live. Match IOResources (or a nub of our own) and look up
IGPU by path when started by the sysctl; check IOPCIFamily for the FLR-on-getResources condition before any claim.
