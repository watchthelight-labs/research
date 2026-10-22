<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-190/README.md | author: watchthelight </wtl> -->
# N-190: renamed framebuffer class with the built-in panel; black desktop with flashes, rolled back

Booted 2026-10-20 14:10 through boot-next (same package as N-189, `2.4.3-nvgfx.2-hdr2`, NVRMFB 6b93c26301a5 registered
as `NVRMFramebufferHDR`; `nvfbexternal=1` removed from the OCEFI boot-args, backup `config.n189.plist.bak`). Bash was at
the machine. OpenCore logs `opencore-2026-10-20-181019.txt` (hdr2 boot) and `opencore-2026-10-20-182021.txt` (rollback boot
14:20:35, recovery 2.4.3-nvgfx.1, class `NVRMNVDAFramebuffer` again).

Result: **Fail, rolled back** (no Good within 300 s of the 14:14:50 login). Bash (14:25): "couldn't see anything except
some flashes of the screen".

What the logs say:

- CoreDisplay, both WindowServers: `gpuVendor = 0x1`, `force8BPC = NO` (the class rename does what it did on N-189).
- WindowServer pid 207 aborted at 14:14:42 on the same CoreAnimation assertion as N-189, `_current_surface != surf` in
  `CA::OGL::Context::push_surface` under `FlattenNode::retain_surface` (`WindowServer-2026-10-20-141452.ips`, I-087).
  loginwindow logged out (WindowServerExited) and the login flow ran again.
- The second WindowServer (pid 767) set 1680x1050 HiDPI (`setDisplayMode 0x80001005`, switchMode COMMIT 3360x2100
  raster 2560x1600) and then **never presented**: 2 `flipToMemory` lines and no `present stats` line between 14:14:40 and
  14:19:55, against 30 flips a minute logged and 165 flips/s on the N-188 desktop. The panel kept whatever the scanout
  held, so Bash saw black with flashes.
- No NullMoth plugin, NVRMFB or NVAccel failure line in the window; NVAccel shaped the usual surfaces (3360x2100 pair,
  the 8192x4320 pair that N-188 also had).
- On N-188 SkyLight logged `Metal compositor activated.` 0.7 s after CoreDisplay's display init. In the same window
  on N-190 that line is absent. The crash stack of both assertions sits under SkyLight `layer_blit_byte` /
  `CGLayerKitFetch`, CoreAnimation's CPU blit path.

Reading: CoreDisplay's vendor code 1 ("unknown") does more than lift force8BPC. SkyLight does not activate its Metal
compositor for it and composes through CoreAnimation's OGL/byte-blit path, which asserts once and otherwise never
reaches our flip path. The NVDA class name is what puts NullMoth on the accelerated compositor; renaming the class is
not a usable route to 10 bpc on its own.

Two ways forward, neither a quick boot:

1. Keep `NVRMNVDAFramebuffer` and remove only the 8 bpc rule: a user-space patch of CoreDisplay's
   `get_display_device_info` (the `gpuVendor == 8` branch at +3954, see N-188 README) through Lilu's user patcher,
   the way WhateverGreen patches CoreDisplay. Everything else stays on the NVDA path.
2. Find what SkyLight keys the Metal compositor on for vendor 1 (strings around "Metal compositor activated" in
   SkyLight, the renderer selection in `WSInitialize`) and satisfy it under the renamed class.

The boot loop stays stopped (two rollbacks in a row). Boot-args are back to the pre-N-188 set; the running driver is
2.4.3-nvgfx.1; developer mode is still enabled for lldb.

Files: `WindowServer-2026-10-20-141452.ips`, the two OpenCore logs. Guard captures `~/.cache/legion/gpu/N-190-login`,
`N-190-rollback`.
