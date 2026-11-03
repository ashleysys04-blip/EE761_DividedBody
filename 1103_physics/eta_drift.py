#!/usr/bin/env python3
"""Island hole transport with the drain current's ohmic field (drift-aided n+ base), against the snapshot eta(I_D, W).
Holes injected at the right island edge (p(0) = p0, set by the right body-island junction, p0 ~ I_D), collected at the left edge
(p(W) = 0). In the island the electron current I_D sets E = J/sigma, J = I_D/(W_dev t_si), sigma = q N_D mu_n, which drifts holes
toward the left body.  L_p^2 p'' - L_E p' - p = 0,  L_p = sqrt(D_p tau_p),  L_E = mu_p E tau_p.
eta = gamma * J_p(W) / (q D_p p0 / L_p)  ->  gamma / sinh(W/L_p) at E = 0.   mu_n, mu_p at 1e20 (ATLAS conmob table), tau_p consrh.
Output: eta_drift.dat, eta_drift.png"""
import os, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
VT, Q = 0.02585, 1.602e-19
ND, NSRH, MUN, MUP = 1e20, 5e16, 90.0, 45.0
WDEV, TSI = 0.5e-4, 50e-7                                  # cm


def eta_phys(ID, W_nm, tau_isl, gamma):
    taup = tau_isl / (1 + ND / NSRH); Lp = np.sqrt(VT * MUP * taup)                     # cm
    E = np.asarray(ID) / (WDEV * TSI) / (Q * ND * MUN); LE = MUP * E * taup; W = W_nm * 1e-7
    r = np.sqrt(LE ** 2 + 4 * Lp ** 2); s1, s2 = (LE + r) / (2 * Lp ** 2), (LE - r) / (2 * Lp ** 2)   # s1 > 0 > s2
    # p = A e^{s1 x} + B e^{s2 x}, p(0) = 1, p(W) = 0  (written to avoid overflow: e^{s1 W} large)
    d = 1 - np.exp((s2 - s1) * W)                                                        # A = -e^{(s2-s1)W}/d, B = 1/d
    dpW = (-np.exp((s2 - s1) * W) * s1 * np.exp(s1 * W) + s2 * np.exp(s2 * W)) / d       # p'(W)
    return gamma * (-Lp ** 2 * dpW) / Lp


B = [l.split() for l in open(os.path.join(R, '1103_model', 'balance.dat')) if not l.startswith('#')]
pts = [(int(r[1]), float(r[13]), float(r[16]), r[4], float(r[8])) for r in B if r[0] == 'width' and float(r[13]) > 1e-8 and float(r[16]) > 0]
# gamma: state II of ISLW120 (W 120 nm, left off), as in stl_model.py
g120 = np.exp(np.mean([np.log(e) for w, ID, e, dr, IL in pts if w == 120 and dr == 'up' and IL < 1e-7]))
GAMMA = g120 / eta_phys(1.5e-7, 120, 1e-8, 1.0)
out = ['# eta_drift.py: gamma %.4f (from ISLW120 state II); L_p %.1f nm' % (GAMMA, 1e7 * np.sqrt(VT * MUP * 1e-8 / (1 + ND / NSRH))),
       '# W_nm  I_D(A)  eta snapshot  eta model (drift+diffusion)  eta model (diffusion only)  ratio']
fig, ax = plt.subplots(1, 2, figsize=(13, 4.8)); cm = plt.get_cmap('viridis'); WS = sorted({p[0] for p in pts})
for i, w in enumerate(WS):
    P = sorted([(ID, e) for ww, ID, e, dr, IL in pts if ww == w]); x = np.array([p[0] for p in P]); y = np.array([p[1] for p in P])
    ax[0].loglog(x, y, 'o', color=cm(i / len(WS)), ms=4, label=f'W {w} nm')
    II = np.logspace(-7.5, -1.2, 200); ax[0].loglog(II, eta_phys(II, w, 1e-8, GAMMA), '-', color=cm(i / len(WS)))
    for ID, e in zip(x, y):
        m = eta_phys(ID, w, 1e-8, GAMMA); m0 = eta_phys(1e-12, w, 1e-8, GAMMA)
        out.append('%4d %9.2e %9.2e %9.2e %9.2e %6.2f' % (w, ID, e, m, m0, e / m))
ax[0].set_xlabel('|I_D| (A)'); ax[0].set_ylabel('eta = island holes / I_D'); ax[0].legend(fontsize=7); ax[0].grid(alpha=.3, which='both')
ax[0].set_title('eta(I_D, W): snapshots (symbols) vs drift-aided n+ base (lines, one gamma)', fontsize=9)
II = np.logspace(-6, -1, 100); E = II / (WDEV * TSI) / (Q * ND * MUN); taup = 1e-8 / (1 + ND / NSRH); Lp = np.sqrt(VT * MUP * taup)
LE = MUP * E * taup; Lplus = 2 * Lp ** 2 / (np.sqrt(LE ** 2 + 4 * Lp ** 2) - LE)
ax[1].loglog(II, Lplus * 1e7, 'r-', label='downstream decay length (drift + diffusion)'); ax[1].loglog(II, LE * 1e7, 'r:', label='drift length mu_p E tau_p')
ax[1].axhline(Lp * 1e7, color='gray', ls='--', label='L_p (diffusion)')
lef = [(2e-7, 19), (1e-5, 44), (5e-5, 70), (2e-4, 64), (1e-3, 65), (4e-3, 78), (2e-2, 127)]
ax[1].loglog(*zip(*lef), 'ko', label='L_eff from eta(W) fits (third_latch.dat)')
ax[1].set_xlabel('|I_D| (A)'); ax[1].set_ylabel('length (nm)'); ax[1].legend(fontsize=7); ax[1].grid(alpha=.3, which='both')
fig.tight_layout(); fig.savefig(os.path.join(H, 'eta_drift.png'), dpi=100)
open(os.path.join(H, 'eta_drift.dat'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out[:2])); print('\n'.join(l for l in out[2:] if float(l.split()[1]) > 1e-4 or l.split()[0] in ('30',)))
