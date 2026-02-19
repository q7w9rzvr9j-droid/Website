from pathlib import Path
from PIL import Image

SITE_ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    SITE_ROOT / "images/projects/Portable Standing Desk.jpeg",
    SITE_ROOT / "images/projects/Portable Standing Desk Electronics.jpeg",
]

for path in TARGETS:
    with Image.open(path) as img:
        rotated = img.rotate(-90, expand=True)
        exif = img.getexif()
        kwargs = {"exif": exif.tobytes()} if exif else {}
        rotated.save(path, **kwargs)
    print(f"rotated {path.relative_to(SITE_ROOT).as_posix()}")
