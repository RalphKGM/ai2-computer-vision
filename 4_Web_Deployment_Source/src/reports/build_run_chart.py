"""Bar chart of validation mask mAP50 for every run in runs/run_history.csv."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[2]
rows = list(csv.DictReader(open(REPO / "runs/run_history.csv")))
labels, values, colors = [], [], []
for r in rows:
    name = r["run"].replace(" pilot", "")
    v = r["mask_mAP50"]
    if not v and r["run"].startswith("Run 25"):
        v = (0.985 + 0.949) / 2  # mean of apple and tomato per-fruit validation
        name += " *"
    labels.append(name)
    values.append(float(v))
    if r["run"].startswith(("Run 21", "Run 22")):
        colors.append("#2E7D32")
    elif "Stage" in r["run"]:
        colors.append("#5B6F82")
    else:
        colors.append("#B8C2CC")
fig, ax = plt.subplots(figsize=(11, 6.6), dpi=200)
y = range(len(labels))[::-1]
ax.barh(list(y), values, color=colors, height=0.65)
for yi, v in zip(y, values):
    ax.text(v + 0.008, yi, f"{v:.3f}", va="center", fontsize=9)
ax.set_yticks(list(y))
ax.set_yticklabels(labels, fontsize=9.5)
ax.set_xlim(0, 1.08)
ax.set_xlabel("Validation mask mAP50", fontsize=11)
ax.set_title("Every training run from first pilot to final model", loc="left", fontsize=13, color="#1F2933")
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
fig.text(0.13, 0.01, "Grey: pilots and single-stage runs. Blue-grey: other two-stage runs (apple 26m, tomato, combined). "
         "Green: final apple two-stage YOLO26l. * mean of apple and tomato. Different datasets are not controlled "
         "comparisons.", fontsize=8, color="#52606D", wrap=True)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(REPO / "reports/figures/run_history_map50.png")
print("saved")
