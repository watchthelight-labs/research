<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-195/README.md | author: watchthelight </wtl> -->
# N-195: dGPU mode, no -nvoff, NMIntelFB 0.1 installed (2026-10-20 19:30)

Same config as N-194. OpenCore log `opencore-2026-10-20-232942.txt`: 15 GOP modes, `Current FB at 0x6000000000`
(NVIDIA). AuxKC loaded at 19:31:05, NMIntelFB declined (no lit Intel pipe), NVRM boot hold `display armed` at 19:31:47,
`Metal compositor activated` at 19:32:30. Bash: "I do have acceleration rn". PASS.

During this boot: NMIntelFB 0.2 (NVRAM step breadcrumbs) built and installed in the AuxKC, the kext auto-approver
installed (`native/tools/kext-autoapprove`), OCEFI boot-args end in `-nvoff` again for N-196.
