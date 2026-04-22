from helpers import validations
from pathlib import Path
import re

WORKING_DIR = Path.cwd()

def evaluate_model(model: str, validation_page: str, typeOCR: str = 'md', line_level: bool = False, save_result: bool = True) -> None:
    """Evaluate the transcription done from a specific model against a ground true transcription.

    Args:
        model (str): Name and version of the model to evaluate. Example: 'GLM-4.5V'
        validation_page (str): Name of the page to evaluate, without extension. Example: 'pineda1_page_4'
        typeOCR (str, optional): Type of the OCR files. Defaults to 'md', but can be 'mmd' or 'txt' depending on the format of the transcriptions.
        validation_level (str, optional): Level of validation, either 'page' or 'line'. Defaults to 'page'.
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
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate a model's transcription against a ground truth.")
    parser.add_argument('model', type=str, help="Name and version of the model to evaluate. Example: 'GLM-4.5V'")
    parser.add_argument('validation_page', type=str, help="Name of the page to evaluate, without extension. Example: 'pineda1_page_4'")
    parser.add_argument('--typeOCR', type=str, default='md', help="Type of the OCR files. Defaults to 'md', but can be 'mmd' or 'txt' depending on the format of the transcriptions.")
    parser.add_argument('--line_level', action='store_true', help="Whether to validate at the line level or page level. Defaults to False (page level).")
    
    args = parser.parse_args()
    evaluate_model(args.model, args.validation_page, args.typeOCR, args.line_level)