<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-153/windows-check.md | author: watchthelight </wtl> -->
# N-153 (stock NullMoth 2.3.6), checked from Windows

Read on 2026-10-18 ~16:20 UTC, read-only (Tahoe Data volume via `scripts/diag/apfs-read.py`).

Bash (Claude Code on Windows, no photo): "my mac install isnt realy working well with the new nullmoth drivers. Please investigate and repair for next boot". No specific symptom named.

- `/Library/NullMoth/driver-version` = 2.3.6 (stock package installed 15:23 UTC, backup of 2.3.5-nvgfx.5 in /Library/NullMoth/backup-20261018-112309.BpSOZV).
- gpu-guard: N-153 confirmed by Bash at 15:34:42 UTC ("confirmed (dialog 1792337442)"), result pass, so the guard kept 2.3.6. It stays idle on later boots ("attempt already finished (pass)"), and it has no boot-arg or NVRAM trigger, so nothing on OCEFI can make it roll back.
- Boots 15:30 and 15:45 UTC: flips keep counting (15:30 boot: 289 at 180 s, 1347 at 300 s; 15:45 boot: 443 at 180 s), latch timeouts 0, iop_fail 0, vm_refused 0, WindowServer pid 204 steady. So the I-069 panel freeze did not show in these windows.
- cpu_resource reports: WindowServer 61 % over 148 s from 89 s after boot, in NVMTLLibrary newFunctionWithName -> nvmtl_translate_with_fc (shader translation, cold cache after the driver swap). Terminal 99 % over 91 s at 142 s after boot (shell/Claude Code activity, no GPU frames).
- Stock 2.3.6 has none of the fork's fixes (submit-ahead I-061, per-module caches I-062, icon deferral 879f9fe), so slower window drags and slow Settings/icon loading are expected on it.

Repair (has to run on the Mac; Windows cannot write APFS): reinstall 2.3.5-nvgfx.5, the last proven package (N-152 PASS, 59-61 flips/s): `cd ~/src/NvGfx-build/pkg/2.3.5-nvgfx.5 && sudo bash ./install.sh`, then restart. Do not use `uninstall.sh <backup>`, which removed the driver on N-151.

## Follow-up (Bash, same day)
Bash can't use Terminal on 2.3.6 because he cannot see its window, and many Dock menus show no glass (clear background). Open upstream issues for the same 2.3.6 regression (checked 2026-10-18 with `gh issue list/view -R nullmoth/nvidia-macos-driver`):
- #276 "Broken Liquid Glass rendering in Dock context menus and missing System Settings icons (RTX 5080, v2.3.6)". A comment (GTX 1660 SUPER) adds that Terminal's context menu has doubled text and that "Rolling back to 2.3.3 fixes it". Another comment (RTX 2060 SUPER) reports icons black or grey and green video.
- #287 "Icons on the dock and menus are blurred + no liquid glass on those menus", #290 "App icons missing some parts and Liquid Glass menu's missing", #281 "transparency bug in the dock".
So the glass loss is a stock 2.3.6 regression, and going back to 2.3.5-nvgfx.5 removes it.

## N-154 (applied on OCEFI from Windows)
Boot-args + `-nvoff` (backup `EFI/OC/config.n-154.plist.bak`). Every NullMoth kext honours it (`kexts/*/nvrm_off.h`): the driver stays off and the desktop runs unaccelerated on the firmware framebuffer, as in N-50, so Terminal and Claude Code are visible for the reinstall. On that boot: `cd ~/src/NvGfx-build/pkg/2.3.5-nvgfx.5 && sudo bash ./install.sh`, remove ` -nvoff` from OCEFI config.plist, restart.

## N-154 result and N-155 (same day)
N-154 (16:19 UTC boot, `-nvoff`): Bash saw everything tiny, a white background and a cursor that would not move, and Claude Code did nothing (it only acts on typed input; the autostart passes a prompt only for reboot/wifi/gpu guard state files). The boot itself was alive: the bootdump ran to 300 s, WindowServer pid 204 stayed up. dmesg: "driver off - firmware framebuffer 2560x1600 rowbytes 16384 in BAR1", so WindowServer composited the full 2560x1600 panel in software straight into VRAM over PCIe. Far too slow on Tahoe, with no HiDPI (tiny UI) and no wallpaper drawn.
N-155 (applied on OCEFI from Windows, backup `EFI/OC/config.n-155.plist.bak`): `UEFI > Output > Resolution` Max -> `1280x800@32` (GOP mode 5 of 15 on the RTX 5070), `-nvoff` kept. A quarter of the pixels, normal-sized UI, so the desktop should respond enough to type into Claude Code. After the reinstall of 2.3.5-nvgfx.5, put Resolution back to `Max` and remove `-nvoff`.
