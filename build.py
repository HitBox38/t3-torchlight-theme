#!/usr/bin/env python3
"""Build the installable Torchlight theme using only Python's standard library."""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSS_LIMIT = 20_000


def compact_css(css: str) -> str:
    # Preserve quoted strings while removing comments and source formatting.
    strings = []

    def preserve(match):
        value = match.group(0)
        if value.startswith("/*"):
            return " "
        strings.append(value)
        return f"\x00{len(strings) - 1}\x00"

    css = re.sub(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|/\*.*?\*/''', preserve, css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};])\s*", r"\1", css).strip()
    return re.sub(r"\x00(\d+)\x00", lambda m: strings[int(m.group(1))], css)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check that torchlight.json matches its sources without writing it.")
    args = parser.parse_args()

    theme = json.loads((ROOT / "palette.json").read_text(encoding="utf-8"))
    theme["css"] = compact_css((ROOT / "theme.css").read_text(encoding="utf-8"))
    if len(theme["css"]) > CSS_LIMIT:
        parser.exit(1, f"CSS is {len(theme['css'])} characters; T3 accepts at most {CSS_LIMIT}.\n")

    output = ROOT / "torchlight.json"
    content = json.dumps(theme, indent=2).encode("utf-8")
    if args.check:
        if not output.is_file() or output.read_bytes() != content:
            parser.exit(1, "torchlight.json is out of date. Run python3 build.py.\n")
        print(f"torchlight.json is current ({len(theme['css'])} CSS characters).")
    else:
        output.write_bytes(content)
        print(f"Built torchlight.json ({len(theme['css'])} CSS characters).")


if __name__ == "__main__":
    main()
