#!/usr/bin/env python3
"""Convierte el RNE.txt (texto de las separatas de El Peruano) en rne-data.js."""
import json, re, sys

SRC, OUT = sys.argv[1], sys.argv[2]
L = open(SRC, encoding='utf-8').read().split('\n')

# (id, código, título, versión, vigente_desde, pre_ini, body_ini, fin) — líneas 1-based, inclusivas
NORMS = [
 ('A010','A.010','Condiciones generales de diseño','RM 191-2021-VIVIENDA (El Peruano, 8 jul 2021)',True, 1,94,996),
 ('A020','A.020','Vivienda','RM 188-2021-VIVIENDA (El Peruano, 7 jul 2021)',True, 997,1083,1756),
 ('A030','A.030','Hospedaje','Texto del archivo (la resolución no figura en él)',False, None,2517,3412),
 ('A040','A.040','Educación','RM 068-2020-VIVIENDA (El Peruano, 13 mar 2020)',True, 3545,3702,4113),
 ('A050','A.050','Salud','D.S. 011-2006-VIVIENDA (texto original)',False, None,4115,4541),
 ('A060','A.060','Industria','D.S. 011-2006-VIVIENDA (texto original)',False, None,4542,4704),
 ('A070','A.070','Comercio','RM 061-2021-VIVIENDA (El Peruano, 11 feb 2021)',True, 4706,4797,5723),
 ('A080','A.080','Oficinas','D.S. 011-2006-VIVIENDA (texto original)',False, None,5724,5853),
 ('A090','A.090','Servicios comunales','D.S. 011-2006-VIVIENDA (texto original)',False, None,5854,5984),
 ('A100','A.100','Recreación y deportes','D.S. 011-2006-VIVIENDA (texto original)',False, None,5985,6319),
 ('A110','A.110','Transportes y comunicaciones','D.S. 011-2006-VIVIENDA (texto original)',False, None,6320,6494),
 ('A120','A.120','Accesibilidad universal en edificaciones','RM 075-2023-VIVIENDA',True, 6495,6601,7330),
 ('A130','A.130','Requisitos de seguridad','D.S. 011-2006-VIVIENDA (cap. VIII Comercio derogado por la RM 061-2021)',False, None,7331,11837),
]
TITLED = {'A010','A020','A030','A040','A070','A120'}

JUNK = [
 re.compile(r'^\d+\s+NORMAS LEGALES\b'), re.compile(r'^El Peruano\s*/.*NORMAS LEGALES\s*\d*\s*$'),
 re.compile(r'^NORMAS LEGALES\s*$'), re.compile(r'^AÑO DEL BICENTENARIO'), re.compile(r'^“AÑO DEL'),
 re.compile(r'^\d{6,7}-\d\s*$'), re.compile(r'^SEPARATA ESPECIAL\s*$'), re.compile(r'^Firmado Digitalmente por'),
 re.compile(r'^EMPRESA PERUANA DE SERVICIOS'), re.compile(r'^EDITORIALES S\.A\.'), re.compile(r'^Fecha: \d\d/\d\d/'),
]
def junk(s): return any(r.search(s) for r in JUNK)

LIG = re.compile(r'(?<![A-Za-zÁÉÍÓÚáéíóúñÑ])(\w*?(?:fi|fl|Fi|Fl|FI|FL)) (?=[a-záéíóúñ])')
def fix(s):
    s = s.replace('­', '').replace('\t', ' ')
    s = LIG.sub(lambda m: m.group(1), s)
    return re.sub(r'\s+', ' ', s).strip()

import unicodedata
def unac(t): return ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
def nice(h):
    h = fix(h)
    letters = [c for c in h if c.isalpha()]
    if letters and (sum(c.isupper() for c in letters) / len(letters) > 0.6 or re.search(r'[a-z][A-Z]', h)):
        h = h.lower()
        h = h[0].upper() + h[1:]
        h = re.sub(r'\b(i{1,3}|iv|v|vi{1,3}|ix|x|xi{1,3})\b', lambda m: m.group(1).upper(), h)
        h = re.sub(r'\ba\.(\d)', r'A.\1', h)
    return h

RE_ART = re.compile(r'^Art[ií]culos?\s+(\d+)\s*[\.°º]?\s*-\s*(.*)$')
RE_CH = re.compile(r'^(CAP[IÍ]TULO|SUB-?CAP[IÍ]TULO|T[IÍ]TULO|ANEXO|DISPOSICI[OÓ]N|GENERALIDADES)\b(.*)$', re.I)
RE_NUM = re.compile(r'^(\d+)\.(\d+)(?:\.(\d+))?\.?\s+(\S.*)$')
RE_LIT = re.compile(r'^([a-zA-Z])\)\s*(\S.*)$')
RE_CUADRO = re.compile(r'^(Cuadro|CUADRO|Tabla|TABLA)\s*(N[°º]|Nº)?\s*\d', re.I)
RE_GRAF = re.compile(r'^(Gr[aá]fi ?co|GRÁFICO)\b', re.I)
RE_ITEM = re.compile(r'^(\d+\)|[ivx]+\.|[ivx]+\)|-|•|Notas?:|[A-Z]\.\s|Nota\b)\s*', re.I)

def norm_data(nid, code, title, ver, vig, pre, b0, b1):
    lines = [l for l in L[b0-1:b1]]
    data = {'id': nid, 'code': code, 'title': title, 'version': ver, 'vigente': vig, 'secs': []}
    if pre:
        txt = [fix(l) for l in L[pre-1:b0-1] if l.strip() and not junk(l)]
        data['rm'] = paragraphs(txt)
    secs = data['secs']          # lista de capítulos/artículos en orden
    ids = set()
    def uid(i):
        base, k = i, 2
        while i in ids:
            i = f'{base}_{k}'; k += 1
        ids.add(i); return i
    cur = {'t': 'intro', 'id': uid(f'{nid}-inicio'), 'title': 'Encabezado', 'b': []}
    secs.append(cur)
    num_ctx = None
    anexo_n = 0
    i = 0
    raw = [l for l in lines if not junk(l)]
    # quitar el título de la norma de las primeras líneas
    while i < len(raw):
        s = raw[i].rstrip()
        st = s.strip()
        i += 1
        if not st:
            continue
        m = RE_ART.match(st)
        if m:
            n = int(m.group(1)); rest = fix(m.group(2))
            aid = uid(f'{nid}-art-{n}')
            art = {'t': 'art', 'n': n, 'id': aid, 'b': []}
            if nid in TITLED and rest and len(rest) < 95 and not rest.endswith('.'):
                # el título puede seguir en la línea siguiente (A.040 a dos columnas)
                nx = raw[i].strip() if i < len(raw) else ''
                if nx and len(nx) < 30 and not nx.endswith('.') and not RE_NUM.match(nx) and not RE_LIT.match(nx) and not RE_ART.match(nx):
                    rest += ' ' + fix(nx); i += 1
                art['title'] = rest.rstrip(' :')
            else:
                art['title'] = ''
                if rest: art['b'].append(['p', None, rest])
            secs.append(art); cur = art; num_ctx = None
            continue
        m = RE_CH.match(st)
        if m and not re.match(r'^ANEXO\s+\d+\.\s*$', st) and len(st) < 120 and (m.group(1).isupper() or re.search(r'[a-záéíóú][A-ZÁÉÍÓÚ]', m.group(1))) and (m.group(1).upper() != 'GENERALIDADES' or len(st) < 20):
            kind = m.group(1).upper()
            head = fix(st)
            # título del capítulo en la línea siguiente si va en mayúsculas
            nxt = raw[i].strip() if i < len(raw) else ''
            sub = ''
            if nxt and not RE_ART.match(nxt) and len(nxt) < 90 and (sum(c.isupper() for c in nxt) > 0.6 * max(1, sum(c.isalpha() for c in nxt)) or re.search(r'[a-záéíóú][A-ZÁÉÍÓÚ]', nxt)):
                sub = fix(nxt); i += 1
            if kind.startswith('ANEXO') or kind.startswith('DISPOSICI'):
                anexo_n += 1
                sid = uid(f'{nid}-anexo-{anexo_n}') if kind.startswith('ANEXO') else uid(f'{nid}-disp-{anexo_n}')
                cur = {'t': 'anexo', 'id': sid, 'title': nice(head + (' — ' + sub if sub else '')), 'b': []}
                secs.append(cur); num_ctx = None
            else:
                level = 2 if 'SUB' in kind else 1
                rom = (re.findall(r'\b([IVXLivxl]+)\b', head[len(m.group(1)):]) or [''])[0].upper()
                slug = ('subcap-' if level == 2 else 'cap-') + rom.lower() if rom else re.sub(r'[^a-z0-9]+', '-', unac(nice(head).lower())).strip('-')
                secs.append({'t': 'h', 'lvl': level, 'id': uid(f'{nid}-{slug}'),
                             'title': nice(head) + (' — ' + nice(sub) if sub else '')})
            continue
        cur['b'].append(['raw', None, s])
    # convertir las líneas crudas de cada sección en bloques
    for sec in secs:
        if 'b' not in sec: continue
        sec['b'] = blocks(sec, nid, uid)
    return data

def paragraphs(lines):
    out, buf = [], ''
    for t in lines:
        new = (not buf) or RE_NUM.match(t) or RE_LIT.match(t) or RE_ITEM.match(t) or re.search(r'[\.:;]$', buf)
        if new and buf:
            out.append(buf); buf = ''
        buf = (buf + ' ' + t).strip() if buf else t
    if buf: out.append(buf)
    return out

def blocks(sec, nid, uid):
    out = []
    ctx_num = None
    rows = None
    buf = None
    def flush():
        nonlocal buf
        if buf is not None:
            out.append(buf); buf = None
    for kind, _, s in sec['b']:
        if kind == 'p':
            flush(); buf = ['p', None, s]; continue
        st = fix(s)
        if not st: continue
        mnum = RE_NUM.match(st)
        is_num = mnum and sec['t'] == 'art' and int(mnum.group(1)) == sec['n']
        mlit = RE_LIT.match(st)
        # tablas: «Cuadro N° …» y líneas cortas siguientes
        if rows is not None:
            stop = is_num or mlit or len(s.rstrip()) >= 104 or RE_CUADRO.match(st) or RE_GRAF.match(st) \
                   or re.match(r'^(Notas?|[ivx]+\.)\s', st) \
                   or (len(st) >= 50 and not re.search(r'\d', st) and re.search(r'[\.;:]$', st))
            if not stop:
                rows.append(st); continue
            rows = None
        if re.search(r'[a-zá-ú][A-ZÁ-Ú]', st) and len(st) < 60 and not st.endswith('.') and not mlit and not is_num:
            flush(); out.append(['sub', None, nice(st)]); continue
        if RE_CUADRO.match(st):
            flush(); rows = []
            out.append(['tab', None, st, rows]); continue
        if RE_GRAF.match(st) and len(st) < 120:
            flush(); out.append(['fig', None, st]); continue
        if is_num:
            flush()
            nid_ = f"{sec['id']}.{mnum.group(2)}" + (f".{mnum.group(3)}" if mnum.group(3) else '')
            nid_ = uid(nid_)
            label = f"{mnum.group(1)}.{mnum.group(2)}" + (f".{mnum.group(3)}" if mnum.group(3) else '')
            ctx_num = nid_
            buf = ['num', nid_, mnum.group(4), label]; continue
        if mlit:
            flush()
            parent = ctx_num or sec['id']
            lid = uid(f"{parent}-{mlit.group(1).lower()}")
            buf = ['lit', lid, mlit.group(2), mlit.group(1) + ')']; continue
        if RE_ITEM.match(st):
            flush(); buf = ['p', None, st]; continue
        if buf is None:
            buf = ['p', None, st]; continue
        prev = buf[2]
        if re.search(r'[\.:;]$', prev) and st[:1].isupper():
            flush(); buf = ['p', None, st]; continue
        # unir líneas cortadas (guion final)
        if prev.endswith('-') and not prev.endswith(' -'):
            buf[2] = prev[:-1] + st
        else:
            buf[2] = prev + ' ' + st
    flush()
    # rows -> listas finales
    res = []
    for b in out:
        if b[0] == 'tab':
            res.append(['tab', None, b[2], '\n'.join(b[3])])
        else:
            res.append(b)
    return res

DATA = [norm_data(*n) for n in NORMS]
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('// Generado a partir del texto del RNE (separatas de El Peruano). No editar a mano: ver rne/README.md\n')
    f.write('window.RNE_NORMAS=')
    json.dump(DATA, f, ensure_ascii=False, separators=(',', ':'))
    f.write(';\n')
# resumen
for n in DATA:
    arts = [s for s in n['secs'] if s['t'] == 'art']
    nums = sum(1 for s in arts for b in s['b'] if b[0] == 'num')
    print(n['code'], 'art', len(arts), 'num', nums, 'secs', len(n['secs']), 'dup', [s['id'] for s in arts if '_' in s['id']][:5])
