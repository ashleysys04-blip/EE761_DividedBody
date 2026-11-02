#!/usr/bin/env python3
"""Is the divided-body device just two STLs in series? Test the left half against the series-circuit rule.

In the series circuit the left STL operating point (I_left = |Is|, V_left = V_tap) must lie on the standalone
left STL I-V (1028_leftstl/LSTL_P6e17, on-branch = down sweep). Body->body hole coupling through the island moves
it off that curve. Compared: killed island (DDS_TE8_XS60, island tau 1e-12 s), not killed (NOKILL_TE8_XS60, 1e-8 s),
metal-core sink (SINK_TE8_XS60). The first two decks differ only in the island lifetime line.
Also lists every fixed-bias jump of |Id| > 0.3 decade (smaller than the 1-decade latch criterion of analyze_ddsplit).
Output: coupling_vs_circuit.dat"""
import os, sys, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit')); sys.path.insert(0, os.path.join(R, 'tools'))
import analyze_ddsplit as A
from plog import load

I_LIST = [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 3e-3, 1e-2]
RUNS = [('DDS_TE8_XS60', os.path.join(R, '1007_ddsplit', 'DDS_TE8_XS60')),
        ('NOKILL_TE8_XS60', os.path.join(H, 'NOKILL_TE8_XS60')),
        ('SINK_TE8_XS60', os.path.join(H, 'SINK_TE8_XS60')),
        ('ISL_TAU1em10_XS60', os.path.join(R, '1029_isltau', 'ISL_TAU1em10_XS60')),
        ('ISL_TAU3em9_XS60', os.path.join(R, '1029_isltau', 'ISL_TAU3em9_XS60'))]


def get(fn):
    M, m = load(fn), A.columns(fn)
    c = lambda k: M[:, m[k]] if k in m else None
    return c('V[1]'), c('V[3]'), c('Adev_drain'), c('Adev_source')


def v_on_down(v, I, k, I0):
    """voltage on the down sweep at the last point where |I| >= I0 (on-branch just before turn-off)"""
    j = np.where(np.abs(I[k:]) >= I0)[0]
    return (k + j[-1]) if len(j) else None


def jumps(v, Id, sign, thr=0.3):
    l = np.log10(np.abs(Id) + 1e-30); out, i, n = [], 0, len(v)
    while i < n - 1:
        j = i
        while j + 1 < n and abs(v[j + 1] - v[i]) < 2e-3:
            j += 1
        if j > i and sign * (l[j] - l[i]) > thr:
            out.append('%.3f(%+.1f)' % (v[i], l[j] - l[i])); i = j
        else:
            i += 1
    return out


v, _, Id, _ = get(os.path.join(R, '1028_leftstl', 'LSTL_P6e17.log_tr.log')); k = int(np.argmax(v))
std = [v[i] if i is not None else np.nan for i in (v_on_down(v, Id, k, I0) for I0 in I_LIST)]
lines = ['# V_left (V) on the on-branch at |I_left| (A): standalone = Vd of LSTL_P6e17, devices = V_tap at |Is|',
         '%-18s ' % 'I_left' + ' '.join('%8.0e' % I for I in I_LIST),
         '%-18s ' % 'standalone' + ' '.join('%8.3f' % x for x in std)]
jl = ['', '# fixed-bias jumps of |Id| > 0.3 decade: V_D(decades)']
for name, base in RUNS:
    v, vt, Id, Is = get(base + '.log_tr.log'); k = int(np.argmax(v))
    row = [vt[i] if i is not None else np.nan for i in (v_on_down(v, Is, k, I0) for I0 in I_LIST)]
    lines.append('%-18s ' % name + ' '.join('%8.3f' % x for x in row))
    jl.append('%-18s up: %s | down: %s' % (name, ' '.join(jumps(v[:k + 1], Id[:k + 1], +1)), ' '.join(jumps(v[k:], Id[k:], -1))))
txt = '\n'.join(lines + jl) + '\n'
open(os.path.join(H, 'coupling_vs_circuit.dat'), 'w').write(txt); print(txt)
