#!/usr/bin/env python3
"""Build tools/lab/c_rounds.html: the 11-17 chart rounds side by side.

For each data chart and each round (c1.py, c2.py, c3.py): the round's base, its aesthetic and innovative versions, and
the merge that becomes the next round's base, at desktop width, with the phone versions underneath.

    python3 tools/lab/c_rounds.py [NAME ...]      # ROUNDS=2 shows one round only; FINAL_ONLY=1 shows the finals only
"""
import importlib
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from figlib import LG, SM  # noqa: E402
from c_kit import CHARTS  # noqa: E402

KINDS = [('BASE', 'base'), ('AES', 'aesthetic'), ('INNO', 'innovative'), ('MERGED', 'merged')]


def load():
    if os.environ.get('FINAL_ONLY'):
        import c_final

        class Final:
            MERGED = c_final.FINAL
        return [(9, Final)]
    out = []
    for r in (1, 2, 3):
        try:
            mod = importlib.import_module(f'c{r}')
        except ModuleNotFoundError:
            continue
        out.append((r, mod))
    return out


def main():
    only = set(sys.argv[1:])
    show = os.environ.get('ROUNDS')
    rounds = load()
    parts = []
    for name in CHARTS:
        if only and name not in only:
            continue
        blocks = []
        for r, mod in rounds:
            if show and str(r) not in show.split(','):
                continue
            cols = []
            for attr, label in KINDS:
                d = getattr(mod, attr, {})
                if name in d:
                    cols.append((f'C{r} {label}', d[name]))
            if not cols:
                continue
            note = getattr(mod, 'NOTES', {}).get(name, '')
            lg = ''.join(f'<div class="v"><div class="tag">{lab}</div><div class="frame lg">{fn(LG).render()}</div></div>' for lab, fn in cols)
            sm = ''.join(f'<div class="v"><div class="tag">{lab} · phone</div><div class="frame sm">{fn(SM).render()}</div></div>' for lab, fn in cols)
            blocks.append(f'<div class="round" id="{name}-c{r}"><h3>Round {r}</h3>'
                          + (f'<p class="note">{note}</p>' if note else '')
                          + f'<div class="grid">{lg}</div><div class="row">{sm}</div></div>')
        parts.append(f'<section class="chart" id="{name}"><h2>{name}</h2>{"".join(blocks)}</section>')
    html = f'''<!doctype html><html lang="en" data-lang="en"><head><meta charset="utf-8">
<script>(function(){{var l;try{{l=localStorage.getItem('lang')}}catch(e){{}}if(l!=='zh')l='en';var r=document.documentElement;r.setAttribute('data-lang',l);r.setAttribute('lang',l==='zh'?'zh-CN':'en')}})();</script>
<link rel="stylesheet" href="../../assets/css/site.css">
<style>
body {{ padding: 20px; }}
.chart {{ margin: 0 0 40px; padding: 0 0 20px; border-bottom: 1px solid var(--line); width: 1900px; }}
.chart h2 {{ font: 600 18px/1.2 var(--mono); margin: 0 0 10px; }}
.round h3 {{ font: 600 14px/1.2 var(--mono); margin: 18px 0 6px; color: var(--muted); }}
.round .note {{ font-size: 13px; color: var(--muted); margin: 0 0 8px; max-width: 1860px; }}
.grid {{ display: grid; grid-template-columns: repeat(2, 930px); gap: 14px; align-items: start; }}
.row {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 12px; align-items: flex-start; }}
.v .tag {{ font: 600 12px/1 var(--mono); color: var(--muted); margin: 0 0 6px; }}
.frame {{ border: 1px solid var(--line); border-radius: 12px; padding: 12px; background: var(--bg); }}
.frame svg {{ display: block; width: 100%; height: auto; }}
.frame.lg {{ width: 900px; }} .frame.sm {{ width: 360px; }}
</style></head><body>{''.join(parts)}</body></html>'''
    (HERE / 'c_rounds.html').write_text(html, encoding='utf-8')
    print('wrote', HERE / 'c_rounds.html', len(parts), 'charts')


if __name__ == '__main__':
    main()
