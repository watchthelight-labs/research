# Upstream port of the fetch-off fix (for Bash to turn into a PR in his own words)

Upstream: nullmoth/nvidia-macos-driver, main at 8b120f3 (v2.3.5, 2026-10-17). Local branch `fetch-off-zero-reads` in
~/src/upstream-nmd, one commit (67d9144), patch file beside this note. CONTRIBUTING.md says pull requests must be
written by a person who understands them and the template asks you to confirm you wrote the change yourself. The
code and this analysis came from Claude Code, so the PR text has to be yours and you have to be able to answer for
every line below. If you would rather not, the fix still belongs in our fork (it is already there as 179f619).

## Already upstream, no PR needed
The dropped-draw bug (a fetch pass whose fragment reads a colour attachment the pass lacks lost every draw) is fixed in
upstream head: nvmtl_fetch_set binds the dummy image for the missing attachment, and the comment there describes the
same symptom we hit on N-80. Our fork should take that fix from upstream when it merges 2.3.5 instead of exporting
e120760.

## What was wrong (the remaining defect)
With framebuffer fetch off, which is the WindowServer default (nvmtl_fbfetch_on returns 0 there unless
NVMTL_FBFETCH_WS=1), a pipeline whose fragment shader reads [[color(n)]] is built without descriptor set 3. The
shader's reads of binding 192..194 then hit nothing. Core Animation's uber fragment shader (fixed_frag_lpf_cpf) reads
color(0), color(1) and color(2) at its entry, so every compositor pass that uses it depends on an undefined value.
On the Legion (RTX 5070 Laptop, Tahoe 26.7.1) the same draw read zeros in a small test process and garbage in
WindowServer, which is how we noticed: identical inputs, different pixels.

## What the patch does, hunk by hunk
1. nvmtl_vk.h: a new field `fetch_zero` on nvk_pipeline, next to `fetch_mask`.
2. Pipeline creation: `fetch_zero` gets the shader's fetch mask when fetch is off (`fetch_mask` keeps it when fetch is
   on, as before). The pipeline layout block now adds set 3 when either field is set, so the layout matches the shader.
3. nvmtl_fetch_zero_set(): one descriptor set per process, allocated from the existing fetch pools with the existing
   fetch layout, every binding pointing at g_dummyImg (the zeroed 1x1 image the driver already uses for unbound
   textures) in SHADER_READ_ONLY_OPTIMAL, which is the layout upstream's own fetch_set uses for that image.
4. nvmtl_vk_cmd_bind_set: when `fetch_zero` is set, bind that set at NVMTL_FETCH_SET before the draw. It is bound
   whether or not the render pass has begun; descriptor set bindings persist into the pass.

Not a conformant Vulkan render pass (the image is not a subpass input attachment), but NVK lowers input attachment
reads to descriptor loads, so it works, and it is the same liberty upstream's fetch_set already takes.

## How it was tested
- On our fork (2.1.0 base, same logic): installed as the system plugin, a single-process replay of the Dock badge
  label draw over a filled target with the system device; the plugin logged the new set being made and bound, the
  draw rendered the glyph deterministically; a8rt (17 render-target cases) and the Metal self-test (16 ran, 0 failed)
  unchanged; one boot (N-109) with WindowServer on it: desktop and Dock blur normal.
- On upstream head: compiles with upstream's own clang invocation (0 errors). Not booted; our kexts are the fork's.
- It did not fix the Dock badge digit on its own (that investigation is still open), it only removes the undefined
  read.

## If you write the PR
Keep to the template: what was wrong, what this changes, how you tested it. Say the card and macOS version. Do not
tick the "I wrote this myself" box unless that is true for the words and the code you submit.
