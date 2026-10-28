#!/bin/bash
# 2026-10-26 (b): replaces queue_1026.sh after ROB_SR1e4; inserts the gate work-function check WF417_BASE next.
# ONE ATLAS job at a time, calculation only. First marks the end of the ROB_SG_W60 run started by queue_1026.sh.
while kill -0 107142 2>/dev/null; do sleep 30; done
echo "end $(date)" >> /home/ysseo/novel/1026_sinkrob/ROB_SG_W60.queue
echo "1026_sinkrob/ROB_SG_W60 $(date)" >> /home/ysseo/novel/1026_sinkrob/queue_1026.log
JOBS="1026_sinkrob/WF417_BASE 1026_sinkrob/ROB_SR1e2 1026_sinkrob/ROB_RES5 1026_sinkrob/ROB_OFFM5 1026_sinkrob/ROB_W60
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
