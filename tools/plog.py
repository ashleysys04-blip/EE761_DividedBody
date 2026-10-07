#!/usr/bin/env python3
"""Read Silvaco ATLAS .log / MixedMode *.log_tr.log files into a numpy array.

    from plog import load
    d = load('1001/tap/TAPT_ISL_W30LK_L3_R7_R1e6_UD7S_VGm0p2.log')

Every 'd ' line becomes one row. Rows whose length differs from the most common length are dropped.

Column map used in this project
-------------------------------
Transient device-only decks (log ... j.electron j.hole), 5 electrodes gate/source/drain/tap/substrate, o = 1:
    col 0          time
    per electrode e (0=gate, 1=source, 2=drain, 3=tap, 4=substrate): 5 columns starting at o + 5*e
        [o+5e+0] applied V   [o+5e+1] internal V   [o+5e+2] total I   [o+5e+3] electron I   [o+5e+4] hole I
    e.g. drain V = d[:, o+11], drain I = d[:, o+12], source I = d[:, o+7], tap internal V = d[:, o+16], tap I = d[:, o+17]
    probes follow the electrodes in deck order, e.g. VB_left = o+25, VB_right = o+26, V_island = o+27
LEFTONLY decks (4 electrodes, no tap): drain V = o+11, drain I = o+12, source I = o+7, VB_left = o+20
MixedMode *.log_tr.log: read the 'p' header line; for the MM_TAPT_* decks:
    0 time | 1 V(drain node) | 2 V(gate node) | 3 V(tap node) | 4 T | 5-7 I(Vdrain, Vgate, Rtap) | 8-12 I(device drain, source, gate, tap, substrate)
"""
import sys
import numpy as np


def load(fn):
    rows = []
    with open(fn) as f:
        for l in f:
            if l.startswith('d '):
                try:
                    rows.append([float(v) for v in l.split()[1:]])
                except ValueError:
                    pass
    n = max(set(len(r) for r in rows), key=[len(r) for r in rows].count)
    return np.array([r for r in rows if len(r) == n])


if __name__ == '__main__':
    for fn in sys.argv[1:]:
        d = load(fn)
        print(fn, d.shape)
