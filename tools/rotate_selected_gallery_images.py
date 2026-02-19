from pathlib import Path
from PIL import Image

SITE_ROOT = Path(__file__).resolve().parents[1]

TARGETS = [
    "images/projects/gym pic.jpeg",
    "images/_thumbs/projects/gym pic.jpg",
    "images/projects/gym pic inside.jpeg",
    "images/_thumbs/projects/gym pic inside.jpg",
    "images/boats/after dash.jpeg",
    "images/_thumbs/boats/after dash.jpg",
    "images/boats/before1.jpeg",
    "images/_thumbs/boats/before1.jpg",
    "images/boats/big boat sub.jpeg",
    "images/_thumbs/boats/big boat sub.jpg",
    "images/boats/big boat wiring.jpeg",
    "images/_thumbs/boats/big boat wiring.jpg",
    "images/boats/big boat wiring 2.jpeg",
    "images/_thumbs/boats/big boat wiring 2.jpg",
    "images/boats/big boat wiring full.jpeg",
    "images/_thumbs/boats/big boat wiring full.jpg",
    "images/boats/carbs.jpeg",
    "images/_thumbs/boats/carbs.jpg",
    "images/boats/flooring.jpeg",
    "images/_thumbs/boats/flooring.jpg",
    "images/boats/fuel pump.jpeg",
    "images/_thumbs/boats/fuel pump.jpg",
    "images/boats/launching pic.jpeg",
    "images/_thumbs/boats/launching pic.jpg",
    "images/boats/trigger.jpeg",
    "images/_thumbs/boats/trigger.jpg",
]


def rotate_right_90(path: Path) -> None:
    with Image.open(path) as img:
        rotated = img.rotate(-90, expand=True)
        if path.suffix.lower() in {".jpg", ".jpeg"} and rotated.mode in {"RGBA", "P"}:
            rotated = rotated.convert("RGB")

        save_kwargs = {}
        exif = img.getexif()
        if exif:
            save_kwargs["exif"] = exif.tobytes()

        rotated.save(path, **save_kwargs)


def main() -> int:
    rotated_count = 0
    missing = []
    errors = []

    for rel in TARGETS:
        abs_path = SITE_ROOT / rel
        if not abs_path.exists():
            missing.append(rel)
            continue

        try:
            rotate_right_90(abs_path)
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
