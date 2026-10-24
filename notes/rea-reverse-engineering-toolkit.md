<!-- <wtl> project: research | file: notes/rea-reverse-engineering-toolkit.md | author: watchthelight -->
# REA (Reverse Engineer Anything) for Hackintosh driver work

Checked 2026-10-24. Source: https://github.com/morluto/rea (MIT). Confidence: High for what 6.7.0 does, Medium for the rest of the repo, which was read, not run.

## What it is

An agent-oriented reverse engineering toolkit: a Node CLI (`rea-agents` on npm), an MCP server, skills and docs. It parses Mach-O and PE files itself and can drive Ghidra, Hopper or IDA for deeper work.

## Audit verdict

Approved with conditions. Read the checkout only (shallow clone, no submodules, nothing run inside it). Install only the pinned `rea-agents@6.7.0` tarball (sha256 `20958a66dba1a011e50a486beb9463a343128ed368c984f94065362c13f51f90`) with `npm install --ignore-scripts --omit=optional` into a private prefix; that leaves out frida, the only dependency with an install script. Not approved: `curl | bash` installers, `npx rea-agents setup`, `rea setup`, `rea update`, `@latest`, Hopper, and the look-alike repos below.

## What 6.7.0 can and cannot do

- Can: Mach-O load commands, PE resources and inventory, with no engine installed.
- Cannot: PE imports, certificates, exports and `.ips` parsing. Those are on unreleased `main` only (the repo docs list them, the npm package does not have them). Use `llvm-objdump -p` for PE imports and exports.
- Has no dyld shared cache, kext, kernelcache or IOKit support. For QuartzCore and other cache frameworks use `dyld_info` plus lldb on a throwaway process; for kexts copy the file and use `nm`, `kmutil` and `llvm-objdump`.
- `trace_native_values` and the capture modes launch the target, so they stay off system binaries and drivers.

## Look-alike repos to avoid

Several repos and zips use the REA name. Fake REA zips in particular target Windows users. Take REA only from npm `rea-agents`, morluto/rea or rea.tools. The full do-not-use list is in the private audit.

## How we use it

A project skill `rea` (watchthelight-labs/agents, `claude/skills/rea`) scopes it to the Legion: dyld-cache frameworks, Apple GPU bundles and kexts, IOKit selector mapping, and NVIDIA or Intel Windows driver files copied off the read-only Windows volume. Work happens on copies, results go to the evidence folder of the task. The skill keeps the MIT notice with credit to morluto/rea and has no `npx -y` lines. Decompiling needs Ghidra 12.1.4 and a JDK, which are pinned but not installed; the Ghidra zip has no macOS decompiler, so it has to be built from the bundled source.
