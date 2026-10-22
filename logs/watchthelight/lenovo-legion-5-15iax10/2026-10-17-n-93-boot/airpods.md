<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-93/airpods.md | author: watchthelight </wtl> -->
# N-93 AirPods A2DP runs (LegionBtFix 0.2.0)

2026-10-17, Tahoe 25G241, MT7925 over USB, MtkBt 0.2.0, AirPods Pro, codec AAC-ELD 48 kHz. Traces taken with bluetoothd's own PacketLogger (`HCITraces` in `/Library/Preferences/com.apple.MobileBluetooth.debug`); the .pklg files hold device addresses and stay out of git. Parsers: `scripts/diag/bt/`.

| Time (PDT) | HCI logging | Result |
|---|---|---|
| 08:19 | off | stream starts, no "Failed to read BT clock", no self-pause, silent |
| 08:24 | full + raw audio, right after `killall bluetoothd` | AirPods reject AVDTP START with 0x13 SEP_IN_USE, bluetoothd "result 253, disconnecting" (stale state from the restart, not the real fault) |
| 08:30 | full + raw audio, fresh connect from the case | **music audible** |
| 08:32 | off | silent, Spotify paused, AirPods disconnected |
| 08:33 | full + raw audio, fresh connect | **music audible** |
| 08:35 | full, raw audio off | silent, could not unpause, disconnected |
| 08:38 | full + raw audio, after `killall bluetoothd`, AirPods reconnected on their own | **music audible** (unpaused in Spotify) |

What the failing run (08:35:56) shows, with times relative to the first media packet:
- 0.000 first media packet (952-byte ACL, PB=10, handle 0x33, L2CAP CID of the AVDTP media channel); 0.001 a 7-byte ATT packet.
- After 0.000 the controller sends no Number Of Completed Packets for that link and receives nothing from the AirPods except one AVRCP message at 2.86 s. 8 packets end up outstanding (the controller's ACL buffer count is 8), so bluetoothd sends only 5 media packets in 10 s.
- The controller itself stays alive: LE advertising reports keep arriving and HCI commands complete normally.
- 10.28 s: Disconnection Complete, reason 0x08 (connection timeout).
In the working runs the same kind of packets go out every ~32 ms (32/32/32/32/21 ms cadence) and each one completes within 2-15 ms; at most 5 are outstanding.

RTP timestamps are anchored in both good and bad runs (first values 36412, 51104, 128310, 414650; 1 tick = 1 ms), so the Read Clock patch keeps working and the time base is not what separates them.

`RawAudioTrace` only changes the packet logger in bluetoothd (the flag global is read only inside the PacketLogger record builder, to decide how many payload bytes to copy), so the 3-of-3 vs 0-of-3 split may be chance or a side effect of the logging work. Open lead: Wi-Fi/Bluetooth coexistence on the shared MT7925 radio (our MtkWlan sends no coex information to the BT firmware).
