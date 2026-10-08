#!/usr/bin/env python3
"""Find latch events in the DD split MixedMode logs (DDS_*.log_tr.log) and write ddsplit_summary.dat.

Latch event = a run of consecutive points where Vd moves < 2 mV but a path current changes by > 1 decade
and reaches a real level (left |Is| > 1e-7 A, right |Itap| > 1e-9 A) -> regenerative jump at fixed bias.
For each event: Vd, which path jumped (right = tap current, left = source current, both = together)
and the jump size in decades of |Id|.
Columns are found by name from the log header ('p', 'Q', 'X' lines), so circuits with extra elements
(e.g. a drain series resistor) work: Vd = APPLIED drain voltage (node of the Vdrain source), Id/Is/Itap = Adev_drain/source/tap currents.
"""
import sys, glob, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from plog import load

def events(v, I_d, I_s, I_t, sign):
    """sign=+1: rising jumps (up sweep), -1: falling jumps (down sweep)."""
    ld, ls, lt = (np.log10(np.abs(x) + 1e-30) for x in (I_d, I_s, I_t))
    out, i, n = [], 0, len(v)
    while i < n - 1:
        j = i
        while j + 1 < n and abs(v[j + 1] - v[i]) < 2e-3:
            j += 1
        if j > i:
            dd, ds, dt = ld[j] - ld[i], ls[j] - ls[i], lt[j] - lt[i]
            # a latch must change the path current by > 1 decade AND reach a real level
            # (left: |Is| > 1e-7 A, right: |Itap| > 1e-9 A on the 'on' side of the event)
            hi_s = max(abs(I_s[i]), abs(I_s[j])); hi_t = max(abs(I_t[i]), abs(I_t[j]))
            left = sign * ds > 1.0 and hi_s > 1e-7
            right = sign * dt > 1.0 and hi_t > 1e-9
            if left and right:
                out.append((v[i], 'both', dd, ds, dt))
            elif left:
                out.append((v[i], 'left', dd, ds, dt))
            elif right:
                out.append((v[i], 'right', dd, ds, dt))
            i = j
        else:
            i += 1
    return out

def columns(fn):
    """Map names -> column index using the MixedMode log header."""
    nodes, elems, codes = {}, {}, None
    for l in open(fn):
        if l.startswith('Q '):
            p = l.split(); nodes[int(p[1])] = p[3].strip('"')
        elif l.startswith('X '):
            p = l.split(); elems[1300 + int(p[1])] = p[2]
        elif l.startswith('p '):
            codes = [int(c) for c in l.split()[2:]]
        elif l.startswith('d '):
            break
    m = {}
    for i, c in enumerate(codes):
        if c in nodes: m[nodes[c]] = i
        if c in elems: m[elems[c]] = i
    return m

def drain_node(fn):
    """Circuit node number that the device drain is connected to (from the deck)."""
    deck = fn.replace('.log_tr.log', '.in')
    for l in open(deck):
        if l.startswith('Adev'):
            for tok in l.split():
                if tok.endswith('=drain'): return int(tok.split('=')[0])
    return 1

def source_node(fn):
    """Circuit node driven by the Vdrain source (= applied voltage)."""
    for l in open(fn.replace('.log_tr.log', '.in')):
        if l.startswith('Vdrain'):
            return int(l.split()[1])
    return 1

def load_cols(fn, device_v=False):
    """v = applied drain voltage (source node) by default; with a drain series resistor the device node
    snaps back during a latch, so events are detected at fixed APPLIED voltage. device_v=True returns the device node."""
    M = load(fn); m = columns(fn); n = drain_node(fn) if device_v else source_node(fn)
    return M, M[:, m[f'V[{n}]']], M[:, m['Adev_drain']], M[:, m['Adev_source']], M[:, m['Adev_tap']], M[:, m['V[3]']]

def analyse(fn):
    M, v, Id, Is, It, Vt = load_cols(fn)
    k = int(np.argmax(v)); up = slice(0, k + 1); dn = slice(k, None)
    eu = events(v[up], Id[up], Is[up], It[up], +1)
    ed = events(v[dn], Id[dn], Is[dn], It[dn], -1)
    # turn-off points on the down sweep (threshold based, robust when the fall is gradual)
    vdn, sdn, tdn = v[dn], np.abs(Is[dn]), np.abs(It[dn])
    on_l = np.where(sdn > 1e-8)[0]; on_r = np.where(tdn > 1e-9)[0]
    vld_left = vdn[on_l[-1]] if len(on_l) else np.nan
    vld_right = vdn[on_r[-1]] if len(on_r) else np.nan
    return eu, ed, vld_left, vld_right, v.max()

def turnoff_width(fn):
    """Down sweep, left STL: Vd span over which |Is| falls from 1e-6 to 1e-8 A (0 = abrupt), and # of falling jumps."""
    M, v, Id, Is, It, Vt = load_cols(fn); k = int(np.argmax(v))
    vd, s = v[k:], np.abs(Is[k:])
    a = np.where(s > 1e-6)[0]; b = np.where(s > 1e-8)[0]
    if not len(a) or not len(b): return np.nan, 0
    ed = events(v[k:], Id[k:], Is[k:], It[k:], -1)
    return vd[a[-1]] - vd[b[-1]], sum(1 for e in ed if e[1] in ('left', 'both'))

if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    rows = []
    for fn in sorted(glob.glob(os.path.join(here, 'DDS_*.log_tr.log'))):
        name = os.path.basename(fn).replace('.log_tr.log', '')
        q = os.path.join(here, name + '.queue')
        if not (os.path.exists(q) and 'end' in open(q).read()):
            continue   # still running / not started
        try:
            eu, ed, vl, vr, vmax = analyse(fn)
        except Exception as e:
            print(name, 'ERROR', e); continue
        r = [e for e in eu if e[1] in ('right', 'both')]; l = [e for e in eu if e[1] in ('left', 'both')]
        w, nj = turnoff_width(fn)
        rows.append((name, len(eu), r[0][0] if r else np.nan, r[0][2] if r else np.nan,
                     l[0][0] if l else np.nan, l[0][2] if l else np.nan, vl, vr, w, nj, vmax,
                     ';'.join(f'{e[0]:.3f}{e[1][0]}' for e in eu)))
    with open(os.path.join(here, 'ddsplit_summary.dat'), 'w') as fo:
        fo.write('# generated by 1007_ddsplit/analyze_ddsplit.py from DDS_*.log_tr.log\n')
        fo.write('# name n_up_latches V_on_right dec_right V_on_left dec_left V_off_left(Is<1e-8) V_off_right(Itap<1e-9) dV_turnoff_left(1e-6->1e-8) n_fall_jumps_left Vmax up_events\n')
        for r in rows:
            fo.write('%-22s %d %8.4f %6.2f %8.4f %6.2f %8.4f %8.4f %7.3f %d %5.2f %s\n' % r)
    for r in rows:
        print('%-22s latches=%d  right %6.3f V (%4.1f dec)  left %6.3f V (%4.1f dec)  off: left %5.2f right %5.2f  turn-off width %.3f V, falling jumps %d' % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9]))
