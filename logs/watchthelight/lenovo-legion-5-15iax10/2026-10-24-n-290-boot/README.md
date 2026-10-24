<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-290/README.md | author: watchthelight </wtl> -->
# N-290 (2026-10-24 12:07 EDT): XeGfx 0.0.43 (interrupts-off watchdog), ws=1 with 900 s settle

Panel: Intel iGPU (OC log `Current FB at 0x70800000`, Hybrid). Stack: XeGfx 0.0.43, XeGfxAccel, XeGfxIntelFB 0.5,
plugin NvGfx-xe e60f462.

Result: **pass**. xe-guard: "stages 1-7 passed, WindowServer stable 900 s". The first run to survive the full
settle since I-116 appeared. WindowServer 1982 on the Intel GPU from about 12:10 and still the desktop at 12:27
(4451 IOPresentment transactions at the end of the settle, interrupts 34750, all handled, shim spins max 642 us). The
watchdog never fired.

## What Bash saw (reported in Claude Code, no photo, ~12:18)

- Terminal has a lot of visual artifacts; the frame rate is very low everywhere.
- Geekbench 6's Dock icon turned yellow after he clicked it.
- VRAM still shows 15 MB. System Information reads the IONDRV framebuffer's `IOFBMemorySize` (16384000, the
  firmware framebuffer), and "VRAM (Dynamic, Max)" is empty. The accelerator reports 11.4 GB of GART.
- Geekbench never completes. Cause found (I-117): its CPU benchmark worker `geekbench_avx2` runs ML workloads
  through MPSGraph on the GPU, and the NullMoth translator could not translate MPS's `depthwiseConv_3x3` with
  function constants ("Private pointer phi ... has differing structural sources; pointer merge storage mismatch
  Function vs Private", `geekbench-translate-fail.txt`). Metal then asserted in `MPSLibrary::MPSKey_Compile` and
  the worker aborted at 12:11:09. The app stayed open and idle.

## Is 0.0.43 the fix?

Pass after three crashes in a row (15-45 s) on a build that only added instrumentation. The instrumentation does
two things that could matter: a thread call wakes a CPU every 20 ms (which keeps cores and the package out of deep
idle, and N-288's panicking CPU was idle), and every spin section writes a per-CPU slot. One pass is not proof:
N-285 also lived 4 minutes. So N-291 runs XeGfx 0.0.44, the same code with `xegfx.irqoff_check=0` turning the
checker off. If N-291 crashes, the periodic wakeup is what keeps the desktop alive, which points at idle states.

XeGfxBlock back on after this run (config.n290-post.plist.bak), off again for N-291 (config.n291-pre.plist.bak).
