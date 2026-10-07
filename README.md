# Divided-Body SOI STL: 소자 하나로 "직렬 두 STL" 만들기

EE762 (KAIST, 2026 가을) 프로젝트 연구 기록 · Silvaco ATLAS 2D (device-only transient + MixedMode)

> **한 줄 요약 (2026-10-07)**
> SOI body를 n+ 섬으로 둘로 나누고, 섬을 저항(1e7 Ω)으로 접지하고, 섬 lifetime을 줄여 두 body를 분리했다.
> 그 결과 **drift-diffusion(DD) MixedMode 시뮬레이션에서 Id-Vd에 래치가 두 번(2.254 V, 3.296 V) 히스테리시스와 함께 나왔다.**
> 같은 소자를 에너지 균형 모델(hcte)로 확인하는 run이 진행 중이다.

![double latch](1001/tap/fig/DOUBLE_LATCH_DD_MM.png)
*그림 0. 최종 결과 (DD, MixedMode). 데이터: `1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_VGm0p2.log_tr.log` · 덱: `1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_VGm0p2.in` · 그린 코드: `1001/tap/fig/plot_double_latch.py`*

---

## 목차
- [읽는 법](#읽는-법)
- [저장소 구성](#저장소-구성)
- [공통 조건과 분석 도구](#공통-조건과-분석-도구)
- [전체 흐름 한눈에](#전체-흐름-한눈에)
- [Phase 0. 초기 split-body 실험 (08/27 – 09/08)](#phase-0-초기-split-body-실험-0827--0908)
- [Step 1. 도핑을 나누면 래치가 두 번 나올까? (09/21)](#step-1-도핑을-나누면-래치가-두-번-나올까-0921)
- [Step 2. 도핑 차이를 크게 (09/27)](#step-2-도핑-차이를-크게-0927)
- [Step 3. 왜 한 번뿐인가 → body를 물리적으로 나누기 (09/28)](#step-3-왜-한-번뿐인가--body를-물리적으로-나누기-0928)
- [Step 4. 다른 시도들 (09/28 – 10/01)](#step-4-다른-시도들-0928--1001)
- [Step 5. 섬을 저항으로 접지 (탭) (10/01 – 10/03)](#step-5-섬을-저항으로-접지-탭-1001--1003)
- [Step 6. 섬을 건너는 정공 막기 (10/03 – 10/04)](#step-6-섬을-건너는-정공-막기-1003--1004)
- [Step 7. 섬 전위 올리기: R 키우기 (10/04 – 10/06)](#step-7-섬-전위-올리기-r-키우기-1004--1006)
- [Step 8. 고전압 수치 폭주 (10/05 – 10/07)](#step-8-고전압-수치-폭주-1005--1007)
- [Step 9. 왼쪽 STL은 래치할 수 있나? → 단독 소자 (10/06)](#step-9-왼쪽-stl은-래치할-수-있나--단독-소자-1006)
- [Step 10. 본 소자: 래치 두 번 (10/07)](#step-10-본-소자-래치-두-번-1007)
- [트레이드오프 요약](#트레이드오프-요약)
- [현재 상태와 다음 단계](#현재-상태와-다음-단계)
- [부록: 핵심 데이터 파일](#부록-핵심-데이터-파일)

---

## 읽는 법

각 Step은 항상 같은 순서로 적었다.

| 기호 | 의미 |
|---|---|
| 🎯 **왜** | 이 구조/조건을 왜 만들었나 |
| 🛠 **어떻게** | 무엇을 바꿨나 (구조를 바꾼 경우 구조 그림 필수) |
| ⚠️ **문제** | 결과에서 무엇이 기대와 달랐나 |
| ✅ **해결** | 그래서 다음에 무엇을 바꿨나 → 다음 Step |

모든 그림 아래에 **데이터 출처**(이 저장소 기준 경로)와 **그린 코드**를 적었다. 그린 코드가 저장되지 않은 그림(작업 중 일회성 스크립트)은 그렇다고 명시했다.

---

## 저장소 구성

```
novel/
├── README.md                 ← 이 문서 (연구 기록)
├── tools/                    ← 필수 분석 코드 (log/str 읽기, 구조 그림)
├── docs/fig/                 ← README용 그림 (struct_*.png = 구조, prev/ = 1차 정리 그림)
├── *.in (루트), 0908/        ← Phase 0
├── 0921/ 0927/ 0927_bigsplit/ 0928/ 0929/ 1001/ 1001_ibody/   ← 날짜별 실험 (덱 .in, 표 .dat, 그림 .png)
└── 1001/tap/                 ← 탭 섬 구조 (이번 결과의 대부분), fig/ 에 그림
```

**올린 것**: 모든 덱(`.in`), 표(`.dat`), 그림(`.png`), 필수 코드(`.py` 6개), 핵심 log (부록 참고)
**안 올린 것**: `.str`(구조/해 스냅샷), `.out`(solver 출력), 나머지 `.log`, MixedMode 스냅샷(`*_tr_N`). 합계 약 5.4 GB로, 연구 서버 `/home/ysseo/novel/` 에 같은 경로로 남아 있다.
100 MB가 넘는 log 2개는 핵심 열만 뽑은 `*_extract.dat` 로 대신 올렸다.

---

## 공통 조건과 분석 도구

### 기준 소자 (Step 1 이후 공통)
| 항목 | 값 |
|---|---|
| Lg / S·D 길이 / 폭 | 0.30 µm / 0.50 µm / 0.5 µm (mesh width) |
| Tsi / gate oxide / BOX | 50 nm / 20 nm / 200 nm |
| S/D, gate | n+ 1e20, n+ poly 1e21 |
| 모델 | `bgn hcte consrh conmob fldmob fermi trap.tunnel bbt.std`, `impact selb length.rel` |
| solver | `method block newton climit=100 itlimit=200 NBLOCKIT=200 trap maxtraps=10` |
| bias | VG = −0.2 V, VD sweep (Step 5부터 transient ramp 0.7 V/ms) |

DD(drift-diffusion)라고 적힌 run은 위 모델에서 `hcte`만 뺀 것이다.

### 분석 도구 (`tools/`, 그 외 필수 코드)
| 파일 | 역할 |
|---|---|
| `tools/plog.py` | ATLAS `.log` / MixedMode `.log_tr.log` → numpy 배열. **열 번호 규칙이 docstring에 있다** |
| `0927/ebd/strcut.py` | `.str` 에서 Si 노드의 Ec, Ev, Efp, ψ, p, n 읽기 + 가로 cutline |
| `1001/tap/fig/strfig.py` | `.str` 스냅샷 → EBD(y = 25 nm) 그림, Si 막 2D 지도(정공·전위) |
| `tools/strstruct.py` | `.str` → 구조 그림(영역 + net doping). `docs/fig/struct_*.png` 생성 |
| `tools/make_struct_figs.py` | 이 문서의 구조 그림 전부를 다시 그림 |
| `1001/tap/fig/plot_double_latch.py` | 그림 0 재생성 |

```python
# 예: transient log에서 Id-Vd 꺼내기   (출처: tools/plog.py 의 열 규칙)
import sys; sys.path.insert(0, 'tools'); from plog import load
d = load('1001/tap/TAPT_ISL_W30LK_L3_R7_R1e6_UD7S_VGm0p2.log'); o = 1
Vd, Id, Is, Itap = d[:, o+11], d[:, o+12], d[:, o+7], d[:, o+17]
```

---

## 전체 흐름 한눈에

| Step | 구조/조건 변경 | 결과 | 다음으로 간 이유 |
|---|---|---|---|
| 1 | 도핑 split (소농도차), 산화막 notch | 래치 1번 | 차이가 너무 작은가? |
| 2 | 도핑 split (대농도차, 방향) | 래치 1번 (창은 조절 가능) | body가 전기적으로 하나 |
| 3 | Tsi split, **n+ 섬** | 래치 1번 (좌·우 동시) | 직렬이라 함께 켜짐 |
| 4 | split gate, n+/n−/p/n+, body 전류 추출 | 래치 1번 | — |
| 5 | **섬을 R로 접지 (탭)**, transient ramp | 여전히 동시 | 정공이 섬을 건넘 |
| 6 | 섬 폭 100 nm / 윗면 contact / **섬 lifetime 감소** | lifetime 감소만 분리 성공 | 왼쪽이 구동 안 됨 |
| 7 | **R 증가** (1e4 → 1e6 Ω) | 섬 전위 상승 | 5.3 V에서 계산 중단 |
| 8 | solver, 격자, hcte 제거 시도 | 원인 = 오른쪽 STL 전압 | 큰 R 필요 |
| 9 | **왼쪽 STL 단독 소자**, 도핑 탐색 | 3e17은 래치 불가, **6e17 래치** | 본 소자에 적용 |
| 10 | 왼쪽 6e17 + **R 1e7 Ω**, MixedMode | **DD에서 래치 2번** | hcte로 확인 중 |

---

## Phase 0. 초기 split-body 실험 (08/27 – 09/08)

> 이 단계는 덱 머리말 기준으로만 요약한다 (결과 분석 그림은 이 저장소에 없음).

🎯 **왜** 한 소자의 body 도핑을 좌/우(P / P+)로 나누면 래치 특성을 설계할 수 있는지 보려고.
🛠 **어떻게** `ver1.in` – `ver3_*.in`(루트): Lg 0.6 µm, P / P+ split body FDSOI. `0908/`: Lim (2026) 논문 치수 재현(`limref_*`), split 위치 sweep(`sw_*`), back-gate / BBT / body 전류 싱크 / floating-body 평형 시간(`tau_*`), cycle 간 차이 원인(`ver4_*`), 래치 창 닫기(`win_*`).
⚠️ **문제** 기생 BJT 이득이 커서 래치 창이 잘 닫히지 않고(VLD 0.2 V대), cycle마다 결과가 달라지는 등 기준 소자 자체가 불안정했다.
✅ **해결** 09/21부터 기준 소자를 Lg 0.3 µm, Tsi 50 nm, 균일 5e17 STL로 다시 잡고 거기서 출발.

| ![](docs/fig/struct_00_ver2_split.png) | ![](docs/fig/struct_00b_0908_sw_orig.png) |
|---|---|
| 출처: `split_body_init.str` (덱 `ver2.in`) | 출처: `0908/sw_orig_idvd.str` (덱 `0908/sw_idvd_orig.in`) |

*구조 그림 코드: `tools/make_struct_figs.py` → `tools/strstruct.py`*

---

## Step 1. 도핑을 나누면 래치가 두 번 나올까? (09/21)

🎯 **왜** body 왼쪽/오른쪽 도핑이 다르면 두 영역의 래치 전압이 달라서, Id-Vd에 래치가 두 번 나올 것이라고 기대했다.

🛠 **어떻게**
- 기준: 균일 5e17 STL (`0921/STL_NB5p0_localfine.in`)
- 소농도차 split: L/R = 4.8–5.4e17, split 위치 Lg의 40/50/60 % (`0921/SPLIT_*.in`)
- 아래쪽에 산화막 notch를 넣어 두 body를 떼고 위쪽 얇은 Si bridge로만 연결 (`0921/B*_W*_L*_R*.in`)

| ![](docs/fig/struct_01_uniform_STL.png) | ![](docs/fig/struct_02_small_split.png) | ![](docs/fig/struct_03_notch_bridge.png) |
|---|---|---|
| 기준 STL · `0921/STL_NB5p0_localfine_END.str` | 소농도차 · `0921/SPLIT_L5p0_R5p2_X50_END.str` | notch + bridge · `0921/B10_W20_L5p0_R5p2_END.str` |

⚠️ **문제** 모두 **래치 1번**. 소농도차는 균일 소자(V_LU 3.85 / V_LD 3.50 V)와 ±0.15 V 이내로 같았다. notch 소자도 단일 래치(V_LU 4.27–4.44 V).

| ![](docs/fig/prev/A_split_small.png) | ![](docs/fig/prev/B_notch.png) |
|---|---|
| 데이터: `0921/SPLIT_*.log`, `0921/STL_NB5p0_localfine.log` | 데이터: `0921/B*_W*_L*_R*.log` |

*그린 코드: 1차 정리 때의 일회성 스크립트 (저장 안 됨)*

✅ **해결** 도핑 차이가 4–12 %로 너무 작아서일 수 있다 → Step 2에서 차이를 2–10배로 키운다.

---

## Step 2. 도핑 차이를 크게 (09/27)

🎯 **왜** 도핑 차이를 크게 하면 두 영역의 래치 전압이 확실히 갈라질 것.

🛠 **어떻게** 평균 약 5e17을 유지하면서 L/R 비율 2.3 / 4 / 10배, 고도핑을 drain 쪽 또는 source 쪽에 둔다 (`0927/BIG_*_X50.in`, `0927_bigsplit/BIG_*_X50.in`). 전이 전후 `.str`을 저장해 EBD를 그렸다.

![](docs/fig/struct_04_big_split.png)
*출처: `0927/BIG_L3_R7_X50_END.str` (덱 `0927/BIG_L3_R7_X50.in`)*

⚠️ **문제** **여전히 래치 1번.** 대신 방향과 비율로 래치 창은 조절된다.

| 케이스 | V_LU (V) | V_LD (V) | 창 (V) |
|---|---|---|---|
| L3_R7 (drain 쪽 고도핑 2.3×) | 3.67 | 3.32 | 0.35 |
| L7_R3 (source 쪽 2.3×) | 4.89 | 3.88 | 1.01 |
| L8_R2 (source 쪽 4×) | 5.76 | 4.11 | 1.66 |

| ![](docs/fig/prev/C_big_idvd.png) | ![](docs/fig/prev/D_vlu_ratio.png) |
|---|---|
| 데이터: `0927/BIG_*_X50.log`, `0927_bigsplit/BIG_*_X50.log` | 데이터: 같은 log + `0921/STL_NB5p0_localfine.log` |

EBD를 보면 원인이 보인다. 정공 준페르미 준위(Efp, 점선)가 **body 전체에서 하나로 이어져** 있어서 왼쪽/오른쪽 body 전위가 따로 움직일 수 없다.

![](docs/fig/prev/EBD_L3_R7.png)
*데이터: `0927/BIG_L3_R7_X50_{HRS,FWD_*,REV_*}.str` · 그린 코드: `0927/ebd/strcut.py` (+ 일회성 `ebd_plot.py`)*

✅ **해결** 래치가 한 번인 이유 세 가지:
1. **Efp 연속**: p / p+ 계단은 다수 캐리어(정공)를 막지 못한다.
2. **저농도 쪽 공핍**: 저농도 body가 drain 쪽이면 공핍되어 정공 저장소가 하나만 남는다.
3. (다음 Step에서 확인) 물리적으로 나눠도 직렬이면 함께 켜진다.

→ body를 **물리적으로** 나눠야 한다 (Step 3).

> 참고: 이 Step부터 S자 I-V(NDR)에서 전압 sweep이 멈추는 문제가 보였다 (L2_R8, L1_R10이 3.49–3.50 V에서 정지). Step 5에서 transient ramp로 해결.

---

## Step 3. 왜 한 번뿐인가 → body를 물리적으로 나누기 (09/28)

🎯 **왜** 정공이 두 body 사이를 자유롭게 오가지 못하게 하면 두 body가 따로 래치할 것.

🛠 **어떻게**
- Tsi split: 왼쪽 20 nm / 오른쪽 50 nm (`0928/TSI_*.in`)
- **n+ 섬**: 채널 가운데 30 nm, 1e20, Tsi 전체 → 왼쪽 STL(source–섬)과 오른쪽 STL(섬–drain)이 직렬 (`0928/ISL_W30_*.in`)

| ![](docs/fig/struct_05_tsi_split.png) | ![](docs/fig/struct_06_floating_island.png) |
|---|---|
| `0928/TSI_L20_R50_END.str` | `0928/ISL_W30_L3_R7_END.str` |

⚠️ **문제** n+ 섬은 body를 **분리하는 데는 성공**했다(래치 전 좌/우 body 전위 −0.02 V vs 0.36 V). 하지만 **3.26 V에서 좌·우·섬이 동시에 점프**해서 여전히 래치 1번.

| ![](docs/fig/prev/G_island.png) | ![](docs/fig/prev/G_island_probes.png) |
|---|---|
| 데이터: `0928/ISL_W30_{L3_R7,L5_R5,L7_R3}.log` | 데이터: `0928/ISL_W30_L3_R7.log` (probe VB_left, VB_right, V_island) |

✅ **해결** 원인은 **직렬 제약**이다. 섬이 떠 있으면 오른쪽 STL 전류는 반드시 왼쪽 STL을 통과해야 해서, 한쪽만 켜질 수 없다. → 섬에 따로 빠져나갈 길을 만들어야 한다 (Step 5).

<details><summary>같은 시기의 Id-Vg 결과 (부수 결과)</summary>

drain 쪽 고도핑(L3_R7)만 Vg 방향 래치가 있었다 (up 1.390 / down 1.335 V, SS 36 mV/dec).

| ![](docs/fig/prev/E_idvg.png) | ![](docs/fig/prev/F_idvg_updown.png) |
|---|---|
| 데이터: `0928/idvg/IDVG_BIG_*_X50_vd0p05.log`, `*_vd1.log` | 데이터: `0928/idvg_return/IDVGR_BIG_*_X50_vd1.log` |
</details>

---

## Step 4. 다른 시도들 (09/28 – 10/01)

🎯 **왜** 섬 이외의 방법으로도 두 body를 독립시킬 수 있는지 확인.

| 시도 | 구조 | 결과 |
|---|---|---|
| split gate (`0929/splitgate/SG_*.in`) | ![](docs/fig/struct_07_split_gate.png) `0929/splitgate/SG_G2D_m0p2_END.str` | 래치 1번. 대신 G2 전압으로 **래치 창 0.36 → 1.18 V 조절** |
| n+ / n− / p / n+ (`1001/nnpn/NNPN_*.in`) | ![](docs/fig/struct_08_nnpn.png) `1001/nnpn/NNPN_D_Ln150_N1e16_P5e17_HRS.str` | 래치 1번 |
| body 전류 추출 (`0928/idvg_ibody2/RB_*.in`) | BOX 관통 p neck + 직렬 저항 | 박막 SOI는 −12 V에서도 최대 약 2e-11 A만 추출 |
| integrate-and-fire / 기억 (`0929/burst`, `1001/memory`) | MixedMode, drain에 전류원 + C | bursting 없음, 단기 문턱 기억(~ms)만 |

| ![](docs/fig/prev/RB_idvg.png) | ![](docs/fig/prev/BURST_grid.png) | ![](docs/fig/prev/H_memory.png) |
|---|---|---|
| `0928/idvg_ibody2/RB_BIG_L3_R7_*_vd1.log` | `0929/burst/BURST_*.log_tr.log` | `1001/memory/MEM_BIG_L3_R7_I1n.log_tr.log` |

✅ **해결** 래치 2번이 목표라면 n+ 섬 구조가 가장 가깝다 → 섬의 직렬 제약을 푸는 쪽으로 간다.

---

## Step 5. 섬을 저항으로 접지 (탭) (10/01 – 10/03)

🎯 **왜** 섬을 저항 R로 접지하면, 오른쪽 STL이 먼저 켜졌을 때 그 전류가 왼쪽을 거치지 않고 R로 빠진다. 섬 전위(= I·R)가 올라가면 그게 왼쪽 STL의 drain 전압이 되어 **두 번째 래치**를 일으킬 것.

🛠 **어떻게** 섬 아래 BOX를 n+ 기둥(neck)으로 관통시켜 바닥에 `tap` 전극을 두고 `contact name=tap resistance=…`로 R을 단다.

![](docs/fig/struct_09_tap_W30.png)
*출처: `1001/tap/TAPT_ISL_W30_L3_R7_R3e5_VGm0p2_INIT.str` (덱 `1001/tap/TAPT_ISL_W30_L3_R7_R3e5_VGm0p2.in`)*

```
# 출처: 1001/tap/TAPT_ISL_W30_L3_R7_R3e5_VGm0p2.in
region num=9  x.min=$XiL x.max=$XiR y.min=$tsi y.max=$Ybot silicon      # neck through BOX
electrode name=tap x.min=$XiL x.max=$XiR y.min=$Ybot y.max=$Ybot
doping uniform conc=1e20 n.type reg=9
contact name=tap resistance=300000                                      # 2D 단위 Ω·µm → 실제 R = 값 / 0.5 µm = 6e5 Ω
```

⚠️ **문제 1: 계산이 래치 직전에 멈춤.** S자 I-V의 fold에서 Newton이 수렴하지 못했다.

| 방법 | 결과 (R = 6e5 Ω) |
|---|---|
| 전압 sweep (`TAP_…_R3e5`) | 2.934 V, 1.65e-11 A에서 정지 |
| drain 직렬 1e5 Ω 추가 (`TAP_…_RD1e5`) | 효과 없음 (pA에서는 I·R ≈ 0) |
| 전류 sweep (`TAPI_…`) | 2.3e-15 A (0.69 V)에서 실패 |
| 전압 → 전류 제어 (`TAPS_…`) | 4.3e-11 A에서 정지 |
| **transient ramp 0.7 V/ms** (`TAPT_…`) | **0 → 7 → 0 V 완주** |

✅ **해결 1** `solve vdrain=X ramptime=… tstop=…`로 drain을 시간에 대해 ramp한다. 실제 시간 동역학이 불안정 가지를 건너가므로 점프와 히스테리시스가 바로 나온다. 이후 모든 run은 이 방식이다.

⚠️ **문제 2: 탭이 있어도 좌·우가 동시에 래치.** R을 60배 바꿔도 V_LU가 똑같다.

| R (실제) | V_LU | V_LD | 왼쪽(Is)도 점프? |
|---|---|---|---|
| 6e5 Ω | 2.990 | 2.289 | 예 |
| 6e4 Ω | 2.990 | 2.248 | 예 |
| 1e4 Ω | 2.990 | – | 예 |

| ![](1001/tap/TAPT_compare_R.png) | ![](1001/tap/TAPT_R3e5_two_stage.png) |
|---|---|
| 데이터: `1001/tap/TAPT_ISL_W30_L3_R7_{R3e5,R3e4}_VGm0p2.log` | 데이터: `1001/tap/TAPT_ISL_W30_L3_R7_R3e5_VGm0p2.log` (점프 부근 100 ns 확대) |

*그린 코드: 일회성 스크립트 (저장 안 됨)*

점프 순간을 확대하면 오른쪽 body가 먼저 오르고 약 10 ns 뒤 왼쪽이 따라온다. **한 번의 점프 안의 순서**일 뿐 두 단계 래치는 아니다.
원인: 오른쪽 p body / n+ 섬(30 nm) / 왼쪽 p body가 **가로 PNP**를 이룬다. 오른쪽에서 섬으로 들어간 정공이 얇은 섬을 재결합 없이 건너 왼쪽 body를 채운다.

✅ **해결 2** 정공이 섬을 못 건너게 해야 한다 (Step 6).

---

## Step 6. 섬을 건너는 정공 막기 (10/03 – 10/04)

🎯 **왜** 가로 PNP 결합을 끊으면 오른쪽 STL만 혼자 래치할 것.

🛠 **어떻게** 세 가지를 비교 (모두 R = 1e4 Ω, VG = −0.2 V)

| W100: 섬 폭 30 → 100 nm | C: 섬 윗면 ohmic contact로 탭 | B: 섬 + neck lifetime 1e-12 s |
|---|---|---|
| ![](docs/fig/struct_10_tap_W100.png) | ![](docs/fig/struct_11_top_contact.png) | ![](docs/fig/struct_12_lifetime_killed.png) |
| `1001/tap/TAPT_ISL_W100_L3_R7_R1e4_UD6S_VGm0p2_INIT.str` | `1001/tap/TAPT_ISL_W30TC_L3_R7_R1e4_UD6S_VGm0p2_INIT.str` | `1001/tap/TAPT_ISL_W30LK_L3_R7_R1e4_UD6S_VGm0p2_INIT.str` |

```
# B 구조: 출처 1001/tap/TAPT_ISL_W30LK_L3_R7_R1e4_UD6S_VGm0p2.in
region num=10 x.min=$XiL x.max=$XiR y.min=0 y.max=$tsi silicon     # island as its own region
material region=10 taun0=1e-12 taup0=1e-12
material region=9  taun0=1e-12 taup0=1e-12
```

| 구조 | V_LU / V_LD (V) | 왼쪽 STL |
|---|---|---|
| W100 | 1.656 / 1.648 | 서서히 켜짐 (정공이 100 nm 섬도 건넘) |
| C (윗면 contact) | 3.035 / 2.402 | 동시에 점프 (정공이 5 nm 깊이 contact 아래로 지나감) |
| **B (lifetime 감소)** | **3.058 / 2.997** | **꺼진 채 (Is ≤ 5.4e-10 A)** |

| ![](1001/tap/fig/IdVd_C_B_W100.png) | ![](1001/tap/fig/W100_UD6S_EBD_up.png) |
|---|---|
| 데이터: `1001/tap/TAPT_ISL_{W30TC,W30LK,W100}_L3_R7_R1e4_UD6S_VGm0p2.log` (B는 그림 당시 4.7 V까지) · 일회성 스크립트 | 데이터: `1001/tap/TAPT_ISL_W100_L3_R7_R1e4_UD6S_VGm0p2_UP_*.str` · 코드: `1001/tap/fig/strfig.py` |

B 구조 왕복(0 → 6 → 0 V)은 B 계열에서 **끝까지 완주한 유일한 결과**다. 같은 3.0 V에서 꺼진 상태(up)와 켜진 상태(down)가 공존하고(쌍안정), 왼쪽 body는 네 상태 모두 그대로다.

| ![](1001/tap/fig/B_R1e4_full_updown.png) | ![](1001/tap/fig/B_R1e4_EBD_window.png) |
|---|---|
| 데이터: `1001/tap/TAPT_ISL_W30LK_L3_R7_R1e4_UD6S_VGm0p2_extract.dat` (원본 log 116 MB는 서버) | 데이터: `…_R1e4_UD6S_VGm0p2_{UP_3p0,UP_3p1,DN_3p0,DN_2p8}.str` · 코드: `strfig.py` |

⚠️ **문제** 분리는 됐지만 이번엔 **왼쪽이 아예 구동되지 않는다.** R = 1e4 Ω에서는 섬 전위가 +0.4 V 이상 오르지 못한다. 또 래치 창이 0.70 → 0.06 V로 좁아졌다 (원인 미확인, lifetime 감소와 관련 추정).

✅ **해결** **B 구조를 기본으로 채택**하고, 섬 전위를 올리기 위해 R을 키운다 (Step 7).

---

## Step 7. 섬 전위 올리기: R 키우기 (10/04 – 10/06)

🎯 **왜** 섬 전위 = I·R. R을 키우면 같은 전류로 섬 전위가 더 올라가서 왼쪽 STL을 구동할 것.

🛠 **어떻게** B 구조에서 R = 1e4 / 3e5 / 1e6 Ω (`1001/tap/TAPT_ISL_W30LK_L3_R7_{R1e4_UD6S,R3e5_UD7S,R1e6_UD7S}_VGm0p2.in`). 구조는 Step 6 B와 같다.

![](1001/tap/fig/B_R_compare_IdIs.png)
*데이터: `1001/tap/TAPT_ISL_W30LK_L3_R7_{R1e4_UD6S_extract.dat, R3e5_UD7S_extract.dat, R1e6_UD7S.log}` · 일회성 스크립트. R1e6의 5.28 V "점프"는 수치 오류다 (Step 8).*

| Vd = 4.98 V | R 1e4 | R 3e5 | R 1e6 |
|---|---|---|---|
| Id (오른쪽) | 3.2e-5 A | 3.2e-6 A | 1.1e-6 A |
| Is (왼쪽) | 2.1e-10 A | 3.3e-8 A | 7.3e-8 A |
| 섬 전위 상승 | +0.32 V | +0.94 V | +1.05 V |

⚠️ **문제** R을 키우자 섬 전위가 Vd 1 V당 약 0.73 V씩 오르고 왼쪽 Is도 지수적으로 커졌다. 그런데 **R1e6이 Vd = 5.284 V에서 계산 중단**됐다. 그 직전에 Id, Is가 음수로 튀었다.

✅ **해결** 그 점프가 진짜인지부터 확인 (Step 8).

---

## Step 8. 고전압 수치 폭주 (10/05 – 10/07)

🎯 **왜** 5.28 V 점프가 두 번째 래치인지, 수치 오류인지 판정해야 했다.

🛠 **어떻게** 마지막 log 점과 `.str`(전자 온도)을 진단했다.

![](1001/tap/fig/R1e6_crash_diagnosis.png)
*데이터: `1001/tap/TAPT_ISL_W30LK_L3_R7_R1e6_UD7S_VGm0p2.log` (마지막 45점), `…_UP_{3p0,4p0,4p5,5p0}.str` · 일회성 스크립트*

| 진단 기준 | 정상 구간 | 마지막 20점 |
|---|---|---|
| time step | 2e-8 s | **1e-25 s** |
| 내부 전위 (섬, body) | 변함 | 소수점 3자리까지 고정 |
| gate 전류 | 1e-13 A | **1e-2 A** (변위전류) |
| KCL 잔차 | 1e-15 A | **1e-2 A** |

⚠️ **문제** **가짜 점프였다.** 오른쪽 STL drain 접합 표면의 전자 온도(hcte)가 12000 K를 넘으면서 time step이 붕괴했다. 이 문제를 풀려고 네 가지를 시도했다.

| 시도 | 덱 | 결과 |
|---|---|---|
| solver를 연립 Newton으로 (5.0 V `.str`에서 재시작) | `…_R1e6_RS50_NEWT_VGm0p2.in` | 원래 run과 5자리 일치, **같은 5.284 V에서 중단** |
| hcte 제거 후 4.5 V `.str`에서 재시작 | `…_R1e6_RS45_NOHC_VGm0p2.in` | 0.35 ns 만에 양쪽 래치 → **모델이 달라 이어지지 않음** (모델 섞기 금지) |
| drain 접합 격자 5 nm → 1 nm (MF) | `…_R1e6_UD7S_MF_VGm0p2.in` | 오른쪽 V_LU 3.058 → 2.989 V로 보정, **5.033 V에서 중단** |
| 왼쪽 6e17 (원래 격자) | `…_L6_R7_R1e6_UD75S_VGm0p2.in` | 5.20 V에서 중단 |

![](docs/fig/struct_15_mesh_compare.png)
*격자 비교. 출처: `1001/tap/TAPT_ISL_W30LK_L6_R7_R1e6_UD75S{,_MF}_VGm0p2_INIT.str` · 코드: `tools/make_struct_figs.py`*

✅ **해결: 진짜 원인 찾기.** 멈춘 run을 모두 겹쳐 보니, **오른쪽 STL에 걸린 전압(Vd − 섬 전위)이 약 3.35–3.7 V에 들어가면 예외 없이 멈춘다.**
R = 1e6 Ω에서 왼쪽 래치에 필요한 섬 전위 +2.54 V를 만들려면 I = 2.5e-6 A가 필요하다. 그 전류에서 오른쪽 STL 전압은 3.6 V 이상이라, **R1e6으로는 원리적으로 두 번째 래치까지 계산할 수 없다.**
→ **R = 1e7 Ω**이면 I = 2.5e-7 A, 오른쪽 STL 전압 약 3.0 V로 안전 구간이다 (Step 10).

![](1001/tap/fig/crash_zone_rightSTL.png)
*데이터: `1001/tap/TAPT_ISL_W30LK_*_R*_VGm0p2.log` (R1e6 원래/MF/6e17, R3e5) · 일회성 스크립트*

---

## Step 9. 왼쪽 STL은 래치할 수 있나? → 단독 소자 (10/06)

🎯 **왜** Step 7에서 왼쪽(3e17) 전류는 점프 없이 매끄럽게 올랐다. 섬 전위가 충분해도 **왼쪽 STL 자체가 래치를 못 하는 도핑**일 수 있다. B 소자는 한 번에 하루가 걸리지만, 왼쪽만 떼어 낸 소자는 몇 분이면 판정할 수 있다.

🛠 **어떻게** 같은 격자·gate·모델에서 섬부터 오른쪽을 모두 n+ drain으로 바꾼다 → 단독 소자의 Vd = B 소자에서 필요한 섬 전위. 왼쪽 body 도핑만 바꿔 가며 탐색 (`1001/tap/LEFTONLY_L135_P*_*.in`).

![](docs/fig/struct_13_left_only.png)
*출처: `1001/tap/LEFTONLY_L135_P6e17_UD3_VGm0p2_INIT.str`*

B 소자 안의 왼쪽 STL 전류가 단독 소자 곡선과 2–3배 이내로 겹쳐서, 단독 소자가 대표성이 있음을 먼저 확인했다.

![](1001/tap/fig/LEFT_IdVd_vs_B.png)
*데이터: `1001/tap/LEFTONLY_L135_P3e17_UD6S_VGm0p2.log`, `TAPT_ISL_W30LK_L3_R7_{R3e5,R1e6}_UD7S_VGm0p2` · 일회성 스크립트*

⚠️ **문제** **3e17·5e17은 래치하지 않고 연속적으로 켜진다.** 장벽이 낮아서(1 V에서 약 0.35 eV) 정공이 쌓였다가 한 번에 무너지지 않는다.

✅ **해결** 도핑을 올려 장벽을 세운다. 판정 기준은 **1 mV 구간 전류 상승 + time step 축소**로 정했다.

| 왼쪽 도핑 (hcte) | 1 mV 최대 상승 | V_LU |
|---|---|---|
| 3e17 | 연속 | – |
| 5e17 | 0.04 dec | – (연속) |
| **6e17** | **3.8 dec** | **2.539 V** |
| 7e17 | 5.1 dec | 3.002 V (= B 오른쪽 STL 3.06 V와 일치) |

![](1001/tap/fig/LEFT_doping_compare4.png)
*데이터: `1001/tap/LEFTONLY_L135_P{3e17,5e17,6e17,7e17}_UD6S_VGm0p2.log` · 일회성 스크립트*

6e17은 0 → 3 → 0 V 왕복에서 **히스테리시스**가 있는 진짜 래치다 (켜짐 2.541 V, 꺼짐 2.48–2.32 V). 같은 2.4 V에서 꺼진 상태와 켜진 상태의 장벽 높이가 다르다.

| ![](1001/tap/fig/LEFT6_roundtrip.png) | ![](1001/tap/fig/LEFT6_bistable_EBD.png) |
|---|---|
| 데이터: `1001/tap/LEFTONLY_L135_P6e17_UD3_VGm0p2.log` | 데이터: `…_P6e17_UD3_VGm0p2_{UP,DN}_{2p4,2p5}.str` · 코드: `strfig.py` |

조건 확인 두 가지:
- **ramp 속도**: 7 V/ms로 10배 빠르게 하면 V_LU가 2.645 V로 0.1 V 밀린다 (꺼짐은 같음) → 0.7 V/ms 유지 (`LEFTONLY_L135_P6e17_UD3_R7_VGm0p2.log`).
- **DD (hcte 없음)**: 래치 전압이 0.7–0.8 V 낮아진다 (5e17 1.218, 6e17 1.778, 7e17 2.235 V). 4e17(0.72 V), 5e17(1.22 V)처럼 밴드갭 근처나 그 아래에서도 래치가 나와서, **DD는 impact ionization을 과대평가**한다고 본다.

![](1001/tap/fig/DD_scan_left.png)
*데이터: `1001/tap/LEFTONLY_L135_P*_DD_UP4_VGm0p2.log` (실선), `*_UD6S_*.log` (점선) · 일회성 스크립트*

✅ **결론** 왼쪽 body = **6e17** (래치하는 최저 도핑).

---

## Step 10. 본 소자: 래치 두 번 (10/07)

🎯 **왜** 왼쪽 6e17 + 오른쪽 7e17 B 구조에, Step 8에서 정한 R = 1e7 Ω을 달면 두 번째 래치가 안전 구간 안에서 나올 것.

🛠 **어떻게**
- 구조: 왼쪽 6e17 | lifetime 감소 섬 + 탭 | 오른쪽 7e17, 고운 격자(MF)
- **MixedMode**: 구조와 VG = −0.2 V 상태를 `.str`로 만들고, 회로(drain 전압원, Rtap)에서 불러온다. 0 → 7.5 → 0 V, 0.7 V/ms.

![](docs/fig/struct_14_main_L6.png)
*출처: `1001/tap/TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_VGm0p2_INIT.str`*

```
# 출처: 1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_VGm0p2.in (MixedMode 부분)
.begin
Vdrain 1 0 pwl 0, 0, 1.071429e-02, 7.5, 2.142857e-02, 0
Vgate  2 0 -0.2
Rtap   3 0 1e7
Adev 1=drain 0=source 2=gate 3=tap 0=substrate infile=MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_VGm0p2_VG.str
.numeric lte=0.3 toltr=1e-5
.tran 1e-9 2.142857e-02
.end
```

⚠️ **문제 1: R이 크면 첫 번째 래치의 점프가 작아진다.** R이 오른쪽 STL 전류를 막기 때문이다 (R 1e4: 약 2자리 → R 1e6: 1.3자리). 다만 오른쪽 body 전위는 같이 뛰므로 래치는 있다.

![](1001/tap/fig/first_latch_vs_R.png)
*데이터: `1001/tap/TAPT_ISL_W30LK_L3_R7_R1e4_UD6S_VGm0p2_extract.dat`, `TAPT_ISL_W30LK_L6_R7_R1e6_UD75S_MF_VGm0p2.log` · 일회성 스크립트*

⚠️ **문제 2: hcte 소자 단독 방식은 너무 느리다.** 4–5 V 구간 하나에 31,500 step(약 17시간)이 걸렸다. ramp를 빠르게 하면 V_LU가 밀려서(Step 9) 쓸 수 없다.

✅ **해결: MixedMode + DD로 먼저 확인** → 왕복 전체가 **42분**(1089 step)에 끝났고, **래치가 두 번 나왔다** (그림 0).

| 래치 | 켜짐 (up) | 꺼짐 (down) | 확인 |
|---|---|---|---|
| 1번째 (오른쪽) | **2.254 V** (Itap 1e-10 → 7e-8 A) | 약 1.2 V | DD 단독 7e17 V_LU 2.235 V와 일치 |
| 2번째 (왼쪽) | **3.296 V** (Is 1.8e-7 → 1.1e-4 A, 같은 Vd에서 2 ns) | 3.0 → 2.2 V | 점프 순간 섬 전압 1.72 V ≈ DD 단독 6e17 V_LU 1.778 V |

두 번째 점프가 수치 오류가 아님을 Step 8과 같은 기준으로 확인했다. 점프 동안 Vd 고정, time step 1–5e-10 s로 과정을 따라감, KCL 잔차 1e-15 A 이하, 점프 후 1.13e-4 A에서 안정, 직전 Is 기울기 증가(양의 되먹임).

| ![](1001/tap/fig/MM_DD_EBD_up.png) | ![](1001/tap/fig/MM_DD_2D_up.png) |
|---|---|
| 데이터: `1001/tap/MM_TAPT_…_DD_VGm0p2_T_tr_{1,2,5,6}` (MixedMode 스냅샷 = .str) · 코드: `strfig.py` | 같은 스냅샷, Si 막 정공·전위 지도 |

1.5 V: 둘 다 꺼짐 → 2.5 V: 오른쪽 body만 정공으로 참 → 3.1 V: 오른쪽만 켜짐 → 3.5 V: 양쪽 body 모두 1e18 cm⁻³.
(MixedMode 스냅샷은 저장 전위 기준이 달라 EBD의 밴드 절대 위치가 어긋나 있다. 정공 분포를 보면 된다.)

**한계**
1. DD 결과다. 래치 전압이 hcte보다 0.7–0.8 V 낮게 나오는 모델이다.
2. 이 MixedMode run은 소자 폭이 1 µm로 계산됐다 (저전압 전류가 소자 단독 방식의 정확히 2배). 따라서 R = 1e7 Ω은 0.5 µm 소자 기준 2e7 Ω에 해당한다.
3. 4 V 이상 전류(mA 단위)는 발열이 없는 DD라 비현실적이다.

---

## 트레이드오프 요약

| 조절 변수 | 올리면 좋아지는 것 | 올리면 나빠지는 것 | 현재 선택 |
|---|---|---|---|
| 탭 저항 R | 섬 전위가 적은 전류로 오름, 오른쪽 STL 전압이 안전 구간에 머묾 | 첫 번째 래치 점프가 작아짐, R → ∞이면 직렬 제약 복귀 | 1e7 Ω |
| 섬 폭 | 가로 PNP 결합 약화 | 오른쪽 body 짧아져 V_LU ↓, 결합은 여전 | 30 nm |
| 섬 lifetime ↓ | 정공이 섬에서 재결합 → 분리 | 공정 구현 필요, 래치 창 0.70 → 0.06 V | 1e-12 s |
| 왼쪽 body 도핑 | 급격한 래치 (장벽 ↑) | V_LU ↑ → 필요한 섬 전위 ↑ | 6e17 |
| 물리 모델 hcte | 정확한 impact / 래치 전압 | 고전압 전자 온도 폭주, 매우 느림 | 확인 중 (DD로 먼저) |
| ramp 속도 | 계산 시간 ↓ | V_LU 왜곡 (7 V/ms에서 +0.1 V) | 0.7 V/ms |
| drain 접합 격자 | 래치 전압 정확도 (2 %) | 계산량 ↑, 폭주는 해결 못 함 | 1 nm (MF) |

---

## 현재 상태와 다음 단계

- **실행 중**: `1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_HC_VGm0p2.in`. 같은 소자를 hcte + MixedMode(`width=0.5`)로 계산 중이다.
- **다음**:
  1. hcte에서도 래치 두 번이 나오는지 확인 (예상: 오른쪽 약 3.0 V, 왼쪽은 섬 전위 약 2.54 V일 때)
  2. DD MixedMode를 `width=0.5`로 다시 돌려 R 기준 맞추기
  3. 래치 창이 좁아지는 원인(lifetime 감소?) 확인

---

## 부록: 핵심 데이터 파일

저장소에 올린 log (그 외 raw 데이터는 서버 `/home/ysseo/novel/` 같은 경로):

| Step | 파일 |
|---|---|
| 1 | `0921/STL_NB5p0_localfine.log`, `0921/SPLIT_L5p0_R5p2_X50.log`, `0921/B10_W20_L5p0_R5p2.log` |
| 2 | `0927/BIG_{L3_R7,L7_R3,L8_R2}_X50.log` |
| 3 | `0928/ISL_W30_L3_R7.log`, `0928/idvg_return/IDVGR_BIG_L3_R7_X50_vd1.log` |
| 4 | `0929/splitgate/SG_G2D_m0p2.log` |
| 5 | `1001/tap/TAPT_ISL_W30_L3_R7_{R3e5,R3e4}_VGm0p2.log`, `…_R1e4_UP_VGm0p2.log` |
| 6 | `1001/tap/TAPT_ISL_{W100,W30TC}_L3_R7_R1e4_UD6S_VGm0p2.log`, `TAPT_ISL_W30LK_L3_R7_R1e4_UD6S_VGm0p2_extract.dat` |
| 7 | `1001/tap/TAPT_ISL_W30LK_L3_R7_R3e5_UD7S_VGm0p2_extract.dat`, `…_R1e6_UD7S_VGm0p2.log` |
| 8 | `…_R1e6_RS50_NEWT_VGm0p2.log`, `…_R1e6_UD7S_MF_VGm0p2.log`, `…_L6_R7_R1e6_UD75S_MF_VGm0p2.log` |
| 9 | `1001/tap/LEFTONLY_L135_P*_{UD6S,UD3,UD3_R7,DD_UP4}_VGm0p2.log` |
| 10 | `1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_VGm0p2.log_tr.log` |

`*_extract.dat` 열: `time_s Vd_V Id_A Is_A Itap_A Vtap_internal_V VB_left_V VB_right_V V_island_V` (원본의 20행마다 1행 + |Id| 변화가 큰 행 전부).
