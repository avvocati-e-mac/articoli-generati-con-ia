# CLAUDE.md — Regole operative del progetto

Questo file descrive come funziona il progetto e come aggiungere nuovi articoli.
Leggilo all'inizio di ogni sessione prima di toccare qualsiasi file.

---

## Struttura del progetto

```
articoli-rev-umana/     ← File .md revisionati dall'umano, con annotazioni iA Writer (NON modificare)
articolo-gen-ia/        ← File .md generati dall'IA pura, stesso nome file (NON modificare)
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

2. **Copia il file `.md` nella cartella `articoli-rev-umana/`** del progetto.
   Il nome del file diventa lo slug dell'URL — usa nomi descrittivi in italiano.

2b. *(Opzionale)* **Se hai anche la versione generata dall'IA**, salvala con lo stesso nome
    nella cartella `articolo-gen-ia/`. Lo script rileverà il file automaticamente e inserirà
    un banner in cima all'HTML con il link alla versione AI-only su GitHub.

3. **Fai commit e push su `main`**:
   ```bash
   git add articoli-rev-umana/nome-articolo.md
   git add articolo-gen-ia/nome-articolo.md   # se esiste
   git commit -m "feat: aggiungi articolo 'titolo'"
   git push
   ```

4. **GitHub Actions parte automaticamente** (trigger: push di `*.md` in `articoli-rev-umana/`).
   In circa 15 secondi genera l'HTML e aggiorna il README con il nuovo link.
   Il commit automatico avviene solo se i file sono effettivamente cambiati
   (nessun commit vuoto se si rigenera un articolo già esistente senza modifiche).

5. **L'URL pubblico** sarà:
   ```
   https://avvocati-e-mac.github.io/articoli-generati-con-ia/articoli/{slug}/
   ```
   dove `{slug}` è il nome del file (senza `.md`), normalizzato in ASCII minuscolo
   con trattini. Esempio:
   ```
   articoli-rev-umana/Il mio articolo.md
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
python3 scripts/render_authorship.py "articoli-rev-umana/nome-articolo.md"

# Rigenera tutti gli articoli
for f in articoli-rev-umana/*.md; do
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
5. Se esiste un file con lo stesso nome in `articolo-gen-ia/`, inserisce in cima
   all'articolo un banner arancione con link alla versione AI-only su GitHub.
6. Scrive `docs/articoli/{slug}/index.html`.

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
