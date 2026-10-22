# N-156 (boot 12:40, Bash's own): stock 2.3.6 set with -nvoff in the OCEFI boot-args

`/Volumes/OCEFI/EFI/OC/config.plist` was modified at 12:36 (between N-155 and N-156) and its boot-args end in
`-nvoff`, the NullMoth kill switch (nvrm_off.h: the driver stays off, macOS runs on the firmware framebuffer). The
session that checked this boot at 12:47 did not notice and read the result as stock 2.3.6's display modes: wrong.
`modes.txt` (one mode, 1280x800 1x, 0 Hz), `desktop.png` and `dmesg-full.txt` describe a boot without the NVIDIA
driver: no NVRMNVDAFramebuffer in the registry, IONDRVFramebuffer + NVRMBootFB only, no NVRM lines in dmesg. The
"Liquid Glass clear, Terminal invisible" report of 11:35 was made on N-153 with the driver active and is still
unexplained; the 1280x800 mode is not stock 2.3.6's doing.
