# N-139: stage C, MtkWlan 0.11.0 + MtkWlanNative 0.3.0, boot-args mtkfe=native mtknativeif=1

Guard result: PASS (lease IP-88, gateway IP-6 answers), captured 01:14:59, then the guard restored the
known-good set and rebooted at 01:16 (post-pass reboot so the next session has network).

Stage C itself did not run: `MtkNativeCalls` shows `I:1b9=32` and `MtkNativeRejected` 65, no `S:25b` (slot 603), no
`P:c9` / `P:ed`, no `MtkNativeScan` property. The Family's `apple80211setWCL_SCAN_REQ` asks `isCommandProhibited(0x1b9)`
first (25G241 asm) and our allowlist in `MtkWlanNative.cpp::commandAllowed` refused it, so the scan request never
reached our handler. Fix in 0.3.1: allow 0x1b9 (WCL_SCAN_REQ) and 0x1b3 (WCL_SCAN_ABORT). Full WCL ioctl table for
later stages in `docs/native-wifi.md`.

Address follow (N-137/138 fix) held: `MtkNativeMacFollow follows 1`, core `MtkMacAddr MAC-3`, TX 132 / RX 492.
Files: guard capture (ifconfig, netstat, kextstat, configd lines for en1, Mtk* ioreg properties, pcap summary, guard log).
