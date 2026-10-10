#!/bin/bash
# When every DDS_*.in has finished: analyse, plot, mechanism, update README Step 12 block, commit and push.
cd /home/ysseo/novel/1007_ddsplit
LOG=finalize_ddsplit.log
all_done() { for f in DDS_*.in; do q=${f%.in}.queue; [ -f $q ] && grep -q end $q || return 1; done; return 0; }
until all_done; do sleep 300; done
{
  echo "== $(date) all decks done"
  python3 analyze_ddsplit.py && python3 plot_ddsplit.py && python3 mech_ddsplit.py DDS_BASE DDS_BASE_SNAP && python3 update_readme_ddsplit.py
  cd /home/ysseo/novel
  git add -A && git commit -q -m "DD split: all results, latch mechanism and turn-off tests (auto-generated Step 12 block)" && git push
  echo "== $(date) pushed: $(git log --oneline -1)"
} >> $LOG 2>&1
