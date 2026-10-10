#!/usr/bin/env python3
"""Figures for paper/main.tex (IEEE TED style). Every figure is drawn from simulation outputs in this repository;
the data path of each figure is written in its LaTeX caption. Run from anywhere: python3 paper/make_figs.py"""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.tri as mtri
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'tools')); sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
from plog import load
from analyze_ddsplit import load_cols
OUT = os.path.join(R, 'paper', 'fig'); os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Nimbus Roman', 'Nimbus Roman No9 L', 'Times New Roman', 'DejaVu Serif'],
                     'mathtext.fontset': 'stix', 'font.size': 8, 'axes.labelsize': 8, 'axes.titlesize': 8, 'legend.fontsize': 6.5,
                     'xtick.labelsize': 7, 'ytick.labelsize': 7, 'lines.linewidth': 1.1, 'axes.linewidth': 0.6, 'savefig.bbox': 'tight',
                     'savefig.pad_inches': 0.02})
P = lambda *a: os.path.join(R, *a)
C1, C2 = 3.5, 7.16          # IEEE single / double column width (in)
RED, BLUE, GRN, PUR, GRY = '#c0392b', '#2c7fb8', '#2ca25f', '#8856a7', '0.45'

def save(fig, name):
    fig.tight_layout(pad=0.3)
    fig.savefig(os.path.join(OUT, name + '.pdf')); fig.savefig(os.path.join(OUT, name + '.png'), dpi=200); plt.close(fig); print('ok', name)

def tag(ax, s): ax.text(0.02, 0.97, s, transform=ax.transAxes, va='top', ha='left', fontsize=8, fontweight='bold')

def mm(name):   # MixedMode split log -> applied Vd, Id, Is, Itap, Vtap ; up/down masks
    M, v, Id, Is, It, Vt = load_cols(P('1007_ddsplit', f'{name}.log_tr.log')); k = int(np.argmax(v))
    up = np.arange(len(v)) <= k
    return v, np.abs(Id), np.abs(Is), np.abs(It), Vt, up

# ---------------- Fig. 3: why the obvious structures give one latch ----------------
fig, ax = plt.subplots(1, 3, figsize=(C2, 2.1))
d = load(P('0928', 'ISL_W30_L3_R7.log')); v, i = d[:, 11], np.abs(d[:, 12]); k = int(np.argmax(v))
ax[0].semilogy(v[:k + 1], i[:k + 1], color=RED, label='up'); ax[0].semilogy(v[k:], i[k:], '--', color=BLUE, label='down')
ax[0].set_title('floating n$^+$ island'); tag(ax[0], '(a)')
d = load(P('1001', 'tap', 'TAPT_ISL_W30_L3_R7_R3e5_VGm0p2.log')); o = 1; v = d[:, o + 11]; k = int(np.argmax(v)); up = np.arange(len(v)) <= k
for arr, c, lab in ((np.abs(d[:, o + 12]), 'k', '$I_D$'), (np.abs(d[:, o + 17]), GRN, '$I_{tap}$ (right STL)'), (np.abs(d[:, o + 7]), PUR, '$I_S$ (left STL)')):
    ax[1].semilogy(v[up], arr[up], color=c, label=lab)
ax[1].set_title('tapped island ($R_{tap}$ = 600 k$\\Omega$)'); tag(ax[1], '(b)')
e = np.loadtxt(P('1001', 'tap', 'TAPT_ISL_W30LK_L3_R7_R1e4_UD6S_VGm0p2_extract.dat')); v = e[:, 1]; k = int(np.argmax(v)); up = np.arange(len(v)) <= k
for col, c, lab in ((2, 'k', '$I_D$'), (4, GRN, '$I_{tap}$'), (3, PUR, '$I_S$')):
    ax[2].semilogy(v[up], np.abs(e[up, col]), color=c, label=lab)
ax[2].set_title('+ lifetime-killed island (10 k$\\Omega$)'); tag(ax[2], '(c)')
for a in ax:
    a.set_xlim(0, 6); a.set_ylim(1e-17, 1e-2); a.set_xlabel('$V_D$ (V)'); a.grid(alpha=.25); a.legend(loc='lower right')
ax[0].set_ylabel('current (A)')
save(fig, 'fig3_evolution')

# ---------------- Fig. 4: standalone left STL ----------------
fig, ax = plt.subplots(1, 2, figsize=(C2, 2.1))
cols = {'3e17': '0.2', '5e17': BLUE, '6e17': GRN, '7e17': RED}
for dop, c in cols.items():
    d = load(P('1001', 'tap', f'LEFTONLY_L135_P{dop}_UD6S_VGm0p2.log')); o = 1; v = d[:, o + 11]; k = int(np.argmax(v))
    m = v[:k + 1] <= 3.1
    ax[0].semilogy(v[:k + 1][m], np.abs(d[:k + 1, o + 7])[m], color=c, label=dop.replace('e17', r'$\times10^{17}$'))
d = load(P('1001', 'tap', 'LEFTONLY_L135_P6e17_UD3_VGm0p2.log')); o = 1; v = d[:, o + 11]; k = int(np.argmax(v))
ax[0].semilogy(v[k:], np.abs(d[k:, o + 7]), '--', color=GRN, label=r'6$\times10^{17}$ down')
ax[0].set_title('hydrodynamic (hcte)'); tag(ax[0], '(a)')
for dop, c in (('3e17', '0.2'), ('4e17', '#e6a100'), ('5e17', BLUE), ('6e17', GRN), ('7e17', RED)):
    d = load(P('1001', 'tap', f'LEFTONLY_L135_P{dop}_DD_UP4_VGm0p2.log')); o = 1; v = d[:, o + 11]
    ax[1].semilogy(v, np.abs(d[:, o + 7]), color=c, label=dop.replace('e17', r'$\times10^{17}$'))
ax[1].axvspan(0, 1.12, color='0.85', alpha=.5); ax[1].text(0.3, 3e-15*30, '$V_D<E_g/q$', fontsize=6.5)
ax[1].set_title('drift-diffusion (DD)'); tag(ax[1], '(b)')
for a in ax:
    a.set_xlim(0, 3.1); a.set_ylim(1e-15, 1e-3); a.set_xlabel('$V_D$ (V)'); a.grid(alpha=.25); a.legend(loc='lower right', ncol=1)
ax[0].set_ylabel('$|I_S|$ (A)')
save(fig, 'fig4_left_stl')

# ---------------- Fig. 5: double latch (DD MixedMode, width 0.5 um) ----------------
v, Id, Is, It, Vt, up = mm('DDS_BASE')
fig, ax = plt.subplots(1, 3, figsize=(C2, 2.1))
ax[0].semilogy(v[up], Id[up], color=RED, label='up'); ax[0].semilogy(v[~up], Id[~up], '--', color=BLUE, label='down')
ax[0].set_ylabel('$|I_D|$ (A)'); ax[0].legend(loc='lower right'); tag(ax[0], '(a)')
for x, y, s in ((2.251, 1e-10, 'I$\\rightarrow$II'), (3.300, 1e-6, 'II$\\rightarrow$III')): ax[0].annotate(s, (x, y), xytext=(x - 1.2, y * 30), fontsize=6.5, arrowprops=dict(arrowstyle='->', lw=0.6))
ax[1].semilogy(v[up], It[up], color=GRN, label='$I_{tap}$: right STL'); ax[1].semilogy(v[up], Is[up], color=PUR, label='$I_S$: left STL')
ax[1].set_ylabel('current (A), up sweep'); ax[1].legend(loc='lower right'); tag(ax[1], '(b)')
ax[2].plot(v[up], Vt[up], color=RED, label='up'); ax[2].plot(v[~up], Vt[~up], '--', color=BLUE, label='down')
ax[2].axhline(1.778, color=PUR, lw=0.7, ls='-.'); ax[2].text(0.15, 1.86, 'left STL alone: $V_{LU}$ (DD)', fontsize=6, color=PUR)
ax[2].set_ylabel('$V_{tap}=I_{tap}R_{tap}$ (V)'); ax[2].set_ylim(-0.1, 2.3); ax[2].legend(loc='lower right'); tag(ax[2], '(c)')
for a in ax[:2]: a.set_ylim(1e-16, 1e-3)
for a in ax: a.set_xlim(0, 4); a.set_xlabel('$V_D$ (V)'); a.grid(alpha=.25)
save(fig, 'fig5_double_latch')

# ---------------- Fig. 6: mechanism (BASE_SNAP) ----------------
m1 = np.genfromtxt(P('1007_ddsplit', 'mech_DDS_BASE_SNAP.dat'), dtype=None, encoding=None)
m2 = np.genfromtxt(P('1007_ddsplit', 'mech2_DDS_BASE_SNAP.dat'), dtype=None, encoding=None)
fig, ax = plt.subplots(1, 3, figsize=(C2, 2.15))
for sw, mk in (('up', 'o-'), ('down', 's--')):
    a = [r for r in m1 if r[1] == sw]; vv = [r[2] for r in a]
    ax[0].plot(vv, [r[3] for r in a], mk, ms=2.5, color=PUR, label=f'left, {sw}'); ax[0].plot(vv, [r[5] for r in a], mk, ms=2.5, color=GRN, label=f'right, {sw}')
ax[0].set_ylabel('source$\\rightarrow$body barrier (eV)'); ax[0].legend(loc='lower left', fontsize=5.5); tag(ax[0], '(a)')
for side, off, c in (('left', 3, PUR), ('right', 9, GRN)):
    a = [r for r in m2 if r[1] == 'up']; vv = [r[2] for r in a]
    ax[1].semilogy(vv, [max(r[off + 1], 1e-22) for r in a], '-', color=c, label=f'$I_{{ii}}$ {side}')
    ax[1].semilogy(vv, [max(r[off + 2] + r[off + 3], 1e-22) for r in a], ':', color=c, label=f'recomb. {side}')
ax[1].set_ylim(1e-20, 1e-4); ax[1].set_ylabel('hole current (A), up sweep'); ax[1].legend(loc='lower right', fontsize=5.5); tag(ax[1], '(b)')
from mech2_ddsplit import read_full
cen, area, f, nodes, ix = read_full(P('1007_ddsplit', 'DDS_BASE_SNAP_T_tr_10'))
m = (nodes[:, 1] <= 0.0505) & (nodes[:, 0] > 0.45) & (nodes[:, 0] < 0.85); nd = nodes[m]
tri = mtri.Triangulation((nd[:, 0] - 0.5) * 1000, nd[:, 1] * 1000)
cs = ax[2].tricontourf(tri, np.log10(np.maximum(nd[:, 2 + ix['105']], 1e10)), levels=np.linspace(14, 30, 17), cmap='inferno', extend='both')
for xv in (0, 135, 165, 300): ax[2].axvline(xv, color='w', lw=.5, ls='--')
ax[2].set_ylim(50, 0); ax[2].set_ylabel('$y$ (nm)'); ax[2].set_xlabel('$x$ (nm)'); ax[2].text(0.03, 0.95, '(c)', transform=ax[2].transAxes, va='top', color='w', fontweight='bold')
cb = fig.colorbar(cs, ax=ax[2], pad=0.02); cb.set_label('log$_{10}G_{ii}$ (cm$^{-3}$s$^{-1}$)', fontsize=6.5); cb.ax.tick_params(labelsize=6)
for a in ax[:2]: a.set_xlabel('$V_D$ (V)'); a.grid(alpha=.25)
save(fig, 'fig6_mechanism')

# ---------------- Fig. 7: abrupt turn-off by Si lifetime ----------------
fig, ax = plt.subplots(1, 2, figsize=(C2, 2.1))
for name, c, lab in (('DDS_BASE', '0.2', '$10^{-7}$ s'), ('DDS_TE2em8', BLUE, '$2\\times10^{-8}$ s'), ('DDS_TE1em8', GRN, '$10^{-8}$ s'), ('DDS_TE5em9', RED, '$5\\times10^{-9}$ s')):
    v, Id, Is, It, Vt, up = mm(name)
    ax[0].semilogy(v[up], Id[up], color=c, label=lab); ax[0].semilogy(v[~up], Id[~up], '--', color=c, lw=0.8)
ax[0].set_xlim(1.5, 4.6); ax[0].set_ylim(1e-13, 1e-2); ax[0].set_xlabel('$V_D$ (V)'); ax[0].set_ylabel('$|I_D|$ (A)')
ax[0].legend(loc='lower right', title='Si lifetime', title_fontsize=6.5); tag(ax[0], '(a)')
for name, c, lab in (('DDS_BASE_SNAP', '0.2', '$10^{-7}$ s'), ('DDS_TE8_SNAP', GRN, '$10^{-8}$ s')):
    a = np.genfromtxt(P('1007_ddsplit', f'mech2_{name}.dat'), dtype=None, encoding=None)
    rr = [r for r in a if r[1] == 'down' and r[7] > 1e-9]
    ax[1].semilogx([r[7] for r in rr], [100 * (r[5] + r[6]) / r[4] for r in rr], 'o-', ms=3, color=c, label=lab)
ax[1].set_xlabel('left-STL electron current (A), down sweep'); ax[1].set_ylabel('impact holes lost to recomb. (%)')
ax[1].legend(loc='upper right', title='Si lifetime', title_fontsize=6.5); tag(ax[1], '(b)')
for a in ax: a.grid(alpha=.25)
save(fig, 'fig7_turnoff')

# ---------------- Fig. 8: design knobs (DD splits) ----------------
S = {l.split()[0]: [float(z) for z in l.split()[2:9]] for l in open(P('1007_ddsplit', 'ddsplit_summary.dat')) if not l.startswith('#')}
groups = [('$R_{tap}$ ($\\Omega$)', True, [('R3e5', 3e5), ('R1e6', 1e6), ('R3e6', 3e6), ('BASE', 1e7), ('R3e7', 3e7), ('R1e8', 1e8), ('R3e8', 3e8)]),
          ('$N_{A,L}$ (cm$^{-3}$)', False, [('NL4e17', 4e17), ('NL5e17', 5e17), ('NL5p5e17', 5.5e17), ('BASE', 6e17), ('NL6p5e17', 6.5e17), ('NL7e17', 7e17), ('NL8e17', 8e17)]),
          ('$N_{A,R}$ (cm$^{-3}$)', False, [('NR5e17', 5e17), ('NR6e17', 6e17), ('NR6p5e17', 6.5e17), ('BASE', 7e17), ('NR7p5e17', 7.5e17), ('NR8e17', 8e17), ('NR9e17', 9e17), ('NR1e18', 1e18)]),
          ('$V_G$ (V)', False, [('VGm1p0', -1.0), ('VGm0p5', -0.5), ('VGm0p3', -0.3), ('BASE', -0.2), ('VGm0p1', -0.1), ('VG0', 0.0), ('VGp0p2', 0.2)]),
          ('island lifetime (s)', True, [('TAU1em13', 1e-13), ('BASE', 1e-12), ('TAU1em11', 1e-11), ('TAU1em10', 1e-10), ('TAU1em9', 1e-9)]),
          ('island position (% of $L_g$)', False, [('XS40', 40), ('BASE', 50), ('XS60', 60)])]
fig, axs = plt.subplots(2, 3, figsize=(C2, 3.9))
for a, (xl, lg, items) in zip(axs.flat, groups):
    pts = [(x, S['DDS_' + t]) for t, x in items if 'DDS_' + t in S]
    x = np.array([p[0] for p in pts])
    a.plot(x, [p[1][0] for p in pts], 'o-', ms=3, color=GRN, label='1st ON'); a.plot(x, [p[1][5] for p in pts], 'o--', ms=3, mfc='w', color=GRN, label='1st OFF')
    a.plot(x, [p[1][2] for p in pts], 's-', ms=3, color=PUR, label='2nd ON'); a.plot(x, [p[1][4] for p in pts], 's--', ms=3, mfc='w', color=PUR, label='2nd OFF')
    if lg: a.set_xscale('log')
    a.set_xlabel(xl); a.set_ylim(0.6, 4.2); a.grid(alpha=.25)
axs[0, 0].legend(loc='lower left', fontsize=5.5); axs[0, 0].set_ylabel('$V_D$ (V)'); axs[1, 0].set_ylabel('$V_D$ (V)')
for a, s in zip(axs.flat, '(a) (b) (c) (d) (e) (f)'.split()): tag(a, s)
save(fig, 'fig8_knobs')

# ---------------- Fig. 9: two separated abrupt rectangles ----------------
paper = [n for n in ('DDS_TE8_XS60_NR8e17_RD1e5', 'DDS_TE5em9_XS60_NR8e17_RD1e5') if os.path.exists(P('1007_ddsplit', n + '.queue')) and 'end' in open(P('1007_ddsplit', n + '.queue')).read()]
sets = [('(a) island position', [('DDS_BASE', '50 %, $\\tau$=1e-7 s', '0.5'), ('DDS_XS60', '60 %, 1e-7 s', BLUE), ('DDS_TE8_XS60', '60 %, 1e-8 s', RED)]),
        ('(b) right-body doping', [('DDS_TE8_XS60', '7e17', RED), ('DDS_TE8_XS60_NR8e17', '8e17', GRN), ('DDS_TE8_XS60_NR1e18', '1e18', BLUE)]),
        ('(c) drain series resistor', [('DDS_TE8_XS60', '0', RED), ('DDS_TE8_XS60_RD1e5', '100 k$\\Omega$', GRN), ('DDS_TE8_XS60_RD1e6', '1 M$\\Omega$', BLUE)]),
        ('(d) combined device', [(n, lab, c) for n, lab, c in (('DDS_TE8_XS60_NR8e17_RD1e5', '$\\tau$=1e-8 s', RED), ('DDS_TE5em9_XS60_NR8e17_RD1e5', '$\\tau$=5e-9 s', BLUE)) if n in paper])]
fig, axs = plt.subplots(2, 2, figsize=(C2, 3.6))
for a, (title, items) in zip(axs.flat, sets):
    for n, lab, c in items:
        v, Id, Is, It, Vt, up = mm(n)
        a.semilogy(v[up], Id[up], color=c, label=lab); a.semilogy(v[~up], Id[~up], '--', color=c, lw=0.8)
    a.set_xlim(0, 6); a.set_ylim(1e-14, 1e-2); a.grid(alpha=.25); a.set_xlabel('applied $V_D$ (V)'); a.set_title(title, fontsize=7.5)
    if items: a.legend(loc='lower right', fontsize=5.5)
axs[0, 0].set_ylabel('$|I_D|$ (A)'); axs[1, 0].set_ylabel('$|I_D|$ (A)')
save(fig, 'fig9_rectangles')

# ---------------- Fig. 10: hcte limitation ----------------
runs = [('$R_{tap}$=1 M$\\Omega$', 5.284), ('+ coupled Newton', 5.284), ('+ 1-nm mesh', 5.033), ('left 6e17', 5.201), ('$R_{tap}$=10 M$\\Omega$', 4.422),
        ('MixedMode', 4.422), ('+ T tolerance', 4.422), ('+ graded drain', 3.607), ('$R_{tap}$=30 M$\\Omega$', 4.167), ('$R_{tap}$=100 M$\\Omega$', 4.084)]
fig, a = plt.subplots(figsize=(C1, 2.0)); y = np.arange(len(runs))[::-1]
a.barh(y, [r[1] for r in runs], color=RED, alpha=.8, height=0.6); a.set_yticks(y); a.set_yticklabels([r[0] for r in runs], fontsize=6.5)
a.axvspan(5.6, 7.5, color=PUR, alpha=.15); a.text(5.65, len(runs) - 1.2, 'needed for\n2nd latch', fontsize=6, color=PUR)
a.set_xlim(0, 7.5); a.set_xlabel('$V_D$ where the hcte run stops (V)'); a.grid(alpha=.25, axis='x')
save(fig, 'fig10_hcte')
