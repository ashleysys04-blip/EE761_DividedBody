#!/bin/bash
# 2026-11-02: ISLW200_KILL was replaced by ISLW120_KILL in queue_1030.sh while the queue was already running
# (the running instance still has the old job list and skips ISLW200_KILL via its .queue file).
# Wait for that run (run_when_licensed.sh PID given as $1) to finish, then run the queue once more: only ISLW120_KILL is left.
cd /home/ysseo/novel/1030_islw
while kill -0 "$1" 2>/dev/null; do sleep 60; done
./run_when_licensed.sh
