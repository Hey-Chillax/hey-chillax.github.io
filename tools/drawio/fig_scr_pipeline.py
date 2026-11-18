"""StepCredit-RL full pipeline: expert demonstrations -> SFT -> multi-turn RL (StepCredit-RL) -> paired evaluation,
with ALFWorld success (seen / unseen) after each stage.

Variants: r1a / r1i / r1m, r2a / r2i / r2m, r3a / r3i / r3m; rounds 4-6 (r4a ... r6m) English only; final: r6m.
Facts (projects/stepcredit-rl.html, tools/data/alfworld_val.csv): the planner expert solves 2,145 of 3,553 training
games (60.4%) within 20 steps, giving 22,810 step examples; SFT with the loss only on tool calls, one epoch (356 steps,
about 1.4 h; data generation about 40 min more); RL 100 steps, 16 tasks x 8 rollouts per step, asynchronous vLLM
rollouts; greedy validation and an exact McNemar test on the same tasks. Success: base 7.1 / 2.2, after SFT 67.1 / 67.2,
RL step 20 98.6 / 91.0, step 100 98.6 / 94.0 (14.4 h into RL).
"""
from dlib import Fig, INK, LEMON, MUTED, SKY, SLATE, WHITE, label_w, TIMES

WIDTH = 720
LABEL = ('StepCredit-RL pipeline: expert demonstrations, SFT, multi-turn RL with StepCredit-RL and paired evaluation, '
         'with ALFWorld success after each stage')
LABEL_ZH = 'StepCredit-RL 全流程：专家示范、SFT、用 StepCredit-RL 的多轮 RL、配对评测，标出每段之后的 ALFWorld 成功率'


def T(lang, en, zh):
    return zh if lang == 'zh' else en


def two_line(title, sub, size=13, sub_size=11.5):
    return f'<b>{title}</b><br><span style="font-size:{sub_size}px;color:{MUTED};">{sub}</span>'


def stages(lang):
    return [
        (T(lang, 'Expert Demonstrations', '专家示范'), T(lang, '2,145 of 3,553 games solved', '解出 2,145 / 3,553 局'), LEMON, 'soft'),
        ('SFT', T(lang, 'Loss on tool calls · 1 epoch', '只在工具调用上算 loss · 1 轮'), SKY, 'soft'),
        (T(lang, 'Multi-Turn RL', '多轮 RL'), T(lang, 'StepCredit-RL · 100 steps', 'StepCredit-RL · 100 步'), SKY, 'fill'),
        (T(lang, 'Paired Evaluation', '配对评测'), T(lang, 'Same tasks · McNemar test', '同一批任务 · McNemar 检验'), SLATE, 'soft'),
    ]


def layout(lang, gap=18):
    st = stages(lang)
    need = [max(label_w(t, 13, True), label_w(s_, 11.5)) + 26 for t, s_, _, _ in st]
    extra = (WIDTH - 12 - 3 * gap - sum(need)) / 4
    ws = [n + extra for n in need]
    xs = [6 + sum(ws[:i]) + i * gap for i in range(4)]
    return st, xs, ws


def stage_row(f, st, xs, ws, y, h, gap):
    for i, (title, sub, pal, tone) in enumerate(st):
        key = i == 2
        f.box(xs[i], y, ws[i], h, fill=pal[tone], stroke=pal['line'], width=1.8 if key else 1.2, label=two_line(title, sub), size=13)
        if i:
            f.edge([(xs[i] - gap + 1, y + h / 2), (xs[i] - 1, y + h / 2)], width=1.2, end=5)


def build_a(lang):
    f = Fig(WIDTH, 168, LABEL)
    gap = 18
    st, xs, ws = layout(lang, gap)
    y, h = 10, 56
    stage_row(f, st, xs, ws, y, h, gap)
    ys = y + h + 32
    f.text(xs[0] + 4, ys, T(lang, 'ALFWorld success, seen / unseen (%)', 'ALFWorld 成功率，seen / unseen（%）'), size=12, color=MUTED)
    f.text(xs[0] + 4, ys + 26, T(lang, 'Base model 7.1 / 2.2', '基座 7.1 / 2.2'), size=12, color=MUTED)
    for i, val, note, key in ((1, '67.1 / 67.2', T(lang, 'After SFT', 'SFT 后'), False),
                              (2, '98.6 / 94.0', T(lang, 'Already 98.6 / 91.0 at step 20', '第 20 步已达 98.6 / 91.0'), True)):
        cx = xs[i] + ws[i] / 2
        f.line([(cx, y + h + 1), (cx, ys - 13)], color=SLATE['tok'], width=1, dashed=True, dash='2 2')
        f.cbox(cx, ys, 104, 24, fill=SKY['fill'] if key else WHITE, stroke=SKY['line'] if key else SLATE['line'],
               width=1.6 if key else 1.1, arc=12, label=f'<b>{val}</b>', size=13.5)
        f.text(cx, ys + 26, note, size=11.5, color=SKY['dark'] if key else MUTED, anchor='c')
    cx = xs[3] + ws[3] / 2
    f.text(cx, ys, T(lang, 'Per-task results', '逐任务记录结果'), size=12, color=MUTED, anchor='c')
    return f


def minibars(f, x, y, w, seen, unseen, key):
    """Seen (solid) and unseen (outlined) success as two thin bars, value at the right."""
    for k, (v, solid) in enumerate(((seen, True), (unseen, False))):
        yy = y + k * 14
        f.box(x, yy - 4, w, 8, fill=SLATE['soft'], stroke='none', width=0, arc=4)
        f.box(x, yy - 4, w * v / 100, 8, fill=SKY['tok'] if solid else WHITE, stroke=SKY['line'], width=1, arc=4)
        f.text(x + w + 6, yy, f'{v:.1f}', size=11.5, color=INK, bold=key)


def build_i(lang):
    """Model states with seen / unseen micro-bars under the stages, and the wall-clock time of each stage."""
    f = Fig(WIDTH, 196, LABEL)
    gap = 18
    st, xs, ws = layout(lang, gap)
    y, h = 10, 56
    stage_row(f, st, xs, ws, y, h, gap)
    yb = y + h + 34
    f.text(xs[0] + 4, yb - 2, T(lang, 'Base model', '基座'), size=12, color=MUTED)
    minibars(f, xs[0] + 4, yb + 16, ws[0] - 52, 7.1, 2.2, False)
    for i, (s_, u_, key) in ((1, (67.1, 67.2, False)), (2, (98.6, 94.0, True))):
        f.text(xs[i] + 4, yb - 2, T(lang, 'After SFT', 'SFT 后') if i == 1 else T(lang, 'After 100 RL steps', '100 步 RL 后'), size=12, color=MUTED)
        minibars(f, xs[i] + 4, yb + 16, ws[i] - 52, s_, u_, key)
    times = [(0, T(lang, '≈ 40 min to generate', '生成约 40 分钟')), (1, T(lang, '≈ 1.4 h', '约 1.4 小时')), (2, T(lang, '14.4 h (98.6 / 91.0 at 3.5 h)', '14.4 小时（3.5 小时时 98.6 / 91.0）'))]
    for i, t in times:
        f.text(xs[i] + 4, yb + 52, t, size=11.5, color=MUTED)
    swatch_legend(f, xs[3] + 4, yb - 2, lang)          # round-1 innovative kept as drawn, but with drawn swatches
    return f


def swatch_legend(f, x, y, lang):
    f.box(x, y - 4, 18, 8, fill=SKY['tok'], stroke=SKY['line'], width=1, arc=4)
    x0, x1 = f.text(x + 24, y, 'seen', size=12, color=MUTED)
    f.box(x1 + 12, y - 4, 18, 8, fill=WHITE, stroke=SKY['line'], width=1, arc=4)
    f.text(x1 + 36, y, 'unseen', size=12, color=MUTED)


def build_m(lang):
    """Round-1 merge: the stage row, seen / unseen micro-bars under the model states, proper swatches, wall-clock time."""
    f = Fig(WIDTH, 196, LABEL)
    gap = 18
    st, xs, ws = layout(lang, gap)
    y, h = 10, 56
    stage_row(f, st, xs, ws, y, h, gap)
    yb = y + h + 32
    heads = [T(lang, 'Base model', '基座'), T(lang, 'After SFT', 'SFT 后'), T(lang, 'After 100 RL steps', '100 步 RL 后')]
    vals = [(7.1, 2.2), (67.1, 67.2), (98.6, 94.0)]
    times = [T(lang, 'demos: ≈ 40 min', '生成示范约 40 分钟'), T(lang, '≈ 1.4 h', '约 1.4 小时'),
             T(lang, '14.4 h · 98.6 / 91.0 by step 20', '14.4 小时 · 第 20 步已达 98.6 / 91.0')]
    for i in range(3):
        f.text(xs[i] + 4, yb, heads[i], size=12, color=MUTED, bold=False)
        minibars(f, xs[i] + 4, yb + 20, ws[i] - 56, *vals[i], i == 2)
        f.text(xs[i] + 4, yb + 56, times[i], size=11.5, color=MUTED)
    f.text(xs[3] + 4, yb, T(lang, 'ALFWorld success (%)', 'ALFWorld 成功率（%）'), size=12, color=MUTED)
    swatch_legend(f, xs[3] + 4, yb + 20, lang)
    f.text(xs[3] + 4, yb + 56, T(lang, 'Time on 2 × A100', '2 张 A100 上的耗时'), size=11.5, color=MUTED)
    return f


def build_r2(lang, two_obj=False):
    """Round 2: the merged layout polished (a step-20 tick on the RL bars); with two_obj, a row for the two-object
    task, which the expert rarely solves (55 of 813 games) and RL lifts from 27% to 95% (seen and unseen together)."""
    H = 232 if two_obj else 196
    f = Fig(WIDTH, H, LABEL)
    gap = 18
    st, xs, ws = layout(lang, gap)
    y, h = 8, 56
    stage_row(f, st, xs, ws, y, h, gap)
    yb = y + h + 30
    heads = [T(lang, 'Base model', '基座'), T(lang, 'After SFT', 'SFT 后'), T(lang, 'After 100 RL steps', '100 步 RL 后')]
    vals = [(7.1, 2.2), (67.1, 67.2), (98.6, 94.0)]
    for i in range(3):
        f.text(xs[i] + 4, yb, heads[i], size=12, color=MUTED)
        bw = ws[i] - 56
        minibars(f, xs[i] + 4, yb + 20, bw, *vals[i], i == 2)
        if i == 2:
            xt = xs[i] + 4 + bw * 91.0 / 100
            f.line([(xt, yb + 27), (xt, yb + 41)], color=INK, width=1.4)
    times = [T(lang, 'demos: ≈ 40 min', '生成示范约 40 分钟'), T(lang, '≈ 1.4 h', '约 1.4 小时'),
             T(lang, '14.4 h · | 91.0 unseen at step 20', '14.4 小时 · | 第 20 步 unseen 91.0')]
    for i in range(3):
        f.text(xs[i] + 4, yb + 56, times[i], size=11.5, color=MUTED)
    f.text(xs[3] + 4, yb, T(lang, 'ALFWorld success (%)', 'ALFWorld 成功率（%）'), size=12, color=MUTED)
    swatch_legend(f, xs[3] + 4, yb + 20, lang)
    f.text(xs[3] + 4, yb + 56, T(lang, 'Time on 2 × A100', '2 张 A100 上的耗时'), size=11.5, color=MUTED)
    if two_obj:
        y2 = yb + 88
        f.line([(xs[0], y2 - 14), (WIDTH - 6, y2 - 14)], color=SLATE['tok'], width=1, dashed=True, dash='3 3')
        f.text(xs[0] + 4, y2, T(lang, 'Two-object task (the expert solves 55 of 813)', '双物体任务（专家只解出 813 局中的 55 局）'), size=12, color=MUTED)
        for i, v in ((1, 27), (2, 95)):
            bw = ws[i] - 56
            f.box(xs[i] + 4, y2 - 4, bw, 8, fill=SLATE['soft'], stroke='none', width=0, arc=4)
            f.box(xs[i] + 4, y2 - 4, bw * v / 100, 8, fill=SKY['line'] if i == 2 else SKY['tok'], stroke=SKY['line'], width=1, arc=4)
            f.text(xs[i] + 4 + bw + 6, y2, f'{v}%', size=11.5, bold=(i == 2))
    return f


def build_r2m(lang, final_polish=False):
    """Round-2 merge: one bar scale for every column, step 20 written out, the two-object row with a two-line label."""
    f = Fig(WIDTH, 238, LABEL)
    gap = 18
    st, xs, ws = layout(lang, gap)
    y, h = 8, 56
    stage_row(f, st, xs, ws, y, h, gap)
    yb = y + h + 30
    bw = min(ws[:3]) - 58
    heads = [T(lang, 'Base model', '基座'), T(lang, 'After SFT', 'SFT 后'), T(lang, 'After 100 RL steps', '100 步 RL 后')]
    vals = [(7.1, 2.2), (67.1, 67.2), (98.6, 94.0)]
    times = [T(lang, 'demos: ≈ 40 min', '生成示范约 40 分钟'), T(lang, '≈ 1.4 h', '约 1.4 小时'),
             T(lang, '14.4 h · step 20: 98.6 / 91.0', '14.4 小时 · 第 20 步 98.6 / 91.0')]
    for i in range(3):
        f.text(xs[i] + 4, yb, heads[i], size=12, color=MUTED)
        minibars(f, xs[i] + 4, yb + 20, bw, *vals[i], i == 2)
        f.text(xs[i] + 4, yb + 56, times[i], size=11.5, color=MUTED)
    f.text(xs[3] + 4, yb, T(lang, 'ALFWorld success (%)', 'ALFWorld 成功率（%）'), size=12, color=MUTED)
    swatch_legend(f, xs[3] + 4, yb + 20, lang)
    f.text(xs[3] + 4, yb + 56, T(lang, 'Time on 2 × A100', '2 张 A100 上的耗时'), size=11.5, color=MUTED)
    y2 = yb + 98
    f.line([(xs[0], y2 - 22), (WIDTH - 6, y2 - 22)], color=SLATE['tok'], width=1, dashed=True, dash='3 3')
    f.text(xs[0] + 4, y2, T(lang, 'Two-object task<br>the expert solves 55 of 813', '双物体任务<br>专家只解出 813 局中的 55 局'), size=12, color=MUTED, lh=1.3)
    for i, v in ((1, 27), (2, 95)):
        f.box(xs[i] + 4, y2 - 4, bw, 8, fill=SLATE['soft'], stroke='none', width=0, arc=4)
        f.box(xs[i] + 4, y2 - 4, bw * v / 100, 8, fill=SKY['line'] if i == 2 else SKY['tok'], stroke=SKY['line'], width=1, arc=4)
        f.text(xs[i] + 4 + bw + 6, y2, f'{v}%', size=11.5, bold=(i == 2))
    f.text(xs[3] + 4, y2, T(lang, 'Seen and unseen together', 'seen 与 unseen 合计'), size=11.5, color=MUTED)
    return f


def build_r3(lang, takeaway=False):
    """Round 3: r2m with every number checked against the page and the data (SFT about 1.4 h; RL 14.4 h to step 100,
    98.6 / 91.0 at step 20), no time for the base column, the bottom trimmed; with takeaway, the two-object row ends
    with the page's lesson instead of the seen + unseen note (moved into the row label)."""
    f = Fig(WIDTH, 222, LABEL)
    gap = 18
    st, xs, ws = layout(lang, gap)
    y, h = 8, 56
    stage_row(f, st, xs, ws, y, h, gap)
    yb = y + h + 30
    bw = min(ws[:3]) - 58
    heads = [T(lang, 'Base model', '基座'), T(lang, 'After SFT', 'SFT 后'), T(lang, 'After 100 RL steps', '100 步 RL 后')]
    vals = [(7.1, 2.2), (67.1, 67.2), (98.6, 94.0)]
    times = [None, T(lang, '≈ 1.4 h', '约 1.4 小时'), T(lang, '14.4 h · step 20: 98.6 / 91.0', '14.4 小时 · 第 20 步 98.6 / 91.0')]
    for i in range(3):
        f.text(xs[i] + 4, yb, heads[i], size=12, color=MUTED)
        minibars(f, xs[i] + 4, yb + 20, bw, *vals[i], i == 2)
        if times[i]:
            f.text(xs[i] + 4, yb + 56, times[i], size=11.5, color=MUTED)
    f.text(xs[3] + 4, yb, T(lang, 'ALFWorld success (%)', 'ALFWorld 成功率（%）'), size=12, color=MUTED)
    swatch_legend(f, xs[3] + 4, yb + 20, lang)
    f.text(xs[3] + 4, yb + 56, T(lang, f'training time, 2 {TIMES} A100', f'训练耗时，2 {TIMES} A100'), size=11.5, color=MUTED)
    y2 = yb + 98
    f.line([(xs[0], y2 - 22), (WIDTH - 6, y2 - 22)], color=SLATE['tok'], width=1, dashed=True, dash='3 3')
    if takeaway:
        lab = T(lang, 'Two-object task, seen + unseen<br>the expert solves 55 of 813', '双物体任务，seen + unseen<br>专家只解出 813 局中的 55 局')
    else:
        lab = T(lang, 'Two-object task<br>the expert solves 55 of 813', '双物体任务<br>专家只解出 813 局中的 55 局')
    f.text(xs[0] + 4, y2, lab, size=12, color=MUTED, lh=1.3)
    for i, v in ((1, 27), (2, 95)):
        f.box(xs[i] + 4, y2 - 4, bw, 8, fill=SLATE['soft'], stroke='none', width=0, arc=4)
        f.box(xs[i] + 4, y2 - 4, bw * v / 100, 8, fill=SKY['line'] if i == 2 else SKY['tok'], stroke=SKY['line'], width=1, arc=4)
        f.text(xs[i] + 4 + bw + 6, y2, f'{v}%', size=11.5, bold=(i == 2))
    if takeaway:
        f.text(xs[3] + 4, y2, T(lang, 'RL covers what the<br>demonstrations miss', 'RL 补上示范<br>覆盖不到的部分'), size=12,
               color=SKY['dark'], bold=True, lh=1.3)
    else:
        f.text(xs[3] + 4, y2, T(lang, 'Seen and unseen together', 'seen 与 unseen 合计'), size=11.5, color=MUTED)
    return f


def build(v, lang):
    if v[:2] in ('r4', 'r5', 'r6'):
        return {'r4a': build4a, 'r4i': build4i, 'r4m': build4m, 'r5a': build5a, 'r5i': build5i,
                'r5m': lambda: build5a(named=True), 'r6a': build6, 'r6i': lambda: build6(times_in_boxes=True),
                'r6m': build6}[v]()
    if v in ('r3a', 'r3i', 'r3m'):
        return build_r3(lang, takeaway=(v != 'r3a'))
    if v == 'r1i':
        return build_i(lang)
    if v == 'r1a':
        return build_a(lang)
    if v == 'r1m':
        return build_m(lang)
    if v == 'r2a':
        return build_r2(lang, False)
    if v == 'r2i':
        return build_r2(lang, True)
    return build_r2m(lang)


# ------------------------------------------------------------------ rounds 4-6 (English only)
VALS = [(7.1, 2.2), (67.1, 67.2), (98.6, 94.0)]


def minibars4(f, x, y, w, seen, unseen, pal, key, gap=15):
    for k, (v, solid) in enumerate(((seen, True), (unseen, False))):
        yy = y + k * gap
        f.box(x, yy - 4.5, w, 9, fill=SLATE['soft'], stroke='none', width=0, arc=4.5)
        f.box(x, yy - 4.5, w * v / 100, 9, fill=pal['tok'] if solid else WHITE, stroke=pal['line'], width=1, arc=4.5)
        f.text(x + w + 6, yy, f'{v:.1f}', size=12, color=INK, bold=key)


def build4a():
    """Round-4 aesthetic: r3m with the base model drawn in neutral grey (it is the starting point, not the product of
    the expert-demonstration stage), slightly thicker bars, and one row rhythm for heads, bars, notes."""
    H = 226
    f = Fig(WIDTH, H, LABEL)
    gap = 18
    st, xs, ws = layout('en', gap)
    y, h = 8, 56
    stage_row(f, st, xs, ws, y, h, gap)
    yb = y + h + 30
    bw = min(ws[:3]) - 60
    heads = ['Base model', 'After SFT', 'After 100 RL steps']
    times = [None, '≈ 1.4 h', '14.4 h · step 20: 98.6 / 91.0']
    for i in range(3):
        f.text(xs[i] + 4, yb, heads[i], size=12.5, color=MUTED if i == 0 else INK, bold=(i > 0))
        minibars4(f, xs[i] + 4, yb + 22, bw, *VALS[i], SLATE if i == 0 else SKY, i == 2)
        if times[i]:
            f.text(xs[i] + 4, yb + 58, times[i], size=12, color=MUTED)
    f.text(xs[3] + 4, yb, 'ALFWorld success (%)', size=12.5, color=MUTED)
    sx = xs[3] + 4
    f.box(sx, yb + 22 - 4.5, 18, 9, fill=SKY['tok'], stroke=SKY['line'], width=1, arc=4.5)
    x0, x1 = f.text(sx + 24, yb + 22, 'seen', size=12, color=MUTED)
    f.box(x1 + 12, yb + 22 - 4.5, 18, 9, fill=WHITE, stroke=SKY['line'], width=1, arc=4.5)
    f.text(x1 + 36, yb + 22, 'unseen', size=12, color=MUTED)
    f.text(xs[3] + 4, yb + 58, f'Training time, 2 {TIMES} A100', size=12, color=MUTED)
    y2 = yb + 104
    f.line([(xs[0], y2 - 24), (WIDTH - 6, y2 - 24)], color=SLATE['tok'], width=1, dashed=True, dash='3 3')
    f.text(xs[0] + 4, y2, 'Two-object task, seen + unseen<br>the expert solves 55 of 813', size=12, color=MUTED, lh=1.3)
    for i, v in ((1, 27), (2, 95)):
        f.box(xs[i] + 4, y2 - 4.5, bw, 9, fill=SLATE['soft'], stroke='none', width=0, arc=4.5)
        f.box(xs[i] + 4, y2 - 4.5, bw * v / 100, 9, fill=SKY['line'] if i == 2 else SKY['tok'], stroke=SKY['line'], width=1, arc=4.5)
        f.text(xs[i] + 4 + bw + 6, y2, f'{v}%', size=12, bold=(i == 2))
    f.text(xs[3] + 4, y2, 'RL covers what the<br>demonstrations miss', size=12.5, color=SKY['dark'], bold=True, lh=1.3)
    return f


def build4i():
    """Round-4 innovative: success as small columns on one 0-100 baseline under the stages, so the jump from the base
    model through SFT to RL reads at a glance; the two-object task as a pair of columns of its own."""
    H = 214
    f = Fig(WIDTH, H, LABEL)
    gap = 18
    st, xs, ws = layout('en', gap)
    y, h = 8, 56
    stage_row(f, st, xs, ws, y, h, gap)
    base = H - 44
    top = y + h + 44
    hh = base - top                      # 100 %
    cw, cg = 22, 6
    heads = ['Base model', 'After SFT', 'After 100 RL steps']
    notes = [None, '≈ 1.4 h', '14.4 h']
    for i in range(3):
        cx = xs[i] + ws[i] / 2
        pal = SLATE if i == 0 else SKY
        for k, (v, solid) in enumerate(((VALS[i][0], True), (VALS[i][1], False))):
            x = cx - cw - cg / 2 + k * (cw + cg)
            f.box(x, base - hh * v / 100, cw, hh * v / 100, fill=pal['tok'] if solid else WHITE, stroke=pal['line'], width=1.1, arc=2)
            f.text(x + cw / 2, base - hh * v / 100 - 9, f'{v:.1f}', size=12, color=INK, anchor='c', bold=(i == 2))
        f.text(cx, base + 15, heads[i], size=12.5, color=MUTED if i == 0 else INK, anchor='c', bold=(i > 0))
        if notes[i]:
            f.text(cx, base + 32, notes[i], size=12, color=MUTED, anchor='c')
    f.line([(xs[0] + 4, base), (xs[2] + ws[2] - 4, base)], color=SLATE['line'], width=1)
    # legend and the two-object pair under the evaluation stage
    lx = xs[3] + 8
    f.text(lx, top + 2, 'ALFWorld success (%)', size=12.5, color=MUTED)
    f.box(lx, top + 22 - 6, 12, 12, fill=SKY['tok'], stroke=SKY['line'], width=1, arc=2)
    x0, x1 = f.text(lx + 17, top + 22, 'seen', size=12, color=MUTED)
    f.box(x1 + 12, top + 22 - 6, 12, 12, fill=WHITE, stroke=SKY['line'], width=1, arc=2)
    f.text(x1 + 29, top + 22, 'unseen', size=12, color=MUTED)
    f.text(lx, top + 52, '<b>Two-object task</b><br>expert: 55 of 813 solved', size=12, color=MUTED, lh=1.3)
    for k, (v, lab) in enumerate(((27, 'SFT'), (95, 'RL'))):
        bx = lx + 4 + k * 64
        f.box(bx, base - 4.5 - 0, 0.01, 0.01, fill=WHITE, stroke='none', width=0)
        f.box(bx, base - 9, 52 * v / 100, 9, fill=SKY['line'] if k else SKY['tok'], stroke=SKY['line'], width=1, arc=4.5)
        f.text(bx, base + 15, f'{lab} {v}%', size=12, color=INK, bold=(k == 1))
    return f


def build4m():
    """Round-4 merge: the columns of r4i for the three model states (one baseline, base model in grey), the notes of
    r4a under them (time; the step-20 result), the legend over the evaluation stage, and the two-object row of r4a."""
    H = 282
    f = Fig(WIDTH, H, LABEL)
    gap = 18
    st, xs, ws = layout('en', gap)
    y, h = 8, 56
    stage_row(f, st, xs, ws, y, h, gap)
    top = y + h + 42
    base = top + 72
    hh = base - top
    cw, cg = 24, 6
    heads = ['Base model', 'After SFT', 'After 100 RL steps']
    notes = [None, '≈ 1.4 h', '14.4 h · step 20: 98.6 / 91.0']
    for i in range(3):
        cx = xs[i] + ws[i] / 2
        pal = SLATE if i == 0 else SKY
        for k, (v, solid) in enumerate(((VALS[i][0], True), (VALS[i][1], False))):
            x = cx - cw - cg / 2 + k * (cw + cg)
            f.box(x, base - hh * v / 100, cw, hh * v / 100, fill=pal['tok'] if solid else WHITE, stroke=pal['line'], width=1.1, arc=2)
            f.text(x + cw / 2, base - hh * v / 100 - 9, f'{v:.1f}', size=12, color=INK, anchor='c', bold=(i == 2))
        f.text(cx, base + 15, heads[i], size=12.5, color=MUTED if i == 0 else INK, anchor='c', bold=(i > 0))
        if notes[i]:
            f.text(cx, base + 33, notes[i], size=12, color=MUTED, anchor='c')
    f.line([(xs[0] + 4, base), (xs[2] + ws[2] - 4, base)], color=SLATE['line'], width=1)
    lx = xs[3] + 6
    f.text(lx, top + 4, 'ALFWorld success (%)', size=12.5, color=MUTED)
    f.box(lx, top + 28 - 6, 12, 12, fill=SKY['tok'], stroke=SKY['line'], width=1, arc=2)
    x0, x1 = f.text(lx + 17, top + 28, 'seen', size=12, color=MUTED)
    f.box(x1 + 14, top + 28 - 6, 12, 12, fill=WHITE, stroke=SKY['line'], width=1, arc=2)
    f.text(x1 + 31, top + 28, 'unseen', size=12, color=MUTED)
    f.text(lx, base + 33, f'Training time, 2 {TIMES} A100', size=12, color=MUTED)
    y2 = H - 26
    f.line([(xs[0], y2 - 24), (WIDTH - 6, y2 - 24)], color=SLATE['tok'], width=1, dashed=True, dash='3 3')
    f.text(xs[0] + 4, y2, 'Two-object task, seen + unseen<br>the expert solves 55 of 813', size=12, color=MUTED, lh=1.3)
    bw = min(ws[:3]) - 60
    for i, v in ((1, 27), (2, 95)):
        bx = xs[i] + ws[i] / 2 - (bw + 40) / 2
        f.box(bx, y2 - 4.5, bw, 9, fill=SLATE['soft'], stroke='none', width=0, arc=4.5)
        f.box(bx, y2 - 4.5, bw * v / 100, 9, fill=SKY['line'] if i == 2 else SKY['tok'], stroke=SKY['line'], width=1, arc=4.5)
        f.text(bx + bw + 6, y2, f'{v}%', size=12, bold=(i == 2))
    f.text(lx, y2, 'RL covers what the<br>demonstrations miss', size=12.5, color=SKY['dark'], bold=True, lh=1.3)
    return f


# ------------------------------------------------------------------ round 5
def columns5(f, xs, ws, top, base, cw=24, cg=6, notes=True, named=False):
    hh = base - top
    heads = ['Base model (Qwen3-4B)' if named else 'Base model', 'After SFT', 'After 100 RL steps']
    tnotes = [None, '≈ 1.4 h', ('14.4 h · 98.6 / 91.0 by step 20' if named else '14.4 h · step 20: 98.6 / 91.0')]
    for i in range(3):
        cx = xs[i] + ws[i] / 2
        pal = SLATE if i == 0 else SKY
        for k, (v, solid) in enumerate(((VALS[i][0], True), (VALS[i][1], False))):
            x = cx - cw - cg / 2 + k * (cw + cg)
            f.box(x, base - hh * v / 100, cw, hh * v / 100, fill=pal['tok'] if solid else WHITE, stroke=pal['line'], width=1.1, arc=2)
            f.text(x + cw / 2, base - hh * v / 100 - 9, f'{v:.1f}', size=12, color=INK, anchor='c', bold=(i == 2))
        f.text(cx, base + 15, heads[i], size=12.5, color=MUTED if i == 0 else INK, anchor='c', bold=(i > 0))
        if notes and tnotes[i]:
            f.text(cx, base + 33, tnotes[i], size=12, color=MUTED, anchor='c')
    f.line([(xs[0] + 4, base), (xs[2] + ws[2] - 4, base)], color=SLATE['line'], width=1)


def legend5(f, lx, top):
    f.text(lx, top + 4, 'ALFWorld success (%)', size=12.5, color=MUTED)
    f.box(lx, top + 28 - 6, 12, 12, fill=SKY['tok'], stroke=SKY['line'], width=1, arc=2)
    x0, x1 = f.text(lx + 17, top + 28, 'seen', size=12, color=MUTED)
    f.box(x1 + 14, top + 28 - 6, 12, 12, fill=WHITE, stroke=SKY['line'], width=1, arc=2)
    f.text(x1 + 31, top + 28, 'unseen', size=12, color=MUTED)


def two_object5(f, xs, ws, y2, lx):
    f.text(xs[0] + 4, y2, 'Two-object task, seen + unseen<br>the expert solves 55 of 813', size=12, color=MUTED, lh=1.3)
    bw = min(ws[:3]) - 60
    for i, v in ((1, 27), (2, 95)):
        bx = xs[i] + ws[i] / 2 - (bw + 40) / 2
        f.box(bx, y2 - 4.5, bw, 9, fill=SLATE['soft'], stroke='none', width=0, arc=4.5)
        f.box(bx, y2 - 4.5, bw * v / 100, 9, fill=SKY['line'] if i == 2 else SKY['tok'], stroke=SKY['line'], width=1, arc=4.5)
        f.text(bx + bw + 6, y2, f'{v}%', size=12, bold=(i == 2))
    f.text(lx, y2, 'RL covers what the<br>demonstrations miss', size=12.5, color=SKY['dark'], bold=True, lh=1.3)


def build5a(named=False):
    """Round-5 aesthetic: r4m without the empty bottom margin. named (the merge): the base model is named, as in the
    Scaffold-OPD pipeline, and the RL note says when 98.6 / 91.0 was reached."""
    H = 276
    f = Fig(WIDTH, H, LABEL)
    gap = 18
    st, xs, ws = layout('en', gap)
    y, h = 8, 56
    stage_row(f, st, xs, ws, y, h, gap)
    top = y + h + 42
    base = top + 72
    columns5(f, xs, ws, top, base, named=named)
    lx = xs[3] + 6
    legend5(f, lx, top)
    f.text(lx, base + 33, f'Training time, 2 {TIMES} A100', size=12, color=MUTED)
    y2 = H - 20
    f.line([(xs[0], y2 - 22), (WIDTH - 6, y2 - 22)], color=SLATE['tok'], width=1, dashed=True, dash='3 3')
    two_object5(f, xs, ws, y2, lx)
    return f


# wall-clock hours on 2 x A100 (project page): expert data about 40 min, SFT about 1.4 h, RL 14.4 h to step 100, of which
# about 3.4 h to step 20 (SFT + 20 RL steps took about 5.5 h with the data generation)
TIMELINE = [('Demos', 0.67, LEMON, 'soft'), ('SFT', 1.4, SKY, 'soft'), ('RL to step 20', 3.4, SKY, 'fill'), ('RL, steps 20–100', 11.0, SKY, 'pale')]


def build5i():
    """Round-5 innovative: the time notes become a wall-clock strip, to scale: demonstrations, SFT, RL to step 20
    (98.6 / 91.0 already), and the remaining 80 RL steps, which add little (unseen 91.0 to 94.0)."""
    H = 330
    f = Fig(WIDTH, H, LABEL)
    gap = 18
    st, xs, ws = layout('en', gap)
    y, h = 8, 56
    stage_row(f, st, xs, ws, y, h, gap)
    top = y + h + 42
    base = top + 72
    columns5(f, xs, ws, top, base, notes=False)
    lx = xs[3] + 6
    legend5(f, lx, top)
    ys = base + 50
    x0, x1 = xs[0] + 4, WIDTH - 10
    total = sum(t for _, t, _, _ in TIMELINE)
    f.text(x0, ys - 14, f'Wall-clock hours on 2 {TIMES} A100', size=12, color=MUTED)
    x = x0
    edges = [x0]
    for name, t, pal, tone in TIMELINE:
        w = (x1 - x0) * t / total
        f.box(x, ys, w, 16, fill=pal[tone], stroke=pal['line'], width=1, arc=2)
        x += w
        edges.append(x)
    f.text((edges[3] + edges[4]) / 2, ys + 8, 'RL steps 20–100: unseen 91.0 → 94.0', size=12, color=MUTED, anchor='c')
    f.text((edges[2] + edges[3]) / 2, ys + 8, 'RL to step 20', size=12, color=SKY['dark'], anchor='c')
    for e, lab, bold in ((edges[2], '2.1 h', False), (edges[3], '5.5 h: 98.6 / 91.0', True), (edges[4], '16.5 h', False)):
        f.line([(e, ys + 16), (e, ys + 22)], color=SLATE['line'], width=1)
        f.text(e, ys + 32, lab, size=12, color=SKY['dark'] if bold else MUTED, anchor='e' if e == edges[4] else 'c', bold=bold)
    f.text(x0, ys + 32, 'Demos + SFT', size=12, color=MUTED)
    y2 = H - 24
    f.line([(xs[0], y2 - 26), (WIDTH - 6, y2 - 26)], color=SLATE['tok'], width=1, dashed=True, dash='3 3')
    two_object5(f, xs, ws, y2, lx)
    return f


# ------------------------------------------------------------------ round 6
def three_line(title, a, b, size=13, sub_size=11.5):
    return f'<b>{title}</b><br><span style="font-size:{sub_size}px;color:{MUTED};">{a}<br>{b}</span>'


def build6(times_in_boxes=False):
    """Round 6: r5m on a tighter canvas, the legend level with the top of the columns. times_in_boxes: each stage box
    carries its own duration on a second line, so under the columns only the step-20 result remains."""
    H = 270 if not times_in_boxes else 284
    f = Fig(WIDTH, H, LABEL)
    gap = 18
    st, xs, ws = layout('en', gap)
    y = 8
    h = 56 if not times_in_boxes else 66
    if times_in_boxes:
        subs = [('2,145 of 3,553', 'games solved'), ('Loss on tool calls', f'1 epoch · ≈ 1.4 h'),
                ('StepCredit-RL', '100 steps · 14.4 h'), ('Same tasks', 'McNemar test')]
        for i, ((title, _, pal, tone), (a, b)) in enumerate(zip(st, subs)):
            key = i == 2
            f.box(xs[i], y, ws[i], h, fill=pal[tone], stroke=pal['line'], width=1.8 if key else 1.2, label=three_line(title, a, b), size=13)
            if i:
                f.edge([(xs[i] - gap + 1, y + h / 2), (xs[i] - 1, y + h / 2)], width=1.2, end=5)
    else:
        stage_row(f, st, xs, ws, y, h, gap)
    top = y + h + 40
    base = top + 72
    columns5(f, xs, ws, top, base, named=True, notes=not times_in_boxes)
    if times_in_boxes:
        cx = xs[2] + ws[2] / 2
        f.text(cx, base + 33, '98.6 / 91.0 already by step 20', size=12, color=MUTED, anchor='c')
    lx = xs[3] + 6
    legend5(f, lx, top - 2)
    if not times_in_boxes:
        f.text(lx, base + 33, f'Training time, 2 {TIMES} A100', size=12, color=MUTED)
    y2 = H - 20
    f.line([(xs[0], y2 - 22), (WIDTH - 6, y2 - 22)], color=SLATE['tok'], width=1, dashed=True, dash='3 3')
    two_object5(f, xs, ws, y2, lx)
    return f
