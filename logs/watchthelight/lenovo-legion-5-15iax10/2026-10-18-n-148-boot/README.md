# N-148: stage E, MtkWlanNative 0.4.7 (beacon-counter events), native boot-args

Guard PASS 09:36. Beacon-counter events flow (`P:af=201` in four minutes, `beaconreports 196`). Of the six leaves in
that window five were `WiFiNetworkDisconnectReason = ControlCenter` (Bash toggling the network in Control Center while
testing) and one was BeaconLoss, 60 s after a join on channel 100 (`cycles.txt`). The 0.4.7 gate (post 0xaf only while
the core's cache entry for the associated BSS is younger than 3 s) starves on a channel the core refreshes only during
scans: the firmware keeps the associated AP's beacons to itself, so the entry ages. 0.4.8 posts the event while the
core holds the link (`radioUp`) instead; the core's own link drop still reaches the Family as 0xd8 down.
