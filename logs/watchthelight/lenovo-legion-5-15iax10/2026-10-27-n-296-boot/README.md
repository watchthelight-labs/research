# N-296: Hybrid xe-guard run, nvram_trace=0 (PASS)

Date: 2026-10-27, OpenCore start 17:02 EDT. BIOS GPU mode Hybrid, OC log FB at 0x70800000 (Intel iGPU), OCEFI config with
XeGfxBlock off (Kernel:Add 29). XeGfx 0.0.45, XeGfxAGDC 0.1.1 with FBCAPEX on, xe-2.6.2 superset plugin e429fca1.

## What changed from N-295
Only `xegfx.nvram_trace=0` (N-295 ran with 1 and stalled 16 min into its desktop, I-116). Hypothesis: the trace wrote
NVRAM every 250 ms, EDK2 runtime variable writes go through SMM, and a CPU held in SMM does not answer the NMI of a
TLB-shootdown rendezvous, which matches the "23 of 24 responses" panics.

## Result
xe-guard verdict `pass`: stages 1-7 passed, post rc 0, WindowServer on the Intel GPU stable for the whole 3600 s
settle (pid 2079 from 17:05:08 to 18:06:06), no panic report. The desktop stayed up after the verdict as well.
During the hour Bash used it normally, including a full Geekbench 6 CPU run (2447 single / 17755 multi,
`geekbench6-cpu-2447-17755.png`). Files: `guard/` (verdict, post, ws, ws-progress, xegfx logs, sysctl, ioreg) and
`opencore-2026-10-27-210239.txt` (redacted).

One pass is not proof for I-116 (N-290 died at 88 min). N-297 repeats it for 2 h with disk and GPU load.

## Bugs seen on the Intel desktop
- I-119: clear squares and strips where the cursor moves or a window is dragged over the translucent terminal.
  NMIntelFB has no hardware cursor, so WindowServer draws a software cursor; partial recomposites over the
  blurred terminal come out clear. Open.
- I-120: symbol icons (System Settings sidebar, the Geekbench 6 Dock icon) drawn as flat yellow shapes
  (`settings-icons-yellow.png`, `dock-yellow-icon-1728.png`). Found and fixed, see below.

## I-120 cause and fix
Symbol image layers are RG8 textures with swizzle (r, r, r, g). Unswizzled, white opaque reads (1, 1, 0, 1) =
yellow. Tests in `i-120/` (built with clang, run on the live Intel device):
- `swztest.m`: plain and IOSurface textures, compute read and sample: correct.
- `swz2.m`: fragment sampling, descriptor swizzle and `newTextureView...swizzle:`: correct; the unswizzled control
  gives 255 255 0 255, the yellow on screen.
- `swz3.m`: textures from an `MTLHeapTypeAutomatic` heap came out yellow/red; placement heaps were correct.

`-[NVMTLHeap nvmtlPlacedTexture:charge:align:]` (plugin/NVMTLObjects.m), which places textures for automatic
heaps, never called `nvmtl_texture_desc_swizzle`. The fix (NvGfx xe-2.6.2 103e011) adds that call. With the fixed
release plugin installed, `swz3` reads correct for both heap types. NullMoth 2.6.2 has the same gap
(`upstream-note-i120.md`).
