.PHONY: helene

helene: build/specs/2024-hurricane-helene.json
	mkdir -p assets/plots/2024-hurricane-helene
	python scripts/build_interactive_from_spec.py --csv data/storms/2024-hurricane-helene/Hurricane_Helene_Plot_Data.csv --spec build/specs/2024-hurricane-helene.json --out assets/plots/2024-hurricane-helene/
	python scripts/embed_plots_in_storm_page.py --spec build/specs/2024-hurricane-helene.json --storm-md _storms/2024-hurricane-helene.md --public-dir assets/plots/2024-hurricane-helene/

build/specs/2024-hurricane-helene.json: analysis/notebooks/2024-hurricane-helene/Hurricane_Helene_Analysis.ipynb | build/specs
	python scripts/parse_notebook_plots.py $< > $@

build/specs:
	mkdir -p build/specs
