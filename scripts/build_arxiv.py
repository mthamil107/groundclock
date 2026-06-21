"""Build the flat arXiv submission tarball from docs/paper/arxiv-submission/.

Includes only the .tex and .bib at the archive root (arXiv compiles LaTeX; the README is
instructions only). Validates total size < 50 MB.

Usage: python scripts/build_arxiv.py
"""

from __future__ import annotations

import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SUB = ROOT / "docs" / "paper" / "arxiv-submission"
OUT = ROOT / "docs" / "paper" / "arxiv-submission.tar.gz"
INCLUDE = ["groundclock-paper.tex", "groundclock.bib"]
MAX_BYTES = 50 * 1024 * 1024


def main() -> int:
    missing = [f for f in INCLUDE if not (SUB / f).exists()]
    if missing:
        print(f"ERROR missing files: {missing}", file=sys.stderr)
        return 1
    with tarfile.open(OUT, "w:gz") as tar:
        for name in INCLUDE:
            tar.add(SUB / name, arcname=name)  # arcname => flat (root) layout
    size = OUT.stat().st_size
    if size > MAX_BYTES:
        print(f"ERROR tarball {size} bytes exceeds 50 MB", file=sys.stderr)
        return 1
    print(f"OK   wrote {OUT.relative_to(ROOT)} ({size} bytes) with {INCLUDE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
