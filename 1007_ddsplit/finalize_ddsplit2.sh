#!/bin/bash
# After batch 4: analyse, plot, mechanism, update README Step 12 block, commit as ysseo <ashleysys04@gmail.com>, rebase on GitHub, push.
cd /home/ysseo/novel/1007_ddsplit
LOG=finalize_ddsplit2.log
all_done() { for f in DDS_*.in; do q=${f%.in}.queue; [ -f $q ] && grep -q end $q || return 1; done; return 0; }
until all_done; do sleep 300; done
{
  echo "== $(date) all decks done"
  python3 analyze_ddsplit.py && python3 plot_ddsplit.py && python3 mech_ddsplit.py DDS_BASE DDS_BASE_SNAP DDS_TE8_SNAP && python3 update_readme_ddsplit.py
  cd /home/ysseo/novel
  git add -A
  git -c user.name=ysseo -c user.email=ashleysys04@gmail.com commit -q -m "DD split batch 4: sharp turn-off condition (Si lifetime 1e-8 s) re-tuned with doping, R, Vg, island; auto-generated Step 12 block"
  git fetch -q origin && git rebase origin/main && git push
  echo "== $(date) pushed: $(git log --format='%h %an <%ae> %s' -1)"
} >> $LOG 2>&1
