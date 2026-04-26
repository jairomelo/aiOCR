from helpers import validations
from pathlib import Path
import re

WORKING_DIR = Path.cwd()

_EXCLUDED_DIRS = {'groundtruth', 'source'}


def evaluate_model(model: str, validation_page: str, typeOCR: str = 'md', line_level: bool = False, save_result: bool = True) -> None:
    """Evaluate the transcription done from a specific model against a ground true transcription.

    Args:
        model (str): Name and version of the model to evaluate. Example: 'GLM-4.5V'
        validation_page (str): Name of the page to evaluate, without extension. Example: 'pineda1_page_4'
        typeOCR (str, optional): Type of the OCR files. Defaults to 'md', but can be 'mmd' or 'txt' depending on the format of the transcriptions.
        line_level (bool, optional): Whether to validate at the line level. Defaults to False (page level).
        save_result (bool, optional): Whether to save the evaluation result as a JSON file. Defaults to True.
    """
    
    # better safe than sorry
    validation_page = re.sub(r'\.[a-zA-Z0-9]+$', '', validation_page)  # Remove file extension if provided
    
    gt_page = Path(WORKING_DIR, 'transcriptions/groundtruth/', f'{validation_page}.txt')
    ocr_page = Path(WORKING_DIR, 'transcriptions/', model, f'{validation_page}.{typeOCR}')
    
    if not Path(gt_page).exists() or not Path(ocr_page).exists():
        print(f"Either the ground truth page '{gt_page}' or the OCR page '{ocr_page}' does not exist.")
        return
    
    evaluation = validations.validate_ocr_from_markdown(model, gt_page, ocr_page, save_result=save_result, line_level=line_level)
    print(evaluation)


def evaluate_batch(models: list[str] | None = None, typeOCR: str = 'md', line_level: bool = False, save_result: bool = True) -> None:
    """Evaluate all ground truth pages against a list of models (or all available models).

    Ground truth pages are discovered automatically from transcriptions/groundtruth/.
    For each model, only pages that have a matching transcription file are evaluated.

    Args:
        models (list[str] | None): Models to evaluate. If None, all subdirectories in
            transcriptions/ (except 'groundtruth' and 'source') are used.
        typeOCR (str, optional): Extension of model transcription files. Defaults to 'md'.
        line_level (bool, optional): Whether to validate at the line level. Defaults to False.
        save_result (bool, optional): Whether to save each result as a JSON file. Defaults to True.
    """
    gt_dir = Path(WORKING_DIR, 'transcriptions', 'groundtruth')
    gt_pages = [p.stem for p in gt_dir.glob('*.txt')]

    if not gt_pages:
        print(f"No ground truth .txt files found in '{gt_dir}'.")
        return

    if models is None:
        transcriptions_dir = Path(WORKING_DIR, 'transcriptions')
        models = [
            d.name for d in transcriptions_dir.iterdir()
            if d.is_dir() and d.name not in _EXCLUDED_DIRS
        ]

    if not models:
        print("No model directories found in 'transcriptions/'.")
        return

    print(f"Ground truth pages : {gt_pages}")
    print(f"Models             : {models}\n")

    for model in models:
        for page in gt_pages:
            ocr_file = Path(WORKING_DIR, 'transcriptions', model, f'{page}.{typeOCR}')
            if not ocr_file.exists():
                print(f"[SKIP] {model} / {page} — transcription not found.")
                continue
            print(f"[EVAL] {model} / {page}")
            evaluate_model(model, page, typeOCR=typeOCR, line_level=line_level, save_result=save_result)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate model transcription(s) against ground truth.")
    subparsers = parser.add_subparsers(dest='command')

    # --- single evaluation (original behaviour) ---
    single = subparsers.add_parser('single', help="Evaluate one model against one page.")
    single.add_argument('model', type=str, help="Model name. Example: 'GLM-4.5V'")
    single.add_argument('validation_page', type=str, help="Page stem to evaluate. Example: 'pineda1_page_4'")
    single.add_argument('--typeOCR', type=str, default='md', help="Transcription file extension (default: md).")
    single.add_argument('--line_level', action='store_true', help="Validate at line level instead of page level.")

    # --- batch evaluation ---
    batch = subparsers.add_parser('batch', help="Evaluate one or more models against all ground truth pages.")
    batch.add_argument('--models', nargs='+', default=None,
                       metavar='MODEL',
                       help="Models to evaluate. Defaults to all directories in transcriptions/.")
    batch.add_argument('--typeOCR', type=str, default='md', help="Transcription file extension (default: md).")
    batch.add_argument('--line_level', action='store_true', help="Validate at line level instead of page level.")
    batch.add_argument('--no_save', action='store_true', help="Do not save evaluation results to disk.")

    args = parser.parse_args()

    if args.command == 'single':
        evaluate_model(args.model, args.validation_page, args.typeOCR, args.line_level)
    elif args.command == 'batch':
        evaluate_batch(
            models=args.models,
            typeOCR=args.typeOCR,
            line_level=args.line_level,
            save_result=not args.no_save,
        )
    else:
        parser.print_help()