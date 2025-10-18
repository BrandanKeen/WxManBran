#!/usr/bin/env python3
"""Automate the end-to-end plot generation pipeline for storm datasets."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "storms"
NOTEBOOKS_DIR = ROOT / "analysis" / "notebooks"
SPECS_DIR = ROOT / "build" / "specs"
PLOTS_DIR = ROOT / "assets" / "plots"
STORMS_DIR = ROOT / "_storms"
SCRIPTS_DIR = ROOT / "scripts"

MARKER_START = "<!-- DATA-SECTION:START -->"
MARKER_END = "<!-- DATA-SECTION:END -->"


class StormProcessingError(RuntimeError):
    """Raised when a storm cannot be processed."""


def slug_to_title(slug: str) -> str:
    parts = slug.split("-")
    if len(parts) <= 1:
        return slug.replace("-", " ").title()

    words = [part.replace("_", " ") for part in parts[1:]]
    title_words = [w.capitalize() for w in words]
    return " ".join(title_words)


def slug_to_permalink(slug: str) -> str:
    parts = slug.split("-")
    if len(parts) <= 1:
        return f"/storms/{slug}/"
    year, *rest = parts
    rest_slug = "-".join(rest)
    return f"/storms/{rest_slug}-{year}/"


def slug_to_season(slug: str) -> str:
    year = slug.split("-", 1)[0]
    return year if year.isdigit() else "TBD"


def default_sort_date(season: str) -> str:
    if season.isdigit() and len(season) == 4:
        return f"{season}-01-01"
    return "1970-01-01"


def ensure_storm_container(slug: str) -> Path:
    path = STORMS_DIR / f"{slug}.md"
    season = slug_to_season(slug)
    title = slug_to_title(slug)
    permalink = slug_to_permalink(slug)
    sort_date = default_sort_date(season)

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        template = dedent(
            f"""\
            ---
            layout: default
            title: {title}
            season: {season}
            landfall: TBD
            permalink: {permalink}
            sort_date: {sort_date}
            overview: >-
              TBD.
            ---

            # {title} ({season})

            SummaryComingSoon

            ## Overview

            OverviewComingSoon

            ## Timeline

            TimelineComingSoon

            ## Impacts

            ImpactsComingSoon

            ## Media

            MediaComingSoon

            ## Data

            DataComingSoon

            {MARKER_START}
            {MARKER_END}
            """
        ).strip("\n") + "\n"
        # Ensure markers are on their own lines without indentation.
        template = template.replace(MARKER_START, f"{MARKER_START}")
        template = template.replace(MARKER_END, f"{MARKER_END}")
        path.write_text(template, encoding="utf-8")
    else:
        text = path.read_text(encoding="utf-8")
        if MARKER_START not in text or MARKER_END not in text:
            addition = dedent(
                f"""\

                ## Data

                DataComingSoon

                {MARKER_START}
                {MARKER_END}
                """
            )
            path.write_text((text.rstrip("\n") + addition + "\n"), encoding="utf-8")

    return path


def find_notebook(slug: str) -> Path:
    nb_dir = NOTEBOOKS_DIR / slug
    if not nb_dir.exists():
        raise StormProcessingError(f"Notebook directory not found: {nb_dir}")
    notebooks = sorted(nb_dir.glob("*.ipynb"))
    if not notebooks:
        raise StormProcessingError(f"No notebooks found in {nb_dir}")
    return notebooks[0]


def find_csv(slug: str) -> Path:
    csv_dir = DATA_DIR / slug
    if not csv_dir.exists():
        raise StormProcessingError(f"CSV directory not found: {csv_dir}")
    preferred = sorted(csv_dir.glob("*Plot_Data.csv"))
    if preferred:
        return preferred[0]
    csvs = sorted(csv_dir.glob("*.csv"))
    if not csvs:
        raise StormProcessingError(f"No CSV files found in {csv_dir}")
    return csvs[0]


def run_parse(notebook: Path, spec: Path) -> None:
    spec.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "parse_notebook_plots.py"),
            str(notebook),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    spec.write_text(result.stdout, encoding="utf-8")


def run_build(csv_path: Path, spec: Path, public_dir: Path) -> None:
    public_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "build_interactive_from_spec.py"),
            "--csv",
            str(csv_path),
            "--spec",
            str(spec),
            "--out",
            str(public_dir),
        ],
        check=True,
    )


def run_build_static(csv_path: Path, spec: Path, public_dir: Path) -> None:
    public_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "build_static_from_spec.py"),
            "--csv",
            str(csv_path),
            "--spec",
            str(spec),
            "--out",
            str(public_dir),
        ],
        check=True,
    )


def run_embed(spec: Path, storm_md: Path, public_dir: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(SCRIPTS_DIR / "embed_plots_in_storm_page.py"),
            "--spec",
            str(spec),
            "--storm-md",
            str(storm_md),
            "--public-dir",
            str(public_dir.relative_to(ROOT)),
        ],
        check=True,
    )


def process_storm(slug: str) -> None:
    print(f"Processing {slug}...")
    storm_md = ensure_storm_container(slug)
    notebook = find_notebook(slug)
    csv_path = find_csv(slug)
    spec_path = SPECS_DIR / f"{slug}.json"
    public_dir = PLOTS_DIR / slug

    run_parse(notebook, spec_path)
    run_build(csv_path, spec_path, public_dir)
    run_build_static(csv_path, spec_path, public_dir)
    run_embed(spec_path, storm_md, public_dir)
    print(f"Completed {slug}.")


def discover_slugs() -> list[str]:
    if not DATA_DIR.exists():
        return []
    return sorted(p.name for p in DATA_DIR.iterdir() if p.is_dir())


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate interactive plots for storms.")
    parser.add_argument(
        "--slug",
        action="append",
        dest="slugs",
        help="Storm slug to process (e.g., 2024-hurricane-helene). Can be repeated.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all storms that have data and notebooks available.",
    )
    args = parser.parse_args()

    if args.slugs and args.all:
        parser.error("--slug and --all cannot be used together")

    if args.slugs:
        slugs = args.slugs
    else:
        slugs = discover_slugs()

    if not slugs:
        print("No storms found to process.")
        return 0

    exit_code = 0
    for slug in slugs:
        try:
            process_storm(slug)
        except StormProcessingError as exc:
            print(f"Skipping {slug}: {exc}", file=sys.stderr)
            exit_code = 1
        except subprocess.CalledProcessError as exc:
            print(f"Error processing {slug}: {exc}", file=sys.stderr)
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
