<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-283/README.md | author: watchthelight </wtl> -->
# N-283 (2026-10-24 09:30 EDT): first WindowServer on the Intel-named head 4 (XeGfxIntelFB 0.2), ws=1 (Bash's go)

Result: **fail** (WindowServer died during the 45 s wait; xe-guard rebooted). Big step all the same.

What changed against N-280 (same stack, head 4 was IONDRVFramebuffer):
- SkyLight logs "Metal compositor activated" and CoreDisplay drives head 4 through IOPresentment:
  `debug.nvaccel_pipe_perform` 33, `nvaccel_iop_ok` 33, `iop_fail` 0, `iop_blank` 25 (frame not ready, previous kept).
- No push_surface assert. I-108's cause (vendor mask 0 -> no IOPresentment -> CompositorSW) is gone.

How it died (`WindowServer-2026-10-24-093240.ips`, `guard/ws.txt`, `guard/ws-xegfx-log.txt`):
- About 14 s in, the plugin logs `vk: queue submit -> -4` (VK_ERROR_DEVICE_LOST) and disables its backend; the next
  command buffer is refused, CoreDisplay::DisplaySurface::GetMTLTexture throws inside DisplayPipe::RunGPUDisplayPipe
  and WindowServer aborts. Every WindowServer restart (5 pids) dies the same way.
- Kernel side, one line per WindowServer pid: `ioctl 0x80406469 (nr 0x69) -> errno 14`: DRM_IOCTL_I915_GEM_EXECBUFFER2
  returns EFAULT. No other process sees it. This is I-113 on the main composite path.
- Plugin e7238ee's syslog of Mesa errors printed nothing: ANV reports the failed submit without a debug message.

Lead (Unverified): EFAULT from execbuffer is i915's answer when a userptr object's pages cannot be held. The plugin
imports IOSurface pages as host memory (userptr). WindowServer's surfaces come from the accelerator, so either their
user mapping cannot be wired, or their pages are shim GPU pages (vm_fault_quick_hold_pages refuses those). XeGfx 0.0.39
logs which one ("userptr hold: ...").

Also: XeGfxIntelFB 0.2's guard clear logged but did not reach NVRAM (removeProperty); counter reached 2, cleared by
hand; 0.3 writes 0 instead. XeGfxBlock back on (OCEFI backup config.n283-post.plist.bak).
