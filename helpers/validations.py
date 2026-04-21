import jiwer
import frontmatter
from pathlib import Path

def validate_ocr(gt_page: list[str], ocr_page: list[str]) -> dict:
    evaluation = {}
    
    ln = 1
    for ref, hyp in zip(gt_page, ocr_page):
        wer = jiwer.wer(ref, hyp)
        cer = jiwer.cer(ref, hyp)
        evaluation[ln] = {"text": ref, "wer": wer, "cer": cer}
        ln += 1
        
    return evaluation

def validate_ocr_from_markdown(md_file: str | Path , gen_page: str | Path) -> dict:
    post = frontmatter.load(str(md_file))
    try:
        ocr = frontmatter.loads(str(gen_page))
    except TypeError:
        with open(gen_page, 'r') as f:
            ocr = frontmatter.load(f)
    gt_page = post.content.splitlines()
    ocr_page = ocr.content.splitlines()
    print(type(gt_page), type(ocr_page))
    
    return validate_ocr(gt_page, ocr_page)

if __name__ == "__main__":
    # Example usage
    WORKING_DIR = Path.cwd()
    md_file = Path(WORKING_DIR, 'transcriptions/groundtruth/pineda1_page_4.md.md')
    ocr_page = Path(WORKING_DIR, 'transcriptions/GLM-4.5V/pineda1_page_4.md')
    
    evaluation = validate_ocr_from_markdown(md_file, ocr_page)
    print(evaluation)
