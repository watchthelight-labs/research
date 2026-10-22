# N-103: every input of the digit draw captured, stage one proven (2026-10-17, 12:26 boot)

Boot PASS (WindowServer 12:26:44, plugin db9d95beb4f2, en1 up, captive 200, no new crash reports).

## Capture
52974 lines (c-trace-badge.txt.gz). The digit draw this time goes into a 256x320 ImageOffscreen (CoreAnimation packs
the label into whatever offscreen it has; 128x128 in N-102, 320x64 in N-101). Vertex buffer 2 (mvp) and 3
(texture_matrix) are dumped now: texture_matrix = (1, 1, 0, 0), mvp maps the quad to target pixels x 0..46, y 2..26.
Three target readbacks happened (84x60 and 76x60 FlattenSurface passes from A8 glyph draws); the label pass was skipped
because 256x320x4 exceeded the 256 KB cap.

## Replay (replay/badge-digit-n103.json, env REALBUF=1 binds the captured mvp and texture_matrix)
With every captured input (vertex data, mvp, texture_matrix, uniforms, constants 47=38 51=1 53=1 and vertex 53=1,
indices) at the real 256x320 target, a half-covered RG8 glyph draws exactly its half at x 0..22 / 23..45, y 2..25, and a
fully covered one the whole 46x24 quad at 236 grey. So the digit draw is correct on our driver given CoreAnimation's
inputs. What remains unknown is WindowServer's actual label content (upload or ordering) and the downstream passes.

## Plugin (NvGfx dock-trace, next build)
Readback cap raised to 2 MB; chained readbacks: a pass that samples a texture already read back is read back too
("OFFS CHAIN" line), up to 24 targets, so the next capture should show the label, the field pass and the combine.
