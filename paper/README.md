# Paper (IEEE TED style)

- `main.pdf` — the paper (Korean body text, English key terms). Every figure caption lists its data file(s), relative to the repository root.
- `main.tex` — source. `make_figs.py` draws `fig/fig3–fig10` from the simulation logs; Fig. 1–2 are `../docs/fig/paper/`.
- `paperdevice.py` — fills the combined-device sentence in Section VI (`paperdevice.tex`) from `1007_ddsplit/ddsplit_summary.dat`.

Build (needs the Tectonic binary; it is not committed):

```bash
mkdir -p .bin && curl -sL https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-x86_64-unknown-linux-musl.tar.gz | tar -xz -C .bin
./build.sh
```

The server's TeX Live 2013 LuaLaTeX is broken (Lua library mismatch) and has no Korean packages, so Tectonic (XeTeX + xeCJK, NanumGothic for Hangul, TeX Gyre Termes for Latin) is used instead.
