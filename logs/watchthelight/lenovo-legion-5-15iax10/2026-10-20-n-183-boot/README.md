<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-183/README.md | author: watchthelight </wtl> -->
# N-183: morning cold boot on 2.4.1-nvgfx.1, no acceleration (I-083, third event)

Booted 2026-10-20 06:39:33 EDT by Bash (no staging, same driver files as N-181 and N-182: plugin fb7983353d66,
NVRM e327ea0c808a, NVRMFB 4e541f9ef81c). OpenCore log `opencore-2026-10-20-103914.txt` (UTC), panel on the NVIDIA
GPU (`Current FB at 0x6000000000`). Bash: "There is no GPU drivers atm, this is a fresh boot after I slept."

Result: **Fail** (desktop on software rendering, Metal absent, all four NullMoth kexts loaded). WindowServer (pid 204)
aborted at 06:41:53 at `CGXMappedDisplayStart` (CoreDisplay assertion inside `CGXDisplayDriverInitialize`,
`WindowServer-2026-10-20-064201.ips` in `../I-083-windowserver-crash/`), the replacement (pid 513, 06:42:04) came
up before the driver armed, and NVRM refuses to arm with WindowServer up. The replacement then burned CPU for the
software desktop (`WindowServer_2026-10-20-064346...cpu_resource.diag`).

## Timeline (unified log through /usr/bin/log and the bootdump `/Users/Shared/legion-diag/20261020-103932Z/log-nv.txt`)

| time | +s | event |
|---|---|---|
| 06:39:33 | 0 | kernel boot |
| 06:40:43 | 70 | WindowServer 204 "Server is starting up"; waits in IOKitWaitQuiet for the display |
| 06:41:07 | 94 | NVRMFB claims the IOFramebuffer category on GFX0; "boot guard: start 1 without a display so far" |
| 06:41:13 | 100 | NVRM armed; auto-go: go(2) in 500 ms; "registry held busy until the display is armed (cap settle + 40 s)" |
| 06:41:14 | 101 | RmInitAdapter (GSP boot from inside macOS) starts |
| 06:41:33 | 120 | PHYSMAP / WATCHPAGE / QUARANTINE armed (RM init still running) |
| 06:41:53.57 | 140 | "boot hold RELEASED by the settle + 40 s cap: the bring-up will not arm with WindowServer up" |
| 06:41:53.97 | 140 | WindowServer 204 aborts: CoreDisplay assertion in CGXMappedDisplayStart (no armed display behind the framebuffer) |
| 06:42:04 | 151 | WindowServer 513 starts on software rendering; the driver stays unarmed by design (2.4.1 boot hold) |

## Comparison with the other 2.4.1-nvgfx.1 boots

| boot | go(2) at | display armed ("boot guard cleared") | bring-up time | outcome |
|---|---|---|---|---|
| N-181 19:39 | 19:39:08 | 19:39:12 | 4 s | pass |
| 20:57 boot | 20:59:18 | 21:00:06 | 48 s | hold released by the cap at 20:59:58, no arm, software rendering |
| N-182 21:04 | 21:06:06 | 21:06:10 | 4 s | pass |
| N-183 06:39 | 06:41:13 | not before the cap | > 40 s | hold released by the cap at 06:41:53, WindowServer abort, software rendering |

So the start-time half of I-083 is a race between the boot hold and a slow bring-up (correction from N-184: the hold
and its cap are in 2.3.5, 2.3.7 and 2.4.1 alike, so this is not a 2.4.1 regression; the slow bring-up is the new
factor). NVRM holds the
IORegistry busy from go(2) until the display is armed, capped at settle + 40 s (`kexts/NVRM/NVRM.cpp:702-710`).
On two of four boots the GSP bring-up (RmInitAdapter) took longer than 40 s instead of 4 s; the cap then released the
hold while the bring-up was still running, WindowServer's CGXDisplayDriverInitialize found a framebuffer without an
armed display and asserted, and the driver refused to arm afterwards. 2.3.7-nvgfx.1 had no hold and armed whenever
the bring-up finished, so a slow GSP boot only delayed the desktop there. Why the bring-up is sometimes 10x slower is
still open (the RM log of the slow boot is in the I-083 README); the cap is the part that turns a slow boot into a
lost desktop.

Next: N-184 under the gpu-guard with recovery 2.3.7-nvgfx.1 (Bash is away, so the guard rolls back after its window
and the Mac ends on the proven driver), and package 2.4.1-nvgfx.2 with the hold cap tied to the bring-up state (release
on arm or on failure, not on a timer) for a guard boot when Bash is back.
