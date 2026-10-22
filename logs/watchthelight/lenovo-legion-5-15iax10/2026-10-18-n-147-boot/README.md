# N-147: stage E, MtkWlanNative 0.4.6 (candidate BSSID at +0x21c), native boot-args

Guard PASS 09:03. The candidate BSSID is now read right (`assoc:candidates 1 bssid MAC-55`, the channel 52
AP the Family asked for, and the join landed on it), yet the Family still left about 60 s after every join
(`missed-beacons-cycles.txt`: ASSOCIATE 09:05:01 -> LEAVE 09:06:02, 09:06:46 -> 09:07:51, 09:08:04 -> 09:09:10,
09:09:25 -> 09:10:30 ...). The kernel log names the reason: corecapture "errorCodeStr for fault missed beacons timeout",
a fault the Family raises from `WCLNetManager::handleMissedBeacons` (it then reports the fault, takes a CoreCapture and
sends `leaveNetworkCommand`; airportd logs the disconnect as BeaconLoss). The driver has to keep reporting beacons:
event 0xaf `WCLNetManager::updateBeaconCounter` adds the u32 at payload +0x54 to a counter and sets the flag the
missed-beacons check looks at. 0.4.7 posts 0xaf once a second while the link is up, when the core's cache entry for the
associated BSS is fresher than 3 s. The candidate-BSSID fix (I-067, first half) is confirmed by this boot.
