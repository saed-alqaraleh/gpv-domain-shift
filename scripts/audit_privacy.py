"""Pre-release privacy gate for the tracked repository and reachable Git history.

Checks for email-like strings in release files and requires GitHub's opaque
noreply identity for every author/committer in reachable commit history.
No discovered address or matched value is printed.
"""

from __future__ import annotations

import gzip
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EMAIL_RE = re.compile(
    rb"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.-])"
)
# Only first-party GitHub user noreply addresses are permitted in commit headers.
NOREPLY_DOMAIN = "@users.noreply.github.com"


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [ROOT / Path(x.decode("utf-8")) for x in result.stdout.split(b"\0") if x]


def read_for_scan(path: Path) -> bytes:
    if path.suffix == ".gz":
        with gzip.open(path, "rb") as handle:
            return handle.read()
    if path.suffix in {".npz", ".zip"}:
        with zipfile.ZipFile(path) as archive:
            return b"\n".join(archive.read(x) for x in archive.namelist())
    return path.read_bytes()


def main() -> int:
    problems: list[str] = []
    file_count = 0
    for path in tracked_files():
        file_count += 1
        if EMAIL_RE.search(read_for_scan(path)):
            problems.append(f"Email-like string in {path.relative_to(ROOT).as_posix()}")

    history = subprocess.run(
        ["git", "log", "--all", "--format=%ae%n%ce"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    identities = [x.strip() for x in history.stdout.splitlines() if x.strip()]
    if not identities:
        problems.append("No Git commit identities found")
    if any(not x.lower().endswith(NOREPLY_DOMAIN) for x in identities):
        problems.append("Non-noreply author/committer identity found in Git history")

    if problems:
        for reason in problems:
            print(f"PRIVACY CHECK FAILED: {reason}")
        return 1
    print(f"PASS: {file_count} tracked files and {len(identities)} Git author/committer identity fields; no exposed personal emails")
    return 0


if __name__ == "__main__":
    sys.exit(main())
