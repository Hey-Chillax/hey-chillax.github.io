"""Aesthetic versions of every figure: same content as the base version, refined drawing."""
import math

from figlib import (ALF, FAMILY, HPQ, LG, OPD, PAIRED, SM, Svg, T, arrow, chevron, chip_legend, data_table, end_labels,
                    hbar, hit_points, legend, moving_avg, polyline, run, scale, vbar, width_of, x_axis, y_axis, bi)


def _pills(svg, names, key, y, h, size=12, gap=18, W=None):
    widths = [max(width_of(n, size) + 22, 44) for n in names]
    total = sum(widths) + gap * (len(names) - 1)
    x = ((W or svg.w) - total) / 2
    centers = []
    for i, (n, w) in enumerate(zip(names, widths)):
        k = i == key
        svg.rect(x, y, w, h, 'box-fill' if k else 'box', rx=h / 2)
        svg.text(x + w / 2, y + h / 2 + 4.2, n, cls='t-on' if k else 't-strong', anchor='middle', size=size)
        centers.append(x + w / 2)
        if i < len(names) - 1:
            chevron(svg, x + w + gap / 2, y + h / 2, 4)
        x += w + gap
    return centers


def card_opd(W=380):
    svg = Svg(W, 120, 'Scaffold-OPD pipeline; in the Scaffold-OPD stage the teacher takes over the student rollout')
    names = [T('Teacher data', '老师数据'), T('SFT'), T('Scaffold-OPD'), T('GRPO')]
    c = _pills(svg, names, 2, 8, 26)
    n, cw, cg = 25, 10.4, 3
    sw = n * cw + (n - 1) * cg
    x0, sy = (W - sw) / 2, 70
    teacher = {8: 'Wait,', 9: None, 10: None, 11: None, 18: 'But', 19: None, 20: None}
    svg.line(c[2], 38, c[2], sy - 18, 'leader')
    for i in range(n):
        x = x0 + i * (cw + cg)
        t = i in teacher
        svg.rect(x, sy, cw, 14, 'tok-t' if t else 'tok-s', rx=3, extra='' if t else 'opacity=".7"')
        if teacher.get(i):
            svg.text(x, sy - 5, teacher[i], cls='t-accent', size=11)
    chip_legend(svg, x0 + 38, sy + 38, [('tok-s', T('student writes', '学生写')), ('tok-t', T('teacher takes over', '老师接管'))])
    return svg


def card_scr(W=380):
    svg = Svg(W, 120, 'StepCredit-RL pipeline; multi-turn RL gives each step its own credit')
    names = [T('Expert demos', '专家示范'), T('SFT'), T('Multi-turn RL', '多轮 RL'), T('Paired eval', '配对评测')]
    c = _pills(svg, names, 2, 8, 26)
    credit = [0.15, 0.25, 0.95, 0.2, 0.1, 0.3, 0.85, 0.2, 0.6]
    n = len(credit)
    x0, x1, base = 40, W - 40, 88
    step = (x1 - x0) / (n - 1)
    svg.line(c[2], 38, c[2], base - 30, 'leader')
    svg.line(x0, base, x1, base, 'grid')
    for i, v in enumerate(credit):
        x = x0 + i * step
        hgt = 4 + 20 * v
        cls = 's1' if v > 0.5 else 's3'
        svg.path(vbar(x - 4, base - 6, base - 6 - hgt, 8, 2.5), cls)
        svg.circle(x, base, 3.6, f'dot {cls}')
    svg.text(W / 2, base + 22, T('one outcome reward → credit for each step', '一个结局奖励 → 每一步各自的信用'), cls='t-muted', anchor='middle', size=11.5)
    return svg


def _stage_cards(svg, items, key, x, y, w, h, gap):
    for i, (title, detail) in enumerate(items):
        bx = x + i * (w + gap)
        svg.rect(bx, y, w, h, 'box-key' if i == key else 'box', rx=10)
        svg.text(bx + 12, y + 18, f'0{i + 1}', cls='t-accent' if i == key else 't-faint', size=10.5, ls='0.08em')
        svg.text(bx + 12, y + 38, title, cls='t-strong', size=12.5)
        svg.text(bx + 12, y + 55, detail, cls='t-muted', size=11)
        if i:
            cx = bx - gap / 2
            svg.line(bx - gap + 3, y + h / 2, bx - 3, y + h / 2, 'arrow')
            chevron(svg, bx - 5, y + h / 2, 3.5)


def _score_pill(svg, cx, y, text, cls_box, cls_text, size=12):
    w = width_of(text, size) + 18
    svg.rect(cx - w / 2, y, w, 22, cls_box, rx=11)
    svg.text(cx, y + 15, text, cls=cls_text, anchor='middle', size=size)


def opd_pipeline(W):
    items = [(T('Teacher solutions', '老师解答'), T('14,116 problems', '14,116 道题')),
             (T('Rejection sampling', '拒绝采样'), T('79% kept', '保留 79%')),
             (T('SFT'), T('1 epoch', '1 轮')),
             (T('Scaffold-OPD'), T('40 steps', '40 步')),
             (T('GRPO on failures', '错题回流 GRPO'), T('2,212 problems', '2,212 道题'))]
    scores = ['25.4', None, '38.0', '42.6', '46.6']
    if W >= 500:
        w, gap, h = 126, 17, 68
        x = (W - (5 * w + 4 * gap)) / 2
        svg = Svg(W, 126, 'Scaffold-OPD pipeline with the 4-benchmark average after each stage')
        _stage_cards(svg, items, 3, x, 6, w, h, gap)
        for i, s in enumerate(scores):
            if s:
                cx = x + i * (w + gap) + w / 2
                if i == 0:
                    _score_pill(svg, cx, 92, T(f'base {s}', f'基座 {s}'), 'box-soft', 't-muted', 11.5)
                else:
                    _score_pill(svg, cx, 92, s, 'box-fill' if i == 3 else 'box-soft', 't-on' if i == 3 else 't-strong')
        return svg
    w, h, gap = W - 16, 50, 12
    H = 6 + 5 * h + 4 * gap + 6
    svg = Svg(W, H, 'Scaffold-OPD pipeline with the 4-benchmark average after each stage')
    for i, (title, detail) in enumerate(items):
        y = 6 + i * (h + gap)
        svg.rect(8, y, w, h, 'box-key' if i == 3 else 'box', rx=10)
        svg.text(22, y + 21, f'0{i + 1}', cls='t-accent' if i == 3 else 't-faint', size=10.5, ls='0.08em')
        svg.text(48, y + 21, title, cls='t-strong', size=12.5)
        svg.text(48, y + 38, detail, cls='t-muted', size=11)
        if scores[i]:
            txt = T(f'base {scores[i]}', f'基座 {scores[i]}') if i == 0 else scores[i]
            pw = width_of(txt, 12) + 16
            svg.rect(8 + w - 12 - pw, y + 14, pw, 22, 'box-fill' if i == 3 else 'box-soft', rx=11)
            svg.text(8 + w - 12 - pw / 2, y + 29, txt, cls='t-on' if i == 3 else ('t-muted' if i == 0 else 't-strong'), anchor='middle', size=12)
        if i:
            chevron(svg, 8 + w / 2, y - gap / 2, 3.5, 'arrow')
    return svg


def opd_takeover(W):
    narrow = W < 500
    H = 236 if narrow else 196
    svg = Svg(W, H, 'One relayed answer: student tokens with two teacher takeovers')
    x0, x1 = 14, W - 14
    sy = 108 if narrow else 84
    segs = [(0.26, 's', None), (0.17, 't', 'Wait, …'), (0.31, 's', None), (0.14, 't', 'But …')]
    width = (x1 - x0) * 0.9
    cx = x0
    pos = []
    for frac, who, lab in segs:
        sw = width * frac
        svg.rect(cx, sy, sw - 3, 26, 'tok-t' if who == 't' else 'tok-s', rx=6, extra='' if who == 't' else 'opacity=".75"')
        if lab:
            svg.text(cx + (sw - 3) / 2, sy + 17.5, lab, cls='t-on', anchor='middle', size=12)
        pos.append((cx, cx + sw - 3))
        cx += sw
    svg.text(cx + 4, sy + 17.5, T('end', '结束'), cls='t-faint', size=11.5)
    (t1s, t1e), (t2s, t2e) = pos[1], pos[3]

    def badge(x, y, n):
        svg.circle(x, y, 8.5, 'box-key')
        svg.text(x, y + 4, str(n), cls='t-accent', anchor='middle', size=11)

    if narrow:
        lines = [(1, T('Teacher’s top next token is a reflection', '老师最想写的下一个 token 是反思词，')),
                 (None, T('word not in the student’s top-5 → take over', '且不在学生 top-5 里 → 老师接管')),
                 (2, T('Write ≤ 3 paragraphs, then hand back', '最多写 3 段（≤256 token）后交还'))]
        y = 18
        for n, t in lines:
            if n:
                badge(x0 + 8, y - 4, n)
            svg.text(x0 + 24, y, t, size=12)
            y += 20 if n is None or n == 1 else 20
        svg.line(t1s + 1, 72, t1s + 1, sy - 4, 'leader')
        svg.text(x0, sy + 48, T('At most 2 takeovers; the answer ends after the second.', '每条回答最多接管 2 次，第 2 次后结束。'), cls='t-muted', size=11.5)
        badge(x0 + 8, sy + 72, 3)
        svg.text(x0 + 24, sy + 76, T('Every token carries its author →', '每个 token 都带作者标记 →'), size=12)
        svg.text(x0 + 24, sy + 94, T('token-level reverse KL on the whole answer', '对整条回答做 token 级反向 KL'), size=12)
        chip_legend(svg, x0, H - 8, [('tok-s', T('student', '学生')), ('tok-t', T('teacher', '老师'))])
        return svg
    badge(t1s + 9, 22, 1)
    svg.text(t1s + 24, 26, T('Teacher’s most likely next token is a reflection word', '老师最想写的下一个 token 是反思词（Wait、But 等），'), size=12.5)
    svg.text(t1s + 24, 44, T('(Wait, But, …) that is not in the student’s top-5', '且不在学生的 top-5 里'), cls='t-muted', size=12)
    svg.line(t1s + 1, 52, t1s + 1, sy - 4, 'leader')
    svg.line(t1e - 1, sy + 30, t1e - 1, sy + 42, 'leader')
    badge(t1e + 9, sy + 50, 2)
    svg.text(t1e + 24, sy + 54, T('≤ 3 paragraphs (≤ 256 tokens), then hand back', '最多 3 段（≤ 256 token）后交还'), size=12)
    svg.text(t2s, sy + 78, T('at most 2 takeovers per answer', '每条回答最多接管 2 次'), cls='t-faint', size=11.5)
    badge(x0 + 9, sy + 100, 3)
    svg.text(x0 + 24, sy + 104, T('Every token carries its author → token-level reverse KL to the teacher on the whole answer',
                                  '每个 token 都带作者标记 → 对整条回答做对老师的 token 级反向 KL'), size=12.5)
    chip_legend(svg, x1 - 150, 26, [('tok-s', T('student', '学生')), ('tok-t', T('teacher', '老师'))])
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
    H = top + pitch * len(rows) + 24
    svg = Svg(W, H, '4-benchmark math average by post-training method')
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
        if narrow:
            svg.text(x0, yb - 6, lab, cls='t-strong' if strong else ('t-muted' if i == 5 else ''), size=12)
        else:
            svg.text(x0 - 12, yb + bh / 2 + 4.2, lab, cls='t-strong' if strong else ('t-muted' if i == 5 else ''), anchor='end', size=12.5)
        svg.mark(f'{lab[0]}: {v:.2f}', f'<path class="bar s{idx}" d="{hbar(x0, yb, sx(v), bh)}"{" opacity=\".55\"" if i == 5 else ""}/>')
        svg.text(sx(v) + 6, yb + bh / 2 + 4.2, f'{v:.1f}', cls='t-strong' if strong else '', size=12)
    # bracket: Scaffold-OPD vs OPD
    xb = sx(d['takeover_conclude_40']) + (40 if not narrow else 34)
    yo, yt = ys[3] + bh / 2, ys[4] + bh / 2
    svg.path(f'M{xb - 5:.1f},{yo:.1f} H{xb:.1f} V{yt:.1f} H{xb - 5:.1f}', 'leader')
    svg.text(xb + 6, (yo + yt) / 2 + 4, '+6.2', cls='t-accent', size=12)
    return svg


def opd_budget(W):
    import math as m
    b = OPD['budget']
    xs = [m.log2(t) for t in b['tokens']]
    narrow = W < 500
    H = 300
    box = (40, 46, W - (64 if narrow else 150), H - 34)
    svg = Svg(W, H, 'Accuracy versus evaluation token budget, Scaffold-OPD vs OPD')
    legend(svg, box[0], 16, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    sx, sy = scale(10, 15, box[0], box[2]), scale(0, 50, box[3], box[1])
    tk, op = b['takeover_40'], b['opd_40']
    # shaded gap between the curves, coloured by which one leads
    for lead, cls in [(1, 'wash1'), (-1, 'wash2')]:
        seg = []
        for x, a, c in zip(xs, tk, op):
            if (a - c) * lead > 0:
                seg.append((x, a, c))
            elif seg:
                break
        if len(seg) >= 2:
            top_pts = ' '.join(f'L{sx(x):.1f},{sy(max(a, c)):.1f}' for x, a, c in seg)
            bot_pts = ' '.join(f'L{sx(x):.1f},{sy(min(a, c)):.1f}' for x, a, c in reversed(seg))
            svg.path('M' + top_pts[1:] + ' ' + bot_pts + ' Z', cls)
    y_axis(svg, box, sy, range(0, 51, 10))
    ticks = [10, 11, 12, 13, 14, 15]
    x_axis(svg, box, sx, ticks, fmt=lambda v: f'{int(2 ** v / 1024)}k', title=None)
    svg.text(box[2], box[3] + 32, T('evaluation budget (tokens)', '评测预算（token）'), cls='t-faint', anchor='end', size=11)
    for t in (13, 14, 15):
        i = xs.index(t)
        diff = tk[i] - op[i]
        svg.line(sx(t), box[1] - 4, sx(t), box[3], 'grid')
        svg.text(sx(t), box[1] - 8, f'{diff:+.1f}', cls='t-strong' if diff > 1 else 't-muted', anchor='middle', size=11.5)
    for idx, pts in [(2, list(zip(xs, op))), (1, list(zip(xs, tk)))]:
        svg.path(polyline(pts, sx, sy), f'line l{idx}')
    for idx, name, pts in [(1, 'Scaffold-OPD', list(zip(xs, tk))), (2, 'OPD', list(zip(xs, op)))]:
        hit_points(svg, pts, sx, sy, lambda x, y, n=name: f'{n} · {int(round(2 ** x)):,} tokens: {y:.1f}')
        svg.circle(sx(pts[-1][0]), sy(pts[-1][1]), 4, f'dot s{idx}')
    end_labels(svg, [(sx(15) + 9, sy(tk[-1]), f'{tk[-1]:.1f}' if narrow else f'Scaffold-OPD {tk[-1]:.1f}', 't-strong'),
                     (sx(15) + 9, sy(op[-1]), f'{op[-1]:.1f}' if narrow else f'OPD {op[-1]:.1f}', '')])
    svg.text(box[0] + 2, box[1] - 8, T('gap at 8k / 16k / 32k →', '8k / 16k / 32k 处的差距 →'), cls='t-faint', size=10.5) if not narrow else None
    return svg


def _panel_title(svg, x, y, t, sub=None):
    svg.text(x, y, t, cls='t-strong', size=12.5)
    if sub:
        svg.text(x + width_of(t, 12.5) + 8, y, sub, cls='t-faint', size=11)


def opd_training(W):
    tr = OPD['train']
    tk = moving_avg([(s, l) for s, l in zip(tr['takeover']['step'], tr['takeover']['response_length']) if s != 19])
    op = moving_avg(list(zip(tr['opd']['step'], tr['opd']['response_length'])))
    ratio = moving_avg([(s, 100 * r) for s, r in zip(tr['takeover']['step'], tr['takeover']['teacher_token_ratio']) if s != 19])
    narrow = W < 500
    if narrow:
        H = 480
        bA, bB = (44, 62, W - 70, 212), (44, 304, W - 70, 448)
    else:
        H = 292
        bA, bB = (46, 62, W / 2 - 78, H - 40), (W / 2 + 44, 62, W - 62, H - 40)
    svg = Svg(W, H, 'Training dynamics: response length and teacher-token share')
    legend(svg, bA[0], 16, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    sxA, syA = scale(0, 60, bA[0], bA[2]), scale(0, 6000, bA[3], bA[1])
    _panel_title(svg, bA[0], bA[1] - 16, T('Response length', '回答长度'), T('tokens', 'token'))
    y_axis(svg, bA, syA, [0, 2000, 4000, 6000], fmt=lambda v: f'{v / 1000:.0f}k' if v else '0')
    x_axis(svg, bA, sxA, [0, 20, 40, 60], title=T('step', '步'))
    for idx, pts in [(2, op), (1, tk)]:
        svg.path(polyline(pts, sxA, syA), f'line l{idx}')
        svg.circle(sxA(pts[-1][0]), syA(pts[-1][1]), 4, f'dot s{idx}')
    hit_points(svg, tk, sxA, syA, lambda x, y: f'Scaffold-OPD · step {x}: {y:,.0f} tokens', r=5)
    hit_points(svg, op, sxA, syA, lambda x, y: f'OPD · step {x}: {y:,.0f} tokens', r=5)
    end_labels(svg, [(sxA(60) + 8, syA(tk[-1][1]), f'{tk[-1][1]:,.0f}', 't-strong'), (sxA(60) + 8, syA(op[-1][1]), f'{op[-1][1]:,.0f}', '')])
    sxB, syB = scale(0, 60, bB[0], bB[2]), scale(0, 20, bB[3], bB[1])
    _panel_title(svg, bB[0], bB[1] - 16, T('Teacher-token share', '老师 token 占比'), T('Scaffold-OPD, %', 'Scaffold-OPD，%'))
    y_axis(svg, bB, syB, [0, 5, 10, 15, 20])
    x_axis(svg, bB, sxB, [0, 20, 40, 60], title=T('step', '步'))
    area = polyline(ratio, sxB, syB) + f' L{sxB(ratio[-1][0]):.1f},{syB(0):.1f} L{sxB(ratio[0][0]):.1f},{syB(0):.1f} Z'
    svg.path(area, 'wash1')
    svg.path(polyline(ratio, sxB, syB), 'line l1')
    svg.circle(sxB(ratio[-1][0]), syB(ratio[-1][1]), 4, 'dot s1')
    hit_points(svg, ratio, sxB, syB, lambda x, y: f'step {x}: {y:.1f}%', r=5)
    svg.text(sxB(60) + 8, syB(ratio[-1][1]) + 4, f'{ratio[-1][1]:.1f}%', cls='t-strong', size=12)
    return svg


def scr_pipeline(W):
    items = [(T('Expert demos', '专家示范'), T('22,810 tool-call steps', '22,810 步工具调用')),
             (T('SFT'), T('1 epoch · 356 steps', '1 轮 · 356 步')),
             (T('Multi-turn RL', '多轮 RL'), T('StepCredit-RL', 'StepCredit-RL')),
             (T('Paired eval', '配对评测'), T('McNemar, same tasks', '同题 McNemar 检验'))]
    scores = [T('base 7.1 / 2.2', '基座 7.1 / 2.2'), T('67.1 / 67.2'), T('98.6 / 94.0'), None]
    if W >= 500:
        w, gap, h = 163, 21, 68
        x = (W - (4 * w + 3 * gap)) / 2
        svg = Svg(W, 126, 'StepCredit-RL pipeline with ALFWorld success after each stage')
        _stage_cards(svg, items, 2, x, 6, w, h, gap)
        for i, s in enumerate(scores):
            if s:
                cx = x + i * (w + gap) + w / 2
                _score_pill(svg, cx, 92, s, 'box-fill' if i == 2 else 'box-soft', 't-on' if i == 2 else ('t-muted' if i == 0 else 't-strong'))
        return svg
    w, h, gap = W - 16, 50, 12
    H = 6 + 4 * h + 3 * gap + 6
    svg = Svg(W, H, 'StepCredit-RL pipeline with ALFWorld success after each stage')
    for i, (title, detail) in enumerate(items):
        y = 6 + i * (h + gap)
        svg.rect(8, y, w, h, 'box-key' if i == 2 else 'box', rx=10)
        svg.text(22, y + 21, f'0{i + 1}', cls='t-accent' if i == 2 else 't-faint', size=10.5, ls='0.08em')
        svg.text(48, y + 21, title, cls='t-strong', size=12.5)
        svg.text(48, y + 38, detail, cls='t-muted', size=11)
        if scores[i]:
            pw = width_of(scores[i], 12) + 16
            svg.rect(8 + w - 12 - pw, y + 14, pw, 22, 'box-fill' if i == 2 else 'box-soft', rx=11)
            svg.text(8 + w - 12 - pw / 2, y + 29, scores[i], cls='t-on' if i == 2 else ('t-muted' if i == 0 else 't-strong'), anchor='middle', size=12)
        if i:
            chevron(svg, 8 + w / 2, y - gap / 2, 3.5)
    return svg


def scr_steplevel(W):
    narrow = W < 500
    rows = [(['A', 'B', 'C', 'D'], True), (['A', 'E', 'B', 'F'], False), (['A', 'B', 'G'], True)]
    if narrow:
        colx, rowy, H = [36, 98, 160, 222], [34, 88, 142], 288
    else:
        colx, rowy, H = [52, 140, 228, 316], [40, 98, 156], 196
    svg = Svg(W, H, 'Steps from the same environment state are compared across rollouts')
    bpos = []
    for r, (states, ok) in enumerate(rows):
        y = rowy[r]
        svg.text(colx[0] - 28, y + 4, f'#{r + 1}', cls='t-faint', anchor='middle', size=11)
        for c, s in enumerate(states):
            x = colx[c]
            key = s == 'B'
            if c:
                arrow(svg, colx[c - 1] + 15, y, x - 16, y)
            svg.circle(x, y, 14, 'box-key' if key else 'box-soft')
            svg.text(x, y + 4.3, s, cls='t-accent' if key else 't-muted', anchor='middle', size=12)
            if key:
                bpos.append((x, y))
        ex = colx[len(states) - 1] + 26
        svg.rect(ex, y - 11, 64, 22, 'box-soft', rx=11)
        svg.text(ex + 32, y + 4, T('success', '成功') if ok else T('fail', '失败'), cls='t-strong' if ok else 't-muted', anchor='middle', size=11.5)
    for (xa, ya), (xb, yb) in zip(bpos, bpos[1:]):
        svg.path(f'M{xa:.1f},{ya + 14:.1f} C{xa:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{yb - 14:.1f}', 'line l1', 'opacity=".45" stroke-width="1.5"')
    if narrow:
        tx, ty = 12, 196
        svg.line(tx, ty - 16, W - 12, ty - 16, 'grid')
        svg.text(tx, ty, T('Episode level', '整局'), cls='t-strong', size=12.5)
        svg.text(tx + 92, ty, T('compare the outcomes of #1–#3', '比较 #1–#3 的最终成败'), size=12)
        svg.text(tx, ty + 24, T('Step level', '步级'), cls='t-strong', size=12.5)
        svg.text(tx + 92, ty + 24, T('compare actions taken from B', '比较从 B 出发的动作'), size=12)
        svg.text(tx + 92, ty + 42, T('by what followed them', '各自之后的结果'), cls='t-muted', size=12)
        svg.text(tx, ty + 70, T('No critic, no extra rollouts.', '无需 critic，也无需额外 rollout。'), cls='t-faint', size=11.5)
        return svg
    tx = 492
    svg.line(tx - 22, 26, tx - 22, 170, 'grid')
    svg.text(tx, 46, T('Episode level', '整局'), cls='t-strong', size=13)
    svg.text(tx, 65, T('compare the outcomes of #1–#3', '比较 #1–#3 的最终成败'), size=12)
    svg.text(tx, 104, T('Step level', '步级'), cls='t-strong', size=13)
    svg.text(tx, 123, T('compare actions taken from B', '比较从 B 出发的动作'), size=12)
    svg.text(tx, 140, T('(B→C, B→F, B→G) by what followed', '（B→C、B→F、B→G）之后的结果'), cls='t-muted', size=12)
    svg.text(tx, 172, T('No critic, no extra rollouts.', '无需 critic，也无需额外 rollout。'), cls='t-faint', size=11.5)
    return svg


def scr_sft_rl(W):
    sft = dict(run(ALF, 'sft_gigpo', 'seen'))
    sftu = dict(run(ALF, 'sft_gigpo', 'unseen'))
    stages = [(T('Base', '基座'), 7.1, 2.2), (T('SFT'), sft[0], sftu[0])] + [(T(f'RL {k}', f'RL {k} 步'), sft[k], sftu[k]) for k in (10, 20, 50, 100)]
    narrow = W < 500
    if narrow:
        pitch, bh = 46, 12
        x0, x1, top = 62, W - 44, 32
        H = top + pitch * len(stages) + 22
        svg = Svg(W, H, 'ALFWorld success by stage, seen and unseen')
        legend(svg, 8, 16, [(1, 'seen'), (2, 'unseen')])
        sx = scale(0, 100, x0, x1)
        for v in range(0, 101, 25):
            svg.line(sx(v), top, sx(v), top + pitch * len(stages) - 6, 'grid' if v else 'axis')
            svg.text(sx(v), top + pitch * len(stages) + 10, str(v), cls='t-faint', anchor='middle', size=11)
        for i, (lab, s, u) in enumerate(stages):
            y = top + i * pitch + 8
            svg.text(x0 - 8, y + bh + 4, lab, anchor='end', size=12, cls='t-strong' if i == 5 else '')
            for j, (v, idx) in enumerate([(s, 1), (u, 2)]):
                yb = y + j * (bh + 2)
                svg.mark(f'{lab[0]} {("seen", "unseen")[j]}: {v:.1f}%', f'<path class="bar s{idx}" d="{hbar(x0, yb, sx(v), bh, 3)}"/>')
                svg.text(sx(v) + 5, yb + bh - 1.5, f'{v:.1f}', size=11, cls='t-strong' if i == 5 else '')
        return svg
    H = 300
    x0, x1, y0, y1 = 44, W - 14, 50, H - 36
    svg = Svg(W, H, 'ALFWorld success by stage, seen and unseen')
    legend(svg, x0, 16, [(1, 'seen'), (2, 'unseen')])
    sy = scale(0, 100, y1, y0)
    y_axis(svg, (x0, y0, x1, y1), sy, [0, 25, 50, 75, 100])
    gw = (x1 - x0) / len(stages)
    bw = 20
    for i, (lab, s, u) in enumerate(stages):
        cx = x0 + gw * (i + 0.5)
        svg.text(cx, y1 + 19, lab, anchor='middle', size=12, cls='t-strong' if i == 5 else '')
        for j, (v, idx) in enumerate([(s, 1), (u, 2)]):
            bx = cx - bw - 1.5 if j == 0 else cx + 1.5
            svg.mark(f'{lab[0]} {("seen", "unseen")[j]}: {v:.1f}%', f'<path class="bar s{idx}" d="{vbar(bx, y1, sy(v), bw)}"/>')
            svg.text(bx + bw / 2, sy(v) - 6, f'{v:.1f}', anchor='middle', size=10.5, cls='t-strong' if i == 5 else 't-muted')
    # annotation: plateau after 20 RL steps
    xa, xb = x0 + gw * 3.5, x0 + gw * 5.5
    ya = sy(100) - 18
    svg.path(f'M{xa - 22:.1f},{ya + 5:.1f} V{ya:.1f} H{xb + 22:.1f} V{ya + 5:.1f}', 'leader')
    svg.text((xa + xb) / 2, ya - 6, T('flat after 20 RL steps', 'RL 20 步后基本不动'), cls='t-muted', anchor='middle', size=11.5)
    return svg


def _gap_wash(svg, a_pts, b_pts, sx, sy):
    """Shade between two series sampled at the same x: blue where a leads, sand where b leads."""
    for i in range(len(a_pts) - 1):
        (x0, a0), (x1, a1) = a_pts[i], a_pts[i + 1]
        (_, b0), (_, b1) = b_pts[i], b_pts[i + 1]
        cls = 'wash1' if (a0 + a1) >= (b0 + b1) else 'wash2'
        svg.path(f'M{sx(x0):.1f},{sy(a0):.1f} L{sx(x1):.1f},{sy(a1):.1f} L{sx(x1):.1f},{sy(b1):.1f} L{sx(x0):.1f},{sy(b0):.1f} Z', cls)


def scr_vs_grpo(W):
    narrow = W < 500
    g = {k: run(ALF, 'gigpo', k) for k in ('seen', 'unseen')}
    r = {k: run(ALF, 'grpo', k) for k in ('seen', 'unseen')}
    if narrow:
        H = 520
        boxes = {'seen': (40, 70, W - 64, 236), 'unseen': (40, 318, W - 64, 484)}
    else:
        H = 310
        boxes = {'seen': (40, 70, W / 2 - 60, H - 40), 'unseen': (W / 2 + 44, 70, W - 58, H - 40)}
    svg = Svg(W, H, 'ALFWorld validation success over 200 steps, StepCredit-RL vs GRPO')
    legend(svg, 40, 16, [(1, 'StepCredit-RL'), (2, 'GRPO')])
    for name, box in boxes.items():
        sx, sy = scale(0, 200, box[0], box[2]), scale(0, 100, box[3], box[1])
        _panel_title(svg, box[0], box[1] - 20, f'valid_{name}', T('success, %', '成功率，%'))
        svg.rect(sx(160), box[1], sx(200) - sx(160), box[3] - box[1], 'band')
        late_g = sum(v for s, v in g[name] if s >= 160) / 5
        late_r = sum(v for s, v in r[name] if s >= 160) / 5
        svg.text((sx(160) + sx(200)) / 2, box[1] + 13, f'{late_g:.1f} vs {late_r:.1f}', cls='t-muted', anchor='middle', size=10.5)
        y_axis(svg, box, sy, [0, 25, 50, 75, 100])
        x_axis(svg, box, sx, [0, 50, 100, 150, 200], title=None)
        _gap_wash(svg, g[name], r[name], sx, sy)
        for idx, pts in [(2, r[name]), (1, g[name])]:
            svg.path(polyline(pts, sx, sy), f'line l{idx}')
            svg.circle(sx(pts[-1][0]), sy(pts[-1][1]), 4, f'dot s{idx}')
        hit_points(svg, g[name], sx, sy, lambda x, y: f'StepCredit-RL · step {x}: {y:.1f}%', r=5)
        hit_points(svg, r[name], sx, sy, lambda x, y: f'GRPO · step {x}: {y:.1f}%', r=5)
        end_labels(svg, [(sx(200) + 8, sy(g[name][-1][1]), f'{g[name][-1][1]:.1f}', 't-strong'),
                         (sx(200) + 8, sy(r[name][-1][1]), f'{r[name][-1][1]:.1f}', '')], min_gap=14)
    svg.text(boxes['seen'][0] + 2, H - 8, T('shaded band: mean of the last 5 validations (steps 160–200)', '灰色区间：最后 5 次验证（第 160–200 步）的均值'), cls='t-faint', size=10.5)
    return svg


def scr_updates(W):
    narrow = W < 500
    four = run(ALF, 'gigpo_4upd', 'seen')
    one = [(s, v) for s, v in run(ALF, 'gigpo', 'seen') if s <= 150]
    H = 300
    box = (40, 50, W - (64 if narrow else 140), H - 40)
    svg = Svg(W, H, 'Seen success with one vs four updates per step')
    legend(svg, box[0], 16, [(1, T('4 updates / step', '每步 4 次更新')), (2, T('1 update / step', '每步 1 次更新'))])
    sx, sy = scale(0, 150, box[0], box[2]), scale(0, 100, box[3], box[1])
    y_axis(svg, box, sy, [0, 25, 50, 75, 100])
    x_axis(svg, box, sx, [0, 50, 100, 150], title=T('step', '步'))
    for idx, pts in [(2, one), (1, four)]:
        svg.path(polyline(pts, sx, sy), f'line l{idx}')
        svg.circle(sx(pts[-1][0]), sy(pts[-1][1]), 4, f'dot s{idx}')
    hit_points(svg, four, sx, sy, lambda x, y: f'4 updates · step {x}: {y:.1f}%', r=5)
    hit_points(svg, one, sx, sy, lambda x, y: f'1 update · step {x}: {y:.1f}%', r=5)
    y100 = dict(one)[100]
    svg.circle(sx(100), sy(y100), 4, 'dot s2')
    # "same level" link: 4 updates at step 100 ≈ 1 update at step 150
    ya = sy(dict(four)[100]) - 18
    svg.path(f'M{sx(100):.1f},{ya + 6:.1f} V{ya:.1f} H{sx(150):.1f} V{ya + 6:.1f}', 'leader')
    svg.text((sx(100) + sx(150)) / 2, ya - 6, T('≈ 1.5× fewer steps', '约少 1/3 的步数'), cls='t-muted', anchor='middle', size=11.5)
    if narrow:
        end_labels(svg, [(sx(100) + 8, sy(four[-1][1]) + 14, f'{four[-1][1]:.1f}', 't-strong'), (sx(150) + 8, sy(one[-1][1]), f'{one[-1][1]:.1f}', '')])
    else:
        svg.text(sx(100) + 8, sy(four[-1][1]) + 18, f'{four[-1][1]:.1f}', cls='t-strong', size=12)
        svg.text(sx(150) + 8, sy(one[-1][1]) + 4, T(f'1 update {one[-1][1]:.1f}', f'1 次更新 {one[-1][1]:.1f}'), size=12)
    svg.text(sx(100) + 8, sy(y100) + 16, T(f'step 100: {y100:.1f}', f'第 100 步：{y100:.1f}'), cls='t-faint', size=11)
    return svg


def scr_hotpotqa(W):
    narrow = W < 500
    em_em, em_sh = run(HPQ, 'em', 'em'), run(HPQ, 'shaped', 'em')
    rq_em, rq_sh = run(HPQ, 'em', 'repeat_queries'), run(HPQ, 'shaped', 'repeat_queries')
    if narrow:
        H = 500
        bA, bB = (44, 70, W - 64, 230), (44, 318, W - 64, 470)
    else:
        H = 300
        bA, bB = (44, 70, W / 2 - 64, H - 40), (W / 2 + 46, 70, W - 64, H - 40)
    svg = Svg(W, H, 'HotpotQA: exact match and repeated queries, EM reward vs shaped reward')
    legend(svg, bA[0], 16, [(1, T('EM reward', 'EM 奖励')), (2, T('shaped reward', '稠密奖励'))])
    sxA, syA = scale(0, 200, bA[0], bA[2]), scale(40, 60, bA[3], bA[1])
    _panel_title(svg, bA[0], bA[1] - 20, T('Exact match', 'EM'), '%')
    y_axis(svg, bA, syA, [40, 45, 50, 55, 60])
    x_axis(svg, bA, sxA, [0, 100, 200])
    _gap_wash(svg, em_em, em_sh, sxA, syA)
    for idx, pts in [(2, em_sh), (1, em_em)]:
        svg.path(polyline(pts, sxA, syA), f'line l{idx}')
        svg.circle(sxA(pts[-1][0]), syA(pts[-1][1]), 4, f'dot s{idx}')
    hit_points(svg, em_em, sxA, syA, lambda x, y: f'EM reward · step {x}: {y:.1f}%', r=5)
    hit_points(svg, em_sh, sxA, syA, lambda x, y: f'shaped · step {x}: {y:.1f}%', r=5)
    end_labels(svg, [(sxA(200) + 8, syA(em_em[-1][1]), f'{em_em[-1][1]:.1f}', 't-strong'), (sxA(200) + 8, syA(em_sh[-1][1]), f'{em_sh[-1][1]:.1f}', '')])
    sxB, syB = scale(0, 200, bB[0], bB[2]), scale(0, 0.2, bB[3], bB[1])
    _panel_title(svg, bB[0], bB[1] - 20, T('Repeated queries', '重复查询'), T('per question', '每题'))
    y_axis(svg, bB, syB, [0, 0.05, 0.1, 0.15, 0.2], fmt=lambda v: f'{v:.2f}' if v else '0')
    x_axis(svg, bB, sxB, [0, 100, 200])
    _gap_wash(svg, rq_em, rq_sh, sxB, syB)
    for idx, pts in [(2, rq_sh), (1, rq_em)]:
        svg.path(polyline(pts, sxB, syB), f'line l{idx}')
        svg.circle(sxB(pts[-1][0]), syB(pts[-1][1]), 4, f'dot s{idx}')
    hit_points(svg, rq_em, sxB, syB, lambda x, y: f'EM reward · step {x}: {y:.3f}', r=5)
    hit_points(svg, rq_sh, sxB, syB, lambda x, y: f'shaped · step {x}: {y:.3f}', r=5)
    end_labels(svg, [(sxB(200) + 8, syB(rq_em[-1][1]), f'{rq_em[-1][1]:.3f}', ''), (sxB(200) + 8, syB(rq_sh[-1][1]), f'{rq_sh[-1][1]:.3f}', 't-strong')])
    svg.text(bA[0], H - 8, T('training step', '训练步'), cls='t-faint', size=10.5)
    return svg


FIGS = {
    'card-opd': card_opd, 'card-scr': card_scr,
    'opd-pipeline': opd_pipeline, 'opd-takeover': opd_takeover, 'opd-methods': opd_methods,
    'opd-budget': opd_budget, 'opd-training': opd_training,
    'scr-pipeline': scr_pipeline, 'scr-steplevel': scr_steplevel, 'scr-sft-rl': scr_sft_rl,
    'scr-vs-grpo': scr_vs_grpo, 'scr-updates': scr_updates, 'scr-hotpotqa': scr_hotpotqa,
}
