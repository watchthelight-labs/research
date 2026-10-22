# N-107: root cause of the missing badge digit (2026-10-17, 12:54 boot)

Boot PASS (WindowServer 12:55:13, plugin 32f7db470f6a, en1 up, captive 200, no new crash reports).

## What the full dumps showed
- GPU-side bytes of the digit draw's uniform buffer (FBUF1) and vertex buffer are identical to the encode-time dump.
  Every input of the draw was already right. (FBUF2 differs only beyond its 4 used bytes.)
- With all 24 rows visible, the "46x24 RG8" texture is not a digit: it is the rounded pill outline of the label, and
  the 4x24 RG8 is a pill piece. The digits are the two 22x28 BGRA draws that follow the label fill in the same pass:
  a black glyph image drawn with tf 1 (colour ffffffff) and the glyph again with tf 3 and fc 47=25 (colour e5).
- The uber fragment (fixed_frag_lpf_cpf) reads its colour attachments [[color(0..2)]] through three input attachments
  at its entry, before any constant check, and blend function 62 (fc 29) uses that destination value.

## The root cause
`/Library/GPUBundles/nvmtl/nvrm610.conf` had `NVMTL_NO_FBFETCH=1`, and the plugin keeps fetch off in WindowServer
anyway (nvmtl_fbfetch_on, N-80). With fetch off, those destination reads hit an unbound input attachment: undefined.
In a small process the read happens to return zeros and the digit renders black over the label (replay.m, draw 3 over
an e5 fill: mean 18 18 18 alpha 252); in WindowServer the read returns something else and the draws come out as the
inverted hairlines of N-106. Same inputs, undefined read, different outcome.

Why fetch was off: N-80 turned it on in WindowServer and the desktop went blank (memory note f1e04349). The reason is a
second bug: the uber fragment's fetch mask names three attachments while CoreAnimation's passes have one, and
nvmtl_fetch_set returned no descriptor set for a missing attachment, so EVERY uber-shader draw was skipped. The N-81
fetch-copy emulation has the same drop (nvmtl_fcopy_set).

## Fix (NvGfx dock-trace e120760, release sha f7ac5c5f6357 installed via mv)
nvmtl_fetch_set binds the pass's first colour attachment for a fetch of an attachment the pass lacks (the read is dead
for the enabled attachment count; Metal tolerates it) instead of dropping the draw. In-process with fetch on: the digit
draw renders the black glyph, CARenderer badge/text tests unchanged, a8rt 17 ok, rg8 ok, metal_selftest 16 ran 0 failed.

## N-108
Conf: NVMTL_NO_FBFETCH=0 and NVMTL_FBFETCH_WS=1 (backup ~/.cache/legion/nvrm610.conf.pre-n108; rollback = mv it back
and reboot, doable blind from the autostart session). Expect: the badge digit on screen, and possibly the blocky Dock
blur (I-049, same unbound-fetch cause per the N-77..N-80 note) fixed as well. Watch for N-80-style blanking and
I-048-style stale content (fetch passes use GENERAL layout and a self-dependency).
