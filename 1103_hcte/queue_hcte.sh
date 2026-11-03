#!/bin/bash
# 2026-11-03: hcte check of the coupled devices (make_hcte.py). One ATLAS job at a time, kill after 5 h (same rule as 1030_islw/queue_1030.sh).
N=/home/ysseo/novel; LOG=$N/1103_hcte/queue_hcte.log
JOBS="HCD_W030 HCD_W120 HCD_W060 HCD_W120_KILL"   # 11/03: MixedMode HC_* stop at the start (island 60 %), device-only versions (make_hcte_dev.py)
d=$N/1103_hcte; cd $d
for f in $JOBS; do
  grep -q '^end' $f.queue 2>/dev/null && continue
  echo "start $(date)" > $f.queue; echo "$f start $(date)" >> $LOG
  timeout -k 60 5h deckbuild -ascii -run $f.in > $f.out 2>&1 < /dev/null; rc=$?
  if grep -q "Can not get needed licenses" $f.out; then   # no licence: leave the deck unstarted and stop (run_when_licensed.sh retries)
    rm -f $f.queue; echo "$f LICENSE FAIL, queue stopped $(date)" >> $LOG; exit 3
  fi
  if [ $rc -eq 124 ] || [ $rc -eq 137 ]; then
    for p in $(pgrep -u ysseo atlas); do [ "$(readlink /proc/$p/cwd)" = "$d" ] && kill -9 $p; done
    echo "end $(date) KILLED (over 5 h)" >> $f.queue; echo "$f KILLED over 5 h $(date)" >> $LOG
  else
    echo "end $(date) rc=$rc" >> $f.queue; echo "$f end rc=$rc $(date)" >> $LOG
  fi
done
echo "ALL DONE $(date)" >> $LOG
