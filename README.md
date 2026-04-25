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

This project evaluates the following model:

### Running with 4-bit compression (quantization)

- DeepSeek OCR [model card](https://huggingface.co/deepseek-ai/DeepSeek-OCR)
- Qwen2.5-VL-3B-Instruct [model card](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct)
- Qwen2.5-VL-7B-Instruct [model card](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct)

### Failed tests

- Gemma 4 E4B [model card](https://huggingface.co/google/gemma-4-E4B) -> Failed to identify the text in the image
- InternVL3-2B [model card](https://huggingface.co/OpenGVLab/InternVL3-2B) -> No run on compressed mode
- MiniCPM-V-2_6 [model card](https://huggingface.co/openbmb/MiniCPM-V-2_6) -> Depends on `flash-attn`, no compatible with T4 GPU

### Foundation Models

The following foundation model is included as a baseline for comparison:

- GLM-4.5V (VLM) - [model card](https://huggingface.co/zai-org/GLM-4.5V)

## Folder Structure

### Source Artifacts

PDFs and images are stored in two corresponding directories. The `images` directory groups images into subdirectories named after the source PDF. A simple conversion manifest is kept in each folder to document the parameters used during conversion.

An important aspect of this transformation is that image size is kept manageable (about 300 DPI). This can affect OCR quality, particularly for complex layouts or small font sizes, but it helps reduce token consumption.

The text layer is extracted using `PyMuPDF`, and each page's text is stored in the `transcriptions/source` directory.

## Relevant files

- **Configuration**: A simple global configuration file is included in `helpers/globalc.py`. You can apply local directory changes in the workspace by running `python helpers/globalc.py --config-local`.
- **pdf2img**: CLI tool that extracts the text layer and converts PDF pages into images. Explore available parameters by running `python pdf2img.py --help`.
- **evaluatemodel**: CLI tool that evaluates a model's text recognition output against a ground-truth, human-generated transcription.
