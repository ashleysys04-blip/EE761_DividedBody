#!/bin/bash
# 2026-11-03 (copied from 1030_islw): the Silvaco licence (SFLM, RPC on this host) can be unavailable after a reboot.
# Run queue_hcte.sh; if a deck gets no licence it stops with exit 3 -> wait 10 min and try again.
# (A TCP check of 27000/24020 is not a valid test: SFLM is served over RPC.)
cd /home/ysseo/novel/1103_hcte; LOG=queue_hcte.log
while true; do
  ./queue_hcte.sh; [ $? -eq 3 ] && { sleep 600; continue; }
  break
done
