"""Generate favicons and touch icons from Craig's white signature logo.

Usage: python3 scripts/make-icons.py
Writes favicon.ico, apple-touch-icon.png, icon-192.png and icon-512.png to public/.
"""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'public/images/craig-logo-white-nobg@3x.webp'
OUT = ROOT / 'public'
BG = (9, 9, 9, 255)  # --bg in global.css

logo = Image.open(SRC).convert('RGBA')
logo = logo.crop(logo.split()[3].getbbox())  # trim transparent edges


def tile(size: int, padding: float, radius: float = 0.0) -> Image.Image:
    """Logo centred on a dark square; padding and radius are fractions of size."""
    scale = 4  # draw large, then downsample for smooth edges
    big = size * scale
    canvas = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    mask = Image.new('L', (big, big), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, big - 1, big - 1), radius=int(big * radius), fill=255)
    canvas.paste(Image.new('RGBA', (big, big), BG), mask=mask)

    box = int(big * (1 - 2 * padding))
    fitted = logo.copy()
    fitted.thumbnail((box, box), Image.LANCZOS)
    canvas.alpha_composite(fitted, ((big - fitted.width) // 2, (big - fitted.height) // 2))
    return canvas.resize((size, size), Image.LANCZOS)


# Browser tab icon: rounded tile, tight padding so the signature stays legible at 16px.
tile(256, padding=0.08, radius=0.2).save(OUT / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])

# iOS home screen: opaque square (iOS rounds the corners itself), more breathing room.
tile(180, padding=0.16).convert('RGB').save(OUT / 'apple-touch-icon.png', optimize=True)

# Android / PWA manifest icons.
for size in (192, 512):
    tile(size, padding=0.16).convert('RGB').save(OUT / f'icon-{size}.png', optimize=True)

print('Icons written to', OUT)
