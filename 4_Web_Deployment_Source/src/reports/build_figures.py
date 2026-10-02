"""Paper and slide figures built from the datasets, run logs and final metrics."""
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]
SUB = REPO.parent  # folder that also holds dataset/ and from-drive/
FIG = REPO / "reports/figures"
SCR = Path(__file__).resolve().parent
M = json.loads((REPO / "runs/final_metrics.json").read_text())
DATA = {"apple": SUB / "dataset/apple-sep30-fruit9", "tomato": SUB / "dataset/tomato-sep29-source-oct01"}
DEFECTS = ["bruise_discoloration", "rot_mold_decay", "surface_damage"]
SHORT = {"bruise_discoloration": "Bruise", "rot_mold_decay": "Rot", "surface_damage": "Surface"}
COL = {"bruise_discoloration": (230, 159, 0), "rot_mold_decay": (204, 121, 167), "surface_damage": (0, 114, 178),
       "fruit": (0, 158, 115)}
HEX = {k: "#%02x%02x%02x" % v for k, v in COL.items()}
INK, MUTED, GRID = "#1F2933", "#52606D", "#D9DEE3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK})


def clean_axes(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def read_labels(fruit, split):
    """Yield (image_path, [(class_name, polygon_xy_normalized)]) for one split."""
    root = DATA[fruit]
    import yaml
    names = yaml.safe_load((root / "data.yaml").read_text())["names"]
    names = names if isinstance(names, list) else [names[i] for i in sorted(names)]
    for img in sorted((root / split / "images").glob("*")):
        lab = root / split / "labels" / (img.stem + ".txt")
        items = []
        if lab.exists():
            for line in lab.read_text().splitlines():
                p = line.split()
                if len(p) >= 7:
                    cls = names[int(p[0])]
                    items.append(("fruit" if cls in ("apple", "tomato") else cls, np.array(p[1:], float).reshape(-1, 2)))
        yield img, items


def poly_area(xy):
    x, y = xy[:, 0], xy[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def draw_polys(img, items, alpha=0.45, width=None):
    im = img.convert("RGB")
    w, h = im.size
    over = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    lw = width or max(2, round(min(w, h) / 160))
    for cls, xy in items:
        pts = [(float(x * w), float(y * h)) for x, y in xy]
        if cls == "fruit":
            d.line(pts + [pts[0]], fill=COL["fruit"] + (255,), width=lw)
        else:
            d.polygon(pts, fill=COL[cls] + (int(255 * alpha),))
            d.line(pts + [pts[0]], fill=COL[cls] + (255,), width=lw)
    return Image.alpha_composite(im.convert("RGBA"), over).convert("RGB")


def square(img, size=420):
    w, h = img.size
    s = min(w, h)
    img = img.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    return img.resize((size, size), Image.LANCZOS)


# 1. Pipeline diagram ---------------------------------------------------------------------------
def fig_pipeline():
    steps = [
        ("Image sources", "AFruitDB apple\nand tomato, Lab2Wild,\nteam photos"),
        ("Pixel masks", "Polygons drawn\nin Roboflow.\nEvery mask reviewed"),
        ("Frozen splits", "By capture group.\nNo exact copies\nacross splits"),
        ("Stage 1", "YOLO26l-seg learns\nthe whole fruit\n(SGD, lr 0.001)"),
        ("Stage 2", "Starts from Stage 1.\nLearns 3 defects\n(AdamW, lr 0.0005)"),
        ("Unseen test", "Run once per model\nafter freezing.\nPer class, per fruit"),
        ("Streamlit app", "Upload a photo.\nMasks, coverage,\nfruit name"),
    ]
    fig, ax = plt.subplots(figsize=(13, 2.7), dpi=200)
    ax.set_xlim(0, len(steps) * 1.9)
    ax.set_ylim(0, 2.4)
    ax.axis("off")
    for i, (head, body) in enumerate(steps):
        x = i * 1.9 + 0.1
        accent = i in (3, 4)
        box = FancyBboxPatch((x, 0.15), 1.6, 2.0, boxstyle="round,pad=0.02,rounding_size=0.06",
                             linewidth=1.4, edgecolor="#2E7D32" if accent else MUTED,
                             facecolor="#EAF4EA" if accent else "#F5F7FA")
        ax.add_patch(box)
        ax.text(x + 0.8, 1.85, head, ha="center", va="center", fontsize=11, fontweight="bold", color=INK)
        ax.text(x + 0.8, 0.95, body, ha="center", va="center", fontsize=8.6, color=INK, linespacing=1.35)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 1.88, 1.15), xytext=(x + 1.62, 1.15),
                        arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.4))
    fig.tight_layout()
    fig.savefig(FIG / "pipeline.png")
    plt.close(fig)


# 2. Defect gallery from team labels ------------------------------------------------------------
def dhash(path):
    """Colour histogram signature. Unlike a difference hash it ignores rotation."""
    a = np.asarray(Image.open(path).convert("RGB").resize((96, 96)), dtype=np.int32) // 32
    h = np.bincount((a[..., 0] * 64 + a[..., 1] * 8 + a[..., 2]).ravel(), minlength=512).astype(float)
    return h / h.sum()


def fig_gallery(per_cell=2):
    picks = {}
    chosen_hashes = []
    for fruit in ("apple", "tomato"):
        rows = list(read_labels(fruit, "train"))
        group_of = {r["file"]: r["capture_group"] for r in json.loads((DATA[fruit] / "manifest.json").read_text())}
        seen_groups = set()
        for cls in DEFECTS + ["none"]:
            cands = []
            for img, items in rows:
                defects = {c for c, _ in items if c != "fruit"}
                if cls == "none":
                    if not defects and any(c == "fruit" for c, _ in items):
                        cands.append((0, img, items))
                elif defects == {cls}:
                    area = sum(poly_area(xy) for c, xy in items if c == cls)
                    cands.append((area, img, items))
            cands.sort(key=lambda t: -t[0])
            chosen = []
            # skip Roboflow variants of the same photo
            start = {"rot_mold_decay": len(cands) // 2, "none": 0}.get(cls, len(cands) // 4)
            for _, img, items in cands[start:]:
                stem = group_of.get(img.name, img.name.split(".rf.")[0])
                if stem in seen_groups:
                    continue
                origin = "__".join(img.name.split("__")[:2])
                if cls != "none" and any(origin == "__".join(c.name.split("__")[:2]) for c, _ in chosen):
                    continue
                h = dhash(img)
                if any(np.minimum(h, o).sum() >= 0.6 for o in chosen_hashes):
                    continue
                seen_groups.add(stem)
                chosen_hashes.append(h)
                chosen.append((img, items))
                if len(chosen) == per_cell:
                    break
            picks[(fruit, cls)] = chosen
    cols = DEFECTS + ["none"]
    titles = ["Bruise or discoloration", "Rot mold or decay", "Surface damage", "No defect (fruit outline only)"]
    nrows = 2 * per_cell
    fig, axes = plt.subplots(nrows, 4, figsize=(11, 2.8 * nrows), dpi=170)
    for r in range(nrows):
        fruit = "apple" if r < per_cell else "tomato"
        k = r % per_cell
        for c, cls in enumerate(cols):
            ax = axes[r, c]
            ax.axis("off")
            got = picks[(fruit, cls)]
            if k < len(got):
                img, items = got[k]
                ax.imshow(square(draw_polys(Image.open(img), items)))
            if r == 0:
                ax.set_title(titles[c], fontsize=10.5, color=INK)
            if c == 0:
                ax.text(-0.06, 0.5, fruit.capitalize(), transform=ax.transAxes, rotation=90, ha="right",
                        va="center", fontsize=12, fontweight="bold", color=INK)
    fig.text(0.5, 0.005, "Team-drawn masks on training images. Green outline is the whole-fruit mask (Stage 1). "
             "Filled regions are defect masks (Stage 2).", ha="center", fontsize=9, color=MUTED)
    fig.tight_layout(rect=(0.02, 0.02, 1, 1))
    fig.savefig(FIG / "defect_gallery.png")
    plt.close(fig)


# 3. Class and size distribution ----------------------------------------------------------------
def fig_distribution():
    splits = [("train", "Train"), ("valid", "Val"), ("test", "Test")]
    counts = {f: {s: {c: 0 for c in DEFECTS} for s, _ in splits} for f in DATA}
    sizes = {f: {c: [] for c in DEFECTS} for f in DATA}
    for fruit in DATA:
        for s, _ in splits:
            for img, items in read_labels(fruit, s):
                fruit_area = sum(poly_area(xy) for c, xy in items if c == "fruit") or None
                for c, xy in items:
                    if c in DEFECTS:
                        counts[fruit][s][c] += 1
                        if s == "train" and fruit_area:
                            sizes[fruit][c].append(100 * poly_area(xy) / fruit_area)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8), dpi=200, gridspec_kw={"width_ratios": [1, 1, 1.15]})
    for ax, fruit in zip(axes[:2], DATA):
        x = np.arange(len(DEFECTS))
        width = 0.26
        shades = {"train": 1.0, "valid": 0.65, "test": 0.4}
        for j, (s, lab) in enumerate(splits):
            vals = [counts[fruit][s][c] for c in DEFECTS]
            bars = ax.bar(x + (j - 1) * width, vals, width, label=lab,
                          color=[HEX[c] for c in DEFECTS], alpha=shades[s], edgecolor="white")
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width() / 2, v, str(v), ha="center", va="bottom", fontsize=7.5)
        ax.set_xticks(x)
        ax.set_xticklabels([SHORT[c] for c in DEFECTS])
        ax.set_title(f"{fruit.capitalize()}: defect masks per split", fontsize=11, loc="left")
        ax.set_ylabel("Masks")
        clean_axes(ax)
        from matplotlib.patches import Patch
        ax.legend(handles=[Patch(color="#5B6F82", alpha=shades[s], label=lab) for s, lab in splits],
                  frameon=False, fontsize=8)
    ax = axes[2]
    data, labels, colors = [], [], []
    for fruit in DATA:
        for c in DEFECTS:
            data.append(sizes[fruit][c])
            labels.append(f"{fruit[0].upper()} {SHORT[c]}")
            colors.append(HEX[c])
    bp = ax.boxplot(data, patch_artist=True, showfliers=False, widths=0.6)
    for patch, col in zip(bp["boxes"], colors):
        patch.set_facecolor(col)
        patch.set_alpha(0.75)
    for med in bp["medians"]:
        med.set_color(INK)
    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8.5)
    ax.set_ylabel("Mask area, % of fruit")
    ax.set_title("Defect size relative to the fruit (train)", fontsize=11, loc="left")
    clean_axes(ax)
    fig.tight_layout()
    fig.savefig(FIG / "class_distribution.png")
    plt.close(fig)
    return counts, {f: {c: float(np.median(v)) for c, v in d.items()} for f, d in sizes.items()}


# 4. Learning curves from the training logs -----------------------------------------------------
def parse_log(nb_path):
    nb = json.loads(Path(nb_path).read_text())
    t = "".join("".join(o.get("text", "")) for c in nb["cells"] for o in c.get("outputs", []))
    t = re.sub(r"\x1b\[K", "", t)
    val = {}
    for m in re.finditer(r"EPOCH (\d+)/\d+ VALIDATION\nMASK precision: ([\d.]+)% \| recall: ([\d.]+)% \| "
                         r"mAP50: ([\d.]+)% \| mAP50-95: ([\d.]+)%", t):
        val[int(m.group(1))] = [float(m.group(i)) / 100 for i in range(2, 6)]
    loss = {}
    for m in re.finditer(r"^\s+(\d+)/\d+\s+[\d.]+G\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+[\d.]+\s+[\d.]+\s+\d+\s+864: 100%",
                         t, re.M):
        loss[int(m.group(1))] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
    return val, loss


def fig_learning():
    runs = [("Run 22: apple Stage 2", SUB / "from-drive/colab_final.ipynb", "#2E7D32"),
            ("Run 26: combined Stage 2", SUB / "from-drive/colab_final_with_tests.ipynb", "#5B6F82")]
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), dpi=200)
    for name, path, color in runs:
        val, loss = parse_log(path)
        ep = sorted(val)
        m50 = [val[e][2] for e in ep]
        m95 = [val[e][3] for e in ep]
        axes[0].plot(ep, m50, color=color, lw=1.4, label=name)
        best = ep[int(np.argmax(m50))]
        axes[0].scatter([best], [max(m50)], color=color, s=22, zorder=3)
        axes[1].plot(ep, m95, color=color, lw=1.4, label=name)
        le = sorted(loss)
        axes[2].plot(le, [loss[e][1] for e in le], color=color, lw=1.4, label=f"{name.split(':')[0]} seg loss")
        axes[2].plot(le, [loss[e][2] for e in le], color=color, lw=1.0, ls="--", label=f"{name.split(':')[0]} cls loss")
    axes[0].set_title("Validation mask mAP50", loc="left", fontsize=11)
    axes[1].set_title("Validation mask mAP50-95", loc="left", fontsize=11)
    axes[2].set_title("Training loss", loc="left", fontsize=11)
    axes[2].set_yscale("log")
    for ax in axes:
        ax.set_xlabel("Epoch")
        clean_axes(ax)
    axes[0].legend(frameon=False, fontsize=8.5)
    axes[2].legend(frameon=False, fontsize=7.5, ncol=1)
    fig.text(0.01, 0.005, "Values logged during training. Dot marks the highest validation mAP50. The saved best.pt is chosen by "
             "fitness (mostly mAP50-95), so final validation numbers differ slightly.", fontsize=8.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(FIG / "learning_curves.png")
    plt.close(fig)


# 5. Validation vs test per class ---------------------------------------------------------------
def fig_val_test():
    a2, t2 = M["apple"]["stage2"], M["tomato"]["stage2"]
    clean = a2["test_without_near_duplicates"]["per_class"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.6), dpi=200, gridspec_kw={"width_ratios": [1.25, 1]})
    groups = [("Validation", "#B8C2CC"), ("Test", "#5B6F82"), ("Test, no near-duplicates", "#2E7D32")]
    x = np.arange(4)
    for ax, fruit, d in ((axes[0], "Apple (Run 22)", a2), (axes[1], "Tomato (Run 24)", t2)):
        series = [[d["validation_per_class"][c]["mAP50"] for c in DEFECTS] + [d["validation"]["mAP50"]],
                  [d["test_per_class"][c]["mAP50"] for c in DEFECTS] + [d["test"]["mAP50"]]]
        n = len(series)
        w = 0.8 / n
        for j, vals in enumerate(series):
            bars = ax.bar(x + (j - (n - 1) / 2) * w, vals, w, color=groups[j][1], label=groups[j][0])
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.2f}", ha="center", fontsize=7.5)
        ax.set_xticks(x)
        ax.set_xticklabels(["Bruise", "Rot", "Surface", "All"])
        ax.set_ylim(0, 1)
        ax.set_ylabel("Mask mAP50")
        ax.set_title(fruit, loc="left", fontsize=11)
        clean_axes(ax)
        ax.legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG / "val_vs_test.png")
    plt.close(fig)


# 6. Separate vs combined -----------------------------------------------------------------------
def fig_sep_comb():
    a2, t2, c2 = M["apple"]["stage2"], M["tomato"]["stage2"], M["apple_tomato"]["stage2"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 3.6), dpi=200, sharey=True)
    x = np.arange(4)
    for ax, fruit, sep in ((axes[0], "apple", a2), (axes[1], "tomato", t2)):
        s = [sep["test_per_class"][c]["mAP50"] for c in DEFECTS] + [sep["test"]["mAP50"]]
        cb = [c2["test_per_fruit_class"][fruit][c]["mAP50"] for c in DEFECTS] + [c2["test_per_fruit"][fruit]["mAP50"]]
        for j, (vals, lab, col) in enumerate(((s, "Separate model", "#2E7D32"), (cb, "One combined model", "#5B6F82"))):
            bars = ax.bar(x + (j - 0.5) * 0.38, vals, 0.38, color=col, label=lab)
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.2f}", ha="center", fontsize=8)
        ax.set_xticks(x)
        ax.set_xticklabels(["Bruise", "Rot", "Surface", "All"])
        ax.set_ylim(0, 1)
        ax.set_title(f"{fruit.capitalize()} test images", loc="left", fontsize=11)
        clean_axes(ax)
    axes[0].set_ylabel("Test mask mAP50")
    axes[0].legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "separate_vs_combined.png")
    plt.close(fig)


FIGURES = {"pipeline": fig_pipeline, "gallery": fig_gallery, "distribution": fig_distribution,
           "learning": fig_learning, "val_test": fig_val_test, "sep_comb": fig_sep_comb}

if __name__ == "__main__":
    for name in (sys.argv[1:] or FIGURES):
        out = FIGURES[name]()
        print("built", name, "" if out is None else out)
