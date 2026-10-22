# N-102: untruncated constants, the replay harness made faithful (2026-10-17, 12:13 boot)

Boot PASS (WindowServer 12:13:44, plugin 6b415a84a1be, en1 up, captive 200, no new crash reports).

## Capture
`badge-trace.sh` with both flags: 55061 lines (c-trace-badge.txt.gz), 149 texture dumps, 4771 "OFFS vfc" lines,
6 "PIPE" descriptor lines (pipelines made before the flag were cached). The digit draw ("7", 46x24 RG8) into the
128x128 label ImageOffscreen has fragment constants 5=1 7=1 15=1 28=3 29=62 32=1 47=38 51=1 53=1 (59..62 zero vectors),
vertex constant 53=1. The capsule (66x38 A8) uses the same set with 47=25. The in-process rounded rect used 47=10.
Vertex buffer 0 is not bound for these draws; vertex buffers 2 (mvp) and 3 (texture_matrix) were not dumped yet.

## Replay (native/tools/dock/replay.m)
- With vertex constant 53 the uber vertex stage reads `texture_matrix` from vertex buffer 3 (bindrefl.m). Unbound in the
  harness it was zero, so every fragment sampled texel (0,0): a glyph covered only on one half drew nothing or the whole
  quad. With an identity matrix bound the half-covered glyph draws exactly its half, on the known-good in-process text
  draw and on the digit draw alike. The harness is now faithful.
- With the real constants, fc 47=38 takes the coverage from G (coverage in R draws nothing), the A8 capsule mode 47=25
  takes it from alpha. Output colour 236 grey for vertex colour e5 (blend function 62). So the digit draw itself renders
  correctly offline given correct inputs: the remaining unknowns in WindowServer are the real texture_matrix (buffer 3),
  and whatever happens downstream of the label (tf 11 field pass, the fc 12/35 blend-30 combine, the glass passes).
- Readback of render targets at encode time is meaningless (the GPU has not run yet): the dumps of the 128x128
  offscreens read as zeros. The plugin now copies the glyph pass's target into a shared buffer when the pass ends and
  logs the pixels in the command buffer's completion handler ("TGT READBACK", proven in-process on an A8 glyph draw).

## Next: N-103
Plugin dock-trace with the target readback and VBUF[2..3] dumps (release sha in the tracker row). The readback shows
whether the label offscreen contains the digit in WindowServer; the buffers complete the replay either way.
