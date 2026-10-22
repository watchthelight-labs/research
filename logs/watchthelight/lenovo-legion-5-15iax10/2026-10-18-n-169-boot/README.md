<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-169/README.md | author: watchthelight </wtl> -->
# N-169: NvGfx 2.3.7-nvgfx.1 (fork on NullMoth 2.3.7), feature test pass B

Package `~/src/NvGfx-build/pkg/2.3.7-nvgfx.1` (REF 2.3.7 pkgroot; plugin from nvgfx-2.3.7 60621ca, fb1994ff5bee after
re-signing; fork NVRM 4e44684f0677 with the 115 W nvrmtgp glue, physctl and PR 273; firmware path /Library/NullMoth/nvfw).
Installed 19:43; backup /Library/NullMoth/backup-20261018-194312.gh9joK. Staged with the gpu-guard (recovery 2.3.5-nvgfx.5).
Bash went to Windows first (recording), so this boot comes after a Windows session, not a legion-reboot.

After Bash's Good: `/legion-check N-169`, then `FT_PW=... ft.py run --pass B` (automatic only, Bash: no more manual
tests today), `ft.py report A B`, issues for anything new, and close or confirm NvGfx #1 (function table), #5 (scaled mode).

## Conditions (2026-10-19 08:50)

Bash: the laptop fell off the bed and the stand broke; pass B runs with the laptop directly on his lap, so cooling is worse than in pass A. Performance numbers (drag fps, decode rates, CPU clocks) are not comparable one to one, Bash then allowed the 45 s GPU burn (08:52), so gpu.power.b runs as planned.
