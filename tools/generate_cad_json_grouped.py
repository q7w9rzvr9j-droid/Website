from pathlib import Path
import json
import re

SITE_ROOT = Path(__file__).resolve().parents[1]
CAD_DIR = SITE_ROOT / "docs" / "cad"
OUT_JSON = SITE_ROOT / "data" / "cad.json"

PLACEHOLDER_THUMB = "assets/placeholders/cad1.svg"

def slugify(text: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80] if s else "cad-item"

def nice_label(pdf_path: Path) -> str:
    name = pdf_path.stem
    name = name.replace("_", " ").replace("-", " ").strip()
    return name[:60] if name else "PDF"

def group_key(filename: str) -> str:
    stem = re.sub(r"\.pdf$", "", filename, flags=re.I).strip()
    if " - " in stem:
        return stem.split(" - ")[0].strip()
    if "_" in stem:
        return stem.split("_")[0].strip()
    words = stem.split()
    return " ".join(words[:2]) if len(words) >= 2 else stem

items = []

if not CAD_DIR.exists():
    raise SystemExit(f"❌ Can't find {CAD_DIR}. Put your PDFs in docs/cad/")

pdfs = sorted(CAD_DIR.glob("*.pdf"), key=lambda p: p.name.lower())
groups = {}

for pdf in pdfs:
    key = group_key(pdf.name)
    groups.setdefault(key, []).append(pdf)

for key in sorted(groups.keys(), key=lambda s: s.lower()):
    drawings = []
    for pdf in groups[key]:
        rel = pdf.relative_to(SITE_ROOT).as_posix()
        drawings.append({"label": nice_label(pdf), "file": rel})

    items.append({
        "slug": slugify(key),
        "title": key,
        "subtitle": f"{len(drawings)} drawing file(s)",
        "thumb": PLACEHOLDER_THUMB,
        "tags": [],
        "drawings": drawings,
        "images": [],
        "notes": ""
    })

OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
OUT_JSON.write_text(json.dumps(items, indent=2), encoding="utf-8")

print(f"✅ Wrote {OUT_JSON} with {len(items)} CAD card(s).")
