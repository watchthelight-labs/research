<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-294/README.md | author: watchthelight </wtl> -->
# N-294: NvGfx 2.6.2-nvgfx.1, Discrete (2026-10-27 15:53 EDT)

Change: NvGfx 2.6.2-nvgfx.1 package (NullMoth 2.6.2 base plus the fork; HiDPI flag for I-059, sampler restore for
I-049, PR #385 for I-117), then the xe-2.6.2 superset plugin e429fca1 in place of the package plugin. gpu-guard
rollback was 2.5.3-nvgfx.1.

Result: pass. OpenCore log: FB at 0x6000000000 (NVIDIA), kernel patches OK, EXITBS 19:52:45 UTC. Bash clicked Good
in the guard dialog at 15:56 (`ok` = dialog). Loaded: NVRM, NVRMFB, NVAccel 2.6.2 (the package's Tahoe variant,
c91f6759), NVRMAGDC 2.6.2. Metal 3, 1680x1050 HiDPI at 165 Hz.

- `i117-depthwise-system.txt`: the I-117 MPSGraph depthwise test through the installed plugin gives 4 / 9 / 6 as
  expected (before: translator abort on the phi). I-117 is fixed on hardware.
- `guard-login/`: the guard's login capture (kexts, sysctls, NVRM props, dmesg).

Still to check with Bash: the scaled-mode list in System Settings > Displays (I-059; the public CoreGraphics list
hides HiDPI duplicates by design, 23 HiDPI modes are present), Dock blur (I-049), window drag and an OpenGL
terminal (the two state-cache commits from nullmoth #412).
