<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-203/README.md | author: watchthelight </wtl> -->
# N-203: SSDT-DGPU-ON v2 (run-time DGON) + IGPUConsoleRange 0.3, BIOS Hybrid (2026-10-20 21:12 to 21:16 EDT)

Read from Windows on 2026-10-20 ~21:25 EDT (OCEFI logs, Tahoe Data volume via `scripts/diag/apfs-read.py`, NVRAM,
Windows event log). Times UTC unless marked.

## Symptom (Bash, reported in Claude Code, no photo)
"Last few boots on macos failed like the laptop shut off."

## What the logs show
| OC log (UTC) | FB | legion-diag boot dump |
|---|---|---|
| 01:06:23 | 0x70800000 (Hybrid) | N-202, ran to a desktop, ended with a shutdown_stall at 01:11:42 |
| 01:11:59 | Hybrid | 20261021-011201Z: the 20 s dump completed (dmesg, ioreg), nothing later |
| 01:13:26 | Hybrid | 20261021-011327Z |
| 01:14:51 | Hybrid | 20261021-011452Z |
| 01:15:55 | Hybrid | 20261021-011557Z: only 00-info.txt, so it stopped before the 20 s dump |

Windows started at 01:16:38. So each N-203 boot lasted about 40 to 80 s. No panic file on OCEFI, no panic report in
/Library/Logs/DiagnosticReports, no `aapl,panic-info` in NVRAM, no shutdown_stall (macOS did not shut down by itself).
A power cut with no panic fits the EC doing it.

## Lenovo ACPI, read 2026-10-20 (probe scan tables, Intel iasl-win 20260408)
- `GATY = 2` is not a GPU mode switch. Lenovo's own `PXP._ON` (SSDT18) writes it every time the dGPU powers up in
  Hybrid (Windows runtime D3cold exit). `GATY = 0` in `_OFF`.
- EC byte 0x8E: `IGPS` (2 bits, the Vantage GPU working mode), `CUMA` (UMA flag; `PXSX._STA` returns 0 while it is
  set), `HPFF` (detached), `GSTA`. `WEJF(4, x)` and `WEJF(5, x)` write HPFF and CUMA together; `_EJ0` sets both.
- `GZFD.HTPL` ejects the dGPU only for IGPS 1, or IGPS 2 on battery. Windows reports IGPS 0 now
  (`LENOVO_GAMEZONE_DATA.GetIGPUModeStatus` = 0), the RTX 5070 is present in Windows, and the 1401 probe's Linux saw it
  at 00:06.0/02:00.0 in Hybrid. Windows and Linux power it through `_PR0` (PXP._ON) during enumeration; macOS never
  evaluates `_PR0`, which fits RP01 `nolink` under macOS.
- Lenovo's `_ON` exits GC6 (`GC6O`) instead of running PON when `TDGC == 1`; DGON v2 always runs PON + L23D.

## Likely cause, revised (Medium-Low)
The first N-203 boot was still running at 23 s (dmesg, WindowServer up), and the attach runs ~4 s after
IGPUConsoleRange starts. The cuts came 40-80 s in, around the AuxKC (NvGfx) load at ~60 s. So either the attach did
work and NVRM bringing up the RTX 5070 in Hybrid (with nvrmtgp/nvrmnvpcf/nvrmphysctl) tripped the EC, or the attach
left the GPU half powered. N-204 separates the two.

## Change for N-204 (applied from Windows, replaces the "SSDT off" change made first)
OCEFI `config.plist`: SSDT-DGPU-ON enabled again (as N-203) plus `-nvoff` in boot-args (backup of the N-203 config:
`config.n204-pre.plist.bak`), mirrored in `native/tools/make_config.py`. BIOS Hybrid. Expected: no power cut, IONDRV
desktop, and the RTX 5070 on PCI (`ioreg -p IOService -n PXSX`, IGPUConsoleRange's DGST/DGI values). Then:
- no cut + GPU present: the attach is safe; N-205 = NvGfx on, without nvrmtgp/nvrmnvpcf/nvrmphysctl.
- cut again: the attach itself is the problem; DGON v3 = Lenovo's own `WEJF(5, 0)` + `PXP._ON()` (GC6 aware).

## For the Mac session
Read the kext's DGST/DGI1-3 after N-204 and check `lspci`-equivalent state. Log each DGON step to NVRAM from the kext
before calling it, so a power cut leaves a breadcrumb.
