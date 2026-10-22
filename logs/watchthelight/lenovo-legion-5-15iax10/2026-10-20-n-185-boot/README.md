<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-185/README.md | author: watchthelight </wtl> -->
# N-185: plain reboot on 2.3.7-nvgfx.1, accelerated (bring-up 15 s)

Booted 2026-10-20 07:09:11 EDT through legion-reboot after the N-184 rollback boot had lost the desktop (I-083). No
driver change: 2.3.7-nvgfx.1 (plugin fb1994ff5bee, NVRM 4e44684f0677). OpenCore log `opencore-2026-10-20-110852.txt`,
panel on the NVIDIA GPU.

Result: **Pass** (no Good needed: the same files Bash confirmed on N-171 to N-180). WindowServer started 07:10:10,
go(2) 07:10:40, firmware loaded in 0.1 s, `NBCI _DSM 0x10` at 07:10:41.5, RmInitAdapter succeeded 07:10:55.2 (15 s
after go, 13.7 s of it after the NBCI call), "boot hold RELEASED (display armed)" 07:10:55.9, Metal 3 on the desktop.
No crash report on this boot. The shutdown before it stalled again (`shutdown_stall_2026-10-20-070839`), as every
restart since 2026-10-19 21:04 has.

Bring-up times so far (go(2) to RmInitAdapter succeeded): 4, 48, 4, >40, 2.6, 40, 15 s. The hold cap is 40 s.
