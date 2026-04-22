"""Plot WER and CER box plots from evaluation JSON files."""

import json
import re
from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

EVALUATIONS_DIR = Path("evaluations")


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

        # Overlay individual data points
        for i, vals in enumerate(values_per_model):
            jitter = rng.uniform(-0.08, 0.08, size=len(vals))
            ax.scatter(
                x[i] + jitter,
                vals,
                color=color,
                edgecolors="black",
                linewidths=0.6,
                s=60,
                zorder=5,
                label="_nolegend_",
            )
            # Annotate page labels
            pages = data[models[i]]["pages"]
            for j, (v, page) in enumerate(zip(vals, pages)):
                ax.annotate(
                    page,
                    (x[i] + jitter[j], v),
                    textcoords="offset points",
                    xytext=(6, 2),
                    fontsize=7,
                    color="dimgray",
                )

        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=15, ha="right", fontsize=9)
        ax.set_ylabel(label)
        ax.set_title(label)
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=1))
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_xlim(-0.5, n - 0.5)

    plt.tight_layout()
    out = Path("evaluations/results_boxplot.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved → {out}")
    plt.show()


if __name__ == "__main__":
    data = load_evaluations()
    if not data:
        print("No evaluation files found in evaluations/")
    else:
        for model, vals in sorted(data.items()):
            print(f"{model}: {len(vals['wer'])} page(s) — "
                  f"WER {np.mean(vals['wer']):.3f} ± {np.std(vals['wer']):.3f} | "
                  f"CER {np.mean(vals['cer']):.3f} ± {np.std(vals['cer']):.3f}")
        plot(data)
