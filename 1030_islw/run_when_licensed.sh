#!/bin/bash
# 2026-11-02: after the 11:33 reboot the Silvaco licence (SFLM, RPC on this host) was not available for a while.
# Run queue_1030.sh; if a deck gets no licence it stops with exit 3 -> wait 10 min and try again.
# (A TCP check of 27000/24020 is not a valid test: SFLM is served over RPC.)
cd /home/ysseo/novel/1030_islw; LOG=queue_1030.log
while true; do
  ./queue_1030.sh; [ $? -eq 3 ] && { sleep 600; continue; }
  break
done
