"""Round 2 (2026-11-16), data charts: each starts from the version kept in round 1 (see PICKS in rounds.py)."""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE / 'v2'))
sys.path.insert(0, str(HERE))

from figlib import ALF, HPQ, OPD, PAIRED, Svg, T, hbar, hit_points, moving_avg, polyline, run, scale  # noqa: E402
import figures_v2 as V2  # noqa: E402
import r1_charts as R1  # noqa: E402

pick, per_lang, legend, chip_legend, gap_wash, signed = V2.pick, V2.per_lang, V2.legend, V2.chip_legend, V2.gap_wash, V2.signed
axes, ptitle, lines, end_label = R1.axes, R1.ptitle, R1.lines, R1.end_label


def k_fmt(v):
    return f'{int(2 ** v / 1024)}k'


# ============================================================================ opd-methods (from R1 aes)
def _method_rows():
    d = OPD['eval_avg4']
    return [(T('Base (Qwen3-1.7B)', '基座（Qwen3-1.7B）'), d['base'], 3, False),
            (T('GRPO, 60 steps', 'GRPO，60 步'), d['grpo_60'], 3, False),
            (T('SFT, 1 epoch', 'SFT，1 轮'), d['sft'], 3, False),
            (T('OPD, 40 steps', 'OPD，40 步'), d['opd_40'], 2, False),
            (T('Scaffold-OPD, 40 steps', 'Scaffold-OPD，40 步'), d['takeover_conclude_40'], 1, True),
            (T('without concluding trigger', '关闭收尾触发'), d['takeover_40'], 1, False)]


def opd_methods_aes(W):
    """R1 bars, polished: thinner bars with more air, values in the text colour, the base line labelled at the axis."""
    rows = _method_rows()
    d = OPD['eval_avg4']
    narrow = W < 500
    pitch, bh = (46, 13) if narrow else (36, 14)
    x0 = 10 if narrow else 220
    x1 = W - (60 if narrow else 100)
    top = 26
    y_end = top + pitch * len(rows) - 6
    H = y_end + 46
    svg = Svg(W, H, '4-benchmark math average by post-training method')
    sx = scale(0, 50, x0, x1)
    for v in range(10, 51, 10):
        svg.line(sx(v), top - 8, sx(v), y_end, 'grid')
    axes(svg, (x0, top - 8, x1, y_end), sx, lambda v: v, [0, 10, 20, 30, 40, 50], [], grid=False)
    svg.text((x0 + x1) / 2, y_end + 33, T('4-benchmark average (MATH-500, AIME 2024–26)', '4 项平均（MATH-500、AIME 2024–26）'), cls='t-muted', anchor='middle', size=11.5)
    svg.line(sx(d['base']), top - 8, sx(d['base']), y_end, 'leader', 'stroke-dasharray="3 3"')
    svg.text(sx(d['base']) + 4, top - 12, T('base', '基座'), cls='t-faint', size=10.5)
    ys = []
    for i, (lab, v, idx, strong) in enumerate(rows):
        yb = top + i * pitch + (22 if narrow else (pitch - bh) / 2 - 2)
        ys.append(yb)
        cls = 't-strong' if strong else ('t-muted' if i == 5 else '')
        if narrow:
            svg.text(x0, yb - 6, lab, cls=cls, size=12)
        else:
            svg.text(x0 - 12, yb + bh / 2 + 4.2, lab, cls=cls, anchor='end', size=12.5)
        op = ' opacity=".45"' if i == 5 else ''
        svg.mark(f'{lab[0]}: {v:.2f}', f'<path class="bar s{idx}" d="{hbar(x0, yb, sx(v), bh)}"{op}/>')
        svg.text(sx(v) + 7, yb + bh / 2 + 4.2, f'{v:.1f}', cls='t-strong' if strong else 't-muted', size=12)
    xb = sx(d['takeover_conclude_40']) + (36 if narrow else 42)
    yo, yt = ys[3] + bh / 2, ys[4] + bh / 2
    svg.path(f'M{xb - 5:.1f},{yo:.1f} H{xb:.1f} V{yt:.1f} H{xb - 5:.1f}', 'leader')
    svg.text(xb + 6, (yo + yt) / 2 + 4.5, signed(d['takeover_conclude_40'] - d['opd_40']), cls='tx-blue', size=13, weight=700)
    return svg


def opd_methods_inno(W):
    """The same numbers as gains: an arrow from the base model's 25.4 to each method's score, gain written at the tip."""
    rows = _method_rows()[1:]
    d = OPD['eval_avg4']
    narrow = W < 500
    pitch = 46 if narrow else 38
    x0 = 10 if narrow else 220
    x1 = W - (70 if narrow else 120)
    top = 30
    y_end = top + pitch * len(rows)
    H = y_end + 44
    svg = Svg(W, H, 'Gain of each post-training method over the base model on the 4-benchmark average')
    sx = scale(20, 50, x0, x1)
    for v in (20, 30, 40, 50):
        svg.line(sx(v), top - 10, sx(v), y_end - 6, 'grid')
    axes(svg, (x0, top - 10, x1, y_end - 6), sx, lambda v: v, [20, 30, 40, 50], [], grid=False)
    svg.text((x0 + x1) / 2, y_end + 28, T('4-benchmark average', '4 项平均'), cls='t-muted', anchor='middle', size=11.5)
    svg.line(sx(d['base']), top - 10, sx(d['base']), y_end - 6, 'line l3', 'stroke-width="1.4"')
    svg.text(sx(d['base']), top - 14, T(f'base {d["base"]:.1f}', f'基座 {d["base"]:.1f}'), cls='t-muted', anchor='middle', size=11)
    for i, (lab, v, idx, strong) in enumerate(rows):
        y = top + i * pitch + (24 if narrow else pitch / 2)
        cls = 't-strong' if strong else ('t-muted' if i == 4 else '')
        if narrow:
            svg.text(x0, y - 10, lab, cls=cls, size=12)
        else:
            svg.text(x0 - 12, y + 4.2, lab, cls=cls, anchor='end', size=12.5)
        op = ' opacity=".45"' if i == 4 else ''
        svg.mark(f'{lab[0]}: {v:.2f} ({signed(v - d["base"])} over base)',
                 f'<line class="line l{idx}" x1="{sx(d["base"]):.1f}" y1="{y:.1f}" x2="{sx(v) - 6:.1f}" y2="{y:.1f}" stroke-width="3"{op}/>'
                 f'<path class="s{idx}" d="M{sx(v):.1f},{y:.1f} L{sx(v) - 9:.1f},{y - 5.5:.1f} L{sx(v) - 9:.1f},{y + 5.5:.1f} Z"{op}/>')
        svg.text(sx(v) + 8, y + 4.2, f'{v:.1f}', cls='t-strong' if strong else 't-muted', size=12)
        svg.text(sx(v) + 44, y + 4.2, signed(v - d['base']), cls='tx-blue' if strong else 't-faint', size=12, weight=700 if strong else None)
    return svg


# ============================================================================ opd-budget (from R1 inno)
def opd_budget_aes(W):
    """R1 three panels, polished: one legend, matching x ticks in every panel, (c) labelled at its ends."""
    b = OPD['budget']
    xs = [math.log2(t) for t in b['tokens']]
    tk, op, ft, fo, gap, se = b['takeover_40'], b['opd_40'], b['aime_finished_takeover_40'], b['aime_finished_opd_40'], b['gap_40'], b['gap_se_40']
    narrow = W < 500
    if narrow:
        H = 700
        A, B, C = (46, 58, W - 56, 226), (46, 296, W - 56, 436), (46, 506, W - 56, 646)
    else:
        H = 480
        A = (52, 54, W - 150, 232)
        B = (52, 306, W / 2 - 44, H - 54)
        C = (W / 2 + 56, 306, W - 150, H - 54)
    svg = Svg(W, H, 'Accuracy, the paired gap, and the share of AIME answers finished, against the evaluation budget')
    legend(svg, A[0], 18, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    ticks = [10, 11, 12, 13, 14, 15]
    sxA, syA = scale(10, 15, A[0], A[2]), scale(0, 50, A[3], A[1])
    ptitle(svg, A[0], A[1] - 14, 'a', T('Accuracy', '准确率'), T('4-benchmark average', '4 项平均'))
    axes(svg, A, sxA, syA, ticks, [0, 10, 20, 30, 40, 50], xfmt=k_fmt)
    gap_wash(svg, xs, tk, op, sxA, syA)
    lines(svg, [(2, list(zip(xs, op)), 'OPD'), (1, list(zip(xs, tk)), 'Scaffold-OPD')], sxA, syA, set(ticks),
          title_fn=lambda n, x, y: f'{n} · {int(round(2 ** x)):,} tokens: {y:.1f}')
    end_label(svg, sxA(15), syA(tk[-1]), f'{tk[-1]:.1f}' if narrow else f'Scaffold-OPD {tk[-1]:.1f}', 't-strong')
    end_label(svg, sxA(15), syA(op[-1]), f'{op[-1]:.1f}' if narrow else f'OPD {op[-1]:.1f}')
    sxB, syB = scale(10, 15, B[0], B[2]), scale(-5, 8, B[3], B[1])
    ptitle(svg, B[0], B[1] - 14, 'b', T('Paired gap', '配对差'), '±1 SE')
    axes(svg, B, sxB, syB, ticks, [-4, 0, 4, 8], xfmt=k_fmt, yfmt=lambda v: signed(v, 0) if v else '0')
    up = ' L'.join(f'{sxB(x):.1f},{syB(g + s):.1f}' for x, g, s in zip(xs, gap, se))
    lo = ' L'.join(f'{sxB(x):.1f},{syB(g - s):.1f}' for x, g, s in reversed(list(zip(xs, gap, se))))
    svg.path(f'M{up} L{lo} Z', 'wash1')
    svg.line(B[0], syB(0), B[2], syB(0), 'axis', 'stroke-dasharray="4 3"')
    lines(svg, [(1, list(zip(xs, gap)), 'gap')], sxB, syB, {13, 14, 15}, r=3.5)
    for t in (13, 14, 15):
        i = xs.index(t)
        svg.text(sxB(t), syB(gap[i] + se[i]) - 7, signed(gap[i]), cls='t-strong', anchor='middle', size=11)
    sxC, syC = scale(10, 15, C[0], C[2]), scale(0, 100, C[3], C[1])
    ptitle(svg, C[0], C[1] - 14, 'c', T('AIME answers finished', '写完的 AIME 回答'), '%')
    axes(svg, C, sxC, syC, ticks, [0, 50, 100], xfmt=k_fmt)
    lines(svg, [(2, list(zip(xs, fo)), 'OPD'), (1, list(zip(xs, ft)), 'Scaffold-OPD')], sxC, syC, {14, 15}, r=3.5,
          title_fn=lambda n, x, y: f'{n} · {int(round(2 ** x)):,} tokens: {y:.1f}% finished')
    i16 = xs.index(14)
    svg.text(sxC(14) - 7, syC(fo[i16]) - 6, f'{fo[i16]:.0f}', cls='t-strong', anchor='end', size=11)
    svg.text(sxC(14) + 7, syC(ft[i16]) + 14, f'{ft[i16]:.0f}', cls='t-strong', size=11)
    if not narrow:
        end_label(svg, sxC(15), syC(fo[-1]) - 4, 'OPD')
        end_label(svg, sxC(15), syC(ft[-1]) + 10, 'Scaffold-OPD', 't-strong')
    return svg


def opd_budget_inno(W):
    """R1 three panels tied together: the 16k–32k range is marked in every panel and annotated once."""
    svg = opd_budget_aes(W)
    narrow = W < 500
    if narrow:
        return svg
    b = OPD['budget']
    xs = [math.log2(t) for t in b['tokens']]
    A = (52, 54, W - 150, 232)
    sxA = scale(10, 15, A[0], A[2])
    svg.parts.insert(0, f'<rect class="band" x="{sxA(14):.1f}" y="{A[1]:.1f}" width="{sxA(15) - sxA(14):.1f}" height="{A[3] - A[1]:.1f}" rx="4"/>')
    syA = scale(0, 50, A[3], A[1])
    svg.text(sxA(14) - 8, syA(14), T('16k → 32k: OPD has finished', '16k → 32k：OPD 已写完'), cls='t-muted', anchor='end', size=11)
    svg.text(sxA(14) - 8, syA(14) + 15, T('its answers and stops rising;', '回答，不再提升；'), cls='t-muted', anchor='end', size=11)
    svg.text(sxA(14) - 8, syA(14) + 30, T('Scaffold-OPD keeps reasoning', 'Scaffold-OPD 还在继续推理'), cls='t-muted', anchor='end', size=11)
    return svg


# ============================================================================ opd-training (from R1 aes)
def opd_training_aes(W):
    """R1 two panels, polished: the share panel labels its start and end, the length panel its two end values."""
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
    ptitle(svg, bA[0], bA[1] - 16, 'a', T('Response length', '回答长度'), T('tokens, 5-step mean', 'token，5 步均值'))
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
    for x_, y_ in (ratio[0], ratio[-1]):
        svg.circle(sxB(x_), syB(y_), 4, 'dot s5')
    hit_points(svg, ratio, sxB, syB, lambda x, y: f'step {x}: {y:.1f}%', r=5)
    svg.text(sxB(ratio[0][0]) + 8, syB(ratio[0][1]) + 4, f'{ratio[0][1]:.0f}%', cls='t-strong', size=12)
    end_label(svg, sxB(60), syB(ratio[-1][1]), f'{ratio[-1][1]:.1f}%', 't-strong')
    return svg


def opd_training_inno(W):
    """(a) response length as before; (b) teacher tokens per answer instead of the share: flat at ~100–140 tokens
    while answers grow, which is why the share falls."""
    tr = OPD['train']
    tk = moving_avg([(s_, l) for s_, l in zip(tr['takeover']['step'], tr['takeover']['response_length']) if s_ != 19])
    op = moving_avg(list(zip(tr['opd']['step'], tr['opd']['response_length'])))
    t = tr['takeover']
    teach = moving_avg([(s_, v) for s_, v in zip(t['step'], t['teacher_tokens_per_answer']) if v is not None and s_ != 19])
    ratio = {s_: 100 * r_ for s_, r_ in zip(t['step'], t['teacher_token_ratio'])}
    narrow = W < 500
    if narrow:
        H = 500
        bA, bB = (52, 62, W - 64, 212), (52, 316, W - 64, 460)
    else:
        H = 300
        bA, bB = (56, 62, W / 2 - 70, H - 52), (W / 2 + 54, 62, W - 60, H - 52)
    svg = Svg(W, H, 'Response length, and the teacher-written tokens per answer in Scaffold-OPD')
    legend(svg, bA[0], 16, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    sxA, syA = scale(0, 60, bA[0], bA[2]), scale(0, 6000, bA[3], bA[1])
    ptitle(svg, bA[0], bA[1] - 16, 'a', T('Response length', '回答长度'), T('tokens', 'token'))
    axes(svg, bA, sxA, syA, [0, 20, 40, 60], [0, 2000, 4000, 6000], yfmt=lambda v: f'{v / 1000:.0f}k' if v else '0', xtitle=T('training step', '训练步'))
    lines(svg, [(2, op, 'OPD'), (1, tk, 'Scaffold-OPD')], sxA, syA, {60}, r=4, title_fn=lambda n, x, y: f'{n} · step {x}: {y:,.0f} tokens')
    end_label(svg, sxA(60), syA(tk[-1][1]), f'{tk[-1][1]:,.0f}', 't-strong')
    end_label(svg, sxA(60), syA(op[-1][1]), f'{op[-1][1]:,.0f}')
    sxB, syB = scale(0, 60, bB[0], bB[2]), scale(0, 200, bB[3], bB[1])
    ptitle(svg, bB[0], bB[1] - 16, 'b', T('Teacher tokens per answer', '每条回答的老师 token'), 'Scaffold-OPD')
    axes(svg, bB, sxB, syB, [0, 20, 40, 60], [0, 50, 100, 150, 200], xtitle=T('training step', '训练步'))
    area = polyline(teach, sxB, syB) + f' L{sxB(teach[-1][0]):.1f},{syB(0):.1f} L{sxB(teach[0][0]):.1f},{syB(0):.1f} Z'
    svg.path(area, 'fl-green')
    svg.path(polyline(teach, sxB, syB), 'line l5')
    svg.circle(sxB(teach[-1][0]), syB(teach[-1][1]), 4, 'dot s5')
    hit_points(svg, teach, sxB, syB, lambda x, y: f'step {x}: {y:.0f} teacher tokens per answer', r=5)
    end_label(svg, sxB(60), syB(teach[-1][1]), f'{teach[-1][1]:.0f}', 't-strong')
    s0 = sum(ratio[s_] for s_ in range(1, 6)) / 5
    s1 = sum(ratio[s_] for s_ in range(56, 61)) / 5
    svg.text(bB[2], bB[1] + 14, T(f'share of all tokens: {s0:.0f}% → {s1:.0f}%', f'占全部 token：{s0:.0f}% → {s1:.0f}%'), cls='t-muted', anchor='end', size=11.5)
    svg.text(bB[2], bB[1] + 30, T('(answers get ~3× longer)', '（回答变长约 3 倍）'), cls='t-faint', anchor='end', size=11)
    return svg


# ============================================================================ opd-compute (from R1 inno)
def _compute_bars(svg, W, narrow, with_scores=False):
    g, p = OPD['gpu_hours']['pipeline'], OPD['pipeline_avg4']
    alone_h, alone_s = OPD['gpu_hours']['takeover_40'], OPD['eval_avg4']['takeover_40']
    x0 = 150 if not narrow else 16
    x1 = W - (126 if not narrow else 22)
    sx = scale(0, 56, x0, x1)
    rows_y = (70, 150) if not narrow else (96, 196)
    segs = [(g['sft_incl_teacher_data'], 'pn-yellow', T('data + SFT', '数据 + SFT'), p['sft']),
            (g['takeover_40'], 'pn-blue', T('Scaffold-OPD', 'Scaffold-OPD'), p['takeover_40']),
            (g['grpo_30'], 'pn-orange', T('GRPO', 'GRPO'), p['grpo_30'])]
    for v in (0, 10, 20, 30, 40, 50):
        svg.line(sx(v), 44, sx(v), rows_y[1] + 34, 'grid')
        svg.line(sx(v), rows_y[1] + 34, sx(v), rows_y[1] + 38, 'axis')
        svg.text(sx(v), rows_y[1] + 52, str(v), cls='t-faint', anchor='middle', size=11)
    svg.line(x0, rows_y[1] + 34, sx(56), rows_y[1] + 34, 'axis')
    svg.text((x0 + x1) / 2, rows_y[1] + 70, T('training GPU-hours (2 × A100)', '训练卡时（2 × A100）'), cls='t-muted', anchor='middle', size=11.5)
    y = rows_y[0]
    if narrow:
        svg.text(x0, y - 22, T('Full pipeline', '全流程'), cls='t-strong', size=12.5)
    else:
        svg.text(x0 - 12, y + 20, T('Full pipeline', '全流程'), cls='t-strong', anchor='end', size=12.5)
    x = 0
    for hrs, cls, lab, score in segs:
        svg.mark(f'{lab[0]}: {hrs:.1f} GPU-hours, average {score:.1f} after it',
                 f'<rect class="{cls}" x="{sx(x) + 1:.1f}" y="{y:.1f}" width="{sx(x + hrs) - sx(x) - 2:.1f}" height="30" rx="6"/>')
        svg.text((sx(x) + sx(x + hrs)) / 2, y + 14, lab, cls='t-strong', anchor='middle', size=11 if not narrow else 9.5)
        svg.text((sx(x) + sx(x + hrs)) / 2, y + 26, f'{hrs:.1f} h', cls='t-muted', anchor='middle', size=10)
        if with_scores:
            svg.text(sx(x + hrs) - 4, y - 7, f'{score:.1f}', cls='t-strong' if cls == 'pn-orange' else 't-muted', anchor='end', size=11)
        x += hrs
    svg.text(sx(x) + 10, y + 20, f'→ {p["grpo_30"]:.1f}', cls='t-strong', size=13.5)
    y = rows_y[1]
    if narrow:
        svg.text(x0, y - 22, T('Scaffold-OPD alone', '只做 Scaffold-OPD'), cls='t-strong', size=12.5)
    else:
        svg.text(x0 - 12, y + 20, T('Scaffold-OPD alone', '只做 Scaffold-OPD'), cls='t-strong', anchor='end', size=12.5)
    svg.mark(f'Scaffold-OPD alone: {alone_h:.1f} GPU-hours', f'<rect class="pn-blue" x="{sx(0) + 1:.1f}" y="{y:.1f}" width="{sx(alone_h) - sx(0) - 2:.1f}" height="30" rx="6"/>')
    svg.text((sx(0) + sx(alone_h)) / 2, y + 20, f'{alone_h:.1f} h', cls='t-muted', anchor='middle', size=10.5)
    svg.text(sx(alone_h) + 10, y + 20, f'→ {alone_s:.1f}', cls='t-strong', size=13.5)
    total = x
    svg.path(f'M{sx(alone_h):.1f},{y - 8:.1f} V{y - 14:.1f} H{sx(total):.1f} V{y - 8:.1f}', 'leader')
    svg.text((sx(alone_h) + sx(total)) / 2, y - 18, T(f'{total / alone_h:.1f}× the GPU-hours for the same score', f'分数相同，卡时多 {total / alone_h:.1f} 倍'), cls='tx-blue', anchor='middle', size=11.5, weight=700)
    return svg


def opd_compute_aes(W):
    """R1 stacked bars, polished: GPU-hours written in each segment, the 4× gap bracketed, a real axis."""
    narrow = W < 500
    svg = Svg(W, 232 if not narrow else 290, 'Training GPU-hours of the full pipeline and of Scaffold-OPD alone, with the score each reached')
    return _compute_bars(svg, W, narrow)


def opd_compute_inno(W):
    """As the aesthetic version, plus the average after each pipeline stage written above the segment it closes."""
    narrow = W < 500
    svg = Svg(W, 232 if not narrow else 290, 'Training GPU-hours of the full pipeline (with the average after each stage) and of Scaffold-OPD alone')
    return _compute_bars(svg, W, narrow, with_scores=True)


# ============================================================================ scr-sft-rl (from R1 aes)
def scr_sft_rl_aes(W):
    """R1 dumbbells, polished: families ordered by success after SFT, every row's fraction after RL at the right."""
    narrow = W < 500
    if narrow:
        H = 496
        panels = [('seen', (100, 70, W - 64, 228)), ('unseen', (100, 310, W - 64, 468))]
    else:
        H = 290
        panels = [('seen', (130, 66, W / 2 - 66, H - 50)), ('unseen', (W / 2 + 96, 66, W - 66, H - 50))]
    svg = Svg(W, H, 'ALFWorld success by task family, after SFT and after 100 more steps of RL')
    chip_legend(svg, 14 if not narrow else 8, 18, [('s3', T('after SFT', 'SFT 后')), ('s1', T('after SFT + 100 RL steps', 'SFT + 100 步 RL 后'))])
    for k, (split, box) in enumerate(panels):
        a, b = V2.family_counts('sft', split), V2.family_counts('sft_gigpo_step100', split)
        order = sorted(V2.FAM_ORDER, key=lambda f: a[f][0] / a[f][1])
        sx = scale(0, 100, box[0], box[2])
        ptitle(svg, box[0], box[1] - 18, 'ab'[k], f'valid_{split}', T('success, %', '成功率，%'))
        for v in (25, 50, 75, 100):
            svg.line(sx(v), box[1] - 6, sx(v), box[3], 'grid')
        axes(svg, (box[0], box[1] - 6, box[2], box[3]), sx, lambda v: v, [0, 25, 50, 75, 100], [], grid=False)
        svg.text(box[2] + 40, box[1] - 18, T('solved', '解出'), cls='t-faint', anchor='end', size=10.5)
        pitch = (box[3] - box[1]) / len(order)
        for i, fam in enumerate(order):
            y = box[1] + i * pitch + pitch / 2 - 4
            key = fam == 'pick_two_obj_and_place'
            (sa, n), (sb, _) = a[fam], b[fam]
            pa, pb = 100 * sa / n, 100 * sb / n
            svg.text(box[0] - 10, y + 4, V2.FAM_NAMES[fam], cls='t-strong' if key else '', anchor='end', size=11.5)
            svg.line(sx(pa), y, sx(pb), y, 'line l1' if key else 'line l3', 'stroke-width="2.4"' + ('' if key else ' opacity=".55"'))
            svg.mark(f'{V2.FAM_NAMES[fam][0]}, {split}: {sa}/{n} after SFT → {sb}/{n} after RL',
                     f'<circle class="dot s3" cx="{sx(pa):.1f}" cy="{y:.1f}" r="4.5"/><circle class="dot s1" cx="{sx(pb):.1f}" cy="{y:.1f}" r="5"/>')
            svg.text(box[2] + 40, y + 4, f'{sa}→{sb}/{n}', cls='tx-blue' if key else 't-muted', anchor='end', size=11, weight=700 if key else None)
    return svg


def scr_sft_rl_inno(W):
    """Families sorted by gain, with the gain in points at the right; the two-object family leads."""
    narrow = W < 500
    if narrow:
        H = 496
        panels = [('seen', (100, 70, W - 60, 228)), ('unseen', (100, 310, W - 60, 468))]
    else:
        H = 290
        panels = [('seen', (130, 66, W / 2 - 60, H - 50)), ('unseen', (W / 2 + 96, 66, W - 60, H - 50))]
    svg = Svg(W, H, 'ALFWorld success by task family, after SFT and after 100 RL steps, sorted by the gain')
    chip_legend(svg, 14 if not narrow else 8, 18, [('s3', T('after SFT', 'SFT 后')), ('s1', T('after SFT + 100 RL steps', 'SFT + 100 步 RL 后'))])
    for k, (split, box) in enumerate(panels):
        a, b = V2.family_counts('sft', split), V2.family_counts('sft_gigpo_step100', split)
        gain = {f: 100 * (b[f][0] - a[f][0]) / a[f][1] for f in V2.FAM_ORDER}
        order = sorted(V2.FAM_ORDER, key=lambda f: -gain[f])
        sx = scale(0, 100, box[0], box[2])
        ptitle(svg, box[0], box[1] - 18, 'ab'[k], f'valid_{split}', T('success, %', '成功率，%'))
        for v in (25, 50, 75, 100):
            svg.line(sx(v), box[1] - 6, sx(v), box[3], 'grid')
        axes(svg, (box[0], box[1] - 6, box[2], box[3]), sx, lambda v: v, [0, 50, 100], [], grid=False)
        svg.text(box[2] + 34, box[1] - 18, T('gain', '提升'), cls='t-faint', anchor='end', size=10.5)
        pitch = (box[3] - box[1]) / len(order)
        for i, fam in enumerate(order):
            y = box[1] + i * pitch + pitch / 2 - 4
            key = fam == 'pick_two_obj_and_place'
            (sa, n), (sb, _) = a[fam], b[fam]
            pa, pb = 100 * sa / n, 100 * sb / n
            svg.text(box[0] - 10, y + 4, V2.FAM_NAMES[fam], cls='t-strong' if key else '', anchor='end', size=11.5)
            svg.line(sx(pa), y, sx(pb), y, 'line l1' if key else 'line l3', 'stroke-width="2.4"' + ('' if key else ' opacity=".55"'))
            svg.mark(f'{V2.FAM_NAMES[fam][0]}, {split}: {sa}/{n} → {sb}/{n}',
                     f'<circle class="dot s3" cx="{sx(pa):.1f}" cy="{y:.1f}" r="4.5"/><circle class="dot s1" cx="{sx(pb):.1f}" cy="{y:.1f}" r="5"/>')
            svg.text(box[2] + 34, y + 4, f'+{gain[fam]:.0f}', cls='tx-blue' if key else 't-muted', anchor='end', size=11.5, weight=700 if key else None)
    return svg


# ============================================================================ scr-vs-grpo (from R1 inno)
def _vs(W, summary=False, p_in_title=False):
    narrow = W < 500
    g = {k: run(ALF, 'gigpo', k) for k in ('seen', 'unseen')}
    r = {k: run(ALF, 'grpo', k) for k in ('seen', 'unseen')}
    disc = {k: PAIRED[f'alfworld_steplevel_vs_grpo:valid_{k}'] for k in ('seen', 'unseen')}
    if narrow:
        H = 740
        boxes = {'seen': ((44, 64, W - 56, 212), (44, 236, W - 56, 316)), 'unseen': ((44, 414, W - 56, 562), (44, 586, W - 56, 666))}
    else:
        H = 410 if not summary else 440
        boxes = {'seen': ((48, 64, W / 2 - 52, 224), (48, 250, W / 2 - 52, 344)), 'unseen': ((W / 2 + 54, 64, W - 46, 224), (W / 2 + 54, 250, W - 46, 344))}
    svg = Svg(W, H, 'StepCredit-RL vs GRPO: validation curves and the difference at every validation')
    legend(svg, 48, 16, [(1, 'StepCredit-RL'), (2, 'GRPO')])
    for k, (name, (A, B)) in enumerate(boxes.items()):
        sx = scale(0, 200, A[0], A[2])
        syA = scale(0, 100, A[3], A[1])
        if p_in_title:
            pv_ = float(disc[name]['p'])
            pv_s = f'{pv_:.3f}' if pv_ < 0.1 else f'{pv_:.2f}'
            ptitle(svg, A[0], A[1] - 14, 'ab'[k], f'valid_{name}', T(f'success, %  ·  step 200: p = {pv_s}', f'成功率，%  ·  第 200 步 p = {pv_s}'))
        else:
            ptitle(svg, A[0], A[1] - 14, 'ab'[k], f'valid_{name}', T('success, %', '成功率，%'))
        svg.rect(sx(160), A[1], sx(200) - sx(160), A[3] - A[1], 'band')
        axes(svg, A, sx, syA, [], [0, 25, 50, 75, 100])
        gap_wash(svg, [s_ for s_, _ in g[name]], [v for _, v in g[name]], [v for _, v in r[name]], sx, syA)
        lines(svg, [(2, r[name], 'GRPO'), (1, g[name], 'StepCredit-RL')], sx, syA, {200}, r=4, title_fn=lambda n, x, y: f'{n} · step {x}: {y:.1f}%')
        V2.end_labels(svg, [(sx(200) + 8, syA(g[name][-1][1]), f'{g[name][-1][1]:.1f}', 't-strong'),
                            (sx(200) + 8, syA(r[name][-1][1]), f'{r[name][-1][1]:.1f}', '')], min_gap=14)
        late_g = sum(v for s_, v in g[name] if s_ >= 160) / 5
        late_r = sum(v for s_, v in r[name] if s_ >= 160) / 5
        svg.text((sx(160) + sx(200)) / 2, A[1] + 13, f'{late_g:.1f} vs {late_r:.1f}', cls='t-muted', anchor='middle', size=10.5)
        syB = scale(-30, 40, B[3], B[1])
        axes(svg, B, sx, syB, [0, 50, 100, 150, 200], [-20, 0, 20, 40], yfmt=lambda v: signed(v, 0) if v else '0',
             xtitle=T('training step', '训练步') if narrow or True else None)
        svg.line(B[0], syB(0), B[2], syB(0), 'axis')
        bw = (B[2] - B[0]) / 23
        for (s_, a_), (_, b_) in zip(g[name], r[name]):
            d = a_ - b_
            cls = 's1' if d >= 0 else 's2'
            y0, y1 = (syB(d), syB(0)) if d >= 0 else (syB(0), syB(d))
            svg.mark(f'step {s_}: {signed(d)}', f'<rect class="{cls}" x="{sx(s_) - bw / 2:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(y1 - y0, 0.8):.1f}" rx="1.5"/>')
        svg.text(B[0] + 4, B[1] + 4, T('StepCredit-RL − GRPO, points', 'StepCredit-RL − GRPO（百分点）'), cls='t-faint', size=10.5)
        if summary:
            p_ = disc[name]
            pv = float(p_['p'])
            yy = B[3] + 54 if not narrow else B[3] + 50
            svg.text(A[0], yy, T(f'step 200: solved by only one run {p_["only_a"]} vs {p_["only_b"]},', f'第 200 步：只有一方解出 {p_["only_a"]} 对 {p_["only_b"]}，'), cls='t-muted', size=11.5)
            svg.text(A[2], yy, f'McNemar p = {pv:.3f}' if pv < 0.1 else f'McNemar p = {pv:.2f}', cls='tx-blue' if pv < 0.05 else 't-muted', anchor='end', size=11.5, weight=700 if pv < 0.05 else None)
    return svg


def scr_vs_grpo_aes(W):
    """R1 curves + difference bars, polished: late-stage band and means restored, axis titles, aligned panels."""
    return _vs(W)


def scr_vs_grpo_inno(W):
    """As the aesthetic version, plus the McNemar comparison at step 200 written under each split."""
    return _vs(W, summary=True)


# ============================================================================ scr-updates (from R1 inno)
def scr_updates_aes(W):
    """R1 bars, polished: shared scales per panel with ticks, the ratio written next to each pair."""
    narrow = W < 500
    four = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo_4upd']
    one = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo']
    thr = [50, 70]
    H = 268 if not narrow else 470
    svg = Svg(W, H, 'Training steps and hours needed to first reach 50% and 70% seen success, one vs four updates per step')
    legend(svg, 20, 16, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
    panels = [(0, T('Training steps', '训练步'), 160, [0, 50, 100, 150]), (2, T('Wall-clock hours', '耗时（小时）'), 32, [0, 10, 20, 30])]
    for k, (key, title, xmax, ticks) in enumerate(panels):
        if narrow:
            x0, x1, ytop = 70, W - 60, 64 + k * 206
        else:
            x0, x1, ytop = 100 + k * (W / 2), W / 2 - 50 + k * (W / 2), 64
        sx = scale(0, xmax, x0, x1)
        ptitle(svg, x0, ytop - 16, 'ab'[k], title, T('to first reach the level', '首次达到该水平'))
        bottom = ytop + 150
        for v in ticks:
            svg.line(sx(v), ytop - 2, sx(v), bottom, 'grid')
        axes(svg, (x0, ytop - 2, x1, bottom), sx, lambda v: v, ticks, [], grid=False)
        for i, t_ in enumerate(thr):
            yy = ytop + 12 + i * 70
            svg.text(x0 - 10, yy + 24, f'≥ {t_}%', cls='t-strong', anchor='end', size=12)
            vals = []
            for j, (rows, cls, nm) in enumerate([(four, 's1', '4 updates'), (one, 's3', '1 update')]):
                row = R1._first_reach(rows, t_, key)
                y = yy + j * 21
                v = row[key]
                vals.append(v)
                svg.mark(f'{nm}: reaches {t_}% at step {row[0]} ({row[2]:.1f} h)', f'<path class="bar {cls}" d="{hbar(x0, y, sx(v), 15, 4)}"/>')
                svg.text(sx(v) + 6, y + 12, f'{v:.0f}' if key == 0 else f'{v:.1f} h', cls='t-strong' if j == 0 else 't-muted', size=11.5)
            svg.text(x1 + (4 if not narrow else 0), yy + 24, f'{vals[1] / vals[0]:.1f}×', cls='tx-blue', anchor='end' if narrow else 'start', size=12.5, weight=700)
    return svg


def scr_updates_inno(W):
    """Dumbbells: for each target level, the step at which each setting first reaches it, joined by the saving."""
    narrow = W < 500
    four = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo_4upd']
    one = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo']
    thr = [30, 40, 50, 60, 70]
    H = 300 if not narrow else 330
    x0, x1 = (90, W - 120) if not narrow else (64, W - 40)
    svg = Svg(W, H, 'Training step at which each setting first reaches 30–70% seen success')
    legend(svg, 20, 16, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
    top, bottom = 52, H - 52
    sx = scale(0, 160, x0, x1)
    for v in (0, 50, 100, 150):
        svg.line(sx(v), top - 8, sx(v), bottom, 'grid')
    axes(svg, (x0, top - 8, x1, bottom), sx, lambda v: v, [0, 50, 100, 150], [], grid=False, xtitle=T('training step at which the level is first reached', '首次达到该水平时的训练步'))
    pitch = (bottom - top) / len(thr)
    for i, t_ in enumerate(thr):
        y = top + i * pitch + pitch / 2 - 4
        a_ = R1._first_reach(four, t_, 0)[0]
        b_ = R1._first_reach(one, t_, 0)[0]
        svg.text(x0 - 10, y + 4, f'≥ {t_}%', cls='t-strong', anchor='end', size=12)
        svg.line(sx(a_), y, sx(b_), y, 'line l3', 'stroke-width="2.4" opacity=".6"')
        svg.mark(f'≥ {t_}%: 4 updates at step {a_}, 1 update at step {b_}',
                 f'<circle class="dot s1" cx="{sx(a_):.1f}" cy="{y:.1f}" r="5"/><circle class="dot s3" cx="{sx(b_):.1f}" cy="{y:.1f}" r="4.5"/>')
        if not narrow:
            svg.text(x1 + 12, y + 4, T(f'{b_ / a_:.1f}× fewer steps', f'步数少 {b_ / a_:.1f} 倍'), cls='tx-blue', size=11.5, weight=700)
        else:
            svg.text(x1 + 2, y - 8, f'{b_ / a_:.1f}×', cls='tx-blue', anchor='end', size=11, weight=700)
    return svg


# ============================================================================ scr-hotpotqa (from R1 inno)
def scr_hotpotqa_aes(W, label_frac=0.5):
    """R1 small multiples, polished: markers at every validation, McNemar p under EM, the −71% marked on repeats.
    label_frac places the −71% between the two end values (0.5 = midway; round 3 moves it up, clear of the line)."""
    narrow = W < 500
    em = {k: run(HPQ, 'em', k) for k in ('em', 'f1', 'repeat_queries')}
    sh = {k: run(HPQ, 'shaped', k) for k in ('em', 'f1', 'repeat_queries')}
    specs = [('em', T('Exact match', 'EM'), '%', (40, 60), [40, 50, 60], lambda v: f'{v:.0f}'),
             ('f1', T('Token F1', 'Token F1'), '', (0.55, 0.75), [0.55, 0.65, 0.75], lambda v: f'{v:.2f}'),
             ('repeat_queries', T('Repeated queries', '重复查询'), T('per question', '每题'), (0, 0.2), [0, 0.1, 0.2], lambda v: f'{v:.1f}' if v else '0')]
    H = 300 if not narrow else 800
    svg = Svg(W, H, 'HotpotQA: exact match, F1 and repeated queries under the EM reward and the shaped reward')
    legend(svg, 48, 16, [(1, T('EM reward', 'EM 奖励')), (2, T('shaped reward', '稠密奖励'))])
    p_ = PAIRED['hotpotqa_em_vs_shaped:all']
    for k, (key, title, unit, (lo, hi), ticks, fmt) in enumerate(specs):
        if narrow:
            box = (56, 70 + k * 246, W - 72, 70 + k * 246 + 160)
        else:
            pw = (W - 60) / 3
            box = (56 + k * pw, 70, 56 + k * pw + pw - 80, H - 64)
        sx, sy = scale(0, 200, box[0], box[2]), scale(lo, hi, box[3], box[1])
        ptitle(svg, box[0], box[1] - 16, 'abc'[k], title, unit or None)
        axes(svg, box, sx, sy, [0, 100, 200], ticks, yfmt=fmt, xtitle=T('step', '步'))
        if key != 'repeat_queries':
            gap_wash(svg, [s_ for s_, _ in em[key]], [v for _, v in em[key]], [v for _, v in sh[key]], sx, sy)
        lines(svg, [(2, sh[key], 'shaped'), (1, em[key], 'EM reward')], sx, sy, None, r=2.6, title_fn=lambda n, x, y: f'{n} · step {x}: {y}')
        a_, b_ = em[key][-1][1], sh[key][-1][1]
        f = (lambda v: f'{v:.1f}') if key == 'em' else (lambda v: f'{v:.3f}')
        hi_first = a_ >= b_
        end_label(svg, sx(200), sy(a_) + (-3 if hi_first else 7), f(a_), 't-strong' if key != 'repeat_queries' else '')
        end_label(svg, sx(200), sy(b_) + (7 if hi_first else -3), f(b_), 't-strong' if key == 'repeat_queries' else '')
        if key == 'em':
            svg.text(box[2], sy(lo) - 8, f'McNemar p = {float(p_["p"]):.2f}', cls='t-faint', anchor='end', size=10.5)
        if key == 'repeat_queries':
            ya, yb = sy(a_), sy(b_)
            xl = sx(200) - 6
            svg.line(xl, ya + 6, xl, yb - 6, 'leader')
            svg.text(xl - 5, ya + (yb - ya) * (1 - label_frac) + 4, signed(100 * (b_ - a_) / a_, 0) + '%', cls='tx-orange', anchor='end', size=12, weight=700)
    return svg


def scr_hotpotqa_inno(W):
    """Small multiples plus a fourth column that reads the result off: shaped minus EM reward at step 200."""
    narrow = W < 500
    if narrow:
        return scr_hotpotqa_aes(W)
    em = {k: run(HPQ, 'em', k)[-1][1] for k in ('em', 'f1', 'repeat_queries')}
    sh = {k: run(HPQ, 'shaped', k)[-1][1] for k in ('em', 'f1', 'repeat_queries')}
    svg = Svg(W, 236, 'HotpotQA at step 200: change from the EM reward to the shaped reward, relative to the EM reward')
    legend(svg, 48, 16, [(2, T('shaped reward, relative to the EM reward', '稠密奖励相对 EM 奖励的变化'))])
    rows = [(T('Exact match', 'EM'), em['em'], sh['em'], 'pt'), (T('Token F1', 'Token F1'), em['f1'], sh['f1'], 'rel'), (T('Repeated queries', '重复查询'), em['repeat_queries'], sh['repeat_queries'], 'rel')]
    x0, x1 = 230, W - 140
    sx = scale(-80, 20, x0, x1)
    for v in (-80, -60, -40, -20, 0, 20):
        svg.line(sx(v), 44, sx(v), 196, 'grid' if v else 'axis')
        svg.text(sx(v), 212, f'{v:+d}%' if v else '0', cls='t-faint', anchor='middle', size=11)
    for i, (lab, a_, b_, kind) in enumerate(rows):
        y = 70 + i * 46
        rel = 100 * (b_ - a_) / a_
        svg.text(x0 - 14, y + 4, lab, cls='t-strong', anchor='end', size=12.5)
        x_a, x_b = (sx(0), sx(rel)) if rel < 0 else (sx(0), sx(rel))
        cls = 's2' if rel < 0 else 's1'
        svg.mark(f'{lab[0]}: {a_} → {b_} ({rel:+.1f}%)', f'<rect class="{cls}" x="{min(x_a, x_b):.1f}" y="{y - 9:.1f}" width="{abs(x_b - x_a):.1f}" height="18" rx="4"/>')
        val = f'{a_:.1f} → {b_:.1f}' if kind == 'pt' else f'{a_:.3f} → {b_:.3f}'
        svg.text(x1 + 10, y + 4, val, cls='t-muted', size=11.5)
        svg.text(min(x_a, x_b) - 6, y + 4, f'{rel:+.0f}%'.replace('-', '−'), cls='t-strong', anchor='end', size=12)
    return svg


AES = {'opd-methods': opd_methods_aes, 'opd-budget': opd_budget_aes, 'opd-training': opd_training_aes, 'opd-compute': opd_compute_aes,
       'scr-sft-rl': scr_sft_rl_aes, 'scr-vs-grpo': scr_vs_grpo_aes, 'scr-updates': scr_updates_aes, 'scr-hotpotqa': scr_hotpotqa_aes}
INNO = {'opd-methods': opd_methods_inno, 'opd-budget': opd_budget_inno, 'opd-training': opd_training_inno, 'opd-compute': opd_compute_inno,
        'scr-sft-rl': scr_sft_rl_inno, 'scr-vs-grpo': scr_vs_grpo_inno, 'scr-updates': scr_updates_inno, 'scr-hotpotqa': scr_hotpotqa_inno}
