# N-149: stage E, MtkWlanNative 0.4.8 (beacon-counter events while the core holds the link)

Guard PASS 09:51. Beacon-counter events flowed the whole time (279 in nine quiet minutes), the Family still left with
BeaconLoss about 60 s after each join (`cycles.txt`). Read from the 25G241 disassembly: `WCLNetManager::assocTimerAction`
runs every 5 s and calls `handleMissedBeacons` when two timestamps (net manager +0x150 and +0x158) are both older than
60 s; the first call reports the fault, the second leaves. Event 0xaf only sets a flag that is read elsewhere. Both
timestamps are refreshed by `WCLNetManager::handleLqmUpdate`, event 0x27 with exactly 0x1dc bytes: the beacon one when
bytes +0x1d8, +0x1d9, +0x30 and the u32 beacon count at +0x28 are nonzero; the traffic one when +0x1d8, +0x1d9 are
nonzero and the u32 at +0x1c exceeds the u32 at +0x14 or the u32 at +0x24 is nonzero. Apple's driver posts this link
quality update periodically; ours never did. 0.4.9 posts it once a second next to the beacon counter.
