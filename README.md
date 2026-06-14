# Beyond "Dirty OCR"

This repository contains the code and documentation for the project 'Beyond "Dirty OCR".' The project evaluates whether small, local MLMs and VLMs can transcribe low-quality and legacy digitizations, both printed (OCR) and handwritten (HWTR). The goals are to assess:

- Performance: Time required for a small local model to perform text recognition
- Accuracy: WER and CER for each model
- Cost: Token consumption during recognition tasks
- Reproducibility: Consistency of results across iterations
- Accessibility: Minimum hardware requirements for these tasks

## Base Prompt

> Convert the document to plain text, as close to the original as possible (including typos, print errors, and original grammar and spelling). Do not add any formatting, markdown, or annotations.

## Models

This project evaluates the following models:

### Running with 4-bit compression (quantization)

These models run successfully with 4-bit quantization:

- DeepSeek OCR [model card](https://huggingface.co/deepseek-ai/DeepSeek-OCR)
- Qwen2.5-VL-3B-Instruct [model card](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct)
- Qwen2.5-VL-7B-Instruct [model card](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct)
- Florence-2-large [model card](https://huggingface.co/microsoft/Florence-2-large)

### UCSB GRIT-hosted models

These OpenAI-compatible models are used through the UCSB GRIT infrastructure and run under the same OCR workflow as the local quantized models. The best results in this project have been observed with:

- qwen3.5:latest
- gemma3:latest

Other GRIT models were also tested, but several produced hallucinations or poor OCR output. A current compatibility summary is documented in the `transcribe.py` section below.

### Failed tests

These models were tested but did not meet evaluation criteria:

- Gemma 4 E4B [model card](https://huggingface.co/google/gemma-4-E4B) -> Failed to identify the text in the image
- InternVL3-2B [model card](https://huggingface.co/OpenGVLab/InternVL3-2B) -> No support for 4-bit compression
- MiniCPM-V-2_6 [model card](https://huggingface.co/openbmb/MiniCPM-V-2_6) -> Requires `flash-attn`, not compatible with T4 GPU
- Phi-3.5-vision [model card](https://huggingface.co/microsoft/Phi-3.5-vision-instruct) -> Generates excessive hallucinations in limited GPU settings

### Foundation Models

The following foundation model is included as a baseline for comparison:

- GLM-4.5V (multimodal) - [model card](https://huggingface.co/zai-org/GLM-4.5V)

### Tesseract

Tesseract is included as a traditional OCR baseline for comparison.

### Source

The legacy OCR.

## Folder Structure

### Source Artifacts

PDFs and images are stored in two corresponding directories. The `images` directory groups images into subdirectories named after the source PDF. A simple conversion manifest is kept in each folder to document the parameters used during conversion.

An important aspect of this transformation is that image size is kept manageable (about 300 DPI). This can affect OCR quality, particularly for complex layouts or small font sizes, but it helps reduce token consumption.

The text layer is extracted using `PyMuPDF`, and each page's text is stored in the `transcriptions/source` directory.

## Relevant files

- **Configuration**: A simple global configuration file is included in `helpers/globalc.py`. You can apply local directory changes in the workspace by running `python helpers/globalc.py --config-local`.
- **pdf2img**: CLI tool that extracts the text layer and converts PDF pages into images. Explore available parameters by running `python pdf2img.py --help`.
- **evaluatemodel**: CLI tool that evaluates a model's text recognition output against a ground-truth, human-generated transcription.
- **transcribe**: CLI tool that sends images to an OpenAI-compatible LLM service and saves the transcription output. Replaces the model-specific Jupyter notebooks that previously ran on Google Colab.

## Transcribing with `transcribe.py`

`transcribe.py` uses the OpenAI-compatible API to batch-transcribe images using university-hosted or other external LLM services. Transcription output is saved to `transcriptions/{model}/` and is directly compatible with `evaluatemodel.py`.

### Setup

Add the required API keys to a `.env` file at the project root (already excluded from version control):

```
GRIT_KEY=your-grit-api-key
DL_KEY=your-dream-lab-api-key   # optional
```

### Configured services

| Service | Base URL |
|---|---|
| `grit` | `https://llm.grit.ucsb.edu/api/v1` |
| `dream-lab` | `https://litellm.dreamlab.ucsb.edu/` |

New services can be added by extending the `SERVICES` dict in `transcribe.py` and adding the corresponding key to `.env`.

### GRIT tested compatibility (current)

Based on local tests for this OCR workflow:

- `compatible`: `gemma3:latest`, `llava:7b`, `mistral:latest`, `qwen3-coder-next:latest`, `qwen3.5:latest`
- `compatible_slow`: `gemma4:31b`
- `not_sure`: `deepseek-r1:latest`, `llama3:latest`, `qwen3:latest`, `phi4:latest`, `llama3.1:8b`, `qwen3-coder:latest`
- `incompatible`: `gpt-oss:20b`

`transcribe.py --list-models --service grit` shows these labels next to each model.

### Usage

**List available models for a service:**

```bash
python transcribe.py --list-models --service grit
```

**Enforce only tested compatible models (GRIT):**

```bash
python transcribe.py --service grit --model gemma3:latest --images images/pineda1/ --enforce-compatible
```

**Transcribe a single image:**

```bash
python transcribe.py --model gemma4:31b --image images/pineda1/pineda1_page_1.png
```

**Transcribe all images in a folder:**

```bash
python transcribe.py --model gemma4:31b --images images/pineda1/
```

If no `--images` folder is specified, the script defaults to the entire `images/` directory.

If the provider returns `413 Request Entity Too Large`, `transcribe.py` automatically retries with progressively smaller image encodings (downscale/compression/grayscale) before failing.

**Use a custom prompt from a file:**

```bash
python transcribe.py --model gemma4:31b --images images/pineda1/ --prompt prompts/my_prompt.txt
```

**Track token usage:**

```bash
python transcribe.py --model gemma4:31b --images images/pineda1/ --usage-data
```

Usage records are appended to `evaluations/usage.json`.

**Re-run and overwrite existing transcriptions:**

```bash
python transcribe.py --model gemma4:31b --images images/pineda1/ --overwrite
```

By default the script skips images that already have a transcription file.

### Output and model names

Transcriptions are saved to `transcriptions/{model}/{stem}.md`, where colons in the model name are replaced with hyphens (e.g. `gemma4:31b` → `gemma4-31b`). Use the same sanitized name when evaluating:

```bash
python evaluatemodel.py single gemma4-31b pineda1_page_1
```

## End-to-end pipeline script

Use `transcribe_all.sh` to run the complete workflow in one command:

1. Transcribe selected image folders with GRIT-compatible models
2. Run batch evaluation against available ground truth
3. Generate `boxplot` and `spotlight` charts

Run it from the project root:

```bash
bash transcribe_all.sh
```

The script currently targets these models:

- `gemma3:latest`
- `llava:7b`
- `mistral:latest`
- `qwen3-coder-next:latest`
- `qwen3.5:latest`
