#!/usr/bin/env python3
"""Paper figures 1 and 2 (TED draft), drawn from the reference deck (1007_ddsplit/DDS_TE8_XS60.in: L_g 300 nm, island 30 nm at 60 % of L_g,
left/right body 165/105 nm, T_si 50 nm, t_ox 20 nm, T_box 200 nm, tau_0,Si 1e-8 s, R_tap 10 MOhm, V_G -0.2 V).
figW_concept: (a) 3-D view, (b) cross section with the design parameters, (c) |I_D|-V_D of the killed and coupled islands
              (1007_ddsplit/DDS_TE8_XS60, 1010_sink/NOKILL_TE8_XS60, 1030_islw/ISLW120), (d)-(g) body holes in states I, II, III (killed, coupled).
figX_circuits: equivalent circuits of (a) the killed island (series pair) and (b) the coupled island (hole source eta*I_D between the bodies).
Output: paper/fig/figW_concept.{pdf,png}, paper/fig/figX_circuits.{pdf,png}"""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle, FancyArrowPatch
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..'); O = os.path.join(H, 'fig')
sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
from analyze_ddsplit import analyse, load_cols
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Nimbus Roman', 'Nimbus Roman No9 L', 'Times New Roman', 'DejaVu Serif'],
                     'font.size': 7.5, 'mathtext.fontset': 'stix', 'axes.linewidth': 0.6, 'hatch.linewidth': 0.6,
                     'xtick.major.size': 2.5, 'ytick.major.size': 2.5})
NP, PL, PR, BOX, SUB, OX, MET = '#e4574c', '#a9cdf0', '#5e9fd9', '#c9eef2', '#eedcab', '#86d3dc', '#5a5a5a'
RED, BLU, GRN, HOLE = '#c0392b', '#2563a8', '#2e8b3e', 'w'
RUNS = dict(killed='1007_ddsplit/DDS_TE8_XS60', c30='1010_sink/NOKILL_TE8_XS60', c120='1030_islw/ISLW120')


def tag(a, s, x=0.0, y=1.0): a.text(x, y, s, transform=a.transAxes, fontsize=9, weight='bold', va='bottom')


def arrow(a, p, q, c='k', lw=1.0, ms=7, ls='-', z=6, style='-|>'):
    a.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=ms, color=c, lw=lw, ls=ls, zorder=z, shrinkA=0, shrinkB=0))


# ------------------------------------------------------------------ Fig. 1
def box3d(a, x0, x1, y0, y1, d, fc, hatch=None, k=(0.42, 0.30), ec='k', lw=0.5):
    """Oblique block: front face x0..x1, y0..y1; depth d drawn along (k0, k1)."""
    dx, dy = k[0] * d, k[1] * d
    for pts in ([(x0, y1), (x1, y1), (x1 + dx, y1 + dy), (x0 + dx, y1 + dy)],          # top
                [(x1, y0), (x1 + dx, y0 + dy), (x1 + dx, y1 + dy), (x1, y1)],          # right side
                [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]):                             # front
        a.add_patch(Polygon(pts, closed=True, fc=fc, ec=ec, lw=lw, hatch=hatch, joinstyle='round'))


def panel_3d(a):
    d = 260; S0, S1, LB, IS0, IS1, D1 = 0, 140, 140 + 165, 305, 335, 335 + 105 + 140
    yS, yB, yF, yO, yG = 0, 45, 115, 165, 172                     # sub / BOX / film / oxide / gate (vertical scale exaggerated)
    box3d(a, -10, D1 + 10, yS - 40, yS + 45, d, SUB)
    box3d(a, -10, D1 + 10, yB, yF, d, BOX)
    for x0, x1, c, h in ((S0, S1, NP, None), (S1, IS0, PL, None), (IS0, IS1, NP, '////'), (IS1, D1 - 140, PR, None), (D1 - 140, D1, NP, None)):
        box3d(a, x0, x1, yF, yO, d, c, h)
    a.add_patch(Rectangle((IS0, yB), IS1 - IS0, yF - yB, fc=NP, ec='k', lw=.5, hatch='////', zorder=3))      # BOX via (front face)
    a.add_patch(Rectangle((IS0 - 2, yB - 6), D1 + 12 - IS0 + 2, 6, fc='#333', ec='none', zorder=3))           # buried tap contact
    box3d(a, S1, D1 - 140, yO, yG, d, OX); box3d(a, S1, D1 - 140, yG, yG + 32, d, NP)
    for x0 in (S0 + 30, D1 - 110):
        box3d(a, x0, x0 + 80, yO, yO + 8, d * 0.8, MET, k=(0.42, 0.30))
    a.text((S1 + IS0) / 2, (yF + yO) / 2, 'left STL\np-body', ha='center', va='center', fontsize=6.3, color='#123d6a')
    a.text((IS1 + D1 - 140) / 2, (yF + yO) / 2, 'right STL\np-body', ha='center', va='center', fontsize=6.3, color='w')
    a.text(70, (yF + yO) / 2, r'n$^+$', ha='center', va='center', fontsize=7, color='w'); a.text(D1 - 70, (yF + yO) / 2, r'n$^+$', ha='center', va='center', fontsize=7, color='w')
    a.text((S1 + D1 - 140) / 2, yG + 16, r'n$^+$ poly gate', ha='center', va='center', fontsize=6.5, color='w')
    a.text(30, (yB + yF) / 2, 'BOX', fontsize=6.5, va='center'); a.text(30, yS, 'Si sub.', fontsize=6.5, va='center')
    # terminals
    for x, y, s, ha in ((S0 + 70 + 55, yO + 8 + 50, 'S', 'right'), ((S1 + D1 - 140) / 2 + 55, yG + 32 + 60, r'G ($V_G$)', 'left'),
                        (D1 - 70 + 55, yO + 8 + 50, r'D ($V_D$)', 'left')):
        a.plot([x, x], [y - 50 + (24 if s[0] != 'G' else 18), y], color='k', lw=.7); a.plot(x, y, 'o', mfc='w', mec='k', ms=4)
        a.text(x + (12 if ha == 'left' else -12), y, s, fontsize=7, va='center', ha=ha,
               bbox=dict(fc='w', ec='none', pad=.6, alpha=.85) if s[0] == 'D' else None)
    # tap resistor to ground
    xr = D1 + 12; yr = yB - 3
    zz = np.array([[0, 0], [12, 0], [15, 6], [21, -6], [27, 6], [33, -6], [39, 6], [42, 0], [54, 0]])
    a.plot(xr + zz[:, 0], yr + zz[:, 1], color='k', lw=.7); a.plot([xr + 54, xr + 54], [yr, yr - 25], color='k', lw=.7)
    for i, w in enumerate((14, 9, 4)): a.plot([xr + 54 - w, xr + 54 + w], [yr - 25 - 4 * i] * 2, color='k', lw=.7)
    a.text(xr + 8, yr - 12, r'$R_{tap}$', fontsize=7, ha='center', va='top')
    a.annotate('n$^+$ island + BOX via\n' r'(width $W_{IS}$, lifetime $\tau_{0,isl}$)', xy=(IS0 + 15, yB + 20), xytext=(IS0 + 30, yS - 75),
               fontsize=6.8, color=RED, ha='center', va='top', arrowprops=dict(arrowstyle='-|>', color=RED, lw=.8, mutation_scale=7))
    a.set_xlim(-20, D1 + 160); a.set_ylim(-130, 330); a.set_aspect('equal'); a.axis('off')


def dim(a, x0, x1, y, s, c='k', fs=6.3, above=True):
    arrow(a, (x0, y), (x1, y), c=c, lw=.6, ms=5, style='<|-|>')
    a.text((x0 + x1) / 2, y + (4 if above else -4), s, ha='center', va='bottom' if above else 'top', fontsize=fs, color=c)


def panel_xsec(a):
    S1, IS0, IS1, D0 = 0, 165, 195, 300; X0, X1 = -55, 355
    yB0, yF, yO, yG = -200, 0, 50, 70
    a.add_patch(Rectangle((X0, yB0), X1 - X0, -yB0, fc=BOX, ec='k', lw=.5))
    a.add_patch(Rectangle((X0, yF), S1 - X0, yO, fc=NP, ec='k', lw=.5)); a.add_patch(Rectangle((D0, yF), X1 - D0, yO, fc=NP, ec='k', lw=.5))
    a.add_patch(Rectangle((S1, yF), IS0, yO, fc=PL, ec='k', lw=.5)); a.add_patch(Rectangle((IS1, yF), D0 - IS1, yO, fc=PR, ec='k', lw=.5))
    a.add_patch(Rectangle((IS0, yB0 + 12), IS1 - IS0, yO - yB0 - 12, fc=NP, ec='k', lw=.5, hatch='////'))
    a.add_patch(Rectangle((IS0 - 10, yB0), X1 + 20 - IS0 + 10, 12, fc='#333', ec='none'))
    a.add_patch(Rectangle((S1, yO), D0, 20, fc=OX, ec='k', lw=.5)); a.add_patch(Rectangle((S1, yG), D0, 40, fc=NP, ec='k', lw=.5))
    for x in (X0 + 8, X1 - 8):                                                   # break marks: S/D are 500 nm long
        a.plot([x - 5, x + 5], [yF - 6, yO + 6], color='k', lw=.6)
    a.text((X0 + S1) / 2, yO + 8, 'S', ha='center', va='bottom', fontsize=7); a.text((D0 + X1) / 2, yO + 8, 'D', ha='center', va='bottom', fontsize=7)
    a.text(S1 + IS0 / 2, yO / 2, r'$6\times10^{17}$', ha='center', va='center', fontsize=6.2)
    a.text((IS1 + D0) / 2, yO / 2, r'$7\times10^{17}$', ha='center', va='center', fontsize=6.2, color='w')
    dim(a, S1, D0, yG + 48, r'$L_g$ = 300 nm')
    dim(a, S1, IS0, -32, r'$L_{P,L}$ = 165 nm', above=False); dim(a, IS1, D0, -32, r'$L_{P,R}$ = 105', above=False)
    a.annotate(r'$W_{IS}$ = 30 nm' '\n' r'n$^+$ $10^{20}$ cm$^{-3}$', xy=(IS1, -110), xytext=(235, -120), fontsize=6.2, color=RED, va='center',
               arrowprops=dict(arrowstyle='-', color=RED, lw=.6))
    a.text(X0 + 8, -165, r'BOX 200 nm', fontsize=6.2)
    a.text(X0 - 6, yO / 2, r'$T_{si}$ 50', fontsize=6.2, ha='right', va='center'); a.text(X0 - 6, yO + 22, r'$t_{ox}$ 20', fontsize=6.2, ha='right', va='center')
    a.text(X1 + 20, yB0 - 14, r'$R_{tap}$ 10 M$\Omega$', fontsize=6.2, ha='right', va='top')
    a.set_xlim(X0 - 75, X1 + 25); a.set_ylim(yB0 - 45, yG + 75); a.set_aspect('equal'); a.axis('off')


def panel_iv(a):
    sty = [('killed', 'k', r'killed (1 ps), 30 nm'), ('c30', RED, r'coupled (10 ns), 30 nm'), ('c120', '#e8968c', r'coupled (10 ns), 120 nm')]
    for k, c, lab in sty:
        M, v, Id, *_ = load_cols(os.path.join(R, RUNS[k] + '.log_tr.log')); j = int(np.argmax(v))
        a.semilogy(v[:j + 1], np.abs(Id[:j + 1]), '-', color=c, lw=1.0, label=lab); a.semilogy(v[j:], np.abs(Id[j:]), '--', color=c, lw=.7)
    E = {k: analyse(os.path.join(R, p + '.log_tr.log'))[0] for k, p in RUNS.items()}
    g = lambda k, s: next(e[0] for e in E[k] if e[1] == s)
    a.text(g('killed', 'right') + 0.1, 1e-11, f"{g('killed', 'right'):.2f} V", fontsize=6.2)
    a.text(g('c30', 'left') + 0.08, 1e-9, f"{g('c30', 'left'):.2f} V", fontsize=6.2, color=RED)
    a.text(g('c120', 'left') + 0.08, 1e-9, f"{g('c120', 'left'):.2f} V", fontsize=6.2, color='#d9776b')
    a.text(g('killed', 'left') - 0.08, 1e-11, f"{g('killed', 'left'):.2f} V", fontsize=6.2, ha='right')
    for s, x, y in (('I', 0.5, 1e-11), ('II', 2.9, 3e-6), ('III', 5.05, 1e-6)):
        a.text(x, y, s, fontsize=6, ha='center', va='center', bbox=dict(boxstyle='round,pad=0.15', fc='w', ec='k', lw=.5))
    a.set_xlabel(r'$V_D$ (V)'); a.set_ylabel(r'$|I_D|$ (A)'); a.set_xlim(0, 5.4); a.set_ylim(1e-14, 10); a.grid(alpha=.25)
    a.legend(loc='upper left', fontsize=5.8, labelspacing=.2, borderpad=.3, handlelength=1.5)


def mini(a, holesL, holesR, title, sub, island='k', notes=()):
    """Cross-section cartoon (x 0..100). island: 'k' killed (hatched) or 'c' coupled (plain n+)."""
    a.add_patch(Rectangle((0, 0), 100, 14, fc=BOX, ec='k', lw=.5))
    a.add_patch(Rectangle((0, 14), 14, 22, fc=NP, ec='k', lw=.5)); a.add_patch(Rectangle((86, 14), 14, 22, fc=NP, ec='k', lw=.5))
    a.add_patch(Rectangle((14, 14), 38, 22, fc=PL, ec='k', lw=.5)); a.add_patch(Rectangle((58, 14), 28, 22, fc=PR, ec='k', lw=.5))
    a.add_patch(Rectangle((52, 2), 6, 34, fc=NP, ec='k', lw=.5, hatch='////' if island == 'k' else None))
    a.add_patch(Rectangle((14, 36), 72, 3, fc=OX, ec='k', lw=.4)); a.add_patch(Rectangle((14, 39), 72, 6, fc=NP, ec='k', lw=.4))
    for x, y, s in ((7, 25, 'S'), (50, 42, 'G'), (93, 25, 'D')): a.text(x, y, s, ha='center', va='center', fontsize=6.3, color='w')
    rng = np.random.default_rng(3)
    for (x0, x1, n) in ((14, 52, holesL), (58, 86, holesR)):
        for k in range(n):
            a.add_patch(Circle((x0 + 4 + (x1 - x0 - 8) * ((k * 0.618) % 1), 18 + 14 * ((k * 0.381 + 0.2) % 1)), 1.7, fc=HOLE, ec='k', lw=.5, zorder=4))
    for f in notes: f(a)
    a.text(50, -4, title, ha='center', va='top', fontsize=6.8, weight='bold'); a.text(50, -12, sub, ha='center', va='top', fontsize=6.2, linespacing=1.1)
    a.set_xlim(-2, 102); a.set_ylim(-30, 47); a.set_aspect('equal'); a.axis('off')


def fig1():
    fig = plt.figure(figsize=(7.16, 3.75))
    a = fig.add_axes([0.0, 0.40, 0.43, 0.58]); panel_3d(a); tag(a, '(a)', 0.01, 0.9)
    a = fig.add_axes([0.42, 0.42, 0.30, 0.56]); panel_xsec(a); tag(a, '(b)', 0.0, 0.9)
    a = fig.add_axes([0.795, 0.52, 0.195, 0.44]); panel_iv(a); tag(a, '(c)', -0.36, 1.0)
    bk = lambda x, y, s, c='k', fs=5.8, ha='center': (lambda a: a.text(x, y, s, fontsize=fs, color=c, ha=ha, va='center', zorder=7))
    inj = lambda a: arrow(a, (66, 25), (57, 25), c=RED, lw=1.0, ms=6)
    pos = lambda i: [0.005 + 0.25 * i, 0.0, 0.24, 0.39]
    a = fig.add_axes(pos(0)); mini(a, 0, 0, 'State I: both off', r'$V_D<V_{LU,1}=1.45$ V' '\n' 'bodies empty, barriers high'); tag(a, '(d)', 0.0, 0.9)
    a = fig.add_axes(pos(1)); mini(a, 0, 7, 'State II: right STL latched', 'holes back-injected into the island:\nkilled: recombine; coupled: diffuse on',
                                   notes=[inj]); tag(a, '(e)', 0.0, 0.9)
    a = fig.add_axes(pos(2)); mini(a, 7, 7, 'State III, killed island', r'$V_I=I_{tap}R_{tap}$ turns on the left STL' '\n' r'(series pair): $V_{LU,2}=4.78$ V',
                                   notes=[inj, lambda a: arrow(a, (55, 2), (55, -2.5), c='k', lw=.8, ms=5), bk(66, 7, r'$V_I\uparrow$', fs=6.2)]); tag(a, '(f)', 0.0, 0.9)
    def cross(a):
        arrow(a, (66, 30), (40, 30), c=GRN, lw=1.3, ms=7)
        a.text(30, 7, r'$T=1/\cosh(W_{IS}/L)$', fontsize=5.8, color=GRN, ha='center', va='center', zorder=8)
    a = fig.add_axes(pos(3)); mini(a, 7, 7, 'State III, coupled island', r'island holes charge the left body:' '\n' r'$V_{LU,2}=1.97$ V at $W_{IS}=30$ nm',
                                   island='c', notes=[inj, cross]); tag(a, '(g)', 0.0, 0.9)
    [fig.savefig(os.path.join(O, 'figW_concept.' + e), dpi=300) for e in ('pdf', 'png')]


# ------------------------------------------------------------------ Fig. 2
def ln(a, *pts, c='k', lw=.8, ls='-'):
    p = np.array(pts, float); a.plot(p[:, 0], p[:, 1], color=c, lw=lw, ls=ls, solid_capstyle='round', zorder=3)


def dot(a, x, y, c='k'): a.plot(x, y, 'o', color=c, ms=2.6, zorder=5)


def mosfet(a, x, y):
    """n-MOSFET, channel along y (source left, drain right at x -/+ 1), gate above, body terminal down to (x, y-0.75)."""
    ln(a, (x - 1, y), (x - 1, y + 0.45), (x - 0.55, y + 0.45)); ln(a, (x + 1, y), (x + 1, y + 0.45), (x + 0.55, y + 0.45))
    for s in (-0.55, -0.12, 0.31): ln(a, (x + s, y + 0.45), (x + s + 0.24, y + 0.45), lw=1.6)
    ln(a, (x - 0.6, y + 0.85), (x + 0.6, y + 0.85), lw=1.6)
    arrow(a, (x, y - 0.75), (x, y + 0.42), lw=.8, ms=5)


def npn(a, x, y):
    """npn with horizontal base bar at y, emitter to the left-down (arrow out), collector to the right-down."""
    ln(a, (x - 0.55, y), (x + 0.55, y), lw=1.6)
    arrow(a, (x - 0.25, y), (x - 0.85, y - 0.6), lw=.8, ms=5); ln(a, (x + 0.25, y), (x + 0.85, y - 0.6))


def csrc(a, x, y, d, dep=False, c='k'):
    """current source centred at (x, y), arrow direction d = (dx, dy) unit; dep -> diamond (controlled source)."""
    if dep: a.add_patch(Polygon([(x - .42, y), (x, y + .42), (x + .42, y), (x, y - .42)], fc='w', ec=c, lw=.9, zorder=4))
    else: a.add_patch(Circle((x, y), .36, fc='w', ec=c, lw=.9, zorder=4))
    arrow(a, (x - .22 * d[0], y - .22 * d[1]), (x + .24 * d[0], y + .24 * d[1]), c=c, lw=.8, ms=4.5, z=7)


def resistor_v(a, x, y0, y1):
    n = 6; ys = np.linspace(y0, y1, 2 * n + 1); xs = [x] + [x + (0.18 if k % 2 else -0.18) for k in range(1, 2 * n)] + [x]
    a.plot(xs, ys, color='k', lw=.8, zorder=3)


def cap_v(a, x, y):
    ln(a, (x - .3, y + .08), (x + .3, y + .08), lw=1.4); ln(a, (x - .3, y - .08), (x + .3, y - .08), lw=1.4)


def gnd(a, x, y):
    ln(a, (x, y), (x, y - .15))
    for i, w in enumerate((.3, .19, .08)): ln(a, (x - w, y - .15 - .1 * i), (x + w, y - .15 - .1 * i))


def term(a, x, y, s, ha):
    a.plot(x, y, 'o', mfc='w', mec='k', ms=4, zorder=6); a.text(x + (-.25 if ha == 'right' else .25), y, s, ha=ha, va='center', fontsize=7.5)


def circuit(a, coupled):
    y0 = 4.0; xL, xR = 4.0, 14.0; xI0, xI1 = 7.0, 11.0
    for x0, x1, c, s, tc, xt, yt, ha, va in ((1.6, 6.6, '#e8f1fb', 'left STL (2nd latch)', BLU, 3.85, 5.65, 'right', 'bottom'),
                                             (6.8, 11.2, '#e9f5ea', r'island (n$^+$)', GRN, 9.0, 5.5, 'center', 'top'),
                                             (11.4, 16.4, '#fbebea', 'right STL (1st latch)', RED, 14.15, 5.65, 'left', 'bottom')):
        a.add_patch(Rectangle((x0, 1.45), x1 - x0, 4.15, fc=c, ec=tc, lw=.6, ls=(0, (3, 2)), zorder=0))
        a.text(xt, yt, s, ha=ha, va=va, fontsize=6.4, color=tc)
    # gate
    ln(a, (xL, y0 + .85), (xL, 6.0), (xR, 6.0), (xR, y0 + .85)); ln(a, (9.0, 6.0), (9.0, 6.4)); dot(a, 9.0, 6.0)
    term(a, 9.0, 6.5, r'G ($V_G$)', 'left')
    # main path S - M_L - island - M_R - D
    ln(a, (0.5, y0), (xL - 1, y0)); ln(a, (xL + 1, y0), (xR - 1, y0)); ln(a, (xR + 1, y0), (17.5, y0))
    term(a, 0.4, y0, 'S', 'right'); term(a, 17.6, y0, r'D ($V_D$)', 'left')
    mosfet(a, xL, y0); mosfet(a, xR, y0)
    a.text(xL + .7, y0 + .95, r'$M_L$', fontsize=7.5, ha='left'); a.text(xR - .7, y0 + .95, r'$M_R$', fontsize=7.5, ha='right')
    # bodies, II sources, parasitic npn
    for x, xs, xd, nm in ((xL, 2.2, xI0, 'L'), (xR, xI1, 15.8, 'R')):
        yb = y0 - .75; yq = y0 - 1.55
        ln(a, (x, yb), (x, yq)); dot(a, x, yb)
        a.text(x - .15, yb + .05, rf'$B_{nm}$', fontsize=7.5, ha='right', va='bottom', color=BLU if nm == 'L' else RED)
        csrc(a, x + 1.2, yb, (-1, 0)); ln(a, (x, yb), (x + .84, yb)); ln(a, (x + 1.56, yb), (xd, yb)); dot(a, xd, yb)
        a.text(x + 1.2, yb - .42, rf'$I_{{ii,{nm}}}$', fontsize=6.5, ha='center', va='top')
        npn(a, x, yq); ln(a, (x - .85, yq - .6), (xs, yq - .6), (xs, y0)); ln(a, (x + .85, yq - .6), (xd, yq - .6), (xd, y0))
        dot(a, xs, y0); dot(a, xd, y0)
        a.text(x - .85, yq + .12, rf'$Q_{nm}$', fontsize=7.5, ha='right', va='bottom')
    # island node: C_I, R_tap
    dot(a, 8.2, y0); dot(a, 9.8, y0); a.text(9.0, y0 + .12, r'$V_I$', fontsize=7.5, color=GRN, ha='center', va='bottom')
    ln(a, (8.2, y0), (8.2, 2.6)); cap_v(a, 8.2, 2.5); ln(a, (8.2, 2.42), (8.2, 2.0)); gnd(a, 8.2, 2.0); a.text(8.5, 2.5, r'$C_I$', fontsize=7, va='center')
    ln(a, (9.8, y0), (9.8, 3.4)); resistor_v(a, 9.8, 3.4, 2.4); ln(a, (9.8, 2.4), (9.8, 2.0)); gnd(a, 9.8, 2.0); a.text(10.1, 2.9, r'$R_{tap}$', fontsize=7, va='center')
    # body-to-body hole path below the npn base bars
    yc = 1.0
    if coupled:
        ln(a, (xL, y0 - 1.55), (xL, yc), (xR, yc), (xR, y0 - 1.55), c=GRN, lw=1.0); dot(a, xL, y0 - 1.55, GRN); dot(a, xR, y0 - 1.55, GRN)
        csrc(a, 9.0, yc, (-1, 0), dep=True, c=GRN)
        a.text(9.0, yc - .5, r'hole source $\eta I_D=\gamma_R(I_D)\,T(W_{IS},\tau_{0,isl},I_D)\,I_D$', fontsize=6.6, color=GRN, ha='center', va='top')
    else:
        ln(a, (xL, y0 - 1.55), (xL, yc), (xR, yc), (xR, y0 - 1.55), c='0.55', lw=.8, ls=(0, (2, 2)))
        a.text(9.0, yc, r'$\times$', fontsize=12, color='0.3', ha='center', va='center', bbox=dict(fc='w', ec='none', pad=.2))
        a.text(9.0, yc - .5, r'no hole path: back-injected holes recombine in the island ($\eta\approx0$)', fontsize=6.4, color='0.25', ha='center', va='top')
    a.set_xlim(-.6, 19.6); a.set_ylim(0.05, 6.95); a.set_aspect('equal'); a.axis('off')


def fig2():
    fig, ax = plt.subplots(2, 1, figsize=(3.5, 3.3)); fig.subplots_adjust(left=0.0, right=1.0, top=0.95, bottom=0.0, hspace=0.12)
    circuit(ax[0], False); ax[0].set_title('(a) killed island: series pair', fontsize=7.5, loc='left', weight='bold', pad=1)
    circuit(ax[1], True); ax[1].set_title('(b) coupled island', fontsize=7.5, loc='left', weight='bold', pad=1)
    [fig.savefig(os.path.join(O, 'figX_circuits.' + e), dpi=300) for e in ('pdf', 'png')]


if __name__ == '__main__':
    fig1(); fig2()
