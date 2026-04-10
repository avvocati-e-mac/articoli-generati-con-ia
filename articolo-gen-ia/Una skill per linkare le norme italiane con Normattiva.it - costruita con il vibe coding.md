# Una skill per linkare le norme italiane con Normattiva.it — costruita con il vibe coding

Ho passato anni a dire ai miei colleghi che usare bene la tecnologia significa non fare mai due volte la stessa cosa stupida. Poi un giorno mi sono accorto che costruivo a mano i link a Normattiva.it ogni volta che scrivevo un documento con riferimenti normativi — copiare la data di emanazione, ricordarmi che il codice civile è l'allegato 2 del R.D. 262/1942, non dimenticare il `;` prima del numero. David Sparks chiama questo genere di attività *donkey work*: lavoro da mulo, meccanico, ripetitivo, che non aggiunge nessun valore intellettuale. E poi c'è un secondo motivo, tutto pratico: come ti ho già spiegato nei miei articoli sugli [atti telematici avanzati](https://avvocati-e-mac.it/blog/2022/9/27/atti-telematici-avanzati-scritti-in-testo-semplice), i link ipertestuali ai riferimenti normativi sono uno dei requisiti che ti permettono di ottenere l'aumento del 30% nel computo delle pagine. Così ho fatto quello che avrei dovuto fare da subito: ho creato una skill per Claude che genera questi link in automatico. In questo articolo ti racconto cos'è la skill, come funziona, e come l'ho costruita — prima con **Perplexity**, poi con **Claude Cowork** — senza scrivere una riga di codice.

---

## 1. Normattiva.it e il sistema URN-NIR

**Normattiva.it** è il portale ufficiale della normativa italiana, gestito dalla Presidenza del Consiglio dei Ministri. Non è solo un motore di ricerca delle leggi: è una banca dati con URL *stabili e permanenti* per ogni singolo articolo di ogni norma italiana — dalle leggi ai decreti legislativi, dalla Costituzione ai codici storici.

Il sistema che rende possibile tutto questo si chiama **URN-NIR** (Uniform Resource Name – Norme In Rete), uno standard definito originariamente dal CNIPA (oggi AgID). Ogni norma ha un identificatore univoco che non cambia nel tempo, costruito seguendo una struttura precisa.

Un link a Normattiva ha questa forma:

```
https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:{tipo}:{data};{numero}~art{N}
```

Per esempio, l'art. 2043 del codice civile diventa:

```
https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262:2~art2043
```

### 1.1 La trappola dei codici storici

I grandi codici italiani — civile, penale, procedura civile, legge fallimentare — furono approvati nel periodo pre-repubblicano come *allegati numerati* di Regi Decreti. Nell'URN bisogna indicare anche il numero dell'allegato, dopo il numero del decreto, separato da `:`.

| Codice | R.D. | Allegato |
|--------|------|----------|
| Codice civile | R.D. 262/1942 | `:2` |
| Cod. proc. civile | R.D. 1443/1940 | `:1` |
| Codice penale | R.D. 1398/1930 | `:1` |
| Legge fallimentare | R.D. 267/1942 | `:1` |

Se ometti il numero allegato, il link porta al Regio Decreto originale — non al codice. È un errore che si fa facilmente se non si conosce questa particolarità.

### 1.2 La data di emanazione, non quella della G.U.

La data nell'URN è quella di *emanazione* dell'atto — quando il provvedimento è stato firmato — non quella di pubblicazione in Gazzetta Ufficiale. Possono differire di giorni o settimane. Usare la data sbagliata genera un link rotto.

Normattiva mette già a disposizione un [parser normativo](https://www.normattiva.it/staticPage/utilita) incorporato nel portale, che analizza testi giuridici e trasforma i riferimenti in link URN. Il problema è che funziona solo sul sito — non è qualcosa che puoi integrare nel tuo flusso di lavoro esterno.

---

## 2. Il donkey work: perché costruire questi link a mano è un problema

Il termine *donkey work* — letteralmente "lavoro da mulo" — è usato da [David Sparks (MacSparky)](https://www.macsparky.com) per descrivere tutto il lavoro attorno al lavoro vero: smistare email, riorganizzare task, fare data entry ripetitivo. Attività meccaniche che non richiedono intelligenza ma che consumano tempo e, soprattutto, attenzione.

Costruire a mano i link URN per ogni riferimento normativo in un atto o in un parere è esattamente questo. Il processo richiede di identificare il tipo di atto, trovare la data esatta di emanazione (non quella della G.U.), inserire il numero corretto, verificare se si tratta di un codice storico con numero allegato, comporre la stringa URN senza errori di sintassi, e testare che il link funzioni. In un atto con venti o trenta citazioni normative, questo giro si ripete decine di volte. Non c'è nulla di intellettuale.

E come dicevo nell'introduzione, c'è anche la questione del 30%. Come ti ho spiegato nei miei articoli sulle [tecniche avanzate di redazione degli atti](https://avvocati-e-mac.it/blog/2023/2/9/tecniche-avanzate-di-redazione-degli-atti-giuridici-mediante-text-editor-e-markup-language-parte-iii), la presenza di link ipertestuali ai riferimenti normativi è uno dei requisiti per ottenere l'incremento del 30% nel computo delle pagine previsto dalla normativa sul PCT. Non è solo una questione estetica: incide concretamente sulla lunghezza dell'atto che puoi depositare.

---

## 3. Cosa sono le skill di Anthropic

Una **skill** (nel senso che usa Anthropic) è una directory su filesystem con un file `SKILL.md` che contiene istruzioni strutturate per un task specifico. Quando Claude legge una skill prima di rispondere, acquisisce quelle istruzioni e le applica — come un assistente che consulta un manuale di procedura prima di fare un lavoro.

La differenza rispetto a un prompt in chat si vede nell'uso quotidiano. Un prompt in chat dura una conversazione e poi sparisce. Una skill invece è un file: vive su disco, la puoi modificare, tenerla in git, passarla a un collega. Claude si comporta allo stesso modo ogni volta che la invoca. Se cambio le istruzioni nel file, cambia il comportamento in tutte le sessioni future — senza dover riscrivere niente.

Un altro aspetto utile è la modularità. Il contesto della skill arriva solo quando la skill viene invocata, non appesantisce ogni conversazione. Anthropic ha un [repository pubblico di skill su GitHub](https://github.com/anthropics/skills) — il concetto viene dalla tradizione degli strumenti professionali: come un modello di atto o uno stencil per i brief, la skill codifica le best practice una volta sola.

La skill che ho creato si chiama `normattiva`. Il suo compito è semplice: ogni volta che Claude produce un testo con riferimenti normativi italiani, genera automaticamente i link a Normattiva.it al posto delle citazioni nude.

---

## 4. Come l'ho costruita: vibe coding con Perplexity e Claude

Il termine **vibe coding** è stato coniato da [Andrej Karpathy](https://x.com/karpathy/status/1886192184808149383) — co-fondatore di OpenAI — nel febbraio 2025. La definizione originale: *"there's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists."* Il termine è entrato nel Collins English Dictionary come Word of the Year 2025.

Di solito si parla di vibe coding in riferimento al software tradizionale. Nel mio caso non si trattava di scrivere codice Python o Swift, ma il principio è lo stesso: ho descritto in linguaggio naturale quello che volevo ottenere, ho iterato finché il risultato era giusto, e non ho mai aperto un editor di codice.

### 4.1 Prima fase: la ricerca con Perplexity

Ho iniziato con **Perplexity**, che mi ha permesso di fare ricerca live sulla documentazione di Normattiva.it. Ho esaminato come funziona il sistema URN-NIR, la struttura dei link con tutti i casi particolari (tipo atto, data, numero, allegato, articolo, comma), le insidie specifiche dei codici storici, e gli errori più comuni che portano a link non funzionanti.

**Perplexity** era lo strumento giusto per questa fase: sa fare ricerca sul web e sintetizzare documentazione tecnica in modo affidabile. Ne è uscita una prima versione del file SKILL.md — funzionante, ma non ottimizzata. Un unico file lungo con tutte le tabelle, tutti i casi, tutte le eccezioni. Caricava molto contesto a ogni invocazione.

### 4.2 Seconda fase: la strutturazione con Claude Cowork

Ho passato il materiale a **Claude Cowork** con una richiesta precisa: ristrutturare la skill applicando il principio di *progressive disclosure* — di cui ti parlo nella sezione successiva — per ridurre il consumo di token senza perdere precisione nei risultati.

Il risultato è una skill in due file:

- `SKILL.md` — regole essenziali, tabella di lookup rapida con le norme più citate, workflow in tre passi
- `lookup-extended.md` — tabella completa, tipi di atto rari, note sugli allegati, errori comuni

Il file principale è snello. Il file esteso viene letto solo quando serve.

---

## 5. La skill ottimizzata: progressive disclosure

La **progressive disclosure** è un principio di UX design formulato da Carroll e Rosson all'IBM nel 1983. L'idea: mostra prima solo le informazioni essenziali, e rivela i dettagli solo quando — e solo se — servono davvero.

Applicata al design di una skill per LLM, la logica è identica. Un LLM legge il file `SKILL.md` intero ogni volta che la skill viene invocata: se il file è lungo, consuma molti token. La soluzione è strutturare il contenuto in livelli:

- **Livello 1 (SKILL.md)**: regole fondamentali + tabella rapida delle norme più frequenti (c.c., c.p.c., c.p., Costituzione, i D.Lgs. più usati). Per il 90% dei casi, basta questo.
- **Livello 2 (lookup-extended.md)**: tutto il resto — tipi di atto rari, tabella completa, note sugli allegati, errori comuni. Viene letto *solo* se la norma cercata non è nella tabella rapida.

Il workflow nella skill è esplicito: se la norma è nella quick lookup, genera subito il link; se non c'è, vai a leggere il file esteso. C'è anche un terzo caso, per i documenti con molte citazioni normative: la skill prevede di delegare la generazione dei link a un subagente con il modello **Haiku** — più piccolo e veloce — invece di usare il modello principale. Il modello principale rimane libero per i ragionamenti complessi; il lavoro meccanico di costruzione degli URN viene scaricato su un modello più leggero. Stesso principio: usa le risorse giuste per il task giusto.

---

## 6. Usare la skill in Perplexity Spaces e in qualsiasi sistema RAG

Dopo aver creato la skill, ho scoperto che si può usare anche fuori da Claude Cowork — in qualsiasi sistema che supporti documenti allegati come fonte di conoscenza.

Il meccanismo è semplice: alleghi il file `SKILL.md` come documento allo spazio o al sistema RAG, e nel system prompt istruisci il modello a consultarlo ogni volta che deve citare riferimenti normativi. Il modello applica le regole della skill come se fossero sue.

Ho provato negli **Spazi di Perplexity** — la funzionalità che permette di creare ambienti di lavoro con documenti allegati e un system prompt personalizzato. Nel video qui sotto puoi vedere come funziona in pratica: Perplexity produce i link URN corretti a Normattiva.it semplicemente perché ha il file SKILL.md a disposizione.

{{VIDEO: https://youtu.be/jyTRHz-e4vM}}

Lo stesso approccio funziona con **NotebookLM**, con gli spazi documentali di **BuddaLaw**, e con qualsiasi altro sistema che consenta di allegare file e personalizzare il system prompt. Il file diventa un modulo portabile: lo prepari una volta e lo alleghi dove ti serve.

---

## In conclusione

Ho costruito la versione iniziale della skill in un pomeriggio con Perplexity, l'ho ottimizzata con Claude Cowork applicando il principio di progressive disclosure, e adesso la uso sia in Claude che negli Spazi di Perplexity. Genera i link URN corretti a Normattiva.it senza che io debba pensarci, e nei documenti per il PCT mi aiuta a soddisfare uno dei requisiti per il 30% aggiuntivo di pagine.

Il vibe coding — inteso come "descrivere in linguaggio naturale quello che vuoi, iterare finché funziona" — è una di quelle cose che all'inizio sembrano un giocattolo e poi entrano nel flusso di lavoro fisso. Non è necessario saper scrivere codice. È necessario saper descrivere con precisione cosa si vuole ottenere.

Come sempre, se ti è piaciuto quel che hai letto o visto e non l'hai già fatto, ti suggerisco di iscriverti alla mia [newsletter](https://www.avvocati-e-mac.it/mailinglist). Ti avvertirò dei nuovi articoli che pubblico (oltre ai podcast e video su YouTube) e, mensilmente, ti segnalerò articoli che ho raccolto nel corso del mese ed ho ritenuto interessanti.

---

## Immagini suggerite per l'articolo

1. **Sezione 1 — URN-NIR** — Screenshot di una pagina di Normattiva.it con un articolo del codice civile aperto, evidenziando la barra URL con l'URN completo — Didascalia suggerita: "La barra URL di Normattiva.it mostra la struttura URN-NIR per l'articolo aperto"

2. **Sezione 1.1 — Tabella allegati** — Screenshot del file `lookup-extended.md` aperto in un editor, con la sezione "Note sugli allegati nei codici storici" visibile — Didascalia suggerita: "La tabella degli allegati per i codici storici nel file di riferimento esteso"

3. **Sezione 4.1 — Perplexity** — Screenshot della sessione Perplexity usata per la ricerca sulla documentazione URN-NIR — Didascalia suggerita: "La ricerca su Perplexity per capire il sistema URN-NIR di Normattiva"

4. **Sezione 4.2 — SKILL.md** — Screenshot del file `SKILL.md` finale aperto in un editor di testo, con la tabella di quick lookup visibile — Didascalia suggerita: "Il file SKILL.md della skill normattiva con la tabella di lookup rapida"

5. **Sezione 5 — Progressive disclosure** — Schema che mostra i due livelli della skill: SKILL.md (livello 1, sempre caricato) e lookup-extended.md (livello 2, solo se necessario) — Didascalia suggerita: "La struttura a due livelli della skill: progressive disclosure applicata al consumo di contesto"

6. **Sezione 6 — Perplexity Spaces** — Screenshot dello Spazio Perplexity con il file SKILL.md allegato e una risposta con link URN corretti nel testo — Didascalia suggerita: "Lo Spazio Perplexity con il file SKILL.md allegato: i link a Normattiva vengono generati in automatico"
