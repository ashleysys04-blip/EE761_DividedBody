#!/usr/bin/env python3
# Renders every device structure referenced in README.md into docs/fig/struct_*.png (source .str noted on each figure).
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from strstruct import draw
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
N = '/home/ysseo/novel/'; O = N + 'docs/fig/'
S = [
 ('00_ver2_split', 'split_body_init.str', 'Phase 0 (08/27): split-body FDSOI, P / P+ body (ver2)', None, None, 'early deck ver2.in'),
 ('00b_0908_sw_orig', '0908/sw_orig_idvd.str', 'Phase 0 (09/08): drain-side heavy split (NA_src 1e17 / NA_drn 3e18), Tsi 20 nm', None, None, '0908/sw_idvd_orig.in'),
 ('01_uniform_STL', '0921/STL_NB5p0_localfine_END.str', '01 reference STL: uniform body 5e17, Lg 0.3 um, Tsi 50 nm', None, None, '0921/STL_NB5p0_localfine.in'),
 ('02_small_split', '0921/SPLIT_L5p0_R5p2_X50_END.str', '02 small doping split: L 5.0e17 | R 5.2e17 (split at Lg/2)', None, None, '0921/SPLIT_L5p0_R5p2_X50.in'),
 ('03_notch_bridge', '0921/B10_W20_L5p0_R5p2_END.str', '03 oxide notch (W 20 nm) + top Si bridge (B 10 nm) between L / R bodies', None, None, '0921/B10_W20_L5p0_R5p2.in'),
 ('04_big_split', '0927/BIG_L3_R7_X50_END.str', '04 large doping split: L 3e17 | R 7e17', None, None, '0927/BIG_L3_R7_X50.in'),
 ('05_tsi_split', '0928/TSI_L20_R50_END.str', '05 Tsi split: left 20 nm | right 50 nm', None, None, '0928/TSI_L20_R50.in'),
 ('06_floating_island', '0928/ISL_W30_L3_R7_END.str', '06 floating n+ island (30 nm, full Tsi) between L 3e17 | R 7e17', None, None, '0928/ISL_W30_L3_R7.in'),
 ('07_split_gate', '0929/splitgate/SG_G2D_m0p2_END.str', '07 split gate over L / R bodies (G2 on drain side)', None, None, '0929/splitgate/SG_G2D_m0p2.in'),
 ('08_nnpn', '1001/nnpn/NNPN_D_Ln150_N1e16_P5e17_HRS.str', '08 n+ / n- / p / n+ body (n- 150 nm 1e16, p 5e17)', None, None, '1001/nnpn/NNPN_D_Ln150_N1e16_P5e17.in'),
 ('09_tap_W30', '1001/tap/TAPT_ISL_W30_L3_R7_R3e5_VGm0p2_INIT.str', '09 tapped island: n+ neck through BOX -> tap electrode -> R -> GND', (0.3, 1.0), (0.27, -0.13), '1001/tap/TAPT_ISL_W30_L3_R7_R3e5_VGm0p2.in'),
 ('10_tap_W100', '1001/tap/TAPT_ISL_W100_L3_R7_R1e4_UD6S_VGm0p2_INIT.str', '10 tapped island, island width 100 nm (W100)', (0.3, 1.0), (0.27, -0.13), '1001/tap/TAPT_ISL_W100_L3_R7_R1e4_UD6S_VGm0p2.in'),
 ('11_top_contact', '1001/tap/TAPT_ISL_W30TC_L3_R7_R1e4_UD6S_VGm0p2_INIT.str', '11 (C) island tapped from the top (split gate, ohmic contact on the island)', (0.3, 1.0), (0.27, -0.13), '1001/tap/TAPT_ISL_W30TC_L3_R7_R1e4_UD6S_VGm0p2.in'),
 ('12_lifetime_killed', '1001/tap/TAPT_ISL_W30LK_L3_R7_R1e4_UD6S_VGm0p2_INIT.str', '12 (B) tapped island with carrier lifetime 1e-12 s in island + neck (same geometry as 09)', (0.3, 1.0), (0.27, -0.13), '1001/tap/TAPT_ISL_W30LK_L3_R7_R1e4_UD6S_VGm0p2.in'),
 ('13_left_only', '1001/tap/LEFTONLY_L135_P6e17_UD3_VGm0p2_INIT.str', '13 standalone LEFT STL: body 135 nm (3e17..7e17), everything right of the island = n+ drain', (0.3, 1.0), (0.27, -0.13), '1001/tap/LEFTONLY_L135_P6e17_UD3_VGm0p2.in'),
 ('14_main_L6', '1001/tap/TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_VGm0p2_INIT.str', '14 main device: left 6e17 | lifetime-killed island + tap | right 7e17, fine mesh', (0.3, 1.0), (0.27, -0.13), '1001/tap/TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_VGm0p2.in'),
]
for tag, f, title, xl, yl, deck in S:
    draw(N + f, O + f'struct_{tag}.png', title=title, xlim=xl, ylim=yl, note='deck: ' + deck)
    print('ok', tag)
# mesh refinement comparison at the right drain junction
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
for a, (f, t) in zip(ax, [('1001/tap/TAPT_ISL_W30LK_L6_R7_R1e6_UD75S_VGm0p2_INIT.str', 'original mesh (5 nm at drain junction)'),
                         ('1001/tap/TAPT_ISL_W30LK_L6_R7_R1e6_UD75S_MF_VGm0p2_INIT.str', 'fine mesh MF (1 nm, surface 2 nm)')]):
    draw(N + f, None, title=t, xlim=(0.74, 0.84), ylim=(0.06, -0.025), mesh=True, ax=a, note='source: ' + f)
fig.suptitle('Mesh refinement at the right drain junction (x = 800 nm)', fontsize=11); fig.tight_layout(); fig.savefig(O + 'struct_15_mesh_compare.png', dpi=130)
print('ok mesh')
