#!/bin/bash
# When the two combined-device runs finish: analyse, refresh figures and the paper sentence, rebuild PDF, update README, commit/push.
cd /home/ysseo/novel/1007_ddsplit
LOG=/home/ysseo/novel/paper/finalize_paper.log
for f in DDS_TE8_XS60_NR8e17_RD1e5 DDS_TE5em9_XS60_NR8e17_RD1e5; do until grep -q end $f.queue 2>/dev/null; do sleep 120; done; done
{
  echo "== $(date) paper decks done"
  python3 analyze_ddsplit.py > /dev/null && python3 plot_ddsplit.py > /dev/null && python3 update_readme_ddsplit.py
  python3 ../paper/paperdevice.py
  ../paper/build.sh > ../paper/build.log 2>&1 && echo "pdf built: $(pdfinfo ../paper/main.pdf | grep Pages)"
  cd /home/ysseo/novel
  git add -A
  git -c user.name=ysseo -c user.email=ashleysys04@gmail.com commit -q -m "Paper: combined two-rectangle device results (Fig. 9d) and rebuilt PDF"
  git fetch -q origin && git rebase origin/main && git push
  echo "== $(date) pushed: $(git log --format='%h %an <%ae> %s' -1)"
} >> $LOG 2>&1
