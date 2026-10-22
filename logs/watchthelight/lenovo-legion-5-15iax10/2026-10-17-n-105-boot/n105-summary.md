# N-105: the RG8 glyph is intact on the GPU; the whole digit pass comes out empty (2026-10-17, 12:39 boot)

Boot PASS (WindowServer 12:39:54, plugin 8c1d91bb39ee, en1 up, captive 200, no new crash reports).

## Capture
59773 lines (c-trace-badge.txt.gz). GPU-side readbacks of the six sampled glyph textures: the 46x24 RG8 "7" reads
288/2208 non-zero on the GPU, byte-identical to its CPU shadow on every sampled row; the 4x24 "1" 24/192 likewise;
the A8 textures (capsule 66x38, 230x108, 42x28, 28x28) all non-zero. The texture upload is not the fault.

## What the pass order shows (N-104 trace re-read)
The capsule is drawn in its own pass (A8, load action Clear) and the digits in a later pass (load action Clear) with
the "7" (fc 47=38), a second "7" draw (47=11), the "1", and two 22x28 BGRA draws (tf 1 and tf 3). Readbacks were
deduplicated per target texture, and the passes share textures, so the capsule-only readback of N-104 was the
capsule pass's; the digit pass's own result is one of the all-zero 128x128 readbacks. So the entire digit pass,
including its BGRA draws, produced nothing, while the same draws reproduce offline. That points at pass-level state the
replay never had: viewport, scissor, cull mode / winding, or the clear.

## Next: N-106
Readbacks per pass (tagged with the encoder pointer), and for every small-offscreen draw an "OFFS state" line with the
encoder's viewport, scissor, cull bits and depth state, plus an "OFFS pass" line with the clear colour.
