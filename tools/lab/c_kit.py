"""Shared drawing helpers for the 11-17 chart rounds (c1.py, c2.py, c3.py).

One small type scale (11 / 12 / 13 px), ink-coloured text, colour only on the marks, thin axes. Everything is drawn
with figlib's Svg so the charts stay bilingual (T(en, zh)) and follow the page theme through the site's CSS classes.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
for p in (str(HERE.parent), str(HERE), str(HERE / 'v2')):
    if p not in sys.path:
        sys.path.insert(0, p)

from figlib import ALF, FAMILY, HPQ, OPD, PAIRED, Svg, T, hbar, hit_points, moving_avg, polyline, run, scale, text_w, vbar, width_of  # noqa: E402,F401
import figures_v2 as V2  # noqa: E402

LANGS = ('en', 'zh-CN')
FS_TICK, FS_LABEL, FS_TITLE = 11, 12, 13
CHARTS = ['opd-methods', 'opd-budget', 'opd-training', 'opd-compute', 'scr-sft-rl', 'scr-vs-grpo', 'scr-updates', 'scr-hotpotqa']


def pick(t, i):
    return t[i] if isinstance(t, tuple) else t


def per_lang(svg, draw):
    for i, lang in enumerate(LANGS):
        svg.add(f'<g lang="{lang}">')
        draw(i)
        svg.add('</g>')


def signed(v, nd=1):
    return f'{v:+.{nd}f}'.replace('-', '−')


def pct(v, nd=1):
    return f'{v:.{nd}f}%'


# ----------------------------------------------------------------------------- frames
def frame(svg, box, sx, sy, xticks, yticks, xfmt=str, yfmt=str, xtitle=None, ytitle=None, grid='y', ticks_out=True):
    """Plot frame: horizontal grid at y ticks, a baseline axis, tick labels outside. `grid` is 'y', 'x', 'xy' or ''."""
    x0, y0, x1, y1 = box
    if 'y' in grid:
        for v in yticks:
            if abs(sy(v) - y1) > 0.5:
                svg.line(x0, sy(v), x1, sy(v), 'grid')
    if 'x' in grid:
        for v in xticks:
            if abs(sx(v) - x0) > 0.5:
                svg.line(sx(v), y0, sx(v), y1, 'grid')
    svg.line(x0, y1, x1, y1, 'axis')
    for v in xticks:
        if ticks_out:
            svg.line(sx(v), y1, sx(v), y1 + 4, 'axis')
        svg.text(sx(v), y1 + 16, xfmt(v), cls='t-faint', anchor='middle', size=FS_TICK)
    for v in yticks:
        svg.text(x0 - 7, sy(v) + 3.8, yfmt(v), cls='t-faint', anchor='end', size=FS_TICK)
    if xtitle:
        svg.text((x0 + x1) / 2, y1 + 32, xtitle, cls='t-muted', anchor='middle', size=FS_TICK)
    if ytitle:
        svg.text(x0, y0 - 10, ytitle, cls='t-muted', size=FS_TICK)


def panel_title(svg, x, y, letter, title, sub=None):
    """'(a) Title  sub' — title in ink 13 px semibold, sub in faint 11 px."""
    def draw(i):
        t = (f'({letter}) ' if letter else '') + pick(title, i)
        svg.text(x, y, t, cls='t-strong', size=FS_TITLE)
        if sub:
            svg.text(x + svg.tw(t, FS_TITLE, 600) + 8, y, pick(sub, i), cls='t-faint', size=FS_TICK)
    per_lang(svg, draw)


def key_lines(svg, x, y, items, gap=18):
    """Legend of line keys: items = [(series index, label, dashed?)]."""
    def draw(i):
        xx = x
        for it in items:
            idx, label = it[0], pick(it[1], i)
            dashed = len(it) > 2 and it[2]
            svg.line(xx, y - 4, xx + 18, y - 4, f'line l{idx}', 'stroke-dasharray="4 3"' if dashed else '')
            svg.text(xx + 24, y, label, size=FS_LABEL)
            xx += 24 + text_w(label, FS_LABEL) + gap
    per_lang(svg, draw)


def key_chips(svg, x, y, items, gap=18):
    """Legend of square keys: items = [(css class, label)]."""
    def draw(i):
        xx = x
        for cls, label in items:
            s = pick(label, i)
            svg.rect(xx, y - 9, 10, 10, cls, rx=2)
            svg.text(xx + 15, y, s, size=FS_LABEL)
            xx += 15 + text_w(s, FS_LABEL) + gap
    per_lang(svg, draw)


def path_line(svg, pts, sx, sy, idx, dashed=False, width=None, extra=''):
    ex = ('stroke-dasharray="5 4" ' if dashed else '') + (f'stroke-width="{width}" ' if width else '') + extra
    svg.path(polyline(pts, sx, sy), f'line l{idx}', ex.strip())


def dots(svg, pts, sx, sy, idx, r=3.2, every=None, hollow=False, ring=True):
    """Markers on a line. ring=False draws plain filled dots (no background ring), for dense markers that would
    otherwise make the line look dashed."""
    for k, (x, y) in enumerate(pts):
        if every is None or x in every:
            if hollow:
                svg.add(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="{r}" class="l{idx}" fill="var(--bg)" stroke-width="1.8"/>')
            elif ring:
                svg.circle(sx(x), sy(y), r, f'dot s{idx}', 'stroke-width="1.5"')
            else:
                svg.circle(sx(x), sy(y), r, f's{idx}')


def hits(svg, pts, sx, sy, fn, r=6):
    hit_points(svg, pts, sx, sy, fn, r=r)


def label_stack(svg, x, items, min_gap=14, size=FS_LABEL):
    """Right-of-line labels without overlap: items = [(y, text, cls)] (y is the data y in px)."""
    items = sorted(items, key=lambda it: it[0])
    placed = []
    for y, t, cls in items:
        ty = y + 4
        if placed and ty - placed[-1] < min_gap:
            ty = placed[-1] + min_gap
        placed.append(ty)
        svg.text(x, ty, t, cls=cls, size=size)
    return placed


def bracket_v(svg, x, ya, yb, tick=5, side='right'):
    d = tick if side == 'right' else -tick
    svg.path(f'M{x - d:.1f},{ya:.1f} H{x:.1f} V{yb:.1f} H{x - d:.1f}', 'leader')


def wash_between(svg, xs, a, b, sx, sy, pos='wash1', neg='wash2'):
    V2.gap_wash(svg, xs, a, b, sx, sy, pos, neg)


def family_counts(run_name, split):
    return V2.family_counts(run_name, split)


FAM_NAMES, FAM_ORDER = V2.FAM_NAMES, V2.FAM_ORDER
