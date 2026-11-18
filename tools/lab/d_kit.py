"""Shared helpers for the second 11-17 chart cycle (d1.py, d2.py, d3.py).

The pages now show every figure in English only (make_figures.english_only), so the rounds judge the English
rendering; the T(en, zh) calls stay so the Chinese export keeps working. Three type sizes only (11 / 12 / 13 px), text
in ink tones, colour on the marks.
"""
from c_kit import (ALF, CHARTS, FAM_NAMES, FAM_ORDER, FAMILY, HPQ, OPD, PAIRED, Svg, T, dots, family_counts, frame, hbar,  # noqa: F401
                   hits, key_chips, key_lines, label_stack, moving_avg, panel_title, path_line, per_lang, pick, polyline, run,
                   scale, signed, text_w, vbar, wash_between)

FS_TICK, FS_LABEL, FS_TITLE = 11, 12, 13


def span(svg, xa, xb, y, label, drops=(), cls='t-strong', size=FS_LABEL, gap=7):
    """Horizontal span with an arrowhead at each end and its label centred above. drops = [(x, y_to)]: dotted guides
    from the span down to the points it compares. The same mark is used wherever a chart compares two times."""
    for x, yt in drops:
        svg.line(x, y + 5, x, yt, 'leader', 'stroke-dasharray="2 3"')
    svg.line(xa + 2, y, xb - 2, y, 'leader')
    svg.path(f'M{xa:.1f},{y:.1f} l5.5,-3.5 v7 Z', 'arrow-head')
    svg.path(f'M{xb:.1f},{y:.1f} l-5.5,-3.5 v7 Z', 'arrow-head')
    if label:
        svg.text((xa + xb) / 2, y - gap, label, cls=cls, anchor='middle', size=size)


def bracket(svg, x, ya, yb, label=None, tick=5, cls='t-strong', size=FS_LABEL):
    """Vertical bracket on the right of two marks, with its label to the right."""
    svg.path(f'M{x - tick:.1f},{ya:.1f} H{x:.1f} V{yb:.1f} H{x - tick:.1f}', 'leader')
    if label:
        svg.text(x + 6, (ya + yb) / 2 + 4.2, label, cls=cls, size=size)


def seg_sign(xs, ys):
    """Split a polyline at its zero crossings: [(sign, [(x, y), ...])], each run including the crossing points."""
    out = []
    cur, sg = [(xs[0], ys[0])], ys[0] >= 0
    for (xa, ya), (xb, yb) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if (ya >= 0) != (yb >= 0):
            xc = xa + (xb - xa) * (0 - ya) / (yb - ya)
            cur.append((xc, 0.0))
            out.append((sg, cur))
            cur, sg = [(xc, 0.0)], yb >= 0
        cur.append((xb, yb))
    out.append((sg, cur))
    return out


# Background-coloured shapes use the class 'box' (fill: the page background) with an inline style that removes its
# stroke, never fill="var(--bg)": make_figures.standalone() maps classes to colours for the exported SVG / PNG files,
# while a var() left in an attribute has no value there and paints black.
BG = 'class="box" style="stroke:none"'


def soft_box(svg, x, y, w, h, rx=6):
    """A background-coloured box (no stroke) that hides the grid behind an inset."""
    svg.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" {BG}/>')


def ring(cx, cy, r, width, series):
    """A hollow marker: a series-coloured disc with a background disc on top, so the ring is `width` thick around
    radius r (the look of stroke-width `width` on a bg-filled circle, but exportable). Returns the markup."""
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r + width / 2:.2f}" class="{series}"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r - width / 2:.2f}" {BG}/>')
