from pathlib import Path

# Google Drive Paths
GD_WORKING_DIR = Path('/content/drive/MyDrive/aiOCR')
GD_IMAGES_DIR = Path(GD_WORKING_DIR, 'images')
GD_PDF_DIR = Path(GD_WORKING_DIR, 'PDF')
GD_TRANSCRIPTIONS_DIR = Path(GD_WORKING_DIR, 'transcriptions')
GD_GT_DIR = Path(GD_TRANSCRIPTIONS_DIR, 'groundtruth')

# Local Paths
WORKING_DIR = Path.cwd()
IMAGES_DIR = Path(WORKING_DIR, 'images')
PDF_DIR = Path(WORKING_DIR, 'PDF')
TRANSCRIPTIONS_DIR = Path(WORKING_DIR, 'transcriptions')
GT_DIR = Path(TRANSCRIPTIONS_DIR, 'groundtruth')


def set_local_paths():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TRANSCRIPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    GT_DIR.mkdir(parents=True, exist_ok=True)
    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ensure Paths and other configurations are ready.")
    parser.add_argument('--config-local', action='store_true', help="Create paths if empty to local directories.")
    args = parser.parse_args()
    if args.config_local:
        set_local_paths()
    
        