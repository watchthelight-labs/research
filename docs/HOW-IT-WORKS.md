<!-- <wtl> project: research | file: docs/HOW-IT-WORKS.md | author: watchthelight </wtl> -->
# How it works

## Redaction (`tools/redact.py`)

Redaction runs in four passes over the text, in this order:

1. **Keyed values.** A table of keys that hold an identity: `IOPlatformSerialNumber`, `Serial Number (system)`, `MLB`, `ROM`, `Hardware UUID`, `SSID`, `BSSID`, `Computer Name`, the OpenCore `OC: Setting SSN/MLB/ROM` lines and so on. Whatever value follows the key (quoted, `<hex>`, or bare up to the end of the field) is swapped for a token. Values that are already placeholders (`<redacted>`, `(null)`, `<private>`) are left alone.
2. **Network blocks.** In `system_profiler SPAirPortDataType` output, network names aren't keyed, they're indented headings under "Current Network Information:" and "Other Local Wi-Fi Networks:". Those headings become `SSID-n`.
3. **Shapes.** UUIDs, MAC addresses, IPv6 (only `::` forms or the full eight groups, so clock times survive), IPv4 (with tcpdump's `address.port` form handled, and four-part version numbers after "version" left alone), e-mail addresses, and the user name in home-folder paths. A short allowlist keeps public constants: EFI variable GUIDs, GPT partition types, broadcast and loopback addresses.
4. **Second guard.** Every original value the machine has ever had is replaced anywhere it appears, longest first. This catches a serial printed without its key, or a network name inside a sentence.

Tokens are numbered per machine and kind (`MAC-1`, `MAC-2`) and stored in a private map outside this repo, so the same value gets the same token in every log from that machine.

`leftovers()` then looks for anything that still has the shape of an identity: a UUID or MAC that isn't on the allowlist, a serial key followed by a serial-shaped value, or a token, key or password. If it finds one, the file is refused.

## Ingest (`tools/ingest.py`)

Given an issue, it reads the issue and every comment through `gh api`. Fenced code blocks of five lines or more (or shorter ones that are clearly an ioreg, panic, OpenCore or kernel log) and attached `.txt`/`.log`/`.panic` files become one log set per post, filed under the post's author. Given local files, it takes the list plus `--user`, `--machine` and `--source`.

Every file is redacted, and so are file names, since they can carry a host name. If one file is refused, nothing from that post is written.

`logs/ingested.json` remembers each post URL and each local file's hash, so running it twice adds nothing. `machines.json` gets the model, the chips and every macOS build seen. The build is only read next to a label ("macOS", "Build", "ProductBuildVersion") or as "26.7.1 (25G241)", so hex dumps don't count.

## The privacy check (`tools/privacy_check.py`)

CI runs it on every push, and it scans each tracked file with `leftovers()`. Run locally with the private map, it also checks that no original value from the map appears anywhere. `--fix` runs the redactor again over every log first, because a value learned from a later log (a network name, say) wasn't known yet when an earlier log of the same machine was redacted.

## The index (`tools/index.py`)

`INDEX.md` is generated from the `meta.json` files and `machines.json`: a table of machines, then each person's machines with their log sets, newest first, then the scout reports.

## The scout

The scout itself runs from the private project repo. It reads the watchlist, collects what changed in each related repository since its last run, searches for new related projects, and has the findings read and judged. What lands here is the write-ups in `scout/<project>/`, the run reports in `scout/reports/` and the public copy of the watchlist (`scout/watchlist.json`).

The `related-watch` workflow in this repo posts a short digest of new releases and commits to Discord every few hours, so nothing big waits for the next daily run.
