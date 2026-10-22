# N-159: I-069 A/B, stock 2.3.6 kexts and plugin + our fork NVRM only

Package `~/src/NvGfx-build/pkg/2.3.6-stock-nvrm` (package.sh with REF = the audited stock 2.3.6 pkgroot copy and
NVGFX_NVRM = the fork NVRM.kext from 2.3.6-nvgfx.2, e019fc32ebf1: power glue + PR 273 viewport scaling on the 2.3.6
NVRM). Everything else stock: NVRMFB 61574b21b8cb, NVAccel 2fc9363721b1 / 760d6d908660 (26), plugin from the stock
package (re-signed by package.sh, so its hash differs from 8ab9ddc4a4da), stock translator. gpu-guard armed, recovery
2.3.5-nvgfx.5.

Question: does the panel freeze with the fork NVRM on 2.3.6 (N-151 froze with the whole fork set, N-153 stock did
not)? If yes: the viewport scaling patch under 2.3.6's cursor thread call is the suspect; if no: the fork plugin or
the fork NVRMFB/NVAccel builds. Also expected on this boot: HiDPI modes back (PR 273), 115 W (glue), and the 2.3.6
glass regression (I-070) still present because the plugin is stock.

## Result (boot 13:10, checked 13:13, Bash clicked Good 13:13)

No freeze with the fork NVRM on stock 2.3.6: NVRMNVDAFramebuffer, kexts 2.3.6 (NVRM e019fc32ebf1 fork), plugin
fca181fac0c6 (stock, re-signed), flip path alive (`sysctl-1.txt` 2233 flips, 2235 latch waits, 0 timeouts; dmesg
"present stats head 0: 510 flips in 10005 ms (51/s)", "cursor apply 8000: ok"), Finder drag 60/63/44 flips/s
(`drag.txt`), 1680x1050 HiDPI at 165 Hz with 87 modes (PR 273 at work), 115 W (`nvgfx_tgp_applies 1`), 0 crashes.
So the fork NVRM (power glue + viewport scaling) is NOT the I-069 cause. Remaining suspects: the fork plugin, then
the fork NVRMFB/NVAccel builds and the fork translator build.

I-070 on this boot (stock plugin): Bash's screenshot `dock-menu-no-glass.png`: the Terminal Dock context menu drawn
with no material at all (text straight over the wallpaper) and the Terminal Dock icon a black square. "note this.
Look how its clear" (Bash 13:14). Matches upstream 276/281/287/290.

Next: N-160 = stock 2.3.6 + fork plugin only (2.3.6-stock-plugin), under the guard. It answers two questions: does
the fork plugin freeze the panel on 2.3.6, and does it bring the glass and icons back.
