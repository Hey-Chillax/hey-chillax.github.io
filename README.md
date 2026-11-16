# hey-chillax.github.io

Personal homepage of Yi Zhang (张益): <https://hey-chillax.github.io>

Plain HTML and CSS with a few lines of JavaScript. There is no framework and no build step: GitHub Pages serves the files as they are.

## Layout

```text
index.html                 home: about, research directions, projects, publications, education, skills
projects/*.html            project reports (Scaffold-OPD, StepCredit-RL)
404.html                   page-not-found
assets/css/site.css        styles, light / dark colours, chart colours
assets/js/site.js          language switch (English / 中文) and the e-mail link
assets/fonts/              web-font subsets and their licenses
assets/img/                photo, social card, icons
files/                     public CV (PDF)
tools/figures.py           which version of each figure is final, plus the data tables shown under them
tools/figlib.py            small SVG toolkit and data loading shared by the figures
tools/figkit.py            diagram parts: tinted panels, token squares, chips, line icons, math with sub/superscripts
tools/make_figures.py      writes the figures into the pages; can also export them as standalone SVG files
tools/lab/                 every figure's iterations: r1_*.py, r2_*.py, r3.py (three rounds, each with an aesthetic and an
                           innovative version), v2/ (the previous generation) and figs_*.py (the first one)
tools/data/                data behind the figures, and the glyph widths used to lay out their text
tools/make_assets.py       builds the font subsets, photo, social card and icons
```

## Editing

- **Text.** Every sentence is written twice, as `<span lang="en">` and `<span lang="zh-CN">` (or the same attribute on a block). Edit both. The page shows the visitor's browser language first and remembers the choice made with the switch.
- **Figures.** Charts and diagrams are inline SVG between `<!-- fig:NAME -->` and `<!-- /fig:NAME -->`. Change the data in `tools/data/` or the drawing in `tools/figures.py`, then run `python3 tools/make_figures.py` (standard library only). Colours are CSS classes, so the figures follow the light and dark themes; each figure is drawn at a desktop and a phone width.
- **Standalone figures.** `python3 tools/make_figures.py --export DIR` also writes every figure to `DIR/en/` and `DIR/zh/` as a self-contained SVG with plain colour attributes, ready for slides. `--theme dark` writes dark versions and `--embed-fonts` inlines the web font, which an SVG shown as an image needs; the GitHub profile README uses the two project cards exported this way.
- **Where the drawings are.** The final figures are the round-3 picks: `tools/figures.py` (`PICKS3`) chooses between the aesthetic and the innovative version in `tools/lab/r3.py`, and some of those reuse functions from earlier rounds. Method diagrams and the two project thumbnails use the hand-drawn face Comic Neue (`YZ Hand`, class `hand` on the SVG); charts use the site's sans. The two framework diagrams are drawn 880 px wide (`WIDE` in `tools/figures.py`) and break out of the text column on wide screens (`figure.fig.wide`).
- **Comparing versions.** `python3 tools/lab/rounds.py [NAME ...]` writes `tools/lab/rounds.html`: for each figure, v2 and the two versions of every round, with the pick of each round ticked (`PICKS`); `ROUNDS=3` shows one round only. Open it through the preview server. `tools/lab/figure_lab.py` does the same for the first generation.
- **Fonts and images.** The serif face is used only for the name; its Chinese subset contains just the characters of the page headings. After adding headings with new characters, or changing the photo or its crop (`PORTRAIT_BOX`), run `python tools/make_assets.py` (needs Pillow, fontTools and brotli; see its header). It also rewrites `tools/data/font_widths.json`, so rerun `tools/make_figures.py` afterwards.
- **Preview.** Run `python3 -m http.server` in this directory and open <http://localhost:8000>.

## Credits

Text, photo and data © Yi Zhang. Fonts are under the SIL Open Font License 1.1; see `assets/fonts/`.
