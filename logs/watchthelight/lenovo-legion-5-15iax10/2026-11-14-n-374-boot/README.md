# N-374: NvGfx 2.9-nvgfx.1 trial on a Discrete boot

Prepared on the Mac on 2026-11-14 at 09:10 EST, on an ordinary NVIDIA boot (RTX 5070, Metal 3, 165 Hz, installed driver
2.6.2-nvgfx.1). Bash gave the OK for this trial in the Windows session of 2026-11-14; his Good at the gpu-guard after
the boot is still his to give. The install and the restart wait for his word, because he is working on the machine.

## Change
- Package `~/src/NvGfx-build/pkg/2.9-nvgfx.1-nr`: NullMoth 2.9 with our plugin, translator, NVRM, NVRMFB and NVAccel
  (fork branch `nvgfx-2.9`, 9d492cf) and NVIDIA's 620.70.06 firmware carried over, so nothing is downloaded.
- Against the first 2.9 package (`pkg/2.9-nvgfx.1`, eb14b62) only `install.sh` differs: the two `shutdown -r now`
  lines of upstream's fallback job and boot guard are log lines now (Bash approved, 2026-11-14). All other 89 files
  are byte-identical, `SHA256SUMS` checks, `sums_complete.sh` passes, `bash -n` is clean. Restarts and rollback stay
  with our gpu-guard.
- NVRAM: the installer and the two upstream jobs use the `nullmoth-nv-starts`, `nullmoth-nv-ok` and `nullmoth-remove`
  variables as 2.6.2 does. New in 2.9 is `nullmoth-ws-loop`, written only when WindowServer loops.

## Steps (main session, when Bash says go)
1. `cd ~/src/NvGfx-build/pkg/2.9-nvgfx.1-nr && sudo bash install.sh` (rebuilds the auxiliary collection; the knobs in
   the my-settings block of `nvrm610.conf` stay).
2. `native/tools/gpu-guard/stage.sh N-374 "2.9-nvgfx.1" ~/src/NvGfx-build/pkg/2.6.2-nvgfx.1`, tracker row, commit.
3. `legion-reboot N-374 "nvgfx 2.9-nvgfx.1 trial"`. Bash picks the NVIDIA panel as today.
4. After login Bash has 180 s for Good. No mouse tests before it. After Good: the early-drag spindump
   (`evidence/native/i-069-bisect/early-drag-spindump.sh N-374`), `nvgfx-smi`, the window drag rate, HiDPI modes.

## Undo
- No Good within 180 s: the gpu-guard installs `pkg/2.6.2-nvgfx.1` (its installer also rewrites the boot guard) and
  restarts once.
- Screen black at the login window: nothing restarts by itself any more. Hold the power button, start again: the
  driver is then off for that start (upstream's counter), the desktop comes up unaccelerated, log in, and the
  gpu-guard rolls back.

## Pass
- Bash's Good; `/Library/NullMoth/driver-version` 2.9; Metal 3 at 165 Hz; 115 W through `nvrmtgp=1`; no WindowServer
  report since boot.

## Install (2026-11-14 09:07 EST, Bash: go)
Installer rc 0 in 11 s: package integrity ok, test collection holds all four kexts, backup
`/Library/NullMoth/backup-20261114-090716.h2fRL8`, 3 settings lines of `nvrm610.conf` kept, air and spv caches start
empty, boot-args untouched. `/Library/NullMoth/driver-version` reads 2.9; `lastgood.sh` and `bootguard.sh` carry the
log line in place of the restart. Manual undo: `sudo ./uninstall.sh` with that backup folder.

## Result: pass (2026-11-14, boot at 09:08:55 EST)
- OpenCore (`opencore-2026-11-14-140835.txt`, redacted): Current FB at 0x6000000000, so the panel is on the NVIDIA
  GPU. 6 kernel patches applied, prelinked status Success, EXITBS 14:08:42 UTC.
- Login 09:10:22. Bash pressed Good in the gpu-guard dialog at 09:10:55 (`ok` = dialog), 33 s into the 180 s window.
  No rollback, no second restart. Upstream's boot guard logged "the desktop came up and stayed up (WindowServer 215
  for 45 s); this start counts as good" and cleared `nullmoth-nv-starts`; `nullmoth-nv-ok` is 1.
- Loaded: NVRM, NVRMFB, NVAccel (package 2.9), NVRMAGDC 2.9, NMIntelFB 0.3. `/Library/NullMoth/driver-version` 2.9,
  plugin 2f185ed8b545 as staged. `nvrm-display` "heads 0x1 accel 4 agdc 1 k5 1 iop 1", boot raster 165 Hz.
- System Information: RTX 5070 Laptop GPU, 8 GB, **Metal 4** (2.6.2 reported Metal 3), panel "Legion 5 panel (NvGfx
  HiDPI)" at 1512x945 HiDPI (3024x1890 pixels), 165 Hz.
- `nvgfx-smi`: enforced power limit 115000 mW (`nvrmtgp=1`), graphics clock 2767 MHz, GPU 66 C under the drag load.
- No WindowServer or kernel report since boot (`guard-login/crashes.txt` is empty, DiagnosticReports has nothing
  newer than the install).
- `modes.txt` (`native/tools/display/setmode.py list`): 87 modes, 34 of them HiDPI, at 60 and 165 Hz. A session
  switch to 1680x1050 HiDPI at 165 Hz took and went back by itself.

### Drags and the WindowServer spindumps (I-069, I-136)
`early-drag-spindump.sh N-374 3` started late, at +163 s after login, because the session only came back then, so
the first 160 s (where the slow phase used to be) are not measured on this boot.
- `drags.txt`: 81 to 92 flips/s in nine runs from +164 s to +244 s, and 87 to 91 afterwards. Never the 4 to 26
  flips/s of the old slow phase (N-160, N-168).
- `frames.txt`: the spindump at +164 s has WindowServer's `com.apple.coreanimation.pipelines` thread in
  `CA::OGL::MetalContext::create_fragment_shader` for 478 of 600 samples (437 in the translator's `translate_one`),
  no `writeToFile`, one `fsync`. The one at +244 s has none of it. The caches were empty after the install, so this
  is the cold translation, and the drags kept their rate while it ran.
- New, I-136: the steady rate is about 90 flips/s, where earlier builds measured 147 to 148 (N-160, N-186). It is
  the same at 1512x945 and at 1680x1050 HiDPI (89 each), so it is not the mode. There is no same-day 2.6.2 figure.
- The two spindumps are 12 MB each and stay out of git: `~/.cache/legion/gpu/N-374-spindump/`.

### Other observations
- I-137: brightness reads 65535 of 65535 after the restart and NVRAM `nullmoth-backlight` is `02 ff ff`. That
  matches upstream #582 (backlight back at 100 % after every restart on 2.9), fixed in 3.0. The level before the
  restart was not recorded, so it is a match, not a proof.
- The kernel log has 28 sandbox denials of `iconservicesagent` for `file-write-times` on its `nvmtl/spvcache`
  files (`guard-login/dmesg-nvidia.txt`): the plugin touches cache files from a process that may not.
- `guard-login/ioreg-fb.txt` is empty: the guard's framebuffer query matches nothing on 2.9.

### Next
NullMoth 3.0 came out on 2026-11-14 (driver and 1401). It has the backlight fix, a hybrid panel rework, 4:2:2 video
textures on by default, and an installer that adds `gfxrst=4` with WhateverGreen and keeps override HiDPI sizes.
Next step: rebase the fork onto 3.0, build, and trial it the same way (needs Bash's OK, as this one did).
