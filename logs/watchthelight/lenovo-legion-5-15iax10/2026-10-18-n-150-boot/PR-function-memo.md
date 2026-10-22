**What was wrong**

Every CF-backed string is a kind of `NSMutableString` on macOS, so the AIR digest `nvmtl_air_state` tried to keep on the module text never stuck. Each reflection, function-constant and variant lookup converted and hashed the module's megabytes of AIR again, `newFunctionWithName` scanned the text twice more for the dyld and intersection table markers and re-read the entry's SPIR-V for every library made from the same file, and `nvmtl_air_max_tg` walked the module for every pipeline state. VideoToolbox makes a library, a function and a pipeline for every transfer, so a System Settings pane with a video preview (Displays) spent most of its CPU time in those lookups.

**What this changes**

The strings `nvmtl_air_to_text` returns are marked and keep the digest, the two marker flags and the threadgroup sizes by function name. The entry's SPIR-V rides on its bitcode object, which the library index shares between libraries made from the same file. The function-constant, reflection and variant caches, and a new render sampler cache, memoize in this process even when no cache folder is writable (a sandbox that allows none), using the same digest as the file name.

**How I tested it** (card, macOS version, what you ran or did)

RTX 5070 Laptop (GB206, 10DE:2D18), macOS 26.7.1 (25G241), Lenovo Legion 5 15IAX10. In-process timing with the plugin loaded by a small test program: a VideoToolbox session's Metal setup (library, function, pipeline) took about 75 ms per call before and 2 ms once warm after. Booted in a plugin build that also carried the fetch descriptor set change: no crash, icons and panes rendered, but the Displays pane still spent seconds of CPU in translation misses, and a window drag measured lower than the build before it (43 to 50 flips per second against 63) while a plain Core Animation animation also dropped from 165 to 113 per second with heavy post-boot indexing running, so that comparison is not clean and the two changes have not been measured apart. The plugin on this branch (on top of 2.3.6) builds with the release command line, 0 errors, minos 15.0.
