<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-184/README.md | author: watchthelight </wtl> -->
# N-184: guard boot of 2.4.1-nvgfx.1 (armed fine), rollback boot on 2.3.7-nvgfx.1 lost acceleration (I-083)

Two boots, Bash away, staged at 06:53 with recovery 2.3.7-nvgfx.1 and a 180 s window so that the Mac would end on
the proven driver without anyone clicking Good.

**Boot 1** (06:54:29, 2.4.1-nvgfx.1, OpenCore log `opencore-2026-10-20-105410.txt`): WindowServer started at 06:55:29,
go(2) at 06:55:59, firmware loaded in 0.16 s, RmInitAdapter succeeded at 06:56:01, "boot hold RELEASED (display
armed)" at 06:56:01.9, Metal 3 on the desktop. Nobody could give the Good, so the guard installed 2.3.7-nvgfx.1 at
07:00:01 (`rollback-install.log`) and restarted. Result for the driver: a clean 2.6 s bring-up.

**Boot 2** (07:00:48, rollback boot, 2.3.7-nvgfx.1: plugin fb1994ff5bee, NVRM 4e44684f0677, OpenCore log
`opencore-2026-10-20-110030.txt`): go(2) at 07:02:22, firmware loaded in 0.17 s, then nothing from RM between the
`NBCI _DSM 0x10` call and the first page allocations for 17 s, IOKit's "busy timeout (60s): 'NVRM'" at 07:02:49,
"boot hold RELEASED by the settle + 40 s cap" at 07:03:01.2, RmInitAdapter succeeded at 07:03:02.1 (40 s after go),
WindowServer 204 aborted at 07:03:01.6 in `CGXMappedDisplayStart` (`../I-083-windowserver-crash/WindowServer-2026-10-20-070310.ips`),
the replacement runs the desktop on software rendering. The guard counted the boot as `pass-after-rollback` because it
only checks that the kexts are loaded and the plugin sum matches; it does not know whether the display armed.

So the start-time I-083 failure is not a 2.4.1 regression: the settle + 40 s cap is in 2.3.5-nvgfx, v2.3.7 and 2.4.1
alike (`grep 'settle + 40 s' kexts/NVRM/NVRM.cpp` in all three trees). What changed is the bring-up time: 2.6 to 4 s on
N-181, N-182 and boot 1 here, 40 to 48 s on the 20:57 boot, N-183 and boot 2 here. The slow boots spend the time after
the NBCI `_DSM` call and before RM's first allocations (on N-183 also 19 s loading the 84 MB GSP firmware), while the
kernel log shows the Wi-Fi driver's IOC debug chatter, AppleACPIPlatform warnings for `\_SB.PC00.RP01.PXSX._DSM`
(argument 4 type mismatch) and the battery manager polling. Why RM waits there is still open.

Next: plain reboots on 2.3.7-nvgfx.1 until one arms (the bring-up time of each boot goes into the I-083 README), and
package 2.4.1-nvgfx.2 with the hold cap tied to the bring-up for a guard boot when Bash is back.
