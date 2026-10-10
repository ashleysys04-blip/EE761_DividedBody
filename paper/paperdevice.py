#!/usr/bin/env python3
"""Writes paper/paperdevice.tex (sentence for Section VI) from the combined-device runs in ddsplit_summary.dat / ddsplit_rect.dat."""
import os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); D = os.path.join(R, '1007_ddsplit')
S = {l.split()[0]: l.split() for l in open(os.path.join(D, 'ddsplit_summary.dat')) if not l.startswith('#')}
Q = {l.split()[0]: l.split() for l in open(os.path.join(D, 'ddsplit_rect.dat')) if not l.startswith('#')}
out = []
for n, tau in (('DDS_TE8_XS60_NR8e17_RD1e5', '10^{-8}'), ('DDS_TE5em9_XS60_NR8e17_RD1e5', '5\\times10^{-9}')):
    if n not in S or n not in Q: continue
    s, q = S[n], Q[n]
    v1, v2, offl, offr = float(s[2]), float(s[4]), float(s[6]), float(s[7])
    sep, wl, wr, f3 = float(q[3]), float(q[4]), float(q[5]), float(q[7])
    out.append(f'$\\tau_{{Si}}={tau}$~s에서 루프 1은 {offr:.2f}--{v1:.2f}~V, 루프 2는 {offl:.2f}--{v2:.2f}~V이고 간격은 {sep:.2f}~V이다. '
               f'꺼짐 폭은 {wr:.3f}/{wl:.3f}~V, 상태 III 전류 기울기는 {f3:.1f}자리이다.')
open(os.path.join(R, 'paper', 'paperdevice.tex'), 'w').write(' '.join(out) + '\n' if out else '(조합 소자 계산 진행 중.)\n')
print('\n'.join(out))
