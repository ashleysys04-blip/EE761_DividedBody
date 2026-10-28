#!/bin/bash
# 2026-10-28 calibration stage 2 (Id-Vd split at V_G 0.4 V). ONE ATLAS job at a time: waits for the 1028_osc queue to finish.
cd /home/ysseo/novel/1010_calib
while pgrep -u ysseo -f queue_1028.sh > /dev/null; do sleep 120; done
for f in TRI_IV_CAL TRI_IV_CAL_BN1p1 TRI_IV_CAL_BN1p2 TRI_IV_CAL_BN0p9 TRI_IV_CAL_AN0p5 TRI_IV_CAL_AN2 TRI_IV_CAL_TAU1e-6 TRI_IV_CAL_TAU1e-8; do
  [ -f $f.queue ] && grep -q '^end' $f.queue && continue
  while [ $(pgrep -u ysseo -x atlas.exe2 | wc -l) -ge 1 ]; do sleep 60; done
  echo "start $(date)" > $f.queue
  deckbuild -ascii -run $f.in > $f.out 2>&1 < /dev/null
  echo "end $(date)" >> $f.queue
  echo "$f $(date)" >> queue_cal2.log
done
echo "ALL DONE $(date)" >> queue_cal2.log
