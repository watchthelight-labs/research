<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-379/README.md | author: watchthelight </wtl> -->
# N-379: boot away from home, Wi-Fi joins a range extender network but gets no lease (2026-11-26 12:05 EST)

Bash booted the laptop away from home. Nothing was changed for this boot. It is not the N-378 plan (that one needs
the HDMI monitor at power-on).

- Mode: Hybrid (OpenCore log: "Current FB at 0x70800000", the Intel framebuffer). No external monitor, no NVIDIA
  device on the PCI bus. XeGfxIntelFB 0.9 and XeGfxAGDC loaded, XeGfx not staged.
- Config: OCEFI as in N-377. WTLWireless 0.15.0, boot-args `mtkfe=native mtknativeif=1`.
- Internet during the session: iPhone USB tether (`en2`).
- Log: `opencore-2026-11-26-170547.txt` (redacted copy).

Network names, addresses and passwords are left out of this folder on purpose.

## I-142: joined, link up, no DHCP lease

The house has a main network and a range extender network. Bash joined the extender network from Control Center
with a typed password.

What worked:
- 4-way handshake complete (`MtkW2Sec`: m1 to m4 = 1, installs 2/0, MIC of message 3 verified), link up, port
  open, channel 44, 80 MHz, RSSI about -39.
- Transmit: `MtkW6TxPackets` 723, no failed frames.

What did not:
- `en1` kept a self-assigned 169.254 address. A probe with fixed addresses on 17 common /24 subnets got no ARP
  answer, so unicast replies were lost too.
- `MtkW6RxPackets` stayed at 1 while `MtkW6RxTrans` went 66, 448, 1238, 3513. `MtkW2Sec` "trans" (the drop
  counter) equals it.

Cause: the firmware hands every data frame of this AP to the host already translated to 802.3 (RXD2 bit 7,
HDR_TRANS). `rxFrame` dropped translated frames on a WPA2 link (`if (tgtRsn || !portOpen)`), because at home they
do not occur: the station record asks for no translation (STA_REC_HDR_TRANS, dis_rx_hdr_tran 1) and the home
captures show `MtkW6RxTrans` 0 to 27 beside thousands of delivered packets.

Update from N-380: the translated frames are this AP's broadcast and multicast frames (WLAN index 19, the
group key entry), and its DHCP replies are sent as broadcast. That is the whole fault; see
`evidence/native/N-380/README.md`. The unicast path was fine. Written before that boot:

Open: why this AP is translated. Candidates are the hardware de-AMSDU path (MDP_DCR0 bit 15 is on; an extender that
aggregates) and the state after the private address change (`MtkMacChanges` 3: the device record is registered
again with the new address). One rx block-ack session was active (`MtkW9Ba` rx sessions 1).

Ruled out on the way:
- A TKIP group key: the macOS log lists `mcast=aes_ccm, bip=none, auths={ psk }, mfp=no` for the network.
- A wrong typed password: the handshake completed.

## Fix prepared: WTLWireless 0.15.3

Branch `wifi-0.15.3` (99a8f636 the change, 2d93009b the version), on top of the 0.15.2 candidate. In
`MtkNet.cpp`, `rxTranslated`:
- on a WPA2 link a translated frame is taken when the hardware decrypted it with the expected cipher (SEC_MODE, no
  CM or CLM flag), as `mt7925_mac_fill_rx` in Linux 6.18 does; undecrypted ones are still dropped;
- TID and sequence number come from RXD group 4 (frame control, sequence control, QoS control), so the block-ack
  reorder buffer and the per-TID replay counters work as on the 802.11 path;
- the subframes of one A-MSDU (RXD4 payload format first, middle, last) share one sequence number and one PN. They
  are linked with `mbuf_setnextpkt` and pass reorder and the replay check as one unit;
- an encrypted EAPOL frame (a rekey) goes to the supplicant queue;
- new property `MtkW6RxTransInfo`: "ok, undecrypted, amsdu, nogroup4, last" (last = SEC_MODE, decrypted flag,
  payload format, group 4 flag, WLAN index of the newest translated frame).

Host proof: `tests/run.sh` 75 checks 0 failures; `tests/hwtrace/run.sh` passes; `tests/hwtrace/compare.sh 35e98835`
identical (3589 events). The core imports two more kernel functions than 0.15.1 (`mbuf_nextpkt`,
`mbuf_setnextpkt`; RealtekRTL8111, loaded on this machine, imports both). No host test drives the data path.
Status: passed N-380 (lease in 38 s, link stable).

## I-143: six failed auto-joins to the main network

Between 12:06:33 and 12:08:33 macOS tried the saved main network six times (profile of 2026-11-08, private
address). Each ended with airportd error -3905, in the driver as deauth reason 15 (`MtkW6LastDeauth` 786447): the
AP sent message 1 four times per attempt and never took our message 2 (eapol rx 51, tx 51). Cause open: a stale
saved password, or a key method the driver does not do. The AP was not in the scan list later, so its RSN element
could not be read.
