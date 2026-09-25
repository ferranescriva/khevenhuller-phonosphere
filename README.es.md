# Fonosfera de un embajador imperial

**Español** · [English](README.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22958464.svg)](https://doi.org/10.5281/zenodo.22958464)

Material suplementario del artículo «A Habsburg Ambassador's Phonosphere: Musical Experience and Material Culture in the Writings of Hans Khevenhüller».

Este repositorio contiene los datos, el instrumento léxico y los scripts con los que se extrajeron y codificaron las referencias musicales y sonoras de los escritos de Hans Khevenhüller (1538-1606), embajador de los emperadores Maximiliano II y Rodolfo II ante Felipe II.

**Presentación web:** `index.html` (abrir en el navegador o consultar en GitHub Pages). La página es bilingüe y alterna entre español e inglés.

**Despliegue:** véase [`DEPLOY.md`](DEPLOY.md) para los pasos de publicación en GitHub Pages y la obtención del DOI en Zenodo.

---

## 1. Qué contiene este repositorio

| Carpeta | Contenido |
|---|---|
| `data/` | Tablas de datos en CSV y el léxico en JSON |
| `scripts/` | Los cinco programas del pipeline de extracción |
| `index.html` | Presentación web autocontenida de los resultados |

El repositorio **no incluye los textos fuente**, que son ediciones sujetas a derechos de autor. Contiene únicamente los datos derivados, con citas breves de extensión propia del comentario académico. Para reproducir el pipeline hay que disponer de las ediciones y digitalizarlas por cuenta propia.

## 2. Corpus

El trabajo se apoya en dos ediciones en castellano que se complementan. Ambas traducen el original alemán y por ello no siempre son literales, pero las dos se consideran válidas.

**Edición A. El diario.**
Khevenhüller, Hans. *Diario de Hans Khevenhüller: embajador imperial en la corte de Felipe II*. Edición de Sara Veronelli y Félix Labrador Arroyo. Madrid: Sociedad Estatal para la Conmemoración de los Centenarios de Felipe II y Carlos V, 2001.

Ofrece el texto seguido en castellano de época. Es la fuente principal de la actividad musical vivida, es decir, de la escucha, la asistencia y la valoración. La digitalización empleada cubre el Libro XIV y conserva la paginación impresa mediante marcadores `[p. N]`.

**Edición B. La documentación.**
Alvar Ezquerra, Alfredo (ed.). *El embajador imperial. Hans Khevenhüller (1538-1606) en España*. Madrid: Boletín Oficial del Estado, 2015.

Edición crítica que ordena por año el diario junto con cartas y documentación variada. Aporta el inventario, la almoneda y las cédulas de paso, que son la base de la evidencia sobre cultura material.

Conviene advertir que el título *Geheimes Tagebuch* (Diario secreto) fue añadido por Georg Khevenhüller en la edición de 1971. El embajador redactó el texto como *Khurzer Extrakt*.

## 3. Procedimiento de extracción

El pipeline consta de cinco pasos. Cada uno corresponde a un script de la carpeta `scripts/`.

**Paso 1. Extracción léxica sobre el corpus completo.**
`01_extraer_referencias.py` lee el texto, reconstruye la paginación impresa, detecta las entradas datadas y localiza los términos de un léxico organizado por categorías. La normalización elimina acentos y mayúsculas para el emparejamiento, pero conserva la grafía original en la cita. El emparejamiento tolera plurales, saltos de línea del OCR y términos de varias palabras. Un término terminado en asterisco funciona como raíz.

**Paso 2. Auditoría del instrumento y barrido evaluativo.**
`02_auditoria_y_evaluativos.py` cuenta las apariciones de cada término del léxico y marca los pasajes en cuyo entorno inmediato aparece un cualificador. La auditoría se conserva íntegra, incluidos los términos con cero apariciones, porque documentar qué se buscó y no aparece forma parte del resultado.

**Paso 3. Extracción del material funerario.**
`03_analisis_exequias.py` localiza los pasajes sobre exequias, honras y entierros, les asigna el difunto probable por proximidad de nombres y etiqueta cada uno como voz del diario o como aparato del editor.

**Paso 4. Codificación fonosférica.**
`04_capa_escucha.py` es el paso central. Localiza los pasajes con vocabulario musical en el diario y codifica cada uno según los tres ejes descritos en el apartado 5.

**Paso 5. Libro de codificación para revisión manual.**
`05_libro_codificacion.py` genera un libro de cálculo con listas desplegables validadas, pensado para que la codificación automática se revise a mano.

**Paso 6. Presentación web.**
`06_construir_web.py` lee los CSV, calcula los recuentos y escribe `index.html` con los datos incrustados. La página no depende de ficheros externos ni de conexión, de modo que funciona igual servida por GitHub Pages que descargada desde Zenodo.

## 4. Instrumento léxico

El léxico vive en `data/lexico_fonosfera.json` y está organizado en cuatro campos.

| Campo | Contenido |
|---|---|
| Música | voces genéricas, instrumentos, agrupaciones, géneros y acciones musicales |
| Sonido y ruido | campanas, pólvora y artillería, voz colectiva, pregón y silencio |
| Voz y rumor | rumor, murmuración y habla sub-audible |
| Metáfora musical | vocabulario musical migrado al lenguaje político y diplomático |

La auditoría en `data/auditoria_lexico.csv` recoge las apariciones de cada término. De los 158 términos del instrumento, 73 aparecen en el corpus y 85 no. Las ausencias son informativas. No se documenta ni un solo cañonazo, mosquete, cohete, vítor ni algazara, y tampoco aparecen «murmullo» ni «murmurar».

El anclaje semántico de los términos ambiguos se fijó en la lexicografía de la época, concretamente en el *Tesoro de la lengua castellana o española* de Sebastián de Covarrubias (Madrid, 1611). Tres entradas resultaron decisivas.

- **Murmullo.** «El ruido manso que haze el agua corriente, *a murmure*, por la figura onomatopeya. Y de allí *murmurar*, que es dezir mal de alguno, medio entre dientes.» El sonido reside aquí, no en «rumor».
- **Rumor.** «Lo que se dize, no en público, pero se esparce secretamente en el Pueblo.» En 1611 la voz es informativa y carece de componente acústico.
- **Salva.** Covarrubias reúne tres sentidos bajo la raíz de *salvo*: la prueba de manjares del maestresala, el disparo de arcabucería «en demostración de reconocimiento, paz, amistad», y la salvilla de plata. Solo el segundo es fonosférico. En este corpus la salva sonora aparece una sola vez, y el paisaje artillero viaja bajo «artillería», «disparo» y «arcabucería».

## 5. Ejes de codificación

La codificación aplica el marco de la fonosfera histórica de Antonio Rostagno, que distingue el sonido *pedal* o de fondo, la *señal* y el *símbolo*. Cada pasaje musical se codifica según tres ejes.

**Ámbito.** Dónde suena: sacro y litúrgico, profano y cortesano, militar y señalético, u otros. Se decide por los marcadores de contexto presentes en una ventana de 320 caracteres a cada lado del pasaje.

**Nivel.** Cómo funciona el sonido en la retícula de Rostagno. El sonido de ámbito militar se codifica como índice, es decir, como señal que ordena o avisa sin intención de significar más allá de su función. El sonido ceremonial, sacro o cortesano se codifica como símbolo, cargado de intención comunicativa. Un mismo instrumento cambia de nivel según el contexto, y el caso más claro es la trompeta.

**Postura del oyente.** Qué hace el testigo con lo que oye. Se limita al registro del hecho, pondera su magnitud mediante fórmulas de abundancia, o emite una valoración estética. El tercer caso es el que documenta la escucha experta.

A estos ejes se añaden cuatro campos descriptivos: los cualificadores estéticos empleados, los instrumentos nombrados, los géneros o piezas litúrgicas mencionados y la presencia de marcadores explícitos de escucha.

## 6. Diccionario de datos

### `data/escucha_codificacion.csv`
Los 103 pasajes musicales del diario, codificados. Es la tabla central.

| Columna | Descripción |
|---|---|
| `id` | identificador secuencial por orden de aparición |
| `pagina` | página impresa de la edición de Veronelli y Labrador Arroyo |
| `termino` | término musical que activó la detección |
| `ambito` | sacro / profano-cortesano / militar-señalético / otros |
| `nivel_rostagno` | índice / símbolo |
| `postura_oyente` | registro / ponderación de magnitud / valoración estética |
| `cualificadores` | cualificadores estéticos presentes en la cita |
| `magnitud` | fórmulas de abundancia presentes en la cita |
| `instrumentos_nombrados` | instrumentos citados explícitamente |
| `generos_piezas` | géneros o piezas litúrgicas citadas |
| `escucha_explicita` | marca si hay verbos u objetos de escucha |
| `cita` | la frase completa del diario |

### `data/exequias_pasajes.csv`
621 pasajes sobre exequias, honras y entierros extraídos de la edición de Alvar Ezquerra, con la columna `voz` que distingue la narración del diario del aparato del editor.

### `data/referencias_fonosfera.csv`
577 referencias del cribado amplio sobre la edición de Alvar Ezquerra, con las columnas de codificación preparadas para revisión manual.

### `data/auditoria_lexico.csv`
Apariciones de cada uno de los 158 términos del instrumento léxico.

### `data/lexico_fonosfera.json`
El léxico completo, editable. Sirve de entrada a los scripts 1 y 2.

## 7. Reproducción

Los scripts requieren Python 3.8 o superior. Los pasos 4 y 6 usan únicamente la biblioteca estándar. Los pasos 1, 3 y 5 requieren `openpyxl`, y el paso 1 requiere además `pdfplumber` si se parte de un PDF en vez de un texto.

Las transcripciones del corpus van en la carpeta `corpus/`, que se distribuye vacía por las razones indicadas en el apartado 1.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install openpyxl pdfplumber

# Paso 4, la codificación central
python3 scripts/04_capa_escucha.py corpus/diario_veronelli_labrador.md \
        -o data/escucha_codificacion.csv

# Paso 6, regenerar la presentación web
python3 scripts/06_construir_web.py
```

Los scripts 2, 3 y 5 llevan las rutas del corpus como constantes al principio del fichero y hay que ajustarlas a la ubicación local. Se espera que la transcripción conserve la paginación impresa mediante marcadores `[p. N]`.

## 8. Límites

La codificación es automática y por tanto revisable. Constituye un punto de partida para la lectura crítica y no un resultado cerrado. Tres advertencias concretas.

El corpus procede de dos traducciones del alemán que no siempre son literales, de modo que las conclusiones sobre el léxico de apreciación deben tomarse con la prudencia que impone esa cadena de transmisión.

Las cifras tienen valor indicativo y no estadístico, dada la desigualdad de las submuestras. El ámbito profano reúne 12 pasajes y el sacro 54, por lo que comparar sus porcentajes de valoración exige cautela.

La asignación del difunto en la tabla de exequias se hace por proximidad de nombres y requiere verificación caso por caso, especialmente en las filas marcadas con interrogación.

## 9. Cita

> Escrivà-Llorca, Ferran. *Fonosfera de un embajador imperial: datos y código*. Material suplementario. 2026. [DOI pendiente de asignación en Zenodo]

Para el artículo al que acompaña este material, véase la referencia completa en la publicación correspondiente.

## 10. Licencia

Los datos se distribuyen bajo Creative Commons Reconocimiento 4.0 Internacional (CC BY 4.0). El código se distribuye bajo licencia MIT. Las citas del diario proceden de ediciones con derechos de autor y se reproducen en la extensión breve propia del comentario académico.

---
