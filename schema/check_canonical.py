#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check_canonical.py - verify the vendored schema mirrors match the canonical source.

The canonical WML schema lives in a separate repo, **WMOOP/wmoop.json**. The copies in
this repo (`schema/wml.schema.json`, `schema/wml.xsd`) are line-for-line **mirrors** kept
here so the validator and CI run offline. This script fetches the canonical files and fails
(exit 1) if a mirror has drifted - the signal to re-sync (edit the schema in `wmoop.json`,
then copy it back here). Line endings are normalised before comparison, so CRLF/LF checkout
differences never count as drift.

A network failure fetching the canonical copy is a soft pass (warn, exit 0): the grammar gate
in validate_wml.py still runs against the local mirror, so offline/transient issues do not
break CI; only a confirmed content difference fails.

Usage:
    python schema/check_canonical.py            # compare mirrors against WMOOP/wmoop.json@main
    python schema/check_canonical.py --ref v1   # compare against a specific ref/branch/tag
"""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW_BASE = "https://raw.githubusercontent.com/WMOOP/wmoop.json"
MIRRORS = ["wml.schema.json", "wml.xsd"]


def norm(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Check schema mirrors against WMOOP/wmoop.json.")
    ap.add_argument("--ref", default="main", help="ref/branch/tag in wmoop.json (default: main)")
    args = ap.parse_args(argv)

    stale: list[str] = []
    for name in MIRRORS:
        local = HERE / name
        if not local.exists():
            stale.append(f"{name}: missing locally (expected a mirror of wmoop.json)")
            continue
        url = f"{RAW_BASE}/{args.ref}/{name}"
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                remote = resp.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"warning: could not fetch canonical {name} ({exc}); "
                  f"skipping the freshness check for it.")
            continue
        if norm(local.read_bytes()) != norm(remote):
            stale.append(f"{name}: DIFFERS from canonical {url}")

    if stale:
        print("Schema mirrors are STALE versus the canonical WMOOP/wmoop.json:")
        for s in stale:
            print(f"  - {s}")
        print("\nRe-sync: copy the file(s) from https://github.com/WMOOP/wmoop.json back into schema/.")
        return 1

    print(f"OK - schema mirrors match canonical WMOOP/wmoop.json@{args.ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
