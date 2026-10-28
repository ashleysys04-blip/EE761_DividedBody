#!/bin/bash
# 2026-10-28 Step 16 oscillation queue. ONE ATLAS job at a time (user rule): waits for any running atlas (ROB_C10p) first.
JOBS="OSC_R_1n OSC_L_600n OSC_R_3n OSC_L_800n"
d=/home/ysseo/novel/1028_osc
for f in $JOBS; do
  [ -f $d/$f.queue ] && grep -q '^end' $d/$f.queue && continue
  while [ $(pgrep -u ysseo -x atlas.exe2 | wc -l) -ge 1 ]; do sleep 60; done
  cd $d; echo "start $(date)" > $f.queue
  deckbuild -ascii -run $f.in > $f.out 2>&1 < /dev/null
  echo "end $(date)" >> $f.queue
  echo "$f $(date)" >> $d/queue_1028.log
done
echo "ALL DONE $(date)" >> $d/queue_1028.log
