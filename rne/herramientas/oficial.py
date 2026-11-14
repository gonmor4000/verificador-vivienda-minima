"""Página de cada artículo en los PDF oficiales (rne/oficial/Axxx.pdf) -> rne/oficial-data.js"""
import json, re, subprocess, sys, os, glob
DIR = sys.argv[1]; OUT = sys.argv[2]
RE = re.compile(r'^\s*Art[ií]culos?\s+(\d+)\s*[\.°º]?\s*-', re.M)
res = {}
for f in sorted(glob.glob(os.path.join(DIR, 'A*.pdf'))):
    nid = os.path.basename(f)[:-4]
    n = int(subprocess.run(['pdfinfo', f], capture_output=True, text=True).stdout.split('Pages:')[1].split()[0])
    occ = {}
    for p in range(1, n + 1):
        t = subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), f, '-'], capture_output=True, text=True).stdout
        for m in RE.finditer(t):
            occ.setdefault(int(m.group(1)), []).append(p)
    # el art. 1-2 de la resolución va antes que la norma: tomar la última aparición antes del art. 3
    pages = {}
    lim = min(occ.get(3, [1]))
    for a in sorted(occ):
        cand = occ[a]
        if a <= 2:
            before = [p for p in cand if p <= lim]
            pages[a] = before[-1] if before else cand[0]
        else:
            prev = max([pages[b] for b in pages if b < a] or [1])
            ok = [p for p in cand if p >= prev]
            pages[a] = ok[0] if ok else cand[0]
    res[nid] = {'pdf': f'oficial/{nid}.pdf', 'pages': n, 'art': pages}
    print(nid, n, len(pages), [pages.get(k) for k in (1, 2, 3, 10, max(pages) if pages else 0)])
open(OUT, 'w').write('// Página de cada artículo en el PDF oficial de cada norma. Generado por herramientas/oficial.py\nwindow.RNE_OFICIAL=' + json.dumps(res, separators=(',', ':')) + ';\n')
