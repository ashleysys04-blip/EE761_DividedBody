#!/bin/bash
# Build paper/main.pdf with Tectonic (XeTeX + xeCJK). Tectonic binary: paper/.bin/tectonic (not in git; see README in this folder).
cd "$(dirname "$0")"
export XDG_CACHE_HOME="$PWD/.cache"
python3 make_figs_ext.py > /dev/null 2>&1 || echo "make_figs_ext failed"   # also runs make_figs.py (imported)
[ -f IEEEtran.cls ] || curl -sL -o IEEEtran.cls https://mirrors.ctan.org/macros/latex/contrib/IEEEtran/IEEEtran.cls
.bin/tectonic -X compile main.tex
