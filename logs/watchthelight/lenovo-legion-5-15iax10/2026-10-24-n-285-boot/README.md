<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-285/README.md | author: watchthelight </wtl> -->
# N-285 (2026-10-24 10:11 EDT): ws=1 with the plugin's read-only buffer fix (standing go)

Panel: Intel iGPU (OC log `Current FB at 0x70800000`, Hybrid). Stack: XeGfx 0.0.39, XeGfxAccel, XeGfxIntelFB 0.4,
NVMTLDriver plugin from NvGfx-xe e60f462.

Result: **pass**. xe-guard: "stages 1-7 passed, WindowServer stable 120 s" (`guard/result.json`). The first
WindowServer on the Intel GPU that stayed up: pid 210 was swapped for pid 2026, and 2026 kept running past the settle
window. It is the session's desktop at the time of this write-up (10:16, 3660 IOPresentment transactions and climbing,
`guard/ws-progress.txt`).

What the logs show:
- I-113 is fixed. The plugin refused four host-pointer imports and copied those buffers instead
  (`vk: host-pointer import refused ... is not all writable memory; that buffer is COPIED`, sizes 20 KiB, 1.1 MiB,
  8 KiB, 8 KiB). No `userptr hold` failure and no execbuffer EFAULT in `guard/ws-xegfx-log.txt`; no `queue submit`
  device loss, no WindowServer crash report.
- IOPresentment on head 4: 645 transactions in the counter snapshot, 0 failed, 38 blank; 618 frames copied to head 4.
  12 accelerator clients in WindowServer.
- XeGfxIntelFB 0.4's boot guard cleared itself (nvram `xeintelfb-starts` is 0 after 120 s).

Milestone: WindowServer composites with Metal on the Intel GPU (XeGfx, ANV through the plugin) and stays up; frames
reach the panel through a CPU copy into the scanout (head 4 completes each transaction after the copy). Not yet
claimed: what the panel looks like to Bash, input and drag smoothness, a reboot with the stack loaded at boot.

## Then a hard freeze (I-115)

About 75 s after the pass the whole Mac froze. The unified log stops at 10:17:50 with no panic, no panic report and
no GPU, XeGfx or WindowServer error before it. WindowServer 2026 logs nothing after 10:17:15 (its last lines are
RunningBoard updates for the OCEFI mount), the rest of the system logs normally until 10:17:50. The guard's
off-box log stream stops at the pass (10:16:32), so it does not cover the freeze. The Mac restarted at 10:25
(SMC shutdown cause 5); xe-guard did not issue it (its log ends with the pass). `debug.xegfx_spin` showed panic
armed, max 760 us, no long spins at 10:16.

So the Intel desktop runs for about 4 minutes (10:13:44 to 10:17:50), not indefinitely. Next: keep the
log stream running after the pass and run the desktop longer, to catch what precedes the freeze.

XeGfxBlock is back on in OCEFI (backup config.n285-post.plist.bak); the next boot comes up on the IONDRV desktop again.
