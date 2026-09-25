#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06_construir_web.py  ·  Build the bilingual web presentation
============================================================

Genera index.html, la presentacion web bilingue (espanol / ingles) del material
suplementario. Lee data/escucha_codificacion.csv y data/auditoria_lexico.csv,
calcula los recuentos y escribe una pagina HTML con los datos incrustados.

Builds index.html, the bilingual (Spanish / English) web presentation of the
supplementary material. It reads the two CSV files, computes the counts and
writes a single HTML page with the data embedded.

La pagina no depende de ficheros externos ni de conexion, de modo que funciona
igual servida por GitHub Pages que descargada desde Zenodo.

USO / USAGE
-----------
    python3 scripts/06_construir_web.py      (from the repository root)
"""

import csv
import json
import re
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CSV_ESCUCHA = RAIZ / "data" / "escucha_codificacion.csv"
CSV_LEXICO = RAIZ / "data" / "auditoria_lexico.csv"
SALIDA = RAIZ / "index.html"

NORMALIZA_INSTRUMENTO = {
    "chirimia": "chirimía", "menestrile": "menestril", "ministrile": "ministril",
    "sacabuza": "sacabuche", "clarine": "clarín", "clarin": "clarín",
    "atabale": "atabal", "organo": "órgano",
}

# --- Traducciones de los valores codificados / labels for coded values -------
EN_AMBITO = {
    "sacro / litúrgico": "sacred / liturgical",
    "profano / cortesano": "secular / courtly",
    "militar / señalético": "military / signalling",
    "(otros)": "(other)",
}
EN_NIVEL = {"símbolo": "symbol", "índice": "signal"}
EN_POSTURA = {
    "registro": "plain record",
    "ponderación de magnitud": "magnitude",
    "valoración estética": "aesthetic judgement",
}
EN_INSTRUMENTO = {
    "trompeta": "trumpet", "chirimía": "shawm", "menestril": "wind player",
    "ministril": "wind player", "órgano": "organ", "corneta": "cornett",
    "flauta": "flute", "sacabuche": "sackbut", "clarín": "clarion",
    "atabal": "kettledrum",
}


def cargar():
    filas = list(csv.DictReader(CSV_ESCUCHA.open(encoding="utf-8")))
    for f in filas:
        f["pagina"] = int(f["pagina"])
    lexico = list(csv.DictReader(CSV_LEXICO.open(encoding="utf-8")))
    return filas, lexico


def instrumentos(filas):
    c = Counter()
    for f in filas:
        for w in [x.strip() for x in f["instrumentos_nombrados"].split(",") if x.strip()]:
            base = re.sub(r"(es|s)$", "", w)
            c[NORMALIZA_INSTRUMENTO.get(base, base)] += 1
    return c.most_common()


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def barras(items, total, clase_por_etiqueta, traduccion, con_pct=True):
    """Filas de barra horizontal con etiqueta directa y rotulo ingles."""
    out = []
    mayor = max(v for _, v in items) if items else 1
    for etiqueta, valor in items:
        pct = 100 * valor / mayor
        clase = clase_por_etiqueta(etiqueta)
        share = f"{round(100*valor/total)}%"
        en = traduccion.get(etiqueta, etiqueta)
        sufijo = f'<span class="bar-pct">{share}</span>' if con_pct else ""
        rot_es = f"{valor} pasajes ({share})" if con_pct else f"{valor} menciones"
        rot_en = f"{valor} passages ({share})" if con_pct else f"{valor} mentions"
        out.append(
            f'<div class="bar-row">'
            f'<div class="bar-name" data-en="{esc(en)}">{esc(etiqueta)}</div>'
            f'<div class="bar-track"><div class="bar {clase}" style="width:{pct:.1f}%" '
            f'title="{esc(etiqueta)}: {rot_es}" data-en-title="{esc(en)}: {rot_en}"></div></div>'
            f'<div class="bar-val">{valor}{sufijo}</div></div>')
    return "\n".join(out)


def barras_apiladas(items):
    """Ambito: total del ambito con el segmento de valoracion destacado."""
    out = []
    mayor = max(t for _, t, _ in items) if items else 1
    for etiqueta, total, val in items:
        resto = total - val
        w_total = 100 * total / mayor
        en = EN_AMBITO.get(etiqueta, etiqueta)
        out.append(
            f'<div class="bar-row">'
            f'<div class="bar-name" data-en="{esc(en)}">{esc(etiqueta)}</div>'
            f'<div class="bar-track"><div class="stack" style="width:{w_total:.1f}%">'
            f'<div class="bar s-resto" style="flex:{resto}" '
            f'title="{esc(etiqueta)}: {resto} sin valoración" '
            f'data-en-title="{esc(en)}: {resto} without judgement"></div>'
            f'<div class="bar s-val" style="flex:{val}" '
            f'title="{esc(etiqueta)}: {val} con valoración estética" '
            f'data-en-title="{esc(en)}: {val} with aesthetic judgement"></div>'
            f'</div></div>'
            f'<div class="bar-val">{total}'
            f'<span class="bar-pct" data-en="{val} judg.">{val} val.</span></div></div>')
    return "\n".join(out)


def puntos_pagina(filas):
    """Dispersion de los pasajes a lo largo del diario, con la valoracion marcada."""
    p_min = min(f["pagina"] for f in filas)
    p_max = max(f["pagina"] for f in filas)
    span = p_max - p_min
    pos = lambda p: 1 + 98 * (p - p_min) / span
    out = []
    for f in sorted(filas, key=lambda r: r["pagina"]):
        val = f["postura_oyente"] == "valoración estética"
        cls = "dot dot-val" if val else "dot"
        cita = esc(f["cita"][:110])
        post_en = EN_POSTURA.get(f["postura_oyente"], f["postura_oyente"])
        out.append(
            f'<span class="{cls}" style="left:{pos(f["pagina"]):.2f}%" '
            f'title="p. {f["pagina"]} · {esc(f["postura_oyente"])} · {cita}…" '
            f'data-en-title="p. {f["pagina"]} · {esc(post_en)} · {cita}…"></span>')
    x0, x1 = pos(53), pos(62)
    banda = (f'<span class="band" style="left:{x0:.2f}%;width:{max(x1-x0,1.4):.2f}%" '
             f'title="Coronación de Praga, pp. 53-62" '
             f'data-en-title="Prague coronation, pp. 53-62"></span>')
    return banda + "\n" + "\n".join(out), p_min, p_max


def construir():
    filas, lexico = cargar()
    total = len(filas)

    postura = Counter(f["postura_oyente"] for f in filas)
    orden_post = ["registro", "ponderación de magnitud", "valoración estética"]
    items_post = [(k, postura[k]) for k in orden_post if k in postura]

    ambitos = Counter(f["ambito"] for f in filas)
    items_amb = []
    for a, n in ambitos.most_common():
        v = sum(1 for f in filas
                if f["ambito"] == a and f["postura_oyente"] == "valoración estética")
        items_amb.append((a, n, v))

    nivel = Counter(f["nivel_rostagno"] for f in filas)
    items_niv = [(k, nivel[k]) for k in ["símbolo", "índice"] if k in nivel]

    instr = instrumentos(filas)
    con_instr = sum(1 for f in filas if f["instrumentos_nombrados"])
    paginas = len(set(f["pagina"] for f in filas))
    n_val = postura.get("valoración estética", 0)

    activos = sum(1 for t in lexico if int(t["apariciones"]) > 0)
    muertos = sum(1 for t in lexico if int(t["apariciones"]) == 0)

    clase_post = lambda e: {"registro": "s-neutro",
                            "ponderación de magnitud": "s-indigo",
                            "valoración estética": "s-val"}.get(e, "s-indigo")
    clase_niv = lambda e: "s-indigo" if e == "símbolo" else "s-neutro"

    dispersion, p_min, p_max = puntos_pagina(filas)

    datos = [{"id": int(f["id"]), "p": f["pagina"], "t": f["termino"],
              "a": f["ambito"], "ae": EN_AMBITO.get(f["ambito"], f["ambito"]),
              "n": f["nivel_rostagno"], "ne": EN_NIVEL.get(f["nivel_rostagno"], f["nivel_rostagno"]),
              "o": f["postura_oyente"], "oe": EN_POSTURA.get(f["postura_oyente"], f["postura_oyente"]),
              "c": f["cualificadores"], "i": f["instrumentos_nombrados"],
              "cita": f["cita"]} for f in filas]

    html = PLANTILLA
    for k, v in {
        "{{TOTAL}}": str(total),
        "{{PAGINAS}}": str(paginas),
        "{{NVAL}}": str(n_val),
        "{{CONINSTR}}": str(con_instr),
        "{{PCTINSTR}}": str(round(100 * con_instr / total)),
        "{{PCTVAL}}": str(round(100 * n_val / total)),
        "{{LEXTOTAL}}": str(len(lexico)),
        "{{LEXACTIVOS}}": str(activos),
        "{{LEXMUERTOS}}": str(muertos),
        "{{BARRAS_POSTURA}}": barras(items_post, total, clase_post, EN_POSTURA),
        "{{BARRAS_AMBITO}}": barras_apiladas(items_amb),
        "{{BARRAS_NIVEL}}": barras(items_niv, total, clase_niv, EN_NIVEL),
        "{{BARRAS_INSTR}}": barras(instr, sum(v for _, v in instr),
                                   lambda e: "s-indigo", EN_INSTRUMENTO, con_pct=False),
        "{{DISPERSION}}": dispersion,
        "{{PMIN}}": str(p_min),
        "{{PMAX}}": str(p_max),
        "{{DATOS}}": json.dumps(datos, ensure_ascii=False, separators=(",", ":")),
    }.items():
        html = html.replace(k, v)

    SALIDA.write_text(html, encoding="utf-8")
    print(f"Escrito / written: {SALIDA}  ({len(html)//1024} KB)")
    print(f"  {total} pasajes · {paginas} páginas · {n_val} valoraciones "
          f"· {con_instr} con instrumentos")


PLANTILLA = r"""<title>Fonosfera Khevenhüller</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  color-scheme: light;
  --paper:#f5f6f9; --surface:#ffffff; --surface-2:#eef0f5;
  --ink:#14182a; --ink-2:#4c5268; --ink-3:#7c8296;
  --rule:#dfe3ea; --rule-2:#eaedf3;
  --indigo:#2f3fb0; --indigo-soft:#e8eaf7;
  --brass:#a87209; --brass-soft:#f6eeda;
  --neutro:#8a8fa3;
  --serif:"Spectral",Georgia,"Times New Roman",serif;
  --sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,"SFMono-Regular",Menlo,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme: dark;
    --paper:#0e1120; --surface:#171b2b; --surface-2:#1e2334;
    --ink:#e9ebf3; --ink-2:#a6acc2; --ink-3:#787e94;
    --rule:#272c3e; --rule-2:#20253550;
    --indigo:#7581d0; --indigo-soft:#232a4a;
    --brass:#ba8a22; --brass-soft:#332a14;
    --neutro:#5b6072;
  }
}
:root[data-theme="dark"]{
  color-scheme: dark;
  --paper:#0e1120; --surface:#171b2b; --surface-2:#1e2334;
  --ink:#e9ebf3; --ink-2:#a6acc2; --ink-3:#787e94;
  --rule:#272c3e; --rule-2:#20253550;
  --indigo:#7581d0; --indigo-soft:#232a4a;
  --brass:#ba8a22; --brass-soft:#332a14;
  --neutro:#5b6072;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font-family:var(--sans); font-size:16px; line-height:1.6;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1080px; margin:0 auto; padding-inline:20px; padding-block:0}
.prose{max-width:66ch}
h1,h2,h3{font-family:var(--serif); font-weight:600; text-wrap:balance; margin:0}
h1{font-size:clamp(2rem,5vw,3.1rem); line-height:1.08; letter-spacing:-.015em}
h2{font-size:clamp(1.35rem,2.6vw,1.75rem); line-height:1.2; margin-bottom:.5rem}
h3{font-size:1.05rem; line-height:1.3}
p{margin:0 0 1rem}
a{color:var(--indigo)}
.eyebrow{
  font-family:var(--mono); font-size:.72rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink-3); margin:0 0 1rem
}

/* ---------- selector de idioma ---------- */
.langbar{display:flex; justify-content:flex-end; padding-top:1rem}
.lang{display:inline-flex; border:1px solid var(--rule); border-radius:3px; overflow:hidden}
.lang button{
  font-family:var(--mono); font-size:.74rem; letter-spacing:.08em; text-transform:uppercase;
  background:var(--surface); color:var(--ink-3); border:0; padding:.4rem .75rem; cursor:pointer;
}
.lang button + button{border-left:1px solid var(--rule)}
.lang button[aria-pressed="true"]{background:var(--indigo); color:#fff}
.lang button:focus-visible{outline:2px solid var(--indigo); outline-offset:-2px}

/* ---------- cabecera ---------- */
header{
  border-bottom:1px solid var(--rule); background:var(--surface);
  padding-bottom:clamp(2rem,4vw,2.75rem)
}
header h1{margin-top:.25rem}
.head-main{padding-top:clamp(1.5rem,4vw,2.5rem)}
.deck{
  font-family:var(--serif); font-size:clamp(1.05rem,2vw,1.3rem);
  line-height:1.5; color:var(--ink-2); max-width:56ch; margin:1.25rem 0 0
}
.byline{
  display:flex; flex-wrap:wrap; gap:.45rem 1.25rem; margin-top:1.75rem;
  font-size:.85rem; color:var(--ink-3); font-family:var(--mono)
}
.byline strong{color:var(--ink-2); font-weight:500}

/* ---------- secciones ---------- */
section{padding-block:clamp(2.25rem,5vw,3.5rem); border-bottom:1px solid var(--rule)}
.lede{color:var(--ink-2); margin-bottom:1.75rem}

/* ---------- cifras ---------- */
.stats{display:grid; grid-template-columns:repeat(auto-fit,minmax(min(160px,100%),1fr)); gap:1px;
  background:var(--rule); border:1px solid var(--rule); border-radius:3px; overflow:hidden}
.stat{background:var(--surface); padding:1.25rem 1.1rem}
.stat .n{font-family:var(--mono); font-size:2.1rem; font-weight:500; line-height:1;
  letter-spacing:-.02em; font-variant-numeric:tabular-nums}
.stat .n.brass{color:var(--brass)}
.stat .k{font-size:.82rem; color:var(--ink-3); margin-top:.45rem; line-height:1.35}

/* ---------- corpus ---------- */
.cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr)); gap:1rem}
.card{background:var(--surface); border:1px solid var(--rule); border-radius:3px; padding:1.25rem}
.card .tag{font-family:var(--mono); font-size:.7rem; letter-spacing:.1em; text-transform:uppercase;
  color:var(--indigo); margin-bottom:.6rem}
.card cite{font-style:italic; font-family:var(--serif)}
.card p{font-size:.9rem; color:var(--ink-2); margin:.7rem 0 0}

/* ---------- pasos ---------- */
ol.steps{list-style:none; counter-reset:s; margin:0; padding:0;
  display:grid; gap:1px; background:var(--rule); border:1px solid var(--rule); border-radius:3px}
ol.steps li{counter-increment:s; background:var(--surface); padding:1.1rem 1.25rem 1.1rem 3.4rem; position:relative}
ol.steps li::before{
  content:counter(s,decimal-leading-zero); position:absolute; left:1.25rem; top:1.15rem;
  font-family:var(--mono); font-size:.78rem; color:var(--indigo); letter-spacing:.04em
}
ol.steps b{font-weight:600}
ol.steps span{display:block; color:var(--ink-2); font-size:.9rem; margin-top:.2rem}
ol.steps code{font-family:var(--mono); font-size:.78rem; color:var(--ink-3)}

/* ---------- figuras ---------- */
.figs{display:grid; grid-template-columns:repeat(auto-fit,minmax(min(420px,100%),1fr)); gap:1.5rem}
figure{margin:0; background:var(--surface); border:1px solid var(--rule); border-radius:3px; padding:1.25rem}
figcaption{font-size:.82rem; color:var(--ink-3); margin-top:1rem; line-height:1.45}
.figtitle{font-family:var(--serif); font-size:1.02rem; font-weight:600; margin-bottom:1.1rem}
.bar-row{display:grid; grid-template-columns:minmax(0,9rem) minmax(0,1fr) auto; align-items:center;
  gap:.7rem; margin-bottom:.7rem}
.bar-name{font-size:.82rem; color:var(--ink-2); line-height:1.25; min-width:0; overflow-wrap:anywhere}
.bar-track{height:14px; background:var(--surface-2); border-radius:3px; overflow:hidden}
.bar{height:14px; border-radius:0 4px 4px 0; min-width:2px}
.stack{display:flex; height:14px; gap:2px}
.stack .bar{border-radius:0}
.stack .bar:last-child{border-radius:0 4px 4px 0}
.s-indigo{background:var(--indigo)}
.s-neutro{background:var(--neutro)}
.s-val{background:var(--brass)}
.s-resto{background:var(--neutro)}
.bar-val{font-family:var(--mono); font-size:.85rem; font-variant-numeric:tabular-nums;
  text-align:right; white-space:nowrap; line-height:1.15}
.bar-pct{display:block; font-size:.68rem; color:var(--ink-3)}
.legend{display:flex; flex-wrap:wrap; gap:.4rem 1rem; margin-top:.9rem; font-size:.76rem; color:var(--ink-2)}
.legend i{width:10px; height:10px; border-radius:2px; display:inline-block; margin-right:.35rem;
  vertical-align:-1px}

/* ---------- dispersión ---------- */
.strip{position:relative; height:66px; margin:.4rem 0 .2rem;
  border-bottom:1px solid var(--rule); background:
  linear-gradient(var(--rule-2),var(--rule-2)) 0 22px/100% 1px no-repeat}
.dot{position:absolute; top:16px; width:7px; height:7px; margin-left:-3.5px; border-radius:50%;
  background:var(--neutro); border:2px solid var(--surface)}
.dot-val{top:8px; width:11px; height:11px; margin-left:-5.5px; background:var(--brass); z-index:2}
.band{position:absolute; top:3px; height:24px; background:var(--indigo-soft); border-radius:2px; z-index:0}
.axis{display:flex; justify-content:space-between; font-family:var(--mono); font-size:.7rem;
  color:var(--ink-3)}

/* ---------- glosario ---------- */
.gloss{display:grid; gap:1px; background:var(--rule); border:1px solid var(--rule); border-radius:3px}
.gloss > div{background:var(--surface); padding:1.1rem 1.25rem}
.gloss dt{font-family:var(--mono); font-size:.74rem; letter-spacing:.1em; text-transform:uppercase;
  color:var(--brass); margin-bottom:.45rem}
.gloss q{font-family:var(--serif); font-style:italic; color:var(--ink)}
.gloss .note{font-size:.86rem; color:var(--ink-2); margin-top:.5rem; display:block}

/* ---------- tabla ---------- */
.controls{display:flex; flex-wrap:wrap; gap:.6rem; margin-bottom:1rem; align-items:center}
.controls select,.controls input{
  font-family:var(--sans); font-size:.85rem; color:var(--ink); background:var(--surface);
  border:1px solid var(--rule); border-radius:3px; padding:.45rem .6rem
}
.controls input{flex:1; min-width:180px}
.controls select:focus-visible,.controls input:focus-visible{outline:2px solid var(--indigo); outline-offset:1px}
.count{font-family:var(--mono); font-size:.78rem; color:var(--ink-3); margin-left:auto}
.tablebox{overflow-x:auto; border:1px solid var(--rule); border-radius:3px; background:var(--surface)}
table{border-collapse:collapse; width:100%; min-width:720px; font-size:.86rem}
th{
  text-align:left; font-family:var(--mono); font-size:.68rem; letter-spacing:.09em;
  text-transform:uppercase; color:var(--ink-3); font-weight:400;
  padding:.7rem .8rem; border-bottom:1px solid var(--rule); white-space:nowrap
}
td{padding:.7rem .8rem; border-bottom:1px solid var(--rule-2); vertical-align:top}
tr:last-child td{border-bottom:none}
td.pg{font-family:var(--mono); color:var(--ink-3); white-space:nowrap; font-variant-numeric:tabular-nums}
td.cita{font-family:var(--serif); line-height:1.45; min-width:280px}
td.cita em{font-style:normal; background:var(--brass-soft); color:var(--ink);
  padding:0 .15em; border-radius:2px}
.pill{display:inline-block; font-size:.7rem; font-family:var(--mono); padding:.12rem .4rem;
  border-radius:2px; white-space:nowrap; border:1px solid transparent}
.p-val{background:var(--brass-soft); color:var(--brass); border-color:var(--brass)}
.p-ind{background:var(--surface-2); color:var(--ink-2)}
.p-sim{background:var(--indigo-soft); color:var(--indigo)}
.empty{padding:2rem; text-align:center; color:var(--ink-3); font-size:.9rem}

/* ---------- ficheros ---------- */
.files{display:grid; gap:1px; background:var(--rule); border:1px solid var(--rule); border-radius:3px}
.file{background:var(--surface); padding:.9rem 1.15rem; display:grid;
  grid-template-columns:minmax(200px,auto) 1fr; gap:.3rem 1.25rem; align-items:baseline}
.file code{font-family:var(--mono); font-size:.82rem; color:var(--indigo)}
.file span{font-size:.86rem; color:var(--ink-2)}

footer{padding-block:2.5rem 3.5rem; color:var(--ink-3); font-size:.85rem}
footer p{max-width:70ch}
@media (max-width:600px){
  .file{grid-template-columns:1fr}
  .bar-row{grid-template-columns:minmax(0,1fr) auto;
    grid-template-areas:"name name" "track val"; gap:.35rem .6rem; margin-bottom:.9rem}
  .bar-name{grid-area:name}
  .bar-track{grid-area:track}
  .bar-val{grid-area:val; display:flex; align-items:baseline; gap:.35rem}
  .bar-pct{display:inline}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important; animation:none!important}}
</style>

<header>
  <div class="wrap">
    <div class="langbar">
      <div class="lang" role="group" aria-label="Idioma / Language">
        <button type="button" id="btn-es" aria-pressed="true">Español</button>
        <button type="button" id="btn-en" aria-pressed="false">English</button>
      </div>
    </div>
    <div class="head-main">
      <p class="eyebrow" data-en="Supplementary material">Material suplementario</p>
      <h1 data-en="An ambassador&#39;s listening">La escucha de un embajador</h1>
      <p class="deck" data-en="{{TOTAL}} musical passages from the writings of Hans Khevenhüller (1538-1606), extracted and coded through Antonio Rostagno&#39;s historical phonosphere.">{{TOTAL}} pasajes musicales de los escritos de Hans Khevenhüller
        (1538-1606), extraídos y codificados según la fonosfera histórica de Antonio Rostagno.</p>
      <div class="byline">
        <span><strong>Ferran Escrivà-Llorca</strong></span>
        <span>Universitat de València</span>
        <span>ORCID 0000-0002-5959-2595</span>
        <span>2026</span>
      </div>
    </div>
  </div>
</header>

<section>
  <div class="wrap">
    <div class="stats">
      <div class="stat"><div class="n">{{TOTAL}}</div>
        <div class="k" data-en="passages with musical vocabulary">pasajes con vocabulario musical</div></div>
      <div class="stat"><div class="n">{{PAGINAS}}</div>
        <div class="k" data-en="pages of the diary involved">páginas del diario implicadas</div></div>
      <div class="stat"><div class="n brass">{{NVAL}}</div>
        <div class="k" data-en="carry an aesthetic judgement, {{PCTVAL}} % of the total">con valoración estética, el {{PCTVAL}} % del total</div></div>
      <div class="stat"><div class="n">{{CONINSTR}}</div>
        <div class="k" data-en="name specific instruments, {{PCTINSTR}} %">nombran instrumentos concretos, el {{PCTINSTR}} %</div></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2 data-en="The corpus">El corpus</h2>
    <p class="lede prose" data-en="Two Spanish editions share the testimony. Both translate the German original and are therefore not always literal, but both are taken as valid. What separates them is not their validity but the kind of material each one supplies.">Dos ediciones en castellano se reparten el testimonio. Ambas traducen
      el original alemán y por ello no siempre son literales, pero las dos se consideran válidas.
      Lo que se distingue no es su validez, sino la clase de material que aporta cada una.</p>
    <div class="cards">
      <div class="card">
        <div class="tag" data-en="Edition A · the diary">Edición A · el diario</div>
        <cite>Diario de Hans Khevenhüller: embajador imperial en la corte de Felipe II</cite>,
        ed. Sara Veronelli <span data-en="and">y</span> Félix Labrador Arroyo (Madrid, 2001).
        <p data-en="Continuous text in period Spanish. The source for musical activity as lived: listening, attendance and judgement. The passages coded here come from this edition.">Texto seguido en castellano de época. Fuente de la actividad musical vivida: la escucha,
          la asistencia y la valoración. Los pasajes codificados aquí proceden de esta edición.</p>
      </div>
      <div class="card">
        <div class="tag" data-en="Edition B · the documents">Edición B · la documentación</div>
        <cite>El embajador imperial. Hans Khevenhüller (1538-1606) en España</cite>,
        ed. Alfredo Alvar Ezquerra (Madrid, 2015).
        <p data-en="A critical edition arranging the diary by year alongside letters and documents. It supplies the inventory, the auction and the customs licences, the basis for the evidence on material culture.">Edición crítica que ordena por año el diario junto con cartas y documentos. Aporta el
          inventario, la almoneda y las cédulas de paso, base de la evidencia sobre cultura material.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2 data-en="The procedure">El procedimiento</h2>
    <p class="lede prose" data-en="Six steps, one per script. The full pipeline is in the repository&#39;s scripts/ folder, and steps 4 and 6 need only the Python standard library.">Seis pasos, uno por script. El pipeline completo está en la carpeta
      <code>scripts/</code> del repositorio y los pasos 4 y 6 solo requieren biblioteca estándar.</p>
    <ol class="steps">
      <li><b data-en="Lexical extraction over the corpus">Extracción léxica sobre el corpus</b>
        <span data-en="Rebuilds the printed pagination, detects the dated entries and locates the terms of the lexicon. Matching ignores accents and case, tolerates plurals and OCR line breaks, and preserves the original spelling in the quotation.">Reconstruye la paginación impresa, detecta las entradas datadas y localiza los términos
          del léxico. El emparejamiento ignora acentos y mayúsculas, tolera plurales y saltos de línea
          del OCR, y conserva la grafía original en la cita.</span>
        <code>01_extraer_referencias.py</code></li>
      <li><b data-en="Audit of the instrument">Auditoría del instrumento</b>
        <span data-en="Counts the occurrences of each term and flags passages with a qualifier nearby. The audit keeps the terms with zero occurrences, because recording what was searched for and not found is part of the result.">Cuenta las apariciones de cada término y marca los pasajes con un cualificador en su
          entorno inmediato. La auditoría conserva los términos con cero apariciones, porque documentar
          qué se buscó y no aparece forma parte del resultado.</span>
        <code>02_auditoria_y_evaluativos.py</code></li>
      <li><b data-en="Extraction of the funerary material">Extracción del material funerario</b>
        <span data-en="Locates exequies, honours and burials, assigns the probable deceased by name proximity and labels each passage as the diary&#39;s voice or the editor&#39;s apparatus.">Localiza exequias, honras y entierros, asigna el difunto probable por proximidad de
          nombres y etiqueta cada pasaje como voz del diario o aparato del editor.</span>
        <code>03_analisis_exequias.py</code></li>
      <li><b data-en="Phonospheric coding">Codificación fonosférica</b>
        <span data-en="The central step. It codes each musical passage by domain, Rostagno level and listener&#39;s stance, and extracts the qualifiers, instruments and genres named.">El paso central. Codifica cada pasaje musical según ámbito, nivel de Rostagno y postura
          del oyente, y extrae los cualificadores, los instrumentos y los géneros nombrados.</span>
        <code>04_capa_escucha.py</code></li>
      <li><b data-en="Coding workbook for review">Libro de codificación para revisión</b>
        <span data-en="Generates a spreadsheet with validated dropdown lists, meant for reviewing by hand what the machine proposed.">Genera una hoja de cálculo con listas desplegables validadas, pensada para revisar a mano
          lo que la máquina propuso.</span>
        <code>05_libro_codificacion.py</code></li>
      <li><b data-en="Web presentation">Presentación web</b>
        <span data-en="Reads the CSV files, computes the counts and writes this page with the data embedded, so that it works the same on GitHub Pages and downloaded from Zenodo.">Lee los CSV, calcula los recuentos y escribe esta página con los datos incrustados, de modo
          que funciona igual en GitHub Pages que descargada desde Zenodo.</span>
        <code>06_construir_web.py</code></li>
    </ol>
  </div>
</section>

<section>
  <div class="wrap">
    <h2 data-en="What was searched for">Qué se buscó</h2>
    <p class="lede prose" data-en="The lexical instrument gathers {{LEXTOTAL}} terms across four fields: music, sound and noise, voice and rumour, and musical metaphor. Of these, {{LEXACTIVOS}} occur in the corpus and {{LEXMUERTOS}} do not. The absences are informative: not a single cannon shot, musket, rocket, cheer or uproar is recorded, nor «murmullo» or «murmurar».">El instrumento léxico reúne {{LEXTOTAL}} términos repartidos en cuatro campos:
      música, sonido y ruido, voz y rumor, y metáfora musical. De ellos {{LEXACTIVOS}} aparecen en el
      corpus y {{LEXMUERTOS}} no. Las ausencias son informativas: no se documenta ni un solo cañonazo,
      mosquete, cohete, vítor ni algazara, y tampoco «murmullo» ni «murmurar».</p>
    <h3 style="margin-bottom:1rem" data-en="Anchored in the lexicography of the period">Anclaje en la lexicografía de la época</h3>
    <div class="gloss">
      <div>
        <dt>Murmullo</dt>
        <q>El ruido manso que haze el agua corriente, a murmure, por la figura onomatopeya. Y de allí
        murmurar, que es dezir mal de alguno, medio entre dientes.</q>
        <span class="note" data-en="Sound resides here, not in «rumor». Covarrubias himself traces the move from physical noise to sub-audible speech.">El sonido reside aquí, no en «rumor». Covarrubias traza él mismo el paso del
        ruido físico al habla sub-audible.</span>
      </div>
      <div>
        <dt>Rumor</dt>
        <q>Lo que se dize, no en público, pero se esparce secretamente en el Pueblo.</q>
        <span class="note" data-en="By 1611 the word is already informational and has no acoustic component.">En 1611 la voz es ya informativa y carece de componente acústico.</span>
      </div>
      <div>
        <dt>Salva</dt>
        <q>Hazen salva los soldados a su Rey… disparando la arcabuzería por alto, y sin pelotas… en
        demostración de reconocimiento, paz, amistad.</q>
        <span class="note" data-en="Only this sense is phonospheric. The silver salver and the tasting of dishes share the root but not the sound. In this corpus the sounding salvo appears just once.">Solo este sentido es fonosférico. La salvilla de plata y la prueba de manjares
        comparten raíz pero no sonido. En este corpus la salva sonora aparece una sola vez.</span>
      </div>
    </div>
    <p style="font-size:.82rem; color:var(--ink-3); margin-top:1rem">Sebastián de Covarrubias,
      <cite>Tesoro de la lengua castellana o española</cite> (Madrid: Luis Sánchez, 1611).
      <span data-en="Normalised transcription.">Transcripción normalizada.</span></p>
  </div>
</section>

<section>
  <div class="wrap">
    <h2 data-en="Results">Resultados</h2>
    <p class="lede prose" data-en="The coding is automatic and therefore open to revision. The figures are indicative rather than statistical, given how uneven the subsamples are.">La codificación es automática y por tanto revisable. Las cifras tienen valor
      indicativo y no estadístico, dada la desigualdad de las submuestras.</p>
    <div class="figs">

      <figure>
        <div class="figtitle" data-en="Listener&#39;s stance">Postura del oyente</div>
        {{BARRAS_POSTURA}}
        <div class="legend">
          <span><i style="background:var(--neutro)"></i><span data-en="plain record of the event">registro del hecho</span></span>
          <span><i style="background:var(--indigo)"></i><span data-en="weighing of magnitude">ponderación de magnitud</span></span>
          <span><i style="background:var(--brass)"></i><span data-en="aesthetic judgement">valoración estética</span></span>
        </div>
        <figcaption data-en="The ambassador records far more than he judges. Aesthetic judgement, which is what documents expert listening, appears in slightly under a sixth of the passages.">El embajador consigna mucho más de lo que juzga. La valoración estética, que es la
          que documenta la escucha experta, aparece en algo menos de una sexta parte de los pasajes.</figcaption>
      </figure>

      <figure>
        <div class="figtitle" data-en="Domain of the sound">Ámbito del sonido</div>
        {{BARRAS_AMBITO}}
        <div class="legend">
          <span><i style="background:var(--neutro)"></i><span data-en="without judgement">sin valoración</span></span>
          <span><i style="background:var(--brass)"></i><span data-en="with aesthetic judgement">con valoración estética</span></span>
        </div>
        <figcaption data-en="The share of judgement is similar across domains, on very uneven subsamples that call for caution. The sacred dominates the absolute count.">La proporción de valoración es semejante en los distintos ámbitos, con submuestras
          muy desiguales que aconsejan prudencia. Lo sacro domina el recuento absoluto.</figcaption>
      </figure>

      <figure>
        <div class="figtitle" data-en="Level in Rostagno&#39;s triad">Nivel en la retícula de Rostagno</div>
        {{BARRAS_NIVEL}}
        <div class="legend">
          <span><i style="background:var(--indigo)"></i><span data-en="symbol, with communicative intent">símbolo, con intención comunicativa</span></span>
          <span><i style="background:var(--neutro)"></i><span data-en="signal, which orders or warns">índice, señal que ordena o avisa</span></span>
        </div>
        <figcaption data-en="The same instrument shifts level with the context. The trumpet that commands in the field and the one that signifies in church are recorded differently.">El mismo instrumento cambia de nivel según el contexto. La trompeta que manda en el
          campo militar y la que significa en la iglesia se consignan de manera distinta.</figcaption>
      </figure>

      <figure>
        <div class="figtitle" data-en="Instruments named">Instrumentos nombrados</div>
        {{BARRAS_INSTR}}
        <figcaption data-en="Organological precision is the firmest finding, because it does not depend on adjectives. Almost half the passages name specific instruments, and the witness has the technical vocabulary to tell them apart.">La precisión organológica es el dato más firme, porque no depende de la adjetivación.
          Casi la mitad de los pasajes nombra instrumentos concretos y el testigo dispone del léxico
          técnico para distinguirlos.</figcaption>
      </figure>

    </div>

    <figure style="margin-top:1.5rem">
      <div class="figtitle" data-en="Where expert listening clusters">Dónde se concentra la escucha experta</div>
      <div class="strip">{{DISPERSION}}</div>
      <div class="axis"><span>p. {{PMIN}}</span><span>p. {{PMAX}}</span></div>
      <div class="legend">
        <span><i style="background:var(--neutro)"></i><span data-en="musical passage">pasaje musical</span></span>
        <span><i style="background:var(--brass)"></i><span data-en="with aesthetic judgement">con valoración estética</span></span>
        <span><i style="background:var(--indigo-soft); border:1px solid var(--indigo)"></i><span data-en="Prague coronation, pp. 53-62">coronación de Praga, pp. 53-62</span></span>
      </div>
      <figcaption data-en="Five of the {{NVAL}} judgements belong to the account of the coronation of Maximilian II and Maria as sovereigns of Bohemia, in September 1562. Expert listening is not spread evenly across the diary; it switches on before the extraordinary ceremonial event.">Cinco de las {{NVAL}} valoraciones corresponden al relato de la coronación de
        Maximiliano II y María como reyes de Bohemia, en septiembre de 1562. La escucha experta no se
        reparte de manera uniforme a lo largo del diario, sino que se activa ante el acontecimiento
        ceremonial extraordinario.</figcaption>
    </figure>
  </div>
</section>

<section>
  <div class="wrap">
    <h2 data-en="The passages">Los pasajes</h2>
    <p class="lede prose" data-en="The full coding table. Aesthetic qualifiers are highlighted inside the quotation. Quotations are given in the original Spanish of the edition.">Tabla completa de la codificación. Los cualificadores estéticos aparecen
      resaltados dentro de la cita.</p>
    <div class="controls">
      <select id="f-ambito" aria-label="Ámbito"></select>
      <select id="f-nivel" aria-label="Nivel"></select>
      <select id="f-postura" aria-label="Postura"></select>
      <input id="f-texto" type="search" placeholder="Buscar en las citas…" data-en-placeholder="Search the quotations…" aria-label="Buscar">
      <span class="count" id="conteo"></span>
    </div>
    <div class="tablebox">
      <table>
        <thead><tr>
          <th data-en="Page">Pág.</th>
          <th data-en="Term">Término</th>
          <th data-en="Domain">Ámbito</th>
          <th data-en="Level">Nivel</th>
          <th data-en="Stance">Postura</th>
          <th data-en="Instruments">Instrumentos</th>
          <th data-en="Quotation">Cita</th>
        </tr></thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
    <div class="empty" id="vacio" hidden data-en="No passage matches those filters.">Ningún pasaje coincide con esos filtros.</div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2 data-en="Files">Ficheros</h2>
    <div class="files">
      <div class="file"><code>data/escucha_codificacion.csv</code><span data-en="The {{TOTAL}} coded musical passages. The central table.">Los {{TOTAL}} pasajes musicales codificados. Tabla central.</span></div>
      <div class="file"><code>data/exequias_pasajes.csv</code><span data-en="621 passages on exequies, honours and burials, with the diary&#39;s voice kept apart from the editor&#39;s apparatus.">621 pasajes sobre exequias, honras y entierros, con la voz del diario distinguida del aparato del editor.</span></div>
      <div class="file"><code>data/referencias_fonosfera.csv</code><span data-en="577 references from the broad sweep, prepared for manual review.">577 referencias del cribado amplio, preparadas para revisión manual.</span></div>
      <div class="file"><code>data/auditoria_lexico.csv</code><span data-en="Occurrences of each of the {{LEXTOTAL}} terms in the instrument.">Apariciones de cada uno de los {{LEXTOTAL}} términos del instrumento.</span></div>
      <div class="file"><code>data/lexico_fonosfera.json</code><span data-en="The full lexicon, editable, feeding scripts 1 and 2.">El léxico completo, editable, que alimenta los scripts 1 y 2.</span></div>
      <div class="file"><code>scripts/</code><span data-en="The six programs of the pipeline, including the one that builds this page.">Los seis programas del pipeline, incluido el que genera esta página.</span></div>
      <div class="file"><code>README.md</code><span data-en="Full methodology, data dictionary and limits of the exercise.">Metodología completa, diccionario de datos y límites del ejercicio.</span></div>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <p><strong data-en="Citation.">Cita.</strong> Escrivà-Llorca, Ferran. <cite>Fonosfera de un embajador imperial: datos y
      código</cite>. <span data-en="Supplementary material, 2026. DOI pending.">Material suplementario, 2026. DOI pendiente de asignación.</span></p>
    <p><strong data-en="Licence.">Licencia.</strong> <span data-en="Data under CC BY 4.0 and code under the MIT licence. Quotations from the diary come from editions under copyright and are reproduced at the brief length proper to scholarly commentary. The source texts are not distributed here.">Datos bajo CC BY 4.0 y código bajo licencia MIT. Las citas del diario
      proceden de ediciones con derechos de autor y se reproducen en la extensión breve propia del
      comentario académico. Los textos fuente no se distribuyen aquí.</span></p>
  </div>
</footer>

<script>
const DATOS = {{DATOS}};
const $ = s => document.querySelector(s);
const tbody = $("#tbody"), vacio = $("#vacio"), conteo = $("#conteo");
let LANG = "es";

const UI = {
  es: {todosAmbitos:"Todos los ámbitos", todosNiveles:"Todos los niveles",
       todasPosturas:"Todas las posturas", de:"de", pasajes:"pasajes", titulo:"Fonosfera Khevenhüller"},
  en: {todosAmbitos:"All domains", todosNiveles:"All levels",
       todasPosturas:"All stances", de:"of", pasajes:"passages", titulo:"Khevenhüller Phonosphere"}
};

const esc = s => String(s).replace(/[&<>"]/g, c =>
  ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]));

/* ---- filtros ---- */
function llenarSelect(sel, campoEs, campoEn, textoTodos){
  const prev = sel.value;
  sel.innerHTML = "";
  const o0 = document.createElement("option");
  o0.value = ""; o0.textContent = textoTodos;
  sel.appendChild(o0);
  const vistos = new Set();
  for (const d of DATOS){
    if (vistos.has(d[campoEs])) continue;
    vistos.add(d[campoEs]);
    const o = document.createElement("option");
    o.value = d[campoEs];
    o.textContent = LANG === "es" ? d[campoEs] : d[campoEn];
    sel.appendChild(o);
  }
  sel.value = prev;
}
function construirFiltros(){
  llenarSelect($("#f-ambito"), "a", "ae", UI[LANG].todosAmbitos);
  llenarSelect($("#f-nivel"), "n", "ne", UI[LANG].todosNiveles);
  llenarSelect($("#f-postura"), "o", "oe", UI[LANG].todasPosturas);
}

function resaltar(cita, cual){
  let out = esc(cita);
  if (!cual) return out;
  for (const t of cual.split(",").map(x => x.trim()).filter(Boolean)){
    const re = new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "gi");
    out = out.replace(re, "<em>$1</em>");
  }
  return out;
}
function pill(txtEs, txtMostrar, tipo){
  const cls = tipo === "postura" && txtEs.startsWith("valoración") ? "p-val"
            : tipo === "nivel" && txtEs === "símbolo" ? "p-sim" : "p-ind";
  return '<span class="pill ' + cls + '">' + esc(txtMostrar) + "</span>";
}

function pintar(){
  const fa = $("#f-ambito").value, fn = $("#f-nivel").value,
        fo = $("#f-postura").value, ft = $("#f-texto").value.trim().toLowerCase();
  const filas = DATOS.filter(d =>
    (!fa || d.a === fa) && (!fn || d.n === fn) && (!fo || d.o === fo) &&
    (!ft || (d.cita + " " + d.t + " " + d.i).toLowerCase().includes(ft)));

  tbody.innerHTML = filas.map(d =>
    "<tr>" +
    '<td class="pg">' + d.p + "</td>" +
    "<td>" + esc(d.t) + "</td>" +
    "<td>" + esc(LANG === "es" ? d.a : d.ae) + "</td>" +
    "<td>" + pill(d.n, LANG === "es" ? d.n : d.ne, "nivel") + "</td>" +
    "<td>" + pill(d.o, LANG === "es" ? d.o : d.oe, "postura") + "</td>" +
    '<td style="color:var(--ink-2)">' + esc(d.i || "—") + "</td>" +
    '<td class="cita">' + resaltar(d.cita, d.c) + "</td>" +
    "</tr>").join("");

  vacio.hidden = filas.length > 0;
  conteo.textContent = filas.length + " " + UI[LANG].de + " " + DATOS.length + " " + UI[LANG].pasajes;
}

/* ---- cambio de idioma ---- */
function aplicarIdioma(lang){
  LANG = lang;
  document.documentElement.lang = lang;
  document.title = UI[lang].titulo;
  for (const el of document.querySelectorAll("[data-en]")){
    if (!el.dataset.es) el.dataset.es = el.innerHTML;
    el.innerHTML = lang === "en" ? el.dataset.en : el.dataset.es;
  }
  for (const el of document.querySelectorAll("[data-en-title]")){
    if (!el.dataset.esTitle) el.dataset.esTitle = el.getAttribute("title") || "";
    el.setAttribute("title", lang === "en" ? el.dataset.enTitle : el.dataset.esTitle);
  }
  for (const el of document.querySelectorAll("[data-en-placeholder]")){
    if (!el.dataset.esPlaceholder) el.dataset.esPlaceholder = el.getAttribute("placeholder") || "";
    el.setAttribute("placeholder",
      lang === "en" ? el.dataset.enPlaceholder : el.dataset.esPlaceholder);
  }
  $("#btn-es").setAttribute("aria-pressed", String(lang === "es"));
  $("#btn-en").setAttribute("aria-pressed", String(lang === "en"));
  try { localStorage.setItem("khev-lang", lang); } catch (e) {}
  construirFiltros();
  pintar();
}

$("#btn-es").addEventListener("click", () => aplicarIdioma("es"));
$("#btn-en").addEventListener("click", () => aplicarIdioma("en"));
for (const id of ["#f-ambito", "#f-nivel", "#f-postura"]) $(id).addEventListener("change", pintar);
$("#f-texto").addEventListener("input", pintar);

let inicial = "es";
try {
  const guardado = localStorage.getItem("khev-lang");
  if (guardado === "en" || guardado === "es") inicial = guardado;
  else if ((navigator.language || "").slice(0,2) !== "es") inicial = "en";
} catch (e) {}
aplicarIdioma(inicial);
</script>
"""


if __name__ == "__main__":
    construir()
