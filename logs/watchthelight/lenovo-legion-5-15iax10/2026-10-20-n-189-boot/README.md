<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-189/README.md | author: watchthelight </wtl> -->
# N-189: framebuffer class without "NVDA"; CoreDisplay stops forcing 8 bpc, WindowServer asserts once, guard rolls back

Booted 2026-10-20 13:48 through boot-next (package `~/src/NvGfx-build/pkg/2.4.3-nvgfx.2-hdr2` = 2.4.3-nvgfx.1 with NVRMFB
6b93c26301a5: hdr-phase0 + `nvfbexternal` + the personality's `IOClass` set to an empty subclass `NVRMFramebufferHDR`
of `NVRMNVDAFramebuffer`, fork e87a1d7). Boot-args unchanged from N-188 (`nvfbexternal=1` still on). OpenCore log
`opencore-2026-10-20-174759.txt`. Guard window 300 s, recovery 2.4.3-nvgfx.1.

Result: **Fail, rolled back.** No Good within 300 s of login; the guard installed 2.4.3-nvgfx.1 at 13:56:09 and
restarted (`opencore-2026-10-20-175632.txt`, boot 13:56:56, "rollback boot ok", NVRMFB f2e415e5136f, class
`NVRMNVDAFramebuffer`, display armed, gpuVendor 0x8 and force8BPC YES again). The gpubench quick set that the
after-good hook started on the rollback boot under the hdr2 label was stopped before it wrote rows.

## What the renamed class did (`coredisplay` lines from the unified log, debug level persisted)

```
13:50:43.462  InitializeMPPriv: 0x1000006a9 1 NVRMFramebufferHDR IOService:/.../GFX0@0/NVRM/NVRMDisplay/NVRMFramebuffer
13:50:43.744  get_display_device_info: gpuVendor           = 0x1
13:50:43.745  get_display_device_info: force8BPC = NO
13:50:43.745  Display 0x23d09140 force8BPC=NO isBDW=YES isSKL=NO isCNL=NO isAcc=YES isMUX=NO isBuiltIn=NO isMobile=YES
```

Exactly the prediction from N-188: `IOObjectCopyClass` returns the subclass name, the vendor sniff yields 1, the
NVDA rule no longer applies, and the unknown-vendor fallback (not accelerated) does not fire. `serviceMatching`,
`metaCast` and `ioreg -c NVRMNVDAFramebuffer` kept working: NVAccel attached, Metal was up (surfvram lines), the guard
read its properties.

## What went wrong

`WindowServer-2026-10-20-135110.ips`: WindowServer pid 204 (launched 13:49:25) aborted at 13:50:55 (loginwindow:
`startDirectLogout reason: WindowServerExited`) with `SIGABRT` from `__assert_rtn` in
`CA::OGL::Context::push_surface(CA::OGL::Surface*, bool, unsigned, unsigned)`, called from
`CA::OGL::FlattenNode::retain_surface` inside a nested `render_layers` chain under `SkyLight layer_blit_byte` /
`CGLayerKitFetch`. The assertion text, from QuartzCore's strings next to `push_surface`, is `_current_surface != surf`:
CoreAnimation's renderer tried to push as a render target the surface that was already current (a flatten
surface aliasing the destination). No NullMoth plugin line, no NVRMFB or NVAccel error in the window (the release
plugin's log filter would have passed a failure). The replacement WindowServer (pid 745, 13:50:56) went through the
same CoreDisplay path (gpuVendor 1, force8BPC NO, startup mode 2560x1600 `CGSThirtytwoBitColor`, depth 0) and was
still running at the rollback capture 13:56; the guard's login capture at 13:51:05 saw it too. Whether its desktop was
usable, and what Bash saw, is not in any log: no Claude session ran on that desktop (no transcript touched between
13:50 and 13:57) and no HDR probe happened. Filed as **I-087**.

Reading: the crash is CoreAnimation's own, 12 s after display init, in the first WindowServer (login UI). It is the
first time this machine ran with `force8BPC = NO`; with the "unknown vendor" classification SkyLight or CoreAnimation
takes a compositing path NullMoth has never been exercised on. Two candidates to separate: a CoreAnimation
vendor-dependent path (would need the renderer's options read), or surface aliasing on our side (the plugin's texture
cache keyed by IOSurface id, `NVMTLDevice.m:961`). The second WindowServer surviving five minutes says the path is
not fatal every time.

## Next

No new boot before Bash says what the screen did between 13:50 and 13:56. Then one variable back: N-190 = hdr2 with
`nvfbexternal` removed (built-in flag restored; the force8BPC decision does not depend on it, HRCalc does), under the
guard, with the HDR probe run by hand right after the Good. If WindowServer asserts again, the renderer path comes
first; if not, the external flag was the second ingredient.

Files: `WindowServer-2026-10-20-135110.ips`, `opencore-2026-10-20-174759.txt` (hdr2 boot), `opencore-2026-10-20-175632.txt`
(rollback boot). Guard captures: `~/.cache/legion/gpu/N-189-login`, `N-189-rollback`.

## Bash (14:12)

He was AFK during N-189, so no Good was possible and the rollback says nothing about the second WindowServer's desktop. The
only known fault stays the first WindowServer's assertion. N-190 goes ahead with `nvfbexternal` removed and Bash present.
