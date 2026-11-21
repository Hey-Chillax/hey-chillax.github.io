"""Scaffold-OPD full pipeline: teacher solutions -> rejection sampling -> SFT -> Scaffold-OPD -> GRPO on failures, with the
four-benchmark average after each training stage.

Variants: r1a / r1i / r1m, r2a / r2i / r2m, r3a / r3i / r3m; rounds 4-6 (r4a ... r6m) English only;
r7m (2026-11-21) is the interview deck's final ported back; final: r7m.
Facts (projects/scaffold-opd.html, tools/data/scaffold_opd.json): 14,116 DAPO-Math problems, one teacher solution each
(up to 16k tokens); a rule-based checker keeps 11,158 (79%); SFT one epoch; Scaffold-OPD 40 steps; GRPO on the 2,212
problems the teacher solved but the student never got right during Scaffold-OPD, 30 steps. Average 25.4 -> 38.0 -> 42.6
-> 46.6; training GPU-hours 16.8 (teacher solutions + SFT), 15.4, 20.0 (52.4 in total before rounding).
"""
from dlib import Fig, INK, LEAF, LINE, MUTED, SKY, SLATE, WHITE, label_w

WIDTH = 720
LABEL = ('Scaffold-OPD pipeline: teacher solutions, rejection sampling, SFT, Scaffold-OPD and GRPO on failures, with the '
         'four-benchmark average after each training stage')
LABEL_ZH = 'Scaffold-OPD 全流程：老师解答、拒绝采样、SFT、Scaffold-OPD、错题回流 GRPO，标出每个训练阶段之后的 4 项平均分'


def T(lang, en, zh):
    return zh if lang == 'zh' else en


def two_line(title, sub, size=13, sub_size=11.5):
    return f'<b>{title}</b><br><span style="font-size:{sub_size}px;color:{MUTED};">{sub}</span>'


def stages(lang):
    return [
        (T(lang, 'Teacher Solutions', '老师解答'), T(lang, '14,116 problems', '14,116 道题'), LEAF, 'soft'),
        (T(lang, 'Rejection Sampling', '拒绝采样'), T(lang, '11,158 kept (79%)', '保留 11,158 条（79%）'), SLATE, 'soft'),
        ('SFT', T(lang, '1 epoch', '1 轮'), SKY, 'soft'),
        ('Scaffold-OPD', T(lang, '40 steps', '40 步'), SKY, 'fill'),
        (T(lang, 'GRPO on Failures', '错题回流 GRPO'), T(lang, '2,212 problems · 30 steps', '2,212 道题 · 30 步'), SKY, 'soft'),
    ]


SCORES = [None, None, (38.0, 12.6, 16.8), (42.6, 4.6, 15.4), (46.6, 4.0, 20.0)]


def build_a(lang):
    f = Fig(WIDTH, 176, LABEL)
    st = stages(lang)
    gap, h, y = 14, 56, 10
    w = (WIDTH - 12 - 4 * gap) / 5
    xs = [6 + i * (w + gap) for i in range(5)]
    for i, (title, sub, pal, tone) in enumerate(st):
        key = i == 3
        f.box(xs[i], y, w, h, fill=pal[tone], stroke=pal['line'], width=1.8 if key else 1.2, label=two_line(title, sub), size=13)
        if i:
            f.edge([(xs[i] - gap + 1, y + h / 2), (xs[i] - 1, y + h / 2)], width=1.2, end=5)
    # scores under the training stages
    ys = y + h + 30
    x0, x1 = f.text(xs[0] + 4, ys, T(lang, '4-benchmark average', '4 项平均分'), size=12.5, color=MUTED)
    f.text(xs[0] + 4, ys + 22, T(lang, 'Base model: 25.4', '基座：25.4'), size=12.5, color=MUTED)
    for i, sc in enumerate(SCORES):
        if not sc:
            continue
        v, g, hrs = sc
        cx = xs[i] + w / 2
        key = i == 3
        f.cbox(cx, ys, 58, 24, fill=SKY['fill'] if key else WHITE, stroke=SKY['line'] if key else SLATE['line'],
               width=1.6 if key else 1.1, arc=12, label=f'<b>{v:.1f}</b>', size=13.5)
        f.text(cx, ys + 24, f'+{g:.1f}', size=12.5, color=SKY['dark'] if key else INK, anchor='c', bold=key)
        f.text(cx, ys + 44, T(lang, f'{hrs:.1f} GPU-h', f'{hrs:.1f} 卡时'), size=11.5, color=MUTED, anchor='c')
        f.line([(cx, y + h + 1), (cx, ys - 13)], color=SLATE['tok'], width=1, dashed=True, dash='2 2')
    f.text(xs[0] + 4, ys + 44, T(lang, 'Training GPU-hours', '训练卡时'), size=11.5, color=MUTED)
    return f


def build_i(lang):
    """Two tracks: the data on top, the model below; arrows show which data each training stage consumes."""
    f = Fig(WIDTH, 214, LABEL)
    # data track
    dy, dh = 14, 40
    data = [(T(lang, '14,116 Problems', '14,116 道题'), T(lang, 'DAPO-Math', 'DAPO-Math'), SLATE),
            (T(lang, 'Teacher Solutions', '老师解答'), T(lang, 'Up to 16k tokens', '最长 16k token'), LEAF),
            (T(lang, '11,158 Kept', '保留 11,158 条'), T(lang, 'Finished and correct', '写完且答对'), LEAF)]
    dw = [128, 140, 140]
    dx = [6, 6 + 128 + 30, 6 + 128 + 30 + 140 + 30]
    for (t, s_, pal), x, w in zip(data, dx, dw):
        f.box(x, dy, w, dh, fill=pal['soft'], stroke=pal['line'], label=two_line(t, s_, 12.5, 11), size=12.5)
    for a, b in ((dx[0] + dw[0], dx[1]), (dx[1] + dw[1], dx[2])):
        f.edge([(a + 1, dy + dh / 2), (b - 1, dy + dh / 2)], width=1.2, end=5)
    f.text((dx[1] + dw[1] + dx[2]) / 2, dy - 2 + 0, '', size=1)
    f.text(dx[2] - 15, dy + dh + 10, T(lang, 'Rejection sampling', '拒绝采样'), size=11, color=MUTED, anchor='c')
    fx = 560
    f.box(fx, dy, 154, dh, fill=SLATE['soft'], stroke=SLATE['line'],
          label=two_line(T(lang, '2,212 Failures', '2,212 道错题'), T(lang, 'Teacher right, student never', '老师做对、学生始终没做对'), 12.5, 11), size=12.5)
    # model track
    my, mh = 126, 46
    model = [(T(lang, 'Base', '基座'), '25.4', SLATE, 'soft'), ('SFT', '38.0', SKY, 'soft'), ('Scaffold-OPD', '42.6', SKY, 'fill'),
             (T(lang, 'GRPO on Failures', '错题回流 GRPO'), '46.6', SKY, 'soft')]
    mw = [96, 120, 150, 166]
    mx = [6, 6 + 96 + 34, 6 + 96 + 34 + 120 + 34, 720 - 6 - 166]
    for (t, v, pal, tone), x, w in zip(model, mx, mw):
        key = t == 'Scaffold-OPD'
        f.box(x, my, w, mh, fill=pal[tone], stroke=pal['line'], width=1.8 if key else 1.2,
              label=f'<b>{t}</b><br><span style="font-size:13px;color:{SKY["dark"] if key else INK};"><b>{v}</b></span>', size=13)
    gains = ['+12.6', '+4.6', '+4.0']
    for k, (a, b) in enumerate(((mx[0] + mw[0], mx[1]), (mx[1] + mw[1], mx[2]), (mx[2] + mw[2], mx[3]))):
        f.edge([(a + 1, my + mh / 2), (b - 1, my + mh / 2)], width=1.2, end=5)
        f.text((a + b) / 2, my + mh / 2 - 12, gains[k], size=11.5, color=MUTED, anchor='c')
    # data -> training
    f.edge([(dx[2] + dw[2] / 2, dy + dh), (dx[2] + dw[2] / 2, my - 18), (mx[1] + mw[1] / 2, my - 18), (mx[1] + mw[1] / 2, my)],
           color=LEAF['line'], width=1.3, end=5)
    f.text(mx[1] + mw[1] / 2 + 6, my - 26, T(lang, 'SFT data', 'SFT 数据'), size=11, color=LEAF['dark'])
    f.edge([(dx[0] + dw[0] / 2, dy + dh), (dx[0] + dw[0] / 2, my - 34), (mx[2] + mw[2] / 2 - 20, my - 34), (mx[2] + mw[2] / 2 - 20, my)],
           color=SLATE['line'], width=1.3, end=5, dashed=True, dash='4 3')
    f.edge([(mx[2] + mw[2] / 2 + 20, my), (mx[2] + mw[2] / 2 + 20, my - 46), (fx + 40, my - 46), (fx + 40, dy + dh)],
           color=SLATE['line'], width=1.3, end=5)
    f.edge([(fx + 114, dy + dh), (fx + 114, my)], color=SLATE['line'], width=1.3, end=5)
    f.text(6, my + mh + 22, T(lang, 'Under each model: its 4-benchmark average; over each arrow: the gain from that stage.',
                              '模型框里是该阶段后的 4 项平均分，箭头上是这一阶段的提升。'), size=11.5, color=MUTED)
    return f


def build_m(lang):
    """Round-1 merge: the single row of the aesthetic version, with box widths fitted to their labels."""
    f = Fig(WIDTH, 176, LABEL)
    st = stages(lang)
    gap, h, y = 16, 56, 10
    need = [max(label_w(t, 13, True), label_w(s_, 11.5)) + 26 for t, s_, _, _ in st]
    extra = (WIDTH - 12 - 4 * gap - sum(need)) / 5
    ws = [n + extra for n in need]
    xs = [6 + sum(ws[:i]) + i * gap for i in range(5)]
    for i, (title, sub, pal, tone) in enumerate(st):
        key = i == 3
        f.box(xs[i], y, ws[i], h, fill=pal[tone], stroke=pal['line'], width=1.8 if key else 1.2, label=two_line(title, sub), size=13)
        if i:
            f.edge([(xs[i] - gap + 1, y + h / 2), (xs[i] - 1, y + h / 2)], width=1.2, end=5)
    ys = y + h + 30
    f.text(xs[0] + 4, ys, T(lang, '4-benchmark average', '4 项平均分'), size=12.5, color=MUTED)
    f.text(xs[0] + 4, ys + 22, T(lang, 'Base model 25.4', '基座 25.4'), size=12.5, color=MUTED)
    f.text(xs[0] + 4, ys + 44, T(lang, 'Training GPU-hours', '训练卡时'), size=11.5, color=MUTED)
    for i, sc in enumerate(SCORES):
        if not sc:
            continue
        v, g, hrs = sc
        cx = xs[i] + ws[i] / 2
        key = i == 3
        f.line([(cx, y + h + 1), (cx, ys - 13)], color=SLATE['tok'], width=1, dashed=True, dash='2 2')
        f.cbox(cx, ys, 58, 24, fill=SKY['fill'] if key else WHITE, stroke=SKY['line'] if key else SLATE['line'],
               width=1.6 if key else 1.1, arc=12, label=f'<b>{v:.1f}</b>', size=13.5)
        f.text(cx, ys + 22, f'+{g:.1f}', size=12.5, color=SKY['dark'] if key else INK, anchor='c', bold=key)
        f.text(cx, ys + 44, T(lang, f'{hrs:.1f} GPU-h', f'{hrs:.1f} 卡时'), size=11.5, color=MUTED, anchor='c')
    return f


def stage_row(f, lang, y=10, h=56, gap=16):
    st = stages(lang)
    need = [max(label_w(t, 13, True), label_w(s_, 11.5)) + 26 for t, s_, _, _ in st]
    extra = (WIDTH - 12 - 4 * gap - sum(need)) / 5
    ws = [n + extra for n in need]
    xs = [6 + sum(ws[:i]) + i * gap for i in range(5)]
    for i, (title, sub, pal, tone) in enumerate(st):
        key = i == 3
        f.box(xs[i], y, ws[i], h, fill=pal[tone], stroke=pal['line'], width=1.8 if key else 1.2, label=two_line(title, sub), size=13)
        if i:
            f.edge([(xs[i] - gap + 1, y + h / 2), (xs[i] - 1, y + h / 2)], width=1.2, end=5)
    return xs, ws


def build_r2a(lang):
    """Round-2 aesthetic: the merged layout with a header column and tighter rows."""
    f = Fig(WIDTH, 164, LABEL)
    y, h = 8, 56
    xs, ws = stage_row(f, lang, y, h)
    ys = y + h + 28
    hx = xs[0] + 6
    f.text(hx, ys, T(lang, '4-benchmark average', '4 项平均分'), size=12.5, bold=True)
    f.text(hx, ys + 22, T(lang, 'Gain · base model 25.4', '提升 · 基座 25.4'), size=12, color=MUTED)
    f.text(hx, ys + 42, T(lang, 'Training GPU-hours', '训练卡时'), size=12, color=MUTED)
    for i, sc in enumerate(SCORES):
        if not sc:
            continue
        v, g, hrs = sc
        cx = xs[i] + ws[i] / 2
        key = i == 3
        f.line([(cx, y + h + 1), (cx, ys - 13)], color=SLATE['tok'], width=1, dashed=True, dash='2 2')
        f.cbox(cx, ys, 60, 24, fill=SKY['fill'] if key else WHITE, stroke=SKY['line'] if key else SLATE['line'],
               width=1.6 if key else 1.1, arc=12, label=f'<b>{v:.1f}</b>', size=13.5)
        f.text(cx, ys + 22, f'+{g:.1f}', size=12.5, color=SKY['dark'] if key else INK, anchor='c', bold=key)
        f.text(cx, ys + 42, f'{hrs:.1f}', size=12, color=MUTED, anchor='c')
    return f


def build_r2i(lang):
    """Round-2 innovative: the scores as bars on one 0-50 scale, base model included, like the StepCredit-RL pipeline."""
    f = Fig(WIDTH, 186, LABEL)
    y, h = 8, 56
    xs, ws = stage_row(f, lang, y, h)
    yb = y + h + 30
    hx = xs[0] + 6
    f.text(hx, yb - 4, T(lang, '4-benchmark average', '4 项平均分'), size=12.5, bold=True)
    bw0 = ws[0] - 60
    f.text(hx, yb + 18, T(lang, 'Base model', '基座'), size=12, color=MUTED)
    f.box(hx, yb + 32, bw0 * 25.4 / 50, 9, fill=SLATE['tok'], stroke=SLATE['line'], width=0.9, arc=4)
    f.text(hx + bw0 * 25.4 / 50 + 6, yb + 36.5, '25.4', size=12)
    for i, sc in enumerate(SCORES):
        if not sc:
            continue
        v, g, hrs = sc
        key = i == 3
        x = xs[i] + 6
        bw = ws[i] - 54
        f.text(x, yb + 18, f'+{g:.1f}', size=12, color=SKY['dark'] if key else MUTED, bold=key)
        f.box(x, yb + 32, bw, 9, fill=SLATE['soft'], stroke='none', width=0, arc=4)
        f.box(x, yb + 32, bw * v / 50, 9, fill=SKY['line'] if key else SKY['tok'], stroke=SKY['line'], width=0.9, arc=4)
        f.text(x + bw + 6, yb + 36.5, f'{v:.1f}', size=12.5, bold=True)
        f.text(x, yb + 60, T(lang, f'{hrs:.1f} GPU-h', f'{hrs:.1f} 卡时'), size=11.5, color=MUTED)
    f.text(hx, yb + 60, T(lang, 'Training GPU-hours', '训练卡时'), size=11.5, color=MUTED)
    return f


def build_r3a(lang, merged=False):
    """Round-3 aesthetic: r2a with the hours row named for what it holds (per stage; SFT includes the teacher solutions).
    merged: the gain row says what the gain is measured against, as the caption does."""
    f = Fig(WIDTH, 162, LABEL)
    y, h = 8, 56
    xs, ws = stage_row(f, lang, y, h)
    ys = y + h + 28
    hx = xs[0] + 6
    f.text(hx, ys, T(lang, '4-benchmark average', '4 项平均分'), size=12.5, bold=True)
    if merged:
        f.text(hx, ys + 22, T(lang, 'Gain over the previous stage (base model 25.4)', '相对上一阶段的提升（基座 25.4）'), size=12, color=MUTED)
    else:
        f.text(hx, ys + 22, T(lang, 'Gain · base model 25.4', '提升 · 基座 25.4'), size=12, color=MUTED)
    f.text(hx, ys + 42, T(lang, 'GPU-hours per stage', '每阶段卡时'), size=12, color=MUTED)
    for i, sc in enumerate(SCORES):
        if not sc:
            continue
        v, g, hrs = sc
        cx = xs[i] + ws[i] / 2
        key = i == 3
        f.line([(cx, y + h + 1), (cx, ys - 13)], color=SLATE['tok'], width=1, dashed=True, dash='2 2')
        f.cbox(cx, ys, 60, 24, fill=SKY['fill'] if key else WHITE, stroke=SKY['line'] if key else SLATE['line'],
               width=1.6 if key else 1.1, arc=12, label=f'<b>{v:.1f}</b>', size=13.5)
        f.text(cx, ys + 22, f'+{g:.1f}', size=12.5, color=SKY['dark'] if key else INK, anchor='c', bold=key)
        f.text(cx, ys + 42, f'{hrs:.1f}', size=12, color=MUTED, anchor='c')
    return f


def build_r3i(lang):
    """Round-3 innovative: the averages as one progression from the base model, the gains on the arrows between them."""
    f = Fig(WIDTH, 142, LABEL)
    y, h = 8, 56
    xs, ws = stage_row(f, lang, y, h)
    ys = y + h + 30
    pills = [(xs[0] + ws[0] / 2, 25.4, T(lang, 'Base model', '基座'))]
    for i, sc in enumerate(SCORES):
        if sc:
            pills.append((xs[i] + ws[i] / 2, sc[0], T(lang, f'{sc[2]:.1f} GPU-h', f'{sc[2]:.1f} 卡时')))
            f.line([(xs[i] + ws[i] / 2, y + h + 1), (xs[i] + ws[i] / 2, ys - 13)], color=SLATE['tok'], width=1, dashed=True, dash='2 2')
    for k, (cx, v, tag) in enumerate(pills):
        key = k == 2
        f.cbox(cx, ys, 60, 24, fill=SKY['fill'] if key else WHITE, stroke=SKY['line'] if key else SLATE['line'],
               width=1.6 if key else 1.1, arc=12, label=f'<b>{v:.1f}</b>', size=13.5)
        f.text(cx, ys + 24, tag, size=11.5, color=MUTED, anchor='c')
        if k:
            px = pills[k - 1][0]
            f.edge([(px + 32, ys), (cx - 32, ys)], width=1.1, end=4, color=SLATE['line'])
            f.text((px + cx) / 2, ys - 11, f'+{v - pills[k - 1][1]:.1f}', size=12, color=SKY['dark'] if key else MUTED,
                   anchor='c', bold=key)
    return f


def build(v, lang):
    if v == 'r7m':
        return staircase7()
    if v[:2] in ('r4', 'r5', 'r6'):
        return {'r4a': build4a, 'r4i': build4i, 'r4m': build4m,
                'r5a': lambda: staircase5(drops=True),
                'r5i': lambda: staircase5(drops=True, total=True, base_name=True),
                'r5m': lambda: staircase5(drops=True, base_name=True),
                'r6a': staircase6, 'r6i': lambda: staircase6(fill=True), 'r6m': staircase6}[v]()
    if v in ('r3a', 'r3m'):
        return build_r3a(lang, merged=(v == 'r3m'))
    if v == 'r3i':
        return build_r3i(lang)
    if v == 'r1i':
        return build_i(lang)
    if v == 'r1a':
        return build_a(lang)
    if v == 'r1m':
        return build_m(lang)
    if v == 'r2a':
        return build_r2a(lang)
    if v == 'r2i':
        return build_r2i(lang)
    return build_r2a(lang)


# ------------------------------------------------------------------ rounds 4-6 (English only)
BASE = 25.4


def build4a():
    """Round-4 aesthetic: r3m with a lighter table: the row labels share one left column, a hairline separates the
    score row from the two detail rows, the key stage's column is tinted, and the empty bottom margin is gone."""
    H = 160
    f = Fig(WIDTH, H, LABEL)
    y, h = 8, 56
    xs, ws = stage_row(f, 'en', y, h)
    ys = y + h + 28
    hx = xs[0] + 6
    k = 3
    f.box(xs[k] + 6, y + h + 6, ws[k] - 12, H - (y + h + 6) - 4, fill=SKY['pale'], stroke='none', width=0, arc=8)
    f.text(hx, ys, '4-benchmark average', size=12.5, bold=True)
    f.line([(hx, ys + 17), (WIDTH - 12, ys + 17)], color=SLATE['soft'], width=1)
    f.text(hx, ys + 32, 'Gain over the previous stage (base model 25.4)', size=12, color=MUTED)
    f.text(hx, ys + 51, 'GPU-hours per stage', size=12, color=MUTED)
    for i, sc in enumerate(SCORES):
        if not sc:
            continue
        v, g, hrs = sc
        cx = xs[i] + ws[i] / 2
        key = i == k
        f.line([(cx, y + h + 1), (cx, ys - 13)], color=SLATE['tok'], width=1, dashed=True, dash='2 2')
        f.cbox(cx, ys, 62, 24, fill=SKY['fill'] if key else WHITE, stroke=SKY['line'] if key else SLATE['line'],
               width=1.6 if key else 1.1, arc=12, label=f'<b>{v:.1f}</b>', size=14)
        f.text(cx, ys + 32, f'+{g:.1f}', size=12.5, color=SKY['dark'] if key else INK, anchor='c', bold=key)
        f.text(cx, ys + 51, f'{hrs:.1f}', size=12, color=MUTED, anchor='c')
    return f


def build4i():
    """Round-4 innovative: the average as a staircase under the stages. One tread per training stage, at its score
    (25.4 to 46.6 on one scale), the gain written on each riser; the base model's tread runs under the two data
    stages; GPU-hours under each tread."""
    H = 176
    f = Fig(WIDTH, H, LABEL)
    y, h = 8, 56
    xs, ws = stage_row(f, 'en', y, h)
    top, bot = y + h + 34, H - 40            # y of 46.6 and of 25.4
    lo, hi = BASE, 46.6

    def yv(v):
        return bot - (v - lo) / (hi - lo) * (bot - top)

    levels = [(xs[0], xs[1] + ws[1], BASE, None)] + [(xs[i], xs[i] + ws[i], sc[0], sc) for i, sc in enumerate(SCORES) if sc]
    prev = None
    for k, (x0, x1, v, sc) in enumerate(levels):
        key = sc is not None and sc[0] == 42.6
        yy = yv(v)
        pal = SKY if sc else SLATE
        f.line([(x0 + 4, yy), (x1 - 4, yy)], color=pal['line'], width=2.6 if key else 1.8)
        if prev is not None:
            px, py = prev
            f.line([(px, py), (px, yy)], color=SLATE['tok'], width=1, dashed=True, dash='2 2')
            f.line([(px, yy), (x0 + 4, yy)], color=SLATE['tok'], width=1, dashed=True, dash='2 2')
            f.text(px + 6, (py + yy) / 2 + 1, f'+{v - prev_v:.1f}', size=12, color=SKY['dark'] if key else MUTED, bold=key)
        cx = (x0 + x1) / 2
        lab = f'<b>{v:.1f}</b>' if sc else 'Base model <b>25.4</b>'
        f.text(cx, yy - 11, lab, size=13.5 if sc else 12.5, color=INK if sc else MUTED, anchor='c')
        if sc:
            f.text(cx, bot + 22, f'{sc[2]:.1f} GPU-h', size=12, color=MUTED, anchor='c')
        prev, prev_v = (x1 - 4, yy), v
    f.text(xs[0] + 6, bot + 22, '4-benchmark average', size=12, color=MUTED, bold=True)
    return f


def build4m():
    """Round-4 merge: the staircase of r4i, cleaned up: the treads joined by sloped risers across the gaps between the
    stages, each score above its tread and its gain below it, the GPU-hours as a labelled row (as in r4a), and the
    row label of the scores in the empty corner over the base tread."""
    H = 200
    f = Fig(WIDTH, H, LABEL)
    y, h = 8, 56
    xs, ws = stage_row(f, 'en', y, h)
    top, bot = y + h + 46, y + h + 104
    lo, hi = BASE, 46.6

    def yv(v):
        return bot - (v - lo) / (hi - lo) * (bot - top)

    hx = xs[0] + 6
    f.text(hx, top - 4, '4-benchmark average', size=12.5, bold=True)
    yg = H - 16
    f.text(hx, yg, 'GPU-hours per stage', size=12, color=MUTED)
    levels = [(xs[0], xs[1] + ws[1], BASE, None)] + [(xs[i], xs[i] + ws[i], sc[0], sc) for i, sc in enumerate(SCORES) if sc]
    prev = None
    for x0, x1, v, sc in levels:
        key = sc is not None and sc[0] == 42.6
        yy = yv(v)
        a, b = x0 + 6, x1 - 6
        if prev is not None:
            f.line([prev, (a, yy)], color=SKY['line'], width=1.3)
        f.line([(a, yy), (b, yy)], color=(SKY if sc else SLATE)['line'], width=3 if key else 2)
        cx = (a + b) / 2
        if sc:
            f.text(cx, yy - 12, f'<b>{v:.1f}</b>', size=14, color=SKY['dark'] if key else INK, anchor='c')
            f.text(cx, yy + 13, f'+{sc[1]:.1f}', size=12, color=SKY['dark'] if key else MUTED, anchor='c', bold=key)
            f.text(cx, yg, f'{sc[2]:.1f}', size=12, color=MUTED, anchor='c')
        else:
            f.text(b, yy - 12, 'Base model <b>25.4</b>', size=12.5, color=MUTED, anchor='e')
        prev = (b, yy)
    return f


# ------------------------------------------------------------------ round 5
def staircase5(drops=False, total=False, base_name=False, H=200):
    """The r4m staircase; drops: a dotted line from each training stage down to its score; total: the GPU-hours row
    ends with the pipeline's total; base_name: the base tread names the student model."""
    f = Fig(WIDTH, H, LABEL)
    y, h = 8, 56
    xs, ws = stage_row(f, 'en', y, h)
    top, bot = y + h + 46, y + h + 104
    lo, hi = BASE, 46.6

    def yv(v):
        return bot - (v - lo) / (hi - lo) * (bot - top)

    hx = xs[0] + 6
    f.text(hx, top - 4, '4-benchmark average', size=12.5, bold=True)
    yg = H - 16
    f.text(hx, yg, 'GPU-hours per stage', size=12, color=MUTED)
    levels = [(xs[0], xs[1] + ws[1], BASE, None)] + [(xs[i], xs[i] + ws[i], sc[0], sc) for i, sc in enumerate(SCORES) if sc]
    prev = None
    for x0, x1, v, sc in levels:
        key = sc is not None and sc[0] == 42.6
        yy = yv(v)
        a, b = x0 + 6, x1 - 6
        cx = (a + b) / 2
        if drops and sc:
            f.line([(cx, y + h + 2), (cx, yy - 22)], color=SLATE['tok'], width=1, dashed=True, dash='1 3')
        if prev is not None:
            f.line([prev, (a, yy)], color=SKY['line'], width=1.3)
        f.line([(a, yy), (b, yy)], color=(SKY if sc else SLATE)['line'], width=3 if key else 2)
        if sc:
            f.text(cx, yy - 12, f'<b>{v:.1f}</b>', size=14, color=SKY['dark'] if key else INK, anchor='c')
            f.text(cx, yy + 13, f'+{sc[1]:.1f}', size=12, color=SKY['dark'] if key else MUTED, anchor='c', bold=key)
            f.text(cx, yg, f'{sc[2]:.1f}', size=12, color=MUTED, anchor='c')
        else:
            lab = 'Base model (Qwen3-1.7B) <b>25.4</b>' if base_name else 'Base model <b>25.4</b>'
            f.text(b, yy - 12, lab, size=12.5, color=MUTED, anchor='e')
        prev = (b, yy)
    if total:
        f.text(WIDTH - 8, yg, '52.4 in total', size=12, color=MUTED, anchor='e', italic=True)
    return f


# ------------------------------------------------------------------ round 6
def staircase6(fill=False, H=192):
    """Round 6: r5m on a tighter canvas; fill: a pale column under each training tread, down to the base level, so the
    climb reads as area."""
    f = Fig(WIDTH, H, LABEL)
    y, h = 8, 56
    xs, ws = stage_row(f, 'en', y, h)
    top, bot = y + h + 46, y + h + 104
    lo, hi = BASE, 46.6

    def yv(v):
        return bot - (v - lo) / (hi - lo) * (bot - top)

    hx = xs[0] + 6
    f.text(hx, top - 4, '4-benchmark average', size=12.5, bold=True)
    yg = H - 14
    f.text(hx, yg, 'GPU-hours per stage', size=12, color=MUTED)
    levels = [(xs[0], xs[1] + ws[1], BASE, None)] + [(xs[i], xs[i] + ws[i], sc[0], sc) for i, sc in enumerate(SCORES) if sc]
    prev = None
    for x0, x1, v, sc in levels:
        key = sc is not None and sc[0] == 42.6
        yy = yv(v)
        a, b = x0 + 6, x1 - 6
        cx = (a + b) / 2
        if sc:
            f.line([(cx, y + h + 2), (cx, yy - 22)], color=SLATE['tok'], width=1, dashed=True, dash='1 3')
            if fill:
                f.box(a, yy, b - a, bot - yy, fill=SKY['pale'], stroke='none', width=0, arc=0)
        if prev is not None:
            f.line([prev, (a, yy)], color=SKY['line'], width=1.3)
        f.line([(a, yy), (b, yy)], color=(SKY if sc else SLATE)['line'], width=3 if key else 2)
        if sc:
            f.text(cx, yy - 12, f'<b>{v:.1f}</b>', size=14, color=SKY['dark'] if key else INK, anchor='c')
            f.text(cx, yy + 13, f'+{sc[1]:.1f}', size=12, color=SKY['dark'] if key else MUTED, anchor='c', bold=key)
            f.text(cx, yg, f'{sc[2]:.1f}', size=12, color=MUTED, anchor='c')
        else:
            f.text(b, yy - 12, 'Base model (Qwen3-1.7B) <b>25.4</b>', size=12.5, color=MUTED, anchor='e')
        prev = (b, yy)
    return f


# ------------------------------------------------------------------ round 7 (2026-11-21): the deck's final, ported back
# The interview deck redrew this figure for its slide in three rounds (resume repo:
# ppt_src/figures/drawio/fig_opd_pipeline.py, final r3m) and the user chose that version for the homepage too. r7m is
# that layout at the homepage's width and type scale: the benchmarks named under the row title, every level labelled the
# same way (value above its tread, what it is below), dashed drop lines from each training stage to its score, and the
# GPU-hours as brackets under the stages they cover (16.8 covers teacher solutions + SFT), the numbers in ink. The deck
# drew the treads in the data charts' blue (#3B73B9) so they hold up on a projector; here they take the palette's dark
# sky, which is just as strong and has a dark-theme colour.
def ink_unit(num, rest):
    """'16.8 GPU-h ...': the number in ink, the rest muted."""
    return f'<span style="color:{INK};">{num}</span>{rest}'


def bracket_row(f, spans, y, foot=5, label_dy=12, size=12):
    """GPU-hour brackets: spans = [(x0, x1, label), ...]; the feet point up at the stages they cover."""
    for x0, x1, lab in spans:
        f.edge([(x0, y - foot), (x0, y), (x1, y), (x1, y - foot)], color=SLATE['line'], width=1, arrow=False,
               rounded=False)
        f.text((x0 + x1) / 2, y + label_dy, lab, size=size, color=MUTED, anchor='c')


def staircase7():
    y, h = 8, 56
    top, bot = y + h + 46, y + h + 112          # treads: 46.6 at top, the base model's 25.4 at bot
    yb = bot + 13 + 20                          # bracket line, under the base model's label
    H = yb + 12 + 11
    f = Fig(WIDTH, H, LABEL)
    xs, ws = stage_row(f, 'en', y, h)
    lo, hi = BASE, 46.6
    line = SKY['dark']

    def yv(v):
        return bot - (v - lo) / (hi - lo) * (bot - top)

    hx = xs[0] + 6
    f.text(hx, top - 12, '4-benchmark average', size=12.5, bold=True)
    f.text(hx, top + 5, 'MATH-500 · AIME 2024–26', size=12, color=MUTED)
    levels = [(xs[0], xs[1] + ws[1], BASE, None)] + [(xs[i], xs[i] + ws[i], sc[0], sc) for i, sc in enumerate(SCORES) if sc]
    prev = None
    for x0, x1, v, sc in levels:
        key = sc is not None and sc[0] == 42.6
        yy = yv(v)
        a, b = x0 + 6, x1 - 6
        cx = (a + b) / 2
        if sc:
            f.line([(cx, y + h + 2), (cx, yy - 22)], color=SLATE['line'], width=1, dashed=True, dash='2 3')
        if prev is not None:
            f.line([prev, (a, yy)], color=line, width=1.3)
        f.line([(a, yy), (b, yy)], color=line if sc else SLATE['line'], width=3 if key else 2)
        if sc:
            f.text(cx, yy - 12, f'<b>{v:.1f}</b>', size=14, color=line if key else INK, anchor='c')
            f.text(cx, yy + 13, f'+{sc[1]:.1f}', size=12, color=line if key else MUTED, anchor='c', bold=key)
        else:
            cxb = b - 90
            f.text(cxb, yy - 12, '<b>25.4</b>', size=14, color=MUTED, anchor='c')
            f.text(cxb, yy + 13, 'Base model (Qwen3-1.7B)', size=12, color=MUTED, anchor='c')
        prev = (b, yy)
    spans = [(xs[0] + 3, xs[2] + ws[2] - 3, ink_unit('16.8', ' GPU-h · teacher solutions + SFT')),
             (xs[3] + 3, xs[3] + ws[3] - 3, ink_unit('15.4', ' GPU-h')),
             (xs[4] + 3, xs[4] + ws[4] - 3, ink_unit('20.0', ' GPU-h'))]
    bracket_row(f, spans, yb)
    return f
