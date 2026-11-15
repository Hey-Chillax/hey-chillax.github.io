"""Innovative versions: each figure re-thought, sometimes restructured, with the same data and the same claims."""
import math

from figlib import (ALF, FAMILY, HPQ, OPD, PAIRED, Svg, T, arrow, chevron, chip_legend, end_labels, hbar, hit_points, legend,
                    moving_avg, polyline, run, scale, vbar, width_of, x_axis, y_axis)


def _breadcrumb(svg, names, key, y, size=11.5):
    gap = 16
    widths = [width_of(n, size) for n in names]
    x = (svg.w - (sum(widths) + gap * (len(names) - 1))) / 2
    for i, (n, w) in enumerate(zip(names, widths)):
        svg.text(x, y, n, cls='t-accent' if i == key else 't-faint', size=size)
        if i == key:
            svg.line(x, y + 5, x + w, y + 5, 'line l1', 'stroke-width="1.6"')
        if i < len(names) - 1:
            chevron(svg, x + w + gap / 2, y - 4, 3)
        x += w + gap


def card_opd(W=380):
    """A paragraph of word-chips: the student's own text, with two runs written by the teacher."""
    svg = Svg(W, 122, 'An answer written by the student, with two passages written by the teacher')
    words = [[34, 18, 46, 26, 40, 22, 30, 38, 20], [28, 44, 20, 32, 48, 36, 26, 30], [40, 24, 30, 52, 22, 34, 28, 26], [30, 46, 22, 38, 26, 20, 44]]
    teacher = {(1, 4), (1, 5), (1, 6), (1, 7), (3, 2), (3, 3)}
    labels = {(1, 4): 'Wait,', (3, 2): 'But'}
    x0, gap, y0 = 26, 5, 18
    for r, row in enumerate(words):
        x = x0
        y = y0 + r * 20
        for c, w in enumerate(row):
            if x + w > W - 26:
                break
            t = (r, c) in teacher
            svg.rect(x, y, w, 10, 'tok-t' if t else 'tok-s', rx=5, extra='' if t else 'opacity=".55"')
            if (r, c) in labels:
                svg.text(x, y - 3.5, labels[(r, c)], cls='t-accent', size=10.5)
            x += w + gap
    _breadcrumb(svg, [T('Teacher data', '老师数据'), T('SFT'), T('Scaffold-OPD'), T('GRPO')], 2, 108)
    return svg


def card_scr(W=380):
    """Two rollouts meet at the same state B; the actions taken from B get opposite credit."""
    svg = Svg(W, 122, 'Two rollouts share state B; the steps taken from B receive opposite credit')
    A, B = (40, 52), (118, 52)
    up, dn = [(196, 26), (262, 26)], [(196, 78), (262, 78)]
    arrow(svg, A[0] + 12, A[1], B[0] - 14, B[1])
    for path, ok in [(up, True), (dn, False)]:
        px, py = B
        for i, (x, y) in enumerate(path):
            arrow(svg, px + (12 if i else 13), py + (0 if i else (y - py) * 0.18), x - 12, y)
            px, py = x, y
        for (x, y) in path:
            svg.circle(x, y, 10, 'box-soft')
        svg.rect(path[-1][0] + 20, path[-1][1] - 10, 62, 20, 'box-soft', rx=10)
        svg.text(path[-1][0] + 51, path[-1][1] + 4, T('success', '成功') if ok else T('fail', '失败'), cls='t-strong' if ok else 't-muted', anchor='middle', size=11)
    svg.circle(A[0], A[1], 10, 'box-soft')
    svg.text(A[0], A[1] + 4, 'A', cls='t-muted', anchor='middle', size=11)
    svg.circle(B[0], B[1], 12, 'box-key')
    svg.circle(B[0], B[1], 17, 'ring', 'opacity=".35"')
    svg.text(B[0], B[1] + 4, 'B', cls='t-accent', anchor='middle', size=11.5)
    # credit of the two actions taken from B
    svg.path(vbar(150, 30, 14, 8, 2.5), 's1')
    svg.text(162, 24, '+', cls='t-accent', size=13)
    svg.path(f'M150,74 V86 A2.5,2.5 0 0 0 152.5,88.5 H155.5 A2.5,2.5 0 0 0 158,86 V74 Z', 's2')
    svg.text(162, 90, '−', cls='t-muted', size=13)
    _breadcrumb(svg, [T('Expert demos', '专家示范'), T('SFT'), T('Multi-turn RL', '多轮 RL'), T('Paired eval', '配对评测')], 2, 112)
    return svg


def opd_pipeline(W):
    """The pipeline as a path through (training GPU-hours, score): same score as Scaffold-OPD alone at ~4x compute."""
    narrow = W < 500
    H = 320 if not narrow else 330
    box = (44, 52, W - (24 if narrow else 150), H - 42)
    svg = Svg(W, H, 'Score versus cumulative training GPU-hours: the full pipeline and Scaffold-OPD alone')
    legend(svg, box[0], 18, [(2, T('full pipeline', '全流程')), (1, T('Scaffold-OPD alone', '只做 Scaffold-OPD'))])
    sx, sy = scale(0, 56, box[0], box[2]), scale(20, 50, box[3], box[1])
    y_axis(svg, box, sy, [20, 30, 40, 50])
    x_axis(svg, box, sx, [0, 10, 20, 30, 40, 50], title=None)
    svg.text(box[2], box[3] + 32, T('cumulative training GPU-hours (2 × A100)', '累计训练卡时（2 × A100）'), cls='t-faint', anchor='end', size=11)
    svg.text(box[0] - 36, box[1] - 14, T('4-benchmark average', '4 项平均'), cls='t-faint', size=11)
    g = OPD['gpu_hours']['pipeline']
    p = OPD['pipeline_avg4']
    pts = [(0, p['base']), (g['sft_incl_teacher_data'], p['sft']), (g['sft_incl_teacher_data'] + g['takeover_40'], p['takeover_40']),
           (g['sft_incl_teacher_data'] + g['takeover_40'] + g['grpo_30'], p['grpo_30'])]
    labels = [T('base', '基座'), T('+ SFT'), T('+ Scaffold-OPD'), T('+ GRPO')]
    svg.path(polyline(pts, sx, sy), 'line l2')
    for (x, y), lab in zip(pts, labels):
        svg.circle(sx(x), sy(y), 4.5, 'dot s2')
        dy = 18 if lab[0] in ('+ SFT', '+ Scaffold-OPD') else -10
        svg.text(sx(x) + 8, sy(y) + dy, (f'{lab[0]} {y:.1f}', f'{lab[1]} {y:.1f}'), cls='t-muted' if lab[0] == 'base' else '', size=11.5)
    alone = (OPD['gpu_hours']['takeover_40'], OPD['eval_avg4']['takeover_40'])
    svg.line(sx(0), sy(p['base']), sx(alone[0]), sy(alone[1]), 'line l1', 'opacity=".9"')
    svg.circle(sx(alone[0]), sy(alone[1]), 5.5, 'dot s1')
    svg.line(sx(alone[0]) + 8, sy(alone[1]), sx(pts[-1][0]) - 8, sy(alone[1]), 'leader')
    mid = (sx(alone[0]) + sx(pts[-1][0])) / 2
    svg.text(mid, sy(alone[1]) - 8, T('same score, about 4× the GPU-hours', '分数相同，卡时约 4 倍'), cls='t-strong', anchor='middle', size=12)
    svg.text(sx(alone[0]) - 6, sy(alone[1]) + 20, T(f'Scaffold-OPD alone {alone[1]:.1f}', f'只做 Scaffold-OPD {alone[1]:.1f}'), cls='t-accent', anchor='start', size=11.5)
    hit_points(svg, pts, sx, sy, lambda x, y: f'{x:.1f} GPU-h: {y:.2f}')
    hit_points(svg, [alone], sx, sy, lambda x, y: f'Scaffold-OPD alone · {x:.1f} GPU-h: {y:.2f}')
    return svg


def opd_takeover(W):
    """Two lanes: the student drafts, the teacher verifies; at a reflection point the generation moves to the teacher lane."""
    narrow = W < 500
    H = 300 if narrow else 238
    svg = Svg(W, H, 'Student and teacher lanes: the teacher takes over at a reflection point, then hands back')
    lx = 64 if not narrow else 54
    ys, yt = (64, 128) if not narrow else (60, 116)
    x_end = W - 18
    svg.text(10, ys + 4, T('student', '学生'), cls='t-muted', size=11.5)
    svg.text(10, yt + 4, T('teacher', '老师'), cls='t-accent', size=11.5)
    svg.line(lx, ys, x_end, ys, 'grid')
    svg.line(lx, yt, x_end, yt, 'grid')
    span = x_end - lx
    segs = [('s', 0.00, 0.24), ('t', 0.26, 0.42), ('s', 0.44, 0.70), ('t', 0.72, 0.84)]
    for who, a, b in segs:
        y = ys if who == 's' else yt
        n = max(2, int((b - a) * span / 13))
        cw = (b - a) * span / n
        for i in range(n):
            svg.rect(lx + a * span + i * cw, y - 7, cw - 3, 14, 'tok-t' if who == 't' else 'tok-s', rx=3, extra='' if who == 't' else 'opacity=".7"')
    for frac_from, frac_to, down in [(0.24, 0.26, True), (0.42, 0.44, False), (0.70, 0.72, True)]:
        x1, x2 = lx + frac_from * span, lx + frac_to * span
        if down:
            svg.path(f'M{x1:.1f},{ys + 8:.1f} C{x1 + 10:.1f},{(ys + yt) / 2:.1f} {x2 - 10:.1f},{(ys + yt) / 2:.1f} {x2:.1f},{yt - 9:.1f}', 'line l1', 'stroke-width="1.6"')
        else:
            svg.path(f'M{x1:.1f},{yt - 8:.1f} C{x1 + 10:.1f},{(ys + yt) / 2:.1f} {x2 - 10:.1f},{(ys + yt) / 2:.1f} {x2:.1f},{ys + 9:.1f}', 'line l3', 'stroke-width="1.6"')
    t1 = lx + 0.26 * span
    t2 = lx + 0.72 * span
    svg.text(t1 + 2, yt + 26, 'Wait, …', cls='t-accent', size=11.5)
    svg.text(t2 + 2, yt + 26, 'But …', cls='t-accent', size=11.5)
    svg.text(lx + 0.86 * span, ys + 4, T('end', '结束'), cls='t-faint', size=11)
    # decision inset at the first takeover
    bx, by = (lx, yt + 44) if narrow else (lx + 0.30 * span, 16)
    if not narrow:
        bx, by = 16, yt + 40
    bw = (W - 32) if narrow else 418
    svg.rect(bx, by, bw, 52, 'box-soft', rx=10)
    svg.text(bx + 12, by + 20, T('teacher’s next token', '老师的下一个 token'), cls='t-faint', size=11)
    svg.rect(bx + 12, by + 27, 46, 18, 'box-fill', rx=5)
    svg.text(bx + 35, by + 40, 'Wait', cls='t-on', anchor='middle', size=11.5)
    sx0 = bx + 148
    svg.text(sx0, by + 20, T('student’s top-5', '学生的 top-5'), cls='t-faint', size=11)
    cands = ['So', 'Then', 'We', 'The', 'Let']
    cx = sx0
    for c in cands:
        w = width_of(c, 11.5) + 12
        svg.rect(cx, by + 27, w, 18, 'box', rx=5)
        svg.text(cx + w / 2, by + 40, c, cls='t-muted', anchor='middle', size=11.5)
        cx += w + 4
    if not narrow:
        svg.text(bx + bw - 12, by + 40, T('not in top-5 → take over', '不在 top-5 → 接管'), cls='t-strong', anchor='end', size=11.5)
        svg.text(bx + bw + 16, by + 20, T('≤ 3 paragraphs, ≤ 2 takeovers per answer', '每段 ≤ 3 段，每条回答 ≤ 2 次'), cls='t-faint', size=11)
        svg.text(bx + bw + 16, by + 40, T('every token keeps its author', '每个 token 都记录作者'), cls='t-faint', size=11)
    else:
        svg.text(bx + 12, by + 70, T('Wait is not in the top-5 → the teacher takes over', 'Wait 不在 top-5 → 老师接管'), cls='t-strong', size=11.5)
        svg.text(bx + 12, by + 90, T('≤ 3 paragraphs, ≤ 2 takeovers per answer', '每次 ≤ 3 段，每条回答 ≤ 2 次'), cls='t-faint', size=11)
    return svg


def opd_methods(W):
    """Accuracy against training compute: the same 13 GPU-hours buy +6.2 with Scaffold-OPD."""
    d, g = OPD['eval_avg4'], OPD['gpu_hours']
    pts = [(T('Base', '基座'), 0, d['base'], 3), (T('SFT (incl. teacher solutions)', 'SFT（含老师解答）'), g['sft_incl_teacher_data'], d['sft'], 3),
           (T('GRPO, 60 steps', 'GRPO，60 步'), g['grpo_60'], d['grpo_60'], 3), (T('OPD, 40 steps', 'OPD，40 步'), g['opd_40'], d['opd_40'], 2),
           (T('Scaffold-OPD, 40 steps', 'Scaffold-OPD，40 步'), g['takeover_40'], d['takeover_conclude_40'], 1)]
    narrow = W < 500
    H = 320
    box = (44, 34, W - (26 if narrow else 30), H - 44)
    svg = Svg(W, H, 'Four-benchmark average against training GPU-hours for each method')
    sx, sy = scale(-2, 40, box[0], box[2]), scale(20, 50, box[3], box[1])
    y_axis(svg, box, sy, [20, 30, 40, 50])
    x_axis(svg, box, sx, [0, 10, 20, 30, 40])
    svg.text(box[2], box[3] + 32, T('training GPU-hours', '训练卡时'), cls='t-faint', anchor='end', size=11)
    svg.text(box[0] - 36, box[1] - 14, T('4-benchmark average', '4 项平均'), cls='t-faint', size=11)
    xo, yo = sx(g['opd_40']), sy(d['opd_40'])
    xs_, ys_ = sx(g['takeover_40']), sy(d['takeover_conclude_40'])
    arrow(svg, xo, yo - 7, xs_, ys_ + 8, 'line l1', 6)
    svg.text(xo + 10, (yo + ys_) / 2 + 4, T('+6.2 at the same compute', '同样算力 +6.2'), cls='t-accent', size=11.5)
    for lab, x, y, idx in pts:
        r = 6.5 if idx == 1 else 5
        svg.mark(f'{lab[0]}: {y:.2f} at {x} GPU-h', f'<circle class="dot s{idx}" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="{r}"/>')
        anchor = 'end' if lab[0].startswith('GRPO') else 'start'
        dx = -10 if anchor == 'end' else 10
        dy = 4 if not lab[0].startswith('OPD') else 14
        if lab[0].startswith('Scaffold'):
            dy = 4
        svg.text(sx(x) + dx, sy(y) + dy, (f'{lab[0]} {y:.1f}', f'{lab[1]} {y:.1f}'), cls='t-strong' if idx == 1 else ('' if idx == 2 else 't-muted'), anchor=anchor, size=11.5)
    return svg


def opd_budget(W):
    """Top: accuracy against the budget. Bottom: the paired gap with a ±1 SE band; it crosses zero near 8k."""
    b = OPD['budget']
    xs = [math.log2(t) for t in b['tokens']]
    narrow = W < 500
    H = 420 if not narrow else 440
    right = 70 if narrow else 140
    top = (44, 46, W - right, 220)
    bot = (44, 268, W - right, H - 40)
    svg = Svg(W, H, 'Accuracy and the Scaffold-OPD minus OPD gap against the evaluation budget')
    legend(svg, 44, 16, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    sx = scale(10, 15, top[0], top[2])
    syA = scale(0, 50, top[3], top[1])
    y_axis(svg, top, syA, [0, 25, 50])
    tk, op = b['takeover_40'], b['opd_40']
    for idx, vals in [(2, op), (1, tk)]:
        pts = list(zip(xs, vals))
        svg.path(polyline(pts, sx, syA), f'line l{idx}')
        svg.circle(sx(15), syA(vals[-1]), 4, f'dot s{idx}')
        hit_points(svg, pts, sx, syA, lambda x, y, n=('Scaffold-OPD', 'OPD')[idx - 1]: f'{n} · {int(round(2 ** x)):,} tokens: {y:.1f}', r=5)
    end_labels(svg, [(sx(15) + 8, syA(tk[-1]), f'{tk[-1]:.1f}' if narrow else f'Scaffold-OPD {tk[-1]:.1f}', 't-strong'),
                     (sx(15) + 8, syA(op[-1]), f'{op[-1]:.1f}' if narrow else f'OPD {op[-1]:.1f}', '')])
    svg.text(top[0], top[1] - 10, T('Accuracy', '准确率'), cls='t-strong', size=12.5)
    gap, se = b['gap_40'], b['gap_se_40']
    syB = scale(-5, 8, bot[3], bot[1])
    svg.text(bot[0], bot[1] - 12, T('Gap: Scaffold-OPD − OPD', '差距：Scaffold-OPD − OPD'), cls='t-strong', size=12.5)
    svg.text(bot[0] + width_of(T('Gap: Scaffold-OPD − OPD', '差距：Scaffold-OPD − OPD'), 12.5) + 8, bot[1] - 12, T('± 1 SE', '± 1 个标准误'), cls='t-faint', size=11)
    y_axis(svg, bot, syB, [-4, 0, 4, 8], fmt=lambda v: f'{v:+.0f}' if v else '0')
    band = ' '.join(f'L{sx(x):.1f},{syB(g + s):.1f}' for x, g, s in zip(xs, gap, se))
    band_back = ' '.join(f'L{sx(x):.1f},{syB(g - s):.1f}' for x, g, s in reversed(list(zip(xs, gap, se))))
    svg.path('M' + band[1:] + ' ' + band_back + ' Z', 'wash1')
    svg.line(bot[0], syB(0), bot[2], syB(0), 'axis')
    pts = list(zip(xs, gap))
    svg.path(polyline(pts, sx, syB), 'line l1')
    hit_points(svg, pts, sx, syB, lambda x, y: f'{int(round(2 ** x)):,} tokens: {y:+.2f}', r=5)
    for t in (13, 14, 15):
        i = xs.index(t)
        svg.circle(sx(t), syB(gap[i]), 4, 'dot s1')
        svg.text(sx(t), syB(gap[i]) - 10, f'{gap[i]:+.1f}', cls='t-strong', anchor='middle', size=11.5)
    x_axis(svg, bot, sx, [10, 11, 12, 13, 14, 15], fmt=lambda v: f'{int(2 ** v / 1024)}k')
    svg.text(bot[2], bot[3] + 32, T('evaluation budget (tokens)', '评测预算（token）'), cls='t-faint', anchor='end', size=11)
    return svg


def opd_training(W):
    """Indexed to the first five steps: the teacher's share falls mostly because answers get longer."""
    tr = OPD['train']['takeover']
    keep = [(s, l, r, tt) for s, l, r, tt in zip(tr['step'], tr['response_length'], tr['teacher_token_ratio'], tr['teacher_tokens_per_answer']) if s != 19 and tt is not None]
    L = moving_avg([(s, l) for s, l, r, tt in keep])
    R = moving_avg([(s, 100 * r) for s, l, r, tt in keep])
    TT = moving_avg([(s, tt) for s, l, r, tt in keep])
    def index(series):
        base = series[4][1]
        return [(s, 100 * v / base) for s, v in series[4:]]
    narrow = W < 500
    H = 310
    box = (48, 40, W - (76 if narrow else 196), H - 40)
    svg = Svg(W, H, 'Response length, teacher tokens per answer and teacher-token share, indexed to steps 1 to 5')
    sx, sy = scale(5, 60, box[0], box[2]), scale(0, 400, box[3], box[1])
    y_axis(svg, box, sy, [0, 100, 200, 300, 400])
    x_axis(svg, box, sx, [5, 20, 40, 60], title=T('step', '步'))
    svg.text(box[0] - 40, box[1] - 16, T('index, steps 1–5 = 100', '指数，第 1–5 步 = 100'), cls='t-faint', size=11)
    series = [(2, T('response length', '回答长度'), index(L)), (3, T('teacher tokens / answer', '每条回答的老师 token'), index(TT)), (1, T('teacher-token share', '老师 token 占比'), index(R))]
    labels = []
    for idx, name, pts in series:
        svg.path(polyline(pts, sx, sy), f'line l{idx}')
        svg.circle(sx(pts[-1][0]), sy(pts[-1][1]), 4, f'dot s{idx}')
        hit_points(svg, pts, sx, sy, lambda x, y, n=name[0]: f'{n} · step {x}: {y:.0f}', r=5)
        ratio = pts[-1][1] / 100
        txt = f'×{ratio:.2f}' if narrow else (f'{name[0]} ×{ratio:.2f}', f'{name[1]} ×{ratio:.2f}')
        labels.append((sx(60) + 8, sy(pts[-1][1]), txt, 't-strong' if idx == 1 else ''))
    end_labels(svg, labels, min_gap=15)
    return svg


def scr_pipeline(W):
    """Stage cards with the model's success built in as micro-bars."""
    stages = [(T('Base model', '基座模型'), T('before training', '训练前'), (7.1, 2.2)),
              (T('Expert SFT', '专家 SFT'), T('22,810 steps · 1 epoch', '22,810 步 · 1 轮'), (67.1, 67.2)),
              (T('Multi-turn RL', '多轮 RL'), T('StepCredit-RL · 100 steps', 'StepCredit-RL · 100 步'), (98.6, 94.0)),
              (T('Paired eval', '配对评测'), T('McNemar, same tasks', '同题 McNemar 检验'), None)]
    narrow = W < 500
    if not narrow:
        w, gap, h = 163, 21, 104
        x = (W - (4 * w + 3 * gap)) / 2
        svg = Svg(W, 120, 'StepCredit-RL pipeline with ALFWorld success after each stage')
        for i, (title, detail, sc) in enumerate(stages):
            bx = x + i * (w + gap)
            svg.rect(bx, 6, w, h, 'box-key' if i == 2 else 'box', rx=10)
            svg.text(bx + 12, 28, title, cls='t-strong', size=12.5)
            svg.text(bx + 12, 45, detail, cls='t-muted', size=11)
            if sc:
                for j, (v, idx, nm) in enumerate([(sc[0], 1, 'seen'), (sc[1], 2, 'unseen')]):
                    yb = 62 + j * 18
                    svg.rect(bx + 12, yb, w - 24 - 34, 8, 'box-soft', rx=4)
                    svg.mark(f'{nm}: {v:.1f}%', f'<path class="bar s{idx}" d="{hbar(bx + 12, yb, bx + 12 + (w - 58) * v / 100, 8, 4)}"/>')
                    svg.text(bx + w - 12, yb + 8, f'{v:.1f}', cls='t-strong' if i == 2 else '', anchor='end', size=11)
            else:
                svg.text(bx + 12, 74, T('p = 0.006 vs GRPO (seen)', '对比 GRPO：p = 0.006（seen）'), cls='t-accent', size=11.5)
                svg.text(bx + 12, 92, T('per-task records', '逐任务记录'), cls='t-faint', size=11)
            if i:
                chevron(svg, bx - gap / 2, 6 + h / 2, 3.5)
        return svg
    h, gap = 76, 10
    H = 30 + 4 * h + 3 * gap
    svg = Svg(W, H, 'StepCredit-RL pipeline with ALFWorld success after each stage')
    chip_legend(svg, 8, 16, [('s1', 'seen'), ('s2', 'unseen')])
    for i, (title, detail, sc) in enumerate(stages):
        y = 26 + i * (h + gap)
        svg.rect(8, y, W - 16, h, 'box-key' if i == 2 else 'box', rx=10)
        svg.text(20, y + 21, title, cls='t-strong', size=12.5)
        svg.text(20, y + 38, detail, cls='t-muted', size=11)
        if sc:
            for j, (v, idx) in enumerate([(sc[0], 1), (sc[1], 2)]):
                yb = y + 48 + j * 12
                svg.rect(20, yb, W - 80, 7, 'box-soft', rx=3.5)
                svg.path(hbar(20, yb, 20 + (W - 80) * v / 100, 7, 3.5), f's{idx}')
                svg.text(W - 20, yb + 7, f'{v:.1f}', anchor='end', size=11, cls='t-strong' if i == 2 else '')
        else:
            svg.text(20, y + 60, T('p = 0.006 vs GRPO (seen)', '对比 GRPO：p = 0.006（seen）'), cls='t-accent', size=11.5)
    return svg


def scr_steplevel(W):
    """GRPO gives every step of a trajectory the same advantage; StepCredit-RL separates the steps taken from state B."""
    narrow = W < 500
    rollouts = [(['A', 'B', 'C', 'D'], 1), (['A', 'E', 'B', 'F'], -1), (['A', 'B', 'G'], 1)]
    step_credit = {(0, 1): 0.8, (1, 2): -0.9, (2, 1): 0.6}   # the step taken from B in each rollout
    panels = [(T('GRPO: one advantage per trajectory', 'GRPO：每条轨迹一个优势'), False),
              (T('StepCredit-RL: credit per step', 'StepCredit-RL：每一步各自的信用'), True)]
    if narrow:
        H, pw, ph = 380, W - 16, 160
        origins = [(8, 30), (8, 210)]
    else:
        H, pw, ph = 214, (W - 40) / 2, 168
        origins = [(12, 30), (12 + pw + 16, 30)]
    svg = Svg(W, H, 'Illustration: GRPO versus StepCredit-RL credit on three rollouts')
    for (title, stepwise), (ox, oy) in zip(panels, origins):
        svg.rect(ox, oy, pw, ph, 'box', rx=12)
        svg.text(ox + 14, oy + 22, title, cls='t-strong', size=12.5)
        for r, (states, outcome) in enumerate(rollouts):
            y = oy + 50 + r * 38
            svg.text(ox + 14, y + 4, f'#{r + 1}', cls='t-faint', size=11)
            for c, s in enumerate(states):
                x = ox + 44 + c * 50
                v = outcome * 0.55
                if stepwise:
                    v = step_credit.get((r, c), outcome * 0.25)
                cls = 's1' if v > 0 else 's2'
                op = min(1.0, 0.25 + abs(v))
                svg.rect(x - 18, y - 11, 36, 22, cls, rx=6, extra=f'opacity="{op:.2f}"')
                txt_cls = 't-on' if op > 0.6 else 't-strong'
                svg.text(x, y + 4.3, s, cls=txt_cls, anchor='middle', size=11.5)
            svg.text(ox + 44 + len(states) * 50 - 14, y + 4, T('success', '成功') if outcome > 0 else T('fail', '失败'), cls='t-muted', size=11)
    leg_y = H - 8
    chip_legend(svg, 14, leg_y, [('s1', T('positive advantage', '正优势')), ('s2', T('negative', '负优势'))])
    svg.text(W - 14, leg_y, T('illustration; darker = larger', '示意图；颜色越深，绝对值越大'), cls='t-faint', anchor='end', size=11)
    return svg


FAM_NAMES = {'look_at_obj_in_light': T('Look in light', '灯下查看'), 'pick_and_place': T('Pick & place', '拿取放置'),
             'pick_clean_then_place': T('Clean & place', '清洗后放置'), 'pick_cool_then_place': T('Cool & place', '冷却后放置'),
             'pick_heat_then_place': T('Heat & place', '加热后放置'), 'pick_two_obj_and_place': T('Two objects', '双物体')}


def scr_sft_rl(W):
    """Dumbbells by task family: SFT → SFT + 100 RL steps. The family the expert rarely solves gains most."""
    def frac(run_name, split):
        return {r['family']: 100 * int(r['solved']) / int(r['total']) for r in FAMILY if r['run'] == run_name and r['split'] == split}
    order = ['pick_two_obj_and_place', 'pick_clean_then_place', 'pick_heat_then_place', 'look_at_obj_in_light', 'pick_cool_then_place', 'pick_and_place']
    narrow = W < 500
    if narrow:
        H = 470
        panels = [('seen', (96, 54, W - 20, 222)), ('unseen', (96, 286, W - 20, 446))]
    else:
        H = 268
        panels = [('seen', (132, 54, W / 2 - 22, H - 36)), ('unseen', (W / 2 + 112, 54, W - 26, H - 36))]
    svg = Svg(W, H, 'ALFWorld success by task family: after SFT and after 100 RL steps')
    chip_legend(svg, 14, 18, [('s3', T('after SFT', 'SFT 后')), ('s1', T('after SFT + 100 RL steps', 'SFT + 100 步 RL 后'))])
    for split, box in panels:
        a, b = frac('sft', split), frac('sft_gigpo_step100', split)
        sx = scale(0, 100, box[0], box[2])
        svg.text(box[0], box[1] - 14, f'valid_{split}', cls='t-strong', size=12.5)
        for v in (0, 50, 100):
            svg.line(sx(v), box[1] - 4, sx(v), box[3] - 6, 'grid' if v else 'axis')
            svg.text(sx(v), box[3] + 10, str(v), cls='t-faint', anchor='middle', size=10.5)
        pitch = (box[3] - box[1]) / len(order)
        for i, fam in enumerate(order):
            y = box[1] + i * pitch + pitch / 2 - 4
            key = fam == 'pick_two_obj_and_place'
            svg.text(box[0] - 10, y + 4, FAM_NAMES[fam], cls='t-strong' if key else '', anchor='end', size=11.5)
            svg.line(sx(a[fam]), y, sx(b[fam]), y, 'line l1' if key else 'line l3', 'stroke-width="2.5"' + ('' if key else ' opacity=".7"'))
            svg.mark(f'{FAM_NAMES[fam][0]} {split}: SFT {a[fam]:.0f}% → RL {b[fam]:.0f}%',
                     f'<circle class="dot s3" cx="{sx(a[fam]):.1f}" cy="{y:.1f}" r="4.5"/><circle class="dot s1" cx="{sx(b[fam]):.1f}" cy="{y:.1f}" r="5"/>')
            if key:
                svg.text(sx(a[fam]) - 8, y + 4, f'{a[fam]:.0f}', cls='t-muted', anchor='end', size=11)
                svg.text(sx(b[fam]) + 8, y + 4, f'{b[fam]:.0f}', cls='t-strong', size=11) if b[fam] < 92 else None
    return svg


def _waffle(svg, x, y, counts, cols=14, cell=10, gap=2):
    """counts: [(css class, n, extra)] filled row by row."""
    k = 0
    for cls, n, extra in counts:
        for _ in range(n):
            r, c = divmod(k, cols)
            svg.rect(x + c * (cell + gap), y + r * (cell + gap), cell, cell, cls, rx=2.5, extra=extra)
            k += 1
    return math.ceil(k / cols) * (cell + gap)


def scr_vs_grpo(W):
    """Validation curves, plus who solved what at step 200 (the McNemar table as a waffle)."""
    narrow = W < 500
    g = {k: run(ALF, 'gigpo', k) for k in ('seen', 'unseen')}
    r = {k: run(ALF, 'grpo', k) for k in ('seen', 'unseen')}
    if narrow:
        H = 640
        boxes = {'seen': (40, 66, W - 52, 200), 'unseen': (40, 356, W - 52, 490)}
        waffle_y = {'seen': 222, 'unseen': 512}
    else:
        H = 420
        boxes = {'seen': (40, 66, W / 2 - 46, 236), 'unseen': (W / 2 + 46, 66, W - 52, 236)}
        waffle_y = {'seen': 286, 'unseen': 286}
    svg = Svg(W, H, 'StepCredit-RL vs GRPO: validation curves and per-task outcomes at step 200')
    legend(svg, 40, 16, [(1, 'StepCredit-RL'), (2, 'GRPO')])
    for name, box in boxes.items():
        sx, sy = scale(0, 200, box[0], box[2]), scale(0, 100, box[3], box[1])
        svg.text(box[0], box[1] - 18, f'valid_{name}', cls='t-strong', size=12.5)
        y_axis(svg, box, sy, [0, 50, 100])
        x_axis(svg, box, sx, [0, 100, 200])
        for idx, pts in [(2, r[name]), (1, g[name])]:
            svg.path(polyline(pts, sx, sy), f'line l{idx}')
            svg.circle(sx(pts[-1][0]), sy(pts[-1][1]), 4, f'dot s{idx}')
        hit_points(svg, g[name], sx, sy, lambda x, y: f'StepCredit-RL · step {x}: {y:.1f}%', r=5)
        hit_points(svg, r[name], sx, sy, lambda x, y: f'GRPO · step {x}: {y:.1f}%', r=5)
        p = PAIRED[f'alfworld_steplevel_vs_grpo:valid_{name}']
        both, only_a, only_b, n = int(p['both_correct']), int(p['only_a']), int(p['only_b']), int(p['items'])
        neither = n - both - only_a - only_b
        wy = waffle_y[name]
        svg.text(box[0], wy - 10, T(f'Step 200, {n} tasks', f'第 200 步，{n} 个任务'), cls='t-strong', size=12)
        pv = float(p['p'])
        svg.text(box[2], wy - 10, f'McNemar p = {pv:.3f}' if pv < 0.1 else f'McNemar p = {pv:.2f}', cls='t-accent' if pv < 0.05 else 't-muted', anchor='end', size=11.5)
        cols = 20 if not narrow else 24
        hgt = _waffle(svg, box[0], wy, [('s1', only_a, ''), ('s2', only_b, ''), ('s3', both, 'opacity=".45"'), ('box', neither, '')], cols=cols, cell=9 if narrow else 10)
        ly = wy + hgt + 14
        chip_legend(svg, box[0], ly, [('s1', T(f'only StepCredit-RL {only_a}', f'仅 StepCredit-RL {only_a}')), ('s2', T(f'only GRPO {only_b}', f'仅 GRPO {only_b}'))], size=11, gap=12)
        chip_legend(svg, box[0], ly + 16, [('s3', T(f'both {both}', f'都解出 {both}')), ('box', T(f'neither {neither}', f'都没解出 {neither}'))], size=11, gap=12)
    return svg


def scr_updates(W):
    """The same comparison by step and by wall-clock hours."""
    narrow = W < 500
    four = [(int(r_['step']), float(r_['seen']), float(r_['hours'])) for r_ in ALF if r_['run'] == 'gigpo_4upd']
    one = [(int(r_['step']), float(r_['seen']), float(r_['hours'])) for r_ in ALF if r_['run'] == 'gigpo' and int(r_['step']) <= 150]
    if narrow:
        H = 500
        bA, bB = (40, 66, W - 70, 222), (40, 314, W - 70, 470)
    else:
        H = 300
        bA, bB = (40, 66, W / 2 - 56, H - 40), (W / 2 + 44, 66, W - 70, H - 40)
    svg = Svg(W, H, 'Seen success with one vs four updates per step, by step and by wall-clock hours')
    legend(svg, 40, 16, [(1, T('4 updates / step', '每步 4 次更新')), (2, T('1 update / step', '每步 1 次更新'))])
    for box, key, xmax, ticks, title, unit in [(bA, 0, 150, [0, 50, 100, 150], T('by training step', '按训练步'), T('step', '步')),
                                               (bB, 2, 30, [0, 10, 20, 30], T('by wall-clock hours', '按耗时'), T('hours', '小时'))]:
        sx, sy = scale(0, xmax, box[0], box[2]), scale(0, 100, box[3], box[1])
        svg.text(box[0], box[1] - 18, title, cls='t-strong', size=12.5)
        y_axis(svg, box, sy, [0, 25, 50, 75, 100])
        x_axis(svg, box, sx, ticks, title=unit)
        for idx, data in [(2, one), (1, four)]:
            pts = [(d[key], d[1]) for d in data]
            svg.path(polyline(pts, sx, sy), f'line l{idx}')
            svg.circle(sx(pts[-1][0]), sy(pts[-1][1]), 4, f'dot s{idx}')
            hit_points(svg, pts, sx, sy, lambda x, y, k=key: (f'{x:.0f} steps' if k == 0 else f'{x:.1f} h') + f': {y:.1f}%', r=5)
        end_labels(svg, [(sx(four[-1][key]) + 8, sy(four[-1][1]), f'{four[-1][1]:.1f}', 't-strong'), (sx(one[-1][key]) + 8, sy(one[-1][1]), f'{one[-1][1]:.1f}', '')])
        if key == 2:
            svg.text(sx(four[-1][2]), sy(four[-1][1]) - 14, f'{four[-1][2]:.1f} h', cls='t-faint', anchor='middle', size=11)
            svg.text(sx(one[-1][2]), sy(one[-1][1]) - 14, f'{one[-1][2]:.1f} h', cls='t-faint', anchor='middle', size=11)
    return svg


def scr_hotpotqa(W):
    """Connected scatter: the shaped reward moves left (fewer repeated queries) but not up (exact match)."""
    narrow = W < 500
    em = [(float(r_['repeat_queries']), float(r_['em']), int(r_['step'])) for r_ in HPQ if r_['run'] == 'em']
    sh = [(float(r_['repeat_queries']), float(r_['em']), int(r_['step'])) for r_ in HPQ if r_['run'] == 'shaped']
    H = 330
    box = (48, 40, W - (24 if narrow else 160), H - 44)
    svg = Svg(W, H, 'HotpotQA training paths: repeated queries per question against exact match')
    legend(svg, 48, 16, [(1, T('EM reward', 'EM 奖励')), (2, T('shaped reward', '稠密奖励'))])
    sx, sy = scale(0, 0.2, box[0], box[2]), scale(44, 56, box[3], box[1])
    y_axis(svg, box, sy, [44, 48, 52, 56])
    x_axis(svg, box, sx, [0, 0.05, 0.1, 0.15, 0.2], fmt=lambda v: f'{v:.2f}' if v else '0')
    svg.text(box[2], box[3] + 32, T('repeated queries per question', '每题重复查询次数'), cls='t-faint', anchor='end', size=11)
    svg.text(box[0] - 40, box[1] - 14, T('exact match, %', 'EM，%'), cls='t-faint', size=11)
    for idx, data in [(2, sh), (1, em)]:
        pts = [(x, y) for x, y, _ in data]
        svg.path(polyline(pts, sx, sy), f'line l{idx} thin', 'opacity=".9"')
        for x, y, s in data:
            svg.mark(f'step {s}: EM {y:.1f}%, repeats {x:.3f}', f'<circle class="dot s{idx}" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="{4.5 if s in (0, 200) else 3}"/>')
        x0, y0, _ = data[0]
        x1, y1, _ = data[-1]
        svg.text(sx(x0) + 7, sy(y0) + 15, T('step 0', '第 0 步'), cls='t-faint', size=11)
        svg.text(sx(x1) + (8 if idx == 1 else -8), sy(y1) - 8, T(f'step 200: {y1:.1f}', f'第 200 步：{y1:.1f}'), cls='t-strong' if idx == 1 else '', anchor='start' if idx == 1 else 'end', size=11.5)
    if not narrow:
        svg.text(box[2] + 16, box[1] + 30, T('Shaped reward:', '稠密奖励：'), cls='t-strong', size=12)
        svg.text(box[2] + 16, box[1] + 48, T('repeats −71%', '重复查询 −71%'), size=12)
        svg.text(box[2] + 16, box[1] + 66, T('EM not higher', 'EM 没有提高'), size=12)
        svg.text(box[2] + 16, box[1] + 84, '(p = 0.16)', cls='t-faint', size=11.5)
    return svg


FIGS = {
    'card-opd': card_opd, 'card-scr': card_scr,
    'opd-pipeline': opd_pipeline, 'opd-takeover': opd_takeover, 'opd-methods': opd_methods,
    'opd-budget': opd_budget, 'opd-training': opd_training,
    'scr-pipeline': scr_pipeline, 'scr-steplevel': scr_steplevel, 'scr-sft-rl': scr_sft_rl,
    'scr-vs-grpo': scr_vs_grpo, 'scr-updates': scr_updates, 'scr-hotpotqa': scr_hotpotqa,
}
