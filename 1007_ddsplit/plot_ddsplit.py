#!/usr/bin/env python3
"""Plots for the DD split study: ddsplit_trends.png (latch voltages / jump sizes per variable) and
ddsplit_idvd_<var>.png (Id-Vd overlays). Data: DDS_*.log_tr.log via analyze_ddsplit.analyse()."""
import sys, os, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); sys.path.insert(0, os.path.join(here, '..', 'tools'))
from analyze_ddsplit import analyse, load_cols
from plog import load
OUT = os.path.join(here, 'fig'); os.makedirs(OUT, exist_ok=True)
BASE = dict(R=1e7, NL=6e17, NR=7e17, VG=-0.2, TAU=1e-12, WISL=30, XS=50, TSI=50, RATE=0.7, RD=1e3, TE=1e-7, TE8_NL=6e17, TE8_NR=7e17, TE8_R=1e7, TE8_VG=-0.2)
GROUPS = {
 'R':   ('Rtap (Ohm)', True,  [('R3e5', 3e5), ('R1e6', 1e6), ('R3e6', 3e6), ('BASE', 1e7), ('R3e7', 3e7), ('R1e8', 1e8), ('R3e8', 3e8)]),
 'NL':  ('left body doping (cm$^{-3}$)', False, [('NL4e17', 4e17), ('NL5e17', 5e17), ('NL5p5e17', 5.5e17), ('BASE', 6e17), ('NL6p5e17', 6.5e17), ('NL7e17', 7e17), ('NL8e17', 8e17)]),
 'NR':  ('right body doping (cm$^{-3}$)', False, [('NR5e17', 5e17), ('NR6e17', 6e17), ('NR6p5e17', 6.5e17), ('BASE', 7e17), ('NR7p5e17', 7.5e17), ('NR8e17', 8e17), ('NR9e17', 9e17), ('NR1e18', 1e18)]),
 'VG':  ('Vg (V)', False, [('VGm1p0', -1.0), ('VGm0p5', -0.5), ('VGm0p3', -0.3), ('BASE', -0.2), ('VGm0p1', -0.1), ('VG0', 0.0), ('VGp0p2', 0.2)]),
 'TAU': ('island lifetime (s)', True, [('TAU1em13', 1e-13), ('BASE', 1e-12), ('TAU1em11', 1e-11), ('TAU1em10', 1e-10), ('TAU1em9', 1e-9)]),
 'WISL': ('island width (nm)', False, [('WISL20', 20), ('BASE', 30), ('WISL50', 50), ('WISL100', 100)]),
 'XS':  ('island centre (% of Lg)', False, [('XS40', 40), ('BASE', 50), ('XS60', 60)]),
 'TSI': ('Si film thickness (nm)', False, [('TSI30', 30), ('BASE', 50), ('TSI70', 70)]),
 'RATE': ('ramp rate (V/ms)', True, [('RATE0p07', 0.07), ('BASE', 0.7), ('RATE7', 7.0)]),
 'RD':  ('drain series R (Ohm, base = 0 shown at 1e3)', True, [('BASE', 1e3), ('RD1e4', 1e4), ('RD3e4', 3e4), ('RD1e5', 1e5)]),
 'TE':  ('Si carrier lifetime (s)', True, [('TE1em9', 1e-9), ('TE5em9', 5e-9), ('TE1em8', 1e-8), ('TE2em8', 2e-8), ('TE5em8', 5e-8), ('BASE', 1e-7)]),
 'TE8_NL': ('left body doping, Si lifetime 1e-8 s', False, [('TE8_NL5e17', 5e17), ('TE8_NL5p5e17', 5.5e17), ('TE1em8', 6e17), ('TE8_NL6p5e17', 6.5e17)]),
 'TE8_NR': ('right body doping, Si lifetime 1e-8 s', False, [('TE8_NR5e17', 5e17), ('TE8_NR6e17', 6e17), ('TE1em8', 7e17)]),
 'TE8_R': ('Rtap (Ohm), Si lifetime 1e-8 s', True, [('TE8_R3e6', 3e6), ('TE1em8', 1e7), ('TE8_R3e7', 3e7)]),
 'TE8_VG': ('Vg (V), Si lifetime 1e-8 s', False, [('TE8_VG0', 0.0), ('TE8_VGm0p1', -0.1), ('TE1em8', -0.2)]),
}
res = {}
def get(tag):
    if tag in res: return res[tag]
    fn = os.path.join(here, f'DDS_{tag}.log_tr.log')
    q = os.path.join(here, f'DDS_{tag}.queue')
    if not (os.path.exists(fn) and os.path.exists(q) and 'end' in open(q).read()):
        res[tag] = None; return None
    eu, ed, vl, vr, vmax = analyse(fn)
    r = [e for e in eu if e[1] in ('right', 'both')]; l = [e for e in eu if e[1] in ('left', 'both')]
    res[tag] = dict(v1=r[0][0] if r else np.nan, d1=r[0][2] if r else np.nan, v2=l[0][0] if l else np.nan,
                    d2=l[0][2] if l else np.nan, off_l=vl, off_r=vr, merged=bool(r and l and abs(r[0][0] - l[0][0]) < 0.01))
    return res[tag]

fig, axs = plt.subplots(4, 4, figsize=(22, 17))
for ax in axs.flat: ax.axis('off')
for ax, (g, (xl, logx, items)) in zip(axs.flat, GROUPS.items()):
    ax.axis('on')
    pts = [(x, get(t)) for t, x in items if get(t)]
    if not pts: continue
    x = np.array([p[0] for p in pts]); R = [p[1] for p in pts]
    ax.plot(x, [r['v1'] for r in R], 'o-', color='#2ca25f', label='1st latch ON (right)')
    ax.plot(x, [r['off_r'] for r in R], 'o--', color='#2ca25f', mfc='w', label='1st OFF (down)')
    ax.plot(x, [r['v2'] for r in R], 's-', color='#8856a7', label='2nd latch ON (left)')
    ax.plot(x, [r['off_l'] for r in R], 's--', color='#8856a7', mfc='w', label='2nd OFF (down)')
    for xx, r in zip(x, R):
        if r['merged']: ax.annotate('merged', (xx, r['v2']), textcoords='offset points', xytext=(-10, 8), fontsize=8, color='r')
    bx = BASE[g]; ax.axvline(bx, color='0.6', lw=0.8, ls=':')
    if logx: ax.set_xscale('log')
    ax.set_xlabel(xl); ax.set_ylabel('Vd (V)'); ax.set_ylim(0.5, 4.5); ax.grid(alpha=.3)
    a2 = ax.twinx(); a2.bar(x if not logx else x, [r['d1'] for r in R], width=(x * 0.15 if logx else (x.max() - x.min() + 1e-30) * 0.03), alpha=.25, color='#2ca25f')
    a2.bar(x * (1.18 if logx else 1) + (0 if logx else (x.max() - x.min()) * 0.03), [r['d2'] for r in R], width=(x * 0.15 if logx else (x.max() - x.min() + 1e-30) * 0.03), alpha=.25, color='#8856a7')
    a2.set_ylim(0, 12); a2.set_ylabel('jump size (decades of Id), bars', fontsize=8)
    ax.set_title(f'{g}  (dotted = base)', fontsize=10)
    a2.axis('on')
axs.flat[0].legend(fontsize=8, loc='upper left')
fig.suptitle('DD MixedMode splits: latch voltages (lines) and jump sizes (bars), one variable at a time\n'
             'data: novel/1007_ddsplit/DDS_*.log_tr.log  ·  code: 1007_ddsplit/plot_ddsplit.py (events from analyze_ddsplit.py)', fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'ddsplit_trends.png'), dpi=120); plt.close(fig)

for g, (xl, logx, items) in GROUPS.items():
    done = [(t, x) for t, x in items if get(t)]
    if len(done) < 2: continue
    fig, ax = plt.subplots(figsize=(9, 5.2)); cm = plt.cm.viridis(np.linspace(0, 0.9, len(done)))
    for c, (t, x) in zip(cm, done):
        M, v, Id_, Is_, It_, Vt_ = load_cols(os.path.join(here, f'DDS_{t}.log_tr.log')); k = np.argmax(v)
        lab = f'{x:g}' + (' (base)' if t == 'BASE' else '')
        ax.semilogy(v[:k + 1], np.abs(Id_[:k + 1]), color=c, lw=1.8, label=lab)
        ax.semilogy(v[k:], np.abs(Id_[k:]), color=c, lw=1, ls='--')
    ax.set_xlim(0, 4.5); ax.set_ylim(1e-14, 1e-3); ax.grid(alpha=.3); ax.legend(fontsize=8, title=xl)
    ax.set_xlabel('Vd (V)'); ax.set_ylabel('|Id| (A)   solid up / dashed down')
    ax.set_title(f'DD split: {g}   [data: novel/1007_ddsplit/DDS_*.log_tr.log · code: plot_ddsplit.py]', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, f'ddsplit_idvd_{g}.png'), dpi=120); plt.close(fig)
from strstruct import draw
for g, items in (('WISL', [('WISL20', 'island 20 nm'), ('BASE', 'island 30 nm (base)'), ('WISL50', 'island 50 nm'), ('WISL100', 'island 100 nm')]),
                 ('XS', [('XS40', 'island at 40 % of Lg'), ('BASE', '50 % (base)'), ('XS60', '60 %')]),
                 ('TSI', [('TSI30', 'Tsi 30 nm'), ('BASE', 'Tsi 50 nm (base)'), ('TSI70', 'Tsi 70 nm')])):
    ok = [(t, d) for t, d in items if os.path.exists(os.path.join(here, f'DDS_{t}_INIT.str'))]
    if len(ok) < 2: continue
    fig, axs2 = plt.subplots(1, len(ok), figsize=(5.6 * len(ok), 4))
    for a, (t, d) in zip(axs2, ok):
        draw(os.path.join(here, f'DDS_{t}_INIT.str'), None, title=d, xlim=(0.45, 0.85), ylim=(0.29, -0.13), ax=a, note=f'source: 1007_ddsplit/DDS_{t}_INIT.str')
    fig.suptitle(f'DD split {g}: structures (net doping; rendered with tools/strstruct.py)', fontsize=10); fig.tight_layout()
    fig.savefig(os.path.join(OUT, f'ddsplit_struct_{g}.png'), dpi=110); plt.close(fig)
print('ok')
