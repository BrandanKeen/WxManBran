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
from typing import Dict, List, Optional


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


def load_data(csv_path: Path) -> StormData:
    times: List[str] = []
    columns: Dict[str, List[Optional[float]]] = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_time = row.get("Date Time")
            if not raw_time:
                continue
            dt = datetime.strptime(raw_time.strip(), "%m/%d/%Y %H:%M")
            times.append(dt.isoformat())
            for key, value in row.items():
                if key == "Date Time" or key is None:
                    continue
                columns.setdefault(key, []).append(parse_float(value.strip()))
    return StormData(times=times, columns=columns)


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


def build_single_figure(spec: FigureSpec, data: StormData) -> Dict[str, object]:
    traces: List[Dict[str, object]] = []
    legend_name = None
    layout: Dict[str, object] = {
        "hovermode": "x unified",
        "plot_bgcolor": "#ffffff",
        "paper_bgcolor": "#ffffff",
        "margin": {"l": 60, "r": 60, "t": 60 if spec.title else 40, "b": 60},
        "font": {"family": "Arial", "size": 12},
    }
    if spec.title:
        layout["title"] = spec.title
    if spec.legend_loc:
        legend_settings = legend_position(spec.legend_loc, [0.0, 1.0], [0.0, 1.0])
        if legend_settings:
            layout["legend"] = legend_settings
            legend_name = "legend"
    for series in spec.series or []:
        column_values = data.columns.get(series.column)
        if column_values is None:
            continue
        trace: Dict[str, object] = {
            "type": "scatter",
            "mode": "lines",
            "x": data.times,
            "y": column_values,
            "name": series.label or series.column,
            "line": {"color": series.color, "dash": map_linestyle(series.linestyle)},
            "opacity": series.alpha if series.alpha is not None else 1.0,
        }
        if series.secondary_y:
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
        "spikemode": "across",
        "spikethickness": 1,
        "spikedash": "solid",
        "spikesnap": "hovered data",
    }
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
            "spikemode": "across",
            "spikethickness": 1,
            "spikedash": "solid",
            "spikesnap": "hovered data",
        }
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
        "spikemode": "across",
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
        "hovermode": "x unified",
        "plot_bgcolor": "#ffffff",
        "paper_bgcolor": "#ffffff",
        "margin": {"l": 60, "r": 60, "t": 60 if spec.title else 40, "b": 80},
        "font": {"family": "Arial", "size": 12},
        "grid": {"rows": rows, "columns": cols, "pattern": "independent", "roworder": "top to bottom"},
    }
    if spec.title:
        layout["title"] = spec.title
    legend_count = 0
    total_axes = rows * cols
    secondary_counter = 0
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
        for series in subplot.series:
            column_values = data.columns.get(series.column)
            if column_values is None:
                continue
            trace = {
                "type": "scatter",
                "mode": "lines",
                "x": data.times,
                "y": column_values,
                "name": series.label or series.column,
                "line": {"color": series.color, "dash": map_linestyle(series.linestyle)},
                "opacity": series.alpha if series.alpha is not None else 1.0,
                "xaxis": axis_ref("x", index),
                "yaxis": axis_ref("y", index),
            }
            if series.secondary_y:
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
            "spikemode": "across",
            "spikethickness": 1,
            "spikedash": "solid",
            "spikesnap": "hovered data",
        }
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
            "spikemode": "across",
            "spikethickness": 1,
            "spikedash": "solid",
            "spikesnap": "hovered data",
        }
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
                "spikemode": "across",
                "spikethickness": 1,
                "spikedash": "solid",
                "spikesnap": "hovered data",
            }
            if subplot.secondary_grid is not None and not subplot.secondary_grid:
                secondary_axis["showgrid"] = False
            if subplot.secondary_ylabel_color:
                secondary_axis["titlefont"] = {"color": subplot.secondary_ylabel_color}
                secondary_axis["tickfont"] = {"color": subplot.secondary_ylabel_color}
            layout[secondary_name] = secondary_axis
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
        }
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
            size: 8,
            color,
            symbol: 'circle',
            line: {{ color: '#ffffff', width: 1.5 }},
            opacity: 1
          }},
          showlegend: false,
          hoverinfo: 'skip',
          xaxis: trace.xaxis,
          yaxis: trace.yaxis,
          visible: false
        }});
      }});
      const addHighlights = highlightTraces.length ? Plotly.addTraces(gd, highlightTraces) : Promise.resolve();
      const dataLookup = originalTraces.map((trace) => {{
        if (!trace.x || !trace.y) {{
          return [];
        }}
        const entries = [];
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
          entries.push({{ time: timestamp, x: xValue, y: yValue }});
        }}
        return entries;
      }});
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
          if (!event.points || !event.points.length) {{
            hideHighlights();
            return;
          }}
          const targetTime = toTimestamp(event.points[0].x);
          if (!Number.isFinite(targetTime)) {{
            hideHighlights();
            return;
          }}
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
          }});
        }});
        gd.on('plotly_unhover', () => {{
          hideHighlights();
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
