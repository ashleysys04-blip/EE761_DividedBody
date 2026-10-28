#!/usr/bin/env python3
"""Step 16 schematic: oscillation circuit on the divided-body device and the expected drain-node waveforms
(drawn from the DC latch voltages of 1010_sink/SINK_TE8_XS60, not simulation output). Output: osc_schematic.png"""
import os, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
H = os.path.dirname(os.path.abspath(__file__))
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 4.2), gridspec_kw=dict(width_ratios=[1.15, 1]))
a.set_xlim(0, 10); a.set_ylim(0, 6); a.axis('off'); a.set_aspect('equal')
def box(x, w, c, t, y=2.4, h=1.0, fs=8):
    a.add_patch(Rectangle((x, y), w, h, fc=c, ec='k', lw=.6)); a.text(x + w / 2, y + h / 2, t, ha='center', va='center', fontsize=fs)
box(1.0, 0.9, '#f5c4b3', 'source\nn+'); box(1.9, 1.6, '#9fe1cb', 'left body\n6e17'); box(3.5, 0.6, '#f5c4b3', '', fs=7)
a.add_patch(Rectangle((3.7, 2.4), 0.2, 1.0, fc='0.4', ec='k', lw=.4)); box(4.1, 1.6, '#9fe1cb', 'right body\n7e17'); box(5.7, 0.9, '#f5c4b3', 'drain\nn+')
a.add_patch(Rectangle((1.9, 3.6), 3.8, 0.35, fc='0.85', ec='k', lw=.6)); a.text(3.8, 3.78, 'gate  -0.2 V (fixed)', ha='center', va='center', fontsize=8)
a.text(3.8, 2.15, 'island + metal core', ha='center', fontsize=7)
def gnd(x, y): a.plot([x - .2, x + .2], [y, y], 'k', lw=1.2); a.plot([x - .1, x + .1], [y - .1, y - .1], 'k', lw=.8)
a.plot([1.0, 0.5, 0.5], [2.9, 2.9, 1.0], 'k', lw=.8); gnd(0.5, 1.0)
a.plot([3.8, 3.8], [2.4, 1.75], 'k', lw=.8); a.add_patch(Rectangle((3.3, 1.15), 1.0, 0.6, fc='w', ec='k', lw=.6)); a.text(3.8, 1.45, 'Rtap 1e7 Ohm', ha='center', va='center', fontsize=7)
a.plot([3.8, 3.8], [1.15, 0.8], 'k', lw=.8); gnd(3.8, 0.8)
a.plot([6.6, 9.2], [2.9, 2.9], 'k', lw=.8); a.plot(7.6, 2.9, 'o', color='C3', ms=5); a.text(7.6, 2.5, 'V_D (drain node)', ha='center', fontsize=8, color='C3')
a.plot([7.6, 7.6], [2.9, 3.9], 'k', lw=.8); a.add_patch(Circle((7.6, 4.3), 0.4, fc='w', ec='C3', lw=1.2))
a.annotate('', xy=(7.6, 4.0), xytext=(7.6, 4.6), arrowprops=dict(arrowstyle='->', color='C3', lw=1.2)); a.plot([7.6, 7.6], [4.7, 5.3], 'k', lw=.8); gnd(7.6, 5.3)
a.text(7.05, 4.3, 'constant\ncurrent I', ha='right', va='center', fontsize=8, color='C3')
a.plot([9.2, 9.2], [2.9, 2.2], 'k', lw=.8); a.plot([8.85, 9.55], [2.2, 2.2], 'C2', lw=2); a.plot([8.85, 9.55], [2.0, 2.0], 'C2', lw=2)
a.plot([9.2, 9.2], [2.0, 1.4], 'k', lw=.8); gnd(9.2, 1.4); a.text(9.65, 2.1, 'C', fontsize=9, color='C2', va='center')
a.set_title('(a) circuit: DC sweep source replaced by I + C on the drain node', fontsize=9)
t1 = [0, 1.0]; v1 = [0, 1.5]
for k in range(16): t1 += [1.0 + .3 * k + .01, 1.0 + .3 * (k + 1)]; v1 += [1.09, 1.5]
t2 = [0, .55, 3.0]; v2 = [0, 1.5, 4.62]
for k in range(4): t2 += [3.0 + 1.5 * k + .02, 3.0 + 1.5 * (k + 1)]; v2 += [2.09, 4.62]
b.plot(t1, v1, 'C2', label='I = 1 nA: right latch only'); b.plot(t2, v2, 'C3--', label='I = 600 nA: right stays on, left repeats')
for v, l in ((1.50, 'right on 1.50'), (1.09, 'right off 1.09'), (4.62, 'left on 4.62'), (2.09, 'left off 2.09')):
    b.axhline(v, ls=':', lw=.6, color='k'); b.text(9.05, v, l, fontsize=7, va='center')
b.set_xlim(0, 9); b.set_ylim(0, 5.2); b.set_xlabel('time (arb.)'); b.set_ylabel('V_D (V)'); b.legend(fontsize=7, loc='upper left')
b.set_title('(b) expected V_D (sketch from DC latch voltages, not simulated)', fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(H, 'osc_schematic.png'), dpi=130)
