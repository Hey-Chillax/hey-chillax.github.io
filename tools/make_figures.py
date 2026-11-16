#!/usr/bin/env python3
"""Write the site's figures into the HTML pages, and optionally export them as standalone SVG files.

Every figure lives between <!-- fig:NAME --> and <!-- /fig:NAME --> in a page; running this script replaces what
is between the markers. The drawings are in tools/figures.py (final versions; earlier versions in tools/lab/),
the shared toolkit in tools/figlib.py and the data in tools/data/. On the page, colours are CSS classes, so the
figures follow the light / dark theme, and text that differs by language is written twice (lang="en" /
lang="zh-CN") for the page's language switch.

    python3 tools/make_figures.py                    # update the pages (standard library only)
    python3 tools/make_figures.py --export DIR       # also write DIR/en/NAME.svg and DIR/zh/NAME.svg

Exported files are self-contained: one language, light theme, colours written as plain attributes instead of CSS
classes, so they open the same way in a browser, Inkscape, Keynote or PowerPoint.
"""
import argparse
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import figures  # noqa: E402
from figlib import LG, ROOT, SM  # noqa: E402

PAGES = {
    'index.html': ['card-opd', 'card-scr'],
    'projects/scaffold-opd.html': ['opd-pipeline', 'opd-takeover', 'opd-methods', 'opd-budget', 'opd-training', 'opd-compute'],
    'projects/stepcredit-rl.html': ['scr-pipeline', 'scr-steplevel', 'scr-sft-rl', 'scr-vs-grpo', 'scr-updates', 'scr-hotpotqa'],
}


def markup(name):
    fn, table = figures.FIGS[name]
    if name in figures.CARDS:
        return fn().render()
    out = fn(figures.WIDE.get(name, LG)).render('v-lg') + fn(SM).render('v-sm')
    return out + (table() if table else '')


def inject():
    for page, names in PAGES.items():
        path = ROOT / page
        src = path.read_text(encoding='utf-8')
        for name in names:
            pat = re.compile(rf'(<!-- fig:{re.escape(name)} -->).*?(<!-- /fig:{re.escape(name)} -->)', re.S)
            if not pat.search(src):
                raise SystemExit(f'{page}: marker for {name} not found')
            src = pat.sub(lambda m, n=name: m.group(1) + markup(n) + m.group(2), src)
        path.write_text(src, encoding='utf-8')
        print(f'{page}: {len(names)} figures')


# ----------------------------------------------------------------------------- standalone export
FONT = "'Source Sans 3', 'Source Sans Pro', 'Noto Sans CJK SC', 'Source Han Sans SC', 'Microsoft YaHei', 'PingFang SC', sans-serif"
PALETTES = {   # the .viz colour tokens of assets/css/site.css, light and dark
    'light': dict(ink='#1a1f26', ink2='#444d59', muted='#5e6773', faint='#8a919c', accent='#2d5a96', on='#ffffff',
                  s1='#3b73b9', s2='#c9741a', s3='#a7adb6', bg='#ffffff', bg_soft='#f5f7fa', line='#e3e7ec',
                  accent_soft='#eef3fa', grid='#eaedf1', axis='#c5cad2', wash1=('#3b73b9', '0.12'), wash2=('#c9741a', '0.12'),
                  s4='#8a63b5', s5='#4e9338', sred='#c8524a',
                  tones={'blue': ('#e4edf8', '#8caedc', '#2c5c99'), 'orange': ('#fbebd8', '#dfa864', '#9a5a12'),
                         'purple': ('#efe8f6', '#b39bd3', '#6e4a96'), 'green': ('#e3f0dd', '#93c27e', '#3d7529'),
                         'red': ('#fbe3e1', '#de9a94', '#a6413a'), 'yellow': ('#fff4cf', '#ddbf5e', '#856a0e'),
                         'gray': ('#f3f4f6', '#c3c8cf', '#5f6873')}),
    'dark': dict(ink='#e8eaed', ink2='#bcc2cb', muted='#8f97a2', faint='#727a85', accent='#8db1e6', on='#111317',
                 s1='#5b8fd6', s2='#c98026', s3='#6a717c', bg='#111317', bg_soft='#181b20', line='#2a2f37',
                 accent_soft='#19222f', grid='#23272e', axis='#3b424c', wash1=('#5b8fd6', '0.18'), wash2=('#c98026', '0.18'),
                 s4='#9a7bcb', s5='#5e9e48', sred='#d9736b',
                 tones={'blue': ('#1b2738', '#3f6496', '#a9c6f0'), 'orange': ('#33261a', '#8f6125', '#f0c27e'),
                        'purple': ('#2a2334', '#6f5994', '#cdb8ea'), 'green': ('#1e2b1c', '#4c7a3c', '#a9d898'),
                        'red': ('#36201f', '#9a5550', '#f0a7a0'), 'yellow': ('#352e17', '#8f7a2c', '#ead487'),
                        'gray': ('#1e2227', '#444b55', '#aeb5bf')}),
}


def style_for(theme):
    """CSS class -> presentation attributes, mirroring the .viz rules in assets/css/site.css."""
    p = PALETTES[theme]
    return {
        't-muted': {'fill': p['muted']}, 't-faint': {'fill': p['faint']},
        't-strong': {'fill': p['ink'], 'font-weight': '600'}, 't-accent': {'fill': p['accent'], 'font-weight': '600'},
        't-on': {'fill': p['on'], 'font-weight': '600'},
        'grid': {'stroke': p['grid'], 'stroke-width': '1'}, 'axis': {'stroke': p['axis'], 'stroke-width': '1'},
        'line': {'fill': 'none', 'stroke-width': '2', 'stroke-linejoin': 'round', 'stroke-linecap': 'round'},
        'thin': {'stroke-width': '1.5'},
        's1': {'fill': p['s1']}, 's2': {'fill': p['s2']}, 's3': {'fill': p['s3']},
        'l1': {'stroke': p['s1']}, 'l2': {'stroke': p['s2']}, 'l3': {'stroke': p['s3']},
        'dot': {'stroke': p['bg'], 'stroke-width': '2'},
        'wash1': {'fill': p['wash1'][0], 'fill-opacity': p['wash1'][1]}, 'wash': {'fill': p['wash1'][0], 'fill-opacity': p['wash1'][1]},
        'wash2': {'fill': p['wash2'][0], 'fill-opacity': p['wash2'][1]},
        'band': {'fill': p['bg_soft']},
        'box': {'fill': p['bg'], 'stroke': p['line'], 'stroke-width': '1.2'},
        'box-soft': {'fill': p['bg_soft'], 'stroke': p['line'], 'stroke-width': '1'},
        'box-key': {'fill': p['accent_soft'], 'stroke': p['accent'], 'stroke-width': '1.4'},
        'box-fill': {'fill': p['accent']},
        'arrow': {'stroke': p['faint'], 'stroke-width': '1.4', 'fill': 'none'}, 'arrow-head': {'fill': p['faint']},
        'leader': {'stroke': p['faint'], 'stroke-width': '1', 'fill': 'none'},
        'tok-s': {'fill': p['s3']}, 'tok-t': {'fill': p['s1']},
        'ring': {'fill': 'none', 'stroke': p['accent'], 'stroke-width': '1.4'},
        's4': {'fill': p['s4']}, 's5': {'fill': p['s5']}, 's-red': {'fill': p['sred']},
        'l4': {'stroke': p['s4']}, 'l5': {'stroke': p['s5']}, 'l-red': {'stroke': p['sred']},
        'dash': {'stroke-dasharray': '5 4'}, 'ink': {'fill': p['ink']}, 'ink-line': {'stroke': p['ink2'], 'fill': 'none'},
        'math': {'font-family': "'Times New Roman', 'Noto Serif', serif", 'font-style': 'italic'},
        **{f'pn-{k}': {'fill': a, 'stroke': b, 'stroke-width': '1.2'} for k, (a, b, c) in p['tones'].items()},
        **{f'fl-{k}': {'fill': a} for k, (a, b, c) in p['tones'].items()},
        **{f'ln-{k}': {'stroke': b, 'fill': 'none'} for k, (a, b, c) in p['tones'].items()},
        **{f'tx-{k}': {'fill': c} for k, (a, b, c) in p['tones'].items()},
    }


SVG_NS = 'http://www.w3.org/2000/svg'


def font_faces():
    """@font-face rules with the site's sans subsets inlined, so the file renders the same anywhere (e.g. as an <img>)."""
    import base64
    rules = []
    for family, weight, name in [('YZ Sans', 400, 'YZSans-Regular.woff2'), ('YZ Sans', 600, 'YZSans-Semibold.woff2'),
                                 ('YZ Hand', 400, 'ComicNeue-Regular.woff2'), ('YZ Hand', 700, 'ComicNeue-Bold.woff2')]:
        data = base64.b64encode((ROOT / 'assets' / 'fonts' / name).read_bytes()).decode()
        rules.append(f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2')}}")
    return ''.join(rules)


def standalone(svg_text, lang, theme='light', embed_fonts=False):
    """One language and theme, presentation attributes instead of classes; hover targets removed."""
    ET.register_namespace('', SVG_NS)
    root = ET.fromstring(svg_text)   # our own markup from figures.py, never outside input
    keep = 'en' if lang == 'en' else 'zh-CN'
    style = style_for(theme)
    hand_root = 'hand' in root.get('class', '').split()

    def prune(el):
        for child in list(el):
            cls = child.get('class', '').split()
            if (child.get('lang') and child.get('lang') != keep) or 'hit' in cls:
                el.remove(child)
            else:
                prune(child)
    prune(root)
    for el in root.iter():
        tag = el.tag.split('}')[-1]
        attrs = {'fill': PALETTES[theme]['ink2']} if tag == 'text' else {}
        for c in el.get('class', '').split():
            attrs.update(style.get(c, {}))
        for k, v in attrs.items():
            if el.get(k) is None:
                el.set(k, v)
        el.attrib.pop('class', None)
        el.attrib.pop('lang', None)
    for g in list(root.iter(f'{{{SVG_NS}}}g')):      # drop groups emptied by the pruning
        for child in list(g):
            if child.tag.endswith('g') and len(child) == 0:
                g.remove(child)
    face = ("'YZ Hand', 'Comic Neue', 'Comic Sans MS', " if hand_root else '') + ("'YZ Sans', " if embed_fonts else '') + FONT
    root.set('font-family', face)
    root.attrib.pop('role', None)
    if embed_fonts:
        st = ET.Element(f'{{{SVG_NS}}}style')
        st.text = font_faces()
        root.insert(0, st)
    return ET.tostring(root, encoding='unicode')


def export(out, theme='light', embed_fonts=False, names=None):
    out = pathlib.Path(out)
    names = names or list(figures.FIGS)
    suffix = '' if theme == 'light' else f'-{theme}'
    for lang in ('en', 'zh'):
        (out / lang).mkdir(parents=True, exist_ok=True)
        for name in names:
            fn = figures.FIGS[name][0]
            svg = fn() if name in figures.CARDS else fn(figures.WIDE.get(name, LG))
            (out / lang / f'{name}{suffix}.svg').write_text(standalone(svg.render(), lang, theme, embed_fonts) + '\n', encoding='utf-8')
    print(f'exported {len(names)} figures × 2 languages ({theme} theme) to {out}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--export', metavar='DIR', help='also write standalone SVG files to DIR/en and DIR/zh')
    ap.add_argument('--theme', choices=['light', 'dark'], default='light', help='colours of the exported files (dark adds a -dark suffix)')
    ap.add_argument('--embed-fonts', action='store_true', help='inline the site font in exported files (for use as <img>)')
    ap.add_argument('--only', nargs='+', metavar='NAME', help='export only these figures')
    args = ap.parse_args()
    inject()
    if args.export:
        export(args.export, args.theme, args.embed_fonts, args.only)


if __name__ == '__main__':
    main()
