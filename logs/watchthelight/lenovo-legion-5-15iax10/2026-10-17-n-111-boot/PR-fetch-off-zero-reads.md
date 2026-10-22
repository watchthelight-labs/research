# PR 1: NVMTLDriver: give fetch-off [[color(n)]] reads a zeroed image

Branch `fetch-off-zero-reads` in ~/src/upstream-nmd (one commit on upstream main 8b120f3, v2.3.5).
Files: plugin/nvmtl_vk.c (+46), plugin/nvmtl_vk.h (+1). Patch: 0001-fetch-off-zero-reads.patch beside this file.

Draft description (the template's three headings; the AI checkbox is NOT ticked here on purpose, see README):

**What was wrong**

With framebuffer fetch off, which is the WindowServer default, a pipeline whose fragment shader reads `[[color(n)]]` was
built without descriptor set 3. The shader's reads of bindings 192 to 194 then hit an unbound descriptor. Core Animation's
uber fragment shader (`fixed_frag_lpf_cpf`) reads color(0), color(1) and color(2) at its entry, so every compositor pass
that uses it depended on an undefined value. On my machine the same draw read zeros in a small test process and garbage
inside WindowServer: identical inputs, different pixels.

**What this changes**

The pipeline records the shader's fetch mask as a new `fetch_zero` field when fetch is off (`fetch_mask` keeps it when
fetch is on, as before). The layout keeps set 3 when either field is set, so it matches the shader. A new
`nvmtl_fetch_zero_set()` allocates one descriptor set per process from the existing fetch pools and layout, every binding
pointing at `g_dummyImg`, the zeroed 1x1 image the driver already uses for unbound textures, in SHADER_READ_ONLY_OPTIMAL,
the layout your own `nvmtl_fetch_set` uses for that image. `nvmtl_vk_cmd_bind_set` binds that set at NVMTL_FETCH_SET
before a draw whose pipeline has `fetch_zero`. The reads then see zeros everywhere instead of whatever was left in the
descriptor.

**How I tested it**

RTX 5070 Laptop (GB206, 10DE:2D18), macOS 26.7.1 (25G241), Lenovo Legion 5 15IAX10. The change first ran in my fork on
the 2.1.0 base: installed as the system plugin, a single-process replay of a Dock badge draw over a filled target drew the
glyph the same way every run; the A8 render-target test (34 cases) and the Metal self-test (16 ran, 0 failed) were
unchanged; one boot with WindowServer on it (N-109): desktop and Dock blur normal. Ported onto 2.3.5 it has booted as
part of my 2.3.5-based plugin on five boots (N-112 to N-116) with the desktop, Terminal, screenshots and the Dock normal.
It does not by itself fix the missing Dock badge digit I was chasing; it removes the undefined read.

Not a conformant Vulkan render pass (the image is not a subpass input attachment), but NVK lowers input attachment
reads to descriptor loads, which is the same liberty `nvmtl_fetch_set` already takes.
