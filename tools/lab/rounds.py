#!/usr/bin/env python3
"""Build tools/lab/rounds.html: every figure's iterations side by side.

For each figure: v2 (the starting point), then for each round its aesthetic and innovative versions and which one
was kept. Rounds are modules r1_*.py, r2_*.py, r3_*.py exporting AES and INNO dicts; PICKS records the choice.

    python3 tools/lab/rounds.py [NAME ...]     # then serve the repository root and open /tools/lab/rounds.html
"""
import importlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'v2'))

import figures_v2 as V2  # noqa: E402
from figlib import LG, SM  # noqa: E402

ORDER = ['card-opd', 'card-scr', 'opd-takeover', 'opd-pipeline', 'opd-methods', 'opd-budget', 'opd-training', 'opd-compute',
         'scr-steplevel', 'scr-pipeline', 'scr-sft-rl', 'scr-vs-grpo', 'scr-updates', 'scr-hotpotqa']
WIDE = {'opd-takeover': 880, 'scr-steplevel': 880}   # framework figures are drawn wider
PICKS = {   # round -> {figure: 'aes' | 'inno'}; the next round starts from the version kept here
    1: {'card-opd': 'inno', 'card-scr': 'inno', 'opd-takeover': 'inno', 'scr-steplevel': 'inno',
        'opd-pipeline': 'aes', 'scr-pipeline': 'aes', 'opd-methods': 'aes', 'opd-budget': 'inno', 'opd-training': 'aes',
        'opd-compute': 'inno', 'scr-sft-rl': 'aes', 'scr-vs-grpo': 'inno', 'scr-updates': 'inno', 'scr-hotpotqa': 'inno'},
    2: {'card-opd': 'aes', 'card-scr': 'inno', 'opd-takeover': 'aes', 'scr-steplevel': 'inno',
        'opd-pipeline': 'aes', 'scr-pipeline': 'aes', 'opd-methods': 'aes', 'opd-budget': 'inno', 'opd-training': 'inno',
        'opd-compute': 'inno', 'scr-sft-rl': 'inno', 'scr-vs-grpo': 'aes', 'scr-updates': 'aes', 'scr-hotpotqa': 'aes'},
    3: {'card-opd': 'aes', 'card-scr': 'aes', 'opd-takeover': 'aes', 'scr-steplevel': 'inno',
        'opd-pipeline': 'aes', 'scr-pipeline': 'aes', 'opd-methods': 'aes', 'opd-budget': 'aes', 'opd-training': 'inno',
        'opd-compute': 'aes', 'scr-sft-rl': 'aes', 'scr-vs-grpo': 'aes', 'scr-updates': 'inno', 'scr-hotpotqa': 'aes'},
}


def load_rounds():
    rounds = []
    for r in (1, 2, 3):
        aes, inno = {}, {}
        for part in ('_diagrams', '_charts', ''):
            try:
                mod = importlib.import_module(f'r{r}{part}')
            except ModuleNotFoundError:
                continue
            aes.update(getattr(mod, 'AES', {}))
            inno.update(getattr(mod, 'INNO', {}))
        if aes or inno:
            rounds.append((r, aes, inno))
    return rounds


def draw(fn, name, phone=False):
    if name.startswith('card-'):
        return fn().render() if not phone else ''
    w = SM if phone else WIDE.get(name, LG)
    try:
        return fn(w).render()
    except TypeError:
        return fn(w).render()


def main():
    only = set(sys.argv[1:])
    rounds = load_rounds()
    parts = []
    for name in ORDER:
        if only and name not in only:
            continue
        base = V2.FIGS[name][0]
        show = os.environ.get('ROUNDS')
        cols = [] if show else [('v2', base)]
        for r, aes, inno in rounds:
            if show and str(r) not in show.split(','):
                continue
            if name in aes:
                cols.append((f'R{r} aesthetic' + (' ✓' if PICKS.get(r, {}).get(name) == 'aes' else ''), aes[name]))
            if name in inno:
                cols.append((f'R{r} innovative' + (' ✓' if PICKS.get(r, {}).get(name) == 'inno' else ''), inno[name]))
        lg = ''.join(f'<div class="v"><div class="tag">{lab}</div><div class="frame lg">{draw(fn, name)}</div></div>' for lab, fn in cols)
        sm = '' if name.startswith('card-') else ''.join(
            f'<div class="v"><div class="tag">{lab} · phone</div><div class="frame sm">{draw(fn, name, True)}</div></div>' for lab, fn in cols)
        parts.append(f'<section class="chart" id="{name}"><h2>{name}</h2><div class="grid">{lg}</div><div class="row">{sm}</div></section>')
    html = f'''<!doctype html><html lang="en" data-lang="en"><head><meta charset="utf-8">
<script>(function(){{var l;try{{l=localStorage.getItem('lang')}}catch(e){{}}if(l!=='zh')l='en';var r=document.documentElement;r.setAttribute('data-lang',l);r.setAttribute('lang',l==='zh'?'zh-CN':'en')}})();</script>
<link rel="stylesheet" href="../../assets/css/site.css">
<style>
body {{ padding: 20px; }}
.chart {{ margin: 0 0 40px; padding: 0 0 20px; border-bottom: 1px solid var(--line); width: 1900px; }}
.chart h2 {{ font: 600 18px/1.2 var(--mono); margin: 0 0 10px; }}
.grid {{ display: grid; grid-template-columns: repeat(2, 930px); gap: 14px; align-items: start; }}
.row {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 12px; align-items: flex-start; }}
.v .tag {{ font: 600 12px/1 var(--mono); color: var(--muted); margin: 0 0 6px; }}
.frame {{ border: 1px solid var(--line); border-radius: 12px; padding: 12px; background: var(--bg); }}
.frame svg {{ display: block; width: 100%; height: auto; }}
.frame.lg {{ width: 900px; }} .frame.sm {{ width: 360px; }}
</style></head><body>{''.join(parts)}</body></html>'''
    (HERE / 'rounds.html').write_text(html, encoding='utf-8')
    print('wrote', HERE / 'rounds.html', len(parts), 'figures')


if __name__ == '__main__':
    main()
