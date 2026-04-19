#!/usr/bin/env python3
"""
scripts/fix_pasted_file.py

Fix the four classes of damage GitHub's web paste introduces into
Python source files pasted from a chat UI:

  1. smart quotes ("" '' en/em dash, ellipsis, nbsp) -> ASCII
  2. markdown code fences (```) stripped
  3. markdown bold (**name**, **main**) -> __name__, __main__
  4. class and function bodies pasted flush-left re-indented to 4/8

Heuristic, not a parser. Always review the diff before trusting the
output. Run `python -m py_compile <output>` after fixing.

Usage:
  python scripts/fix_pasted_file.py INPUT OUTPUT
  python scripts/fix_pasted_file.py --in-place FILE

Prints a report of what changed. Exits 0 if the file parses as Python
after fixing; exits 1 with the error if it does not.

CC0. Stdlib only.
"""

import argparse
import ast
import pathlib
import re
import sys
from typing import List, Tuple


SMART_QUOTES = {
    "\u201c": '"', "\u201d": '"',
    "\u2018": "'", "\u2019": "'",
    "\u201e": '"', "\u201a": "'",
    "\u2013": "-", "\u2014": "-",
    "\u2026": "...",
    "\u00a0": " ",
}

MARKDOWN_BOLD = [
    ("**name**", "__name__"),
    ("**main**", "__main__"),
]


def fix_smart_quotes(text: str) -> Tuple[str, int]:
    count = 0
    for bad, good in SMART_QUOTES.items():
        n = text.count(bad)
        if n:
            text = text.replace(bad, good)
            count += n
    return text, count


def fix_markdown(text: str) -> Tuple[str, int]:
    """Remove code fences; fix **name** / **main** bolding."""
    count = 0
    out: List[str] = []
    for L in text.splitlines():
        if L.strip() == "```":
            count += 1
            continue
        for bad, good in MARKDOWN_BOLD:
            if bad in L:
                L = L.replace(bad, good)
                count += 1
        out.append(L)
    return "\n".join(out), count


_BLOCK_OPENER = re.compile(r"^(class\s|def\s|if __name__)")
_BLOCK_END_MARKER = re.compile(
    r"^(class\s|def\s|@|[A-Z_][A-Z_0-9]*\s*=|# ====)"
)


def _reindent_one_pass(lines: List[str]) -> Tuple[List[str], int]:
    """Indent bodies of top-level class/def/if-main blocks that were
    pasted flush-left. One pass: catches outermost blocks only. Run
    iteratively until no changes are made."""
    out: List[str] = []
    fixes = 0
    i = 0
    n = len(lines)
    while i < n:
        L = lines[i]
        out.append(L)
        if _BLOCK_OPENER.match(L):
            # collect body lines until a block-end marker at indent 0
            j = i + 1
            while j < n:
                nxt = lines[j]
                if not nxt.strip():
                    out.append(nxt)
                    j += 1
                    continue
                # only consider indent-0 lines as potentially ending the block
                if nxt[0] not in " \t" and _BLOCK_END_MARKER.match(nxt):
                    break
                # only re-indent lines that are already at indent 0
                # (paste damage). Lines that are already indented stay.
                if nxt and nxt[0] not in " \t":
                    out.append("    " + nxt)
                    fixes += 1
                else:
                    out.append(nxt)
                j += 1
            i = j
            continue
        i += 1
    return out, fixes


def fix_indentation(text: str) -> Tuple[str, int]:
    """Iteratively fix paste-flattened class/function bodies.

    Runs the single-pass fixer multiple times because nested methods
    inside a re-indented class still appear flush-left after the first
    pass (their indent went from 0 to 4, but they are now at the outer
    class's body level, not the method level). A second pass catches
    them.

    Stops when a pass makes no changes or after MAX_PASSES.
    """
    MAX_PASSES = 8
    lines = text.splitlines()
    total = 0
    for _ in range(MAX_PASSES):
        new_lines, fixes = _reindent_one_pass(lines)
        if fixes == 0:
            break
        total += fixes
        lines = new_lines
    return "\n".join(lines), total


def fix_all(text: str) -> Tuple[str, dict]:
    report = {}
    text, report["smart_quotes"] = fix_smart_quotes(text)
    text, report["markdown"] = fix_markdown(text)
    text, report["indent"] = fix_indentation(text)
    return text, report


def verify_parses(text: str) -> Tuple[bool, str]:
    try:
        ast.parse(text)
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Fix chat-paste damage in Python source files."
    )
    ap.add_argument("input", help="Input file path")
    ap.add_argument(
        "output", nargs="?",
        help="Output file path (omit with --in-place)"
    )
    ap.add_argument(
        "--in-place", action="store_true",
        help="Overwrite the input file",
    )
    ap.add_argument(
        "--no-verify", action="store_true",
        help="Skip the ast.parse verification step",
    )
    args = ap.parse_args()

    inp = pathlib.Path(args.input)
    if args.in_place:
        if args.output:
            ap.error("cannot combine --in-place with an output path")
        out = inp
    else:
        if not args.output:
            ap.error("must supply output path or use --in-place")
        out = pathlib.Path(args.output)

    text = inp.read_text()
    fixed, report = fix_all(text)

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(fixed if fixed.endswith("\n") else fixed + "\n")

    print(f"wrote {out}")
    print(f"  smart quotes fixed: {report['smart_quotes']}")
    print(f"  markdown artifacts: {report['markdown']}")
    print(f"  indentation fixes:  {report['indent']}")

    if args.no_verify:
        return 0
    ok, err = verify_parses(fixed)
    if ok:
        print("  ast.parse: OK")
        return 0
    print(f"  ast.parse: FAILED")
    print(f"    {err}")
    print(
        "  (the heuristic did not fully reconstruct valid Python; "
        "review the diff and finish by hand)"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
