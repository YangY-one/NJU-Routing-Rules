#!/usr/bin/env python3
"""Render all published rule formats from the files in sources/."""

import argparse
import ipaddress
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY = "NJU-VPN"  # Replace this policy/outbound tag in client configuration.


def source_lines(name):
    return [line.strip() for line in (ROOT / "sources" / name).read_text().splitlines()
            if line.strip() and not line.lstrip().startswith("#")]


def load_sources():
    domains = source_lines("domains.txt")
    cidrs = source_lines("ip-cidrs.txt")
    if len(domains) != len(set(domains)) or len(cidrs) != len(set(cidrs)):
        raise ValueError("duplicate source entry")
    for domain in domains:
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.nju\.edu\.cn", domain):
            raise ValueError(f"invalid domain: {domain}")
    for cidr in cidrs:
        network = ipaddress.ip_network(cidr, strict=True)
        if network.version != 4 or str(network) != cidr:
            raise ValueError(f"noncanonical CIDR: {cidr}")
    return domains, cidrs


def as_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def outputs(domains, cidrs):
    standard = [f"DOMAIN,{domain}" for domain in domains]
    standard += [f"IP-CIDR,{cidr},no-resolve" for cidr in cidrs]
    standard_text = "\n".join(standard) + "\n"
    quantumultx = [f"HOST,{domain},{POLICY}" for domain in domains]
    quantumultx += [f"IP-CIDR,{cidr},{POLICY},no-resolve" for cidr in cidrs]
    mihomo = ["payload:"] + [f"  - '{rule}'" for rule in standard]
    v2ray = {"routing": {"domainStrategy": "AsIs", "rules": [
        {"type": "field", "domain": [f"full:{domain}" for domain in domains],
         "outboundTag": POLICY},
        {"type": "field", "ip": cidrs, "outboundTag": POLICY},
    ]}}
    sing_box = {"version": 1, "rules": [{"domain": domains}, {"ip_cidr": cidrs}]}
    return {
        "rules/surge/nju.list": standard_text,
        "rules/loon/nju.list": standard_text,
        "rules/shadowrocket/nju.list": standard_text,
        "rules/quantumultx/nju.list": "\n".join(quantumultx) + "\n",
        "rules/mihomo/nju.yaml": "\n".join(mihomo) + "\n",
        "rules/v2ray/nju-routing.json": as_json(v2ray),
        "rules/sing-box/nju.json": as_json(sing_box),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify published rules match sources")
    args = parser.parse_args()
    domains, cidrs = load_sources()
    changed = []
    for name, content in outputs(domains, cidrs).items():
        path = ROOT / name
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            changed.append(name)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    if args.check and changed:
        parser.exit(1, "out of date: " + ", ".join(changed) + "\n")
    print(f"{'Checked' if args.check else 'Built'} 7 formats from "
          f"{len(domains)} domains and {len(cidrs)} CIDRs")


if __name__ == "__main__":
    main()
