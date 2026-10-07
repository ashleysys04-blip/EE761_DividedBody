#!/usr/bin/env python3
"""Render the device structure stored in a Silvaco .str file: regions (material) + net doping in Si.

Usage (python):
    from strstruct import draw
    draw('path/to/file.str', 'out.png', title='...', xlim=(0.35, 0.95), ylim=(0.30, -0.15), mesh=False)

.str format used here
    c <i> x y z                coordinate i (1-based)
    r <region> <material>      material code: 3 Si, 1 SiO2, 4 poly, 28 vacuum, 91 conductor
    t <i> <region> v1 v2 v3 .. triangle (1-based coordinate indices)
    s <n> <codes...>           solution field codes; 115 = net doping (cm^-3, n > 0)
    n <coord-1> <material> <values...>
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

MAT = {1: ('SiO2', '#cfe8f7'), 4: ('poly-Si gate', '#b39ddb'), 28: ('vacuum', '#ffffff'), 91: ('conductor', '#616161')}


def read(fn):
    C, reg, tri, codes, dop = {}, {}, [], None, {}
    for l in open(fn):
        k = l[:2]
        if k == 'c ':
            p = l.split(); C[int(p[1])] = (float(p[2]), float(p[3]))
        elif k == 'r ':
            p = l.split(); reg[int(p[1])] = int(p[2])
        elif k == 't ':
            p = l.split(); tri.append((int(p[2]), int(p[3]), int(p[4]), int(p[5])))
        elif k == 's ':
            codes = l.split()[2:]
        elif k == 'n ':
            p = l.split()
            if p[2] == '3' and codes and '115' in codes:
                dop[int(p[1]) + 1] = float(p[3 + codes.index('115')])
    return C, reg, tri, dop


def draw(fn, out, title='', xlim=None, ylim=None, mesh=False, ax=None, note=None):
    C, reg, tri, dop = read(fn)
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(11, 4.2))
    polys, cols = [], []
    cmap = plt.get_cmap('RdBu_r')
    for r, a, b, c in tri:
        m = reg.get(r, 0)
        xy = [C[a], C[b], C[c]]
        polys.append([(x * 1000, y * 1000) for x, y in xy])
        if m == 3:
            d = np.mean([dop.get(v, 0.0) for v in (a, b, c)])
            s = np.sign(d) * (np.log10(max(abs(d), 1e15)) - 15) / 6.0      # 1e15..1e21 -> 0..1
            cols.append(cmap(0.5 + 0.5 * s))
        else:
            cols.append(MAT.get(m, ('?', '#eeeeee'))[1])
    pc = PolyCollection(polys, facecolors=cols, edgecolors='k' if mesh else 'face', linewidths=0.15 if mesh else 0.2)
    ax.add_collection(pc)
    xs = [p[0] for q in polys for p in q]; ys = [p[1] for q in polys for p in q]
    ax.set_xlim(*(np.array(xlim) * 1000 if xlim else (min(xs), max(xs))))
    ax.set_ylim(*(np.array(ylim) * 1000 if ylim else (max(ys), min(ys))))
    ax.set_xlabel('x (nm)'); ax.set_ylabel('y (nm)'); ax.set_title(title, fontsize=10)
    if note: ax.text(0.01, 0.02, note, transform=ax.transAxes, fontsize=8, va='bottom', bbox=dict(fc='w', ec='0.7', alpha=0.9))
    if own:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(-6, 6))
        cb = fig.colorbar(sm, ax=ax, pad=0.01)
        cb.set_ticks([-6, -4, -2, 0, 2, 4, 6]); cb.set_ticklabels(['p 1e21', 'p 1e19', 'p 1e17', '1e15', 'n 1e17', 'n 1e19', 'n 1e21'])
        cb.set_label('net doping in Si (cm$^{-3}$)')
        fig.text(0.01, 0.005, 'source: ' + fn.split('/home/ysseo/')[-1] + '  (rendered with tools/strstruct.py)', fontsize=7, color='0.4')
        fig.tight_layout(); fig.savefig(out, dpi=130); plt.close(fig)
