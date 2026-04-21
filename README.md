# Beyond "Dirty OCR"

This repository contains the code and documentation for the project 'Beyond "Dirty OCR".' The project evaluates whether small, local MLMs and VLMs can transcribe low-quality and legacy digitizations, both printed (OCR) and handwritten (HWTR). The goals are to assess:

- Performance: Time required for a small local model to perform text recognition
- Accuracy: WER and CER for each model
- Cost: Token consumption during recognition tasks
- Reproducibility: Consistency of results across iterations
- Accessibility: Minimum hardware requirements for these tasks

## Models

This project evaluates the following model:

- DeepSeek OCR [model card](https://huggingface.co/deepseek-ai/DeepSeek-OCR)

### Foundation Models

The following foundation model is included as a baseline for comparison:

- GLM-4.5V (multimodal) - [model card](https://huggingface.co/zai-org/GLM-4.5V)

## Relevant files

- **Configuration**: A simple global configuration file is included in `helpers/globalc.py`. You can apply local directory changes in the workspace by running `python helpers/globalc.py --config-local`.
