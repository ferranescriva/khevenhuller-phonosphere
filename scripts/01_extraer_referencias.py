#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extraer_referencias.py
======================

Extrae de un dietario (PDF con OCR limpio, en castellano y con entradas
datadas) todas las referencias vinculadas a música, representación, indicios
sonoros / de ruido y cultura material festiva.

Salida: un fichero .xlsx con una fila por hallazgo (fecha, página, categoría,
término, texto detectado y cita de contexto) más una hoja de recuento.
Opcionalmente, un .csv paralelo (cómodo para control de versiones en git).

USO
---
    python3 extraer_referencias.py dietario.pdf
    python3 extraer_referencias.py dietario.pdf -o salida.xlsx --csv
    python3 extraer_referencias.py dietario.pdf --page-offset 12
    python3 extraer_referencias.py dietario.pdf --lexicon mi_lexico.json

INSTALACIÓN (macOS)
-------------------
    python3 -m pip install --user pdfplumber openpyxl
  (o, mejor, dentro de un entorno virtual:)
    python3 -m venv .venv && source .venv/bin/activate
    pip install pdfplumber openpyxl

EL LÉXICO ES EDITABLE
---------------------
El diccionario LEXICON (más abajo) es el corazón del método y está pensado
para ampliarse iterativamente. Cada término se empareja como palabra completa,
sin acentos ni distinción de mayúsculas, admitiendo el plural español y los
saltos de línea del OCR. Un término terminado en '*' funciona como raíz
(p. ej. 'repic*' captura repicar / repique / repicaron). Los términos con
varias palabras ('arcos triunfales') se emparejan tolerando espacios y saltos
de línea intermedios. Cada término pertenece a UNA sola categoría (elección
curatorial que evita filas duplicadas); muévelos si te conviene otra adscripción.
"""

import argparse
import bisect
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

# ---------------------------------------------------------------------------
# LÉXICO. Amplíalo/edítalo libremente. '*' = raíz; espacios = multipalabra.
# ---------------------------------------------------------------------------
LEXICON = {
    "musica": [
        # voces genéricas
        "música", "músic*", "sonar", "sonó", "sonaron", "sonaba", "sonando",
        # instrumentos y agrupaciones
        "ministril", "ministriles", "chirimía", "sacabuche", "bajón", "corneta",
        "trompeta", "clarín", "atabal", "atambor", "tambor", "timbal", "pífano",
        "dulzaina", "tamboril", "gaita", "arpa", "vihuela", "guitarra", "laúd",
        "órgano", "organista", "cantor", "cantores", "capilla de música",
        "maestro de capilla", "coro", "coros", "seises",
        # géneros y formas
        "villancico", "motete", "canción", "canto llano", "canto de órgano",
        "misa", "Te Deum", "tedeum", "salve", "himno", "letanía", "responso",
        "romance", "copla", "coplas", "tono", "tonada", "folía", "chacona",
        "zarabanda", "seguidilla",
        # acciones
        "cantar", "cantó", "cantaron", "cantando", "cantaban", "cantan",
        "canto", "cantos", "entonar", "entonó", "entonaron",
        "tañer", "tañó", "tañía", "tañían", "tañen", "tañendo", "tañido",
        "tañidos", "tocar música", "tocaron", "concierto", "concento",
    ],
    "representacion": [
        "comedia", "auto sacramental", "auto", "autos", "entremés", "entremeses",
        "farsa", "mojiganga", "máscara", "mascarada", "sarao", "danza", "danzas",
        "danzar", "baile", "bailes", "tablado", "carro", "carro triunfal",
        "carros triunfales", "tramoya", "invención", "invenciones", "comediante",
        "farsante",
        "coloquio", "loa", "jácara", "momo", "momos", "momería", "gigantes",
        "gigantones", "tarasca", "cabezudos", "fin de fiesta",
    ],
    "sonoro_ruido": [
        # campanas
        "campana", "campanas", "campanas al vuelo", "repic*", "esquila",
        "esquilas", "campanario", "tañido de campanas",
        # pólvora / armas / estruendo
        "salva", "salvas", "arcabuz", "arcabuces", "arcabucería", "mosquete",
        "mosquetería", "artillería", "tiro", "tiros", "cañonazo", "cañonazos",
        "pólvora", "cohete", "cohetes", "petardo", "morterete", "morteretes",
        "bombarda", "estruendo", "estampido", "traca",
        # voz colectiva
        "algazara", "vocería", "vítor", "vítores", "aclam*", "gritos", "grita",
        "alarido", "alaridos", "clamor", "bullicio", "estrépito",
        # pregón y marcadores de sonido/silencio
        "pregón", "pregones", "pregonar", "pregonó", "silencio",
        "disparar", "disparó", "dispararon", "disparo", "disparos",
    ],
    "cultura_material": [
        # luces
        "luminaria", "luminarias", "hacha de cera", "hachas de cera", "cirio",
        "cirios", "vela", "velas", "antorcha", "antorchas", "tea", "teas",
        "farol", "faroles", "fuego", "fuegos", "fuegos artificiales",
        "castillo de fuego", "rueda de fuego", "girándula",
        # textiles y arquitectura efímera
        "colgadura", "colgaduras", "tapiz", "tapices", "dosel", "palio",
        "andas", "peana", "tálamo", "altar", "altares", "arco triunfal",
        "arcos triunfales", "arco de triunfo", "enramada", "ramaje",
        # insignias
        "pendón", "pendones", "estandarte", "estandartes", "bandera", "banderas",
        "gallardete", "guión", "pabellón", "librea", "libreas", "galas",
        # funerario y visual/emblemático
        "túmulo", "túmulos", "catafalco", "pira", "retablo", "jeroglífico",
        "jeroglíficos", "emblema", "tarja", "insignia",
    ],
    "fiesta_ceremonia": [
        "fiesta", "fiestas", "festividad", "festividades", "celebración",
        "celebrar", "celebró", "celebraron", "procesión", "procesiones",
        "entrada", "recibimiento", "cortejo", "comitiva", "desfile", "séquito",
        "Corpus", "Corpus Christi", "canonización", "beatificación", "exequias",
        "honras", "aniversario", "centenario", "jura", "proclamación",
        "coronación", "boda", "casamiento", "bautizo", "rogativa", "novena",
        "octavario", "triunfo", "torneo", "justa", "sortija", "toros",
        "juego de cañas", "auto de fe",
    ],
}

CATEGORIAS_ES = {
    "musica": "Música",
    "representacion": "Representación / danza",
    "sonoro_ruido": "Indicios sonoros / ruido",
    "cultura_material": "Cultura material festiva",
    "fiesta_ceremonia": "Fiesta / ceremonia",
}

# ---------------------------------------------------------------------------
# Normalización que PRESERVA la longitud (para no desalinear los offsets).
# ---------------------------------------------------------------------------
def fold(text):
    out = []
    for ch in text:
        base = "".join(c for c in unicodedata.normalize("NFD", ch)
                       if not unicodedata.combining(c))
        out.append(base.lower() if len(base) == 1 else ch.lower())
    return "".join(out)


# ---------------------------------------------------------------------------
# Fechas (dietario en castellano con entradas datadas).
# ---------------------------------------------------------------------------
MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}
WEEKDAYS = "lunes|martes|miercoles|jueves|viernes|sabado|domingo"
DATE_RE = re.compile(
    r"(?<!\w)(?:a\s+|en\s+|el\s+)?(?:dia\s+)?"
    r"(?:(?:" + WEEKDAYS + r")[,\s]+)?"
    r"(\d{1,2})\s+de\s+(" + "|".join(MESES) + r")"
    r"(?:\s+de\s+(\d{3,4}))?"
)


def find_dates(folded, raw):
    """Devuelve lista ordenada de (offset, fecha_norm, fecha_raw)."""
    dates = []
    last_year = None
    for m in DATE_RE.finditer(folded):
        day = int(m.group(1))
        month = MESES[m.group(2)]
        year = int(m.group(3)) if m.group(3) else last_year
        if m.group(3):
            last_year = year
        if year:
            norm = f"{year:04d}-{month:02d}-{day:02d}"
        else:
            norm = f"----{month:02d}-{day:02d}"
        raw_str = re.sub(r"\s+", " ", raw[m.start():m.end()]).strip()
        dates.append((m.start(), norm, raw_str))
    return dates


# ---------------------------------------------------------------------------
# Carga del PDF y construcción del corpus (con mapa offset -> página).
# ---------------------------------------------------------------------------
def dehyphenate(t):
    if not t:
        return ""
    # une palabras partidas por guion al final de línea (proce-\nsión)
    return re.sub(r"(\w)[\-\u00ad]\s*\n\s*(\w)", r"\1\2", t)


# marca de nº de página impreso: "23 ■" o "■ 24" (glifo cuadro negro)
PAGENUM_RE = re.compile(r"■\s*(\d{1,4})|(\d{1,4})\s*■")
# línea suelta que es solo un entero (nº de página sin glifo, p. ej. portada/índice)
LONE_INT_RE = re.compile(r"^\s*(\d{1,4})\s*$", re.MULTILINE)


def _pick_page_number(chunk, expected):
    """Elige el nº de página impreso más plausible dentro del fragmento."""
    cands = [int(a or b) for a, b in PAGENUM_RE.findall(chunk)]
    if cands:
        return min(cands, key=lambda n: abs(n - expected))
    lone = [int(x) for x in LONE_INT_RE.findall(chunk)]
    near = [n for n in lone if abs(n - expected) <= 3]
    if near:
        return min(near, key=lambda n: abs(n - expected))
    return expected


def _strip_markers(chunk):
    """Quita marcas de página del texto visible (no de la numeración)."""
    chunk = PAGENUM_RE.sub(" ", chunk)
    chunk = chunk.replace("■", " ")
    return chunk


def load_markdown_pages(path):
    text = Path(path).read_text(encoding="utf-8")
    # elimina el título markdown de cabecera (primera línea '# ...') si existe
    text = re.sub(r"\A#.*\n", "", text, count=1)
    chunks = text.split("\f")
    pages, expected = [], 1
    for chunk in chunks:
        num = _pick_page_number(chunk, expected)
        pages.append((num, _strip_markers(chunk)))
        expected = num + 1
    return pages


def load_pdf_pages(path):
    try:
        import pdfplumber
    except ImportError:
        sys.exit("Falta pdfplumber. Instálalo con:\n"
                 "    python3 -m pip install --user pdfplumber openpyxl")
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            pages.append((i, page.extract_text() or ""))
    return pages


def load_pages(path):
    ext = Path(path).suffix.lower()
    if ext in (".md", ".markdown", ".txt"):
        return load_markdown_pages(path)
    return load_pdf_pages(path)


def build_corpus(pages, page_offset=0):
    texts, page_starts, cursor = [], [], 0
    for idx, text in pages:
        cleaned = dehyphenate(text)
        page_starts.append((cursor, idx + page_offset))
        texts.append(cleaned)
        cursor += len(cleaned) + 1  # +1 por el '\n' de unión
    return "\n".join(texts), page_starts


def page_for(offset, starts_offsets, page_starts):
    i = bisect.bisect_right(starts_offsets, offset) - 1
    return page_starts[max(i, 0)][1]


def date_for(offset, date_offsets, dates):
    i = bisect.bisect_right(date_offsets, offset) - 1
    if i < 0:
        return "(sin fecha)", ""
    return dates[i][1], dates[i][2]


# ---------------------------------------------------------------------------
# Matchers y extracción.
# ---------------------------------------------------------------------------
def make_pattern(term):
    folded = fold(term.strip())
    if folded.endswith("*"):
        stem = re.escape(folded[:-1])
        return re.compile(r"\b" + stem + r"\w*")
    parts = [re.escape(p) for p in folded.split()]
    core = r"\s+".join(parts)
    return re.compile(r"\b" + core + r"(?:es|s)?\b")


def build_matchers(lexicon):
    matchers = []
    for category, terms in lexicon.items():
        for term in terms:
            matchers.append((category, term, make_pattern(term)))
    return matchers


def get_context(raw, s, e, max_len=600, pad=180):
    seps = ".;:!?\n"
    left = max((raw.rfind(ch, 0, s) for ch in seps), default=-1)
    rights = [r for r in (raw.find(ch, e) for ch in seps) if r != -1]
    right = min(rights) if rights else len(raw)
    ctx = raw[left + 1:right + 1].strip()
    if len(ctx) > max_len:
        ctx = raw[max(0, s - pad):min(len(raw), e + pad)].strip()
    return re.sub(r"\s+", " ", ctx).strip(" .;:,")


def extract(folded, raw, matchers, page_starts, dates):
    starts_offsets = [cs for cs, _ in page_starts]
    date_offsets = [d[0] for d in dates]
    seen, rows = set(), []
    for category, term, rx in matchers:
        for m in rx.finditer(folded):
            key = (m.start(), m.end(), category)
            if key in seen:
                continue
            seen.add(key)
            fecha, entrada = date_for(m.start(), date_offsets, dates)
            rows.append({
                "_off": m.start(),
                "fecha": fecha,
                "entrada": entrada,
                "pagina": page_for(m.start(), starts_offsets, page_starts),
                "categoria": CATEGORIAS_ES.get(category, category),
                "termino": term,
                "detectado": raw[m.start():m.end()],
                "cita": get_context(raw, m.start(), m.end()),
            })
    rows.sort(key=lambda r: r["_off"])
    for n, r in enumerate(rows, start=1):
        r["id"] = n
    return rows


# ---------------------------------------------------------------------------
# Salidas.
# ---------------------------------------------------------------------------
COLS = [("id", "id"), ("fecha", "fecha"), ("entrada", "entrada (texto)"),
        ("pagina", "página"), ("categoria", "categoría"),
        ("termino", "término (lema)"), ("detectado", "detectado"),
        ("cita", "cita / contexto")]


def write_xlsx(rows, path):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, Alignment, PatternFill
    except ImportError:
        sys.exit("Falta openpyxl. Instálalo con:\n"
                 "    python3 -m pip install --user openpyxl")

    wb = Workbook()
    ws = wb.active
    ws.title = "Referencias"
    header_fill = PatternFill("solid", fgColor="1F3864")
    header_font = Font(bold=True, color="FFFFFF")

    ws.append([label for _, label in COLS])
    for c in ws[1]:
        c.fill, c.font = header_fill, header_font
        c.alignment = Alignment(vertical="center")
    for r in rows:
        ws.append([r[k] for k, _ in COLS])
    # ancho y ajuste de texto
    widths = {"id": 6, "fecha": 12, "entrada": 20, "pagina": 8,
              "categoria": 24, "termino": 20, "detectado": 18, "cita": 90}
    for i, (key, _) in enumerate(COLS, start=1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = widths[key]
    cita_col = len(COLS)
    for row in ws.iter_rows(min_row=2, min_col=cita_col, max_col=cita_col):
        row[0].alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    # anadir una columna vacía "notas" para anotación manual
    ws.cell(1, len(COLS) + 1, "notas").font = header_font
    ws.cell(1, len(COLS) + 1).fill = header_fill
    ws.column_dimensions[ws.cell(1, len(COLS) + 1).column_letter].width = 40

    # hoja de recuento
    ws2 = wb.create_sheet("Resumen")
    from collections import Counter
    por_cat = Counter(r["categoria"] for r in rows)
    por_ter = Counter(r["termino"] for r in rows)
    ws2.append(["Categoría", "nº"])
    for cat, n in sorted(por_cat.items(), key=lambda x: -x[1]):
        ws2.append([cat, n])
    ws2.append(["TOTAL", len(rows)])
    ws2.append([])
    ws2.append(["Término", "nº"])
    for ter, n in sorted(por_ter.items(), key=lambda x: -x[1]):
        ws2.append([ter, n])
    for c in list(ws2["1"]) + [ws2.cell(len(por_cat) + 4, 1),
                               ws2.cell(len(por_cat) + 4, 2)]:
        c.font = Font(bold=True)
    ws2.column_dimensions["A"].width = 28
    ws2.column_dimensions["B"].width = 8

    wb.save(path)


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([label for _, label in COLS])
        for r in rows:
            w.writerow([r[k] for k, _ in COLS])


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="ruta al fichero del dietario (.md, .txt o .pdf)")
    ap.add_argument("-o", "--output", help="ruta del .xlsx de salida")
    ap.add_argument("--csv", action="store_true", help="además, escribir .csv")
    ap.add_argument("--page-offset", type=int, default=0,
                    help="sumar este valor al nº de página del PDF "
                         "(p. ej. si el texto empieza en la pág. 13 del PDF)")
    ap.add_argument("--lexicon", help="JSON {categoria: [términos]} que amplía "
                                      "el léxico interno")
    ap.add_argument("--replace", action="store_true",
                    help="con --lexicon, REEMPLAZA el léxico interno en vez de "
                         "ampliarlo (útil para perfiles temáticos)")
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        sys.exit(f"No existe el fichero: {pdf_path}")
    out_path = Path(args.output) if args.output else \
        pdf_path.with_name(pdf_path.stem + "_referencias.xlsx")

    lexicon = {} if args.replace else {k: list(v) for k, v in LEXICON.items()}
    if args.lexicon:
        extra = json.loads(Path(args.lexicon).read_text(encoding="utf-8"))
        for cat, terms in extra.items():
            lexicon.setdefault(cat, [])
            CATEGORIAS_ES.setdefault(cat, cat)
            lexicon[cat].extend(terms)

    print(f"Leyendo {pdf_path} ...")
    pages = load_pages(pdf_path)
    raw, page_starts = build_corpus(pages, args.page_offset)
    folded = fold(raw)
    assert len(folded) == len(raw), "desalineación en fold()"

    dates = find_dates(folded, raw)
    matchers = build_matchers(lexicon)
    rows = extract(folded, raw, matchers, page_starts, dates)

    write_xlsx(rows, out_path)
    if args.csv:
        csv_path = out_path.with_suffix(".csv")
        write_csv(rows, csv_path)

    from collections import Counter
    por_cat = Counter(r["categoria"] for r in rows)
    print(f"\nPáginas procesadas : {len(pages)}")
    print(f"Fechas detectadas  : {len(dates)}")
    print(f"Referencias totales: {len(rows)}")
    for cat, n in sorted(por_cat.items(), key=lambda x: -x[1]):
        print(f"  - {cat:<28} {n}")
    print(f"\nEscrito: {out_path}")
    if args.csv:
        print(f"Escrito: {csv_path}")


if __name__ == "__main__":
    main()
