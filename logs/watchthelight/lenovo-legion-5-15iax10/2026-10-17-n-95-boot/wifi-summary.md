<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-95/wifi-summary.md | author: watchthelight </wtl> -->
# N-95 Wi-Fi summary (MtkWlan 0.10.0 core, MtkFrontEnd ethernet; MtkWlanNative 0.1.0 controller only)

2026-10-17, boot 09:54 PDT (kern.boottime), checked at 09:57-10:00 by the Dock session after the restart.

- OpenCore: "Prelinked injection MtkWlanNative.kext v0.1.0" Success, Lilu 1.7.2 and the rest as before; panel on the NVIDIA GPU (Current FB at 0x6000000000); every OCAK patch OK. Log: opencore-2026-10-17-165353.txt (redacted).
- `kmutil showloaded`: MtkWlan 0.10.0 and MtkWlanNative 0.1.0 both loaded; LegionBtFix 0.2.0, MtkBt 0.2.0, LegionCpuProbe 1.0.0 as before.
- MtkWlanNative: MtkNativeEnabled Yes, MtkNativeInterface No, MtkNativeVersion 0.1.0, MtkNativeTrace "ctl:start; ctl:work queue ok; ctl:logger ok; ctl:fault reporter ok; base start begin; ctl:base start ok; ctl:media auto=1; ctl:controller only (no interface requested)". MtkNativeAbi carries the 25G241 sizes. No MtkNativeDeclined text.
- MtkWlan: MtkFrontEnd "ethernet", MtkNativeAbiBuild 25G241, MtkState "W6 pass: en1 passing traffic", MtkW1Join "state 5 joins 1 fails 0", MtkCm "autoopen 1 (2 ssids) fails 0", MtkW2Cmd "indispatch 0 timeouts 0 fails 0 dead 0".
- `mtkwifi status`: connected to SSID-1, ch 52, rssi -56 dBm, open, port open, front end ethernet, last join ok, 2 scans 1 join 0 failures.
- en1 active, DHCP lease in Boingo's CGNAT range (router IP-6), captive.apple.com 200 (no portal). airportd running (pid 225).
- wifi.sh N-95 (/Volumes/DIAGOUT/wifi-N-95): down 192.7 Mb/s (24.09 MB/s), up 134.6 Mb/s (16.82 MB/s, 20 MB POST); N-93 on 0.9.0: 190.8 / 174.8. Ping idle 15.9 ms avg, under download 19.3 ms (max 52), under upload 16.9 ms, 0 % loss.
- Counters: MtkW6RxDropped 15 (N-93: 0), RxBad 0, Deauths 0, TxDrop 0, TxFailed 0, TxRingFull 0, TxCapped 51, MtkW6Link 15.
- No new .ips in /Library/Logs/DiagnosticReports. A shutdown_stall report at 09:53 belongs to the restart into this boot (the N-94 shutdown stalled; not a panic).

Result: stage A PASS (every item of the N-95 pass list). Upload 135 vs 175 Mb/s and 15 dropped RX frames are the only differences from N-93; worth a second look in stage B.
