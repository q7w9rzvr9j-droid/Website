from __future__ import annotations

from pathlib import Path
import argparse
import subprocess
import sys


SITE_ROOT = Path(__file__).resolve().parents[1]
IMAGES_ROOT = SITE_ROOT / "images"
DEFAULT_SECTIONS = ["projects", "boats", "fabrication"]
HEIC_EXTENSIONS = {".heic", ".heif"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert HEIC/HEIF files in image sections to JPG copies."
    )
    parser.add_argument(
        "--sections",
        nargs="+",
        default=DEFAULT_SECTIONS,
        help="Image sections under images/ to scan (default: projects boats fabrication).",
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=92,
        help="JPEG quality from 1-100 (default: 92).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing JPG files if present.",
    )
    parser.add_argument(
        "--delete-original",
        action="store_true",
        help="Delete source HEIC/HEIF files after successful conversion.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would convert without writing files.",
    )
    parser.add_argument(
        "--update-gallery",
        action="store_true",
        help="Run tools/generate_gallery_json.py after conversion.",
    )
    return parser


def load_imaging_dependencies() -> tuple[object, object] | None:
    try:
        from PIL import Image
        from pillow_heif import register_heif_opener
    except Exception:
        return None

    register_heif_opener()
    return Image, register_heif_opener


def iter_heic_files(section: str):
    section_dir = IMAGES_ROOT / section
    if not section_dir.exists():
        return []
    return [
        path
        for path in sorted(section_dir.rglob("*"), key=lambda p: p.as_posix().lower())
        if path.is_file() and path.suffix.lower() in HEIC_EXTENSIONS
    ]


def convert_file(source: Path, target: Path, image_module, quality: int, dry_run: bool) -> bool:
    if dry_run:
        return True

    with image_module.open(source) as img:
        rgb = img.convert("RGB")
        exif = img.getexif()
        rgb.save(target, format="JPEG", quality=quality, optimize=True, exif=exif.tobytes())
    return True


def run_gallery_refresh() -> int:
    cmd = [sys.executable, str(SITE_ROOT / "tools" / "generate_gallery_json.py")]
    proc = subprocess.run(cmd, cwd=SITE_ROOT)
    return proc.returncode


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    quality = max(1, min(args.quality, 100))
    deps = load_imaging_dependencies()
    if deps is None:
        print("Missing dependencies. Install with:")
        print("  pip install pillow pillow-heif")
        return 1

    image_module, _ = deps

    converted = 0
    skipped = 0
    deleted = 0
    failed = 0

    for section in args.sections:
        section_files = iter_heic_files(section)
        if not section_files:
            print(f"[{section}] No HEIC/HEIF files found.")
            continue

        print(f"[{section}] Found {len(section_files)} file(s).")
        for source in section_files:
            target = source.with_suffix(".jpg")
            rel_source = source.relative_to(SITE_ROOT).as_posix()
            rel_target = target.relative_to(SITE_ROOT).as_posix()

            if target.exists() and not args.overwrite:
                skipped += 1
                print(f"  skip  {rel_source} -> {rel_target} (exists)")
                continue

            try:
                ok = convert_file(source, target, image_module, quality=quality, dry_run=args.dry_run)
                if ok:
                    converted += 1
                    action = "would convert" if args.dry_run else "convert"
                    print(f"  {action}  {rel_source} -> {rel_target}")

                    if args.delete_original and not args.dry_run:
                        source.unlink(missing_ok=True)
                        deleted += 1
                        print(f"  delete   {rel_source}")
            except Exception as err:
                failed += 1
                print(f"  error    {rel_source}: {err}")

    print("\nSummary:")
    print(f"  converted: {converted}")
    print(f"  skipped:   {skipped}")
    print(f"  deleted:   {deleted}")
    print(f"  failed:    {failed}")

    if args.update_gallery and not args.dry_run:
        rc = run_gallery_refresh()
        if rc != 0:
            print("Gallery manifest refresh failed.")
            return rc

    return 0 if failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
