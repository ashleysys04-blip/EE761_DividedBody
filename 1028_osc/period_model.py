#!/usr/bin/env python3
"""Step 16: oscillation period predicted from the DC Id-Vd only (1010_sink/SINK_TE8_XS60, 0.7 V/ms) vs the OSC_* runs.
charge:    T_c = int_{V_off}^{V_on} C dV / (I - I_off(V))   I_off(V) = DC up sweep, latch off (right-on branch for the left loop)
discharge: T_d = int_{V_off}^{V_on} C dV / (I_on(V) - I)    I_on(V)  = DC down sweep, latch on
V_on / V_off are taken from each OSC run (peak / valley). Output: osc_period.png, osc_period.dat (this folder)."""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '1007_ddsplit'))
import analyze_ddsplit as A
M, v, Id, Is, It, Vt = A.load_cols(os.path.join(H, '..', '1010_sink', 'SINK_TE8_XS60.log_tr.log')); k = int(np.argmax(v))
vu, iu = v[:k], np.abs(Id[:k]); vd, idn = v[k:], np.abs(Id[k:])
RUNS = [('OSC_R_1n', 1e-9, 1e-12, 1.4, (lambda i: i < 5e-10), (lambda i: (i >= 1.2e-8) & (i <= 5e-7))),   # right loop: off branch / right-on branch
        ('OSC_R_3n', 3e-9, 3e-12, 1.4, (lambda i: i < 5e-10), (lambda i: (i >= 1.2e-8) & (i <= 5e-7))),
        ('OSC_L_450n', 4.5e-7, 2.25e-10, 3.0, (lambda i: (i > 5e-8) & (i < 4.5e-7)), (lambda i: i >= 6e-7))]  # left loop: right-on branch / left-on branch
def integ(C, I, Voff, Von, vv, ii, m, sign):
    s = m(ii) & (vv > Voff - 0.03) & (vv < Von + 0.05); o = np.argsort(vv[s]); Vg = np.linspace(Voff, Von, 400)
    Ig = np.interp(Vg, vv[s][o], ii[s][o]); return np.trapz(C / (sign * (I - Ig)), Vg)
rows = []
for n, I, C, vmin, moff, mon in RUNS:
    L = A.load(os.path.join(H, n + '.log_tr.log')); c = A.columns(os.path.join(H, n + '.log_tr.log')); t = L[:, 0]; V = L[:, c['V[1]']]; d = np.diff(V)
    pk = [i for i in range(1, len(V) - 1) if d[i - 1] > 0 and d[i] <= 0 and V[i] > vmin]; vl = [i for i in range(1, len(V) - 1) if d[i - 1] < 0 and d[i] >= 0 and V[i] > vmin - 1.0]
    Von, Voff = V[pk[0]], V[[x for x in vl if x > pk[0]][0]]; Tsim = np.diff(t[pk]).mean()
    v0 = [x for x in vl if x > pk[0]][0]; p1 = [x for x in pk if x > v0][0]; Tc_sim, Td_sim = t[p1] - t[v0], t[v0] - t[pk[0]]
    Tc = integ(C, I, Voff, Von, vu, iu, moff, 1); Td = integ(C, I, Voff, Von, vd, idn, mon, -1)
    rows.append((n, I, C, Von, Voff, C * (Von - Voff) / I, Tc, Tc_sim, Td, Td_sim, Tc + Td, Tsim, len(pk)))
with open(os.path.join(H, 'osc_period.dat'), 'w') as f:
    f.write('# name I C V_on V_off C*dV/I T_charge(model) T_charge(sim) T_dis(model) T_dis(sim) T(model) T(sim) n_peaks  [s]\n')
    for r in rows: f.write('%-11s %.2e %.2e %.4f %.4f %.4e %.4e %.4e %.4e %.4e %.4e %.4e %d\n' % r)
fig, ax = plt.subplots(figsize=(7.5, 3.8)); x = np.arange(len(rows)); w = .2
for j, (lab, idx, col) in enumerate((('C dV / I (simple)', 5, '0.7'), ('model (DC Id-Vd)', 10, 'C0'), ('simulation', 11, 'C3'))):
    ax.bar(x + (j - 1) * w, [r[idx] * 1e3 for r in rows], w, color=col, label=lab)
ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows]); ax.set_ylabel('period (ms)'); ax.legend(fontsize=8); ax.grid(alpha=.3, axis='y')
ax.set_title('oscillation period: model from DC Id-Vd only vs OSC runs\ndata: 1010_sink/SINK_TE8_XS60.log_tr.log, 1028_osc/OSC_*.log_tr.log', fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(H, 'osc_period.png'), dpi=130)
print(open(os.path.join(H, 'osc_period.dat')).read())
