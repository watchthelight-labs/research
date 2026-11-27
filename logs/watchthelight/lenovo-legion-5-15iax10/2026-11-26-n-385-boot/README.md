# N-385: WTLWireless 0.15.5 (5.9 GHz power limits, firmware command status)

Staged 2026-11-26 about 14:50 EST through the wifi-guard, stage E, Hybrid, macOS 26.7.3 beta 25G416. Same boot as the
XeGfx run N-386, which waits for this attempt's verdict.

## What changed against 0.15.4 (booted N-381)

Both come from mt76 commits of the last two weeks (scout write-up `scout/mt7925-wifi/2026-11-26.md` in the research repo).

1. `ratePowerBand` sends per-rate power limits for channels 163, 169, 173, 175 and 177 too (mt76 99265f9a). Before,
   the 5 GHz list ended at 167, so 5.9 GHz channels got no limit from us. 51 channels are 17 full messages; the old
   list ended with a one-channel message.
2. `uniCmd` reads the firmware status that DEV_INFO, BSS_INFO and STA_REC answers carry (`{cid, pad[3], status}` after
   the 44-byte header, as `mt7925_mcu_parse_response` does; mt76 bc394ec4 added the log line). It only counts and
   publishes: `MtkW2Cmd` gains "status seen N odd N refused N (last cid, status)", and the first eight refusals go to
   the kernel log. The return value of `uniCmd` is unchanged, so a refused command is treated as before.

Not in it: the group key replay counter case (mt76 339bbc19), which needs a rekey test first.

## Checks before the boot

- `tests/run.sh`: 75 checks, 0 failures.
- `tests/hwtrace/compare.sh HEAD`: the trace differs only in the power limit messages (3 one-channel messages gone,
  6 more full ones, one more message per power stage) and in the ring indexes and sequence numbers that follow from
  that. Every other MCU message is byte-identical.
- Bundle built with `NO_KMUTIL=1 NO_LINKCHECK=1` (XeGfx was loaded). Imports of all three binaries are identical to
  the tested 0.15.4 bundle (510, 750 and 310 names). sha256 starts: core 83b3ea869b2c846e, Native fedd4664d6ff44ba,
  Bt 670632a237894214.

## Pass

1. wifi-guard stage E: joined, lease, gateway answers.
2. `MtkW2Cmd`: "status seen" above 0 and "odd 0" (the status field is where Linux says it is). Any "refused" count
   is a finding to record, not a failure of this boot.
3. `MtkW9Power`: "sku 2g failed 0, sku 5g failed 0".
4. All three parts report 0.15.5; Bluetooth controller present.

## Way back

The wifi-guard restores `EFI/OC/wifi-lastgood` (0.15.4 and its config) and restarts by itself when the join fails.
By hand, from Windows: `config.n-385.plist.bak` on disk0s5 and the kext folder from `wifi-lastgood/Kexts`.

## Result: pass (second start), first start lost after the handover (I-118 again)

Two OpenCore logs belong to this attempt.

- `opencore-2026-11-26-194642.txt`: the restart that `legion-reboot` issued at 14:46 EST. OpenCore injected the kexts
  and reached `EXITBS:START` at 14:46:46. No macOS log line exists after that: the unified log has nothing between
  14:46:28 (the shutdown) and 23:10:34, no panic report was written, and neither guard ran. With `debug=0x100` a
  panic halts the machine. This is the I-118 picture, the second time on 2026-11-26 after a `legion-reboot` restart
  (the first was 14:04, N-383). What was on the screen and who started the laptop again is not known.
- `opencore-2026-11-27-041026.txt`: the start at 23:10:26 EST, 8 h 24 min later, with the same files. It booted
  normally (Hybrid, `Current FB at 0x70800000`), kernel boot time 23:10:33. Everything below is from this start.

Against the pass list:

1. wifi-guard stage E: pass at 23:11, lease and gateway answer, `auto_reboots 0`. `MtkW1Join`: state 5, joins 1,
   fails 0, tries 1.
2. `MtkW2Cmd`: "status seen 20 odd 0 refused 0". The status field is where Linux reads it, for all 20 answers of the
   join, and the firmware refused none of them. No "command ... refused" line in the kernel log.
3. `MtkW9Power`: "clc 0, sku 2g failed 0, sku 5g failed 0", so the firmware took all 17 messages of the longer
   5 GHz list.
4. Core, Native and Bt report 0.15.5; `MtkBtState` ready, controller On. The bluetoothd user fault report of I-145
   was written again (23:11:09).

The link also survived the WindowServer restart of N-386 two minutes later (gateway answers, no rejoin:
`joins 1`, `rejoins 0`).

So on our machine no DEV_INFO, BSS_INFO or STA_REC command is refused in a normal WPA2 join on 5 GHz. That takes
"a refused command we never noticed" out of the list of causes for I-144 and I-143 as far as a plain join goes; the
counter stays in the driver for the cases those issues are about (roam, rekey, a second link).

Files: `post-boot.txt`, the two OpenCore logs (redacted). Guard captures stay in `~/.cache/legion/wifi/N-385-pass`.
