import fitz
from pathlib import Path
import helpers.globalc as globalc

def convert_pdf_to_images(pdf_path, dpi=300, limit=None, verbose=False, overwrite=False):

    pdf_path = Path(pdf_path)
    try:
        doc = fitz.open(pdf_path)
        
        manifest = {
            "pdf_name": pdf_path.name,
            "total_pages_in_pdf": len(doc),
            "dpi": dpi,
            "output_format": "png",
            "output_directory": str(Path(globalc.IMAGES_DIR, f'{pdf_path.stem}').relative_to(Path.cwd())),
        }
        
        for i, page_number in enumerate(range(len(doc))):
            if limit and limit > 0 and i == limit:
                break
            
            page = doc.load_page(page_number)
            pix = page.get_pixmap(dpi=dpi)

            output_image_dir = Path(globalc.IMAGES_DIR, f'{pdf_path.stem}')
            output_image_dir.mkdir(exist_ok=True, parents=True)
            
            output_image_path = Path(output_image_dir, f'{pdf_path.stem}_page_{page_number + 1}.png')
            if output_image_path.exists() and not overwrite:
                continue
            pix.save(output_image_path)
            manifest[f'page_{page_number + 1}'] = str(output_image_path.relative_to(Path.cwd()))
            if verbose:
                print(f'Saved: {output_image_path}')
            

        doc.close()
        
        with open(Path(globalc.IMAGES_DIR, f'{pdf_path.stem}', 'manifest.json'), 'w') as f:
            import json
            json.dump(manifest, f, indent=4)
        
        print(f"PDF '{pdf_path.name}' has been converted to images in ={pdf_path.parent / 'images'}=")
    except Exception as e:
        print(f"Error processing PDF '{pdf_path.name}': {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert PDF to images.")
    parser.add_argument('pdf_path', type=str, help="Path to the PDF file.")
    parser.add_argument('--dpi', type=int, default=300, help="DPI for the output images.")
    parser.add_argument('--limit', type=int, default=None, help="Limit the number of pages to convert.")
    parser.add_argument('--verbose', action='store_true', help="Print verbose output.")
    parser.add_argument('--overwrite', action='store_true', help="Overwrite existing images.")
    
    args = parser.parse_args()
    convert_pdf_to_images(args.pdf_path, dpi=args.dpi, limit=args.limit, verbose=args.verbose, overwrite=args.overwrite)