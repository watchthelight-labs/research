<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-188/README.md | author: watchthelight </wtl> -->
# N-188: panel reported external (nvfbexternal=1), pass; CoreDisplay forces 8 bpc because the framebuffer class name says NVDA

Booted 2026-10-20 13:27:13 EDT through boot-next (package `~/src/NvGfx-build/pkg/2.4.3-nvgfx.2-hdr1` = 2.4.3-nvgfx.1 with
NVRMFB f344c0b37d9a: hdr-phase0 plus the `nvfbexternal` boot-arg, fork 9d89533; NVRM, NVAccel, plugin unchanged).
Boot-args carry `nvfbexternal=1` (OCEFI, backup `config.n187.plist.bak`). OpenCore log `opencore-2026-10-20-172654.txt`,
panel on the NVIDIA GPU. Bash's Good through the guard dialog at 13:27, no crash report, quick set normal
(draw.encode 1.7 us, fakews 8328, surfin 777 frames/s 0 bad, 428k draws/s, GPU 52 C at 19 W; `gpubench/`).

Result: **Pass** for the boot, **no** for the question. The panel came up as an external display (`fb0: display 0x200
is internal but nvfbexternal=1 -- reporting it as external`; `AppleDisplay` instead of `AppleBacklightDisplay`,
`IODisplayConnectFlags 0`, brightness keys dead as expected, the desktop at native 2560x1600 1x because the display
identity changed and the HiDPI "looks like" modes of the override did not come back; `setmode.py set 1680x1050 --hidpi`
bounced with error 1007). `CoreDisplay_Display_SupportsHDRMode` false and EDR potential 1.0 on the scaled mode and on
the native mode held for 25 s. Framebuffer side identical to N-187 (sink parsed, range published, no HDR-flavoured
timing, no `hdrm`).

## What the CoreDisplay debug log says at display attach (`coredisplay-debug-attach.log`, 20723 lines)

CoreDisplay parses the sink's CTA blocks itself (`ParseCEAColorimetryDataBlock, block with length 3`,
`ParseCEAExtendedHDR10DataBlock, block with length 6`), builds its own scaled-mode list from the EDID, then in
`get_display_device_info` decides:

```
isBroadwellOrLater  = YES      isSkylakeOrLater = NO      isCannonLakeOrLater = NO
isAccelerated = YES  isMuxSystem = NO  gpuVendor = 0x8  isMobileSystem = YES  newIsBuiltIn = NO
force8BPC = YES
```

`force8BPC` is the gate: with it set, CoreDisplay never asks the framebuffer for a 10-bit depth or an HDR timing, so
nothing in the IOFBTimingRange or the connection depths is ever read. Disassembly of CoreDisplay (lldb on a scratch
process, `/private/tmp/.../cd-disasm2.txt`, `cd-vendor.txt`; developer mode was enabled with `DevToolsSecurity` for it):

- `GetGPUVendorForFramebufferService` takes `IOObjectCopyClass` of the IOFramebuffer service and substring-matches
  the class name: contains "Intel" -> 2, "AMD" -> 4, "AppleParavirt" -> 0x10, "NVDA" -> 8, anything else -> 1.
  Our class is `NVRMNVDAFramebuffer`, so `gpuVendor = 8`.
- In `get_display_device_info` (+3937): `if (gpuVendor == 8) force8BPC = 1`, before any other test. Vendor 2 (Intel)
  goes through the CPU-generation checks (`isBroadwellOrLater` = "SMAP" in `machdep.cpu.leaf7_features`,
  `isSkylakeOrLater` = "SGX" in the same string, which an Arrow Lake CPU does not have; `isMobileSystem` =
  IOPSPowerSourceSupported("Battery Power")). Vendor 1 (unknown) and 4 (AMD) skip that and are forced to 8 bpc only
  when `isSkylakeMacBook` or when a field of the device record (`device->0x160->0x5c`) is 0.
- `force8BPC` lands in the device flags (bit 21) and is logged as above.

So: the "NVDA" in NullMoth's framebuffer class name puts every NullMoth machine on Apple's old NVIDIA-web-driver rule
(8 bits per channel, no 10-bit, no HDR), independent of the panel, the timing range or built-in vs external. N-187's
built-in reading was not wrong, only not the first gate.

## Next boot (N-189, one variable)

Same hdr1 build and boot-args, with the IOFramebuffer registered under a class name without "NVDA": an empty
subclass `NVRMFramebufferHDR : NVRMNVDAFramebuffer` as the personality's `IOClass`. `IOObjectCopyClass` then returns the
subclass name (vendor 1); `serviceMatching("NVRMNVDAFramebuffer")`, `ioreg -c NVRMNVDAFramebuffer` and OSDynamicCast
still match through the subclass, so NVAccel, NVRMAGDC, the gpu-guard and the tools keep working. Expected in the
log: `gpuVendor = 0x1`, then either `force8BPC = NO` (and the HDR probe turns) or the `device->0x160->0x5c == 0`
fallback, which is the next thing to decode.

Files: `opencore-2026-10-20-172654.txt`, `coredisplay-debug-attach.log`, `gpubench/`. Disassembly notes in the scratch
folder of this session are summarised above; the decisive instructions are quoted in `evidence/native/hdr/README.md`.
