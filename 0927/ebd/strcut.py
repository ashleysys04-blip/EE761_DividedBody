#!/usr/bin/env python3
"""Minimal Silvaco .str reader: pull Ec, Ev, Efp(hole QFL), psi, p, n along a horizontal cutline."""
import numpy as np
CODES = {'psi': '100', 'n': '106', 'p': '107', 'efp': '112', 'e1': '113', 'e2': '114'}

def read(fn):
    C, rows, codes = {}, [], None
    for l in open(fn):
        if l.startswith('c '):
            p = l.split(); C[int(p[1])] = (float(p[2]), float(p[3]))
        elif l.startswith('s '):
            codes = l.split()[2:]
        elif l.startswith('n '):
            rows.append(l.split())
    ix = {k: codes.index(v) for k, v in CODES.items()}
    out = []
    for p in rows:
        mat = p[2]
        if mat != '3':          # silicon only
            continue
        x, y = C[int(p[1]) + 1]
        v = p[3:]
        e1, e2 = float(v[ix['e1']]), float(v[ix['e2']])
        out.append((x, y, max(e1, e2), min(e1, e2), float(v[ix['efp']]),
                    float(v[ix['psi']]), float(v[ix['p']]), float(v[ix['n']])))
    return np.array(out)   # cols: x y Ec Ev Efp psi p n

def cut(a, y0, xmin=0.40, xmax=0.90):
    ys = np.unique(np.round(a[:, 1], 6))
    y = ys[np.argmin(abs(ys - y0))]
    b = a[(abs(a[:, 1] - y) < 1e-6) & (a[:, 0] >= xmin) & (a[:, 0] <= xmax)]
    b = b[np.argsort(b[:, 0])]
    _, u = np.unique(np.round(b[:, 0], 6), return_index=True)
    return y, b[u]
