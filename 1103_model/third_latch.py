#!/usr/bin/env python3
"""Third jump (hole loop, README Step 18) in TCAD and in the body hole-balance model (model_latch.py).

TCAD: every fixed-bias jump of |I_D| > 0.3 decade above I_D = 1e-4 A (above the second latch), up and down sweep.
Model: the same search on the S-shaped V_D(I) of model_latch.py (up: new maxima with rising I, down: new minima).
Loop condition: on the on-branch M-1(V) = 1/beta(I) - eta(I_D) I_D / I, so V(I) falls with I (negative differential
resistance of the left STL) where d(eta I_D/I)/d ln I > d(1/beta)/d ln I, i.e. where the island transmission eta grows
with current faster than the hole loss per electron. The right STL in series adds dV_R/dI; a fold of V_D(I) = third jump.
Output: third_latch.dat, third_latch.png"""
import os, runpy, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__))
G = runpy.run_path(os.path.join(H, 'model_latch.py'))
T, Mo, RUNS, eta_tab, g_of, pg = G['T'], G['Mo'], G['RUNS'], G['eta_tab'], G['g_of'], G['pg']


def tjumps(v, I, sign, thr=0.3):
    l = np.log10(I + 1e-30); out, i, n = [], 0, len(v)
    while i < n - 1:
        j = i
        while j + 1 < n and abs(v[j + 1] - v[i]) < 2e-3: j += 1
        if j > i and sign * (l[j] - l[i]) > thr and min(I[i], I[j]) > 1e-4: out.append((v[i], l[j] - l[i])); i = j
        else: i += 1
    return out


def mjumps(mo, key):
    ix = np.where(mo[key])[0]; ID = mo['ID'][ix]; d = np.diff(np.log10(ID))
    return [(mo['VD'][ix[k]], d[k]) for k in np.where((d > 0.3) & (ID[:-1] > 1e-4))[0]]


lines = ['# run  W  | TCAD up jumps (V_D, dec) | TCAD down | model up | model down   (I_D > 1e-4 A, > 0.3 dec)']
fig, ax = plt.subplots(1, 3, figsize=(15, 4.3))
for run, d, w, s in RUNS:
    t, mo = T[run], Mo[run]; k = t['k']
    tu, td = tjumps(t['v'][:k + 1], t['Id'][:k + 1], +1), tjumps(t['v'][k:], t['Id'][k:], -1)
    mu, md = mjumps(mo, 'up'), mjumps(mo, 'dn')
    f = lambda L: ' '.join('%.2f(%+.1f)' % x for x in L) or '-'
    lines.append('%-16s %3d | %s | %s | %s | %s' % (run, w, f(tu), f(td), f(mu), f(md)))
for run, c in (('ISLW015', 'tab:purple'), ('NOKILL_TE8_XS60', 'tab:red'), ('ISLW060', 'tab:orange'), ('ISLW120', 'tab:green'), ('ISLW120_KILL', 'k')):
    t, mo = T[run], Mo[run]; k = t['k']
    ax[0].plot(t['v'][:k + 1], t['Id'][:k + 1], '-', color=c, lw=.8, label='TCAD ' + run); ax[0].plot(mo['VD'], mo['ID'], '--', color=c, lw=1.6, alpha=.6)
    I = np.logspace(-6, -1.3, 200); et = eta_tab(run)
    ax[1].semilogx(I, et(I), '-', color=c, label=run)
    ax[2].semilogx(mo['I'], mo['V'], '-', color=c, label=run)
ax[0].set_yscale('log'); ax[0].set_xlim(2.5, 5); ax[0].set_ylim(1e-5, 1e-1); ax[0].set_xlabel('V_D (V)'); ax[0].set_ylabel('|I_D| (A)')
ax[0].set_title('third jump: TCAD up (solid) vs model V_D(I) (dashed)', fontsize=9); ax[0].legend(fontsize=6); ax[0].grid(alpha=.3)
ax[1].semilogx(I, g_of(I, pg), 'k:', label='1/beta (universal)'); ax[1].set_xlabel('|I_D| (A)'); ax[1].set_ylabel('eta = island holes / I_D')
ax[1].set_title('island transmission rises with current (snapshots)', fontsize=9); ax[1].legend(fontsize=6); ax[1].grid(alpha=.3, which='both')
ax[2].set_xlim(1e-6, 5e-2); ax[2].set_ylim(0.8, 3.0); ax[2].set_xlabel('left-STL current |I_S| (A)'); ax[2].set_ylabel('island potential V(I) from the balance (V)')
ax[2].set_title('left STL alone: falling V(I) = negative differential resistance', fontsize=9); ax[2].legend(fontsize=6); ax[2].grid(alpha=.3)
fig.tight_layout(); fig.savefig(os.path.join(H, 'third_latch.png'), dpi=100)
open(os.path.join(H, 'third_latch.dat'), 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines))

# ---------- onset width of the third jump from the universal coupling eta(I_D, W) = eta0(I_D) exp(-W / L_eff(I_D)) ----------
WS = np.array([15, 30, 45, 60, 90, 120]); RW = ['ISLW015', 'NOKILL_TE8_XS60', 'ISLW045', 'ISLW060', 'ISLW090', 'ISLW120']
IDg = np.logspace(-7.5, -1.2, 60); E0, LE = [], []
for ID in IDg:
    p = np.polyfit(WS, np.log([eta_tab(r)(ID) for r in RW]), 1); E0.append(np.exp(p[1])); LE.append(-1 / p[0])
E0, LE = np.array(E0), np.array(LE)
eta_u = lambda ID, W: np.interp(np.log10(ID), np.log10(IDg), E0) * np.exp(-W / np.interp(np.log10(ID), np.log10(IDg), LE))
m_of, pm, RTAP, G0 = G['m_of'], G['pm'], G['RTAP'], G['G0']
VR = T['NOKILL_TE8_XS60']['VR']                       # right STL is the same body (105 nm) in every run


def third(W):
    I = np.logspace(-13, -1.3, 1600)
    h = lambda V: m_of(V, pm) * I + eta_u(I + V / RTAP, W) * (I + V / RTAP) + G0 - g_of(I, pg) * I
    lo, hi = np.zeros_like(I), np.full_like(I, 8.0)
    for _ in range(50):
        mid = 0.5 * (lo + hi); pos = h(mid) > 0; hi = np.where(pos, mid, hi); lo = np.where(pos, lo, mid)
    V = np.where((h(np.zeros_like(I)) < 0) & (h(np.full_like(I, 8.0)) > 0), 0.5 * (lo + hi), np.nan)
    ID = I + V / RTAP; VD = V + VR(ID); g = np.isfinite(VD); ID, VD = ID[g], VD[g]
    hiI = ID > 1e-4; d = np.diff(VD[hiI])                                       # on-branch above 0.1 mA: any V_D fold?
    fold = np.where((d[:-1] > 0) & (d[1:] <= 0))[0]
    return (VD[hiI][fold[0] + 1], ID[hiI][fold[0] + 1]) if len(fold) else (np.nan, np.nan)


scan = [(W,) + third(W) for W in np.arange(10, 62.5, 2.5)]
Wc3 = next((W for W, v, i in scan if not np.isfinite(v)), np.nan)
txt = ['# onset of the third jump with the universal eta(I_D, W) = eta0(I_D) exp(-W / L_eff(I_D)) (fit over W 15-120 nm at each I_D)',
       '# I_D  eta0  L_eff(nm): ' + ', '.join('%.0e %.3f %.0f' % (a, b, c) for a, b, c in zip(IDg[::6], E0[::6], LE[::6])),
       '# W_nm  V_D at the on-branch fold (local max of V_D(I) above 0.1 mA)  I_D there',
       *['%5.1f  %s  %s' % (W, '%.3f' % v if np.isfinite(v) else '  -  ', '%.2e' % i if np.isfinite(i) else '-') for W, v, i in scan],
       '# predicted onset: third jump disappears at W >= %.1f nm' % Wc3]
open(os.path.join(H, 'third_latch.dat'), 'a').write('\n'.join(txt) + '\n'); print('\n'.join(txt))
