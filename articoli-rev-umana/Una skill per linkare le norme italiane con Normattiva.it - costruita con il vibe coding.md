# Una skill per linkare le norme italiane con Normattiva.it: costruita con il vibe coding

> Quello che stai per leggere è un articolo scritto grazie all’IA: ad un LLM, in particolare [Claude Sonnet 4.6](https://www.anthropic.com/claude/sonnet). Fa parte di un esperimento di cui ti parlerò più avanti su queste pagine ma, per ora, mi interessa solo segnalarti la cosa.
> Se il documento è scritto (prevalentemente) dall’IA, quello che stai leggendo tuttavia nasce dalla mio pensiero; l’IA l’ha eseguito al mio posto ed “impersonandomi” (usando la mia “voce”).
> [Qui]() trovi l’articolo originale generato completamente dall’IA, l’ultima revisione è la mia e [qui]() trovi la versione che stai leggendo ma con annotate le parti mie e quelle dell’IA.
> Ultima nota prima di iniziare: ho revisionato questo articolo con [iAWriter](https://ia.net/writer) ed utilizzando le funzioni di [Authorship](https://ia.net/topics/see-what-ai-wrote).
> **Se ti interessa solo la skill** la puoi scaricare da [qui]().

Ho passato anni a dire ai colleghi che **usare bene la tecnologia significa non fare mai due volte la stessa cosa stupida**. Poi un giorno mi sono accorto che costruivo a mano i link a [Normattiva.it](https://www.normattiva.it) ogni volta che scrivevo un documento con riferimenti normativi; copiavo la data di emanazione, cercavo di ricordarmi che il codice civile è l'allegato 2 del R.D. 262/1942, di non dimenticare il `;` prima del numero.  
[David Sparks chiama questo genere di attività *donkey work*](https://www.macsparky.com/blog/2026/02/donkey-work-what-i-actually-want-ai-to-do/): lavoro da mulo… meccanico, ripetitivo, che non aggiunge nessun valore intellettuale.
 
Creare i link a Normattiva ha un secondo motivo, tutto pratico: come ti ho già spiegato nei miei articoli sugli [atti telematici avanzati](https://avvocati-e-mac.it/blog/2022/9/27/atti-telematici-avanzati-scritti-in-testo-semplice), i link iper-testuali ai riferimenti normativi sono uno dei requisiti che ti permettono di ottenere l'aumento del 30% sulla liquidazione del compenso professionale. 

In questo mese ho sperimentato molto con l’IA per automatizzare la mia attività lavorativa e così ho fatto quello che avrei dovuto fare da subito: ho provato a creare una **skill per Claude che genera questi link in automatico** e **ci sono riuscito**! 

In questo articolo ti racconto cos'è una skill di Claude, come funziona, come l'ho costruita progressivamente — prima con **Perplexity**, poi con **Claude Cowork** — senza scrivere una riga di codice e come l’ho utilizzata in sistemi differenti da Claude.

## 1. Normattiva.it e il sistema URN-NIR

**Normattiva.it** è il portale ufficiale della normativa italiana, gestito dalla Presidenza del Consiglio dei Ministri. Non è solo un motore di ricerca delle leggi: è una banca dati con URL _stabili e permanenti_ per ogni singolo articolo di ogni norma italiana — dalle leggi ai decreti legislativi, dalla Costituzione ai codici storici.

Il sistema che rende possibile tutto questo si chiama **URN-NIR** (Uniform Resource Name – Norme In Rete), uno standard definito originariamente dal CNIPA (oggi AgID). Ogni norma ha un identificatore univoco che non cambia nel tempo, costruito seguendo una struttura precisa.

Un link a Normattiva ha questa forma:

```
https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:{tipo}:{data};{numero}~art{N}
```

Per esempio, l'art. 2043 del codice civile diventa:

```
https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262:2~art2043
```

### 1.1 La trappola dei “grandi” codici

I grandi codici italiani — civile, penale, procedura civile, legge fallimentare — furono approvati nel periodo pre-repubblicano come *allegati numerati* di Regi Decreti. Questi codici sono anche quelli più utilizzati abitualmente nei documenti legali.
Sono anche quelli con una particolarità specifica: nell'URN bisogna indicare anche il numero dell'allegato, dopo il numero del decreto, separato da `:`.

| Codice | R.D. | Allegato |
|--------|------|----------|
| Codice civile | R.D. 262/1942 | `:2` |
| Cod. proc. civile | R.D. 1443/1940 | `:1` |
| Codice penale | R.D. 1398/1930 | `:1` |
| Legge fallimentare | R.D. 267/1942 | `:1` |

Se ometti il numero allegato, il link porta irrimediabilmente al primo articolo del Regio Decreto originale — non al numero specifico dell’articolo del codice indicato. È un errore che si fa facilmente se non si conosce questa particolarità ed è la prima grossa barriera nell’utilizzo di Normattiva.it da parte dell’avvocato inesperto.

### 1.2 La data di emanazione, non quella della G.U.

La data nell'URN è quella di *emanazione* dell'atto — quando il provvedimento è stato firmato — non quella di pubblicazione in Gazzetta Ufficiale. Possono differire di giorni o settimane. Usare la data sbagliata genera un link rotto. Inoltre, raramente ci si ricorda della data specifica di una Legge, quindi creare i link a memoria è praticamente impossibile.

Normattiva mette già a disposizione un [parser normativo](https://www.normattiva.it/staticPage/utilita) incorporato nel portale, che analizza testi giuridici e trasforma i riferimenti in link URN. Il problema è che funziona solo sul sito — non è qualcosa che puoi integrare nel tuo flusso di lavoro esterno.

---

## 2. Il donkey work: perché costruire questi link a mano è un problema

Il termine *donkey work* — letteralmente "lavoro da mulo" — è usato da [David Sparks (MacSparky)](https://www.macsparky.com) per descrivere tutto il lavoro attorno al lavoro vero: smistare email, riorganizzare task, fare data entry ripetitivo. Attività meccaniche che non richiedono intelligenza ma che consumano tempo e, soprattutto, attenzione.

Se ti interessa approfondire l’argomento ti segnalo [questo suo post in inglese](https://www.macsparky.com/blog/2026/02/donkey-work-what-i-actually-want-ai-to-do/) e [questa puntata del podcast Focused](https://www.macsparky.com/blog/2026/03/focused-252-donkey-work/) (sempre in inglese).

**Costruire a mano i link URN per ogni riferimento normativo in un atto o in un parere per me è lavoro da mulo** (donkey work). 
Il processo richiede di identificare il tipo di atto, trovare la data esatta di emanazione, inserire il numero corretto, ricordarsi, nel caso sia un “grande” codice del numero allegato, comporre la stringa URN senza errori di sintassi, e testare che il link funzioni. 

Nel concreto io vado su Normattiva.it, cerco il Codice o la legge e poi copio l’URN di base e poi aggiungo l’articolo a mano (ad esempio `~art2043`). Ma è un lavoro tedioso.

In un atto con venti o trenta citazioni normative, questo giro si ripete decine di volte. Non c'è nulla di altamente professionale.

### 2.1 Comandi Rapidi in soccorso

Trovo che inserire i riferimenti normativi nei miei atti sia una buona prassi, oltre che potenzialmente utile per far riconoscere il 30% in più in giudizio.

Infatti **i link rendono più semplice e fruibile anche all’utente inesperto l’accesso alle norme** e, secondariamente, permettono di far **conoscere il servizio di Normattiva.it** che, secondo me, dovrebbe essere diventare un progetto conosciuto ai tecnici (avvocati, commercialisti, etc…) e non.

Nel 2023 mi ero già dedicato ad automatizzare e spiegare il sistema (un po astruso bisogna dirlo) di Normattiva in [questa Office Hour](https://avvocati-e-mac.it/blog/2023/2/9/officehour-9-febbraio-2023-e-link-ai-comandi-rapidi-a-normattivait?rq=normattiva) ma [Comandi Rapidi](https://support.apple.com/it-it/guide/shortcuts/welcome/ios) è disponibile solo nella “gabbia dorata” di Apple.

Così mentre stava facendo generare una ricerca alla IA mi è balenata l’idea della skill…

## 3. Cosa sono le skill di Anthropic?

Veniamo quindi al cuore dell’articolo: cosa sono le skill di Anthropic?

Una **skill** (nel senso che usa Anthropic) è una directory su filesystem con un file `SKILL.md` che contiene istruzioni strutturate per un task specifico. Quando Claude legge una skill prima di rispondere, acquisisce quelle istruzioni e le applica — come un assistente che consulta un manuale di procedura prima di fare un lavoro.

La differenza rispetto a un prompt in chat si vede nell'uso quotidiano. Un prompt in chat dura una conversazione e poi sparisce. Una _skill_ invece è un file: vive su disco, la puoi modificare, versionarla in [git](https://git-scm.com/), passarla a un collega. [Claude](https://claude.ai/) si comporta allo stesso modo ogni volta che la invoca. Se cambio le istruzioni nel file, cambia il comportamento in tutte le sessioni future — senza dover riscrivere niente.

Un altro aspetto utile è la **modularità**. Il contesto della skill arriva solo quando la skill viene invocata, non appesantisce ogni conversazione. Anthropic ha un [repository pubblico di skill su GitHub](https://github.com/anthropics/skills) — il concetto viene dalla tradizione degli strumenti professionali: come un modello di atto o uno stencil per i brief, la skill codifica le best practice una volta sola.

La skill che ho creato si chiama `normattiva`. Il suo compito è semplice: ogni volta che Claude produce un testo con riferimenti normativi italiani, genera automaticamente i link a Normattiva.it al posto delle citazioni nude.


## 4. Come l'ho costruita: vibe coding con Perplexity e Claude

Il termine **vibe coding** è stato coniato da [Andrej Karpathy](https://x.com/karpathy/status/1886192184808149383) — co-fondatore di OpenAI — nel febbraio 2025. La definizione originale:
 
> _”there's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists.”_  
> ovvero in italiano: C'è un nuovo tipo di scrittura del codice che chiamo “vibe coding”, in cui si cede completamente alle vibrazioni, si abbracciano gli esponenziali e si dimentica che il codice esiste.

Il termine è entrato nel Collins English Dictionary come Word of the Year 2025.

Di solito si parla di *vibe coding* in riferimento al software tradizionale. 
Nel mio caso non si trattava di scrivere codice Python o Swift, ma il principio è lo stesso: **ho descritto in linguaggio naturale quello che volevo ottenere, ho iterato finché il risultato era giusto, e non ho mai aperto un editor di codice**.

### 4.1 Prima fase: la ricerca con Perplexity

Ho iniziato con **[Perplexity](https://www.perplexity.ai/)**: ho l’abbonamento a questo servizio di ricerca aumentato con IA da Settembre 2025 ed ormai lo padroneggio professionalmente.\

Ho imparato ad _hackerare_ Perplexity per permettermi di creare in modo semplice una prima soluzione e “risparmiare” tokens.

Il mio primo prompt è stato il seguente:

```
Sei programmatore, un esperto di Claude Code. Ragiona passo passo e segui un filo logico.

Esamina il funzionamento di Normattiva.it, in particolare degli
UNR https://www.normattiva.it/staticPage/guidaAllUso_Normattiva.

Fatto uno studio approfondito del funzionamento, crea una skill
per Claude https://github.com/anthropics/skills che permetta di
inserire i link ai riferimenti normativi italiani usando normattiva come da specifiche.

Esempio di collegamento a norma:
- [art. 2028 c.c.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1942-03-16;262:2~art2048)
- [art. 83 c.p.c.](https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:regio.decreto:1940-10-28;1443:1~art83)
```

Di seguito vedi il risultato del mio prompt.

![Immagine dell’interfaccia di Perplexity e realizzazione file skill.md](01-perplexity-skill-preliminare.png)

Ne è uscita una prima versione del file SKILL.md — funzionante, ma non ottimizzata. Un unico file lungo con tutte le tabelle, tutti i casi, tutte le eccezioni. Caricava molto contesto a ogni invocazione.


### 4.2 Seconda fase: la strutturazione con Claude Cowork

Ho fatto l’abbonamento Pro (quello da 22 € mese per intenderci) a [Claude di Anthropic](https://www.anthropic.com/) a Marzo 2026 e, dopo un mese di “prova”, ho deciso di fare quello annuale.

Proprio mentre passavo all’abbonamento annuale Anthropic ha gentilmente deciso di limitare (ulteriormente) il suo utilizzo per i clienti Pro. Sono quindi molto attento ai tokens che utilizzo nelle mie sessioni con le varie sfaccettature di Claude: per me prevalentemente [Claude Cowork](https://claude.com/product/cowork) e [Claude Code](https://claude.com/product/claude-code). 

È proprio per questo motivo che ho fatto fare il lavoro “sporco” prima a Perplexity.

Ho passato, quindi, il materiale a **Claude Cowork** con una richiesta precisa: ristrutturare la skill applicando il principio di _progressive disclosure_ — di cui ti parlo nella sezione successiva — per ridurre il consumo di token senza perdere precisione nei risultati.

![Esempio della skill in Claude Cowork](02-claude-cowork-skill-normattiva.jpeg)

Il risultato è una skill in due file:

- `SKILL.md` — regole essenziali, tabella di lookup rapida con le norme più citate, workflow in tre passi
- `lookup-extended.md` — tabella completa, tipi di atto rari, note sugli allegati, errori comuni

Il file principale è snello. Il file esteso viene letto solo quando serve.

## 5. La skill ottimizzata: progressive disclosure

La **progressive disclosure** è un principio di UX design formulato da Carroll e Rosson all'IBM nel 1983. L'idea: mostra prima solo le informazioni essenziali, e rivela i dettagli solo quando — e solo se — servono davvero.

Applicata al design di una skill per LLM, la logica è identica. Un LLM legge il file `SKILL.md` intero ogni volta che la skill viene invocata: se il file è lungo, consuma molti token. La soluzione è strutturare il contenuto in livelli:

- **Livello 1 (SKILL.md)**: regole fondamentali + tabella rapida delle norme più frequenti (c.c., c.p.c., c.p., Costituzione, i D.Lgs. più usati). Per il 90% dei casi, basta questo.
- **Livello 2 (lookup-extended.md)**: tutto il resto — tipi di atto rari, tabella completa, note sugli allegati, errori comuni. Viene letto *solo* se la norma cercata non è nella tabella rapida.

Il workflow nella skill è esplicito: se la norma è nella quick lookup, genera subito il link; se non c'è, vai a leggere il file esteso (**punto 1** immagine sottostante). 

![Esempio di _progressive disclosure_ nella skill](03-progressive-disclosure.jpeg)

Come ti dicevo, Anthropic è molto “avara” con l’uso dei tokens, per questo motivo, oltre ad ottimizzare la skill con il *grogressive disclosure* ho fatto dei test con Haiku (il modello più leggero e meno costoso di Anthropic) e, dopo aver confermato che gestisce la skill correttamente, ho implementato una ulteriore opzione: la skill come sub-agent (**punto 2** immagine soprastante).

Infatti, per i documenti con molte citazioni normative: la skill prevede di delegare la generazione dei link a un subagente con il modello **Haiku** — più piccolo e veloce — invece di usare il modello principale. Il modello principale rimane libero per i ragionamenti complessi, questa skill infatti è utile a se stante ma molto di più in congiunzione con la generazione di documenti da parte dell’LLM. 

In futuri articoli ti racconterò di come uso Claude Cowork per abbozzare gli atti assieme all’[MCP](https://modelcontextprotocol.io/docs/getting-started/intro) [BuddaLaw](https://www.buddalaw.com/).

 Il lavoro meccanico di costruzione degli URN, così, viene scaricato su un modello più leggero. Stesso principio: usa le risorse giuste per il task giusto.

[Qui]() ho pubblicato la skill: ho creato un repository su GitHub per condividere questa e future skill nel mondo legale.

## 6. Usare la skill negli Spazi di Perplexity e in qualsiasi sistema RAG

Dopo aver creato **la skill**, ho scoperto che **si può usare** anche fuori da Claude; in particolare **in qualsiasi sistema che supporti documenti allegati come fonte di conoscenza**.

Il meccanismo è semplice: alleghi il file `SKILL.md` come documento allo [Spazio di Perplexity](https://www.perplexity.ai/help-center/it/articles/10352961-cosa-sono-gli-spazi) o al tuo sistema RAG (ad esempio [OpenWeb UI](https://docs.openwebui.com/) https://docs.openwebui.com/), e nel _system prompt_ istruisci il modello a consultarlo ogni volta che deve citare riferimenti normativi. Il modello applica le regole della skill come se fossero sue.

Nel video qui sotto puoi vedere come funziona in pratica: Perplexity produce i link URN corretti a Normattiva.it semplicemente perché ha il file SKILL.md a disposizione.

{{VIDEO: https://youtu.be/jyTRHz-e4vM}}

Lo stesso approccio funziona con **NotebookLM** (anche se può essere limitato se non esegue le ricerche online delle norme – da cui vengono estrapolate i dati per generare l’URN). 
Teoricamente questa “skill” funziona anche con gli spazi documentali di sistemi specializzati legali come [Lexroom](https://www.lexroom.ai/),  [BuddaLaw](https://www.buddalaw.com/) o [DIKAIA](https://www.dikaia.ai/) o similare, e con qualsiasi altro sistema che consenta di allegare file e personalizzare il system prompt. 

Il file diventa un modulo portabile: lo prepari una volta e lo alleghi dove ti serve.

Ovviamente **questo principio** non **si applica** solo alla mia skill, ma **a qualsiasi skill**. È uno dei corollari più interessanti e meno utilizzati delle capacità linguistiche degli LLM. 

È il mio _hack_ che ti regalo.

## In conclusione

Ho costruito la versione iniziale della skill in un pomeriggio con Perplexity, l'ho ottimizzata con Claude Cowork applicando il principio di _progressive disclosure_, e adesso la uso sia in Claude che negli Spazi di Perplexity. Il mio sistema genera i link URN corretti a Normattiva.it senza che io debba pensarci, e nei documenti per il PCT mi aiuta a soddisfare uno dei requisiti per poter richiedere la maggiorazione del 30% sul compenso professionale. Win win!

Il _vibe coding_ — inteso come "descrivere in linguaggio naturale quello che vuoi all’LLM ed iterare finché funziona" — è una di quelle cose che all'inizio sembrano “cose da programmatore”, lontane dal mondo legale, spero con questo articolo di averti dimostrato il contrario.  
Usando il _vibe coding_ non è necessario saper scrivere codice. È necessario saper descrivere con precisione cosa si vuole ottenere; come avvocati dovremmo essere in grado di farlo.

Come sempre, se ti è piaciuto quel che hai letto o visto e non l'hai già fatto, ti suggerisco di iscriverti alla mia [newsletter](https://www.avvocati-e-mac.it/mailinglist). Ti avvertirò dei nuovi articoli che pubblico (oltre ai podcast e video su YouTube) e, mensilmente, ti segnalerò articoli che ho raccolto nel corso del mese ed ho ritenuto interessanti.

---
Annotazioni: 0,18580 SHA-256 ac22e414f68daf44fbba  
&IA: 0,59 60,30 1004,40 1046,80 1128,62 1191,13 1232,63 1296,6 1304,24 1349,56 1408,41 1452,46 1499,11 1595,16 1612,69 1682 1713,215 1929,105 2079,2 2177,56 2249,5 2256,53 2335 2338,37 2378,6 2394,37 2448,89 2592,235 2828,20 2849,712 3570,179 3883,96 3980,282 4298 4301,34 4370,7 4386,73 4553,290 4970,735 5995,2 5999,85 6091,2 6111,11 6123,2 6126,121 6294,100 6571,107 6701,2 7676,38 7715 7757,30 7789,467 8257,5 8263,54 8328,4 8333,3 8359,25 8385,6 8412,204 8618,10 8630,851 9482 9488,148 9639 9847,103 9951,11 9963,42 10006,93 10101,146 10249,67 10318,10 10357,2 11515,203 11719,61 12439,10 12458,111 12570,22 12593,117 12791,1346 14172,2 14657,267 15252 15254,43 15304,105 15530,23 15567,57 15626,8 15636,18 15656,12 15670,22 15708 15711,77 15790,76 15868,5 15968,6 15978,11 16072,8 16081,13 16095,148 16244,259 16635 16779 16781,7 16863,97 16962,87 17274,161 17436,22 17459,63 17538,142 17717,5 17748 17758,5 17764,11 17776,65 17852,73 18035,2 18064,106 18220,360  
@Filippo Strozzi <info@studiolegalestrozzi.com>: 59 90,914 1044,2 1126,2 1190 1204,28 1295 1302,2 1328,21 1405,3 1449,3 1498 1510,3 1594 1611 1681 1683,30 1928 2034,45 2081,96 2233,16 2254,2 2309,26 2336,2 2375,3 2384,10 2431,17 2537,55 2827 2848 3561,9 3749,134 3979 4262,36 4299,2 4335,35 4377,9 4459,94 4843,127 5705,290 5997,2 6084,7 6093,18 6122 6125 6247,47 6394,177 6678,23 6703,629 7452,22 7533,143 7714 7716,41 7787,2 8256 8262 8317,11 8332 8336,23 8384 8391,21 8616,2 8628,2 9481 9483,5 9636,3 9640,23 9684,20 9716,13 9845,2 9950 9962 10005 10099,2 10247,2 10316,2 10328,2 10356 10359,300 10813 10943 11007 11017 11352,125 11512,3 11718 11780,148 11935,474 12417,22 12449,9 12569 12592 12710,42 12790 14137,35 14174,53 14257,400 14924,299 15248,4 15253 15297,7 15409,121 15553,14 15624,2 15634,2 15654,2 15668,2 15692,16 15709,2 15788,2 15866,2 15873,95 15974,4 15989,55 16071 16080 16094 16243 16503,132 16636,143 16780 16788,41 16851,12 16960,2 17049,225 17435 17458 17522,16 17680,37 17722,26 17749,9 17763 17775 17841,11 17948,87 18037,27 18170,50  
...
