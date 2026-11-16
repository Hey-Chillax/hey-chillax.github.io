"""Diagram building blocks, after the owner's paper figures: tinted panels with a coloured border and a titled,
numbered heading; token squares; chips; small line icons; math set in an italic serif.

Tones are CSS classes defined in assets/css/site.css (light and dark): pn-<tone> (tinted fill + border),
fl-<tone> (tint only), ln-<tone> (border colour as a stroke), tx-<tone> (text). The solid mark of a tone is the
matching series class (blue = s1, orange = s2, gray = s3, purple = s4, green = s5, red = s-red).
"""
import math as _m

from figlib import arrow

SOLID = {'blue': 's1', 'orange': 's2', 'gray': 's3', 'purple': 's4', 'green': 's5', 'red': 's-red'}
LINE = {'blue': 'l1', 'orange': 'l2', 'gray': 'l3', 'purple': 'l4', 'green': 'l5', 'red': 'l-red'}


def panel(svg, x, y, w, h, tone='gray', title=None, num=None, dashed=False, rx=12, size=13, sub=None):
    svg.rect(x, y, w, h, f'pn-{tone}' + (' dash' if dashed else ''), rx=rx)
    if title:
        tx = x + 14
        if num is not None:
            badge(svg, tx + 8, y + 19, num, tone if tone in SOLID else 'gray')
            tx += 22
        svg.text(tx, y + 23.5, title, cls=f'tx-{tone}', size=size, weight=700)
        if sub:
            svg.text(tx + svg.tw(title, size, 700) + 8, y + 23.5, sub, cls='t-faint', size=11)


def badge(svg, cx, cy, n, tone='blue', r=8.5):
    svg.circle(cx, cy, r, SOLID[tone])
    svg.text(cx, cy + 3.9, str(n), cls='t-on', anchor='middle', size=11, weight=700)


def chip(svg, x, y, text, tone='gray', solid=False, size=11.5, h=20, pad=7, weight=None, dashed=False):
    """A labelled rounded box; returns the x after it."""
    bold = solid or (weight or 0) >= 600
    w = svg.tw(text, size, 600 if bold else 400) + 2 * pad
    if solid:
        svg.rect(x, y, w, h, SOLID[tone], rx=5)
        svg.text(x + w / 2, y + h / 2 + size * 0.36, text, cls='t-on', anchor='middle', size=size)
    else:
        svg.rect(x, y, w, h, f'pn-{tone}' + (' dash' if dashed else ''), rx=5)
        svg.text(x + w / 2, y + h / 2 + size * 0.36, text, cls=f'tx-{tone}', anchor='middle', size=size, weight=weight)
    return x + w


def chip_w(svg, text, size=11.5, pad=7, bold=False):
    return svg.tw(text, size, 600 if bold else 400) + 2 * pad


def tokens(svg, x, y, n, tone, size=11, gap=3, dashed=False, solid=False):
    """A run of n token squares; returns the x after it."""
    for i in range(n):
        cls = SOLID[tone] if solid else f'pn-{tone}' + (' dash' if dashed else '')
        svg.rect(x + i * (size + gap), y, size, size, cls, rx=2.5)
    return x + n * (size + gap) - gap


def math(svg, x, y, s, size=13, anchor='start', cls='ink'):
    svg.text(x, y, s, cls=f'math {cls}', size=size, anchor=anchor)


def curve(svg, x1, y1, x2, y2, cls, extra='', bend=None):
    """A smooth S-curve from (x1, y1) to (x2, y2)."""
    my = (y1 + y2) / 2 if bend is None else bend
    svg.path(f'M{x1:.1f},{y1:.1f} C{x1 + 10:.1f},{my:.1f} {x2 - 10:.1f},{my:.1f} {x2:.1f},{y2:.1f}', cls,
             'fill="none" stroke-width="1.6"' + (' ' + extra if extra else ''))


def flow_arrow(svg, x1, y1, x2, y2, cls='arrow', head=6.5):
    arrow(svg, x1, y1, x2, y2, cls, head)


def icon(svg, kind, cx, cy, s=18, tone='gray'):
    """Small line icons drawn in a tone (stroke = border colour, fill = tint)."""
    k = s / 18
    st, fl = f'ln-{tone}', f'pn-{tone}'
    w = 'stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"'
    P = lambda pts: ' '.join(f'{"M" if i == 0 else "L"}{cx + a * k:.1f},{cy + b * k:.1f}' for i, (a, b) in enumerate(pts))
    if kind == 'robot':
        svg.rect(cx - 7.5 * k, cy - 4.5 * k, 15 * k, 11.5 * k, fl, rx=3 * k, extra=w)
        svg.circle(cx - 3 * k, cy + 1 * k, 1.5 * k, SOLID.get(tone, 's3'))
        svg.circle(cx + 3 * k, cy + 1 * k, 1.5 * k, SOLID.get(tone, 's3'))
        svg.path(P([(0, -4.5), (0, -7.5)]), st, w)
        svg.circle(cx, cy - 8.3 * k, 1.4 * k, SOLID.get(tone, 's3'))
    elif kind == 'cap':
        svg.path(P([(-9, -2), (0, -6.5), (9, -2), (0, 2.5)]) + ' Z', fl, w)
        svg.path(P([(-5, 0), (-5, 4.5)]) + ' ' + P([(5, 0), (5, 4.5)]).replace('M', 'M', 1), st, w)
        svg.path(f'M{cx - 5 * k:.1f},{cy + 4.5 * k:.1f} Q{cx:.1f},{cy + 7.5 * k:.1f} {cx + 5 * k:.1f},{cy + 4.5 * k:.1f}', st, w)
        svg.path(P([(9, -2), (9, 4)]), st, w)
    elif kind == 'doc':
        svg.path(P([(-6, -8), (3, -8), (7, -4), (7, 8), (-6, 8)]) + ' Z', fl, w)
        svg.path(P([(3, -8), (3, -4), (7, -4)]), st, w)
        for yy in (-1.5, 1.5, 4.5):
            svg.path(P([(-3.2, yy), (4, yy)]), st, w)
    elif kind == 'funnel':
        svg.path(P([(-8, -7), (8, -7), (2, 0), (2, 7), (-2, 5), (-2, 0)]) + ' Z', fl, w)
    elif kind == 'book':
        svg.path(P([(0, -5), (-8, -7), (-8, 6), (0, 8)]) + ' Z', fl, w)
        svg.path(P([(0, -5), (8, -7), (8, 6), (0, 8)]) + ' Z', fl, w)
    elif kind == 'target':
        svg.circle(cx, cy, 8 * k, fl, w)
        svg.circle(cx, cy, 4.5 * k, st, w)
        svg.circle(cx, cy, 1.6 * k, SOLID.get(tone, 's3'))
    elif kind == 'house':
        svg.path(P([(-8, -1), (0, -8), (8, -1), (6, -1), (6, 8), (-6, 8), (-6, -1)]) + ' Z', fl, w)
        svg.path(P([(-2, 8), (-2, 3), (2, 3), (2, 8)]), st, w)
    elif kind == 'chart':
        for i, hgt in enumerate((5, 9, 13)):
            svg.rect(cx + (-7 + i * 5) * k, cy + (7 - hgt) * k, 3.6 * k, hgt * k, fl, rx=1, extra=w)
    elif kind == 'relay':
        svg.path(f'M{cx - 8 * k:.1f},{cy - 2 * k:.1f} A{8 * k:.1f},{6 * k:.1f} 0 0 1 {cx + 7 * k:.1f},{cy - 3 * k:.1f}', st, w)
        svg.path(P([(4, -6), (7, -3), (3, -1)]), st, w)
        svg.path(f'M{cx + 8 * k:.1f},{cy + 2 * k:.1f} A{8 * k:.1f},{6 * k:.1f} 0 0 1 {cx - 7 * k:.1f},{cy + 3 * k:.1f}', st, w)
        svg.path(P([(-4, 6), (-7, 3), (-3, 1)]), st, w)
    elif kind == 'check':
        svg.path(P([(-5, 0), (-1.5, 4), (6, -5)]), st, 'stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round" fill="none"')
    elif kind == 'cross':
        svg.path(P([(-4.5, -4.5), (4.5, 4.5)]) + ' ' + P([(4.5, -4.5), (-4.5, 4.5)]), st, 'stroke-width="2.2" stroke-linecap="round" fill="none"')
    elif kind == 'gpu':
        svg.rect(cx - 7 * k, cy - 6 * k, 14 * k, 12 * k, fl, rx=2 * k, extra=w)
        svg.rect(cx - 3.5 * k, cy - 2.5 * k, 7 * k, 5 * k, st, rx=1, extra=w)
        for d in (-4, 0, 4):
            svg.path(P([(d, -6), (d, -8.5)]) + ' ' + P([(d, 6), (d, 8.5)]), st, w)
    elif kind == 'scale':
        svg.path(P([(0, -7), (0, 7)]) + ' ' + P([(-7, -4), (7, -4)]) + ' ' + P([(-4, 7), (4, 7)]), st, w)
        svg.path(P([(-7, -4), (-9.5, 2), (-4.5, 2)]) + ' Z', fl, w)
        svg.path(P([(7, -4), (4.5, 2), (9.5, 2)]) + ' Z', fl, w)
    else:
        raise ValueError(kind)


def wedge_bracket(svg, x1, x2, y, cls='leader', h=5, down=True):
    d = h if down else -h
    svg.path(f'M{x1:.1f},{y - d:.1f} V{y:.1f} H{x2:.1f} V{y - d:.1f}', cls)


def polar(cx, cy, r, deg):
    return cx + r * _m.cos(_m.radians(deg)), cy + r * _m.sin(_m.radians(deg))


def mrich(svg, x, y, s, size=13, anchor='start', cls='ink'):
    """Math with sub/superscripts: 'log π_T(y_t | y_{<t})', 'A^E'. Shifts use dy so every browser renders them."""
    def esc(t):
        return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    out, i, shift = [], 0, 0.0
    small = size * 0.72
    while i < len(s):
        c = s[i]
        if c in '_^' and i + 1 < len(s):
            if s[i + 1] == '{':
                j = s.index('}', i + 2)
                body, i = s[i + 2:j], j + 1
            else:
                body, i = s[i + 1], i + 2
            d = size * (0.28 if c == '_' else -0.38)
            out.append(f'<tspan dy="{d - shift:.1f}" font-size="{small:.1f}">{esc(body)}</tspan>')
            shift = d
        else:
            j = i
            while j < len(s) and s[j] not in '_^':
                j += 1
            out.append(f'<tspan dy="{-shift:.1f}">{esc(s[i:j])}</tspan>' if shift else esc(s[i:j]))
            shift, i = 0.0, j
    a = f'x="{x:.1f}" y="{y:.1f}" font-size="{size}" class="math {cls}"' + (f' text-anchor="{anchor}"' if anchor != 'start' else '')
    svg.add(f'<text {a}>{"".join(out)}</text>')
