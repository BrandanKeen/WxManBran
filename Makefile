.PHONY: helene

helene: tabs/data/datasets/2024-hurricane-helene/specs/2024-hurricane-helene.json
	mkdir -p tabs/data/datasets/2024-hurricane-helene/plots
	python tabs/data/pipeline/build_interactive_from_spec.py --csv tabs/data/datasets/2024-hurricane-helene/raw/Hurricane_Helene_Plot_Data.csv --spec tabs/data/datasets/2024-hurricane-helene/specs/2024-hurricane-helene.json --out tabs/data/datasets/2024-hurricane-helene/plots/
	python tabs/data/pipeline/embed_plots_in_storm_page.py --spec tabs/data/datasets/2024-hurricane-helene/specs/2024-hurricane-helene.json --storm-md tabs/previous-storms/_storms/2024-hurricane-helene.md --public-dir tabs/data/datasets/2024-hurricane-helene/plots/

tabs/data/datasets/2024-hurricane-helene/specs/2024-hurricane-helene.json: tabs/data/datasets/2024-hurricane-helene/notebooks/Hurricane_Helene_Analysis.ipynb | tabs/data/datasets/2024-hurricane-helene/specs
	python tabs/data/pipeline/parse_notebook_plots.py $< > $@

tabs/data/datasets/2024-hurricane-helene/specs:
	mkdir -p tabs/data/datasets/2024-hurricane-helene/specs
