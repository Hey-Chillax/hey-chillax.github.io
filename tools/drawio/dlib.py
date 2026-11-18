"""Small library for the homepage's method diagrams, drawn as draw.io files.

The conventions follow the author's hand-drawn figure style:

* soft fills with a darker stroke of the same hue; large areas stay pale, colour sits on the modules and tokens;
* one colour, one meaning: sky = student / ours, leaf = teacher, lavender = takeover point or shared state,
  lemon = environment, rose = failure or negative, slate = neutral;
* words in a hand-drawn face (Comic Sans MS in the .drawio files, Comic Neue on the web), symbols in Times New Roman;
* titles in black, Title Case; labels centred and clear of their borders; arrows land on borders with a visible shaft.

Coordinates are pixels of the displayed figure (1 draw.io unit = 1 px at the intended width), origin top left.
"""
import pathlib
import re
from xml.sax.saxutils import quoteattr

from PIL import ImageFont

HERE = pathlib.Path(__file__).resolve().parent

# ------------------------------------------------------------------ colours
# Every family: pale (container), soft (secondary box), fill (main box), tok (token), line (border, arrow), dark (text).
SKY = dict(pale='#F4F9FE', soft='#DDEEFB', fill='#C6E2F9', tok='#A9D8F6', line='#5B9BD5', dark='#2B6A9E')
LEAF = dict(pale='#F3FAF1', soft='#E6F4E1', fill='#DDF1D6', tok='#B8E3AD', line='#6AAE5C', dark='#3B7631')
LAV = dict(pale='#FBF9FE', soft='#F1ECFA', fill='#E2D8F4', tok='#C9B8EA', line='#8F76C2', dark='#5B448C')
LEMON = dict(pale='#FFFDF2', soft='#FDF3C4', fill='#FAEA94', tok='#F3DA6A', line='#CDAA2A', dark='#7A6210')
ROSE = dict(pale='#FEF5F5', soft='#FCE3E3', fill='#F9CCCC', tok='#F6B6B6', line='#DA7474', dark='#A63D3D')
SLATE = dict(pale='#FAFBFC', soft='#F1F3F6', fill='#E8EBEF', tok='#C7CCD4', line='#8F98A6', dark='#4A5361')
FAMILIES = {'sky': SKY, 'leaf': LEAF, 'lav': LAV, 'lemon': LEMON, 'rose': ROSE, 'slate': SLATE}
INK, LINE, MUTED, WHITE = '#1E1E1E', '#3A3A3A', '#5C5C5C', '#FFFFFF'

# Dark-mode values for the same names (page background #111317): tinted near-blacks for areas, mid tones for
# tokens, lighter strokes and text.
DARK = {
    'sky': dict(pale='#15202B', soft='#1B2A39', fill='#22374C', tok='#3E6E99', line='#6FA8DE', dark='#9CC8F0'),
    'leaf': dict(pale='#162216', soft='#1C2B1C', fill='#253A24', tok='#4E7E45', line='#7DBB6E', dark='#A5D896'),
    'lav': dict(pale='#1D1828', soft='#252033', fill='#33294A', tok='#6A5A92', line='#A48FD6', dark='#C9B6EE'),
    'lemon': dict(pale='#221F10', soft='#2C2814', fill='#3D3719', tok='#8A7A2C', line='#D4B848', dark='#E6CF6F'),
    'rose': dict(pale='#261819', soft='#321F21', fill='#46292B', tok='#9A5555', line='#E28A8A', dark='#F0A9A9'),
    'slate': dict(pale='#171A1F', soft='#1D2127', fill='#2A2F37', tok='#5A626E', line='#8E97A5', dark='#B5BDC8'),
}
DARK_BASE = {'ink': '#E6E8EB', 'line': '#C4C9D0', 'muted': '#A3AAB4', 'white': '#1B1F25'}


def palette_vars():
    """CSS variable name -> (light, dark) for every colour the diagrams use."""
    out = {}
    for fam, pal in FAMILIES.items():
        for role, hexv in pal.items():
            out[f'--dg-{fam}-{role}'] = (hexv, DARK[fam][role])
    for name, hexv in (('ink', INK), ('line', LINE), ('muted', MUTED), ('white', WHITE)):
        out[f'--dg-{name}'] = (hexv, DARK_BASE[name])
    return out


# ------------------------------------------------------------------ fonts and text width
HAND, MATH = 'Comic Sans MS', 'Times New Roman'
_FILES = {
    # Measured with Comic Sans MS, the face draw.io itself uses when it lays out and crops the figure; the web shows the
    # slightly narrower Comic Neue, so every label still fits there.
    (HAND, False): pathlib.Path('/mnt/c/Windows/Fonts/comic.ttf'), (HAND, True): pathlib.Path('/mnt/c/Windows/Fonts/comicbd.ttf'),
    (MATH, False): pathlib.Path('/mnt/c/Windows/Fonts/timesi.ttf'), (MATH, True): pathlib.Path('/mnt/c/Windows/Fonts/timesbi.ttf'),
    ('cjk', False): pathlib.Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
    ('cjk', True): pathlib.Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'),
}
_cache = {}


def _font(kind, bold):
    key = (kind, bold)
    if key not in _cache:
        path = _FILES[key]
        _cache[key] = ImageFont.truetype(str(path), 100, index=2 if kind == 'cjk' else 0)   # index 2: SC in the CJK collection
    return _cache[key]


def _seg_w(s, size, bold, family):
    """Width in px of plain text s at size px; CJK characters are measured with the CJK fallback."""
    w = 0.0
    for run in re.findall(r'[⺀-鿿＀-￯　-〿]+|[^⺀-鿿＀-￯　-〿]+', s):
        kind = 'cjk' if re.match(r'[⺀-鿿＀-￯　-〿]', run) else family
        w += _font(kind, bold).getlength(run) / 100 * size
    return w


def line_w(html, size, bold=False, family=HAND):
    """Width in px of one line of an HTML label: <b>, <i>, Times spans (math) and <sub>/<sup> at 70 %."""
    w = 0.0
    pos = 0
    for m in re.finditer(r'<span style="font-family:Times New Roman;[^"]*">(.*?)</span>', html):
        w += _plain(html[pos:m.start()], size, bold, family)
        w += _plain(m.group(1), size, bold, MATH)
        pos = m.end()
    return w + _plain(html[pos:], size, bold, family)


def _plain(html, size, bold, family):
    w = 0.0
    for part in re.split(r'(<su[bp]>.*?</su[bp]>)', html):
        if part.startswith('<su'):
            w += _seg_w(_strip(part), size * 0.7, bold, family)
        else:
            b = bold or '<b>' in part
            w += _seg_w(_strip(part), size, b, family)
    return w


def _strip(html):
    s = re.sub(r'<[^>]+>', '', html)
    return s.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')


def label_w(html, size, bold=False, family=HAND):
    return max(line_w(t, size, bold, family) for t in html.split('<br>'))


def m(s, size=None):
    """A symbol in the math face (Times New Roman italic); size in px, optional."""
    fs = f'font-size:{size}px;' if size else ''
    return f'<span style="font-family:Times New Roman;{fs}"><i>{s}</i></span>'


def msub(base, sub, size=None):
    """Italic symbol with a subscript, e.g. msub('s', '2') -> s₂ in Times."""
    fs = f'font-size:{size}px;' if size else ''
    return f'<span style="font-family:Times New Roman;{fs}"><i>{base}</i><sub>{sub}</sub></span>'


def col(html, color):
    return f'<span style="color:{color};">{html}</span>'


# ------------------------------------------------------------------ figure builder
class Fig:
    def __init__(self, w, h, label):
        self.w, self.h, self.label = w, h, label
        self.cells = []
        self.n = 0
        self.frame()

    def _id(self, p):
        self.n += 1
        return f'{p}{self.n}'

    def vertex(self, x, y, w, h, style, value='', p='v'):
        cid = self._id(p)
        self.cells.append(f'<mxCell id="{cid}" value={quoteattr(value)} style={quoteattr(style)} vertex="1" parent="1">'
                          f'<mxGeometry x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" as="geometry"/></mxCell>')
        return cid

    # -- shapes with labels
    def box(self, x, y, w, h, fill=WHITE, stroke=SLATE['line'], label='', size=13, color=INK, bold=False, italic=False,
            width=1.2, arc=7, dashed=False, align='center', valign='middle', family=HAND, pad=0, lift=0.0, wrap=False):
        fstyle = (1 if bold else 0) | (2 if italic else 0)
        style = (f'rounded=1;arcSize={arc};absoluteArcSize=1;html=1;whiteSpace={"wrap" if wrap else "nowrap"};'
                 f'fillColor={fill};strokeColor={stroke};strokeWidth={width};fontFamily={family};fontSize={size};'
                 f'fontColor={color};align={align};verticalAlign={valign};spacing={pad};fontStyle={fstyle};')
        if dashed:
            style += 'dashed=1;dashPattern=5 3;'
        if lift:
            style += f'spacingBottom={2 * lift:.1f};'
        return self.vertex(x, y, w, h, style, label, 'b')

    def cbox(self, cx, cy, w, h, **kw):
        return self.box(cx - w / 2, cy - h / 2, w, h, **kw)

    def text(self, x, y, html, size=13, color=INK, anchor='w', bold=False, italic=False, family=HAND, lh=1.25):
        """Label anchored at (x, y): anchor w / e / c, vertically centred on y. Returns (x0, x1)."""
        if italic and any('\u3000' <= ch <= '\u9fff' or '\uff00' <= ch <= '\uffef' for ch in html):
            italic = False          # no slanted Chinese: a synthesized oblique looks broken
        lines = html.split('<br>')
        w = label_w(html, size, bold, family) + 4
        h = len(lines) * size * lh + 2
        x0 = {'w': x, 'e': x - w, 'c': x - w / 2}[anchor]
        align = {'w': 'left', 'e': 'right', 'c': 'center'}[anchor]
        fstyle = (1 if bold else 0) | (2 if italic else 0)
        style = (f'text;html=1;whiteSpace=nowrap;fontFamily={family};fontSize={size};fontColor={color};align={align};'
                 f'verticalAlign=middle;spacing=0;fontStyle={fstyle};')
        self.vertex(x0, y - h / 2, w, h, style, html, 't')
        return x0, x0 + w

    # -- lines
    def edge(self, pts, color=LINE, width=1.2, arrow=True, dashed=False, dash='4 3', end=6, curved=False, start=False,
             rounded=True):
        (x0, y0), *mid, (x1, y1) = pts
        style = (f'edgeStyle=none;html=1;rounded={1 if rounded and not curved else 0};strokeColor={color};strokeWidth={width};'
                 f'endArrow={"block" if arrow else "none"};endFill=1;endSize={end};'
                 f'startArrow={"block" if start else "none"};startFill=1;startSize={end};')
        if curved:
            style += 'curved=1;'
        if dashed:
            style += f'dashed=1;dashPattern={dash};'
        way = ''.join(f'<mxPoint x="{x:.2f}" y="{y:.2f}"/>' for x, y in mid)
        way = f'<Array as="points">{way}</Array>' if mid else ''
        cid = self._id('e')
        self.cells.append(f'<mxCell id="{cid}" value="" style={quoteattr(style)} edge="1" parent="1">'
                          f'<mxGeometry relative="1" as="geometry"><mxPoint x="{x0:.2f}" y="{y0:.2f}" as="sourcePoint"/>'
                          f'<mxPoint x="{x1:.2f}" y="{y1:.2f}" as="targetPoint"/>{way}</mxGeometry></mxCell>')
        return cid

    def line(self, pts, color=LINE, width=1.2, dashed=False, dash='4 3'):
        return self.edge(pts, color, width, arrow=False, dashed=dashed, dash=dash)

    # -- small parts
    def token(self, cx, cy, pal, size=10, fill=None, stroke=None, width=0.9):
        return self.box(cx - size / 2, cy - size / 2, size, size, fill=fill or pal['tok'], stroke=stroke or pal['line'],
                        width=width, arc=2)

    def token_row(self, x0, cy, n, pal, size=10, pitch=13, **kw):
        xs = [x0 + size / 2 + i * pitch for i in range(n)]
        for x in xs:
            self.token(x, cy, pal, size, **kw)
        return xs

    def chip(self, x, cy, label, pal, size=12, h=20, pad=7, solid=False, bold=False, family=HAND, color=None):
        """Rounded word chip, left edge at x, centred on cy; returns its right edge."""
        w = label_w(label, size, bold, family) + 2 * pad
        fill, stroke = (pal['tok'], pal['line']) if solid else (pal['soft'], pal['line'])
        self.box(x, cy - h / 2, w, h, fill=fill, stroke=stroke, label=label, size=size, color=color or INK, bold=bold,
                 width=1, arc=5, family=family)
        return x + w

    def badge(self, cx, cy, n, pal, r=9, size=11.5, role='line'):
        style = (f'ellipse;html=1;fillColor={pal[role]};strokeColor=none;fontFamily={HAND};fontSize={size};'
                 f'fontColor={WHITE};fontStyle=1;spacing=0;')
        return self.vertex(cx - r, cy - r, 2 * r, 2 * r, style, str(n), 'g')

    def done_icon(self, cx, cy, s=11, pal=LEAF):
        """The check-box glyph of '### \u2705 Final Answer', drawn (the web font has no emoji)."""
        self.box(cx - s / 2, cy - s / 2, s, s, fill=pal['line'], stroke='none', width=0, arc=2.5)
        self.check(cx, cy + s * 0.03, s=s * 0.6, color=WHITE, width=1.5)

    def text_icon(self, x, y, parts, size=13, color=INK, bold=False, italic=False, anchor='w', icon=11, gap=3.5):
        """One line of text with drawn check-box glyphs: parts are strings, or None for a glyph. The pieces are placed
        with the web font's own advance widths (Comic Neue), so on the page the glyph sits one space from its
        neighbours. Returns (x0, x1)."""
        widths = [icon + 2 * gap if p is None else web_w(p, size, bold) for p in parts]
        total = sum(widths)
        x0 = {'w': x, 'e': x - total, 'c': x - total / 2}[anchor]
        cx = x0
        for p, w in zip(parts, widths):
            if p is None:
                self.done_icon(cx + w / 2, y, s=icon)
            else:
                self.text(cx, y, p, size=size, color=color, bold=bold, italic=italic)
            cx += w
        return x0, x0 + total

    def dot(self, cx, cy, r=2.6, color=LINE):
        return self.vertex(cx - r, cy - r, 2 * r, 2 * r, f'ellipse;html=1;fillColor={color};strokeColor=none;', '', 'd')

    def circle_op(self, cx, cy, kind='plus', r=8, color=LINE):
        shape = {'plus': 'summing_function', 'times': 'or'}[kind]
        return self.vertex(cx - r, cy - r, 2 * r, 2 * r,
                           f'shape=mxgraph.flowchart.{shape};html=1;fillColor={WHITE};strokeColor={color};strokeWidth=1.2;',
                           '', 'o')

    def check(self, cx, cy, s=8, color=LEAF['dark'], width=2.2):
        self.edge([(cx - s * 0.55, cy), (cx - s * 0.12, cy + s * 0.45), (cx + s * 0.62, cy - s * 0.5)], color=color,
                  width=width, arrow=False, rounded=False)

    def cross(self, cx, cy, s=7, color=ROSE['dark'], width=2.2):
        self.edge([(cx - s / 2, cy - s / 2), (cx + s / 2, cy + s / 2)], color=color, width=width, arrow=False)
        self.edge([(cx - s / 2, cy + s / 2), (cx + s / 2, cy - s / 2)], color=color, width=width, arrow=False)

    def hbracket(self, x0, x1, y, depth=5, color=SLATE['line'], down=True, width=1):
        """A flat bracket under (down=True) or over a span, with its feet pointing at the span."""
        d = depth if down else -depth
        self.edge([(x0, y - d), (x0, y), (x1, y), (x1, y - d)], color=color, width=width, arrow=False, rounded=False)

    def panel(self, x, y, w, h, pal, title='', num=None, size=14, dashed=False, title_color=INK, arc=10, width=1.3,
              fill=None, num_role='dark'):
        self.box(x, y, w, h, fill=fill or pal['pale'], stroke=pal['line'], width=width, arc=arc, dashed=dashed)
        if title:
            tx = x + 14
            if num is not None:
                self.badge(x + 23, y + 20, num, pal, role=num_role)
                tx = x + 39
            self.text(tx, y + 20, title, size=size, bold=True, color=title_color)

    def frame(self):
        """Invisible rectangle spanning the figure, so the cropped export is exactly w x h."""
        self.vertex(0, 0, self.w, self.h, 'rounded=0;html=1;fillColor=none;strokeColor=none;', '', 'c')

    def to_xml(self):
        return ('<mxfile host="Electron"><diagram id="fig" name="Page-1"><mxGraphModel grid="0" page="0" math="0" shadow="0">'
                '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + ''.join(self.cells) +
                '</root></mxGraphModel></diagram></mxfile>')


_WEB = None


def web_w(text, size, bold=False):
    """Advance width on the page: Comic Neue, from the site's tools/data/font_widths.json (hand400 / hand700)."""
    global _WEB
    if _WEB is None:
        import json
        _WEB = json.loads((pathlib.Path(__file__).resolve().parent.parent / 'data' / 'font_widths.json').read_text())['widths']
    table = _WEB['hand700' if bold else 'hand400']
    return sum(table.get(ch, 0.55) for ch in text) * size


def icon_line_w(parts, size, bold=False, icon=11, gap=3.5):
    """Width of a text_icon line, on the page."""
    return sum(icon + 2 * gap if p is None else web_w(p, size, bold) for p in parts)


TIMES = '<span style="font-family:Times New Roman;">×</span>'   # the hand font's × is tiny; Times has a proper one
