#!/bin/bash
# Lane B (2026-10-28): LSTL_P7e17 / P8e17 keep running in the original loop; when P8e17 ends, take calibration decks.
. /home/ysseo/novel/1028_osc/cal_pull.sh
while ! grep -q '^end' /home/ysseo/novel/1028_leftstl/LSTL_P8e17.queue 2>/dev/null; do sleep 30; done
cal_pull B
echo "ALL DONE lane B $(date)" >> /home/ysseo/novel/1010_calib/queue_cal2.log
