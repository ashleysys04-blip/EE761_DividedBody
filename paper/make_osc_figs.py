#!/usr/bin/env python3
"""Paper figures for the current-driven oscillation section (Step 16).
figP_osc_circuit: explanatory behavioural equivalent circuit (not simulated) + current windows of the two loops.
figQ_osc_wave:    V_D(t) of OSC_R_1n / OSC_L_450n / OSC_L_600n and the period model vs simulation.
Data: 1010_sink/SINK_TE8_XS60.log_tr.log, 1028_osc/OSC_*.log_tr.log, 1028_osc/osc_period.dat. Output: paper/fig/."""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..'); O = os.path.join(H, 'fig')
sys.path.insert(0, os.path.join(R, '1007_ddsplit')); import analyze_ddsplit as A
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Nimbus Roman', 'Nimbus Roman No9 L', 'Times New Roman', 'DejaVu Serif'],
                     'font.size': 7, 'mathtext.fontset': 'stix', 'axes.linewidth': 0.6})

# ---------------- figP: behavioural equivalent circuit ----------------
fig = plt.figure(figsize=(7.0, 2.6)); a = fig.add_axes([0.0, 0.0, 0.62, 1.0]); b = fig.add_axes([0.70, 0.17, 0.28, 0.72])
a.set_xlim(0, 12); a.set_ylim(0, 5.2); a.axis('off'); a.set_aspect('equal')
def gnd(x, y):
    a.plot([x - .22, x + .22], [y, y], 'k', lw=1); a.plot([x - .13, x + .13], [y - .1, y - .1], 'k', lw=.8); a.plot([x - .05, x + .05], [y - .2, y - .2], 'k', lw=.6)
def stl(x0, col, name, txt):
    a.add_patch(FancyBboxPatch((x0, 2.55), 2.3, 1.3, boxstyle='round,pad=0.04', fc=col, ec='k', lw=.6))
    # hysteresis icon (x = V, y = log I): off branch -> jump up at V_on; on branch back to V_off -> drop
    X = lambda u: x0 + .3 + 1.7 * u; Y = lambda w: 2.7 + 1.0 * w
    a.plot([X(0), X(.75), X(.75), X(1.0)], [Y(0), Y(.18), Y(.85), Y(.95)], 'k', lw=.8)
    a.plot([X(.75), X(.3), X(.3)], [Y(.85), Y(.72), Y(.05)], 'k--', lw=.6)
    a.text(X(.78), Y(.45), '$V_{on}$', fontsize=5); a.text(X(.08), Y(.42), '$V_{off}$', fontsize=5)
    a.text(x0 + 1.15, 3.98, name, ha='center', fontsize=7.5, weight='bold'); a.text(x0 + 1.15, 2.35, txt, ha='center', va='top', fontsize=6)
a.plot([0.5, 2.0], [3.2, 3.2], 'k', lw=.8); a.plot(0.5, 3.2, 'ko', ms=3); a.text(0.35, 3.5, 'S', fontsize=8); gnd(0.5, 2.6); a.plot([0.5, 0.5], [3.2, 2.6], 'k', lw=.8)
stl(2.0, '#dbe8f7', 'left STL', '$V_{on,L}$ 3.55 V, $V_{hold,L}$ 1.15 V\n$I_{off,L}$ 2e-11 A, $I_{h,L}$ 4.3e-7 A')
a.plot([4.3, 6.6], [3.2, 3.2], 'k', lw=.8); a.plot(5.2, 3.2, 'o', color='g', ms=4); a.text(5.2, 3.45, '$V_I$', ha='center', color='g', fontsize=8)
a.plot([5.2, 5.2], [3.2, 2.2], 'k', lw=.8); a.add_patch(Rectangle((4.95, 1.25), .5, .95, fc='w', ec='k', lw=.6)); a.text(4.85, 1.4, '$R_{tap}$', fontsize=7, ha='right'); a.plot([5.2, 5.2], [1.25, .95], 'k', lw=.8); gnd(5.2, .95)
a.annotate('', xy=(5.6, 1.3), xytext=(5.6, 2.15), arrowprops=dict(arrowstyle='->', lw=.6, color='g')); a.text(5.7, 1.7, '$V_I/R_{tap}$', fontsize=6, color='g')
a.annotate('', xy=(4.45, 3.0), xytext=(5.0, 3.0), arrowprops=dict(arrowstyle='->', lw=.6, color='b')); a.text(4.7, 2.75, '$I_L$', fontsize=6, color='b', ha='center')
stl(6.6, '#f7dede', 'right STL', '$V_{on,R}$ 1.50 V, $V_{off,R}$ 1.09 V\n$I_{fire,R}$ 6e-11 A, $I_{keep,R}$ 1.2e-8 A')
a.plot([8.9, 11.4], [3.2, 3.2], 'k', lw=.8); a.plot(9.9, 3.2, 'ro', ms=3.5); a.text(10.0, 2.85, 'D ($V_D$)', fontsize=7)
a.plot([9.9, 9.9], [3.2, 4.0], 'k', lw=.8); a.add_patch(Circle((9.9, 4.35), .35, fc='w', ec='r', lw=.9)); a.annotate('', xy=(9.9, 4.08), xytext=(9.9, 4.62), arrowprops=dict(arrowstyle='->', color='r', lw=.9))
a.plot([9.9, 9.9], [4.7, 5.0], 'k', lw=.8); a.text(9.45, 4.35, '$I_{in}$', ha='right', va='center', fontsize=8, color='r')
a.plot([11.4, 11.4], [3.2, 2.45], 'k', lw=.8); a.plot([11.0, 11.8], [2.45, 2.45], 'k', lw=1.4); a.plot([11.0, 11.8], [2.25, 2.25], 'k', lw=1.4); a.text(11.9, 2.35, '$C$', fontsize=8, va='center')
a.plot([11.4, 11.4], [2.25, 1.8], 'k', lw=.8); gnd(11.4, 1.8)
a.text(0.2, 0.55, r'island KCL: $I_{in}=I_L+V_I/R_{tap}$;  left: $I_{fire}=V_{on,L}/R_{tap}+I_{off,L}$,  $I_{keep}=V_{hold,L}/R_{tap}+I_{h,L}$', fontsize=6.2)
a.text(0.2, 4.95, '(a)', fontsize=8, weight='bold')
# (b) current windows on a log axis
for y, lo, hi, col, lab in ((1, 6e-11, 1.2e-8, '#d62728', 'right loop'), (0, 3.6e-7, 5.5e-7, '#1f77b4', 'left loop')):
    b.barh(y, np.log10(hi) - np.log10(lo), left=np.log10(lo), height=.45, color=col, alpha=.35, ec=col); b.text(np.log10(lo) - .15, y, lab, ha='right', va='center', fontsize=6.5)
for I, lab, ok in ((1e-9, '1 nA', 'o'), (3e-9, '3 nA', 'o'), (3e-8, '30 nA', '?'), (4.5e-7, '450 nA', 'o'), (6e-7, '600 nA', 'x')):
    yy = 1 if I < 1e-7 else 0; b.plot(np.log10(I), yy + .38, marker={'o': 'v', 'x': 'x', '?': 'v'}[ok], color={'o': 'k', 'x': 'r', '?': '0.6'}[ok], ms=4)
    b.text(np.log10(I) + {'1 nA': -.25, '3 nA': .25, '450 nA': -.45, '600 nA': .45}.get(lab, 0), yy + .52, lab, ha='center', fontsize=5.5)
b.set_yticks([]); b.set_ylim(-.5, 1.85); b.set_xlim(-11.5, -5.5); b.set_xlabel(r'$\log_{10} I_{in}$ (A)'); b.grid(alpha=.3, axis='x')
b.set_title(r'(b) oscillation windows $I_{fire}<I_{in}<I_{keep}$' '\n' r'$\blacktriangledown$ oscillates, $\times$ stays on, grey: running', fontsize=6.5)
os.makedirs(O, exist_ok=True); fig.savefig(os.path.join(O, 'figP_osc_circuit.png'), dpi=300); fig.savefig(os.path.join(O, 'figP_osc_circuit.pdf'))

# ---------------- figQ: waveforms + period model ----------------
fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.2), gridspec_kw=dict(width_ratios=[1, 1.25, .8]))
def load(n):
    f = os.path.join(R, '1028_osc', n + '.log_tr.log'); M = A.load(f); c = A.columns(f); return M[:, 0] * 1e3, M[:, c['V[1]']], M[:, c['V[3]']]
t, v, vt = load('OSC_R_1n'); ax[0].plot(t, v, 'r', lw=.8, label='$V_D$'); ax[0].plot(t, vt, 'g', lw=.6, label='$V_I$')
for y in (1.50, 1.09): ax[0].axhline(y, ls=':', lw=.5, color='k')
ax[0].set_title('(a) right loop, 1 nA, 1 pF', fontsize=7); ax[0].set_xlabel('t (ms)'); ax[0].set_ylabel('V'); ax[0].legend(fontsize=5.5, loc='upper left'); ax[0].set_ylim(-.1, 1.8)
t, v, vt = load('OSC_L_600n'); m = t < 11; ax[1].plot(t[m], v[m], color='0.65', lw=.8, label='$V_D$, 600 nA (stays on)')
t, v, vt = load('OSC_L_450n'); ax[1].plot(t, v, 'b', lw=.8, label='$V_D$, 450 nA'); ax[1].plot(t, vt, 'g', lw=.6, label='$V_I$, 450 nA')
for y in (4.62, 2.08): ax[1].axhline(y, ls=':', lw=.5, color='k')
ax[1].set_title('(b) left loop, 450 nA, 0.225 nF', fontsize=7); ax[1].set_xlabel('t (ms)'); ax[1].legend(fontsize=5.5, loc='lower right'); ax[1].set_ylim(-.1, 5.1)
P = [l.split() for l in open(os.path.join(R, '1028_osc', 'osc_period.dat')) if not l.startswith('#')]
x = np.arange(len(P)); w = .27
for j, (lab, idx, col) in enumerate(((r'$C\Delta V/I$', 5, '0.75'), ('model (DC)', 10, 'C0'), ('TCAD', 11, 'C3'))):
    ax[2].bar(x + (j - 1) * w, [float(p[idx]) * 1e3 for p in P], w, color=col, label=lab)
ax[2].set_xticks(x); ax[2].set_xticklabels(['1 nA', '3 nA', '450 nA']); ax[2].set_ylabel('period (ms)'); ax[2].legend(fontsize=5.5); ax[2].set_title('(c) period', fontsize=7); ax[2].grid(alpha=.3, axis='y')
for q in ax: q.tick_params(labelsize=6)
fig.tight_layout(); fig.savefig(os.path.join(O, 'figQ_osc_wave.png'), dpi=300); fig.savefig(os.path.join(O, 'figQ_osc_wave.pdf'))
print('ok')
