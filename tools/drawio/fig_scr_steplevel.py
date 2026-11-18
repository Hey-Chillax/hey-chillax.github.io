"""StepCredit-RL method figure: the multi-turn agent loop, a group of rollouts with a shared state, and how each step's
advantage combines an episode-level part with a step-level part.

Variants: r1a / r1i / r1m (round 1: aesthetic, innovative, merged), r2a / r2i / r2m, r3a / r3i / r3m;
rounds 4-6 (r4a ... r6m) are English only and 720 px wide (one unit = one pixel on the project page); final: r6m.
Facts (projects/stepcredit-rl.html): each agent step (one LLM call plus one tool call) is a training sample, the context
does not grow; ALFWorld gives R = 1 if the task is solved within 20 steps, else 0 (gamma = 1); a group holds N = 8
rollouts of the same task; identical states are found by hashing the observation; the episode-level advantage compares
a rollout's outcome with the group, the step-level advantage compares the return after a step with other steps taken
from the same state; the two are added; no critic and no extra rollouts. The example (s2 = holding the mug, the three
actions) is illustrative.
"""
from dlib import (Fig, INK, LAV, LEAF, LEMON, LINE, MUTED, ROSE, SKY, SLATE, WHITE, label_w, msub, m, TIMES)

WIDTH = 880
LABEL = ('StepCredit-RL: a group of rollouts of the same task; steps from the same environment state are compared by '
         'the return that followed, and this step-level advantage is added to the episode-level advantage')
LABEL_ZH = 'StepCredit-RL：同一任务的一组 rollout；从同一环境状态出发的各步按之后的回报比较，这一步级优势与整局优势相加'


def T(lang, en, zh):
    return zh if lang == 'zh' else en


def two_line(title, sub, size=13.5, sub_size=12):
    return f'<b>{title}</b><br><span style="font-size:{sub_size}px;color:{MUTED};">{sub}</span>'


ROWS = [(['0', '1', '2', '3', '4'], True), (['0', '5', '1', '2', '6'], False), (['0', '1', '2', '7'], False)]
# round 2 on: only s0 (every rollout starts there) and s2 are shared, so the step-level groups shown are the real ones
ROWS2 = [(['0', '1', '2', '3', '4'], True), (['0', '5', '6', '2', '7'], False), (['0', '8', '2', '9'], False)]


def state(f, cx, cy, k, shared=False, w=30, h=22):
    pal = LAV if shared else SLATE
    f.box(cx - w / 2, cy - h / 2, w, h, fill=pal['fill'] if shared else WHITE, stroke=pal['line'], width=1.1, arc=6,
          label=msub('s', k, 14), size=13, family='Times New Roman')


def outcome(f, x, cy, ok, w=64, h=22):
    pal = LEAF if ok else ROSE
    f.box(x, cy - h / 2, w, h, fill=pal['soft'], stroke=pal['line'], width=1.1, arc=11)
    (f.check if ok else f.cross)(x + 14, cy, s=8 if ok else 7)
    f.text(x + 26, cy, f'{m("R", 14)} = {1 if ok else 0}', size=13)


def agent_loop(f, lang, X, Y, W, H, compact=False):
    f.panel(X, Y, W, H, SKY, T(lang, 'Multi-Turn Agent Loop', '多轮 Agent 交互'))
    bw = W - 32
    f.box(X + 16, Y + 40, bw, 46, fill=SKY['fill'], stroke=SKY['line'], label=two_line(T(lang, 'LLM Agent', 'LLM Agent'), 'Qwen3-4B'), size=13.5)
    yb = Y + (190 if not compact else 160)
    f.box(X + 16, yb, bw, 46, fill=LEMON['soft'], stroke=LEMON['line'],
          label=two_line(T(lang, 'Environment', '环境'), T(lang, 'ALFWorld household tasks', 'ALFWorld 家务任务')), size=13.5)
    xa, xb = X + 16 + bw * 0.28, X + 16 + bw * 0.72
    f.edge([(xa, Y + 86), (xa, yb)], end=5)
    f.edge([(xb, yb), (xb, Y + 86)], end=5)
    f.text(xa, Y + 104, T(lang, 'Tool call', '工具调用'), size=12, color=MUTED, anchor='c')
    f.chip(xa - 46, Y + 126, 'go to fridge 1', SLATE, size=11.5, h=19, pad=5)
    f.text(xb, Y + 136 if not compact else Y + 112, T(lang, 'Observation', '观察'), size=12, color=MUTED, anchor='c')
    f.chip(xb - 60, (Y + 158) if not compact else (Y + 134), '“You arrive at fridge 1.”', SLATE, size=11.5, h=19, pad=5)
    notes = T(lang, 'One LLM call + one tool call<br>= one training sample;<br>the context does not grow.',
              '一次 LLM 调用 + 一次工具调用<br>= 一条训练样本，<br>上下文不随步数增长。')
    f.text(X + 16, yb + 80, notes, size=12, color=MUTED, lh=1.3)
    f.text(X + 16, yb + 140, T(lang, 'Reward only at the end:<br>R = 1 if solved within 20 steps.', '只在最后给奖励：<br>20 步内完成 R = 1，否则 0。'),
           size=12, color=MUTED, lh=1.3)


def group_rows(f, X, Y, x0, pitch, row_y, with_outcome=True, w=30, rows=None):
    """The three rollouts; returns the centres of the shared state s2 and per-row state centres."""
    shared, centres = [], []
    for r, (states, ok) in enumerate(rows or ROWS):
        y = row_y[r]
        f.text(X + 16, y, msub('τ', r + 1, 15), size=13)
        cs = []
        for c, k in enumerate(states):
            cx = x0 + c * pitch
            state(f, cx, y, k, shared=(k == '2'), w=w)
            if c:
                f.edge([(cx - pitch + w / 2 + 1, y), (cx - w / 2 - 1, y)], width=1.1, end=5)
            if k == '2':
                shared.append((cx, y))
            cs.append(cx)
        centres.append(cs)
        if with_outcome:
            outcome(f, x0 + 5 * pitch - 12, y, ok)
    for (xa, ya), (xb, yb) in zip(shared, shared[1:]):
        f.edge([(xa, ya + 11), (xb, yb - 11)], color=LAV['line'], width=1.4, arrow=False, dashed=True, dash='3 3', curved=True)
    return shared, centres


def bar(f, x0, cy, length, pal, h=12):
    """Horizontal bar from x0: positive length to the right, negative to the left."""
    if length >= 0:
        f.box(x0, cy - h / 2, length, h, fill=pal['tok'], stroke=pal['line'], width=0.9, arc=2)
    else:
        f.box(x0 + length, cy - h / 2, -length, h, fill=pal['tok'], stroke=pal['line'], width=0.9, arc=2)


def build_a(lang):
    """Round-1 aesthetic: the five-part loop of the current figure, redrawn; mechanisms instead of formulas."""
    f = Fig(WIDTH, 508, LABEL)
    agent_loop(f, lang, 6, 6, 232, 496)
    # group
    GX, GY, GW, GH = 250, 6, 624, 210
    f.panel(GX, GY, GW, GH, SLATE, T(lang, 'A Group of N = 8 Rollouts of the Same Task', '同一任务的一组 N = 8 条 rollout'))
    f.text(GX + GW - 14, GY + 20, T(lang, f'{msub("s", "2")} = holding the mug (same observation hash)', f'{msub("s", "2")}：手里拿着杯子（环境观察的哈希相同）'),
           size=12, color=LAV['dark'], anchor='e')
    row_y = [GY + 58, GY + 104, GY + 150]
    group_rows(f, GX, GY, GX + 66, 76, row_y)
    f.text(GX + 16, GY + 186, '⋮', size=15, family='Times New Roman')
    # episode level
    EX, EY, EW, EH = 250, 228, 306, 170
    f.panel(EX, EY, EW, EH, SLATE, T(lang, 'Episode Level', '整局'))
    zero = EX + 182
    for r, (states, ok) in enumerate(ROWS):
        y = EY + 56 + r * 30
        f.text(EX + 16, y, msub('τ', r + 1, 15), size=13)
        f.text(EX + 48, y, f'{m("R", 14)} = {1 if ok else 0}', size=13)
        bar(f, zero, y, 54 if ok else -27, LEAF if ok else ROSE)
    f.line([(zero, EY + 40), (zero, EY + 132)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(zero, EY + 148, T(lang, 'group mean', '组均值'), size=11.5, color=MUTED, anchor='c')
    # step level
    SX, SY, SW, SH = 568, 228, 306, 170
    f.panel(SX, SY, SW, SH, LAV, T(lang, 'Step Level: Same-State Group', '步级：同状态分组'))
    zero2 = SX + 252
    acts = [('go to fridge 1', 1), ('go to cabinet 1', 0), ('go to sinkbasin 1', 0)]
    for r, (act, g) in enumerate(acts):
        y = SY + 56 + r * 30
        state(f, SX + 30, y, '2', shared=True, w=28, h=20)
        f.edge([(SX + 45, y), (SX + 58, y)], width=1.1, end=4)
        f.chip(SX + 60, y, act, SLATE, size=11.5, h=19, pad=5)
        f.text(SX + 196, y, f'{m("G", 14)} = {g}', size=13)
        bar(f, zero2, y, 36 if g else -18, LEAF if g else ROSE)
    f.line([(zero2, SY + 40), (zero2, SY + 132)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(SX + 16, SY + 148, T(lang, 'return after the step, vs other steps from ' + msub('s', '2'), '这一步之后的回报，与从 ' + msub('s', '2') + ' 出发的其他步比较'),
           size=11.5, color=MUTED)
    f.text(EX + 16, EY + 148, T(lang, 'outcome vs the group', '结局与整组比较'), size=11.5, color=MUTED)
    # combine
    CX, CY, CW, CH = 250, 410, 624, 92
    f.panel(CX, CY, CW, CH, SKY, T(lang, 'Add the Two and Update the Agent', '两部分相加，更新 Agent'))
    y = CY + 58
    x = CX + 24
    f.text(x, y, T(lang, 'Step from ' + msub('s', '2') + ' in ' + msub('τ', '1') + ':', msub('τ', '1') + ' 中从 ' + msub('s', '2') + ' 出发的一步：'), size=12.5)
    x += 150
    bar(f, x, y, 54, LEAF)
    f.text(x + 27, y + 17, T(lang, 'episode', '整局'), size=11, color=MUTED, anchor='c')
    f.circle_op(x + 72, y, 'plus', r=8)
    bar(f, x + 90, y, 36, LEAF)
    f.text(x + 108, y + 17, T(lang, 'step', '步级'), size=11, color=MUTED, anchor='c')
    f.text(x + 136, y, '=', size=15)
    f.box(x + 150, y - 6, 54, 12, fill=SKY['tok'], stroke=SKY['line'], width=0.9, arc=2)
    f.box(x + 204, y - 6, 36, 12, fill=SKY['fill'], stroke=SKY['line'], width=0.9, arc=2)
    f.text(x + 195, y + 17, T(lang, 'its advantage', '这一步的优势'), size=11, color=MUTED, anchor='c')
    f.text(CX + CW - 18, y, T(lang, 'No critic · no extra rollouts', '无需 critic · 无需额外 rollout'), size=12.5, color=MUTED, anchor='e')
    return f


def build_i(lang):
    """Round-1 innovative: every step of every rollout gets a bar; its light part is the episode part (equal along the
    rollout, as in GRPO), its dark part the step part (only steps that leave a shared state)."""
    f = Fig(WIDTH, 404, LABEL)
    agent_loop(f, lang, 6, 6, 232, 392, compact=True)
    GX, GY, GW, GH = 250, 6, 624, 392
    f.panel(GX, GY, GW, GH, SLATE, T(lang, 'Credit for Every Step: Episode Part + Step Part', '每一步的信用：整局部分 + 步级部分'))
    pitch, x0 = 92, GX + 70
    row_y = [GY + 70, GY + 170, GY + 270]
    shared, centres = group_rows(f, GX, GY, x0, pitch, row_y)
    # per-step advantage bars under each arrow (vertical, baseline at row_y + 34)
    for r, (states, ok) in enumerate(ROWS):
        base = row_y[r] + 44
        f.line([(x0 - 16, base), (x0 + (len(states) - 1) * pitch - 30, base)], color=SLATE['tok'], width=1)
        ep = 16 if ok else -8
        for c in range(len(states) - 1):
            bx = x0 + c * pitch + pitch / 2 - 6
            pal = LEAF if ok else ROSE
            y0 = base - ep if ep > 0 else base
            f.box(bx, y0, 12, abs(ep), fill=pal['fill'], stroke=pal['line'], width=0.9, arc=1.5)
            if states[c] == '2':
                st = 12 if ok else -6
                y1 = (base - ep - st) if st > 0 else (base - ep if ep < 0 else base) + (0 if ep > 0 else abs(ep))
                if st > 0:
                    f.box(bx, base - ep - st, 12, st, fill=pal['tok'], stroke=pal['line'], width=0.9, arc=1.5)
                else:
                    f.box(bx, base + abs(ep), 12, -st, fill=pal['tok'], stroke=pal['line'], width=0.9, arc=1.5)
    f.text(GX + 16, GY + 330, '⋮', size=15, family='Times New Roman')
    # legend
    ly = GY + 362
    x = GX + 20
    f.box(x, ly - 6, 12, 12, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=1.5)
    x0_, x1_ = f.text(x + 18, ly, T(lang, 'Episode part: the outcome vs the group, same for every step', '整局部分：结局与整组比较，整条 rollout 的每一步都相同'), size=12)
    x = x1_ + 16
    f.box(x, ly - 6, 12, 12, fill=LEAF['tok'], stroke=LEAF['line'], width=0.9, arc=1.5)
    f.text(x + 18, ly, T(lang, 'Step part: vs other steps from ' + msub('s', '2'), '步级部分：与从 ' + msub('s', '2') + ' 出发的其他步比较'), size=12)
    return f


def agent_loop_m(f, lang, X, Y, W, H):
    """Agent loop with the tool call and observation as labels on the arrows, and one training sample per step."""
    f.panel(X, Y, W, H, SKY, T(lang, 'Multi-Turn Agent Loop', '多轮 Agent 交互'))
    bx, bw = X + 14, W - 28
    f.box(bx, Y + 40, bw, 46, fill=SKY['fill'], stroke=SKY['line'], label=two_line('LLM Agent', 'Qwen3-4B'), size=13.5)
    yb = Y + 194
    f.box(bx, yb, bw, 46, fill=LEMON['soft'], stroke=LEMON['line'],
          label=two_line(T(lang, 'Environment', '环境'), T(lang, 'ALFWorld household tasks', 'ALFWorld 家务任务')), size=13.5)
    xa, xb = bx + bw * 0.3, bx + bw * 0.72
    f.edge([(xa, Y + 86), (xa, yb)], end=5)
    f.edge([(xb, yb), (xb, Y + 86)], end=5)
    ca = 'go to fridge 1'
    wa = label_w(ca, 11.5) + 10
    f.chip(xa - wa / 2, Y + 122, ca, SLATE, size=11.5, h=19, pad=5)
    cb = '“You arrive at fridge 1.”'
    wb = label_w(cb, 11.5) + 10
    f.chip(min(xb - wb / 2, X + W - 8 - wb), Y + 160, cb, SLATE, size=11.5, h=19, pad=5)
    # one training sample per step
    y0 = yb + 70
    f.text(bx, y0, T(lang, 'One training sample per step:', '每一步一条训练样本：'), size=12, color=MUTED)
    for k in range(3):
        lab = f'<span style="font-family:Times New Roman;"><i>s</i><sub>{k}</sub> → <i>a</i><sub>{k}</sub></span>'
        f.box(bx, y0 + 16 + k * 26, 74, 20, fill=WHITE, stroke=SLATE['line'], width=1, arc=5, label=lab, size=13,
              family='Times New Roman')
    f.text(bx + 86, y0 + 52, T(lang, 'The context does<br>not grow with<br>the steps', '上下文不随<br>步数增长'), size=12, color=MUTED, lh=1.3)
    f.text(bx, y0 + 128, T(lang, 'Reward only at the end:<br>' + m('R', 14) + ' = 1 if solved within 20 steps', '只在最后给奖励：<br>20 步内完成 ' + m('R', 14) + ' = 1'),
           size=12, color=MUTED, lh=1.3)


MEAN_X = 760


def build_m(lang):
    f = Fig(WIDTH, 500, LABEL)
    agent_loop_m(f, lang, 6, 6, 226, 488)
    # group with outcomes and the episode-level comparison
    GX, GY, GW, GH = 258, 6, 616, 220
    f.panel(GX, GY, GW, GH, SLATE, T(lang, 'A Group of N = 8 Rollouts of the Same Task', '同一任务的一组 N = 8 条 rollout'))
    f.text(MEAN_X, GY + 46, T(lang, 'Episode Level', '整局'), size=12.5, bold=True, anchor='c')
    row_y = [GY + 70, GY + 114, GY + 158]
    shared, centres = group_rows(f, GX, GY, GX + 60, 62, row_y)
    for r, (states, ok) in enumerate(ROWS):
        bar(f, MEAN_X, row_y[r], 48 if ok else -24, LEAF if ok else ROSE)
    f.line([(MEAN_X, GY + 58), (MEAN_X, GY + 172)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(MEAN_X, GY + 184, T(lang, 'Outcome vs group mean', '结局与组均值比较'), size=11.5, color=MUTED, anchor='c')
    f.text(GX + 16, GY + 194, '⋮', size=15, family='Times New Roman')
    f.text(GX + 40, GY + 204, T(lang, msub('s', '2') + ': holding the mug, reached in all three (same observation hash)',
                                 msub('s', '2') + '：手里拿着杯子，三条都到达了（环境观察的哈希相同）'), size=12, color=LAV['dark'])
    # step level: one shared state, three steps
    SX, SY, SW, SH = 258, 238, 616, 166
    f.panel(SX, SY, SW, SH, LAV, T(lang, 'Step Level: Steps Taken from the Same State', '步级：从同一状态出发的各步'))
    f.text(MEAN_X, SY + 46, T(lang, 'Step Level', '步级'), size=12.5, bold=True, anchor='c')
    cy = SY + 96
    state(f, SX + 44, cy, '2', shared=True)
    acts = [('go to fridge 1', '3', 1), ('go to cabinet 1', '6', 0), ('go to sinkbasin 1', '7', 0)]
    for k, (act, nxt, g) in enumerate(acts):
        y = SY + 64 + k * 32
        f.edge([(SX + 60, cy), (SX + 84, y)], width=1.1, end=4)
        e = f.chip(SX + 86, y, act, SLATE, size=11.5, h=19, pad=5)
        f.edge([(e + 4, y), (SX + 248, y)], width=1.1, end=4)
        state(f, SX + 266, y, nxt, w=30)
        f.text(SX + 300, y, f'{m("G", 14)} = {g}', size=13)
        bar(f, MEAN_X, y, 40 if g else -20, LEAF if g else ROSE)
    f.line([(MEAN_X, SY + 54), (MEAN_X, SY + 138)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(MEAN_X, SY + 150, T(lang, 'Return vs the mean of these steps', '回报与这几步的均值比较'), size=11.5, color=MUTED, anchor='c')
    # combine and update
    CX, CY, CW, CH = 258, 416, 616, 78
    f.panel(CX, CY, CW, CH, SKY, T(lang, 'Add the Two, Then Update the Agent', '两部分相加，再更新 Agent'))
    y = CY + 52
    x = CX + 18
    x0, x1 = f.text(x, y, T(lang, 'Step from ' + msub('s', '2') + ' in ' + msub('τ', '1') + ':', msub('τ', '1') + ' 中从 ' + msub('s', '2') + ' 出发的一步：'), size=12.5)
    x = x1 + 14
    bar(f, x, y, 48, LEAF)
    f.circle_op(x + 64, y, 'plus', r=8)
    bar(f, x + 80, y, 40, LEAF)
    f.text(x + 132, y, '=', size=15)
    f.box(x + 146, y - 6, 48, 12, fill=SKY['tok'], stroke=SKY['line'], width=0.9, arc=2)
    f.box(x + 194, y - 6, 40, 12, fill=SKY['fill'], stroke=SKY['line'], width=0.9, arc=2)
    f.text(x + 24, y + 16, T(lang, 'episode', '整局'), size=11, color=MUTED, anchor='c')
    f.text(x + 100, y + 16, T(lang, 'step', '步级'), size=11, color=MUTED, anchor='c')
    f.text(x + 190, y + 16, T(lang, 'advantage', '优势'), size=11, color=MUTED, anchor='c')
    f.text(CX + CW - 16, y, T(lang, 'No critic · no extra rollouts', '无需 critic · 无需额外 rollout'), size=12.5, color=MUTED, anchor='e')
    f.edge([(CX + 6, CY + 40), (232 + 2, CY + 40)], color=SKY['line'], width=1.6, end=6)
    return f


# ------------------------------------------------------------------ round 2
def agent_loop2(f, lang, X, Y, W, H):
    """Round-2 agent panel: the same parts, spread over the panel's full height."""
    f.panel(X, Y, W, H, SKY, T(lang, 'Multi-Turn Agent Loop', '多轮 Agent 交互'))
    bx, bw = X + 14, W - 28
    f.box(bx, Y + 42, bw, 48, fill=SKY['fill'], stroke=SKY['line'], label=two_line('LLM Agent', 'Qwen3-4B'), size=13.5)
    yb = Y + 206
    f.box(bx, yb, bw, 48, fill=LEMON['soft'], stroke=LEMON['line'],
          label=two_line(T(lang, 'Environment', '环境'), T(lang, 'ALFWorld household tasks', 'ALFWorld 家务任务')), size=13.5)
    xa, xb = bx + bw * 0.3, bx + bw * 0.72
    f.edge([(xa, Y + 90), (xa, yb)], end=5)
    f.edge([(xb, yb), (xb, Y + 90)], end=5)
    ca, cb = 'go to fridge 1', '“You arrive at fridge 1.”'
    wa, wb = label_w(ca, 11.5) + 10, label_w(cb, 11.5) + 10
    f.chip(xa - wa / 2, Y + 128, ca, SLATE, size=11.5, h=19, pad=5)
    f.chip(min(xb - wb / 2, X + W - 8 - wb), Y + 168, cb, SLATE, size=11.5, h=19, pad=5)
    y0 = yb + 82
    f.text(bx, y0, T(lang, 'One training sample per step', '每一步一条训练样本'), size=12.5, bold=True)
    for k in range(3):
        lab = f'<span style="font-family:Times New Roman;"><i>s</i><sub>{k}</sub> → <i>a</i><sub>{k}</sub></span>'
        f.box(bx, y0 + 18 + k * 27, 74, 21, fill=WHITE, stroke=SLATE['line'], width=1, arc=5, label=lab, size=13.5,
              family='Times New Roman')
    f.text(bx + 86, y0 + 56, T(lang, 'The context does<br>not grow with<br>the steps', '上下文不随<br>步数增长'), size=12, color=MUTED, lh=1.3)
    f.text(bx, Y + H - 34, T(lang, 'Reward only at the end:<br>' + m('R', 14) + ' = 1 if solved within 20 steps', '只在最后给奖励：<br>20 步内完成 ' + m('R', 14) + ' = 1'),
           size=12, color=MUTED, lh=1.3)


def group_panel(f, lang, GX, GY, GW, GH):
    f.panel(GX, GY, GW, GH, SLATE, T(lang, 'A Group of N = 8 Rollouts of the Same Task', '同一任务的一组 N = 8 条 rollout'))
    f.text(MEAN_X, GY + 46, T(lang, 'Episode Level', '整局'), size=12.5, bold=True, anchor='c')
    row_y = [GY + 70, GY + 114, GY + 158]
    group_rows(f, GX, GY, GX + 60, 62, row_y, rows=ROWS2)
    for r, (states, ok) in enumerate(ROWS2):
        bar(f, MEAN_X, row_y[r], 48 if ok else -24, LEAF if ok else ROSE)
    f.line([(MEAN_X, GY + 58), (MEAN_X, GY + 172)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(MEAN_X, GY + 186, T(lang, 'Outcome vs group mean', '结局与组均值比较'), size=11.5, color=MUTED, anchor='c')
    f.text(GX + 16, GY + 194, '⋮', size=15, family='Times New Roman')
    f.text(GX + 40, GY + 204, T(lang, 'All start from ' + msub('s', '0') + '; ' + msub('s', '2') + ' (holding the mug) is reached in three: the same observation hash',
                                 '都从 ' + msub('s', '0') + ' 出发；三条都到达了 ' + msub('s', '2') + '（手里拿着杯子）：环境观察的哈希相同'), size=12, color=LAV['dark'])


def step_panel(f, lang, SX, SY, SW, SH):
    f.panel(SX, SY, SW, SH, LAV, T(lang, 'Step Level: Steps Taken from the Same State', '步级：从同一状态出发的各步'))
    f.text(MEAN_X, SY + 46, T(lang, 'Step Level', '步级'), size=12.5, bold=True, anchor='c')
    cy = SY + 96
    state(f, SX + 44, cy, '2', shared=True)
    acts = [('go to fridge 1', '3', 1), ('go to cabinet 1', '7', 0), ('go to sinkbasin 1', '9', 0)]
    for k, (act, nxt, g) in enumerate(acts):
        y = SY + 64 + k * 32
        f.edge([(SX + 60, cy), (SX + 84, y)], width=1.1, end=4)
        e = f.chip(SX + 86, y, act, SLATE, size=11.5, h=19, pad=5)
        f.edge([(e + 4, y), (SX + 248, y)], width=1.1, end=4)
        state(f, SX + 266, y, nxt, w=30)
        f.text(SX + 300, y, f'{m("G", 14)} = {g}', size=13)
        bar(f, MEAN_X, y, 40 if g else -20, LEAF if g else ROSE)
    f.line([(MEAN_X, SY + 54), (MEAN_X, SY + 138)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(MEAN_X, SY + 150, T(lang, 'Return vs the mean of these steps', '回报与这几步的均值比较'), size=11.5, color=MUTED, anchor='c')


def combine_eq(f, lang, CX, CY, CW, CH):
    f.panel(CX, CY, CW, CH, SKY, T(lang, 'Add the Two, Then Update the Agent', '两部分相加，再更新 Agent'))
    y = CY + 54
    x0, x1 = f.text(CX + 18, y, T(lang, 'Step from ' + msub('s', '2') + ' in ' + msub('τ', '1') + ':', msub('τ', '1') + ' 中从 ' + msub('s', '2') + ' 出发的一步：'), size=12.5)
    x = x1 + 16
    bar(f, x, y, 52, LEAF, h=14)
    f.circle_op(x + 70, y, 'plus', r=8.5)
    bar(f, x + 88, y, 42, LEAF, h=14)
    f.text(x + 144, y, '=', size=15)
    f.box(x + 160, y - 7, 52, 14, fill=SKY['tok'], stroke=SKY['line'], width=0.9, arc=2)
    f.box(x + 212, y - 7, 42, 14, fill=SKY['fill'], stroke=SKY['line'], width=0.9, arc=2)
    for cx_, t in ((x + 26, T(lang, 'episode', '整局')), (x + 109, T(lang, 'step', '步级')), (x + 207, T(lang, 'advantage', '优势'))):
        f.text(cx_, y + 18, t, size=11, color=MUTED, anchor='c')
    f.text(CX + CW - 16, y, T(lang, 'No critic · no extra rollouts', '无需 critic · 无需额外 rollout'), size=12.5, color=MUTED, anchor='e')
    f.edge([(CX + 6, CY + 40), (232 + 2, CY + 40)], color=SKY['line'], width=1.6, end=6)


def combine_contrast(f, lang, CX, CY, CW, CH):
    """Round-2 innovative: the credit of every step of the successful rollout, GRPO against StepCredit-RL."""
    f.panel(CX, CY, CW, CH, SKY, T(lang, 'Credit for the Steps of ' + msub('τ', '1') + ', Then Update the Agent', msub('τ', '1') + ' 各步的信用，再更新 Agent'))
    labels = [('GRPO', False), ('StepCredit-RL', True)]
    xs = [CX + 150 + i * 58 for i in range(4)]
    steps = [msub('s', '0') + ' →', msub('s', '1') + ' →', msub('s', '2') + ' →', msub('s', '3') + ' →']
    for i, x in enumerate(xs):
        f.text(x + 12, CY + 44, steps[i], size=12.5, anchor='c')
    for r, (name, ours) in enumerate(labels):
        y = CY + 70 + r * 26
        f.text(CX + 18, y, name, size=12.5, bold=ours)
        for i, x in enumerate(xs):
            f.box(x, y - 7, 26, 14, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
            if ours and i in (0, 2):
                f.box(x + 26, y - 7, 14 if i == 0 else 18, 14, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
    f.text(xs[-1] + 66, CY + 70, T(lang, 'Same credit for every step', '每一步的信用都相同'), size=12, color=MUTED)
    f.text(xs[-1] + 66, CY + 96, T(lang, 'Steps from shared states get more', '从共享状态出发的步得到更多'), size=12, color=MUTED)
    f.text(CX + 18, CY + 118, T(lang, 'Episode part + step part · no critic · no extra rollouts', '整局部分 + 步级部分 · 无需 critic · 无需额外 rollout'), size=12, color=MUTED)
    f.edge([(CX + 6, CY + 40), (232 + 2, CY + 40)], color=SKY['line'], width=1.6, end=6)


def build(v, lang):
    if v[:2] in ('r4', 'r5', 'r6'):
        return build46(v)
    if v.startswith('r3'):
        return build3(v, lang)
    if v == 'r1i':
        return build_i(lang)
    if v == 'r1a':
        return build_a(lang)
    if v == 'r1m':
        return build_m(lang)
    contrast = v in ('r2i', 'r2m', 'r3a', 'r3i', 'r3m')
    H = 562 if contrast else 500
    f = Fig(WIDTH, H, LABEL)
    agent_loop2(f, lang, 6, 6, 226, H - 12)
    group_panel(f, lang, 258, 6, 616, 220)
    step_panel(f, lang, 258, 238, 616, 166)
    if contrast:
        combine_contrast(f, lang, 258, 416, 616, H - 6 - 416)
    else:
        combine_eq(f, lang, 258, 416, 616, 78)
    return f


# ------------------------------------------------------------------ round 3
def agent_loop3(f, lang, X, Y, W, H):
    """Round 3: numbered; below the loop three short sections with the same heading style: one sample per step,
    one RL step (16 tasks x 8 rollouts, asynchronous vLLM rollouts), the reward."""
    f.panel(X, Y, W, H, SKY, T(lang, 'Multi-Turn Agent Loop', '多轮 Agent 交互'), num=1)
    bx, bw = X + 14, W - 28
    f.box(bx, Y + 42, bw, 48, fill=SKY['fill'], stroke=SKY['line'], label=two_line('LLM Agent', 'Qwen3-4B'), size=13.5)
    yb = Y + 196
    f.box(bx, yb, bw, 48, fill=LEMON['soft'], stroke=LEMON['line'],
          label=two_line(T(lang, 'Environment', '环境'), T(lang, 'ALFWorld household tasks', 'ALFWorld 家务任务')), size=13.5)
    xa, xb = bx + bw * 0.3, bx + bw * 0.72
    f.edge([(xa, Y + 90), (xa, yb)], end=5)
    f.edge([(xb, yb), (xb, Y + 90)], end=5)
    ca, cb = 'go to fridge 1', '“You arrive at fridge 1.”'
    wa, wb = label_w(ca, 11.5) + 10, label_w(cb, 11.5) + 10
    f.chip(xa - wa / 2, Y + 124, ca, SLATE, size=11.5, h=19, pad=5)
    f.chip(min(xb - wb / 2, X + W - 8 - wb), Y + 162, cb, SLATE, size=11.5, h=19, pad=5)
    y0 = yb + 80
    f.text(bx, y0, T(lang, 'One Training Sample per Step', '每一步一条训练样本'), size=12.5, bold=True)
    for k in range(3):
        lab = f'<span style="font-family:Times New Roman;"><i>s</i><sub>{k}</sub> → <i>a</i><sub>{k}</sub></span>'
        f.box(bx, y0 + 16 + k * 26, 74, 20, fill=WHITE, stroke=SLATE['line'], width=1, arc=5, label=lab, size=13.5,
              family='Times New Roman')
    f.text(bx + 86, y0 + 52, T(lang, 'The context does<br>not grow with<br>the steps', '上下文不随<br>步数增长'), size=12, color=MUTED, lh=1.3)
    y1 = y0 + 124
    f.text(bx, y1, T(lang, 'One RL Step', '每个 RL 步'), size=12.5, bold=True)
    f.text(bx, y1 + 26, T(lang, f'16 tasks {TIMES} 8 rollouts,<br>asynchronous vLLM rollouts', f'16 个任务 {TIMES} 8 条 rollout，<br>vLLM 异步 rollout'),
           size=12, color=MUTED, lh=1.3)
    y2 = y1 + 80
    f.text(bx, y2, T(lang, 'Reward', '奖励'), size=12.5, bold=True)
    f.text(bx, y2 + 26, T(lang, 'Only at the end: ' + m('R', 14) + ' = 1<br>if solved within 20 steps', '只在最后给：20 步内<br>完成 ' + m('R', 14) + ' = 1，否则 0'),
           size=12, color=MUTED, lh=1.3)


def group_panel3(f, lang, GX, GY, GW, GH, task=False):
    f.panel(GX, GY, GW, GH, SLATE, T(lang, 'A Group of N = 8 Rollouts of the Same Task', '同一任务的一组 N = 8 条 rollout'), num=2)
    if task:
        t = T(lang, 'Task: “put a cool mug in cabinet”', '任务：“put a cool mug in cabinet”')
        w = label_w(t, 11.5) + 12
        f.chip(GX + GW - 14 - w, GY + 20, t, LEMON, size=11.5, h=20, pad=6)
    head = T(lang, 'Episode Level', '整局')
    hw = label_w(head, 12.5, True)
    f.badge(MEAN_X - hw / 2 - 13, GY + 46, 3, SLATE, r=8.5, size=11, role='dark')
    f.text(MEAN_X + 2, GY + 46, head, size=12.5, bold=True, anchor='c')
    row_y = [GY + 74, GY + 116, GY + 158]
    group_rows(f, GX, GY, GX + 60, 62, row_y, rows=ROWS2)
    for r, (states, ok) in enumerate(ROWS2):
        bar(f, MEAN_X, row_y[r], 48 if ok else -24, LEAF if ok else ROSE)
    f.line([(MEAN_X, GY + 60), (MEAN_X, GY + 172)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(MEAN_X, GY + 186, T(lang, 'Outcome vs group mean', '结局与组均值比较'), size=11.5, color=MUTED, anchor='c')
    f.text(GX + 16, GY + 192, '⋮', size=15, family='Times New Roman')
    f.text(GX + 40, GY + 202, T(lang, 'All start at ' + msub('s', '0') + '; three reach ' + msub('s', '2') + ' (holding the mug): the same observation hash',
                                 '都从 ' + msub('s', '0') + ' 出发；三条到达 ' + msub('s', '2') + '（手里拿着杯子）：环境观察的哈希相同'), size=12, color=LAV['dark'])


def step_panel3(f, lang, SX, SY, SW, SH):
    f.panel(SX, SY, SW, SH, LAV, T(lang, 'Step Level: Steps Taken from the Same State', '步级：从同一状态出发的各步'), num=4)
    f.text(MEAN_X, SY + 46, T(lang, 'Step Level', '步级'), size=12.5, bold=True, anchor='c')
    cy = SY + 96
    state(f, SX + 44, cy, '2', shared=True)
    acts = [('go to fridge 1', '3', 1), ('go to cabinet 1', '7', 0), ('go to sinkbasin 1', '9', 0)]
    for k, (act, nxt, g) in enumerate(acts):
        y = SY + 64 + k * 32
        f.edge([(SX + 60, cy), (SX + 84, y)], width=1.1, end=4)
        e = f.chip(SX + 86, y, act, SLATE, size=11.5, h=19, pad=5)
        f.edge([(e + 4, y), (SX + 248, y)], width=1.1, end=4)
        state(f, SX + 266, y, nxt, w=30)
        f.text(SX + 300, y, f'{m("G", 14)} = {g}', size=13)
        bar(f, MEAN_X, y, 40 if g else -20, LEAF if g else ROSE)
    f.line([(MEAN_X, SY + 54), (MEAN_X, SY + 138)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(MEAN_X, SY + 150, T(lang, 'Return vs the mean of these steps', '回报与这几步的均值比较'), size=11.5, color=MUTED, anchor='c')


def combine3(f, lang, CX, CY, CW, CH):
    """Round 3: numbered; the bottom line is a small equation with swatches, so the two shades need no guessing."""
    f.panel(CX, CY, CW, CH, SKY, T(lang, 'Credit for the Steps of ' + msub('τ', '1') + ', Then Update the Agent',
                                   msub('τ', '1') + ' 各步的信用，再更新 Agent'), num=5)
    xs = [CX + 150 + i * 58 for i in range(4)]
    steps = [msub('s', str(i)) + ' →' for i in range(4)]
    for i, x in enumerate(xs):
        f.text(x + 12, CY + 44, steps[i], size=12.5, anchor='c')
    for r, (name, ours) in enumerate((('GRPO', False), ('StepCredit-RL', True))):
        y = CY + 68 + r * 26
        f.text(CX + 18, y, name, size=12.5, bold=ours)
        for i, x in enumerate(xs):
            f.box(x, y - 7, 26, 14, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
            if ours and i in (0, 2):
                f.box(x + 26, y - 7, 14 if i == 0 else 18, 14, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
    f.text(xs[-1] + 66, CY + 68, T(lang, 'Same credit for every step', '每一步的信用都相同'), size=12, color=MUTED)
    f.text(xs[-1] + 66, CY + 94, T(lang, 'Steps from shared states get more', '从共享状态出发的步得到更多'), size=12, color=MUTED)
    y = CY + 120
    x = CX + 18
    f.box(x, y - 6, 16, 12, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
    x0, x = f.text(x + 21, y, T(lang, 'Episode part', '整局部分'), size=12, color=MUTED)
    f.box(x + 16, y - 6, 16, 12, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
    f.text(x + 37, y, T(lang, 'Step part, added on top', '步级部分，叠加在上面'), size=12, color=MUTED)
    f.text(CX + CW - 16, y, T(lang, 'No critic · no extra rollouts', '无需 critic · 无需额外 rollout'), size=12, color=MUTED, anchor='e')
    f.edge([(CX + 6, CY + 40), (232 + 2, CY + 40)], color=SKY['line'], width=1.6, end=6)


def build3(v, lang):
    H = 562
    f = Fig(WIDTH, H, LABEL)
    agent_loop3(f, lang, 6, 6, 226, H - 12)
    group_panel3(f, lang, 258, 6, 616, 220, task=(v in ('r3i', 'r3m')))
    step_panel3(f, lang, 258, 238, 616, 166)
    combine3(f, lang, 258, 416, 616, H - 6 - 416)
    return f


# ------------------------------------------------------------------ rounds 4-6: English only, 720 px wide
# The project pages show figures 724 px wide on a desktop; at 880 px every label was shown at 0.82 of its size.
W4 = 720


def two4(title, sub):
    return two_line(title, sub, 13.5, 12)


def sample_cards(f, x, y, n=3, w=58, h=20, gap=8, vertical=False):
    """One training sample per step: equal cards s_k -> a_k."""
    for k in range(n):
        lab = f'<span style="font-family:Times New Roman;"><i>s</i><sub>{k}</sub> → <i>a</i><sub>{k}</sub></span>'
        xx, yy = (x, y + k * (h + gap)) if vertical else (x + k * (w + gap), y)
        f.box(xx, yy, w, h, fill=WHITE, stroke=SLATE['line'], width=1, arc=5, label=lab, size=13.5, family='Times New Roman')


def agent_loop4a(f, X, Y, W, H):
    """Round-4 aesthetic: the round-3 agent column on the 720 grid (200 px wide)."""
    f.panel(X, Y, W, H, SKY, 'Multi-Turn Agent Loop', num=1)
    bx, bw = X + 14, W - 28
    f.box(bx, Y + 42, bw, 48, fill=SKY['fill'], stroke=SKY['line'], label=two4('LLM Agent', 'Qwen3-4B'), size=13.5)
    yb = Y + 196
    f.box(bx, yb, bw, 48, fill=LEMON['soft'], stroke=LEMON['line'], label=two4('Environment', 'ALFWorld household tasks'), size=13.5)
    xa, xb = bx + bw * 0.27, bx + bw * 0.74
    f.edge([(xa, Y + 90), (xa, yb)], end=5)
    f.edge([(xb, yb), (xb, Y + 90)], end=5)
    ca = 'go to fridge 1'
    wa = label_w(ca, 12) + 12
    f.chip(xa - wa / 2, Y + 124, ca, SLATE, size=12, h=20, pad=6)
    cb = '“You arrive<br>at fridge 1.”'
    wb = label_w(cb, 12) + 12
    f.box(xb - wb / 2, Y + 144, wb, 36, fill=SLATE['soft'], stroke=SLATE['line'], width=1, arc=5, label=cb, size=12)
    y0 = yb + 78
    f.text(bx, y0, 'One Training Sample per Step', size=12, bold=True)
    sample_cards(f, bx, y0 + 14, w=72, h=20, gap=6, vertical=True)
    f.text(bx + 84, y0 + 51, 'The context<br>does not grow<br>with the steps', size=12, color=MUTED, lh=1.3)
    y1 = y0 + 116
    f.text(bx, y1, 'One RL Step', size=12, bold=True)
    f.text(bx, y1 + 24, f'16 tasks {TIMES} 8 rollouts,<br>asynchronous vLLM rollouts', size=12, color=MUTED, lh=1.3)
    y2 = y1 + 74
    f.text(bx, y2, 'Reward', size=12, bold=True)
    f.text(bx, y2 + 24, 'Only at the end: ' + m('R', 13.5) + ' = 1<br>if solved within 20 steps', size=12, color=MUTED, lh=1.3)


def group4a(f, X, Y, W, H, mean_x):
    f.panel(X, Y, W, H, SLATE, 'A Group of N = 8 Rollouts of the Same Task', num=2)
    t = 'Task: “put a cool mug in cabinet”'
    f.chip(X + 14, Y + 48, t, LEMON, size=12, h=20, pad=6)
    head = 'Episode Level'
    hw = label_w(head, 12.5, True)
    f.badge(mean_x - hw / 2 - 12, Y + 48, 3, SLATE, r=8.5, size=11, role='dark')
    f.text(mean_x + 2, Y + 48, head, size=12.5, bold=True, anchor='c')
    row_y = [Y + 84, Y + 122, Y + 160]
    group_rows(f, X, Y, X + 54, 47, row_y, with_outcome=False, w=28, rows=ROWS2)
    for r, (states, ok) in enumerate(ROWS2):
        outcome(f, X + 54 + 4 * 47 + 26, row_y[r], ok, w=60)
        bar(f, mean_x, row_y[r], 44 if ok else -22, LEAF if ok else ROSE)
    f.line([(mean_x, Y + 68), (mean_x, Y + 174)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(mean_x, Y + 188, 'Outcome vs group mean', size=12, color=MUTED, anchor='c')
    f.text(X + 16, Y + 186, '⋮', size=15, family='Times New Roman')
    f.text(X + 34, Y + 196, 'All start at ' + msub('s', '0') + '; three reach ' + msub('s', '2') + ' (holding the mug):<br>the same observation hash',
           size=12, color=LAV['dark'], lh=1.25)


def step4a(f, X, Y, W, H, mean_x):
    f.panel(X, Y, W, H, LAV, 'Step Level: Steps Taken from the Same State', num=4)
    f.text(mean_x, Y + 46, 'Step Level', size=12.5, bold=True, anchor='c')
    cy = Y + 98
    state(f, X + 34, cy, '2', shared=True, w=28)
    acts = [('go to fridge 1', '3', 1), ('go to cabinet 1', '7', 0), ('go to sinkbasin 1', '9', 0)]
    for k, (act, nxt, g) in enumerate(acts):
        y = Y + 66 + k * 32
        f.edge([(X + 48, cy), (X + 70, y)], width=1.1, end=4)
        e = f.chip(X + 72, y, act, SLATE, size=12, h=20, pad=6)
        f.edge([(e + 4, y), (X + 222, y)], width=1.1, end=4)
        state(f, X + 236, y, nxt, w=28)
        f.text(X + 262, y, f'{m("G", 13.5)} = {g}', size=13)
        bar(f, mean_x, y, 38 if g else -19, LEAF if g else ROSE)
    f.line([(mean_x, Y + 54), (mean_x, Y + 142)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(mean_x, Y + 160, 'Return vs the mean<br>of these steps', size=12, color=MUTED, anchor='c', lh=1.2)


def credit4a(f, X, Y, W, H, arrow_to=None):
    f.panel(X, Y, W, H, SKY, 'Credit for the Steps of ' + msub('τ', '1') + ', Then Update the Agent', num=5)
    pitch = 46
    xs = [X + 118 + i * pitch for i in range(4)]
    for i, x in enumerate(xs):
        f.text(x + 12, Y + 44, msub('s', str(i)) + ' →', size=12.5, anchor='c')
    rows = (('GRPO', False, 'Same credit for every step'), ('StepCredit-RL', True, 'Steps from shared<br>states get more'))
    for r, (name, ours, desc) in enumerate(rows):
        y = Y + 70 + r * 30
        f.text(X + 14, y, name, size=12.5, bold=ours)
        for i, x in enumerate(xs):
            f.box(x, y - 7, 24, 14, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
            if ours and i in (0, 2):
                f.box(x + 24, y - 7, 12 if i == 0 else 16, 14, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
        f.text(xs[-1] + 52, y, desc, size=12, color=MUTED, lh=1.2)
    y = Y + H - 18
    x = X + 14
    f.box(x, y - 6, 16, 12, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
    x0, x = f.text(x + 21, y, 'Episode part', size=12, color=MUTED)
    f.box(x + 14, y - 6, 16, 12, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
    f.text(x + 35, y, 'Step part, added on top', size=12, color=MUTED)
    f.text(X + W - 14, y, 'No critic · no extra rollouts', size=12, color=MUTED, anchor='e')
    if arrow_to is not None:
        f.edge([(X, Y + 20), (arrow_to + 1, Y + 20)], color=SKY['line'], width=1.6, end=6)


def build4a():
    H = 578
    f = Fig(W4, H, LABEL)
    LW = 200
    agent_loop4a(f, 6, 6, LW, H - 12)
    RX, RW = 6 + LW + 22, W4 - 6 - (6 + LW + 22)
    mean_x = RX + 404
    group4a(f, RX, 6, RW, 216, mean_x)
    step4a(f, RX, 234, RW, 176, mean_x)
    credit4a(f, RX, 422, RW, H - 6 - 422, arrow_to=6 + LW)
    return f


def agent_strip4(f, X, Y, W, H):
    """Round-4 innovative: the agent loop as a strip: the agent and the environment side by side, the action and the
    observation on the two arrows between them; on the right, one training sample per step."""
    f.panel(X, Y, W, H, SKY, 'Multi-Turn Agent Loop', num=1)
    bw, bh = 136, 46
    ay = Y + 72
    ax0 = X + 14
    ex0 = ax0 + bw + 168
    ew = label_w('ALFWorld household tasks', 12) + 26
    f.box(ax0, ay - bh / 2, bw, bh, fill=SKY['fill'], stroke=SKY['line'], label=two4('LLM Agent', 'Qwen3-4B'), size=13.5)
    f.box(ex0, ay - bh / 2, ew, bh, fill=LEMON['soft'], stroke=LEMON['line'], label=two4('Environment', 'ALFWorld household tasks'), size=13.5)
    y1, y2 = ay - 13, ay + 13
    f.edge([(ax0 + bw + 1, y1), (ex0 - 1, y1)], end=5)
    f.edge([(ex0 - 1, y2), (ax0 + bw + 1, y2)], end=5)
    mid = (ax0 + bw + ex0) / 2
    ca, cb = 'go to fridge 1', '“You arrive at fridge 1.”'
    wa, wb = label_w(ca, 12) + 12, label_w(cb, 12) + 12
    f.chip(mid - wa / 2, y1 - 11, ca, SLATE, size=12, h=20, pad=6)
    f.chip(mid - wb / 2, y2 + 11, cb, SLATE, size=12, h=20, pad=6)
    rx = X + W - 14 - 180
    f.text(rx, Y + 46, 'One Training Sample per Step', size=12, bold=True)
    sample_cards(f, rx, Y + 62, w=54, h=20, gap=9)
    f.text(rx, Y + 98, 'The context does not grow', size=12, color=MUTED)


ALIGNED4 = [(['0', '1', '2'], '3', 'go to fridge 1', True), (['0', '5', '2'], '7', 'go to cabinet 1', False),
            (['0', '8', '2'], '9', 'go to sinkbasin 1', False)]


def group_table4(f, X, Y, W, H, ex, sx):
    """Round-4 innovative: panels 2-4 as one table. The three rollouts reach s2 at the same step, so the shared state
    is one column; the step that leaves it carries its action; the right columns hold the two comparisons."""
    f.panel(X, Y, W, H, SLATE, 'A Group of N = 8 Rollouts of the Same Task', num=2)
    t = 'Task: “put a cool mug in cabinet”'
    tw = label_w(t, 12) + 12
    f.chip(X + W - 14 - tw, Y + 20, t, LEMON, size=12, h=20, pad=6)
    row_y = [Y + 86, Y + 124, Y + 162]
    pitch, w = 46, 28
    c0 = X + 56
    cs2 = c0 + 2 * pitch
    f.box(cs2 - 21, row_y[0] - 24, 42, row_y[-1] - row_y[0] + 48, fill=LAV['soft'], stroke=LAV['tok'], width=1, arc=9)
    for r, (states, nxt, act, ok) in enumerate(ALIGNED4):
        y = row_y[r]
        f.text(X + 14, y, msub('τ', r + 1, 15), size=13)
        for c, k in enumerate(states):
            cx = c0 + c * pitch
            state(f, cx, y, k, shared=(k == '2'), w=w)
            if c:
                f.edge([(cx - pitch + w / 2 + 1, y), (cx - w / 2 - 1, y)], width=1.1, end=5)
        nx = cs2 + 150
        pal = LEAF if ok else ROSE
        f.edge([(cs2 + w / 2 + 1, y), (nx - w / 2 - 1, y)], color=pal['line'], width=1.5, end=5)
        aw = label_w(act, 12) + 12
        f.chip((cs2 + nx) / 2 - aw / 2 - 4, y, act, SLATE, size=12, h=20, pad=6)
        state(f, nx, y, nxt, w=w)
        f.text(nx + w / 2 + 8, y, '⋯', size=14, family='Times New Roman')
        outcome(f, nx + 46, y, ok)
        bar(f, ex, y, 44 if ok else -22, LEAF if ok else ROSE)
        bar(f, sx, y, 38 if ok else -19, LEAF if ok else ROSE)
    for cx, num, head, sub, nl in ((ex, 3, 'Episode Level', 'Outcome vs group mean', 1), (sx, 4, 'Step Level', 'Return vs the mean<br>of these steps', 2)):
        hw = label_w(head, 12.5, True)
        f.badge(cx - hw / 2 - 12, Y + 52, num, LAV if num == 4 else SLATE, r=8.5, size=11, role='dark')
        f.text(cx + 2, Y + 52, head, size=12.5, bold=True, anchor='c')
        f.line([(cx, Y + 68), (cx, Y + 178)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
        f.text(cx, Y + 192 + (6 if nl == 2 else 0), sub, size=12, color=MUTED, anchor='c', lh=1.2)
    f.text(X + 14, Y + H - 17, 'All start at ' + msub('s', '0') + '; three reach ' + msub('s', '2') + ' (holding the mug), found by the same observation hash',
           size=12, color=LAV['dark'])


def credit4i(f, X, Y, W, H):
    f.panel(X, Y, W, H, SKY, 'Credit for the Steps of ' + msub('τ', '1') + ', Then Update the Agent', num=5)
    pitch = 62
    xs = [X + 150 + i * pitch for i in range(4)]
    for i, x in enumerate(xs):
        f.text(x + 14, Y + 46, msub('s', str(i)) + ' →', size=13, anchor='c')
    rows = (('GRPO', False, 'Same credit for every step'), ('StepCredit-RL', True, 'Steps from shared states get more'))
    for r, (name, ours, desc) in enumerate(rows):
        y = Y + 72 + r * 28
        f.text(X + 14, y, name, size=13, bold=ours)
        for i, x in enumerate(xs):
            f.box(x, y - 7.5, 28, 15, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
            if ours and i in (0, 2):
                f.box(x + 28, y - 7.5, 14 if i == 0 else 19, 15, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
        f.text(xs[-1] + 74, y, desc, size=12.5, color=MUTED)
    y = Y + H - 18
    x = X + 14
    f.box(x, y - 6, 16, 12, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
    x0, x = f.text(x + 21, y, 'Episode part', size=12, color=MUTED)
    f.box(x + 14, y - 6, 16, 12, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
    f.text(x + 35, y, 'Step part, added on top', size=12, color=MUTED)
    f.text(X + W - 14, y, 'No critic · no extra rollouts', size=12, color=MUTED, anchor='e')


def build4i():
    H = 6 + 118 + 12 + 224 + 12 + 140 + 6
    f = Fig(W4, H, LABEL)
    agent_strip4(f, 6, 6, 708, 118)
    group_table4(f, 6, 136, 708, 224, ex=500, sx=626)
    credit4i(f, 6, 372, 708, 140)
    return f


# Illustrative baselines: the episode level compares with all N = 8 rollouts (say four of them succeed, mean 0.5), the
# step level only with the three steps taken from s2 (mean 1/3); so the two columns differ, as they do in training.
EP4 = {True: 0.5, False: -0.5}
ST4 = {True: 2 / 3, False: -1 / 3}


def group_table4m(f, X, Y, W, H, ex, sx, unit=60):
    """Round-4 merge: the r4i table with the column notes under the column heads, bars that show the two different
    baselines, and the observation-hash note on its own line."""
    f.panel(X, Y, W, H, SLATE, 'A Group of N = 8 Rollouts of the Same Task', num=2)
    t = 'Task: “put a cool mug in cabinet”'
    tw = label_w(t, 12) + 12
    f.chip(X + W - 14 - tw, Y + 20, t, LEMON, size=12, h=20, pad=6)
    row_y = [Y + 100, Y + 138, Y + 176]
    pitch, w = 46, 28
    c0 = X + 56
    cs2 = c0 + 2 * pitch
    f.box(cs2 - 21, row_y[0] - 24, 42, row_y[-1] - row_y[0] + 48, fill=LAV['soft'], stroke=LAV['tok'], width=1, arc=9)
    for r, (states, nxt, act, ok) in enumerate(ALIGNED4):
        y = row_y[r]
        f.text(X + 14, y, msub('τ', r + 1, 15), size=13)
        for c, k in enumerate(states):
            cx = c0 + c * pitch
            state(f, cx, y, k, shared=(k == '2'), w=w)
            if c:
                f.edge([(cx - pitch + w / 2 + 1, y), (cx - w / 2 - 1, y)], width=1.1, end=5)
        nx = cs2 + 150
        pal = LEAF if ok else ROSE
        f.edge([(cs2 + w / 2 + 1, y), (nx - w / 2 - 1, y)], color=pal['line'], width=1.5, end=5)
        aw = label_w(act, 12) + 12
        f.chip((cs2 + nx) / 2 - aw / 2 - 4, y, act, SLATE, size=12, h=20, pad=6)
        state(f, nx, y, nxt, w=w)
        f.text(nx + w / 2 + 8, y, '⋯', size=14, family='Times New Roman')
        outcome(f, nx + 46, y, ok)
        bar(f, ex, y, unit * EP4[ok], LEAF if ok else ROSE)
        bar(f, sx, y, unit * ST4[ok], LEAF if ok else ROSE)
    for cx, num, head, sub in ((ex, 3, 'Episode Level', 'Outcome vs group mean'), (sx, 4, 'Step Level', 'Return vs steps from ' + msub('s', '2'))):
        hw = label_w(head, 12.5, True)
        f.badge(cx - hw / 2 - 12, Y + 50, num, LAV if num == 4 else SLATE, r=8.5, size=11, role='dark')
        f.text(cx + 2, Y + 50, head, size=12.5, bold=True, anchor='c')
        f.text(cx, Y + 69, sub, size=12, color=MUTED, anchor='c')
        f.line([(cx, Y + 82), (cx, Y + 192)], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(X + 14, Y + H - 17, 'All start at ' + msub('s', '0') + '; three reach ' + msub('s', '2') + ' (holding the mug), found by the same observation hash',
           size=12, color=LAV['dark'])


def credit4m(f, X, Y, W, H):
    """Round-4 merge: r4i's credit panel; the extra parts follow the step-level bars (s0: 0.5, s2: 2/3 of the unit)."""
    f.panel(X, Y, W, H, SKY, 'Credit for the Steps of ' + msub('τ', '1') + ', Then Update the Agent', num=5)
    pitch = 64
    xs = [X + 150 + i * pitch for i in range(4)]
    base_w = 26
    for i, x in enumerate(xs):
        f.text(x + 16, Y + 46, msub('s', str(i)) + ' →', size=13, anchor='c')
    rows = (('GRPO', False, 'Same credit for every step'), ('StepCredit-RL', True, 'Steps from shared states get more'))
    for r, (name, ours, desc) in enumerate(rows):
        y = Y + 72 + r * 28
        f.text(X + 14, y, name, size=13, bold=ours)
        for i, x in enumerate(xs):
            f.box(x, y - 7.5, base_w, 15, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
            if ours and i in (0, 2):
                f.box(x + base_w, y - 7.5, base_w * (1.0 if i == 0 else 4 / 3), 15, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
        f.text(xs[-1] + 78, y, desc, size=12.5, color=MUTED)
    y = Y + H - 18
    x = X + 14
    f.box(x, y - 6, 16, 12, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
    x0, x = f.text(x + 21, y, 'Episode part', size=12, color=MUTED)
    f.box(x + 14, y - 6, 16, 12, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
    f.text(x + 35, y, 'Step part, added on top', size=12, color=MUTED)
    f.text(X + W - 14, y, 'No critic · no extra rollouts', size=12, color=MUTED, anchor='e')


def build4m():
    H = 6 + 118 + 12 + 236 + 12 + 140 + 6
    f = Fig(W4, H, LABEL)
    agent_strip4(f, 6, 6, 708, 118)
    group_table4m(f, 6, 136, 708, 236, ex=486, sx=630)
    credit4m(f, 6, 384, 708, 140)
    return f


def build46(v):
    """Rounds 4-6 (English only)."""
    return {'r4a': build4a, 'r4i': build4i, 'r4m': build4m, 'r5a': build5a, 'r5i': build5i,
            'r5m': lambda: build5(rest='line'), 'r6a': build6a, 'r6i': build6i, 'r6m': build6m}[v]()


# ------------------------------------------------------------------ round 5
def group_table5(f, X, Y, W, H, ex, sx, unit=60, rest=False, chip_left=True):
    """Round 5: r4m's table; the task chip fills the empty corner under the title; with rest, a faded fourth row
    stands for the other five rollouts of the group, which never reach s2 (three of them succeed), so the reader can
    see why the episode-level mean is 0.5 while the mean of the steps from s2 is 1/3."""
    f.panel(X, Y, W, H, SLATE, 'A Group of N = 8 Rollouts of the Same Task', num=2)
    t = 'Task: “put a cool mug in cabinet”'
    tw = label_w(t, 12) + 12
    if chip_left:
        f.chip(X + 14, Y + 52, t, LEMON, size=12, h=20, pad=6)
    else:
        f.chip(X + W - 14 - tw, Y + 20, t, LEMON, size=12, h=20, pad=6)
    row_y = [Y + 100, Y + 138, Y + 176]
    pitch, w = 46, 28
    c0 = X + 56
    cs2 = c0 + 2 * pitch
    f.box(cs2 - 21, row_y[0] - 24, 42, row_y[2] - row_y[0] + 48, fill=LAV['soft'], stroke=LAV['tok'], width=1, arc=9)
    nx = cs2 + 150
    for r, (states, nxt, act, ok) in enumerate(ALIGNED4):
        y = row_y[r]
        f.text(X + 14, y, msub('τ', r + 1, 15), size=13)
        for c, k in enumerate(states):
            cx = c0 + c * pitch
            state(f, cx, y, k, shared=(k == '2'), w=w)
            if c:
                f.edge([(cx - pitch + w / 2 + 1, y), (cx - w / 2 - 1, y)], width=1.1, end=5)
        pal = LEAF if ok else ROSE
        f.edge([(cs2 + w / 2 + 1, y), (nx - w / 2 - 1, y)], color=pal['line'], width=1.5, end=5)
        aw = label_w(act, 12) + 12
        f.chip((cs2 + nx) / 2 - aw / 2 - 4, y, act, SLATE, size=12, h=20, pad=6)
        state(f, nx, y, nxt, w=w)
        f.text(nx + w / 2 + 8, y, '⋯', size=14, family='Times New Roman')
        outcome(f, nx + 46, y, ok)
        bar(f, ex, y, unit * EP4[ok], LEAF if ok else ROSE)
        bar(f, sx, y, unit * ST4[ok], LEAF if ok else ROSE)
    y_end = row_y[-1] + 16
    if rest == 'line':
        # the rest of the group on one dashed line, its label sitting on the line; their outcomes under the pills
        y4 = row_y[-1] + 40
        lab = '<span style="font-family:Times New Roman;"><i>τ</i><sub>4</sub>–<i>τ</i><sub>8</sub></span>'
        f.text(X + 14, y4, lab, size=13, color=MUTED)
        f.line([(X + 64, y4), (nx + 16, y4)], color=SLATE['tok'], width=1.2, dashed=True, dash='4 3')
        t4 = 'Five more rollouts that never reach ' + msub('s', '2')
        w4 = label_w(t4, 12) + 14
        f.box((X + 64 + nx + 16) / 2 - w4 / 2, y4 - 9, w4, 18, fill=SLATE['pale'], stroke='none', width=0, arc=4,
              label=t4, size=12, color=MUTED)
        for k in range(5):
            cx = nx + 46 + 8 + k * 12
            (f.check if k < 3 else f.cross)(cx, y4, s=6.5 if k < 3 else 6, color=(LEAF['dark'] if k < 3 else ROSE['dark']), width=1.8)
        y_end = y4 + 12
    elif rest == 'above':
        # the rest of the group: a dashed line with its label above it, clear of the s2 band
        y4 = row_y[-1] + 50
        lab = '<span style="font-family:Times New Roman;"><i>τ</i><sub>4</sub>–<i>τ</i><sub>8</sub></span>'
        f.text(X + 14, y4, lab, size=13, color=MUTED)
        f.line([(X + 64, y4), (nx + 16, y4)], color=SLATE['tok'], width=1.2, dashed=True, dash='4 3')
        f.text((X + 64 + nx + 16) / 2, y4 - 12, 'Five more rollouts that never reach ' + msub('s', '2'), size=12, color=MUTED, anchor='c')
        for k in range(5):
            cx = nx + 46 + 8 + k * 12
            (f.check if k < 3 else f.cross)(cx, y4, s=6.5 if k < 3 else 6, color=(LEAF['dark'] if k < 3 else ROSE['dark']), width=1.8)
        y_end = y4 + 12
    elif rest:
        y4 = row_y[-1] + 42
        lab = '<span style="font-family:Times New Roman;"><i>τ</i><sub>4</sub>–<i>τ</i><sub>8</sub></span>'
        f.text(X + 14, y4, lab, size=13, color=MUTED)
        f.line([(c0 - 14, y4), (nx + 14, y4)], color=SLATE['tok'], width=1.2, dashed=True, dash='4 3')
        f.text((c0 + nx) / 2, y4 - 11, 'Five more rollouts that never reach ' + msub('s', '2'), size=12, color=MUTED, anchor='c')
        for k in range(5):
            cx = nx + 46 + 8 + k * 12
            (f.check if k < 3 else f.cross)(cx, y4, s=6.5 if k < 3 else 6, color=(LEAF['dark'] if k < 3 else ROSE['dark']), width=1.8)
        y_end = y4 + 12
    for cx, num, head, sub in ((ex, 3, 'Episode Level', 'Outcome vs group mean'), (sx, 4, 'Step Level', 'Return vs steps from ' + msub('s', '2'))):
        hw = label_w(head, 12.5, True)
        f.badge(cx - hw / 2 - 12, Y + 50, num, LAV if num == 4 else SLATE, r=8.5, size=11, role='dark')
        f.text(cx + 2, Y + 50, head, size=12.5, bold=True, anchor='c')
        f.text(cx, Y + 69, sub, size=12, color=MUTED, anchor='c')
        f.line([(cx, Y + 82), (cx, (y_end if num == 3 else row_y[-1] + 16))], color=SLATE['line'], width=1, dashed=True, dash='3 2')
    f.text(X + 14, Y + H - 17, 'All start at ' + msub('s', '0') + '; three reach ' + msub('s', '2') + ' (holding the mug), found by the same observation hash',
           size=12, color=LAV['dark'])


def credit5(f, X, Y, W, H, pitch=74):
    """Round 5: r4m's credit panel with room between the step columns."""
    f.panel(X, Y, W, H, SKY, 'Credit for the Steps of ' + msub('τ', '1') + ', Then Update the Agent', num=5)
    xs = [X + 150 + i * pitch for i in range(4)]
    base_w = 26
    for i, x in enumerate(xs):
        f.text(x + 16, Y + 46, msub('s', str(i)) + ' →', size=13, anchor='c')
    rows = (('GRPO', False, 'Same credit for every step'), ('StepCredit-RL', True, 'Steps from shared states get more'))
    for r, (name, ours, desc) in enumerate(rows):
        y = Y + 72 + r * 28
        f.text(X + 14, y, name, size=13, bold=ours)
        for i, x in enumerate(xs):
            f.box(x, y - 7.5, base_w, 15, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
            if ours and i in (0, 2):
                f.box(x + base_w, y - 7.5, base_w * (1.0 if i == 0 else 4 / 3), 15, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
        f.text(xs[-1] + 70, y, desc, size=12.5, color=MUTED)
    y = Y + H - 18
    x = X + 14
    f.box(x, y - 6, 16, 12, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
    x0, x = f.text(x + 21, y, 'Episode part', size=12, color=MUTED)
    f.box(x + 14, y - 6, 16, 12, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
    f.text(x + 35, y, 'Step part, added on top', size=12, color=MUTED)
    f.text(X + W - 14, y, 'No critic · no extra rollouts', size=12, color=MUTED, anchor='e')


def build5(rest=False):
    H2 = 236 + (40 if rest == 'line' else 42 if rest else 0)
    H = 6 + 118 + 12 + H2 + 12 + 140 + 6
    f = Fig(W4, H, LABEL)
    agent_strip4(f, 6, 6, 708, 118)
    group_table5(f, 6, 136, 708, H2, ex=486, sx=630, rest=rest)
    credit5(f, 6, 136 + H2 + 12, 708, 140)
    return f


def build5a():
    """Round-5 aesthetic: r4m with the task chip in the empty corner and room between the credit columns."""
    return build5()


def build5i():
    """Round-5 innovative: the rest of the group drawn as one faded row (five rollouts that never reach s2, three of
    them successful), which explains the two baselines."""
    return build5(rest=True)


# ------------------------------------------------------------------ round 6
def credit6(f, X, Y, W, H, pitch=74, update_chip=False):
    """Round 6: r5m's credit panel; update_chip: the title names only the credit, and the update is drawn at the right
    end of the title row as an arrow into a small copy of panel 1's agent box (the same symbol, instead of a long
    arrow back to panel 1)."""
    title = 'Credit for the Steps of ' + msub('τ', '1') + ('' if update_chip else ', Then Update the Agent')
    f.panel(X, Y, W, H, SKY, title, num=5)
    if update_chip:
        bw_ = label_w('LLM Agent', 12.5, True) + 18
        bx_ = X + W - 14 - bw_
        f.box(bx_, Y + 9, bw_, 22, fill=SKY['fill'], stroke=SKY['line'], width=1.2, arc=6, label='<b>LLM Agent</b>', size=12.5)
        f.edge([(bx_ - 30, Y + 20), (bx_ - 1, Y + 20)], color=SKY['line'], width=1.4, end=5)
        f.text(bx_ - 36, Y + 20, 'Policy-gradient update', size=12, color=SKY['dark'], anchor='e', italic=True)
    xs = [X + 150 + i * pitch for i in range(4)]
    base_w = 26
    for i, x in enumerate(xs):
        f.text(x + 16, Y + 46, msub('s', str(i)) + ' →', size=13, anchor='c')
    rows = (('GRPO', False, 'Same credit for every step'), ('StepCredit-RL', True, 'Steps from shared states get more'))
    for r, (name, ours, desc) in enumerate(rows):
        y = Y + 72 + r * 28
        f.text(X + 14, y, name, size=13, bold=ours)
        for i, x in enumerate(xs):
            f.box(x, y - 7.5, base_w, 15, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
            if ours and i in (0, 2):
                f.box(x + base_w, y - 7.5, base_w * (1.0 if i == 0 else 4 / 3), 15, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
        f.text(xs[-1] + 70, y, desc, size=12.5, color=MUTED)
    y = Y + H - 18
    x = X + 14
    f.box(x, y - 6, 16, 12, fill=LEAF['fill'], stroke=LEAF['line'], width=0.9, arc=2)
    x0, x = f.text(x + 21, y, 'Episode part', size=12, color=MUTED)
    f.box(x + 14, y - 6, 16, 12, fill=LEAF['line'], stroke=LEAF['line'], width=0.9, arc=2)
    f.text(x + 35, y, 'Step part, added on top', size=12, color=MUTED)
    f.text(X + W - 14, y, 'No critic · no extra rollouts', size=12, color=MUTED, anchor='e')


def build6(update_chip=False, H2=286):
    H = 6 + 118 + 12 + H2 + 12 + 140 + 6
    f = Fig(W4, H, LABEL)
    agent_strip4(f, 6, 6, 708, 118)
    group_table5(f, 6, 136, 708, H2, ex=486, sx=630, rest='above')
    credit6(f, 6, 136 + H2 + 12, 708, 140, update_chip=update_chip)
    return f


def build6a():
    """Round-6 aesthetic: r5m with the faded row's label above its line (on the line it hid the line), clear of the
    s2 band."""
    return build6()


def build6i():
    """Round-6 innovative: panel 5 ends in the agent box of panel 1 (a policy-gradient update), so the loop closes
    without a long arrow."""
    return build6(update_chip=True)


def build6m():
    """Round-6 merge (final): r6a's faded row and r6i's update into the agent box, the panel 8 px shorter."""
    return build6(update_chip=True, H2=278)
