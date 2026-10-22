<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-202/README.md | author: watchthelight </wtl> -->
# N-202: SSDT-DGPU-ON v1 + NVRMFB proxy, BIOS Hybrid (2026-10-20 21:06)

Result: desktop on Apple's IONDRV (the N-201 fallback worked), **not accelerated** (Bash). The RTX 5070 was still absent
from PCI: RP01 `nolink` at the 2.8 s scan (linkStatus 0x5081), NVRM/NVRMFB/NVAccel did not load (no device), the SSDT's
WDGO device exists (`_STA` 0x0B), IGPUConsoleRange 0.2 saw no NVIDIA GPU and let IONDRV keep the panel.

Why v1 could not work: in Hybrid mode Lenovo's EC detaches the unused dGPU (GZFD.HTPL sends an eject request and sets
HPFF), and PXP._ON refuses to power the GPU while HPFF is set (`REJF(2) != 1 || DSMF == 2`). Clearing HPFF needs the EC,
which is not usable during `_INI`. Lenovo's own attach (HTPE/HTPL) is: WEJF(4, 0), PXP._ON, Notify(PXSX, 0).

N-203: SSDT-DGPU-ON v2 (`WDGO.DGON`, called at run time) does that sequence with a bounded wait; IGPUConsoleRange 0.3
calls it 4 s after start, rescans PC00.RP01, logs the EC values before the attach (IGPS, HPFF, PXP status), and gives the
slot back to IONDRV if no NVIDIA GPU appears within 24 s.
