#!/usr/bin/env python3
"""Latch mechanism from the .str snapshots of one DD split (default DDS_BASE).

For every snapshot: electrostatic potential and hole density along y = 25 nm, and two numbers per STL:
  barrier = psi(source side) - min psi(body)   (electron barrier from the STL's source into its body, eV)
  p_body  = mean hole density in the body (cm^-3)
Left STL : source = n+ source (x < 0.50 um), body x = 0.50 .. XiL
Right STL: source = n+ island (x = XiL .. XiR), body x = XiR .. 0.80
Writes fig/mech_<name>.png and mech_<name>.dat.
Snapshot -> Vd mapping is read from the deck header line '# Sweep ... Snapshots (..): up a, b, .. / down c, d, ..'.
"""
import sys, os, re, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, '..', '0927', 'ebd'))
from strcut import read, cut

def snap_map(name):
    hdr = open(os.path.join(here, name + '.in')).read().split('\n')[2]
    up, dn = re.search(r'up ([^/]+) / down (.+?) V', hdr).groups()
    lst = [('up', float(x)) for x in up.split(',')] + [('down', float(x)) for x in dn.split(',')]
    return {i + 1: v for i, v in enumerate(lst)}

def island(name):
    s = open(os.path.join(here, name + '.in')).read()
    w = float(re.search(r'^set Wisl = ([0-9.]+)', s, re.M).group(1))
    xs = re.search(r'^set Xsplit = \$Lsd\+\$Lg\*([0-9.]+)', s, re.M)
    xc = 0.5 + 0.3 * (float(xs.group(1)) if xs else 0.5)
    return xc - w / 2, xc + w / 2

def metrics(fn, xil, xir):
    a = read(fn); yv, b = cut(a, 0.025, 0.30, 1.00)
    x, psi, p = b[:, 0], b[:, 5], b[:, 6]
    def stl(src, body):
        ps = np.mean(psi[(x > src[0]) & (x < src[1])]); mb = (x > body[0]) & (x < body[1])
        return ps - psi[mb].min(), np.mean(p[mb])
    bl, pl = stl((0.40, 0.48), (0.505, xil - 0.003))
    br, pr = stl((xil + 0.003, xir - 0.003), (xir + 0.003, 0.795))
    return x, psi, p, bl, pl, br, pr

def main(name='DDS_BASE'):
    mp = snap_map(name); xil, xir = island(name)
    rows, curves = [], []
    for k, (d, v) in sorted(mp.items()):
        fn = os.path.join(here, f'{name}_T_tr_{k}')
        if not os.path.exists(fn): continue
        x, psi, p, bl, pl, br, pr = metrics(fn, xil, xir)
        rows.append((k, d, v, bl, pl, br, pr)); curves.append((d, v, x, psi, p))
    with open(os.path.join(here, f'mech_{name}.dat'), 'w') as fo:
        fo.write(f'# {name}: snapshot sweep Vd barrier_left_eV p_left_cm3 barrier_right_eV p_right_cm3  (mech_ddsplit.py, y = 25 nm)\n')
        for r in rows: fo.write('%2d %-4s %5.2f %7.3f %10.3e %7.3f %10.3e\n' % r)
    fig = plt.figure(figsize=(16, 9)); gs = fig.add_gridspec(2, 3)
    a0 = fig.add_subplot(gs[0, 0:2]); a1 = fig.add_subplot(gs[1, 0:2]); a2 = fig.add_subplot(gs[0, 2]); a3 = fig.add_subplot(gs[1, 2])
    cu = plt.cm.Reds(np.linspace(0.35, 1, sum(1 for c in curves if c[0] == 'up')))
    cd = plt.cm.Blues(np.linspace(0.35, 1, sum(1 for c in curves if c[0] == 'down')))
    iu = idn = 0
    for d, v, x, psi, p in curves:
        if d == 'up': c = cu[iu]; iu += 1; ls = '-'
        else: c = cd[idn]; idn += 1; ls = '--'
        xx = (x - 0.5) * 1000
        a0.plot(xx, psi, ls, color=c, lw=1.2, label=f'{d} {v:g} V'); a1.semilogy(xx, np.maximum(p, 1), ls, color=c, lw=1.2)
    for A in (a0, a1):
        A.axvspan((xil - 0.5) * 1000, (xir - 0.5) * 1000, color='orange', alpha=.15); A.axvline(0, color='k', lw=.5); A.axvline(300, color='k', lw=.5)
        A.set_xlim(-60, 360); A.grid(alpha=.3)
    a0.set_ylabel('potential psi (V), y = 25 nm'); a0.legend(fontsize=7, ncol=3); a0.set_title(f'{name}: potential and hole density along the channel (shaded = n+ island)', fontsize=10)
    a1.set_ylabel('hole density (cm$^{-3}$)'); a1.set_ylim(1e6, 1e20); a1.set_xlabel('x from source edge (nm)   left body | island | right body')
    for d, mk in (('up', 'o-'), ('down', 's--')):
        R = [r for r in rows if r[1] == d]
        if not R: continue
        v = [r[2] for r in R]
        a2.plot(v, [r[3] for r in R], mk, color='#8856a7', label=f'left STL ({d})'); a2.plot(v, [r[5] for r in R], mk, color='#2ca25f', label=f'right STL ({d})')
        a3.semilogy(v, [r[4] for r in R], mk, color='#8856a7', label=f'left body ({d})'); a3.semilogy(v, [r[6] for r in R], mk, color='#2ca25f', label=f'right body ({d})')
    a2.set_ylabel('electron barrier source->body (eV)'); a2.set_xlabel('Vd (V)'); a2.grid(alpha=.3); a2.legend(fontsize=7)
    a3.set_ylabel('mean hole density in body (cm$^{-3}$)'); a3.set_xlabel('Vd (V)'); a3.grid(alpha=.3); a3.legend(fontsize=7)
    a2.set_title('latch = barrier collapses as the body fills with holes', fontsize=10)
    fig.text(0.01, 0.005, f'data: novel/1007_ddsplit/{name}_T_tr_N (MixedMode .str snapshots) · code: 1007_ddsplit/mech_ddsplit.py (strcut.read)', fontsize=8, color='0.4')
    fig.tight_layout(); os.makedirs(os.path.join(here, 'fig'), exist_ok=True)
    fig.savefig(os.path.join(here, 'fig', f'mech_{name}.png'), dpi=115); plt.close(fig)
    for r in rows: print('%2d %-4s %5.2f  left: barrier %.3f eV p %.2e | right: barrier %.3f eV p %.2e' % r)

if __name__ == '__main__':
    for n in (sys.argv[1:] or ['DDS_BASE']): main(n)
