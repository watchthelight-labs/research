#!/usr/bin/env python3
# <wtl> project: research | file: tests/test_redact.py | author: watchthelight </wtl>
"""Checks for tools/redact.py with made-up identities. Run: python tests/test_redact.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from redact import leftovers, redact  # noqa: E402

IOREG = '''+-o J717AP  <class IOPlatformExpertDevice>
    "IOPlatformSerialNumber" = "C02ZK1ABCD12"
    "IOPlatformUUID" = "1A2B3C4D-5E6F-4A1B-8C9D-0E1F2A3B4C5D"
    "board-id" = <"Mac-27AD2F918AE68F61">
    "MtkBtFirmwareBuild" = "20260813113236"
    "MtkBtEndpoints" = "intr-in 81 bulk-in 82 bulk-out 02"
'''
PROFILER = '''Hardware Overview:
      Model Identifier: MacPro7,1
      Serial Number (system): C02ZK1ABCD12
      Hardware UUID: 1A2B3C4D-5E6F-4A1B-8C9D-0E1F2A3B4C5D
      Provisioning UDID: 1A2B3C4D-5E6F-4A1B-8C9D-0E1F2A3B4C5D
Wi-Fi:
      Interfaces:
        en1:
          MAC Address: a4:5e:60:12:34:56
          Current Network Information:
            Home Fibre 5G:
              PHY Mode: 802.11ac
              BSSID: 3c:84:6a:aa:bb:cc
          Other Local Wi-Fi Networks:
            NETGEAR-Guest:
              Channel: 11
Bluetooth Controller:
          Address: 10:2B:41:DE:AD:01
          State: On
'''
OCLOG = '''00:812 00:004 OC: Setting HW_SSN C02ZK1ABCD12
00:812 00:004 OC: Setting MLB C02912345ABCDEFG1
00:812 00:004 OC: Setting ROM 112233445566
00:900 00:001 OCVAR: Setting NVRAM 7C436110-AB2A-4BBB-A880-FE41995C9F82:boot-args - ok
00:950 00:001 OCB: Path /Users/ikurina/Desktop/EFI and C:\\Users\\bash\\Desktop
inet 192.168.1.23 netmask 255.255.255.0; inet6 fe80::1c2d:3e4f:5a6b:7c8d%en1; kernel 25.0.0 OC 1.0.8
mail me at someone.real@example.org
'''


def main():
    mapping = {"version": 1, "machines": {}}
    a, ha = redact(IOREG + PROFILER, "ikurina/asus-tuf-gaming-b850-plus-wifi", mapping)
    b, hb = redact(OCLOG, "ikurina/asus-tuf-gaming-b850-plus-wifi", mapping)
    text = a + b
    bad = ["C02ZK1ABCD12", "1A2B3C4D-5E6F", "a4:5e:60", "3c:84:6a", "10:2B:41", "Home Fibre 5G", "NETGEAR-Guest",
           "C02912345ABCDEFG1", "112233445566", "192.168.1.23", "fe80::1c2d", "ikurina", "bash", "someone.real"]
    fails = [s for s in bad if s.lower() in text.lower()]
    keep = ["Mac-27AD2F918AE68F61", "MacPro7,1", "20260813113236", "intr-in 81 bulk-in 82 bulk-out 02",
            "7C436110-AB2A-4BBB-A880-FE41995C9F82", "255.255.255.0", "25.0.0", "1.0.8", "802.11ac", "Channel: 11"]
    lost = [s for s in keep if s not in text]
    # the same serial must get the same token in both texts
    same = a.count("SERIAL-1") >= 2 and "SERIAL-1" in b
    left = leftovers(text, mapping)
    planted = leftovers("token ghp_" + "A" * 30)
    serial_key = leftovers('"IOPlatformSerialNumber" = "C02ZK1ABCD12"')
    serializable = leftovers('"IODeviceMemory" = (({"address"=4093640704}),"not serializable",({"address"=4093640704')
    ok = not fails and not lost and same and not left and planted and serial_key and not serializable
    print("unredacted serial key caught:", bool(serial_key), "| 'not serializable' left alone:", not serializable)
    print(text)
    print("hits:", ha, hb)
    print("still present:", fails)
    print("wrongly removed:", lost)
    print("stable token across files:", same)
    print("leftovers after redaction:", left)
    print("planted secret caught:", bool(planted))
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
