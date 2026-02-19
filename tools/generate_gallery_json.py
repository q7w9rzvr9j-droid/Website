from pathlib import Path
import json

SITE_ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = SITE_ROOT / "images"
THUMBS_DIR = IMAGES_DIR / "_thumbs"
OUT_JSON = SITE_ROOT / "data" / "gallery.json"

SECTIONS = ["projects", "boats", "fabrication"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg", ".heic", ".heif"}
PREFERRED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg", ".heic", ".heif"]


def list_images(section: str) -> list[dict[str, str]]:
    folder = IMAGES_DIR / section
    if not folder.exists():
        return []

    candidates: dict[str, dict[str, Path]] = {}
    for file_path in sorted(folder.rglob("*"), key=lambda p: p.as_posix().lower()):
        if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS:
            rel_no_ext = file_path.relative_to(folder).with_suffix("").as_posix().lower()
            bucket = candidates.setdefault(rel_no_ext, {})
            bucket[file_path.suffix.lower()] = file_path

    files: list[dict[str, str]] = []
    for rel_no_ext in sorted(candidates.keys()):
        options = candidates[rel_no_ext]
        chosen_path = None
        for ext in PREFERRED_EXTENSIONS:
            if ext in options:
                chosen_path = options[ext]
                break
        if chosen_path is not None:
            src_rel = chosen_path.relative_to(SITE_ROOT).as_posix()
            thumb_candidate = (THUMBS_DIR / section / chosen_path.relative_to(IMAGES_DIR / section)).with_suffix(".jpg")
            if thumb_candidate.exists():
                thumb_rel = thumb_candidate.relative_to(SITE_ROOT).as_posix()
            else:
                thumb_rel = src_rel
            files.append({"src": src_rel, "thumb": thumb_rel})
    return files


def main() -> None:
    payload = {section: list_images(section) for section in SECTIONS}
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    total = sum(len(v) for v in payload.values())
    print(f"Wrote {OUT_JSON} with {total} images across {len(SECTIONS)} sections.")


if __name__ == "__main__":
    main()
