"""Figures that need model predictions: two-stage walkthrough, coverage agreement, tomato examples."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

SUB = Path.home() / "Desktop/final-submission"
REPO = SUB / "instancesegmentation"
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inference import load_image, overlay, predict  # noqa: E402
from build_figures import COL, DATA, DEFECTS, FIG, HEX, INK, MUTED, SHORT, clean_axes, read_labels  # noqa: E402
from ultralytics import YOLO  # noqa: E402

OUT = REPO / "runs/test_per_image_predictions.json"
MODELS = {"apple": ("apple_stage1.pt", "apple_stage2.pt"), "tomato": ("tomato_stage1.pt", "tomato_stage2.pt")}
NEAR_DUP = set(json.loads((REPO / "runs/run22_stage2_yolo26l/final_test/near_duplicate_test_images.json")
                          .read_text())["near_dup_test"])


def raster(items, w, h, keep):
    out = {}
    for cls, xy in items:
        if cls not in keep:
            continue
        canvas = Image.new("L", (w, h), 0)
        ImageDraw.Draw(canvas).polygon([(float(x * w), float(y * h)) for x, y in xy], fill=1)
        out[cls] = out.get(cls, np.zeros((h, w), bool)) | np.array(canvas, bool)
    return out


def evaluate(conf=0.25):
    rows = []
    for fruit, (s1, s2) in MODELS.items():
        fm, dm = YOLO(str(REPO / "models" / s1)), YOLO(str(REPO / "models" / s2))
        for img_path, items in read_labels(fruit, "test"):
            image = load_image(img_path)
            h, w = image.shape[:2]
            pred = predict(dm, image, conf=conf, fruit_model=fm)
            gt = raster(items, w, h, DEFECTS + ["fruit"])
            gt_fruit = gt.pop("fruit", None)
            pr = {}
            for d in pred.detections:
                pr[d.class_name] = pr.get(d.class_name, np.zeros((h, w), bool)) | d.mask
            gt_union = np.logical_or.reduce(list(gt.values())) if gt else np.zeros((h, w), bool)
            pr_union = np.logical_or.reduce(list(pr.values())) if pr else np.zeros((h, w), bool)
            gt_cov = 100 * (gt_union & gt_fruit).sum() / gt_fruit.sum() if gt_fruit is not None and gt_fruit.sum() else None
            pf = pred.fruit_mask
            pr_cov = 100 * (pr_union & pf).sum() / pf.sum() if pf is not None and pf.sum() else None
            ious = []
            for c in set(gt) | set(pr):
                a, b = gt.get(c, np.zeros((h, w), bool)), pr.get(c, np.zeros((h, w), bool))
                ious.append((a & b).sum() / max(1, (a | b).sum()))
            rows.append({"fruit": fruit, "file": img_path.name, "gt_classes": sorted(gt), "pred_classes": sorted(pr),
                         "gt_cov": gt_cov, "pred_cov": pr_cov, "iou": float(np.mean(ious)) if gt else None,
                         "near_dup": img_path.name in NEAR_DUP})
        print(fruit, "done")
    OUT.write_text(json.dumps(rows, indent=1))
    return rows


def fig_coverage(rows):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), dpi=200)
    for ax, fruit in zip(axes, ("apple", "tomato")):
        r = [x for x in rows if x["fruit"] == fruit and x["gt_cov"] is not None and x["pred_cov"] is not None]
        g = np.array([x["gt_cov"] for x in r])
        p = np.array([x["pred_cov"] for x in r])
        nd = np.array([x["near_dup"] for x in r])
        ax.scatter(g, p, s=22, color="#2E7D32" if fruit == "apple" else "#C0392B", alpha=0.75,
                   label="Test image")
        lim = max(5, g.max(), p.max()) * 1.05
        ax.plot([0, lim], [0, lim], color=MUTED, lw=1, ls="--")
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        rr = np.corrcoef(g, p)[0, 1]
        mae = np.abs(g - p).mean()
        ax.set_title(f"{fruit.capitalize()} test ({len(r)} images)   r = {rr:.2f}   MAE = {mae:.1f} pts",
                     loc="left", fontsize=10.5)
        ax.set_xlabel("Labeled defect area, % of labeled fruit")
        ax.set_ylabel("Predicted defect area, % of Stage 1 fruit")
        clean_axes(ax)
        ax.grid(axis="x", color="#D9DEE3", linewidth=0.6)
        ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    fig.text(0.01, 0.005, "Each point is one test image. Dashed line is perfect agreement. Confidence 0.25.",
             fontsize=8.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "coverage_agreement.png")
    plt.close(fig)


def gt_overlay(img_path, fruit):
    items = dict(read_labels(fruit, "test"))[img_path] if False else None
    return items


def side_by_side(fruit, picks, out_name, title):
    lab = {p.name: items for p, items in read_labels(fruit, "test")}
    fm, dm = (YOLO(str(REPO / "models" / m)) for m in MODELS[fruit])
    from build_figures import draw_polys, square
    n = len(picks)
    fig, axes = plt.subplots(2, n, figsize=(2.6 * n, 5.6), dpi=170)
    for j, (name, note) in enumerate(picks):
        path = DATA[fruit] / "test/images" / name
        img = Image.open(path)
        gt = draw_polys(img, [(c, xy) for c, xy in lab[name] if c != "fruit"])
        pred = predict(dm, load_image(path), conf=0.25, fruit_model=fm)
        pv = Image.fromarray(overlay(pred, {c: True for c in DEFECTS}, alpha=0.45, show_fruit=False))
        for i, im in enumerate((gt, pv)):
            ax = axes[i, j]
            ax.imshow(square(im, 360))
            ax.set_xticks([])
            ax.set_yticks([])
            for s in ax.spines.values():
                s.set_color("#D9DEE3")
        axes[0, j].set_title(note, fontsize=9, color=INK)
    axes[0, 0].set_ylabel("Team label", fontsize=11)
    axes[1, 0].set_ylabel("Model", fontsize=11)
    handles = [plt.Rectangle((0, 0), 1, 1, color=HEX[c]) for c in DEFECTS]
    fig.legend(handles, [SHORT[c] for c in DEFECTS], loc="lower center", ncol=3, frameon=False, fontsize=9)
    fig.suptitle(title, x=0.01, ha="left", fontsize=11.5, color=INK)
    fig.tight_layout(rect=(0, 0.05, 1, 0.95))
    fig.savefig(FIG / out_name)
    plt.close(fig)


def fig_tomato_examples(rows):
    t = [x for x in rows if x["fruit"] == "tomato" and x["iou"] is not None]
    t.sort(key=lambda x: -x["iou"])
    good = [(x["file"], f"IoU {x['iou']:.2f}") for x in t[:3]]
    bad = [(x["file"], "Missed" if not x["pred_classes"] else f"IoU {x['iou']:.2f}") for x in t[-3:]]
    side_by_side("tomato", good + bad, "tomato_examples.png",
                 "Tomato test images: three best (left) and three worst (right) by defect IoU")


def fig_two_stage():
    cases = [("apple", REPO / "app/samples/apple/rot_b.jpg"), ("tomato", REPO / "app/samples/tomato/surface_a.jpg")]
    fig, axes = plt.subplots(2, 4, figsize=(12, 6.4), dpi=170)
    from build_figures import square
    for r, (fruit, path) in enumerate(cases):
        fm, dm = (YOLO(str(REPO / "models" / m)) for m in MODELS[fruit])
        image = load_image(path)
        pred = predict(dm, image, conf=0.25, fruit_model=fm)
        base = Image.fromarray(image)
        fruit_only = Image.fromarray(overlay(pred.__class__(image=image, fruit_mask=pred.fruit_mask),
                                             {}, alpha=0.4, show_fruit=True))
        if pred.fruit_mask is not None:
            arr = np.array(fruit_only).astype(float)
            arr[pred.fruit_mask] = arr[pred.fruit_mask] * 0.7 + np.array(COL["fruit"]) * 0.3
            fruit_only = Image.fromarray(arr.astype(np.uint8))
        defects_only = Image.fromarray(overlay(pred, {c: True for c in DEFECTS}, alpha=0.5, show_fruit=False))
        both = Image.fromarray(overlay(pred, {c: True for c in DEFECTS}, alpha=0.5, show_fruit=True))
        cov = 0.0
        if pred.fruit_mask is not None and pred.detections:
            u = np.logical_or.reduce([d.mask for d in pred.detections])
            cov = 100 * (u & pred.fruit_mask).sum() / pred.fruit_mask.sum()
        titles = ["Input photo", f"Stage 1: {pred.fruit_name or fruit} mask",
                  "Stage 2: defect masks", f"Output: {cov:.1f}% of fruit damaged"]
        for c, im in enumerate((base, fruit_only, defects_only, both)):
            ax = axes[r, c]
            ax.imshow(square(im, 380))
            ax.axis("off")
            ax.set_title(titles[c], fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(FIG / "two_stage_example.png")
    plt.close(fig)


if __name__ == "__main__":
    what = sys.argv[1:] or ["eval", "coverage", "tomato", "two_stage"]
    rows = json.loads(OUT.read_text()) if OUT.exists() and "eval" not in what else None
    if "eval" in what:
        rows = evaluate()
    if "coverage" in what:
        fig_coverage(rows)
    if "tomato" in what:
        fig_tomato_examples(rows)
    if "two_stage" in what:
        fig_two_stage()
    print("done")
