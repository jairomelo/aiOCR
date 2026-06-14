from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv
import argparse
import base64
import json
import logging
import os
import sys

if TYPE_CHECKING:
    from openai.types.completion_usage import CompletionUsage

load_dotenv()

# ---------------------------------------------------------------------------
# Service configuration
# Add new providers here: each entry needs a "url" and an "key" from env.
# ---------------------------------------------------------------------------
SERVICES: dict[str, dict] = {
    "grit": {
        "url": "https://llm.grit.ucsb.edu/api/v1",
        "key": os.getenv("GRIT_KEY"),
    },
    "dream-lab": {
        "url": "https://litellm.dreamlab.ucsb.edu/",
        "key": os.getenv("DL_KEY"),
    },
}

# GRIT model behavior based on local project tests.
# Status labels:
# - compatible: produces usable transcriptions for this OCR workflow
# - compatible_slow: usable but significantly slower
# - not_sure: responds but often fails to recognize image text
# - incompatible: not suitable for image transcription in this workflow
GRIT_MODEL_COMPATIBILITY: dict[str, set[str]] = {
    "compatible": {
        "gemma3:latest",
        "llava:7b",
        "mistral:latest",
        "qwen3-coder-next:latest",
        "qwen3.5:latest",
    },
    "compatible_slow": {
        "gemma4:31b",
    },
    "not_sure": {
        "deepseek-r1:latest",
        "llama3:latest",
        "qwen3:latest",
        "phi4:latest",
        "llama3.1:8b",
        "qwen3-coder:latest",
    },
    "incompatible": {
        "gpt-oss:20b",
    },
}

DEFAULT_PROMPT = (
    "Convert the document to plain text, as close to the original as possible "
    "(including typos, print errors, and original grammar and spelling). "
    "Do not add any formatting, markdown, or annotations."
)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}

WORKING_DIR = Path.cwd()
TRANSCRIPTIONS_DIR = WORKING_DIR / "transcriptions"
EVALUATIONS_DIR = WORKING_DIR / "evaluations"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sanitize_model_name(model: str) -> str:
    """Make a model name filesystem-safe (e.g. 'gemma4:31b' -> 'gemma4-31b')."""
    return model.replace(":", "-").replace("/", "-")


def _client(service: dict) -> OpenAI:
    return OpenAI(
        base_url=service["url"],
        api_key=service["key"],
        timeout=300.0,  # large models can take several minutes to load from cold
        max_retries=0,
    )


def _encode_image(image_path: str | Path, max_width: int = 2048) -> str:
    """Resize image to max_width and return as base64-encoded JPEG string."""
    img = Image.open(image_path)

    if img.mode != "RGB":
        img = img.convert("RGB")

    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.Resampling.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def _read_if_file(value: str) -> str:
    """Return file contents if value is an existing path, otherwise return value as-is."""
    p = Path(value)
    if p.exists() and p.is_file():
        return p.read_text(encoding="utf-8")
    return value


def _is_image(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def _validate_service(parser: argparse.ArgumentParser, service_name: str) -> dict:
    if service_name not in SERVICES:
        parser.error(f"Unknown service '{service_name}'. Available: {list(SERVICES.keys())}")
    config = SERVICES[service_name]
    if not config.get("key"):
        parser.error(
            f"Service '{service_name}' has no API key configured. "
            f"Set the corresponding environment variable in your .env file."
        )
    return config


def _get_grit_model_status(model: str) -> str | None:
    """Return compatibility status for a GRIT model, if known."""
    for status, models in GRIT_MODEL_COMPATIBILITY.items():
        if model in models:
            return status
    return None


def _log_grit_model_guidance(model: str, enforce_compatible: bool = False) -> None:
    """Log compatibility guidance for GRIT-tested models.

    When enforce_compatible=True, only models in "compatible" are allowed.
    """
    status = _get_grit_model_status(model)

    if status is None:
        msg = (
            f"Model '{model}' is not in the local compatibility table. "
            "Proceeding without compatibility guidance."
        )
        if enforce_compatible:
            raise ValueError(msg)
        logging.warning(msg)
        return

    if status == "compatible":
        logging.info(f"Model '{model}' status: compatible.")
        return

    if status == "compatible_slow":
        msg = f"Model '{model}' status: compatible but slow."
    elif status == "not_sure":
        msg = (
            f"Model '{model}' status: uncertain image recognition; "
            "outputs may not contain useful text."
        )
    else:
        msg = f"Model '{model}' status: incompatible for this OCR workflow."

    if enforce_compatible:
        raise ValueError(
            f"{msg} Use a model marked as compatible, or rerun without --enforce-compatible."
        )

    logging.warning(msg)


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------

def list_models(service_name: str) -> None:
    """Print available models for a configured service."""
    config = SERVICES.get(service_name)
    if not config:
        print(f"Unknown service '{service_name}'. Available: {list(SERVICES.keys())}")
        return
    if not config.get("key"):
        print(f"No API key configured for '{service_name}'.")
        return

    client = _client(config)
    try:
        models_page = client.models.list()
        print(f"\nModels available on '{service_name}':")
        for model in models_page.data:
            if service_name == "grit":
                status = _get_grit_model_status(model.id)
                status_tag = f" [{status}]" if status else ""
                print(f"  {model.id}{status_tag}")
            else:
                print(f"  {model.id}")
    except Exception as e:
        print(f"Error fetching models from '{service_name}': {e}")


def transcribe_image(
    client: OpenAI,
    model: str,
    image_path: str | Path,
    prompt: str,
) -> tuple[str | None, CompletionUsage | None]:
    """Send a single image to the model and return the plain-text transcription."""
    b64 = _encode_image(image_path)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                ],
            }
        ],
    )

    return response.choices[0].message.content, response.usage


def batch_transcribe(
    service: dict,
    model: str,
    images_dir: str | Path,
    prompt: str,
    overwrite: bool = False,
    save_usage: bool = False,
) -> None:
    """Transcribe all images in a directory, saving one .md file per image.

    Output path: transcriptions/{sanitized_model_name}/{image_stem}.md
    Skips images that already have a transcription unless --overwrite is set.
    """
    images_dir = Path(images_dir)
    if not images_dir.exists():
        logging.error(f"Images directory '{images_dir}' does not exist.")
        sys.exit(1)

    model_dir = TRANSCRIPTIONS_DIR / _sanitize_model_name(model)
    model_dir.mkdir(parents=True, exist_ok=True)

    client = _client(service)

    images = sorted([p for p in images_dir.iterdir() if _is_image(p)])
    if not images:
        logging.warning(f"No image files found in '{images_dir}'.")
        return

    logging.info(f"Found {len(images)} image(s) in '{images_dir}'.")

    usage_cumulative = {"completion_tokens": 0, "prompt_tokens": 0, "total_tokens": 0}

    for image in images:
        out_path = model_dir / f"{image.stem}.md"

        if out_path.exists() and not overwrite:
            logging.info(f"[SKIP] {image.name} — transcription already exists.")
            continue

        logging.info(f"[TRANSCRIBE] {image.name}")
        try:
            content, usage = transcribe_image(client, model, image, prompt)
        except Exception as e:
            logging.error(f"[ERROR] {image.name}: {e}")
            continue

        out_path.write_text(content or "", encoding="utf-8")
        logging.info(f"[SAVED] {out_path}")

        if save_usage and usage:
            usage_cumulative["completion_tokens"] += getattr(usage, "completion_tokens", 0) or 0
            usage_cumulative["prompt_tokens"] += getattr(usage, "prompt_tokens", 0) or 0
            usage_cumulative["total_tokens"] += getattr(usage, "total_tokens", 0) or 0

    if save_usage:
        _append_usage(model, images_dir, usage_cumulative)


def _append_usage(model: str, images_dir: Path, usage: dict) -> None:
    """Append a usage record to evaluations/usage.json."""
    EVALUATIONS_DIR.mkdir(parents=True, exist_ok=True)
    usage_file = EVALUATIONS_DIR / "usage.json"

    records: list = []
    if usage_file.exists():
        try:
            records = json.loads(usage_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    records.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": model,
            "source_folder": str(images_dir),
            **usage,
        }
    )

    usage_file.write_text(json.dumps(records, indent=4, ensure_ascii=False), encoding="utf-8")
    logging.info(f"Usage data appended to '{usage_file}'.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transcribe images using OpenAI-compatible LLM services (GRIT, Dream Lab, etc.)."
    )

    parser.add_argument(
        "--service",
        default="grit",
        choices=list(SERVICES.keys()),
        help="LLM service to use (default: grit).",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model ID to use for transcription. Required unless --list-models is set.",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models for the selected service and exit.",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=DEFAULT_PROMPT,
        help="Transcription prompt string, or path to a .txt file (default: standard OCR prompt).",
    )

    img_group = parser.add_mutually_exclusive_group()
    img_group.add_argument(
        "--images",
        type=str,
        default=None,
        metavar="DIR",
        help="Directory of images to transcribe (default: images/).",
    )
    img_group.add_argument(
        "--image",
        type=str,
        default=None,
        metavar="FILE",
        help="Single image file to transcribe.",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Re-transcribe images that already have an output file (default: skip).",
    )
    parser.add_argument(
        "--usage-data",
        action="store_true",
        help="Save cumulative token usage to evaluations/usage.json.",
    )
    parser.add_argument(
        "--enforce-compatible",
        action="store_true",
        help=(
            "For --service grit, only allow models marked as compatible in local tests. "
            "Blocks incompatible, uncertain, slow, or unknown models."
        ),
    )

    args = parser.parse_args()

    if args.list_models:
        list_models(args.service)
        return

    if not args.model:
        parser.error("--model is required unless --list-models is set.")

    service_config = _validate_service(parser, args.service)
    if args.service == "grit":
        try:
            _log_grit_model_guidance(args.model, enforce_compatible=args.enforce_compatible)
        except ValueError as e:
            parser.error(str(e))

    prompt = _read_if_file(args.prompt)

    if args.image:
        image_path = Path(args.image)
        if not image_path.exists():
            parser.error(f"Image file '{image_path}' does not exist.")

        model_dir = TRANSCRIPTIONS_DIR / _sanitize_model_name(args.model)
        model_dir.mkdir(parents=True, exist_ok=True)
        out_path = model_dir / f"{image_path.stem}.md"

        if out_path.exists() and not args.overwrite:
            print(f"Transcription already exists at '{out_path}'. Use --overwrite to replace.")
            return

        client = _client(service_config)
        logging.info(f"[TRANSCRIBE] {image_path.name}")
        try:
            content, usage = transcribe_image(client, args.model, image_path, prompt)
        except Exception as e:
            logging.error(f"[ERROR] {e}")
            sys.exit(1)

        out_path.write_text(content or "", encoding="utf-8")
        logging.info(f"[SAVED] {out_path}")

        if args.usage_data and usage:
            _append_usage(
                args.model,
                image_path.parent,
                {
                    "completion_tokens": getattr(usage, "completion_tokens", 0) or 0,
                    "prompt_tokens": getattr(usage, "prompt_tokens", 0) or 0,
                    "total_tokens": getattr(usage, "total_tokens", 0) or 0,
                },
            )

    else:
        images_dir = Path(args.images) if args.images else WORKING_DIR / "images"
        batch_transcribe(
            service=service_config,
            model=args.model,
            images_dir=images_dir,
            prompt=prompt,
            overwrite=args.overwrite,
            save_usage=args.usage_data,
        )


if __name__ == "__main__":
    main()
