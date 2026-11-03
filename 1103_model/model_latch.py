#!/usr/bin/env python3
"""Body hole-balance model of the second (left-STL) latch, driven by the applied drain voltage as in TCAD.

Left p body in steady state (control volume of extract_balance.py; I = left-STL electron current |I_S|, V = island potential):
    m(V) I + eta(I_D) I_D + G0 = g(I) I,          I_D = I + V / R_tap
      m(V) = M - 1 of the left drain junction        universal, fitted to the snapshots of all runs
      g(I) = 1 / beta (recombination + back-injection into the n+ source per electron)   universal, fitted to all runs
      eta  = holes from the island per drain-current electron   measured per run from the snapshots (no fit)
      G0   = other hole generation, 1e-15 A (scale of the off-state hole currents of the killed runs)
For every I the balance gives the island potential V(I) (m is monotonic), so the left STL is one curve V(I).
Right STL in series (on in states II and III): V_D = V(I) + V_R(I_D), with V_R(I_D) the right-STL on-branch read from the
same run's log (V_D - V_tap vs |I_D|). V_D(I) is S-shaped: the up sweep follows new maxima of V_D(I) with rising I and jumps
at a local maximum (2nd latch); the down sweep follows new minima with falling I and drops at a local minimum (turn-off).
No local maximum = continuous turn-on. On the on-branch d ln I / dV = (d ln m / dV) / (d ln g_eff / d ln I): the slant
of the down sweep is the field sensitivity of impact ionization over the current roll-off of beta (plus the right STL in series).
Inputs: balance.dat, TCAD logs. Output: model_fit.dat, model_latch.png"""
import os, sys, numpy as np, matplotlib
from scipy.optimize import least_squares
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
from analyze_ddsplit import load_cols, analyse
RTAP, G0 = 1e7, 1e-15
B = [l.split() for l in open(os.path.join(H, 'balance.dat')) if not l.startswith('#')]
col = {k: i for i, k in enumerate('sweep W tau snap dir VD Vtap Visl IeL Iii Rb Rs Ic ID m g eta res run'.split())}
F = lambda r, k: float(r[col[k]])
RUNS = [('ISLW015', '1030_islw', 15, 'width'), ('NOKILL_TE8_XS60', '1010_sink', 30, 'width'), ('ISLW045', '1030_islw', 45, 'width'),
        ('ISLW060', '1030_islw', 60, 'width'), ('ISLW090', '1030_islw', 90, 'width'), ('ISLW120', '1030_islw', 120, 'width'),
        ('ISLW200', '1030_islw', 200, 'width'), ('DDS_TE8_XS60', '1007_ddsplit', 30, 'killed'), ('ISLW120_KILL', '1030_islw', 120, 'killed')]
LAB = {'DDS_TE8_XS60': 'W 30 nm, killed', 'ISLW120_KILL': 'W 120 nm, killed'}

# ---------- universal m(V), g(I): every snapshot whose left-body balance closes (|res| < 0.3) ----------
ok = [r for r in B if F(r, 'IeL') > 1e-12 and abs(F(r, 'res')) < 0.3 and F(r, 'g') > 0 and F(r, 'm') > 0]
mV = np.array([[F(r, 'Visl'), F(r, 'm')] for r in ok if F(r, 'IeL') < 3e-3])          # m depends on V only below ~3 mA
gI = np.array([[F(r, 'IeL'), F(r, 'g')] for r in ok])


def m_of(V, p): return p[0] / (1 + np.exp(-(V - p[1]) / p[2]))
def g_of(I, q): return q[0] * (I / 1e-6) ** (-q[1]) + q[2] * (I / 1e-6) ** q[3] / (1 + (I / q[4]) ** q[3])


pm = least_squares(lambda p: np.log(m_of(mV[:, 0], p)) - np.log(mV[:, 1]), [0.5, 2.0, 0.5]).x
pg = least_squares(lambda q: np.log(g_of(gI[:, 0], q)) - np.log(gI[:, 1]), [0.03, 0.25, 0.03, 0.6, 3e-4],
                   bounds=([1e-4, 0, 1e-4, 0.05, 1e-6], [1, 1, 1, 2, 1])).x


def eta_tab(run):
    pts = sorted({(F(r, 'ID'), max(F(r, 'eta'), 1e-10)) for r in B if r[-1] == run and F(r, 'ID') > 1e-9})
    x, y = np.log10([p[0] for p in pts]), np.log10([p[1] for p in pts])
    return lambda ID: 10 ** np.interp(np.log10(ID), x, y)


def tcad(run, d):
    """TCAD sweep, the right-STL on-branch V_R(I_D) = V_D - V_tap (median per 0.05-decade bin of |I_D|), and the
    second-latch events of analyse() (turn-on / turn-off V_D, jump in decades of I_D)"""
    fn = os.path.join(R, d, run + '.log_tr.log'); M, v, Id, Is, It, Vt = load_cols(fn); k = int(np.argmax(v))
    ID, VR = np.abs(Id), v - Vt
    on = (np.abs(It) + np.abs(Is) > 1e-9) & (v > 1.2)                                  # right STL latched (states II, III)
    lx = np.log10(ID[on]); bins = np.arange(lx.min(), lx.max() + 0.05, 0.05); c = np.digitize(lx, bins)
    xb = np.array([np.median(lx[c == j]) for j in np.unique(c)]); yb = np.array([np.median(VR[on][c == j]) for j in np.unique(c)])
    yb = np.convolve(np.pad(yb, 4, mode='edge'), np.ones(9) / 9, mode='valid')          # 9-bin (0.45 decade) running mean: removes bin noise
    eu, ed = analyse(fn)[:2]; lu = [e for e in eu if e[1] == 'left']; ld = [e for e in ed if e[1] == 'left']
    return dict(v=v, Id=ID, k=k, VR=lambda I: np.interp(np.log10(I), xb, yb),
                von=lu[0][0] if lu else np.nan, jump=lu[0][2] if lu else 0.0, voff=ld[0][0] if ld else np.nan)


def model(run, t, scale=1.0):
    """left curve V(I) from the balance, V_D(I) with the right STL in series, and the up/down sweeps in V_D"""
    et = eta_tab(run); I = np.logspace(-17, -1.3, 1600)
    h = lambda V: m_of(V, pm) * I + scale * et(I + V / RTAP) * (I + V / RTAP) + G0 - g_of(I, pg) * I   # rises with V
    lo, hi = np.zeros_like(I), np.full_like(I, 8.0)                                     # bisection for the island potential
    for _ in range(50):
        mid = 0.5 * (lo + hi); pos = h(mid) > 0; hi = np.where(pos, mid, hi); lo = np.where(pos, lo, mid)
    V = np.where((h(np.zeros_like(I)) < 0) & (h(np.full_like(I, 8.0)) > 0), 0.5 * (lo + hi), np.nan)
    ID = I + V / RTAP; VD = V + t['VR'](ID)
    good = np.isfinite(VD); I, V, ID, VD = I[good], V[good], ID[good], VD[good]
    up = VD >= np.maximum.accumulate(VD) - 1e-9                                          # new maxima while I rises
    dn = VD <= np.minimum.accumulate(VD[::-1])[::-1] + 1e-9                              # new minima while I falls
    def big_gap(ix):                       # the 2nd-latch jump/drop: largest gap whose lower end is in state II (50 nA < I_D < 1 uA)
        g_ = np.diff(np.log10(ID[ix])); g_ = np.where((ID[ix][:-1] < 1e-6) & (ID[ix][:-1] > 5e-8), g_, 0); j = int(np.argmax(g_)) if len(g_) else 0
        return (j, g_[j]) if len(g_) and g_[j] > 0.3 else (None, 0.0)
    iu = np.where(up)[0]; ju, jump = big_gap(iu); idn = np.where(dn)[0]; jd, drop = big_gap(idn)
    return dict(I=I, V=V, ID=ID, VD=VD, up=up, dn=dn, von=VD[iu[ju]] if ju is not None else np.nan,
                voff=VD[idn[jd + 1]] if jd is not None else np.nan, jump=jump)


# state-II coupling vs island width: eta_II = eta0 exp(-W / L_p)
e2 = {}
for r in B:
    if r[col['dir']] == 'up' and F(r, 'IeL') < 1e-7 and F(r, 'ID') > 1e-9: e2.setdefault((r[0], int(r[1]), float(r[2])), []).append(F(r, 'eta'))
E = {k: np.exp(np.mean(np.log(v))) for k, v in e2.items()}
wd = sorted((k[1], v) for k, v in E.items() if k[0] == 'width')
pe = np.polyfit([x for x, y in wd], np.log([y for x, y in wd]), 1); LP = -1 / pe[0]; ETA0 = np.exp(pe[1])

T = {run: tcad(run, d) for run, d, w, s in RUNS}
Mo = {run: model(run, T[run]) for run, d, w, s in RUNS}
cusp = [(f, model('NOKILL_TE8_XS60', T['NOKILL_TE8_XS60'], f)['jump']) for f in np.geomspace(0.25, 8, 16)]
fc = next((f for f, j in cusp if j == 0.0), np.nan); Wc = 30 - LP * np.log(fc)

fig, ax = plt.subplots(3, 4, figsize=(16, 11)); ax = ax.ravel(); lines = []
for n, (run, d, w, s) in enumerate(RUNS):
    t, mo = T[run], Mo[run]; a = ax[n]; k = t['k']
    a.plot(mo['VD'], mo['ID'], '-', color='0.8', lw=3, label='model V_D(I), all')
    a.plot(t['v'][:k + 1], t['Id'][:k + 1], 'k-', lw=1, label='TCAD up'); a.plot(t['v'][k:], t['Id'][k:], 'k--', lw=1, label='TCAD down')
    a.plot(mo['VD'][mo['up']], mo['ID'][mo['up']], 'r-', lw=1.3, label='model up'); a.plot(mo['VD'][mo['dn']], mo['ID'][mo['dn']], 'b--', lw=1.3, label='model down')
    a.set_yscale('log'); a.set_ylim(1e-8, 1e-1); a.set_xlim(1.0, 6.0); a.grid(alpha=.3)
    a.set_title(LAB.get(run, f'W {w} nm, coupled') + f'  ({run})', fontsize=8); a.set_xlabel('V_D (V)'); a.set_ylabel('|I_D| (A)')
    if n == 0: a.legend(fontsize=6, loc='lower right')
    eII = E.get((s, w, 1e-12 if s == 'killed' else 1e-8), np.nan)
    lines.append('%-16s %4d  %8.2e   %.3f %.3f   %.3f %.3f   %4.1f %4.1f' % (run, w, eII, t['von'], mo['von'], t['voff'], mo['voff'], t['jump'], mo['jump']))
a = ax[9]; cw = [(r_, w) for r_, d_, w, s in RUNS if s == 'width']; ws = [w for r_, w in cw]
for key, mk, lab in (('von', 'o', 'turn-on'), ('voff', 's', 'turn-off')):
    a.plot(ws, [T[r_][key] for r_, w in cw], 'k' + mk + '-', ms=4, label='TCAD ' + lab)
    a.plot(ws, [Mo[r_][key] for r_, w in cw], 'r' + mk + '--', ms=4, mfc='w', label='model ' + lab)
a.set_xlabel('island width W (nm)'); a.set_ylabel('2nd latch V_D (V)'); a.grid(alpha=.3); a.legend(fontsize=6, loc='upper left')
b = a.twinx(); b.plot(ws, [T[r_]['jump'] for r_, w in cw], 'g^-', ms=4); b.plot(ws, [Mo[r_]['jump'] for r_, w in cw], 'g^--', ms=4, mfc='w')
b.set_ylabel('2nd jump, decades of I_D (green: solid TCAD, dashed model)', color='g', fontsize=7)
a = ax[10]; II = np.logspace(-12, -1, 200)
a.loglog(gI[:, 0], gI[:, 1], 'r.', ms=4); a.loglog(II, g_of(II, pg), 'r-')
VV = np.linspace(0.5, 3.0, 100); b = a.twiny(); b.semilogy(mV[:, 0], mV[:, 1], 'k.', ms=4); b.semilogy(VV, m_of(VV, pm), 'k-')
a.set_xlabel('|I_S| (A)   red: g = 1/beta', color='r'); a.set_ylabel('g (red), M - 1 (black)'); b.set_xlabel('island potential (V)   black: M - 1'); a.grid(alpha=.3, which='both')
a = ax[11]
for kk, v in E.items():
    a.semilogy(kk[1], v, {'width': 'ro', 'tau': 'bs', 'killed': 'kx'}[kk[0]], ms=5)
    if kk[0] == 'tau': a.annotate('tau %.0e s' % kk[2], (kk[1], v), fontsize=6, xytext=(4, 0), textcoords='offset points')
WW = np.linspace(0, 210, 50); a.semilogy(WW, ETA0 * np.exp(-WW / LP), 'r-', lw=.8, label='eta0 exp(-W/L_p), L_p = %.1f nm' % LP)
a.semilogy([30], [ETA0 * np.exp(-30 / (LP * np.sqrt(0.3)))], 'b+', ms=9, label='prediction tau 3e-9 s (L_p sqrt(0.3))')
a.set_xlabel('island width W (nm)'); a.set_ylabel('eta_II = island holes / I_D (state II)'); a.grid(alpha=.3); a.legend(fontsize=6)
fig.suptitle('Left-STL body hole balance m(V) I + eta(I_D) I_D + G0 = g(I) I with the right STL in series (its on-branch from the same run). '
             'm, g universal (all runs), eta measured per run (.str), no per-run fit', fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(H, 'model_latch.png'), dpi=100)
txt = ['# model_latch.py', 'm(V) = %.4g / (1 + exp(-(V - %.4g) / %.4g))   (V = island potential)' % tuple(pm),
       'g(I) = %.4g (I/1uA)^-%.4g + %.4g (I/1uA)^%.4g / (1 + (I/%.4g)^%.4g)' % (pg[0], pg[1], pg[2], pg[3], pg[4], pg[3]),
       'G0 = %g A, R_tap = %g Ohm' % (G0, RTAP),
       'eta_II(W) = %.4g exp(-W / %.1f nm)   (state-II snapshots, width sweep)' % (ETA0, LP),
       'eta_II: ' + ', '.join('%s W%d tau %.0e: %.2e' % (k[0], k[1], k[2], v) for k, v in sorted(E.items(), key=lambda z: (z[0][0], z[0][1]))),
       'cusp: the 2nd-latch jump of the 30 nm run vanishes at %.2f x its coupling -> W_c = %.1f nm' % (fc, Wc),
       'cusp scan (factor, jump dec): ' + ', '.join('%.2f %.1f' % c for c in cusp),
       '# run              W   eta_II     Von TCAD model   Voff TCAD model   jump TCAD model   (V_D in V; jump in decades of I_D)'] + lines
open(os.path.join(H, 'model_fit.dat'), 'w').write('\n'.join(txt) + '\n'); print('\n'.join(txt))
