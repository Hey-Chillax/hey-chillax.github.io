"""Generate, export, webify and preview the homepage's draw.io diagrams.

    python3 tools/drawio/build.py FIGURE VARIANT [VARIANT ...] [--lang en,zh] [--final VARIANT] [--dark]

* FIGURE is a module fig_<name>.py next to this file (opd_takeover, scr_steplevel, opd_pipeline, scr_pipeline,
  card_opd, card_scr); it exposes WIDTH (display width in px), LABEL and LABEL_ZH (aria-labels) and build(variant, lang) -> Fig.
  Previews are rendered at each variant's own width (Fig.w): the frameworks moved from 880 to 720 px in round 4.
* Sources go to tools/drawio/src/FIGURE/VARIANT.LANG.drawio (kept: they open in draw.io for editing).
* The SVG export (draw.io Desktop command line), the webified SVGs and the PNG previews go to the scratch folder.
* --final VARIANT copies that variant's webified SVGs to tools/drawio/out/FIGURE.LANG.svg.
Needs draw.io Desktop (WSL: /mnt/c/Program Files/draw.io/draw.io.exe), Pillow, and node + playwright for previews
(DRAWIO_NODE_PATH = the node_modules folder that holds playwright). DRAWIO_SCRATCH sets the build folder.
"""
import argparse
import importlib
import json
import os
import re
import pathlib
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import webify  # noqa: E402

DRAWIO = '/mnt/c/Program Files/draw.io/draw.io.exe'
# Exports, webified copies and previews are build products: they go to a scratch folder outside the repository.
SCRATCH = pathlib.Path(os.environ.get('DRAWIO_SCRATCH') or pathlib.Path(tempfile.gettempdir()) / 'drawio-build')
NODE_RENDER = HERE / 'render.js'
NAMES = {'opd_takeover': 'opd-takeover', 'scr_steplevel': 'scr-steplevel', 'opd_pipeline': 'opd-pipeline',
         'scr_pipeline': 'scr-pipeline', 'card_opd': 'card-opd', 'card_scr': 'card-scr'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('figure')
    ap.add_argument('variants', nargs='+')
    ap.add_argument('--lang', default='en')
    ap.add_argument('--final')
    ap.add_argument('--dark', action='store_true', help='also render dark-theme previews')
    a = ap.parse_args()
    mod = importlib.import_module(f'fig_{a.figure}')
    name = NAMES[a.figure]
    langs = a.lang.split(',')
    src = HERE / 'src' / name
    batch, exp, web, prev = (SCRATCH / d / name for d in ('batch', 'export', 'web', 'previews'))
    for d in (src, batch, exp, web, prev):
        d.mkdir(parents=True, exist_ok=True)
    for old in batch.glob('*.drawio'):
        old.unlink()
    jobs = []
    for v in a.variants:
        for lang in langs:
            fig = mod.build(v, lang)
            xml = fig.to_xml()
            for cell in fig.cells:
                g = re.search(r'x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" height="([\d.]+)"', cell)
                if g:
                    x, y, w, h = (float(q) for q in g.groups())
                    if x < -0.5 or y < -0.5 or x + w > fig.w + 0.5 or y + h > fig.h + 0.5:
                        val = re.search(r'value="([^"]*)"', cell)
                        print(f'OUTSIDE {name} {v}.{lang}: x={x:.0f}..{x + w:.0f} y={y:.0f}..{y + h:.0f} {val.group(1)[:60] if val else ""}')
            (src / f'{v}.{lang}.drawio').write_text(xml, encoding='utf-8')
            (batch / f'{v}.{lang}.drawio').write_text(xml, encoding='utf-8')
            jobs.append((v, lang, fig))
    r = subprocess.run([DRAWIO, '-x', '-f', 'svg', '--crop', '-b', '0', '-o', str(exp) + '/', str(batch) + '/'],
                       capture_output=True, text=True, timeout=600)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit('draw.io export failed')
    items = []
    for v, lang, fig in jobs:
        raw = (exp / f'{v}.{lang}.svg').read_text(encoding='utf-8')
        vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', raw).group(1).split()]
        if abs(vb[2] - fig.w) > 1.5 or abs(vb[3] - fig.h) > 1.5:
            print(f'WARNING {name} {v}.{lang}: exported size {vb[2]:.0f} x {vb[3]:.0f}, expected {fig.w} x {fig.h} (something overflows)')
        out = webify.webify(raw, getattr(mod, 'LABEL_ZH', fig.label) if lang == 'zh' else fig.label)
        (web / f'{v}.{lang}.svg').write_text(out, encoding='utf-8')
        for theme in (['light', 'dark'] if a.dark else ['light']):
            suffix = '' if theme == 'light' else '.dark'
            items.append(dict(svg=str(web / f'{v}.{lang}.svg'), png=str(prev / f'{v}.{lang}{suffix}.png'),
                              width=fig.w, theme=theme))
    if webify.unknown:
        print('colours not in the palette:', ', '.join(sorted(webify.unknown)))
    css = webify.write_css(SCRATCH / 'diagram-colors.css')
    job = SCRATCH / 'render_job.json'
    job.write_text(json.dumps(dict(css=str(css), items=items)))
    env = dict(os.environ, NODE_PATH=os.environ.get('DRAWIO_NODE_PATH', os.environ.get('NODE_PATH', '')))
    r = subprocess.run(['node', str(NODE_RENDER), str(job)], capture_output=True, text=True, timeout=600, env=env)
    print(r.stdout.strip()[-1500:])
    if r.returncode:
        print(r.stderr[-1500:])
    if a.final:
        for lang in langs:
            shutil.copy(web / f'{a.final}.{lang}.svg', HERE / 'out' / f'{name}.{lang}.svg')
            print('final ->', HERE / 'out' / f'{name}.{lang}.svg')


if __name__ == '__main__':
    main()
