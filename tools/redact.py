#!/usr/bin/env python3
# <wtl> project: research | file: tools/redact.py | author: watchthelight </wtl>
"""Redact a log before it goes into this public repo.

Hardware identity and network data become tokens that stay the same for one machine (SERIAL-1, MAC-2,
SSID-1 ...), so two logs from the same machine still line up. The value-to-token map is private and
lives outside this repo (pass it with --map); without it the tokens are still consistent inside one run.

  python tools/redact.py --map <private map.json> --machine <username>/<machine> <in> [<out>]

As a module: redact(text, machine, mapping) -> (text, hits) and leftovers(text) -> [problems].
Works on Python 3.9 (the macOS system Python).
"""
import argparse
import json
import re
import sys
from pathlib import Path

VERSION = "1"

# Public constants that look like identifiers but identify nobody: EFI variable GUIDs OpenCore and Apple
# use, GPT partition types, all-zero/broadcast values, loopback and unspecified addresses.
ALLOW = {
    # EFI / OpenCore / Apple NVRAM GUIDs
    "7C436110-AB2A-4BBB-A880-FE41995C9F82", "4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14",
    "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B38C14", "8BE4DF61-93CA-11D2-AA0D-00E098032B8C",
    "5EDDA193-A070-416A-85EB-2A1181F45B18", "E09B9297-7928-4440-9AAB-D1F8536FBF0A",
    "36C28AB5-6566-4C50-9EBD-CBB920F83843", "D8F0CCF5-580E-4334-87B6-9FBBA831271F",
    "8D63D4FE-BD3C-4AAD-881D-86FD974BC1DF", "EB704011-1402-11D3-8E77-00A0C969723B",
    "4D1FDA02-38C7-4A6A-9CC6-4BCCA8B30102", "BE74FCF7-0B7C-49F3-9147-01F4042E6842",
    "64517CC8-6561-4051-B03C-5964B60F4C7A",
    "00000000-0000-0000-0000-000000000000",
    # GPT partition types
    "C12A7328-F81F-11D2-BA4B-00A0C93EC93B", "7C3457EF-0000-11AA-AA11-00306543ECAC",
    "48465300-0000-11AA-AA11-00306543ECAC", "EBD0A0A2-B9E5-4433-87C0-68B6B72699C7",
    "E3C9E316-0B5C-4DB8-817D-F92DF00215AE", "DE94BBA4-06D1-4D40-A16A-BFD50179D6AC",
    "426F6F74-0000-11AA-AA11-00306543ECAC", "52637672-7900-11AA-AA11-00306543ECAC",
    "0FC63DAF-8483-4772-8E79-3D69D8477DE4",
    # MACs and addresses
    "00:00:00:00:00:00", "FF:FF:FF:FF:FF:FF", "0.0.0.0", "127.0.0.1", "255.255.255.255", "255.255.255.0",
}

HEX = r"[0-9A-Fa-f]"
UUID_RE = re.compile(rf"\b{HEX}{{8}}-{HEX}{{4}}-{HEX}{{4}}-{HEX}{{4}}-{HEX}{{12}}\b")
MAC_RE = re.compile(rf"(?<![0-9A-Fa-f:-]){HEX}{{2}}([:-]){HEX}{{2}}(?:\1{HEX}{{2}}){{4}}(?![0-9A-Fa-f:-])")
# a full stop right after an address ends a sentence; only a digit (or ".digit") means it is part of a longer number
IPV4_RE = re.compile(r"(?<!\d)(?<!\d\.)((?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3})(?!\d|\.\d)")
# IPv6 candidates; _is_ipv6 then keeps only "::" forms or the full eight groups, so clock times (12:34:56)
# and MAC-like strings are left alone
IPV6_RE = re.compile(rf"(?<![\w:])((?:{HEX}{{0,4}}:){{2,7}}{HEX}{{0,4}}(?:%\w+)?)(?![\w:])")


def _is_ipv6(s: str) -> bool:
    core = s.split("%")[0]
    groups = [g for g in core.split(":") if g]
    return len(groups) >= 2 and ("::" in core or core.count(":") == 7)
# tcpdump prints address.port ("192.0.2.1.68"): take the four octets, keep the port
IPV4_PORT_RE = re.compile(r"(?<![\d.])((?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3})\.\d{1,5}(?=[\s:,>)]|$)",
                          re.M)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
HOME_RE = re.compile(r"(/Users/|/home/|[A-Za-z]:\\Users\\)(?!Shared\b|USER\b|Public\b|Default\b)([^/\\\s\"'<>:]+)")

# key  ->  (token kind, value pattern). Matches ioreg ("Key" = "value" / <hex>), plist, JSON, system_profiler
# ("Key: value") and OpenCore ("OC: Setting SSN value") lines.
KEYED = [
    (r"OC: Setting (?:HW_)?SSN", "SERIAL", r"\S+"),
    (r"OC: Setting (?:HW_)?MLB", "MLB", r"\S+"),
    (r"OC: Setting (?:HW_)?ROM", "ROM", r"\S+"),
    (r"IOPlatformSerialNumber|SystemSerialNumber|Serial Number \(system\)|serial-number|SerialNumber|"
     r"Serial Number|SSN|BoardSerialNumber|ChassisSerialNumber", "SERIAL", None),
    (r"MLB|Board Serial", "MLB", None),
    (r"\bROM\b|HW_ROM", "ROM", None),
    (r"IOPlatformUUID|Hardware UUID|SystemUUID|Provisioning UDID|platform-uuid", "UUID", None),
    (r"\bSSID\b|SSID_STR|Network Name|ssid|Current Network", "SSID", None),
    (r"\bBSSID\b|bssid", "MAC", None),
    (r"Computer Name|Local Host Name|LocalHostName|HostName|hostname|ComputerName", "HOST", None),
    (r"supplying hostname|host name", "HOST", None),
    (r"Apple ID|AppleID|apple_id", "EMAIL", None),
]
# value shapes after the key: "quoted", <hex or quoted data>, or a bare token up to the end of the field
VALUE = r"(?P<q>\"[^\"\n]*\"|<[^>\n]*>|[^\s,;\"<>][^,;\n]*?)(?=\s*(?:$|[,;\n}\)]|\s{2,}))"
KEY_SEP = r"(?P<sep>\"?\s*(?:=|:)\s*)"

# a few things are never published, token or not
SECRETS = [
    (re.compile(r"(?i)-----BEGIN [A-Z ]*PRIVATE KEY-----"), "private key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}"), "GitHub token"),
    (re.compile(r"\b(?:xox[bpa]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9]{20,})"), "API token"),
    (re.compile(r"\b[MN][A-Za-z\d]{23,25}\.[\w-]{6}\.[\w-]{27,38}\b"), "Discord token"),
    (re.compile(r"(?i)\b(?:passphrase|password|psk|pmk)\b\s*[:=]\s*\S{6,}"), "credential"),
]


# placeholders other tools (and macOS's log privacy) already put in place of a value; never tokenised
PLACEHOLDER = re.compile(r"(?i)^\(?<?(?:redacted|private|null|nil|none|hidden|n/?a|unknown|-|)>?\)?$")


class Tokens:
    """value -> token for one machine, persisted in the private map."""

    def __init__(self, mapping: dict, machine: str):
        self.m = mapping.setdefault("machines", {}).setdefault(machine, {})

    def get(self, kind: str, value: str) -> str:
        key = value.strip().strip("\"<>").strip()
        norm = key.upper() if kind in ("MAC", "UUID", "SERIAL", "MLB", "ROM") else key
        if kind == "MAC":
            norm = norm.replace("-", ":")
        table = self.m.setdefault(kind, {})
        if norm not in table:
            table[norm] = f"{kind}-{len(table) + 1}"
        return table[norm]

    def known(self):
        for kind, table in self.m.items():
            for value, token in table.items():
                yield kind, value, token


def _keyed(text: str, tok: Tokens, hits: dict) -> str:
    for key, kind, shape in KEYED:
        if shape:   # OpenCore "OC: Setting X value"
            pat = re.compile(rf"(?P<k>{key} )(?P<q>{shape})")
        else:
            pat = re.compile(rf"(?P<k>\"?(?:{key})){KEY_SEP}{VALUE}", re.M)

        def sub(m):
            raw = m.group("q")
            inner = raw.strip("\"<>'").strip()
            if not inner or inner.startswith(kind + "-") or PLACEHOLDER.match(inner) or "redacted" in inner.lower():
                return m.group(0)
            if kind == "SSID" and inner.lower() in ("yes", "no", "on", "off", "true", "false"):
                return m.group(0)
            token = tok.get(kind, inner)
            hits[kind] = hits.get(kind, 0) + 1
            wrapped = f"\"{token}\"" if raw.startswith("\"") else f"<{token}>" if raw.startswith("<") else token
            return m.group(0)[: m.start("q") - m.start(0)] + wrapped
        text = pat.sub(sub, text)
    return text


def _pattern(text: str, regex, kind: str, tok: Tokens, hits: dict, group: int = 0) -> str:
    def sub(m):
        v = m.group(group)
        if v.upper() in ALLOW or v in ALLOW or (regex is IPV6_RE and not _is_ipv6(v)):
            return m.group(0)
        # "version 1.0.8.2", "v1.2.3.4", "ver 4.0.1.2": a four-part version, not an address
        if kind == "IP" and re.search(r"(?i)(?:\bversion|\bver|\bv)[\s:=]*$", m.string[max(0, m.start() - 12):m.start()]):
            return m.group(0)
        hits[kind] = hits.get(kind, 0) + 1
        return m.group(0).replace(v, tok.get(kind, v))
    return regex.sub(sub, text)


def _ssid_blocks(text: str, tok: Tokens, hits: dict) -> str:
    # system_profiler SPAirPortDataType lists networks as an indented "<name>:" line under
    # "Current Network Information:" and "Other Local Wi-Fi Networks:"
    out, mode, depth = [], False, 0
    for line in text.split("\n"):
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if stripped in ("Current Network Information:", "Other Local Wi-Fi Networks:", "Preferred Networks:"):
            mode, depth = True, indent
            out.append(line)
            continue
        if mode and stripped and indent <= depth:
            mode = False
        if (mode and stripped.endswith(":") and indent == depth + 2 and not stripped.startswith("SSID-")
                and not PLACEHOLDER.match(stripped[:-1]) and "redacted" not in stripped.lower()):
            name = stripped[:-1]
            hits["SSID"] = hits.get("SSID", 0) + 1
            line = line.replace(name, tok.get("SSID", name), 1)
        out.append(line)
    return "\n".join(out)


def redact(text: str, machine: str, mapping: dict):
    """Returns (redacted text, {kind: count})."""
    text = text.replace("\0", "")
    tok = Tokens(mapping, machine)
    hits = {}
    text = _keyed(text, tok, hits)
    text = _ssid_blocks(text, tok, hits)
    text = _pattern(text, UUID_RE, "UUID", tok, hits)
    text = _pattern(text, MAC_RE, "MAC", tok, hits)
    text = _pattern(text, IPV6_RE, "IP", tok, hits, 1)
    text = _pattern(text, IPV4_PORT_RE, "IP", tok, hits, 1)
    text = _pattern(text, IPV4_RE, "IP", tok, hits, 1)
    text = _pattern(text, EMAIL_RE, "EMAIL", tok, hits)
    text = HOME_RE.sub(lambda m: m.group(1) + "USER", text)
    # second guard: every value this machine ever had, anywhere in the text (also catches a serial printed
    # without its key, the way the OpenCore log redactor does)
    for kind, value, token in sorted(tok.known(), key=lambda t: -len(t[1])):
        if len(value) >= 4 and not PLACEHOLDER.match(value):
            text = re.sub(re.escape(value), token, text, flags=re.I)
    return text, hits


def leftovers(text: str, mapping: dict = None):
    """Anything that still looks like an identity or a secret. Empty list = safe to publish."""
    problems = []
    for n, line in enumerate(text.split("\n"), 1):
        for regex, what in SECRETS:
            if regex.search(line):
                problems.append(f"line {n}: {what}")
        for m in UUID_RE.finditer(line):
            if m.group(0).upper() not in ALLOW:
                problems.append(f"line {n}: UUID {m.group(0)[:8]}...")
        for m in MAC_RE.finditer(line):
            if m.group(0).upper().replace("-", ":") not in ALLOW:
                problems.append(f"line {n}: MAC address")
        # a serial key ("IOPlatformSerialNumber", "Serial Number (system)", "MLB") followed by a serial-shaped value;
        # "serial" must end the word, so ioreg's "not serializable" next to an address is not a hit
        if re.search(r"(?i)\b(?:\w*serial(?:[ _-]?(?:number|no))?(?: \(system\))?|MLB|BoardSerial)\b\"?\s*[:=]\s*\"?"
                     r"(?!(?:SERIAL|MLB)-\d)[A-Z0-9]{10,17}\b", line):
            problems.append(f"line {n}: serial-like value")
    if mapping:   # no known private value may survive anywhere
        low = text.lower()
        for machine in mapping.get("machines", {}).values():
            for table in machine.values():
                for value in table:
                    if len(value) >= 4 and not PLACEHOLDER.match(value) and value.lower() in low:
                        problems.append("a value from the private map is still present")
                        break
    return problems


def load_map(path):
    p = Path(path) if path else None
    if p and p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"version": 1, "machines": {}}


def save_map(path, mapping):
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(mapping, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--map", help="private value-to-token map (JSON); kept outside this repo")
    ap.add_argument("--machine", required=True, help="<username>/<machine>")
    ap.add_argument("src")
    ap.add_argument("dst", nargs="?")
    a = ap.parse_args()
    mapping = load_map(a.map)
    text, hits = redact(Path(a.src).read_bytes().decode("utf-8", "replace"), a.machine, mapping)
    left = leftovers(text, mapping)
    if left:
        sys.exit("refusing, still identifying:\n  " + "\n  ".join(left[:20]))
    save_map(a.map, mapping)
    if a.dst:
        Path(a.dst).parent.mkdir(parents=True, exist_ok=True)
        with open(a.dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    print("redacted: " + (", ".join(f"{k} {v}" for k, v in sorted(hits.items())) or "nothing found"), file=sys.stderr)


if __name__ == "__main__":
    main()
