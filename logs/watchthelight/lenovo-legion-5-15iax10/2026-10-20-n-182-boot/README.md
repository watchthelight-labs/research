<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-182/README.md | author: watchthelight </wtl> -->
# N-182: clean reboot on 2.4.1-nvgfx.1 after the WindowServer aborts (I-083)

Booted 2026-10-19 21:04:40 EDT from OCEFI (OpenCore log `opencore-2026-10-20-010422.txt`, times in UTC). Staged with
the gpu-guard at 21:03:54 (recovery 2.3.7-nvgfx.1, 300 s window), no driver change: the same package as N-181
(plugin fb7983353d66, NVRM e327ea0c808a, NVRMFB 4e541f9ef81c, NVAccel 881569a85c9a; `driver-sums.txt`).

Result: **Pass.** Bash's Good through the guard dialog right after login (`pending.json` result pass, reason
"confirmed by Bash"). Panel on the NVIDIA GPU (`Current FB at 0x6000000000`), Metal 3 on the RTX 5070 Laptop GPU,
3360x2100 scaled mode, all four NullMoth kexts loaded, TGP mode on (`debug.nvgfx_tgp_state 1`, `sysctl.txt`). No crash
report belongs to this boot. The wifi-guard passed (lease and gateway answer).

Reports from the previous boot, copied into `../I-083-windowserver-crash/`: `WindowServer_...210215...cpu_resource.diag`
(the software-rendering WindowServer burning CPU between 21:00:16 and 21:02:14, after its abort at 21:00:13) and the
shutdown stall at 21:04:08 (spindump binary, the restart took longer than the watchdog allows; not kept).

`opencore-2026-10-20-005727.txt` is the log of the 20:57 boot that ended on software rendering (I-083, second event).

So I-083 is not a persistent state: the same files boot clean. The two aborts on 2026-10-19 (20:49:36 during a present,
21:00:13 at WindowServer start) stay open as an intermittent CoreDisplay assertion; see the I-083 README.
