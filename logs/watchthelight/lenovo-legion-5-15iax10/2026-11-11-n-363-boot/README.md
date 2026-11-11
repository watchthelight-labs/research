# N-363: MtkWlan 0.12.2, chip table (MT792x phase 0)

Staged 2026-11-10 with `native/tools/wifi-guard/stage.sh N-363 E "mtkfe=native mtknativeif=1"`.

## Change since N-362

MtkWlan 0.12.1 -> 0.12.2 (MtkWlanNative 0.4.16 unchanged, same binary). What differs between MT792x chips is now data
in `MtkChip.cpp` with one MT7925 row; the driver picks the row from the PCI device ID before its first register
access. Nothing it does to the MT7925 changes. Also: `MtkFrontEnd` shows the request after the boot-arg (I-133), a
card without a row is left untouched, and a CHIPID that does not match its row gets fw_own back.

## Proof before the boot

- `tests/hwtrace/compare.sh HEAD`: `hwtrace: identical (3589 events)`, driver at 12e2c486 against the refactor.
- `tests/hwtrace/selftest.sh`: six mutations (map entry, prefetch value, TX ring, RX ring, RX interrupt bit, MCU
  interrupt bit) each change the trace; the unmodified copy does not.
- `tests/hwtrace/run.sh`: two runs identical, UBSan clean, and a fake card with ID 14c3:7927 gets no hardware access.
- `tests/run.sh` (WPA2 vectors, supervisor): pass.
- Kext build with `NO_KMUTIL=1` (I-116): the undefined symbol list is the same as 0.12.1.

## Pass means

The wifi-guard's stage E checks (native front end, lease, gateway), plus on the core node: `MtkChipName` = MT7925,
`MtkPciDevice` = 0x7925, `MtkFrontEnd` = native, and the link figures of N-362 (5 GHz, 80 MHz).

## Result

**Pass** (boot 2026-11-10 19:14:06 EST, 25G416, Hybrid: "Current FB at 0x70800000").

- wifi-guard stage E: pass, lease on en1, gateway answers. Capture in `~/.cache/legion/wifi/N-363-pass/`.
- MtkWlan 0.12.2 and MtkWlanNative 0.4.16 loaded. `MtkChipName` MT7925, `MtkPciDevice` 0x7925, `MtkChipId` 0x7925,
  `MtkChipBands` 7, `MtkChipNss` 2, `MtkChipMaxBw` 3.
- `MtkFrontEnd` native, `MtkFrontEndActive` native: I-133 fixed.
- Link as in N-362: 5g44/80, 11ac, MCS 9, 2 streams, 866 Mbps, WPA2 Personal, country US. No attach recovery, no bad
  register access.
- Bluetooth ready. No panic. The per-boot bluetoothd ExcUserFault report is the known one.

The restart was asked for with the on-screen dialog first; it ran out after two minutes with nobody at the machine,
and the restart then went ahead under the standing authorization.

Files: `state.txt`, `opencore-2026-11-11-001400.txt` (redacted).

## Done after the pass

- Exported the same day: WTLMtkWireless f9497a3 (code) and 305aab5 (changelog, README row, how-it-works). A build of
  the public checkout gives the booted binary bit for bit (sha256 5fa47778...17a9).
- Release https://github.com/watchthelight-labs/WTLMtkWireless/releases/tag/0.12.2 with `MtkWlan-0.12.2-RELEASE.zip`
  and `mt7925-wifi-bundle-0.12.2+0.4.16.zip`.
- WTLMtkWireless #6: our first explanation of `MtkFrontEnd = ethernet` was wrong (it is the Info.plist default, not
  the Ethernet object); corrected there with the fix.
- qqwqtzd/mt7927-hackintosh #1: told the author where the chip table is and what a 7927 row would cover.
- Found by the export: the `mtkwifi` folder fix for labs issue #6 existed only in the public repo. Ported back to
  `native/tools/mtkwifi/mtkwifi.c`, otherwise this export would have reverted it.
- Not exported yet: `tests/hwtrace/` (its paths assume the project layout).
