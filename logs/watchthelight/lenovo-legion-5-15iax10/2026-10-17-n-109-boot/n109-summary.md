# N-109: zeroed destination reads, badges still plain circles; the white screenshots were a capture artefact (2026-10-17, 13:27 boot)

Boot PASS (WindowServer 13:28:00, plugin 2696b7d096d0 = zeroed-fetch fallback, conf NVMTL_NO_FBFETCH=1, en1 up).

## Findings
- The desktop renders and the Dock blur looks right (full.png, taken before the trace; sck-full.png through
  ScreenCaptureKit afterwards). Both Dock badges (System Settings "1", badgeapp "71") are still solid white circles
  without a digit (sck-dock-3x.png). Fix B (destination reads bound to a zeroed dummy) did not surface the digit.
- The "white screen" of N-108 was NOT the display: after badge-trace.sh runs, `screencapture -x` returns an all-white
  image (always 72937 bytes) while ScreenCaptureKit shows the real desktop (sckscreen.swift: 867 white pixels of a
  1280x800 capture). The legacy capture path breaks once the trace's completion-time readback blits have run inside
  WindowServer's command buffers; it stays broken. In N-108 the first screenshot was white before any trace, so the
  trigger is not fully understood, but the N-108 verdict "screen blank" is unproven. Launchd carries no NVMTL keys, so
  N-108 did run with fetch on, and its label pass readback was identical to N-106's.
- The 24 per-pass readbacks of this capture were all consumed by chained passes, so the label pass with zero reads was
  not read back. The trace now dumps every draw of a flagged pass (OFFS PASSDRAW + VBUF/FBUF/indices), reads back only
  glyph-flagged passes, and the GPU glyph/buffer readbacks are off.

## Next: N-110
Capture the whole label pass (pill, fill, 47=11 pill, pill piece, digit tf1, digit tf3) with its per-draw inputs and the
pass readback, then replay the sequence offline draw by draw with intermediate readbacks, and find the first draw whose
result differs from WindowServer's. Verify screens with ScreenCaptureKit, never with screencapture after a trace.
