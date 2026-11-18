# Fonts

| File | Source | License |
|---|---|---|
| `YZSerif-Regular.woff2`, `YZSerif-Semibold.woff2` | Subsets of Adobe [Source Serif 4](https://github.com/adobe-fonts/source-serif) | SIL OFL 1.1, `LICENSE-SourceSerif4.md` |
| `YZSans-Regular.woff2`, `YZSans-Semibold.woff2` | Subsets of Adobe [Source Sans 3](https://github.com/adobe-fonts/source-sans) | SIL OFL 1.1, `LICENSE-SourceSans3.md` |
| `NotoSerif-Regular.subset.woff2`, `NotoSerif-Italic.subset.woff2`, `NotoSerif-SemiBold.subset.woff2` | Latin subsets of [Noto Serif](https://github.com/notofonts/latin-greek-cyrillic), the page text face since 2026-11-18 | SIL OFL 1.1, `LICENSE-NotoSerif.txt` |
| `NotoSerifSC-Regular.subset.woff2`, `NotoSerifSC-SemiBold.subset.woff2` | Subsets of [Noto Serif CJK SC](https://github.com/notofonts/noto-cjk), every CJK character on the pages (the Chinese page text) | SIL OFL 1.1, `LICENSE-NotoSerifCJK.txt` |
| `NotoSerifSC-Bold.subset.woff2` | Subset of [Noto Serif CJK SC](https://github.com/notofonts/noto-cjk) Bold, only the characters used in headings | SIL OFL 1.1, `LICENSE-NotoSerifCJK.txt` |

The Latin subsets are renamed because Source Serif 4 and Source Sans 3 reserve the font name “Source”, and the OFL does not allow modified versions to use a Reserved Font Name. `tools/make_assets.py` builds all of them; `python tools/make_assets.py --text-fonts` rebuilds only the page text face, which is needed after adding Chinese text. The YZ Serif and Bold CJK files are no longer used by the pages (the GitHub profile banner still inlines YZ Serif).
