# N-123 offline replays (installed release plugin 2a7fab7702d9, NvGfx ec6944b)

All run on the system device from a user process after the N-123 capture.

- u16tex: 15x30 RGBA16Unorm / RGBA16Float / BGRA8 textures uploaded with replaceRegion (managed and shared), getBytes
  round trip identical, sampled into BGRA8 and RGBA16F targets with linear, nearest and half samplers: no wrong pixel.
- u16buf: the same glyph as a buffer-backed linear texture (newTextureWithDescriptor:offset:bytesPerRow:) with pitches
  128, 256, 512 and offsets 0, 256, 4096, managed and shared, plus CPU writes after creation and blit uploads from a
  staging buffer with pitches 120..512: all correct. Pitch 120 (15 px * 8 B, unpadded) returns nil from the plugin.
- dithertest: the N-107 22x28 glyph pass replayed with CoreAnimation's own metallib. Menu bar constants (47=25, 28=3):
  the pass is a MASK draw, colour comes from a uniform (a gradient texture still draws e5e5e5e5). Dock digit constants
  (47=0, 28=1, 21=1, 36=32, fc 8 dither with a 32x32 noise texture at slot 9): an IMAGE draw, the texture colour comes
  through (gradient fill reproduced, uniform fills identity, 16-bit values decode linearly); the menu bar mask glyph
  rendered through that mode is black-on-alpha because its colour channels are zero, which is correct. With the SPV
  cache off the translation is deterministic (8 identical runs).

Nothing offline reproduces the missing digit. The capture shows the digit as a 15x30 RGBA16Unorm image (fmt 110) drawn
with the dither constant into the 128x128 scratch offscreen (19:52:10.369); N-124 dumps that texture, reads the scratch
back and records the composite.
