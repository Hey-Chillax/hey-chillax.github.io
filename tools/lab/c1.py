"""Chart round 1 (2026-11-17).

BASE   = the finals that were live before this cycle (opd-compute: the 11-15 drawing the user preferred).
AES    = polish only: one type scale, ink-coloured text, colour on the marks, no redundant guides.
INNO   = a new idea per chart (restructuring allowed).
MERGED = what goes on to round 2 (see NOTES for the reasons).
"""
import math

from c_kit import (ALF, CHARTS, FAM_NAMES, FAM_ORDER, FS_LABEL, FS_TICK, FS_TITLE, HPQ, OPD, PAIRED, Svg, T, dots,
                   family_counts, frame, hbar, hits, key_chips, key_lines, label_stack, moving_avg, panel_title, path_line,
                   per_lang, pick, polyline, run, scale, signed, text_w, wash_between)
import figures as F

BASE = {name: F.FIGS[name][0] for name in CHARTS}


# ============================================================================ opd-methods
def _method_rows():
    d = OPD['eval_avg4']
    return [(T('Base (Qwen3-1.7B)', '基座（Qwen3-1.7B）'), d['base'], 's3', 'ref'),
            (T('GRPO, 60 steps', 'GRPO，60 步'), d['grpo_60'], 's3', 'ref'),
            (T('SFT, 1 epoch', 'SFT，1 轮'), d['sft'], 's3', 'ref'),
            (T('OPD, 40 steps', 'OPD，40 步'), d['opd_40'], 's2', 'opd'),
            (T('Scaffold-OPD, 40 steps', 'Scaffold-OPD，40 步'), d['takeover_conclude_40'], 's1', 'ours'),
            (T('without the concluding trigger', '关闭收尾触发'), d['takeover_40'], 'pn-blue', 'variant')]


# per-benchmark scores (the table on the project page): MATH-500, AIME24, AIME25, AIME26
BENCH = {'ref0': [72.55, 11.67, 9.06, 8.23], 'ref1': [78.05, 20.83, 13.54, 11.46], 'ref2': [83.35, 27.92, 23.12, 17.50],
         'opd': [86.05, 31.88, 24.79, 20.21], 'ours': [87.75, 39.38, 31.67, 28.75], 'variant': [87.80, 40.83, 28.96, 28.12]}


def methods_aes(W):
    """Same bars, quieter: thinner bars, ink labels, the base line removed (the base is the first bar), a small gap
    between the baselines and the two distillation runs, and the +6.2 bracket kept as the one coloured number."""
    rows = _method_rows()
    narrow = W < 500
    pitch, bh = (44, 12) if narrow else (32, 12)
    x0, x1 = (12, W - 46) if narrow else (206, W - 104)
    top = 10 if not narrow else 8
    ys = []
    y = top
    for i in range(len(rows)):
        if i == 3:
            y += 10
        ys.append(y + (20 if narrow else 0))
        y += pitch
    y_end = y - (pitch - bh) + (20 if narrow else 0) + 8
    H = y_end + 42
    svg = Svg(W, H, '4-benchmark math average by post-training method')
    sx = scale(0, 50, x0, x1)
    frame(svg, (x0, top - 4, x1, y_end), sx, None, [0, 10, 20, 30, 40, 50], [], grid='x',
          xtitle=T('4-benchmark average (MATH-500, AIME 2024–26)', '4 项平均分（MATH-500、AIME 2024–26）'))
    for (lab, v, cls, kind), yb in zip(rows, ys):
        strong = kind == 'ours'
        if kind == 'variant':
            lab = T('↳ ' + lab[0], '↳ ' + lab[1])
        tcls = 't-strong' if strong else ('t-muted' if kind == 'variant' else '')
        if narrow:
            svg.text(x0 + (12 if kind == 'variant' else 0), yb - 6, lab, cls=tcls, size=FS_LABEL)
        else:
            svg.text(x0 - 12, yb + bh / 2 + 4.2, lab, cls=tcls, anchor='end', size=FS_LABEL)
        d = hbar(x0, yb, sx(v), bh, 3) if kind != 'variant' else hbar(x0, yb + 0.6, sx(v) - 0.6, bh - 1.2, 3)
        svg.mark(f'{lab[0]}: {v:.2f}', f'<path class="{"bar " if kind != "variant" else ""}{cls}" d="{d}"/>')
        svg.text(sx(v) + 6, yb + bh / 2 + 4.2, f'{v:.1f}', cls='t-strong' if strong else '', size=FS_LABEL)
    d = OPD['eval_avg4']
    xb = sx(d['takeover_conclude_40']) + (34 if narrow else 40)
    yo, yt = ys[3] + bh / 2, ys[4] + bh / 2
    svg.path(f'M{xb - 5:.1f},{yo:.1f} H{xb:.1f} V{yt:.1f} H{xb - 5:.1f}', 'leader')
    svg.text(xb + 5, (yo + yt) / 2 + 4.3, signed(d['takeover_conclude_40'] - d['opd_40']), cls='tx-blue', size=FS_LABEL, weight=700)
    return svg


def methods_inno(W):
    """A dot plot with a second mark per method: the AIME-only average (the three harder benchmarks), computed from the
    table on the page. The four-benchmark average is the filled dot; the AIME average shows where the gain comes from."""
    rows = _method_rows()
    keys = ['ref0', 'ref1', 'ref2', 'opd', 'ours', 'variant']
    narrow = W < 500
    pitch = 44 if narrow else 30
    x0, x1 = (12, W - 40) if narrow else (206, W - 120)
    top = 34
    ys = []
    y = top
    for i in range(len(rows)):
        if i == 3:
            y += 10
        ys.append(y + (18 if narrow else 0))
        y += pitch
    y_end = y - pitch + (18 if narrow else 0) + 16
    H = y_end + 42
    svg = Svg(W, H, 'Four-benchmark average and AIME-only average by post-training method')
    def legend(i):
        xx = x0 if not narrow else 12
        svg.circle(xx + 5, 14, 4.5, 'dot s1')
        s = pick(T('four-benchmark average', '4 项平均'), i)
        svg.text(xx + 15, 18, s, size=FS_LABEL)
        xx += 15 + text_w(s, FS_LABEL) + 18
        svg.add(f'<circle cx="{xx + 5:.1f}" cy="14" r="4" class="l1" fill="var(--bg)" stroke-width="1.8"/>')
        svg.text(xx + 15, 18, pick(T('AIME 2024–26 average', 'AIME 2024–26 平均'), i), size=FS_LABEL)
    per_lang(svg, legend)
    sx = scale(0, 50, x0, x1)
    frame(svg, (x0, top - 6, x1, y_end), sx, None, [0, 10, 20, 30, 40, 50], [], grid='x',
          xtitle=T('score', '分数'))
    for (lab, v, cls, kind), yb, k in zip(rows, ys, keys):
        b = BENCH[k]
        aime = sum(b[1:]) / 3
        strong = kind == 'ours'
        if kind == 'variant':
            lab = T('↳ ' + lab[0], '↳ ' + lab[1])
        tcls = 't-strong' if strong else ('t-muted' if kind == 'variant' else '')
        if narrow:
            svg.text(x0 + (12 if kind == 'variant' else 0), yb - 10, lab, cls=tcls, size=FS_LABEL)
        else:
            svg.text(x0 - 12, yb + 4.2, lab, cls=tcls, anchor='end', size=FS_LABEL)
        idx = {'s3': 3, 's2': 2, 's1': 1, 'pn-blue': 1}[cls]
        svg.line(sx(aime), yb, sx(v), yb, f'line l{idx}', 'stroke-width="1.4" opacity=".5"')
        svg.mark(f'{lab[0]}: AIME average {aime:.1f}', f'<circle cx="{sx(aime):.1f}" cy="{yb:.1f}" r="4" class="l{idx}" fill="var(--bg)" stroke-width="1.8"/>')
        svg.mark(f'{lab[0]}: four-benchmark average {v:.2f}', f'<circle class="dot s{idx}" cx="{sx(v):.1f}" cy="{yb:.1f}" r="5"{" opacity=.55" if kind == "variant" else ""}/>')
        svg.text(sx(v) + 9, yb + 4.2, f'{v:.1f}', cls='t-strong' if strong else '', size=FS_LABEL)
        svg.text(sx(aime) - 8, yb + 4.2, f'{aime:.1f}', cls='t-faint', anchor='end', size=FS_TICK)
    d = OPD['eval_avg4']
    xb = sx(d['takeover_conclude_40']) + (40 if narrow else 44)
    yo, yt = ys[3], ys[4]
    svg.path(f'M{xb - 5:.1f},{yo:.1f} H{xb:.1f} V{yt:.1f} H{xb - 5:.1f}', 'leader')
    svg.text(xb + 5, (yo + yt) / 2 + 4.3, signed(d['takeover_conclude_40'] - d['opd_40']), cls='tx-blue', size=FS_LABEL, weight=700)
    return svg


# ============================================================================ opd-budget
LOG = math.log2
KT = [10, 11, 12, 13, 14, 15]
kfmt = lambda v: f'{2 ** v // 1024:.0f}k'
DOUBLINGS = {1024, 2048, 4096, 8192, 16384, 32768}


def _budget():
    b = OPD['budget']
    xs = [LOG(t) for t in b['tokens']]
    return b, xs


def _band(svg, sx, box, a=14, z=15):
    svg.rect(sx(a), box[1], sx(z) - sx(a), box[3] - box[1], 'band')


def _budget_panel_a(svg, box, sx, b, xs, labels=True, note=True, narrow=False):
    sy = scale(0, 50, box[3], box[1])
    _band(svg, sx, box)
    frame(svg, box, sx, sy, KT, [0, 10, 20, 30, 40, 50], kfmt, str)
    wash_between(svg, xs, b['takeover_40'], b['opd_40'], sx, sy)
    for idx, key in ((2, 'opd_40'), (1, 'takeover_40')):
        pts = list(zip(xs, b[key]))
        path_line(svg, pts, sx, sy, idx)
        dots(svg, [(x, y) for x, y, t in zip(xs, b[key], b['tokens']) if t in DOUBLINGS], sx, sy, idx, r=3)
    if labels:
        label_stack(svg, box[2] + 8, [(sy(b['takeover_40'][-1]), T(f'Scaffold-OPD {b["takeover_40"][-1]:.1f}'), 't-strong'),
                                     (sy(b['opd_40'][-1]), T(f'OPD {b["opd_40"][-1]:.1f}'), '')], min_gap=15)
    if note and not narrow:
        svg.text(sx(14) - 8, sy(47.5), T('16k → 32k: OPD stops rising, Scaffold-OPD keeps reasoning', '16k → 32k：OPD 不再提升，Scaffold-OPD 还在推理'),
                 cls='t-muted', anchor='end', size=FS_TICK)
    return sy


def _budget_panel_b(svg, box, sx, b, xs, band=True, xlabels=True):
    sy = scale(-5, 8, box[3], box[1])
    if band:
        _band(svg, sx, box)
    frame(svg, box, sx, sy, KT if xlabels else [], [-4, 0, 4, 8], kfmt, lambda v: signed(v, 0) if v else '0')
    if not xlabels:
        pass
    svg.line(box[0], sy(0), box[2], sy(0), 'axis', 'stroke-dasharray="3 3"')
    up = [(x, g + s) for x, g, s in zip(xs, b['gap_40'], b['gap_se_40'])]
    lo = [(x, g - s) for x, g, s in zip(xs, b['gap_40'], b['gap_se_40'])]
    svg.path(polyline(up, sx, sy) + ' L' + polyline(list(reversed(lo)), sx, sy)[1:] + ' Z', 'wash1')
    pts = list(zip(xs, b['gap_40']))
    path_line(svg, pts, sx, sy, 1)
    for t_ in (8192, 16384, 32768):
        k = b['tokens'].index(t_)
        x, g = xs[k], b['gap_40'][k]
        svg.circle(sx(x), sy(g), 3, 'dot s1', 'stroke-width="1.5"')
        svg.text(sx(x) - (4 if t_ == 32768 else 0), sy(g) - 9, signed(g), cls='t-strong', anchor='end' if t_ == 32768 else 'middle', size=FS_TICK)
    return sy


def _budget_panel_c(svg, box, sx, b, xs, band=True, labels=True):
    sy = scale(0, 100, box[3], box[1])
    if band:
        _band(svg, sx, box)
    frame(svg, box, sx, sy, KT, [0, 50, 100], kfmt, str)
    for idx, key in ((2, 'aime_finished_opd_40'), (1, 'aime_finished_takeover_40')):
        path_line(svg, list(zip(xs, b[key])), sx, sy, idx)
    k = b['tokens'].index(16384)
    for idx, key, dy, anchor in ((2, 'aime_finished_opd_40', -8, 'end'), (1, 'aime_finished_takeover_40', 14, 'start')):
        v = b[key][k]
        svg.circle(sx(xs[k]), sy(v), 3, f'dot s{idx}', 'stroke-width="1.5"')
        svg.text(sx(xs[k]) + (-6 if anchor == 'end' else 6), sy(v) + dy, f'{v:.0f}%', cls='t-strong', anchor=anchor, size=FS_TICK)
    if labels:
        label_stack(svg, box[2] + 8, [(sy(b['aime_finished_opd_40'][-1]), 'OPD', ''),
                                     (sy(b['aime_finished_takeover_40'][-1]), 'Scaffold-OPD', '')], min_gap=14, size=FS_TICK)
    return sy


def budget_aes(W):
    """The three panels kept; the top legend replaced by labels at the line ends, the 16k–32k band drawn in every panel,
    and the numbers written in ink."""
    b, xs = _budget()
    narrow = W < 500
    if narrow:
        H = 760
        A, B_, C = (44, 58, W - 96, 230), (44, 330, W - 70, 460), (44, 560, W - 96, 690)
    else:
        H = 480
        A, B_, C = (52, 40, W - 150, 214), (52, 318, W / 2 - 46, 420), (W / 2 + 60, 318, W - 150, 420)
    svg = Svg(W, H, 'Accuracy against the evaluation token budget, the paired gap, and the share of AIME answers finished')
    sx_a = scale(10, 15, A[0], A[2])
    panel_title(svg, A[0], A[1] - 18, 'a', T('Accuracy', '准确率'), T('4-benchmark average', '4 项平均'))
    _budget_panel_a(svg, A, sx_a, b, xs, narrow=narrow)
    sx_b = scale(10, 15, B_[0], B_[2])
    panel_title(svg, B_[0], B_[1] - 18, 'b', T('Paired gap', '配对差'), T('Scaffold-OPD − OPD, ±1 SE', 'Scaffold-OPD − OPD，±1 标准误'))
    _budget_panel_b(svg, B_, sx_b, b, xs)
    sx_c = scale(10, 15, C[0], C[2])
    panel_title(svg, C[0], C[1] - 18, 'c', T('AIME answers finished', '写完的 AIME 回答'), '%')
    _budget_panel_c(svg, C, sx_c, b, xs)
    if not narrow:
        svg.text(W / 2, H - 6, T('evaluation budget, tokens (log scale)', '评测预算，token（对数刻度）'), cls='t-muted', anchor='middle', size=FS_TICK)
    return svg


def budget_inno(W, merged=False):
    """The three measures stacked on one shared x-axis, so the 16k column reads straight down: OPD has finished 93% of
    its AIME answers there and stops gaining, while the paired gap keeps growing."""
    b, xs = _budget()
    narrow = W < 500
    short = merged and narrow
    x0, x1 = (44, W - 92) if narrow else (64, W - 150)
    hA, hB, hC, gap = (160, 74, 74, 34) if not narrow else (150, 74, 74, 38)
    yA = 30 if not short else 56
    if short:
        x1 = W - 52
    A = (x0, yA, x1, yA + hA)
    B_ = (x0, A[3] + gap, x1, A[3] + gap + hB)
    C = (x0, B_[3] + gap, x1, B_[3] + gap + hC)
    H = C[3] + 46
    svg = Svg(W, H, 'Accuracy, paired gap and finished AIME answers against the evaluation token budget, on a shared axis')
    sx = scale(10, 15, x0, x1)
    if short:
        key_lines(svg, x0, 18, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    svg.rect(sx(14), A[1] - 6, sx(15) - sx(14), C[3] - A[1] + 6, 'band')
    if not narrow:
        svg.text(sx(14.5), A[1] - 12, T('16k → 32k', '16k → 32k'), cls='t-faint', anchor='middle', size=FS_TICK)
    syA = scale(0, 50, A[3], A[1])
    frame(svg, A, sx, syA, [], [0, 25, 50], kfmt, str)
    wash_between(svg, xs, b['takeover_40'], b['opd_40'], sx, syA)
    for idx, key in ((2, 'opd_40'), (1, 'takeover_40')):
        path_line(svg, list(zip(xs, b[key])), sx, syA, idx)
        dots(svg, [(x, y) for x, y, t in zip(xs, b[key], b['tokens']) if t in DOUBLINGS], sx, syA, idx, r=3)
    if short:
        label_stack(svg, x1 + 8, [(syA(b['takeover_40'][-1]), f'{b["takeover_40"][-1]:.1f}', 't-strong'),
                                  (syA(b['opd_40'][-1]), f'{b["opd_40"][-1]:.1f}', '')], min_gap=15)
    else:
        label_stack(svg, x1 + 8, [(syA(b['takeover_40'][-1]), f'Scaffold-OPD {b["takeover_40"][-1]:.1f}', 't-strong'),
                                  (syA(b['opd_40'][-1]), f'OPD {b["opd_40"][-1]:.1f}', '')], min_gap=15)
    panel_title(svg, x0, A[1] - 12 if narrow else A[1] - 12, 'a', T('Accuracy', '准确率'), T('4-benchmark average', '4 项平均'))
    syB = scale(-5, 8, B_[3], B_[1])
    frame(svg, B_, sx, syB, [], [-4, 0, 4, 8], kfmt, lambda v: signed(v, 0) if v else '0')
    up = [(x, g + s) for x, g, s in zip(xs, b['gap_40'], b['gap_se_40'])]
    lo = [(x, g - s) for x, g, s in zip(xs, b['gap_40'], b['gap_se_40'])]
    svg.path(polyline(up, sx, syB) + ' L' + polyline(list(reversed(lo)), sx, syB)[1:] + ' Z', 'wash1')
    svg.line(x0, syB(0), x1, syB(0), 'axis', 'stroke-dasharray="3 3"')
    path_line(svg, list(zip(xs, b['gap_40'])), sx, syB, 1)
    for t_ in (8192, 16384, 32768):
        k = b['tokens'].index(t_)
        svg.circle(sx(xs[k]), syB(b['gap_40'][k]), 3, 'dot s1', 'stroke-width="1.5"')
    k32 = b['tokens'].index(32768)
    svg.text(x1 + 8, syB(b['gap_40'][k32]) + 4, signed(b['gap_40'][k32]), cls='t-strong', size=FS_LABEL)
    panel_title(svg, x0, B_[1] - 12, 'b', T('Paired gap', '配对差'), T('Scaffold-OPD − OPD, ±1 SE', 'Scaffold-OPD − OPD，±1 标准误'))
    syC = scale(0, 100, C[3], C[1])
    frame(svg, C, sx, syC, KT, [0, 50, 100], kfmt, str)
    for idx, key in ((2, 'aime_finished_opd_40'), (1, 'aime_finished_takeover_40')):
        path_line(svg, list(zip(xs, b[key])), sx, syC, idx)
    k16 = b['tokens'].index(16384)
    for idx, key in ((2, 'aime_finished_opd_40'), (1, 'aime_finished_takeover_40')):
        svg.circle(sx(xs[k16]), syC(b[key][k16]), 3, f'dot s{idx}', 'stroke-width="1.5"')
    svg.text(sx(xs[k16]) - 6, syC(b['aime_finished_opd_40'][k16]) - 6, f'{b["aime_finished_opd_40"][k16]:.0f}%', cls='t-strong', anchor='end', size=FS_TICK)
    svg.text(sx(xs[k16]) + 6, syC(b['aime_finished_takeover_40'][k16]) + 12, f'{b["aime_finished_takeover_40"][k16]:.0f}%', cls='t-strong', size=FS_TICK)
    if not short:
        label_stack(svg, x1 + 8, [(syC(b['aime_finished_opd_40'][-1]), 'OPD', ''), (syC(b['aime_finished_takeover_40'][-1]), 'Scaffold-OPD', '')], min_gap=14, size=FS_TICK)
    panel_title(svg, x0, C[1] - 12, 'c', T('AIME answers finished', '写完的 AIME 回答'), '%')
    svg.text((x0 + x1) / 2, C[3] + 34, T('evaluation budget, tokens (log scale)', '评测预算，token（对数刻度）'), cls='t-muted', anchor='middle', size=FS_TICK)
    return svg


# ============================================================================ opd-training
def _train():
    tr = OPD['train']
    t = tr['takeover']
    tk = moving_avg([(s, l) for s, l in zip(t['step'], t['response_length']) if s != 19])
    op = moving_avg(list(zip(tr['opd']['step'], tr['opd']['response_length'])))
    teach = moving_avg([(s, v) for s, v in zip(t['step'], t['teacher_tokens_per_answer']) if v is not None and s != 19])
    return t, tk, op, teach


def _window(t, a, z, key):
    vals = [v for s, v in zip(t['step'], t[key]) if a <= s <= z and v is not None and s != 19]
    return sum(vals) / len(vals)


def _length_panel(svg, box, tk, op, ends=True):
    sx, sy = scale(0, 60, box[0], box[2]), scale(0, 6000, box[3], box[1])
    frame(svg, box, sx, sy, [0, 20, 40, 60], [0, 2000, 4000, 6000], str, lambda v: f'{v / 1000:.0f}k' if v else '0',
          xtitle=T('training step', '训练步'))
    path_line(svg, op, sx, sy, 2)
    path_line(svg, tk, sx, sy, 1)
    for idx, pts in ((2, op), (1, tk)):
        svg.circle(sx(pts[-1][0]), sy(pts[-1][1]), 3.2, f'dot s{idx}', 'stroke-width="1.5"')
    hits(svg, op, sx, sy, lambda x, y: f'OPD · step {x}: {y:,.0f} tokens')
    hits(svg, tk, sx, sy, lambda x, y: f'Scaffold-OPD · step {x}: {y:,.0f} tokens')
    if ends:
        label_stack(svg, box[2] + 8, [(sy(tk[-1][1]), f'{tk[-1][1]:,.0f}', 't-strong'), (sy(op[-1][1]), f'{op[-1][1]:,.0f}', '')])
    return sx, sy


def training_aes(W):
    """Panel (b) quieter: a thin teacher line over a pale area, the shares written in ink with the step range they
    average, and both panels on the same type scale."""
    t, tk, op, teach = _train()
    narrow = W < 500
    if narrow:
        H = 520
        bA, bB = (48, 62, W - 70, 222), (48, 320, W - 70, 470)
    else:
        H = 300
        bA, bB = (56, 62, W / 2 - 74, H - 52), (W / 2 + 54, 62, W - 64, H - 52)
    svg = Svg(W, H, 'Response length, and the teacher-written tokens per answer in Scaffold-OPD')
    key_lines(svg, bA[0], 18, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    panel_title(svg, bA[0], bA[1] - 16, 'a', T('Response length', '回答长度'), T('tokens', 'token'))
    _length_panel(svg, bA, tk, op)
    panel_title(svg, bB[0], bB[1] - 16, 'b', T('Teacher tokens per answer', '每条回答的老师 token'), 'Scaffold-OPD')
    sx, sy = scale(0, 60, bB[0], bB[2]), scale(0, 200, bB[3], bB[1])
    frame(svg, bB, sx, sy, [0, 20, 40, 60], [0, 50, 100, 150, 200], xtitle=T('training step', '训练步'))
    area = polyline(teach, sx, sy) + f' L{sx(teach[-1][0]):.1f},{sy(0):.1f} L{sx(teach[0][0]):.1f},{sy(0):.1f} Z'
    svg.path(area, 'fl-green', 'opacity=".7"')
    path_line(svg, teach, sx, sy, 5)
    svg.circle(sx(teach[-1][0]), sy(teach[-1][1]), 3.2, 'dot s5', 'stroke-width="1.5"')
    hits(svg, teach, sx, sy, lambda x, y: f'step {x}: {y:.0f} teacher tokens per answer')
    s0 = 100 * _window(t, 1, 5, 'teacher_token_ratio')
    s1 = 100 * _window(t, 56, 60, 'teacher_token_ratio')
    svg.text(sx(1), sy(teach[0][1]) - 12, T(f'{s0:.0f}% of the tokens', f'占全部 token {s0:.0f}%'), size=FS_TICK)
    svg.text(sx(60), sy(teach[-1][1]) - 14, T(f'{s1:.0f}% of the tokens', f'占全部 token {s1:.0f}%'), anchor='end', size=FS_TICK)
    if not narrow:
        svg.text(bB[2] + 8, sy(teach[-1][1]) + 4, f'{teach[-1][1]:.0f}', cls='t-strong', size=FS_LABEL)
    return svg


def training_inno(W):
    """(b) becomes the anatomy of an answer at three points of training: each bar is the average Scaffold-OPD answer,
    split into the tokens the student wrote and the tokens the teacher wrote. The teacher part stays about the same
    while the answer triples."""
    t, tk, op, teach = _train()
    narrow = W < 500
    if narrow:
        H = 500
        bA, bB = (48, 62, W - 70, 222), (16, 318, W - 16, 470)
    else:
        H = 300
        bA, bB = (56, 62, W / 2 - 74, H - 52), (W / 2 + 40, 62, W - 24, H - 60)
    svg = Svg(W, H, 'Response length, and the average Scaffold-OPD answer split into student and teacher tokens at three points of training')
    key_lines(svg, bA[0], 18, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    panel_title(svg, bA[0], bA[1] - 16, 'a', T('Response length', '回答长度'), T('tokens', 'token'))
    _length_panel(svg, bA, tk, op)
    panel_title(svg, bB[0], bB[1] - 16, 'b', T('Who writes a Scaffold-OPD answer', 'Scaffold-OPD 回答由谁写'), T('average tokens', '平均 token'))
    wins = [(T('steps 1–5', '第 1–5 步'), 1, 5), (T('steps 28–32', '第 28–32 步'), 28, 32), (T('steps 56–60', '第 56–60 步'), 56, 60)]
    lab_w = 0 if narrow else 78
    x0, x1 = bB[0] + lab_w, bB[2] - 70
    sx = scale(0, 4000, x0, x1)
    pitch = (bB[3] - bB[1]) / 3
    for k, (lab, a, z) in enumerate(wins):
        L = _window(t, a, z, 'response_length')
        Tt = _window(t, a, z, 'teacher_tokens_per_answer')
        y = bB[1] + k * pitch + (18 if narrow else 10)
        h = 16
        if narrow:
            svg.text(x0, y - 6, lab, cls='t-muted', size=FS_TICK)
        else:
            svg.text(x0 - 10, y + h / 2 + 4, lab, cls='t-muted', anchor='end', size=FS_TICK)
        svg.mark(f'{lab[0]}: {L - Tt:,.0f} student tokens', f'<rect x="{x0:.1f}" y="{y:.1f}" width="{sx(L - Tt) - x0:.1f}" height="{h}" rx="3" class="fl-blue"/>')
        svg.mark(f'{lab[0]}: {Tt:,.0f} teacher tokens', f'<rect x="{sx(L - Tt) + 1:.1f}" y="{y:.1f}" width="{max(sx(L) - sx(L - Tt) - 1, 1.5):.1f}" height="{h}" rx="2" class="s5"/>')
        svg.text(sx(L) + 8, y + h / 2 + 4, T(f'{L:,.0f} · teacher {100 * Tt / L:.0f}%', f'{L:,.0f} · 老师 {100 * Tt / L:.0f}%'), size=FS_TICK)
    yk = bB[3] + 18
    def keys(i):
        xx = x0
        for cls, s in (('fl-blue', pick(T('student', '学生'), i)), ('s5', pick(T('teacher', '老师'), i))):
            svg.rect(xx, yk - 9, 10, 10, cls, rx=2)
            svg.text(xx + 15, yk, s, size=FS_TICK)
            xx += 15 + text_w(s, FS_TICK) + 16
    per_lang(svg, keys)
    return svg


# ============================================================================ opd-compute
def _compute_data():
    g, p = OPD['gpu_hours']['pipeline'], OPD['pipeline_avg4']
    c1 = g['sft_incl_teacher_data']
    c2 = c1 + g['takeover_40']
    c3 = c2 + g['grpo_30']
    pts = [(0, p['base']), (c1, p['sft']), (c2, p['takeover_40']), (c3, p['grpo_30'])]
    alone = (OPD['gpu_hours']['takeover_40'], OPD['eval_avg4']['takeover_40'])
    return pts, alone


def compute_aes(W, slopes=False):
    """The 11-15 drawing kept (score against cumulative GPU-hours) and tidied: labels in ink next to each stage, a
    dimension line for the four-fold cost at the shared final score, and the axis titles on the axes."""
    pts, alone = _compute_data()
    narrow = W < 500
    H = 330 if not narrow else 360
    box = (46, 44, W - (28 if narrow else 120), H - 44)
    svg = Svg(W, H, 'Score against cumulative training GPU-hours: the full pipeline and Scaffold-OPD alone')
    key_lines(svg, box[0], 16, [(2, T('full pipeline', '全流程')), (1, T('Scaffold-OPD alone', '只做 Scaffold-OPD'))])
    sx, sy = scale(0, 56, box[0], box[2]), scale(20, 52, box[3], box[1])
    frame(svg, box, sx, sy, [0, 10, 20, 30, 40, 50], [20, 30, 40, 50], xtitle=T('cumulative training GPU-hours (2 × A100)', '累计训练卡时（2 × A100）'))
    svg.text(box[0] - 7, box[1] - 10, T('4-benchmark average', '4 项平均分'), cls='t-muted', size=FS_TICK)
    path_line(svg, pts, sx, sy, 2)
    path_line(svg, [pts[0], alone], sx, sy, 1)
    c3 = pts[-1][0]
    # dimension line at the shared final score
    yd = sy(50)
    for x in (alone[0], c3):
        svg.line(sx(x), yd + 4, sx(x), sy(max(alone[1], pts[-1][1])) - 8, 'leader', 'stroke-dasharray="2 3"')
    svg.line(sx(alone[0]), yd, sx(c3), yd, 'leader')
    for x, d in ((alone[0], 1), (c3, -1)):
        svg.path(f'M{sx(x):.1f},{yd:.1f} l{5 * d},-3.5 v7 Z', 'arrow-head')
    svg.text((sx(alone[0]) + sx(c3)) / 2, yd - 7, T(f'same score, ≈ {c3 / alone[0]:.0f}× the GPU-hours', f'分数相同，卡时约 {c3 / alone[0]:.0f} 倍'),
             cls='t-strong', anchor='middle', size=FS_LABEL)
    names = [T('base', '基座'), T('+ SFT'), T('+ Scaffold-OPD'), T('+ GRPO on failures', '+ 错题回流 GRPO')]
    for k, ((x, y), lab) in enumerate(zip(pts, names)):
        svg.mark(f'{lab[0]}: {y:.2f} after {x:.1f} GPU-hours', f'<circle class="dot s2" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4"/>')
        text = (f'{lab[0]} {y:.1f}', f'{lab[1]} {y:.1f}')
        if k == 0:
            svg.text(sx(x) + 8, sy(y) + 15, text, cls='t-muted', size=FS_TICK)
        elif k == 3:
            svg.text(sx(x) + (-8 if narrow else 8), sy(y) + 16, text, anchor='end' if narrow else 'start', size=FS_TICK)
        else:
            svg.text(sx(x) + 8, sy(y) + 16, text, size=FS_TICK)
    svg.mark(f'Scaffold-OPD alone: {alone[1]:.2f} after {alone[0]:.1f} GPU-hours',
             f'<circle class="dot s1" cx="{sx(alone[0]):.1f}" cy="{sy(alone[1]):.1f}" r="4.5"/>')
    svg.text(sx(alone[0]) + 9, sy(alone[1]) + 16, T(f'Scaffold-OPD alone {alone[1]:.1f}', f'只做 Scaffold-OPD {alone[1]:.1f}'),
             cls='t-strong', size=FS_TICK)
    if slopes:
        segs = [(pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[3])]
        for (xa, ya), (xb, yb) in segs + [((0, pts[0][1]), alone)]:
            r = (yb - ya) / (xb - xa)
            mx, my = (sx(xa) + sx(xb)) / 2, (sy(ya) + sy(yb)) / 2
            ang = math.degrees(math.atan2(sy(yb) - sy(ya), sx(xb) - sx(xa)))
            svg.text(mx, my - 7, T(f'{r:.2f} pt/h', f'{r:.2f} 分/卡时'), cls='t-muted', anchor='middle', size=FS_TICK,
                     extra=f'transform="rotate({ang:.1f} {mx:.1f} {my:.1f})"')
    return svg


def compute_inno(W):
    """As the aesthetic version, plus the slope of every segment written along it (points gained per GPU-hour): the
    pipeline's returns shrink stage by stage, while Scaffold-OPD alone gains about 1.6 points per GPU-hour."""
    return compute_aes(W, slopes=True)


# ============================================================================ scr-sft-rl
def _fam(split):
    a, b = family_counts('sft', split), family_counts('sft_gigpo_step100', split)
    gain = {f: 100 * (b[f][0] - a[f][0]) / a[f][1] for f in FAM_ORDER}
    order = sorted(FAM_ORDER, key=lambda f: -gain[f])
    return a, b, gain, order


def sft_rl_aes(W, bars=False, light=False):
    """Dumbbells kept, sorted by gain: the key row gets a faint band, gains in ink with the key one in blue, the task
    counts under the two-object rows, and plain split names."""
    narrow = W < 500
    if narrow:
        H = 510
        panels = [('seen', (100, 72, W - 56, 232)), ('unseen', (100, 318, W - 56, 478))]
    else:
        H = 296
        panels = [('seen', (128, 70, W / 2 - 56, H - 50)), ('unseen', (W / 2 + 96, 70, W - 52, H - 50))]
    svg = Svg(W, H, 'ALFWorld success by task family, after SFT and after 100 RL steps, sorted by the gain')
    if bars:
        def keys(i):
            xx = 16 if not narrow else 8
            for cls, s, op in (('s3', pick(T('after SFT', 'SFT 后'), i), ' opacity=".55"' if light else ''),
                               ('s1', pick(T('gain from 100 RL steps', '100 步 RL 的提升'), i), '')):
                svg.add(f'<rect x="{xx:.1f}" y="9" width="10" height="10" rx="2" class="{cls}"{op}/>')
                svg.text(xx + 15, 18, s, size=FS_LABEL)
                xx += 15 + text_w(s, FS_LABEL) + 18
        per_lang(svg, keys)
    else:
        def keys(i):
            xx = 16 if not narrow else 8
            for cls, s in (('s3', pick(T('after SFT', 'SFT 后'), i)), ('s1', pick(T('after SFT + 100 RL steps', 'SFT + 100 步 RL 后'), i))):
                svg.circle(xx + 5, 14, 4.5, f'dot {cls}')
                svg.text(xx + 15, 18, s, size=FS_LABEL)
                xx += 15 + text_w(s, FS_LABEL) + 18
        per_lang(svg, keys)
    for k, (split, box) in enumerate(panels):
        a, b, gain, order = _fam(split)
        sx = scale(0, 100, box[0], box[2])
        panel_title(svg, box[0] - (0 if narrow else 0), box[1] - 20, 'ab'[k], T(split, split), T('success, %', '成功率，%'))
        frame(svg, (box[0], box[1] - 8, box[2], box[3]), sx, None, [0, 25, 50, 75, 100], [], grid='x')
        svg.text(box[2] + 40, box[1] - 20, T('gain', '提升'), cls='t-faint', anchor='end', size=FS_TICK)
        pitch = (box[3] - box[1]) / len(order)
        for i, fam in enumerate(order):
            y = box[1] + i * pitch + pitch / 2 - 4
            key = fam == 'pick_two_obj_and_place'
            (sa, n), (sb, _) = a[fam], b[fam]
            pa, pb = 100 * sa / n, 100 * sb / n
            if key:
                svg.rect(box[0] - (110 if not narrow else 92), y - pitch / 2 + 2, (box[2] - box[0]) + (152 if not narrow else 132), pitch - 4, 'band', rx=4)
            svg.text(box[0] - 10, y + 4, FAM_NAMES[fam], cls='t-strong' if key else '', anchor='end', size=FS_LABEL if not narrow else FS_TICK)
            if bars:
                bh_ = 9 if light else 10
                op_ = ' opacity=".55"' if light else ''
                svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sa}/{n} after SFT', f'<path class="bar s3"{op_} d="{hbar(box[0], y - bh_ / 2, sx(pa), bh_, 2)}"/>')
                svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sb}/{n} after RL', f'<rect class="s1" x="{sx(pa) + 1:.1f}" y="{y - bh_ / 2:.1f}" width="{max(sx(pb) - sx(pa) - 1, 1):.1f}" height="{bh_}" rx="2"/>')
            else:
                svg.line(sx(pa), y, sx(pb), y, 'line l1' if key else 'line l3', 'stroke-width="2.2"' + ('' if key else ' opacity=".6"'))
                svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sa}/{n} → {sb}/{n}',
                         f'<circle class="dot s3" cx="{sx(pa):.1f}" cy="{y:.1f}" r="4.2"/><circle class="dot s1" cx="{sx(pb):.1f}" cy="{y:.1f}" r="4.8"/>')
            svg.text(box[2] + 40, y + 4, f'+{gain[fam]:.0f}', cls='tx-blue' if key else '', anchor='end', size=FS_LABEL, weight=700 if key else None)
            if key:
                svg.text((sx(pa) + sx(pb)) / 2, y + 15, f'{sa}/{n} → {sb}/{n}', cls='t-muted', anchor='middle', size=10.5)
    return svg


def sft_rl_inno(W):
    """Progress bars instead of dumbbells: the gray part is the success after SFT, the blue extension is what 100 RL
    steps add; sorted by the gain, so the two-object family, which the expert rarely solves, leads both splits."""
    return sft_rl_aes(W, bars=True)


# ============================================================================ scr-vs-grpo
def _vs_data():
    g = {k: run(ALF, 'gigpo', k) for k in ('seen', 'unseen')}
    r = {k: run(ALF, 'grpo', k) for k in ('seen', 'unseen')}
    disc = {k: PAIRED[f'alfworld_steplevel_vs_grpo:valid_{k}'] for k in ('seen', 'unseen')}
    return g, r, disc


def _pfmt(p):
    return f'{p:.3f}' if p < 0.1 else f'{p:.2f}'


def vs_aes(W, strip=False):
    """Curves and per-validation differences kept; titles reduced to the split name, the McNemar p written once per
    panel at the top right, thinner difference bars, and the late-stage means in the band."""
    g, r, disc = _vs_data()
    narrow = W < 500
    if narrow:
        H = 700 if not strip else 600
        bx = [(44, 64, W - 56, 212), (44, 64 + (322 if not strip else 280), W - 56, 212 + (322 if not strip else 280))]
    else:
        H = 400 if not strip else 316
        bx = [(46, 64, W / 2 - 52, 220), (W / 2 + 52, 64, W - 50, 220)]
    svg = Svg(W, H, 'StepCredit-RL vs GRPO: validation success over 200 steps, and the difference at every validation')
    key_lines(svg, bx[0][0], 18, [(1, 'StepCredit-RL'), (2, 'GRPO')])
    for k, (name, A) in enumerate(zip(('seen', 'unseen'), bx)):
        sx, sy = scale(0, 200, A[0], A[2]), scale(0, 100, A[3], A[1])
        panel_title(svg, A[0], A[1] - 16, 'ab'[k], T(name, name), T('success, %', '成功率，%'))
        p_ = float(disc[name]['p'])
        svg.text(A[2], A[1] - 16, f'p = {_pfmt(p_)}' + (' ' if True else ''), cls='t-strong' if p_ < 0.05 else 't-faint', anchor='end', size=FS_TICK)
        svg.rect(sx(160), A[1], sx(200) - sx(160), A[3] - A[1], 'band')
        frame(svg, A, sx, sy, [] if not strip else [0, 50, 100, 150, 200], [0, 25, 50, 75, 100])
        wash_between(svg, [s for s, _ in g[name]], [v for _, v in g[name]], [v for _, v in r[name]], sx, sy)
        path_line(svg, r[name], sx, sy, 2)
        path_line(svg, g[name], sx, sy, 1)
        for idx, pts in ((2, r[name]), (1, g[name])):
            svg.circle(sx(200), sy(pts[-1][1]), 3.2, f'dot s{idx}', 'stroke-width="1.5"')
        hits(svg, g[name], sx, sy, lambda x, y: f'StepCredit-RL · step {x}: {y:.1f}%')
        hits(svg, r[name], sx, sy, lambda x, y: f'GRPO · step {x}: {y:.1f}%')
        label_stack(svg, A[2] + 7, [(sy(g[name][-1][1]), f'{g[name][-1][1]:.1f}', 't-strong'), (sy(r[name][-1][1]), f'{r[name][-1][1]:.1f}', '')], min_gap=13)
        lg = sum(v for s, v in g[name] if s >= 160) / 5
        lr = sum(v for s, v in r[name] if s >= 160) / 5
        svg.text((sx(160) + sx(200)) / 2, A[1] + 13, f'{lg:.1f} / {lr:.1f}', cls='t-muted', anchor='middle', size=10.5)
        if strip:
            # one square per validation: blue where StepCredit-RL is ahead, orange where GRPO is, gray for a tie
            ys = A[3] + 34
            ahead = 0
            for (s_, a_), (_, b_) in zip(g[name], r[name]):
                d_ = a_ - b_
                cls = 's1' if d_ > 0.05 else ('s2' if d_ < -0.05 else 's3')
                ahead += d_ > 0.05
                svg.mark(f'step {s_}: {signed(d_)} points', f'<rect class="{cls}" x="{sx(s_) - 4:.1f}" y="{ys:.1f}" width="8" height="8" rx="1.5"/>')
            svg.text(A[0], ys + 24, T(f'StepCredit-RL ahead at {ahead} of {len(g[name])} validations', f'{len(g[name])} 次验证中 StepCredit-RL 领先 {ahead} 次'), cls='t-muted', size=FS_TICK)
            svg.text(A[2], ys + 24, T('training step →', '训练步 →'), cls='t-faint', anchor='end', size=FS_TICK)
            continue
        B_ = (A[0], A[3] + 30, A[2], A[3] + 104)
        syB = scale(-30, 40, B_[3], B_[1])
        frame(svg, B_, sx, syB, [0, 50, 100, 150, 200], [-20, 0, 20, 40], str, lambda v: signed(v, 0) if v else '0', grid='', ticks_out=True,
              xtitle=T('training step', '训练步'))
        svg.line(B_[0], syB(0), B_[2], syB(0), 'axis')
        bw = (B_[2] - B_[0]) / 30
        for (s_, a_), (_, b_) in zip(g[name], r[name]):
            d_ = a_ - b_
            cls = 's1' if d_ >= 0 else 's2'
            y0, y1 = (syB(d_), syB(0)) if d_ >= 0 else (syB(0), syB(d_))
            svg.mark(f'step {s_}: {signed(d_)}', f'<rect class="{cls}" x="{sx(s_) - bw / 2:.1f}" y="{y0:.1f}" width="{bw:.1f}" height="{max(y1 - y0, 0.8):.1f}" rx="1"/>')
        svg.text(B_[0] + 4, B_[1] + 2, T('StepCredit-RL − GRPO, points', 'StepCredit-RL − GRPO，百分点'), cls='t-faint', size=10.5)
    return svg


def vs_inno(W):
    """The difference bars replaced by a win strip: one square per validation, blue where StepCredit-RL is ahead,
    orange where GRPO is; the count is written under it. The curves already show the size of the gap."""
    return vs_aes(W, strip=True)


# ============================================================================ scr-updates
def _upd():
    four = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo_4upd']
    one = [(int(x['step']), float(x['seen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo' and int(x['step']) <= 150]
    return four, one


def updates_aes(W):
    """Two panels kept (by step, by wall-clock time); solid lines with a dot at each validation, ink end labels, and
    the 'same level' comparison drawn once, as a bracket in (a) and step tags in (b)."""
    four, one = _upd()
    narrow = W < 500
    if narrow:
        H = 560
        pA, pB = (44, 64, W - 60, 230), (44, 330, W - 60, 496)
    else:
        H = 322
        pA, pB = (48, 66, W / 2 - 64, H - 50), (W / 2 + 46, 66, W - 64, H - 50)
    svg = Svg(W, H, 'Seen success with four updates per step and with one, by training step and by wall-clock time')
    key_lines(svg, pA[0], 18, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
    for k, (box, xi, xmax, xt, title) in enumerate(((pA, 0, 150, [0, 50, 100, 150], T('By training step', '按训练步')),
                                                     (pB, 2, 30, [0, 10, 20, 30], T('By wall-clock time', '按耗时')))):
        sx, sy = scale(0, xmax, box[0], box[2]), scale(0, 100, box[3], box[1])
        panel_title(svg, box[0], box[1] - 18, 'ab'[k], title, T('seen success, %', 'seen 成功率，%'))
        frame(svg, box, sx, sy, xt, [0, 25, 50, 75, 100], xtitle=T('training step', '训练步') if k == 0 else T('hours (2 × A100)', '小时（2 × A100）'))
        for idx, rows in ((3, one), (1, four)):
            pts = [(rw[xi], rw[1]) for rw in rows]
            path_line(svg, pts, sx, sy, idx)
            dots(svg, pts, sx, sy, idx, r=2.2, ring=False)
            hits(svg, pts, sx, sy, lambda x, y, xi=xi: f'{x:g} {"h" if xi else "steps"}: {y:.1f}%')
        e4, e1 = (four[-1][xi], four[-1][1]), (one[-1][xi], one[-1][1])
        svg.text(sx(e4[0]) + 8, sy(e4[1]) + 4, f'{e4[1]:.1f}', cls='t-strong', size=FS_LABEL)
        svg.text(sx(e1[0]) + 8, sy(e1[1]) + 4, f'{e1[1]:.1f}', size=FS_LABEL)
        if k == 0:
            yb = sy(87)
            svg.path(f'M{sx(100):.1f},{yb + 5:.1f} V{yb:.1f} H{sx(150):.1f} V{yb + 5:.1f}', 'leader')
            svg.text((sx(100) + sx(150)) / 2, yb - 6, T('same level: step 100 vs 150', '相同水平：第 100 步对第 150 步'), cls='t-muted', anchor='middle', size=FS_TICK)
        else:
            svg.text(sx(e4[0]), sy(e4[1]) - 10, T('step 100', '第 100 步'), cls='t-faint', anchor='middle', size=10.5)
            svg.text(sx(e1[0]), sy(e1[1]) - 10, T('step 150', '第 150 步'), cls='t-faint', anchor='middle', size=10.5)
    return svg


def updates_inno(W):
    """One panel on the wall-clock axis, with the training step marked along each curve every 50 steps: four updates per
    step reach 76.4% at step 100 after 16 hours; one update needs 150 steps and 29 hours for 72.1%."""
    four, one = _upd()
    narrow = W < 500
    H = 330 if not narrow else 360
    box = (48, 50, W - (90 if not narrow else 62), H - 50)
    svg = Svg(W, H, 'Seen success against wall-clock hours for four updates per step and for one, with training steps marked')
    key_lines(svg, box[0], 18, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
    sx, sy = scale(0, 30, box[0], box[2]), scale(0, 100, box[3], box[1])
    frame(svg, box, sx, sy, [0, 5, 10, 15, 20, 25, 30], [0, 25, 50, 75, 100], xtitle=T('hours on 2 × A100', '耗时（2 × A100，小时）'))
    svg.text(box[0] - 7, box[1] - 12, T('seen success, %', 'seen 成功率，%'), cls='t-muted', size=FS_TICK)
    for idx, rows in ((3, one), (1, four)):
        pts = [(h, s) for _, s, h in rows]
        path_line(svg, pts, sx, sy, idx)
        hits(svg, pts, sx, sy, lambda x, y: f'{x:g} h: {y:.1f}%')
        for st, s, h in rows:
            if st in (50, 100, 150):
                svg.circle(sx(h), sy(s), 3.6, f'dot s{idx}', 'stroke-width="1.5"')
                svg.text(sx(h) - 6, sy(s) - 8, T(f'step {st}', f'第 {st} 步'), cls='t-muted', anchor='end', size=10.5)
    e4, e1 = four[-1], one[-1]
    svg.text(sx(e4[2]) + 8, sy(e4[1]) + 4, f'{e4[1]:.1f}%', cls='t-strong', size=FS_LABEL)
    svg.text(sx(e1[2]) + 8, sy(e1[1]) + 4, f'{e1[1]:.1f}%', size=FS_LABEL)
    yb = sy(90)
    svg.path(f'M{sx(e4[2]):.1f},{yb + 5:.1f} V{yb:.1f} H{sx(e1[2]):.1f} V{yb + 5:.1f}', 'leader')
    svg.text((sx(e4[2]) + sx(e1[2])) / 2, yb - 6, T(f'about the same level {e1[2] - e4[2]:.0f} h sooner', f'约早 {e1[2] - e4[2]:.0f} 小时达到同等水平'),
             cls='t-muted', anchor='middle', size=FS_TICK)
    return svg


# ============================================================================ scr-hotpotqa
def _hpq():
    em = {k: run(HPQ, 'em', k) for k in ('em', 'f1', 'repeat_queries')}
    sh = {k: run(HPQ, 'shaped', k) for k in ('em', 'f1', 'repeat_queries')}
    return em, sh


def hotpot_aes(W):
    """Three small multiples kept; no shading between the lines, small dots, ink end values, the McNemar p as a plain
    note under the EM panel and the −71% next to its bracket."""
    em, sh = _hpq()
    narrow = W < 500
    specs = [('em', T('Exact match', 'EM'), '%', (40, 60), [40, 50, 60], lambda v: f'{v:.0f}'),
             ('f1', T('Token F1', 'Token F1'), '', (0.55, 0.75), [0.55, 0.65, 0.75], lambda v: f'{v:.2f}'),
             ('repeat_queries', T('Repeated queries', '重复查询'), T('per question', '每题'), (0, 0.2), [0, 0.1, 0.2], lambda v: f'{v:.1f}' if v else '0')]
    H = 296 if not narrow else 800
    svg = Svg(W, H, 'HotpotQA: exact match, F1 and repeated queries under the EM reward and the shaped reward')
    key_lines(svg, 48, 18, [(1, T('EM reward', 'EM 奖励')), (2, T('shaped reward', '稠密奖励'))])
    pw = (W - 60) / 3
    for k, (key, title, unit, (lo, hi), ticks, fmt) in enumerate(specs):
        box = (56, 70 + k * 246, W - 70, 70 + k * 246 + 160) if narrow else (52 + k * pw, 68, 52 + k * pw + pw - 82, H - 60)
        sx, sy = scale(0, 200, box[0], box[2]), scale(lo, hi, box[3], box[1])
        panel_title(svg, box[0], box[1] - 16, 'abc'[k], title, unit or None)
        frame(svg, box, sx, sy, [0, 100, 200], ticks, str, fmt, xtitle=T('step', '步'))
        for idx, d in ((2, sh), (1, em)):
            path_line(svg, d[key], sx, sy, idx)
            dots(svg, d[key], sx, sy, idx, r=2.2, ring=False)
            hits(svg, d[key], sx, sy, lambda x, y: f'step {x}: {y}')
        a_, b_ = em[key][-1][1], sh[key][-1][1]
        f = (lambda v: f'{v:.1f}') if key == 'em' else (lambda v: f'{v:.3f}')
        label_stack(svg, box[2] + 7, [(sy(a_), f(a_), 't-strong' if key != 'repeat_queries' else ''),
                                      (sy(b_), f(b_), 't-strong' if key == 'repeat_queries' else '')], min_gap=13)
        if key == 'em':
            p_ = float(PAIRED['hotpotqa_em_vs_shaped:all']['p'])
            svg.text(box[2], sy(lo) - 8, f'McNemar p = {p_:.2f}', cls='t-faint', anchor='end', size=10.5)
        if key == 'repeat_queries':
            ya, yb = sy(a_), sy(b_)
            xl = sx(200) - 7
            svg.line(xl, ya + 5, xl, yb - 5, 'leader')
            svg.text(xl - 5, ya + (yb - ya) * 0.35 + 4, signed(100 * (b_ - a_) / a_, 0) + '%', cls='t-strong', anchor='end', size=FS_LABEL)
    return svg


def hotpot_inno(W, slim=False):
    """F1 dropped (it tracks EM) to make room for the training signal behind the result: all-failed groups, the groups
    that give GRPO no signal, fall from about 27% to 4% with the shaped reward; EM and repeated queries stay as curves."""
    em, sh = _hpq()
    narrow = W < 500
    H = 296 if not narrow else 800
    svg = Svg(W, H, 'HotpotQA: exact match and repeated queries over training, and the share of all-failed groups, under the EM and shaped rewards')
    key_lines(svg, 48, 18, [(1, T('EM reward', 'EM 奖励')), (2, T('shaped reward', '稠密奖励'))])
    pw = (W - 60) / 3
    specs = [('em', T('Exact match', 'EM'), '%', (40, 60), [40, 50, 60], lambda v: f'{v:.0f}'),
             ('repeat_queries', T('Repeated queries', '重复查询'), T('per question', '每题'), (0, 0.2), [0, 0.1, 0.2], lambda v: f'{v:.1f}' if v else '0')]
    for k, (key, title, unit, (lo, hi), ticks, fmt) in enumerate(specs):
        box = (56, 70 + k * 246, W - 70, 70 + k * 246 + 160) if narrow else (52 + k * pw, 68, 52 + k * pw + pw - 82, H - 60)
        sx, sy = scale(0, 200, box[0], box[2]), scale(lo, hi, box[3], box[1])
        panel_title(svg, box[0], box[1] - 16, 'ab'[k], title, unit or None)
        frame(svg, box, sx, sy, [0, 100, 200], ticks, str, fmt, xtitle=T('step', '步'))
        for idx, d in ((2, sh), (1, em)):
            path_line(svg, d[key], sx, sy, idx)
            dots(svg, d[key], sx, sy, idx, r=2.2, ring=False)
            hits(svg, d[key], sx, sy, lambda x, y: f'step {x}: {y}')
        a_, b_ = em[key][-1][1], sh[key][-1][1]
        f = (lambda v: f'{v:.1f}') if key == 'em' else (lambda v: f'{v:.3f}')
        label_stack(svg, box[2] + 7, [(sy(a_), f(a_), 't-strong' if key == 'em' else ''), (sy(b_), f(b_), 't-strong' if key != 'em' else '')], min_gap=13)
        if key == 'em':
            p_ = float(PAIRED['hotpotqa_em_vs_shaped:all']['p'])
            svg.text(box[2], sy(lo) - 8, f'McNemar p = {p_:.2f}', cls='t-faint', anchor='end', size=10.5)
        else:
            ya, yb = sy(a_), sy(b_)
            xl = sx(200) - 7
            svg.line(xl, ya + 5, xl, yb - 5, 'leader')
            svg.text(xl - 5, ya + (yb - ya) * 0.35 + 4, signed(100 * (b_ - a_) / a_, 0) + '%', cls='t-strong', anchor='end', size=FS_LABEL)
    box = (56, 70 + 2 * 246, W - 70, 70 + 2 * 246 + 160) if narrow else (52 + 2 * pw, 68, 52 + 2 * pw + pw - 60, H - 60)
    panel_title(svg, box[0], box[1] - 16, 'c', T('All-failed groups', '全错组'), T('during training', '训练中'))
    sy = scale(0, 30, box[3], box[1])
    frame(svg, box, lambda v: v, sy, [], [0, 10, 20, 30], str, lambda v: f'{v}%')
    cw = (box[2] - box[0]) / 2
    for j, (idx, v, lab) in enumerate(((1, 27, T('EM reward', 'EM 奖励')), (2, 4, T('shaped', '稠密奖励')))):
        cx = box[0] + cw * (j + 0.5)
        hw = 11 if slim else 18
        svg.mark(f'{lab[0]}: about {v}% of the groups had no successful answer', f'<path class="bar s{idx}" d="M{cx - hw:.1f},{sy(0):.1f} V{sy(v) + 3:.1f} A3,3 0 0 1 {cx - hw + 3:.1f},{sy(v):.1f} H{cx + hw - 3:.1f} A3,3 0 0 1 {cx + hw:.1f},{sy(v) + 3:.1f} V{sy(0):.1f} Z"/>')
        svg.text(cx, sy(v) - 7, f'≈ {v}%', cls='t-strong', anchor='middle', size=FS_LABEL)
        svg.text(cx, box[3] + 16, lab, cls='t-faint', anchor='middle', size=FS_TICK)
    return svg


AES = {'opd-methods': methods_aes, 'opd-budget': budget_aes, 'opd-training': training_aes, 'opd-compute': compute_aes,
       'scr-sft-rl': sft_rl_aes, 'scr-vs-grpo': vs_aes, 'scr-updates': updates_aes, 'scr-hotpotqa': hotpot_aes}
INNO = {'opd-methods': methods_inno, 'opd-budget': budget_inno, 'opd-training': training_inno, 'opd-compute': compute_inno,
        'scr-sft-rl': sft_rl_inno, 'scr-vs-grpo': vs_inno, 'scr-updates': updates_inno, 'scr-hotpotqa': hotpot_inno}
MERGED = {'opd-methods': methods_aes,
          'opd-budget': lambda W: budget_inno(W, merged=True),
          'opd-training': training_aes,
          'opd-compute': compute_aes,
          'scr-sft-rl': lambda W: sft_rl_aes(W, bars=True, light=True),
          'scr-vs-grpo': vs_inno,
          'scr-updates': updates_inno,
          'scr-hotpotqa': lambda W: hotpot_inno(W, slim=True)}
NOTES = {
    'opd-methods': 'Merged: aesthetic. The AIME-average dots of the innovative version are informative but add a second encoding to a chart whose job is the four-benchmark ranking.',
    'opd-budget': 'Merged: innovative (three measures on one shared x-axis, the 16k column reads straight down), with phone labels shortened to values plus a key.',
    'opd-training': 'Merged: aesthetic. The anatomy bars of the innovative version read well but leave panel (b) mostly empty and drop the 100–150 token level the caption cites.',
    'opd-compute': 'Merged: aesthetic (dimension line for the 4× cost). The rotated slope labels of the innovative version add noise; the efficiency idea returns as an inset in round 2.',
    'scr-sft-rl': 'Merged: innovative progress bars (gray = after SFT, blue = what RL adds), with a lighter gray so the gains carry the colour.',
    'scr-vs-grpo': 'Merged: innovative win strip (ahead at 16 of 21 validations in both splits); the curves already show the size of the gap.',
    'scr-updates': 'Merged: innovative single panel on the wall-clock axis with the steps marked, which shows both comparisons at once.',
    'scr-hotpotqa': 'Merged: innovative; F1 (which tracks EM) gives way to the all-failed groups, the training signal behind the result. Caption needs updating.',
}
