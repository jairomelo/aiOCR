"""Plot WER and CER charts from evaluation JSON files."""

import argparse
import json
import re
from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from matplotlib import gridspec
from matplotlib.image import imread
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

EVALUATIONS_DIR = Path("evaluations")

MODEL_COLORS = {
    "DeepSeek-OCR":    "#4C72B0",
    "Florence-2-large":"#DD8452",
    "GLM-4.5V":        "#55A868",
    "Qwen2.5-VL-3B":   "#C44E52",
    "Qwen2.5-VL-7B":   "#8172B2",
    "Tesseract-OCR":   "#937860",
}

MODEL_SHORT = {
    "DeepSeek-OCR":    "DeepSeek",
    "Florence-2-large":"Florence-2",
    "GLM-4.5V":        "GLM-4.5V",
    "Qwen2.5-VL-3B":   "Qwen-3B",
    "Qwen2.5-VL-7B":   "Qwen-7B",
    "Tesseract-OCR":   "Tesseract",
}

DOC_META = {
    "pineda1_page_4": {
        "label": "pineda1 — page 4",
        "desc":  "Printed book (1852)\n300 DPI · PNG",
    },
    "AR_SR8V4R3_4": {
        "label": "AR_SR8V4R3 — page 4",
        "desc":  "Handwritten archival\n200 DPI · JPG\nMultispectral scan",
    },
}


def load_by_page() -> dict[str, dict[str, tuple]]:
    """Return {page: {model: (wer, cer, has_text)}}."""
    pattern = re.compile(r"^(.+?)_(.+?)_evaluation\.json$")
    data: dict = {}
    for path in sorted(EVALUATIONS_DIR.glob("*_evaluation.json")):
        m = pattern.match(path.name)
        if not m:
            continue
        model, page = m.group(1), m.group(2)
        record = json.load(path.open())
        has_text = bool(record.get("ocr", "").strip())
        data.setdefault(page, {})[model] = (record["wer"], record["cer"], has_text)
    return data


def find_image(page_key: str) -> Path | None:
    """Locate the image file for a given page key."""
    for img_dir in sorted(Path("images").iterdir()):
        if not img_dir.is_dir():
            continue
        for ext in ("png", "jpg", "jpeg"):
            candidate = img_dir / f"{page_key}.{ext}"
            if candidate.exists():
                return candidate
    return None


def load_evaluations() -> dict[str, dict[str, list[float]]]:
    """Return {model: {wer: [...], cer: [...], pages: [...]}}."""
    data: dict[str, dict] = defaultdict(lambda: {"wer": [], "cer": [], "pages": []})

    pattern = re.compile(r"^(.+?)_(.+?)_evaluation\.json$")
    for path in sorted(EVALUATIONS_DIR.glob("*_evaluation.json")):
        m = pattern.match(path.name)
        if not m:
            continue
        model, page = m.group(1), m.group(2)
        with path.open() as f:
            record = json.load(f)
        # Support both per-page (flat keys) and per-line (numbered keys) formats
        if "wer" in record and "cer" in record:
            data[model]["wer"].append(record["wer"])
            data[model]["cer"].append(record["cer"])
            data[model]["pages"].append(page)
        else:
            # per-line format: aggregate across lines
            wers = [v["wer"] for v in record.values() if isinstance(v, dict)]
            cers = [v["cer"] for v in record.values() if isinstance(v, dict)]
            if wers:
                data[model]["wer"].extend(wers)
                data[model]["cer"].extend(cers)
                data[model]["pages"].extend([page] * len(wers))

    return data


def plot(data: dict) -> None:
    models = sorted(data.keys())
    n = len(models)
    x = np.arange(n)
    width = 0.35

    # Use compact page IDs on points to avoid overlapping long labels.
    seen_pages: set[str] = set()
    page_order: list[str] = []
    for model in models:
        for page in data[model]["pages"]:
            if page not in seen_pages:
                seen_pages.add(page)
                page_order.append(page)
    page_ids = {page: f"P{i + 1:02d}" for i, page in enumerate(page_order)}
    marker_cycle = ["o", "s", "^", "D", "v", "P", "X", "<", ">", "h", "*"]
    page_markers = {page: marker_cycle[i % len(marker_cycle)] for i, page in enumerate(page_order)}
    cmap = plt.get_cmap("tab20")
    page_colors = {page: cmap(i % 20) for i, page in enumerate(page_order)}

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), sharey=False)
    fig.suptitle("OCR Evaluation — WER and CER by Model", fontsize=13, fontweight="bold")

    rng = np.random.default_rng(42)

    for ax, metric, label, color in [
        (axes[0], "wer", "Word Error Rate (WER)", "#4C72B0"),
        (axes[1], "cer", "Character Error Rate (CER)", "#DD8452"),
    ]:
        values_per_model = [data[m][metric] for m in models]

        bp = ax.boxplot(
            values_per_model,
            positions=x,
            widths=width,
            patch_artist=True,
            medianprops=dict(color="black", linewidth=2),
            boxprops=dict(facecolor=color, alpha=0.5),
            whiskerprops=dict(linewidth=1.5),
            capprops=dict(linewidth=1.5),
            flierprops=dict(marker="x", color=color),
        )

        # Overlay individual data points with page-specific marker + color.
        for i, vals in enumerate(values_per_model):
            jitter = rng.uniform(-0.08, 0.08, size=len(vals))
            pages = data[models[i]]["pages"]
            for j, (v, page) in enumerate(zip(vals, pages)):
                ax.scatter(
                    x[i] + jitter[j],
                    v,
                    color=page_colors[page],
                    marker=page_markers[page],
                    edgecolors="black",
                    linewidths=0.5,
                    s=58,
                    zorder=5,
                    label="_nolegend_",
                )

        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=15, ha="right", fontsize=9)
        ax.set_ylabel(label)
        ax.set_title(label)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=1))
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_xlim(-0.5, n - 0.5)

    # Add compact page legend/key outside the plotting area.
    page_handles = [
        Line2D(
            [0],
            [0],
            marker=page_markers[page],
            color="none",
            markerfacecolor=page_colors[page],
            markeredgecolor="black",
            markeredgewidth=0.5,
            markersize=6,
            linewidth=0,
            label=page_ids[page],
        )
        for page in page_order
    ]
    if page_handles:
        fig.legend(
            handles=page_handles,
            loc="lower center",
            ncol=min(8, len(page_handles)),
            fontsize=7,
            title="Page IDs",
            title_fontsize=8,
            bbox_to_anchor=(0.5, 0.08),
            frameon=False,
            handletextpad=0.4,
            columnspacing=0.8,
        )

    legend_items = [(page_ids[page], page) for page in page_order]
    if legend_items:
        columns = min(3, len(legend_items))
        chunks = np.array_split(legend_items, columns)
        fig.text(0.02, 0.055, "Page key", fontsize=8, fontweight="bold", ha="left", va="bottom")
        for col, chunk in enumerate(chunks):
            key_text = "\n".join(f"{item[0]}: {item[1]}" for item in chunk)
            fig.text(
                0.02 + col * 0.32,
                0.005,
                key_text,
                fontsize=7,
                ha="left",
                va="bottom",
                family="monospace",
            )

    plt.tight_layout(rect=(0, 0.22, 1, 1))
    out = Path("evaluations/results_boxplot.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved → {out}")
    plt.show()


def plot_spotlight(
    data_by_page: dict,
    best_page: str = "pineda1_page_4",
    worst_page: str = "AR_SR8V4R3_4",
) -> None:
    pages      = [best_page, worst_page]
    accents    = ["#2ca02c", "#d62728"]
    row_labels = ["Best document", "Worst document"]

    fig = plt.figure(figsize=(14, 8))
    gs  = gridspec.GridSpec(2, 3, width_ratios=[1.5, 2, 2], hspace=0.55, wspace=0.35)
    fig.suptitle(
        "OCR Spotlight — Best vs. Worst Document",
        fontsize=14, fontweight="bold", y=1.01,
    )

    for row, (page, accent, row_label) in enumerate(zip(pages, accents, row_labels)):
        meta         = DOC_META.get(page, {"label": page, "desc": ""})
        page_results = data_by_page.get(page, {})
        models_here  = sorted(page_results.keys())
        x            = np.arange(len(models_here))
        bar_width    = 0.55

        # --- Thumbnail ---
        ax_img = fig.add_subplot(gs[row, 0])
        img_path = find_image(page)
        if img_path:
            img = imread(str(img_path))
            ax_img.imshow(img, aspect="auto")
        else:
            ax_img.text(0.5, 0.5, "Image\nnot found",
                        ha="center", va="center",
                        transform=ax_img.transAxes, color="gray")
        ax_img.set_xticks([])
        ax_img.set_yticks([])
        for spine in ax_img.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor(accent)
            spine.set_linewidth(2.5)
        ax_img.set_title(
            f"{row_label}\n{meta['label']}\n{meta['desc']}",
            fontsize=9, loc="left", pad=6,
        )

        # --- WER and CER bar charts ---
        short_labels = [MODEL_SHORT.get(m, m) for m in models_here]
        for col, (metric_idx, metric_label) in enumerate(
            [(0, "Word Error Rate (WER)"), (1, "Character Error Rate (CER)")], start=1
        ):
            ax = fig.add_subplot(gs[row, col])
            vals      = [page_results[m][metric_idx] for m in models_here]
            has_texts = [page_results[m][2]           for m in models_here]
            colors    = [MODEL_COLORS.get(m, "#888888") for m in models_here]

            y_cap = 1.0
            capped_vals = [min(v, y_cap) for v in vals]
            bars = ax.bar(x, capped_vals, width=bar_width, color=colors,
                          edgecolor="white", linewidth=0.8)

            for bar, val, capped, has_text in zip(bars, vals, capped_vals, has_texts):
                if not has_text:
                    bar.set_hatch("////")
                    bar.set_edgecolor("black")
                    label_y = min(capped, y_cap)
                    ax.annotate(
                        "empty",
                        (bar.get_x() + bar.get_width() / 2, label_y),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", fontsize=7, color="black",
                    )
                else:
                    label = f"{val:.2f}" if val <= y_cap else f"{val:.2f} ⚠"
                    ax.annotate(
                        label,
                        (bar.get_x() + bar.get_width() / 2, capped),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", fontsize=8,
                        color="black" if val <= y_cap else "#d62728",
                        fontweight="normal" if val <= y_cap else "bold",
                    )

            ax.set_xticks(x)
            ax.set_xticklabels(short_labels, rotation=20, ha="right", fontsize=8)
            ax.set_ylim(0, 1.18)
            ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=0))
            ax.set_title(metric_label, fontsize=9)
            ax.grid(axis="y", linestyle="--", alpha=0.4)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

    fig.legend(
        handles=[
            Patch(facecolor="gray", hatch="////", edgecolor="black",
                  label="Empty output (model refused / hallucinated)"),
            Patch(facecolor="#d62728", label="⚠ WER > 100% (more errors than words in reference)"),
        ],
        loc="lower center", ncol=1, fontsize=9, bbox_to_anchor=(0.5, -0.07),
    )

    out = Path("evaluations/results_spotlight.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved → {out}")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--chart",
        choices=["boxplot", "spotlight"],
        default="boxplot",
        help="Chart type to generate (default: boxplot)",
    )
    args = parser.parse_args()

    if args.chart == "spotlight":
        by_page = load_by_page()
        if not by_page:
            print("No evaluation files found in evaluations/")
        else:
            plot_spotlight(by_page)
    else:
        data = load_evaluations()
        if not data:
            print("No evaluation files found in evaluations/")
        else:
            for model, vals in sorted(data.items()):
                print(f"{model}: {len(vals['wer'])} page(s) — "
                      f"WER {np.mean(vals['wer']):.3f} ± {np.std(vals['wer']):.3f} | "
                      f"CER {np.mean(vals['cer']):.3f} ± {np.std(vals['cer']):.3f}")
            plot(data)
