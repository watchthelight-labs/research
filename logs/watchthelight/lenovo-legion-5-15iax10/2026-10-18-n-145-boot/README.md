# N-145: stage E, MtkWlan 0.11.0 + MtkWlanNative 0.4.4, native boot-args

Guard PASS at 08:12:25 (lease, SSID, an unscoped default route once Bash passed the captive portal), native set kept and
promoted to the known-good set. No panic: the CoreCapture pipes started after the core binding (`cc:fault pipe start=1`).
`ipconfig getsummary en1` says InterfaceType WiFi, the hardware port is listed as Wi-Fi, internet worked for apps.

What was wrong (I-067): the Family left and re-joined every 15 to 60 s (`MtkNativeJoin requests 15 ok 15 leaves 14`).
`join-cycles.txt`: airportd "Will associate to [... channel=52]", then 11, then 108, while our trace answered
`wcl:bss info answered ch=52` every time. `setWCL_ASSOCIATE` zeroed the BSSID, so the core joined its own favourite BSS;
the Family compared the BSS it got with the candidate it chose and re-joined. Fixed in 0.4.5: the first candidate's BSSID
(`apple80211AssocCandidates` +0x222, count at +0x214, read from `WCLJoinRequest::addAssocCandidates` on 25G241) goes into
the core's join parameters.

Also seen: the Settings toggle Bash used writes `PrivateMACAddressModeUserSetting = "static"` (a fixed private address),
so the join still used a private MAC and the portal asked again; "Off" is a different value. Bash put the Ethernet
boot-args back by hand at 08:38 (config.n-146.plist.bak), so N-146 is his manual revert, not an attempt of this loop.
