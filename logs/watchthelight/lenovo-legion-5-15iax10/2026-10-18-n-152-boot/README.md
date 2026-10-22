# N-152: rollback boot, 2.3.5-nvgfx.5 reinstalled after I-069

Boot 11:13 (kernel), check 11:16. Loaded: NVRMFB 2.3.5, NVRMAGDC 2.3.5, NVRM 0.1, NVAccel 2.3.5; plugin
08c59a70009c (2.3.5-nvgfx.5). Panel updates again. Power limit 115 W enforced, `debug.nvgfx_tgp_applies 1`.
Crash reports since boot: 0 (a shutdownStall from the N-152 reboot at 11:12:38 only). Wi-Fi: native set unchanged,
wifi-guard still shows N-150 stage E pass.

Drag (`evidence/native/N-134/run.sh`, 8 s Finder title-bar drag, `drag.txt`): the first two runs without a Finder
window open read 11 flips/s (the drag hit the desktop), with a Finder window 59, 61, 61 flips/s and 59, 62, 61
presents/s, the 2.3.5-nvgfx.5 baseline (63 on N-135).

Result: PASS. 2.3.5-nvgfx.5 is the installed driver again.

## What the N-151 numbers say about I-069

`N-151/sysctl-nvrmfb-nvaccel.txt` (taken 11:12, after the three 0 flips/s drag runs): `nvaccel_iop_flips 2214`,
`nvrmfb_flip_n 2214`, `nvrmfb_flip_latch_waits 2217`, `latch_timeouts 0`, `flip_latch_max_us 6437`,
`nvaccel_vm_parked 8 / unparked 2 / park_released 6`. The flip path on 2.3.6 worked for about 2200 flips (login and
the first desktop seconds) and then stopped; the counters are the 2.3.5 ones and still count on 2.3.6. The upstream
2.3.5..2.3.6 kext diff is 93 lines: NVRMFB moves the cursor position to a thread call (`fCursorCall`, position-only
cursor flips through NVKMS's immediate channel, the surface named only when the image or visibility changes),
NVAccel restores a parked allocation before a dirty mark (`nvAccelRestoreParkedForDirty`, PR 245). The fork changes
no NVRMFB or NVAccel source; its NVRM carries the power glue and the viewport scaling patch. Next: N-153 with the
stock 2.3.6 package untouched.
