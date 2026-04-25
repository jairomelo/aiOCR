import fitz
import json
from pathlib import Path
import helpers.globalc as globalc

def _resolve_pages(pages_arg, limit, total):
    """Return a sorted list of 0-indexed page numbers to process.

    pages_arg: list of 1-indexed page numbers, or None.
    limit:     max number of pages from the start, or None.
    total:     total pages in the document.
    """
    if pages_arg is not None:
        return sorted(p - 1 for p in pages_arg if 1 <= p <= total)
    indices = list(range(total))
    if limit and limit > 0:
        indices = indices[:limit]
    return indices


def extract_text_layer(pdf_path, limit=None, pages=None, verbose=False, overwrite=False):
    """Extract the embedded text layer from each PDF page and save as .txt files."""
    pdf_path = Path(pdf_path)
    try:
        doc = fitz.open(pdf_path)
        output_text_dir = Path(globalc.TRANSCRIPTIONS_DIR, 'source', pdf_path.stem)
        output_text_dir.mkdir(exist_ok=True, parents=True)

        for page_number in _resolve_pages(pages, limit, len(doc)):

            output_text_path = output_text_dir / f'{pdf_path.stem}_page_{page_number + 1}.txt'
            if output_text_path.exists() and not overwrite:
                continue

            page = doc.load_page(page_number)
            text = page.get_text()
            output_text_path.write_text(text, encoding='utf-8')

            if verbose:
                print(f'Saved text layer: {output_text_path}')


        doc.close()
        print(f"Text layers for '{pdf_path.name}' saved to {output_text_dir.relative_to(Path.cwd())}")
    except Exception as e:
        print(f"Error extracting text from '{pdf_path.name}': {e}")


def convert_pdf_to_images(pdf_path, dpi=300, limit=None, pages=None, verbose=False, overwrite=False):

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

        for page_number in _resolve_pages(pages, limit, len(doc)):
            
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
            json.dump(manifest, f, indent=4)
        
        print(f"PDF '{pdf_path.name}' has been converted to images in ={pdf_path.parent / 'images'}=")
    except Exception as e:
        print(f"Error processing PDF '{pdf_path.name}': {e}")

def convert_pdf(pdf_path, dpi=300, limit=None, pages=None, verbose=False, overwrite=False):
    """Convert a PDF to images and extract its text layer."""
    convert_pdf_to_images(pdf_path, dpi=dpi, limit=limit, pages=pages, verbose=verbose, overwrite=overwrite)
    extract_text_layer(pdf_path, limit=limit, pages=pages, verbose=verbose, overwrite=overwrite)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert PDF to images and extract text layer.")
    parser.add_argument('pdf_path', type=str, help="Path to the PDF file.")
    parser.add_argument('--dpi', type=int, default=300, help="DPI for the output images.")
    parser.add_argument('--limit', type=int, default=None, help="Limit the number of pages to convert.")
    parser.add_argument('--range', dest='page_range', type=str, default=None,
                        help="Pages to convert (1-indexed, no brackets needed). "
                             "Use START-END for an inclusive range (e.g. --range 1-46), "
                             "or comma-separated values for an explicit list (e.g. --range 1,3,46).")
    parser.add_argument('--verbose', action='store_true', help="Print verbose output.")
    parser.add_argument('--overwrite', action='store_true', help="Overwrite existing images.")
    parser.add_argument('--images-only', action='store_true', help="Only convert pages to images, skip text extraction.")
    parser.add_argument('--text-only', action='store_true', help="Only extract the text layer, skip image conversion.")

    args = parser.parse_args()

    pages = None
    if args.page_range is not None:
        raw = args.page_range.strip()
        if '-' in raw:
            # START-END inclusive range
            start, end = (int(x) for x in raw.split('-', 1))
            pages = list(range(start, end + 1))
        else:
            # comma-separated explicit list
            pages = [int(x) for x in raw.split(',')]

    if args.images_only:
        convert_pdf_to_images(args.pdf_path, dpi=args.dpi, limit=args.limit, pages=pages, verbose=args.verbose, overwrite=args.overwrite)
    elif args.text_only:
        extract_text_layer(args.pdf_path, limit=args.limit, pages=pages, verbose=args.verbose, overwrite=args.overwrite)
    else:
        convert_pdf(args.pdf_path, dpi=args.dpi, limit=args.limit, pages=pages, verbose=args.verbose, overwrite=args.overwrite)