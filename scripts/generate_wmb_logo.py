"""Generate the WxManBran hurricane warning logo.

This script redraws the double-flag WxManBran logo and writes it to the
``assets/images/WMB_Hurricane_Warning_Logo.svg`` asset used on the site.
Running the script keeps the vector asset reproducible from source code
without checking in a binary file.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle


mpl.rcParams["svg.hashsalt"] = "wxmanbran-logo"
SVG_METADATA = {
    "Date": "2024-01-01T00:00:00",
    "Creator": "WxManBran logo generator",
}


FLAG_FILL = "#c8102e"
FLAG_EDGE = "#980f26"
FLAG_SHADOW = "#860d21"
FLAG_SQUARE = "#050505"
TEXT_FILL = "#a61127"
STROKE_INNER = "#b3132c"
STROKE_OUTER = "#ffffff"


def _add_flag(ax, base_y: float) -> None:
    """Draw a stylized hurricane warning flag."""
    wave = [
        (-0.05, base_y + 0.0),
        (2.75, base_y + 0.05),
        (3.2, base_y + 0.65),
        (2.75, base_y + 1.28),
        (-0.05, base_y + 1.33),
        (-0.35, base_y + 0.68),
    ]
    flag = Polygon(
        wave,
        closed=True,
        facecolor=FLAG_FILL,
        edgecolor=FLAG_EDGE,
        linewidth=28,
        joinstyle="round",
    )
    ax.add_patch(flag)

    shadow = Polygon(
        [(pt[0] + 0.09, pt[1] - 0.02) for pt in wave],
        closed=True,
        facecolor=FLAG_FILL,
        edgecolor=FLAG_SHADOW,
        linewidth=10,
        alpha=0.55,
    )
    ax.add_patch(shadow)

    square = Rectangle(
        (0.42, base_y + 0.35),
        0.95,
        0.63,
        facecolor=FLAG_SQUARE,
        edgecolor=FLAG_SQUARE,
    )
    ax.add_patch(square)


def build_logo(output_path: Path) -> None:
    """Create the WxManBran logo and write it to ``output_path``.

    The output is saved as an SVG so the logo stays textual in version
    control while still matching the raster asset used on the site.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig = plt.figure(figsize=(9.5, 4.1), dpi=144)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-0.75, 9.5)
    ax.set_ylim(-0.25, 4.15)
    ax.axis("off")
    fig.patch.set_alpha(0.0)
    ax.set_facecolor((0, 0, 0, 0))

    _add_flag(ax, 2.05)
    _add_flag(ax, 0.55)

    text = ax.text(
        3.45,
        1.95,
        "WMB",
        fontsize=280,
        fontweight="bold",
        fontfamily="DejaVu Serif",
        color=TEXT_FILL,
        va="center",
        ha="left",
    )
    text.set_path_effects(
        [
            path_effects.Stroke(linewidth=26, foreground=STROKE_OUTER),
            path_effects.Stroke(linewidth=12, foreground=STROKE_INNER),
            path_effects.Normal(),
        ]
    )

    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.savefig(output_path, format="svg", transparent=True, metadata=SVG_METADATA)
    plt.close(fig)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "assets" / "images" / "WMB_Hurricane_Warning_Logo.svg"
    build_logo(output_path)


if __name__ == "__main__":
    main()
