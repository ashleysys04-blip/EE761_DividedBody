#!/usr/bin/env python3
"""Control experiment: is the divided-body device anything more than two STLs in series?

Reference device: 1010_sink/SINK_TE8_XS60 (island at 60 % of Lg, tau0_Si 1e-8 s, Si-deep metal core + n+ shell 10 nm,
left body 6e17, right body 7e17, VG -0.2 V, Rtap 1e7 Ohm). Same models and the same 0.7 V/ms ramp.

Two control circuits, each built from TWO separate ATLAS devices wired in MixedMode
(right STL drain = applied drain, right STL source = left STL drain = node 3 = Rtap to GND, both gates on node 2):

  CUT : the reference device cut in half through the middle of the metal core. Every half keeps exactly its own
        geometry, doping and mesh, and half of the core as its internal electrode. The only thing removed is that the
        two halves are one piece of silicon / one gate / one BOX. If CUT == SINK, the device is exactly the series circuit.
  SD  : a realistic discrete pair. The internal node is a normal 500 nm n+ S/D with a top contact on each device
        (gate stops at the body edge). This is the 'two SOI MOSFETs wired together' that a reviewer has in mind.

Decks written here (run CTRL_*_IDVD first: it writes the *_VG.str files the oscillation decks load):
  CTRL_CUT_IDVD.in, CTRL_SD_IDVD.in              Id-Vd, 0 -> 6 -> 0 V at 0.7 V/ms (compare with 1010_sink/SINK_TE8_XS60)
  CTRL_CUT_OSC_R_1n.in, CTRL_CUT_OSC_L_450n.in   current-driven oscillation (compare with 1028_osc/OSC_R_1n, OSC_L_450n)
Analysis: compare_ctrl.py.
"""
import os
H = os.path.dirname(os.path.abspath(__file__))

COMMON = """set Lg = 0.3
set Lsd = 0.5
set tox = 0.02
set tbox = 0.2
set tgate = 0.1
set LT = 300
set Xsplit = $Lsd+$Lg*0.60
set W = 0.5
set tsi = 0.05
set Wisl = 0.03
set shell = 0.01
set XiL = $Xsplit-$Wisl/2
set XiR = $Xsplit+$Wisl/2
set XcL = $XiL+$shell
set XcR = $XiR-$shell
set Ybot = $tsi+$tbox
"""
Y_MESH = """y.mesh loc=-$tox-$tgate spac=0.05
y.mesh loc=-$tox spac=0.005
y.mesh loc=0.00 spac=0.002
y.mesh loc=$tsi/2 spac=0.01
y.mesh loc=$tsi spac=0.005
y.mesh loc=$tsi+0.05 spac=0.02
y.mesh loc=$Ybot-0.03 spac=0.01
y.mesh loc=$Ybot spac=0.005
"""
PHYS = """material material=silicon taun0=1e-8 taup0=1e-8
models print bgn consrh conmob fldmob fermi trap.tunnel bbt.std temp=300
impact selb length.rel
output band.param con.band val.band recomb u.srh u.bbt qtunn.bbt impact e.field traps
method newton climit=100 itlimit=200 trap maxtraps=10
"""
# After .end with two A-devices the manual (Atlas User's Manual 13.2.3) asks for DEVICE= on every device statement.
PHYS_MM = ''.join(f"""material device={a} material=silicon taun0=1e-8 taup0=1e-8
models device={a} print bgn consrh conmob fldmob fermi trap.tunnel bbt.std temp=300
impact device={a} selb length.rel
""" for a in ('Aright', 'Aleft')) + """output band.param con.band val.band recomb u.srh u.bbt qtunn.bbt impact e.field traps
method newton climit=100 itlimit=200 trap maxtraps=10
"""

# ---------------- device bodies: (x mesh, regions, electrodes, doping, probes) ----------------
# CUT halves: x mesh copied from SINK_TE8_XS60 and cut at Xsplit (centre of the 10 nm metal core).
CUT_L = """x.mesh loc=0.00 spac=0.1
x.mesh loc=$Lsd spac=0.005
x.mesh loc=$XiL spac=0.003
x.mesh loc=$XcL spac=0.001
x.mesh loc=$Xsplit spac=0.001
""" + Y_MESH + """
region num=1 x.min=$Lsd x.max=$Xsplit y.max=-$tox poly
region num=2 x.min=$Lsd x.max=$Xsplit y.max=0 y.min=-$tox oxide
region num=3 y.min=0 y.max=$tsi silicon
region num=4 x.min=0 x.max=$Lsd y.min=0 y.max=$tsi silicon
region num=5 y.min=$tsi y.max=$Ybot oxide
region num=6 x.min=0 x.max=$Lsd y.max=0 material=vacuum

electrode name=gate x.min=$Lsd x.max=$Xsplit y.min=-$tox y.max=-$tox
electrode name=source x.max=$Lsd y.min=0 y.max=0
# internal node = left half of the metal core (Si-film deep)
electrode name=drain x.min=$XcL x.max=$Xsplit y.min=0 y.max=$tsi
electrode name=substrate x.max=$XiL-0.03 y.min=$Ybot y.max=$Ybot

doping uniform conc=6.0e17 p.type x.min=$Lsd x.max=$XiL y.min=0 y.max=$tsi
doping uniform conc=1e20 n.type x.min=$XiL x.max=$Xsplit y.min=0 y.max=$tsi
doping uniform conc=1e20 n.type reg=4
doping uniform conc=1e21 n.type reg=1
"""
CUT_R = """x.mesh loc=$Xsplit spac=0.001
x.mesh loc=$XcR spac=0.001
x.mesh loc=$XiR spac=0.003
x.mesh loc=0.760 spac=0.003
x.mesh loc=0.785 spac=0.001
x.mesh loc=$Lsd+$Lg spac=0.001
x.mesh loc=0.815 spac=0.003
x.mesh loc=$Lsd+$Lg+$Lsd spac=0.1
""" + Y_MESH + """
region num=1 x.min=$Xsplit x.max=$Lsd+$Lg y.max=-$tox poly
region num=2 x.min=$Xsplit x.max=$Lsd+$Lg y.max=0 y.min=-$tox oxide
region num=3 y.min=0 y.max=$tsi silicon
region num=4 x.min=$Lsd+$Lg y.min=0 y.max=$tsi silicon
region num=5 y.min=$tsi y.max=$Ybot oxide
region num=6 x.min=$Lsd+$Lg y.max=0 material=vacuum

electrode name=gate x.min=$Xsplit x.max=$Lsd+$Lg y.min=-$tox y.max=-$tox
# internal node = right half of the metal core (Si-film deep)
electrode name=source x.min=$Xsplit x.max=$XcR y.min=0 y.max=$tsi
electrode name=drain x.min=$Lsd+$Lg y.min=0 y.max=0
electrode name=substrate x.min=$XiR+0.03 y.min=$Ybot y.max=$Ybot

doping uniform conc=1e20 n.type x.min=$Xsplit x.max=$XiR y.min=0 y.max=$tsi
doping uniform conc=7.0e17 p.type x.min=$XiR x.max=$Lsd+$Lg y.min=0 y.max=$tsi
doping uniform conc=1e20 n.type reg=4
doping uniform conc=1e21 n.type reg=1
"""
# SD: same bodies, but the internal node is a conventional 500 nm n+ S/D with a top contact. Gate = body only.
# Drain-junction mesh of the left STL kept at 3 nm as in SINK_TE8_XS60, so SD vs SINK is not a mesh effect.
SD_L = """set XdE = $XiL+$Lsd
x.mesh loc=0.00 spac=0.1
x.mesh loc=$Lsd spac=0.005
x.mesh loc=$XiL-0.02 spac=0.003
x.mesh loc=$XiL spac=0.003
x.mesh loc=$XiL+0.02 spac=0.003
x.mesh loc=$XdE spac=0.1
""" + Y_MESH + """
region num=1 x.min=$Lsd x.max=$XiL y.max=-$tox poly
region num=2 x.min=$Lsd x.max=$XiL y.max=0 y.min=-$tox oxide
region num=3 y.min=0 y.max=$tsi silicon
region num=4 x.min=0 x.max=$Lsd y.min=0 y.max=$tsi silicon
region num=5 x.min=$XiL x.max=$XdE y.min=0 y.max=$tsi silicon
region num=6 y.min=$tsi y.max=$Ybot oxide
region num=7 x.min=0 x.max=$Lsd y.max=0 material=vacuum
region num=8 x.min=$XiL x.max=$XdE y.max=0 material=vacuum

electrode name=gate x.min=$Lsd x.max=$XiL y.min=-$tox y.max=-$tox
electrode name=source x.max=$Lsd y.min=0 y.max=0
electrode name=drain x.min=$XiL y.min=0 y.max=0
electrode name=substrate x.max=$XiL-0.03 y.min=$Ybot y.max=$Ybot

doping uniform conc=6.0e17 p.type x.min=$Lsd x.max=$XiL y.min=0 y.max=$tsi
doping uniform conc=1e20 n.type reg=4
doping uniform conc=1e20 n.type reg=5
doping uniform conc=1e21 n.type reg=1
"""
SD_R = """set XsB = $XiR-$Lsd
x.mesh loc=$XsB spac=0.1
x.mesh loc=$XiR-0.02 spac=0.003
x.mesh loc=$XiR spac=0.003
x.mesh loc=0.760 spac=0.003
x.mesh loc=0.785 spac=0.001
x.mesh loc=$Lsd+$Lg spac=0.001
x.mesh loc=0.815 spac=0.003
x.mesh loc=$Lsd+$Lg+$Lsd spac=0.1
""" + Y_MESH + """
region num=1 x.min=$XiR x.max=$Lsd+$Lg y.max=-$tox poly
region num=2 x.min=$XiR x.max=$Lsd+$Lg y.max=0 y.min=-$tox oxide
region num=3 y.min=0 y.max=$tsi silicon
region num=4 x.max=$XiR y.min=0 y.max=$tsi silicon
region num=5 x.min=$Lsd+$Lg y.min=0 y.max=$tsi silicon
region num=6 y.min=$tsi y.max=$Ybot oxide
region num=7 x.max=$XiR y.max=0 material=vacuum
region num=8 x.min=$Lsd+$Lg y.max=0 material=vacuum

electrode name=gate x.min=$XiR x.max=$Lsd+$Lg y.min=-$tox y.max=-$tox
electrode name=source x.max=$XiR y.min=0 y.max=0
electrode name=drain x.min=$Lsd+$Lg y.min=0 y.max=0
electrode name=substrate x.min=$XiR+0.03 y.min=$Ybot y.max=$Ybot

doping uniform conc=7.0e17 p.type x.min=$XiR x.max=$Lsd+$Lg y.min=0 y.max=$tsi
doping uniform conc=1e20 n.type reg=4
doping uniform conc=1e20 n.type reg=5
doping uniform conc=1e21 n.type reg=1
"""
PROBE = {'L': 'probe name=VB_left  potential x=0.5675 y=0.035\nprobe name=PH_left  P.CONC x=0.5675 y=0.035\n',
         'R': 'probe name=VB_right potential x=0.7325 y=0.035\nprobe name=PH_right P.CONC x=0.7325 y=0.035\n'}


def structure(tag, side, body):
    """One ATLAS device: build, solve VG = -0.2 V, save <tag>_<side>_VG.str for MixedMode."""
    name = f'{tag}_{side}'
    return f"""#### ---------- {name}: {'left STL (source -> internal node)' if side == 'L' else 'right STL (internal node -> drain)'} ----------
go atlas simflags="-P 1"
{COMMON}
mesh space.mult = 1.0 width = $W
{body}
save outf={name}_INIT.str

contact name=drain
contact name=source
contact name=substrate

{PROBE[side]}
{PHYS}
solve vfinal=-0.2 vstep=-0.05 name=gate
save outf={name}_VG.str master
"""


def circuit(name, tag, drive, tstop, tsave):
    """MixedMode block: right STL on top, left STL below, internal node 3 -> Rtap -> GND, gates tied on node 2."""
    return f"""#### ---------- MixedMode: two separate devices in series ----------
go atlas simflags="-P 1"
.begin
{drive}
Vgate  2 0 -0.2
Rtap   3 0 1e7
Aright 1=drain 3=source 2=gate 0=substrate width=0.5 infile={tag}_R_VG.str
Aleft  3=drain 0=source 2=gate 0=substrate width=0.5 infile={tag}_L_VG.str
.nodeset v(1)=0 v(2)=-0.2 v(3)=0
.numeric lte=0.3 toltr=1e-5
.options print relpot
.log outfile={name}.log
.tran 1e-9 {tstop:g}
.save master={name}_T tsave={tsave}
.end

# same models as the reference deck, given once per device
{PHYS_MM}
go atlas simflags="-P 1"
quit
"""


IDVD_DRIVE = 'Vdrain 1 0 pwl 0, 0, 8.571429e-03, 6.0, 1.714286e-02, 0'   # 0 -> 6 -> 0 V at 0.7 V/ms, as SINK_TE8_XS60
IDVD_TSAVE = '2.142857e-03 2.857143e-03 3.571429e-03 4.285714e-03 5.000000e-03 5.714286e-03 7.142857e-03 8.571429e-03 1.000000e-02 1.142857e-02 1.285714e-02 1.428571e-02 1.571429e-02 1.714286e-02'
OSC = [  # name, I_in (A), C (F), t_stop (s), snapshots -- identical to 1028_osc/make_osc.py
    ('OSC_R_1n',   1e-9,   1e-12,    5e-3,  '1e-3 2e-3 3e-3 4e-3 5e-3'),
    ('OSC_L_450n', 4.5e-7, 2.25e-10, 15e-3, '3e-3 5e-3 7e-3 9e-3 11e-3 13e-3 15e-3')]
HDR = """# {n} : control experiment, generated by 1029_ctrl/make_ctrl.py
# {what}
# Reference: {ref}
# Two separate ATLAS devices (Aright, Aleft) in MixedMode: Vd node 1 -> right STL -> node 3 (Rtap 1e7 -> GND) -> left STL -> GND.
# Gates tied (node 2, -0.2 V). Same models, tau0_Si 1e-8 s, width 0.5 um.
"""
WHAT = {'CUT': 'CUT: SINK_TE8_XS60 cut in half through the centre of the metal core (same geometry/doping/mesh per half).',
        'SD': 'SD: realistic discrete pair, internal node = 500 nm n+ S/D with a top contact on each device; gate over the body only.'}
BODY = {'CUT': (CUT_L, CUT_R), 'SD': (SD_L, SD_R)}

jobs = []
for tag in ('CUT', 'SD'):
    n = f'CTRL_{tag}_IDVD'
    deck = (HDR.format(n=n, what=WHAT[tag], ref='1010_sink/SINK_TE8_XS60 (Id-Vd, 0 -> 6 -> 0 V at 0.7 V/ms)')
            + structure(f'CTRL_{tag}', 'L', BODY[tag][0]) + structure(f'CTRL_{tag}', 'R', BODY[tag][1])
            + circuit(n, f'CTRL_{tag}', IDVD_DRIVE, 1.714286e-02, IDVD_TSAVE))
    jobs.append((n, deck))
for o, i, c, t, ts in OSC:   # oscillation only for CUT (the strict equivalence test); reuses CTRL_CUT_{L,R}_VG.str
    n = f'CTRL_CUT_{o}'
    deck = (HDR.format(n=n, what=WHAT['CUT'] + f' Constant {i:g} A into the drain node, C = {c:g} F. Run CTRL_CUT_IDVD first (it writes the _VG.str files).',
                       ref=f'1028_osc/{o}')
            + circuit(n, 'CTRL_CUT', f'Idrain 1 0 pwl 0, 0, 1e-6, {-i:g}\nCdrain 1 0 {c:g}', t, ts))
    jobs.append((n, deck))

for n, deck in jobs:
    fn = os.path.join(H, n + '.in')
    if os.path.exists(fn):
        print('exists, not rewritten:', n); continue
    open(fn, 'w').write(deck); print('wrote', n + '.in')
