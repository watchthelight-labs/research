<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-278/README.md | author: watchthelight </wtl> -->
# N-278: WindowServer on the Intel GPU again, with ring capture and relogin in the guard (I-113, I-114), BIOS Hybrid

Bash's go (2026-10-24, "Go."), one run. Same as N-277 (XeGfx 0.0.35, release plugin 139d1ae4 reinstalled via cp
beside + mv, backup of 4a50e082 in /Library/XeGfx/plugin-backup-20261024-060144) plus xe-guard 3c6fe2f0:
- debug.xegfx_log saved every 5 s from the WindowServer kill to the end of the settle (guard ws-xegfx-log.txt),
  so a Vulkan device lost (I-113) leaves the i915 side;
- the step fails when the first new WindowServer dies in its 45 s wait;
- loginwindow's didRunThisBoot markers removed before the kill, so auto-login should bring the session back (I-114).

OCEFI: XeGfxBlock Enabled false (config.n278-pre.plist.bak, make_config KEXTS_OFF). Queue: this entry only, stages 7,
N-276 env, wdog 180, settle 120, xe-post (400 s), ws=1, reboot_on_fail=1. On a failure: stop, report, XeGfxBlock back on.

## Result: Fail (read from Windows, 2026-10-24 07:00)

xe-guard verdict (xe-guard-result.json): fail, "WindowServer 1925 died during the 45 s wait (now 2236)". Stages 1-7
and xe-post passed. This is the 4th failed ws run in a row.

| Time | What |
|---|---|
| 06:45:27 UTC-4 | boot through OCEFI (Hybrid, iGPU FB), Tahoe |
| 06:47:44 | WindowServer 210 killed. 1925 starts on NMXAccel. Relogin markers removed once, before the kill |
| 06:47:50 | plugin: `reflection: SimpleTextureFragment has no AIR — cannot be reflected` (and SimpleVertex) |
| 06:47:56 | 1925 aborts: Core Animation assertion in `CA::OGL::Context::push_surface` <- `FlattenNode::retain_surface` (an offscreen surface failed) |
| 06:47:55-06:48:17 | 2181 runs about 21 s, then `vk: queue submit -> -4; disabling backend` (device lost, as in N-277) and the `pipeline: Vulkan is not up in this process` abort |
| 06:48:38 | verdict written, WindowServer 2236 running. reboot_on_fail restarts (shutdown stall report 06:48:42) |
| 06:49:08 | OCEFI picker, Bash chose Windows |

- I-114: Bash reported "I eventually got stuck in the login screen again". The markers were removed only before the
  guard's kill. The auto-login after it writes them again, so a crash relaunch stops at the login screen. Fixed from
  Windows in xe-guard (relogin_start: a thread keeps the markers deleted every 0.2 s until xe-guard exits). Needs
  `sudo native/tools/xe-guard/install.sh` on the Mac, and a ws run to prove it.
- I-113: device lost again about 21 s into an Intel WindowServer. So it is reproducible, not a one-off.
- New in this run: an assertion in Core Animation's surface push with "no AIR" reflection failures just before it.
  The plugin cannot reflect CA's built-in shaders, which seems to break an offscreen surface (flatten node).
- ws-xegfx-log.txt (06:48:33) holds only i915 init lines, about the same size as the 06:46 snapshot: no reset or hang
  line. Either i915 printed nothing about the device lost, or `debug.xegfx_log` returns only the start of the
  buffer. The Mac should check which, since the I-113 capture plan depends on it.

After the run, done from Windows: OCEFI XeGfxBlock enabled again (backup config.n278-post.plist.bak), make_config.py
KEXTS_OFF empty. Files: ws.txt, ws-xegfx-log.txt, xe-guard-result.json, windowserver-crashes-summary.txt.
