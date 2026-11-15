#!/usr/bin/env python3
"""Normas del RNE que no están en RNE.txt (Títulos I, II y III salvo A.010–A.130).

Lee el texto de cada PDF oficial (pdftotext, páginas separadas por \\f; las escaneadas
pasan antes por OCR) y escribe rne/normas/<ID>.js con la misma estructura que rne-data.js,
más rne/normas/indice.js con la lista de normas (código, título, versión, grupo, páginas).

Uso: python3 otras.py <carpeta_txt> <carpeta_salida>
  carpeta_txt: <ID>.txt por norma (texto de pdftotext sin -layout, con \\f entre páginas).
"""
import json, re, sys, os, unicodedata

TXT, OUT = sys.argv[1], sys.argv[2]

# id, código, título, versión, vigente (versión actualizada), grupo, ocr
NORMAS = [
 ('G010','G.010','Consideraciones básicas','Texto del archivo (separata de El Peruano 2309793)',False,'I','',False),
 ('G020','G.020','Principios generales','Texto del archivo (separata de El Peruano 2309793; el PDF empieza en el numeral 5.6)',False,'I','',False),
 ('G030','G.030','Derechos y responsabilidades','D.S. 011-2006-VIVIENDA y modificatorias (texto del archivo)',False,'I','',False),
 ('G040','G.040','Definiciones','RM 029-2021-VIVIENDA (El Peruano, 29 ene 2021)',True,'I','',False),
 ('G050','G.050','Seguridad durante la construcción','D.S. 010-2009-VIVIENDA',False,'I','',False),
 ('GH010','GH.010','Condiciones generales de las habilitaciones','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('GH020','GH.020','Componentes de diseño urbano','D.S. 006-2011-VIVIENDA',False,'II','',False),
 ('TH010','TH.010','Habilitaciones residenciales','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('TH020','TH.020','Habilitaciones para uso comercial','D.S. 006-2011-VIVIENDA',False,'II','',False),
 ('TH030','TH.030','Habilitaciones para uso industrial','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('TH040','TH.040','Habilitaciones para usos especiales','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('TH050','TH.050','Habilitaciones en riberas y laderas','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('TH060','TH.060','Reurbanización','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('CE010','CE.010','Pavimentos urbanos','D.S. 010-2010-VIVIENDA',False,'II','',False),
 ('CE020','CE.020','Suelos y taludes','D.S. 017-2012-VIVIENDA',False,'II','',False),
 ('CE030','CE.030','Obras especiales y complementarias','D.S. 005-2014-VIVIENDA',False,'II','',False),
 ('CE040','CE.040','Drenaje pluvial','RM 126-2021-VIVIENDA',True,'II','',False),
 ('OS010','OS.010','Captación y conducción de agua para consumo humano','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('OS020','OS.020','Plantas de tratamiento de agua para consumo humano','D.S. 024-2009-VIVIENDA',False,'II','',False),
 ('OS030','OS.030','Almacenamiento de agua para consumo humano','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('OS040','OS.040','Estaciones de bombeo de agua para consumo humano','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('OS050','OS.050','Redes de distribución de agua para consumo humano','D.S. 010-2009-VIVIENDA',False,'II','',False),
 ('OS070','OS.070','Redes de aguas residuales','D.S. 010-2009-VIVIENDA',False,'II','',False),
 ('OS080','OS.080','Estaciones de bombeo de aguas residuales','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('OS090','OS.090','Plantas de tratamiento de aguas residuales','D.S. 022-2009-VIVIENDA',False,'II','',False),
 ('OS100','OS.100','Consideraciones básicas de diseño de infraestructura sanitaria','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('EC010','EC.010','Redes de distribución de energía eléctrica','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('EC020','EC.020','Redes de alumbrado público','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('EC030','EC.030','Subestaciones eléctricas','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'II','',False),
 ('EC040','EC.040','Redes e instalaciones de comunicaciones','D.S. 006-2011-VIVIENDA',False,'II','',False),
 ('GE010','GE.010','Alcances y contenido','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('GE020','GE.020','Componentes y características de los proyectos','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('GE030','GE.030','Calidad de la construcción','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('GE040','GE.040','Uso y mantenimiento','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('A011','A.011','Criterios generales y condiciones de las edificaciones de interés (EIV)','Texto del archivo',False,'III','',False),
 ('A140','A.140','Bienes culturales inmuebles','RM 185-2021-VIVIENDA (El Peruano, 1 jul 2021)',True,'III','',False),
 ('E010','E.010','Madera','D.S. 005-2014-VIVIENDA',False,'III','',False),
 ('E020','E.020','Cargas','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('E030','E.030','Diseño sismorresistente','RM 355-2018-VIVIENDA, rectificada por la RM 043-2019-VIVIENDA',True,'III','',True),
 ('E040','E.040','Vidrio','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('E060','E.060','Concreto armado','D.S. 010-2009-VIVIENDA',False,'III','',False),
 ('E070','E.070','Albañilería','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('E080','E.080','Diseño y construcción con tierra reforzada','RM 121-2017-VIVIENDA',True,'III','',True),
 ('E090','E.090','Estructuras metálicas','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('E100','E.100','Bambú','D.S. 011-2012-VIVIENDA',False,'III','',False),
 ('IS010','IS.010','Instalaciones sanitarias para edificaciones','D.S. 017-2012-VIVIENDA',False,'III','',False),
 ('IS020','IS.020','Tanques sépticos','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('EM010','EM.010','Instalaciones eléctricas interiores','RM 083-2019-VIVIENDA',True,'III','',False),
 ('EM020','EM.020','Instalaciones de telecomunicaciones','RM 400-2018-VIVIENDA',True,'III','',False),
 ('EM030','EM.030','Instalaciones de ventilación','D.S. 005-2014-VIVIENDA',False,'III','',False),
 ('EM040','EM.040','Instalaciones de gas','RM 341-2018-VIVIENDA',True,'III','',True),
 ('EM050','EM.050','Instalaciones de climatización','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('EM060','EM.060','Chimeneas y hogares','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('EM070','EM.070','Transporte mecánico','RM 084-2019-VIVIENDA',True,'III','',False),
 ('EM080','EM.080','Instalaciones con energía solar','D.S. 010-2009-VIVIENDA',False,'III','',False),
 ('EM090','EM.090','Instalaciones con energía eólica','D.S. 017-2012-VIVIENDA',False,'III','',False),
 ('EM100','EM.100','Instalaciones de alto riesgo','D.S. 011-2006-VIVIENDA (texto del archivo)',False,'III','',False),
 ('EM110','EM.110','Confort térmico y lumínico con eficiencia energética','D.S. 006-2014-VIVIENDA',False,'III','',False),
]
VERSION_FIX = {}

JUNK = [
 re.compile(r'^\d+\s+NORMAS LEGALES\b'), re.compile(r'^El Peruano\s*/'), re.compile(r'NORMAS LEGALES\s*\d*\s*$'),
 re.compile(r'^NORMAS LEGALES\s*$'), re.compile(r'^“?AÑO DEL'), re.compile(r'^"AÑO DEL'),
 re.compile(r'^\d{6,7}-\d\s*$'), re.compile(r'^SEPARATA ESPECIAL\s*$'), re.compile(r'^Firmado Digitalmente por'),
 re.compile(r'^EMPRESA PERUANA DE SERVICIOS'), re.compile(r'^EDITORIALES S\.A\.'), re.compile(r'^EDITORA PERU\s*$'),
 re.compile(r'^Fecha: \d\d/\d\d/'), re.compile(r'^(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo) \d+ de \w+ de \d{4}\s*/?\s*$'),
re.compile(r'^Página \d+'), re.compile(r'^-\s*\d+\s*-$'),
]
def junk(s): return any(r.search(s) for r in JUNK)

LIG = re.compile(r'(?<![A-Za-zÁÉÍÓÚáéíóúñÑ])(\w*?(?:fi|fl|Fi|Fl|FI|FL)) (?=[a-záéíóúñ])')
def fix(s):
    s = unicodedata.normalize('NFC', s).replace('\u00ad', '').replace('\t', ' ').replace('\uf0b7', '•').replace('\uf0a7', '•').replace('\uf02d', '-')
    s = LIG.sub(lambda m: m.group(1), s)
    s = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', s)
    return re.sub(r'\s+', ' ', s).strip()

def unac(t): return ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
def nice(h):
    h = fix(h)
    letters = [c for c in h if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.6:
        h = h.lower()
        h = h[0].upper() + h[1:]
        h = re.sub(r'\b(i{1,3}|iv|v|vi{1,3}|ix|x|xi{1,3}|xiv|xv)\b', lambda m: m.group(1).upper(), h)
        h = re.sub(r'\b(rne|ntp|pmr|ph|glp|gn|cne|sencico|mvcs|iso|astm|aci)\b', lambda m: m.group(1).upper(), h)
        h = re.sub(r'\b([a-z]{1,2})\.(\d{3})\b', lambda m: m.group(1).upper() + '.' + m.group(2), h)
    return h

RE_ART = re.compile(r'^ART[ÍI]CULO\s+(\d+)\s*[°º]?\s*[\.\-–—:,]+\s*(.*)$', re.I)
RE_CH = re.compile(r'^(CAP[IÍ]TULO|SUB-?CAP[IÍ]TULO|T[IÍ]TULO|ANEXO|DISPOSICI[OÓ]N(?:ES)?\s+(?:COMPLEMENTARIAS?|FINAL(?:ES)?|TRANSITORIAS?)|SUB-T[IÍ]TULO)\b\s*(.*)$', re.I)
RE_NUMONLY = re.compile(r'^(\d{1,2}(?:\.\d{1,2}){0,4})\.?$')
RE_NUM = re.compile(r'^(\d{1,2}(?:\.\d{1,2}){0,4})\.?\s+(\S.*)$')
RE_LIT = re.compile(r'^([a-zA-Z])\)\s*(\S.*)?$')
RE_ITEM = re.compile(r'^(\d+\)|[ivx]+\.|[ivx]+\)|-|•|Notas?:|Nota\b)\s*', re.I)
RE_CUADRO = re.compile(r'^(Cuadro|CUADRO|Tabla|TABLA)\s*(N[°º]|Nº|N\.?)?\s*[\d\.]+', re.I)
RE_GRAF = re.compile(r'^(Gr[aá]fi ?co|GRÁFICO|Figura|FIGURA|Fig\.)\s*(N[°º])?\s*[\d\.]+', re.I)

def load(nid):
    t = open(os.path.join(TXT, nid + '.txt'), encoding='utf-8').read()
    lines = []
    for p, page in enumerate(t.split('\f'), 1):
        for l in page.split('\n'):
            s = fix(l)
            if s and not junk(s):
                lines.append((p, s))
    return lines

def code_re(code):
    a, d = code.split('.')
    return re.compile(r'^\W{0,3}NORMA(?:\s+T[ÉE]CNICA)?(?:\s+DE\s+EDIFICACI[ÓO]N)?\s+' + a + r'\s*\.?\s*' + d[0] + r'\s*' + d[1:] + r'\b', re.I)

def body_start(lines, code):
    cr = code_re(code)
    hits = [i for i, (_, s) in enumerate(lines) if cr.match(s)]
    reg = [i for i, (_, s) in enumerate(lines[:2500]) if re.match(r'^(Reg[íi]strese|Publ[íi]quese|SE RESUELVE)', s, re.I)]
    after = [i for i in hits if not reg or i > reg[-1]]
    if after: return after[0], (reg[-1] if reg else None)
    if hits: return hits[0], None
    return 0, None

def join_numbers(lines):
    """«3.1» sola en una línea + «Título» en la siguiente → «3.1 Título»; lo mismo con «Artículo» y «a)»."""
    out = []
    i = 0
    while i < len(lines):
        p, s = lines[i]
        if re.fullmatch(r'\d{1,3}', s) and i + 1 < len(lines) and not (is_title(lines[i+1][1]) and lines[i+1][1].upper() == lines[i+1][1]):
            i += 1; continue
        if (RE_NUMONLY.match(s) or re.match(r'^[a-z]\)$', s) or re.match(r'^ART[ÍI]CULO$', s, re.I)) and i + 1 < len(lines):
            nxt = lines[i + 1][1]
            if not RE_NUMONLY.match(nxt) and not re.match(r'^[a-z]\)$', nxt):
                out.append((p, s + ' ' + nxt)); i += 2; continue
        if not re.fullmatch(r'\d{1,3}', s): out.append((p, s))
        i += 1
    return out

def upper_start(t):
    w = re.findall(r'[A-Za-zÁÉÍÓÚÑáéíóúñ]+', t)[:2]
    return bool(w) and all(x.upper() == x for x in w) and len(w[0]) > 2

def dedupe_toc(secs):
    arts = [(i, s) for i, s in enumerate(secs) if s['t'] == 'art' and isinstance(s['n'], int)]
    cut = None
    for k in range(1, len(arts)):
        i, s = arts[k]
        if s['n'] <= 2 and arts[k-1][1]['n'] > s['n'] and any(a[1]['n'] > s['n'] + 1 for a in arts[:k]):
            prev = [a[1] for a in arts[:k]]
            txt = sum(len(b[2]) for a in prev for b in a['b'] if isinstance(b[2], str))
            if txt / len(prev) < 300: cut = i
    if cut is not None:
        secs = [s for j, s in enumerate(secs) if j >= cut or s['t'] == 'intro' or (s['t'] == 'anexo' and sum(len(x[2]) for x in s['b']) > 300)]
        seen = {}
        for s in secs:
            if s['t'] == 'art':
                base = re.sub(r'_\d+$', '', s['id'])
                if base not in seen: seen[base] = 1; s['id'] = base
    return dedupe_toc_old(secs)

def dedupe_toc_old(secs):
    """Índice al inicio («Artículo 1.- Objeto» sin texto) seguido del texto real: quitar el índice."""
    by = {}
    for s in secs:
        if s['t'] == 'art': by.setdefault(str(s['n']), []).append(s)
    drop = set()
    for n, lst in by.items():
        if len(lst) > 1 and sum(len(b[2]) for b in lst[0]['b'] if len(b) > 2 and isinstance(b[2], str)) < 200:
            drop.add(id(lst[0]))
    if len(drop) < 3: return secs
    first_real = min(i for i, s in enumerate(secs) if s['t'] == 'art' and id(s) not in drop and str(s['n']) in by and len(by[str(s['n'])]) > 1)
    out = [s for i, s in enumerate(secs) if not (i < first_real and s['t'] in ('art', 'h') and (id(s) in drop or s['t'] == 'h'))]
    for s in out:
        s['id'] = re.sub(r'_\d+$', '', s['id']) if s['t'] == 'art' and re.sub(r'_\d+$', '', s['id']) not in [x['id'] for x in out if x is not s] else s['id']
    return out

def is_title(t):
    """Título corto de sección: sin punto final, empieza en mayúscula, no es una frase larga."""
    t = t.strip()
    return 0 < len(t) <= 110 and t[0].isupper() and not re.search(r'[;,]$', t) and not (t.endswith('.') and len(t) > 60)

def parse(spec):
    nid, code, title, ver, vig, grp, _, ocr = spec
    lines = load(nid)
    b0, reg = body_start(lines, code)
    data = {'id': nid, 'code': code, 'title': title, 'version': VERSION_FIX.get(nid, ver), 'vigente': vig, 'grp': grp, 'secs': []}
    if ocr: data['ocr'] = True
    if reg is not None and b0 > 20:
        pre = [s for _, s in lines[:b0]]
        data['rm'] = paragraphs(pre)
    body = join_numbers(lines[b0:])
    # saltar el título de la norma (y el índice, si lo hay) hasta el primer contenido
    n_art = sum(1 for _, s in body if RE_ART.match(s))
    mode = 'art' if n_art >= 3 else 'num'
    secs = data['secs']; ids = set()
    def uid(i):
        base, k = i, 2
        while i in ids:
            i = f'{base}_{k}'; k += 1
        ids.add(i); return i
    cur = {'t': 'intro', 'id': uid(f'{nid}-inicio'), 'title': 'Encabezado', 'b': [], 'p': body[0][0] if body else 1}
    secs.append(cur)
    # numeración de primer nivel esperada (modo num): 1, 2, 3… ; con capítulos «N» se usa N.M
    top = 0
    chap = None      # número del capítulo actual (para normas tipo E.060 «CAPÍTULO 1 / 1.1 / 1.1.1»)
    lvl2 = False
    if mode == 'num':
        # ¿hay primer nivel secuencial «1 TÍTULO», «2 TÍTULO»…? si no, usar «N.M Título» bajo capítulos
        seq = 0
        for _, s in body:
            m = RE_NUM.match(s)
            if m and '.' not in m.group(1) and int(m.group(1)) == seq + 1 and is_title(m.group(2)) and upper_start(m.group(2)):
                seq += 1
        lvl2 = seq < 3
    anexo_n = 0
    in_toc = False
    for idx, (p, s) in enumerate(body):
        if idx < 3 and (code_re(code).match(s) or (idx and s.upper() == s and len(s) < 120 and not RE_NUM.match(s) and not RE_ART.match(s) and not RE_CH.match(s))):
            continue  # título de la norma
        m = RE_ART.match(s) if mode == 'art' else None
        if m:
            n = int(m.group(1)); rest = m.group(2).strip()
            art = {'t': 'art', 'n': n, 'id': uid(f'{nid}-art-{n}'), 'b': [], 'p': p}
            tm = re.match(r'^([A-ZÁÉÍÓÚÑ][^\.]{2,90}?)\s*[\.:]\s*[-–—]?\s*(.*)$', rest)
            if rest and rest.upper() == rest and len(rest) < 110 and re.search('[A-Z]', rest):
                art['title'] = nice(rest.rstrip(' .:-'))
            elif tm and len(tm.group(1)) < 70 and (tm.group(1).upper() == tm.group(1) or len(tm.group(1).split()) <= 7) and tm.group(2) == '' and len(rest) < 90:
                art['title'] = nice(tm.group(1))
            elif rest and len(rest) < 80 and not rest.endswith('.') and not rest.endswith(':') and len(rest.split()) <= 9 and rest[0].isupper():
                art['title'] = nice(rest)
            else:
                art['title'] = ''
                if rest: art['b'].append(['raw', None, rest])
            secs.append(art); cur = art
            continue
        mc = RE_CH.match(s)
        if mc and len(s) < 140:
            kind = unac(mc.group(1).upper())
            head = fix(s)
            if kind.startswith('ANEXO') or kind.startswith('DISPOSICION'):
                anexo_n += 1
                sid = uid(f'{nid}-anexo-{anexo_n}') if kind.startswith('ANEXO') else uid(f'{nid}-disp-{anexo_n}')
                cur = {'t': 'anexo', 'id': sid, 'title': nice(head), 'b': [], 'p': p}
                secs.append(cur)
                continue
            level = 2 if kind.startswith('SUB') else 1
            num = (re.findall(r'\b([IVXL]+|\d+)\b', mc.group(2)) or [''])[0]
            if num.isdigit(): chap = int(num)
            elif num: chap = roman(num)
            sl = ('subcap-' if level == 2 else 'cap-') + num.lower() if num else re.sub(r'[^a-z0-9]+', '-', unac(nice(head).lower())).strip('-')[:40]
            secs.append({'t': 'h', 'lvl': level, 'id': uid(f'{nid}-{sl}'), 'title': nice(head)})
            continue
        if mode == 'num':
            m = RE_NUM.match(s)
            if m:
                parts = m.group(1).split('.')
                rest = m.group(2)
                is_top = False
                if not lvl2 and len(parts) == 1 and int(parts[0]) in (top + 1, top + 2) and is_title(rest) and upper_start(rest):
                    top = int(parts[0]); is_top = True
                elif lvl2 and len(parts) == 2 and is_title(rest) and (chap is None or int(parts[0]) == chap) and \
                        (cur.get('lab', '').split('.')[0] != parts[0] or int(parts[1]) > int((cur.get('lab') or '0.0').split('.')[-1])):
                    is_top = True
                if is_top:
                    lab = m.group(1)
                    tt, body_txt = split_title(rest)
                    sec = {'t': 'art', 'n': lab, 'lab': lab, 'id': uid(f'{nid}-{lab}'), 'title': nice(tt), 'b': [], 'p': p}
                    if body_txt: sec['b'].append(['raw', None, body_txt])
                    secs.append(sec); cur = sec
                    continue
        cur['b'].append(['raw', None, s])
    if nid == 'G040':
        return defs(data, body, uid)
    secs = data['secs'] = dedupe_toc(secs)
    for sec in secs:
        if 'b' in sec:
            sec['b'] = blocks(sec, uid, mode)
    # quitar el índice inicial (líneas de un «Encabezado» muy largo hechas de títulos con número de página)
    return data

RE_DEF = re.compile(r'^([A-ZÁÉÍÓÚÑ][\wáéíóúñÁÉÍÓÚÑ ()/,\-]{1,70}?)\s*:\s+(\S.*)$')
def defs(data, body, uid):
    """G.040: una sección por letra y un bloque por definición («Término: texto»)."""
    secs = data['secs'][:1]; data['secs'] = secs; secs[0]['b'] = []
    cur = secs[0]; started = False; buf = None
    def flush():
        nonlocal buf
        if buf: cur['b'].append(buf); buf = None
    for p, s in body:
        if re.match(r'^ART[ÍI]CULO\s+[ÚU]NICO', s, re.I):
            started = True; cur['b'].append(['p', None, s]); continue
        if not started: continue
        m = RE_DEF.match(s)
        if m and len(m.group(1).split()) <= 7 and m.group(1) not in ('Nota', 'Ejemplo'):
            flush()
            term = m.group(1).strip(); L = unac(term[0]).upper()
            if cur.get('lab') != L:
                cur = {'t': 'art', 'n': L, 'lab': L, 'id': uid(f"G040-{L}"), 'title': 'Definiciones con ' + L, 'b': [], 'p': p}
                secs.append(cur)
            slug = re.sub(r'[^a-z0-9]+', '-', unac(term.lower())).strip('-')[:50]
            buf = ['num', uid(f'G040-def-{slug}'), m.group(2), term]
            continue
        if buf is None:
            buf = ['p', None, s]; continue
        if RE_GRAF.match(s) or re.match(r'^(Gr[aá]fico|Imagen)\b', s):
            continue
        buf[2] = buf[2][:-1] + s if buf[2].endswith('-') else buf[2] + ' ' + s
    flush()
    return data

def roman(r):
    v = {'I': 1, 'V': 5, 'X': 10, 'L': 50}; t = 0
    for a, b in zip(r, r[1:] + ' '):
        t += -v[a] if b != ' ' and v[a] < v.get(b, 0) else v[a]
    return t

def split_title(rest):
    """«ALCANCE Esta Norma…» → («ALCANCE», «Esta Norma…»); «Ubicación» → («Ubicación», '')."""
    m = re.match(r'^((?:[A-ZÁÉÍÓÚÑ0-9,/()\-]+\s?){1,12})\s+([A-ZÁÉÍÓÚ][a-záéíóúñ].*)$', rest)
    if m and m.group(1).strip().upper() == m.group(1).strip() and len(m.group(1)) > 3:
        return m.group(1).strip().rstrip('.:'), m.group(2)
    m = re.match(r'^(.{3,80}?)[\.:]\s+(\S.*)$', rest)
    if m and len(m.group(1).split()) <= 8:
        return m.group(1), m.group(2)
    if len(rest) <= 110:
        return rest.rstrip('.:'), ''
    return '', rest

def paragraphs(lines):
    out, buf = [], ''
    for t in lines:
        new = (not buf) or RE_NUM.match(t) or RE_LIT.match(t) or RE_ITEM.match(t) or re.search(r'[\.:;]$', buf)
        if new and buf:
            out.append(buf); buf = ''
        buf = (buf + ' ' + t).strip() if buf else t
    if buf: out.append(buf)
    return out

def blocks(sec, uid, mode):
    out = []
    buf = None
    ctx = None
    short = []   # líneas cortas seguidas: probable tabla
    def flush():
        nonlocal buf
        if buf is not None:
            out.append(buf); buf = None
    def flush_short():
        nonlocal short
        if len(short) >= 6:
            flush()
            title = short[0] if RE_CUADRO.match(short[0]) else 'Tabla'
            rows = short[1:] if RE_CUADRO.match(short[0]) else short
            out.append(['tab', None, title, '\n'.join(rows)])
        else:
            for x in short: add(x)
        short = []
    def add(st):
        nonlocal buf, ctx
        mnum = RE_NUM.match(st)
        mlit = RE_LIT.match(st)
        if RE_CUADRO.match(st) and len(st) < 140:
            flush(); out.append(['sub', None, st]); return
        if RE_GRAF.match(st) and len(st) < 140:
            flush(); out.append(['fig', None, st]); return
        if mnum and sec['t'] == 'art':
            lab = mnum.group(1)
            base = str(sec.get('lab') or sec['n'])
            if lab.startswith(base + '.') or (sec.get('lab') is None and lab.split('.')[0] == str(sec['n'])):
                flush()
                suf = lab[len(base):] if lab.startswith(base + '.') else lab[len(lab.split('.')[0]):]
                nid_ = uid(sec['id'] + suf)
                ctx = nid_
                buf = ['num', nid_, mnum.group(2), lab]; return
        if mlit and mlit.group(2):
            flush()
            lid = uid(f"{ctx or sec['id']}-{mlit.group(1).lower()}")
            buf = ['lit', lid, mlit.group(2), mlit.group(1) + ')']; return
        if RE_ITEM.match(st):
            flush(); buf = ['p', None, st]; return
        if buf is None:
            buf = ['p', None, st]; return
        prev = buf[2]
        if re.search(r'[\.:;]$', prev) and st[:1].isupper():
            flush(); buf = ['p', None, st]; return
        if prev.endswith('-') and not prev.endswith(' -'):
            buf[2] = prev[:-1] + st
        else:
            buf[2] = prev + ' ' + st
    for kind, _, s in sec['b']:
        st = fix(s)
        if not st: continue
        tabular = len(st) <= 38 and not re.search(r'[a-záéíóúñ]{3,}[\.;:]$', st) and not RE_LIT.match(st) and not RE_NUM.match(st)
        if tabular and not RE_ITEM.match(st):
            short.append(st); continue
        flush_short()
        add(st)
    flush_short()
    flush()
    return out

os.makedirs(OUT, exist_ok=True)
index = []
for spec in NORMAS:
    if not os.path.exists(os.path.join(TXT, spec[0] + '.txt')):
        print('falta', spec[0]); continue
    d = parse(spec)
    arts = [s for s in d['secs'] if s['t'] == 'art']
    nums = sum(1 for s in arts for b in s['b'] if b[0] == 'num')
    tabs = sum(1 for s in d['secs'] for b in s.get('b', []) if b[0] == 'tab')
    js = json.dumps(d, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(OUT, d['id'] + '.js'), 'w', encoding='utf-8') as f:
        f.write('// Generado por rne/herramientas/otras.py desde el PDF oficial. No editar a mano.\n')
        f.write('window.RNE_ADD(' + js + ');\n')
    words = len(' '.join(b[2] for s in d['secs'] for b in s.get('b', [])).split())
    index.append({k: d[k] for k in ('id', 'code', 'title', 'version', 'vigente', 'grp')} | ({'ocr': True} if d.get('ocr') else {}) | {'kb': round(len(js.encode()) / 1024), 'pages': open(os.path.join(TXT, d['id'] + '.txt'), encoding='utf-8').read().count('\f') + 1})
    print(f"{d['code']:7} secs {len(d['secs']):4} art {len(arts):4} num {nums:4} tab {tabs:3} words {words:6} kb {len(js.encode())//1024:5}  {[ (s.get('n'), s.get('title','')[:28]) for s in arts[:4]]}")
with open(os.path.join(OUT, 'indice.js'), 'w', encoding='utf-8') as f:
    f.write('// Normas cargadas aparte (una por archivo). Generado por rne/herramientas/otras.py\nwindow.RNE_OTRAS=')
    json.dump(index, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')
