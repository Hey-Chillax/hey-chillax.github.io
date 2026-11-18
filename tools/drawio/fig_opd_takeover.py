"""Scaffold-OPD method figure: relay rollout in vLLM speculative decoding, the two takeover rules, and the training signal.

Variants: r1a / r1i / r1m (round 1: aesthetic, innovative, merged), r2a / r2i / r2m, r3a / r3i / r3m;
rounds 4-6 (r4a ... r6m) are English only and 720 px wide (one unit = one pixel on the project page); final: r6m.
Facts (projects/scaffold-opd.html): the student (Qwen3-1.7B) drafts inside vLLM speculative decoding and the teacher
(Qwen3-4B) verifies; when the teacher's top-1 next token is one of 45 reflection words and not in the student's top-5,
or when the teacher wants to start the final answer while the student keeps going (the author's addition, in the
verification step), the teacher takes over, writes at most three paragraphs (256 tokens) and hands back; at most two
takeovers, the answer ends after the second; a teacher scorer on a separate GPU scores the whole answer, and every
token, whoever wrote it, is trained with token-level reverse KL to the teacher. The example text is illustrative.
"""
from dlib import (Fig, INK, LAV, LEAF, LINE, MUTED, ROSE, SKY, SLATE, WHITE, label_w, icon_line_w, web_w)

WIDTH = 880
LABEL = ('Scaffold-OPD: the student drafts and the teacher verifies inside vLLM speculative decoding; at a reflection '
         'point or at the conclusion the teacher writes a short passage and hands back; every token of the relayed '
         'answer is then trained toward the teacher')
LABEL_ZH = 'Scaffold-OPD：学生在 vLLM 投机解码中写草稿、老师验证；在反思处或收尾处，老师写一小段后交还；接力回答的每个 token 都向老师训练'


def T(lang, en, zh):
    return zh if lang == 'zh' else en


def two_line(title, sub, size=13.5, sub_size=12):
    return f'<b>{title}</b><br><span style="font-size:{sub_size}px;color:{MUTED};">{sub}</span>'


def legend(f, lang, x, y):
    items = [(SKY, T(lang, 'Student token', '学生 token')), (LEAF, T(lang, 'Teacher token', '老师 token')),
             (LAV, T(lang, 'Takeover point', '接管点')), (None, T(lang, 'Answer ends', '回答结束'))]
    for pal, text in items:
        if pal is None:
            f.box(x, y - 5.5, 11, 11, fill=INK, stroke=INK, width=0.9, arc=2)
        else:
            f.token(x + 5.5, y, pal, size=11)
        x0, x1 = f.text(x + 17, y, text, size=12.5)
        x = x1 + 18


def lanes(f, lang, x0, ys, yt, segs, tok=10, pitch=13, gap=16):
    """Tokens on two lanes. segs: list of (lane, n). The first token of each teacher segment is the takeover point.
    Returns per-segment token centres."""
    x = x0
    out = []
    for lane, n in segs:
        y = ys if lane == 's' else yt
        cs = []
        for i in range(n):
            pal = SKY if lane == 's' else (LAV if i == 0 else LEAF)
            f.token(x + tok / 2, y, pal, size=tok)
            cs.append(x + tok / 2)
            x += pitch
        out.append(cs)
        x += gap - pitch + tok
    return out, x


def relay_panel(f, lang, X, Y, W, H, callouts=False):
    """Panel 1: the models on the left, the relayed answer on two lanes."""
    f.panel(X, Y, W, H, SLATE, T(lang, 'Relay Rollout Inside vLLM Speculative Decoding', 'vLLM 投机解码中的接力生成'), 1)
    bw, bh = 178, 50
    bx = X + 18
    ys, yt = Y + 72, Y + 172
    stu = two_line(T(lang, 'Student', '学生'), T(lang, 'Qwen3-1.7B · Drafts', 'Qwen3-1.7B · 写草稿'))
    tea = two_line(T(lang, 'Teacher', '老师'), T(lang, 'Qwen3-4B · Verifies', 'Qwen3-4B · 验证'))
    f.box(bx, ys - bh / 2, bw, bh, fill=SKY['fill'], stroke=SKY['line'], label=stu, size=13.5)
    f.box(bx, yt - bh / 2, bw, bh, fill=LEAF['fill'], stroke=LEAF['line'], label=tea, size=13.5)
    xa, xb = bx + 52, bx + bw - 52
    f.edge([(xa, ys + bh / 2), (xa, yt - bh / 2)], width=1.2, end=5)
    f.edge([(xb, yt - bh / 2), (xb, ys + bh / 2)], width=1.2, end=5)
    f.text(xa - 7, (ys + yt) / 2, T(lang, 'Draft', '草稿'), size=12, color=MUTED, anchor='e')
    f.text(xb + 7, (ys + yt) / 2, T(lang, 'Accept or<br>Take Over', '接受或<br>接管'), size=12, color=MUTED, anchor='w')
    lx0, lx1 = bx + bw + 22, X + W - 18
    for y in (ys, yt):
        f.line([(lx0, y), (lx1, y)], color=SLATE['tok'], width=1, dashed=True, dash='2 3')
    segs, xend = lanes(f, lang, lx0 + 8, ys, yt, [('s', 12), ('t', 9), ('s', 10), ('t', 6)])
    end_x = xend - 13 + 5 + 3
    f.box(end_x - 5, yt - 5, 10, 10, fill=INK, stroke=INK, width=0.9, arc=2)
    s1, t1, s2, t2 = segs
    # takeovers (lavender, numbered) and the hand back (slate, dashed)
    for k, (a, b) in enumerate(((s1[-1], t1[0]), (s2[-1], t2[0])), start=1):
        p0, p1 = (a + 2, ys + 6), (b - 2, yt - 6)
        f.edge([p0, p1], color=LAV['line'], width=1.6, end=5)
        f.badge((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, k, LAV, r=8.5, size=11)
    f.edge([(t1[-1] + 2, yt - 6), (s2[0] - 2, ys + 6)], color=SLATE['line'], width=1.3, end=5, dashed=True, dash='3 2')
    # example text: the student's words above its lane, the teacher's below its lane
    f.text((s1[0] + s1[-1]) / 2, ys - 19, '“… so the answer is 47.”', size=12.5, color=MUTED, anchor='c', italic=True)
    f.text((s2[0] + s2[-1]) / 2, ys - 19, '“… so the answer is 52.”', size=12.5, color=MUTED, anchor='c', italic=True)
    q1 = '“Wait, let me check step 2 …”'
    q2 = '“### Final Answer: 52”'
    f.text((t1[0] + t1[-1]) / 2, yt + 20, q1, size=12.5, color=LEAF['dark'], anchor='c', bold=True)
    f.text(t2[0] - 4, yt + 20, q2, size=12.5, color=LEAF['dark'], anchor='w', bold=True)
    if not callouts:
        f.hbracket(t1[0] - 5, t1[-1] + 5, yt + 36, depth=4)
        f.text((t1[0] + t1[-1]) / 2, yt + 49, T(lang, 'Up to 3 paragraphs (256 tokens), then hand back', '最多写 3 段（256 token）后交还'),
               size=12, color=MUTED, anchor='c')
        f.text(lx1, yt + 49, T(lang, 'At most 2 takeovers; the answer ends after the second', '最多接管 2 次，第 2 次写完回答即结束'),
               size=12, color=MUTED, anchor='e')
    return dict(ys=ys, yt=yt, s1=s1, t1=t1, s2=s2, t2=t2, end_x=end_x, bx=bx, bw=bw)


def rule_rows(f, lang, x, y, right, kind):
    """One takeover rule drawn as chips: teacher's top-1 on the first row, the student's top-k on the second."""
    lab_w = max(label_w(T(lang, 'Teacher’s top-1', '老师 top-1'), 12.5), label_w(T(lang, 'Student’s top-5', '学生 top-5'), 12.5)) + 10
    if kind == 'reflect':
        f.text(x, y, T(lang, 'Teacher’s top-1', '老师 top-1'), size=12.5, color=MUTED)
        e = f.chip(x + lab_w, y, 'Wait', LEAF, size=12.5, solid=True, bold=True)
        f.text(e + 8, y, T(lang, 'is a reflection word (one of 45, e.g. Wait, But)', '是反思词（共 45 个，如 Wait、But）'), size=12.5)
        y2 = y + 30
        f.text(x, y2, T(lang, 'Student’s top-5', '学生 top-5'), size=12.5, color=MUTED)
        e = x + lab_w
        for w in ('So', 'Then', 'We', 'The', 'Let'):
            e = f.chip(e, y2, w, SKY, size=12.5) + 4
        f.cross(e + 8, y2, s=7)
        f.text(e + 18, y2, T(lang, 'none is a reflection word', '都不是反思词'), size=12.5)
    else:
        f.text(x, y, T(lang, 'Teacher’s top-1', '老师 top-1'), size=12.5, color=MUTED)
        e = f.chip(x + lab_w, y, '### Final Answer', LEAF, size=12.5, solid=True, bold=True)
        f.text(e + 8, y, T(lang, 'starts the final answer', '开始写最终答案'), size=12.5)
        y2 = y + 30
        f.text(x, y2, T(lang, 'Student’s top-1', '学生 top-1'), size=12.5, color=MUTED)
        e = f.chip(x + lab_w, y2, 'So', SKY, size=12.5) + 4
        f.text(e + 6, y2, T(lang, 'keeps reasoning', '还在往下推理'), size=12.5)
    # result
    ym = y + 15
    f.edge([(right - 92, ym), (right - 66, ym)], color=LAV['line'], width=1.6, end=5)
    f.chip(right - 62, ym, T(lang, 'Take Over', '接管'), LAV, size=12.5, solid=True, bold=True)


def rules_panel(f, lang, X, Y, W, H):
    f.panel(X, Y, W, H, LAV, T(lang, 'When Does the Teacher Take Over?', '老师何时接管？'), 2)
    x = X + 20
    f.text(x, Y + 54, T(lang, 'Reflection Trigger', '反思触发'), size=13.5, bold=True)
    rule_rows(f, lang, x, Y + 84, X + W - 14, 'reflect')
    f.line([(X + 14, Y + 138), (X + W - 14, Y + 138)], color=LAV['tok'], width=1, dashed=True, dash='3 3')
    x0, x1 = f.text(x, Y + 160, T(lang, 'Concluding Trigger', '收尾触发'), size=13.5, bold=True)
    f.text(x1 + 8, Y + 160, T(lang, 'Added in the verification step', '我在验证步中实现'), size=12, color=MUTED, italic=True)
    rule_rows(f, lang, x, Y + 190, X + W - 14, 'conclude')


def gap_row(f, xs, y, levels, size=10):
    """Per-token training signal: a square per token whose depth shows the gap to the teacher (illustrative)."""
    for x, lv in zip(xs, levels):
        fill = [SLATE['pale'], SLATE['fill'], SLATE['tok'], SLATE['line']][lv]
        f.box(x - size / 2, y - size / 2, size, size, fill=fill, stroke=SLATE['line'], width=0.9, arc=2)


ANSWER = ['s'] * 5 + ['l'] + ['t'] * 3 + ['s'] * 4 + ['l'] + ['t'] * 2
LEVELS = [1, 2, 0, 1, 3, 2, 1, 0, 1, 2, 1, 3, 1, 2, 0, 1, 1]


def answer_row(f, x0, y, tok=10, pitch=13):
    xs = []
    for i, kind in enumerate(ANSWER):
        pal = {'s': SKY, 'l': LAV, 't': LEAF}[kind]
        cx = x0 + tok / 2 + i * pitch
        f.token(cx, y, pal, size=tok)
        xs.append(cx)
    return xs


def train_panel(f, lang, X, Y, W, H):
    f.panel(X, Y, W, H, SKY, T(lang, 'Token-Level Distillation', '逐 token 蒸馏'), 3)
    n = len(ANSWER)
    row_w = (n - 1) * 13 + 10
    x0 = X + (W - row_w) / 2
    xs = answer_row(f, x0, Y + 56)
    cx = X + W / 2
    f.text(cx, Y + 74, T(lang, 'The whole relayed answer', '整条接力回答'), size=12, color=MUTED, anchor='c')
    sw_ = label_w(T(lang, 'Teacher Scorer', '老师打分器'), 13.5, True) + 30
    f.edge([(cx, Y + 84), (cx, Y + 98)], end=5)
    f.cbox(cx, Y + 116, max(sw_, 170), 36, fill=LEAF['soft'], stroke=LEAF['line'],
           label=two_line(T(lang, 'Teacher Scorer', '老师打分器'), T(lang, 'Separate GPU', '单独一张卡'), 13, 11.5), size=13)
    f.edge([(cx, Y + 134), (cx, Y + 150)], end=5)
    gap_row(f, xs, Y + 162, LEVELS)
    f.text(cx, Y + 180, T(lang, 'Per-token reverse KL to the teacher', '每个 token 对老师的反向 KL'), size=12, color=MUTED, anchor='c')
    f.edge([(cx, Y + 190), (cx, Y + 204)], end=5)
    f.cbox(cx, Y + 220, 170, 30, fill=SKY['fill'], stroke=SKY['line'], label=f'<b>{T(lang, "Update the Student", "更新学生")}</b>', size=13)
    return xs


def relay_panel_m(f, lang, X, Y, W, H):
    """Merged panel: no panel number; one sentence for the limits; the free trigger check under the teacher."""
    f.panel(X, Y, W, H, SLATE, T(lang, 'Relay Rollout Inside vLLM Speculative Decoding', 'vLLM 投机解码中的接力生成'))
    r = relay_body(f, lang, X, Y, W)
    f.text(r['bx'], r['yt'] + 52, T(lang, 'Verifying a draft already gives the<br>teacher’s next-token distribution,<br>so checking for a takeover is free.',
                                   '验证草稿时已得到老师的下一 token<br>分布，判断是否接管不需额外计算。'),
           size=12, color=MUTED, lh=1.3)
    f.text(r['lx0'] + 8, Y + H - 20, T(lang, 'Each takeover writes up to 3 paragraphs (256 tokens), then hands back; the answer ends after the 2nd takeover.',
                                       '每次接管最多写 3 段（256 token）后交还；第 2 次接管写完，回答即结束。'), size=12, color=MUTED)
    return r


def relay_body(f, lang, X, Y, W):
    bw, bh = 178, 50
    bx = X + 18
    ys, yt = Y + 72, Y + 172
    stu = two_line(T(lang, 'Student', '学生'), T(lang, 'Qwen3-1.7B · Drafts', 'Qwen3-1.7B · 写草稿'))
    tea = two_line(T(lang, 'Teacher', '老师'), T(lang, 'Qwen3-4B · Verifies', 'Qwen3-4B · 验证'))
    f.box(bx, ys - bh / 2, bw, bh, fill=SKY['fill'], stroke=SKY['line'], label=stu, size=13.5)
    f.box(bx, yt - bh / 2, bw, bh, fill=LEAF['fill'], stroke=LEAF['line'], label=tea, size=13.5)
    xa, xb = bx + 52, bx + bw - 52
    f.edge([(xa, ys + bh / 2), (xa, yt - bh / 2)], width=1.2, end=5)
    f.edge([(xb, yt - bh / 2), (xb, ys + bh / 2)], width=1.2, end=5)
    f.text(xa - 7, (ys + yt) / 2, T(lang, 'Draft', '草稿'), size=12, color=MUTED, anchor='e')
    f.text(xb + 7, (ys + yt) / 2, T(lang, 'Accept or<br>Take Over', '接受或<br>接管'), size=12, color=MUTED, anchor='w')
    lx0, lx1 = bx + bw + 22, X + W - 18
    for y in (ys, yt):
        f.line([(lx0, y), (lx1, y)], color=SLATE['tok'], width=1, dashed=True, dash='2 3')
    segs, xend = lanes(f, lang, lx0 + 8, ys, yt, [('s', 12), ('t', 9), ('s', 10), ('t', 6)])
    end_x = xend - 13 + 5 + 3
    f.box(end_x - 5, yt - 5, 10, 10, fill=INK, stroke=INK, width=0.9, arc=2)
    s1, t1, s2, t2 = segs
    for k, (a, b) in enumerate(((s1[-1], t1[0]), (s2[-1], t2[0])), start=1):
        p0, p1 = (a + 2, ys + 6), (b - 2, yt - 6)
        f.edge([p0, p1], color=LAV['line'], width=1.6, end=5)
        f.badge((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, k, LAV, r=8.5, size=11)
    f.edge([(t1[-1] + 2, yt - 6), (s2[0] - 2, ys + 6)], color=SLATE['line'], width=1.3, end=5, dashed=True, dash='3 2')
    f.text((s1[0] + s1[-1]) / 2, ys - 19, '“… so the answer is 47.”', size=12.5, color=MUTED, anchor='c', italic=True)
    f.text((s2[0] + s2[-1]) / 2, ys - 19, '“… so the answer is 52.”', size=12.5, color=MUTED, anchor='c', italic=True)
    f.text((t1[0] + t1[-1]) / 2, yt + 20, '“Wait, let me check step 2 …”', size=12.5, color=LEAF['dark'], anchor='c', bold=True)
    f.text(t2[0] - 4, yt + 20, '“### Final Answer: 52”', size=12.5, color=LEAF['dark'], anchor='w', bold=True)
    return dict(ys=ys, yt=yt, s1=s1, t1=t1, s2=s2, t2=t2, end_x=end_x, bx=bx, bw=bw, lx0=lx0, lx1=lx1)


def rules_panel_m(f, lang, X, Y, W, H):
    """Rules with chip rows; the result sits in its own column; badges match the takeovers on the lanes."""
    f.panel(X, Y, W, H, LAV, T(lang, 'When Does the Teacher Take Over?', '老师何时接管？'))
    x = X + 20
    res_x = X + W - 96
    lab = [T(lang, 'Teacher’s top-1', '老师 top-1'), T(lang, 'Student’s top-5', '学生 top-5'), T(lang, 'Student’s top-1', '学生 top-1')]
    lab_w = max(label_w(t, 12.5) for t in lab) + 12
    for k, (title, yt) in enumerate(((T(lang, 'Reflection Trigger', '反思触发'), Y + 54), (T(lang, 'Concluding Trigger', '收尾触发'), Y + 156)), start=1):
        f.badge(x + 8, yt, k, LAV, r=8.5, size=11)
        x0, x1 = f.text(x + 22, yt, title, size=13.5, bold=True)
        if k == 2:
            f.text(x1 + 6, yt, T(lang, 'Added in the verification step', '我在验证步中实现'), size=12, color=MUTED, italic=True)
        ya, yb = yt + 30, yt + 60
        f.text(x, ya, lab[0], size=12.5, color=MUTED)
        f.text(x, yb, lab[1] if k == 1 else lab[2], size=12.5, color=MUTED)
        if k == 1:
            e = f.chip(x + lab_w, ya, 'Wait', LEAF, size=12.5, solid=True, bold=True, pad=6)
            f.text(e + 8, ya, T(lang, 'is one of 45 reflection words', '是 45 个反思词之一'), size=12.5)
            e = x + lab_w
            for w in ('So', 'Then', 'We', 'The', 'Let'):
                e = f.chip(e, yb, w, SKY, size=12.5, pad=6) + 4
            f.cross(e + 7, yb, s=7)
            f.text(e + 16, yb, T(lang, 'no reflection word', '没有反思词'), size=12.5)
        else:
            e = f.chip(x + lab_w, ya, '### Final Answer', LEAF, size=12.5, solid=True, bold=True, pad=6)
            f.text(e + 8, ya, T(lang, 'starts the final answer', '开始写最终答案'), size=12.5)
            e = f.chip(x + lab_w, yb, 'So', SKY, size=12.5, pad=6)
            f.text(e + 8, yb, T(lang, 'keeps reasoning', '还在往下推理'), size=12.5)
        ym = (ya + yb) / 2
        f.line([(res_x - 12, ya - 12), (res_x - 12, yb + 12)], color=LAV['tok'], width=1)
        f.edge([(res_x - 4, ym), (res_x + 14, ym)], color=LAV['line'], width=1.6, end=5)
        f.chip(res_x + 16, ym, T(lang, 'Take Over', '接管'), LAV, size=12.5, solid=True, bold=True, pad=6)
    f.line([(X + 14, Y + 132), (X + W - 14, Y + 132)], color=LAV['tok'], width=1, dashed=True, dash='3 3')


def train_panel_m(f, lang, X, Y, W, H):
    """Both models score the relayed answer; their per-token gap is the loss; the gradient goes back to the student."""
    f.panel(X, Y, W, H, SKY, T(lang, 'Token-Level Distillation', '逐 token 蒸馏'))
    n = len(ANSWER)
    row_w = (n - 1) * 13 + 10
    cx = X + W / 2
    x0 = cx - row_w / 2
    xs = answer_row(f, x0, Y + 54)
    f.text(cx, Y + 72, T(lang, 'The whole relayed answer', '整条接力回答'), size=12, color=MUTED, anchor='c')
    bw, gap = 122, 14
    lx, rx = cx - gap / 2 - bw, cx + gap / 2
    yb0, yb1 = Y + 94, Y + 134
    f.box(lx, yb0, bw, yb1 - yb0, fill=LEAF['soft'], stroke=LEAF['line'],
          label=two_line(T(lang, 'Teacher Scorer', '老师打分器'), T(lang, 'Separate GPU', '单独一张卡'), 13, 11.5), size=13)
    f.box(rx, yb0, bw, yb1 - yb0, fill=SKY['fill'], stroke=SKY['line'],
          label=two_line(T(lang, 'Student', '学生'), T(lang, 'Being trained', '正在训练'), 13, 11.5), size=13)
    for bxc in (lx + bw / 2, rx + bw / 2):
        f.edge([(bxc, Y + 80), (bxc, yb0)], end=5)
        f.edge([(bxc, yb1), (bxc, Y + 152)], end=5)
    gap_row(f, xs, Y + 162, LEVELS)
    f.text(cx, Y + 180, T(lang, 'Per-token reverse KL to the teacher', '每个 token 对老师的反向 KL'), size=12, color=MUTED, anchor='c')
    kr = xs[-1] + 9
    f.edge([(kr, Y + 162), (X + W - 14, Y + 162), (X + W - 14, (yb0 + yb1) / 2), (rx + bw, (yb0 + yb1) / 2)],
           color=SKY['line'], width=1.4, end=5)
    f.text(X + W - 22, Y + 146, T(lang, 'Gradient', '梯度'), size=12, color=SKY['dark'], anchor='e', italic=True)
    f.text(cx, Y + 206, T(lang, 'Same loss for every token, whoever wrote it', '无论谁写的 token，损失都相同'), size=12, color=MUTED, anchor='c')


# ------------------------------------------------------------------ round 2
def relay_body2(f, lang, X, Y, W):
    """As relay_body, but the tokens are spaced to fill the lanes, so the answer ends near the right edge."""
    bw, bh = 178, 50
    bx = X + 18
    ys, yt = Y + 72, Y + 172
    stu = two_line(T(lang, 'Student', '学生'), T(lang, 'Qwen3-1.7B · Drafts', 'Qwen3-1.7B · 写草稿'))
    tea = two_line(T(lang, 'Teacher', '老师'), T(lang, 'Qwen3-4B · Verifies', 'Qwen3-4B · 验证'))
    f.box(bx, ys - bh / 2, bw, bh, fill=SKY['fill'], stroke=SKY['line'], label=stu, size=13.5)
    f.box(bx, yt - bh / 2, bw, bh, fill=LEAF['fill'], stroke=LEAF['line'], label=tea, size=13.5)
    xa, xb = bx + 52, bx + bw - 52
    f.edge([(xa, ys + bh / 2), (xa, yt - bh / 2)], width=1.2, end=5)
    f.edge([(xb, yt - bh / 2), (xb, ys + bh / 2)], width=1.2, end=5)
    f.text(xa - 7, (ys + yt) / 2, T(lang, 'Draft', '草稿'), size=12, color=MUTED, anchor='e')
    f.text(xb + 7, (ys + yt) / 2, T(lang, 'Accept or<br>Take Over', '接受或<br>接管'), size=12, color=MUTED, anchor='w')
    lx0, lx1 = bx + bw + 22, X + W - 18
    for y in (ys, yt):
        f.line([(lx0, y), (lx1, y)], color=SLATE['tok'], width=1, dashed=True, dash='2 3')
    segs_spec = [('s', 12), ('t', 9), ('s', 10), ('t', 6)]
    n = sum(k for _, k in segs_spec)
    gap = 26
    tok = 10
    avail = (lx1 - 22) - (lx0 + 10)
    pitch = (avail - 3 * gap - tok) / (n)      # last pitch leads to the end mark
    x = lx0 + 10
    segs = []
    for lane, k in segs_spec:
        y = ys if lane == 's' else yt
        cs = []
        for i in range(k):
            pal = SKY if lane == 's' else (LAV if i == 0 else LEAF)
            f.token(x + tok / 2, y, pal, size=tok)
            cs.append(x + tok / 2)
            x += pitch
        segs.append(cs)
        x += gap - pitch + tok
    end_x = segs[-1][-1] + pitch
    f.box(end_x - 5, yt - 5, 10, 10, fill=INK, stroke=INK, width=0.9, arc=2)
    s1, t1, s2, t2 = segs
    for k, (a, b) in enumerate(((s1[-1], t1[0]), (s2[-1], t2[0])), start=1):
        p0, p1 = (a + 2, ys + 6), (b - 2, yt - 6)
        f.edge([p0, p1], color=LAV['line'], width=1.6, end=5)
        f.badge((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, k, LAV, r=8.5, size=11)
    f.edge([(t1[-1] + 2, yt - 6), (s2[0] - 2, ys + 6)], color=SLATE['line'], width=1.3, end=5, dashed=True, dash='3 2')
    f.text((s1[0] + s1[-1]) / 2, ys - 19, '“… so the answer is 47.”', size=12.5, color=MUTED, anchor='c', italic=True)
    f.text((s2[0] + s2[-1]) / 2, ys - 19, '“… so the answer is 52.”', size=12.5, color=MUTED, anchor='c', italic=True)
    f.text((t1[0] + t1[-1]) / 2, yt + 20, '“Wait, let me check step 2 …”', size=12.5, color=LEAF['dark'], anchor='c', bold=True)
    f.text((t2[0] + end_x) / 2, yt + 20, '“### Final Answer: 52”', size=12.5, color=LEAF['dark'], anchor='c', bold=True)
    return dict(ys=ys, yt=yt, s1=s1, t1=t1, s2=s2, t2=t2, end_x=end_x, bx=bx, bw=bw, lx0=lx0, lx1=lx1)


def relay_panel2(f, lang, X, Y, W, H, loop=False):
    f.panel(X, Y, W, H, SLATE, T(lang, 'Relay Rollout Inside vLLM Speculative Decoding', 'vLLM 投机解码中的接力生成'))
    r = relay_body2(f, lang, X, Y, W)
    f.text(r['bx'], r['yt'] + 52, T(lang, 'Verifying a draft already gives the<br>teacher’s next-token distribution,<br>so checking for a takeover is free.',
                                   '验证草稿时已得到老师的下一 token<br>分布，判断是否接管不需额外计算。'), size=12, color=MUTED, lh=1.3)
    f.text(r['lx0'] + 10, Y + H - 20, T(lang, 'Each takeover writes up to 3 paragraphs (256 tokens), then hands back; the answer ends after the 2nd takeover.',
                                        '每次接管最多写 3 段（256 token）后交还；第 2 次接管写完，回答即结束。'), size=12, color=MUTED)
    return r


def dist(f, x, y, words, pal, highlight=0, cross=False, wmax=64, size=12):
    """A tiny next-token distribution: one bar per word, longest first (illustrative probabilities)."""
    probs = [0.55, 0.18, 0.11, 0.07, 0.05][:len(words)]
    lw = max(label_w(w_, size) for w_ in words) + 6
    for i, (w_, pr) in enumerate(zip(words, probs)):
        yy = y + i * 15
        f.text(x + lw - 2, yy, w_, size=size, anchor='e', bold=(i == highlight and not cross))
        f.box(x + lw + 2, yy - 4.5, max(wmax * pr / probs[0], 3), 9, fill=pal['line'] if i == highlight and not cross else pal['tok'],
              stroke=pal['line'], width=0.9, arc=2)
    return x + lw + 2 + wmax


def rules_panel2(f, lang, X, Y, W, H, mode='chips'):
    if mode == 'chips':
        return rules_panel_m(f, lang, X, Y, W, H)
    f.panel(X, Y, W, H, LAV, T(lang, 'When Does the Teacher Take Over?', '老师何时接管？'))
    x = X + 20
    res_x = X + W - 96
    rows = [(T(lang, 'Reflection Trigger', '反思触发'), Y + 50, ['Wait', 'So', 'The'], ['So', 'Then', 'We', 'The', 'Let'],
             T(lang, 'top-1 is a reflection word', 'top-1 是反思词'), T(lang, 'no reflection word in top-5', 'top-5 里没有反思词')),
            (T(lang, 'Concluding Trigger', '收尾触发'), Y + 156, ['###', 'So', 'Thus'], ['So', 'Thus', 'We'],
             T(lang, 'top-1 starts the final answer', 'top-1 开始写最终答案'), T(lang, 'keeps reasoning', '还在往下推理'))]
    for k, (title, yt, tw, sw_, tnote, snote) in enumerate(rows, start=1):
        f.badge(x + 8, yt, k, LAV, r=8.5, size=11)
        x0, x1 = f.text(x + 22, yt, title, size=13.5, bold=True)
        if k == 2:
            f.text(x1 + 6, yt, T(lang, 'Added in the verification step', '我在验证步中实现'), size=12, color=MUTED, italic=True)
        f.text(x, yt + 24, T(lang, 'Teacher', '老师'), size=12, color=LEAF['dark'], bold=True)
        e = dist(f, x, yt + 42, tw, LEAF)
        f.text(x, yt + 42 + 15 * len(tw) + 6, tnote, size=11.5, color=MUTED)
        x2 = X + 230
        f.text(x2, yt + 24, T(lang, 'Student', '学生'), size=12, color=SKY['dark'], bold=True)
        dist(f, x2, yt + 42, sw_, SKY, highlight=-1, cross=True)
        f.text(x2, yt + 42 + 15 * len(sw_) + 6, snote, size=11.5, color=MUTED)
        ym = yt + 50
        f.edge([(res_x - 4, ym), (res_x + 14, ym)], color=LAV['line'], width=1.6, end=5)
        f.chip(res_x + 16, ym, T(lang, 'Take Over', '接管'), LAV, size=12.5, solid=True, bold=True, pad=6)


PAIRS = [(0.9, 0.7), (0.8, 0.8), (0.6, 0.3), (0.9, 0.85), (0.7, 0.4), (0.5, 0.2), (0.95, 0.6), (0.9, 0.8), (0.85, 0.7),
         (0.8, 0.75), (0.6, 0.45), (0.9, 0.9), (0.7, 0.35), (0.5, 0.25), (0.9, 0.6), (0.8, 0.7), (0.9, 0.85)]


def train_panel2(f, lang, X, Y, W, H, mode='squares'):
    if mode == 'squares':
        return train_panel_m(f, lang, X, Y, W, H)
    f.panel(X, Y, W, H, SKY, T(lang, 'Token-Level Distillation', '逐 token 蒸馏'))
    n = len(ANSWER)
    row_w = (n - 1) * 13 + 10
    cx = X + W / 2
    x0 = cx - row_w / 2
    xs = answer_row(f, x0, Y + 54)
    f.text(cx, Y + 72, T(lang, 'The whole relayed answer', '整条接力回答'), size=12, color=MUTED, anchor='c')
    bw, gap = 122, 14
    lx, rx = cx - gap / 2 - bw, cx + gap / 2
    yb0, yb1 = Y + 94, Y + 134
    f.box(lx, yb0, bw, yb1 - yb0, fill=LEAF['soft'], stroke=LEAF['line'],
          label=two_line(T(lang, 'Teacher Scorer', '老师打分器'), T(lang, 'Separate GPU', '单独一张卡'), 13, 11.5), size=13)
    f.box(rx, yb0, bw, yb1 - yb0, fill=SKY['fill'], stroke=SKY['line'],
          label=two_line(T(lang, 'Student', '学生'), T(lang, 'Being trained', '正在训练'), 13, 11.5), size=13)
    for bxc in (lx + bw / 2, rx + bw / 2):
        f.edge([(bxc, Y + 80), (bxc, yb0)], end=5)
        f.edge([(bxc, yb1), (bxc, Y + 146)], end=5)
    base = Y + 178
    for x, (pt, ps) in zip(xs, PAIRS):
        f.box(x - 4.5, base - 22 * pt, 4, 22 * pt, fill=LEAF['tok'], stroke=LEAF['line'], width=0.7, arc=1)
        f.box(x + 0.5, base - 22 * ps, 4, 22 * ps, fill=SKY['tok'], stroke=SKY['line'], width=0.7, arc=1)
    f.line([(xs[0] - 7, base), (xs[-1] + 7, base)], color=SLATE['line'], width=1)
    f.text(cx, base + 14, T(lang, 'Per-token reverse KL: teacher vs student', '逐 token 反向 KL：老师对学生'), size=12, color=MUTED, anchor='c')
    kr = xs[-1] + 9
    f.edge([(kr, base - 6), (X + W - 14, base - 6), (X + W - 14, (yb0 + yb1) / 2), (rx + bw, (yb0 + yb1) / 2)],
           color=SKY['line'], width=1.4, end=5)
    f.text(X + W - 20, Y + 147, T(lang, 'Gradient', '梯度'), size=12, color=SKY['dark'], anchor='e', italic=True)
    f.text(cx, Y + 218, T(lang, 'Same loss on every token, whoever wrote it', '无论谁写的 token，损失都相同'), size=12, color=MUTED, anchor='c')


def build(v, lang):
    if v[:2] in ('r4', 'r5', 'r6'):
        return build46(v)
    if v.startswith('r3'):
        return build3(v, lang)
    if v == 'r1i':
        return build_inno(v, lang)
    if v == 'r1a':
        f = Fig(WIDTH, 528, LABEL)
        legend(f, lang, 14, 14)
        relay_panel(f, lang, 6, 30, 868, 238)
        rules_panel(f, lang, 6, 280, 520, 242)
        train_panel(f, lang, 538, 280, 336, 242)
        return f
    if v == 'r1m':
        f = Fig(WIDTH, 556, LABEL)
        legend(f, lang, 14, 14)
        relay_panel_m(f, lang, 6, 30, 868, 266)
        rules_panel_m(f, lang, 6, 308, 548, 242)
        train_panel_m(f, lang, 566, 308, 308, 242)
        return f
    rules_mode, train_mode = {'r2a': ('chips', 'squares'), 'r2i': ('bars', 'pairs')}.get(v, ('chips', 'pairs'))
    f = Fig(WIDTH, 556, LABEL)
    legend(f, lang, 14, 14)
    r = relay_panel2(f, lang, 6, 30, 868, 266)
    rules_panel2(f, lang, 6, 308, 548, 242, rules_mode)
    train_panel2(f, lang, 566, 308, 308, 242, train_mode)
    return f


def build_inno(v, lang):
    """Round-1 innovative: the trigger checks sit at the two takeover points; training is one left-to-right flow."""
    f = Fig(WIDTH, 512, LABEL)
    legend(f, lang, 14, 14)
    r = relay_panel(f, lang, 6, 30, 868, 318, callouts=True)
    # callout cards under the two takeover points
    cy0 = r['yt'] + 44
    for k, (seg, kind) in enumerate(((r['t1'], 'reflect'), (r['t2'], 'conclude')), start=1):
        if kind == 'reflect':
            title = T(lang, 'Reflection Trigger', '反思触发')
            body = T(lang, 'Teacher’s top-1 <b>Wait</b> is a reflection word;<br>none of the student’s top-5 is',
                     '老师 top-1 <b>Wait</b> 是反思词，<br>学生 top-5 里没有反思词')
        else:
            title = T(lang, 'Concluding Trigger', '收尾触发')
            body = T(lang, 'Teacher starts <b>### Final Answer</b>;<br>the student keeps reasoning',
                     '老师要开始写 <b>### Final Answer</b>，<br>学生还在往下推理')
        w = max(label_w(body, 12.5), label_w(title, 13, True)) + 26
        cx = (seg[0] + seg[-1]) / 2 if k == 1 else min((seg[0] + seg[-1]) / 2, 874 - 14 - w / 2)
        x = cx - w / 2
        f.box(x, cy0, w, 66, fill=WHITE, stroke=LAV['line'], width=1.2, arc=8)
        f.badge(x + 16, cy0 + 16, k, LAV, r=8.5, size=11)
        f.text(x + 30, cy0 + 16, title, size=13, bold=True)
        f.text(x + 12, cy0 + 44, body, size=12.5, anchor='w')
        f.line([(seg[0], r['yt'] + 32), (seg[0], cy0)], color=LAV['line'], width=1.1, dashed=True, dash='2 2')
    f.text(18 + 14, 30 + 318 - 18, T(lang, 'Each takeover writes up to 3 paragraphs (256 tokens) and hands back; at most 2 takeovers, the answer ends after the second.',
                                     '每次接管最多写 3 段（256 token）后交还；最多接管 2 次，第 2 次写完回答即结束。'), size=12, color=MUTED)
    # training flow
    Y = 360
    f.panel(6, Y, 868, 146, SKY, T(lang, 'Token-Level Distillation on the Whole Relayed Answer', '对整条接力回答逐 token 蒸馏'), 2)
    xs = answer_row(f, 30, Y + 78)
    f.text(30, Y + 100, T(lang, 'Relayed answer', '接力回答'), size=12, color=MUTED)
    x = xs[-1] + 22
    f.edge([(x, Y + 78), (x + 30, Y + 78)], end=5)
    sw_ = 156
    f.box(x + 32, Y + 56, sw_, 44, fill=LEAF['soft'], stroke=LEAF['line'],
          label=two_line(T(lang, 'Teacher Scorer', '老师打分器'), T(lang, 'Separate GPU', '单独一张卡'), 13, 11.5), size=13)
    x2 = x + 32 + sw_
    f.edge([(x2, Y + 78), (x2 + 30, Y + 78)], end=5)
    gx = [x2 + 40 + i * 13 for i in range(len(ANSWER))]
    gap_row(f, gx, Y + 78, LEVELS)
    f.text((gx[0] + gx[-1]) / 2, Y + 100, T(lang, 'Per-token reverse KL', '逐 token 反向 KL'), size=12, color=MUTED, anchor='c')
    x3 = gx[-1] + 18
    f.edge([(x3, Y + 78), (x3 + 28, Y + 78)], end=5)
    f.box(x3 + 30, Y + 60, 860 - (x3 + 30), 36, fill=SKY['fill'], stroke=SKY['line'],
          label=f'<b>{T(lang, "Update the Student", "更新学生")}</b>', size=13)
    f.text(30, Y + 126, T(lang, 'Every token gets the same loss, whoever wrote it; the updated student drafts the next rollouts.',
                          '无论谁写的 token，损失都相同；更新后的学生写下一批 rollout 的草稿。'), size=12, color=MUTED)
    return f


# ------------------------------------------------------------------ round 3
FINAL = ['###', None, 'Final Answer']          # the concluding header, with its check-box glyph drawn


def relay_body3(f, lang, X, Y, W, blocks=False):
    """Round 3: as relay_body2, the takeovers named by their trigger (the panel numbers follow the caption, so the
    lanes no longer carry numbered badges), the concluding quote with its check-box glyph; with blocks, the student's
    tokens come in draft blocks and each accepted block gets a small check."""
    bw, bh = 178, 50
    bx = X + 18
    ys, yt = Y + 72, Y + 172
    stu = two_line(T(lang, 'Student', '学生'), T(lang, 'Qwen3-1.7B · Drafts', 'Qwen3-1.7B · 写草稿'))
    tea = two_line(T(lang, 'Teacher', '老师'), T(lang, 'Qwen3-4B · Verifies', 'Qwen3-4B · 验证'))
    f.box(bx, ys - bh / 2, bw, bh, fill=SKY['fill'], stroke=SKY['line'], label=stu, size=13.5)
    f.box(bx, yt - bh / 2, bw, bh, fill=LEAF['fill'], stroke=LEAF['line'], label=tea, size=13.5)
    xa, xb = bx + 52, bx + bw - 52
    f.edge([(xa, ys + bh / 2), (xa, yt - bh / 2)], width=1.2, end=5)
    f.edge([(xb, yt - bh / 2), (xb, ys + bh / 2)], width=1.2, end=5)
    f.text(xa - 7, (ys + yt) / 2, T(lang, 'Draft', '草稿'), size=12, color=MUTED, anchor='e')
    f.text(xb + 7, (ys + yt) / 2, T(lang, 'Accept or<br>Take Over', '接受或<br>接管'), size=12, color=MUTED, anchor='w')
    lx0, lx1 = bx + bw + 22, X + W - 18
    for y in (ys, yt):
        f.line([(lx0, y), (lx1, y)], color=SLATE['tok'], width=1, dashed=True, dash='2 3')
    segs_spec = [('s', 12), ('t', 9), ('s', 10), ('t', 6)]
    n = sum(k for _, k in segs_spec)
    gap, tok, bgap = 26, 10, (6 if blocks else 0)
    avail = (lx1 - 22) - (lx0 + 10)
    pitch = (avail - 3 * gap - tok - 4 * bgap) / n
    x = lx0 + 10
    segs, block_spans = [], []
    for lane, k in segs_spec:
        y = ys if lane == 's' else yt
        cs = []
        for i in range(k):
            pal = SKY if lane == 's' else (LAV if i == 0 else LEAF)
            f.token(x + tok / 2, y, pal, size=tok)
            cs.append(x + tok / 2)
            x += pitch
            if lane == 's' and blocks and (i + 1) % 4 == 0 and i + 1 < k:
                x += bgap
        segs.append(cs)
        x += gap - pitch + tok
    end_x = segs[-1][-1] + pitch
    f.box(end_x - 5, yt - 5, 10, 10, fill=INK, stroke=INK, width=0.9, arc=2)
    s1, t1, s2, t2 = segs
    names = (T(lang, 'Reflection', '反思'), T(lang, 'Concluding', '收尾'))
    for (a, b), name in zip(((s1[-1], t1[0]), (s2[-1], t2[0])), names):
        p0, p1 = (a + 2, ys + 6), (b - 2, yt - 6)
        f.edge([p0, p1], color=LAV['line'], width=1.6, end=5)
        f.text((p0[0] + p1[0]) / 2 - 9, (p0[1] + p1[1]) / 2, name, size=12, color=LAV['dark'], anchor='e', bold=True)
    f.edge([(t1[-1] + 2, yt - 6), (s2[0] - 2, ys + 6)], color=SLATE['line'], width=1.3, end=5, dashed=True, dash='3 2')
    if blocks:
        for seg, accepted in ((s1, 2), (s2, 2)):
            for b in range(accepted):
                c = (seg[4 * b] + seg[4 * b + 3]) / 2
                f.check(c, ys + 15, s=6, color=LEAF['line'], width=1.6)
    f.text((s1[0] + s1[-1]) / 2, ys - 19, '“… so the answer is 47.”', size=12.5, color=MUTED, anchor='c', italic=True)
    f.text((s2[0] + s2[-1]) / 2, ys - 19, '“… so the answer is 52.”', size=12.5, color=MUTED, anchor='c', italic=True)
    f.text((t1[0] + t1[-1]) / 2, yt + 20, '“Wait, let me check step 2 …”', size=12.5, color=LEAF['dark'], anchor='c', bold=True)
    f.text_icon((t2[0] + end_x) / 2, yt + 20, ['“###', None, 'Final Answer: 52”'], size=12.5, color=LEAF['dark'],
                bold=True, anchor='c')
    return dict(ys=ys, yt=yt, bx=bx, bw=bw, lx0=lx0)


def relay_panel3(f, lang, X, Y, W, H, blocks=False):
    f.panel(X, Y, W, H, SLATE, T(lang, 'Relay Rollout Inside vLLM Speculative Decoding', 'vLLM 投机解码中的接力生成'), num=1)
    r = relay_body3(f, lang, X, Y, W, blocks)
    f.text(r['bx'], r['yt'] + 52, T(lang, 'Verifying a draft already gives the<br>teacher’s next-token distribution,<br>so checking for a takeover is free.',
                                   '验证草稿时已得到老师的下一 token<br>分布，判断是否接管不需额外计算。'), size=12, color=MUTED, lh=1.3)
    # the run-in note shares the last line of the note on the left (3 lines of 15.6 px centred on yt + 52)
    last = r['yt'] + 52 + (15.6 if lang == 'en' else 7.8)
    f.text(r['lx0'] + 10, last, T(lang, 'Each takeover writes up to 3 paragraphs (256 tokens), then hands back; the answer ends after the 2nd takeover.',
                                        '每次接管最多写 3 段（256 token）后交还；第 2 次接管写完，回答即结束。'), size=12, color=MUTED)


def final_chip(f, x, cy, size=12.5, h=20, pad=6):
    w = icon_line_w(FINAL, size, True) + 2 * pad - 4
    f.box(x, cy - h / 2, w, h, fill=LEAF['tok'], stroke=LEAF['line'], width=1, arc=5)
    f.text_icon(x + pad - 2, cy, FINAL, size=size, bold=True)
    return x + w


def rules_panel3(f, lang, X, Y, W, H):
    """Round 3: rule titles marked with the takeover token; wording as on the page (the teacher's reflection word is not
    in the student's top-5; the student keeps going); the concluding header with its check-box glyph."""
    f.panel(X, Y, W, H, LAV, T(lang, 'When Does the Teacher Take Over?', '老师何时接管？'), num=2)
    x = X + 20
    res_x = X + W - 96
    lab = [T(lang, 'Teacher’s top-1', '老师 top-1'), T(lang, 'Student’s top-5', '学生 top-5'), T(lang, 'Student’s top-1', '学生 top-1')]
    lab_w = max(label_w(t, 12.5) for t in lab) + 12
    rows = ((T(lang, 'Reflection Trigger', '反思触发'), Y + 54), (T(lang, 'Concluding Trigger', '收尾触发'), Y + 156))
    for k, (title, yt) in enumerate(rows, start=1):
        f.token(x + 5, yt, LAV, size=10)
        x0, x1 = f.text(x + 16, yt, title, size=13.5, bold=True)
        if k == 2:
            f.text(x1 + 6, yt, T(lang, 'Implemented in the verification step', '我在验证步中实现'), size=12, color=MUTED, italic=True)
        ya, yb = yt + 30, yt + 60
        f.text(x, ya, lab[0], size=12.5, color=MUTED)
        f.text(x, yb, lab[1] if k == 1 else lab[2], size=12.5, color=MUTED)
        if k == 1:
            e = f.chip(x + lab_w, ya, 'Wait', LEAF, size=12.5, solid=True, bold=True, pad=6)
            f.text(e + 8, ya, T(lang, 'is one of 45 reflection words', '是 45 个反思词之一'), size=12.5)
            e = x + lab_w
            for w_ in ('So', 'Then', 'We', 'The', 'Let'):
                e = f.chip(e, yb, w_, SKY, size=12.5, pad=6) + 4
            f.cross(e + 7, yb, s=7)
            f.text(e + 16, yb, T(lang, 'no Wait', '没有 Wait'), size=12.5)
        else:
            e = final_chip(f, x + lab_w, ya)
            f.text(e + 8, ya, T(lang, 'starts the final answer', '开始写最终答案'), size=12.5)
            e = f.chip(x + lab_w, yb, 'So', SKY, size=12.5, pad=6)
            f.text(e + 8, yb, T(lang, 'keeps going', '还在往下写'), size=12.5)
        ym = (ya + yb) / 2
        f.line([(res_x - 12, ya - 12), (res_x - 12, yb + 12)], color=LAV['tok'], width=1)
        f.edge([(res_x - 4, ym), (res_x + 14, ym)], color=LAV['line'], width=1.6, end=5)
        f.chip(res_x + 16, ym, T(lang, 'Take Over', '接管'), LAV, size=12.5, solid=True, bold=True, pad=6)
    f.line([(X + 14, Y + 132), (X + W - 14, Y + 132)], color=LAV['tok'], width=1, dashed=True, dash='3 3')


def train_panel3(f, lang, X, Y, W, H):
    """Round 3: the paired-bar training panel of round 2, numbered."""
    f.panel(X, Y, W, H, SKY, T(lang, 'Token-Level Distillation', '逐 token 蒸馏'), num=3)
    n = len(ANSWER)
    row_w = (n - 1) * 13 + 10
    cx = X + W / 2
    x0 = cx - row_w / 2
    xs = answer_row(f, x0, Y + 54)
    f.text(cx, Y + 72, T(lang, 'The whole relayed answer', '整条接力回答'), size=12, color=MUTED, anchor='c')
    bw, gap = 122, 14
    lx, rx = cx - gap / 2 - bw, cx + gap / 2
    yb0, yb1 = Y + 94, Y + 134
    f.box(lx, yb0, bw, yb1 - yb0, fill=LEAF['soft'], stroke=LEAF['line'],
          label=two_line(T(lang, 'Teacher Scorer', '老师打分器'), T(lang, 'Separate GPU', '单独一张卡'), 13, 11.5), size=13)
    f.box(rx, yb0, bw, yb1 - yb0, fill=SKY['fill'], stroke=SKY['line'],
          label=two_line(T(lang, 'Student', '学生'), T(lang, 'Being trained', '正在训练'), 13, 11.5), size=13)
    for bxc in (lx + bw / 2, rx + bw / 2):
        f.edge([(bxc, Y + 80), (bxc, yb0)], end=5)
        f.edge([(bxc, yb1), (bxc, Y + 146)], end=5)
    base = Y + 178
    for x, (pt, ps) in zip(xs, PAIRS):
        f.box(x - 4.5, base - 22 * pt, 4, 22 * pt, fill=LEAF['tok'], stroke=LEAF['line'], width=0.7, arc=1)
        f.box(x + 0.5, base - 22 * ps, 4, 22 * ps, fill=SKY['tok'], stroke=SKY['line'], width=0.7, arc=1)
    f.line([(xs[0] - 7, base), (xs[-1] + 7, base)], color=SLATE['line'], width=1)
    f.text(cx, base + 14, T(lang, 'Per-token reverse KL: teacher vs student', '逐 token 反向 KL：老师对学生'), size=12, color=MUTED, anchor='c')
    kr = xs[-1] + 9
    f.edge([(kr, base - 6), (X + W - 14, base - 6), (X + W - 14, (yb0 + yb1) / 2), (rx + bw, (yb0 + yb1) / 2)],
           color=SKY['line'], width=1.4, end=5)
    f.text(X + W - 20, Y + 147, T(lang, 'Gradient', '梯度'), size=12, color=SKY['dark'], anchor='e', italic=True)
    f.text(cx, Y + 218, T(lang, 'Same loss on every token, whoever wrote it', '无论谁写的 token，损失都相同'), size=12, color=MUTED, anchor='c')


def build3(v, lang):
    f = Fig(WIDTH, 556, LABEL)
    legend(f, lang, 14, 14)
    relay_panel3(f, lang, 6, 30, 868, 266, blocks=(v in ('r3i', 'r3m')))
    rules_panel3(f, lang, 6, 308, 548, 242)
    train_panel3(f, lang, 566, 308, 308, 242)
    return f


# ------------------------------------------------------------------ rounds 4-6: English only, 720 px wide
# The project pages show figures 724 px wide on a desktop, so the frameworks are now drawn at 720 px: one unit is one
# pixel on the page (at 880 px every label was shown at 0.82 of its size). Fewer tokens, so they keep visible gaps.
W4 = 720
BX, BW = 20, 136                     # left column: the actors (models, triggers)
LX0, LX1 = 176, 700                  # right column: the token positions, shared by panels 1 and 3
SEGS4 = [('s', 8), ('t', 6), ('s', 10), ('t', 4)]
TOK = 10
LE = '<span style="font-family:Times New Roman;">≤</span>'      # the hand font's ≤ is tiny


def layout4(x0=LX0 + 8, x1=LX1 - 4, spec=SEGS4, gap=22, bgap=5, block=4):
    """Token centres per segment and the end mark's centre: student segments come in draft blocks of four with a small
    gap between blocks; the end mark follows the last token at one pitch."""
    n = sum(k for _, k in spec)
    nb = sum((k - 1) // block for lane, k in spec if lane == 's')
    pitch = (x1 - x0 - TOK - (len(spec) - 1) * (gap + TOK) - nb * bgap) / (n - len(spec) + 1)
    x = x0 + TOK / 2
    segs = []
    for j, (lane, k) in enumerate(spec):
        cs = []
        for i in range(k):
            cs.append(x)
            if i < k - 1:
                x += pitch + (bgap if lane == 's' and (i + 1) % block == 0 else 0)
        segs.append(cs)
        x += TOK + gap
    return segs, segs[-1][-1] + pitch, pitch


def lane_tokens4(f, segs, ys, yt, spec=SEGS4):
    for (lane, _), cs in zip(spec, segs):
        y = ys if lane == 's' else yt
        for i, cx in enumerate(cs):
            pal = SKY if lane == 's' else (LAV if i == 0 else LEAF)
            f.token(cx, y, pal, size=TOK)


def relay4(f, X, Y, W, ys, yt, hand_label=False, block_checks=True, ghosts=False, cross_inside=False):
    """Panel 1 body on the 720 grid: models as lane labels on the left, the relayed answer on two lanes."""
    bh = 46
    stu = two_line('Student', 'Qwen3-1.7B · Drafts', 13.5, 12)
    tea = two_line('Teacher', 'Qwen3-4B · Verifies', 13.5, 12)
    f.box(BX, ys - bh / 2, BW, bh, fill=SKY['fill'], stroke=SKY['line'], label=stu, size=13.5)
    f.box(BX, yt - bh / 2, BW, bh, fill=LEAF['fill'], stroke=LEAF['line'], label=tea, size=13.5)
    xa, xb = BX + 42, BX + 70
    f.edge([(xa, ys + bh / 2), (xa, yt - bh / 2)], width=1.2, end=5)
    f.edge([(xb, yt - bh / 2), (xb, ys + bh / 2)], width=1.2, end=5)
    f.text(xa - 6, (ys + yt) / 2, 'Draft', size=12, color=MUTED, anchor='e')
    f.text(xb + 6, (ys + yt) / 2, 'Accept or<br>Take Over', size=12, color=MUTED, anchor='w')
    for y in (ys, yt):
        f.line([(LX0, y), (LX1, y)], color=SLATE['tok'], width=1, dashed=True, dash='2 3')
    segs, end_x, pitch = layout4()
    lane_tokens4(f, segs, ys, yt)
    f.box(end_x - TOK / 2, yt - TOK / 2, TOK, TOK, fill=INK, stroke=INK, width=0.9, arc=2)
    s1, t1, s2, t2 = segs
    if block_checks:
        for seg in (s1, s2):
            for b in range(0, len(seg), 4):
                blk = seg[b:b + 4]
                f.check((blk[0] + blk[-1]) / 2, ys + 15, s=6, color=LEAF['line'], width=1.6)
    for (a, b), name in zip(((s1[-1], t1[0]), (s2[-1], t2[0])), ('Reflection', 'Concluding')):
        if ghosts:
            # the student's draft token at the takeover position, rejected: the teacher writes there instead
            gx = a + pitch
            f.box(gx - TOK / 2, ys - TOK / 2, TOK, TOK, fill=WHITE, stroke=SKY['line'], width=1, arc=2, dashed=True)
            if cross_inside:
                f.cross(gx, ys, s=5, color=ROSE['line'], width=1.4)
            else:
                f.cross(gx, ys + 15, s=5.5, color=ROSE['line'], width=1.6)
            a = gx - 2
        p0, p1 = (a + 2, ys + 6), (b - 2, yt - 6)
        f.edge([p0, p1], color=LAV['line'], width=1.6, end=5)
        f.text((p0[0] + p1[0]) / 2 - 8, (p0[1] + p1[1]) / 2, name, size=12.5, color=LAV['dark'], anchor='e', bold=True)
    q0, q1 = (t1[-1] + 2, yt - 6), (s2[0] - 2, ys + 6)
    f.edge([q0, q1], color=SLATE['line'], width=1.3, end=5, dashed=True, dash='3 2')
    if hand_label:
        f.text((q0[0] + q1[0]) / 2 + 8, (q0[1] + q1[1]) / 2, '<b>Hand Back</b><br>' + LE + ' 256 tokens', size=12,
               color=SLATE['dark'], anchor='w', lh=1.3)
    f.text((s1[0] + s1[-1]) / 2, ys - 19, '“… so the answer is 47.”', size=12.5, color=MUTED, anchor='c', italic=True)
    f.text((s2[0] + s2[-1]) / 2, ys - 19, '“… so the answer is 52.”', size=12.5, color=MUTED, anchor='c', italic=True)
    f.text((t1[0] + t1[-1]) / 2, yt + 20, '“Wait, let me check step 2 …”', size=12.5, color=LEAF['dark'], anchor='c', bold=True)
    fw = icon_line_w(['“###', None, 'Final Answer: 52”'], 12.5, True)
    f.text_icon(min((t2[0] + end_x) / 2, LX1 - fw / 2), yt + 20, ['“###', None, 'Final Answer: 52”'], size=12.5,
                color=LEAF['dark'], bold=True, anchor='c')
    return dict(segs=segs, end_x=end_x, pitch=pitch)


def legend4(f, y=14):
    legend(f, 'en', BX - 4, y)


def brace(f, x, y0, y1, color, w=7, width=1.2):
    """A right-facing curly brace from y0 to y1 at x, its tip at x + w."""
    ym = (y0 + y1) / 2
    f.edge([(x, y0), (x + w * 0.5, y0 + 4), (x + w * 0.5, ym - 4), (x + w, ym), (x + w * 0.5, ym + 4),
            (x + w * 0.5, y1 - 4), (x, y1)], color=color, width=width, arrow=False, curved=True)
    return x + w


def rules4a(f, X, Y, W, H):
    """Round-4 aesthetic: the round-3 rule rows on the full width; a brace groups each pair of conditions."""
    f.panel(X, Y, W, H, LAV, 'When Does the Teacher Take Over?', num=2)
    x = BX
    lab_w = max(label_w(t, 12.5) for t in ('Teacher’s top-1', 'Student’s top-5', 'Student’s top-1')) + 14
    res_x = X + W - 14 - 84
    rows = (('Reflection Trigger', Y + 54), ('Concluding Trigger', Y + 148))
    for k, (title, yt) in enumerate(rows, start=1):
        f.token(x + 5, yt, LAV, size=10)
        x0, x1 = f.text(x + 16, yt, title, size=13.5, bold=True)
        if k == 2:
            f.text(x1 + 8, yt, 'Implemented in the verification step', size=12, color=MUTED, italic=True)
        ya, yb = yt + 28, yt + 56
        f.text(x, ya, 'Teacher’s top-1', size=12.5, color=MUTED)
        f.text(x, yb, 'Student’s top-5' if k == 1 else 'Student’s top-1', size=12.5, color=MUTED)
        if k == 1:
            e = f.chip(x + lab_w, ya, 'Wait', LEAF, size=12.5, solid=True, bold=True, pad=6)
            e = f.text(e + 8, ya, 'is one of 45 reflection words', size=12.5)[1]
            right = e
            e = x + lab_w
            for w_ in ('So', 'Then', 'We', 'The', 'Let'):
                e = f.chip(e, yb, w_, SKY, size=12.5, pad=6) + 4
            f.cross(e + 7, yb, s=7)
            right = max(right, f.text(e + 16, yb, 'no Wait', size=12.5)[1])
        else:
            e = final_chip(f, x + lab_w, ya)
            right = f.text(e + 8, ya, 'starts the final answer', size=12.5)[1]
            e = f.chip(x + lab_w, yb, 'So', SKY, size=12.5, pad=6)
            right = max(right, f.text(e + 8, yb, 'keeps going', size=12.5)[1])
        tip = brace(f, res_x - 46, ya - 11, yb + 11, LAV['line'])
        ym = (ya + yb) / 2
        f.edge([(tip + 2, ym), (res_x - 2, ym)], color=LAV['line'], width=1.6, end=5)
        f.chip(res_x, ym, 'Take Over', LAV, size=12.5, solid=True, bold=True, pad=8)
    f.line([(X + 14, Y + 124), (X + W - 14, Y + 124)], color=LAV['tok'], width=1, dashed=True, dash='3 3')


def train4a(f, X, Y, W, H):
    """Round-4 aesthetic: the round-3 training panel, centred in a full-width panel."""
    f.panel(X, Y, W, H, SKY, 'Token-Level Distillation', num=3)
    n = len(ANSWER)
    pitch = 16
    row_w = (n - 1) * pitch + TOK
    cx = X + W / 2
    x0 = cx - row_w / 2
    xs = answer_row(f, x0, Y + 52, pitch=pitch)
    f.text(cx, Y + 70, 'The whole relayed answer', size=12.5, color=MUTED, anchor='c')
    bw, gap = 150, 20
    lx, rx = cx - gap / 2 - bw, cx + gap / 2
    yb0, yb1 = Y + 92, Y + 134
    f.box(lx, yb0, bw, yb1 - yb0, fill=LEAF['soft'], stroke=LEAF['line'],
          label=two_line('Teacher Scorer', 'Separate GPU', 13.5, 12), size=13.5)
    f.box(rx, yb0, bw, yb1 - yb0, fill=SKY['fill'], stroke=SKY['line'], label=two_line('Student', 'Being trained', 13.5, 12),
          size=13.5)
    for bxc in (lx + bw / 2, rx + bw / 2):
        f.edge([(bxc, Y + 79), (bxc, yb0)], end=5)
        f.edge([(bxc, yb1), (bxc, Y + 150)], end=5)
    base = Y + 184
    for x, (pt, ps) in zip(xs, PAIRS):
        f.box(x - 5, base - 26 * pt, 4.5, 26 * pt, fill=LEAF['tok'], stroke=LEAF['line'], width=0.7, arc=1)
        f.box(x + 0.5, base - 26 * ps, 4.5, 26 * ps, fill=SKY['tok'], stroke=SKY['line'], width=0.7, arc=1)
    f.line([(xs[0] - 8, base), (xs[-1] + 8, base)], color=SLATE['line'], width=1)
    f.text(cx, base + 15, 'Per-token reverse KL: teacher vs student', size=12.5, color=MUTED, anchor='c')
    kr = xs[-1] + 10
    gx = rx + bw + 30
    f.edge([(kr, base - 6), (gx, base - 6), (gx, (yb0 + yb1) / 2), (rx + bw + 1, (yb0 + yb1) / 2)], color=SKY['line'], width=1.4, end=5)
    f.text(gx + 6, (yb1 + base) / 2 - 4, 'Gradient', size=12.5, color=SKY['dark'], anchor='w', italic=True)
    f.text(cx, Y + H - 16, 'Same loss on every token, whoever wrote it', size=12.5, color=MUTED, anchor='c')


def build4a():
    f = Fig(W4, 796, LABEL)
    legend4(f)
    Y1, ys = 32, 32 + 74
    yt = ys + 92
    H1 = 254
    f.panel(6, Y1, 708, H1, SLATE, 'Relay Rollout Inside vLLM Speculative Decoding', num=1)
    relay4(f, 6, Y1, 708, ys, yt)
    f.text(BX, yt + 50, 'Verifying a draft already gives the teacher’s next-token distribution, so checking for a takeover is free.',
           size=12, color=MUTED)
    f.text(BX, yt + 68, 'Each takeover writes up to 3 paragraphs (256 tokens), then hands back; the answer ends after the 2nd takeover.',
           size=12, color=MUTED)
    Y2 = Y1 + H1 + 12
    rules4a(f, 6, Y2, 708, 232)
    Y3 = Y2 + 232 + 12
    train4a(f, 6, Y3, 708, 796 - 6 - Y3)
    return f


def rules4i(f, X, Y, W, H, footer=True):
    """Round-4 innovative: the two triggers as side-by-side cards, each with its two conditions and its result; a
    footnote says both are checked in the verification step."""
    f.panel(X, Y, W, H, LAV, 'When Does the Teacher Take Over?', num=2)
    gap = 12
    cw = (W - 28 - gap) / 2
    cy0, ch = Y + 40, 124
    lab_w = max(label_w(t, 12.5) for t in ('Teacher’s top-1', 'Student’s top-5')) + 10
    for k in range(2):
        x = X + 14 + k * (cw + gap)
        f.box(x, cy0, cw, ch, fill=WHITE, stroke=LAV['tok'], width=1.1, arc=8)
        f.token(x + 19, cy0 + 20, LAV, size=10)
        f.text(x + 30, cy0 + 20, ('Reflection Trigger', 'Concluding Trigger')[k], size=13.5, bold=True)
        xl = x + 14
        ya, yb = cy0 + 50, cy0 + 78
        f.text(xl, ya, 'Teacher’s top-1', size=12.5, color=MUTED)
        f.text(xl, yb, ('Student’s top-5', 'Student’s top-1')[k], size=12.5, color=MUTED)
        if k == 0:
            e = f.chip(xl + lab_w, ya, 'Wait', LEAF, size=12.5, solid=True, bold=True, pad=6)
            f.text(e + 7, ya, 'one of 45 reflection words', size=12.5)
            e = xl + lab_w
            for w_ in ('So', 'Then', 'We', 'The', 'Let'):
                e = f.chip(e, yb, w_, SKY, size=12.5, pad=6) + 4
            f.cross(e + 6, yb, s=7)
        else:
            final_chip(f, xl + lab_w, ya)
            e = f.chip(xl + lab_w, yb, 'So', SKY, size=12.5, pad=6)
            f.text(e + 7, yb, 'keeps going', size=12.5)
            f.text(xl, cy0 + ch - 18, 'Implemented in the verification step', size=12, color=MUTED, italic=True)
        tw = label_w('Take Over', 12.5, True) + 16
        tx = x + cw - 14 - tw
        f.edge([(tx - 22, cy0 + ch - 18), (tx - 2, cy0 + ch - 18)], color=LAV['line'], width=1.6, end=5)
        f.chip(tx, cy0 + ch - 18, 'Take Over', LAV, size=12.5, solid=True, bold=True, pad=8)
    if footer:
        f.text(BX, Y + H - 17, 'Both are checked while the teacher verifies the draft: no extra forward pass.', size=12, color=MUTED)


# illustrative probabilities of each token of the relayed answer (teacher, student), in SEGS4 order: the student's own
# tokens are likely under the student; its wrong "47" is unlikely under the teacher; the takeover tokens ("Wait",
# "###") are unlikely under the student, so they carry the largest loss
PROBS4 = ([(0.8, 0.85), (0.85, 0.9), (0.55, 0.8), (0.9, 0.9), (0.6, 0.75), (0.7, 0.85), (0.5, 0.9), (0.2, 0.7)] +
          [(0.85, 0.04), (0.9, 0.5), (0.8, 0.6), (0.9, 0.55), (0.85, 0.7), (0.9, 0.65)] +
          [(0.75, 0.8), (0.8, 0.85), (0.85, 0.9), (0.6, 0.75), (0.8, 0.85), (0.7, 0.8), (0.85, 0.9), (0.8, 0.85), (0.75, 0.8), (0.85, 0.9)] +
          [(0.8, 0.1), (0.9, 0.6), (0.95, 0.7), (0.9, 0.75)])


def train4i(f, X, Y, W, H):
    """Round-4 innovative: a matrix on the panel-1 grid. Rows: the relayed answer (tokens at the same x as in panel 1),
    the teacher scorer's and the student's probability of each token, and the per-token reverse KL; the models sit in
    the left column next to their rows, and the gradient goes from the KL row up into the student."""
    import math
    f.panel(X, Y, W, H, SKY, 'Token-Level Distillation', num=3)
    segs, end_x, pitch = layout4()
    xs = [c for s in segs for c in s]
    yA = Y + 54
    yB, yC = yA + 40, yA + 86
    yD = yC + 46
    f.text(BX, yA, 'Relayed Answer', size=12.5, color=MUTED, bold=True)
    for (lane, _), cs in zip(SEGS4, segs):
        for i, cx in enumerate(cs):
            f.token(cx, yA, SKY if lane == 's' else (LAV if i == 0 else LEAF), size=TOK)
    bh = 38
    f.box(BX, yB - bh / 2, BW, bh, fill=LEAF['soft'], stroke=LEAF['line'], label=two_line('Teacher Scorer', 'Separate GPU', 13.5, 12), size=13.5)
    f.box(BX, yC - bh / 2, BW, bh, fill=SKY['fill'], stroke=SKY['line'], label=two_line('Student', 'Being trained', 13.5, 12), size=13.5)
    for y in (yB, yC):
        f.edge([(BX + BW + 1, y), (LX0 + 2, y)], width=1.2, end=5)
    hmax, bwid = 24, 5
    for cx, (pt, ps) in zip(xs, PROBS4):
        for y, p_, pal in ((yB, pt, LEAF), (yC, ps, SKY)):
            base = y + hmax / 2
            f.box(cx - bwid / 2, base - hmax * p_, bwid, hmax * p_, fill=pal['tok'], stroke=pal['line'], width=0.7, arc=1)
        kl = min(1.0, abs(math.log(pt / ps)) / 2.6)
        h = max(2.0, 16 * kl)
        f.box(cx - bwid / 2, yD + 8 - h, bwid, h, fill=SLATE['tok'], stroke=SLATE['line'], width=0.7, arc=1)
    for y in (yB + hmax / 2, yC + hmax / 2, yD + 8):
        f.line([(LX0 + 4, y), (LX1, y)], color=SLATE['tok'], width=0.8)
    f.text(BX, yD, 'Reverse KL', size=12.5, color=MUTED, bold=True)
    ax = BX + 100
    f.edge([(ax, yD - 9), (ax, yC + bh / 2 + 1)], color=SKY['line'], width=1.4, end=5)
    f.text(ax - 6, (yD - 9 + yC + bh / 2) / 2, 'Gradient', size=12, color=SKY['dark'], anchor='e', italic=True)
    f.text((LX0 + LX1) / 2, yD + 24, 'Same loss on every token, whoever wrote it', size=12.5, color=MUTED, anchor='c')


def build4i():
    H = 690
    f = Fig(W4, H, LABEL)
    legend4(f)
    Y1, ys = 32, 32 + 74
    yt = ys + 92
    H1 = yt + 42 - Y1
    f.panel(6, Y1, 708, H1, SLATE, 'Relay Rollout Inside vLLM Speculative Decoding', num=1)
    relay4(f, 6, Y1, 708, ys, yt, hand_label=True)
    Y2 = Y1 + H1 + 12
    rules4i(f, 6, Y2, 708, 202)
    Y3 = Y2 + 202 + 12
    train4i(f, 6, Y3, 708, H - 6 - Y3)
    return f


def build46(v):
    """Rounds 4-6 (English only)."""
    return {'r4a': build4a, 'r4i': build4i, 'r4m': build4m, 'r5a': build5a, 'r5i': build5i, 'r5m': build5m,
            'r6a': build6a, 'r6i': build6i, 'r6m': build6m}[v]()


def rules4m(f, X, Y, W, H):
    """Round-4 merge: the rule rows of round 3 (with the brace of r4a) on the grid of panels 1 and 3: trigger names in the
    left column, the conditions in the token column, the result on the right; the footnote of r4i."""
    f.panel(X, Y, W, H, LAV, 'When Does the Teacher Take Over?', num=2)
    lab_w = max(label_w(t, 12.5) for t in ('Teacher’s top-1', 'Student’s top-5', 'Student’s top-1')) + 12
    x = LX0
    tw = label_w('Take Over', 12.5, True) + 16
    res_x = X + W - 14 - tw
    rows = ((Y + 52, Y + 80), (Y + 126, Y + 154))
    rights = []
    for k, (ya, yb) in enumerate(rows):
        f.token(BX + 5, ya, LAV, size=10)
        f.text(BX + 16, ya, ('Reflection Trigger', 'Concluding Trigger')[k], size=13.5, bold=True)
        f.text(x, ya, 'Teacher’s top-1', size=12.5, color=MUTED)
        f.text(x, yb, ('Student’s top-5', 'Student’s top-1')[k], size=12.5, color=MUTED)
        if k == 0:
            e = f.chip(x + lab_w, ya, 'Wait', LEAF, size=12.5, solid=True, bold=True, pad=6)
            r1 = f.text(e + 8, ya, 'is one of 45 reflection words', size=12.5)[1]
            e = x + lab_w
            for w_ in ('So', 'Then', 'We', 'The', 'Let'):
                e = f.chip(e, yb, w_, SKY, size=12.5, pad=6) + 4
            f.cross(e + 7, yb, s=7)
            r2 = f.text(e + 16, yb, 'no Wait', size=12.5)[1]
        else:
            f.text(BX + 16, yb, 'Implemented in the<br>verification step', size=12, color=MUTED, italic=True, lh=1.25)
            e = final_chip(f, x + lab_w, ya)
            r1 = f.text(e + 8, ya, 'starts the final answer', size=12.5)[1]
            e = f.chip(x + lab_w, yb, 'So', SKY, size=12.5, pad=6)
            r2 = f.text(e + 8, yb, 'keeps going', size=12.5)[1]
        rights.append(max(r1, r2))
    bx_ = max(rights) + 20
    for ya, yb in rows:
        tip = brace(f, bx_, ya - 11, yb + 11, LAV['line'])
        ym = (ya + yb) / 2
        f.edge([(tip + 2, ym), (res_x - 2, ym)], color=LAV['line'], width=1.6, end=5)
        f.chip(res_x, ym, 'Take Over', LAV, size=12.5, solid=True, bold=True, pad=8)
    f.line([(X + 14, Y + 103), (X + W - 14, Y + 103)], color=LAV['tok'], width=1, dashed=True, dash='3 3')
    f.text(BX, Y + H - 17, 'Both are checked while the teacher verifies the draft: no extra forward pass.', size=12, color=MUTED)


def train4m(f, X, Y, W, H):
    """Round-4 merge: the matrix of r4i with room for the gradient arrow, and a taller KL row."""
    import math
    f.panel(X, Y, W, H, SKY, 'Token-Level Distillation', num=3)
    segs, end_x, pitch = layout4()
    xs = [c for s in segs for c in s]
    yA = Y + 54
    yB, yC = yA + 40, yA + 86
    yD = yC + 60
    f.text(BX, yA, 'Relayed Answer', size=12.5, color=MUTED, bold=True)
    for (lane, _), cs in zip(SEGS4, segs):
        for i, cx in enumerate(cs):
            f.token(cx, yA, SKY if lane == 's' else (LAV if i == 0 else LEAF), size=TOK)
    bh = 38
    f.box(BX, yB - bh / 2, BW, bh, fill=LEAF['soft'], stroke=LEAF['line'], label=two_line('Teacher Scorer', 'Separate GPU', 13.5, 12), size=13.5)
    f.box(BX, yC - bh / 2, BW, bh, fill=SKY['fill'], stroke=SKY['line'], label=two_line('Student', 'Being trained', 13.5, 12), size=13.5)
    for y in (yB, yC):
        f.edge([(BX + BW + 1, y), (LX0 + 2, y)], width=1.2, end=5)
    hmax, bwid = 24, 5
    kmax = 20
    for cx, (pt, ps) in zip(xs, PROBS4):
        for y, p_, pal in ((yB, pt, LEAF), (yC, ps, SKY)):
            base = y + hmax / 2
            f.box(cx - bwid / 2, base - hmax * p_, bwid, hmax * p_, fill=pal['tok'], stroke=pal['line'], width=0.7, arc=1)
        kl = min(1.0, abs(math.log(pt / ps)) / 2.6)
        h = max(2.5, kmax * kl)
        f.box(cx - bwid / 2, yD + kmax / 2 - h, bwid, h, fill=SLATE['tok'], stroke=SLATE['line'], width=0.7, arc=1)
    for y in (yB + hmax / 2, yC + hmax / 2, yD + kmax / 2):
        f.line([(LX0 + 4, y), (LX1, y)], color=SLATE['tok'], width=0.8)
    f.text(BX, yD + 2, 'Reverse KL', size=12.5, color=MUTED, bold=True)
    ax = BX + BW - 22
    f.edge([(ax, yD - 8), (ax, yC + bh / 2 + 1)], color=SKY['line'], width=1.4, end=5)
    f.text(ax - 6, (yD - 8 + yC + bh / 2) / 2, 'Gradient', size=12, color=SKY['dark'], anchor='e', italic=True)
    f.text((LX0 + LX1) / 2, yD + kmax / 2 + 18, 'Same loss on every token, whoever wrote it', size=12.5, color=MUTED, anchor='c')


def build4m():
    Y1, ys = 32, 32 + 74
    yt = ys + 92
    H1 = yt + 42 - Y1
    Y2 = Y1 + H1 + 12
    H2 = 196
    Y3 = Y2 + H2 + 12
    H3 = 54 + 86 + 60 + 10 + 18 + 18
    H = Y3 + H3 + 6
    f = Fig(W4, H, LABEL)
    legend4(f)
    f.panel(6, Y1, 708, H1, SLATE, 'Relay Rollout Inside vLLM Speculative Decoding', num=1)
    relay4(f, 6, Y1, 708, ys, yt, hand_label=True)
    rules4m(f, 6, Y2, 708, H2)
    train4m(f, 6, Y3, 708, H3)
    return f


# ------------------------------------------------------------------ round 5
def legend5(f, y=14, ghost=False, cross_inside=False):
    """The token key; with ghost, a fifth item for the rejected draft token."""
    items = [(SKY, 'Student token'), (LEAF, 'Teacher token'), (LAV, 'Takeover point')]
    if ghost:
        items.append(('ghost', 'Rejected draft'))
    items.append((None, 'Answer ends'))
    x = BX - 4
    for pal, text in items:
        if pal is None:
            f.box(x, y - 5.5, 11, 11, fill=INK, stroke=INK, width=0.9, arc=2)
        elif pal == 'ghost':
            f.box(x, y - 5.5, 11, 11, fill=WHITE, stroke=SKY['line'], width=1, arc=2, dashed=True)
            if cross_inside:
                f.cross(x + 5.5, y, s=5, color=ROSE['line'], width=1.4)
        else:
            f.token(x + 5.5, y, pal, size=11)
        x0, x1 = f.text(x + 17, y, text, size=12.5)
        x = x1 + (16 if ghost else 18)


def rules5(f, X, Y, W, H):
    """Round 5: r4m's rule rows with the footnote clear of the left-column note."""
    rules4m(f, X, Y, W, H)


def train5(f, X, Y, W, H, kl_role='line'):
    """Round 5: r4m's matrix with a darker KL row, so the two takeover tokens' loss stands out."""
    import math
    f.panel(X, Y, W, H, SKY, 'Token-Level Distillation', num=3)
    segs, end_x, pitch = layout4()
    xs = [c for s_ in segs for c in s_]
    yA = Y + 54
    yB, yC = yA + 40, yA + 86
    yD = yC + 62
    f.text(BX, yA, 'Relayed Answer', size=12.5, color=MUTED, bold=True)
    for (lane, _), cs in zip(SEGS4, segs):
        for i, cx in enumerate(cs):
            f.token(cx, yA, SKY if lane == 's' else (LAV if i == 0 else LEAF), size=TOK)
    bh = 38
    f.box(BX, yB - bh / 2, BW, bh, fill=LEAF['soft'], stroke=LEAF['line'], label=two_line('Teacher Scorer', 'Separate GPU', 13.5, 12), size=13.5)
    f.box(BX, yC - bh / 2, BW, bh, fill=SKY['fill'], stroke=SKY['line'], label=two_line('Student', 'Being trained', 13.5, 12), size=13.5)
    for y in (yB, yC):
        f.edge([(BX + BW + 1, y), (LX0 + 2, y)], width=1.2, end=5)
    hmax, bwid, kmax = 24, 5, 24
    for cx, (pt, ps) in zip(xs, PROBS4):
        for y, p_, pal in ((yB, pt, LEAF), (yC, ps, SKY)):
            base = y + hmax / 2
            f.box(cx - bwid / 2, base - hmax * p_, bwid, hmax * p_, fill=pal['tok'], stroke=pal['line'], width=0.7, arc=1)
        kl = min(1.0, abs(math.log(pt / ps)) / 2.6)
        h = max(2.5, kmax * kl)
        f.box(cx - bwid / 2, yD + kmax / 2 - h, bwid, h, fill=SLATE[kl_role], stroke=SLATE['line'], width=0.7, arc=1)
    for y in (yB + hmax / 2, yC + hmax / 2, yD + kmax / 2):
        f.line([(LX0 + 4, y), (LX1, y)], color=SLATE['tok'], width=0.8)
    f.text(BX, yD + 4, 'Reverse KL', size=12.5, color=MUTED, bold=True)
    ax = BX + BW - 22
    f.edge([(ax, yD - 6), (ax, yC + bh / 2 + 1)], color=SKY['line'], width=1.4, end=5)
    f.text(ax - 6, (yD - 6 + yC + bh / 2) / 2, 'Gradient', size=12, color=SKY['dark'], anchor='e', italic=True)
    f.text((LX0 + LX1) / 2, yD + kmax / 2 + 18, 'Same loss on every token, whoever wrote it', size=12.5, color=MUTED, anchor='c')
    return yD + kmax / 2 + 18 + 18 - Y


def build5(ghosts=False, kl_role='line', cross_inside=False):
    Y1, ys = 32, 32 + 74
    yt = ys + 92
    H1 = yt + 42 - Y1
    Y2 = Y1 + H1 + 12
    H2 = 210
    Y3 = Y2 + H2 + 12
    H3 = 54 + 86 + 62 + 12 + 18 + 18
    H = Y3 + H3 + 6
    f = Fig(W4, H, LABEL)
    legend5(f, ghost=ghosts, cross_inside=cross_inside)
    f.panel(6, Y1, 708, H1, SLATE, 'Relay Rollout Inside vLLM Speculative Decoding', num=1)
    relay4(f, 6, Y1, 708, ys, yt, hand_label=True, ghosts=ghosts, cross_inside=cross_inside)
    rules5(f, 6, Y2, 708, H2)
    train5(f, 6, Y3, 708, H3, kl_role=kl_role)
    return f


def build5a():
    """Round-5 aesthetic: r4m with breathing room in panel 2 and a darker KL row."""
    return build5()


def build5i():
    """Round-5 innovative: the speculative-decoding detail at the takeover points: the student's draft token there is
    drawn dashed and crossed (the teacher rejects it and writes the reflection or the final-answer header instead);
    the key gets a fifth item."""
    return build5(ghosts=True)


def build5m():
    """Round-5 merge: r5a's spacing and KL row with r5i's rejected draft tokens, the cross drawn inside the dashed token
    (below it, it ran into the takeover arrow)."""
    return build5(ghosts=True, cross_inside=True)


# ------------------------------------------------------------------ round 6
def legend6(f, y=14, draft_pair=False, gap=20):
    """r5m's key; draft_pair: one item explains both marks under the student's drafts (accepted / rejected). Items are
    spaced by the web font's own advance widths (Comic Neue), so the gaps look even on the page."""
    if not draft_pair:
        return legend5(f, y, ghost=True, cross_inside=True)
    x = BX - 4

    def label(x0, text):
        f.text(x0, y, text, size=12.5)
        return x0 + web_w(text, 12.5) + gap

    for pal, text in ((SKY, 'Student token'), (LEAF, 'Teacher token'), (LAV, 'Takeover point')):
        f.token(x + 5.5, y, pal, size=11)
        x = label(x + 17, text)
    f.check(x + 5, y + 0.5, s=6.5, color=LEAF['line'], width=1.7)
    f.box(x + 14, y - 5.5, 11, 11, fill=WHITE, stroke=SKY['line'], width=1, arc=2, dashed=True)
    f.cross(x + 19.5, y, s=5, color=ROSE['line'], width=1.4)
    x = label(x + 31, 'Draft accepted / rejected')
    f.box(x, y - 5.5, 11, 11, fill=INK, stroke=INK, width=0.9, arc=2)
    f.text(x + 17, y, 'Answer ends', size=12.5)


def train6(f, X, Y, W, H):
    """Round 6: r5m's matrix, the KL row closer to the student row and its label centred on the row."""
    import math
    f.panel(X, Y, W, H, SKY, 'Token-Level Distillation', num=3)
    segs, end_x, pitch = layout4()
    xs = [c for s_ in segs for c in s_]
    yA = Y + 54
    yB, yC = yA + 40, yA + 86
    yD = yC + 56
    f.text(BX, yA, 'Relayed Answer', size=12.5, color=MUTED, bold=True)
    for (lane, _), cs in zip(SEGS4, segs):
        for i, cx in enumerate(cs):
            f.token(cx, yA, SKY if lane == 's' else (LAV if i == 0 else LEAF), size=TOK)
    bh = 38
    f.box(BX, yB - bh / 2, BW, bh, fill=LEAF['soft'], stroke=LEAF['line'], label=two_line('Teacher Scorer', 'Separate GPU', 13.5, 12), size=13.5)
    f.box(BX, yC - bh / 2, BW, bh, fill=SKY['fill'], stroke=SKY['line'], label=two_line('Student', 'Being trained', 13.5, 12), size=13.5)
    for y in (yB, yC):
        f.edge([(BX + BW + 1, y), (LX0 + 2, y)], width=1.2, end=5)
    hmax, bwid, kmax = 24, 5, 24
    for cx, (pt, ps) in zip(xs, PROBS4):
        for y, p_, pal in ((yB, pt, LEAF), (yC, ps, SKY)):
            base = y + hmax / 2
            f.box(cx - bwid / 2, base - hmax * p_, bwid, hmax * p_, fill=pal['tok'], stroke=pal['line'], width=0.7, arc=1)
        kl = min(1.0, abs(math.log(pt / ps)) / 2.6)
        h = max(2.5, kmax * kl)
        f.box(cx - bwid / 2, yD + kmax / 2 - h, bwid, h, fill=SLATE['line'], stroke=SLATE['line'], width=0.7, arc=1)
    for y in (yB + hmax / 2, yC + hmax / 2, yD + kmax / 2):
        f.line([(LX0 + 4, y), (LX1, y)], color=SLATE['tok'], width=0.8)
    f.text(BX, yD + 4, 'Reverse KL', size=12.5, color=MUTED, bold=True)
    ax = BX + BW - 22
    f.edge([(ax, yD - 6), (ax, yC + bh / 2 + 1)], color=SKY['line'], width=1.4, end=5)
    f.text(ax - 6, (yD - 6 + yC + bh / 2) / 2, 'Gradient', size=12, color=SKY['dark'], anchor='e', italic=True)
    f.text((LX0 + LX1) / 2, yD + kmax / 2 + 18, 'Same loss on every token, whoever wrote it', size=12.5, color=MUTED, anchor='c')


def build6(draft_pair=False):
    Y1, ys = 32, 32 + 74
    yt = ys + 92
    H1 = yt + 42 - Y1
    Y2 = Y1 + H1 + 12
    H2 = 210
    Y3 = Y2 + H2 + 12
    H3 = 54 + 86 + 56 + 12 + 18 + 18
    H = Y3 + H3 + 6
    f = Fig(W4, H, LABEL)
    legend6(f, draft_pair=draft_pair)
    f.panel(6, Y1, 708, H1, SLATE, 'Relay Rollout Inside vLLM Speculative Decoding', num=1)
    relay4(f, 6, Y1, 708, ys, yt, hand_label=True, ghosts=True, cross_inside=True)
    rules5(f, 6, Y2, 708, H2)
    train6(f, 6, Y3, 708, H3)
    return f


def build6a():
    """Round-6 aesthetic: r5m with the KL row 6 px closer to the student row (less empty band in panel 3)."""
    return build6()


def build6i():
    """Round-6 innovative: the key explains both marks on the student's lane, the checks under accepted draft blocks and
    the crossed draft token where the teacher takes over."""
    return build6(draft_pair=True)


def build6m():
    """Round-6 merge (final): r6a's spacing with r6i's key."""
    return build6(draft_pair=True)
