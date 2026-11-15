# hey-chillax.github.io

Personal homepage of Yi Zhang (张益): <https://hey-chillax.github.io>

Plain HTML and CSS with a few lines of JavaScript. There is no framework and no build step: GitHub Pages serves the files as they are.

## Layout

```text
index.html                 home: about, news, projects, publications, education, skills
projects/*.html            project reports (Scaffold-OPD, StepCredit-RL)
404.html                   page-not-found
assets/css/site.css        styles, light / dark colours, chart colours
assets/js/site.js          language switch (English / 中文) and the e-mail link
assets/fonts/              web-font subsets and their licenses
assets/img/                photo, social card, icons
files/                     public CV (PDF)
tools/figures.py           the charts and diagrams (final versions)
tools/figlib.py            small SVG toolkit and data loading shared by the figures
tools/make_figures.py      writes the figures into the pages; can also export them as standalone SVG files
tools/lab/                 earlier versions of every figure (original, aesthetic, innovative) and a comparison page
tools/data/                data behind the figures, and the glyph widths used to lay out their text
tools/make_assets.py       builds the font subsets, photo, social card and icons
```

## Editing

- **Text.** Every sentence is written twice, as `<span lang="en">` and `<span lang="zh-CN">` (or the same attribute on a block). Edit both. The page shows the visitor's browser language first and remembers the choice made with the switch.
- **Figures.** Charts and diagrams are inline SVG between `<!-- fig:NAME -->` and `<!-- /fig:NAME -->`. Change the data in `tools/data/` or the drawing in `tools/figures.py`, then run `python3 tools/make_figures.py` (standard library only). Colours are CSS classes, so the figures follow the light and dark themes; each figure is drawn at a desktop and a phone width.
- **Standalone figures.** `python3 tools/make_figures.py --export DIR` also writes every figure to `DIR/en/` and `DIR/zh/` as a self-contained SVG with plain colour attributes, ready for slides. `--theme dark` writes dark versions and `--embed-fonts` inlines the web font, which an SVG shown as an image needs; the GitHub profile README uses the two project cards exported this way.
- **Comparing versions.** `python3 tools/lab/figure_lab.py` writes `tools/lab/gallery.html`, which shows each figure's original, aesthetic, innovative and final versions side by side; open it through the preview server.
- **Fonts and images.** Headings use a serif subset that contains only the Chinese characters the headings need. After adding headings with new characters, or changing the photo, run `python tools/make_assets.py` (needs Pillow, fontTools and brotli; see its header). It also rewrites `tools/data/font_widths.json`, so rerun `tools/make_figures.py` afterwards.
- **Preview.** Run `python3 -m http.server` in this directory and open <http://localhost:8000>.

## Credits

Text, photo and data © Yi Zhang. Fonts are under the SIL Open Font License 1.1; see `assets/fonts/`.
