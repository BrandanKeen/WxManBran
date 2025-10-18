#!/usr/bin/env python3
"""Build interactive Plotly HTML charts from a plot specification."""
from __future__ import annotations

import argparse
import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


LINESTYLE_MAP = {
    "-": "solid",
    "--": "dash",
    "-.": "dashdot",
    ":": "dot",
}

LEGEND_LOCATIONS = {
    "best": ("right", "top", 0.01, 0.01),
    "upper right": ("right", "top", 0.01, 0.01),
    "upper left": ("left", "top", 0.01, 0.01),
    "lower right": ("right", "bottom", 0.01, 0.01),
    "lower left": ("left", "bottom", 0.01, 0.01),
    "upper center": ("center", "top", 0.0, 0.01),
    "lower center": ("center", "bottom", 0.0, 0.01),
    "center left": ("left", "middle", 0.01, 0.0),
    "center right": ("right", "middle", 0.01, 0.0),
    "center": ("center", "middle", 0.0, 0.0),
}

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.31.1.min.js"


@dataclass
class SeriesEntry:
    column: str
    label: str
    color: Optional[str]
    linestyle: Optional[str]
    alpha: Optional[float]
    secondary_y: bool


@dataclass
class ProcessedSeries:
    series: SeriesEntry
    values: List[Optional[float]]
    label: str
    unit: str
    hover_format: str


@dataclass
class HoverEntry:
    label: str
    values: List[Optional[float]]
    unit: str
    hover_format: str


@dataclass
class SubplotEntry:
    row: int
    col: int
    title: Optional[str]
    ylabel: Optional[str]
    ylabel_color: Optional[str]
    legend_loc: Optional[str]
    grid: Optional[bool]
    series: List[SeriesEntry]
    secondary_ylabel: Optional[str] = None
    secondary_ylabel_color: Optional[str] = None
    secondary_grid: Optional[bool] = None


@dataclass
class FigureSpec:
    outfile: str
    title: Optional[str]
    xlabel: Optional[str]
    x_tickformat: Optional[str]
    type: str
    ylabel: Optional[str] = None
    ylabel_color: Optional[str] = None
    yaxis_color: Optional[str] = None
    legend_loc: Optional[str] = None
    grid: Optional[bool] = None
    series: Optional[List[SeriesEntry]] = None
    secondary_ylabel: Optional[str] = None
    secondary_ylabel_color: Optional[str] = None
    secondary_grid: Optional[bool] = None
    rows: Optional[int] = None
    cols: Optional[int] = None
    sharex: Optional[bool] = None
    subplots: Optional[List[SubplotEntry]] = None


@dataclass
class StormData:
    times: List[str]
    columns: Dict[str, List[Optional[float]]]


def parse_series(series_data: Dict[str, object]) -> SeriesEntry:
    return SeriesEntry(
        column=series_data.get("column"),
        label=series_data.get("label") or series_data.get("column"),
        color=series_data.get("color"),
        linestyle=series_data.get("linestyle"),
        alpha=series_data.get("alpha"),
        secondary_y=bool(series_data.get("secondary_y")),
    )


def parse_figure(entry: Dict[str, object]) -> FigureSpec:
    series = entry.get("series")
    subplots = entry.get("subplots")
    figure_series = None
    subplot_entries = None
    if series:
        figure_series = [parse_series(item) for item in series]
    if subplots:
        subplot_entries = []
        for subplot in subplots:
            subplot_series = [parse_series(item) for item in subplot.get("series", [])]
            subplot_entries.append(
                SubplotEntry(
                    row=int(subplot.get("row", 1)),
                    col=int(subplot.get("col", 1)),
                    title=subplot.get("title"),
                    ylabel=subplot.get("ylabel"),
                    ylabel_color=subplot.get("ylabel_color"),
                    legend_loc=subplot.get("legend_loc"),
                    grid=subplot.get("grid"),
                    series=subplot_series,
                    secondary_ylabel=subplot.get("secondary_ylabel"),
                    secondary_ylabel_color=subplot.get("secondary_ylabel_color") or subplot.get("secondary_yaxis_color"),
                    secondary_grid=subplot.get("secondary_grid"),
                )
            )
    return FigureSpec(
        outfile=entry.get("outfile"),
        title=entry.get("title"),
        xlabel=entry.get("xlabel"),
        x_tickformat=entry.get("x_tickformat"),
        type=entry.get("type", "single"),
        ylabel=entry.get("ylabel"),
        ylabel_color=entry.get("ylabel_color") or entry.get("yaxis_color"),
        legend_loc=entry.get("legend_loc"),
        grid=entry.get("grid"),
        series=figure_series,
        secondary_ylabel=entry.get("secondary_ylabel"),
        secondary_ylabel_color=entry.get("secondary_ylabel_color") or entry.get("secondary_yaxis_color"),
        secondary_grid=entry.get("secondary_grid"),
        rows=entry.get("rows"),
        cols=entry.get("cols"),
        sharex=entry.get("sharex"),
        subplots=subplot_entries,
    )


def load_spec(path: Path) -> List[FigureSpec]:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [parse_figure(entry) for entry in raw]


def parse_float(value: str) -> Optional[float]:
    if value == "" or value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


TIME_COLUMN_CANDIDATES = [
    "Date Time",
    "Datetime",
    "DateTime",
    "Timestamp",
]


def load_data(csv_path: Path) -> StormData:
    times: List[str] = []
    columns: Dict[str, List[Optional[float]]] = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return StormData(times=times, columns=columns)

        time_key = next(
            (name for name in TIME_COLUMN_CANDIDATES if name in reader.fieldnames),
            None,
        )
        if not time_key:
            raise ValueError(
                "Could not determine time column in CSV. Expected one of: "
                + ", ".join(TIME_COLUMN_CANDIDATES)
            )

        for row in reader:
            raw_time = row.get(time_key)
            if not raw_time:
                continue
            dt = datetime.strptime(raw_time.strip(), "%m/%d/%Y %H:%M")
            times.append(dt.isoformat())
            for key, value in row.items():
                if key in {time_key, None}:
                    continue
                cell = value.strip() if isinstance(value, str) else value
                columns.setdefault(key, []).append(parse_float(cell))
    return StormData(times=times, columns=columns)


def extract_units(label: Optional[str]) -> str:
    if not label:
        return ""
    cleaned = label.strip()
    if not cleaned:
        return ""
    if cleaned.endswith(")") and "(" in cleaned:
        inner = cleaned[cleaned.rfind("(") + 1 : -1].strip()
        if inner:
            return inner
    return cleaned


def hover_time_format(tickformat: Optional[str]) -> str:
    if not tickformat:
        return "%Y-%m-%d %H:%M"
    sanitized = tickformat.replace("\n", " ").strip()
    return sanitized or "%Y-%m-%d %H:%M"


def map_linestyle(style: Optional[str]) -> str:
    if not style:
        return "solid"
    return LINESTYLE_MAP.get(style, "solid")


def compute_domains(rows: int, cols: int, h_spacing: float = 0.08, v_spacing: float = 0.12) -> Dict[Tuple[int, int], Tuple[List[float], List[float]]]:
    usable_width = 1.0 - h_spacing * (cols - 1)
    usable_height = 1.0 - v_spacing * (rows - 1)
    width = usable_width / cols
    height = usable_height / rows
    domains: Dict[Tuple[int, int], Tuple[List[float], List[float]]] = {}
    for r in range(1, rows + 1):
        for c in range(1, cols + 1):
            x_start = (c - 1) * (width + h_spacing)
            x_end = x_start + width
            y_end = 1.0 - (r - 1) * (height + v_spacing)
            y_start = y_end - height
            domains[(r, c)] = ([x_start, x_end], [y_start, y_end])
    return domains


def legend_position(loc: Optional[str], x_domain: List[float], y_domain: List[float]) -> Optional[Dict[str, object]]:
    if not loc:
        return None
    loc_key = loc.lower()
    if loc_key not in LEGEND_LOCATIONS:
        return None
    xanchor, yanchor, dx, dy = LEGEND_LOCATIONS[loc_key]
    x_start, x_end = x_domain
    y_start, y_end = y_domain
    margin_x = dx
    margin_y = dy
    if xanchor == "left":
        x = x_start + margin_x
    elif xanchor == "right":
        x = x_end - margin_x
    else:
        x = (x_start + x_end) / 2
    if yanchor == "bottom":
        y = y_start + margin_y
    elif yanchor == "top":
        y = y_end - margin_y
    else:
        y = (y_start + y_end) / 2
    return {
        "x": x,
        "y": y,
        "xanchor": xanchor,
        "yanchor": yanchor,
        "bgcolor": "rgba(255,255,255,0.8)",
        "bordercolor": "rgba(0,0,0,0)",
        "borderwidth": 0,
        "tracegroupgap": 0,
    }


def is_pressure_context(*parts: Optional[str]) -> bool:
    for part in parts:
        if not part:
            continue
        lowered = part.lower()
        if "pressure" in lowered:
            return True
        if lowered.strip() in {"mb", "millibar", "millibars"}:
            return True
    return False


def pressure_hover_format(is_pressure: bool) -> str:
    return ":.1f" if is_pressure else ""


def format_unit_suffix(unit: str) -> str:
    return f" {unit}" if unit else ""


def find_rain_accumulation_column(
    columns: Dict[str, List[Optional[float]]]
) -> Optional[Tuple[str, List[Optional[float]]]]:
    for key, values in columns.items():
        if key and "rain accum" in key.lower():
            return key, values
    return None


def accumulation_unit_from_rate(rate_unit: str) -> str:
    if not rate_unit:
        return ""
    if "/" in rate_unit:
        prefix = rate_unit.split("/", 1)[0].strip()
        if prefix:
            return prefix
    return rate_unit


def build_hover_details(
    base_label: str,
    base_format: str,
    base_unit: str,
    time_fmt: str,
    values_length: int,
    extras: List[HoverEntry],
) -> Tuple[str, Optional[List[List[Optional[float]]]]]:
    extra_template = ""
    customdata: Optional[List[List[Optional[float]]]] = None
    if extras:
        customdata = [
            [entry.values[i] if i < len(entry.values) else None for entry in extras]
            for i in range(values_length)
        ]
        for idx, entry in enumerate(extras):
            extra_template += (
                f"<br>{entry.label}: %{{customdata[{idx}]{entry.hover_format}}}"
                f"{format_unit_suffix(entry.unit)}"
            )
    hovertemplate = (
        f"Time: %{{x|{time_fmt}}}<br>"
        f"{base_label}: %{{y{base_format}}}{format_unit_suffix(base_unit)}"
        f"{extra_template}<extra></extra>"
    )
    return hovertemplate, customdata


def build_single_figure(spec: FigureSpec, data: StormData) -> Dict[str, object]:
    traces: List[Dict[str, object]] = []
    legend_name = None
    layout: Dict[str, object] = {
        "hovermode": "closest",
        "plot_bgcolor": "#ffffff",
        "paper_bgcolor": "#ffffff",
        "margin": {"l": 60, "r": 60, "t": 60 if spec.title else 40, "b": 60},
        "font": {"family": "Arial", "size": 12},
        "hoverlabel": {"bgcolor": "#f0f0f0"},
    }
    layout["spikedistance"] = -1
    layout["hoverdistance"] = -1
    if spec.title:
        layout["title"] = spec.title
    if spec.legend_loc:
        legend_settings = legend_position(spec.legend_loc, [0.0, 1.0], [0.0, 1.0])
        if legend_settings:
            layout["legend"] = legend_settings
            legend_name = "legend"
    time_fmt = hover_time_format(spec.x_tickformat)
    processed_series: List[ProcessedSeries] = []
    for series in spec.series or []:
        column_values = data.columns.get(series.column)
        if column_values is None:
            continue
        label = series.label or series.column
        base_unit = extract_units(spec.secondary_ylabel if series.secondary_y else spec.ylabel)
        is_pressure = is_pressure_context(
            label,
            series.column,
            format_unit_suffix(base_unit),
            spec.ylabel,
            spec.title,
            spec.secondary_ylabel,
        )
        hover_format = pressure_hover_format(is_pressure)
        processed_series.append(
            ProcessedSeries(
                series=series,
                values=column_values,
                label=label,
                unit=base_unit,
                hover_format=hover_format,
            )
        )
    rain_accum_column = find_rain_accumulation_column(data.columns)
    for meta in processed_series:
        extras: List[HoverEntry] = []
        if len(processed_series) > 1:
            for other in processed_series:
                if other is meta:
                    continue
                extras.append(
                    HoverEntry(
                        label=other.label,
                        values=other.values,
                        unit=other.unit,
                        hover_format=other.hover_format,
                    )
                )
        if rain_accum_column and "rain rate" in meta.series.column.lower():
            accum_label, accum_values = rain_accum_column
            extras.append(
                HoverEntry(
                    label=accum_label,
                    values=accum_values,
                    unit=accumulation_unit_from_rate(meta.unit),
                    hover_format=":.2f",
                )
            )
        hovertemplate, customdata = build_hover_details(
            meta.label,
            meta.hover_format,
            meta.unit,
            time_fmt,
            len(meta.values),
            extras,
        )
        trace: Dict[str, object] = {
            "type": "scatter",
            "mode": "lines",
            "x": data.times,
            "y": meta.values,
            "name": meta.label,
            "line": {"color": meta.series.color, "dash": map_linestyle(meta.series.linestyle)},
            "opacity": meta.series.alpha if meta.series.alpha is not None else 1.0,
            "hovertemplate": hovertemplate,
        }
        if customdata is not None:
            trace["customdata"] = customdata
        if meta.series.secondary_y:
            trace["yaxis"] = "y2"
        if legend_name:
            trace["legend"] = legend_name
        traces.append(trace)
    yaxis = {
        "title": spec.ylabel,
        "showline": True,
        "linecolor": spec.ylabel_color or "black",
        "ticks": "outside",
        "showgrid": True if spec.grid is None else bool(spec.grid),
        "gridcolor": "#d3d3d3",
        "zeroline": False,
        "mirror": False,
        "showspikes": True,
        "spikemode": "across+marker",
        "spikethickness": 1,
        "spikedash": "solid",
        "spikesnap": "hovered data",
    }
    if is_pressure_context(spec.ylabel, spec.title):
        yaxis["separatethousands"] = False
    if spec.ylabel_color:
        yaxis["tickfont"] = {"color": spec.ylabel_color}
        yaxis["titlefont"] = {"color": spec.ylabel_color}
    layout["yaxis"] = yaxis
    if any(series.secondary_y for series in spec.series or []):
        yaxis2 = {
            "title": spec.secondary_ylabel,
            "overlaying": "y",
            "side": "right",
            "showline": True,
            "linecolor": spec.secondary_ylabel_color or "black",
            "ticks": "outside",
            "showgrid": True if spec.secondary_grid is None else bool(spec.secondary_grid),
            "gridcolor": "rgba(0,0,0,0)",
            "zeroline": False,
            "mirror": False,
            "showspikes": True,
            "spikemode": "across+marker",
            "spikethickness": 1,
            "spikedash": "solid",
            "spikesnap": "hovered data",
        }
        if is_pressure_context(spec.secondary_ylabel, spec.title):
            yaxis2["separatethousands"] = False
        if spec.secondary_ylabel_color:
            yaxis2["tickfont"] = {"color": spec.secondary_ylabel_color}
            yaxis2["titlefont"] = {"color": spec.secondary_ylabel_color}
        layout["yaxis2"] = yaxis2
    layout["xaxis"] = {
        "title": spec.xlabel,
        "tickformat": spec.x_tickformat,
        "showline": True,
        "linecolor": "black",
        "ticks": "outside",
        "showgrid": True,
        "gridcolor": "#d3d3d3",
        "zeroline": False,
        "mirror": False,
        "showspikes": True,
        "spikemode": "across+marker",
        "spikethickness": 1,
        "spikedash": "solid",
        "spikesnap": "hovered data",
        "rangeslider": {"visible": True, "bgcolor": "#f0f0f0", "thickness": 0.12},
    }
    if spec.sharex:
        layout["xaxis"] = {
            "domain": [0.0, 1.0],
            "anchor": "free",
            "position": 0.0,
            "showgrid": False,
            "showline": False,
            "ticks": "",
            "showticklabels": False,
            "visible": False,
            "type": "date",
            "rangeslider": {"visible": True, "bgcolor": "#f0f0f0", "thickness": 0.12},
            "spikemode": "across+marker",
            "showspikes": False,
        }
    config = {
        "responsive": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["resetScale2d", "lasso2d", "select2d"],
    }
    return {"data": traces, "layout": layout, "config": config}


def axis_name(prefix: str, index: int) -> str:
    if index == 1:
        return f"{prefix}axis"
    return f"{prefix}axis{index}"


def axis_ref(prefix: str, index: int) -> str:
    if index == 1:
        return prefix
    return f"{prefix}{index}"


def build_grid_figure(spec: FigureSpec, data: StormData) -> Dict[str, object]:
    rows = int(spec.rows or 1)
    cols = int(spec.cols or 1)
    domains = compute_domains(rows, cols)
    traces: List[Dict[str, object]] = []
    layout: Dict[str, object] = {
        "hovermode": "closest",
        "plot_bgcolor": "#ffffff",
        "paper_bgcolor": "#ffffff",
        "margin": {"l": 60, "r": 60, "t": 60 if spec.title else 40, "b": 110},
        "font": {"family": "Arial", "size": 12},
        "grid": {"rows": rows, "columns": cols, "pattern": "independent", "roworder": "top to bottom"},
        "hoverlabel": {"bgcolor": "#f0f0f0"},
    }
    layout["spikedistance"] = -1
    layout["hoverdistance"] = -1
    time_fmt = hover_time_format(spec.x_tickformat)
    if spec.title:
        layout["title"] = spec.title
    legend_count = 0
    total_axes = rows * cols
    secondary_counter = 0
    rain_accum_column = find_rain_accumulation_column(data.columns)
    for subplot in spec.subplots or []:
        index = (subplot.row - 1) * cols + subplot.col
        x_domain, y_domain = domains[(subplot.row, subplot.col)]
        legend_settings = legend_position(subplot.legend_loc, x_domain, y_domain)
        legend_name = None
        if legend_settings:
            legend_count += 1
            key = "legend" if legend_count == 1 else f"legend{legend_count}"
            layout[key] = legend_settings
            legend_name = key
        subplot_series: List[ProcessedSeries] = []
        for series in subplot.series:
            column_values = data.columns.get(series.column)
            if column_values is None:
                continue
            label = series.label or series.column
            base_unit = extract_units(subplot.secondary_ylabel if series.secondary_y else subplot.ylabel)
            is_pressure = is_pressure_context(
                label,
                series.column,
                format_unit_suffix(base_unit),
                subplot.ylabel,
                subplot.title,
                subplot.secondary_ylabel,
            )
            hover_format = pressure_hover_format(is_pressure)
            subplot_series.append(
                ProcessedSeries(
                    series=series,
                    values=column_values,
                    label=label,
                    unit=base_unit,
                    hover_format=hover_format,
                )
            )
        for meta in subplot_series:
            extras: List[HoverEntry] = []
            if len(subplot_series) > 1:
                for other in subplot_series:
                    if other is meta:
                        continue
                    extras.append(
                        HoverEntry(
                            label=other.label,
                            values=other.values,
                            unit=other.unit,
                            hover_format=other.hover_format,
                        )
                    )
            if rain_accum_column and "rain rate" in meta.series.column.lower():
                accum_label, accum_values = rain_accum_column
                extras.append(
                    HoverEntry(
                        label=accum_label,
                        values=accum_values,
                        unit=accumulation_unit_from_rate(meta.unit),
                        hover_format=":.2f",
                    )
                )
            hovertemplate, customdata = build_hover_details(
                meta.label,
                meta.hover_format,
                meta.unit,
                time_fmt,
                len(meta.values),
                extras,
            )
            trace = {
                "type": "scatter",
                "mode": "lines",
                "x": data.times,
                "y": meta.values,
                "name": meta.label,
                "line": {"color": meta.series.color, "dash": map_linestyle(meta.series.linestyle)},
                "opacity": meta.series.alpha if meta.series.alpha is not None else 1.0,
                "xaxis": axis_ref("x", index),
                "yaxis": axis_ref("y", index),
                "hovertemplate": hovertemplate,
            }
            if customdata is not None:
                trace["customdata"] = customdata
            if meta.series.secondary_y:
                secondary_counter += 1
                sec_index = total_axes + secondary_counter
                trace["yaxis"] = axis_ref("y", sec_index)
            if legend_name:
                trace["legend"] = legend_name
            traces.append(trace)
        # Primary axis definition
        xaxis_name = axis_name("x", index)
        yaxis_name = axis_name("y", index)
        layout[xaxis_name] = {
            "domain": x_domain,
            "anchor": axis_ref("y", index),
            "tickformat": spec.x_tickformat,
            "showline": True,
            "linecolor": "black",
            "ticks": "outside",
            "showgrid": True,
            "gridcolor": "#d3d3d3",
            "zeroline": False,
            "mirror": False,
            "showspikes": True,
            "spikemode": "across+marker",
            "spikethickness": 1,
            "spikedash": "solid",
            "spikesnap": "hovered data",
        }
        if spec.sharex:
            layout[xaxis_name]["rangeslider"] = {"visible": False}
        if spec.sharex:
            layout[xaxis_name]["matches"] = "x"
        primary_axis = {
            "domain": y_domain,
            "anchor": axis_ref("x", index),
            "title": subplot.ylabel,
            "showline": True,
            "linecolor": subplot.ylabel_color or "black",
            "ticks": "outside",
            "showgrid": True if subplot.grid is None else bool(subplot.grid),
            "gridcolor": "#d3d3d3",
            "zeroline": False,
            "mirror": False,
            "showspikes": True,
            "spikemode": "across+marker",
            "spikethickness": 1,
            "spikedash": "solid",
            "spikesnap": "hovered data",
        }
        if is_pressure_context(subplot.ylabel, subplot.title):
            primary_axis["separatethousands"] = False
        if subplot.ylabel_color:
            primary_axis["titlefont"] = {"color": subplot.ylabel_color}
            primary_axis["tickfont"] = {"color": subplot.ylabel_color}
        layout[yaxis_name] = primary_axis
        if any(s.secondary_y for s in subplot.series):
            sec_index = total_axes + secondary_counter
            secondary_name = axis_name("y", sec_index)
            secondary_axis = {
                "domain": y_domain,
                "anchor": axis_ref("x", index),
                "title": subplot.secondary_ylabel,
                "showline": True,
                "linecolor": subplot.secondary_ylabel_color or "black",
                "ticks": "outside",
                "overlaying": axis_ref("y", index),
                "side": "right",
                "showgrid": True if subplot.secondary_grid is None else bool(subplot.secondary_grid),
                "gridcolor": "rgba(0,0,0,0)",
                "zeroline": False,
                "mirror": False,
                "showspikes": True,
                "spikemode": "across+marker",
                "spikethickness": 1,
                "spikedash": "solid",
                "spikesnap": "hovered data",
            }
            if subplot.secondary_grid is not None and not subplot.secondary_grid:
                secondary_axis["showgrid"] = False
            if is_pressure_context(subplot.secondary_ylabel, subplot.title):
                secondary_axis["separatethousands"] = False
            if subplot.secondary_ylabel_color:
                secondary_axis["titlefont"] = {"color": subplot.secondary_ylabel_color}
                secondary_axis["tickfont"] = {"color": subplot.secondary_ylabel_color}
            layout[secondary_name] = secondary_axis
        if subplot.title:
            layout.setdefault("annotations", []).append(
                {
                    "text": subplot.title,
                    "xref": "paper",
                    "yref": "paper",
                    "x": sum(x_domain) / 2,
                    "y": min(y_domain[1] + 0.04, 0.99),
                    "xanchor": "center",
                    "yanchor": "bottom",
                    "showarrow": False,
                    "font": {"size": 13},
                }
            )
    if spec.sharex:
        layout["xaxis"] = {
            "domain": [0.0, 1.0],
            "anchor": "free",
            "position": 0.0,
            "showgrid": False,
            "showline": False,
            "ticks": "",
            "showticklabels": False,
            "visible": False,
            "type": "date",
            "rangeslider": {"visible": True, "bgcolor": "#f0f0f0", "thickness": 0.12},
            "spikemode": "across+marker",
            "showspikes": False,
        }
        layout["spikedistance"] = -1
        layout["hoverdistance"] = -1
    else:
        layout["spikedistance"] = -1
        layout["hoverdistance"] = -1
    config = {
        "responsive": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["resetScale2d", "lasso2d", "select2d"],
    }
    return {"data": traces, "layout": layout, "config": config}


def build_figure(spec: FigureSpec, data: StormData) -> Dict[str, object]:
    if spec.type == "grid" and spec.subplots:
        return build_grid_figure(spec, data)
    return build_single_figure(spec, data)


def ensure_output_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_html(path: Path, figure: Dict[str, object]) -> None:
    figure_json = json.dumps({"data": figure["data"], "layout": figure["layout"]})
    config_json = json.dumps(figure["config"])
    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <script src=\"{PLOTLY_CDN}\"></script>
  <style>
    body {{ margin: 0; padding: 0; }}
    #chart {{ width: 100%; height: 100vh; }}
  </style>
</head>
<body>
  <div id=\"chart\"></div>
  <script>
    const figure = {figure_json};
    const config = {config_json};
    const toTimestamp = (value) => {{
      if (value === null || value === undefined) {{
        return NaN;
      }}
      if (typeof value === 'number') {{
        return value;
      }}
      const parsed = Date.parse(value);
      return Number.isNaN(parsed) ? NaN : parsed;
    }};
    Plotly.newPlot('chart', figure.data, figure.layout, config).then((gd) => {{
      const originalCount = gd.data.length;
      const originalTraces = gd.data.slice(0, originalCount);
      const highlightTraces = [];
      const highlightIndexMap = new Map();
      originalTraces.forEach((trace, index) => {{
        if (trace.type !== 'scatter') {{
          highlightIndexMap.set(index, null);
          return;
        }}
        const color = trace.line && trace.line.color ? trace.line.color : '#1f77b4';
        highlightIndexMap.set(index, originalCount + highlightTraces.length);
        highlightTraces.push({{
          x: [trace.x && trace.x.length ? trace.x[0] : null],
          y: [trace.y && trace.y.length ? trace.y[0] : null],
          mode: 'markers',
          marker: {{
            size: 10,
            color,
            symbol: 'circle',
            line: {{ color: 'rgba(0, 0, 0, 0.85)', width: 2 }},
            opacity: 1
          }},
          showlegend: false,
          hoverinfo: 'skip',
          xaxis: trace.xaxis,
          yaxis: trace.yaxis,
          visible: false,
          cliponaxis: false
        }});
      }});
      const addHighlights = highlightTraces.length ? Plotly.addTraces(gd, highlightTraces) : Promise.resolve();
      const dataLookup = originalTraces.map((trace, curveNumber) => {{
        if (!trace.x || !trace.y) {{
          return [];
        }}
        const entries = [];
        const subplotRef = (trace.xaxis || 'x') + (trace.yaxis || 'y');
        for (let i = 0; i < trace.x.length; i += 1) {{
          const xValue = trace.x[i];
          const yValue = trace.y[i];
          if (yValue === null || typeof yValue === 'undefined') {{
            continue;
          }}
          const timestamp = toTimestamp(xValue);
          if (!Number.isFinite(timestamp)) {{
            continue;
          }}
          entries.push({{ time: timestamp, x: xValue, y: yValue, index: i, curveNumber, subplot: subplotRef }});
        }}
        return entries;
      }});
      let suppressSyntheticHover = false;
      function hideHighlights() {{
        highlightIndexMap.forEach((highlightIdx) => {{
          if (highlightIdx === null) {{
            return;
          }}
          Plotly.restyle(gd, {{ visible: false }}, highlightIdx);
        }});
      }}
      function findMatch(entries, targetTime) {{
        let exact = null;
        let best = null;
        let bestDiff = Infinity;
        for (const entry of entries) {{
          const diff = Math.abs(entry.time - targetTime);
          if (diff === 0) {{
            exact = entry;
            break;
          }}
          if (diff < bestDiff) {{
            bestDiff = diff;
            best = entry;
          }}
        }}
        return exact || best;
      }}
      addHighlights.then(() => {{
        if (!highlightTraces.length) {{
          return;
        }}
        gd.on('plotly_hover', (event) => {{
          if (suppressSyntheticHover) {{
            return;
          }}
          if (!event.points || !event.points.length) {{
            hideHighlights();
            return;
          }}
          const targetTime = toTimestamp(event.points[0].x);
          if (!Number.isFinite(targetTime)) {{
            hideHighlights();
            return;
          }}
          const hoverPoints = [];
          highlightIndexMap.forEach((highlightIdx, sourceIdx) => {{
            if (highlightIdx === null) {{
              return;
            }}
            const entries = dataLookup[sourceIdx];
            if (!entries || !entries.length) {{
              Plotly.restyle(gd, {{ visible: false }}, highlightIdx);
              return;
            }}
            const match = findMatch(entries, targetTime);
            if (!match) {{
              Plotly.restyle(gd, {{ visible: false }}, highlightIdx);
              return;
            }}
            Plotly.restyle(gd, {{ x: [[match.x]], y: [[match.y]], visible: true }}, highlightIdx);
            hoverPoints.push({{ curveNumber: match.curveNumber, pointNumber: match.index, subplot: match.subplot }});
          }});
          if (!suppressSyntheticHover) {{
            suppressSyntheticHover = true;
            const uniquePoints = hoverPoints.filter((point, idx, arr) =>
              arr.findIndex(
                (p) =>
                  p.curveNumber === point.curveNumber &&
                  p.pointNumber === point.pointNumber &&
                  p.subplot === point.subplot
              ) === idx
            );
            if (uniquePoints.length) {{
              Plotly.Fx.hover(gd, uniquePoints);
              setTimeout(() => {{
                suppressSyntheticHover = false;
              }}, 0);
            }} else {{
              suppressSyntheticHover = false;
              Plotly.Fx.unhover(gd);
            }}
          }}
        }});
        gd.on('plotly_unhover', () => {{
          hideHighlights();
          if (!suppressSyntheticHover) {{
            Plotly.Fx.unhover(gd);
          }}
        }});
      }});
    }});
  </script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Plotly charts from a plot spec")
    parser.add_argument("--csv", required=True, help="Path to the CSV data file")
    parser.add_argument("--spec", required=True, help="Path to the JSON spec file")
    parser.add_argument("--out", required=True, help="Directory to write HTML files")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    output_dir = Path(args.out)
    ensure_output_directory(output_dir)

    figures = load_spec(spec_path)
    data = load_data(Path(args.csv))

    for spec in figures:
        figure = build_figure(spec, data)
        html_name = Path(spec.outfile).with_suffix(".html").name
        write_html(output_dir / html_name, figure)


if __name__ == "__main__":
    main()
