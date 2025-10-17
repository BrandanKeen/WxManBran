#!/usr/bin/env python3
import argparse
import html
import json
import os
from pathlib import Path
from typing import List

MARKER_START = "<!-- DATA-SECTION:START -->"
MARKER_END = "<!-- DATA-SECTION:END -->"


def load_spec(path: Path) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def render_iframe_block(spec: List[dict], public_dir: Path) -> str:
    items = []
    for entry in spec:
        outfile = entry.get("outfile")
        if not outfile:
            continue
        title = entry.get("title") or Path(outfile).stem.replace("_", " ")
        title = html.escape(title)
        html_name = Path(outfile).with_suffix(".html").name
        rel_path = (public_dir / html_name).as_posix().lstrip("/")
        rel_url = f"/{rel_path}"
        iframe = (
            "  <div class=\"storm-plot\">\n"
            f"    <h3>{title}</h3>\n"
            f"    <iframe src=\"{{{{ '{rel_url}' | relative_url }}}}\" width=\"100%\" height=\"520\" loading=\"lazy\" style=\"border:0\"></iframe>\n"
            "  </div>"
        )
        items.append(iframe)
    content = "\n".join(items)
    return (
        "<h2>Data</h2>\n"
        "<div class=\"storm-data\">\n"
        f"{content}\n"
        "</div>"
    )


def update_markdown(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")

    # Strip placeholder markers so the rendered block replaces any temporary
    # "DataComingSoon" text that may have been left in a freshly created
    # container page.
    placeholder = "DataComingSoon"
    if placeholder in text:
        text = text.replace(f"\n{placeholder}\n", "\n")
        text = text.replace(placeholder, "")

    if MARKER_START in text and MARKER_END in text:
        start_idx = text.index(MARKER_START) + len(MARKER_START)
        end_idx = text.index(MARKER_END)
        new_text = text[:start_idx] + "\n" + block + "\n" + text[end_idx:]
    else:
        if not text.endswith("\n"):
            text += "\n"
        new_text = text + "\n" + MARKER_START + "\n" + block + "\n" + MARKER_END + "\n"
    path.write_text(new_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed Plotly plots into storm markdown page")
    parser.add_argument("--spec", required=True, help="Path to the plot spec JSON")
    parser.add_argument("--storm-md", required=True, help="Path to the storm markdown file")
    parser.add_argument("--public-dir", required=True, help="Directory where plot HTML files are written")
    args = parser.parse_args()

    spec = load_spec(Path(args.spec))
    public_dir = Path(args.public_dir)
    block = render_iframe_block(spec, public_dir)
    update_markdown(Path(args.storm_md), block)


if __name__ == "__main__":
    main()
