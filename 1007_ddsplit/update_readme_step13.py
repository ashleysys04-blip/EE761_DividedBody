#!/usr/bin/env python3
"""Write README Step 13 ('왜 래치가 일어나나: .str 분석') between <!-- STEP13-AUTO-START --> / <!-- STEP13-AUTO-END -->.
Inputs: mech_<name>.dat (barrier, body holes; mech_ddsplit.py) and mech2_<name>.dat (hole balance; mech2_ddsplit.py)
for the dense-snapshot runs DDS_BASE_SNAP, DDS_TE8_SNAP, DDS_TE8_XS60_SNAP. Transitions are found automatically:
a latch ON/OFF = consecutive snapshots of the same sweep where that STL's impact-ionization hole current changes > 100x,
its own source->body barrier collapses / recovers by > 0.2 eV, and the current on the 'on' side is > 1e-11 A."""
import os, datetime
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
README = os.path.join(root, 'README.md'); A, B = '<!-- STEP13-AUTO-START -->', '<!-- STEP13-AUTO-END -->'
RUNS = [('DDS_BASE_SNAP', '기준 (Si 수명 1e-7 s, 섬 50 %)'), ('DDS_TE8_SNAP', 'Si 수명 1e-8 s (급격한 꺼짐)'),
        ('DDS_TE8_XS60_SNAP', 'Si 수명 1e-8 s + 섬 60 % (분리된 두 사각형)')]

def load(name):
    m1, m2 = os.path.join(here, f'mech_{name}.dat'), os.path.join(here, f'mech2_{name}.dat')
    if not (os.path.exists(m1) and os.path.exists(m2)): return None
    a = {int(l.split()[0]): l.split() for l in open(m1) if not l.startswith('#')}
    b = {int(l.split()[0]): l.split() for l in open(m2) if not l.startswith('#')}
    rows = []
    for k in sorted(set(a) & set(b)):
        p, q = a[k], b[k]
        rows.append(dict(k=k, sw=p[1], v=float(p[2]), bL=float(p[3]), pL=float(p[4]), bR=float(p[5]), pR=float(p[6]),
                         EL=float(q[3]), IiiL=float(q[4]), RbL=float(q[5]), RsL=float(q[6]), IeL=float(q[7]), ML=float(q[8]),
                         ER=float(q[9]), IiiR=float(q[10]), RbR=float(q[11]), RsR=float(q[12]), IeR=float(q[13]), MR=float(q[14])))
    return rows

def transitions(rows):
    out = []
    for side in ('R', 'L'):
        for sw, sign in (('up', +1), ('down', -1)):
            R = [r for r in rows if r['sw'] == sw]
            for r0, r1 in zip(R, R[1:]):
                a, b = max(r0['Iii' + side], 1e-30), max(r1['Iii' + side], 1e-30)
                db = r1['b' + side] - r0['b' + side]            # barrier change of THIS STL (eV)
                on = sign > 0 and b / a > 100 and db < -0.2 and b > 1e-11      # its own barrier collapses at a real current
                off = sign < 0 and a / b > 100 and db > 0.2 and a > 1e-11      # its own barrier is restored
                if on or off:
                    out.append((side, sw, r0, r1))
    return out

def g(x): return '%.2e' % x

L = [A, '', f'*(자동 생성: {datetime.datetime.now():%Y-%m-%d %H:%M} · 코드 `1007_ddsplit/mech_ddsplit.py`, `mech2_ddsplit.py`, `update_readme_step13.py`)*', '']
for name, lab in RUNS:
    rows = load(name)
    if not rows: continue
    L += [f'### {lab}: `{name}`', '']
    for f, cap in ((f'fig/mech_{name}.png', '채널(y = 25 nm)의 전위·정공 분포와 STL별 장벽, body 정공'),
                   (f'fig/mech2_{name}.png', 'STL별 정공 수지: impact ionization 생성 vs 재결합 (body, 각 STL의 n+ source), 증배 M-1, 최대 전계'),
                   (f'fig/mech2_maps_{name}.png', '정공이 생기는 곳(impact ionization)과 사라지는 곳(재결합)의 2D 지도')):
        if os.path.exists(os.path.join(here, f)):
            L += [f'![](1007_ddsplit/{f})', f'*{cap}. 데이터: `1007_ddsplit/{name}_T_tr_N` (.str), `{name}.log_tr.log` · 코드: `1007_ddsplit/{"mech_ddsplit.py" if "mech_" in f and "mech2" not in f else "mech2_ddsplit.py"}`*', '']
    L += ['| 래치 | 스냅샷 (Vd) | 장벽 (eV) | body 정공 (cm⁻³) | 최대 전계 (V/cm) | impact 정공 전류 I_ii (A) | body 재결합 (A) | n+ source 재결합 (A) | 전자 전류 I_e (A) | M-1 |',
          '|---|---|---|---|---|---|---|---|---|---|']
    for side, sw, r0, r1 in transitions(rows):
        nm = ('오른쪽' if side == 'R' else '왼쪽') + (' ON' if sw == 'up' else ' OFF')
        for r in (r0, r1):
            L.append(f"| {nm} | {r['sw']} {r['v']:g} V | {r['b'+side]:.3f} | {g(r['p'+side])} | {g(r['E'+side])} | {g(r['Iii'+side])} | "
                     f"{g(r['Rb'+side])} | {g(r['Rs'+side])} | {g(r['Ie'+side])} | {r['M'+side]:.3f} |")
    # holding point: last latched snapshot of the left STL on the down sweep
    dn = [r for r in rows if r['sw'] == 'down']
    tr = [t for t in transitions(rows) if t[0] == 'L' and t[1] == 'down']
    if tr:
        r = tr[0][2]; frac = (r['RbL'] + r['RsL']) / max(r['IiiL'], 1e-30)
        L += ['', f"왼쪽 STL이 켜져 있는 마지막 스냅샷({r['v']:g} V): 전자 전류 {g(r['IeL'])} A (= 유지 전류), impact 정공 {g(r['IiiL'])} A 중 "
              f"**{100*frac:.0f} %가 재결합**으로 사라짐 → 나머지만 body를 순방향으로 유지하는 base 전류가 된다."]
    L.append('')
L.append(B)
block = '\n'.join(L)
s = open(README).read()
if A in s:
    s = s[:s.index(A)] + block + s[s.index(B) + len(B):]
else:
    s = s.replace('<!-- STEP13-AUTO-PLACEHOLDER -->', block)
open(README, 'w').write(s)
print('Step 13 block written')
