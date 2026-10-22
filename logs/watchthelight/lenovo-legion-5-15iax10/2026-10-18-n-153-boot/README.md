# N-153: stock NullMoth 2.3.6 untouched (A/B for I-069)

Installed 11:23 from a copy of the audited release pkgroot (`~/src/NvGfx-build/pkg/2.3.6-stock`, SHA256SUMS
verified) with the package's own installer; backup of 2.3.5-nvgfx.5 at /Library/NullMoth/backup-20261018-112309.BpSOZV
(undo: install the 2.3.5-nvgfx.5 package again, not the uninstaller). Sums in `package-sums.txt`: NVRM 122b3994729c,
NVRMFB 61574b21b8cb, NVAccel 760d6d908660 (the 26 copy), plugin 8ab9ddc4a4da, translator 454a84d57bc8. No fork NVRM
glue (so no 115 W and no viewport scaling), no fork plugin. Wi-Fi set unchanged (native, N-150).

Question: does the panel stop updating on stock 2.3.6 too? If yes, I-069 is 2.3.6 on the RTX 5070 (upstream report
material, our fork not at fault); if no, the next boot is stock kexts + our plugin, then our NVRM. After the boot run
`check.sh` (sudo password on stdin): kexts, plugin hash, sysctl before/after three Finder drags, dmesg NVIDIA lines
(the FBLOG/ALOG lines land in dmesg, not in `log show`), ioreg.

## Result (boot 11:30, checked 11:33 and again 12:47 after three reboots of Bash's own: 11:45, 12:19, 12:40)

No I-069 freeze: all four kexts 2.3.6, plugin 8ab9ddc4a4da, the flip path stays alive (`drag.txt` 26 flips/s during a
Finder drag; `sysctl-0/1.txt` flips 283 -> 907; dmesg "cursor apply 5000: ok", "present stats head 0: 195 flips in
10236 ms (19/s, panel 165 Hz)"), 0 crash reports in the four boots. Bash clicked Good in the gpu-guard dialog at
11:34:42 (`~/.cache/legion/gpu/N-153-login`), then reported: "its not really good bcuz i cant see the terminal and
i also the background to a lot of liquid glass stuff is just clear".

What the stock package does differently on this panel: WindowServer has exactly one display mode, 1280x800 at 1x
(`modes.txt`, `system_profiler` "Resolution: 1280 x 800, UI Looks like: 1280 x 800"); the 2560x1600 native and the
HiDPI "looks like" modes of the DisplayOverride plist are gone. That is upstream issue 221 (scaled and HiDPI modes
rejected on postcomp head-scaling GPUs), fixed by PR 273, which our fork's NVRM carries and stock 2.3.6 does not.
`desktop.png` (the compositor's output) looks normal at 1280x800: the Terminal is drawn, the Dock's glass is dark, so
the clear glass and the invisible Terminal are on the panel side of the compositor or depend on the 1x mode. Not
separated further: the machine is not usable at 1280x800 1x, so 2.3.5-nvgfx.5 was reinstalled at 12:50 (backup of the
stock set: /Library/NullMoth/backup-20261018-125015.5grvFQ) for N-157.

For the I-069 A/B this means: stock 2.3.6 does not freeze, so the freeze comes from a fork part on top of 2.3.6:
the fork NVRM (power glue, PR 273 viewport scaling: the only part that changes the display path, and the 2.3.6
cursor thread call moves the cursor through NVKMS's immediate channel under that scaled viewport), the fork plugin, or
the fork NVRMFB/NVAccel builds. Next A/B boot: stock 2.3.6 kexts and plugin + fork NVRM only, under the gpu-guard.

## Correction (13:00)

The "one display mode, 1280x800 1x" finding above was measured on N-156 (boot 12:40), which ran with `-nvoff` in the
OCEFI boot-args (config.plist edited 12:36): no NVIDIA driver at all. It says nothing about stock 2.3.6. Moved to
`evidence/native/N-156/`. What N-153 itself showed with the driver active (11:33): flip path alive, and Bash's report
"can't see the terminal, Liquid Glass backgrounds clear". The display mode at that time was not recorded.
