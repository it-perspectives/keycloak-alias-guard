#!/usr/bin/env python3
"""Bump project version in pom.xml (major, minor, or patch)."""

from __future__ import annotations

import pathlib
import re
import sys

POM = pathlib.Path(__file__).resolve().parents[1] / "pom.xml"
PROJECT_VERSION_RE = re.compile(
    r"(<artifactId>keycloak-alias-guard</artifactId>\s*\n\s*<version>)([^<]+)(</version>)",
    re.MULTILINE,
)


def parse_version(raw: str) -> tuple[int, int, int, bool]:
    snapshot = raw.endswith("-SNAPSHOT")
    core = raw.removesuffix("-SNAPSHOT")
    major, minor, patch = (int(part) for part in core.split("."))
    return major, minor, patch, snapshot


def format_version(major: int, minor: int, patch: int, snapshot: bool) -> str:
    version = f"{major}.{minor}.{patch}"
    return f"{version}-SNAPSHOT" if snapshot else version


def bump(raw: str, part: str) -> str:
    major, minor, patch, snapshot = parse_version(raw)
    if part == "major":
        major += 1
        minor = 0
        patch = 0
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "patch":
        patch += 1
    else:
        raise ValueError(f"unsupported bump part: {part}")
    return format_version(major, minor, patch, snapshot)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"major", "minor", "patch"}:
        print("usage: bump-version.py {major|minor|patch}", file=sys.stderr)
        sys.exit(1)

    text = POM.read_text(encoding="utf-8")
    match = PROJECT_VERSION_RE.search(text)
    if not match:
        print("project version not found in pom.xml", file=sys.stderr)
        sys.exit(1)

    current = match.group(2)
    updated = bump(current, sys.argv[1])
    POM.write_text(
        PROJECT_VERSION_RE.sub(rf"\g<1>{updated}\g<3>", text, count=1),
        encoding="utf-8",
    )
    print(f"{current} -> {updated}")


if __name__ == "__main__":
    main()
