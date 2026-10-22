<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-187/README.md | author: watchthelight </wtl> -->
# N-187: HDR Phase 0 (2.4.3-nvgfx.2-hdr0), pass; macOS offers no HDR from the timing range alone

Booted 2026-10-20 13:09:00 EDT through `legion-reboot` after the 12:56 attempt never restarted (legion-reboot's
app-quit step had closed iTerm2, its own host; fixed the same hour). Package `~/src/NvGfx-build/pkg/2.4.3-nvgfx.2-hdr0`
= 2.4.3-nvgfx.1 with NVRMFB swapped for the hdr-phase0 build (NVRMFB c49d139d5b76; NVRM c7467dcf0092, NVAccel
881569a85c9a, plugin fb7983353d66 unchanged). OpenCore log `opencore-2026-10-20-170841.txt` (UTC), panel on the NVIDIA
GPU (`Current FB at 0x6000000000`). Guard: Bash's Good through the dialog at 13:09 (window 300 s, recovery
2.4.3-nvgfx.1). No crash report. `boot-args` unchanged, so `nvrmhdr` took its default 1.

Result: **Pass** (desktop accelerated, Metal 3, `nvrm-boot-hold = display armed`; quick gpubench set 13:11 to 13:16
normal: draw.encode 1.6 us, fakews 7052 frames/s, surfin 750 frames/s with 0 bad cells, sampbench 391k draws/s,
GPU 57 C at 24.5 W, limit 115000 mW; `gpubench/`). The first login autostart in iTerm2 worked: this session opened by
itself with the N-187 prompt.

## What Phase 0 answered (`nvrmfb-hdr0-boot.log`, `coredisplay-debug-modeswitch-13-17.log`)

| question | result |
|---|---|
| sink parse on the real driver | `fb0 sink: digital, 10 bpc, colorimetry block yes 0x80/0x00 (BT.2020 yes), HDR block yes eotf 0x05 (PQ+type1 yes) lum codes 139/107/2`; registry `nvrm-sink-bpc 10`, `nvrm-sink-colorimetry 128`, `nvrm-sink-hdr 5`, `nvrm-sink-hdr-lum 9136898`, `nvrm-hdr-level 1`. The EDID macOS holds (`IODisplayEDID`, 384 B) carries the same blocks (input byte 0xb5, ext tag 5 `058000`, ext tag 6 `0605018b6b02`). |
| timing range as published | `fbmodes: published ... IOFBTimingRange (... bpc 0x6 colorimetry 0x303 dynamic range 0x3)`; the registry bytes end `0100 0600 0303 0300`, as intended. |
| what CoreDisplay asked for at boot | 58 `validateDetailedTiming` calls, every one `enc 0x0 bpc 0x0 col 0x0 dr 0x0`; `IOFBSetDisplayModeAndDepth` depth 0 both times; `setAttribute` only `sHDC`, `hdcp`, `capd`. No HDR-flavoured timing, no `hdrm`, no dither control. `nvrm-hdr-timings` and `nvrm-hdrm-calls` never appeared. |
| HDR switch, scaled default mode (3360x2100 HiDPI) | `CoreDisplay_Display_SupportsHDRMode(main) = false`, `IsHDRModeEnabled = false`; `NSScreen.maximumPotentialExtendedDynamicRangeColorComponentValue = 1.0`; CoreGraphics lists 50 modes, all `--------RRRRRRRRGGGGGGGGBBBBBBBB`; `Framebuffer Depth: 24-Bit Color (ARGB8888)`. |
| HDR switch, native 2560x1600 @165 1x (held 25 s at 13:19:38, CG pixels 2560x1600, scale 1) | the same: SupportsHDRMode false, EDR potential 1.0. So it is not the scaled-mode rule from the Tahoe press. |
| what a toggle sends | nothing to toggle. The two mode switches sent only `sHDC`, `hdcp`, `capd` and depth 0. |
| CoreDisplay / WindowServer side | with `com.apple.CoreDisplay` at debug level (`log config`, persists to the next boot): `HRCalc: isBuiltin=1 displayOutputMode=2 activeDisplayPreset has_value=0`, `GetPresetCount_Server => 0`, `GetActivePresetIndex => -1`, `displayLimitedReferenceNits = 104000, m_displayNitsReferencePeak = 0.0`, and 443 `Attempting to get capabilities from plane with no gamma` in 30 s. No line mentions HDR, EDR or dynamic range. |
| anything broken | no. Quick set normal, no crash report, drags fine. |

Reading: the framebuffer side of Phase 0 works (parse, range, depths), but CoreDisplay never consulted the new bits.
Its own log for this display branches on `isBuiltin=1` and on display presets (the XDR / reference-mode machinery of
Apple's built-in panels), and it has none. The "High Dynamic Range" switch that third-party HDR10 displays get is the
external-display path. NVRMFB reports the panel as `kIOConnectionBuiltIn` (`fInternal`, so that AppleBacklightDisplay
attaches and the brightness keys work), which is the one capability answer a Hackintosh AMD framebuffer with a working
HDR switch does not give for its monitor.

Next boot, one variable: the same hdr0 build with the panel reported as not built-in (connection flags 0, no
AppleBacklightDisplay for that boot, brightness keys lost for the boot), `nvrmhdr=1` unchanged. If SupportsHDRMode
turns true, the gate is the built-in path; if not, N-189 is `nvrmhdr=2` (depth 1 as 30-bit) with the CoreDisplay debug
log already on at attach.

Files: `opencore-2026-10-20-170841.txt`, `nvrmfb-hdr0-boot.log` (sink, range, every timing and attribute line),
`coredisplay-debug-modeswitch-13-17.log` (9322 lines around the first native-mode switch), `gpubench/`.
