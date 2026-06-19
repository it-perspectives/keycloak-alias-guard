#!/usr/bin/env python3
"""Cut a release: tag current SNAPSHOT line, push, bump to next SNAPSHOT."""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from version_utils import compute_release_versions, read_version, write_version


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=check, text=True)


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def tag_exists_local(tag: str) -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "-q", "--verify", f"refs/tags/{tag}"],
            capture_output=True,
            text=True,
        ).returncode
        == 0
    )


def tag_exists_remote(tag: str) -> bool:
    result = subprocess.run(
        ["git", "ls-remote", "--tags", "origin", f"refs/tags/{tag}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"preflight failed: cannot check remote tags ({result.stderr.strip()})")
    return bool(result.stdout.strip())


def run_preflight(*, current: str, tag: str, require_git_ready: bool) -> None:
    failures: list[str] = []

    if not current.endswith("-SNAPSHOT"):
        failures.append(f"pom.xml must use -SNAPSHOT (got {current})")

    if tag_exists_local(tag):
        failures.append(f"tag {tag} already exists locally")

    if tag_exists_remote(tag):
        failures.append(f"tag {tag} already exists on origin")

    if require_git_ready:
        branch = git_output("rev-parse", "--abbrev-ref", "HEAD")
        if branch != "main":
            failures.append(f"must run on main branch (current: {branch})")

        if git_output("status", "--porcelain"):
            failures.append("working tree is not clean; commit or stash changes first")

    if failures:
        for message in failures:
            print(f"preflight failed: {message}", file=sys.stderr)
        raise SystemExit(1)

    print("preflight OK")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a release from pom.xml SNAPSHOT version")
    parser.add_argument("part", choices=["patch", "minor", "major"])
    parser.add_argument("--dry-run", action="store_true", help="print planned steps only")
    parser.add_argument("--no-push", action="store_true", help="commit and tag locally without pushing")
    args = parser.parse_args()

    current = read_version()
    try:
        release_version, next_version = compute_release_versions(current, args.part)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    tag = f"v{release_version}"
    print(f"current:  {current}")
    print(f"release:  {release_version} ({tag})")
    print(f"next dev: {next_version}")

    run_preflight(current=current, tag=tag, require_git_ready=not args.dry_run)

    if args.dry_run:
        print("dry-run: no files or git state changed")
        return

    write_version(release_version)
    run(["git", "add", "pom.xml"])
    run(["git", "commit", "-m", f"release: {tag}"])
    run(["git", "tag", "-a", tag, "-m", tag])

    write_version(next_version)
    run(["git", "add", "pom.xml"])
    run(["git", "commit", "-m", f"chore: prepare {next_version}"])

    if not args.no_push:
        run(["git", "push", "origin", "main"])
        run(["git", "push", "origin", tag])

    print(f"done: released {tag}, next development version is {next_version}")


if __name__ == "__main__":
    main()
