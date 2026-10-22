# N-101: full badge draw dump and the offline replay (2026-10-17, 11:31 boot)

Boot PASS (WindowServer up 36 s after boot, plugin dock-trace 83af588 sha 10d025405240, en1 IP-9, captive 200).

## Capture
`badge-trace.sh` during a `badgeapp 71` update: 44105 trace lines (c-trace-badge.txt.gz), 4 glyph textures dumped
once each: 66x38 A8 capsule, 46x24 RG8 "7", 4x24 RG8 "1", 28x28 A8. The digit draw: encoder 0x7f8712114800, target
320x64 BGRA8 `com.apple.coreanimation.ImageOffscreen` (the label offscreen), blend One / OneMinusSrcAlpha, indices
0 1 2 2 3 0, VBUF[1] 192 B (quad 83,18 to 129,42, colour e5e5e5e5), FBUF[1] 512 B, FBUF[2] 512 B, sampler nearest
clamp. The label offscreen is then sampled by draws into a 192x192 offscreen (fc_texture_function 11, then 1) and
combined back into a 320x64 target with two textures (fc 12, 35, blend function 30) before the glass passes.
The trace cut every fc list at 300 characters, so the constants above index 38 of the digit draw are unknown.

## Offline replay (native/tools/dock/replay.m, evidence replay/*.json)
- Harness validated: the in-process CATextLayer draw (text-inproc.json, 64x48 BGRA, fc 51 53 and vertex fc 53)
  replays as a white 64x48 box. Without fc 53 (texcoord count) on BOTH stages the uber fragment outputs nothing,
  which is why every earlier replay was black: the constants were incomplete, not the driver.
- The digit draw replays once fc 53=1 and a texture-function-3 companion constant (47) are set, but for every value of
  fc 47 in 0..16 the RG8 (coverage in G) and the A8 glyph give the same uniform quad: this path reads only the texel
  alpha. A real digit needs the coverage taken from G, so the Dock draw must set a constant we have not captured yet.
- Descriptor swizzles (alpha from green) and buffer-backed glyph textures behave the same in-process.

## In-process CoreAnimation
- cartext.m / badge.m: CATextLayer text and a rounded red badge with a white 7 render correctly through CARenderer
  (the earlier "CARenderer draws nothing" was a missing CATransaction flush). CA uploads CATextLayer text and every
  gray+alpha CGImage variant as BGRA8; alpha-only images become A8 and render. No in-process path produced an RG8
  glyph texture, so the Dock's RG8 digit path cannot be reproduced without WindowServer.
- glassbadge.m: a layer with the glassBackground CAFilter is skipped entirely by CARenderer (no draws), so the glass
  stage cannot be tested in-process either.

## Plugin changes (NvGfx dock-trace 793e261)
Full fc lists in the draw line, a "OFFS vfc" line with the vertex function's constants, "PIPE" lines with the whole
pipeline descriptor (vertex descriptor, blend, depth, fc of both stages), small BGRA texture dumps up to 512 px, all
behind the file flag /Library/GPUBundles/nvmtl/wstrace.alltex (or /tmp/nvmtl-alltex); debug builds trace any process
(the release image loaded beside a debug one wipes NVMTL_* from the environment, so flags are files, not variables).
N-102 = reboot for this build (installed via mv, sha 6b415a84a1be), then the complete digit draw replay.

## Online check (Bash asked)
No report of missing Dock badge digits for the NullMoth driver on the web or in nullmoth/nvidia-macos-driver issues.
Related there: #72 and #79 (Tahoe icon layers, visible functions and descriptor swizzle, fixed in 1.14.0), #246
(2.1.0 Terminal text overlap, reporter says fixed by 2.3.3), #260 (5070 Ti: text missing on web pages, no details).
