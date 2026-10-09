#!/usr/bin/env python3
"""Why each latch happens: hole balance of each STL from the .str snapshots of one split (default DDS_BASE_SNAP).

For every snapshot (MixedMode .str = <name>_T_tr_N) and for each STL (left: x < island centre, right: x > island centre):
  E_peak  : peak |E| (V/cm) in that STL (field code 103)
  I_ii    : hole generation current by impact ionization = q * W * integral(G_ii dA)   (code 105, A)
  R_body  : hole loss by recombination inside the STL's p body = q * W * integral(U dA)   (code 118, A)
  R_src   : recombination in that STL's n+ source (left: n+ source, right: n+ island) = where body holes are injected
  barrier : electron barrier source -> body (eV), p_body : mean hole density in the body
plus the STL electron current from the log (left: |Is|, right: |Itap| + |Is|) and M-1 = I_ii / I_e.
Triangle-area integration over the Si triangles of the .str (W = 0.5 um).
Writes mech2_<name>.dat and fig/mech2_<name>.png (+ fig/mech2_maps_<name>.png: G_ii and U maps at key snapshots).
"""
import sys, os, re, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.tri as mtri
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here); sys.path.insert(0, os.path.join(here, '..', 'tools'))
from mech_ddsplit import snap_map, island
from analyze_ddsplit import load_cols, columns
Q, W = 1.602e-19, 0.5e-4   # C, cm

def read_full(fn):
    C, reg, tri, codes, val = {}, {}, [], None, {}
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
            if p[2] == '3':
                val[int(p[1]) + 1] = [float(x) for x in p[3:3 + len(codes)]]
    ix = {c: i for i, c in enumerate(codes)}
    T = [(a, b, c) for r, a, b, c in tri if reg.get(r) == 3 and a in val and b in val and c in val]
    xy = np.array([[C[a], C[b], C[c]] for a, b, c in T])                       # (n,3,2) um
    area = 0.5 * np.abs((xy[:, 1, 0] - xy[:, 0, 0]) * (xy[:, 2, 1] - xy[:, 0, 1]) - (xy[:, 2, 0] - xy[:, 0, 0]) * (xy[:, 1, 1] - xy[:, 0, 1])) * 1e-8  # cm^2
    cen = xy.mean(axis=1)
    def f(code): return np.array([np.mean([val[a][ix[code]], val[b][ix[code]], val[c][ix[code]]]) for a, b, c in T])
    nodes = np.array([list(C[k]) + v for k, v in val.items()])
    return cen, area, f, nodes, ix

def analyse_snap(fn, xil, xir):
    cen, area, f, nodes, ix = read_full(fn)
    x, y = cen[:, 0], cen[:, 1]; film = y <= 0.0505
    G, U, E = f('105'), f('118'), f('103')
    xc = 0.5 * (xil + xir)
    out = {}
    for side, (lo, hi), (blo, bhi), (slo, shi) in (('L', (0.40, xc), (0.5, xil), (0.0, 0.5)), ('R', (xc, 0.90), (xir, 0.8), (xil, xir))):
        m = film & (x > lo) & (x < hi); mb = film & (x > blo) & (x < bhi); ms = film & (x > slo) & (x < shi)
        out[side] = dict(E=E[m].max(), Iii=Q * W * np.sum(G[m] * area[m]), Rb=Q * W * np.sum(U[mb] * area[mb]),
                         Rs=Q * W * np.sum(U[ms] * area[ms]))
    return out

def main(name='DDS_BASE_SNAP', maps=True):
    mp = snap_map(name); xil, xir = island(name)
    log = os.path.join(here, name + '.log_tr.log')
    M, v, Id, Is, It, Vt = load_cols(log)
    t = M[:, 0]
    deck = open(os.path.join(here, name + '.in')).read()
    tsave = [float(z) for z in re.search(r'tsave=([0-9e.+\- ]+)', deck).group(1).split()]
    rows = []
    for k, (d, vd) in sorted(mp.items()):
        fn = os.path.join(here, f'{name}_T_tr_{k}')
        if not os.path.exists(fn): continue
        j = int(np.argmin(np.abs(t - tsave[k - 1])))
        IeL, IeR = abs(Is[j]), abs(It[j]) + abs(Is[j])
        r = analyse_snap(fn, xil, xir)
        rows.append((k, d, vd, r['L']['E'], r['L']['Iii'], r['L']['Rb'], r['L']['Rs'], IeL, r['L']['Iii'] / max(IeL, 1e-30),
                     r['R']['E'], r['R']['Iii'], r['R']['Rb'], r['R']['Rs'], IeR, r['R']['Iii'] / max(IeR, 1e-30)))
    hdr = '# k sweep Vd | LEFT: E_peak(V/cm) I_ii(A) R_body(A) R_source(A) I_e(A) M-1 | RIGHT: E_peak I_ii R_body R_island I_e M-1   (mech2_ddsplit.py)\n'
    with open(os.path.join(here, f'mech2_{name}.dat'), 'w') as fo:
        fo.write(hdr)
        for r in rows: fo.write('%2d %-4s %5.2f ' % r[:3] + ' '.join('%10.3e' % z for z in r[3:]) + '\n')
    fig, axs = plt.subplots(2, 3, figsize=(18, 9))
    for row, (side, off, col, title) in enumerate((('L', 3, '#8856a7', 'LEFT STL (source = n+ source, drain = island)'),
                                                  ('R', 9, '#2ca25f', 'RIGHT STL (source = island, drain = n+ drain)'))):
        for d, mk in (('up', 'o-'), ('down', 's--')):
            R = [r for r in rows if r[1] == d]
            if not R: continue
            vv = [r[2] for r in R]
            a = axs[row, 0]; a.semilogy(vv, [r[off + 1] for r in R], mk, color='r', label=f'I_ii impact holes ({d})')
            a.semilogy(vv, [r[off + 2] for r in R], mk, color='b', label=f'R in body ({d})'); a.semilogy(vv, [r[off + 3] for r in R], mk, color='c', label=f'R in its n+ source ({d})')
            axs[row, 1].semilogy(vv, [r[off + 5] for r in R], mk, color=col, label=f'M-1 = I_ii / I_e ({d})')
            axs[row, 2].plot(vv, [r[off] / 1e5 for r in R], mk, color=col, label=f'peak E ({d})')
        axs[row, 0].set_ylabel('hole current (A)'); axs[row, 0].set_title(title + ': hole balance', fontsize=10)
        axs[row, 1].set_title('multiplication M-1', fontsize=10); axs[row, 2].set_title('peak field (1e5 V/cm)', fontsize=10)
        for a in axs[row]: a.grid(alpha=.3); a.legend(fontsize=7); a.set_xlabel('Vd (V)')
    fig.suptitle(f'{name}: why each STL latches - impact-ionization hole generation vs recombination sinks  '
                 f'[data: novel/1007_ddsplit/{name}_T_tr_N (.str) + {name}.log_tr.log · code: 1007_ddsplit/mech2_ddsplit.py]', fontsize=10)
    fig.tight_layout(); fig.savefig(os.path.join(here, 'fig', f'mech2_{name}.png'), dpi=110); plt.close(fig)
    if maps:   # G_ii and recombination maps at a few snapshots (first 3 up states around each latch + 2 down states)
        pick = [k for k, (d, vd) in sorted(mp.items()) if os.path.exists(os.path.join(here, f'{name}_T_tr_{k}'))]
        sel = pick[::max(1, len(pick) // 6)][:6]
        fig, axs = plt.subplots(len(sel), 2, figsize=(14, 1.9 * len(sel) + 0.8), squeeze=False)
        for i, k in enumerate(sel):
            cen, area, f, nodes, ix = read_full(os.path.join(here, f'{name}_T_tr_{k}'))
            m = (nodes[:, 1] <= 0.0505) & (nodes[:, 0] > 0.42) & (nodes[:, 0] < 0.86); nd = nodes[m]
            tri = mtri.Triangulation((nd[:, 0] - 0.5) * 1000, nd[:, 1] * 1000)
            for j, (code, lab, cm) in enumerate((('105', 'log10 impact generation (cm$^{-3}$s$^{-1}$)', 'inferno'), ('118', 'log10 recombination (cm$^{-3}$s$^{-1}$)', 'viridis'))):
                z = np.log10(np.maximum(nd[:, 2 + ix[code]], 1e10))
                c = axs[i, j].tricontourf(tri, z, levels=np.linspace(10, 30, 21), cmap=cm, extend='both')
                axs[i, j].set_ylim(50, 0); axs[i, j].set_ylabel(f'{mp[k][0]} {mp[k][1]:g} V\ny (nm)', fontsize=8)
                for xv in (0, (xil - 0.5) * 1000, (xir - 0.5) * 1000, 300): axs[i, j].axvline(xv, color='w', lw=.6, ls='--')
                if i == 0: axs[i, j].set_title(lab, fontsize=9)
                fig.colorbar(c, ax=axs[i, j], pad=0.01)
        axs[-1, 0].set_xlabel('x from source edge (nm)'); axs[-1, 1].set_xlabel('x from source edge (nm)')
        fig.suptitle(f'{name}: where holes are generated (impact ionization) and lost (recombination)  [Python render of novel/1007_ddsplit/{name}_T_tr_N]', fontsize=10)
        fig.tight_layout(); fig.savefig(os.path.join(here, 'fig', f'mech2_maps_{name}.png'), dpi=100); plt.close(fig)
    for r in rows:
        print('%2d %-4s %5.2f | L: E %.2e Iii %.2e Rb %.2e Rs %.2e Ie %.2e M-1 %.2e | R: E %.2e Iii %.2e Rb %.2e Risl %.2e Ie %.2e M-1 %.2e' % r)

if __name__ == '__main__':
    for n in (sys.argv[1:] or ['DDS_BASE_SNAP']): main(n)
