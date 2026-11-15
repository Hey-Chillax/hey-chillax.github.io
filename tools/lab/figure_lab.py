#!/usr/bin/env python3
"""Build tools/lab/gallery.html: every figure in its versions (1 base, 2 aesthetic, 3 innovative, 4 final), side by side.

    python3 tools/lab/figure_lab.py        # then serve the repository root and open /tools/lab/gallery.html
"""
import importlib.util
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import figs_aes  # noqa: E402
import figs_inno  # noqa: E402
import figures  # noqa: E402
from figlib import LG, SM  # noqa: E402

spec = importlib.util.spec_from_file_location('figs_base', HERE / 'figs_base.py')
figs_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(figs_base)

BASE = {
    'card-opd': figs_base.fig_card_opd, 'card-scr': figs_base.fig_card_scr,
    'opd-pipeline': figs_base.fig_opd_pipeline, 'opd-takeover': figs_base.fig_opd_takeover, 'opd-methods': figs_base.fig_opd_methods,
    'opd-budget': figs_base.fig_opd_budget, 'opd-training': figs_base.fig_opd_training,
    'scr-pipeline': figs_base.fig_scr_pipeline, 'scr-steplevel': figs_base.fig_scr_steplevel, 'scr-sft-rl': figs_base.fig_scr_sft_rl,
    'scr-vs-grpo': figs_base.fig_scr_vs_grpo, 'scr-updates': figs_base.fig_scr_updates, 'scr-hotpotqa': figs_base.fig_scr_hotpotqa,
}
FINAL = {name: fn for name, (fn, _) in figures.FIGS.items()}
INNO = dict(figs_inno.FIGS, **{'opd-compute': figs_inno.opd_pipeline})
VERSIONS = [('1 · base', BASE), ('2 · aesthetic', figs_aes.FIGS), ('3 · innovative', INNO), ('4 · final', FINAL)]


def render(fn, name, width):
    if name.startswith('card-'):
        return fn(380).render()
    return fn(width).render()


def main():
    out = HERE / 'gallery.html'
    parts = []
    only = set(sys.argv[1:])
    for name in FINAL:
        if only and name not in only:
            continue
        have = [(label, funcs) for label, funcs in VERSIONS if name in funcs]
        lg = ''.join(f'<div class="v"><div class="tag">{label}</div><div class="frame lg">{render(funcs[name], name, LG)}</div></div>'
                     for label, funcs in have)
        sm = '' if name.startswith('card-') else ''.join(
            f'<div class="v"><div class="tag">{label} · phone</div><div class="frame sm">{render(funcs[name], name, SM)}</div></div>' for label, funcs in have)
        parts.append(f'<section class="chart" id="{name}"><h2>{name}</h2><div class="col">{lg}</div><div class="row">{sm}</div></section>')
    html = f'''<!doctype html><html lang="en" data-lang="en"><head><meta charset="utf-8">
<script>(function(){{var l;try{{l=localStorage.getItem('lang')}}catch(e){{}}if(l!=='zh')l='en';var r=document.documentElement;r.setAttribute('data-lang',l);r.setAttribute('lang',l==='zh'?'zh-CN':'en')}})();</script>
<link rel="stylesheet" href="../../assets/css/site.css">
<style>
body {{ padding: 24px; }}
.chart {{ margin: 0 0 48px; padding: 0 0 24px; border-bottom: 1px solid var(--line); width: 1560px; }}
.chart h2 {{ font: 600 20px/1.2 var(--mono); margin: 0 0 14px; }}
.col {{ display: grid; gap: 14px; }}
.row {{ display: flex; gap: 14px; margin-top: 14px; align-items: flex-start; }}
.v .tag {{ font: 600 12px/1 var(--mono); color: var(--muted); margin: 0 0 6px; }}
.frame {{ border: 1px solid var(--line); border-radius: 12px; padding: 14px 12px 8px; background: var(--bg); }}
.frame.lg {{ width: 760px; }}
.frame.sm {{ width: 372px; }}
.frame svg {{ display: block; width: 100%; height: auto; }}
.col .v {{ display: grid; grid-template-columns: 110px 760px; gap: 10px; align-items: start; }}
</style></head><body>{''.join(parts)}</body></html>'''
    out.write_text(html, encoding='utf-8')
    print('wrote', out)


if __name__ == '__main__':
    main()
