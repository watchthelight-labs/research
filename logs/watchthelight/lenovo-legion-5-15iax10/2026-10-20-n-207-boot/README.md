<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-207/README.md | author: watchthelight </wtl> -->
# N-207: SSDT-DGPU-ON v3, BIOS Hybrid (staged 2026-10-20 ~22:15 EDT)

N-206 found RP01's Link Disable (config 0x50 bit 4, ACPI `LDIS`) set on a boot where DGON never ran, while
IOPCIFamily logged link control 0xc40 (clear) at 1.8 s, so it is set after boot (IOPCIFamily sets it when it saves a
bridge whose shadow has the SleepLinkDisable flag, IOPCIBridge.cpp ~2042). Lenovo's PXP._ON never clears it, and
DGON v2 timed out with the GPU powered and the link down, followed by a power cut.

v3 DGON: as v2, then records LDIS in DGI4, clears it, waits up to 1 s for NVID 0x10DE; on failure sets LDIS again
and runs Lenovo's POFF (reset, power off) at once, so the dGPU is never left powered without a link.
Previous AML on OCEFI: `ACPI/SSDT-DGPU-ON.v2.aml.bak`. Boot-args unchanged (no nvfbigpu).

## Result (2026-10-20 22:09 EDT): FAIL, power cut again (Bash: "Yep, power cut")
- Before: LDIS 1 at 45 s (no DGON yet), PSTA 0. DGON v3 at 53 s: DGI4 = 1 (LDIS was set), result 3 (no link
  within 1 s of clearing LDIS), and afterwards PSTA 1, LDIS 1, LASX 0, NVID 0xffff: Lenovo's POFF did not drop power
  (its `\PPIN.OFF (PWRG)` runs only when `GPPR () == One`). The laptop lost power seconds later; next boot 22:10:06.
- Three live power-ons (N-206, N-207, and the probe-time DGON of N-203/N-204) all ended in a power cut. Clearing
  Link Disable does not bring the link up, and the power-off path does not undo the power-on.

## Decision
The Hybrid dGPU hot-attach is stopped: each attempt is a hard power loss for the laptop and its disks. OCEFI
config: SSDT-DGPU-ON disabled again (backup `config.n208-pre.plist.bak`), make_config.py mirrored. The NVRMFB proxy
plan for accelerated Hybrid depends on this attach, so it is parked with it.
