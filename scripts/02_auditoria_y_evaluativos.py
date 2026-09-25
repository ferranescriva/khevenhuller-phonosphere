#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditoría del léxico + micro-barrido de proximidad evaluativa."""

import csv, json, re
import extraer_referencias as m

# Rutas: ajustar a la ubicacion local del corpus y del lexico.
SRC = "../corpus/alvar_ezquerra_2015.md"
LEX = "../data/lexico_fonosfera.json"
WINDOW = 38   # caracteres a cada lado del término sónico

# cualificadores (formas explícitas; fold aplica acentos/mayúsculas)
CUALITATIVOS = [
    "buen", "buena", "bueno", "buenas", "buenos", "mejor", "mejores",
    "excelente", "excelentes", "admirable", "admirables", "maravillosa",
    "maravilloso", "maravillosas", "maravillosos", "hermosa", "hermoso",
    "hermosas", "hermosos", "lucida", "lucido", "lucidas", "lucidos",
    "solemne", "solemnes", "suntuosa", "suntuoso", "extraordinaria",
    "extraordinario", "singular", "singulares", "diestro", "diestra",
    "diestros", "diestras", "concertada", "concertado", "concertadas",
    "concertados", "dulce", "dulces", "suave", "suaves", "grave", "graves",
    "sonora", "sonoro", "sonoras", "sonoros", "acorde", "entonada", "entonado",
    "devota", "devoto", "devotas", "devotos", "primorosa", "primoroso",
    "exquisita", "exquisito",
    "mala", "malo", "malas", "malos", "destemplada", "destemplado",
    "desconcertada", "desconcertado", "desentonada", "desentonado",
]
MAGNITUD = [
    "mucha", "mucho", "muchas", "muchos", "gran", "grande", "grandes",
    "grandisima", "grandisimo", "infinita", "infinito", "infinitas",
    "infinitos", "innumerable", "innumerables", "sin numero", "poca", "poco",
    "pocas", "pocos",
]

def qpat(words):
    parts = []
    for w in words:
        fw = m.fold(w)
        parts.append(r"\b" + r"\s+".join(re.escape(t) for t in fw.split()) + r"\b")
    return re.compile("|".join(parts))

RX_CUAL = qpat(CUALITATIVOS)
RX_MAGN = qpat(MAGNITUD)

# --- carga corpus + léxico ---------------------------------------------------
lexicon = json.load(open(LEX, encoding="utf-8"))
for cat in lexicon:
    m.CATEGORIAS_ES.setdefault(cat, cat)
matchers = m.build_matchers(lexicon)
pages = m.load_pages(SRC)
raw, page_starts = m.build_corpus(pages)
folded = m.fold(raw)
dates = m.find_dates(folded, raw)

# --- AUDITORÍA: disparos por término ----------------------------------------
audit = []
for cat, term, rx in matchers:
    audit.append((cat, term, len(rx.findall(folded))))
dead = [(c, t) for c, t, n in audit if n == 0]
print("=== AUDITORÍA DE LÉXICO ===")
print(f"Términos totales: {len(audit)} | activos: {sum(1 for *_,n in audit if n)} | "
      f"muertos (0): {len(dead)}")
print("\nMuertos en esta fuente:")
for c, t in dead:
    print(f"  · {t}  ({c})")
print("\nTop 20 términos activos:")
for c, t, n in sorted(audit, key=lambda x: -x[2])[:20]:
    print(f"  {n:4}  {t:<20} ({c})")
with open("../data/auditoria_lexico.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["categoría", "término", "apariciones"])
    for c, t, n in sorted(audit, key=lambda x: -x[2]):
        w.writerow([c, t, n])

# --- BARRIDO EVALUATIVO ------------------------------------------------------
rows = m.extract(folded, raw, matchers, page_starts, dates)
flags = {}
n_cual = n_magn = 0
for r in rows:
    s = r["_off"]; e = s + len(r["detectado"])
    win = folded[max(0, s - WINDOW): e + WINDOW]
    mc = RX_CUAL.search(win); mg = RX_MAGN.search(win)
    if mc:
        flags[r["id"]] = f"⟨cand. evaluativa: {mc.group(0)}⟩"; n_cual += 1
    elif mg:
        flags[r["id"]] = f"⟨cand. magnitud: {mg.group(0)}⟩"; n_magn += 1
with open("../data/flags_evaluativos.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id", "flag"])
    for i, fl in flags.items():
        w.writerow([i, fl])

print("\n=== BARRIDO EVALUATIVO ===")
print(f"Filas: {len(rows)} | cand. evaluativa: {n_cual} | cand. magnitud: {n_magn}")
print("\nMuestra de candidatas evaluativas:")
shown = 0
for r in rows:
    if r["id"] in flags and "evaluativa" in flags[r["id"]]:
        print(f"  [p.{r['pagina']}] {flags[r['id']]:<30} {r['detectado']:<12} :: {r['cita'][:88]}")
        shown += 1
        if shown >= 15:
            break
