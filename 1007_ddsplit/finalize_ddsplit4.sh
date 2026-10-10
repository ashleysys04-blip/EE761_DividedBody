#!/bin/bash
# After batch 5 + DDS_TE8_XS60_SNAP: full .str analysis (mechanism + hole balance), README Step 12 and Step 13 blocks,
# commit as ysseo <ashleysys04@gmail.com>, rebase on GitHub, push.
cd /home/ysseo/novel/1007_ddsplit
LOG=finalize_ddsplit4.log
all_done() { for f in DDS_*.in; do q=${f%.in}.queue; [ -f $q ] && grep -q end $q || return 1; done; return 0; }
until all_done; do sleep 300; done
{
  echo "== $(date) all decks done"
  python3 analyze_ddsplit.py > /dev/null && echo analyze ok
  python3 plot_ddsplit.py && echo plot ok
  python3 mech_ddsplit.py DDS_BASE DDS_BASE_SNAP DDS_TE8_SNAP DDS_TE8_XS60_SNAP > /dev/null && echo mech ok
  python3 mech2_ddsplit.py DDS_BASE_SNAP DDS_TE8_SNAP DDS_TE8_XS60_SNAP > /dev/null && echo mech2 ok
  python3 update_readme_ddsplit.py && python3 update_readme_step13.py
  cd /home/ysseo/novel
  git add -A
  git -c user.name=ysseo -c user.email=ashleysys04@gmail.com commit -q -m "DD split batch 5 (two separated abrupt rectangles) and Step 13: latch mechanism from .str (hole balance: impact ionization vs recombination)"
  git fetch -q origin && git rebase origin/main && git push
  echo "== $(date) pushed: $(git log --format='%h %an <%ae> %s' -1)"
} >> $LOG 2>&1
