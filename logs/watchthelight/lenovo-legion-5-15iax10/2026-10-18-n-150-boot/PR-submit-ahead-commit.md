**What was wrong**

A command buffer committed while the execution worker was blocked in a fence wait reached the GPU, and counted as scheduled, only after that wait ended. WindowServer waits for its swap's command buffer to be scheduled (`commitAndWaitUntilSubmitted`), so compositing and the GPU took turns. On a 165 Hz panel a window drag ran at about 35 flips per second.

**What this changes**

The submit-ahead pass also runs from `nvmtl_pump_buffers` when the worker is busy. The worker claims a part under the class lock before it submits it itself, and the pass stops at a claimed part, so a part is never submitted twice or retired under the worker. `NVMTL_COMMIT_AHEAD=0` restores the worker-only pass.

**How I tested it** (card, macOS version, what you ran or did)

RTX 5070 Laptop (GB206, 10DE:2D18), macOS 26.7.1 (25G241), Lenovo Legion 5 15IAX10, 165 Hz internal panel. A plugin build with only this change on top of 2.3.5: window drag measured with a small flip counter, three runs each, 63 flips per second dragging a Finder window and 64 with an empty window, against 35 and 45 with the build before it on the same desktop. Still short of the panel rate. The plugin on this branch (on top of 2.3.6) builds with the release command line, 0 errors, minos 15.0; the 2.3.6 build itself has not been booted here yet.
