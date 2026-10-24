<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-277/README.md | author: watchthelight </wtl> -->
# N-277: WindowServer on the Intel GPU with the zero-copy release plugin (XeGfx 0.0.35), BIOS Hybrid

Bash's go (2026-10-24, "Yes"), one run. First ws=1 run since N-260's hard freeze (I-109). Since then: XeGfx 0.0.35
(userptr notifier holds the mm, four i915 GuC/heartbeat/GSC fixes; N-275/N-276 stages and xe-post pass), and the
release plugin 139d1ae4ac3c (NvGfx xe e1b2a94: IOSurface textures as DRM-linear images over the surface's own pages,
N-272/N-276) installed system-wide via cp beside + mv. The changed code paths are Intel/AMD only. Previous plugin
4a50e08236cb in /Library/XeGfx/plugin-backup-20261024-060144.

OCEFI: XeGfxBlock (Kernel.Add 29) Enabled false, backup config.n277-pre.plist.bak, make_config.py KEXTS_OFF.
Queue: this entry only. Stages 7, N-276's env, wdog 180, settle 120, xe-post (post_timeout 400), ws=1,
reboot_on_fail=1. On a failure: stop, report, put XeGfxBlock back unless Bash says otherwise.

## Result: Fail (read from Windows, 2026-10-24 06:20)

The boot went through OCEFI at 10:03:18 UTC (Hybrid, iGPU FB 0x70800000, Tahoe). xe-guard ran stages 1-7 and xe-post
at 06:04, then the ws step.

| Time | What |
|---|---|
| 06:05:34 | WindowServer 210 killed. 2095 comes up on NMXAccel: agdc XeGfxDeviceControl, accel NMXAccel, fb0 `.Display_boot` |
| 06:05:53.866 | plugin: `vk: queue submit -> -4; disabling backend` (VK_ERROR_DEVICE_LOST), then `replaceRegion: upload FAILED` |
| 06:05:53.871 | Core Animation: "Metal failed to build render pipeline". WindowServer aborts with `COREANIMATION` code 4, `spec=PBGRAXb_BvcmXh`, `pipeline: Vulkan is not up in this process` (windowserver-crash-060555-summary.txt) |
| 06:05:55 | WindowServer 2141: "Metal compositor activated", then "Unable to find display pipe for IOFB service 0x100000607" |
| 06:06:05 | WindowServer 2183 starts and stays up. ws-progress: frames copied to head 4 rise steadily (77 -> 197), max spin 48 us |
| 06:07:21 | last ws-progress line. No verdict written: `state.json` still says running, stage 7, ws true |
| 06:07:56 | OCEFI log: the picker comes up and Windows is chosen. That restart was not xe-guard's: there is no results/N-277.json |

- Bash saw the login screen. WindowServer restarts end the user session and auto-login runs only once per boot: I-114.
- The device-lost is I-113. The kernel side of it (GuC or engine reset, hang detection) is missing here, because the
  remote log stream to bash-ec2 failed throughout ("Network is unreachable"). The Mac's unified log, 06:05:35 to
  06:05:54, has it.
- No panic report. The only crash reports from that boot are this WindowServer abort and a bluetoothd ExcUserFault
  at 06:03:55.
- Progress since N-260: WindowServer composited on the Intel GPU for about 18 s before the device was lost, and the
  last relaunch kept putting frames on the panel. N-260 froze the whole machine.

After the run, done from Windows: OCEFI XeGfxBlock enabled again (backup config.n277-post.plist.bak), make_config.py
KEXTS_OFF empty. The release plugin 139d1ae4 stays installed (its changes are Intel/AMD only, and XeGfx no longer loads
at boot). The backup is in /Library/XeGfx/plugin-backup-20261024-060144.

Files: ws.txt (xe-guard's ws capture), ws-progress.txt, xe-guard-state-after.json, windowserver-crash-060555-summary.txt.
