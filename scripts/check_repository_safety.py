"""Fail when tracked repository files contain high-confidence secret material."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAX_TEXT_SIZE = 1_000_000
FORBIDDEN_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
FORBIDDEN_NAMES = {".env", "application_default_credentials.json"}
ALLOWED_NAMES = {".env.example"}
MARKERS = (
    "-----BEGIN " + "PRIVATE KEY-----",
    "-----BEGIN RSA " + "PRIVATE KEY-----",
    "-----BEGIN EC " + "PRIVATE KEY-----",
    "-----BEGIN OPENSSH " + "PRIVATE KEY-----",
)
TOKEN_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [
        ROOT / item.decode("utf-8")
        for item in result.stdout.split(b"\0")
        if item
    ]


def main() -> int:
    violations: list[str] = []
    checked = 0

    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        lower_name = path.name.lower()

        if lower_name not in ALLOWED_NAMES and (
            lower_name in FORBIDDEN_NAMES
            or path.suffix.lower() in FORBIDDEN_SUFFIXES
            or "service-account" in lower_name
        ):
            violations.append(f"forbidden tracked filename: {relative}")
            continue

        if not path.is_file() or path.stat().st_size > MAX_TEXT_SIZE:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        checked += 1
        if any(marker in text for marker in MARKERS):
            violations.append(f"private-key marker found: {relative}")
        if any(pattern.search(text) for pattern in TOKEN_PATTERNS):
            violations.append(f"credential-like token found: {relative}")

    if violations:
        print("Repository safety scan failed:")
        for violation in violations:
            print(f"- {violation}")
        return 1

    print(
        "Repository safety scan passed: "
        f"{checked} tracked text files checked; no forbidden credential files "
        "or high-confidence secret markers found."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
