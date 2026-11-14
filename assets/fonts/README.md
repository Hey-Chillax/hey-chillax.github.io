# Fonts

| File | Source | License |
|---|---|---|
| `YZSerif-Regular.woff2`, `YZSerif-Semibold.woff2` | Subsets of Adobe [Source Serif 4](https://github.com/adobe-fonts/source-serif) | SIL OFL 1.1, `LICENSE-SourceSerif4.md` |
| `YZSans-Regular.woff2`, `YZSans-Semibold.woff2` | Subsets of Adobe [Source Sans 3](https://github.com/adobe-fonts/source-sans) | SIL OFL 1.1, `LICENSE-SourceSans3.md` |
| `NotoSerifSC-Bold.subset.woff2` | Subset of [Noto Serif CJK SC](https://github.com/notofonts/noto-cjk) Bold, only the characters used in headings | SIL OFL 1.1, `LICENSE-NotoSerifCJK.txt` |

The Latin subsets are renamed because Source Serif 4 and Source Sans 3 reserve the font name “Source”, and the OFL does not allow modified versions to use a Reserved Font Name. `tools/make_assets.py` builds all five files.
