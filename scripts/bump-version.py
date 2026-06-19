#!/usr/bin/env python3
"""Bump project version in pom.xml (major, minor, or patch)."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from version_utils import bump, read_version, write_version


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"major", "minor", "patch"}:
        print("usage: bump-version.py {major|minor|patch}", file=sys.stderr)
        sys.exit(1)

    current = read_version()
    updated = bump(current, sys.argv[1])
    write_version(updated)
    print(f"{current} -> {updated}")


if __name__ == "__main__":
    main()
