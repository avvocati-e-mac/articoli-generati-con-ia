# CLAUDE.md — Regole operative del progetto

Questo file descrive come funziona il progetto e come aggiungere nuovi articoli.
Leggilo all'inizio di ogni sessione prima di toccare qualsiasi file.

---

## Struttura del progetto

```
articoli/          ← File .md sorgente con annotazioni iA Writer (NON modificare)
scripts/
  render_authorship.py   ← Script di conversione MD → HTML annotato
docs/
  articoli/
    {slug}/
      index.html   ← HTML generato (NON modificare a mano, viene sovrascritto)
.github/
  workflows/
    render-annotations.yml  ← GitHub Actions
README.md          ← Generato automaticamente dallo script (NON modificare a mano)
CLAUDE.md          ← Questo file
```

---

## Come aggiungere un nuovo articolo

1. **Scrivi e revisiona l'articolo in iA Writer** con la funzione Authorship attiva,
   in modo che le annotazioni `@` (umano) e `&` (IA) vengano salvate nel file.

2. **Copia il file `.md` nella cartella `articoli/`** del progetto.
   Il nome del file diventa lo slug dell'URL — usa nomi descrittivi in italiano.

3. **Fai commit e push su `main`**:
   ```bash
   git add articoli/nome-articolo.md
   git commit -m "feat: aggiungi articolo 'titolo'"
   git push
   ```

4. **GitHub Actions parte automaticamente** (trigger: push di `*.md` in `articoli/`).
   In circa 15 secondi genera l'HTML e aggiorna il README con il nuovo link.

5. **L'URL pubblico** sarà:
   ```
   https://avvocati-e-mac.github.io/articoli-generati-con-ia/articoli/{slug}/
   ```
   dove `{slug}` è il nome del file (senza `.md`), normalizzato in ASCII minuscolo
   con trattini. Esempio:
   ```
   articoli/Il mio articolo.md
   → https://avvocati-e-mac.github.io/…/articoli/il-mio-articolo/
   ```

---

## Triggerare il workflow manualmente

Se hai bisogno di rigenerare tutti gli HTML senza fare un nuovo commit:

```bash
gh workflow run render-annotations.yml --ref main
```

Oppure vai su GitHub → Actions → "Render iA Writer Annotations" → "Run workflow".

---

## Esecuzione locale dello script

Dalla root del progetto:

```bash
# Renderizza un singolo articolo
python3 scripts/render_authorship.py "articoli/nome-articolo.md"

# Rigenera tutti gli articoli
for f in articoli/*.md; do
  python3 scripts/render_authorship.py "$f"
done

# Aggiorna README.md con la lista degli articoli
python3 scripts/render_authorship.py --update-readme
```

**Dipendenze** (già installate localmente):
```bash
pip3 install mistune beautifulsoup4 --break-system-packages
```

---

## Come funziona `render_authorship.py`

1. Legge il file `.md` sorgente.
2. Trova il **blocco annotazioni iA Writer** in fondo al file: un blocco `---`/`...`
   la cui prima riga inizia con `Annotazioni:`. Cerca dall'ultima occorrenza di `---`
   per non confondersi con i `---` usati come separatori orizzontali (`<hr>`) nel testo.
3. Converte il Markdown in HTML strutturato con **mistune**.
4. Visita ogni nodo testo dell'HTML con **BeautifulSoup**, cerca la stringa
   corrispondente nel sorgente Markdown originale, e applica gli `<span>` di paternità.
5. Scrive `docs/articoli/{slug}/index.html`.

**Colori paternità:**
- Verde `#22c55e` → testo scritto dall'umano (`@`)
- Arancione `#f97316` → testo scritto dall'IA (`&`)

---

## Regole e vincoli importanti

- **Non modificare `docs/` a mano** — viene sovrascritto ad ogni run del workflow.
- **Non modificare `README.md` a mano** — viene sovrascritto da `--update-readme`.
- **Il blocco annotazioni iA Writer** deve trovarsi in fondo al file, dopo tutto il
  contenuto dell'articolo. Non spostarlo.
- **I `---` nel corpo dell'articolo** (usati come `<hr>`) non creano problemi: lo
  script riconosce il blocco annotazioni solo se la riga dopo `---` inizia con
  `Annotazioni:`.
- **L'URL base GitHub Pages** è `https://avvocati-e-mac.github.io/articoli-generati-con-ia`.
  Se il repository viene rinominato o spostato, aggiorna la costante `GITHUB_PAGES_BASE`
  in `scripts/render_authorship.py` riga 29.

---

## Repository GitHub

`https://github.com/avvocati-e-mac/articoli-generati-con-ia`
