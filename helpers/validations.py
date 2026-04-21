import jiwer
import frontmatter
from pathlib import Path
import globalc

def validate_ocr(gt_page: list[str], ocr_page: list[str]) -> dict:
    evaluation = {}
    
    ln = 1
    for ref, hyp in zip(gt_page, ocr_page):
        wer = jiwer.wer(ref, hyp)
        cer = jiwer.cer(ref, hyp)
        evaluation[ln] = {"text": ref, "wer": wer, "cer": cer}
        ln += 1
        
    return evaluation

def validate_ocr_from_markdown(md_file: str | Path , gen_page: str | Path, save_result: bool = False) -> dict:
    post = frontmatter.load(str(md_file))
    try:
        ocr = frontmatter.loads(str(gen_page))
    except TypeError:
        with open(gen_page, 'r') as f:
            ocr = frontmatter.load(f)
    gt_page = post.content.splitlines()
    ocr_page = ocr.content.splitlines()
    
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
