# N-111: every glyph texture is intact on the GPU; the divergence is not in the inputs (2026-10-17, 13:47 boot)

Boot PASS (desktop verified through ScreenCaptureKit; WindowServer 13:47:57; plugin 8ece931b956b).

## GPU-side readback of every texture the label pass samples (c-trace-badge.txt.gz)
28x44 BGRA image: 43 rows compared, 43 identical to the CPU shadow. 22x28 BGRA digit (both): 27 of 27 identical.
Pill 46x24 RG8 and 4x24 RG8: all rows identical. Capsule 66x38 A8 and the other A8 masks: identical. (The 128x128 and
160x96 textures that differ are render targets read at encode time, before the GPU ran; not inputs.)

## Where this leaves I-057
Every input of the label pass is now verified on the GPU: textures, vertex buffers, mvp, texture matrix, uniforms
(N-107), constants, scissor, viewport, blend state, indices. The same pass replayed offline on the same driver and
build (passreplay.m) draws the 28x44 image and the digit; inside WindowServer the pass leaves the image area empty and
the digit as hairlines. Neither the destination read value (fetch on in N-108, zero in N-109) nor the texture uploads
explain it. What differs between WindowServer and a test process for the same draw must be in how the pipeline is
built or bound there: the specialised SPIR-V WindowServer actually runs (its pipeline/SPV cache entries versus a fresh
translation), the bindless/table paths, or the fetch-pass restart logic. A direct check is to dump, from inside
WindowServer, the SPIR-V hash of the pipeline used by the digit draw and compare it with the replay process's.

## Fixes that stay (NvGfx dock-trace)
- nvmtl_fetch_set no longer drops draws whose fetch mask names an attachment the pass lacks (e120760): this was the
  N-80 blank desktop.
- With fetch off, [[color(n)]] reads bind a zeroed dummy instead of an unbound band (179f619): deterministic reads.
- Trace infrastructure (file-flag gated): untruncated constants, vertex constants, pipeline descriptors, per-pass
  completion readbacks, GPU-side texture and buffer readbacks, whole-pass draw dumps.
