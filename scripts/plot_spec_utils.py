#!/usr/bin/env python3
"""Shared utilities for loading storm plot specifications and data."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


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
                    secondary_ylabel_color=subplot.get("secondary_ylabel_color")
                    or subplot.get("secondary_yaxis_color"),
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
        secondary_ylabel_color=entry.get("secondary_ylabel_color")
        or entry.get("secondary_yaxis_color"),
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


__all__ = [
    "FigureSpec",
    "HoverEntry",
    "ProcessedSeries",
    "SeriesEntry",
    "StormData",
    "SubplotEntry",
    "load_data",
    "load_spec",
]
