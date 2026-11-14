import json, re, subprocess, sys
PDF = sys.argv[1]; OUT = sys.argv[2]
starts = []  # (norm, n, title, page)
norm = None
for p in range(1, 58):
    t = subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), '-layout', PDF, '-'], capture_output=True, text=True).stdout
    for line in t.split('\n'):
        s = line.strip()
        m = re.match(r'^NORMA A\.\s?0(\d0)', s)
        if m: norm = 'A0' + m.group(1)
        m = re.match(r'^Artículo (\d+)\s*([A-ZÁÉÍÓÚÑ ,\.]*)', s)
        if m and norm:
            title = re.split(r'\s{3,}', m.group(2).strip())[0].strip()
            starts.append((norm, int(m.group(1)), title, p))
# descriptores para artículos sin título en el ilustrado
DESC = {('A010',1):'Objeto',('A010',2):'Soluciones alternativas',('A010',3):'Calidad arquitectónica',('A010',4):'Parámetros urbanísticos',
 ('A010',5):'Localidades sin plan urbano',('A010',6):'Uso mixto',('A010',7):'Normas aplicables',('A010',8):'Accesos',('A010',9):'Retiros',
 ('A010',10):'Retiros para ensanche de vías',('A010',16):'Separación entre edificaciones',('A010',17):'Separación sísmica',
 ('A010',21):'Dimensiones de los ambientes',('A010',45):'Ductos (basura)',('A010',59):'Cálculo de ocupantes',('A010',65):'Características de los estacionamientos',
 ('A010',66):'Características de los estacionamientos (2)',('A020',6):'Remisión a la A.010',('A020',17):'Estudio de suelos',
 ('A020',18):'Cerramientos exteriores',('A020',25):'Instalaciones sanitarias',('A020',29):'Conjuntos residenciales y quintas',
 ('A030',1):'Ámbito',('A030',2):'Definición',('A030',3):'Alcance',('A030',4):'Reglamento de hospedajes',('A030',5):'Condiciones mínimas',
 ('A030',6):'Clasificación',('A030',7):'Condiciones',('A030',8):'Condiciones',('A030',9):'Ubicación',('A030',10):'Retiros y áreas libres',('A030',11):'Instalaciones'}
arts = {}
for i, (nm, n, title, p) in enumerate(starts):
    last = {'A010':39,'A020':52,'A030':57}[nm]
    if i + 1 < len(starts) and starts[i+1][0] == nm:
        nxt = starts[i+1][3]; end = max(p, nxt - 1)
    else:
        end = last
    if i + 1 < len(starts) and starts[i+1][3] == p: end = p
    t = title.capitalize() if title and not title.endswith(' LOS') else DESC.get((nm, n), '')
    t = t.replace(' a. ', ' A.')
    arts.setdefault(nm, {})[n] = {'t': t, 'p': [p, end]}
# cruce: artículo vigente -> artículos del ilustrado (2006). 'mismo' = mismo texto/versión
MAP = {
 'A010': {1:[1],2:[1],3:[3],4:[4],5:[2,5],6:[6],7:[8],8:[9,10,11],10:[4],11:[12],12:[13],13:[14],14:[15],16:[16,17,18,19,20],
          17:[21],18:[22,23,24],19:[34,35],20:[25],21:[32],22:[26],23:[29],24:[26],25:[26,27],26:[26],27:[26],28:[26],29:[26],30:[26],31:[26],
          32:[28],33:[29],34:[30,31],35:[33],36:[47,48,49],37:[50],38:[51,52],39:[53],40:[54],41:[55,56],42:[57,58],43:[41,43,44],44:[40],
          45:[46],46:[42],47:[59],48:[36,37,38],49:[39],50:[64],51:[60,61],52:[62,63],53:[67],54:[65,66],55:[69],58:[68]},
 'A020': {1:[1],2:[1],3:[1,2],4:[3],5:[4],7:[5],8:[8],10:[7,9],12:[12,19],13:[10],14:[18,22],15:[10],16:[11],18:[23],19:[20],20:[23],21:[15],
          22:[21,26,27],23:[9,24,25],24:[21],25:[32,33],27:[27],28:[17],29:[16],30:[13,14,34,35]},
 'A030': {1:[1,2,3],2:[2,3],3:[9,10],4:[5,6,7,8,11],6:[5],7:[4,6]},
}
# temas de la A.010 antigua que en la versión vigente pasaron a otra norma
EXTRA = {'A020-art-9':('A010',[22]),'A020-art-11':('A010',[19,20]),'A020-art-13':('A010',[25]),'A020-art-15':('A010',[29]),
         'A020-art-18':('A010',[33]),'A020-art-12':('A010',[34])}
cross = {}
for nm, mp in MAP.items():
    for n, olds in mp.items():
        cross[f'{nm}-art-{n}'] = [[nm, o] for o in olds if o in arts[nm]]
for k, (nm, olds) in EXTRA.items():
    cross.setdefault(k, []).extend([[nm, o] for o in olds])
data = {'pdf': 'RNE_ilustrado.pdf', 'arts': arts, 'cross': cross,
        'normas': {'A010': {'p': [1, 39], 'ed': 'A.010 de 2006 (D.S. 011-2006-VIVIENDA). La vigente es la RM 191-2021: la numeración y varias medidas cambiaron.'},
                   'A020': {'p': [40, 52], 'ed': 'A.020 de 2006. La vigente es la RM 188-2021: la numeración y varias medidas cambiaron.'},
                   'A030': {'p': [53, 57], 'ed': 'A.030 de 2006 (solo arts. 1-11). La del archivo es posterior.'}}}
open(OUT, 'w').write('// Índice del «RNE ilustrado» (PDF de 2012) y cruce con los artículos vigentes. Ver rne/README.md\nwindow.RNE_ILU=' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n')
for nm in arts: print(nm, len(arts[nm]), [ (n,a['t'],a['p']) for n,a in list(arts[nm].items())[:70]])
