<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-282/README.md | author: watchthelight </wtl> -->
# N-282 (2026-10-24 09:15 EDT): XeGfxIntelFB 0.1 in the AuxKC + xe-guard stages-only

Change: XeGfxIntelFB 0.1, an IONDRVFramebuffer subclass named XeGfxIntelFramebuffer (I-108 plan step 1a, Bash's ok),
installed in the AuxKC. OCEFI unchanged. Panel on the Intel iGPU (OC log: Current FB at 0x70800000).

Result: **pass**.
- `ioreg-framebuffer.txt`: display0 (`.Display_boot`) is `XeGfxIntelFramebuffer`; panel, console and desktop as before.
- `guard/`: xe-guard stages 1-7 pass, xe-post rc 0, WindowServer stable 60 s; mtlbench draw avg 5.32 ms, 0 of 1024 wrong.
- `xeintelfb-log.txt`: kernelmanagerd logs "invalid codeful kernel extension in the restricted lookup table" for it
  (it loads from the AuxKC regardless, as NMIntelFB did).
- Problem found: the boot guard counted start 1 and never cleared. IOGraphics handles kIOWindowServerActiveAttribute
  itself and does not pass it to the subclass's setAttribute, so the next boot would have declined. Counter cleared
  by hand; XeGfxIntelFB 0.2 clears the guard when WindowServer opens the server connection (newUserClient type 0).

Not tested here: CoreDisplay's vendor mask and IOPresentment. They need a WindowServer run and step 2 (AGDC up at boot,
head 4 in AGDC 0x980, display pipe capabilities, transaction completion), see docs/plans/xe-head4-iop.md.
