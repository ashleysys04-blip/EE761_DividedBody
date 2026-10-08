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
