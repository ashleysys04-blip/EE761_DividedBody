#!/usr/bin/env python3
"""Extended figures for the full paper (every experiment stage). Run after make_figs.py (same style).
Each figure's data files are listed in the LaTeX captions of paper/main.tex."""
import os, sys, glob, re, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.tri as mtri
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(R, 'paper')); sys.path.insert(0, os.path.join(R, 'tools')); sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
import make_figs as MF          # style, save(), tag(), mm(), colours
from plog import load
P, save, tag, mm = MF.P, MF.save, MF.tag, MF.mm
C1, C2 = MF.C1, MF.C2
cmap = plt.cm.viridis

def dev(fn):
    """Device-only ATLAS log -> dict: 't', 'V:<electrode>', 'I:<electrode>', '<probe name>' (columns found from the header)."""
    names, probes, codes = [], {}, None
    for l in open(fn):
        if l.startswith('f '): names = re.findall(r'"([^"]+)"', l)
        elif l.startswith('o '): p = l.split(); probes[3000 + int(p[1]) - 1] = p[2]
        elif l.startswith('p '): codes = [int(c) for c in l.split()[2:]]
        elif l.startswith('d '): break
    d = load(fn); out = {}
    for i, c in enumerate(codes):
        if c == 61: out['t'] = d[:, i]
        elif 2 <= c <= 1 + len(names): out['Vapp:' + names[c - 2]] = d[:, i]
        elif 601 <= c <= 600 + len(names): out['V:' + names[c - 601]] = d[:, i]
        elif 20 <= c <= 19 + len(names): out['I:' + names[c - 20]] = d[:, i]
        elif c in probes: out[probes[c]] = d[:, i]
    return out

def updown(v):
    k = int(np.argmax(v)); up = np.arange(len(v)) <= k
    return up, ~up

def overlay(ax, items, key='I:drain', xkey='V:drain', down=True, xlim=None, ylim=(1e-15, 1e-2), lw=1.1):
    cs = cmap(np.linspace(0, 0.9, max(len(items), 2)))
    for c, (fn, lab) in zip(cs, items):
        if not os.path.exists(P(fn)): continue
        d = dev(P(fn)); v, i = d[xkey], np.abs(d[key]); up, dn = updown(v)
        ax.semilogy(v[up], i[up], color=c, lw=lw, label=lab)
        if down and dn.sum() > 2: ax.semilogy(v[dn], i[dn], '--', color=c, lw=lw * 0.7)
    ax.set_ylim(*ylim); ax.grid(alpha=.25); ax.set_xlabel('$V_D$ (V)')
    if xlim: ax.set_xlim(*xlim)

def mm_overlay(ax, items, xlim=(0, 6), ylim=(1e-14, 1e-2)):
    cs = cmap(np.linspace(0, 0.9, max(len(items), 2)))
    for c, (n, lab) in zip(cs, items):
        q = P('1007_ddsplit', n + '.queue')
        if not (os.path.exists(q) and 'end' in open(q).read()): continue
        v, Id, Is, It, Vt, up = mm(n); bold = 'ref' in lab
        ax.semilogy(v[up], Id[up], color=c, lw=1.6 if bold else 1.0, label=lab)
        ax.semilogy(v[~up], Id[~up], '--', color=c, lw=0.7)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.grid(alpha=.25); ax.set_xlabel('$V_D$ (V)')

# ---------------- A. doping split (0921, 0927) ----------------
fig, ax = plt.subplots(1, 3, figsize=(C2, 2.15))
overlay(ax[0], [('0921/STL_NB5p0_localfine.log', 'uniform 5.0e17')] + [(f'0921/SPLIT_{s}.log', s.replace('_X50', '').replace('p', '.')) for s in
               ('L4p8_R5p2_X50', 'L5p0_R5p2_X50', 'L5p0_R5p4_X50', 'L5p2_R5p0_X50', 'L5p4_R5p0_X50')], xlim=(2.5, 4.6))
ax[0].set_title('small split (L/R $\\times10^{17}$)'); ax[0].legend(fontsize=5.3, loc='lower right'); tag(ax[0], '(a)')
big = [('0927/BIG_L3_R7_X50.log', 'L3 R7 (drain hi)'), ('0927_bigsplit/BIG_L2_R8_X50.log', 'L2 R8'), ('0927_bigsplit/BIG_L1_R10_X50.log', 'L1 R10'),
       ('0927/BIG_L7_R3_X50.log', 'L7 R3 (source hi)'), ('0927/BIG_L8_R2_X50.log', 'L8 R2'), ('0927/BIG_L10_R1_X50.log', 'L10 R1')]
overlay(ax[1], big, xlim=(2, 7)); ax[1].set_title('large split ($\\times10^{17}$)'); ax[1].legend(fontsize=5.3, loc='lower right'); tag(ax[1], '(b)')
# V_LU / V_LD from the logs (first / last |Id| > 1e-8 A on up / down)
rows = []
for fn, lab in [('0921/STL_NB5p0_localfine.log', 'uniform')] + big:
    d = dev(P(fn)); v, i = d['V:drain'], np.abs(d['I:drain']); up, dn = updown(v)
    on = np.where(up & (i > 1e-8))[0]; off = np.where(dn & (i > 1e-8))[0]
    vlu = v[on[0]] if len(on) else np.nan
    rows.append((lab, vlu, v[off[-1]] if (len(off) and not np.isnan(vlu)) else np.nan, v.max()))
x = np.arange(len(rows))
ax[2].plot(x, [r[1] for r in rows], 'o-', color=MF.RED, label='$V_{LU}$'); ax[2].plot(x, [r[2] for r in rows], 's--', color=MF.BLUE, label='$V_{LD}$')
for xi, r in zip(x, rows):
    if np.isnan(r[1]): ax[2].text(xi, 3.4, 'no latch\n$\\leq$%.1f V' % r[3], ha='center', fontsize=4.8, rotation=90)
ax[2].set_xticks(x); ax[2].set_xticklabels([r[0].split(' (')[0] for r in rows], rotation=60, fontsize=5.5); ax[2].set_ylabel('V (V)'); ax[2].grid(alpha=.25)
ax[2].legend(loc='center left'); ax[2].set_title('latch window'); ax[2].text(0.9, 0.97, '(c)', transform=ax[2].transAxes, va='top', fontsize=8, fontweight='bold')
ax[0].set_ylabel('$|I_D|$ (A)'); save(fig, 'figA_doping_split')
open(os.path.join(MF.OUT, 'figA_table.txt'), 'w').write('\n'.join('%s %.3f %.3f %.2f' % r for r in rows))

# ---------------- B. other single-body attempts ----------------
fig, ax = plt.subplots(1, 4, figsize=(C2, 2.0))
overlay(ax[0], [(f, os.path.basename(f)[:-4].replace('_L5p0_R5p2', '')) for f in sorted(glob.glob(P('0921', 'B*_W*_L5p0_R5p2.log')))], xlim=(2, 7))
ax[0].set_title('oxide notch + bridge'); tag(ax[0], '(a)')
overlay(ax[1], [(f, os.path.basename(f)[4:-4]) for f in sorted(glob.glob(P('0928', 'TSI_*.log')))], xlim=(2, 7)); ax[1].set_title('$T_{si}$ split (L/R nm)'); tag(ax[1], '(b)')
overlay(ax[2], [(f, os.path.basename(f)[3:-4]) for f in sorted(glob.glob(P('0929', 'splitgate', 'SG_*.log')))], xlim=(2, 7)); ax[2].set_title('split gate ($V_{G2}$)'); tag(ax[2], '(c)')
overlay(ax[3], [(f, os.path.basename(f)[5:-4]) for f in sorted(glob.glob(P('1001', 'nnpn', 'NNPN_*.log')))], xlim=(1, 7)); ax[3].set_title('n$^+$/n$^-$/p/n$^+$'); tag(ax[3], '(d)')
for a in ax: a.legend(fontsize=4.6, loc='lower right')
ax[0].set_ylabel('$|I_D|$ (A)'); save(fig, 'figB_single_body')

# ---------------- C. Id-Vg ----------------
fig, ax = plt.subplots(1, 2, figsize=(C1, 1.9))
for c, s in zip(cmap(np.linspace(0, .9, 4)), ('L3_R7', 'L7_R3', 'L8_R2', 'L2_R8')):
    for vd, ls in (('vd0p05', ':'), ('vd1', '-')):
        fn = P('0928', 'idvg', f'IDVG_BIG_{s}_X50_{vd}.log')
        if os.path.exists(fn):
            d = dev(fn); ax[0].semilogy(d['V:gate'], np.abs(d['I:drain']), ls, color=c, label=f'{s} {vd[2:].replace("p", ".")} V' if ls == '-' else None)
    fn = P('0928', 'idvg_return', f'IDVGR_BIG_{s}_X50_vd1.log')
    if os.path.exists(fn):
        d = dev(fn); v, i = d['V:gate'], np.abs(d['I:drain']); up, dn = updown(v)
        ax[1].semilogy(v[up], i[up], color=c, label=s); ax[1].semilogy(v[dn], i[dn], '--', color=c, lw=0.7)
for a, t, s in ((ax[0], '$I_D$--$V_G$ ($V_D$ = 0.05, 1 V)', '(a)'), (ax[1], 'up/down, $V_D$ = 1 V', '(b)')):
    a.set_xlabel('$V_G$ (V)'); a.grid(alpha=.25); a.set_title(t, fontsize=7); a.legend(fontsize=4.8, loc='lower right'); tag(a, s); a.set_ylim(1e-15, 1e-3)
ax[0].set_ylabel('$|I_D|$ (A)'); save(fig, 'figC_idvg')

# ---------------- D. floating island ----------------
fig, ax = plt.subplots(1, 2, figsize=(C1, 1.9))
overlay(ax[0], [(f'0928/ISL_W30_{s}.log', s) for s in ('L3_R7', 'L5_R5', 'L7_R3')], xlim=(2, 6.5)); ax[0].legend(fontsize=5.5, loc='lower right'); tag(ax[0], '(a)')
d = dev(P('0928', 'ISL_W30_L3_R7.log')); v = d['V:drain']; up, dn = updown(v)
for k, c in (('VB_left', MF.PUR), ('VB_right', MF.GRN), ('V_island', MF.RED)):
    ax[1].plot(v[up], d[k][up], color=c, label=k)
ax[1].set_xlabel('$V_D$ (V)'); ax[1].set_ylabel('probe potential (V)'); ax[1].grid(alpha=.25); ax[1].legend(fontsize=5.5, loc='center right'); ax[1].set_xlim(0, 6.5); tag(ax[1], '(b)')
ax[0].set_ylabel('$|I_D|$ (A)'); save(fig, 'figD_island')

# ---------------- E. tapped island: R sweep and two-stage zoom ----------------
fig, ax = plt.subplots(1, 3, figsize=(C2, 2.1))
for c, (fn, lab) in zip(cmap(np.linspace(0, .9, 3)), (('TAPT_ISL_W30_L3_R7_R3e5_VGm0p2.log', '600 k$\\Omega$'), ('TAPT_ISL_W30_L3_R7_R3e4_VGm0p2.log', '60 k$\\Omega$'), ('TAPT_ISL_W30_L3_R7_R1e4_UP_VGm0p2.log', '10 k$\\Omega$'))):
    d = dev(P('1001', 'tap', fn)); v = d['V:drain']; up, dn = updown(v)
    ax[0].semilogy(v[up], np.abs(d['I:drain'][up]), color=c, label=lab); ax[0].semilogy(v[dn], np.abs(d['I:drain'][dn]), '--', color=c, lw=0.7)
    ax[1].plot(v[up], d['V_island'][up] - d['V_island'][0], color=c, label=lab)
ax[0].set_ylim(1e-15, 1e-2); ax[0].set_ylabel('$|I_D|$ (A)'); ax[0].legend(fontsize=5.5, loc='lower right', title='$R_{tap}$', title_fontsize=5.5); tag(ax[0], '(a)')
ax[1].set_ylabel('island rise (V)'); ax[1].legend(fontsize=5.5, loc='center left'); tag(ax[1], '(b)')
d = dev(P('1001', 'tap', 'TAPT_ISL_W30_L3_R7_R3e5_VGm0p2.log')); t, v = d['t'], d['V:drain']; k = np.argmax(np.abs(d['I:drain']) > 1e-8)
m = (t > t[k] - 1e-7) & (t < t[k] + 2e-7)
ax[2].plot((t[m] - t[k]) * 1e9, d['VB_right'][m], color=MF.GRN, label='VB right'); ax[2].plot((t[m] - t[k]) * 1e9, d['VB_left'][m], color=MF.PUR, label='VB left')
ax[2].plot((t[m] - t[k]) * 1e9, d['V_island'][m] - d['V_island'][0], '--', color=MF.RED, label='island rise')
ax[2].set_xlabel('time from jump (ns)'); ax[2].set_ylabel('potential (V)'); ax[2].legend(fontsize=5.5, loc='center right'); ax[2].grid(alpha=.25); tag(ax[2], '(c)')
for a in ax[:2]: a.set_xlim(0, 7); a.grid(alpha=.25); a.set_xlabel('$V_D$ (V)')
save(fig, 'figE_tap')

# ---------------- F. decoupling attempts ----------------
fig, ax = plt.subplots(1, 3, figsize=(C2, 2.1))
for c, (fn, lab) in zip(cmap(np.linspace(0, .9, 3)), (('TAPT_ISL_W100_L3_R7_R1e4_UP_VGm0p2.log', '$V_G$ -0.2'), ('TAPT_ISL_W100_L3_R7_R1e4_UPDN_VGm0p5.log', '-0.5'), ('TAPT_ISL_W100_L3_R7_R1e4_UPDN_VGm1p2.log', '-1.2'))):
    d = dev(P('1001', 'tap', fn)); v = d['V:drain']; up, dn = updown(v)
    ax[0].semilogy(v[up], np.abs(d['I:drain'][up]), color=c, label=lab + ' $I_D$'); ax[0].semilogy(v[up], np.abs(d['I:source'][up]), ':', color=c)
ax[0].set_title('island 100 nm (dotted: $I_S$)'); tag(ax[0], '(a)')
for a, fn, title, s in ((ax[1], 'TAPT_ISL_W30TC_L3_R7_R1e4_UD6S_VGm0p2.log', 'top ohmic contact (C)', '(b)'),):
    d = dev(P('1001', 'tap', fn)); v = d['V:drain']; up, dn = updown(v)
    for k, c, lab in (('I:drain', 'k', '$I_D$'), ('I:tap', MF.GRN, '$I_{tap}$'), ('I:source', MF.PUR, '$I_S$')):
        a.semilogy(v[up], np.abs(d[k][up]), color=c, label=lab)
    a.set_title(title); tag(a, s)
e = np.loadtxt(P('1001', 'tap', 'TAPT_ISL_W30LK_L3_R7_R1e4_UD6S_VGm0p2_extract.dat')); v = e[:, 1]; up, dn = updown(v)
for col, c, lab in ((2, 'k', '$I_D$'), (4, MF.GRN, '$I_{tap}$'), (3, MF.PUR, '$I_S$')):
    ax[2].semilogy(v[up], np.abs(e[up, col]), color=c, label=lab); ax[2].semilogy(v[dn], np.abs(e[dn, col]), '--', color=c, lw=0.6)
ax[2].set_title('island lifetime 1 ps (B)'); tag(ax[2], '(c)')
for a in ax: a.set_xlim(0, 6.5); a.set_ylim(1e-17, 1e-2); a.grid(alpha=.25); a.set_xlabel('$V_D$ (V)'); a.legend(fontsize=5.3, loc='lower right')
ax[0].set_ylabel('current (A)'); save(fig, 'figF_decouple')

# ---------------- G. B structure: R sweep ----------------
fig, ax = plt.subplots(1, 2, figsize=(C1, 1.9))
srcs = [('1001/tap/TAPT_ISL_W30LK_L3_R7_R1e4_UD6S_VGm0p2_extract.dat', '10 k$\\Omega$', 'x'), ('1001/tap/TAPT_ISL_W30LK_L3_R7_R3e5_UD7S_VGm0p2_extract.dat', '300 k$\\Omega$', 'x'),
        ('1001/tap/TAPT_ISL_W30LK_L3_R7_R1e6_UD7S_VGm0p2.log', '1 M$\\Omega$', 'l')]
for c, (fn, lab, kind) in zip(cmap(np.linspace(0, .9, 3)), srcs):
    if kind == 'x':
        e = np.loadtxt(P(fn)); v, Is, vi = e[:, 1], np.abs(e[:, 3]), e[:, 8]
    else:
        d = dev(P(fn)); dt = np.diff(d['t'], prepend=d['t'][0]); m = (dt > 1e-12) | (np.arange(len(dt)) < 3)
        v, Is, vi = d['V:drain'][m], np.abs(d['I:source'][m]), d['V_island'][m]
    up, dn = updown(v)
    ax[0].semilogy(v[up], Is[up], color=c, label=lab); ax[1].plot(v[up], vi[up] - vi[0], color=c, label=lab)
ax[0].set_ylabel('$|I_S|$ left STL (A)'); ax[0].set_ylim(1e-18, 1e-5); ax[1].set_ylabel('island rise (V)')
for a, s in zip(ax, '(a) (b)'.split()): a.set_xlabel('$V_D$ (V)'); a.grid(alpha=.25); a.legend(fontsize=5.5, title='$R_{tap}$', title_fontsize=5.5, loc='center left'); a.set_xlim(0, 6); tag(a, s)
save(fig, 'figG_B_R')

# ---------------- H. standalone left STL extras: B overlay, round trip, ramp rate ----------------
fig, ax = plt.subplots(1, 3, figsize=(C2, 2.1))
d = dev(P('1001', 'tap', 'LEFTONLY_L135_P3e17_UD6S_VGm0p2.log')); v = d['V:drain']; up, _ = updown(v)
ax[0].semilogy(v[up], np.abs(d['I:source'][up]), 'k', label='standalone $I_S$ vs $V_D$')
for c, fn, lab in ((MF.RED, 'TAPT_ISL_W30LK_L3_R7_R3e5_UD7S_VGm0p2_extract.dat', 'B, 300 k$\\Omega$'),):
    e = np.loadtxt(P('1001', 'tap', fn)); vv = e[:, 1]; u, _ = updown(vv)
    ax[0].semilogy(e[u, 8] - e[0, 8], np.abs(e[u, 3]), color=c, label=lab + ': $I_S$ vs island rise')
ax[0].set_xlim(0, 2.8); ax[0].set_ylim(1e-14, 1e-3); ax[0].set_xlabel('left-STL drain bias (V)'); ax[0].set_ylabel('$|I_S|$ (A)'); ax[0].legend(fontsize=5.3, loc='lower right'); ax[0].set_title('left STL in B vs standalone (3e17)'); tag(ax[0], '(a)')
for c, fn, lab in ((MF.GRN, 'LEFTONLY_L135_P6e17_UD3_VGm0p2.log', '0.7 V/ms'), (MF.RED, 'LEFTONLY_L135_P6e17_UD3_R7_VGm0p2.log', '7 V/ms')):
    d = dev(P('1001', 'tap', fn)); v = d['V:drain']; up, dn = updown(v)
    ax[1].semilogy(v[up], np.abs(d['I:source'][up]), color=c, label=lab); ax[1].semilogy(v[dn], np.abs(d['I:source'][dn]), '--', color=c, lw=0.7)
    ax[2].plot(v[up], d['VB_left'][up], color=c, label=lab); ax[2].plot(v[dn], d['VB_left'][dn], '--', color=c, lw=0.7)
ax[1].set_xlim(1.5, 3.05); ax[1].set_ylim(1e-14, 1e-3); ax[1].set_xlabel('$V_D$ (V)'); ax[1].set_ylabel('$|I_S|$ (A)'); ax[1].legend(fontsize=5.5, loc='lower right', title='6e17, ramp', title_fontsize=5.5); tag(ax[1], '(b)')
ax[2].set_xlim(1.5, 3.05); ax[2].set_xlabel('$V_D$ (V)'); ax[2].set_ylabel('VB$_{left}$ (V)'); ax[2].legend(fontsize=5.5, loc='lower right'); tag(ax[2], '(c)')
for a in ax: a.grid(alpha=.25)
save(fig, 'figH_left_extra')

# ---------------- I. all DD split variables (9 panels) ----------------
G = [('(a) $R_{tap}$', [('DDS_R3e5', '300 k'), ('DDS_R1e6', '1 M'), ('DDS_R3e6', '3 M'), ('DDS_BASE', '10 M ref'), ('DDS_R3e7', '30 M'), ('DDS_R1e8', '100 M'), ('DDS_R3e8', '300 M')]),
     ('(b) $N_{A,L}$', [('DDS_NL4e17', '4e17'), ('DDS_NL5e17', '5e17'), ('DDS_NL5p5e17', '5.5e17'), ('DDS_BASE', '6e17 ref'), ('DDS_NL6p5e17', '6.5e17'), ('DDS_NL7e17', '7e17'), ('DDS_NL8e17', '8e17')]),
     ('(c) $N_{A,R}$', [('DDS_NR5e17', '5e17'), ('DDS_NR6e17', '6e17'), ('DDS_NR6p5e17', '6.5e17'), ('DDS_BASE', '7e17 ref'), ('DDS_NR7p5e17', '7.5e17'), ('DDS_NR8e17', '8e17'), ('DDS_NR9e17', '9e17'), ('DDS_NR1e18', '1e18')]),
     ('(d) $V_G$', [('DDS_VGm1p0', '-1.0'), ('DDS_VGm0p5', '-0.5'), ('DDS_VGm0p3', '-0.3'), ('DDS_BASE', '-0.2 ref'), ('DDS_VGm0p1', '-0.1'), ('DDS_VG0', '0'), ('DDS_VGp0p2', '+0.2')]),
     ('(e) island lifetime', [('DDS_TAU1em13', '1e-13'), ('DDS_BASE', '1e-12 ref'), ('DDS_TAU1em11', '1e-11'), ('DDS_TAU1em10', '1e-10'), ('DDS_TAU1em9', '1e-9')]),
     ('(f) island width', [('DDS_WISL20', '20 nm'), ('DDS_BASE', '30 nm ref'), ('DDS_WISL50', '50 nm'), ('DDS_WISL100', '100 nm')]),
     ('(g) island position', [('DDS_XS40', '40 %'), ('DDS_BASE', '50 % ref'), ('DDS_XS60', '60 %')]),
     ('(h) $T_{si}$', [('DDS_TSI30', '30 nm'), ('DDS_BASE', '50 nm ref'), ('DDS_TSI70', '70 nm')]),
     ('(i) ramp rate', [('DDS_RATE0p07', '0.07 V/ms'), ('DDS_BASE', '0.7 ref'), ('DDS_RATE7', '7 V/ms')])]
fig, axs = plt.subplots(3, 3, figsize=(C2, 6.0))
for a, (title, items) in zip(axs.flat, G):
    mm_overlay(a, items, xlim=(0, 4.5)); a.set_title(title, fontsize=7.5); a.legend(fontsize=4.8, loc='lower right', ncol=2)
for a in axs[:, 0]: a.set_ylabel('$|I_D|$ (A)')
save(fig, 'figI_dd_splits')

# ---------------- J. lifetime-1e-8 retuning (batch 4) ----------------
G4 = [('(a) Si lifetime', [('DDS_TE5em9', '5e-9'), ('DDS_TE1em8', '1e-8 ref'), ('DDS_TE2em8', '2e-8'), ('DDS_TE5em8', '5e-8'), ('DDS_BASE', '1e-7')]),
      ('(b) $N_{A,L}$ @ 1e-8 s', [('DDS_TE8_NL5e17', '5e17'), ('DDS_TE8_NL5p5e17', '5.5e17'), ('DDS_TE1em8', '6e17 ref'), ('DDS_TE8_NL6p5e17', '6.5e17')]),
      ('(c) $N_{A,R}$ @ 1e-8 s', [('DDS_TE8_NR5e17', '5e17'), ('DDS_TE8_NR6e17', '6e17'), ('DDS_TE1em8', '7e17 ref')]),
      ('(d) $V_G$, $R_{tap}$ @ 1e-8 s', [('DDS_TE8_VG0', '$V_G$ 0'), ('DDS_TE8_VGm0p1', '$V_G$ -0.1'), ('DDS_TE1em8', 'ref'), ('DDS_TE8_R3e6', '$R$ 3 M'), ('DDS_TE8_R3e7', '$R$ 30 M')]),
      ('(e) structure @ 1e-8 s', [('DDS_TE1em8', 'ref'), ('DDS_TE8_XS60', 'island 60 %'), ('DDS_TE8_WISL50', 'island 50 nm'), ('DDS_TE8_TAU1em11', 'island 1e-11 s')]),
      ('(f) combinations @ 1e-8 s', [('DDS_TE1em8', 'ref'), ('DDS_TE8_NR5e17_NL5e17', 'R5e17 L5e17'), ('DDS_TE8_NR6e17_NL5p5e17', 'R6e17 L5.5e17'), ('DDS_TE8_VG0_NL5p5e17', '$V_G$0 L5.5e17'), ('DDS_RD3e4_TE1em8', '+drain 30 k')])]
fig, axs = plt.subplots(2, 3, figsize=(C2, 4.1))
for a, (title, items) in zip(axs.flat, G4):
    mm_overlay(a, items, xlim=(0, 5.5)); a.set_title(title, fontsize=7.5); a.legend(fontsize=4.8, loc='lower right')
for a in axs[:, 0]: a.set_ylabel('$|I_D|$ (A)')
save(fig, 'figJ_te8')

# ---------------- K. rectangles (batch 5), six variables ----------------
G5 = [('(a) island position', [('DDS_TE8_XS55', '55 %'), ('DDS_TE8_XS60', '60 % ref'), ('DDS_TE8_XS65', '65 %'), ('DDS_TE8_XS70', '70 %')]),
      ('(b) $N_{A,L}$', [('DDS_TE8_XS60_NL5e17', '5e17'), ('DDS_TE8_XS60_NL5p5e17', '5.5e17'), ('DDS_TE8_XS60', '6e17 ref')]),
      ('(c) $V_G$', [('DDS_TE8_XS60_VG0', '0'), ('DDS_TE8_XS60_VGm0p1', '-0.1'), ('DDS_TE8_XS60', '-0.2 ref')]),
      ('(d) $N_{A,R}$', [('DDS_TE8_XS60', '7e17 ref'), ('DDS_TE8_XS60_NR8e17', '8e17'), ('DDS_TE8_XS60_NR1e18', '1e18')]),
      ('(e) Si lifetime', [('DDS_TE5em9_XS60', '5e-9'), ('DDS_TE8_XS60', '1e-8 ref'), ('DDS_TE2em8_XS60', '2e-8'), ('DDS_XS60', '1e-7')]),
      ('(f) drain series R', [('DDS_TE8_XS60', '0 ref'), ('DDS_TE8_XS60_RD1e5', '100 k'), ('DDS_TE8_XS60_RD3e5', '300 k'), ('DDS_TE8_XS60_RD1e6', '1 M'), ('DDS_TE8_XS60_NL5p5e17_RD3e5', 'L5.5e17+300 k')])]
fig, axs = plt.subplots(2, 3, figsize=(C2, 4.1))
for a, (title, items) in zip(axs.flat, G5):
    mm_overlay(a, items); a.set_title(title, fontsize=7.5); a.legend(fontsize=4.8, loc='lower right')
for a in axs[:, 0]: a.set_ylabel('$|I_D|$ (A)')
save(fig, 'figK_rect')

# ---------------- L. mechanism maps: hole density in states I, II, III (BASE_SNAP) ----------------
from mech2_ddsplit import read_full
from mech_ddsplit import snap_map
mp = snap_map('DDS_BASE_SNAP'); want = [('up', 2.0, 'state I (2.0 V)'), ('up', 3.0, 'state II (3.0 V)'), ('up', 4.0, 'state III (4.0 V)')]
fig, axs = plt.subplots(3, 1, figsize=(C1, 3.4), sharex=True)
for a, (sw, vv, lab) in zip(axs, want):
    k = [k for k, (s, v) in mp.items() if s == sw and abs(v - vv) < 1e-6][0]
    cen, area, f, nodes, ix = read_full(P('1007_ddsplit', f'DDS_BASE_SNAP_T_tr_{k}'))
    m = (nodes[:, 1] <= 0.0505) & (nodes[:, 0] > 0.45) & (nodes[:, 0] < 0.85); nd = nodes[m]
    tri = mtri.Triangulation((nd[:, 0] - 0.5) * 1000, nd[:, 1] * 1000)
    cs = a.tricontourf(tri, np.log10(np.maximum(nd[:, 2 + ix['107']], 1e4)), levels=np.linspace(4, 19, 16), cmap='viridis', extend='both')
    for xv in (0, 135, 165, 300): a.axvline(xv, color='w', lw=.5, ls='--')
    a.set_ylim(50, 0); a.set_ylabel('$y$ (nm)'); a.text(0.01, 0.9, lab, transform=a.transAxes, color='w', fontsize=6.5, va='top')
axs[-1].set_xlabel('$x$ from source edge (nm)')
cb = fig.colorbar(cs, ax=axs, pad=0.02); cb.set_label('log$_{10}p$ (cm$^{-3}$)', fontsize=6.5)
fig.savefig(os.path.join(MF.OUT, 'figL_hole_maps.pdf')); fig.savefig(os.path.join(MF.OUT, 'figL_hole_maps.png'), dpi=200); plt.close(fig); print('ok figL_hole_maps')

# ---------------- M. hcte: hot spot and the false jump ----------------
fig, ax = plt.subplots(1, 2, figsize=(C1, 1.9))
def rdT(fn):
    C = {}; rows = []; codes = None
    for l in open(fn):
        if l.startswith('c '): p = l.split(); C[int(p[1])] = (float(p[2]), float(p[3]))
        elif l.startswith('s '): codes = l.split()[2:]
        elif l.startswith('n '): rows.append(l.split())
    i = codes.index('123')
    return np.array([list(C[int(p[1]) + 1]) + [float(p[3 + i])] for p in rows if p[2] == '3'])
a = rdT(P('1001', 'tap', 'TAPT_ISL_W30LK_L3_R7_R1e6_RS50_NEWT_VGm0p2_UP_5p25.str')) if os.path.exists(P('1001', 'tap', 'TAPT_ISL_W30LK_L3_R7_R1e6_RS50_NEWT_VGm0p2_UP_5p25.str')) else None
if a is not None:
    for y0, c in ((0.0, MF.RED), (0.025, MF.BLUE)):
        ys = np.unique(np.round(a[:, 1], 6)); yy = ys[np.argmin(abs(ys - y0))]; s = a[(abs(a[:, 1] - yy) < 1e-6) & (a[:, 0] > 0.70) & (a[:, 0] < 0.86)]; s = s[np.argsort(s[:, 0])]
        ax[0].plot((s[:, 0] - 0.5) * 1000, s[:, 2] / 1e3, '.-', ms=2, color=c, label=f'y = {yy*1000:.0f} nm')
ax[0].axvline(300, color='k', lw=.5, ls='--'); ax[0].set_xlabel('$x$ (nm)'); ax[0].set_ylabel('$T_n$ (10$^3$ K)'); ax[0].legend(fontsize=5.5, loc='center left'); ax[0].grid(alpha=.25); tag(ax[0], '(a)')
d = dev(P('1001', 'tap', 'TAPT_ISL_W30LK_L3_R7_R1e6_UD7S_VGm0p2.log')); t = d['t']; n = len(t); s = np.arange(n - 45, n)
dt = np.diff(t)[n - 46:n - 1]
ax[1].semilogy(s - s[-1], np.abs(d['I:gate'][s]), color=MF.RED, label='$|I_G|$'); ax[1].semilogy(s - s[-1], np.abs(d['I:drain'][s]), color='k', label='$|I_D|$')
ax[1].semilogy(s - s[-1], np.maximum(dt, 1e-26), color=MF.BLUE, label='$\\Delta t$ (s)')
ax[1].set_xlabel('logged point (0 = last)'); ax[1].legend(fontsize=5.5); ax[1].grid(alpha=.25); tag(ax[1], '(b)')
save(fig, 'figM_hcte_diag')

# ---------------- appendix table: every DD split (summary + rectangle metrics) ----------------
def rd(fn):
    out = {}
    for l in open(P('1007_ddsplit', fn)):
        if l.startswith('#') or not l.strip(): continue
        p = l.split(); out[p[0]] = p[1:]
    return out
S, Rm = rd('ddsplit_summary.dat'), rd('ddsplit_rect.dat')
def f(x, k=2):
    try: v = float(x)
    except ValueError: return '--'
    return '--' if np.isnan(v) else f'{v:.{k}f}'
rows = []
for n in sorted(S):
    s, r = S[n], Rm.get(n, ['nan'] * 7)
    rows.append('%s & %s & %s & %s & %s & %s & %s & %s \\\\' % (n[4:].replace('_', '\\_'), s[0], f(s[1]), f(s[3]), f(s[6]), f(s[5]), f(s[7]), f(r[2])))
h = len(rows) // 2 + len(rows) % 2
head = ('\\begin{tabular}{@{}l@{\\,}c@{\\,}c@{\\,}c@{\\,}c@{\\,}c@{\\,}c@{\\,}c@{}}\\toprule\n'
        'split & $n$ & $V_{on,R}$ & $V_{on,L}$ & $V_{off,R}$ & $V_{off,L}$ & $\\Delta V_{off}$ & sep \\\\ \\midrule\n')
tex = head + '\n'.join(rows[:h]) + '\n\\bottomrule\\end{tabular}\\hfill\n' + head + '\n'.join(rows[h:]) + '\n\\bottomrule\\end{tabular}\n'
open(os.path.join(R, 'paper', 'splittable.tex'), 'w').write(tex); print('ok splittable.tex', len(rows))
