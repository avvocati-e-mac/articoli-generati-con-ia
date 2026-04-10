#!/usr/bin/env python3
"""
render_authorship.py — Rende visibili le annotazioni di iA Writer su GitHub Pages.

Uso:
  # Renderizza un singolo articolo:
  python scripts/render_authorship.py articoli/mio-articolo.md

  # Aggiorna README.md con la lista degli articoli:
  python scripts/render_authorship.py --update-readme
"""

import argparse
import re
import unicodedata
from html import escape
from pathlib import Path

# URL base GitHub Pages — modifica con il tuo username/repo
GITHUB_PAGES_BASE = "https://filippostrozzi.github.io/articoli-generati-con-ia"

# Percorso output HTML
DOCS_DIR = Path("docs/articoli")

# Classi CSS per tipo di autore
AUTHOR_KIND_CLASS = {
    "@": "author-human",
    "&": "author-ai",
    "*": "author-ref",
}

ANNOTATION_BLOCK_START = re.compile(r"^\s*---\s*$")
ANNOTATION_BLOCK_END = re.compile(r"^\s*\.\.\.\s*$")


# ── Parsing ──────────────────────────────────────────────────────────────────


def split_text_and_annotations(raw: str):
    lines = raw.splitlines(keepends=True)
    start_idx = None
    for i, line in enumerate(lines):
        if ANNOTATION_BLOCK_START.match(line):
            start_idx = i
            break
    if start_idx is None:
        return raw, ""
    end_idx = None
    for j in range(start_idx + 1, len(lines)):
        if ANNOTATION_BLOCK_END.match(lines[j]):
            end_idx = j
            break
    if end_idx is None:
        return raw, ""
    text_part = "".join(lines[:start_idx]).rstrip("\n")
    annotations_part = "".join(lines[start_idx : end_idx + 1])
    return text_part, annotations_part


def parse_ranges(range_str: str):
    """
    "0,20 33,4 45 62,4" → [(0,20), (33,4), (45,1), (62,4)]
    I token senza virgola hanno lunghezza 1.
    """
    ranges = []
    for token in range_str.strip().split():
        if "," in token:
            s, l = token.split(",", 1)
            ranges.append((int(s), int(l)))
        else:
            ranges.append((int(token), 1))
    return ranges


def parse_annotation_block(block: str):
    authors = []
    for line in block.splitlines()[1:]:  # salta "---"
        if ANNOTATION_BLOCK_END.match(line):
            break
        if ":" not in line or not line.strip():
            continue
        key_part, value_part = line.split(":", 1)
        key = key_part.strip()
        if key.lower().startswith("annotazioni") or key.lower().startswith("annotations"):
            continue
        if key and key[0] in ("@", "&", "*"):
            authors.append((key[0], key, parse_ranges(value_part)))
    return authors


# ── Segmentazione ─────────────────────────────────────────────────────────────


def build_segments(text: str, authors):
    markers = [None] * len(text)
    for kind_char, _key, ranges in authors:
        for start, length in ranges:
            start = max(0, min(start, len(text)))
            end = max(0, min(start + length, len(text)))
            for i in range(start, end):
                markers[i] = kind_char

    segments = []
    if not text:
        return segments
    current = markers[0]
    seg_start = 0
    for i in range(1, len(text)):
        if markers[i] != current:
            segments.append((seg_start, i, current))
            seg_start = i
            current = markers[i]
    segments.append((seg_start, len(text), current))
    return segments


# ── Utilità ───────────────────────────────────────────────────────────────────


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode()
    name = re.sub(r"[^\w\s-]", "", name).strip().lower()
    return re.sub(r"[-\s]+", "-", name)


def extract_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Articolo"


# ── Rendering HTML ────────────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.7;
  color: #24292f;
  background: #fff;
}

.container {
  max-width: 780px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

/* Legenda */
.legend {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 2rem;
  padding: 0.75rem 1rem;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  font-size: 0.85rem;
}
.legend-item { display: flex; align-items: center; gap: 0.4rem; }
.legend-swatch {
  display: inline-block;
  width: 14px; height: 14px;
  border-radius: 3px;
}
.swatch-human { background: rgba(0, 150, 255, 0.35); }
.swatch-ai    { background: linear-gradient(90deg,
                  rgba(255, 0, 150, 0.45), rgba(0, 200, 255, 0.45)); }

/* Testo */
.article-body {
  white-space: pre-wrap;
  word-break: break-word;
}

/* Annotazioni */
.author-human { background-color: rgba(0, 150, 255, 0.15); border-radius: 2px; }
.author-ai    { background: linear-gradient(90deg,
                  rgba(255, 0, 150, 0.18), rgba(0, 200, 255, 0.18));
                border-radius: 2px; }
.author-ref   { opacity: 0.6; }
"""


def render_html(text: str, segments, title: str, source_filename: str) -> str:
    body_parts = []
    for start, end, kind in segments:
        chunk = text[start:end]
        if kind is None:
            body_parts.append(escape(chunk))
        else:
            css_class = AUTHOR_KIND_CLASS.get(kind, "author-unknown")
            body_parts.append(f'<span class="{css_class}">{escape(chunk)}</span>')

    body_html = "".join(body_parts)

    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="container">
  <div class="legend">
    <strong>Paternità:</strong>
    <span class="legend-item">
      <span class="legend-swatch swatch-human"></span> Umano
    </span>
    <span class="legend-item">
      <span class="legend-swatch swatch-ai"></span> IA
    </span>
    <span class="legend-item" style="color:#666; font-size:0.8rem;">
      Sorgente: <code>{escape(source_filename)}</code>
    </span>
  </div>
  <div class="article-body">{body_html}</div>
</div>
</body>
</html>
"""


# ── Azioni principali ─────────────────────────────────────────────────────────


def render_article(md_path: Path):
    raw = md_path.read_text(encoding="utf-8")
    text, annotation_block = split_text_and_annotations(raw)

    if not annotation_block:
        print(f"  [skip] {md_path.name}: nessun blocco Annotazioni trovato")
        return None

    authors = parse_annotation_block(annotation_block)
    if not authors:
        print(f"  [skip] {md_path.name}: nessuna annotazione autore trovata")
        return None

    segments = build_segments(text, authors)
    title = extract_title(text)
    slug = slugify(md_path.stem)

    out_dir = DOCS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.html"

    html = render_html(text, segments, title, md_path.name)
    out_file.write_text(html, encoding="utf-8")

    url = f"{GITHUB_PAGES_BASE}/articoli/{slug}/"
    print(f"  [ok] {md_path.name} → {out_file}  ({url})")
    return {"title": title, "slug": slug, "url": url}


def update_readme(articles):
    readme = Path("README.md")

    rows = "\n".join(
        f"| {escape(a['title'])} | [Apri con annotazioni]({a['url']}) |"
        for a in articles
    )

    content = f"""# Articoli generati con IA

Questo repository raccoglie articoli scritti con il supporto dell'intelligenza artificiale.
Ogni articolo include le annotazioni di paternità di [iA Writer](https://ia.net/topics/ia-writer-7),
che mostrano quali parti sono state scritte dall'umano e quali dall'IA.

## Articoli

| Articolo | Link |
|---|---|
{rows}

---
*I file HTML con evidenziazione della paternità sono generati automaticamente da [`scripts/render_authorship.py`](scripts/render_authorship.py) tramite GitHub Actions.*
"""
    readme.write_text(content, encoding="utf-8")
    print(f"  [ok] README.md aggiornato con {len(articles)} articoli")


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Rende visibili le annotazioni di iA Writer su GitHub Pages"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("input", nargs="?", help="File Markdown sorgente in articoli/")
    group.add_argument(
        "--update-readme",
        action="store_true",
        help="Scansiona docs/articoli/ e aggiorna README.md",
    )
    args = parser.parse_args()

    if args.update_readme:
        articles = []
        for index_html in sorted(DOCS_DIR.glob("*/index.html")):
            slug = index_html.parent.name
            raw_html = index_html.read_text(encoding="utf-8")
            m = re.search(r"<title>(.*?)</title>", raw_html)
            title = m.group(1) if m else slug
            url = f"{GITHUB_PAGES_BASE}/articoli/{slug}/"
            articles.append({"title": title, "slug": slug, "url": url})
        update_readme(articles)
    else:
        render_article(Path(args.input))


if __name__ == "__main__":
    main()
