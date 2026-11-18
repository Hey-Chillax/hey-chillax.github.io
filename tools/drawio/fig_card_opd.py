"""Home page thumbnail for Scaffold-OPD: the teacher steps into the student's answer twice, briefly.

Variants: r1a / r1i / r1m (round 1: aesthetic, innovative, merged), r2a / r2i / r2m, r3a / r3i / r3m;
rounds 4-6 (r4a ... r6m) English only, without a frame of their own (the home-page card already frames them); final: r6m.
"""
from dlib import Fig, INK, LAV, LEAF, MUTED, SKY, SLATE, WHITE, label_w, icon_line_w

WIDTH = 300
LABEL = 'Scaffold-OPD in miniature: the teacher takes over the student’s answer twice, briefly, then hands back'
LABEL_ZH = 'Scaffold-OPD 缩略图：老师两次短暂接管学生的回答，随后交还'
T = lambda lang, en, zh: zh if lang == 'zh' else en


def lanes(v, lang):
    f = Fig(300, 190, LABEL)
    ys, yt = 44, 106
    names = [T(lang, 'Student', '学生'), T(lang, 'Teacher', '老师')]
    bw = max(label_w(n, 13.5, True) for n in names) + 22
    f.box(10, ys - 13, bw, 26, fill=SKY['fill'], stroke=SKY['line'], label=names[0], size=13.5, bold=True)
    f.box(10, yt - 13, bw, 26, fill=LEAF['fill'], stroke=LEAF['line'], label=names[1], size=13.5, bold=True)
    x_lane = 10 + bw + 10
    for y in (ys, yt):
        f.line([(x_lane, y), (292, y)], color=SLATE['tok'], width=1, dashed=True, dash='2 3')
    tok, pitch = 12, 16
    x = x_lane + 10

    def run(n, y, pal, first_lav=False):
        nonlocal x
        cs = []
        for i in range(n):
            p = LAV if (first_lav and i == 0) else pal
            f.token(x + tok / 2, y, p, size=tok)
            cs.append(x + tok / 2)
            x += pitch
        return cs

    s1 = run(3, ys, SKY)
    x += 6
    t1 = run(3, yt, LEAF, first_lav=True)
    x += 6
    s2 = run(2, ys, SKY)
    x += 6
    t2 = run(2, yt, LEAF, first_lav=True)
    end_x = x + tok / 2
    f.box(end_x - tok / 2, yt - tok / 2, tok, tok, fill=INK, stroke=INK, width=0.9, arc=2)
    # relay connectors: takeover (lavender, down), hand back (slate, up)
    for a, b in ((s1[-1], t1[0]), (s2[-1], t2[0])):
        f.edge([(a + 3, ys + tok / 2 + 1), (b - 3, yt - tok / 2 - 1)], color=LAV['line'], width=1.6, end=5)
    f.edge([(t1[-1] + 3, yt - tok / 2 - 1), (s2[0] - 3, ys + tok / 2 + 1)], color=SLATE['line'], width=1.3, end=5,
           dashed=True, dash='3 2')
    f.text((t1[0] + t1[-1]) / 2, yt + 22, '“Wait, …”', size=13, color=LEAF['dark'], anchor='c', bold=True)
    f.text(end_x + tok / 2, yt + 22, '“Final Answer …”', size=13, color=LEAF['dark'], anchor='e', bold=True)
    f.text(150, 166, T(lang, 'The teacher steps in, then hands back', '老师短暂接管，再交还给学生'), size=13, color=MUTED, anchor='c')
    return f


def document(v, lang):
    """The student's answer as a page of text, with the teacher's two short passages written into it."""
    f = Fig(300, 190, LABEL)
    f.box(10, 10, 280, 146, fill=WHITE, stroke=SLATE['line'], width=1.2, arc=9)
    f.text(22, 26, T(lang, 'Student’s Answer', '学生的回答'), size=13, bold=True, color=SKY['dark'])
    bar_h, x0, x1 = 7, 22, 278
    rows = [(46, [(x0, 232, 'sky')]),
            (62, [(x0, 118, 'sky'), ('takeover', '“Wait, let me check step 2 …”')]),
            (78, [(x0, 196, 'leaf')]),
            (94, [(x0, 168, 'sky')]),
            (110, [(x0, 254, 'sky')]),
            (126, [(x0, 86, 'sky'), ('takeover', '“Final Answer: 52”')]),
            (142, [(x0, 150, 'leaf')])]
    for y, parts in rows:
        cursor = x0
        for part in parts:
            if part[0] == 'takeover':
                f.token(cursor + 9, y, LAV, size=10)
                f.text(cursor + 18, y, part[1], size=12.5, color=LEAF['dark'], bold=True)
            else:
                a, b, fam = part
                pal = SKY if fam == 'sky' else LEAF
                f.box(a, y - bar_h / 2, b - a, bar_h, fill=pal['tok'], stroke='none', width=0, arc=4)
                cursor = b
    f.text(150, 172, T(lang, 'Two short teacher passages in the student’s own answer', '学生自己的回答里，老师只写了两小段'),
           size=12.5, color=MUTED, anchor='c')
    return f


def diff_doc(v, lang):
    """Round-1 merge: the answer as a page, with a gutter that shows who wrote each line (blue student, green teacher)
    and a lavender marker where the teacher takes over; black title, short caption."""
    f = Fig(300, 190, LABEL)
    f.box(10, 8, 280, 150, fill=WHITE, stroke=SLATE['line'], width=1.2, arc=9)
    f.text(22, 24, T(lang, 'The Student’s Answer', '学生的回答'), size=13.5, bold=True, color=INK)
    rows = [('s', 156), ('s', 44, 'Wait, let me check …'), ('t', 150), ('s', 176), ('s', 56, '### Final Answer: 52'), ('t', 110)]
    y = 46
    for row in rows:
        who = row[0]
        pal = SKY if who == 's' else LEAF
        f.box(20, y - 7, 4, 14, fill=pal['line'], stroke='none', width=0, arc=2)
        f.box(32, y - 3.5, row[1], 7, fill=pal['tok'], stroke='none', width=0, arc=3.5)
        if len(row) == 3:
            x = 32 + row[1] + 8
            f.token(x + 5, y, LAV, size=10)
            f.text(x + 14, y, '“' + row[2] + '”', size=12.5, color=LEAF['dark'], bold=True)
        y += 18
    f.text(150, 174, T(lang, 'The teacher writes two short passages', '老师只写了两小段'), size=13, color=MUTED, anchor='c')
    return f


def diff_doc2(v, lang, legend=False):
    """Round 2: the answer page with a natural line rhythm and larger quotes; with legend, a key replaces the caption."""
    f = Fig(300, 190, LABEL)
    f.box(8, 6, 284, 150, fill=WHITE, stroke=SLATE['line'], width=1.2, arc=9)
    f.text(20, 23, T(lang, 'The Student’s Answer', '学生的回答'), size=13.5, bold=True, color=INK)
    rows = [('s', 214), ('s', 38, 'Wait, let me check …'), ('t', 176), ('t', 112), ('s', 230), ('s', 46, '### Final Answer: 52'), ('t', 132)]
    y = 44
    for row in rows:
        who = row[0]
        pal = SKY if who == 's' else LEAF
        f.box(18, y - 7, 4, 14, fill=pal['line'], stroke='none', width=0, arc=2)
        f.box(30, y - 3.5, row[1], 7, fill=pal['tok'], stroke='none', width=0, arc=3.5)
        if len(row) == 3:
            x = 30 + row[1] + 7
            f.token(x + 5, y, LAV, size=10)
            f.text(x + 14, y, '“' + row[2] + '”', size=13, color=LEAF['dark'], bold=True)
        y += 16
    if legend:
        x = 22
        for pal, t in ((SKY, T(lang, 'Student', '学生')), (LEAF, T(lang, 'Teacher', '老师')), (LAV, T(lang, 'Takeover', '接管'))):
            f.box(x, 168, 4, 14, fill=pal['line'], stroke='none', width=0, arc=2)
            x0, x1 = f.text(x + 9, 175, t, size=13, color=INK)
            x = x1 + 22
    else:
        f.text(150, 174, T(lang, 'The teacher writes two short passages', '老师只写了两小段'), size=13, color=MUTED, anchor='c')
    return f


def diff_doc3(v, lang, highlight=False):
    """Round 3: the legend card polished, the concluding quote with its check-box glyph (as in the method figure);
    with highlight, the teacher's quotes sit on a marker-pen band, so they read as text inserted into the page."""
    f = Fig(300, 190, LABEL)
    f.box(8, 6, 284, 150, fill=WHITE, stroke=SLATE['line'], width=1.2, arc=9)
    f.text(20, 23, T(lang, 'The Student’s Answer', '学生的回答'), size=13.5, bold=True, color=INK)
    rows = [('s', 214), ('s', 38, ['“Wait, let me check …”']), ('t', 176), ('t', 112), ('s', 230),
            ('s', 46, ['“###', None, 'Final Answer: 52”']), ('t', 132)]
    y = 44
    for row in rows:
        pal = SKY if row[0] == 's' else LEAF
        f.box(18, y - 7, 4, 14, fill=pal['line'], stroke='none', width=0, arc=2)
        f.box(30, y - 3.5, row[1], 7, fill=pal['tok'], stroke='none', width=0, arc=3.5)
        if len(row) == 3:
            x = 30 + row[1] + 7
            f.token(x + 5, y, LAV, size=10)
            if highlight:
                w = icon_line_w(row[2], 13, True)
                f.box(x + 13, y - 8, w + 2, 16, fill=LEAF['soft'], stroke='none', width=0, arc=3)
            f.text_icon(x + 14, y, row[2], size=13, color=LEAF['dark'], bold=True)
        y += 16
    items = ((SKY, T(lang, 'Student', '学生')), (LEAF, T(lang, 'Teacher', '老师')), (LAV, T(lang, 'Takeover', '接管')))
    widths = [label_w(t, 13) + 9 + 4 for _, t in items]
    x = (300 - sum(widths) - 2 * 22) / 2
    for (pal, t), w in zip(items, widths):
        f.box(x, 168, 4, 14, fill=pal['line'], stroke='none', width=0, arc=2)
        f.text(x + 9, 175, t, size=13, color=INK)
        x += w + 22
    return f


def build(v, lang):
    if v[:2] in ('r4', 'r5', 'r6'):
        return {'r4a': lambda: doc4(), 'r4i': lambda: doc4(highlight=True, title=False),
                'r4m': lambda: doc4(highlight=True), 'r5a': doc5, 'r5i': tokens5, 'r5m': doc5,
                'r6a': doc6, 'r6i': lambda: doc6(big=True), 'r6m': lambda: doc6(big=True)}[v]()
    if v in ('r3a', 'r3i', 'r3m'):
        return diff_doc3(v, lang, highlight=(v == 'r3i'))
    if v == 'r1i':
        return document(v, lang)
    if v == 'r1a':
        return lanes(v, lang)
    if v == 'r1m':
        return diff_doc(v, lang)
    return diff_doc2(v, lang, legend=(v == 'r2i'))


# ------------------------------------------------------------------ rounds 4-6 (English only)
# The card already sits in a framed box on the home page, so from round 4 the figure has no frame of its own.
ROWS4 = [('s', 236), ('s', 40, ['“Wait, let me check …”']), ('t', 196), ('t', 124), ('s', 252),
         ('s', 48, ['“###', None, 'Final Answer: 52”']), ('t', 146)]


def legend_row(f, y, size=13):
    items = ((SKY, 'Student'), (LEAF, 'Teacher'), (LAV, 'Takeover'))
    widths = [label_w(t, size) + 10 + 4 for _, t in items]
    x = (300 - sum(widths) - 2 * 24) / 2
    for (pal, t), w in zip(items, widths):
        f.box(x, y - 7.5, 4, 15, fill=pal['line'], stroke='none', width=0, arc=2)
        f.text(x + 10, y, t, size=size, color=INK)
        x += w + 24


def doc4(highlight=False, title=True):
    f = Fig(300, 190, LABEL)
    y = 16
    if title:
        f.text(14, y, 'The Student’s Answer', size=14, bold=True)
        y += 24
    pitch = 17 if title else 19
    for row in ROWS4:
        pal = SKY if row[0] == 's' else LEAF
        f.box(14, y - 7.5, 4, 15, fill=pal['line'], stroke='none', width=0, arc=2)
        f.box(26, y - 3.5, row[1], 7, fill=pal['tok'], stroke='none', width=0, arc=3.5)
        if len(row) == 3:
            x = 26 + row[1] + 7
            f.token(x + 5, y, LAV, size=10)
            if highlight:
                w = icon_line_w(row[2], 13.5, True)
                f.box(x + 13, y - 9, w + 4, 18, fill=LEAF['soft'], stroke='none', width=0, arc=3)
            f.text_icon(x + 15, y, row[2], size=13.5, color=LEAF['dark'], bold=True)
        y += pitch
    legend_row(f, 172)
    return f


# ------------------------------------------------------------------ round 5
def doc5(title=True, pitch=17, title_size=13.5):
    """Round-5 aesthetic: r4m with the title and the lines on one left edge, a calmer title, and even spacing down to
    the key."""
    f = Fig(300, 190, LABEL)
    y = 17
    if title:
        f.text(12, y, 'The Student’s Answer', size=title_size, bold=True)
        y += 25
    for row in ROWS4:
        pal = SKY if row[0] == 's' else LEAF
        f.box(14, y - 7.5, 4, 15, fill=pal['line'], stroke='none', width=0, arc=2)
        f.box(26, y - 3.5, row[1], 7, fill=pal['tok'], stroke='none', width=0, arc=3.5)
        if len(row) == 3:
            x = 26 + row[1] + 7
            f.token(x + 5, y, LAV, size=10)
            w = icon_line_w(row[2], 13.5, True)
            f.box(x + 13, y - 9, w + 4, 18, fill=LEAF['soft'], stroke='none', width=0, arc=3)
            f.text_icon(x + 15, y, row[2], size=13.5, color=LEAF['dark'], bold=True)
        y += pitch
    legend_row(f, 172)
    return f


TOKROWS = [('s', 17, None), ('s', 5, ['“Wait, let me check …”']), ('t', 12, None), ('s', 17, None),
           ('s', 4, ['“###', None, 'Final Answer: 52”']), ('t', 8, 'end')]


def tokens5():
    """Round-5 innovative: the answer as rows of tokens, one square per token as in the method figure; each takeover
    token is followed by the teacher's opening words, and the teacher's passage continues on the next row."""
    f = Fig(300, 190, LABEL)
    tok, pitch = 10, 15.4
    y = 20
    x0 = 14
    for who, n, extra in TOKROWS:
        pal = SKY if who == 's' else LEAF
        x = x0
        for j in range(n):
            f.token(x + tok / 2, y, pal, size=tok)
            x += pitch
        if isinstance(extra, list):
            f.token(x + tok / 2, y, LAV, size=tok)
            w = icon_line_w(extra, 13.5, True)
            f.box(x + tok + 3, y - 9, w + 4, 18, fill=LEAF['soft'], stroke='none', width=0, arc=3)
            f.text_icon(x + tok + 5, y, extra, size=13.5, color=LEAF['dark'], bold=True)
        elif extra == 'end':
            f.box(x, y - tok / 2, tok, tok, fill=INK, stroke=INK, width=0.9, arc=2)
        y += 22
    legend_row(f, 172)
    return f


# ------------------------------------------------------------------ round 6
def legend_web(f, y, size=13, gap=26):
    """The key, centred with the web font's own widths (Comic Neue), so the gaps are even on the page."""
    from dlib import web_w
    items = ((SKY, 'Student'), (LEAF, 'Teacher'), (LAV, 'Takeover'))
    widths = [10 + web_w(t, size) for _, t in items]
    x = (300 - sum(widths) - gap * (len(items) - 1)) / 2
    for (pal, t), w in zip(items, widths):
        f.box(x, y - 7.5, 4, 15, fill=pal['line'], stroke='none', width=0, arc=2)
        f.text(x + 10, y, t, size=size, color=INK)
        x += w + gap


ROWS6 = [('s', 236), ('s', 40, ['“Wait, let me check …”']), ('t', 196), ('s', 252),
         ('s', 48, ['“###', None, 'Final Answer: 52”']), ('t', 146)]


def doc6(big=False):
    """Round 6: doc5 with the key spaced by the web font; big: six lines instead of seven, the quotes and the title a
    size larger (the card is shown about 286 px wide)."""
    f = Fig(300, 190, LABEL)
    y = 17
    tsize, qsize = (14.5, 14.5) if big else (13.5, 13.5)
    f.text(12, y, 'The Student’s Answer', size=tsize, bold=True)
    y += 26 if big else 25
    pitch = 20 if big else 17
    for row in (ROWS6 if big else ROWS4):
        pal = SKY if row[0] == 's' else LEAF
        f.box(14, y - 7.5, 4, 15, fill=pal['line'], stroke='none', width=0, arc=2)
        f.box(26, y - 3.5, row[1], 7, fill=pal['tok'], stroke='none', width=0, arc=3.5)
        if len(row) == 3:
            x = 26 + row[1] + 7
            f.token(x + 5, y, LAV, size=10)
            w = icon_line_w(row[2], qsize, True)
            f.box(x + 13, y - 9.5, w + 4, 19, fill=LEAF['soft'], stroke='none', width=0, arc=3)
            f.text_icon(x + 15, y, row[2], size=qsize, color=LEAF['dark'], bold=True)
        y += pitch
    legend_web(f, 174)
    return f
