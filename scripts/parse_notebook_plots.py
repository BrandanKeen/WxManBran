#!/usr/bin/env python3
import argparse
import ast
import json
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class SeriesSpec:
    label: Optional[str] = None
    column: Optional[str] = None
    color: Optional[str] = None
    linestyle: Optional[str] = None
    alpha: Optional[float] = None
    secondary_y: bool = False

    def to_dict(self) -> Dict[str, object]:
        data = {
            "label": self.label,
            "column": self.column,
            "color": self.color,
            "linestyle": self.linestyle or "-",
            "secondary_y": self.secondary_y,
        }
        if self.alpha is not None:
            data["alpha"] = self.alpha
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class AxisSpec:
    key: str
    row: int = 1
    col: int = 1
    title: Optional[str] = None
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None
    ylabel_color: Optional[str] = None
    legend_loc: Optional[str] = None
    grid: Optional[bool] = None
    yaxis_color: Optional[str] = None
    secondary: bool = False
    series: List[SeriesSpec] = field(default_factory=list)

    def add_series(self, series: SeriesSpec) -> None:
        self.series.append(series)


class FigureParser:
    def __init__(self, source: str, dataframe_names: Optional[Set[str]] = None):
        self.source = source
        self.current_fig: Optional[Dict[str, object]] = None
        self.axis_alias: Dict[str, str] = {}
        self.axis_specs: Dict[str, AxisSpec] = {}
        self.var_to_column: Dict[str, str] = {}
        self.dataframe_names: Set[str] = set(dataframe_names or {"df"})
        self.specs: List[Dict[str, object]] = []

    def normalize_axis_expr(self, expr: str) -> str:
        expr = expr.strip()
        expr = re.sub(r"\s+", "", expr)
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+),(\d+)\]", expr)
        if match:
            name, r, c = match.groups()
            return f"{name}[{r},{c}]"
        return expr

    def resolve_axis(self, expr: str) -> str:
        expr = self.normalize_axis_expr(expr)
        visited = set()
        while expr in self.axis_alias and expr not in visited:
            visited.add(expr)
            expr = self.axis_alias[expr]
        return expr

    def start_new_figure(self, call: ast.Call, axis_target: Optional[ast.AST]) -> None:
        rows = cols = 1
        sharex = False
        if call.args:
            numeric_args = [a for a in call.args if isinstance(a, ast.Constant) and isinstance(a.value, int)]
            if len(numeric_args) >= 2:
                rows = int(numeric_args[0].value)
                cols = int(numeric_args[1].value)
            elif len(numeric_args) == 1:
                rows = int(numeric_args[0].value)
                cols = 1
        for kw in call.keywords:
            if kw.arg == "sharex" and isinstance(kw.value, ast.Constant):
                sharex = bool(kw.value.value)
        self.current_fig = {
            "rows": rows,
            "cols": cols,
            "sharex": sharex,
            "title": None,
            "xlabel": None,
            "x_tickformat": None,
            "axes": self.axis_specs,
        }
        self.axis_alias = {}
        self.axis_specs = {}
        # Ensure axis target alias is registered for tuple assignments
        if isinstance(axis_target, ast.Name):
            name = axis_target.id
            self.axis_alias[name] = name

    def determine_position(self, key: str) -> (int, int):
        base = key
        if key.endswith("__secondary"):
            base = key[: -len("__secondary")]
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\[(\d+),(\d+)\]", base)
        if match:
            _, r, c = match.groups()
            return int(r) + 1, int(c) + 1
        return 1, 1

    def get_axis_spec(self, key: str) -> AxisSpec:
        key = self.normalize_axis_expr(key)
        if key not in self.axis_specs:
            secondary = key.endswith("__secondary")
            row, col = self.determine_position(key)
            spec = AxisSpec(key=key, row=row, col=col, secondary=secondary)
            if secondary:
                base_key = key[: -len("__secondary")]
                base_spec = self.get_axis_spec(base_key)
                spec.row = base_spec.row
                spec.col = base_spec.col
            self.axis_specs[key] = spec
        return self.axis_specs[key]

    def extract_df_column(self, node: ast.Subscript) -> Optional[str]:
        value = node.value
        if isinstance(value, ast.Name) and value.id in self.dataframe_names:
            slice_node = node.slice
            if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
                return slice_node.value
        return None

    def set_alias(self, name: str, value_expr: str) -> None:
        resolved = self.resolve_axis(value_expr)
        self.axis_alias[name] = self.normalize_axis_expr(resolved)

    def process_assign(self, node: ast.Assign) -> None:
        value = node.value
        # Capture df column assignments
        if isinstance(value, ast.Subscript):
            column = self.extract_df_column(value)
            if column:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.var_to_column[target.id] = column
                return
            if isinstance(value.value, ast.Call):
                self.process_call(value.value)
            base_expr = ast.get_source_segment(self.source, value)
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.set_alias(target.id, base_expr)
            return
        if isinstance(value, ast.Call):
            func = value.func
            if isinstance(func, ast.Attribute):
                callee = func.value
                if isinstance(callee, ast.Name):
                    if callee.id == "pd" and func.attr in {"read_csv", "read_excel"}:
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                self.dataframe_names.add(target.id)
                    elif callee.id in self.dataframe_names:
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                self.dataframe_names.add(target.id)
            elif isinstance(func, ast.Name) and func.id in self.dataframe_names:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.dataframe_names.add(target.id)
            if isinstance(func, ast.Attribute) and func.attr == "twinx":
                base_expr = ast.get_source_segment(self.source, func.value)
                base_key = self.resolve_axis(base_expr)
                alias_value = base_key + "__secondary"
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.axis_alias[target.id] = alias_value
                return
            if isinstance(func, ast.Attribute) and func.attr == "subplots":
                axis_target = None
                if node.targets and isinstance(node.targets[0], ast.Tuple) and len(node.targets[0].elts) >= 2:
                    axis_target = node.targets[0].elts[1]
                self.start_new_figure(value, axis_target)
                return
            self.process_call(value)
            return
        # Handle simple tuple assignment from plt.subplots without call detection (rare)

    def map_linestyle(self, value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        return value

    def parse_float(self, node: ast.AST) -> Optional[float]:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        return None

    def process_call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name):
            if func.id == "print":
                return
        if isinstance(func, ast.Attribute):
            attr = func.attr
            target_expr = ast.get_source_segment(self.source, func.value)
            if attr == "savefig":
                self.finalize_figure(node)
                return
            if attr == "suptitle":
                if self.current_fig and node.args and isinstance(node.args[0], ast.Constant):
                    self.current_fig["title"] = node.args[0].value
                return
            if attr in {"plot", "legend", "set_title", "set_ylabel", "set_xlabel", "grid", "minorticks_off", "tick_params"}:
                axis_key = self.resolve_axis(target_expr)
                axis_spec = self.get_axis_spec(axis_key)
                if attr == "plot":
                    series = SeriesSpec()
                    if len(node.args) >= 2:
                        y_arg = node.args[1]
                    elif node.args:
                        y_arg = node.args[0]
                    else:
                        y_arg = None
                    column = None
                    if isinstance(y_arg, ast.Name):
                        column = self.var_to_column.get(y_arg.id)
                    elif isinstance(y_arg, ast.Subscript):
                        column = self.extract_df_column(y_arg)
                    if column:
                        series.column = column
                    for kw in node.keywords:
                        if kw.arg == "label" and isinstance(kw.value, ast.Constant):
                            series.label = kw.value.value
                        elif kw.arg == "color" and isinstance(kw.value, ast.Constant):
                            series.color = kw.value.value
                        elif kw.arg in {"linestyle", "ls"} and isinstance(kw.value, ast.Constant):
                            series.linestyle = kw.value.value
                        elif kw.arg == "alpha":
                            alpha_val = self.parse_float(kw.value)
                            if alpha_val is not None:
                                series.alpha = alpha_val
                    if series.linestyle is None:
                        series.linestyle = "-"
                    series.secondary_y = axis_spec.secondary
                    axis_spec.add_series(series)
                elif attr == "legend":
                    for kw in node.keywords:
                        if kw.arg == "loc" and isinstance(kw.value, ast.Constant):
                            axis_spec.legend_loc = kw.value.value
                elif attr == "set_title":
                    if node.args and isinstance(node.args[0], ast.Constant):
                        axis_spec.title = node.args[0].value
                elif attr == "set_ylabel":
                    if node.args and isinstance(node.args[0], ast.Constant):
                        axis_spec.ylabel = node.args[0].value
                    for kw in node.keywords:
                        if kw.arg == "color" and isinstance(kw.value, ast.Constant):
                            axis_spec.ylabel_color = kw.value.value
                elif attr == "set_xlabel":
                    if node.args and isinstance(node.args[0], ast.Constant):
                        axis_spec.xlabel = node.args[0].value
                        if self.current_fig:
                            self.current_fig["xlabel"] = axis_spec.xlabel
                elif attr == "grid":
                    if node.args and isinstance(node.args[0], ast.Constant):
                        axis_spec.grid = bool(node.args[0].value)
                elif attr == "tick_params":
                    axis = None
                    labelcolor = None
                    for kw in node.keywords:
                        if kw.arg == "axis" and isinstance(kw.value, ast.Constant):
                            axis = kw.value.value
                        if kw.arg == "labelcolor" and isinstance(kw.value, ast.Constant):
                            labelcolor = kw.value.value
                    if axis == "y" and labelcolor:
                        axis_spec.yaxis_color = labelcolor
                return
            if attr == "set_major_formatter":
                formatter_call = node.args[0] if node.args else None
                if isinstance(formatter_call, ast.Call) and isinstance(formatter_call.func, ast.Attribute):
                    fmt_args = formatter_call.args
                    if fmt_args and isinstance(fmt_args[0], ast.Constant):
                        if self.current_fig:
                            self.current_fig["x_tickformat"] = fmt_args[0].value
                return
        if isinstance(func, ast.Name) and func.id == "plt":
            return

    def finalize_figure(self, node: ast.Call) -> None:
        if not self.current_fig:
            self.current_fig = {
                "rows": 1,
                "cols": 1,
                "sharex": False,
                "title": None,
                "xlabel": None,
                "x_tickformat": None,
                "axes": self.axis_specs,
            }
        filename = None
        if node.args and isinstance(node.args[0], ast.Constant):
            filename = node.args[0].value
        if not filename:
            return
        axes_group: Dict[str, Dict[str, Optional[AxisSpec]]] = {}
        for key, axis in self.axis_specs.items():
            base_key = key[:-len("__secondary")] if axis.secondary else key
            base_key = self.normalize_axis_expr(base_key)
            group = axes_group.setdefault(base_key, {"primary": None, "secondary": None})
            if axis.secondary:
                group["secondary"] = axis
            else:
                group["primary"] = axis
        subplots = []
        for base_key, pair in axes_group.items():
            primary = pair["primary"]
            secondary = pair["secondary"]
            if not primary:
                continue
            subplot_entry = {
                "key": base_key,
                "row": primary.row,
                "col": primary.col,
                "title": primary.title,
                "xlabel": primary.xlabel,
                "ylabel": primary.ylabel,
                "legend_loc": primary.legend_loc,
                "grid": primary.grid,
                "series": [series.to_dict() for series in primary.series],
            }
            if primary.yaxis_color:
                subplot_entry["yaxis_color"] = primary.yaxis_color
            if primary.ylabel_color:
                subplot_entry["ylabel_color"] = primary.ylabel_color
            if secondary:
                subplot_entry["secondary_ylabel"] = secondary.ylabel
                if secondary.yaxis_color:
                    subplot_entry["secondary_yaxis_color"] = secondary.yaxis_color
                if secondary.ylabel_color:
                    subplot_entry["secondary_ylabel_color"] = secondary.ylabel_color
                if secondary.grid is not None:
                    subplot_entry["secondary_grid"] = secondary.grid
                subplot_entry["series"].extend([
                    {**series.to_dict(), "secondary_y": True}
                    for series in secondary.series
                ])
            subplots.append(subplot_entry)
        subplots.sort(key=lambda x: (x["row"], x["col"]))
        figure_spec = {
            "outfile": filename,
            "title": self.current_fig.get("title"),
            "xlabel": self.current_fig.get("xlabel"),
            "x_tickformat": self.current_fig.get("x_tickformat"),
        }
        unique_positions = {(s["row"], s["col"]) for s in subplots}
        figure_type = "single" if len(unique_positions) == 1 else "grid"
        figure_spec["type"] = figure_type
        if figure_type == "grid":
            figure_spec["rows"] = self.current_fig.get("rows", 1)
            figure_spec["cols"] = self.current_fig.get("cols", 1)
            figure_spec["sharex"] = self.current_fig.get("sharex", False)
            figure_spec["subplots"] = subplots
        else:
            subplot = subplots[0] if subplots else {}
            if not figure_spec.get("title") and subplot.get("title"):
                figure_spec["title"] = subplot.get("title")
            figure_spec.update({
                "ylabel": subplot.get("ylabel"),
                "legend_loc": subplot.get("legend_loc"),
                "grid": subplot.get("grid"),
                "series": subplot.get("series", []),
                "yaxis_color": subplot.get("yaxis_color"),
                "ylabel_color": subplot.get("ylabel_color"),
            })
            if subplot.get("secondary_ylabel"):
                figure_spec["secondary_ylabel"] = subplot.get("secondary_ylabel")
            if subplot.get("secondary_yaxis_color"):
                figure_spec["secondary_yaxis_color"] = subplot.get("secondary_yaxis_color")
            if subplot.get("secondary_grid") is not None:
                figure_spec["secondary_grid"] = subplot.get("secondary_grid")
        self.specs.append(figure_spec)
        # Reset state for next figure
        self.current_fig = None
        self.axis_alias = {}
        self.axis_specs = {}
        self.var_to_column = {}

    def process_node(self, node: ast.AST) -> None:
        if isinstance(node, ast.Assign):
            self.process_assign(node)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            self.process_call(node.value)
        elif isinstance(node, ast.For):
            self.process_for(node)
        elif isinstance(node, ast.AugAssign):
            return

    def process_for(self, node: ast.For) -> None:
        if not isinstance(node.target, ast.Name):
            return
        iter_values: List[str] = []
        if isinstance(node.iter, (ast.List, ast.Tuple)):
            for elt in node.iter.elts:
                expr = ast.get_source_segment(self.source, elt)
                if expr:
                    iter_values.append(expr)
        if not iter_values:
            return
        loop_var = node.target.id
        original_alias = self.axis_alias.get(loop_var)
        for expr in iter_values:
            self.axis_alias[loop_var] = self.normalize_axis_expr(expr)
            for stmt in node.body:
                self.process_node(stmt)
        if original_alias is not None:
            self.axis_alias[loop_var] = original_alias
        else:
            self.axis_alias.pop(loop_var, None)

    def parse(self) -> List[Dict[str, object]]:
        try:
            tree = ast.parse(self.source)
        except SyntaxError:
            return []
        for stmt in tree.body:
            self.process_node(stmt)
        return self.specs


def load_notebook(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        notebook = json.load(f)
    lines: List[str] = []
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        cell_source = cell.get("source", [])
        cleaned_lines = []
        for line in cell_source:
            if line.lstrip().startswith("%"):
                cleaned_lines.append("\n")
            else:
                cleaned_lines.append(line)
        lines.append("".join(cleaned_lines))
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse notebook Matplotlib plots into a spec")
    parser.add_argument("notebook", help="Path to the .ipynb notebook")
    args = parser.parse_args()

    cell_sources = load_notebook(args.notebook)
    all_specs: List[Dict[str, object]] = []
    known_dataframes: Set[str] = {"df"}
    for source in cell_sources:
        figure_parser = FigureParser(source, dataframe_names=known_dataframes)
        specs = figure_parser.parse()
        all_specs.extend(specs)
        known_dataframes.update(figure_parser.dataframe_names)
    json.dump(all_specs, fp=os.fdopen(os.dup(1), "w"), indent=2)


if __name__ == "__main__":
    main()
