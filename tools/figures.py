"""The site's figures, final versions.

Every figure went through three versions before this one: the original drawing (tools/lab/figs_base.py), an
aesthetic pass (tools/lab/figs_aes.py) and an innovative pass that was free to restructure (tools/lab/figs_inno.py).
This module keeps, for each figure, the version that worked best or a merge of several; tools/lab/figure_lab.py
shows all four side by side. Data comes from tools/data/ (see figlib.py).
"""
import math

from figlib import (ALF, FAMILY, HPQ, OPD, PAIRED, Svg, T, arrow, bi, chevron, data_table, end_labels, hbar, hit_points,
                    moving_avg, polyline, run, scale, text_w, vbar, width_of, x_axis, y_axis)

LANGS = ('en', 'zh-CN')


# ----------------------------------------------------------------------------- helpers
def per_lang(svg, draw):
    """Draw a language-dependent layout twice, once per language; draw(i) uses plain strings (pair[i])."""
    for i, lang in enumerate(LANGS):
        svg.add(f'<g lang="{lang}">')
        draw(i)
        svg.add('</g>')


def pick(t, i):
    return t[i] if isinstance(t, tuple) else t


def legend(svg, x, y, items, size=12, gap=20):
    """Line keys: items = [(series index, label)]."""
    def draw(i):
        xx = x
        for idx, label in items:
            s = pick(label, i)
            svg.line(xx, y - 4, xx + 16, y - 4, f'line l{idx}')
            svg.text(xx + 22, y, s, size=size)
            xx += 22 + text_w(s, size) + gap
    per_lang(svg, draw)


def chip_legend(svg, x, y, items, size=11.5, gap=18):
    """Square keys: items = [(css class, label)]."""
    def draw(i):
        xx = x
        for cls, label in items:
            s = pick(label, i)
            svg.rect(xx, y - 9, 10, 10, cls, rx=2.5)
            svg.text(xx + 15, y, s, size=size)
            xx += 15 + text_w(s, size) + gap
    per_lang(svg, draw)


def panel_title(svg, x, y, title, sub=None):
    def draw(i):
        t = pick(title, i)
        svg.text(x, y, t, cls='t-strong', size=12.5)
        if sub:
            svg.text(x + text_w(t, 12.5, 600) + 8, y, pick(sub, i), cls='t-faint', size=11)
    per_lang(svg, draw)


def breadcrumb(svg, names, key, y, size=11.5, gap=16):
    def draw(i):
        labels = [pick(n, i) for n in names]
        widths = [text_w(s, size, 600 if j == key else 400) for j, s in enumerate(labels)]
        x = (svg.w - (sum(widths) + gap * (len(labels) - 1))) / 2
        for j, (s, w) in enumerate(zip(labels, widths)):
            svg.text(x, y, s, cls='t-accent' if j == key else 't-faint', size=size)
            if j == key:
                svg.line(x, y + 5, x + w, y + 5, 'line l1', 'stroke-width="1.6"')
            if j < len(labels) - 1:
                chevron(svg, x + w + gap / 2, y - 4, 3)
            x += w + gap
    per_lang(svg, draw)


def gap_wash(svg, xs, a, b, sx, sy, pos='wash1', neg='wash2'):
    """Shade between two series sampled at the same x: `pos` where a leads, `neg` where b leads.
    Runs of the same sign become one polygon; the crossing points are interpolated."""
    pts = []
    for i in range(len(xs)):
        if i:
            d0, d1 = a[i - 1] - b[i - 1], a[i] - b[i]
            if d0 * d1 < 0:
                t = d0 / (d0 - d1)
                yc = a[i - 1] + t * (a[i] - a[i - 1])
                pts.append((xs[i - 1] + t * (xs[i] - xs[i - 1]), yc, yc))
        pts.append((xs[i], a[i], b[i]))
    runs, cur, sign = [], [], 0
    for p in pts:
        s = (p[1] > p[2]) - (p[1] < p[2])
        if s and sign and s != sign:
            runs.append((sign, cur))
            cur = [cur[-1]]
        if s:
            sign = s
        cur.append(p)
    runs.append((sign, cur))
    for s, seg in runs:
        if s and len(seg) >= 2:
            top = ' L'.join(f'{sx(x):.1f},{sy(ya):.1f}' for x, ya, _ in seg)
            bot = ' L'.join(f'{sx(x):.1f},{sy(yb):.1f}' for x, _, yb in reversed(seg))
            svg.path(f'M{top} L{bot} Z', pos if s > 0 else neg)


def series_lines(svg, series, sx, sy, title_fn=None, r=5):
    """series = [(index, pts, name)], drawn back to front; end dot on each line."""
    for idx, pts, _ in series:
        svg.path(polyline(pts, sx, sy), f'line l{idx}')
        svg.circle(sx(pts[-1][0]), sy(pts[-1][1]), 4, f'dot s{idx}')
    if title_fn:
        for idx, pts, name in series:
            hit_points(svg, pts, sx, sy, lambda x, y, n=name: title_fn(n, x, y), r=r)


def signed(v, nd=1):
    """+1.2 / −1.2 with a true minus sign."""
    return f'{v:+.{nd}f}'.replace('-', '−')


def score_pill(svg, cx, y, text, box_cls, text_cls, size=12):
    w = width_of(text, size, 600) + 18
    svg.rect(cx - w / 2, y, w, 22, box_cls, rx=11)
    svg.text(cx, y + 15, text, cls=text_cls, anchor='middle', size=size)


# ----------------------------------------------------------------------------- home page cards
def card_opd(W=380):
    """An answer drawn as a paragraph of word-chips: the student's text, with two passages from the teacher."""
    svg = Svg(W, 126, 'An answer written by the student, with two passages written by the teacher')
    rows = [[34, 18, 46, 26, 40, 22, 30, 38, 20], [28, 44, 20, 32, 48, 36, 26, 30],
            [40, 24, 30, 52, 22, 34, 28, 26], [30, 46, 22, 38]]
    teacher = {(1, 4), (1, 5), (1, 6), (1, 7), (3, 2), (3, 3)}
    labels = {(1, 4): 'Wait,', (3, 2): 'But'}
    x0, gap, y0, pitch = 26, 5, 14, 24
    for r, row in enumerate(rows):
        x, y = x0, y0 + r * pitch
        for c, w in enumerate(row):
            t = (r, c) in teacher
            svg.rect(x, y, w, 10, 'tok-t' if t else 'tok-s', rx=5, extra='' if t else 'opacity=".55"')
            if (r, c) in labels:
                svg.text(x, y - 3.5, labels[(r, c)], cls='t-accent', size=10.5)
            x += w + gap
    ly = y0 + 3 * pitch

    def key(i):
        lx = 204
        for cls, op, lab in [('tok-s', '.55', T('student', '学生')), ('tok-t', '', T('teacher', '老师'))]:
            svg.rect(lx, ly + 1, 14, 8, cls, rx=4, extra=f'opacity="{op}"' if op else '')
            svg.text(lx + 19, ly + 9, lab[i], cls='t-muted', size=11)
            lx += 19 + text_w(lab[i], 11) + 14
    per_lang(svg, key)
    breadcrumb(svg, [T('Teacher data', '老师数据'), T('SFT'), T('Scaffold-OPD'), T('GRPO')], 2, 116)
    return svg


def card_scr(W=380):
    """Two rollouts reach the same state B; the steps taken from B get opposite credit."""
    svg = Svg(W, 126, 'Two rollouts reach the same state B; the steps taken from B get opposite credit')
    A, B = (40, 54), (120, 54)
    up, dn = [(200, 28), (262, 28)], [(200, 80), (262, 80)]
    arrow(svg, A[0] + 11, A[1], B[0] - 14, B[1])
    for path, ok in [(up, True), (dn, False)]:
        (x1, y1), (x2, y2) = path
        ang = math.atan2(y1 - B[1], x1 - B[0])
        arrow(svg, B[0] + 14 * math.cos(ang), B[1] + 14 * math.sin(ang), x1 - 11 * math.cos(ang), y1 - 11 * math.sin(ang))
        arrow(svg, x1 + 11, y1, x2 - 11, y2)
        for (x, y) in path:
            svg.circle(x, y, 10, 'box-soft')
        px = x2 + 20
        svg.rect(px, y2 - 10, 62, 20, 'box-soft', rx=10)
        svg.text(px + 31, y2 + 4, T('success', '成功') if ok else T('fail', '失败'), cls='t-strong' if ok else 't-muted',
                 anchor='middle', size=11)
    for (x, y), cls, sign in [(up[0], 's1', '+'), (dn[0], 's2', '−')]:
        mx, my = (B[0] + x) / 2 + 2, (B[1] + y) / 2
        svg.rect(mx - 9, my - 7, 18, 14, cls, rx=7)
        svg.text(mx, my + 4.2, sign, cls='t-on', anchor='middle', size=12)
    svg.circle(A[0], A[1], 10, 'box-soft')
    svg.text(A[0], A[1] + 4, 'A', cls='t-muted', anchor='middle', size=11)
    svg.circle(B[0], B[1], 17, 'ring', 'opacity=".35"')
    svg.circle(B[0], B[1], 12, 'box-key')
    svg.text(B[0], B[1] + 4, 'B', cls='t-accent', anchor='middle', size=11.5)
    svg.text(B[0], B[1] + 32, T('same state', '同一状态'), cls='t-faint', anchor='middle', size=10.5)
    breadcrumb(svg, [T('Expert demos', '专家示范'), T('SFT'), T('Multi-turn RL', '多轮 RL'), T('Paired eval', '配对评测')], 2, 116)
    return svg


# ----------------------------------------------------------------------------- Scaffold-OPD
def opd_pipeline(W):
    items = [(T('Teacher solutions', '老师解答'), T('14,116 problems', '14,116 道题')),
             (T('Rejection sampling', '拒绝采样'), T('79% kept', '保留 79%')),
             (T('SFT'), T('1 epoch', '1 轮')),
             (T('Scaffold-OPD'), T('40 steps', '40 步')),
             (T('GRPO on failures', '错题回流 GRPO'), T('2,212 problems', '2,212 道题'))]
    p = OPD['pipeline_avg4']
    scores = [T(f'base {p["base"]:.1f}', f'基座 {p["base"]:.1f}'), None, f'{p["sft"]:.1f}', f'{p["takeover_40"]:.1f}', f'{p["grpo_30"]:.1f}']
    key = 3
    label = 'Scaffold-OPD pipeline with the 4-benchmark average after each stage'
    if W >= 500:
        w, gap, h = 126, 17, 68
        x = (W - (5 * w + 4 * gap)) / 2
        svg = Svg(W, 126, label)
        for i, (title, detail) in enumerate(items):
            bx = x + i * (w + gap)
            svg.rect(bx, 6, w, h, 'box-key' if i == key else 'box', rx=10)
            svg.text(bx + 12, 24, f'0{i + 1}', cls='t-accent' if i == key else 't-faint', size=10.5, ls='0.08em')
            svg.text(bx + 12, 44, title, cls='t-strong', size=12.5)
            svg.text(bx + 12, 61, detail, cls='t-muted', size=11)
            if i:
                svg.line(bx - gap + 3, 6 + h / 2, bx - 3, 6 + h / 2, 'arrow')
                chevron(svg, bx - 5, 6 + h / 2, 3.5)
            if scores[i]:
                score_pill(svg, bx + w / 2, 92, scores[i], 'box-fill' if i == key else 'box-soft',
                           't-on' if i == key else ('t-muted' if i == 0 else 't-strong'), 11.5 if i == 0 else 12)
        return svg
    w, h, gap = W - 16, 50, 12
    svg = Svg(W, 6 + 5 * h + 4 * gap + 6, label)
    for i, (title, detail) in enumerate(items):
        y = 6 + i * (h + gap)
        svg.rect(8, y, w, h, 'box-key' if i == key else 'box', rx=10)
        svg.text(22, y + 21, f'0{i + 1}', cls='t-accent' if i == key else 't-faint', size=10.5, ls='0.08em')
        svg.text(48, y + 21, title, cls='t-strong', size=12.5)
        svg.text(48, y + 38, detail, cls='t-muted', size=11)
        if scores[i]:
            pw = width_of(scores[i], 12, 600) + 16
            svg.rect(8 + w - 12 - pw, y + 14, pw, 22, 'box-fill' if i == key else 'box-soft', rx=11)
            svg.text(8 + w - 12 - pw / 2, y + 29, scores[i], cls='t-on' if i == key else ('t-muted' if i == 0 else 't-strong'),
                     anchor='middle', size=12)
        if i:
            chevron(svg, 8 + w / 2, y - gap / 2, 3.5)
    return svg


def opd_takeover(W):
    """Student and teacher lanes: generation moves to the teacher at a reflection point and back, twice at most."""
    narrow = W < 500
    lx, ys, yt = (56, 38, 92) if narrow else (70, 40, 100)
    x_end = W - (30 if narrow else 40)
    span = x_end - lx
    segs = [('s', 0.00, 0.25), ('t', 0.28, 0.45), ('s', 0.48, 0.73), ('t', 0.76, 0.90)]
    by = yt + (44 if narrow else 42)
    H = by + (138 if narrow else 64)
    svg = Svg(W, H, 'Illustration: the teacher takes over at a reflection point, writes a short passage and hands back')
    svg.text(10, ys + 4, T('student', '学生'), cls='t-muted', size=11.5)
    svg.text(10, yt + 4, T('teacher', '老师'), cls='t-accent', size=11.5)
    svg.line(lx, ys, x_end, ys, 'grid')
    svg.line(lx, yt, x_end, yt, 'grid')
    for who, a, b in segs:
        y = ys if who == 's' else yt
        n = max(2, int((b - a) * span / 13))
        cw = (b - a) * span / n
        for i in range(n):
            svg.rect(lx + a * span + i * cw, y - 7, cw - 3, 14, 'tok-t' if who == 't' else 'tok-s', rx=3,
                     extra='' if who == 't' else 'opacity=".7"')
    for f0, f1, down in [(0.25, 0.28, True), (0.45, 0.48, False), (0.73, 0.76, True)]:
        x1, x2 = lx + f0 * span - 2, lx + f1 * span
        ya, yb = (ys + 8, yt - 9) if down else (yt - 8, ys + 9)
        mid = (ys + yt) / 2
        svg.path(f'M{x1:.1f},{ya:.1f} C{x1 + 9:.1f},{mid:.1f} {x2 - 9:.1f},{mid:.1f} {x2:.1f},{yb:.1f}',
                 'line l1' if down else 'line l3', 'stroke-width="1.6"')
    t1, t2, t2e = lx + 0.28 * span, lx + 0.76 * span, lx + 0.90 * span
    svg.text(t1, yt + 25, 'Wait, …', cls='t-accent', size=11.5)
    svg.text(t2, yt + 25, 'But …', cls='t-accent', size=11.5)
    svg.text(t2e + 6, yt + 4, T('end', '结束'), cls='t-faint', size=11)

    def chips(x, y, words, cls, text_cls):
        for wd in words:
            w = text_w(wd, 11.5) + 12
            svg.rect(x, y, w, 18, cls, rx=5)
            svg.text(x + w / 2, y + 13, wd, cls=text_cls, anchor='middle', size=11.5)
            x += w + 4
        return x

    top5 = ['So', 'Then', 'We', 'The', 'Let']
    if not narrow:
        bw = 446
        svg.rect(16, by, bw, 52, 'box-soft', rx=10)
        svg.line(t1 + 1, yt + 31, t1 + 1, by, 'leader')

        def inset(i):
            svg.text(28, by + 20, pick(T('teacher’s next token', '老师的下一个 token'), i), cls='t-faint', size=11)
            chips(28, by + 27, ['Wait'], 'box-fill', 't-on')
            svg.text(158, by + 20, pick(T('student’s top-5', '学生的 top-5'), i), cls='t-faint', size=11)
            xe = chips(158, by + 27, top5, 'box', 't-muted')
            svg.text(xe + 12, by + 20, pick(T('not in top-5', '不在 top-5'), i), cls='t-faint', size=11)
            svg.text(xe + 12, by + 40, pick(T('→ take over', '→ 接管'), i), cls='t-strong', size=12)
        per_lang(svg, inset)
        svg.text(16 + bw + 18, by + 20, T('≤ 3 paragraphs per takeover', '每次接管最多写 3 段'), cls='t-muted', size=11.5)
        svg.text(16 + bw + 18, by + 40, T('≤ 2 takeovers per answer', '每条回答最多接管 2 次'), cls='t-muted', size=11.5)
        return svg
    svg.rect(8, by, W - 16, 86, 'box-soft', rx=10)

    def inset_narrow(i):
        svg.text(20, by + 21, pick(T('teacher’s next token', '老师的下一个 token'), i), cls='t-faint', size=11)
        chips(150, by + 8, ['Wait'], 'box-fill', 't-on')
        svg.text(20, by + 47, pick(T('student’s top-5', '学生的 top-5'), i), cls='t-faint', size=11)
        chips(112 if i == 0 else 104, by + 34, top5, 'box', 't-muted')
        svg.text(20, by + 74, pick(T('not in top-5 → take over', '不在 top-5 → 接管'), i), cls='t-strong', size=12)
    per_lang(svg, inset_narrow)
    svg.text(8, by + 108, T('≤ 3 paragraphs per takeover', '每次接管最多写 3 段'), cls='t-muted', size=11.5)
    svg.text(8, by + 126, T('≤ 2 takeovers per answer', '每条回答最多接管 2 次'), cls='t-muted', size=11.5)
    return svg


def opd_methods(W):
    d = OPD['eval_avg4']
    rows = [(T('Base (Qwen3-1.7B)', '基座（Qwen3-1.7B）'), d['base'], 3, False),
            (T('GRPO, 60 steps', 'GRPO，60 步'), d['grpo_60'], 3, False),
            (T('SFT, one epoch', 'SFT，1 轮'), d['sft'], 3, False),
            (T('OPD, 40 steps', 'OPD，40 步'), d['opd_40'], 2, False),
            (T('Scaffold-OPD, 40 steps', 'Scaffold-OPD，40 步'), d['takeover_conclude_40'], 1, True),
            (T('without concluding trigger', '关闭收尾触发'), d['takeover_40'], 1, False)]
    narrow = W < 500
    pitch, bh = (44, 14) if narrow else (34, 16)
    x0 = 8 if narrow else 214
    x1 = W - (58 if narrow else 96)
    top = 22
    svg = Svg(W, top + pitch * len(rows) + 24, '4-benchmark math average by post-training method')
    sx = scale(0, 50, x0, x1)
    y_end = top + pitch * len(rows) - 6
    for v in range(0, 51, 10):
        svg.line(sx(v), top - 6, sx(v), y_end, 'grid' if v else 'axis')
        svg.text(sx(v), y_end + 16, str(v), cls='t-faint', anchor='middle', size=11)
    svg.line(sx(d['base']), top - 10, sx(d['base']), y_end, 'leader', 'opacity=".55"')
    svg.text(sx(d['base']), top - 13, T('base', '基座'), cls='t-faint', anchor='middle', size=10.5)
    ys = []
    for i, (lab, v, idx, strong) in enumerate(rows):
        yb = top + i * pitch + (20 if narrow else (pitch - bh) / 2 - 2)
        ys.append(yb)
        cls = 't-strong' if strong else ('t-muted' if i == 5 else '')
        if narrow:
            svg.text(x0, yb - 6, lab, cls=cls, size=12)
        else:
            svg.text(x0 - 12, yb + bh / 2 + 4.2, lab, cls=cls, anchor='end', size=12.5)
        op = ' opacity=".55"' if i == 5 else ''
        svg.mark(f'{lab[0]}: {v:.2f}', f'<path class="bar s{idx}" d="{hbar(x0, yb, sx(v), bh)}"{op}/>')
        svg.text(sx(v) + 6, yb + bh / 2 + 4.2, f'{v:.1f}', cls='t-strong' if strong else '', size=12)
    xb = sx(d['takeover_conclude_40']) + (34 if narrow else 40)
    yo, yt = ys[3] + bh / 2, ys[4] + bh / 2
    svg.path(f'M{xb - 5:.1f},{yo:.1f} H{xb:.1f} V{yt:.1f} H{xb - 5:.1f}', 'leader')
    svg.text(xb + 6, (yo + yt) / 2 + 4, f'+{d["takeover_conclude_40"] - d["opd_40"]:.1f}', cls='t-accent', size=12)
    return svg


def opd_budget(W):
    """Top: accuracy against the token budget. Bottom: the paired gap with a ±1 SE band; it crosses zero near 8k."""
    b = OPD['budget']
    xs = [math.log2(t) for t in b['tokens']]
    tk, op, gap, se = b['takeover_40'], b['opd_40'], b['gap_40'], b['gap_se_40']
    narrow = W < 500
    right = 64 if narrow else 150
    H = 444 if narrow else 430
    top = (40, 52, W - right, 230)
    bot = (40, 292, W - right, H - 44)
    svg = Svg(W, H, 'Accuracy against the evaluation token budget, and the Scaffold-OPD minus OPD gap with one standard error')
    legend(svg, top[0], 16, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    sx = scale(10, 15, top[0], top[2])
    syA = scale(0, 50, top[3], top[1])
    panel_title(svg, top[0], top[1] - 16, T('Accuracy', '准确率'), T('4-benchmark average', '4 项平均'))
    y_axis(svg, top, syA, [0, 10, 20, 30, 40, 50])
    for t in (13, 14, 15):
        svg.line(sx(t), top[1], sx(t), top[3], 'grid')
        svg.line(sx(t), bot[1], sx(t), bot[3], 'grid')
    gap_wash(svg, xs, tk, op, sx, syA)
    series_lines(svg, [(2, list(zip(xs, op)), 'OPD'), (1, list(zip(xs, tk)), 'Scaffold-OPD')], sx, syA,
                 lambda n, x, y: f'{n} · {int(round(2 ** x)):,} tokens: {y:.1f}')
    end_labels(svg, [(sx(15) + 9, syA(tk[-1]), f'{tk[-1]:.1f}' if narrow else f'Scaffold-OPD {tk[-1]:.1f}', 't-strong'),
                     (sx(15) + 9, syA(op[-1]), f'{op[-1]:.1f}' if narrow else f'OPD {op[-1]:.1f}', '')])
    if not narrow:
        fin = b['aime_finished_opd_40'][xs.index(14)]
        svg.text(sx(15), syA(23), T('At 16k, OPD has already finished', '16k 时 OPD 已经写完'), cls='t-faint', anchor='end', size=11)
        svg.text(sx(15), syA(23) + 15, T(f'{fin:.0f}% of its AIME answers', f'{fin:.0f}% 的 AIME 回答'), cls='t-faint', anchor='end', size=11)
    syB = scale(-5, 8, bot[3], bot[1])
    panel_title(svg, bot[0], bot[1] - 16, T('Gap: Scaffold-OPD − OPD', '差距：Scaffold-OPD − OPD'), T('± 1 standard error', '± 1 个标准误'))
    y_axis(svg, bot, syB, [-4, 0, 4, 8], fmt=lambda v: signed(v, 0) if v else '0')
    upper = ' L'.join(f'{sx(x):.1f},{syB(g + s):.1f}' for x, g, s in zip(xs, gap, se))
    lower = ' L'.join(f'{sx(x):.1f},{syB(g - s):.1f}' for x, g, s in reversed(list(zip(xs, gap, se))))
    svg.path(f'M{upper} L{lower} Z', 'wash1')
    svg.line(bot[0], syB(0), bot[2], syB(0), 'axis')
    pts = list(zip(xs, gap))
    svg.path(polyline(pts, sx, syB), 'line l1')
    hit_points(svg, pts, sx, syB, lambda x, y: f'{int(round(2 ** x)):,} tokens: {signed(y, 2)} ± {se[xs.index(x)]:.2f}', r=5)
    for t in (13, 14, 15):
        i = xs.index(t)
        svg.circle(sx(t), syB(gap[i]), 4, 'dot s1')
        svg.text(sx(t), syB(gap[i] + se[i]) - 8, signed(gap[i]), cls='t-strong', anchor='middle', size=11.5)
    x_axis(svg, bot, sx, [10, 11, 12, 13, 14, 15], fmt=lambda v: f'{int(2 ** v / 1024)}k')
    svg.text(bot[2], bot[3] + 32, T('evaluation budget (tokens)', '评测预算（token）'), cls='t-faint', anchor='end', size=11)
    return svg


def opd_training(W):
    tr = OPD['train']
    tk = moving_avg([(s, l) for s, l in zip(tr['takeover']['step'], tr['takeover']['response_length']) if s != 19])
    op = moving_avg(list(zip(tr['opd']['step'], tr['opd']['response_length'])))
    ratio = moving_avg([(s, 100 * r) for s, r in zip(tr['takeover']['step'], tr['takeover']['teacher_token_ratio']) if s != 19])
    tt = [(s, v) for s, v in zip(tr['takeover']['step'], tr['takeover']['teacher_tokens_per_answer']) if v is not None and s != 19]
    first = sum(v for s, v in tt if s <= 5) / sum(1 for s, v in tt if s <= 5)
    last = sum(v for s, v in tt if s >= 56) / sum(1 for s, v in tt if s >= 56)
    narrow = W < 500
    if narrow:
        H = 480
        bA, bB = (44, 62, W - 70, 212), (44, 304, W - 70, 448)
    else:
        H = 292
        bA, bB = (46, 62, W / 2 - 78, H - 40), (W / 2 + 44, 62, W - 62, H - 40)
    svg = Svg(W, H, 'Training dynamics: response length and the share of tokens written by the teacher')
    legend(svg, bA[0], 16, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    sxA, syA = scale(0, 60, bA[0], bA[2]), scale(0, 6000, bA[3], bA[1])
    panel_title(svg, bA[0], bA[1] - 16, T('Response length', '回答长度'), T('tokens', 'token'))
    y_axis(svg, bA, syA, [0, 2000, 4000, 6000], fmt=lambda v: f'{v / 1000:.0f}k' if v else '0')
    x_axis(svg, bA, sxA, [0, 20, 40, 60], title=T('step', '步'))
    series_lines(svg, [(2, op, 'OPD'), (1, tk, 'Scaffold-OPD')], sxA, syA, lambda n, x, y: f'{n} · step {x}: {y:,.0f} tokens')
    end_labels(svg, [(sxA(60) + 8, syA(tk[-1][1]), f'{tk[-1][1]:,.0f}', 't-strong'), (sxA(60) + 8, syA(op[-1][1]), f'{op[-1][1]:,.0f}', '')])
    sxB, syB = scale(0, 60, bB[0], bB[2]), scale(0, 20, bB[3], bB[1])
    panel_title(svg, bB[0], bB[1] - 16, T('Teacher-token share', '老师 token 占比'), T('Scaffold-OPD, %', 'Scaffold-OPD，%'))
    y_axis(svg, bB, syB, [0, 5, 10, 15, 20])
    x_axis(svg, bB, sxB, [0, 20, 40, 60], title=T('step', '步'))
    area = polyline(ratio, sxB, syB) + f' L{sxB(ratio[-1][0]):.1f},{syB(0):.1f} L{sxB(ratio[0][0]):.1f},{syB(0):.1f} Z'
    svg.path(area, 'wash1')
    series_lines(svg, [(1, ratio, 'share')], sxB, syB, lambda n, x, y: f'step {x}: {y:.1f}%')
    svg.text(sxB(60) + 8, syB(ratio[-1][1]) + 4, f'{ratio[-1][1]:.1f}%', cls='t-strong', size=12)
    svg.text(bB[2], bB[1] + 14, T('teacher tokens per answer', '每条回答中老师写的 token'), cls='t-faint', anchor='end', size=11)
    svg.text(bB[2], bB[1] + 32, f'≈ {round(first, -1):.0f} → {round(last, -1):.0f}', cls='t-strong', anchor='end', size=12)
    return svg


def opd_compute(W):
    """Score against cumulative training GPU-hours: the full pipeline ends level with Scaffold-OPD alone at ~4x the cost."""
    narrow = W < 500
    H = 326
    box = (44, 52, W - (24 if narrow else 150), H - 42)
    svg = Svg(W, H, 'Score against cumulative training GPU-hours: the full pipeline and Scaffold-OPD alone')
    legend(svg, box[0], 18, [(2, T('full pipeline', '全流程')), (1, T('Scaffold-OPD alone', '只做 Scaffold-OPD'))])
    sx, sy = scale(0, 56, box[0], box[2]), scale(20, 50, box[3], box[1])
    y_axis(svg, box, sy, [20, 30, 40, 50])
    x_axis(svg, box, sx, [0, 10, 20, 30, 40, 50])
    svg.text(box[2], box[3] + 32, T('cumulative training GPU-hours (2 × A100)', '累计训练卡时（2 × A100）'), cls='t-faint', anchor='end', size=11)
    svg.text(box[0] - 36, box[1] - 14, T('4-benchmark average', '4 项平均'), cls='t-faint', size=11)
    g, p = OPD['gpu_hours']['pipeline'], OPD['pipeline_avg4']
    c1 = g['sft_incl_teacher_data']
    c2 = c1 + g['takeover_40']
    c3 = c2 + g['grpo_30']
    pts = [(0, p['base']), (c1, p['sft']), (c2, p['takeover_40']), (c3, p['grpo_30'])]
    alone = (OPD['gpu_hours']['takeover_40'], OPD['eval_avg4']['takeover_40'])
    svg.line(sx(alone[0]) + 8, sy(alone[1]), sx(c3) - 8, sy(alone[1]), 'leader', 'stroke-dasharray="3 3"')
    svg.path(polyline(pts, sx, sy), 'line l2')
    svg.line(sx(0), sy(p['base']), sx(alone[0]), sy(alone[1]), 'line l1')
    names = [T('base', '基座'), T('+ SFT'), T('+ Scaffold-OPD'), T('+ GRPO')]
    for k, ((x, y), lab) in enumerate(zip(pts, names)):
        svg.mark(f'{lab[0]}: {y:.2f} after {x:.1f} GPU-hours', f'<circle class="dot s2" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4.5"/>')
        text = (f'{lab[0]} {y:.1f}', f'{lab[1]} {y:.1f}')
        if k == 0:
            svg.text(sx(x) + 8, sy(y) + 16, text, cls='t-muted', size=11.5)
        elif k == 3:
            if narrow:
                svg.text(sx(x), sy(y) - 11, text, anchor='end', size=11.5)
            else:
                svg.text(sx(x) + 8, sy(y) - 9, text, size=11.5)
        else:
            svg.text(sx(x) + 8, sy(y) + 18, text, size=11.5)
    svg.mark(f'Scaffold-OPD alone: {alone[1]:.2f} after {alone[0]:.1f} GPU-hours',
             f'<circle class="dot s1" cx="{sx(alone[0]):.1f}" cy="{sy(alone[1]):.1f}" r="5.5"/>')
    if narrow:
        svg.text(sx(alone[0]) + 10, sy(alone[1]) + 18, f'{alone[1]:.1f}', cls='t-accent', size=11.5)
        svg.text(box[2], sy(30), T('same score,', '分数相同，'), cls='t-strong', anchor='end', size=12)
        svg.text(box[2], sy(30) + 17, T(f'≈ {c3 / alone[0]:.0f}× the GPU-hours', f'卡时约 {c3 / alone[0]:.0f} 倍'), cls='t-strong', anchor='end', size=12)
    else:
        svg.text(sx(alone[0]) + 10, sy(alone[1]) + 18, T(f'Scaffold-OPD alone {alone[1]:.1f}', f'只做 Scaffold-OPD {alone[1]:.1f}'), cls='t-accent', size=11.5)
        svg.text((sx(alone[0]) + sx(c3)) / 2, sy(alone[1]) - 8, T(f'same score, about {c3 / alone[0]:.0f}× the GPU-hours', f'分数相同，卡时约 {c3 / alone[0]:.0f} 倍'),
                 cls='t-strong', anchor='middle', size=12)
    return svg


# ----------------------------------------------------------------------------- StepCredit-RL
def scr_pipeline(W):
    """Stage cards with the model's ALFWorld success built in as micro-bars."""
    stages = [(T('Base model', '基座模型'), T('before training', '训练前'), (7.1, 2.2)),
              (T('Expert SFT', '专家 SFT'), T('22,810 examples · 1 epoch', '22,810 条样本 · 1 轮'), (67.1, 67.2)),
              (T('Multi-turn RL', '多轮 RL'), T('StepCredit-RL · 100 steps', 'StepCredit-RL · 100 步'), (98.6, 94.0)),
              (T('Paired eval', '配对评测'), T('per-task results', '记录每个任务的结果'), None)]
    key = 2
    label = 'StepCredit-RL pipeline with ALFWorld success (seen and unseen) after each stage'
    if W >= 500:
        w, gap, h, y0 = 163, 21, 100, 30
        x = (W - (4 * w + 3 * gap)) / 2
        svg = Svg(W, y0 + h + 6, label)
        chip_legend(svg, x, 15, [('s1', 'seen'), ('s2', 'unseen')], size=11)
        for i, (title, detail, sc) in enumerate(stages):
            bx = x + i * (w + gap)
            svg.rect(bx, y0, w, h, 'box-key' if i == key else 'box', rx=10)
            svg.text(bx + 12, y0 + 22, title, cls='t-strong', size=12.5)
            svg.text(bx + 12, y0 + 39, detail, cls='t-muted', size=11)
            if sc:
                for j, (v, idx, nm) in enumerate([(sc[0], 1, 'seen'), (sc[1], 2, 'unseen')]):
                    yb = y0 + 58 + j * 18
                    tw = w - 24 - 34
                    svg.rect(bx + 12, yb, tw, 8, 'band', rx=4)
                    svg.mark(f'{title[0]} · {nm}: {v:.1f}%', f'<path class="bar s{idx}" d="{hbar(bx + 12, yb, bx + 12 + tw * v / 100, 8, 4)}"/>')
                    svg.text(bx + w - 12, yb + 8, f'{v:.1f}', cls='t-strong' if i == key else '', anchor='end', size=11)
            else:
                svg.text(bx + 12, y0 + 66, T('exact McNemar test', '精确 McNemar 检验'), size=11.5)
                svg.text(bx + 12, y0 + 84, T('two runs, same tasks', '两次运行、同一批任务'), cls='t-faint', size=11)
            if i:
                svg.line(bx - gap + 3, y0 + h / 2, bx - 3, y0 + h / 2, 'arrow')
                chevron(svg, bx - 5, y0 + h / 2, 3.5)
        return svg
    h, gap = 76, 10
    svg = Svg(W, 30 + 4 * h + 3 * gap, label)
    chip_legend(svg, 8, 16, [('s1', 'seen'), ('s2', 'unseen')], size=11)
    for i, (title, detail, sc) in enumerate(stages):
        y = 26 + i * (h + gap)
        svg.rect(8, y, W - 16, h, 'box-key' if i == key else 'box', rx=10)
        svg.text(20, y + 21, title, cls='t-strong', size=12.5)
        svg.text(20, y + 38, detail, cls='t-muted', size=11)
        if sc:
            for j, (v, idx, nm) in enumerate([(sc[0], 1, 'seen'), (sc[1], 2, 'unseen')]):
                yb = y + 48 + j * 12
                svg.rect(20, yb, W - 80, 7, 'band', rx=3.5)
                svg.mark(f'{title[0]} · {nm}: {v:.1f}%', f'<path class="bar s{idx}" d="{hbar(20, yb, 20 + (W - 80) * v / 100, 7, 3.5)}"/>')
                svg.text(W - 20, yb + 7, f'{v:.1f}', anchor='end', size=11, cls='t-strong' if i == key else '')
        else:
            svg.text(20, y + 60, T('exact McNemar test · two runs, same tasks', '精确 McNemar 检验 · 两次运行、同一批任务'), size=11.5)
        if i:
            chevron(svg, W / 2, y - gap / 2, 3.5)
    return svg


def scr_steplevel(W):
    narrow = W < 500
    rows = [(['A', 'B', 'C', 'D'], True), (['A', 'E', 'B', 'F'], False), (['A', 'B', 'G'], True)]
    if narrow:
        colx, rowy, H = [36, 98, 160, 222], [34, 88, 142], 288
    else:
        colx, rowy, H = [52, 140, 228, 316], [40, 98, 156], 196
    svg = Svg(W, H, 'Steps that start from the same environment state are compared across rollouts')
    bpos = []
    for r, (states, ok) in enumerate(rows):
        y = rowy[r]
        svg.text(colx[0] - 28, y + 4, f'#{r + 1}', cls='t-faint', anchor='middle', size=11)
        for c, s in enumerate(states):
            x = colx[c]
            k = s == 'B'
            if c:
                arrow(svg, colx[c - 1] + 15, y, x - 16, y)
            svg.circle(x, y, 14, 'box-key' if k else 'box-soft')
            svg.text(x, y + 4.3, s, cls='t-accent' if k else 't-muted', anchor='middle', size=12)
            if k:
                bpos.append((x, y))
        ex = colx[len(states) - 1] + 26
        svg.rect(ex, y - 11, 64, 22, 'box-soft', rx=11)
        svg.text(ex + 32, y + 4, T('success', '成功') if ok else T('fail', '失败'), cls='t-strong' if ok else 't-muted', anchor='middle', size=11.5)
    for (xa, ya), (xb, yb) in zip(bpos, bpos[1:]):
        svg.path(f'M{xa:.1f},{ya + 14:.1f} C{xa:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{yb - 14:.1f}',
                 'line l1', 'opacity=".45" stroke-width="1.5"')
    if narrow:
        ty = 196
        svg.line(12, ty - 16, W - 12, ty - 16, 'grid')

        def text(i):
            svg.text(12, ty, pick(T('Episode level', '整局'), i), cls='t-strong', size=12.5)
            tx = 104 if i == 0 else 60
            svg.text(tx, ty, pick(T('compare the outcomes of #1–#3', '比较 #1–#3 的最终成败'), i), size=12)
            svg.text(12, ty + 24, pick(T('Step level', '步级'), i), cls='t-strong', size=12.5)
            svg.text(tx, ty + 24, pick(T('compare the steps taken from B', '比较从 B 出发的各步'), i), size=12)
            svg.text(tx, ty + 42, pick(T('by what followed them', '按各自之后的结果'), i), cls='t-muted', size=12)
            svg.text(12, ty + 70, pick(T('No critic, no extra rollouts.', '无需 critic，也无需额外 rollout。'), i), cls='t-faint', size=11.5)
        per_lang(svg, text)
        return svg
    tx = 492
    svg.line(tx - 22, 26, tx - 22, 170, 'grid')
    svg.text(tx, 46, T('Episode level', '整局'), cls='t-strong', size=13)
    svg.text(tx, 65, T('compare the outcomes of #1–#3', '比较 #1–#3 的最终成败'), size=12)
    svg.text(tx, 104, T('Step level', '步级'), cls='t-strong', size=13)
    svg.text(tx, 123, T('compare the steps taken from B', '比较从 B 出发的各步'), size=12)
    svg.text(tx, 140, T('(B→C, B→F, B→G) by what followed', '（B→C、B→F、B→G）之后的结果'), cls='t-muted', size=12)
    svg.text(tx, 172, T('No critic, no extra rollouts.', '无需 critic，也无需额外 rollout。'), cls='t-faint', size=11.5)
    return svg


FAM_NAMES = {'look_at_obj_in_light': T('Look in light', '灯下查看'), 'pick_and_place': T('Pick & place', '拿取放置'),
             'pick_clean_then_place': T('Clean & place', '清洗后放置'), 'pick_cool_then_place': T('Cool & place', '冷却后放置'),
             'pick_heat_then_place': T('Heat & place', '加热后放置'), 'pick_two_obj_and_place': T('Two objects', '双物体')}
FAM_ORDER = ['pick_two_obj_and_place', 'pick_clean_then_place', 'pick_heat_then_place', 'look_at_obj_in_light',
             'pick_cool_then_place', 'pick_and_place']


def family_counts(run_name, split):
    return {r['family']: (int(r['solved']), int(r['total'])) for r in FAMILY if r['run'] == run_name and r['split'] == split}


def scr_sft_rl(W):
    """Dumbbells by task family: after SFT → after SFT + 100 RL steps. The family the expert rarely solves gains most."""
    narrow = W < 500
    if narrow:
        H = 480
        panels = [('seen', (100, 64, W - 44, 224)), ('unseen', (100, 300, W - 44, 460))]
    else:
        H = 276
        panels = [('seen', (130, 62, W / 2 - 34, H - 34)), ('unseen', (W / 2 + 104, 62, W - 34, H - 34))]
    svg = Svg(W, H, 'ALFWorld success by task family, after SFT and after 100 more steps of RL')
    chip_legend(svg, 14 if not narrow else 8, 18, [('s3', T('after SFT', 'SFT 后')), ('s1', T('after SFT + 100 RL steps', 'SFT + 100 步 RL 后'))])
    for split, box in panels:
        a, b = family_counts('sft', split), family_counts('sft_gigpo_step100', split)
        sx = scale(0, 100, box[0], box[2])
        panel_title(svg, box[0], box[1] - 16, f'valid_{split}', T('success, %', '成功率，%'))
        for v in (0, 50, 100):
            svg.line(sx(v), box[1] - 4, sx(v), box[3] - 6, 'grid' if v else 'axis')
            svg.text(sx(v), box[3] + 10, str(v), cls='t-faint', anchor='middle', size=10.5)
        pitch = (box[3] - box[1]) / len(FAM_ORDER)
        for i, fam in enumerate(FAM_ORDER):
            y = box[1] + i * pitch + pitch / 2 - 4
            k = fam == 'pick_two_obj_and_place'
            (sa, n), (sb, _) = a[fam], b[fam]
            pa, pb = 100 * sa / n, 100 * sb / n
            svg.text(box[0] - 10, y + 4, FAM_NAMES[fam], cls='t-strong' if k else '', anchor='end', size=11.5)
            svg.line(sx(pa), y, sx(pb), y, 'line l1' if k else 'line l3', 'stroke-width="2.5"' + ('' if k else ' opacity=".6"'))
            svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sa}/{n} after SFT → {sb}/{n} after RL',
                     f'<circle class="dot s3" cx="{sx(pa):.1f}" cy="{y:.1f}" r="4.5"/><circle class="dot s1" cx="{sx(pb):.1f}" cy="{y:.1f}" r="5"/>')
            if k:
                svg.text(sx(pa) - 9, y + 4, f'{sa}/{n}', cls='t-muted', anchor='end', size=11)
                svg.text(sx(pb) + 9, y + 4, f'{sb}/{n}', cls='t-strong', size=11)
    return svg


def scr_vs_grpo(W):
    """Validation curves with the late-stage band, and the McNemar discordant pairs at step 200."""
    narrow = W < 500
    g = {k: run(ALF, 'gigpo', k) for k in ('seen', 'unseen')}
    r = {k: run(ALF, 'grpo', k) for k in ('seen', 'unseen')}
    if narrow:
        H = 584
        boxes = {'seen': (40, 66, W - 64, 226), 'unseen': (40, 352, W - 64, 512)}
        bar_y = {'seen': 270, 'unseen': 556}
    else:
        H = 346
        boxes = {'seen': (40, 66, W / 2 - 60, 262), 'unseen': (W / 2 + 44, 66, W - 58, 262)}
        bar_y = {'seen': 314, 'unseen': 314}
    svg = Svg(W, H, 'ALFWorld validation success over 200 steps, StepCredit-RL vs GRPO, and tasks solved by only one run at step 200')
    legend(svg, 40, 16, [(1, 'StepCredit-RL'), (2, 'GRPO')])
    disc = {k: PAIRED[f'alfworld_steplevel_vs_grpo:valid_{k}'] for k in ('seen', 'unseen')}
    most = max(int(p['only_a']) + int(p['only_b']) for p in disc.values())
    for name, box in boxes.items():
        sx, sy = scale(0, 200, box[0], box[2]), scale(0, 100, box[3], box[1])
        panel_title(svg, box[0], box[1] - 20, f'valid_{name}', T('success, %', '成功率，%'))
        svg.rect(sx(160), box[1], sx(200) - sx(160), box[3] - box[1], 'band')
        late_g = sum(v for s, v in g[name] if s >= 160) / 5
        late_r = sum(v for s, v in r[name] if s >= 160) / 5
        svg.text((sx(160) + sx(200)) / 2, box[1] + 13, f'{late_g:.1f} vs {late_r:.1f}', cls='t-muted', anchor='middle', size=10.5)
        y_axis(svg, box, sy, [0, 25, 50, 75, 100])
        x_axis(svg, box, sx, [0, 50, 100, 150, 200])
        gap_wash(svg, [s for s, _ in g[name]], [v for _, v in g[name]], [v for _, v in r[name]], sx, sy)
        series_lines(svg, [(2, r[name], 'GRPO'), (1, g[name], 'StepCredit-RL')], sx, sy, lambda n, x, y: f'{n} · step {x}: {y:.1f}%')
        end_labels(svg, [(sx(200) + 8, sy(g[name][-1][1]), f'{g[name][-1][1]:.1f}', 't-strong'),
                         (sx(200) + 8, sy(r[name][-1][1]), f'{r[name][-1][1]:.1f}', '')], min_gap=14)
        p = disc[name]
        a_, b_, pv = int(p['only_a']), int(p['only_b']), float(p['p'])
        by = bar_y[name]
        unit = (box[2] - box[0]) / most
        svg.text(box[0], by - 8, T('solved by only one run at step 200', '第 200 步只有一方解出'), cls='t-muted', size=11)
        svg.text(box[2], by - 8, f'p = {pv:.3f}' if pv < 0.1 else f'p = {pv:.2f}', cls='t-accent' if pv < 0.05 else 't-muted', anchor='end', size=11.5)
        wa, wb = a_ * unit, b_ * unit
        svg.mark(f'{name}: only StepCredit-RL {a_}, only GRPO {b_}, McNemar p = {pv}',
                 f'<rect class="s1" x="{box[0]:.1f}" y="{by:.1f}" width="{wa - 1.5:.1f}" height="16" rx="3"/>'
                 f'<rect class="s2" x="{box[0] + wa + 1.5:.1f}" y="{by:.1f}" width="{wb - 1.5:.1f}" height="16" rx="3"/>')
        svg.text(box[0] + wa / 2, by + 12, str(a_), cls='t-on', anchor='middle', size=11)
        svg.text(box[0] + wa + 1.5 + wb / 2, by + 12, str(b_), cls='t-on', anchor='middle', size=11)
    return svg


def scr_updates(W):
    """The same comparison by training step and by wall-clock hours."""
    narrow = W < 500
    four = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo_4upd']
    one = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo' and int(x['step']) <= 150]
    if narrow:
        H = 538
        bA, bB = (40, 82, W - 64, 240), (40, 336, W - 64, 494)
    else:
        H = 316
        bA, bB = (40, 82, W / 2 - 60, H - 40), (W / 2 + 44, 82, W - 64, H - 40)
    svg = Svg(W, H, 'Seen success with one vs four updates per step, by training step and by wall-clock hours')
    legend(svg, 40, 16, [(1, T('4 updates per step', '每步 4 次更新')), (2, T('1 update per step', '每步 1 次更新'))])
    for box, key, xmax, ticks, title, unit in [(bA, 0, 150, [0, 50, 100, 150], T('By training step', '按训练步'), T('step', '步')),
                                               (bB, 2, 30, [0, 10, 20, 30], T('By wall-clock time', '按耗时'), T('hours', '小时'))]:
        sx, sy = scale(0, xmax, box[0], box[2]), scale(0, 100, box[3], box[1])
        panel_title(svg, box[0], box[1] - 26, title, T('seen success, %', 'seen 成功率，%'))
        y_axis(svg, box, sy, [0, 25, 50, 75, 100])
        x_axis(svg, box, sx, ticks, title=unit)
        pf = [(d[key], d[1]) for d in four]
        po = [(d[key], d[1]) for d in one]
        fmt = (lambda x: f'step {x:.0f}') if key == 0 else (lambda x: f'{x:.1f} h')
        series_lines(svg, [(2, po, '1 update'), (1, pf, '4 updates')], sx, sy, lambda n, x, y: f'{n} · {fmt(x)}: {y:.1f}%')
        end_labels(svg, [(sx(pf[-1][0]) + 8, sy(pf[-1][1]), f'{pf[-1][1]:.1f}', 't-strong'), (sx(po[-1][0]) + 8, sy(po[-1][1]), f'{po[-1][1]:.1f}', '')])
        if key == 0:
            ya = sy(max(pf[-1][1], po[-1][1])) - 16
            svg.path(f'M{sx(100):.1f},{ya + 6:.1f} V{ya:.1f} H{sx(150):.1f} V{ya + 6:.1f}', 'leader')
            svg.text((sx(100) + sx(150)) / 2, ya - 6, T('same level: step 100 vs 150', '水平相当：第 100 步对第 150 步'), cls='t-muted', anchor='middle', size=11)
        else:
            svg.text(sx(pf[-1][0]), sy(pf[-1][1]) - 12, T('step 100', '第 100 步'), cls='t-faint', anchor='middle', size=10.5)
            svg.text(sx(po[-1][0]), sy(po[-1][1]) - 12, T('step 150', '第 150 步'), cls='t-faint', anchor='middle', size=10.5)
    return svg


def scr_hotpotqa(W):
    narrow = W < 500
    em_em, em_sh = run(HPQ, 'em', 'em'), run(HPQ, 'shaped', 'em')
    rq_em, rq_sh = run(HPQ, 'em', 'repeat_queries'), run(HPQ, 'shaped', 'repeat_queries')
    p = PAIRED['hotpotqa_em_vs_shaped:all']
    if narrow:
        H = 514
        bA, bB = (44, 70, W - 64, 230), (44, 318, W - 64, 470)
    else:
        H = 300
        bA, bB = (44, 70, W / 2 - 64, H - 40), (W / 2 + 46, 70, W - 64, H - 40)
    svg = Svg(W, H, 'HotpotQA: exact match and repeated queries per question, EM reward vs shaped reward')
    legend(svg, bA[0], 16, [(1, T('EM reward', 'EM 奖励')), (2, T('shaped reward', '稠密奖励'))])
    sxA, syA = scale(0, 200, bA[0], bA[2]), scale(40, 60, bA[3], bA[1])
    panel_title(svg, bA[0], bA[1] - 20, T('Exact match', 'EM'), '%')
    y_axis(svg, bA, syA, [40, 45, 50, 55, 60])
    x_axis(svg, bA, sxA, [0, 100, 200], title=T('step', '步'))
    gap_wash(svg, [s for s, _ in em_em], [v for _, v in em_em], [v for _, v in em_sh], sxA, syA)
    series_lines(svg, [(2, em_sh, 'shaped'), (1, em_em, 'EM reward')], sxA, syA, lambda n, x, y: f'{n} · step {x}: {y:.1f}%')
    end_labels(svg, [(sxA(200) + 8, syA(em_em[-1][1]), f'{em_em[-1][1]:.1f}', 't-strong'), (sxA(200) + 8, syA(em_sh[-1][1]), f'{em_sh[-1][1]:.1f}', '')])
    svg.text(bA[2], syA(42), T(f'step 200: McNemar p = {float(p["p"]):.2f}', f'第 200 步：McNemar p = {float(p["p"]):.2f}'), cls='t-faint', anchor='end', size=11)
    sxB, syB = scale(0, 200, bB[0], bB[2]), scale(0, 0.2, bB[3], bB[1])
    panel_title(svg, bB[0], bB[1] - 20, T('Repeated queries', '重复查询'), T('per question', '每题'))
    y_axis(svg, bB, syB, [0, 0.05, 0.1, 0.15, 0.2], fmt=lambda v: f'{v:.2f}' if v else '0')
    x_axis(svg, bB, sxB, [0, 100, 200], title=T('step', '步'))
    series_lines(svg, [(2, rq_sh, 'shaped'), (1, rq_em, 'EM reward')], sxB, syB, lambda n, x, y: f'{n} · step {x}: {y:.3f}')
    end_labels(svg, [(sxB(200) + 8, syB(rq_em[-1][1]), f'{rq_em[-1][1]:.3f}', ''), (sxB(200) + 8, syB(rq_sh[-1][1]), f'{rq_sh[-1][1]:.3f}', 't-strong')])
    ya, yb = syB(rq_em[-1][1]), syB(rq_sh[-1][1])
    xl = sxB(200) - 6
    svg.line(xl, ya + 7, xl, yb - 7, 'leader')
    svg.text(xl - 6, (ya + yb) / 2 + 4, signed(100 * (rq_sh[-1][1] - rq_em[-1][1]) / rq_em[-1][1], 0) + '%', cls='t-strong', anchor='end', size=12)
    return svg


# ----------------------------------------------------------------------------- data tables under the figures
def fmt1(v):
    return f'{v:.1f}'


def opd_budget_table():
    b = OPD['budget']
    rows = [[f'{t:,}', fmt1(o), fmt1(r), f'{signed(g, 2)} ± {s:.2f}'] for t, o, r, g, s in
            zip(b['tokens'], b['opd_40'], b['takeover_40'], b['gap_40'], b['gap_se_40'])]
    return data_table([bi(T('Budget (tokens)', '预算（token）')), 'OPD', 'Scaffold-OPD', bi(T('Paired gap', '配对差'))], rows)


def opd_training_table():
    tr = OPD['train']
    t = dict(zip(tr['takeover']['step'], zip(tr['takeover']['response_length'], tr['takeover']['teacher_token_ratio'])))
    o = dict(zip(tr['opd']['step'], tr['opd']['response_length']))
    rows = []
    for s in range(5, 61, 5):
        tl, ratio = t[s]
        rows.append([str(s), f'{tl:,.0f}', f'{o[s]:,.0f}', f'{100 * ratio:.1f}%'])
    return data_table([bi(T('Step', '步')), bi(T('Scaffold-OPD length', 'Scaffold-OPD 长度')), bi(T('OPD length', 'OPD 长度')),
                       bi(T('Teacher-token share', '老师 token 占比'))], rows,
                      summary=T('Data (raw values every 5 steps)', '数据（每 5 步的原始值）'))


def opd_compute_table():
    g, p = OPD['gpu_hours']['pipeline'], OPD['pipeline_avg4']
    rows = [[bi(T('Base', '基座')), '0', fmt1(p['base'])],
            [bi(T('+ SFT (incl. teacher solutions)', '+ SFT（含老师解答生成）')), fmt1(g['sft_incl_teacher_data']), fmt1(p['sft'])],
            [bi(T('+ Scaffold-OPD, 40 steps', '+ Scaffold-OPD，40 步')), fmt1(g['sft_incl_teacher_data'] + g['takeover_40']), fmt1(p['takeover_40'])],
            [bi(T('+ GRPO on failures, 30 steps', '+ 错题回流 GRPO，30 步')), fmt1(g['sft_incl_teacher_data'] + g['takeover_40'] + g['grpo_30']), fmt1(p['grpo_30'])],
            [bi(T('Scaffold-OPD alone, 40 steps', '只做 Scaffold-OPD，40 步')), fmt1(OPD['gpu_hours']['takeover_40']), fmt1(OPD['eval_avg4']['takeover_40'])]]
    return data_table([bi(T('Route', '路线')), bi(T('Cumulative GPU-h', '累计卡时')), bi(T('Average', '平均'))], rows)


def scr_sft_rl_table():
    rows = []
    for fam in FAM_ORDER:
        cells = [bi(FAM_NAMES[fam])]
        for split in ('seen', 'unseen'):
            (sa, n), (sb, _) = family_counts('sft', split)[fam], family_counts('sft_gigpo_step100', split)[fam]
            cells.append(f'{sa}/{n} → {sb}/{n}')
        rows.append(cells)
    return data_table([bi(T('Task family', '任务类型')), 'seen', 'unseen'], rows)


def scr_vs_grpo_table():
    g = {int(x['step']): (x['seen'], x['unseen']) for x in ALF if x['run'] == 'gigpo'}
    r_ = {int(x['step']): (x['seen'], x['unseen']) for x in ALF if x['run'] == 'grpo'}
    rows = [[str(s), f'{g[s][0]} / {g[s][1]}', f'{r_[s][0]} / {r_[s][1]}'] for s in sorted(g)]
    return data_table([bi(T('Step', '步')), 'StepCredit-RL (seen / unseen)', 'GRPO (seen / unseen)'], rows)


def scr_updates_table():
    f = {int(x['step']): x for x in ALF if x['run'] == 'gigpo_4upd'}
    o = {int(x['step']): x for x in ALF if x['run'] == 'gigpo' and int(x['step']) <= 150}
    rows = []
    for s in sorted(set(f) | set(o)):
        a = f'{f[s]["seen"]} ({f[s]["hours"]} h)' if s in f else '—'
        b = f'{o[s]["seen"]} ({o[s]["hours"]} h)' if s in o else '—'
        rows.append([str(s), a, b])
    return data_table([bi(T('Step', '步')), bi(T('4 updates: seen (hours)', '4 次更新：seen（小时）')), bi(T('1 update: seen (hours)', '1 次更新：seen（小时）'))], rows)


def scr_hotpotqa_table():
    em = {int(x['step']): x for x in HPQ if x['run'] == 'em'}
    sh = {int(x['step']): x for x in HPQ if x['run'] == 'shaped'}
    rows = [[str(s), em[s]['em'], sh[s]['em'], em[s]['repeat_queries'], sh[s]['repeat_queries']] for s in sorted(em)]
    return data_table([bi(T('Step', '步')), 'EM (EM reward)', bi(T('EM (shaped)', 'EM（稠密）')),
                       bi(T('Repeats (EM reward)', '重复查询（EM 奖励）')), bi(T('Repeats (shaped)', '重复查询（稠密）'))], rows)


# name -> (draw function, data table or None); cards are drawn once at a fixed width
FIGS = {
    'card-opd': (card_opd, None), 'card-scr': (card_scr, None),
    'opd-pipeline': (opd_pipeline, None), 'opd-takeover': (opd_takeover, None), 'opd-methods': (opd_methods, None),
    'opd-budget': (opd_budget, opd_budget_table), 'opd-training': (opd_training, opd_training_table),
    'opd-compute': (opd_compute, opd_compute_table),
    'scr-pipeline': (scr_pipeline, None), 'scr-steplevel': (scr_steplevel, None), 'scr-sft-rl': (scr_sft_rl, scr_sft_rl_table),
    'scr-vs-grpo': (scr_vs_grpo, scr_vs_grpo_table), 'scr-updates': (scr_updates, scr_updates_table),
    'scr-hotpotqa': (scr_hotpotqa, scr_hotpotqa_table),
}
CARDS = {'card-opd', 'card-scr'}
