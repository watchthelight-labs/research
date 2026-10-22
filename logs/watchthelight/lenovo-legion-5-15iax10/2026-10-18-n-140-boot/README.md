# N-140: stage C retry, MtkWlan 0.11.0 + MtkWlanNative 0.3.1, boot-args mtkfe=native mtknativeif=1

Guard result: PASS (lease IP-88, gateway IP-6 answers) 73 s after boot, captured 01:27:30, then the
post-pass reboot to the known-good set.

Stage C ran this time (I-063 fixed): `MtkNativeCalls` `I:1b9=6 S:25b=6 P:c9=256 P:ed=5` (the call recorder caps a
code at 256), `MtkNativeScan` "requests 6 delivered 6 results 280 (last 47 of 48 cached)", trace `scan:request rc=0
ssidLen=0` / `scan:delivered 46..47 of 48`. The Family went on to ask 0x1be (WCL_SET_SCAN_HOME_AWAY_TIME, refused,
harmless). The address follow held (`MtkNativeMacFollow 1`), TX 115 / RX 182.

Open: proof that the Family accepted the 0xc9 payloads (networks in the Wi-Fi menu). The previous boot's unified log is
not persisted across the guard's reboot, so the capture now adds `system_profiler SPAirPortDataType` and the Wi-Fi
daemons' log (guard change after N-140). Files: guard capture (ifconfig, netstat, kextstat, configd lines for en1,
Mtk* ioreg properties, pcap summary, guard log).
