#!/usr/bin/env python3
"""
Convert images in the images folder (including subfolders) to WebP format.
Output is saved to the output folder, preserving the directory structure.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps, ImageSequence

# Supported image extensions
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp"}

# Paths relative to script location
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_FOLDER = SCRIPT_DIR / "images"
OUTPUT_FOLDER = SCRIPT_DIR / "output"


@dataclass(frozen=True)
class ConvertOptions:
    quality: int = 85
    lossless: bool = False
    method: int = 4
    keep_metadata: bool = False


def _normalize_mode(img: Image.Image) -> Image.Image:
    """Convert to a mode WebP supports while keeping transparency."""
    has_alpha = img.mode in ("RGBA", "LA", "PA") or (img.mode == "P" and "transparency" in img.info)
    if has_alpha:
        return img.convert("RGBA") if img.mode != "RGBA" else img
    return img.convert("RGB") if img.mode != "RGB" else img


def convert_to_webp(input_path: Path, output_path: Path, quality: int = 85, options: ConvertOptions | None = None) -> bool:
    """Convert a single image to WebP format."""
    options = options or ConvertOptions(quality=quality)
    try:
        with Image.open(input_path) as img:
            output_path.parent.mkdir(parents=True, exist_ok=True)

            save_kwargs: dict = {
                "format": "WEBP",
                "quality": options.quality,
                "lossless": options.lossless,
                "method": options.method,
            }
            animated = getattr(img, "is_animated", False) and img.n_frames > 1
            # exif_transpose rotates the pixels and drops the orientation tag from the copy's EXIF.
            source = img if animated else ImageOps.exif_transpose(img)
            if options.keep_metadata:
                if img.info.get("icc_profile"):
                    save_kwargs["icc_profile"] = img.info["icc_profile"]
                exif = source.getexif()
                if exif:
                    save_kwargs["exif"] = exif.tobytes()

            if animated:
                frames, durations = [], []
                for frame in ImageSequence.Iterator(img):
                    durations.append(frame.info.get("duration", img.info.get("duration", 100)))
                    frames.append(_normalize_mode(frame.copy()))
                frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=durations,
                    loop=img.info.get("loop", 0),
                    **save_kwargs,
                )
            else:
                _normalize_mode(source).save(output_path, **save_kwargs)
        return True
    except Exception as e:
        print(f"  错误: {e}")
        return False


def _is_up_to_date(input_path: Path, output_path: Path) -> bool:
    return output_path.exists() and output_path.stat().st_mtime >= input_path.stat().st_mtime


def collect_jobs(input_folder: Path, output_folder: Path) -> list[tuple[Path, Path]]:
    jobs = []
    for root, _, files in os.walk(input_folder):
        root_path = Path(root)
        out_dir = output_folder / root_path.relative_to(input_folder)
        for filename in sorted(files):
            if Path(filename).suffix.lower() in IMAGE_EXTENSIONS:
                input_path = root_path / filename
                jobs.append((input_path, out_dir / (input_path.stem + ".webp")))
    return jobs


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量将图片转换为 WebP 格式（保留目录结构）。")
    parser.add_argument("-i", "--input", type=Path, default=INPUT_FOLDER, help="输入文件夹（默认: ./images）")
    parser.add_argument("-o", "--output", type=Path, default=OUTPUT_FOLDER, help="输出文件夹（默认: ./output）")
    parser.add_argument("-q", "--quality", type=int, default=85, help="质量 0-100（默认: 85）")
    parser.add_argument("--lossless", action="store_true", help="使用无损压缩")
    parser.add_argument("--method", type=int, default=4, choices=range(7), metavar="0-6", help="压缩速度/体积权衡，越大越慢越小（默认: 4）")
    parser.add_argument("--keep-metadata", action="store_true", help="保留 EXIF 与 ICC 色彩配置")
    parser.add_argument("--force", action="store_true", help="即使输出已存在且较新也重新转换")
    parser.add_argument("--copy-webp", action="store_true", help="把已是 WebP 的文件复制到输出目录（默认跳过）")
    parser.add_argument("-j", "--jobs", type=int, default=os.cpu_count() or 1, help="并行任务数（默认: CPU 核心数）")
    args = parser.parse_args(argv)
    if not 0 <= args.quality <= 100:
        parser.error("--quality 必须在 0 到 100 之间")
    if args.jobs < 1:
        parser.error("--jobs 必须大于 0")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_folder: Path = args.input.resolve()
    output_folder: Path = args.output.resolve()

    if not input_folder.exists():
        print(f"输入文件夹不存在: {input_folder}")
        return 1

    output_folder.mkdir(parents=True, exist_ok=True)
    options = ConvertOptions(quality=args.quality, lossless=args.lossless, method=args.method, keep_metadata=args.keep_metadata)
    converted = failed = skipped = 0

    print(f"输入文件夹: {input_folder}")
    print(f"输出文件夹: {output_folder}")
    print("-" * 50)

    pending: list[tuple[Path, Path]] = []
    for input_path, output_path in collect_jobs(input_folder, output_folder):
        rel_input = input_path.relative_to(input_folder)
        if input_path.suffix.lower() == ".webp":
            if args.copy_webp and (args.force or not _is_up_to_date(input_path, output_path)):
                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(input_path, output_path)
                print(f"复制 (已是 WebP): {rel_input}")
            else:
                print(f"跳过 (已是 WebP): {rel_input}")
            skipped += 1
            continue
        if not args.force and _is_up_to_date(input_path, output_path):
            print(f"跳过 (已是最新): {rel_input}")
            skipped += 1
            continue
        pending.append((input_path, output_path))

    def run(job: tuple[Path, Path]) -> bool:
        input_path, output_path = job
        print(f"转换: {input_path.relative_to(input_folder)} -> {output_path.relative_to(output_folder)}")
        return convert_to_webp(input_path, output_path, options=options)

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for ok in pool.map(run, pending):
            if ok:
                converted += 1
            else:
                failed += 1

    print("-" * 50)
    print(f"完成: 成功 {converted}, 失败 {failed}, 跳过 {skipped}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
