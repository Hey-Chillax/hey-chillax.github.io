"""Small SVG toolkit shared by the figure modules.

Colours are CSS classes (see the chart section of assets/css/site.css), so a figure follows the page theme.
Text that differs by language is a pair (en, zh); it becomes two <tspan lang> children that the page's
language switch shows or hides. Every chart is drawn at two widths: LG for desktop and SM for phones.
"""
import csv
import html
import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'tools' / 'data'
LG, SM = 720, 360


def esc(s):
    return html.escape(str(s), quote=False)


def T(en, zh=None):
    return (en, en if zh is None else zh)


FONT_W = json.loads((DATA / 'font_widths.json').read_text())['widths']


def text_w(s, size, weight=400):
    """Width of a string set in the site's sans (YZ Sans = Source Sans 3; CJK falls back to a full-width font)."""
    table = FONT_W['600' if weight >= 600 else '400']
    return size * sum(1.0 if ord(ch) > 0x2e80 else table.get(ch, 0.5) for ch in s)


def width_of(t, size, weight=400):
    if isinstance(t, tuple):
        return max(text_w(t[0], size, weight), text_w(t[1], size, weight))
    return text_w(t, size, weight)


class Svg:
    def __init__(self, w, h, label):
        self.w, self.h, self.label, self.parts = w, h, label, []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, t, cls='', anchor='start', size=12, weight=None, ls=None, extra=''):
        a = f'x="{x:.1f}" y="{y:.1f}" font-size="{size}"'
        if anchor != 'start':
            a += f' text-anchor="{anchor}"'
        if weight:
            a += f' font-weight="{weight}"'
        if ls:
            a += f' letter-spacing="{ls}"'
        if cls:
            a += f' class="{cls}"'
        if extra:
            a += ' ' + extra
        if isinstance(t, tuple) and t[0] != t[1]:
            inner = f'<tspan lang="en">{esc(t[0])}</tspan><tspan lang="zh-CN">{esc(t[1])}</tspan>'
        else:
            inner = esc(t[0] if isinstance(t, tuple) else t)
        self.add(f'<text {a}>{inner}</text>')

    def line(self, x1, y1, x2, y2, cls, extra=''):
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}"{" " + extra if extra else ""}/>')

    def rect(self, x, y, w, h, cls, rx=0, extra=''):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" rx="{rx}" class="{cls}"{" " + extra if extra else ""}/>')

    def circle(self, cx, cy, r, cls, extra=''):
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" class="{cls}"{" " + extra if extra else ""}/>')

    def path(self, d, cls, extra=''):
        self.add(f'<path d="{d}" class="{cls}"{" " + extra if extra else ""}/>')

    def mark(self, title, inner):
        self.add(f'<g class="mark"><title>{esc(title)}</title>{inner}</g>')

    def render(self, variant=''):
        cls = 'viz' + (' ' + variant if variant else '')
        return (f'<svg class="{cls}" viewBox="0 0 {self.w} {self.h:.0f}" width="{self.w}" height="{self.h:.0f}" role="img" '
                f'aria-label="{html.escape(self.label, quote=True)}" xmlns="http://www.w3.org/2000/svg">'
                + ''.join(self.parts) + '</svg>')


def scale(d0, d1, r0, r1):
    return lambda v: r0 + (v - d0) * (r1 - r0) / (d1 - d0)


def hbar(x0, y, x1, h, r=4):
    """Horizontal bar: square at the baseline, rounded data end."""
    r = min(r, max(x1 - x0, 0), h / 2)
    return (f'M{x0:.1f},{y:.1f} H{x1 - r:.1f} A{r},{r} 0 0 1 {x1:.1f},{y + r:.1f} '
            f'V{y + h - r:.1f} A{r},{r} 0 0 1 {x1 - r:.1f},{y + h:.1f} H{x0:.1f} Z')


def vbar(x, base, top, w, r=4):
    """Column: square at the baseline, rounded top."""
    r = min(r, max(base - top, 0), w / 2)
    return (f'M{x:.1f},{base:.1f} V{top + r:.1f} A{r},{r} 0 0 1 {x + r:.1f},{top:.1f} H{x + w - r:.1f} '
            f'A{r},{r} 0 0 1 {x + w:.1f},{top + r:.1f} V{base:.1f} Z')


def arrow(svg, x1, y1, x2, y2, cls='arrow', head=6.5):
    ang = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - head * 0.8 * math.cos(ang), y2 - head * 0.8 * math.sin(ang)
    svg.line(x1, y1, hx, hy, cls)
    p1 = (x2 - head * math.cos(ang - 0.42), y2 - head * math.sin(ang - 0.42))
    p2 = (x2 - head * math.cos(ang + 0.42), y2 - head * math.sin(ang + 0.42))
    svg.path(f'M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z', 'arrow-head')


def chevron(svg, x, y, size=5, cls='arrow'):
    svg.path(f'M{x - size * 0.45:.1f},{y - size:.1f} L{x + size * 0.45:.1f},{y:.1f} L{x - size * 0.45:.1f},{y + size:.1f}',
             cls, 'fill="none" stroke-linecap="round" stroke-linejoin="round"')


def legend(svg, x, y, items, size=12, gap=20):
    """items: [(series index, label)] drawn as a short line key and a name."""
    for idx, label in items:
        svg.line(x, y - 4, x + 16, y - 4, f'line l{idx}')
        svg.text(x + 22, y, label, size=size)
        x += 22 + width_of(label, size) + gap
    return x


def chip_legend(svg, x, y, items, size=11.5, gap=18):
    """items: [(css class, label)] drawn as a small rounded square and a name."""
    for cls, label in items:
        svg.rect(x, y - 9, 10, 10, cls, rx=2.5)
        svg.text(x + 15, y, label, size=size)
        x += 15 + width_of(label, size) + gap
    return x


def y_axis(svg, box, sy, ticks, fmt=str, size=11, grid=True):
    x0, y0, x1, y1 = box
    for v in ticks:
        y = sy(v)
        if grid:
            svg.line(x0, y, x1, y, 'grid' if abs(y - y1) > 0.5 else 'axis')
        svg.text(x0 - 8, y + 3.8, fmt(v), cls='t-faint', anchor='end', size=size)


def x_axis(svg, box, sx, ticks, fmt=str, size=11, title=None):
    x0, y0, x1, y1 = box
    for v in ticks:
        svg.text(sx(v), y1 + 17, fmt(v), cls='t-faint', anchor='middle', size=size)
    if title:
        svg.text(x1, y1 + 32, title, cls='t-faint', anchor='end', size=size)


def polyline(pts, sx, sy):
    return ' '.join(f'{"M" if i == 0 else "L"}{sx(x):.1f},{sy(y):.1f}' for i, (x, y) in enumerate(pts))


def hit_points(svg, pts, sx, sy, title_fn, r=7):
    for (x, y) in pts:
        svg.mark(title_fn(x, y), f'<circle class="hit" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="{r}"/>')


def end_labels(svg, items, min_gap=15):
    """items: [(x, y, text, cls)] placed to the right of line ends without overlapping."""
    items = sorted(items, key=lambda it: it[1])
    placed = []
    for x, y, t, cls in items:
        ty = y + 4
        if placed and ty - placed[-1] < min_gap:
            ty = placed[-1] + min_gap
        placed.append(ty)
        svg.text(x, ty, t, cls=cls, size=12)


def moving_avg(pts, k=5):
    out = []
    for i in range(len(pts)):
        win = [y for (_, y) in pts[max(0, i - k + 1):i + 1]]
        out.append((pts[i][0], sum(win) / len(win)))
    return out


def bi(t):
    return f'<span lang="en">{t[0]}</span><span lang="zh-CN">{t[1]}</span>'


def data_table(head, rows, summary=('Data', '数据')):
    th = ''.join(f'<th>{h}</th>' for h in head)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return (f'<details class="fig-data"><summary>{bi(summary)}</summary><div class="table-wrap"><table>'
            f'<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div></details>')


def read_csv(name):
    with open(DATA / name, newline='') as f:
        return list(csv.DictReader(f))


def run(rows, name, col):
    return [(int(r['step']), float(r[col])) for r in rows if r['run'] == name]


OPD = json.loads((DATA / 'scaffold_opd.json').read_text())
ALF = read_csv('alfworld_val.csv')
HPQ = read_csv('hotpotqa_val.csv')
FAMILY = read_csv('alfworld_family.csv')
PAIRED = {r['test'] + ':' + r['split']: r for r in read_csv('paired_tests.csv')}
