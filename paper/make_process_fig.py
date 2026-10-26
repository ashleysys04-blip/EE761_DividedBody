#!/usr/bin/env python3
"""Proposed (not demonstrated) process route for the split-gate + Si-through metal-core sink variant.
Output: paper/fig/figO_process.{png,pdf}. Schematic, not to scale."""
import os, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fig')
C = dict(box='#cfe2f3', handle='#bbbbbb', pL='#6fa8dc', pR='#3d85c6', n='#cc0000', ox='#fff2cc', poly='#b4a7d6',
         ild='#eeeeee', metal='#555555', spacer='#f6b26b', resist='#93c47d')
plt.rcParams.update({'font.size': 7, 'font.family': 'serif'})

def base(ax, title, body=True, island=False, sd=False):
    ax.add_patch(Rectangle((0, -1.2), 10, 0.8, fc=C['handle'], ec='k', lw=.4))
    ax.add_patch(Rectangle((0, -0.4), 10, 0.4, fc=C['box'], ec='k', lw=.4))
    if body:
        ax.add_patch(Rectangle((1, 0), 4.3, 0.3, fc=C['pL'], ec='k', lw=.4))
        ax.add_patch(Rectangle((5.3, 0), 3.7, 0.3, fc=C['pR'], ec='k', lw=.4))
    if island: ax.add_patch(Rectangle((4.9, 0), 0.8, 0.3, fc=C['n'], ec='k', lw=.4))
    if sd:
        ax.add_patch(Rectangle((0, 0), 1.6, 0.3, fc=C['n'], ec='k', lw=.4)); ax.add_patch(Rectangle((8.4, 0), 1.6, 0.3, fc=C['n'], ec='k', lw=.4))
    ax.set_xlim(-0.2, 10.2); ax.set_ylim(-1.3, 1.9); ax.axis('off'); ax.set_title(title, fontsize=7, loc='left')

def gates(ax, gap=True):
    ax.add_patch(Rectangle((1.6, 0.3), 6.8, 0.12, fc=C['ox'], ec='k', lw=.4))
    if gap:
        ax.add_patch(Rectangle((1.6, 0.42), 3.2, 0.6, fc=C['poly'], ec='k', lw=.4)); ax.add_patch(Rectangle((5.8, 0.42), 2.6, 0.6, fc=C['poly'], ec='k', lw=.4))
    else:
        ax.add_patch(Rectangle((1.6, 0.42), 6.8, 0.6, fc=C['poly'], ec='k', lw=.4))

fig = plt.figure(figsize=(7.16, 4.6))
axs = [fig.add_axes([0.01 + 0.33 * (i % 3), 0.52 - 0.47 * (i // 3), 0.31, 0.37]) for i in range(5)]
a = axs[0]; base(a, '(a) SOI mesa (M1)\n     body B, right-body B add (M2)')
a.text(3.1, 0.12, 'p 6e17', ha='center', color='w'); a.text(7.1, 0.12, 'p 7e17', ha='center', color='w')
a.text(5, -0.25, 'BOX', ha='center'); a.text(5, -0.95, 'handle Si', ha='center')
a = axs[1]; base(a, '(b) island As implant (M3)\n     + activation', island=True)
a.add_patch(Rectangle((0.3, 0.35), 4.5, 0.25, fc=C['resist'], ec='k', lw=.4)); a.add_patch(Rectangle((5.8, 0.35), 3.9, 0.25, fc=C['resist'], ec='k', lw=.4))
for x in (5.05, 5.3, 5.55): a.annotate('', (x, 0.32), (x, 1.0), arrowprops=dict(arrowstyle='->', lw=.6))
a.text(5.3, 1.1, 'As', ha='center')
a = axs[2]; base(a, '(c) split gate (M4), S/D + RTA\n     (high-T steps before metal)', island=True, sd=True)
gates(a); a.text(3.2, 0.62, 'gate', ha='center'); a.text(7.1, 0.62, 'rgate', ha='center')
a = axs[3]; base(a, '(d) gap spacers, trench to BOX (M6)\n     shell = spacer (self-aligned)', island=True, sd=True)
gates(a); a.add_patch(Rectangle((4.8, 0.3), 0.3, 0.72, fc=C['spacer'], ec='k', lw=.4)); a.add_patch(Rectangle((5.5, 0.3), 0.3, 0.72, fc=C['spacer'], ec='k', lw=.4))
a.add_patch(Rectangle((5.1, 0), 0.4, 1.02, fc='w', ec='k', lw=.4, ls='--')); a.text(5.3, 1.15, 'trench', ha='center')
a = axs[4]; base(a, '(e) metal/silicide core, contacts (M7),\n     metal (M8); tap -> external R_tap', island=True, sd=True)
gates(a); a.add_patch(Rectangle((4.8, 0.3), 0.3, 0.72, fc=C['spacer'], ec='k', lw=.4)); a.add_patch(Rectangle((5.5, 0.3), 0.3, 0.72, fc=C['spacer'], ec='k', lw=.4))
a.add_patch(Rectangle((5.1, 0), 0.4, 1.5, fc=C['metal'], ec='k', lw=.4)); a.text(5.3, 1.6, 'tap', ha='center')
a.add_patch(Rectangle((0.4, 0.3), 0.6, 1.2, fc=C['metal'], ec='k', lw=.4)); a.add_patch(Rectangle((9.0, 0.3), 0.6, 1.2, fc=C['metal'], ec='k', lw=.4))
a.text(0.7, 1.6, 'S', ha='center'); a.text(9.3, 1.6, 'D', ha='center')
# (f) top view
t = fig.add_axes([0.67, 0.05, 0.32, 0.37]); t.axis('off'); t.set_title('(f) top view: core crosses\n     the full active width', fontsize=7, loc='left')
t.add_patch(Rectangle((0, 1), 10, 3, fc=C['pL'], ec='k', lw=.4, alpha=.35)); t.text(0.2, 3.6, 'active (SOI mesa)', fontsize=6)
t.add_patch(Rectangle((1.6, 0.3), 3.2, 4.4, fc=C['poly'], ec='k', lw=.4, alpha=.8)); t.add_patch(Rectangle((5.8, 0.3), 2.6, 4.4, fc=C['poly'], ec='k', lw=.4, alpha=.8))
t.add_patch(Rectangle((5.1, 0.6), 0.4, 4.9, fc=C['metal'], ec='k', lw=.4)); t.add_patch(Rectangle((4.6, 5.0), 1.4, 0.8, fc=C['metal'], ec='k', lw=.4))
t.text(5.3, 6.0, 'tap pad', ha='center', fontsize=6)
t.add_patch(Rectangle((1.6, -0.5), 6.8, 0.5, fc=C['metal'], ec='k', lw=.4, alpha=.6)); t.text(5, -0.95, 'gate strap (gate = rgate)', ha='center', fontsize=6)
t.set_xlim(-0.2, 10.2); t.set_ylim(-1.3, 6.5)
fig.text(0.01, 0.005, 'Proposed route, not demonstrated. Schematic, not to scale. Source: paper/make_process_fig.py', fontsize=5.5, color='0.4')
os.makedirs(OUT, exist_ok=True)
fig.savefig(os.path.join(OUT, 'figO_process.png'), dpi=220); fig.savefig(os.path.join(OUT, 'figO_process.pdf')); print('ok figO_process')
