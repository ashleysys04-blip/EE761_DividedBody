#!/bin/bash
# Build paper/ted/main.pdf (IEEE TED submission draft) with Tectonic. Figures come from ../fig (run ../build.sh first) and ../../docs/fig/paper.
cd "$(dirname "$0")"
export XDG_CACHE_HOME="$PWD/../.cache"
[ -f IEEEtran.cls ] || cp ../IEEEtran.cls .
../.bin/tectonic -X compile main.tex
