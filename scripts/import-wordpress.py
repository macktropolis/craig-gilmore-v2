"""One-off import of portfolio projects and blog posts from the WordPress REST API.

Usage: python3 scripts/import-wordpress.py <dir with pages/portfolio/posts/media/tax-*.json>
Writes src/content/portfolio/*.md and src/content/news/*.md, and prints images that
are referenced but missing from public/content/uploads/.
"""
from __future__ import annotations

import html, json, re, sys
from pathlib import Path

SRC = Path(sys.argv[1])
ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / 'public'

load = lambda name: json.loads((SRC / name).read_text())
media = {m['id']: m for m in load('media.json')}
types = {t['id']: t['slug'] for t in load('tax-portfolio_types.json')}
ptags = {t['id']: t['slug'] for t in load('tax-portfolio-tags.json')}
companies = {t['id']: t['slug'] for t in load('tax-companies.json')}

# The only posts written by Craig; the rest of the WordPress blog is injected spam.
REAL_POSTS = {
    'heroes-convention-2024-guest-appearance', 'first-kill-premiere-on-netflix-6-10-22',
    'new-storyboards-from-morbius-for-sony-marvel-studios', 'art-for-heavy-metal-band-mx',
    'mother-mayhem-logomascot-design', 'amc-com-behind-the-walking-dead',
    'another-new-walking-dead-season-4-clip',
}

missing: set[str] = set()


def local(url: str) -> str | None:
    """Map any WordPress/Jetpack image URL to its /content/uploads/ path."""
    m = re.search(r'/wp-content/uploads/([^?#"\s]+)', html.unescape(url))
    if not m:
        return None
    path = '/content/uploads/' + m.group(1)
    if not (PUBLIC / path.lstrip('/')).exists():
        missing.add(path)
    return path


def clean(s: str) -> str:
    s = html.unescape(re.sub(r'<[^>]+>', '', s))
    return re.sub(r'\s+', ' ', s).strip()


def extract(content: str):
    """Return (images, youtube ids, description html) from post content."""
    images, seen = [], set()

    def add(src, caption):
        if src and src not in seen:
            seen.add(src)
            images.append({'src': src, 'caption': caption})

    for fig in re.findall(r'<figure[\s\S]*?</figure>', content):
        a = re.search(r'<a[^>]+href="([^"]+)"', fig)
        img = re.search(r'<img[^>]+>', fig)
        cap = re.search(r'<figcaption[^>]*>([\s\S]*?)</figcaption>', fig)
        alt = re.search(r'alt="([^"]*)"', img.group(0)) if img else None
        href = a.group(1) if a and re.search(r'\.(jpe?g|png|gif|webp)', a.group(1), re.I) else None
        srcm = re.search(r'src="([^"]+)"', img.group(0)) if img else None
        src = local(href) if href else (local(re.sub(r'-\d+x\d+(?=\.\w+)', '', srcm.group(1))) if srcm else None)
        add(src, clean(cap.group(1)) if cap else clean(alt.group(1)) if alt else '')
    rest = re.sub(r'<figure[\s\S]*?</figure>', '', content)
    for a in re.finditer(r'<a[^>]+href="([^"]+\.(?:jpe?g|png|gif|webp)[^"]*)"[^>]*>\s*<img[^>]*?(?:alt="([^"]*)")?[^>]*>\s*</a>', rest, re.I):
        add(local(a.group(1)), clean(a.group(2) or ''))
    rest = re.sub(r'<a[^>]+href="[^"]+\.(?:jpe?g|png|gif|webp)[^"]*"[^>]*>\s*<img[^>]*>\s*</a>', '', rest, flags=re.I)
    for img in re.finditer(r'<img[^>]+>', rest):
        srcm = re.search(r'src="([^"]+)"', img.group(0))
        alt = re.search(r'alt="([^"]*)"', img.group(0))
        if srcm:
            add(local(re.sub(r'-\d+x\d+(?=\.\w+)', '', srcm.group(1))), clean(alt.group(1) if alt else ''))
    videos = list(dict.fromkeys(re.findall(r'youtube\.com/embed/([\w-]{11})', content)))

    rest = re.sub(r'<img[^>]*>|<iframe[\s\S]*?</iframe>|<span class="embed-youtube"[\s\S]*?</span>', '', rest)
    paras = []
    for p in re.findall(r'<p[^>]*>([\s\S]*?)</p>', rest):
        p = re.sub(r'<(?!/?(strong|em|b|i|a)\b)[^>]+>', '', p)
        p = re.sub(r'\s+', ' ', p).strip()
        p = re.sub(r'href="https?://(?:www\.)?craiggilmore\.net', 'href="', p)
        # Facebook hashtag links carry long tracking query strings; keep only the text.
        p = re.sub(r'<a[^>]+facebook\.com/hashtag/[^>]*>([^<]*)</a>', r' \1', p)
        if clean(p):
            paras.append(p)
    return images, videos, '\n\n'.join(paras)


def yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def featured(fid):
    m = media.get(fid)
    return local(m['source_url']) if m else None


# --- Portfolio projects ---------------------------------------------------
out = ROOT / 'src/content/portfolio'
out.mkdir(parents=True, exist_ok=True)
for item in load('portfolio.json'):
    title = clean(item['title']['rendered'])
    name, _, credit = title.partition(' – ')
    images, videos, body = extract(item['content']['rendered'])
    cover = featured(item['featured_media']) or (images[0]['src'] if images else None)
    if not images and cover:  # comics items are a single featured image
        images = [{'src': cover, 'caption': title}]
    fm = [
        '---',
        f'title: {yaml_str(name.strip())}',
        f'credit: {yaml_str(credit.strip())}' if credit else None,
        f'date: {item["date"][:10]}',
        f'types: {json.dumps([types[t] for t in item["portfolio_types"]])}',
        f'tags: {json.dumps([ptags[t] for t in item["portfolio-tags"]])}',
        # The "companies" taxonomy also tags a few studios; only comics get a publisher.
        f'publisher: {companies[item["companies"][0]]}' if item['companies'] and 10 in item['portfolio_types'] else None,
        f'cover: {yaml_str(cover)}' if cover else None,
        f'videos: {json.dumps(videos)}' if videos else None,
        'images:' if images else 'images: []',
        *[f'  - src: {yaml_str(i["src"])}\n    caption: {yaml_str(i["caption"])}' for i in images],
        '---',
    ]
    text = '\n'.join(l for l in fm if l is not None) + '\n'
    if body:
        text += '\n' + body + '\n'
    (out / f'{item["slug"]}.md').write_text(text)

# --- Blog posts -> news ---------------------------------------------------
news = ROOT / 'src/content/news'
for post in load('posts.json'):
    if post['slug'] not in REAL_POSTS:
        continue
    images, videos, body = extract(post['content']['rendered'])
    excerpt = clean(post['excerpt']['rendered']).replace(' [&hellip;]', '').replace('[…]', '').strip()
    excerpt = excerpt if len(excerpt) < 220 else excerpt[:200].rsplit(' ', 1)[0] + '…'
    image = featured(post['featured_media']) or (images[0]['src'] if images else None)
    blocks = [body] if body else []
    blocks += [f'![{i["caption"]}]({i["src"]})' for i in images if i['src'] != image]
    blocks += [f'<div class="video-embed"><iframe src="https://www.youtube-nocookie.com/embed/{v}" title="YouTube video" loading="lazy" allowfullscreen></iframe></div>' for v in videos]
    fm = [
        '---',
        f'title: {yaml_str(clean(post["title"]["rendered"]))}',
        f'date: {post["date"][:10]}',
        f'excerpt: {yaml_str(excerpt or clean(post["title"]["rendered"]))}',
        'tags: []',
        f'image: {yaml_str(image)}' if image else None,
        f'wpSlug: {post["slug"]}',
        '---',
    ]
    (news / f'{post["slug"]}.md').write_text('\n'.join(l for l in fm if l) + '\n\n' + '\n\n'.join(blocks) + '\n')

print('portfolio:', len(list(out.glob('*.md'))), 'news:', len(list(news.glob('*.md'))))
print('missing images:', len(missing))
for m in sorted(missing):
    print(' ', m)
