# A Habsburg Ambassador's Phonosphere

**English** · [Español](README.es.md)

Supplementary material for the article «A Habsburg Ambassador's Phonosphere: Musical Experience and Material Culture in the Writings of Hans Khevenhüller».

This repository holds the data, the lexical instrument and the scripts used to extract and code the musical and sonic references in the writings of Hans Khevenhüller (1538-1606), ambassador of Emperors Maximilian II and Rudolf II to Philip II of Spain.

**Web presentation:** `index.html` (open in a browser, or consult it on GitHub Pages). The page is bilingual and switches between Spanish and English.

**Deployment:** see [`DEPLOY.md`](DEPLOY.md) for the steps to publish on GitHub Pages and mint a DOI through Zenodo.

---

## 1. What this repository holds

| Folder | Contents |
|---|---|
| `data/` | Data tables in CSV and the lexicon in JSON |
| `scripts/` | The six programs of the extraction pipeline |
| `index.html` | Self-contained bilingual web presentation |

The repository **does not include the source texts**, which are editions under copyright. It distributes only derived data, with quotations of the brief length proper to scholarly commentary. Reproducing the pipeline requires access to the editions and digitising them independently.

## 2. Corpus

The work rests on two complementary Spanish editions. Both translate the German original and are therefore not always literal, but both are taken as valid.

**Edition A. The diary.**
Khevenhüller, Hans. *Diario de Hans Khevenhüller: embajador imperial en la corte de Felipe II*. Edited by Sara Veronelli and Félix Labrador Arroyo. Madrid: Sociedad Estatal para la Conmemoración de los Centenarios de Felipe II y Carlos V, 2001.

It gives the continuous text in period Spanish and is the main source for musical activity as lived, that is, for listening, attendance and judgement. The digitisation used here covers Book XIV and preserves the printed pagination through `[p. N]` markers.

**Edition B. The documents.**
Alvar Ezquerra, Alfredo (ed.). *El embajador imperial. Hans Khevenhüller (1538-1606) en España*. Madrid: Boletín Oficial del Estado, 2015.

A critical edition arranging the diary by year alongside letters and varied documentation. It supplies the inventory, the auction and the customs licences, which are the basis of the evidence on material culture.

The title *Geheimes Tagebuch* (Secret Diary) was added by Georg Khevenhüller in the 1971 edition. The ambassador wrote the text as a *Khurzer Extrakt*.

## 3. Extraction procedure

The pipeline has six steps, each one a script in `scripts/`.

**Step 1. Lexical extraction over the whole corpus.**
`01_extraer_referencias.py` reads the text, rebuilds the printed pagination, detects the dated entries and locates the terms of a lexicon organised by category. Normalisation strips accents and case for matching but keeps the original spelling in the quotation. Matching tolerates plurals, OCR line breaks and multi-word terms. A term ending in an asterisk works as a stem.

**Step 2. Audit of the instrument and evaluative sweep.**
`02_auditoria_y_evaluativos.py` counts the occurrences of each term in the lexicon and flags passages with a qualifier in their immediate surroundings. The audit is kept whole, including terms with zero occurrences, because recording what was searched for and not found is part of the result.

**Step 3. Extraction of the funerary material.**
`03_analisis_exequias.py` locates passages on exequies, honours and burials, assigns the probable deceased by name proximity, and labels each one as the diary's voice or the editor's apparatus.

**Step 4. Phonospheric coding.**
`04_capa_escucha.py` is the central step. It locates the passages with musical vocabulary in the diary and codes each one along the three axes described in section 5.

**Step 5. Coding workbook for manual review.**
`05_libro_codificacion.py` generates a spreadsheet with validated dropdown lists, meant for reviewing the automatic coding by hand.

**Step 6. Web presentation.**
`06_construir_web.py` reads the CSV files, computes the counts and writes `index.html` with the data embedded. The page depends on no external file and no connection, so it behaves the same served by GitHub Pages and downloaded from Zenodo.

## 4. Lexical instrument

The lexicon lives in `data/lexico_fonosfera.json` and is organised in four fields.

| Field | Contents |
|---|---|
| Música | generic terms, instruments, ensembles, genres and musical actions |
| Sonido y ruido | bells, gunpowder and artillery, collective voice, proclamation and silence |
| Voz y rumor | rumour, murmuring and sub-audible speech |
| Metáfora musical | musical vocabulary migrated into political and diplomatic language |

The audit in `data/auditoria_lexico.csv` records the occurrences of each term. Of the 158 terms in the instrument, 73 occur in the corpus and 85 do not. The absences are informative. Not a single cannon shot, musket, rocket, cheer or uproar is recorded, and neither «murmullo» nor «murmurar» appears.

The semantic anchoring of ambiguous terms was fixed in the lexicography of the period, namely in Sebastián de Covarrubias's *Tesoro de la lengua castellana o española* (Madrid, 1611). Three entries proved decisive.

- **Murmullo.** «El ruido manso que haze el agua corriente, *a murmure*, por la figura onomatopeya. Y de allí *murmurar*, que es dezir mal de alguno, medio entre dientes.» Sound resides here, not in «rumor».
- **Rumor.** «Lo que se dize, no en público, pero se esparce secretamente en el Pueblo.» By 1611 the word is informational and has no acoustic component.
- **Salva.** Covarrubias brings three senses under the root of *salvo*: the steward's tasting of dishes, the discharge of harquebuses «en demostración de reconocimiento, paz, amistad», and the silver salver. Only the second is phonospheric. In this corpus the sounding salvo appears once, and the artillery landscape travels under «artillería», «disparo» and «arcabucería».

## 5. Coding axes

The coding applies Antonio Rostagno's framework of the historical phonosphere, which distinguishes *pedal* or background sound, *signal* and *symbol*. Each musical passage is coded along three axes.

**Domain.** Where the sound occurs: sacred and liturgical, secular and courtly, military and signalling, or other. It is decided by the context markers present in a window of 320 characters on either side of the passage.

**Level.** How the sound functions in Rostagno's triad. Sound in the military domain is coded as signal, that is, as an indication that orders or warns with no intent to signify beyond its function. Ceremonial, sacred or courtly sound is coded as symbol, charged with communicative intent. The same instrument changes level with the context, and the clearest case is the trumpet.

**Listener's stance.** What the witness does with what he hears. He confines himself to recording the event, weighs its magnitude through formulas of abundance, or delivers an aesthetic judgement. The third case is the one that documents expert listening.

Four descriptive fields are added to these axes: the aesthetic qualifiers used, the instruments named, the genres or liturgical pieces mentioned, and the presence of explicit markers of listening.

## 6. Data dictionary

### `data/escucha_codificacion.csv`
The 103 coded musical passages of the diary. This is the central table. Column values are in Spanish; the English equivalents used in the web presentation are listed in `06_construir_web.py`.

| Column | Description |
|---|---|
| `id` | sequential identifier in order of appearance |
| `pagina` | printed page of the Veronelli and Labrador Arroyo edition |
| `termino` | musical term that triggered the detection |
| `ambito` | sacro / profano-cortesano / militar-señalético / otros |
| `nivel_rostagno` | índice (signal) / símbolo (symbol) |
| `postura_oyente` | registro (record) / ponderación de magnitud (magnitude) / valoración estética (aesthetic judgement) |
| `cualificadores` | aesthetic qualifiers present in the quotation |
| `magnitud` | formulas of abundance present in the quotation |
| `instrumentos_nombrados` | instruments explicitly named |
| `generos_piezas` | genres or liturgical pieces named |
| `escucha_explicita` | flags verbs or objects of listening |
| `cita` | the full sentence from the diary |

### `data/exequias_pasajes.csv`
621 passages on exequies, honours and burials extracted from the Alvar Ezquerra edition, with a `voz` column separating the diary's narration from the editor's apparatus.

### `data/referencias_fonosfera.csv`
577 references from the broad sweep over the Alvar Ezquerra edition, with coding columns prepared for manual review.

### `data/auditoria_lexico.csv`
Occurrences of each of the 158 terms in the lexical instrument.

### `data/lexico_fonosfera.json`
The full lexicon, editable. It feeds scripts 1 and 2.

## 7. Reproduction

The scripts require Python 3.8 or later. Steps 4 and 6 use only the standard library. Steps 1, 3 and 5 require `openpyxl`, and step 1 also requires `pdfplumber` if starting from a PDF rather than text.

Corpus transcriptions go in the `corpus/` folder, distributed empty for the reasons given in section 1.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install openpyxl pdfplumber

# Step 4, the central coding
python3 scripts/04_capa_escucha.py corpus/diario_veronelli_labrador.md \
        -o data/escucha_codificacion.csv

# Step 6, rebuild the web presentation
python3 scripts/06_construir_web.py
```

Scripts 2, 3 and 5 carry the corpus paths as constants at the top of the file and these must be adjusted locally. Transcriptions are expected to preserve the printed pagination through `[p. N]` markers.

## 8. Limits

The coding is automatic and therefore open to revision. It is a starting point for critical reading, not a closed result. Three specific warnings.

The corpus comes from two translations of the German that are not always literal, so conclusions about the vocabulary of appreciation should be taken with the caution that chain of transmission imposes.

The figures are indicative rather than statistical, given how uneven the subsamples are. The secular domain gathers 12 passages and the sacred 54, so comparing their shares of judgement calls for care.

The assignment of the deceased in the exequies table is made by name proximity and needs case-by-case verification, especially in rows marked with a question mark.

## 9. Citation

> Escrivà-Llorca, Ferran. *Fonosfera de un embajador imperial: datos y código*. Supplementary material. 2026. [DOI pending]

For the article this material accompanies, see the full reference in the publication itself.

## 10. Licence

Data are released under Creative Commons Attribution 4.0 International (CC BY 4.0). Code is released under the MIT licence. Quotations from the diary come from editions under copyright and are reproduced at the brief length proper to scholarly commentary.
