#!/usr/bin/env python3
"""Paper figures for the coupling section (README core claim, Steps 17-19).
figR_series:   (a) Id-Vd of the metal-core device, the two-STL series circuits and the coupled device; (b) left-STL operating point
               (V_tap vs |I_S|, down sweep) against the standalone left STL (= series-circuit rule).
figS_knob:     (a) |I_S| of the width sweep, (b) 2nd latch on/off vs L_p/W, (c) 2nd-stage hysteresis, (d) deviation from the series circuit.
figT_holes:    hole density at 3.0 V up / down for W 120 nm coupled vs killed, and W 15 nm at 2.5 V (.str read in Python).
Data: 1010_sink/, 1029_ctrl/, 1029_isltau/, 1030_islw/ (islw_summary.dat, islw_vs_circuit.dat), 1028_leftstl/LSTL_P6e17. Output: paper/fig/."""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.tri as mtri
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..'); O = os.path.join(H, 'fig')
sys.path.insert(0, os.path.join(R, '1007_ddsplit')); sys.path.insert(0, os.path.join(R, 'tools'))
import analyze_ddsplit as A
from plog import load
from mech2_ddsplit import read_full
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Nimbus Roman', 'Nimbus Roman No9 L', 'Times New Roman', 'DejaVu Serif'],
                     'font.size': 7, 'mathtext.fontset': 'stix', 'axes.linewidth': 0.6})
P = lambda *a: os.path.join(R, *a)


def cols(fn):
    """Vd, Vtap, Id, Is for the single device (Adev) or the two-device circuit (Aright/Aleft), as 1029_ctrl/compare_ctrl.py"""
    M, m = load(fn), A.columns(fn)
    c = lambda k: M[:, m[k]] if k in m else None
    if 'Adev_drain' in m: return c('V[1]'), c('V[3]'), c('Adev_drain'), c('Adev_source')
    return c('V[1]'), c('V[3]'), c('Aright_drain'), c('Aleft_source')


def updown(a, x, y, k, **kw):
    a.plot(x[:k + 1], y[:k + 1], **kw); kw.pop('label', None); a.plot(x[k:], y[k:], ls='--', **{**kw, 'lw': kw.get('lw', 1) * .8})


def tag(a, s): a.text(-0.24, 1.02, s, transform=a.transAxes, fontsize=8, weight='bold')


# ---------------- figR: series-circuit control ----------------
fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.5))
a = ax[0]
for fn, c, lab in [('1010_sink/SINK_TE8_XS60', 'tab:blue', 'metal core (one device)'), ('1029_ctrl/CTRL_CUT_IDVD', 'k', 'two STLs in series (cut)'),
                   ('1029_ctrl/CTRL_SD_IDVD', 'gray', 'two STLs in series (S/D)'), ('1010_sink/NOKILL_TE8_XS60', 'tab:red', 'coupled island (one device)')]:
    v, vt, Id, Is = cols(P(fn + '.log_tr.log')); k = int(np.argmax(v))
    updown(a, v, np.abs(Id), k, color=c, lw=1.1 if c == 'tab:red' else .8, label=lab)
a.set_yscale('log'); a.set_xlim(0.8, 5.5); a.set_ylim(1e-13, 1e-1); a.set_xlabel('$V_D$ (V)'); a.set_ylabel('$|I_D|$ (A)'); a.legend(fontsize=5.5, loc='lower right'); a.grid(alpha=.3); tag(a, '(a)')
a = ax[1]
v, _, Id, _ = cols(P('1028_leftstl/LSTL_P6e17.log_tr.log')); k = int(np.argmax(v))
a.plot(np.abs(Id[k:]), v[k:], color='k', lw=1.6, alpha=.35, label='standalone left STL ($V_D$)')
for fn, c, lab in [('1007_ddsplit/DDS_TE8_XS60', 'k', 'killed island'), ('1010_sink/SINK_TE8_XS60', 'tab:blue', 'metal core'),
                   ('1029_isltau/ISL_TAU3em9_XS60', 'tab:orange', r'island $\tau$ 3e-9 s'), ('1010_sink/NOKILL_TE8_XS60', 'tab:red', 'coupled island')]:
    v, vt, Id, Is = cols(P(fn + '.log_tr.log')); k = int(np.argmax(v)); s = slice(k, None)
    a.plot(np.abs(Is[s]), vt[s], color=c, lw=.9, label=lab + ' ($V_{tap}$)')
a.set_xscale('log'); a.set_xlim(1e-7, 2e-2); a.set_ylim(0.9, 3.0); a.set_xlabel('left STL current $|I_S|$ (A), down sweep'); a.set_ylabel('left STL voltage (V)')
a.legend(fontsize=5.5, loc='upper left'); a.grid(alpha=.3, which='both'); tag(a, '(b)')
fig.tight_layout(); [fig.savefig(os.path.join(O, 'figR_series.' + e), dpi=200) for e in ('pdf', 'png')]; plt.close(fig)

# ---------------- figS: coupling knob ----------------
d = np.genfromtxt(P('1030_islw/islw_summary.dat'), dtype=None, encoding=None, comments='#')
dv = np.genfromtxt(P('1030_islw/islw_vs_circuit.dat'), dtype=None, encoding=None, comments='#', skip_header=3)
dv = [r for r in dv if r[0] in ('width', 'tau', 'killed')]
fig, ax = plt.subplots(1, 4, figsize=(7.16, 2.1))
a = ax[0]; cm = plt.get_cmap('viridis')
for i, (w, b) in enumerate([(15, '1030_islw/ISLW015'), (30, '1010_sink/NOKILL_TE8_XS60'), (60, '1030_islw/ISLW060'), (120, '1030_islw/ISLW120'), (200, '1030_islw/ISLW200')]):
    v, vt, Id, Is = cols(P(b + '.log_tr.log')); k = int(np.argmax(v)); updown(a, v, np.abs(Is), k, color=cm(i / 5), lw=.8, label=f'{w} nm')
v, vt, Id, Is = cols(P('1030_islw/ISLW120_KILL.log_tr.log')); k = int(np.argmax(v)); updown(a, v, np.abs(Is), k, color='k', lw=.7, label='120 nm, killed')
a.set_yscale('log'); a.set_xlim(1, 5.2); a.set_ylim(1e-13, 1e-1); a.set_xlabel('$V_D$ (V)'); a.set_ylabel('$|I_S|$ (A)'); a.legend(fontsize=4.8, loc='lower right'); a.grid(alpha=.3); tag(a, '(a)')
SW = (('width', 'o-', 'tab:red', r'width ($\tau$ 1e-8 s)'), ('tau', 's-', 'tab:blue', r'$\tau_{isl}$ (W 30 nm)'))
a = ax[1]
for s, mk, c, lab in SW:
    on = sorted((r[3], r[5]) for r in d if r[0] == s and np.isfinite(r[5])); off = sorted((r[3], r[6]) for r in d if r[0] == s and np.isfinite(r[6]))
    a.semilogx(*zip(*on), mk, color=c, ms=3, lw=.8, label=lab + ', on'); a.semilogx(*zip(*off), mk, color=c, ms=3, lw=.8, mfc='w', ls='--', label='off')
kk = [r for r in d if r[0] == 'killed']
a.semilogx([r[3] for r in kk], [r[5] for r in kk], 'kx', ms=4, label='killed'); a.semilogx([r[3] for r in kk], [r[6] for r in kk], 'kx', ms=4)
w15 = [r for r in d if r[0] == 'width' and r[1] == 15][0]; a.plot([w15[3]] * 2, [1.86, 2.0], 'r-', lw=2.5, alpha=.5)
a.set_xlabel('$L_p/W$'); a.set_ylabel('2nd latch (V)'); a.legend(fontsize=4.8); a.grid(alpha=.3, which='both'); tag(a, '(b)')
a = ax[2]
for s, mk, c, lab in SW + (('killed', 'kx', 'k', 'killed'),):
    pts = sorted((r[3], (r[5] - r[6]) if np.isfinite(r[5]) else 0.0) for r in d if r[0] == s and (np.isfinite(r[6]) or r[1] == 15))
    a.semilogx(*zip(*pts), mk, color=c, ms=3, lw=.8, label=lab)
a.set_xlabel('$L_p/W$'); a.set_ylabel('2nd-stage hysteresis (V)'); a.legend(fontsize=4.8); a.grid(alpha=.3, which='both'); tag(a, '(c)')
a = ax[3]
for s, mk, c, lab in SW + (('killed', 'kx', 'k', 'killed'),):
    for j, (ix, ls) in enumerate(((8, '-'), (7, ':'))):
        pts = sorted((r[3], r[ix]) for r in dv if r[0] == s)
        a.semilogx(*zip(*pts), (mk[0] + ls) if s != 'killed' else 'x', color=c, ms=3 if j == 0 else 2, lw=.8, mfc=None if j == 0 else 'w', label=lab + (', 3 mA' if j == 0 else ', 1 mA') if s != 'killed' else (lab if j == 0 else None))
a.axhline(0, color='gray', lw=.6); a.set_xlabel('$L_p/W$'); a.set_ylabel(r'$V_{tap}-V_{D,\mathrm{standalone}}$ (V)'); a.legend(fontsize=4.5); a.grid(alpha=.3, which='both'); tag(a, '(d)')
fig.tight_layout(w_pad=.6); [fig.savefig(os.path.join(O, 'figS_knob.' + e), dpi=200) for e in ('pdf', 'png')]; plt.close(fig)

# ---------------- figT: hole maps ----------------
MAPS = [('ISLW120', 120, 4, 'W 120 nm, coupled, 3.0 V up'), ('ISLW120', 120, 12, 'W 120 nm, coupled, 3.0 V down'),
        ('ISLW120_KILL', 120, 4, 'W 120 nm, killed, 3.0 V up'), ('ISLW120_KILL', 120, 12, 'W 120 nm, killed, 3.0 V down'),
        ('ISLW015', 15, 3, 'W 15 nm, coupled, 2.5 V up'), ('ISLW015', 15, 13, 'W 15 nm, coupled, 2.5 V down')]
fig, ax = plt.subplots(3, 2, figsize=(7.0, 4.2), sharey=True)
for i, (b, w, k, t) in enumerate(MAPS):
    a = ax[i // 2, i % 2]; cen, area, f, nodes, ix = read_full(P('1030_islw', f'{b}_T_tr_{k}')); wu = w / 1000
    m = (nodes[:, 1] <= 0.0501) & (nodes[:, 0] > 0.47) & (nodes[:, 0] < 0.80 + wu); nd = nodes[m]
    z = np.log10(np.maximum(nd[:, 2 + ix['107']], 1))
    cs = a.tricontourf(mtri.Triangulation((nd[:, 0] - 0.5) * 1e3, nd[:, 1] * 1e3), z, levels=np.linspace(4, 21, 35), cmap='viridis', extend='both')
    for xv in (0, 165, 165 + w, 270 + w): a.axvline(xv, color='w', lw=.5, ls=':')
    a.set_ylim(50, 0); a.set_title(t, fontsize=7); a.set_xlabel('x from source edge (nm)' if i >= 4 else '')
    if i % 2 == 0: a.set_ylabel('y (nm)')
fig.tight_layout(); fig.colorbar(cs, ax=ax, label=r'$\log_{10}p$ (cm$^{-3}$)', shrink=.8, pad=.01)
[fig.savefig(os.path.join(O, 'figT_holes.' + e), dpi=200) for e in ('pdf', 'png')]; plt.close(fig)
