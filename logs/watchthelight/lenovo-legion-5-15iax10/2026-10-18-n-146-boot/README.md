# N-146: stage E, MtkWlanNative 0.4.5 (candidate BSSID, first attempt), native boot-args

Guard PASS 08:53:57 (lease, SSID, unscoped default route; the private MAC MAC-53 had passed the portal
earlier). The rejoin loop stayed (`MtkNativeJoin requests 4 ok 4 leaves 3` after four minutes): the trace reads
`assoc:candidates 1 first bssid 00:00:00:00:00:00 chan bytes 58fb96a0d1a3`, so the BSSID sits at +0x21c (those six bytes
are an access point MAC) and 0.4.5 read +0x222. 0.4.6 reads +0x21c. The repositories were renamed this boot
(mt7925-hackintosh-wifi, -wifi-native, -bluetooth) with topics for search.
