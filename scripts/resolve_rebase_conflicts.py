#!/usr/bin/env python3
"""Resolve a rebase of this session's branch onto a moving main.

The only conflict this branch ever produces is append-only: `COORDINATION.md` gains another session's
section, and the generated artifacts (`site/data.json`, `site/sheets.html`, `site/coverage.json`) change
because another session added data. Both are mechanical:

  * COORDINATION.md — keep every other session's text in full, then this session's text. Nothing is dropped.
  * generated artifacts — clear the conflicted copy, then regenerate from the merged data modules so
    neither session's rows are lost (the artifacts are byte-reproducible from scripts/data_*.py).

Run from the repository root after `git pull --rebase origin main` stops on a conflict.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def sh(*args, check=True):
    return subprocess.run(args, cwd=ROOT, check=check, text=True, capture_output=True)


def conflicted():
    out = sh("git", "diff", "--name-only", "--diff-filter=U", check=False).stdout.split()
    return out


def resolve_board():
    path = ROOT / "COORDINATION.md"
    s = path.read_text(encoding="utf-8")
    while "<<<<<<< " in s:
        start = s.index("<<<<<<< ")
        mid = s.index("=======\n", start)
        end = s.index(">>>>>>> ", mid)
        theirs = s[start:s.index("\n", start) + 1:]
        theirs = s[s.index("\n", start) + 1:mid]
        mine = s[mid + len("=======\n"):end]
        end_line = s.index("\n", end) + 1
        s = s[:start] + theirs.rstrip("\n") + "\n\n---\n\n" + mine + s[end_line:]
    path.write_text(s, encoding="utf-8")


def main():
    files = conflicted()
    if not files:
        print("nothing conflicted")
        return 0
    print("conflicted:", files)
    for f in files:
        if f == "COORDINATION.md":
            resolve_board()
            sh("git", "add", f)
        elif f in {"site/data.json", "site/sheets.html", "site/coverage.json"}:
            # Regenerated below from the merged data modules, so the conflicted copy is irrelevant;
            # staging the upstream side first simply clears the unmerged index entry.
            sh("git", "checkout", "--ours", f, check=False)
            sh("git", "add", f, check=False)
    if sh("git", "diff", "--name-only", "--diff-filter=U", check=False).stdout.strip():
        print("still conflicted:", sh("git", "diff", "--name-only", "--diff-filter=U").stdout)
        return 1
    for script in ("data_source.py", "build_addendum.py", "coverage.py"):
        r = sh("python3", f"scripts/{script}", check=False)
        if r.returncode:
            print(f"FAILED scripts/{script}\n{r.stderr[-2000:]}")
            return 1
    sh("git", "add", "site/data.json", "site/sheets.html", "site/coverage.json")
    print("resolved; artifacts regenerated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
