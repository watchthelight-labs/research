# N-381: WTLWireless 0.15.4 and LegionCpuPower 0.4.2

Staged 2026-11-26 about 14:05 EST on Bash's word ("Stage 0.4.2 and 0.15.4 and reboot"), from boot N-380 (Hybrid).

## What changed on OCEFI
- `WTLWireless.kext` 0.15.4 through `wifi-guard/stage.sh N-381 E` (boot-args unchanged). Source: branch
  `wifi-sequoia-pr12` af8d78f3, the port of Elezorn's Sequoia pull request 12. On Tahoe it adds `getHW_ADDR` and new
  boot-args whose defaults keep today's behaviour. sha256 starts: core `8c86ed81f67a8364`, native `2de5a3e7e1d23601`,
  Bluetooth `4c1d1c487a9530dd`. Details: `evidence/native/wifi-sequoia-pr12/README.md`.
- `LegionCpuPower.kext` 0.4.2 (branch `lcp-0.4.2` 3536a62e, sha256 starts `6802e6f9caa40474`). The 0.4.1 kext was
  renamed to `LegionCpuPower.kext.0.4.1.bak` beside it. Details: `evidence/native/i-116-tester-225h/README.md`.
- Nothing else: no XeGfx change, no config entries changed.

## Rollback
- Wi-Fi: wifi-guard puts the last good set (0.15.3) back by itself when stage E fails.
- LegionCpuPower has no guard. If macOS does not come up: boot the USB stick (F12, last known-good config), mount
  OCEFI, rename `LegionCpuPower.kext` away and `LegionCpuPower.kext.0.4.1.bak` back.

## Pass list
1. wifi-guard: N-381 pass (lease, gateway answers, network name reported).
2. `kextstat`: WTLWireless, .Native, .Bt 0.15.4; LegionCpuPower 0.4.2.
3. `ioreg -rc WTLWirelessNative`: `MtkNativeAbiGeneration` = tahoe; Wi-Fi menu lists and joins; Bluetooth up.
4. `sysctl debug.legioncpu.status`: `hwp 1 (rewrites N, passes N, check 60 s)`, passes about 10 plus one a minute,
   `sched 1 (ok`; `sysctl debug.legioncpu.hwpcheck` reads 60.
5. Which GPU drives the panel (OpenCore log), as for every boot.

## Result: pass (2026-11-26, booted 13:34:42 EST)
Hybrid boot again: `Current FB at 0x70800000`, the Intel iGPU drives the panel. No panic file, no kext rollback.

1. wifi-guard: `N-381 pass`, lease and gateway 47 s after boot; it refreshed its last good set to 0.15.4.
2. Loaded: WTLWireless, .Native and .Bt 0.15.4, LegionCpuPower 0.4.2 (also XeGfxIntelFB 0.9, XeGfxAGDC 0.1.1,
   LegionCpuProbe 1.1.0 as before).
3. `MtkNativeAbiGeneration` = tahoe, `MtkNativeCoreOps` 6, `MtkState` "W6 pass: en1 passing traffic", `MtkW1Join`
   "state 5 joins 1 fails 0", `MtkW6RxTransInfo` "ok 55 undecrypted 0" (the I-142 path still works), ping without
   loss. Bluetooth: `MtkBtState` ready, system shows State On.
4. LegionCpuPower status: `hwp 1 (rewrites 24, passes 10, check 60 s)` at 47 s, passes 11 at about 70 s, 12 at
   about 3 min: ten passes at start, then one a minute, where 0.4.1 made one a second. `rewrites 24` is the one
   write per CPU at the start. `sched 1 (ok, favoured 0x400400, avoid 0x3fc3fc)` as before, `hwpcheck` reads 60.
5. Panel: Intel iGPU.

Not exercised: `getHW_ADDR` was not seen being called (no trace line looked for), the new boot-args, a join
without a private address. LegionCpuPower 0.4.2 lowers the rendezvous rate 60 times; whether that ends the I-116
panics is not known from one short boot.

Seen, not from this change: `ExcUserFault_bluetoothd` (EXC_GUARD, application triggered fault, non-fatal) is
written at every boot today (12:06 N-379, 12:39 N-380, 13:35 N-381); Bluetooth works. The package reached 102 to
103 C in the first two minutes after login (boot load, I-138), 89 C a minute later.

Files: `post-boot.txt` (the readings), `opencore-2026-11-26-183435.txt` (redacted). The guard's capture stays in
`~/.cache/legion/wifi/N-381-pass` (it holds addresses and the network name).
