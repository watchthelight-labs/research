# N-361: 25G416 with MtkWlanNative allow-listed for its xnu (I-132 fix check)

Boot 2026-11-10 18:09 EST, Hybrid (FB at 0x70800000), OCEFI. Change since N-360: the 25G416 entry in
`MtkWlanNative.kext/Contents/Info.plist` on OCEFI, added from Windows (binary 0.4.15 unchanged). LegionCpuPower still off,
XeGfxIntelFB/XeGfxAGDC still parked.

## Result: pass
- `sw_vers`: 26.7.3 25G416, kernel xnu-12377.161.15.702.13~1.
- MtkWlan: `MtkFrontEndWanted native`, `MtkFrontEndActive native`, `MtkNativeAbiBuild 25G416`, join requests 1 ok 1,
  about 170000 frames received, none dropped (ioreg-mtkwlan.txt). en1 has a lease and the internet answers.
- Bluetooth: MtkBt `ready`.
- No panic files.
- This also closes N-359's pass list (the install itself worked on the first try, no I-131 refusal), except the NVIDIA
  line, which needs a Discrete boot with gpu-guard and Bash's Good.

## Not checked
- The Wi-Fi menu itself (no one looked at the screen for this check; the properties above are the driver's view).
- LegionBtFix window counters.
