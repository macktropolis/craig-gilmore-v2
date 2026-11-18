#!/usr/bin/env python3
"""Generate WebP thumbnails for every upload the site references.

Scans src/ for /content/uploads/... image paths and writes a resized WebP copy
to public/content/thumbs/<same path>.webp (max 800 px wide). Galleries and cards
show the thumbnail; the lightbox still opens the full-size original.

Also writes src/data/thumbs.json mapping each upload path to its thumbnail
path and size, which src/data/images.ts reads at build time.

Re-run after adding new images:  python3 scripts/make-thumbs.py
Existing thumbnails are skipped unless the original is newer. Needs Pillow.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / 'public'
MAX_W = 800
QUALITY = 74
REF = re.compile(r"/content/uploads/[^\"' )\n]+?\.(?:jpe?g|png|webp|gif)", re.I)


def referenced() -> list[str]:
    refs: set[str] = set()
    for f in (ROOT / 'src').rglob('*'):
        if f.suffix in {'.astro', '.md', '.ts', '.mdx'}:
            refs.update(REF.findall(f.read_text(encoding='utf-8')))
    return sorted(refs)


def main() -> None:
    manifest: dict[str, dict] = {}
    made = skipped = missing = 0
    for ref in referenced():
        src = PUBLIC / ref.lstrip('/')
        if not src.exists():
            print('missing:', ref)
            missing += 1
            continue
        rel = Path(ref.lstrip('/')).relative_to('content/uploads')
        rel = rel.with_name(rel.name + '.webp')  # keep the original extension: a.jpg and a.png must not collide
        out = PUBLIC / 'content' / 'thumbs' / rel
        thumb_url = '/content/thumbs/' + rel.as_posix()
        if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
            with Image.open(out) as t:
                w, h = t.size
            skipped += 1
        else:
            with Image.open(src) as im:
                im = ImageOps.exif_transpose(im)
                im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
                if im.width > MAX_W:
                    im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
                out.parent.mkdir(parents=True, exist_ok=True)
                im.save(out, 'WEBP', quality=QUALITY, method=6)
                w, h = im.size
            made += 1
        manifest[ref] = {'src': thumb_url, 'width': w, 'height': h}

    (ROOT / 'src' / 'data' / 'thumbs.json').write_text(json.dumps(manifest, indent=1, sort_keys=True) + '\n')
    print(f'{made} made, {skipped} up to date, {missing} missing, {len(manifest)} in manifest')


if __name__ == '__main__':
    main()
