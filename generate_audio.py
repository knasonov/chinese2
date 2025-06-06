"""Generate audio files for all stories using Piper TTS.

Installation instructions:
    1. Install Piper: `pip install piper-tts` or build from source at
       https://github.com/rhasspy/piper .
    2. Download a Mandarin voice model from the Piper releases page and
       note the path to the `.onnx` model file.
    3. Run this script providing the model path, for example:

           python generate_audio.py --model zh_CN.onnx

    Output `.wav` files will be written to the `stories_audio` directory.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


DEFAULT_STORIES_DIR = "stories"
DEFAULT_OUTPUT_DIR = "stories_audio"


def synthesize(text_file: Path, model: Path, out_file: Path, length_scale: float) -> None:
    """Run Piper to synthesize *text_file* into *out_file*."""
    cmd = [
        "piper",
        "--model",
        str(model),
        "--input_file",
        str(text_file),
        "--output_file",
        str(out_file),
        "--length_scale",
        str(length_scale),
    ]
    subprocess.run(cmd, check=True)



def main() -> None:
    parser = argparse.ArgumentParser(description="Generate audio for all stories")
    parser.add_argument("--model", required=True, help="Path to Piper voice model (.onnx)")
    parser.add_argument(
        "--stories-dir",
        default=DEFAULT_STORIES_DIR,
        help="Directory containing story .txt files",
    )
    parser.add_argument(
        "--out-dir",
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where audio files will be written",
    )
    parser.add_argument(
        "--length-scale",
        type=float,
        default=1.1,
        help="Value above 1 slows down speech; below 1 speeds it up",
    )
    args = parser.parse_args()

    stories_dir = Path(args.stories_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model = Path(args.model)

    for text_path in sorted(stories_dir.glob("*.txt")):
        out_file = out_dir / f"{text_path.stem}.wav"
        print(f"Synthesizing {text_path} -> {out_file}")
        synthesize(text_path, model, out_file, args.length_scale)


if __name__ == "__main__":
    main()
