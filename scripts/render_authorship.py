#!/usr/bin/env python3
"""
render_authorship.py — Rende visibili le annotazioni di iA Writer su GitHub Pages.

Strategia:
  1. Converte il Markdown in HTML con mistune (HTML pulito).
  2. Visita i nodi testo dell'HTML con BeautifulSoup.
  3. Per ogni nodo testo, calcola l'offset nel sorgente Markdown cercando
     la stringa corrispondente; applica i marker di paternità.
  4. Sostituisce i nodi testo con frammenti HTML con <span>.

Uso:
  python3 scripts/render_authorship.py articoli/mio-articolo.md
  python3 scripts/render_authorship.py --update-readme

Dipendenze:
  pip3 install mistune beautifulsoup4 --break-system-packages
"""

import argparse
import re
import unicodedata
from html import escape
from pathlib import Path

import mistune
from bs4 import BeautifulSoup, NavigableString, Tag

GITHUB_PAGES_BASE = "https://avvocati-e-mac.github.io/articoli-generati-con-ia"
DOCS_DIR = Path("docs/articoli")

AUTHOR_KIND_CLASS = {
    "@": "author-human",
    "&": "author-ai",
    "*": "author-ref",
}

ANNOTATION_BLOCK_START = re.compile(r"^\s*---\s*$")
ANNOTATION_BLOCK_END   = re.compile(r"^\s*\.\.\.\s*$")


# ── Parsing ───────────────────────────────────────────────────────────────────


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
    return text_part, "".join(lines[start_idx: end_idx + 1])


def parse_ranges(range_str: str):
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
    for line in block.splitlines()[1:]:
        if ANNOTATION_BLOCK_END.match(line):
            break
        if ":" not in line or not line.strip():
            continue
        key_part, value_part = line.split(":", 1)
        key = key_part.strip()
        if key.lower().startswith(("annotazioni", "annotations")):
            continue
        if key and key[0] in ("@", "&", "*"):
            authors.append((key[0], key, parse_ranges(value_part)))
    return authors


# ── Marker per carattere ─────────────────────────────────────────────────────


def build_markers(text: str, authors):
    """Ritorna lista dove markers[i] = kind_char dell'autore al carattere i."""
    markers = [None] * len(text)
    for kind_char, _key, ranges in authors:
        for start, length in ranges:
            s = max(0, min(start, len(text)))
            e = max(0, min(start + length, len(text)))
            for i in range(s, e):
                markers[i] = kind_char
    return markers


# ── Markdown → testo puro (approssimazione per mapping offset) ────────────────


def md_to_plain(text: str) -> str:
    """
    Rimuove la sintassi Markdown più comune per ottenere il testo
    che compare nei nodi testo HTML dopo la conversione.
    Usato per stimare l'offset nel sorgente.
    """
    # Rimuovi heading markers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Rimuovi bold/italic
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    text = re.sub(r"_{1,3}(.*?)_{1,3}", r"\1", text)
    # Rimuovi link: [testo](url) → testo
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # Rimuovi immagini
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    # Rimuovi codice inline
    text = re.sub(r"`([^`]*)`", r"\1", text)
    # Rimuovi blockquote
    text = re.sub(r"^>\s?", "", text, flags=re.MULTILINE)
    # Rimuovi separatori HR
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    return text


# ── Applica span al testo di un nodo, cercando offset nel sorgente MD ─────────


def annotate_text_node(node_text: str, src_text: str, markers, search_from: int):
    """
    Cerca node_text nel sorgente MD a partire da search_from.
    Ritorna (html_fragment, new_search_from).
    html_fragment: stringa HTML con span di paternità.
    """
    # Cerca la posizione nel sorgente (ignora whitespace multiplo)
    # Prima prova esatta, poi con normalizzazione degli spazi
    pos = src_text.find(node_text, search_from)
    if pos == -1:
        # fallback: cerca dopo aver normalizzato newlines
        stripped = node_text.strip()
        if stripped:
            pos = src_text.find(stripped, search_from)
        if pos == -1:
            # non trovato: emetti testo senza annotazione
            return escape(node_text), search_from

    end_pos = pos + len(node_text)

    # Costruisce i segmenti
    segments = []
    if pos >= len(markers):
        return escape(node_text), end_pos

    current_kind = markers[pos] if pos < len(markers) else None
    seg_start = pos
    for i in range(pos + 1, min(end_pos, len(markers))):
        if markers[i] != current_kind:
            segments.append((seg_start - pos, i - pos, current_kind))
            seg_start = i
            current_kind = markers[i]
    segments.append((seg_start - pos, min(end_pos, len(markers)) - pos, current_kind))

    # Gestisci caratteri oltre len(markers)
    if end_pos > len(markers):
        segments.append((len(markers) - pos, end_pos - pos, None))

    parts = []
    for local_start, local_end, kind in segments:
        chunk = node_text[local_start:local_end]
        if not chunk:
            continue
        if kind is None:
            parts.append(escape(chunk))
        else:
            css = AUTHOR_KIND_CLASS.get(kind, "author-unknown")
            parts.append(f'<span class="{css}">{escape(chunk)}</span>')

    return "".join(parts), end_pos


# ── Visita ricorsiva dei nodi testo ───────────────────────────────────────────


def annotate_soup(soup: BeautifulSoup, src_text: str, markers):
    """
    Percorre tutti i nodi testo nell'HTML e li sostituisce con HTML annotato.
    Mantiene un cursore search_from per trovare correttamente le posizioni
    anche se lo stesso testo appare più volte.
    """
    search_from = 0

    # Raccoglie tutti i nodi NavigableString in ordine di documento
    text_nodes = list(soup.find_all(string=True))

    for node in text_nodes:
        # Salta script, style, code (non annotare codice tecnico)
        parent = node.parent
        if parent and parent.name in ("script", "style", "code", "pre"):
            continue
        if not node.strip():
            continue

        annotated_html, search_from = annotate_text_node(
            str(node), src_text, markers, search_from
        )

        # Sostituisce il nodo testo con HTML parsato
        new_tag = BeautifulSoup(annotated_html, "html.parser")
        node.replace_with(new_tag)

    return str(soup)


# ── Pipeline principale ───────────────────────────────────────────────────────


def render_article_html(md_text: str, authors) -> str:
    # 1. Markdown → HTML pulito
    md = mistune.create_markdown(
        plugins=["table", "strikethrough", "footnotes", "task_lists"],
    )
    clean_html = md(md_text)

    # 2. Costruisce i marker sull'intero testo sorgente
    markers = build_markers(md_text, authors)

    # 3. Annota i nodi testo nell'HTML
    soup = BeautifulSoup(clean_html, "html.parser")
    annotated = annotate_soup(soup, md_text, markers)

    return annotated


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


# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.8;
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
  align-items: center;
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
  flex-shrink: 0;
}
.swatch-human { background: rgba(0, 150, 255, 0.45); }
.swatch-ai    { background: linear-gradient(90deg, rgba(255,0,150,0.55), rgba(0,200,255,0.55)); }

/* Tipografia */
.article-body h1,
.article-body h2,
.article-body h3 { margin: 1.8rem 0 0.6rem; font-weight: 600; line-height: 1.3; }
.article-body h1 { font-size: 1.9rem; margin-top: 0; }
.article-body h2 { font-size: 1.4rem; }
.article-body h3 { font-size: 1.15rem; }
.article-body p  { margin-bottom: 1rem; }
.article-body ul,
.article-body ol { margin: 0.5rem 0 1rem 1.5rem; }
.article-body li { margin-bottom: 0.3rem; }
.article-body blockquote {
  border-left: 4px solid #d0d7de;
  padding: 0.5rem 1rem;
  color: #57606a;
  margin: 1rem 0;
}
.article-body code {
  background: #f6f8fa;
  padding: 0.15em 0.4em;
  border-radius: 3px;
  font-size: 0.88em;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
.article-body pre {
  background: #f6f8fa;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 1rem;
}
.article-body pre code { background: none; padding: 0; font-size: 0.85em; }
.article-body a { color: #0969da; }
.article-body hr { border: none; border-top: 1px solid #d0d7de; margin: 2rem 0; }
.article-body table { border-collapse: collapse; width: 100%; margin-bottom: 1rem; }
.article-body th, .article-body td {
  border: 1px solid #d0d7de;
  padding: 0.4rem 0.8rem;
}
.article-body th { background: #f6f8fa; }
.article-body img { max-width: 100%; height: auto; }

/* Paternità */
.author-human { background-color: rgba(0, 150, 255, 0.15); border-radius: 2px; }
.author-ai    { background: linear-gradient(90deg,
                  rgba(255, 0, 150, 0.15), rgba(0, 200, 255, 0.15));
                border-radius: 2px; }
.author-ref   { opacity: 0.65; }
"""


def build_full_html(body_html: str, title: str, source_filename: str) -> str:
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
    <span class="legend-item" style="color:#666; font-size:0.8rem; margin-left:auto;">
      Sorgente: <code>{escape(source_filename)}</code>
    </span>
  </div>
  <div class="article-body">
{body_html}
  </div>
</div>
</body>
</html>
"""


# ── Azioni ────────────────────────────────────────────────────────────────────


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

    title     = extract_title(text)
    slug      = slugify(md_path.stem)
    body_html = render_article_html(text, authors)

    out_dir  = DOCS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.html"

    out_file.write_text(build_full_html(body_html, title, md_path.name), encoding="utf-8")

    url = f"{GITHUB_PAGES_BASE}/articoli/{slug}/"
    print(f"  [ok] {md_path.name} → {out_file}  ({url})")
    return {"title": title, "slug": slug, "url": url}


def update_readme(articles):
    rows = "\n".join(
        f"| {a['title']} | [Apri con annotazioni]({a['url']}) |"
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
    Path("README.md").write_text(content, encoding="utf-8")
    print(f"  [ok] README.md aggiornato con {len(articles)} articoli")


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Rende visibili le annotazioni di iA Writer su GitHub Pages"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("input", nargs="?", help="File Markdown sorgente in articoli/")
    group.add_argument("--update-readme", action="store_true")
    args = parser.parse_args()

    if args.update_readme:
        articles = []
        for index_html in sorted(DOCS_DIR.glob("*/index.html")):
            slug     = index_html.parent.name
            raw_html = index_html.read_text(encoding="utf-8")
            m        = re.search(r"<title>(.*?)</title>", raw_html)
            title    = m.group(1) if m else slug
            url      = f"{GITHUB_PAGES_BASE}/articoli/{slug}/"
            articles.append({"title": title, "slug": slug, "url": url})
        update_readme(articles)
    else:
        render_article(Path(args.input))


if __name__ == "__main__":
    main()
