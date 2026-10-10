# 선행 연구 정리와 이 연구의 위치 (2026-10-10)

> 논문 서론과 비교 표(paper/main.tex, Table "선행 연구 비교")의 근거 문서.
> ✅ = 원문을 직접 읽음 (PDF 제공받음), 🔎 = 초록/서지만 확인 (전문 확인 필요).

## 1. 왜 세 상태(ternary)인가 — 응용 동기

| 근거 | 내용 | 문헌 |
|---|---|---|
| radix 최적값 | 시스템 복잡도가 최소인 radix는 e = 2.718, 가장 가까운 정수는 3 → ternary | ✅ J.-A. Han et al., EDL 46(1) 16–19, 2025 (P-TMOS) 서론 |
| 배선/면적/전력 | MVL은 트랜지스터 수와 배선을 줄여 칩 밀도와 에너지 효율을 높임 | ✅ J.-K. Han et al., EDL 43(7) 1005–1008, 2022 (CMOS ternary + BTS) |
| ternary 회로 블록 | STI/PTI/NTI, decoder, ternary-binary 변환이 필요 | ✅ H.-Y. Kim et al., TED 73(8) 5232–5238, 2026 (SPTI); ✅ S.-J. Han et al., Sci. Rep. 11, 13018, 2021 (TLD) |
| 다중 상태 메모리/뉴런 | multi-valued memory, LLM 시대의 대역폭/전력 요구 | ✅ H.-B. Noh et al., EDL 46(8) 1269–1272, 2025 (triristor) |

## 2. 세 상태를 만드는 기존 방법

| 분류 | 대표 | 소자 수 | 기판 | 메커니즘 | 한계 (원문 기준) |
|---|---|---|---|---|---|
| 비CMOS 소재 | CNTFET, graphene barristor 등 | 1 | – | 소재 고유 | CMOS 호환성 (P-TMOS, BTS 서론) |
| 터널링 T-CMOS | Jeong et al., Nat. Electron. 2019 | 1 | bulk | BTBT 누설 경로 | 모든 상태에 터널 전류 → 정적 전력 (BTS 서론) |
| TS + MOSFET 직렬 | Heo et al., IEDM 2021 (NbO₂) | 2 | – | IMT 문턱 스위치 | TS 누설, 이종 공정 |
| STL 문턱 스위치 + MOSFET | J.-K. Han EDL 2022 (N-TMOS/BTS), J.-A. Han EDL 2025 (P-TMOS) | **2** | SOI/bulk | STL (biristor) | 소자 2개 직렬 |
| feedback FET | Son, Cho, Kim, Sci. Rep. 12, 12907, 2022 | 1 | – | 양의 되먹임 | (전문 확인 필요) 🔎 |
| MOSFET + gate–body diode | H.-Y. Kim et al., TED 2026 (SPTI) | 1+다이오드 | bulk | GBD + MOS | balanced ternary 선택기 |
| **이중 래치 단일 소자** | **Noh et al., EDL 2025 (triristor)** | **1** | **bulk** | **같은 p-well 안의 두 전류 경로**: bulk punchthrough II(1차) + 표면 subthreshold II(2차) | 아래 3절 |

## 3. 가장 가까운 선행 연구: triristor (Noh et al., EDL 2025) ✅

- 소자: bulk Si n-MOSFET, L_G 3 µm, t_ox 20 nm, W 600 µm, shallow p-well (B 2×10¹² cm⁻², 40 keV), S/D As 5×10¹⁵, RTA 1000 °C 7 s. SIMS 프로파일 제공 (Fig. 1e).
- 측정 (V_G = 0.4 V): V_LU,1 = 7.38 V, V_LD,1 = 6.46 V, V_LU,2 = 11.58 V, V_LD,2 = 9.41 V (Fig. 2a).
- 원문 주장: "all prior research has focused on a single latch … no reports on double latches".
- 특징과 한계 (원문 근거):
  1. 두 래치가 **같은 p-well(정공 저장소 하나)** 을 공유. 두 경로의 전류(punchthrough vs 표면)로 나뉨.
  2. **결합되어 있음**: V_B < 0이면 두 래치가 하나로 합쳐짐 (Fig. 2c), 낮은 V_G에서는 1차 래치가 사라짐.
  3. 조절 손잡이가 사실상 V_G 하나: V_G는 1차 래치만 크게 움직이고 2차는 덜 움직임. 두 래치를 독립적으로 설계하는 공정 변수는 제시되지 않음.
  4. 1000회 반복 시 1차 래치 전압이 증가 (잔류 정공), 2차는 안정.
  5. 동작 전압 7–12 V (L_G 3 µm).
  6. TCAD(Silvaco)는 정성 확인용: 시뮬레이션 V_G(0.02–0.1 V)가 측정(0.25–0.4 V)과 다름 → 캘리브레이션 안 됨.

## 4. 이 연구의 차별점 (주장)

| 항목 | triristor (bulk) | 본 연구 (SOI, divided body) |
|---|---|---|
| 정공 저장소 | 1개 (p-well 공유) | **2개, 물리적으로 분리** (n⁺ island + 재결합 sink) |
| 두 래치의 원인 | 같은 body, 두 전류 경로 | **서로 다른 두 STL** (각자의 drain 접합 II) |
| 설계 독립성 | V_G 위주, 결합됨 | **N_A,R → 1차, N_A,L → 2차** 독립 (1차 1.24–2.51 V, 2차 2.28–4.01 V) |
| 루프 분리 | V_B, V_G에 따라 합쳐짐 | 섬 위치·τ_Si로 **완전 분리** (간격 1.12 V), 꺼짐 폭 0.03–0.06 V |
| 기판 | bulk (전기적 floating body) | **SOI (물리적 floating body)**, Tsi 50 nm |
| 동작 전압 | 7–12 V (L_G 3 µm) | 1.2–4.8 V (L_G 300 nm, DD) |
| 대가 | – | tap 단자 + R_tap, 섬의 강한 재결합 필요 (실효 τ ≤ 5×10⁻¹⁴ s) |
| 근거 | 측정 + 정성 TCAD | TCAD만 (캘리브레이션 진행 예정) |

**한 줄 주장**: "SOI 소자 하나 안에서 두 개의 floating body를 재결합 island로 분리하여, 각 body가 독립적인 STL로 동작하는 이중 래치를 처음 제안하고, 두 래치를 서로 다른 공정 변수로 독립 설계할 수 있음을 보인다."

리뷰어 예상 질문과 답:
- "STL 두 개를 회로로 직렬 연결하면 되지 않나?" → 소자 2개 + 배선 대비 한 활성 영역/한 gate. 비교 정량화(면적) 필요 ⚠️.
- "tap 단자가 있으니 3단자가 아니다" → triristor도 gate 포함 3단자. tap R은 poly 저항으로 집적 가정. ⚠️ 면적·공정 논의 필요.
- "섬 재결합 조건이 비현실적" → 손상 주입이 아니라 Si 관통 silicide sink로 등가 구현. ⚠️ TCAD 확인 필요.

## 5. STL/biristor 기반 기술 (배경 인용)

| 문헌 | 내용 | 상태 |
|---|---|---|
| C.-D. Chen et al., "Single-transistor latch in SOI MOSFETs," EDL 9(12) 636–638, 1988 | STL 최초 보고 (SOI) | 🔎 |
| J.-W. Han and Y.-K. Choi, "Biristor—Bistable resistor based on a silicon nanowire," EDL 31(8) 797–799, 2010 | biristor | 🔎 (서지는 triristor 참고문헌에서 확인) |
| D.-O. Kim, D.-I. Moon, Y.-K. Choi, EDL 35(2) 220–222, 2014 | biristor-mode 1T-DRAM | 🔎 |
| D.-I. Moon et al., "Fin-width dependence of BJT-based 1T-DRAM implemented on FinFET," EDL 31(9) 909–911, 2010 | SOI FinFET에서 V_latch의 L_G·W_fin 의존 측정 | 🔎 |
| S. Kim et al., "Carrier lifetime engineering for floating-body cell memory," TED 59(2) 367–373, 2012 | floating body의 lifetime engineering | 🔎 |
| J.-W. Han and M. Meyyappan, "Leaky integrate-and-fire biristor neuron," EDL 39(9) 1457–1460, 2018 | LIF 뉴런 | ✅(서지) |
| J.-K. Han et al., EDL 41(2) 208–211, 2020 | 단일 MOSFET 흥분/억제 뉴런 | ✅(서지) |
| J.-K. Han et al., Sci. Adv. 7, eabg8836, 2021 | SOI(Tsi 50 nm) STL 뉴런 측정, L_G별 firing 전압 | ✅ |
| H.-Y. Kim et al., "A single MOSFET-based oscillator on a bulk-silicon wafer," EDL 45(1) 8–11, 2024 | bulk의 전기적 floating body | ✅(서지) |
| S.-W. Lee et al., "Single transistor latch near 1 V with asymmetric biasing in a MOSFET," TED 71(11) 6539–6543, 2024 | front/back gate로 V_LU ≈ 1 V | 🔎 |
| S. Pazos et al., Nature 640, 69–76, 2025 | 표준 Si 트랜지스터의 시냅스/뉴런 동작 | ✅(서지) |
| K. Gopalakrishnan et al., I-MOS, IEDM 2002; K. E. Moselund et al., PIMOS, SSE 52(9) 2008 | II 기반 급격한 스위칭 | ✅(서지) |
| W. Maes, K. De Meyer, R. Van Overstraeten, SSE 33(6) 705–718, 1990 | impact ionization 계수 리뷰 | ✅(서지) |
| E. Kim and D. Lim, Micromachines 14(12) 2165, 2023 | SOI biristor Silvaco TCAD (시뮬레이션만) | 🔎 웹 전문 |
| S. Cristoloveanu et al., ECS Trans. 66, 2015 | FD-SOI 1T-DRAM 리뷰 (MSDRAM, A2RAM, Z2-FET) | 🔎 |

## 6. 캘리브레이션 데이터 후보 (우선순위)

| 순위 | 문헌 | 측정 데이터 | 공정/도핑 정보 | 판단 |
|---|---|---|---|---|
| 1 | **Noh, EDL 2025 (triristor)** ✅ | V_LU/V_LD × 2, V_G 0.25–0.4 V, V_B sweep | **공정 조건 전부 + SIMS** | 최우선. 도핑을 알고 있어 impact 계수·lifetime만 맞추면 됨. 이중 래치 자체를 재현 → 모델이 "이중 래치를 과대/과소 예측하지 않음"을 보여줌. 단점: bulk, L_G 3 µm |
| 2 | Han, Sci. Adv. 2021 ✅ | V_firing vs L_G (3점), Id-Vd 1개 | Tsi 50, BOX 140, ONO 3/6/8 nm, **body 도핑 없음**, trap 전하 미지 | SOI·Tsi 동일. 보조 검증(L_G 추세)용 |
| 3 | Lee, TED 71(11) 2024 ✅ | V_LU vs back-gate (1.13 V까지), 0–3 V 왕복 | SOI, **Tsi 50 nm, BOX 140 nm**, EOT 13 nm, L_G 500 nm, W 450 nm, n⁺ poly; **body 도핑 미기재** | 우리 SOI 치수와 거의 같음. back-gate 의존성으로 2차 검증 가능하나 도핑이 미지수 |
| 4 | Moon, EDL 31(9) 2010 ✅ | V_latch vs L_G, W_fin | SOI FinFET, **undoped fin**, EOT 10 nm, L_G 300 nm, n⁺ poly, Silvaco | 도핑이 "undoped"로 명확. 3D FinFET이라 2D와 직접 비교는 어려움. W_fin 의존성이 nonlocal(에너지 이완) 효과 때문이라고 Silvaco로 보임 → DD 한계 논의 인용 |
| 5 | Chen, EDL 9(12) 1988 ✅ | 최초 SOI STL, Id-Vg 히스테리시스 | SIMOX, t_ox 26 nm, body **1×10¹⁷**, L 1.8–4 µm; 2×10¹⁶ 소자는 래치 없음 | 정성 근거("도핑이 래치에 가장 큰 영향", "lifetime이 길수록 낮은 V_DS에서 유지") 인용용 |

출처(웹 검색): IEEE Xplore 20420 (Chen 1988), pure.ewha.ac.kr (Moon 2010, Kim 2012), scholarworks.sogang.ac.kr (Lee 2024), pmc.ncbi.nlm.nih.gov/articles/PMC10745293 (Kim & Lim 2023), sites.brown.edu (Cristoloveanu 2015).
