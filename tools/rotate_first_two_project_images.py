from pathlib import Path
from PIL import Image

SITE_ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    "images/projects/Portable Standing Desk.jpg",
    "images/_thumbs/projects/Portable Standing Desk.jpg",
    "images/projects/Portable Standing Desk Electronics.jpg",
    "images/_thumbs/projects/Portable Standing Desk Electronics.jpg",
]


def rotate_right_90(path: Path) -> None:
    with Image.open(path) as img:
        rotated = img.rotate(-90, expand=True)
        if path.suffix.lower() in {".jpg", ".jpeg"} and rotated.mode in {"RGBA", "P"}:
            rotated = rotated.convert("RGB")
        exif = img.getexif()
        save_kwargs = {"exif": exif.tobytes()} if exif else {}
        rotated.save(path, **save_kwargs)


def main() -> int:
    rotated_count = 0
    missing = []
    errors = []

    for rel in TARGETS:
        file_path = SITE_ROOT / rel
        if not file_path.exists():
            missing.append(rel)
            continue
        try:
            rotate_right_90(file_path)
            rotated_count += 1
        except Exception as err:
            errors.append((rel, str(err)))

    print(f"Rotated: {rotated_count}")
    if missing:
        print("Missing:")
        for rel in missing:
            print(f"  - {rel}")
    if errors:
        print("Errors:")
        for rel, msg in errors:
            print(f"  - {rel}: {msg}")

    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
