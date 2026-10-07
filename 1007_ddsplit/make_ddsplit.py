#!/usr/bin/env python3
# Generates the drift-diffusion MixedMode split decks (DDS_*.in) from the double-latch base deck.
# Base: ../1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_W05_VGm0p2.in
#   left body 6e17 | n+ island 30 nm, tau 1e-12 s, tapped | right body 7e17, Rtap 1e7 Ohm, Vg -0.2 V, width 0.5 um, fine mesh, DD
# One variable is changed per deck. Sweep: 0 -> 6 -> 0 V at 0.7 V/ms (pwl source), .str snapshots at fixed Vd.
import os
BASE = '../1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_W05_VGm0p2'
src = open(BASE + '.in').read()
old = os.path.basename(BASE)
RATE0, VMAX = 700.0, 6.0
UP = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0]
DN = [5.0, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.0]

def gate_lines(vg):
    if vg == 0.0:
        return 'solve vgate=0'
    return f'solve vfinal={vg} vstep={-0.05 if vg < 0 else 0.05} name=gate'

SPLITS = [  # tag, description, dict of changes
    ('BASE', 'base (same as the double-latch deck, 0-6-0 V sweep)', {}),
    ('R1e6', 'Rtap 1e6 Ohm', {'R': '1e6'}),
    ('R3e6', 'Rtap 3e6 Ohm', {'R': '3e6'}),
    ('R3e7', 'Rtap 3e7 Ohm', {'R': '3e7'}),
    ('R1e8', 'Rtap 1e8 Ohm', {'R': '1e8'}),
    ('NL5e17', 'left body 5e17', {'NL': '5.0e17'}),
    ('NL7e17', 'left body 7e17', {'NL': '7.0e17'}),
    ('NR6e17', 'right body 6e17', {'NR': '6.0e17'}),
    ('NR8e17', 'right body 8e17', {'NR': '8.0e17'}),
    ('NR1e18', 'right body 1e18', {'NR': '1.0e18'}),
    ('VGm0p5', 'Vg -0.5 V', {'VG': -0.5}),
    ('VG0', 'Vg 0 V', {'VG': 0.0}),
    ('TAU1em11', 'island + neck lifetime 1e-11 s', {'TAU': '1e-11'}),
    ('TAU1em10', 'island + neck lifetime 1e-10 s', {'TAU': '1e-10'}),
    # ---- batch 2 (added 10/07) ----
    ('R3e5', 'Rtap 3e5 Ohm', {'R': '3e5'}),
    ('R3e8', 'Rtap 3e8 Ohm', {'R': '3e8'}),
    ('NL4e17', 'left body 4e17', {'NL': '4.0e17'}),
    ('NL5p5e17', 'left body 5.5e17', {'NL': '5.5e17'}),
    ('NL6p5e17', 'left body 6.5e17', {'NL': '6.5e17'}),
    ('NL8e17', 'left body 8e17', {'NL': '8.0e17'}),
    ('NR5e17', 'right body 5e17', {'NR': '5.0e17'}),
    ('NR6p5e17', 'right body 6.5e17', {'NR': '6.5e17'}),
    ('NR7p5e17', 'right body 7.5e17', {'NR': '7.5e17'}),
    ('NR9e17', 'right body 9e17', {'NR': '9.0e17'}),
    ('VGm1p0', 'Vg -1.0 V', {'VG': -1.0}),
    ('VGm0p3', 'Vg -0.3 V', {'VG': -0.3}),
    ('VGm0p1', 'Vg -0.1 V', {'VG': -0.1}),
    ('VGp0p2', 'Vg +0.2 V', {'VG': 0.2}),
    ('TAU1em9', 'island + neck lifetime 1e-9 s', {'TAU': '1e-9'}),
    ('TAU1em13', 'island + neck lifetime 1e-13 s', {'TAU': '1e-13'}),
    ('WISL20', 'island width 20 nm', {'SET': {'Wisl': '0.02'}}),
    ('WISL50', 'island width 50 nm', {'SET': {'Wisl': '0.05'}}),
    ('WISL100', 'island width 100 nm', {'SET': {'Wisl': '0.10'}}),
    ('XS40', 'island centre at 40 % of Lg (left body shorter)', {'SET': {'Xsplit': '$Lsd+$Lg*0.40'}}),
    ('XS60', 'island centre at 60 % of Lg (left body longer)', {'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TSI30', 'Si film 30 nm', {'SET': {'tsi': '0.03'}}),
    ('TSI70', 'Si film 70 nm', {'SET': {'tsi': '0.07'}}),
    ('RATE0p07', 'ramp 0.07 V/ms (10x slower)', {'RATE': 70.0}),
    ('RATE7', 'ramp 7 V/ms (10x faster)', {'RATE': 7000.0}),
    ('NL5p5e17_R3e6', 'left 5.5e17 and Rtap 3e6', {'NL': '5.5e17', 'R': '3e6'}),
    ('NL5p5e17_R3e7', 'left 5.5e17 and Rtap 3e7', {'NL': '5.5e17', 'R': '3e7'}),
    ('NL6p5e17_R3e6', 'left 6.5e17 and Rtap 3e6', {'NL': '6.5e17', 'R': '3e6'}),
    ('NL6p5e17_R3e7', 'left 6.5e17 and Rtap 3e7', {'NL': '6.5e17', 'R': '3e7'}),
]

for tag, desc, ch in SPLITS:
    name = f'DDS_{tag}'
    if os.path.exists(name + '.in'):
        continue
    RATE = ch.get('RATE', RATE0)
    s = src.replace(old, name)
    rep = []
    for var, val in ch.get('SET', {}).items():
        line = [l for l in s.split('\n') if l.startswith(f'set {var} = ')][0]
        rep.append((line, f'set {var} = {val}'))
    if 'R' in ch: rep.append(('Rtap   3 0 1e7', f'Rtap   3 0 {ch["R"]}'))
    if 'NL' in ch: rep.append(('doping uniform conc=6.0e17 p.type x.min=$Lsd x.max=$XiL', f'doping uniform conc={ch["NL"]} p.type x.min=$Lsd x.max=$XiL'))
    if 'NR' in ch: rep.append(('doping uniform conc=7.0e17 p.type x.min=$XiR', f'doping uniform conc={ch["NR"]} p.type x.min=$XiR'))
    if 'TAU' in ch:
        for r in ('10', '9'):
            rep.append((f'material region={r} taun0=1e-12 taup0=1e-12', f'material region={r} taun0={ch["TAU"]} taup0={ch["TAU"]}'))
    if 'VG' in ch:
        vg = ch['VG']
        rep += [('solve vfinal=-0.2 vstep=-0.05 name=gate', gate_lines(vg)), ('Vgate  2 0 -0.2', f'Vgate  2 0 {vg}'),
                ('.nodeset v(1)=0 v(2)=-0.2 v(3)=0', f'.nodeset v(1)=0 v(2)={vg} v(3)=0')]
    for a, b in rep:
        assert a in s, (tag, a)
        s = s.replace(a, b)
    # sweep 0 -> VMAX -> 0
    tpk, tend = VMAX / RATE, 2 * VMAX / RATE
    s = s.replace('Vdrain 1 0 pwl 0, 0, 1.071429e-02, 7.5, 2.142857e-02, 0', f'Vdrain 1 0 pwl 0, 0, {tpk:.6e}, {VMAX}, {tend:.6e}, 0')
    s = s.replace('.tran 1e-9 2.142857e-02', f'.tran 1e-9 {tend:.6e}')
    ts = [v / RATE for v in UP] + [tpk + (VMAX - v) / RATE for v in DN]
    lines = s.split('\n')
    lines = [f'.save master={name}_T tsave=' + ' '.join(f'{x:.6e}' for x in ts) if l.startswith('.save master=') else l for l in lines]
    hdr = [f'# {name} : DD MixedMode split. Changed vs base: {desc}.',
           '# Generated by 1007_ddsplit/make_ddsplit.py from 1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_W05_VGm0p2.in',
           f'# Sweep 0 -> {VMAX} -> 0 V at {RATE/1000:g} V/ms. Snapshots ({name}_T_tr_N): up ' + ', '.join(map(str, UP)) + ' / down ' + ', '.join(map(str, DN)) + ' V']
    open(name + '.in', 'w').write('\n'.join(hdr + lines))
    print(name, '|', desc)
