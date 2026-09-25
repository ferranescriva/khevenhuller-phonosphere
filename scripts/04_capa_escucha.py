#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_capa_escucha.py
==================

Capa de codificacion fonosferica sobre los pasajes musicales del diario de Hans
Khevenhueller (ed. Veronelli y Labrador Arroyo, 2001).

El script localiza en el texto los pasajes con vocabulario musical y codifica
cada uno segun tres ejes:

  ambito              sacro / profano-cortesano / militar-senaletico / otros
  nivel (Rostagno)    indice / simbolo
  postura del oyente  registro / ponderacion de magnitud / valoracion estetica

Ademas extrae, para cada pasaje, los cualificadores esteticos empleados, los
instrumentos nombrados, los generos o piezas liturgicas mencionados y si hay
marcadores explicitos de escucha (oir, sonar, voces).

USO
---
    python3 04_capa_escucha.py diario.md -o escucha_codificacion.csv

El fichero de entrada es la transcripcion del diario en texto plano o Markdown,
con marcadores de pagina impresa con la forma [p. N].

SALIDA
------
Un CSV con una fila por pasaje y las columnas descritas en el diccionario de
datos del README. La codificacion es automatica y por tanto revisable: es un
punto de partida para la lectura critica, no un resultado definitivo.

DEPENDENCIAS
------------
Solo biblioteca estandar de Python 3.
"""

import argparse
import bisect
import csv
import re
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Vocabulario musical. Define que cuenta como pasaje musical.
# ---------------------------------------------------------------------------
TERMINOS_MUSICALES = [
    r"m[uú]sic\w+",
    r"capilla de (m[uú]sica|cantores)", r"\bcapilla\b",
    r"cantor\w*", r"cantaron", r"cant[oó] de [óo]rgano", r"canto llano", r"\bchoro\b",
    r"chirim\w+", r"\btrompet\w+", r"sacab\w+", r"corneta\w*", r"\bflauta\w*",
    r"atabal\w*", r"menestril\w*", r"ministril\w*", r"\b[óo]rgano\w*", r"clar[íi]n\w*",
    r"villancico\w*", r"motete\w*", r"ant[íi]fona\w*|antipho?n\w+", r"letan[íi]a\w*",
    r"h[iy]mno\w*", r"te ?deum", r"missa cantada|misa cantada", r"v[íi]speras",
    r"\bsalve\b", r"responso\w*", r"\bsarao\w*", r"\bdan[cç]a\w*", r"\bbaile\w*",
    r"\bta[ñn](?:er|[oó]|en|[ií]an?|endo|id[oa]s?)\b",
]

# ---------------------------------------------------------------------------
# 2. Lexicos de codificacion.
# ---------------------------------------------------------------------------
# Cualificadores esteticos: marcan una valoracion de la calidad de lo oido.
CUALIFICADORES = (
    r"suauidad|suavidad|suaue\w*|suave\w*|harmon\w+|armon\w+|mucha arte|con arte|"
    r"concertad\w+|diestr\w+|esmer\w+|excelen\w+|marauill\w+|maravill\w+|admirab\w+|"
    r"l[úu]cid\w+|solem\w+|grandioso|magnific\w+|herm[oó]s\w+|dulce\w*|graue|"
    r"primor\w+|destreza"
)
# Formulas de abundancia: ponderan la magnitud, no la calidad.
MAGNITUD = (
    r"\bmuch[oa]s?\b|\bgran(?:de|des)?\b|grand[íi]ssim\w+|infinit\w+|innumerab\w+|"
    r"todo g[ée]nero|copios\w+|abundan\w+"
)
# Marcadores de escucha explicita.
ESCUCHA = (
    r"\bo[ií]r\b|\bo[ií]a\b|oyendo|\bse oy[óo]\b|escuch\w+|son[óo]|sonaua|"
    r"call[óo]|callado|\bvozes\b|\bvoces\b"
)
# Instrumentos nombrados: precision organologica.
INSTRUMENTOS = (
    r"chirim\w+|trompet\w+|sacab\w+|corneta\w*|flauta\w*|atabal\w*|[óo]rgano\w*|"
    r"clar[íi]n\w*|menestril\w*|ministril\w*"
)
# Generos y piezas liturgicas nombradas.
GENEROS = (
    r"te ?deum|h[iy]mno\w*|ant[íi]fona\w*|antipho?n\w+|letan[íi]a\w*|responso\w*|"
    r"v[íi]speras|misa|missa|villancico\w*|motete\w*|salve"
)
# Marcadores de ambito.
AMBITO_SACRO = (
    r"misa|missa|yglesia|iglesia|altar|arçobispo|obispo|coro|choro|capilla|"
    r"te ?deum|v[íi]speras|responso|letan[íi]a|ant[íi]fona|honras|obsequias|difunt"
)
AMBITO_PROFANO = (
    r"sarao|fest[íi]n|dan[cç]a|baile|torneo|justa|m[áa]scara|enmascarad|"
    r"carro triunfal|entrada|bodas|casamiento"
)
AMBITO_MILITAR = (
    r"campo|batalla|ex[ée]rc|soldado|caualler[íi]a|escuadr|esquadr|arma|"
    r"artiller|acomet|guerra|sitio"
)

RX_TERMINOS = re.compile("|".join(TERMINOS_MUSICALES), re.I)
RX_CUAL = re.compile(CUALIFICADORES, re.I)
RX_MAGN = re.compile(MAGNITUD, re.I)
RX_ESCUCHA = re.compile(ESCUCHA, re.I)
RX_INSTR = re.compile(INSTRUMENTOS, re.I)
RX_GEN = re.compile(GENEROS, re.I)
RX_SACRO = re.compile(AMBITO_SACRO, re.I)
RX_PROF = re.compile(AMBITO_PROFANO, re.I)
RX_MILIT = re.compile(AMBITO_MILITAR, re.I)

SEPARADORES = ".;:!?"
VENTANA_AMBITO = 320   # caracteres a cada lado para decidir el ambito


def mapa_paginas(texto):
    """Devuelve (offsets, paginas) a partir de los marcadores [p. N]."""
    marcas = [(m.start(), int(m.group(1)))
              for m in re.finditer(r"\[p\.\s*(\d+)\]", texto)]
    return [o for o, _ in marcas], [p for _, p in marcas]


def pagina_de(offset, offsets, paginas):
    i = bisect.bisect_right(offsets, offset) - 1
    return paginas[i] if i >= 0 else None


def frase_en(texto, inicio, fin):
    """Delimita la frase que contiene la coincidencia."""
    izq = max(texto.rfind(c, 0, inicio) for c in SEPARADORES + "\n")
    izq = izq if izq > 0 else inicio - 90
    candidatos = [texto.find(c, fin) for c in SEPARADORES]
    candidatos = [c for c in candidatos if c != -1]
    der = min(candidatos) if candidatos else fin + 90
    return izq, der


def unicos(patron, cadena):
    encontrados = patron.findall(cadena)
    limpio = set()
    for x in encontrados:
        if isinstance(x, tuple):
            x = next((p for p in x if p), "")
        if x:
            limpio.add(x.lower())
    return sorted(limpio)


def clasificar(cita, ventana):
    """Asigna ambito, nivel y postura a un pasaje."""
    cual = unicos(RX_CUAL, cita)
    magn = unicos(RX_MAGN, cita)
    instr = unicos(RX_INSTR, cita)
    gen = unicos(RX_GEN, cita)

    if RX_MILIT.search(ventana) and not RX_SACRO.search(cita):
        ambito = "militar / señalético"
    elif RX_PROF.search(ventana) and not RX_SACRO.search(cita):
        ambito = "profano / cortesano"
    elif RX_SACRO.search(ventana):
        ambito = "sacro / litúrgico"
    else:
        ambito = "(otros)"

    if cual:
        postura = "valoración estética"
    elif magn:
        postura = "ponderación de magnitud"
    else:
        postura = "registro"

    # El sonido militar funciona como senal; el ceremonial, como simbolo.
    if ambito == "militar / señalético":
        nivel = "índice"
    elif cual or gen or ambito in ("sacro / litúrgico", "profano / cortesano"):
        nivel = "símbolo"
    else:
        nivel = "índice"

    return dict(ambito=ambito, nivel=nivel, postura=postura,
                cualificadores=", ".join(cual), magnitud=", ".join(magn),
                instrumentos=", ".join(instr), generos=", ".join(gen),
                escucha_explicita="sí" if RX_ESCUCHA.search(cita) else "")


def extraer(texto):
    offsets, paginas = mapa_paginas(texto)
    vistos, filas = set(), []
    for m in RX_TERMINOS.finditer(texto):
        pg = pagina_de(m.start(), offsets, paginas)
        if pg is None:
            continue
        izq, der = frase_en(texto, m.start(), m.end())
        if (izq, der) in vistos:      # una frase se cuenta una sola vez
            continue
        vistos.add((izq, der))
        cita = re.sub(r"\s+", " ", texto[izq + 1:der + 1]).strip(" .;:,")
        ventana = re.sub(r"\s+", " ",
                         texto[max(0, izq - VENTANA_AMBITO): der + VENTANA_AMBITO])
        fila = dict(pagina=pg, termino=m.group(0).lower(), cita=cita)
        fila.update(clasificar(cita, ventana))
        filas.append(fila)
    filas.sort(key=lambda r: r["pagina"])
    for i, r in enumerate(filas, 1):
        r["id"] = i
    return filas


COLUMNAS = [
    ("id", "id"), ("pagina", "pagina"), ("termino", "termino"),
    ("ambito", "ambito"), ("nivel", "nivel_rostagno"),
    ("postura", "postura_oyente"), ("cualificadores", "cualificadores"),
    ("magnitud", "magnitud"), ("instrumentos", "instrumentos_nombrados"),
    ("generos", "generos_piezas"), ("escucha_explicita", "escucha_explicita"),
    ("cita", "cita"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fuente", help="transcripcion del diario (.md o .txt)")
    ap.add_argument("-o", "--output", default="escucha_codificacion.csv")
    args = ap.parse_args()

    ruta = Path(args.fuente)
    if not ruta.exists():
        sys.exit(f"No existe el fichero: {ruta}")

    texto = re.sub(r"[ \t]+", " ", ruta.read_text(encoding="utf-8", errors="replace"))
    filas = extraer(texto)

    with open(args.output, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([cab for _, cab in COLUMNAS])
        for r in filas:
            w.writerow([r[k] for k, _ in COLUMNAS])

    total = len(filas)
    post = Counter(r["postura"] for r in filas)
    amb = Counter(r["ambito"] for r in filas)
    niv = Counter(r["nivel"] for r in filas)
    con_instr = sum(1 for r in filas if r["instrumentos"])

    print(f"Pasajes musicales: {total}")
    print(f"Paginas distintas: {len(set(r['pagina'] for r in filas))}")
    print("\nPostura del oyente")
    for k, v in post.most_common():
        print(f"  {k:<26} {v:4}  ({100*v/total:.0f}%)")
    print("\nAmbito")
    for k, v in amb.most_common():
        sub = [r for r in filas if r["ambito"] == k]
        ev = sum(1 for r in sub if r["postura"] == "valoración estética")
        print(f"  {k:<26} {v:4}  valoracion: {ev} ({100*ev/v:.0f}%)")
    print("\nNivel (Rostagno)")
    for k, v in niv.most_common():
        print(f"  {k:<26} {v:4}")
    print(f"\nCon instrumentos nombrados: {con_instr} ({100*con_instr/total:.0f}%)")
    print(f"\nEscrito: {args.output}")


if __name__ == "__main__":
    main()
