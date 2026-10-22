# N-110: the whole label pass, and a divergence on the simplest draw (2026-10-17, 13:36 boot)

Boot PASS (desktop verified through ScreenCaptureKit; WindowServer 13:37:12; plugin d5e70a39881d, zeroed-fetch).

## The label pass (192x192 ImageOffscreen this time), seven draws in order (replay/pass-n110.json)
0. 28x44 BGRA image, tf 1, colour ffffffff, quad px (1..29, 1..45), scissor 1 1 28 44, blend One/OneMinusSrcAlpha.
1. Pill outline 46x24 RG8, fc 47=38, colour e5, quad (0..46, 2..26), scissor 0 0 70 45.
2. Textureless fill, fc {5, 29=62}, 6-vertex triangle list, colour e5, a strip x 8.6..37.4 y 10.6..17.4, scissor 0 0 52 28.
3. Pill again with fc 47=11: 16 vertices, 24 indices (a nine-slice), scissor 52x28. Only 4 vertices were dumped.
4. Pill piece 4x24 RG8, 47=38.
5. Digit 22x28 BGRA, tf 1, colour ffffffff, blend src ZERO / dst OneMinusSrcAlpha: a knockout (destination out).
6. Digit 22x28 BGRA again, tf 3 with 47=25, colour e5, blend One/OneMinusSrcAlpha.
Pass readback (zeroed reads): the same e5 strip with hairline holes as N-106. Nothing at all in rows 28..45 where
draw 0 should show its lower half.

## Offline whole-pass replay (passreplay.m, same inputs, draw 3 skipped)
Draw 0 paints its image (colourful pixels at x 1..13), the knockout and redraw behave as a knockout would. So on the
same driver, the same draw 0 draws offline and leaves nothing in WindowServer. Draw 0 and draw 5 are both small BGRA
textures created by CoreAnimation inside WindowServer; the N-105 GPU-side texture check covered only A8 and RG8.
Suspect: the small BGRA glyph textures are empty or stale on the GPU in WindowServer (while their CPU shadows are
right), which would make draw 0 invisible and the knockout cut only stale edge pixels.

## N-111
GPU-side readback of the small BGRA glyph textures (every row), 1 KiB vertex dumps for the nine-slice pill draw.
