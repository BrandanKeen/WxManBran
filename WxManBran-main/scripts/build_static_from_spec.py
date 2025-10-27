#!/usr/bin/env python3
"""Build static multi-panel plots from a plot specification."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from zoneinfo import ZoneInfo

from plot_spec_utils import FigureSpec, StormData, load_data, load_spec


EASTERN = ZoneInfo("America/New_York")


def to_datetime(values: Iterable[str]) -> List[datetime]:
    timestamps: List[datetime] = []
    for value in values:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=EASTERN)
        else:
            dt = dt.astimezone(EASTERN)
        timestamps.append(dt)
    return timestamps


def ensure_output_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def series_values(data: StormData, column: str) -> List[Optional[float]]:
    values = data.columns.get(column)
    if values is None:
        return [None for _ in data.times]
    return values


def convert_to_numeric(values: Iterable[Optional[float]]) -> np.ndarray:
    return np.array([np.nan if value is None else value for value in values], dtype=float)


def prepare_axis(ax, subplot, timestamps: List[datetime], shared: bool) -> None:
    ax.set_title(subplot.title)
    if subplot.ylabel:
        if subplot.ylabel_color:
            ax.set_ylabel(subplot.ylabel, color=subplot.ylabel_color)
        else:
            ax.set_ylabel(subplot.ylabel)
    if subplot.grid:
        ax.grid(True, which="major", linestyle="--", linewidth=0.8, alpha=0.6)
    if shared:
        ax.set_xlabel("")
    ax.tick_params(axis="x", labelrotation=0)


def apply_secondary_axis(ax, subplot):
    if subplot.secondary_ylabel:
        sec = ax.twinx()
        if subplot.secondary_ylabel_color:
            sec.set_ylabel(subplot.secondary_ylabel, color=subplot.secondary_ylabel_color)
        else:
            sec.set_ylabel(subplot.secondary_ylabel)
        if subplot.secondary_grid:
            sec.grid(True, which="major", linestyle="--", linewidth=0.8, alpha=0.6)
        return sec
    return None


def plot_subplot(ax, subplot, timestamps: List[datetime], data: StormData) -> None:
    secondary_ax = apply_secondary_axis(ax, subplot)
    primary_lines = []
    secondary_lines = []

    for entry in subplot.series:
        values = convert_to_numeric(series_values(data, entry.column))
        target_ax = secondary_ax if entry.secondary_y and secondary_ax else ax
        line, = target_ax.plot(
            timestamps,
            values,
            label=entry.label,
            color=entry.color,
            linestyle=entry.linestyle or "-",
            alpha=entry.alpha,
        )
        if target_ax is ax:
            primary_lines.append(line)
        else:
            secondary_lines.append(line)

    legend_lines = primary_lines + secondary_lines
    if legend_lines and subplot.legend_loc:
        labels = [line.get_label() for line in legend_lines]
        ax.legend(legend_lines, labels, loc=subplot.legend_loc)


def format_time_axis(fig: plt.Figure, axes: Iterable[plt.Axes], spec: FigureSpec) -> None:
    formatter = None
    if spec.x_tickformat:
        formatter = mdates.DateFormatter(spec.x_tickformat, tz=EASTERN)
    else:
        formatter = mdates.DateFormatter("%m-%d\n%H:%M", tz=EASTERN)
    for ax in axes:
        ax.xaxis.set_major_formatter(formatter)
        for label in ax.get_xticklabels():
            label.set_rotation(0)
            label.set_horizontalalignment("center")
    fig.autofmt_xdate()


def build_multi_panel(spec: FigureSpec, data: StormData, output_dir: Path) -> None:
    if not spec.subplots or not spec.rows or not spec.cols:
        return
    timestamps = to_datetime(data.times)
    fig, ax_grid = plt.subplots(spec.rows, spec.cols, figsize=(14, 8), sharex=bool(spec.sharex))
    if spec.title:
        fig.suptitle(spec.title, fontsize=16)

    # Ensure ax_grid is iterable of lists for consistent indexing
    if spec.rows == 1 and spec.cols == 1:
        axes_matrix = [[ax_grid]]
    elif spec.rows == 1:
        axes_matrix = [np.atleast_1d(ax_grid)]
    elif spec.cols == 1:
        axes_matrix = [[ax] for ax in np.atleast_1d(ax_grid)]
    else:
        axes_matrix = ax_grid

    all_axes: List[plt.Axes] = []
    for subplot in spec.subplots:
        r_idx = subplot.row - 1
        c_idx = subplot.col - 1
        ax = axes_matrix[r_idx][c_idx]
        prepare_axis(ax, subplot, timestamps, bool(spec.sharex))
        plot_subplot(ax, subplot, timestamps, data)
        all_axes.append(ax)

    format_time_axis(fig, all_axes, spec)
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    output_name = Path(spec.outfile)
    if output_name.suffix.lower() not in {".svg"}:
        output_name = output_name.with_suffix(".svg")
    output_path = output_dir / output_name
    fig.savefig(output_path, dpi=300, bbox_inches="tight", format="svg")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static multi-panel plots from a plot spec")
    parser.add_argument("--csv", required=True, help="Path to the CSV data file")
    parser.add_argument("--spec", required=True, help="Path to the JSON spec file")
    parser.add_argument("--out", required=True, help="Directory to write output images")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    output_dir = Path(args.out)
    ensure_output_directory(output_dir)

    figures = load_spec(spec_path)
    data = load_data(Path(args.csv))

    for spec in figures:
        if spec.type != "grid":
            continue
        build_multi_panel(spec, data, output_dir)


if __name__ == "__main__":
    main()
