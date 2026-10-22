# N-106: the digit pass draws an inverted glyph (2026-10-17, 12:46 boot)

Boot PASS (WindowServer 12:47:18, plugin fafefae06012, en1 up, captive 200, no new crash reports).

## Capture
60902 lines (c-trace-badge.txt.gz), 24 per-pass readbacks tagged with their encoder. Digit pass (enc 0x7fdb57995e00,
load Clear, clear 0 0 0 0): viewport 0 0 128 128; draws in order: "7" RG8 fc 47=38 (scissor 0 0 70 45), a textureless
fill (scissor 0 0 52 28), "7" again with fc 47=11 (scissor 52x28), "1" RG8 47=38 (70x45), 22x28 BGRA tf 1 and tf 3
with 47=25 (70x45). Cull 0, no depth state. The capsule pass (enc 0x7fdb57994800) uses scissor 0 0 128 88.

## The digit pass's own readback (same texture as the capsule pass, read right after this pass)
The digit quad (x 0..46, y 2..26) is FILLED with the label colour (e5e5e5e5) except for thin zero lines exactly where
the glyph texture has its edges (G around 0x80): an inverted glyph, a bright rectangle with the "7" cut out as hairlines.
That rectangle is what the glass stage turns into the hollow rectangle seen inside the badge circle (N-104 chain).
The glyph texture is a distance-field style mask (G up to 0x80 at the strokes, 0 elsewhere).

## Offline (replay.m with the N-103 inputs)
With gradient textures (dfdx or dfdy non-zero) and a distance-bar texture the offline path never inverts: coverage grows
with G (left quarter mean G 86, right quarter 216 for a horizontal gradient). So an input the GPU saw differs from the
encode-time dump. The uniforms are the candidate: CoreAnimation can write a uniform ring after encoding, and the N-101
dump of FBUF1 looked like stale blur-kernel data. Derivatives translate one to one (DPdx/DPdy/Fwidth), so they are not it.

## Next: N-107
At pass end the plugin now copies the glyph draw's bound FBUF1, FBUF2 and VBUF1 ranges (512 B each) into shared
buffers and logs them at completion ("GPU FBUF1 enc ... +off/len: hex"); every row of a small glyph is dumped. Replay
with those bytes must reproduce the inverted quad; then the shader's coverage math with the real uniforms is the target.
