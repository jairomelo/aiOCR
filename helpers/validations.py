import jiwer
from pathlib import Path
import helpers.globalc as globalc
import re

def validate_lines(gt_page: list[str], ocr_page: list[str]) -> dict:
    evaluation = {}
    
    gt_page = [line for line in gt_page if line.strip() != '']
    ocr_page = [line for line in ocr_page if line.strip() != '']
    
    gt_page = [line for line in gt_page if not re.match(r'\[.*\]', line)]  # Remove lines that are just markdown links
    ocr_page = [line for line in ocr_page if not re.match(r'\[.*\]', line)]  
    
    ln = 1
    for ref, ocr in zip(gt_page, ocr_page):
        wer = jiwer.wer(ref, ocr)
        cer = jiwer.cer(ref, ocr)
        evaluation[ln] = {"text": ref, "ocr": ocr, "wer": wer, "cer": cer}
        ln += 1
        
    return evaluation

def validate_page(gt_page: str, ocr_page: str) -> dict:
    wer = jiwer.wer(gt_page, ocr_page)
    cer = jiwer.cer(gt_page, ocr_page)
    evaluation = {"text": gt_page, "ocr": ocr_page, "wer": wer, "cer": cer}
    return evaluation

def validate_ocr_from_markdown(model: str, md_file: str | Path , gen_page: str | Path, line_level: bool = False, save_result: bool = False) -> dict:
    """Validate OCR output against ground truth markdown files.
    
    Args:
        model (str): The name of the OCR model being evaluated.
        md_file (str | Path): The path to the ground truth markdown file.
        gen_page (str | Path): The path to the OCR output markdown file.
        line_level (bool, optional): Whether to validate at the line level or page level. Defaults to False (page level).
        save_result (bool, optional): Whether to save the evaluation result as a JSON file. Defaults to False.
    """
    md_file = Path(md_file)
    gen_page = Path(gen_page)
    
    if not md_file.exists() or not gen_page.exists():
        print(f"Either the ground truth page '{md_file}' or the OCR page '{gen_page}' does not exist.")
        return {}
    
    evaluation = validate_lines(md_file.read_text().splitlines(), gen_page.read_text().splitlines()) if line_level else validate_page(md_file.read_text(), gen_page.read_text())
    
    if save_result:
        result_file = Path(globalc.EVALUATION_DIR, f'{model}_{md_file.stem}_evaluation.json')
        if line_level:
            result_file = Path(globalc.EVALUATION_DIR, f'{model}_{md_file.stem}_line_level_evaluation.json')
        with open(result_file, 'w') as f:
            import json
            json.dump(evaluation, f, indent=4)
            
    return evaluation

if __name__ == "__main__":
    # Example usage
    WORKING_DIR = Path.cwd()
    
    validation_page = 'pineda1_page_4'
    against = 'GLM-4.5V'
    
    md_file = Path(WORKING_DIR, 'transcriptions/groundtruth/', f'{validation_page}.md')
    ocr_page = Path(WORKING_DIR, 'transcriptions/', against, f'{validation_page}.md')
    
    evaluation = validate_ocr_from_markdown(against, md_file, ocr_page, save_result=True, line_level=True)
    print(evaluation)
