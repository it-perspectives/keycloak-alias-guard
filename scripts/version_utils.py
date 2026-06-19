from __future__ import annotations

import pathlib
import re

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


def read_version() -> str:
    text = POM.read_text(encoding="utf-8")
    match = PROJECT_VERSION_RE.search(text)
    if not match:
        raise RuntimeError("project version not found in pom.xml")
    return match.group(2)


def write_version(version: str) -> None:
    text = POM.read_text(encoding="utf-8")
    if not PROJECT_VERSION_RE.search(text):
        raise RuntimeError("project version not found in pom.xml")
    POM.write_text(
        PROJECT_VERSION_RE.sub(rf"\g<1>{version}\g<3>", text, count=1),
        encoding="utf-8",
    )


def compute_release_versions(current: str, part: str) -> tuple[str, str]:
    _, _, _, snapshot = parse_version(current)
    if not snapshot:
        raise ValueError(f"release requires -SNAPSHOT version, got {current}")

    core = current.removesuffix("-SNAPSHOT")
    if part == "patch":
        release_version = core
    elif part in {"minor", "major"}:
        release_version = bump(core, part)
    else:
        raise ValueError(f"unsupported release part: {part}")

    next_version = f"{bump(release_version, 'patch')}-SNAPSHOT"
    return release_version, next_version
