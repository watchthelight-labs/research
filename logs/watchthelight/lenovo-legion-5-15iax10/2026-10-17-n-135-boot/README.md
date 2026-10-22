<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-135/README.md | author: watchthelight </wtl> -->
# N-135: 2.3.5-nvgfx.5 (plugin: per-module caches, fetch set per pass)

## N-134 result (2.3.5-nvgfx.4, submit-ahead at commit)
Window drag 63 flips/s (Finder, three runs) and 64 (empty window); N-133 had 35 and 45. WindowServer's main thread
no longer waits in `waitUntilScheduled`; it is now CPU-bound in the Core Animation compositor (4.2 s CPU in a 6 s
drag), 196 of 600 samples inside the plugin's `drawIndexedPrimitives` (`windowserver-drag-n134-profile.txt`):
descriptor snapshot per draw (`nvmtl_snapshot_set_c` 54), framebuffer fetch set plus barrier per draw (36),
IOSurface texture import per frame (`newTextureWithDescriptor:iosurface:` 26, VRAM-backed surfaces are never cached).

## System Settings / icons (Bash: pages slow to switch, icon loading slow)
`DisplaysExt` (the Displays pane extension) used 9 to 14 s of CPU in 12 s on three `cmphoto.canvasTransferQueue`
threads. VideoToolbox makes a Metal library, function and compute pipeline for every image transfer (609
`default.metallib` opens in 20 s, fs_usage). With warm caches the plugin still spent 523 of 846 samples in
`nvmtl_air_state` (`displaysext-profile.txt`): `[ll isKindOfClass:[NSMutableString class]]` is YES for every CF-backed
string (`strclass.m`), so the AIR digest was never kept and each reflection, specialization and variant lookup
re-hashed megabytes of AIR. `newFunctionWithName` also scanned the text twice and re-read the entry SPIR-V per
library, and `nvmtl_air_max_tg` walked the module per pipeline state. iconservicesagent (Launchpad, Dock icons)
showed the same sampler-variant and function paths through RenderBox.

Fix (fork commit on `commit-submit-ahead`): marked AIR strings keep digest, flags and threadgroup sizes; entry SPIR-V
rides on its bitcode object; fc/reflection/variant caches and a new render sampler cache memoize in-process even
without a cache folder. `xlcache3` (VideoToolbox metallib, debug plugin in-process, warm rounds):

| | library | 6 newFunction | 3 compute pipelines |
|---|---|---|---|
| before | 1-2.4 ms | 59-76 ms | 9.4-10.5 ms |
| after | 1-2 ms | 0.1 ms | 0.4-0.8 ms |

No writable cache folder (own path replaced by a file, TMPDIR missing): rounds 2-3 went from 395-430 ms per 2
functions to 16 ms per 3.

## Drag: fetch descriptor set per pass
`nvmtl_fetch_set` reuses the last set of the command buffer when mask and colour views are unchanged (one per pass
instead of one per draw; the self-dependency barrier stays per draw).

Regressions on the packaged release plugin: `order` 0/400 wrong in both parts, `sched3` B scheduled in under 1 ms,
a8rt2 17 ok / 12 known mismatches (unchanged).
