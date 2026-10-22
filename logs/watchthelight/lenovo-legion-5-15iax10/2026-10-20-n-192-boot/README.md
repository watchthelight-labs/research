<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-192/README.md | author: watchthelight </wtl> -->
# N-192: macOS in BIOS Hybrid mode with -nvoff (2026-10-20 17:58)

Change: `-nvoff` on OCEFI (no NVIDIA driver), BIOS Hybrid. OpenCore log `opencore-2026-10-20-215808.txt`: GOP has 9
modes, `Current FB at 0x70800000` (Intel iGPU). Screen (Claude web photo 17:59, note 8b723bfd): verbose text to the
login stage, no GUI.

Unified log of that boot (it ends about 18:00, when Bash powered off): the iGPU nub published with an
`IONDRVFramebuffer` at 17:58:18.17, AGPM initialised for IGPU, and WindowServer at 17:58:18.95 went straight to
`setup_virtual_framebuffers` ("Setting offline display 0x00000000 main in CGXConstructVirtualFramebuffer"). So the
firmware framebuffer on the iGPU is not usable by WindowServer on Tahoe, the I-037 shape without `-wegnoigpu`. That
also means the planned N-193 (stock NVIDIA stack headless on the same IONDRV) would show nothing either, so the next
boot puts NMIntelFB in front of the panel instead.

Afterwards a Windows Claude Code session removed `-nvoff` from OCEFI (config = `config.n192.plist.bak`, the -nvoff file
kept as `config.n193.plist.bak`) and Bash set the BIOS back to dGPU.
