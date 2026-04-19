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
    r"^(class\s|def\s|@|[A-Z_][A-Z_0-9]*\s*=|# ====|if __name__)"
)


def _is_method_def(line: str) -> bool:
    """`def foo(self, ...)` or `def foo(cls, ...)` — a class method
    that lost its indent on paste. Distinguishes methods from
    top-level functions which would not take self/cls."""
    m = re.match(r"^def\s+\w+\s*\(\s*(self|cls)\b", line)
    return bool(m)


def _reindent_one_pass(lines: List[str]) -> Tuple[List[str], int]:
    """Indent bodies of top-level class/def/if-main blocks that were
    pasted flush-left. One pass: catches outermost blocks only. Run
    iteratively until no changes are made.

    Inside a `class X:` body, `def foo(self, ...):` lines at indent 0
    are treated as methods needing indent, NOT as top-level functions
    ending the class."""
    out: List[str] = []
    fixes = 0
    i = 0
    n = len(lines)
    while i < n:
        L = lines[i]
        out.append(L)
        if _BLOCK_OPENER.match(L):
            in_class = L.startswith("class ")
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
                    # EXCEPTION: if we're inside a class and this is
                    # `def foo(self, ...)`, treat it as a method body
                    # rather than end-of-class.
                    if in_class and _is_method_def(nxt):
                        out.append("    " + nxt)
                        fixes += 1
                        j += 1
                        continue
                    # EXCEPTION: when inside a class, CONST = ... patterns
                    # are usually Enum members or class-level constants,
                    # NOT end-of-class. Only break on `class `, `@`,
                    # `# ====`, or `if __name__`.
                    if in_class and re.match(
                        r"^[A-Z_][A-Z_0-9]*\s*=", nxt,
                    ):
                        out.append("    " + nxt)
                        fixes += 1
                        j += 1
                        continue
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


def _leading_spaces(line: str) -> int:
    i = 0
    while i < len(line) and line[i] == " ":
        i += 1
    return i


def _strip_inline_comment(line: str) -> str:
    """Return `line` with any trailing `# ...` comment removed.
    Respects `#` inside simple single/double quoted strings. Not a
    full Python tokenizer — handles the common cases."""
    in_single = False
    in_double = False
    i = 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            i += 2
            continue
        if not in_single and c == '"':
            in_double = not in_double
        elif not in_double and c == "'":
            in_single = not in_single
        elif c == "#" and not in_single and not in_double:
            return line[:i]
        i += 1
    return line


def _reindent_control_flow_one_pass(lines: List[str]) -> Tuple[List[str], int]:
    """Fix control-flow bodies that were flattened to the same indent
    as their opening `:` line.

    Pattern caught:
        for X in Y:
        body              <-- should be at deeper indent

    Iterative: each pass catches one level of nesting. Lines already
    at deeper indent than the colon-opener are left alone (the body
    is presumably correct below the first paste-damaged line).
    """
    fixes = 0
    out: List[str] = []
    i = 0
    n = len(lines)
    while i < n:
        L = lines[i]
        out.append(L)
        # Does this line open a block (ends with `:` after stripping
        # inline comments, starts with a real block-opening keyword,
        # and is not itself a comment)?
        stripped = L.rstrip()
        # strip an inline comment (but not if `#` is inside a string)
        code_part = _strip_inline_comment(stripped).rstrip()
        is_block_opener = (
            code_part.endswith(":")
            and not stripped.lstrip().startswith("#")
            and bool(re.match(
                r"^\s*(if|elif|else|for|while|try|except|finally|"
                r"with|def|class|match|case)\b",
                stripped,
            ))
        )
        if is_block_opener:
            opener_indent = _leading_spaces(L)
            # Restrict to openers INSIDE a function/class (indent >= 4).
            # At indent 0, a `:` line is either a class/def/if-main
            # (handled by _reindent_one_pass) or a rare top-level
            # control-flow we should not touch. Treating indent-0
            # openers here mistakenly consumes sibling top-level
            # statements as if they were body lines.
            if opener_indent < 4:
                i += 1
                continue
            # find the next non-blank, non-comment line
            j = i + 1
            while j < n:
                nxt = lines[j]
                if not nxt.strip():
                    out.append(nxt)
                    j += 1
                    continue
                if nxt.lstrip().startswith("#"):
                    out.append(nxt)
                    j += 1
                    continue
                nxt_indent = _leading_spaces(nxt)
                # if the next body line is at <= opener indent, we have
                # a flattened body. Re-indent all following lines at
                # that exact indent to opener_indent + 4, until we see
                # a line at a LESSER indent (exit of block) or another
                # marker.
                if nxt_indent <= opener_indent:
                    # re-indent nxt and following lines at this same indent
                    while j < n:
                        curr = lines[j]
                        if not curr.strip():
                            out.append(curr)
                            j += 1
                            continue
                        ci = _leading_spaces(curr)
                        if ci < opener_indent:
                            # de-indented past the opener; block ended
                            break
                        # continuation keywords (else/elif/except/finally)
                        # at the same indent as the opener are SIBLINGS
                        # of the opener, not body. Stop re-indenting.
                        if ci == opener_indent and re.match(
                            r"^\s*(else|elif|except|finally)\b",
                            curr,
                        ):
                            break
                        if ci == nxt_indent and ci <= opener_indent:
                            out.append("    " + curr)
                            fixes += 1
                            j += 1
                            continue
                        # deeper than nxt_indent: leave alone
                        out.append(curr)
                        j += 1
                    break
                else:
                    # body is correctly deeper; nothing to fix here
                    break
            i = j
            continue
        i += 1
    return out, fixes


def fix_indentation(text: str) -> Tuple[str, int]:
    """Iteratively fix paste-flattened class/function/control bodies.

    Two kinds of damage:
      1. Top-level class/def bodies pasted at indent 0 (fixed by
         _reindent_one_pass).
      2. Control-flow bodies (if/for/while/etc) pasted at the same
         indent as the opener (fixed by _reindent_control_flow_one_pass).

    Iterative because each pass only catches one level of nesting.
    Stops when no pass makes a change, or after MAX_PASSES.
    """
    MAX_PASSES = 12
    lines = text.splitlines()
    total = 0
    for _ in range(MAX_PASSES):
        new_lines, fixes1 = _reindent_one_pass(lines)
        new_lines, fixes2 = _reindent_control_flow_one_pass(new_lines)
        if fixes1 + fixes2 == 0:
            break
        total += fixes1 + fixes2
        lines = new_lines
    return "\n".join(lines), total


_BOOTSTRAP_SNIPPET = (
    "import sys\n"
    "import os\n"
    "sys.path.insert(\n"
    "    0,\n"
    "    os.path.dirname(os.path.dirname(os.path.dirname("
    "os.path.abspath(__file__)))),\n"
    ")\n\n"
)


def add_sys_path_bootstrap(
    text: str, target_depth: int = 3,
) -> Tuple[str, int]:
    """Insert a sys.path bootstrap after the module docstring so the
    file runs standalone (`python path/to/file.py`) even when it lives
    in a package nested `target_depth` levels below the repo root.

    Skipped (returns 0 fixes) if `sys.path.insert` already appears in
    the file, or if there is no `from <pkg>.` / `import <pkg>` line
    (no bootstrap needed).
    """
    if "sys.path.insert" in text:
        return text, 0
    if not re.search(r"^(from \w|import \w)", text, re.MULTILINE):
        return text, 0

    # find a good insertion point: after the leading docstring, before
    # the first `from` / `import` line
    m = re.search(r"^(from \w|import \w)", text, re.MULTILINE)
    if not m:
        return text, 0
    idx = m.start()
    text = text[:idx] + _BOOTSTRAP_SNIPPET + text[idx:]
    return text, 1


def fix_all(text: str) -> Tuple[str, dict]:
    report = {}
    text, report["smart_quotes"] = fix_smart_quotes(text)
    text, report["markdown"] = fix_markdown(text)
    text, report["indent"] = fix_indentation(text)
    text, report["bootstrap"] = add_sys_path_bootstrap(text)
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
    print(f"  sys.path bootstrap: "
          f"{'added' if report['bootstrap'] else 'skipped'}")

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
