"""Round 1 (2026-11-16), data charts: aesthetic (v2 restyled with paper-like axes) and innovative (new encodings)."""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE / 'v2'))

from figlib import ALF, FAMILY, HPQ, OPD, PAIRED, Svg, T, hbar, hit_points, moving_avg, polyline, run, scale, vbar  # noqa: E402
from figkit import SOLID  # noqa: E402
import figures_v2 as V2  # noqa: E402

pick, per_lang, legend, chip_legend, gap_wash, signed = V2.pick, V2.per_lang, V2.legend, V2.chip_legend, V2.gap_wash, V2.signed

# per-benchmark results (relay_opd_resume_measured.md, the same table as on the project page)
BENCH = ['MATH-500', 'AIME24', 'AIME25', 'AIME26']
METHODS = [  # (label, values, series class, emphasis)
    (T('Base', '基座'), [72.55, 11.67, 9.06, 8.23], 's3', False),
    (T('GRPO, 60 steps', 'GRPO，60 步'), [78.05, 20.83, 13.54, 11.46], 's3', False),
    (T('SFT, 1 epoch', 'SFT，1 轮'), [83.35, 27.92, 23.12, 17.50], 's3', False),
    (T('OPD, 40 steps', 'OPD，40 步'), [86.05, 31.88, 24.79, 20.21], 's2', False),
    (T('Scaffold-OPD, 40 steps', 'Scaffold-OPD，40 步'), [87.75, 39.38, 31.67, 28.75], 's1', True),
]


# ----------------------------------------------------------------------------- paper-like axes
def axes(svg, box, sx, sy, xticks, yticks, xfmt=str, yfmt=str, xtitle=None, ytitle=None, grid=True):
    x0, y0, x1, y1 = box
    if grid:
        for v in yticks:
            if abs(sy(v) - y1) > 0.5:
                svg.line(x0, sy(v), x1, sy(v), 'grid')
    svg.line(x0, y1, x1, y1, 'axis')
    svg.line(x0, y0, x0, y1, 'axis')
    for v in xticks:
        svg.line(sx(v), y1, sx(v), y1 + 4, 'axis')
        svg.text(sx(v), y1 + 16, xfmt(v), cls='t-faint', anchor='middle', size=11)
    for v in yticks:
        svg.line(x0 - 4, sy(v), x0, sy(v), 'axis')
        svg.text(x0 - 7, sy(v) + 3.8, yfmt(v), cls='t-faint', anchor='end', size=11)
    if xtitle:
        svg.text((x0 + x1) / 2, y1 + 31, xtitle, cls='t-muted', anchor='middle', size=11.5)
    if ytitle:
        cx, cy = x0 - 34, (y0 + y1) / 2
        svg.text(cx, cy, ytitle, cls='t-muted', anchor='middle', size=11.5, extra=f'transform="rotate(-90 {cx:.1f} {cy:.1f})"')


def ptitle(svg, x, y, letter, title, sub=None):
    def draw(i):
        t = f'({letter}) ' + pick(title, i)
        svg.text(x, y, t, cls='t-strong', size=12.5)
        if sub:
            svg.text(x + svg.tw(t, 12.5, 600) + 8, y, pick(sub, i), cls='t-faint', size=11)
    per_lang(svg, draw)


def lines(svg, series, sx, sy, markers=None, r=3.2, title_fn=None):
    """series: [(class index, pts, name)]; markers: set of x values that get a dot."""
    for idx, pts, _ in series:
        svg.path(polyline(pts, sx, sy), f'line l{idx}')
    for idx, pts, _ in series:
        for x, y in pts:
            if markers is None or x in markers:
                svg.circle(sx(x), sy(y), r, f'dot s{idx}', 'stroke-width="1.5"')
    if title_fn:
        for idx, pts, name in series:
            hit_points(svg, pts, sx, sy, lambda x, y, n=name: title_fn(n, x, y), r=6)


def end_label(svg, x, y, text, cls=''):
    svg.text(x + 8, y + 4, text, cls=cls, size=12)


# ============================================================================ opd-methods
def opd_methods_aes(W):
    """v2 bars with an axis line, ticks and a value axis title; the gap bracket and the base line stay."""
    d = OPD['eval_avg4']
    rows = [(T('Base (Qwen3-1.7B)', '基座（Qwen3-1.7B）'), d['base'], 3, False),
            (T('GRPO, 60 steps', 'GRPO，60 步'), d['grpo_60'], 3, False),
            (T('SFT, 1 epoch', 'SFT，1 轮'), d['sft'], 3, False),
            (T('OPD, 40 steps', 'OPD，40 步'), d['opd_40'], 2, False),
            (T('Scaffold-OPD, 40 steps', 'Scaffold-OPD，40 步'), d['takeover_conclude_40'], 1, True),
            (T('without concluding trigger', '关闭收尾触发'), d['takeover_40'], 1, False)]
    narrow = W < 500
    pitch, bh = (44, 14) if narrow else (34, 17)
    x0 = 8 if narrow else 214
    x1 = W - (58 if narrow else 96)
    top = 24
    y_end = top + pitch * len(rows) - 4
    H = y_end + (44 if not narrow else 40)
    svg = Svg(W, H, '4-benchmark math average by post-training method')
    sx = scale(0, 50, x0, x1)
    axes(svg, (x0, top - 8, x1, y_end), sx, lambda v: v, [0, 10, 20, 30, 40, 50], [], grid=False)
    for v in range(10, 51, 10):
        svg.line(sx(v), top - 8, sx(v), y_end, 'grid')
    svg.text((x0 + x1) / 2, y_end + 33, T('4-benchmark average (MATH-500, AIME 2024–26)', '4 项平均（MATH-500、AIME 2024–26）'), cls='t-muted', anchor='middle', size=11.5)
    svg.line(sx(d['base']), top - 10, sx(d['base']), y_end, 'leader', 'stroke-dasharray="3 3"')
    ys = []
    for i, (lab, v, idx, strong) in enumerate(rows):
        yb = top + i * pitch + (20 if narrow else (pitch - bh) / 2 - 2)
        ys.append(yb)
        cls = 't-strong' if strong else ('t-muted' if i == 5 else '')
        if narrow:
            svg.text(x0, yb - 6, lab, cls=cls, size=12)
        else:
            svg.text(x0 - 12, yb + bh / 2 + 4.2, lab, cls=cls, anchor='end', size=12.5)
        op = ' opacity=".5"' if i == 5 else ''
        svg.mark(f'{lab[0]}: {v:.2f}', f'<path class="bar s{idx}" d="{hbar(x0, yb, sx(v), bh)}"{op}/>')
        svg.text(sx(v) + 6, yb + bh / 2 + 4.2, f'{v:.1f}', cls='t-strong' if strong else '', size=12)
    xb = sx(d['takeover_conclude_40']) + (34 if narrow else 40)
    yo, yt = ys[3] + bh / 2, ys[4] + bh / 2
    svg.path(f'M{xb - 5:.1f},{yo:.1f} H{xb:.1f} V{yt:.1f} H{xb - 5:.1f}', 'leader')
    svg.text(xb + 6, (yo + yt) / 2 + 4, signed(d['takeover_conclude_40'] - d['opd_40']), cls='tx-blue', size=12.5, weight=700)
    return svg


def opd_methods_inno(W):
    """Dot plot per benchmark: every method on each benchmark, with the Scaffold-OPD − OPD gap written above."""
    narrow = W < 500
    cols = BENCH + [T('Average', '平均')]
    data = [(lab, vals + [sum(vals) / 4], cls, k) for lab, vals, cls, k in METHODS]
    if narrow:
        H = 420
        box = (40, 70, W - 12, 360)
    else:
        H = 330
        box = (46, 54, W - 150, 288)
    svg = Svg(W, H, 'Every post-training method on each benchmark, and the gap between Scaffold-OPD and OPD')
    sy = scale(0, 100, box[3], box[1])
    n = len(cols)
    cw = (box[2] - box[0]) / n
    axes(svg, box, lambda j: box[0] + cw * (j + 0.5), sy, [], [0, 25, 50, 75, 100])
    for j, c in enumerate(cols):
        cx = box[0] + cw * (j + 0.5)
        svg.text(cx, box[3] + 17, c, cls='t-strong' if j == n - 1 else 't-muted', anchor='middle', size=11.5 if not narrow else 10.5)
        if j == n - 1:
            svg.rect(cx - cw / 2 + 4, box[1] - 6, cw - 8, box[3] - box[1] + 6, 'band', rx=6)
    for lab, vals, cls, k in data:
        for j, v in enumerate(vals):
            cx = box[0] + cw * (j + 0.5)
            svg.mark(f'{lab[0]} · {pick(cols[j], 0)}: {v:.2f}', f'<circle class="dot {cls}" cx="{cx:.1f}" cy="{sy(v):.1f}" r="{5.5 if k else 4.2}"/>')
    opd, ours = data[3][1], data[4][1]
    for j in range(n):
        cx = box[0] + cw * (j + 0.5)
        svg.line(cx, sy(opd[j]) - 5, cx, sy(ours[j]) + 6, 'line l1', 'stroke-width="1.6"')
        svg.text(cx + 9, sy(ours[j]) - 6, signed(ours[j] - opd[j]), cls='t-strong', size=11.5)
    if narrow:
        chip_legend(svg, 8, 16, [('s1', 'Scaffold-OPD'), ('s2', 'OPD')], size=11)
        chip_legend(svg, 8, 36, [('s3', T('base · GRPO · SFT', '基座 · GRPO · SFT'))], size=11)
    else:
        y = box[1] + 8
        for lab, vals, cls, k in reversed(data):
            svg.circle(box[2] + 22, y - 4, 4.5, f'dot {cls}')
            svg.text(box[2] + 32, y, lab, cls='t-strong' if k else '', size=11.5)
            y += 20
        svg.text(box[2] + 16, box[1] + 128, T('number: Scaffold-OPD', '数字：Scaffold-OPD'), cls='t-faint', size=10.5)
        svg.text(box[2] + 16, box[1] + 143, T('minus OPD', '减 OPD'), cls='t-faint', size=10.5)
    return svg


# ============================================================================ opd-budget
def opd_budget_aes(W):
    """v2 two panels with paper axes: ticks, panel letters, markers at each doubling of the budget."""
    b = OPD['budget']
    xs = [math.log2(t) for t in b['tokens']]
    tk, op, gap, se = b['takeover_40'], b['opd_40'], b['gap_40'], b['gap_se_40']
    narrow = W < 500
    right = 58 if narrow else 140
    H = 460 if narrow else 440
    top = (48, 50, W - right, 226)
    bot = (48, 290, W - right, H - 50)
    svg = Svg(W, H, 'Accuracy against the evaluation token budget, and the Scaffold-OPD minus OPD gap')
    legend(svg, top[0], 16, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    sx = scale(10, 15, top[0], top[2])
    syA = scale(0, 50, top[3], top[1])
    ptitle(svg, top[0], top[1] - 14, 'a', T('Accuracy', '准确率'), T('4-benchmark average', '4 项平均'))
    axes(svg, top, sx, syA, [], [0, 10, 20, 30, 40, 50])
    gap_wash(svg, xs, tk, op, sx, syA)
    marks = {10, 11, 12, 13, 14, 15}
    lines(svg, [(2, list(zip(xs, op)), 'OPD'), (1, list(zip(xs, tk)), 'Scaffold-OPD')], sx, syA, marks,
          title_fn=lambda n, x, y: f'{n} · {int(round(2 ** x)):,} tokens: {y:.1f}')
    end_label(svg, sx(15), syA(tk[-1]), f'{tk[-1]:.1f}' if narrow else f'Scaffold-OPD {tk[-1]:.1f}', 't-strong')
    end_label(svg, sx(15), syA(op[-1]), f'{op[-1]:.1f}' if narrow else f'OPD {op[-1]:.1f}')
    syB = scale(-5, 8, bot[3], bot[1])
    ptitle(svg, bot[0], bot[1] - 14, 'b', T('Paired gap', '配对差'), T('Scaffold-OPD − OPD, ±1 SE', 'Scaffold-OPD − OPD，±1 个标准误'))
    axes(svg, bot, sx, syB, [10, 11, 12, 13, 14, 15], [-4, 0, 4, 8], xfmt=lambda v: f'{int(2 ** v / 1024)}k',
         yfmt=lambda v: signed(v, 0) if v else '0', xtitle=T('evaluation budget (tokens)', '评测预算（token）'))
    up = ' L'.join(f'{sx(x):.1f},{syB(g + s):.1f}' for x, g, s in zip(xs, gap, se))
    lo = ' L'.join(f'{sx(x):.1f},{syB(g - s):.1f}' for x, g, s in reversed(list(zip(xs, gap, se))))
    svg.path(f'M{up} L{lo} Z', 'wash1')
    svg.line(bot[0], syB(0), bot[2], syB(0), 'axis', 'stroke-dasharray="4 3"')
    lines(svg, [(1, list(zip(xs, gap)), 'gap')], sx, syB, {13, 14, 15}, r=4)
    for t in (13, 14, 15):
        i = xs.index(t)
        svg.text(sx(t), syB(gap[i] + se[i]) - 8, signed(gap[i]), cls='t-strong', anchor='middle', size=11.5)
    return svg


def opd_budget_inno(W):
    """Adds the explanation as a third panel: the share of AIME answers each model has finished within the budget."""
    b = OPD['budget']
    xs = [math.log2(t) for t in b['tokens']]
    tk, op = b['takeover_40'], b['opd_40']
    ft, fo = b['aime_finished_takeover_40'], b['aime_finished_opd_40']
    gap, se = b['gap_40'], b['gap_se_40']
    narrow = W < 500
    if narrow:
        H = 690
        A, B, C = (44, 56, W - 52, 226), (44, 292, W - 52, 432), (44, 498, W - 52, 640)
    else:
        H = 470
        A = (48, 52, W - 150, 230)
        B = (48, 300, W / 2 - 40, H - 52)
        C = (W / 2 + 50, 300, W - 150, H - 52)
    svg = Svg(W, H, 'Accuracy, the paired gap, and the share of AIME answers finished, against the evaluation budget')
    legend(svg, A[0], 16, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    sxA = scale(10, 15, A[0], A[2])
    syA = scale(0, 50, A[3], A[1])
    ptitle(svg, A[0], A[1] - 14, 'a', T('Accuracy', '准确率'), T('4-benchmark average', '4 项平均'))
    axes(svg, A, sxA, syA, [10, 11, 12, 13, 14, 15], [0, 25, 50], xfmt=lambda v: f'{int(2 ** v / 1024)}k')
    gap_wash(svg, xs, tk, op, sxA, syA)
    lines(svg, [(2, list(zip(xs, op)), 'OPD'), (1, list(zip(xs, tk)), 'Scaffold-OPD')], sxA, syA, {10, 11, 12, 13, 14, 15},
          title_fn=lambda n, x, y: f'{n} · {int(round(2 ** x)):,} tokens: {y:.1f}')
    end_label(svg, sxA(15), syA(tk[-1]), f'{tk[-1]:.1f}' if narrow else f'Scaffold-OPD {tk[-1]:.1f}', 't-strong')
    end_label(svg, sxA(15), syA(op[-1]), f'{op[-1]:.1f}' if narrow else f'OPD {op[-1]:.1f}')
    sxB = scale(10, 15, B[0], B[2])
    syB = scale(-5, 8, B[3], B[1])
    ptitle(svg, B[0], B[1] - 14, 'b', T('Paired gap', '配对差'), '±1 SE')
    axes(svg, B, sxB, syB, [10, 12, 14, 15], [-4, 0, 4, 8], xfmt=lambda v: f'{int(2 ** v / 1024)}k', yfmt=lambda v: signed(v, 0) if v else '0')
    up = ' L'.join(f'{sxB(x):.1f},{syB(g + s):.1f}' for x, g, s in zip(xs, gap, se))
    lo = ' L'.join(f'{sxB(x):.1f},{syB(g - s):.1f}' for x, g, s in reversed(list(zip(xs, gap, se))))
    svg.path(f'M{up} L{lo} Z', 'wash1')
    svg.line(B[0], syB(0), B[2], syB(0), 'axis', 'stroke-dasharray="4 3"')
    lines(svg, [(1, list(zip(xs, gap)), 'gap')], sxB, syB, {13, 14, 15}, r=3.5)
    for t in (13, 14, 15):
        i = xs.index(t)
        svg.text(sxB(t), syB(gap[i] + se[i]) - 7, signed(gap[i]), cls='t-strong', anchor='middle', size=11)
    sxC = scale(10, 15, C[0], C[2])
    syC = scale(0, 100, C[3], C[1])
    ptitle(svg, C[0], C[1] - 14, 'c', T('AIME answers finished', '写完的 AIME 回答'), '%')
    axes(svg, C, sxC, syC, [10, 12, 14, 15], [0, 50, 100], xfmt=lambda v: f'{int(2 ** v / 1024)}k')
    lines(svg, [(2, list(zip(xs, fo)), 'OPD'), (1, list(zip(xs, ft)), 'Scaffold-OPD')], sxC, syC, {14, 15}, r=3.5,
          title_fn=lambda n, x, y: f'{n} · {int(round(2 ** x)):,} tokens: {y:.1f}% finished')
    i16 = xs.index(14)
    svg.text(sxC(14) - 6, syC(fo[i16]) - 8, f'{fo[i16]:.0f}', cls='t-strong', anchor='end', size=11)
    svg.text(sxC(14) + 6, syC(ft[i16]) + 16, f'{ft[i16]:.0f}', cls='t-strong', size=11)
    if not narrow:
        svg.text(C[2] + 10, syC(fo[-1]) + 4, 'OPD', size=11.5)
        svg.text(C[2] + 10, syC(ft[-1]) + 16, 'Scaffold-OPD', cls='t-strong', size=11.5)
    return svg


# ============================================================================ opd-training
def opd_training_aes(W):
    """v2 two panels with paper axes, panel letters, axis titles and the per-answer teacher tokens as a note."""
    tr = OPD['train']
    tk = moving_avg([(s_, l) for s_, l in zip(tr['takeover']['step'], tr['takeover']['response_length']) if s_ != 19])
    op = moving_avg(list(zip(tr['opd']['step'], tr['opd']['response_length'])))
    ratio = moving_avg([(s_, 100 * r_) for s_, r_ in zip(tr['takeover']['step'], tr['takeover']['teacher_token_ratio']) if s_ != 19])
    narrow = W < 500
    if narrow:
        H = 500
        bA, bB = (52, 62, W - 64, 212), (52, 316, W - 64, 460)
    else:
        H = 300
        bA, bB = (56, 62, W / 2 - 70, H - 52), (W / 2 + 54, 62, W - 60, H - 52)
    svg = Svg(W, H, 'Training dynamics: response length and the share of tokens written by the teacher')
    legend(svg, bA[0], 16, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    sxA, syA = scale(0, 60, bA[0], bA[2]), scale(0, 6000, bA[3], bA[1])
    ptitle(svg, bA[0], bA[1] - 16, 'a', T('Response length', '回答长度'), T('tokens', 'token'))
    axes(svg, bA, sxA, syA, [0, 20, 40, 60], [0, 2000, 4000, 6000], yfmt=lambda v: f'{v / 1000:.0f}k' if v else '0', xtitle=T('training step', '训练步'))
    lines(svg, [(2, op, 'OPD'), (1, tk, 'Scaffold-OPD')], sxA, syA, {60}, r=4, title_fn=lambda n, x, y: f'{n} · step {x}: {y:,.0f} tokens')
    end_label(svg, sxA(60), syA(tk[-1][1]), f'{tk[-1][1]:,.0f}', 't-strong')
    end_label(svg, sxA(60), syA(op[-1][1]), f'{op[-1][1]:,.0f}')
    sxB, syB = scale(0, 60, bB[0], bB[2]), scale(0, 20, bB[3], bB[1])
    ptitle(svg, bB[0], bB[1] - 16, 'b', T('Teacher-token share', '老师 token 占比'), T('Scaffold-OPD, %', 'Scaffold-OPD，%'))
    axes(svg, bB, sxB, syB, [0, 20, 40, 60], [0, 5, 10, 15, 20], xtitle=T('training step', '训练步'))
    area = polyline(ratio, sxB, syB) + f' L{sxB(ratio[-1][0]):.1f},{syB(0):.1f} L{sxB(ratio[0][0]):.1f},{syB(0):.1f} Z'
    svg.path(area, 'fl-green')
    svg.path(polyline(ratio, sxB, syB), 'line l5')
    svg.circle(sxB(ratio[-1][0]), syB(ratio[-1][1]), 4, 'dot s5')
    hit_points(svg, ratio, sxB, syB, lambda x, y: f'step {x}: {y:.1f}%', r=5)
    end_label(svg, sxB(60), syB(ratio[-1][1]), f'{ratio[-1][1]:.1f}%', 't-strong')
    return svg


def opd_training_inno(W):
    """One panel in tokens: each Scaffold-OPD answer split into student and teacher tokens (stacked), OPD as a line."""
    tr = OPD['train']
    t = tr['takeover']
    rows = [(s, l, tt) for s, l, tt in zip(t['step'], t['response_length'], t['teacher_tokens_per_answer']) if tt is not None and s != 19]
    total = moving_avg([(s, l) for s, l, tt in rows])
    teach = moving_avg([(s, tt) for s, l, tt in rows])
    opd = moving_avg(list(zip(tr['opd']['step'], tr['opd']['response_length'])))
    narrow = W < 500
    H = 330 if not narrow else 350
    box = (52, 50, W - (70 if narrow else 160), H - 52)
    svg = Svg(W, H, 'Tokens per training answer: Scaffold-OPD split into student and teacher tokens, and OPD')
    chip_legend(svg, box[0], 16, [('s1', T('student tokens', '学生 token')), ('s5', T('teacher tokens', '老师 token'))], size=11.5)
    legend(svg, box[0] + (250 if not narrow else 0), 16 if not narrow else 34, [(2, T('OPD answer length', 'OPD 回答长度'))])
    sx, sy = scale(0, 60, box[0], box[2]), scale(0, 6000, box[3], box[1])
    axes(svg, box, sx, sy, [0, 20, 40, 60], [0, 2000, 4000, 6000], yfmt=lambda v: f'{v / 1000:.0f}k' if v else '0',
         xtitle=T('training step', '训练步'), ytitle=T('tokens per answer', '每条回答的 token'))
    st = [(s, a - b) for (s, a), (_, b) in zip(total, teach)]
    poly_s = polyline(st, sx, sy) + f' L{sx(st[-1][0]):.1f},{sy(0):.1f} L{sx(st[0][0]):.1f},{sy(0):.1f} Z'
    svg.path(poly_s, 's1', 'opacity=".85"')
    top = polyline(total, sx, sy)
    bot = ' L'.join(f'{sx(s):.1f},{sy(v):.1f}' for s, v in reversed(st))
    svg.path(top + ' L' + bot + ' Z', 's5')
    svg.path(polyline(opd, sx, sy), 'line l2')
    hit_points(svg, total, sx, sy, lambda x, y: f'Scaffold-OPD · step {x}: {y:,.0f} tokens per answer', r=5)
    hit_points(svg, opd, sx, sy, lambda x, y: f'OPD · step {x}: {y:,.0f} tokens', r=5)
    first = sum(v for s, v in teach[:5]) / 5
    last = sum(v for s, v in teach[-5:]) / 5
    svg.text(sx(60) + 8, sy(opd[-1][1]) + 4, f'{opd[-1][1]:,.0f}', size=12)
    svg.text(sx(60) + 8, sy(total[-1][1]) + 4, f'{total[-1][1]:,.0f}', cls='t-strong', size=12)
    if not narrow:
        svg.text(box[2] + 14, box[1] + 120, T('teacher tokens', '老师 token'), cls='t-muted', size=11.5)
        svg.text(box[2] + 14, box[1] + 137, T(f'per answer: ≈ {round(first, -1):.0f}', f'每条回答约 {round(first, -1):.0f}'), cls='t-muted', size=11.5)
        svg.text(box[2] + 14, box[1] + 154, T(f'→ {round(last, -1):.0f}, while answers', f'→ {round(last, -1):.0f}，回答本身'), cls='t-muted', size=11.5)
        svg.text(box[2] + 14, box[1] + 171, T('grow ~3×', '变长约 3 倍'), cls='t-muted', size=11.5)
    return svg


# ============================================================================ opd-compute
def opd_compute_aes(W):
    """v2 path chart with paper axes, stage markers labelled in their tone, and a dashed 'same score' guide."""
    narrow = W < 500
    H = 340
    box = (56, 48, W - (24 if narrow else 150), H - 56)
    svg = Svg(W, H, 'Score against cumulative training GPU-hours: the full pipeline and Scaffold-OPD alone')
    legend(svg, box[0], 16, [(2, T('full pipeline', '全流程')), (1, T('Scaffold-OPD alone', '只做 Scaffold-OPD'))])
    sx, sy = scale(0, 56, box[0], box[2]), scale(20, 50, box[3], box[1])
    axes(svg, box, sx, sy, [0, 10, 20, 30, 40, 50], [20, 30, 40, 50], xtitle=T('cumulative training GPU-hours (2 × A100)', '累计训练卡时（2 × A100）'),
         ytitle=T('4-benchmark average', '4 项平均'))
    g, p = OPD['gpu_hours']['pipeline'], OPD['pipeline_avg4']
    c1 = g['sft_incl_teacher_data']; c2 = c1 + g['takeover_40']; c3 = c2 + g['grpo_30']
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
            svg.text(sx(x) + (8 if not narrow else 0), sy(y) - (9 if not narrow else 11), text, anchor='start' if not narrow else 'end', size=11.5)
        else:
            svg.text(sx(x) + 8, sy(y) + 18, text, size=11.5)
    svg.mark(f'Scaffold-OPD alone: {alone[1]:.2f} after {alone[0]:.1f} GPU-hours', f'<circle class="dot s1" cx="{sx(alone[0]):.1f}" cy="{sy(alone[1]):.1f}" r="5.5"/>')
    if narrow:
        svg.text(sx(alone[0]) + 10, sy(alone[1]) + 18, f'{alone[1]:.1f}', cls='tx-blue', size=11.5, weight=700)
        svg.text(box[2], sy(30), T('same score,', '分数相同，'), cls='t-strong', anchor='end', size=12)
        svg.text(box[2], sy(30) + 17, T(f'≈ {c3 / alone[0]:.0f}× the GPU-hours', f'卡时约 {c3 / alone[0]:.0f} 倍'), cls='t-strong', anchor='end', size=12)
    else:
        svg.text(sx(alone[0]) + 10, sy(alone[1]) + 18, T(f'Scaffold-OPD alone {alone[1]:.1f}', f'只做 Scaffold-OPD {alone[1]:.1f}'), cls='tx-blue', size=11.5, weight=700)
        svg.text((sx(alone[0]) + sx(c3)) / 2, sy(alone[1]) - 8, T(f'same score, about {c3 / alone[0]:.0f}× the GPU-hours', f'分数相同，卡时约 {c3 / alone[0]:.0f} 倍'), cls='t-strong', anchor='middle', size=12)
    return svg


def opd_compute_inno(W):
    """Two stacked bars of training GPU-hours, each ending in the score it reached."""
    g, p = OPD['gpu_hours']['pipeline'], OPD['pipeline_avg4']
    alone_h, alone_s = OPD['gpu_hours']['takeover_40'], OPD['eval_avg4']['takeover_40']
    narrow = W < 500
    H = 210 if not narrow else 250
    x0 = 150 if not narrow else 16
    x1 = W - (120 if not narrow else 20)
    svg = Svg(W, H, 'Training GPU-hours of the full pipeline and of Scaffold-OPD alone, with the score each reached')
    sx = scale(0, 56, x0, x1)
    rows_y = (60, 128) if not narrow else (84, 176)
    segs = [(g['sft_incl_teacher_data'], 'pn-yellow', T('teacher data + SFT', '老师数据 + SFT')), (g['takeover_40'], 'pn-blue', T('Scaffold-OPD', 'Scaffold-OPD')),
            (g['grpo_30'], 'pn-orange', T('GRPO on failures', '错题回流 GRPO'))]
    for v in (0, 10, 20, 30, 40, 50):
        svg.line(sx(v), 36, sx(v), rows_y[1] + 30, 'grid')
        svg.text(sx(v), rows_y[1] + 46, str(v), cls='t-faint', anchor='middle', size=11)
    svg.text(x1, rows_y[1] + 62, T('training GPU-hours (2 × A100)', '训练卡时（2 × A100）'), cls='t-muted', anchor='end', size=11.5)
    y = rows_y[0]
    lab_y = y - 8
    if narrow:
        svg.text(x0, lab_y - 14, T('Full pipeline', '全流程'), cls='t-strong', size=12.5)
    else:
        svg.text(x0 - 12, y + 18, T('Full pipeline', '全流程'), cls='t-strong', anchor='end', size=12.5)
    x = 0
    for hrs, cls, lab in segs:
        svg.mark(f'{lab[0]}: {hrs:.1f} GPU-hours', f'<rect class="{cls}" x="{sx(x) + 1:.1f}" y="{y:.1f}" width="{sx(x + hrs) - sx(x) - 2:.1f}" height="28" rx="6"/>')
        svg.text((sx(x) + sx(x + hrs)) / 2, y + 18.5, lab, cls='t-strong', anchor='middle', size=11 if not narrow else 9.5)
        x += hrs
    svg.text(sx(x) + 10, y + 19, T(f'→ {p["grpo_30"]:.1f}', f'→ {p["grpo_30"]:.1f}'), cls='t-strong', size=13)
    y = rows_y[1]
    if narrow:
        svg.text(x0, y - 22, T('Scaffold-OPD alone', '只做 Scaffold-OPD'), cls='t-strong', size=12.5)
    else:
        svg.text(x0 - 12, y + 18, T('Scaffold-OPD alone', '只做 Scaffold-OPD'), cls='t-strong', anchor='end', size=12.5)
    svg.mark(f'Scaffold-OPD alone: {alone_h:.1f} GPU-hours', f'<rect class="pn-blue" x="{sx(0) + 1:.1f}" y="{y:.1f}" width="{sx(alone_h) - sx(0) - 2:.1f}" height="28" rx="6"/>')
    svg.text(sx(alone_h) + 10, y + 19, f'→ {alone_s:.1f}', cls='t-strong', size=13)
    svg.text(sx(alone_h) + 64, y + 19, T(f'same score with {x / alone_h:.0f}× fewer GPU-hours', f'分数相同，卡时只有 1/{x / alone_h:.0f}'), cls='tx-blue', size=12, weight=600) if not narrow else None
    if narrow:
        svg.text(x0, H - 6, T('same score, ≈ 1/4 of the GPU-hours', '分数相同，卡时约 1/4'), cls='tx-blue', size=12, weight=600)
    return svg


# ============================================================================ scr-sft-rl
def scr_sft_rl_aes(W):
    """v2 dumbbells with a ticked value axis per panel and panel letters; non-key families in a softer gray."""
    narrow = W < 500
    if narrow:
        H = 496
        panels = [('seen', (100, 70, W - 44, 228)), ('unseen', (100, 310, W - 44, 468))]
    else:
        H = 290
        panels = [('seen', (130, 66, W / 2 - 34, H - 50)), ('unseen', (W / 2 + 104, 66, W - 34, H - 50))]
    svg = Svg(W, H, 'ALFWorld success by task family, after SFT and after 100 more steps of RL')
    chip_legend(svg, 14 if not narrow else 8, 18, [('s3', T('after SFT', 'SFT 后')), ('s1', T('after SFT + 100 RL steps', 'SFT + 100 步 RL 后'))])
    for k, (split, box) in enumerate(panels):
        a, b = V2.family_counts('sft', split), V2.family_counts('sft_gigpo_step100', split)
        sx = scale(0, 100, box[0], box[2])
        ptitle(svg, box[0], box[1] - 18, 'ab'[k], f'valid_{split}', T('success, %', '成功率，%'))
        axes(svg, (box[0], box[1] - 6, box[2], box[3]), sx, lambda v: v, [0, 25, 50, 75, 100], [], grid=False)
        for v in (25, 50, 75, 100):
            svg.line(sx(v), box[1] - 6, sx(v), box[3], 'grid')
        pitch = (box[3] - box[1]) / len(V2.FAM_ORDER)
        for i, fam in enumerate(V2.FAM_ORDER):
            y = box[1] + i * pitch + pitch / 2 - 4
            key = fam == 'pick_two_obj_and_place'
            (sa, n), (sb, _) = a[fam], b[fam]
            pa, pb = 100 * sa / n, 100 * sb / n
            svg.text(box[0] - 10, y + 4, V2.FAM_NAMES[fam], cls='t-strong' if key else '', anchor='end', size=11.5)
            svg.line(sx(pa), y, sx(pb), y, 'line l1' if key else 'line l3', 'stroke-width="2.4"' + ('' if key else ' opacity=".55"'))
            svg.mark(f'{V2.FAM_NAMES[fam][0]}, {split}: {sa}/{n} after SFT → {sb}/{n} after RL',
                     f'<circle class="dot s3" cx="{sx(pa):.1f}" cy="{y:.1f}" r="4.5"/><circle class="dot s1" cx="{sx(pb):.1f}" cy="{y:.1f}" r="5"/>')
            if key:
                svg.text(sx(pa) - 9, y + 4, f'{sa}/{n}', cls='t-muted', anchor='end', size=11)
                svg.text(sx(pb) + 9, y + 4, f'{sb}/{n}', cls='t-strong', size=11)
    return svg


def scr_sft_rl_inno(W):
    """Slope chart: each task family from after SFT (left) to after 100 RL steps (right), seen and unseen."""
    narrow = W < 500
    panels = [('seen', 0), ('unseen', 1)]
    if narrow:
        H = 620
        boxes = [(96, 60, W - 96, 280), (96, 352, W - 96, 572)]
    else:
        H = 330
        boxes = [(120, 56, W / 2 - 100, H - 46), (W / 2 + 110, 56, W - 100, H - 46)]
    svg = Svg(W, H, 'ALFWorld success by task family, after SFT and after 100 RL steps')
    for (split, k), box in zip(panels, boxes):
        a, b = V2.family_counts('sft', split), V2.family_counts('sft_gigpo_step100', split)
        sy = scale(0, 100, box[3], box[1])
        xa, xb = box[0], box[2]
        svg.text((xa + xb) / 2, box[1] - 26, f'valid_{split}', cls='t-strong', anchor='middle', size=12.5)
        svg.text(xa, box[1] - 8, T('after SFT', 'SFT 后'), cls='t-muted', anchor='middle', size=11)
        svg.text(xb, box[1] - 8, T('+100 RL steps', '+100 步 RL'), cls='t-muted', anchor='middle', size=11)
        svg.line(xa, box[1], xa, box[3], 'axis')
        svg.line(xb, box[1], xb, box[3], 'axis')
        for v in (0, 50, 100):
            svg.line(xa, sy(v), xb, sy(v), 'grid')
            svg.text(xa - 8, sy(v) + 4, str(v), cls='t-faint', anchor='end', size=10.5)
        order = sorted(V2.FAM_ORDER, key=lambda f: a[f][0] / a[f][1])
        for fam in order:
            (sa, n), (sb, _) = a[fam], b[fam]
            pa, pb = 100 * sa / n, 100 * sb / n
            key = fam == 'pick_two_obj_and_place'
            svg.line(xa, sy(pa), xb, sy(pb), 'line l1' if key else 'line l3', 'stroke-width="2.4"' if key else 'opacity=".75"')
            svg.mark(f'{V2.FAM_NAMES[fam][0]}, {split}: {sa}/{n} → {sb}/{n}',
                     f'<circle class="dot {"s1" if key else "s3"}" cx="{xa:.1f}" cy="{sy(pa):.1f}" r="{4.5 if key else 3.5}"/>'
                     f'<circle class="dot {"s1" if key else "s3"}" cx="{xb:.1f}" cy="{sy(pb):.1f}" r="{4.5 if key else 3.5}"/>')
        two_a, two_b = a['pick_two_obj_and_place'], b['pick_two_obj_and_place']
        pa, pb = 100 * two_a[0] / two_a[1], 100 * two_b[0] / two_b[1]
        svg.text(xa - 8, sy(pa) + 16, f'{two_a[0]}/{two_a[1]}', cls='t-strong', anchor='end', size=11)
        svg.text(xb + 8, sy(pb) + 4, T(f'two objects {two_b[0]}/{two_b[1]}', f'双物体 {two_b[0]}/{two_b[1]}'), cls='tx-blue', size=11.5, weight=600)
        svg.text(xa - 8, sy(pa) + 4, T('two objects', '双物体'), cls='tx-blue', anchor='end', size=11.5, weight=600)
    return svg


# ============================================================================ scr-vs-grpo
def scr_vs_grpo_aes(W):
    """v2 layout with paper axes, panel letters, end markers and the discordant bars kept."""
    narrow = W < 500
    g = {k: run(ALF, 'gigpo', k) for k in ('seen', 'unseen')}
    r = {k: run(ALF, 'grpo', k) for k in ('seen', 'unseen')}
    if narrow:
        H = 600
        boxes = {'seen': (44, 66, W - 60, 222), 'unseen': (44, 360, W - 60, 516)}
        bar_y = {'seen': 274, 'unseen': 568}
    else:
        H = 360
        boxes = {'seen': (48, 66, W / 2 - 56, 256), 'unseen': (W / 2 + 54, 66, W - 54, 256)}
        bar_y = {'seen': 322, 'unseen': 322}
    svg = Svg(W, H, 'ALFWorld validation success over 200 steps, StepCredit-RL vs GRPO, and tasks solved by only one run at step 200')
    legend(svg, 48, 16, [(1, 'StepCredit-RL'), (2, 'GRPO')])
    disc = {k: PAIRED[f'alfworld_steplevel_vs_grpo:valid_{k}'] for k in ('seen', 'unseen')}
    most = max(int(p_['only_a']) + int(p_['only_b']) for p_ in disc.values())
    for k, (name, box) in enumerate(boxes.items()):
        sx, sy = scale(0, 200, box[0], box[2]), scale(0, 100, box[3], box[1])
        ptitle(svg, box[0], box[1] - 20, 'ab'[k], f'valid_{name}', T('success, %', '成功率，%'))
        svg.rect(sx(160), box[1], sx(200) - sx(160), box[3] - box[1], 'band')
        late_g = sum(v for s_, v in g[name] if s_ >= 160) / 5
        late_r = sum(v for s_, v in r[name] if s_ >= 160) / 5
        svg.text((sx(160) + sx(200)) / 2, box[1] + 13, f'{late_g:.1f} vs {late_r:.1f}', cls='t-muted', anchor='middle', size=10.5)
        axes(svg, box, sx, sy, [0, 50, 100, 150, 200], [0, 25, 50, 75, 100])
        gap_wash(svg, [s_ for s_, _ in g[name]], [v for _, v in g[name]], [v for _, v in r[name]], sx, sy)
        lines(svg, [(2, r[name], 'GRPO'), (1, g[name], 'StepCredit-RL')], sx, sy, {200}, r=4, title_fn=lambda n, x, y: f'{n} · step {x}: {y:.1f}%')
        V2.end_labels(svg, [(sx(200) + 8, sy(g[name][-1][1]), f'{g[name][-1][1]:.1f}', 't-strong'),
                            (sx(200) + 8, sy(r[name][-1][1]), f'{r[name][-1][1]:.1f}', '')], min_gap=14)
        p_ = disc[name]
        a_, b_, pv = int(p_['only_a']), int(p_['only_b']), float(p_['p'])
        by = bar_y[name]
        unit = (box[2] - box[0]) / most
        svg.text(box[0], by - 8, T('solved by only one run at step 200', '第 200 步只有一方解出'), cls='t-muted', size=11)
        svg.text(box[2], by - 8, f'p = {pv:.3f}' if pv < 0.1 else f'p = {pv:.2f}', cls='tx-blue' if pv < 0.05 else 't-muted', anchor='end', size=11.5, weight=700 if pv < 0.05 else None)
        wa, wb = a_ * unit, b_ * unit
        svg.mark(f'{name}: only StepCredit-RL {a_}, only GRPO {b_}, McNemar p = {pv}',
                 f'<rect class="s1" x="{box[0]:.1f}" y="{by:.1f}" width="{wa - 1.5:.1f}" height="16" rx="3"/>'
                 f'<rect class="s2" x="{box[0] + wa + 1.5:.1f}" y="{by:.1f}" width="{wb - 1.5:.1f}" height="16" rx="3"/>')
        svg.text(box[0] + wa / 2, by + 12, str(a_), cls='t-on', anchor='middle', size=11)
        svg.text(box[0] + wa + 1.5 + wb / 2, by + 12, str(b_), cls='t-on', anchor='middle', size=11)
    return svg


def scr_vs_grpo_inno(W):
    """Curves on top; under each, the per-validation difference (StepCredit-RL − GRPO) as bars."""
    narrow = W < 500
    g = {k: run(ALF, 'gigpo', k) for k in ('seen', 'unseen')}
    r = {k: run(ALF, 'grpo', k) for k in ('seen', 'unseen')}
    if narrow:
        H = 720
        boxes = {'seen': ((40, 62, W - 52, 210), (40, 232, W - 52, 312)), 'unseen': ((40, 402, W - 52, 550), (40, 572, W - 52, 652))}
    else:
        H = 400
        boxes = {'seen': ((44, 62, W / 2 - 46, 222), (44, 246, W / 2 - 46, 340)), 'unseen': ((W / 2 + 50, 62, W - 40, 222), (W / 2 + 50, 246, W - 40, 340))}
    svg = Svg(W, H, 'StepCredit-RL vs GRPO: validation curves and the difference at every validation')
    legend(svg, 44, 16, [(1, 'StepCredit-RL'), (2, 'GRPO')])
    for name, (A, B) in boxes.items():
        sx = scale(0, 200, A[0], A[2])
        syA = scale(0, 100, A[3], A[1])
        ptitle(svg, A[0], A[1] - 14, 'a' if name == 'seen' else 'b', f'valid_{name}', T('success, %', '成功率，%'))
        axes(svg, A, sx, syA, [], [0, 50, 100])
        gap_wash(svg, [s for s, _ in g[name]], [v for _, v in g[name]], [v for _, v in r[name]], sx, syA)
        lines(svg, [(2, r[name], 'GRPO'), (1, g[name], 'StepCredit-RL')], sx, syA, {200}, r=4,
              title_fn=lambda n, x, y: f'{n} · step {x}: {y:.1f}%')
        end_label(svg, sx(200), syA(g[name][-1][1]) - (6 if name == 'unseen' else 0), f'{g[name][-1][1]:.1f}', 't-strong')
        end_label(svg, sx(200), syA(r[name][-1][1]) + (8 if name == 'unseen' else 0), f'{r[name][-1][1]:.1f}')
        syB = scale(-30, 40, B[3], B[1])
        axes(svg, B, sx, syB, [0, 50, 100, 150, 200], [-20, 0, 20, 40], yfmt=lambda v: signed(v, 0) if v else '0')
        svg.line(B[0], syB(0), B[2], syB(0), 'axis')
        bw = (B[2] - B[0]) / 22
        for (s, a_), (_, b_) in zip(g[name], r[name]):
            d = a_ - b_
            cls = 's1' if d >= 0 else 's2'
            y0, y1 = (syB(d), syB(0)) if d >= 0 else (syB(0), syB(d))
            svg.mark(f'step {s}: {signed(d)}', f'<rect class="{cls}" x="{sx(s) - bw / 2:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(y1 - y0, 0.8):.1f}" rx="1.5"/>')
        svg.text(B[0] + 4, B[1] + 2, T('difference, points', '差值（百分点）'), cls='t-faint', size=10.5)
    return svg


# ============================================================================ scr-updates
def scr_updates_aes(W):
    """v2 two panels (by step, by hours) with paper axes, panel letters and markers at each validation."""
    narrow = W < 500
    four = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo_4upd']
    one = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo' and int(x['step']) <= 150]
    if narrow:
        H = 548
        bA, bB = (48, 82, W - 64, 236), (48, 340, W - 64, 494)
    else:
        H = 324
        bA, bB = (52, 82, W / 2 - 60, H - 52), (W / 2 + 56, 82, W - 64, H - 52)
    svg = Svg(W, H, 'Seen success with one vs four updates per step, by training step and by wall-clock hours')
    legend(svg, 52, 16, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
    for k, (box, key, xmax, ticks, title, unit) in enumerate([(bA, 0, 150, [0, 50, 100, 150], T('By training step', '按训练步'), T('training step', '训练步')),
                                                             (bB, 2, 30, [0, 10, 20, 30], T('By wall-clock time', '按耗时'), T('hours (2 × A100)', '小时（2 × A100）'))]):
        sx, sy = scale(0, xmax, box[0], box[2]), scale(0, 100, box[3], box[1])
        ptitle(svg, box[0], box[1] - 26, 'ab'[k], title, T('seen success, %', 'seen 成功率，%'))
        axes(svg, box, sx, sy, ticks, [0, 25, 50, 75, 100], xtitle=unit)
        pf = [(d_[key], d_[1]) for d_ in four]
        po = [(d_[key], d_[1]) for d_ in one]
        lines(svg, [(3, po, '1 update'), (1, pf, '4 updates')], sx, sy, None, r=2.8,
              title_fn=lambda n, x, y, kk=key: f'{n} · ' + (f'step {x:.0f}' if kk == 0 else f'{x:.1f} h') + f': {y:.1f}%')
        end_label(svg, sx(pf[-1][0]), sy(pf[-1][1]), f'{pf[-1][1]:.1f}', 't-strong')
        end_label(svg, sx(po[-1][0]), sy(po[-1][1]), f'{po[-1][1]:.1f}')
        if key == 0:
            ya = sy(max(pf[-1][1], po[-1][1])) - 16
            svg.path(f'M{sx(100):.1f},{ya + 6:.1f} V{ya:.1f} H{sx(150):.1f} V{ya + 6:.1f}', 'leader')
            svg.text((sx(100) + sx(150)) / 2, ya - 6, T('same level: step 100 vs 150', '水平相当：第 100 步对第 150 步'), cls='t-muted', anchor='middle', size=11)
        else:
            svg.text(sx(pf[-1][0]), sy(pf[-1][1]) - 12, T('step 100', '第 100 步'), cls='t-faint', anchor='middle', size=10.5)
            svg.text(sx(po[-1][0]), sy(po[-1][1]) - 12, T('step 150', '第 150 步'), cls='t-faint', anchor='middle', size=10.5)
    return svg


def _first_reach(rows, thr, key):
    for row in rows:
        if row[1] >= thr:
            return row
    return None


def scr_updates_inno(W):
    """Sample efficiency read off directly: training steps and hours each setting needs to first reach 50% and 70% (seen)."""
    narrow = W < 500
    four = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo_4upd']
    one = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo']
    thr = [50, 70]
    H = 250 if not narrow else 420
    svg = Svg(W, H, 'Training steps and hours needed to first reach 50% and 70% seen success, one vs four updates per step')
    legend(svg, 20, 16, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
    panels = [(0, T('training steps', '训练步'), 160), (2, T('wall-clock hours', '耗时（小时）'), 32)]
    for k, (key, title, xmax) in enumerate(panels):
        if narrow:
            x0, x1, ytop = 70, W - 50, 60 + k * 180
        else:
            x0, x1, ytop = (100 + k * (W / 2)), (W / 2 - 40 + k * (W / 2)), 60
        sx = scale(0, xmax, x0, x1)
        ptitle(svg, x0, ytop - 14, 'a' if k == 0 else 'b', title)
        for i, t_ in enumerate(thr):
            yy = ytop + 12 + i * 70
            svg.text(x0 - 10, yy + 26, f'≥ {t_}%', cls='t-strong', anchor='end', size=12)
            for j, (rows, cls, nm) in enumerate([(four, 's1', '4 updates'), (one, 's3', '1 update')]):
                row = _first_reach(rows, t_, key)
                y = yy + j * 22
                v = row[key]
                svg.mark(f'{nm}: reaches {t_}% at step {row[0]} ({row[2]:.1f} h)', f'<path class="bar {cls}" d="{hbar(x0, y, sx(v), 16, 4)}"/>')
                svg.text(sx(v) + 6, y + 12.5, f'{v:.0f}' if key == 0 else f'{v:.1f} h', cls='t-strong' if j == 0 else '', size=11.5)
        svg.line(x0, ytop + 6, x0, ytop + 150, 'axis')
    return svg


# ============================================================================ scr-hotpotqa
def scr_hotpotqa_aes(W):
    """v2 two panels with paper axes and panel letters; the gap is labelled instead of shaded in the repeats panel."""
    narrow = W < 500
    em_em, em_sh = run(HPQ, 'em', 'em'), run(HPQ, 'shaped', 'em')
    rq_em, rq_sh = run(HPQ, 'em', 'repeat_queries'), run(HPQ, 'shaped', 'repeat_queries')
    p_ = PAIRED['hotpotqa_em_vs_shaped:all']
    if narrow:
        H = 530
        bA, bB = (52, 72, W - 64, 230), (52, 330, W - 64, 482)
    else:
        H = 310
        bA, bB = (52, 72, W / 2 - 64, H - 52), (W / 2 + 54, 72, W - 64, H - 52)
    svg = Svg(W, H, 'HotpotQA: exact match and repeated queries per question, EM reward vs shaped reward')
    legend(svg, bA[0], 16, [(1, T('EM reward', 'EM 奖励')), (2, T('shaped reward', '稠密奖励'))])
    sxA, syA = scale(0, 200, bA[0], bA[2]), scale(40, 60, bA[3], bA[1])
    ptitle(svg, bA[0], bA[1] - 20, 'a', T('Exact match', 'EM'), '%')
    axes(svg, bA, sxA, syA, [0, 50, 100, 150, 200], [40, 45, 50, 55, 60], xtitle=T('training step', '训练步'))
    gap_wash(svg, [s_ for s_, _ in em_em], [v for _, v in em_em], [v for _, v in em_sh], sxA, syA)
    lines(svg, [(2, em_sh, 'shaped'), (1, em_em, 'EM reward')], sxA, syA, None, r=2.8, title_fn=lambda n, x, y: f'{n} · step {x}: {y:.1f}%')
    V2.end_labels(svg, [(sxA(200) + 8, syA(em_em[-1][1]), f'{em_em[-1][1]:.1f}', 't-strong'), (sxA(200) + 8, syA(em_sh[-1][1]), f'{em_sh[-1][1]:.1f}', '')])
    svg.text(bA[2], syA(42), T(f'step 200: McNemar p = {float(p_["p"]):.2f}', f'第 200 步：McNemar p = {float(p_["p"]):.2f}'), cls='t-faint', anchor='end', size=11)
    sxB, syB = scale(0, 200, bB[0], bB[2]), scale(0, 0.2, bB[3], bB[1])
    ptitle(svg, bB[0], bB[1] - 20, 'b', T('Repeated queries', '重复查询'), T('per question', '每题'))
    axes(svg, bB, sxB, syB, [0, 50, 100, 150, 200], [0, 0.05, 0.1, 0.15, 0.2], yfmt=lambda v: f'{v:.2f}' if v else '0', xtitle=T('training step', '训练步'))
    lines(svg, [(2, rq_sh, 'shaped'), (1, rq_em, 'EM reward')], sxB, syB, None, r=2.8, title_fn=lambda n, x, y: f'{n} · step {x}: {y:.3f}')
    V2.end_labels(svg, [(sxB(200) + 8, syB(rq_em[-1][1]), f'{rq_em[-1][1]:.3f}', ''), (sxB(200) + 8, syB(rq_sh[-1][1]), f'{rq_sh[-1][1]:.3f}', 't-strong')])
    ya, yb = syB(rq_em[-1][1]), syB(rq_sh[-1][1])
    xl = sxB(200) - 6
    svg.line(xl, ya + 7, xl, yb - 7, 'leader')
    svg.text(xl - 6, (ya + yb) / 2 + 4, signed(100 * (rq_sh[-1][1] - rq_em[-1][1]) / rq_em[-1][1], 0) + '%', cls='tx-orange', anchor='end', size=12.5, weight=700)
    return svg


def scr_hotpotqa_inno(W):
    """Three small multiples (EM, F1, repeated queries) for the two rewards; the shaped reward only wins on repeats."""
    narrow = W < 500
    em = {k: run(HPQ, 'em', k) for k in ('em', 'f1', 'repeat_queries')}
    sh = {k: run(HPQ, 'shaped', k) for k in ('em', 'f1', 'repeat_queries')}
    specs = [('em', T('Exact match', 'EM'), '%', (40, 60), [40, 50, 60], lambda v: f'{v:.0f}'),
             ('f1', T('Token F1', 'Token F1'), '', (0.55, 0.75), [0.55, 0.65, 0.75], lambda v: f'{v:.2f}'),
             ('repeat_queries', T('Repeated queries', '重复查询'), T('per question', '每题'), (0, 0.2), [0, 0.1, 0.2], lambda v: f'{v:.1f}' if v else '0')]
    H = 270 if not narrow else 760
    svg = Svg(W, H, 'HotpotQA: exact match, F1 and repeated queries under the EM reward and the shaped reward')
    legend(svg, 44, 16, [(1, T('EM reward', 'EM 奖励')), (2, T('shaped reward', '稠密奖励'))])
    for k, (key, title, unit, (lo, hi), ticks, fmt) in enumerate(specs):
        if narrow:
            box = (52, 66 + k * 236, W - 70, 66 + k * 236 + 160)
        else:
            pw = (W - 60) / 3
            box = (52 + k * pw, 66, 52 + k * pw + pw - 76, H - 50)
        sx, sy = scale(0, 200, box[0], box[2]), scale(lo, hi, box[3], box[1])
        ptitle(svg, box[0], box[1] - 14, 'abc'[k], title, unit or None)
        axes(svg, box, sx, sy, [0, 100, 200], ticks, yfmt=fmt)
        lines(svg, [(2, sh[key], 'shaped'), (1, em[key], 'EM reward')], sx, sy, {0, 200}, r=3.5,
              title_fn=lambda n, x, y: f'{n} · step {x}: {y}')
        a_, b_ = em[key][-1][1], sh[key][-1][1]
        f = (lambda v: f'{v:.1f}') if key == 'em' else (lambda v: f'{v:.3f}')
        hi_first = a_ >= b_
        end_label(svg, sx(200), sy(a_) + (-3 if hi_first else 7), f(a_), 't-strong' if key != 'repeat_queries' else '')
        end_label(svg, sx(200), sy(b_) + (7 if hi_first else -3), f(b_), 't-strong' if key == 'repeat_queries' else '')
    return svg


AES = {'opd-methods': opd_methods_aes, 'opd-budget': opd_budget_aes, 'opd-training': opd_training_aes, 'opd-compute': opd_compute_aes,
       'scr-sft-rl': scr_sft_rl_aes, 'scr-vs-grpo': scr_vs_grpo_aes, 'scr-updates': scr_updates_aes, 'scr-hotpotqa': scr_hotpotqa_aes}
INNO = {'opd-methods': opd_methods_inno, 'opd-budget': opd_budget_inno, 'opd-training': opd_training_inno, 'opd-compute': opd_compute_inno,
        'scr-sft-rl': scr_sft_rl_inno, 'scr-vs-grpo': scr_vs_grpo_inno, 'scr-updates': scr_updates_inno, 'scr-hotpotqa': scr_hotpotqa_inno}
