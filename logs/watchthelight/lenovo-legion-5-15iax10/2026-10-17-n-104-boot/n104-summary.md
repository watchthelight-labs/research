# N-104: the label offscreen read back after the GPU ran: capsule yes, digit no (2026-10-17, 12:32 boot)

Boot PASS (WindowServer 12:33:27, plugin e3c17875a2e1, en1 up, captive 200, no new crash reports).

## Capture
60235 lines (the 60000 cap was reached at the end; c-trace-badge.txt.gz). 19 completion-time readbacks, 1380 chain
lines. The digit draw ("7" 46x24 RG8, fc 47=38) went into a 128x128 ImageOffscreen (0x7fe654e21c20). Its readback,
taken when the command buffer completed, holds exactly the capsule: a 66x38 rounded-rect outline at the top left (border
bright, interior 35353535 premultiplied grey, matching the A8 mask border/interior values) and NOT ONE non-zero pixel
anywhere else in the 128x128. The RG8 digit draw produced nothing in WindowServer. The 256x320 chained readbacks show
the Dock tile with the large glass circle and a small hollow rectangle inside it (the capsule through the SDF glass),
no digit: consistent with what the screen shows.

## What this means
The same draw with every captured input (vertex data, mvp, texture_matrix, uniforms, constants, indices) draws the
glyph correctly offline (N-103). The one input the trace only ever read from the CPU side is the RG8 glyph texture
itself (the GLYPH dump uses getBytes, which returns the managed shadow). The A8 capsule texture, uploaded the same way
by CoreAnimation, reaches the GPU. So the prime suspect is now the GPU copy of the RG8 (fmt 30) glyph texture: empty or
stale on the GPU while the CPU shadow has the coverage. The pixel-size table has RG8 at 2 bytes (NVMTLDevice.m), so the
fault, if there, is in the upload or dirty-region path CoreAnimation takes for these textures, not the table.

## Next: N-105
The plugin now blits every sampled A8/RG8 glyph texture into a shared buffer when the pass ends and logs the GPU-side
bytes at completion ("GLYPH GPU <ptr> ... nonzero", rows). A8 is the control (expected non-zero), RG8 the suspect.
