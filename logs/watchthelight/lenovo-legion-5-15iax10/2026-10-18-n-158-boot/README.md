# N-158: 2.3.5-nvgfx.5 with the OCEFI config restored (-nvoff removed, Resolution Max)

The Windows Claude Code session (note "FOR MAC SESSION (do first)", 12:36) had put `-nvoff` into the OCEFI boot-args
and set UEFI Output Resolution to 1280x800@32 so Bash got a legible firmware framebuffer after stock 2.3.6 (N-153)
left him without a visible Terminal. Both undone at 13:05 (backup config.n157-nvoff.plist.bak on OCEFI); the config
now differs from config.n96.plist.bak only in the Wi-Fi boot-args. Driver: 2.3.5-nvgfx.5 (installed 12:50, plugin
08c59a70009c). gpu-guard armed (recovery = the same package). Expected: accelerated desktop, HiDPI modes back,
Bash says Good.

## Result (boot 13:03, checked 13:06)

Accelerated desktop back: NVRMNVDAFramebuffer attached, kexts 2.3.5 (NVRM 0.1), plugin 08c59a70009c, mode
1680x1050 HiDPI at 165 Hz with 87 modes listed, 115 W glue active, boot-args without -nvoff. Finder drag 94 and 58
flips/s (`drag.txt`), 0 crash reports. Waiting for Bash's Good in the gpu-guard window.
