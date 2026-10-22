<!-- <wtl> project: research | file: README.md | author: watchthelight </wtl> -->
# research

Every log behind the [watchthelight-labs](https://github.com/watchthelight-labs) Hackintosh projects, ours and the ones people send in, plus a running record of what related projects are doing. If you're debugging an MT7925, an Arrow Lake laptop, NullMoth on Blackwell or an Intel Xe iGPU on macOS, there's a good chance someone already hit your problem and the log is here.

Everything is redacted before it lands (see below). Start with [INDEX.md](INDEX.md).

## What's in here

| Path | What |
|---|---|
| `logs/<username>/<machine>/<date>-<source>-<topic>/` | One log set: the files as they were sent, redacted, and a `meta.json` saying where they came from (issue link or boot attempt), the project, the macOS build and what the redactor replaced |
| `machines.json` | One entry per person and machine: model, CPU, GPU, chips, the macOS builds seen |
| `scout/<project>/<date>.md` | What changed in related projects that day and whether it matters to ours, with links |
| `scout/reports/<date>.md` | The full report of each scout run |
| `INDEX.md` | Generated: every machine and log set, newest first |
| `tools/` | The redactor, the ingest tool, the index builder, the privacy check |

`<username>` is the GitHub account that posted the log. `<machine>` is the vendor and model, for example `lenovo-legion-5-15iax10` or `asus-tuf-gaming-b850-plus-wifi`, with `-2` added when one person has two of the same.

## Redaction

Before a log is written here, `tools/redact.py` replaces anything that identifies a machine, a person or a network:

- Apple serials, MLB, ROM, system and hardware UUIDs, other UUIDs
- MAC addresses and BSSIDs, Wi-Fi network names, IPv4 and IPv6 addresses
- e-mail addresses, host names, the user name in `/Users/<name>` and `C:\Users\<name>` paths
- tokens, keys and passwords (a log that has one is refused, not redacted)

Each value becomes a token that stays the same for that machine (`SERIAL-1`, `MAC-2`, `SSID-1`), so you can still follow one device or one network through a log, and across that machine's logs. The table that maps tokens back to values is private and never committed here. Public constants that only look like identifiers (EFI variable GUIDs, GPT partition types, `255.255.255.0`) are left as they are.

A file that still looks identifying after redaction is not written at all, and `tools/privacy_check.py` runs on every push.

If you spot something that should have been removed, open an issue (don't paste the value) and it'll be fixed and scrubbed from history.

## Sending a log

Open an issue with the **Submit logs** form, or attach logs to an issue in the project repo they belong to; both get picked up. Say which machine it's from. Paste text rather than screenshots when you can. Logs are published here redacted, under CC BY 4.0.

Useful ones: `ioreg -l -w0`, `log show --last 10m --predicate 'sender CONTAINS "<KextName>"'`, `system_profiler SPHardwareDataType SPBluetoothDataType SPAirPortDataType`, `kmutil showloaded`, your OpenCore log (`opencore-*.txt` with `Target` 67) and any `.panic` files from `/Library/Logs/DiagnosticReports`.

## The scout

A daily job reads every project ours build on or learn from, plus searches for new ones, and writes up what changed: new releases, commits that touch the same hardware, forum threads. When it finds something we learn from, the matching project here gets a credit and a link in its README the same day. `scout/watchlist.json` lists what it follows.

## Licence

Logs and write-ups: CC BY 4.0. Code in `tools/` and `tests/`: ISC. Both texts are in [LICENSE](LICENSE).

How the tools work, step by step: [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md).
