#!/bin/bash
# 2026-10-26 queue: ONE ATLAS job at a time (user choice). Calculation only, no auto analysis / push.
# Order: calibration Id-Vg (short) -> sink robustness, most important questions first.
JOBS="1010_calib/TRI_IDVG_DP0p28_RC65 1010_calib/TRI_IDVG_DP0p00_RC65 1010_calib/TRI_IDVG_DP0p20_RC65 1010_calib/TRI_IDVG_DP0p35_RC65 1010_calib/TRI_IDVG_DP0p28_RC0
 1026_sinkrob/ROB_SR1e4 1026_sinkrob/ROB_SG_W60 1026_sinkrob/ROB_SR1e2 1026_sinkrob/ROB_RES5 1026_sinkrob/ROB_OFFM5 1026_sinkrob/ROB_W60
 1026_sinkrob/ROB_SR1e6 1026_sinkrob/ROB_RES15 1026_sinkrob/ROB_OFFP5 1026_sinkrob/ROB_W100 1026_sinkrob/ROB_SG_W100 1026_sinkrob/ROB_C100p 1026_sinkrob/ROB_C10p"
for job in $JOBS; do
  d=/home/ysseo/novel/$(dirname $job); f=$(basename $job)
  [ -f $d/$f.queue ] && grep -q '^end' $d/$f.queue && continue
  while [ $(pgrep -u ysseo -x atlas.exe2 | wc -l) -ge 1 ]; do sleep 60; done
  cd $d; echo "start $(date)" > $f.queue
  deckbuild -ascii -run $f.in > $f.out 2>&1 < /dev/null
  echo "end $(date)" >> $f.queue
  echo "$job $(date)" >> /home/ysseo/novel/1026_sinkrob/queue_1026.log
done
echo "ALL DONE $(date)" >> /home/ysseo/novel/1026_sinkrob/queue_1026.log
