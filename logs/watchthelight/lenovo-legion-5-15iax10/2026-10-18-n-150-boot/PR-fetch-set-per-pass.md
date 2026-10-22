**What was wrong**

The framebuffer fetch descriptor set only names the pass's colour views, which do not change between the draws of a pass, but it was allocated and written for every draw. In a WindowServer profile of a window drag that was about a millisecond per frame.

**What this changes**

`nvmtl_fetch_set` keeps the last set with its mask and views and hands it back while they match; `nvmtl_fetch_set_make` does what the function did before. The set is freed with the command buffer's other sets, where the pointer is cleared.

**How I tested it** (card, macOS version, what you ran or did)

RTX 5070 Laptop (GB206, 10DE:2D18), macOS 26.7.1 (25G241), Lenovo Legion 5 15IAX10. Booted in a plugin build that also carried the newFunctionWithName cache change: no crash, composited output unchanged to the eye, but a window drag measured lower than the build before it (43 to 50 flips per second against 63) while a plain Core Animation animation also dropped from 165 to 113 per second with heavy post-boot indexing running; the cause is not isolated and this change alone has not been measured. The plugin on this branch (on top of 2.3.6) builds with the release command line, 0 errors, minos 15.0.
