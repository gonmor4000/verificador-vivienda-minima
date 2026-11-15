# RNE consultable

`rne.html` (en la raíz) muestra el Reglamento Nacional de Edificaciones completo: Título III.1 Arquitectura (A.010 a A.130, en `rne-data.js`) y el resto de normas de los Títulos I, II y III (en `normas/`, una por archivo, cargadas al abrirlas o al buscar).

## Enlaces estables

- Norma: `rne.html#A020`
- Artículo: `rne.html#A020-art-11`
- Numeral: `rne.html#A020-art-11.4`
- Literal: `rne.html#A020-art-11.4-a` (si el literal cuelga directo del artículo: `rne.html#A010-art-13-a`)
- Anexo: `rne.html#A020-anexo-1`

Si un enlace pide un numeral o literal que no existe, la página baja al artículo.
El verificador (`index.html`) convierte solo cada cita «A.0x0 art. N…» en un enlace a estas anclas.

## Archivos

- `rne-data.js`: texto de las normas (generado, no editar a mano).
- `ilustrado-data.js`: índice del RNE ilustrado (página de cada artículo) y cruce con los artículos vigentes.
- `RNE_ilustrado.pdf`: RNE ilustrado (edición 2012; A.010 y A.020 de 2006 y parte de la A.030).
- `oficial/A010.pdf` … `A130.pdf`: PDF oficiales de cada norma; `oficial-data.js` dice en qué página empieza cada artículo (si falta uno, la página usa la del artículo anterior).
- `herramientas/`: `RNE.txt` (texto de las separatas de El Peruano), `parse.py`, `tablas.py` (tablas rearmadas a mano), `ilu.py` y `oficial.py`.

## Otras normas (`normas/`)

- `normas/indice.js`: lista (código, título, versión, grupo, páginas). `normas/<ID>.js`: texto de cada norma (G010, GH020, TH010, CE040, OS090, EC040, GE020, A011, A140, E070, IS010, EM110…).
- Anclas: normas por artículos como `rne.html#E070-art-8.3`; normas por numerales como `rne.html#E060-21.4.2` o `rne.html#OS030-3`; definiciones de la G.040 como `rne.html#G040-def-area-techada`.
- `oficial/<ID>.pdf`: PDF oficial; cada sección guarda su página («PDF oficial p. N»).
- Faltan en la carpeta de origen: E.031 (el archivo traía la E.040), E.050 (traía la EM.020) y la parte inicial de la G.020. La E.030, la E.080 y la EM.040 son escaneos: su texto sale de OCR (tesseract, español).
- Regenerar: `pdftotext <pdf> txt/<ID>.txt` (OCR para los escaneados, páginas separadas por \f) y `python3 rne/herramientas/otras.py txt rne/normas`.

## Versiones

Vigentes en el archivo: A.010 (RM 191-2021), A.020 (RM 188-2021), A.040 (RM 068-2020), A.070 (RM 061-2021), A.120 (RM 075-2023).
Las demás están como vienen en el archivo (texto del D.S. 011-2006). El ilustrado dibuja las versiones de 2006: la numeración no coincide con la vigente, por eso cada artículo vigente indica a qué artículo antiguo corresponde su página.

## Regenerar

```
python3 rne/herramientas/parse.py rne/herramientas/RNE.txt rne/rne-data.js
python3 rne/herramientas/ilu.py rne/RNE_ilustrado.pdf rne/ilustrado-data.js   # necesita pdftotext
python3 rne/herramientas/oficial.py   # página de cada artículo en rne/oficial/*.pdf → rne/oficial-data.js
```
El cruce artículo vigente → artículo del ilustrado está escrito a mano en `ilu.py` (MAP y EXTRA).
