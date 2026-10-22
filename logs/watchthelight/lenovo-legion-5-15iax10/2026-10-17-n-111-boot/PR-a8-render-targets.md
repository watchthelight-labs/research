# PR 2: NVMTLDriver: A8Unorm render targets take alpha in the red lane

Branch `a8-render-targets` in ~/src/upstream-nmd (one commit on upstream main 8b120f3, v2.3.5).
Files: plugin/NVMTLDevice.m, plugin/NVMTLLibraryLoad.m, plugin/NVMTLObjects.h, plugin/NVMTLObjects.m,
translator/translator/src/passes/mod.rs, translator/translator/src/passes/stage_output/mod.rs, translator/wrapper/src/lib.rs.
Patch: 0001-a8-render-targets.patch beside this file.

Draft description:

**What was wrong**

An A8Unorm colour attachment is an R8_UNORM image on the Vulkan side, but the translated fragment shader still wrote its
alpha to the fourth output lane. A render pass into an A8 target left the red lane untouched, so Core Animation's glyph
masks and the Dock badge label (both drawn into A8 offscreens) came out as a filled box or as nothing. The write mask and
the blend factors for alpha were applied to the alpha lane the image does not have, and a clear colour's alpha never
reached the lane either.

**What this changes**

The translator gets an `a8_targets` mask from the plugin (bit n = attachment n is A8Unorm) and, for those attachments,
writes the fragment output's alpha to lane 0. The plugin builds the mask from the pipeline descriptor's attachment
formats, remaps the alpha write mask and the alpha blend factors onto the red lane for those attachments, and lands a
clear colour's alpha in the red lane as well, so clear-to-alpha behaves as it does on Apple's drivers. Pipelines without
an A8 attachment are untouched (mask 0, the translation key is the same as before).

**How I tested it**

RTX 5070 Laptop (GB206), macOS 26.7.1 (25G241), Legion 5 15IAX10. A render-target test (34 cases: 11 formats, blend
off and on) checks a known pixel after a draw: the A8Unorm cases now read ff for a full write, 40 for a half-covered
blend over a cleared target, ff for a saturating blend, 7f for a clear to alpha 0.5; before the change the A8 cases read
00. The Metal self-test (16 ran, 0 failed) and the Dock's minimized-window tiles are unchanged. In WindowServer the
change has been in my plugin since boot N-96 (2.1.0 base) and on the 2.3.5 base since N-112: text in glass controls and
the Dock labels render; the Dock badge's own missing digit turned out to be a different problem.

Side note from the same test, not part of this PR: R8Unorm_sRGB and RG8Unorm_sRGB render targets read 00 and the
linear value respectively where the sRGB-encoded value is expected, so single- and two-channel sRGB targets are
another open defect.
