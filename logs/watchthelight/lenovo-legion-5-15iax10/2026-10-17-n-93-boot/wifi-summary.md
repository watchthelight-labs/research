<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-93/wifi-summary.md | author: watchthelight </wtl> -->
# N-93 Wi-Fi summary (MtkWlan 0.9.0, MtkAutoOpenSsids ["SSID-1", "Boingo"])

2026-10-17, boot 08:17 PDT, checked at 08:21-08:24.

- Automatic open join: `mtkwifi status` connected to SSID-1, ch 36, rssi -52 dBm, open, port open; nothing typed.
- MtkState "W6 pass: en1 passing traffic"; MtkW1Join "state 5 joins 1 fails 0"; MtkCm "autoopen 1 (2 ssids) fails 0"; MtkW2Cmd "indispatch 0 timeouts 0 fails 0 dead 0".
- en1 status active, DHCP lease in Boingo's CGNAT range; captive.apple.com 200 "Success" (no portal).
- wifi.sh N-93: down 190.84 Mb/s, up 174.82 Mb/s (N-91 on 0.8.0: 195 / 97). Ping idle 16.2 ms avg, under download 18.7 ms, under upload 16.4 ms, 0 % loss.
- Counters: MtkW6RxDropped 0, RxBad 0, Deauths 0, TxDrop 0, TxFailed 0, TxRingFull 0, TxCapped 55.
- mtkwifi LaunchDaemon: no saved networks (expected, Boingo is open). WPA2 not tested (no WPA2 network here).

Result: section E PASS (kext loaded, automatic join with DHCP and internet, throughput).
