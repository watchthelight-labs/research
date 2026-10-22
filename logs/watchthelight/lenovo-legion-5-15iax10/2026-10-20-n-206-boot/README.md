<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-206/README.md | author: watchthelight </wtl> -->
# N-206: SSDT-DGPU-ON on + IGPUConsoleRange 0.4, no nvfbigpu, BIOS Hybrid (staged 2026-10-20 21:57 EDT)

Change: OCEFI ACPI Add enables SSDT-DGPU-ON again (WDGO only acts when DGON is called, it has no _INI), and
IGPUConsoleRange 0.4 replaces 0.3. Backup `config.n206-pre.plist.bak` (= N-205). Boot-args unchanged (no nvfbigpu),
so IONDRV gets the panel at boot exactly as in N-205 and nothing touches the iGPU slot.

IGPUConsoleRange 0.4:
- `sysctl debug.wtlacpi="<IOACPIPlane path> <name> [ints]"` evaluates an ACPI object live, e.g.
  `"/_SB/PC00@0/LPCB@1f0000/EC0 REJF 2"` (HPFF) or `"/_SB/WDGO DGON"`; `rescan` rescans PC00.RP01, `nv` reports
  whether an NVIDIA GPU is on PCI. Results in `sysctl debug.wtlacpi_log`.
- With `nvfbigpu=1` the attach runs in probe (waits for EC0, DGON, rescan, up to 10 s for the GPU) and the slot is
  claimed only if the RTX 5070 is there; otherwise it declines at once. It never terminates on the iGPU (I-093).

Plan on this boot: read IGPS/HPFF/PSTA, run DGON live, rescan, see whether the RTX 5070 appears and NVRM attaches.

## Result (2026-10-20 22:01 EDT): FAIL, hard power cut ~10-15 s after a live DGON
Boot itself: PASS (IONDRV desktop, trace ring and `debug.wtlacpi` work; ACPI plane paths are `/_SB/PC00/...`
without `@0`, absolute `\_SB...` names are refused with 0xe00002c2).

Live readings before the attach (`wtlacpi-pre-dgon.txt`):
- EC: IGPS 0, HPFF 0, CUMA 0, GSTA 0, GATY 0. The dGPU is NOT detached in Hybrid. N-203's premise (HPFF set) was wrong.
- PC00: TDGC 0, DGCX 0 (no GC6). RP01: VDID 0xae4d8086, GPRS(1) 1, PSTA 0 (power resource off), D3HT 0, D0ST 0,
  LASX 0, LDIS 1. PXSX NVID 0xffff.
- So Lenovo's PXP._ON would take its normal branch (GATY=2, PON, L23D, CMDR=7, wait for NVID): what DGON does.

DGON at 139 s: result 3 (timed out after its 1000 x Sleep(1) loop), PSTA now 1, NVID still 0xffff, LDIS still 1.
The unified log ends at 22:01:26.5, about 10-15 s after DGON, and the machine lost power (Bash: "Laptop hard
crashed"). Next boot 22:02:07, no panic.

## What this changes for I-093
N-203/N-204 ran DGON ~4 s after IGPUConsoleRange started and lost power ~15 s later; the FLR came in between, so it
was blamed. N-206 had no FLR and still lost power ~10-15 s after DGON. Revised cause (Medium): powering the RTX 5070
through PON while RP01's link stays down (Link Disable set as the ACPI field reads it, link never trains) makes the
platform cut power. The FLR finding stays true (0.4 avoids it) but is probably not what cut the power.
Note Lenovo's own PXP._OFF is `\STMC (4, 0)`, not POFF: the Hybrid power path goes through STMC, which DGON never calls.
