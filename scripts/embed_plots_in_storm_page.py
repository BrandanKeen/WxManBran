#!/usr/bin/env python3
import argparse
import html
import json
from pathlib import Path
from typing import List

MARKER_START = "<!-- DATA-SECTION:START -->"
MARKER_END = "<!-- DATA-SECTION:END -->"


def load_spec(path: Path) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_plot_group(summary: str, body: str, *, open_default: bool = False, extra_classes: str = "") -> str:
    open_attr = " open" if open_default else ""
    classes = "storm-plot"
    if extra_classes:
        classes = f"{classes} {extra_classes}".strip()
    return (
        f"  <details class=\"storm-plot-group\"{open_attr}>\n"
        f"    <summary class=\"storm-plot-summary\">{summary}</summary>\n"
        f"    <div class=\"{classes}\">\n"
        f"{body}\n"
        "    </div>\n"
        "  </details>"
    )


def render_image_group(entry: dict, public_dir: Path) -> str:
    outfile = entry.get("outfile")
    if not outfile:
        return ""
    title = entry.get("title") or Path(outfile).stem.replace("_", " ")
    summary = html.escape("Multi-Panel Plots")
    alt_text = html.escape(f"Multi-panel plot for {title}")
    image_name = Path(outfile).name
    rel_path = (public_dir / image_name).as_posix().lstrip("/")
    image_url = f"{{{{ '/{rel_path}' | relative_url }}}}"
    body = (
        "      <figure class=\"storm-multi-panels__figure\">\n"
        "        <span class=\"storm-multi-panels__watermark\" aria-hidden=\"true\">WxManBran.com</span>\n"
        f"        <img src=\"{image_url}\" alt=\"{alt_text}\" loading=\"lazy\">\n"
        "      </figure>"
    )
    return build_plot_group(summary, body, open_default=True, extra_classes="storm-multi-panels")


def render_iframe_group(entry: dict, public_dir: Path) -> str:
    outfile = entry.get("outfile")
    if not outfile:
        return ""
    title = entry.get("title") or Path(outfile).stem.replace("_", " ")
    summary = html.escape(title)
    html_name = Path(outfile).with_suffix(".html").name
    rel_path = (public_dir / html_name).as_posix().lstrip("/")
    iframe_url = f"{{{{ '/{rel_path}' | relative_url }}}}"
    body = (
        f"      <iframe src=\"{iframe_url}\" width=\"100%\" height=\"520\" loading=\"lazy\" style=\"border:0\"></iframe>"
    )
    return build_plot_group(summary, body, open_default=False)


def render_data_block(spec: List[dict], public_dir: Path) -> str:
    groups: List[str] = []
    for entry in spec:
        if entry.get("type") == "grid" and entry.get("subplots"):
            group = render_image_group(entry, public_dir)
        else:
            group = render_iframe_group(entry, public_dir)
        if group:
            groups.append(group)
    content = "\n".join(groups)
    if content:
        content += "\n"
    return (
        "<h2>Data</h2>\n"
        "<div class=\"storm-data\">\n"
        f"{content}"
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
        new_text = text[:start_idx] + "\n\n" + block + "\n" + text[end_idx:]
    else:
        if not text.endswith("\n"):
            text += "\n"
        new_text = text + "\n" + MARKER_START + "\n\n" + block + "\n" + MARKER_END + "\n"
    path.write_text(new_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Embed Plotly plots into storm markdown page")
    parser.add_argument("--spec", required=True, help="Path to the plot spec JSON")
    parser.add_argument("--storm-md", required=True, help="Path to the storm markdown file")
    parser.add_argument("--public-dir", required=True, help="Directory where plot HTML files are written")
    args = parser.parse_args()

    spec = load_spec(Path(args.spec))
    public_dir = Path(args.public_dir)
    block = render_data_block(spec, public_dir)
    update_markdown(Path(args.storm_md), block)


if __name__ == "__main__":
    main()
