# N-161 (boot 13:31): the gpu-guard's first real rollback, 2.3.5-nvgfx.5 back

Bash was away during N-160's window ("No, I was just AFK lol"), so at 13:30:27 the guard captured
(`~/.cache/legion/gpu/N-160-rollback/`), installed the recovery package 2.3.5-nvgfx.5 (backup of the N-160 set:
/Library/NullMoth/backup-20261018-133035.cjauSO) and restarted. This boot: kexts 2.3.5, plugin 08c59a70009c,
1680x1050 HiDPI at 165 Hz, guard result pass-after-rollback (13:33:21), 0 crash reports. The rollback path works
end to end: capture, install as root from launchd, restart, check on the next boot. N-160's own data was saved
before the window closed (evidence/native/N-160/).
