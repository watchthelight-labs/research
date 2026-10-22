# N-157 (boot 12:51): 2.3.5-nvgfx.5 reinstalled, but -nvoff still in the boot-args

Kexts loaded (NVRMFB 2.3.5, NVRM, NVAccel, NVRMAGDC), plugin 08c59a70009c, but the driver is off: boot-args carry
`-nvoff` (OCEFI config.plist, modified 12:36; the OpenCore Delete list rewrites NVRAM boot-args from the config at
every boot), the registry has IONDRVFramebuffer + NVRMBootFB and no NVRMNVDAFramebuffer, dmesg has no NVRM line,
one display mode 1280x800 1x. OC log opencore-2026-10-18-165146.txt: panel on the NVIDIA GPU (Current FB at
0x6000000000, res 2560x1600). Bash clicked Good in the gpu-guard dialog (the screen works, unaccelerated). Crash
reports since boot: 0. Files: dmesg-raw.txt (MACs redacted), dmesg-nvrmfb.txt (empty), ioreg-nvrmfb.txt (empty).
Next: remove -nvoff from the OCEFI boot-args (with Bash's go, since the edit was his) and reboot N-158 under the guard.
