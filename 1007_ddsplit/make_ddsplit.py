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
    # ---- batch 3 (10/08): sharpen the 2nd-latch turn-off + dense snapshots for the mechanism ----
    ('BASE_SNAP', 'base with dense snapshots around both latches (mechanism)',
     {'UP': [2.0, 2.2, 2.24, 2.26, 2.3, 2.5, 3.0, 3.2, 3.28, 3.32, 3.4, 4.0],
      'DN': [4.0, 3.0, 2.8, 2.6, 2.5, 2.4, 2.3, 2.2, 2.1, 2.0, 1.6, 1.4, 1.3, 1.2, 1.1, 1.0]}),
    ('RD1e4', 'drain series resistor 1e4 Ohm (load line)', {'RD': '1e4'}),
    ('RD3e4', 'drain series resistor 3e4 Ohm (load line)', {'RD': '3e4'}),
    ('RD1e5', 'drain series resistor 1e5 Ohm (load line)', {'RD': '1e5'}),
    ('TE1em8', 'Si carrier lifetime 1e-8 s (base 1e-7)', {'TE': '1e-8'}),
    ('TE1em9', 'Si carrier lifetime 1e-9 s (base 1e-7)', {'TE': '1e-9'}),
    ('RD3e4_TE1em8', 'drain resistor 3e4 Ohm + Si lifetime 1e-8 s', {'RD': '3e4', 'TE': '1e-8'}),
    # ---- batch 4 (10/09): built on the sharp turn-off condition (Si lifetime 1e-8 s) ----
    ('TE5em9', 'Si carrier lifetime 5e-9 s', {'TE': '5e-9'}),
    ('TE2em8', 'Si carrier lifetime 2e-8 s', {'TE': '2e-8'}),
    ('TE5em8', 'Si carrier lifetime 5e-8 s', {'TE': '5e-8'}),
    ('TE8_NL5e17', 'Si lifetime 1e-8 s + left body 5e17', {'TE': '1e-8', 'NL': '5.0e17'}),
    ('TE8_NL5p5e17', 'Si lifetime 1e-8 s + left body 5.5e17', {'TE': '1e-8', 'NL': '5.5e17'}),
    ('TE8_NL6p5e17', 'Si lifetime 1e-8 s + left body 6.5e17', {'TE': '1e-8', 'NL': '6.5e17'}),
    ('TE8_NR5e17', 'Si lifetime 1e-8 s + right body 5e17', {'TE': '1e-8', 'NR': '5.0e17'}),
    ('TE8_NR6e17', 'Si lifetime 1e-8 s + right body 6e17', {'TE': '1e-8', 'NR': '6.0e17'}),
    ('TE8_R3e6', 'Si lifetime 1e-8 s + Rtap 3e6', {'TE': '1e-8', 'R': '3e6'}),
    ('TE8_R3e7', 'Si lifetime 1e-8 s + Rtap 3e7', {'TE': '1e-8', 'R': '3e7'}),
    ('TE8_VG0', 'Si lifetime 1e-8 s + Vg 0 V', {'TE': '1e-8', 'VG': 0.0}),
    ('TE8_VGm0p1', 'Si lifetime 1e-8 s + Vg -0.1 V', {'TE': '1e-8', 'VG': -0.1}),
    ('TE8_XS60', 'Si lifetime 1e-8 s + island at 60 % of Lg', {'TE': '1e-8', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE8_WISL50', 'Si lifetime 1e-8 s + island 50 nm', {'TE': '1e-8', 'SET': {'Wisl': '0.05'}}),
    ('TE8_TAU1em11', 'Si lifetime 1e-8 s + island lifetime 1e-11 s', {'TE': '1e-8', 'TAU': '1e-11'}),
    ('TE8_NR6e17_NL5p5e17', 'Si lifetime 1e-8 s + right 6e17 + left 5.5e17 (pull both latches down)', {'TE': '1e-8', 'NR': '6.0e17', 'NL': '5.5e17'}),
    ('TE8_NR5e17_NL5e17', 'Si lifetime 1e-8 s + right 5e17 + left 5e17', {'TE': '1e-8', 'NR': '5.0e17', 'NL': '5.0e17'}),
    ('TE8_VG0_NL5p5e17', 'Si lifetime 1e-8 s + Vg 0 V + left 5.5e17', {'TE': '1e-8', 'VG': 0.0, 'NL': '5.5e17'}),
    ('TE8_SNAP', 'Si lifetime 1e-8 s with dense snapshots around the turn-off (mechanism)',
     {'TE': '1e-8', 'UP': [2.8, 2.9, 2.94, 2.97, 3.0, 3.5, 3.9, 3.93, 3.96, 4.0, 4.5],
      'DN': [4.5, 4.0, 3.5, 3.2, 3.0, 2.9, 2.8, 2.78, 2.76, 2.74, 2.72, 2.7, 2.6, 2.0, 1.8, 1.72, 1.6]}),
    # ---- batch 5 (10/09): two separated, abrupt rectangles (built on TE8_XS60) ----
    ('TE8_XS55', 'Si lifetime 1e-8 s + island at 55 % of Lg', {'TE': '1e-8', 'SET': {'Xsplit': '$Lsd+$Lg*0.55'}}),
    ('TE8_XS65', 'Si lifetime 1e-8 s + island at 65 % of Lg', {'TE': '1e-8', 'SET': {'Xsplit': '$Lsd+$Lg*0.65'}}),
    ('TE8_XS70', 'Si lifetime 1e-8 s + island at 70 % of Lg', {'TE': '1e-8', 'SET': {'Xsplit': '$Lsd+$Lg*0.70'}}),
    ('TE8_XS60_NL5e17', 'lifetime 1e-8 s + island 60 % + left body 5e17', {'TE': '1e-8', 'NL': '5.0e17', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE8_XS60_NL5p5e17', 'lifetime 1e-8 s + island 60 % + left body 5.5e17', {'TE': '1e-8', 'NL': '5.5e17', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE8_XS60_VG0', 'lifetime 1e-8 s + island 60 % + Vg 0 V', {'TE': '1e-8', 'VG': 0.0, 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE8_XS60_VGm0p1', 'lifetime 1e-8 s + island 60 % + Vg -0.1 V', {'TE': '1e-8', 'VG': -0.1, 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE8_XS60_NR8e17', 'lifetime 1e-8 s + island 60 % + right body 8e17', {'TE': '1e-8', 'NR': '8.0e17', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE8_XS60_NR1e18', 'lifetime 1e-8 s + island 60 % + right body 1e18', {'TE': '1e-8', 'NR': '1.0e18', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE8_XS60_RD1e5', 'lifetime 1e-8 s + island 60 % + drain series R 1e5 (flat top)', {'TE': '1e-8', 'RD': '1e5', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE8_XS60_RD3e5', 'lifetime 1e-8 s + island 60 % + drain series R 3e5 (flat top)', {'TE': '1e-8', 'RD': '3e5', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE8_XS60_RD1e6', 'lifetime 1e-8 s + island 60 % + drain series R 1e6 (flat top)', {'TE': '1e-8', 'RD': '1e6', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE5em9_XS60', 'Si lifetime 5e-9 s + island 60 %', {'TE': '5e-9', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE2em8_XS60', 'Si lifetime 2e-8 s + island 60 %', {'TE': '2e-8', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE8_XS60_NL5p5e17_RD3e5', 'lifetime 1e-8 s + island 60 % + left 5.5e17 + drain R 3e5', {'TE': '1e-8', 'NL': '5.5e17', 'RD': '3e5', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'}}),
    ('TE8_XS65_NL5e17_RD3e5', 'lifetime 1e-8 s + island 65 % + left 5e17 + drain R 3e5', {'TE': '1e-8', 'NL': '5.0e17', 'RD': '3e5', 'SET': {'Xsplit': '$Lsd+$Lg*0.65'}}),
    ('TE8_XS60_SNAP', 'Si lifetime 1e-8 s + island 60 % with dense snapshots around both loops (mechanism of the two-rectangle device)',
     {'TE': '1e-8', 'SET': {'Xsplit': '$Lsd+$Lg*0.60'},
      'UP': [1.3, 1.4, 1.44, 1.46, 1.5, 2.0, 3.0, 4.0, 4.6, 4.75, 4.8, 5.0],
      'DN': [5.0, 4.0, 3.0, 2.7, 2.6, 2.58, 2.56, 2.54, 2.5, 2.0, 1.5, 1.3, 1.25, 1.22, 1.2, 1.0]}),
]

for tag, desc, ch in SPLITS:
    name = f'DDS_{tag}'
    if os.path.exists(name + '.in'):
        continue
    RATE = ch.get('RATE', RATE0)
    up_l, dn_l = ch.get('UP', UP), ch.get('DN', DN)
    s = src.replace(old, name)
    rep = []
    for var, val in ch.get('SET', {}).items():
        line = [l for l in s.split('\n') if l.startswith(f'set {var} = ')][0]
        rep.append((line, f'set {var} = {val}'))
    if 'R' in ch: rep.append(('Rtap   3 0 1e7', f'Rtap   3 0 {ch["R"]}'))
    if 'NL' in ch: rep.append(('doping uniform conc=6.0e17 p.type x.min=$Lsd x.max=$XiL', f'doping uniform conc={ch["NL"]} p.type x.min=$Lsd x.max=$XiL'))
    if 'NR' in ch: rep.append(('doping uniform conc=7.0e17 p.type x.min=$XiR', f'doping uniform conc={ch["NR"]} p.type x.min=$XiR'))
    if 'RD' in ch:   # source drives node 4, drain series resistor 4 -> 1 (device drain stays on node 1)
        rep += [('Vdrain 1 0 pwl', 'Vdrain 4 0 pwl'), ('Rtap   3 0', f'Rdrain 4 1 {ch["RD"]}\nRtap   3 0'),
                ('.nodeset v(1)=0', '.nodeset v(4)=0 v(1)=0')]
    if 'TE' in ch:
        rep += [('set te = 1e-7', f'set te = {ch["TE"]}'), ('set tp = 1e-7', f'set tp = {ch["TE"]}')]
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
    s = s.replace('pwl 0, 0, 1.071429e-02, 7.5, 2.142857e-02, 0', f'pwl 0, 0, {tpk:.6e}, {VMAX}, {tend:.6e}, 0')
    s = s.replace('.tran 1e-9 2.142857e-02', f'.tran 1e-9 {tend:.6e}')
    ts = [v / RATE for v in up_l] + [tpk + (VMAX - v) / RATE for v in dn_l]
    lines = s.split('\n')
    lines = [f'.save master={name}_T tsave=' + ' '.join(f'{x:.6e}' for x in ts) if l.startswith('.save master=') else l for l in lines]
    hdr = [f'# {name} : DD MixedMode split. Changed vs base: {desc}.',
           '# Generated by 1007_ddsplit/make_ddsplit.py from 1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_W05_VGm0p2.in',
           f'# Sweep 0 -> {VMAX} -> 0 V at {RATE/1000:g} V/ms. Snapshots ({name}_T_tr_N): up ' + ', '.join(map(str, up_l)) + ' / down ' + ', '.join(map(str, dn_l)) + ' V']
    open(name + '.in', 'w').write('\n'.join(hdr + lines))
    print(name, '|', desc)
