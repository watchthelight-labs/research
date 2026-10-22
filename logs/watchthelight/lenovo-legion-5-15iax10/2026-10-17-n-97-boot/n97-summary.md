<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-97/n97-summary.md | author: watchthelight </wtl> -->
# N-97 summary (stage A path by boot-arg; Dock trace + A8 plugin)

2026-10-17, boot 10:31 PDT (kern.boottime), checked 10:36-10:45 on the Mac by the Dock session.

## Boot
- OpenCore: boot-args now carry `mtkfe=ethernet mtknativeif=0` (set from Windows after N-96); MtkWlan 0.10.0 (clean build a1645f7e) and MtkWlanNative 0.1.0 injected; panel on the NVIDIA GPU. Log: opencore-2026-10-17-173055.txt (redacted).
- Kernel timeline has no gap over 16 s. The stall Bash saw is at login: WindowServer launched 10:32:44 and built its first shader pipeline at 10:33:55, i.e. about 70 s of cold shader translation (the new translator invalidated the shader caches) while NVMTL_NVGFX_WSTRACE and SURFOUT_TRACE wrote thousands of syslog lines. N-96 had the same storm (cpu_resource report, 90 s CPU). Terminal needed a force quit in that window. Both trace keys were removed from nvrm610.conf at 10:44 (install via mv), so the next login has warm caches and no storm.
- No new .ips crash report. shutdown_stall reports 10:11 and 10:17 belong to the N-95 and N-96 shutdowns.

## Wi-Fi (stage A path)
- MtkFrontEnd ethernet (boot-arg wins over the Info.plist "native"), MtkNativeTrace "ctl:controller only (no interface requested)", MtkNativeInterface plist Yes but interface not requested (mtknativeif=0).
- en1 active, DHCP lease in Boingo's CGNAT range, `mtkwifi status` connected (ch 108, rssi -53), airportd running. MtkW6RxDropped 216 in the first 5 minutes (N-95: 15; N-93: 0), worth watching.

## Dock (I-056, I-057) with the dock-trace plugin (1276500) and translator a8_targets
- A8 render targets: every a8rt case ok on the installed driver (b-a8rt.txt).
- Minimized previews: the Terminal tile minimized by after-login.sh and a fresh Finder window both show the window image with the corner icon (b-dock-right-2x.png, b2-dock-right-2x.png). The Spotify tile that was restored minimized at login still shows only the icon. Legacy single-window capture still returns zeros while a legacy screen-rect capture now passes (b-capture.txt; N-95: both zero); kernel "surfvram pageoff" lines appear in this boot (none in N-95's 6 hours).
- Badge digit: still a blank circle on System Settings ("1") and the badge test app ("7") (b-dock-badges-3x.png). So the A8 fix is not the digit's cause.
- Trace (b-trace-30m.txt, 20,986 lines): 800 SDF draw lines, all glass_background_sdf_no_bleed_lpf / glass_background_no_bleed_lpf into BGRA8 targets (framebuffer and ImageOffscreen), no sdf_gen_field or sdf_gen_gradients pass, no single-channel render target; the SDF draw budget (400) and the pass budget were used up within the first minute after login, before the badge was set at 10:37, so the badge's own draws are not in the capture. Texture dumps at bind time read zeros for the glass source textures (read before their producing pass ran; inconclusive). 800 SURFOUT dirty-marks, 0 copy-outs, 0 blits, 26 GETBYTES (all the trace's own reads).

Result: stage A path PASS; I-056 fixed for new minimizes; I-057 open, trace inconclusive (caps). Next for the Dock: trace v2 that starts on a runtime trigger and logs every draw into small float or single-channel offscreen targets, then one logout.
