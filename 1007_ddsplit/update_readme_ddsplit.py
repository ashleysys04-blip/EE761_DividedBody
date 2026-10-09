#!/usr/bin/env python3
"""Rewrite the auto-generated DD split results block in ../README.md
(between <!-- DDSPLIT-AUTO-START --> and <!-- DDSPLIT-AUTO-END -->) from ddsplit_summary.dat, mech_*.dat and fig/."""
import os, re, glob, datetime
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
README = os.path.join(root, 'README.md')
A, B = '<!-- DDSPLIT-AUTO-START -->', '<!-- DDSPLIT-AUTO-END -->'
REL = '1007_ddsplit'

def desc(name):
    try:
        l = open(os.path.join(here, name + '.in')).readline()
        return l.split('Changed vs base:')[1].strip().rstrip('.')
    except Exception:
        return ''

def done(name):
    q = os.path.join(here, name + '.queue')
    return os.path.exists(q) and 'end' in open(q).read()

rows = []
for l in open(os.path.join(here, 'ddsplit_summary.dat')):
    if l.startswith('#') or not l.strip(): continue
    p = l.split()
    rows.append(dict(name=p[0], n=int(p[1]), v1=float(p[2]), d1=float(p[3]), v2=float(p[4]), d2=float(p[5]),
                     offl=float(p[6]), offr=float(p[7]), w=float(p[8]), nj=int(p[9])))
decks = sorted(os.path.basename(f)[:-3] for f in glob.glob(os.path.join(here, 'DDS_*.in')))
ndone = sum(done(d) for d in decks)
f = lambda x, fmt='%.3f': '–' if x != x else fmt % x

def table(names):
    out = ['| 덱 | 바꾼 것 | 1번째 ON (V) | 점프 (dec) | 2번째 ON (V) | 점프 (dec) | 2번째 OFF (V) | 1번째 OFF (V) | OFF 폭 (V) | 판정 |',
           '|---|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        if r['name'] not in names: continue
        both = r['v1'] == r['v1'] and r['v2'] == r['v2']
        gap = abs(r['v2'] - r['v1']) if both else float('nan')
        verdict = ('합쳐짐 (사실상 한 번)' if gap < 0.01 else ('래치 2번 (간격 %.2f V, 거의 붙음)' % gap if gap < 0.1 else '래치 2번')) if both else '확인 필요'
        out.append(f"| `{r['name']}` | {desc(r['name']) or 'base'} | {f(r['v1'])} | {f(r['d1'], '%.1f')} | {f(r['v2'])} | {f(r['d2'], '%.1f')} | "
                   f"{f(r['offl'], '%.2f')} | {f(r['offr'], '%.2f')} | {f(r['w'])} | {verdict} |")
    return '\n'.join(out)

def rect_table():
    fn = os.path.join(here, 'ddsplit_rect.dat')
    if not os.path.exists(fn): return ''
    rr = {l.split()[0]: l.split()[1:] for l in open(fn) if not l.startswith('#') and l.strip()}
    names = [n for n in rr if re.match(r'DDS_(TE8_XS|TE5em9_XS|TE2em8_XS|XS60$|TE1em8$)', n)]
    out = ['| 덱 | 바꾼 것 | 루프 1 폭 (V) | 루프 2 폭 (V) | 루프 간격 (V) | 2번째 OFF 폭 (V) | 1번째 OFF 폭 (V) | 상태 II 기울기 (dec) | 상태 III 기울기 (dec) |',
           '|---|---|---|---|---|---|---|---|---|']
    for n in names:
        p = rr[n]
        out.append(f"| `{n}` | {desc(n) or 'base'} | " + ' | '.join(p[:5]) + ' | ' + ' | '.join(p[5:7]) + ' |')
    out.append('')
    out.append('루프 간격 > 0이면 두 루프가 겹치지 않음. OFF 폭이 0에 가까울수록 급격히 꺼짐. 기울기(dec)는 그 상태에서 |Id|가 변하는 자릿수 (작을수록 평평한 윗변).')
    return '\n'.join(out)

RECT_GROUPS = [   # (key, title, [(deck, value label)], conclusion)
 ('XS', '① 섬 위치 (Lg 대비 %)', [('DDS_TE8_XS55', '55 %'), ('DDS_TE8_XS60', '60 % (기준)'), ('DDS_TE8_XS65', '65 %'), ('DDS_TE8_XS70', '70 %')],
  '섬을 drain 쪽으로 옮길수록 오른쪽 body가 짧아져 **루프 1이 낮아지고 좁아진다** (55 %: 1.49–2.22 V → 60 %: 1.23–1.45 V). '
  '65 %, 70 %에서는 오른쪽 body(75, 60 nm)가 너무 짧아 **오른쪽 래치가 사라지고** 연속적으로 켜진다. 루프 2는 조금씩 올라간다. → 두 래치를 유지하는 범위에서 간격이 가장 큰 것은 60 %.'),
 ('NL', '② 왼쪽 body 도핑', [('DDS_TE8_XS60_NL5e17', '5e17'), ('DDS_TE8_XS60_NL5p5e17', '5.5e17'), ('DDS_TE8_XS60', '6e17 (기준)')],
  '**루프 2만 움직인다.** 켜짐 4.08 → 4.47 → 4.78 V, 꺼짐은 2.50–2.56 V로 거의 그대로라 루프 2의 폭이 도핑으로 정해진다. 루프 1은 변하지 않는다.'),
 ('VG', '③ Vg', [('DDS_TE8_XS60_VG0', '0 V'), ('DDS_TE8_XS60_VGm0p1', '-0.1 V'), ('DDS_TE8_XS60', '-0.2 V (기준)')],
  'Vg를 올리면 **두 루프가 함께 내려간다** (루프 2 켜짐 4.78 → 4.37 V). 대신 **루프 1이 좁아진다** (폭 0.22 → 0.07 V). Vg는 두 루프를 같이 미는 손잡이.'),
 ('NR', '④ 오른쪽 body 도핑', [('DDS_TE8_XS60', '7e17 (기준)'), ('DDS_TE8_XS60_NR8e17', '8e17'), ('DDS_TE8_XS60_NR1e18', '1e18')],
  '**루프 1이 올라가고 넓어진다** (폭 0.22 → 0.49 → 1.03 V). 루프 2는 조금 올라가 **두 루프 간격이 1.12 → 0.78 → 0.10 V로 줄어든다**. 1e18이면 거의 맞닿는다. → 8e17이 루프 1을 넓히면서 분리를 유지하는 절충점.'),
 ('TE', '⑤ Si 수명', [('DDS_TE5em9_XS60', '5e-9 s'), ('DDS_TE8_XS60', '1e-8 s (기준)'), ('DDS_TE2em8_XS60', '2e-8 s'), ('DDS_XS60', '1e-7 s')],
  '수명이 짧을수록 **두 루프 모두 더 급격히 꺼진다** (2번째 꺼짐 폭 0.29 → 0.16 → 0.06 → 0.001 V). 대신 두 루프 모두 올라간다 (루프 2 켜짐 3.72 → 5.22 V).'),
 ('RD', '⑥ drain 직렬 저항', [('DDS_TE8_XS60', '0 (기준)'), ('DDS_TE8_XS60_RD1e5', '1e5 Ω'), ('DDS_TE8_XS60_RD3e5', '3e5 Ω'), ('DDS_TE8_XS60_RD1e6', '1e6 Ω')],
  '켜진 상태(state III)의 **윗변이 평평해진다** (전류 기울기 3.1 → 1.5 → 1.2 → 0.9자리). 대신 **2번째 래치의 꺼짐이 완만해지고** (꺼짐 폭 0.06 → 0.12 → 0.34 → 0.95 V, 1e6 Ω에서는 점프가 사라짐) 2번째 점프도 작아진다. → 평평한 윗변과 급격한 모서리는 서로 맞바뀐다. 1e5 Ω가 균형점.'),
]

def rect_section():
    fn = os.path.join(here, 'ddsplit_rect.dat')
    if not os.path.exists(fn): return []
    rr = {l.split()[0]: l.split()[1:] for l in open(fn) if not l.startswith('#') and l.strip()}
    sm = {r['name']: r for r in rows}
    out = ['### 두 개의 분리된 급격한 사각형 루프: 변인별 정리 (`DDS_TE8_XS60` 기준)', '',
           '**목표**: 두 래치가 각각 **급격히 켜지고 꺼지며**, 두 히스테리시스 루프가 **겹치지 않고**, 각 상태의 전류가 **평평한** 두 개의 사각형.', '',
           '**기준 소자** `DDS_TE8_XS60`: Si 수명 1e-8 s + 섬 위치 Lg의 60 %. 루프 1(오른쪽 STL) 1.23–1.45 V, 루프 2(왼쪽 STL) 2.56–4.78 V, 간격 1.12 V, 두 꺼짐 모두 점프. '
           '아래에서는 이 소자에서 **변수 하나씩만** 바꿨다.', '',
           fig('fig/ddsplit_rect_groups.png', '변인별 겹친 Id-Vd (실선 올라감, 점선 내려옴, 굵은 선 = 기준). 데이터: `1007_ddsplit/DDS_*.log_tr.log` · 코드: `1007_ddsplit/plot_ddsplit.py`'),
           '표 읽는 법: 루프 1 = 오른쪽 STL (꺼짐–켜짐), 루프 2 = 왼쪽 STL. 간격 = 루프 2 꺼짐 − 루프 1 켜짐 (> 0이면 두 루프가 안 겹침). 꺼짐 폭 = 꺼질 때 전류가 2자리 떨어지는 데 걸린 Vd (0에 가까울수록 급격). 윗변 기울기 = 켜진 상태에서 |Id|가 변하는 자릿수 (작을수록 평평).', '']
    f = lambda x, d=2: '–' if x != x else ('%.' + str(d) + 'f') % x
    for key, title, items, concl in RECT_GROUPS:
        out += [f'#### {title}', '', fig(f'fig/ddsplit_rect_{key}.png', f'데이터: ' + ', '.join(f'`1007_ddsplit/{d}.log_tr.log`' for d, _ in items) + ' · 코드: `plot_ddsplit.py`'),
                '| 값 | 덱 | 루프 1 (V) | 루프 2 (V) | 간격 (V) | 꺼짐 폭 1 / 2 (V) | 윗변 기울기 (dec) |', '|---|---|---|---|---|---|---|']
        for d, lab in items:
            if d not in sm or d not in rr: continue
            s, q = sm[d], [float(z) for z in rr[d]]
            l1 = '–' if s['v1'] != s['v1'] else f"{f(s['offr'])}–{f(s['v1'])}"
            l2 = '–' if s['v2'] != s['v2'] else f"{f(s['offl'])}–{f(s['v2'])}"
            out.append(f"| {lab} | `{d}` | {l1} | {l2} | {f(q[2])} | {f(q[4],3)} / {f(q[3],3)} | {f(q[6],1)} |")
        out += ['', f'→ {concl}', '']
    out += ['#### 조합', '', '| 덱 | 바꾼 것 | 루프 1 (V) | 루프 2 (V) | 간격 (V) | 꺼짐 폭 1 / 2 (V) | 윗변 기울기 (dec) |', '|---|---|---|---|---|---|---|']
    for d in ('DDS_TE8_XS60_NL5p5e17_RD3e5', 'DDS_TE8_XS65_NL5e17_RD3e5'):
        if d not in sm or d not in rr: continue
        s, q = sm[d], [float(z) for z in rr[d]]
        l1 = '–' if s['v1'] != s['v1'] else f"{f(s['offr'])}–{f(s['v1'])}"; l2 = '–' if s['v2'] != s['v2'] else f"{f(s['offl'])}–{f(s['v2'])}"
        out.append(f"| `{d}` | {desc(d)} | {l1} | {l2} | {f(q[2])} | {f(q[4],3)} / {f(q[3],3)} | {f(q[6],1)} |")
    out += ['', '→ 섬 65 % 조합은 오른쪽 래치가 없어 한 루프만 남는다. 섬 60 % + 왼쪽 5.5e17 + 1e5–3e5 Ω가 "분리 + 평평한 윗변" 쪽에 가장 가깝지만 2번째 꺼짐이 완만해진다.', '',
            '**정리**: 루프 1은 오른쪽 도핑·섬 위치·Vg, 루프 2는 왼쪽 도핑·Vg, 모서리의 급격함은 Si 수명, 윗변의 평평함은 drain 직렬 저항이 정한다. 평평한 윗변과 급격한 꺼짐은 서로 맞바뀌는 관계다.', '',
            '<details><summary>전체 사각형 지표 표 (모든 관련 덱)</summary>', '', rect_table(), '', '</details>', '']
    return out

def fig(path, cap):
    return f'![]({REL}/{path})\n*{cap}*\n' if os.path.exists(os.path.join(here, path)) else ''

main = [r['name'] for r in rows if not re.match(r'DDS_(RD|TE|BASE_SNAP)', r['name'])]
off = [r['name'] for r in rows if re.match(r'DDS_(BASE$|RD|TE1em8$|TE1em9$)', r['name'])]
te8 = [r['name'] for r in rows if re.match(r'DDS_(TE1em8$|TE5em9|TE2em8|TE5em8|TE8_)', r['name'])]
L = [A, '', f'### 결과 (자동 생성: {datetime.datetime.now():%Y-%m-%d %H:%M}, 완료 {ndone}/{len(decks)})', '',
     '> 이 블록은 `1007_ddsplit/update_readme_ddsplit.py`가 다시 쓴다. 래치 검출 기준(`analyze_ddsplit.py`): 같은 Vd(2 mV 이내)에서 경로 전류가 1자리 넘게 뛰고 실제 수준(왼쪽 |Is| > 1e-7 A, 오른쪽 |Itap| > 1e-9 A)에 닿으면 래치. '
     'ON = 올라갈 때 켜지는 Vd, OFF = 내려올 때 꺼지는 Vd(왼쪽 |Is| < 1e-8 A, 오른쪽 |Itap| < 1e-9 A), OFF 폭 = 내려올 때 왼쪽 |Is|가 1e-6 → 1e-8 A로 떨어지는 데 걸린 Vd 폭 (0이면 급격).', '',
     '데이터: `1007_ddsplit/DDS_*.log_tr.log` · 표: `1007_ddsplit/ddsplit_summary.dat` · 코드: `analyze_ddsplit.py`, `plot_ddsplit.py`', '',
     table(main), '',
     fig('fig/ddsplit_trends.png', '변수별 두 래치의 ON/OFF 전압(선)과 점프 크기(막대). 데이터: `1007_ddsplit/DDS_*.log_tr.log` · 코드: `1007_ddsplit/plot_ddsplit.py`')]
for g, cap in (('R', '탭 저항'), ('NL', '왼쪽 body 도핑'), ('NR', '오른쪽 body 도핑'), ('VG', 'Vg'), ('TAU', '섬 lifetime'),
               ('WISL', '섬 폭'), ('XS', '섬 위치'), ('TSI', 'Si 두께'), ('RATE', 'ramp 속도')):
    L.append(fig(f'fig/ddsplit_idvd_{g}.png', f'Id-Vd ({cap}). 실선 올라감, 점선 내려옴. 데이터: `1007_ddsplit/DDS_*.log_tr.log` · 코드: `plot_ddsplit.py`'))
    L.append(fig(f'fig/ddsplit_struct_{g}.png', f'구조 변경 ({cap}). 출처: `1007_ddsplit/DDS_*_INIT.str` · 코드: `tools/strstruct.py` (via `plot_ddsplit.py`)'))
L += ['', '### 래치 메커니즘 (.str 스냅샷)', '',
      '각 split은 고정 Vd마다 `.str` 스냅샷(`DDS_*_T_tr_N`)을 저장한다. 채널(y = 25 nm)을 따라 전위와 정공 밀도를 읽고, STL마다 '
      '**source → body 전자 장벽**과 **body 평균 정공 밀도**를 계산했다 (`mech_ddsplit.py`).', '']
for name in ('DDS_BASE', 'DDS_BASE_SNAP', 'DDS_TE8_SNAP'):
    dat = os.path.join(here, f'mech_{name}.dat')
    if not os.path.exists(dat): continue
    L.append(fig(f'fig/mech_{name}.png', f'데이터: `1007_ddsplit/{name}_T_tr_N` · 코드: `1007_ddsplit/mech_ddsplit.py`'))
    L += ['| 스냅샷 | Vd (V) | 왼쪽 장벽 (eV) | 왼쪽 body 정공 (cm⁻³) | 오른쪽 장벽 (eV) | 오른쪽 body 정공 (cm⁻³) |', '|---|---|---|---|---|---|']
    for l in open(dat):
        if l.startswith('#'): continue
        p = l.split(); L.append(f'| {p[1]} | {p[2]} | {p[3]} | {p[4]} | {p[5]} | {p[6]} |')
    L.append('')
L += ['읽는 법: 오른쪽 STL은 첫 번째 래치에서 장벽이 약 0.7 → 0.27 eV로 떨어지고 body 정공이 늘어난다. 이때 섬 전위가 올라가 왼쪽 장벽도 일부 낮아진다 (0.98 → 0.70 eV). '
      '두 번째 래치에서 왼쪽 장벽이 0.68 → 0.09 eV로 무너지며 왼쪽 body가 정공으로 찬다. 내려올 때 왼쪽 장벽은 0.13 → 0.20 → 0.74 eV로 **여러 스냅샷에 걸쳐 서서히** 회복된다. 이게 두 번째 래치가 완만하게 꺼지는 모습이다.', '']
L += ['### 두 번째 래치를 급격히 끄기 위한 시도', '',
      '내려올 때 왼쪽 STL이 약 0.26 V에 걸쳐 서서히 꺼진다 (기준 OFF 폭). 원인 가설: drain이 이상적인 전압원이라 켜진 가지를 끝까지 따라 내려오고, 접힘(fold)에서 튀어 내려올 계기가 없다. '
      '그래서 (1) **drain 직렬 저항**(부하선을 기울여 접힘에서 점프하게), (2) **Si 수명 감소**(body 정공을 빨리 빼서 유지 전류↑)를 시험한다.', '',
      table(off), '',
      fig('fig/ddsplit_idvd_RD.png', 'Id-Vd (drain 직렬 저항). 데이터: `1007_ddsplit/DDS_RD*.log_tr.log` · 코드: `plot_ddsplit.py`'),
      fig('fig/ddsplit_idvd_TE.png', 'Id-Vd (Si 수명). 데이터: `1007_ddsplit/DDS_TE*.log_tr.log` · 코드: `plot_ddsplit.py`'),
      '### Si 수명 1e-8 s 기반 split (급격한 꺼짐 조건 위에서 다시 조절)', '',
      'Si 수명 1e-8 s에서 두 번째 래치가 점프로 꺼졌다 (OFF 폭 0.26 → 0.04 V). 대신 두 래치가 모두 약 0.7 V 올라갔다. 이 조건을 유지한 채 도핑·R·Vg·섬 위치로 래치 전압을 다시 내리고, 꺼짐이 계속 급격한지 본다. '
      '`DDS_TE8_SNAP`은 꺼지는 구간의 촘촘한 스냅샷으로 메커니즘을 본다.', '',
      table(te8), '',
      fig('fig/ddsplit_idvd_TE8_NL.png', 'Id-Vd (수명 1e-8 s + 왼쪽 도핑). 데이터: `1007_ddsplit/DDS_TE8_NL*.log_tr.log` · 코드: `plot_ddsplit.py`'),
      fig('fig/ddsplit_idvd_TE8_NR.png', 'Id-Vd (수명 1e-8 s + 오른쪽 도핑). 데이터: `1007_ddsplit/DDS_TE8_NR*.log_tr.log` · 코드: `plot_ddsplit.py`'),
      fig('fig/ddsplit_idvd_TE8_R.png', 'Id-Vd (수명 1e-8 s + 탭 저항). 데이터: `1007_ddsplit/DDS_TE8_R*.log_tr.log` · 코드: `plot_ddsplit.py`'),
      fig('fig/ddsplit_idvd_TE8_VG.png', 'Id-Vd (수명 1e-8 s + Vg). 데이터: `1007_ddsplit/DDS_TE8_VG*.log_tr.log` · 코드: `plot_ddsplit.py`'),
      *rect_section(),
      B]
s = open(README).read()
block = '\n'.join(x for x in L if x is not None)
if A in s:
    s = s[:s.index(A)] + block + s[s.index(B) + len(B):]
else:
    key = '결과가 나오면 변수별로 두 래치 전압(켜짐/꺼짐), 점프 크기, 히스테리시스 창을 표와 그림으로 이 Step에 추가한다. 구조를 바꾼 split은 `.str` 구조 그림을 함께 넣는다.'
    s = s.replace(key, block)
open(README, 'w').write(s)
print('README updated:', ndone, '/', len(decks), 'decks done')
