<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-220/README.md | author: watchthelight </wtl> -->
# N-220: NvGfx 2.5.3-nvgfx.1 (NullMoth 2.5.3, NVIDIA 615) (staged 2026-10-22 11:25 EDT), BIOS Discrete

Change since the last NVIDIA boot: NvGfx 2.4.3-nvgfx.1 -> 2.5.3-nvgfx.1 (fork branch nvgfx-2.5.3, 95ba277).
- Base NullMoth 2.5.3 (audited, research/repository-audits/nvidia-macos-driver.md G3d): NVIDIA 615.78.08 RM and GSP
  firmware, HiDPI/scaled modes, sRGB writes, XR video formats, our boot hold (PR #317) upstream.
- Our NVRM rebuilt for 615 (build_nvrm.sh with NVRM_TAG=615.78.08): identical to the shipped NVRM in 30875 of 30884
  functions; the rest are the fork's power code (115 W TGP on AC, NVPCF/GPS _DSM, physctl) and two kapi helpers.
- Our plugin (release build) on 2.5.3's sources.
- Opt-in primary-GPU selector and HDMI audio: off.
Guard: gpu-guard, recovery package 2.4.3-nvgfx.1, Bash says Good within 180 s of login.
Check after the boot: NVRM 615 loaded, desktop at 165 Hz, `sysctl debug.nvgfx_tgp_state` (115 W on AC), nvgfx-smi
power, the new BAR0 temperature poll during the slow GSP bring-up (audit red flag), I-085 without NVMTL_NO_POOL_REUSE.

## Result (2026-10-22 11:27 EDT): PASS (Bash pressed Good in the gpu-guard dialog at 11:26:53)
- OpenCore: Discrete mode (`Current FB at 0x6000000000`), no picker.
- Loaded: NVRM (our 615 build), NVRMFB 2.5.3, NVAccel 2.5.3, NVRMAGDC 2.5.3. Metal 3 on the RTX 5070.
- Panel: 1680x1050 HiDPI at 165 Hz (scaled mode, so the 615 viewport patch works in our NVRM build).
- 115 W: `debug.nvgfx_tgp_state=1 ac=1 applies=1 last_status=0`, the fork's power code works on 615.
- GSP bring-up `go(2)` took 13.3 s (610 took 40 to 48 s); boot hold released 11:26:02.
- No crash reports. gpu-guard captures in `N-220-login/`, NVRM function comparison in `nvrm-compare.txt`.
Open: A/B of the async surface upload against upstream's host-import path; I-085 without NVMTL_NO_POOL_REUSE=1;
watch the new BAR0 temperature poll (audit G3d).
