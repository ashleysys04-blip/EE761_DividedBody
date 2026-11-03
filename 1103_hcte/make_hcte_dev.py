#!/usr/bin/env python3
"""Device-only version of the hcte decks (make_hcte.py).

The MixedMode hcte decks HC_* stop at the MixedMode start (11/03: "Unable to trap bias", carrier temperatures
120 K ... 3e4 K at V_D = 0) when the island sits at 60 % of Lg; the same deck with the island at 50 % runs (test
T_XS50_W030). The device section (structure, initial and gate-bias solves with hcte) converges in every case, so here
the transient continues in the device itself, as the earlier hcte runs did (1001/tap/TAPT_*_UD7S_*.in):
tap contact resistance 5e6 Ohm*um (= 1e7 Ohm for the 0.5 um MixedMode width), drain ramped at 0.7 V/ms in segments
that end at the snapshot voltages of HC_* (same .str save points). Currents in the log are per um (MixedMode x 2).
Output decks HCD_*.in. Existing decks are not rewritten."""
import os, re
H = os.path.dirname(os.path.abspath(__file__))
RATE = 700.0
JOBS = [('HC_W030', 4.0), ('HC_W120', 6.0), ('HC_W060', 6.0), ('HC_W120_KILL', 6.0)]   # 11/03: W120, W060 raised to 6 V (hcte 1st latch above 3 V)
for src_name, vmax in JOBS:
    name = src_name.replace('HC_', 'HCD_'); fn = os.path.join(H, name + '.in')
    if os.path.exists(fn):
        print('exists, not rewritten:', name); continue
    s = open(os.path.join(H, src_name + '.in')).read().replace(src_name, name)
    cut = s.index('go atlas simflags="-P 1"\n.begin'); d = s[:cut]
    assert d.count('contact name=substrate\n') == 1
    d = d.replace('contact name=substrate\n', 'contact name=substrate\ncontact name=tap resistance=5e6\n')
    d = d.replace('save outf=%s_VG.str master\n' % name, 'save outf=%s_VG.str\n' % name)
    up = [v for v in (1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0) if v <= vmax]
    dn = [v for v in (5.0, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.0) if v < vmax]
    out = ['\n#### drain ramp 0 -> %g -> 0 V at 0.7 V/ms (device-only transient, tap through contact resistance) ####' % vmax,
           'log outf=%s.log' % name]
    t, v0 = 0.0, 0.0
    for k, v in enumerate(up + dn, 1):
        dt = abs(v - v0) / RATE; t += dt
        out.append('solve vdrain=%g ramptime=%.6e tstop=%.6e tstep=1e-9' % (v, dt, t))
        out.append('save outf=%s_T_tr_%d' % (name, k)); v0 = v
    hdr = ('# %s : device-only transient version of %s (make_hcte_dev.py); hcte, tap resistance 5e6 Ohm*um, 0 -> %g -> 0 V.\n'
           % (name, src_name, vmax))
    open(fn, 'w').write(hdr + d + '\n'.join(out) + '\n\nquit\n'); print('wrote', name)
