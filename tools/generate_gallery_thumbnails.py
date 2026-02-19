from __future__ import annotations

from pathlib import Path
import argparse

from PIL import Image


SITE_ROOT = Path(__file__).resolve().parents[1]
IMAGES_ROOT = SITE_ROOT / "images"
THUMBS_ROOT = IMAGES_ROOT / "_thumbs"
SECTIONS = ["projects", "boats", "fabrication"]
SOURCE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".svg"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate lightweight gallery thumbnails.")
    parser.add_argument("--max-size", type=int, default=720, help="Longest edge in pixels (default: 720).")
    parser.add_argument("--quality", type=int, default=82, help="JPEG quality 1-100 (default: 82).")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing thumbnails.")
    return parser


def iter_source_files(section: str):
    section_dir = IMAGES_ROOT / section
    if not section_dir.exists():
        return []

    return [
        path
        for path in sorted(section_dir.rglob("*"), key=lambda p: p.as_posix().lower())
        if path.is_file() and path.suffix.lower() in SOURCE_EXTENSIONS
    ]


def write_thumbnail(source: Path, target: Path, max_size: int, quality: int) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        rgb = image.convert("RGB")
        rgb.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        rgb.save(target, format="JPEG", quality=quality, optimize=True, progressive=True)


def main() -> int:
    args = build_parser().parse_args()
    max_size = max(200, min(2000, args.max_size))
    quality = max(1, min(100, args.quality))

    generated = 0
    skipped = 0
    failed = 0

    for section in SECTIONS:
        files = iter_source_files(section)
        if not files:
            print(f"[{section}] No source files found.")
            continue

        print(f"[{section}] {len(files)} source file(s).")
        for source in files:
            relative_in_section = source.relative_to(IMAGES_ROOT / section)
            target = (THUMBS_ROOT / section / relative_in_section).with_suffix(".jpg")

            if target.exists() and not args.overwrite:
                skipped += 1
                continue

            try:
                write_thumbnail(source, target, max_size=max_size, quality=quality)
                generated += 1
            except Exception as err:
                failed += 1
                print(f"  error {source.relative_to(SITE_ROOT).as_posix()}: {err}")

    print("\nSummary:")
    print(f"  generated: {generated}")
    print(f"  skipped:   {skipped}")
    print(f"  failed:    {failed}")

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
