#!/usr/bin/env python3
"""Third jump of NOKILL_TE8_XS60 (3.38 V up / 3.35 V down): is it a body -> island -> body hole loop?

Hole balance of each body from the .str snapshots around the jump (up 3.0 / 3.5 V, down 3.5 / 3.0 V):
  I_ii      : impact-ionization hole generation in that half (code 105), A
  R_body    : recombination in that p body (code 118), A
  I_p(x)    : hole current through a vertical cut of the Si film = W * integral(Jp_x dy) (code 221, A/cm^2; < 0 = right -> left)
              cuts: left island edge (into left body), island centre, right island edge (out of right body)
  share     : holes entering the left body from the island / (that + left I_ii)
Same for the killed island (DDS_TE8_XS60) and the island-lifetime sweep where snapshots exist.
Python reading of .str (codes: 105 G_ii, 118 U, 221 Jp_x, 107 p). Output: third_loop.dat, third_loop.png"""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.tri as mtri
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit')); sys.path.insert(0, os.path.join(R, 'tools'))
from mech2_ddsplit import read_full
Q, W, TSI = 1.602e-19, 0.5e-4, 0.05
XIL, XIR = 0.665, 0.695; XC = 0.5 * (XIL + XIR)
SNAP = [(4, 'up 3.0'), (5, 'up 3.5'), (11, 'down 3.5'), (12, 'down 3.0')]
RUNS = [('1e-12 (killed)', os.path.join(R, '1007_ddsplit', 'DDS_TE8_XS60')),
        ('1e-11', os.path.join(H, 'ISL_TAU1em11_XS60')),
        ('1e-10', os.path.join(H, 'ISL_TAU1em10_XS60')),
        ('1e-9', os.path.join(H, 'ISL_TAU1em9_XS60')),
        ('3e-9', os.path.join(H, 'ISL_TAU3em9_XS60')),
        ('1e-8 (not killed)', os.path.join(R, '1010_sink', 'NOKILL_TE8_XS60'))]


def cut_current(nodes, ix, x0, code='221'):
    """W * integral over the Si film of J(code) at x = x0 (A); linear interpolation on the node triangulation"""
    m = (nodes[:, 1] <= TSI + 1e-4) & (np.abs(nodes[:, 0] - x0) < 0.02)
    nd = nodes[m]; tri = mtri.Triangulation(nd[:, 0], nd[:, 1])
    f = mtri.LinearTriInterpolator(tri, nd[:, 2 + ix[code]])
    y = np.linspace(1e-4, TSI - 1e-4, 200); j = np.ma.filled(f(np.full_like(y, x0), y), np.nan)
    return W * np.trapz(np.nan_to_num(j), y * 1e-4)


def balance(fn):
    cen, area, f, nodes, ix = read_full(fn)
    x, y = cen[:, 0], cen[:, 1]; film = y <= TSI + 5e-4
    G, U = f('105'), f('118')
    s = lambda m, z: Q * W * np.sum(z[m] * area[m])
    return dict(IiiL=s(film & (x < XC), G), IiiR=s(film & (x > XC), G),
                RbL=s(film & (x > 0.5) & (x < XIL), U), RbR=s(film & (x > XIR) & (x < 0.8), U), Risl=s(film & (x > XIL) & (x < XIR), U),
                IpL=cut_current(nodes, ix, XIL + 0.001), IpC=cut_current(nodes, ix, XC), IpR=cut_current(nodes, ix, XIR - 0.001))


rows = []
for lab, base in RUNS:
    for k, st in SNAP:
        fn = f'{base}_T_tr_{k}'
        if not os.path.exists(fn): continue
        b = balance(fn); inL = -b['IpL']
        rows.append((lab, st, b['IiiL'], b['IiiR'], b['RbL'], b['RbR'], b['Risl'], -b['IpR'], -b['IpC'], inL, inL / max(inL + b['IiiL'], 1e-30)))
hdr = ('# island tau | snapshot | I_ii left | I_ii right | R left body | R right body | R island | '
       'holes right body->island | at island centre | island->left body | share of left-body hole supply from island   (A, third_loop.py)')
with open(os.path.join(H, 'third_loop.dat'), 'w') as fo:
    fo.write(hdr + '\n')
    for r in rows: fo.write('%-18s %-9s ' % r[:2] + ' '.join('%10.3e' % z for z in r[2:-1]) + '  %.3f\n' % r[-1])
print(open(os.path.join(H, 'third_loop.dat')).read())

# figure: hole balance bars for NOKILL around the jump + Jp_x maps up 3.0 / 3.5 V for killed vs not killed
fig = plt.figure(figsize=(15, 8)); gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1, 1])
a = fig.add_subplot(gs[0, :])
nk = [r for r in rows if r[0].startswith('1e-8')]; xs = np.arange(len(nk)); wd = 0.2
for i, (j, lb, c) in enumerate([(2, 'I_ii left', 'tab:purple'), (3, 'I_ii right', 'tab:green'), (7, 'holes leaving right body into island', 'tab:orange'), (9, 'holes entering left body from island', 'tab:red')]):
    a.bar(xs + (i - 1.5) * wd, [max(r[j], 1e-30) for r in nk], wd, color=c, label=lb)
a.set_yscale('log'); a.set_ylim(1e-9, 1e-1); a.set_xticks(xs); a.set_xticklabels([f'{r[1]} V\n(share from island {r[-1]:.2f})' for r in nk])
a.set_ylabel('hole current (A)'); a.legend(fontsize=8, ncol=4); a.grid(alpha=.3, axis='y')
a.set_title('NOKILL_TE8_XS60 (island tau 1e-8 s): hole balance across the 3.38 V up / 3.35 V down jump', fontsize=10)
for r_, (lab, base) in enumerate([RUNS[0], RUNS[3]]):
    for c_, (k, st) in enumerate(SNAP[:2]):
        ax = fig.add_subplot(gs[1 + r_, c_]); cen, area, f, nodes, ix = read_full(f'{base}_T_tr_{k}')
        m = (nodes[:, 1] <= TSI + 1e-4) & (nodes[:, 0] > 0.45) & (nodes[:, 0] < 0.85); nd = nodes[m]
        z = -nd[:, 2 + ix['221']]; z = np.sign(z) * np.log10(np.maximum(np.abs(z), 1))
        cs = ax.tricontourf(mtri.Triangulation(nd[:, 0], nd[:, 1]), z, levels=np.linspace(-8, 8, 33), cmap='RdBu_r', extend='both'); fig.colorbar(cs, ax=ax)
        for xv in (0.5, XIL, XIR, 0.8): ax.axvline(xv, color='k', lw=.5, ls=':')
        ax.set_ylim(0.05, 0); ax.set_title(f'island tau {lab}, {st} V: hole current toward source (-Jp_x), sign*log10|A/cm2|  ({os.path.basename(base)}_T_tr_{k})', fontsize=8)
fig.suptitle('Python reading of .str (not Tonyplot). Red = holes moving right -> left (drain side -> source side). Dotted = gate edges and island edges', fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(H, 'third_loop.png'), dpi=110)
