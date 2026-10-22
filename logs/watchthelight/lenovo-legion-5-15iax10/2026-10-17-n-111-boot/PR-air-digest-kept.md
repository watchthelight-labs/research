**What was wrong**

`nvmtl_air_state` keeps a module's AIR digest only on strings that are not a kind of `NSMutableString`. On macOS every CF-backed string is one, including the strings `stringWithContentsOfFile` returns, so the digest was never kept. Every reflection, specialization and sampler-variant lookup converted and hashed the module's AIR again. VideoToolbox builds a library, a function and a pipeline for each transfer, so the System Settings Displays pane spends most of its CPU on this. Probably the same thing as #240.

**What this changes**

The strings `nvmtl_air_to_text` returns (cache hit, in-memory conversion, file conversion) get an associated marker, and `nvmtl_air_state` keeps the digest on marked strings instead of testing the class. Short strings stay unmarked, as before.

**How I tested it** (card, macOS version, what you ran or did)

RTX 5070 Laptop (10DE:2D18) in a Lenovo Legion 5 15IAX10, macOS 26.7.1 (25G241), NullMoth 2.3.7 kexts and package. I built the plugin from v2.3.7 with and without this change (release flags), installed each as the system plugin, then opened the Displays pane in a fresh System Settings three times and read DisplaysExt's CPU time 12 s later.

- v2.3.7: 7.64, 7.70, 8.01 s
- v2.3.7 with this change: 3.58, 3.63, 3.76 s

Builds clean with the release line (minos 15.0).

- [x] I wrote this change and this description myself (not an AI tool), and I can explain every line.
