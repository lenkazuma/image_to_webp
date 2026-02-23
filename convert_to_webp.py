#!/usr/bin/env python3
"""
Convert images in the images folder (including subfolders) to WebP format.
Output is saved to the output folder, preserving the directory structure.
"""

import os
from pathlib import Path

from PIL import Image

# Supported image extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp"}

# Paths relative to script location
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_FOLDER = SCRIPT_DIR / "images"
OUTPUT_FOLDER = SCRIPT_DIR / "output"


def convert_to_webp(input_path: Path, output_path: Path, quality: int = 85) -> bool:
    """Convert a single image to WebP format."""
    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (for RGBA, we use the alpha channel)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            output_path.parent.mkdir(parents=True, exist_ok=True)

            save_kwargs = {"format": "WEBP"}
            if img.mode == "RGBA":
                save_kwargs["quality"] = quality
                save_kwargs["lossless"] = False
            else:
                save_kwargs["quality"] = quality

            img.save(output_path, **save_kwargs)
        return True
    except Exception as e:
        print(f"  错误: {e}")
        return False


def main():
    if not INPUT_FOLDER.exists():
        print(f"输入文件夹不存在: {INPUT_FOLDER}")
        return

    OUTPUT_FOLDER.mkdir(exist_ok=True)
    converted = 0
    failed = 0
    skipped = 0

    print(f"输入文件夹: {INPUT_FOLDER}")
    print(f"输出文件夹: {OUTPUT_FOLDER}")
    print("-" * 50)

    for root, _, files in os.walk(INPUT_FOLDER):
        root_path = Path(root)
        rel_path = root_path.relative_to(INPUT_FOLDER)
        out_dir = OUTPUT_FOLDER / rel_path

        for filename in files:
            ext = Path(filename).suffix.lower()
            if ext not in IMAGE_EXTENSIONS:
                continue

            input_path = root_path / filename
            output_name = input_path.stem + ".webp"
            output_path = out_dir / output_name

            # Skip if already WebP and it's a simple same-format case
            if ext == ".webp":
                skipped += 1
                print(f"跳过 (已是 WebP): {rel_path / filename}")
                continue

            print(f"转换: {rel_path / filename} -> {rel_path / output_name}")

            if convert_to_webp(input_path, output_path):
                converted += 1
            else:
                failed += 1

    print("-" * 50)
    print(f"完成: 成功 {converted}, 失败 {failed}, 跳过 {skipped}")


if __name__ == "__main__":
    main()
