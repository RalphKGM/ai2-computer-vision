# Report figures

Scripts that build the charts and example images in `reports/figures/` from the datasets, run logs,
`runs/final_metrics.json` and the checkpoints in `models/`.

- `build_figures.py`: pipeline, defect gallery, class distribution, learning curves, validation vs test, separate vs combined
- `build_model_figures.py`: test inference for coverage agreement, tomato examples and the two-stage walkthrough
- `build_run_chart.py`: validation mAP50 of every run in `runs/run_history.csv`

Run from this folder with the project virtual environment, for example `python build_figures.py gallery`.
