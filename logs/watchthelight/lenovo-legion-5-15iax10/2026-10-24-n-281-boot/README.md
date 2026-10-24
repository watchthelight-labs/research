<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-281/README.md | author: watchthelight </wtl> -->
# N-281: XeGfx 0.0.38 stages + xe-post (clock base, ETIME, syncobj deadline rebase), BIOS Hybrid

Stages-only, self-judged (no WindowServer step). First boot of the 0.0.37 and 0.0.38 shim changes (NvGfx xe 1889786,
2297299): ktime from boot instead of kext load, ETIMEDOUT returned as Darwin ETIME, a per-process ioctl log budget,
and syncobj wait deadlines rebased from Darwin CLOCK_MONOTONIC (calendar minus kern.boottime, ~2.5 s behind
mach_absolute_time) onto the shim's ktime. Also installed, not exercised without WindowServer: XeGfxAccel self-copy
skip (7f9e464) and the release plugin e7238ee (Vulkan errors to syslog).

Checks: stages 1-7 pass, xe-post passes (vkhost pixel check, mtlbench waits finish at normal speed: no polling spin
and no extra 2.5 s), the ring shows no new failing ioctls. Queue entry as N-279 plus post_timeout 400.
OCEFI: XeGfxBlock off (config.n281-pre.plist.bak, make_config KEXTS_OFF), back on after whatever the result.

## Result
**pass.** Stages 1-7, xe-post rc 0, WindowServer stable 60 s (guard/result.json). The guard ran at 08:26-08:29.

- Waits behave: xgprobe render and copy waits ok, vkprobe vkWaitForFences 0, vkhost submit+wait 1.62 ms (0 of
  1048576 wrong). mtlbench 2560x1600: clear avg 3.7-4.1 ms, blit 0.80-0.87 ms, draw 4.5-5.3 ms, every pixel check
  0 wrong; no sign of waits spinning (deadlines too early) or stalling (too late). In line with N-272 and N-279.
- Ring (xegfx-log.txt): the same background as N-279, GETPARAM (0x46) ENODEV, 0x42 ENOENT, 0x73 EINVAL and
  CONTEXT_SETPARAM (0x75) EPERM from ANV probing, now from every process thanks to the per-process budget (16 pids).
  No execbuffer failure, no timed-out wait.
- Not exercised here: XeGfxAccel's self-copy skip and the plugin's nvk-reason syslog (both need the WindowServer step).
- Unrelated: one ExcUserFault_bluetoothd report at 08:26:17, as on every boot today.

XeGfxBlock back on after the run (config.n281-post.plist.bak, make_config KEXTS_OFF empty). Queue empty.
