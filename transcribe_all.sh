#!/usr/bin/env bash
set -euo pipefail

# End-to-end OCR pipeline for GRIT compatible models:
# 1) Transcribe images for each model
# 2) Evaluate against available ground truth
# 3) Generate boxplot and spotlight charts

MODELS=(
    "gemma3:latest"
    "qwen3.5:latest"
)

# Keep folders explicit for reproducibility with your current dataset.
FOLDERS=(
    "images/AR_SR8V4R3"
    "images/CCundinamarca"
    "images/CO_18180627"
    "images/dmcz_18250101"
    "images/el-redactor-1"
    "images/pineda1"
    "images/fpineda_30_pza2"
    "images/fpineda_184_pza6"
    "images/fpineda_196_pza8"
)

echo "==> Starting transcription batch"
for model in "${MODELS[@]}"; do
    for folder in "${FOLDERS[@]}"; do
        if [[ ! -d "$folder" ]]; then
            echo "[WARN] Missing folder: $folder (skipping)"
            continue
        fi

        echo "[TRANSCRIBE] model=$model folder=$folder"
        uv run python transcribe.py \
            --service grit \
            --images "$folder" \
            --model "$model" \
            --enforce-compatible
    done
done

echo "==> Transcriptions finished"

# evaluatemodel.py expects sanitized model folder names (':' -> '-')
EVAL_MODELS=()
for model in "${MODELS[@]}"; do
    EVAL_MODELS+=("${model//:/-}")
done

echo "==> Running batch evaluation"
uv run python evaluatemodel.py batch --models "${EVAL_MODELS[@]}" --typeOCR md

echo "==> Generating charts"
uv run python plotresults.py --chart boxplot
uv run python plotresults.py --chart spotlight

echo "==> Pipeline completed"
