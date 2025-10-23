#!/usr/bin/env python3
"""Build interactive Plotly HTML charts from a plot specification."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from plot_spec_utils import (
    FigureSpec,
    HoverEntry,
    ProcessedSeries,
    SeriesEntry,
    StormData,
    SubplotEntry,
    load_data,
    load_spec,
)

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
    return "%b %d, %I:%M %p"


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


def should_force_legend(
    label: Optional[str],
    column: Optional[str],
    unit: Optional[str],
    *context: Optional[str],
) -> bool:
    label_lower = (label or "").lower()
    column_lower = (column or "").lower()
    if "rain rate" in label_lower or "rain rate" in column_lower:
        return True
    return is_pressure_context(label, column, format_unit_suffix(unit), *context)


def format_unit_suffix(unit: str) -> str:
    return f" {unit}" if unit else ""


def _is_cumulative_series(values: List[Optional[float]]) -> bool:
    prev: Optional[float] = None
    for value in values:
        if value is None:
            continue
        if prev is not None and value < prev - 1e-6:
            return False
        prev = value
    return True


def _forward_fill(values: List[Optional[float]]) -> List[Optional[float]]:
    filled: List[Optional[float]] = []
    last: Optional[float] = None
    for value in values:
        if value is None:
            filled.append(last)
        else:
            last = value
            filled.append(last)
    return filled


def _accumulate_incremental(values: List[Optional[float]]) -> List[Optional[float]]:
    totals: List[Optional[float]] = []
    running: Optional[float] = None
    for value in values:
        if value is None:
            totals.append(running)
            continue
        running = (running or 0.0) + value
        totals.append(running)
    return totals


def find_rain_accumulation_column(
    columns: Dict[str, List[Optional[float]]]
) -> Optional[Tuple[str, List[Optional[float]]]]:
    for key, values in columns.items():
        if not key or "rain accum" not in key.lower():
            continue

        non_null_values = [value for value in values if value is not None]
        if not non_null_values:
            continue

        # Columns with only a single non-null entry are unlikely to capture the
        # evolution of rainfall over time. Skip them unless they explicitly
        # represent a running total.
        if len(non_null_values) <= 1 and "total" not in key.lower():
            continue

        if "total" in key.lower() or _is_cumulative_series(values):
            totals = _forward_fill(values)
            label = key
        else:
            totals = _accumulate_incremental(values)
            label = "Rain Accumulation"

        if any(value is not None for value in totals):
            return label, totals

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
        f" %{{y{base_format}}}{format_unit_suffix(base_unit)}"
        f"{extra_template}<extra></extra>"
    )
    return hovertemplate, customdata


def build_single_figure(spec: FigureSpec, data: StormData) -> Dict[str, object]:
    traces: List[Dict[str, object]] = []
    legend_name = None
    layout: Dict[str, object] = {
        "hovermode": "x unified",
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
    force_persistent_legend = False
    for meta in processed_series:
        extras: List[HoverEntry] = []
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
        if should_force_legend(
            meta.label,
            meta.series.column,
            meta.unit,
            spec.ylabel,
            spec.title,
            spec.secondary_ylabel,
        ):
            trace["showlegend"] = True
            force_persistent_legend = True
        traces.append(trace)
    if force_persistent_legend:
        layout["showlegend"] = True
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
        "hoverformat": time_fmt,
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
        layout["xaxis"]["hoverformat"] = time_fmt
    config = {
        "responsive": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["resetScale2d", "lasso2d", "select2d"],
        "scrollZoom": True,
        "doubleClick": "reset",
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
        "hovermode": "x unified",
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
    force_persistent_legend = False
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
            if should_force_legend(
                meta.label,
                meta.series.column,
                meta.unit,
                subplot.ylabel,
                subplot.title,
                subplot.secondary_ylabel,
                spec.title,
            ):
                trace["showlegend"] = True
                force_persistent_legend = True
            traces.append(trace)
        # Primary axis definition
        xaxis_name = axis_name("x", index)
        yaxis_name = axis_name("y", index)
        layout[xaxis_name] = {
            "domain": x_domain,
            "anchor": axis_ref("y", index),
            "tickformat": spec.x_tickformat,
            "hoverformat": time_fmt,
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
        layout["xaxis"]["hoverformat"] = time_fmt
        layout["spikedistance"] = -1
        layout["hoverdistance"] = -1
    else:
        layout["spikedistance"] = -1
        layout["hoverdistance"] = -1
    if force_persistent_legend:
        layout["showlegend"] = True
    config = {
        "responsive": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["resetScale2d", "lasso2d", "select2d"],
        "scrollZoom": True,
        "doubleClick": "reset",
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
      const captureInitialView = () => {{
        const fullLayout = gd._fullLayout;
        if (!fullLayout) {{
          return {{}};
        }}
        const state = {{}};
        Object.keys(fullLayout).forEach((key) => {{
          if (!key.startsWith('xaxis') && !key.startsWith('yaxis')) {{
            return;
          }}
          const axis = fullLayout[key];
          if (!axis || typeof axis !== 'object') {{
            return;
          }}
          if (axis.autorange) {{
            state[`${{key}}.autorange`] = true;
          }} else if (Array.isArray(axis.range)) {{
            state[`${{key}}.range`] = axis.range.slice();
          }} else if (Array.isArray(axis._range)) {{
            state[`${{key}}.range`] = axis._range.slice();
          }}
        }});
        return state;
      }};
      let initialViewState = captureInitialView();
      const ensureInitialViewState = () => {{
        if (!initialViewState || !Object.keys(initialViewState).length) {{
          initialViewState = captureInitialView();
        }}
      }};
      const resetToInitialView = () => {{
        ensureInitialViewState();
        const relayoutUpdate = {{}};
        Object.keys(initialViewState || {{}}).forEach((key) => {{
          const value = initialViewState[key];
          relayoutUpdate[key] = Array.isArray(value) ? value.slice() : value;
        }});
        if (Object.keys(relayoutUpdate).length) {{
          Plotly.relayout(gd, relayoutUpdate);
        }}
      }};
      const clearHoverTitles = () => {{
        const fullLayout = gd._fullLayout;
        if (!fullLayout) {{
          return;
        }}
        Object.keys(fullLayout).forEach((key) => {{
          if (!key.startsWith('xaxis')) {{
            return;
          }}
          const axis = fullLayout[key];
          if (axis && typeof axis === 'object') {{
            axis._hovertitle = '';
          }}
        }});
      }};
      clearHoverTitles();
      ensureInitialViewState();
      gd.on('plotly_afterplot', ensureInitialViewState);
      gd.on('plotly_afterplot', clearHoverTitles);
      gd.on('plotly_relayout', clearHoverTitles);
      gd.on('plotly_restyle', clearHoverTitles);
      gd.on('plotly_update', clearHoverTitles);
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
      let pendingHoverState = null;
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
      function queuePendingHover(points, isUserEvent) {{
        if (!isUserEvent) {{
          return;
        }}
        if (!points || !points.length) {{
          pendingHoverState = {{ hasPoints: false }};
          return;
        }}
        const targetTime = toTimestamp(points[0].x);
        if (!Number.isFinite(targetTime)) {{
          pendingHoverState = {{ hasPoints: false }};
          return;
        }}
        pendingHoverState = {{ hasPoints: true, targetTime }};
      }}
      function flushPendingHover() {{
        if (!pendingHoverState) {{
          return;
        }}
        const state = pendingHoverState;
        pendingHoverState = null;
        if (!state.hasPoints) {{
          hideHighlights();
          Plotly.Fx.unhover(gd);
          return;
        }}
        applyHoverForTime(state.targetTime);
      }}
      function applyHoverForTime(targetTime) {{
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
        const uniquePoints = hoverPoints.filter((point, idx, arr) =>
          arr.findIndex(
            (p) =>
              p.curveNumber === point.curveNumber &&
              p.pointNumber === point.pointNumber &&
              p.subplot === point.subplot
          ) === idx
        );
        suppressSyntheticHover = true;
        if (uniquePoints.length) {{
          const fullLayout = gd._fullLayout;
          if (fullLayout && typeof fullLayout.hovermode === 'string') {{
            Plotly.Fx.hover(gd, uniquePoints, {{ hovermode: fullLayout.hovermode }});
          }} else {{
            Plotly.Fx.hover(gd, uniquePoints);
          }}
        }} else {{
          Plotly.Fx.unhover(gd);
        }}
        setTimeout(() => {{
          suppressSyntheticHover = false;
          flushPendingHover();
        }}, 0);
      }}
      function isCoarsePointerDevice() {{
        if (typeof window === 'undefined') {{
          return false;
        }}
        if (typeof window.matchMedia === 'function') {{
          try {{
            if (window.matchMedia('(pointer: coarse)').matches) {{
              return true;
            }}
          }} catch (err) {{
            // Ignore errors from matchMedia
          }}
        }}
        return 'ontouchstart' in window;
      }}
      function setupTouchHover() {{
        const root = gd;
        if (!root || typeof root.addEventListener !== 'function') {{
          return;
        }}
        let activeTouchId = null;
        let isScrubbing = false;
        let touchTargets = [];
        const DOUBLE_TAP_MS = 300;
        let lastTapTimestamp = 0;
        let doubleTapTimeoutId = null;
        const resetTapTracking = () => {{
          if (doubleTapTimeoutId) {{
            clearTimeout(doubleTapTimeoutId);
            doubleTapTimeoutId = null;
          }}
          lastTapTimestamp = 0;
        }};
        const scheduleTapReset = () => {{
          if (doubleTapTimeoutId) {{
            clearTimeout(doubleTapTimeoutId);
          }}
          doubleTapTimeoutId = setTimeout(() => {{
            doubleTapTimeoutId = null;
            lastTapTimestamp = 0;
          }}, DOUBLE_TAP_MS);
        }};
        const refreshTouchTargets = () => {{
          const fullLayout = gd._fullLayout;
          if (!fullLayout || !fullLayout._plots) {{
            touchTargets = [];
            return;
          }}
          touchTargets = Object.keys(fullLayout._plots)
            .map((subplot) => {{
              const plot = fullLayout._plots[subplot];
              if (!plot || !plot.xaxis || !plot.yaxis) {{
                return null;
              }}
              const xaxis = plot.xaxis;
              const yaxis = plot.yaxis;
              if (
                typeof xaxis._length !== 'number' ||
                xaxis._length <= 0 ||
                typeof yaxis._length !== 'number' ||
                yaxis._length <= 0
              ) {{
                return null;
              }}
              return {{ axis: xaxis, yaxis }};
            }})
            .filter((entry) => Boolean(entry));
        }};
        const findTouchTarget = (clientX, clientY) => {{
          if (!touchTargets.length) {{
            return null;
          }}
          const rootRect = root.getBoundingClientRect();
          for (const entry of touchTargets) {{
            const axis = entry.axis;
            const yaxis = entry.yaxis;
            if (!axis || !yaxis) {{
              continue;
            }}
            const left =
              rootRect.left + (typeof axis._offset === 'number' ? axis._offset : 0);
            const width = typeof axis._length === 'number' ? axis._length : 0;
            const top =
              rootRect.top + (typeof yaxis._offset === 'number' ? yaxis._offset : 0);
            const height = typeof yaxis._length === 'number' ? yaxis._length : 0;
            if (width <= 0 || height <= 0) {{
              continue;
            }}
            const right = left + width;
            const bottom = top + height;
            if (
              clientX >= left &&
              clientX <= right &&
              clientY >= top &&
              clientY <= bottom
            ) {{
              return {{
                axis,
                rect: {{ left, right, top, bottom, width, height }}
              }};
            }}
          }}
          return null;
        }};
        const computeTargetTime = (axis, rect, clientX) => {{
          if (!axis || !rect) {{
            return NaN;
          }}
          const range = axis.range || axis._range;
          if (!range || range.length < 2) {{
            return NaN;
          }}
          const start = toTimestamp(range[0]);
          const end = toTimestamp(range[1]);
          if (!Number.isFinite(start) || !Number.isFinite(end) || start === end) {{
            return NaN;
          }}
          const clamped = Math.min(Math.max(clientX, rect.left), rect.right);
          const span = rect.width || rect.right - rect.left;
          const length = span > 0 ? span : 1;
          const ratio = (clamped - rect.left) / length;
          return start + ratio * (end - start);
        }};
        const beginScrub = (touch) => {{
          const target = findTouchTarget(touch.clientX, touch.clientY);
          if (!target) {{
            return false;
          }}
          const targetTime = computeTargetTime(target.axis, target.rect, touch.clientX);
          if (!Number.isFinite(targetTime)) {{
            return false;
          }}
          applyHoverForTime(targetTime);
          return true;
        }};
        const moveScrub = (touch) => {{
          const target = findTouchTarget(touch.clientX, touch.clientY);
          if (!target) {{
            hideHighlights();
            Plotly.Fx.unhover(gd);
            return false;
          }}
          const targetTime = computeTargetTime(target.axis, target.rect, touch.clientX);
          if (!Number.isFinite(targetTime)) {{
            hideHighlights();
            Plotly.Fx.unhover(gd);
            return false;
          }}
          applyHoverForTime(targetTime);
          return true;
        }};
        const endScrub = () => {{
          isScrubbing = false;
          activeTouchId = null;
          pendingHoverState = null;
          hideHighlights();
          Plotly.Fx.unhover(gd);
        }};
        const handleTouchEnd = (event) => {{
          if (!isScrubbing || activeTouchId === null) {{
            return;
          }}
          const remaining = Array.from(event.touches || []);
          const stillActive = remaining.some((touch) => touch.identifier === activeTouchId);
          if (stillActive) {{
            return;
          }}
          if (event) {{
            event.preventDefault();
            event.stopPropagation();
            if (typeof event.stopImmediatePropagation === 'function') {{
              event.stopImmediatePropagation();
            }}
          }}
          endScrub();
        }};
        const handleDoubleTap = (event) => {{
          const now = Date.now();
          if (lastTapTimestamp && now - lastTapTimestamp <= DOUBLE_TAP_MS) {{
            resetTapTracking();
            endScrub();
            hideHighlights();
            Plotly.Fx.unhover(gd);
            resetToInitialView();
            if (event) {{
              event.preventDefault();
              event.stopPropagation();
              if (typeof event.stopImmediatePropagation === 'function') {{
                event.stopImmediatePropagation();
              }}
            }}
            return true;
          }}
          lastTapTimestamp = now;
          scheduleTapReset();
          return false;
        }};
        refreshTouchTargets();
        gd.on('plotly_afterplot', refreshTouchTargets);
        gd.on('plotly_relayout', refreshTouchTargets);
        gd.on('plotly_update', refreshTouchTargets);
        if (typeof window !== 'undefined') {{
          window.addEventListener('resize', refreshTouchTargets);
        }}
        root.addEventListener(
          'touchstart',
          (event) => {{
            refreshTouchTargets();
            if (event.touches.length !== 1) {{
              if (isScrubbing) {{
                endScrub();
              }}
              resetTapTracking();
              return;
            }}
            const touch = event.touches[0];
            if (handleDoubleTap(event)) {{
              return;
            }}
            const started = beginScrub(touch);
            if (started) {{
              activeTouchId = touch.identifier;
              isScrubbing = true;
              event.preventDefault();
              event.stopPropagation();
              if (typeof event.stopImmediatePropagation === 'function') {{
                event.stopImmediatePropagation();
              }}
            }} else {{
              isScrubbing = false;
              activeTouchId = null;
            }}
          }},
          {{ passive: false }}
        );
        root.addEventListener(
          'touchmove',
          (event) => {{
            if (!isScrubbing || activeTouchId === null) {{
              return;
            }}
            const touches = Array.from(event.touches || []);
            const touch = touches.find((item) => item.identifier === activeTouchId);
            if (!touch) {{
              return;
            }}
            const moved = moveScrub(touch);
            if (moved) {{
              event.preventDefault();
              event.stopPropagation();
              if (typeof event.stopImmediatePropagation === 'function') {{
                event.stopImmediatePropagation();
              }}
            }}
          }},
          {{ passive: false }}
        );
        root.addEventListener('touchend', handleTouchEnd);
        root.addEventListener('touchcancel', handleTouchEnd);
      }}
      addHighlights.then(() => {{
        if (!highlightTraces.length) {{
          return;
        }}
        gd.on('plotly_hover', (event) => {{
          if (suppressSyntheticHover) {{
            queuePendingHover(event.points, Boolean(event.event));
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
          applyHoverForTime(targetTime);
        }});
        gd.on('plotly_unhover', (event) => {{
          if (suppressSyntheticHover) {{
            queuePendingHover(null, Boolean(event && event.event));
            return;
          }}
          pendingHoverState = null;
          hideHighlights();
          if (event && event.event) {{
            Plotly.Fx.unhover(gd);
          }}
        }});
        if (isCoarsePointerDevice()) {{
          setupTouchHover();
        }}
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
