import fitz
from pathlib import Path
import helpers.globalc as globalc

def convert_pdf_to_images(pdf_path, dpi=300, limit=None):

    pdf_path = Path(pdf_path)
    try:
        doc = fitz.open(pdf_path)
        for i, page_number in enumerate(range(len(doc))):
            page = doc.load_page(page_number)
            pix = page.get_pixmap(dpi=dpi)

            output_image_dir = Path(globalc.IMAGES_DIR, f'{pdf_path.stem}')
            output_image_dir.mkdir(exist_ok=True, parents=True)
            
            output_image_path = Path(output_image_dir, f'{pdf_path.stem}_page_{page_number + 1}.png')
            if output_image_path.exists():
                continue
            pix.save(output_image_path)
            print(f'Saved: {output_image_path}')
            if limit and i + 1 >= limit:
                break

        doc.close()
        print(f"PDF '{pdf_path.name}' has been converted to images in ={pdf_path.parent / 'images'}=")
    except Exception as e:
        print(f"Error processing PDF '{pdf_path.name}': {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert PDF to images.")
    parser.add_argument('pdf_path', type=str, help="Path to the PDF file.")
    parser.add_argument('--dpi', type=int, default=300, help="DPI for the output images.")
    parser.add_argument('--limit', type=int, default=None, help="Limit the number of pages to convert.")
    
    args = parser.parse_args()
    convert_pdf_to_images(args.pdf_path, dpi=args.dpi, limit=args.limit)