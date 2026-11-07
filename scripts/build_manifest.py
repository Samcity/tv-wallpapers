#!/usr/bin/env python3
"""Prepare photos for Projectivy Overflight and write its JSON manifests.

Layout:
    photos/<collection>/<image files>

What it does:
  1. Optimises images in place: fixes phone rotation (EXIF), converts HEIC/PNG/WEBP
     to JPEG, and shrinks anything bigger than 4K so the TV loads them quickly.
  2. Writes wallpapers.json (every photo) and collections/<collection>.json
     (one per folder), in the format Overflight expects.

Usage:  python scripts/build_manifest.py <owner/repo> [branch]
"""
import json
import sys
import urllib.parse
from pathlib import Path

from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "photos"
COLLECTIONS = ROOT / "collections"
MAX_W, MAX_H = 3840, 2160
JPEG_QUALITY = 90
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}


def optimise(path: Path) -> Path:
    """Return the path of a TV-friendly JPEG version of `path` (may be itself)."""
    with Image.open(path) as im:
        was_rotated = im.getexif().get(0x0112, 1) != 1
        rotated = ImageOps.exif_transpose(im) if was_rotated else im
        too_big = rotated.width > MAX_W or rotated.height > MAX_H
        needs_convert = path.suffix.lower() not in {".jpg", ".jpeg"}
        if not (too_big or was_rotated or needs_convert):
            return path
        out = rotated.convert("RGB")
        out.thumbnail((MAX_W, MAX_H), Image.LANCZOS)
    target = path.with_suffix(".jpg")
    out.save(target, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
    if target != path:
        path.unlink()
    print(f"optimised: {target.relative_to(ROOT)}")
    return target


def pretty(name: str) -> str:
    return name.replace("_", " ").replace("-", " ").strip().title()


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    repo = sys.argv[1]
    branch = sys.argv[2] if len(sys.argv) > 2 else "main"
    base = f"https://raw.githubusercontent.com/{repo}/{branch}/"

    everything, per_collection = [], {}
    for path in sorted(PHOTOS.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        path = optimise(path)
        rel = path.relative_to(ROOT).as_posix()
        collection = path.relative_to(PHOTOS).parts[0] if path.parent != PHOTOS else "uncategorised"
        url = base + urllib.parse.quote(rel)
        entry = {
            "location": pretty(collection),
            "title": pretty(path.stem),
            "author": "",
            "url_img": url,
            # Overflight only reads url_img when its "fallback" setting is on, so the
            # same link goes in every quality field too. It still shows as a picture,
            # because Overflight treats a link that matches url_img as an image.
            "url_1080p": url,
            "url_1080p_hdr": url,
            "url_4k": url,
            "url_4k_hdr": url,
        }
        everything.append(entry)
        per_collection.setdefault(collection, []).append(entry)

    (ROOT / "wallpapers.json").write_text(json.dumps(everything, indent=2) + "\n")
    COLLECTIONS.mkdir(exist_ok=True)
    for old in COLLECTIONS.glob("*.json"):
        old.unlink()
    for name, entries in per_collection.items():
        (COLLECTIONS / f"{name}.json").write_text(json.dumps(entries, indent=2) + "\n")
    print(f"{len(everything)} photos across {len(per_collection)} collection(s)")


if __name__ == "__main__":
    main()
