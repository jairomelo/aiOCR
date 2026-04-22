import jiwer
from pathlib import Path
import helpers.globalc as globalc

def validate_ocr(gt_page: list[str], ocr_page: list[str]) -> dict:
    evaluation = {}
    
    gt_page = [line for line in gt_page if line != '' or line.isspace()]
    ocr_page = [line for line in ocr_page if line != '' or line.isspace()]
    
    ln = 1
    for ref, ocr in zip(gt_page, ocr_page):
        wer = jiwer.wer(ref, ocr)
        cer = jiwer.cer(ref, ocr)
        evaluation[ln] = {"text": ref, "ocr": ocr, "wer": wer, "cer": cer}
        ln += 1
        
    return evaluation

def validate_ocr_from_markdown(md_file: str | Path , gen_page: str | Path, save_result: bool = False) -> dict:
    md_file = Path(md_file)
    gen_page = Path(gen_page)
    
    if not md_file.exists() or not gen_page.exists():
        print(f"Either the ground truth page '{md_file}' or the OCR page '{gen_page}' does not exist.")
        return {}
    with open(md_file, 'r') as f:
        gt_page = f.read().splitlines()
    with open(gen_page, 'r') as f:
        ocr_page = f.read().splitlines()

    
    if save_result:
        evaluation = validate_ocr(gt_page, ocr_page)
        result_file = Path(globalc.EVALUATION_DIR, f'{md_file.stem}_vs_{gen_page.stem}_evaluation.json')
        with open(result_file, 'w') as f:
            import json
            json.dump(evaluation, f, indent=4)
            
    return validate_ocr(gt_page, ocr_page)

if __name__ == "__main__":
    # Example usage
    WORKING_DIR = Path.cwd()
    
    validation_page = 'pineda1_page_4'
    against = 'GLM-4.5V'
    
    md_file = Path(WORKING_DIR, 'transcriptions/groundtruth/', f'{validation_page}.md')
    ocr_page = Path(WORKING_DIR, 'transcriptions/', against, f'{validation_page}.md')
    
    evaluation = validate_ocr_from_markdown(md_file, ocr_page, save_result=True)
    print(evaluation)
