# N-292: four macOS starts die after ExitBootServices (I-118)

2026-10-24, 22:41-22:43 EDT (OpenCore log names are UTC, 2026-10-25 02:41-02:43). OCEFI, BIOS Discrete NVIDIA
(Current FB at 0x6000000000), fast-boot config (SetApfsTrimTimeout 0, picker Timeout 2).

- Earlier that evening OCEFI started the Ubuntu probe tool twice (opencore-2026-10-24-183745.txt,
  opencore-2026-10-24-220911.txt).
- Then four OpenCore starts 26-42 s apart. Each reaches `EB|LOG:EXITBS:START` 7-9 s in and stops there; the next
  OpenCore start follows 15-40 s later. The first one has cold-start timing, the other three warm.
- macOS left nothing: no unified log entries, no Kernel-*.panic, no /Users/Shared/legion-diag folder. debug=0x100
  halts on a panic, so an automatic restart means a reset (triple fault or firmware), or a manual power cycle.
- The next boot (N-293, 2026-10-27, cold, same config) reached the desktop. Its APFS mount had to roll back a few
  file sizes on the Data volume (apfs_trim_to_prev_fsize), consistent with an unclean end on 10-24.

Cause unknown. Open question for Bash: what the verbose screen showed, and what ran on the probe stick before.
