<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-96/n96-summary.md | author: watchthelight </wtl> -->
# N-96, read from Windows

Read on 2026-10-17 from Windows, read-only: the Tahoe Data volume via `scripts/diag/apfs-read.py` (bootdump 20261017-171222Z, DiagnosticReports) and the Tahoe unified log parsed with unifiedlog_iterator 0.7.0. Times are UTC. MAC addresses left out.

Bash (Claude Code on Windows, no photo): "really progressive boot", but Terminal and Claude Code were unusable. Wi-Fi and Ethernet both showed "Not Connected", yet his iPhone hotspot was listed in the Wi-Fi menu.

## Native Wi-Fi stage B (I-058)
- dmesg: `MtkWlan: W6 waiting for the native front end (MtkWlanNative)`, then MtkWlanNative ctl/sw steps up to `sw:published, running state false` (28.5 s). The core then joins on its own: `W5 joining SSID-1 (ch 108, open, rssi -49)`, `W5 pass: associated ... (aid 2, open)` (41 s), `W6 pass: en1 passing traffic` (50 s).
- configd / IPConfiguration: `en1 link ACTIVE` (17:13:03-04), `DHCP en1: INIT` with 11 retries until `status = 'no server'` (17:14:10), and a second round from 17:15:10. No lease.
- Every `Apple80211GetWithIOCTL ... 'APPLE80211_IOC_SSID'` returns `0xFFFFFFFFE0822403`, and configd logs `en1: no SSID`.
- Reading: scanning reaches the Wi-Fi menu through the native interface, but the interface reports no SSID and no DHCP reply arrives. Either DHCP frames never reach the air through the Skywalk TX path, or replies never come up the RX path.

## WindowServer and Terminal
- NvGfx dock-trace plugin loaded in WindowServer. 10,526 `NvGfx wstrace` lines, nearly all between 17:14:10 and 17:15:10: SDF and BADGE draws, render pass targets, SURFTEX/SURFOUT, and hex dumps of fragment buffers (`CAP SDF FBUF`) with texture readbacks (`SDF TEX ... nonzero bytes`). Saved as `dock/wstrace-unifiedlog.txt` for I-056/I-057.
- `WindowServer_2026-10-17-101549...cpu_resource.diag`: 90 s of CPU in 165 s, starting 89 s after boot. The heaviest stack is QuartzCore pipeline creation, then `-[NVMTLLibrary newFunctionWithName:constantValues:error:]`, then `nvmtl_translate_fc` (cold shader cache after the translator swap).
- Terminal (autostart) started at 17:14:28 (pid 664) with a TTWindow. login ran at 17:14:32 and zsh at 17:14:55. There's an app-hang signpost from 17:14:31 to 17:14:43, text-input events show keystrokes arriving, and at shutdown `windowShouldClose: prevented close` (a process was still running in it). No Terminal crash report.
- With no network Claude Code cannot work, whatever Terminal does. The trace storm and shader compilation made the first minutes after login slow.

## End of boot
- `shutdown_stall_2026-10-17-101728` (17:17:28): Bash restarted into Windows.

## N-97
- OCEFI boot-args + `mtkfe=ethernet mtknativeif=0` (config backup `EFI/OC/config.n96.plist.bak`), back to the N-95 stage A path. Kexts and the plugin are unchanged.
