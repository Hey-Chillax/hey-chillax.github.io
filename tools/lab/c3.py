"""Chart round 3 (2026-11-17), the last of this cycle. BASE = round 2's merges (c2.MERGED); MERGED here is final.

NOTES records the reasons.
"""
from c_kit import (ALF, FAM_NAMES, FS_LABEL, FS_TICK, HPQ, OPD, PAIRED, Svg, T, dots, frame, hbar, hits, key_lines,
                   label_stack, moving_avg, panel_title, path_line, per_lang, pick, polyline, run, scale, signed, text_w,
                   wash_between)
import c1
import c2

BASE = dict(c2.MERGED)


# ============================================================================ opd-methods
def methods(W, style='aes'):
    """'aes': the round-2 lollipops with the baseline stems lighter, so the two distillation rows lead, and a background
    ring on every dot. 'gain': every stem starts at the base model's 25.4 (each method starts from it), so the stem
    length is the gain; the axis starts at 20."""
    rows = c1._method_rows()
    narrow = W < 500
    gain = style == 'gain'
    if gain:
        rows = rows[1:]
    pitch, bh = (42, 11) if narrow else (30, 11)
    x0, x1 = (12, W - 46) if narrow else (206, W - 104)
    top = 30
    groups = [(0, T('Baselines', '基线'))] if not gain else [(0, T('Baselines', '基线'))]
    groups.append((3 if not gain else 2, T('On-policy distillation', '在线蒸馏')))
    ys, heads = [], []
    y = top
    for i in range(len(rows)):
        for gi, gl in groups:
            if gi == i:
                if i:
                    y += 14
                heads.append((y - 6, gl))
                y += 14
        ys.append(y + (18 if narrow else 0))
        y += pitch
    y_end = y - (pitch - bh) + (18 if narrow else 0) + 8
    H = y_end + 42
    svg = Svg(W, H, '4-benchmark math average by post-training method' + (', drawn as the gain over the base model' if gain else ''))
    lo = 20 if gain else 0
    sx = scale(lo, 50, x0, x1)
    frame(svg, (x0, top - 14, x1, y_end), sx, None, [20, 25, 30, 35, 40, 45, 50] if gain else [0, 10, 20, 30, 40, 50], [], grid='x',
          xtitle=T('4-benchmark average (MATH-500, AIME 2024–26)', '4 项平均分（MATH-500、AIME 2024–26）'))
    d = OPD['eval_avg4']
    if gain:
        bx = sx(d['base'])
        svg.line(bx, top - 14, bx, y_end, 'axis', 'stroke-dasharray="3 3"')
        svg.text(bx + 4, top - 18, T(f'base model {d["base"]:.1f}', f'基座 {d["base"]:.1f}'), cls='t-muted', size=FS_TICK)
    for hy, gl in heads:
        if narrow:
            svg.text(x0, hy, gl, cls='t-faint', size=10.5, ls='0.04em')
        else:
            svg.text(x0 - 12, hy, gl, cls='t-faint', anchor='end', size=10.5, ls='0.04em')
    for (lab, v, cls, kind), yb in zip(rows, ys):
        strong = kind == 'ours'
        if kind == 'variant':
            lab = T('↳ ' + lab[0], '↳ ' + lab[1])
        tcls = 't-strong' if strong else ('t-muted' if kind == 'variant' else '')
        cy = yb + bh / 2
        if narrow:
            svg.text(x0 + (12 if kind == 'variant' else 0), yb - 6, lab, cls=tcls, size=FS_LABEL)
        else:
            svg.text(x0 - 12, cy + 4.2, lab, cls=tcls, anchor='end', size=FS_LABEL)
        idx = {'s3': 3, 's2': 2, 's1': 1, 'pn-blue': 1}[cls]
        start = sx(d['base']) if gain else x0
        op = ' opacity=".5"' if (kind == 'ref' and not gain) else (' opacity=".45"' if kind == 'variant' else '')
        svg.line(start, cy, sx(v), cy, f'line l{idx}', 'stroke-width="2"' + op)
        if kind == 'variant':
            svg.mark(f'{lab[0]}: {v:.2f}', f'<circle cx="{sx(v):.1f}" cy="{cy:.1f}" r="5" class="l1" fill="var(--bg)" stroke-width="2"/>')
        else:
            svg.mark(f'{lab[0]}: {v:.2f}', f'<circle class="dot s{idx}" cx="{sx(v):.1f}" cy="{cy:.1f}" r="{6 if strong else 5}" stroke-width="2"/>')
        if gain:
            svg.text(sx(v) + 11, cy + 4.2, f'{v:.1f}', cls='t-strong' if strong else '', size=FS_LABEL)
            svg.text((start + sx(v)) / 2, cy - 7, signed(v - d['base']), cls='t-faint', anchor='middle', size=10.5)
        else:
            svg.text(sx(v) + 11, cy + 4.2, f'{v:.1f}', cls='t-strong' if strong else '', size=FS_LABEL)
    i_opd = [k for k, r in enumerate(rows) if r[3] == 'opd'][0]
    xb = sx(d['takeover_conclude_40']) + (38 if narrow else 44)
    yo, yt = ys[i_opd] + bh / 2, ys[i_opd + 1] + bh / 2
    svg.path(f'M{xb - 5:.1f},{yo:.1f} H{xb:.1f} V{yt:.1f} H{xb - 5:.1f}', 'leader')
    svg.text(xb + 5, (yo + yt) / 2 + 4.3, signed(d['takeover_conclude_40'] - d['opd_40']), cls='tx-blue', size=FS_LABEL, weight=700)
    return svg


# ============================================================================ opd-budget
def budget(W, callout=False):
    """'aes': round-2 merge with one left edge for all panel titles, slightly shorter panels and the band label inside
    the band. callout=True adds the comparison the page text makes, with a leader into the empty upper left of (a):
    Scaffold-OPD capped at 16k already leads OPD's full 32k by 2.7."""
    b, xs = c1._budget()
    narrow = W < 500
    short = narrow
    kfmt = c1.kfmt
    x0, x1 = (44, W - 52) if narrow else (64, W - 150)
    hA, hB, hC, gap = (152, 76, 72, 34) if not narrow else (150, 76, 72, 40)
    yA = 30 if not short else 56
    A = (x0, yA, x1, yA + hA)
    B_ = (x0, A[3] + gap, x1, A[3] + gap + hB)
    C = (x0, B_[3] + gap, x1, B_[3] + gap + hC)
    H = C[3] + 46
    svg = Svg(W, H, 'Accuracy, paired gap and finished AIME answers against the evaluation token budget, on a shared axis')
    sx = scale(10, 15, x0, x1)
    if short:
        key_lines(svg, x0, 18, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    svg.rect(sx(14), A[1] - 6, sx(15) - sx(14), C[3] - A[1] + 6, 'band')
    svg.text(sx(14.5), A[1] + 8, '16k → 32k', cls='t-faint', anchor='middle', size=10.5)
    syA = scale(0, 50, A[3], A[1])
    frame(svg, A, sx, syA, [], [0, 25, 50], kfmt, str)
    wash_between(svg, xs, b['takeover_40'], b['opd_40'], sx, syA)
    for idx, key in ((2, 'opd_40'), (1, 'takeover_40')):
        path_line(svg, list(zip(xs, b[key])), sx, syA, idx)
        dots(svg, [(x, y) for x, y, t in zip(xs, b[key], b['tokens']) if t in c1.DOUBLINGS], sx, syA, idx, r=3)
    if short:
        label_stack(svg, x1 + 8, [(syA(b['takeover_40'][-1]), f'{b["takeover_40"][-1]:.1f}', 't-strong'), (syA(b['opd_40'][-1]), f'{b["opd_40"][-1]:.1f}', '')], min_gap=15)
    else:
        label_stack(svg, x1 + 8, [(syA(b['takeover_40'][-1]), f'Scaffold-OPD {b["takeover_40"][-1]:.1f}', 't-strong'),
                                  (syA(b['opd_40'][-1]), f'OPD {b["opd_40"][-1]:.1f}', '')], min_gap=15)
    if callout:
        k16 = b['tokens'].index(16384)
        o32, s16 = b['opd_40'][-1], b['takeover_40'][k16]
        px, py = sx(xs[k16]), syA(s16)
        svg.line(px, syA(o32), sx(15), syA(o32), 'leader', 'stroke-dasharray="2 3"')
        svg.circle(px, py, 4.6, 'ring')
        lab1 = T(f'Scaffold-OPD at 16k: {s16:.1f}', f'Scaffold-OPD 在 16k：{s16:.1f}')
        lab2 = T(f'already {s16 - o32:.1f} above OPD at 32k ({o32:.1f})', f'已比 OPD 在 32k（{o32:.1f}）高 {s16 - o32:.1f}')
        tx, ty = sx(10.12), syA(45.8)
        svg.text(tx, ty, lab1, cls='t-strong', size=FS_TICK)
        svg.text(tx, ty + 14, lab2, size=FS_TICK)
        ex = tx + max(svg.tw(lab1, FS_TICK, 600), svg.tw(lab2, FS_TICK)) + 6
        svg.path(f'M{ex:.1f},{ty + 2:.1f} L{px - 6:.1f},{py - 2:.1f}', 'leader')
    panel_title(svg, x0, A[1] - 12, 'a', T('Accuracy', '准确率'), T('4-benchmark average', '4 项平均'))
    syB = scale(-5, 8, B_[3], B_[1])
    frame(svg, B_, sx, syB, [], [-4, 0, 4, 8], kfmt, lambda v: signed(v, 0) if v else '0')
    up = [(x, g + s) for x, g, s in zip(xs, b['gap_40'], b['gap_se_40'])]
    lo = [(x, g - s) for x, g, s in zip(xs, b['gap_40'], b['gap_se_40'])]
    svg.path(polyline(up, sx, syB) + ' L' + polyline(list(reversed(lo)), sx, syB)[1:] + ' Z', 'wash1')
    svg.line(x0, syB(0), x1, syB(0), 'axis', 'stroke-dasharray="3 3"')
    path_line(svg, list(zip(xs, b['gap_40'])), sx, syB, 1)
    for t_ in (8192, 16384, 32768):
        k = b['tokens'].index(t_)
        g = b['gap_40'][k]
        svg.circle(sx(xs[k]), syB(g), 3, 'dot s1', 'stroke-width="1.5"')
        if t_ == 32768:
            svg.text(x1 + 8, syB(g) + 4, signed(g), cls='t-strong', size=FS_LABEL)
        else:
            svg.text(sx(xs[k]) - 6, syB(g) - 7, signed(g), cls='t-strong', anchor='end', size=FS_TICK)
    panel_title(svg, x0, B_[1] - 12, 'b', T('Paired gap', '配对差'), T('Scaffold-OPD − OPD, ±1 SE', 'Scaffold-OPD − OPD，±1 标准误'))
    syC = scale(0, 100, C[3], C[1])
    frame(svg, C, sx, syC, c1.KT, [0, 50, 100], kfmt, str)
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
def training(W, raw=False):
    """'aes': round-2 merge with a short tick from each share label to the curve and the panel-(b) end value on the
    same scale as panel (a). raw=True also draws every step's raw value as a faint dot behind the five-step moving
    average, so the smoothing is visible."""
    t, tk, op, teach = c1._train()
    tr = OPD['train']
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
    if raw:
        sxa, sya = scale(0, 60, bA[0], bA[2]), scale(0, 6000, bA[3], bA[1])
        for idx, steps, vals in ((2, tr['opd']['step'], tr['opd']['response_length']), (1, t['step'], t['response_length'])):
            for s_, v in zip(steps, vals):
                if v is not None and not (idx == 1 and s_ == 19):
                    svg.circle(sxa(s_), sya(min(v, 6000)), 1.6, f's{idx}', 'opacity=".28"')
    c1._length_panel(svg, bA, tk, op)
    panel_title(svg, bB[0], bB[1] - 16, 'b', T('Teacher tokens per answer', '每条回答的老师 token'), 'Scaffold-OPD')
    sx, sy = scale(0, 60, bB[0], bB[2]), scale(0, 200, bB[3], bB[1])
    for v in (100, 150):
        svg.line(bB[0], sy(v), bB[2], sy(v), 'leader', 'stroke-dasharray="3 3"')
    frame(svg, bB, sx, sy, [0, 20, 40, 60], [0, 50, 100, 150, 200], xtitle=T('training step', '训练步'))
    area = polyline(teach, sx, sy) + f' L{sx(teach[-1][0]):.1f},{sy(0):.1f} L{sx(teach[0][0]):.1f},{sy(0):.1f} Z'
    svg.path(area, 'fl-green', 'opacity=".55"')
    if raw:
        for s_, v in zip(t['step'], t['teacher_tokens_per_answer']):
            if v is not None and s_ != 19:
                svg.circle(sx(s_), sy(min(v, 200)), 1.6, 's5', 'opacity=".35"')
    path_line(svg, teach, sx, sy, 5)
    svg.circle(sx(teach[-1][0]), sy(teach[-1][1]), 3.2, 'dot s5', 'stroke-width="1.5"')
    hits(svg, teach, sx, sy, lambda x, y: f'step {x}: {y:.0f} teacher tokens per answer')
    s0 = 100 * c1._window(t, 1, 5, 'teacher_token_ratio')
    s1 = 100 * c1._window(t, 56, 60, 'teacher_token_ratio')
    y0l, y1l = sy(teach[0][1]) - 22, sy(teach[-1][1]) - 24
    svg.line(sx(teach[0][0]) + 2, y0l + 4, sx(teach[0][0]) + 2, sy(teach[0][1]) - 4, 'leader')
    svg.line(sx(60) - 2, y1l + 4, sx(60) - 2, sy(teach[-1][1]) - 5, 'leader')
    svg.text(sx(teach[0][0]) + 6, y0l + 2, T(f'{s0:.0f}% of the tokens', f'占全部 token {s0:.0f}%'), size=FS_TICK)
    svg.text(sx(60) - 6, y1l + 2, T(f'{s1:.0f}% of the tokens', f'占全部 token {s1:.0f}%'), anchor='end', size=FS_TICK)
    if not narrow:
        svg.text(bB[2] + 8, sy(teach[-1][1]) + 4, f'{teach[-1][1]:.0f}', cls='t-strong', size=FS_LABEL)
    return svg


# ============================================================================ opd-compute
def compute(W, spans=False):
    """'aes': round-2 merge with an inset title in ink, thinner inset bars and the pipeline bars in a lighter orange so
    the blue one leads. spans=True adds the three pipeline stages as a strip just above the x-axis, with their hours."""
    pts, alone = c1._compute_data()
    g = OPD['gpu_hours']['pipeline']
    narrow = W < 500
    H = 330 if not narrow else 360
    box = (46, 44, W - (28 if narrow else 118), H - 44)
    svg = Svg(W, H, 'Score against cumulative training GPU-hours: the full pipeline and Scaffold-OPD alone, and the points gained per GPU-hour')
    key_lines(svg, box[0], 16, [(2, T('full pipeline', '全流程')), (1, T('Scaffold-OPD alone', '只做 Scaffold-OPD'))])
    sx, sy = scale(0, 56, box[0], box[2]), scale(20, 52, box[3], box[1])
    frame(svg, box, sx, sy, [0, 10, 20, 30, 40, 50], [20, 30, 40, 50], xtitle=T('cumulative training GPU-hours (2 × A100)', '累计训练卡时（2 × A100）'))
    svg.text(box[0] - 7, box[1] - 10, T('4-benchmark average', '4 项平均分'), cls='t-muted', size=FS_TICK)
    if spans:
        ys_ = sy(20) - 12
        starts = [0, pts[1][0], pts[2][0]]
        names = [T(f'data + SFT · {g["sft_incl_teacher_data"]:.1f} h', f'数据 + SFT · {g["sft_incl_teacher_data"]:.1f} 小时'),
                 T(f'Scaffold-OPD · {g["takeover_40"]:.1f} h', f'Scaffold-OPD · {g["takeover_40"]:.1f} 小时'),
                 T(f'GRPO · {g["grpo_30"]:.1f} h', f'GRPO · {g["grpo_30"]:.1f} 小时')]
        ends = [pts[1][0], pts[2][0], pts[3][0]]
        for a_, z_, nm in zip(starts, ends, names):
            svg.rect(sx(a_) + 1.5, ys_, sx(z_) - sx(a_) - 3, 5, 's2', rx=2.5, extra='opacity=".45"')
            if not narrow:
                svg.text((sx(a_) + sx(z_)) / 2, ys_ - 5, nm, cls='t-faint', anchor='middle', size=10.5)
    path_line(svg, pts, sx, sy, 2)
    path_line(svg, [pts[0], alone], sx, sy, 1)
    c3 = pts[-1][0]
    yd = sy(50)
    for x in (alone[0], c3):
        svg.line(sx(x), yd + 4, sx(x), sy(max(alone[1], pts[-1][1])) - 8, 'leader', 'stroke-dasharray="2 3"')
    svg.line(sx(alone[0]), yd, sx(c3), yd, 'leader')
    for x, d in ((alone[0], 1), (c3, -1)):
        svg.path(f'M{sx(x):.1f},{yd:.1f} l{5 * d},-3.5 v7 Z', 'arrow-head')
    svg.text((sx(alone[0]) + sx(c3)) / 2, yd - 7, T(f'same score · ≈ {c3 / alone[0]:.0f}× the GPU-hours', f'分数相同 · 卡时约 {c3 / alone[0]:.0f} 倍'),
             cls='t-strong', anchor='middle', size=FS_LABEL)
    labels = [T('base', '基座'), T('+ SFT'), T('+ Scaffold-OPD'), T('+ GRPO on failures', '+ 错题回流 GRPO')]
    for k, ((x, y), lab) in enumerate(zip(pts, labels)):
        svg.mark(f'{lab[0]}: {y:.2f} after {x:.1f} GPU-hours', f'<circle class="dot s2" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4"/>')
        text = (f'{lab[0]} {y:.1f}', f'{lab[1]} {y:.1f}')
        if k == 0:
            svg.text(sx(x) + 8, sy(y) + 15, text, cls='t-muted', size=FS_TICK)
        elif k == 3:
            if narrow:
                svg.text(sx(x) - 7, sy(y) - 9, text, anchor='end', size=FS_TICK)
            else:
                svg.text(sx(x) + 8, sy(y) + 16, text, size=FS_TICK)
        else:
            svg.text(sx(x) + 6, sy(y) + 17, text, size=FS_TICK)
    svg.mark(f'Scaffold-OPD alone: {alone[1]:.2f} after {alone[0]:.1f} GPU-hours',
             f'<circle class="dot s1" cx="{sx(alone[0]):.1f}" cy="{sy(alone[1]):.1f}" r="4.5"/>')
    svg.text(sx(alone[0]) + 9, sy(alone[1]) + 16, T(f'Scaffold-OPD alone {alone[1]:.1f}', f'只做 Scaffold-OPD {alone[1]:.1f}'), cls='t-strong', size=FS_TICK)
    if not narrow:
        rates = [(T('Scaffold-OPD alone', '只做 Scaffold-OPD'), (alone[1] - pts[0][1]) / alone[0], 's1', ''),
                 (T('pipeline · SFT', '全流程 · SFT'), (pts[1][1] - pts[0][1]) / (pts[1][0] - pts[0][0]), 's2', ' opacity=".7"'),
                 (T('pipeline · Scaffold-OPD', '全流程 · Scaffold-OPD'), (pts[2][1] - pts[1][1]) / (pts[2][0] - pts[1][0]), 's2', ' opacity=".7"'),
                 (T('pipeline · GRPO', '全流程 · GRPO'), (pts[3][1] - pts[2][1]) / (pts[3][0] - pts[2][0]), 's2', ' opacity=".7"')]
        ix0, ix1 = sx(38.5), sx(53)
        iy = sy(33.5) - (6 if spans else 0)
        svg.text(ix0 - 132, iy, T('points gained per GPU-hour', '每卡时提分'), cls='t-strong', size=FS_TICK)
        sxi = scale(0, 1.7, ix0, ix1)
        for j, (lab, r_, cls, op) in enumerate(rates):
            yy = iy + 8 + j * 14
            svg.text(ix0 - 8, yy + 7.5, lab, anchor='end', size=10.5)
            svg.mark(f'{lab[0]}: {r_:.2f} points per GPU-hour', f'<path class="bar {cls}"{op} d="{hbar(ix0, yy, sxi(r_), 8, 2)}"/>')
            svg.text(sxi(r_) + 5, yy + 7.5, f'{r_:.2f}', cls='t-strong' if j == 0 else '', size=10.5)
    return svg


# ============================================================================ scr-sft-rl
def sft_rl(W, same_order=False):
    """'aes': round-2 merge with the non-key gains muted, so only the two-object rows carry colour and weight.
    same_order=True puts both panels in the seen panel's order, so a family sits on the same row in both splits."""
    svg = c2.sft_rl_polish(W, same_order=same_order)
    out = []
    for p_ in svg.parts:
        if p_.startswith('<text') and 'text-anchor="end"' in p_ and '>+' in p_ and 'tx-blue' not in p_:
            p_ = p_.replace('<text ', '<text class="t-muted" ', 1) if 'class=' not in p_ else p_
        out.append(p_)
    svg.parts = out
    return svg


# ============================================================================ scr-vs-grpo
def vs(W, means=False):
    """'aes': round-2 merge with 'McNemar' written before p (it is the test the page cites) and slightly larger squares.
    means=True draws the late-stage means as short lines inside the gray band instead of the '82.3 / 61.0' text."""
    g, r, disc = c1._vs_data()
    narrow = W < 500
    if narrow:
        H = 600
        bx = [(44, 64, W - 56, 212), (44, 344, W - 56, 492)]
    else:
        H = 318
        bx = [(46, 64, W / 2 - 52, 220), (W / 2 + 52, 64, W - 50, 220)]
    svg = Svg(W, H, 'StepCredit-RL vs GRPO: validation success over 200 steps, and which run is ahead at each validation')
    key_lines(svg, bx[0][0], 18, [(1, 'StepCredit-RL'), (2, 'GRPO')])
    for k, (name, A) in enumerate(zip(('seen', 'unseen'), bx)):
        sx, sy = scale(0, 200, A[0], A[2]), scale(0, 100, A[3], A[1])
        panel_title(svg, A[0], A[1] - 16, 'ab'[k], T(name, name), T('success, %', '成功率，%'))
        p_ = float(disc[name]['p'])
        svg.text(A[2], A[1] - 16, f'McNemar p = {c1._pfmt(p_)}', cls='t-strong' if p_ < 0.05 else 't-faint', anchor='end', size=FS_TICK)
        svg.rect(sx(160), A[1], sx(200) - sx(160), A[3] - A[1], 'band')
        frame(svg, A, sx, sy, [0, 50, 100, 150, 200], [0, 25, 50, 75, 100])
        wash_between(svg, [s for s, _ in g[name]], [v for _, v in g[name]], [v for _, v in r[name]], sx, sy)
        lg = sum(v for s, v in g[name] if s >= 160) / 5
        lr = sum(v for s, v in r[name] if s >= 160) / 5
        if means:
            for idx, m in ((1, lg), (2, lr)):
                svg.line(sx(160) + 2, sy(m), sx(200) - 2, sy(m), f'line l{idx}', 'stroke-width="1.4" stroke-dasharray="4 3" opacity=".9"')
        path_line(svg, r[name], sx, sy, 2)
        path_line(svg, g[name], sx, sy, 1)
        for idx, pts in ((2, r[name]), (1, g[name])):
            svg.circle(sx(200), sy(pts[-1][1]), 3.2, f'dot s{idx}', 'stroke-width="1.5"')
        hits(svg, g[name], sx, sy, lambda x, y: f'StepCredit-RL · step {x}: {y:.1f}%')
        hits(svg, r[name], sx, sy, lambda x, y: f'GRPO · step {x}: {y:.1f}%')
        label_stack(svg, A[2] + 7, [(sy(g[name][-1][1]), f'{g[name][-1][1]:.1f}', 't-strong'), (sy(r[name][-1][1]), f'{r[name][-1][1]:.1f}', '')], min_gap=13)
        if means:
            svg.text(sx(160) - 4, A[1] + 12, T(f'last 5: {lg:.1f} / {lr:.1f}', f'最后 5 次：{lg:.1f} / {lr:.1f}'), cls='t-muted', anchor='end', size=10.5)
        else:
            svg.text((sx(160) + sx(200)) / 2, A[1] + 13, f'{lg:.1f} / {lr:.1f}', cls='t-muted', anchor='middle', size=10.5)
        ys = A[3] + 32
        ahead = 0
        sq = 8
        for (s_, a_), (_, b_) in zip(g[name], r[name]):
            d_ = a_ - b_
            cls = 's1' if d_ > 0.05 else ('s2' if d_ < -0.05 else 's3')
            ahead += d_ > 0.05
            svg.mark(f'step {s_}: {signed(d_)} points', f'<rect class="{cls}" x="{sx(s_) - sq / 2:.1f}" y="{ys:.1f}" width="{sq}" height="{sq}" rx="1.5"/>')
        svg.text(A[0], ys + 24, T(f'StepCredit-RL ahead at {ahead} of {len(g[name])} validations', f'{len(g[name])} 次验证中 StepCredit-RL 领先 {ahead} 次'), cls='t-muted', size=FS_TICK)
    return svg


# ============================================================================ scr-updates
def updates(W, unseen=False):
    """'aes': round-2 merge with the y grid at 25/50/75 only and the end labels aligned. unseen=True adds the unseen
    split as thin dashed lines (the page quotes both splits: 76.4% / 69.4% vs 72.1% / 66.4%)."""
    four, one = c1._upd()
    four_u = [(int(x['step']), float(x['unseen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo_4upd']
    one_u = [(int(x['step']), float(x['unseen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo' and int(x['step']) <= 150]
    narrow = W < 500
    H = 330 if not narrow else 360
    box = (48, 50, W - (92 if not narrow else 64), H - 50)
    svg = Svg(W, H, 'Success against wall-clock hours for four updates per step and for one, with training steps marked')
    if unseen:
        def keys(i):
            xx = box[0]
            for idx, lab, dash in ((1, pick(T('4 updates per step', '每步 4 次更新'), i), False), (3, pick(T('1 update per step', '每步 1 次更新'), i), False),
                                   (3, pick(T('dashed: unseen', '虚线：unseen'), i), True)):
                svg.line(xx, 14, xx + 18, 14, f'line l{idx}', 'stroke-dasharray="4 3"' if dash else '')
                svg.text(xx + 24, 18, lab, size=FS_LABEL)
                xx += 24 + text_w(lab, FS_LABEL) + 18
        per_lang(svg, keys)
    else:
        key_lines(svg, box[0], 18, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
    sx, sy = scale(0, 30, box[0], box[2]), scale(0, 100, box[3], box[1])
    frame(svg, box, sx, sy, [0, 5, 10, 15, 20, 25, 30], [0, 25, 50, 75, 100], xtitle=T('hours on 2 × A100', '耗时（2 × A100，小时）'))
    svg.text(box[0] - 7, box[1] - 12, T('seen success, %', 'seen 成功率，%') if not unseen else T('success, %', '成功率，%'), cls='t-muted', size=FS_TICK)
    if unseen:
        for idx, rows in ((3, one_u), (1, four_u)):
            path_line(svg, [(h, s) for _, s, h in rows], sx, sy, idx, dashed=True, width=1.4)
    for idx, rows in ((3, one), (1, four)):
        pts = [(h, s) for _, s, h in rows]
        path_line(svg, pts, sx, sy, idx)
        hits(svg, pts, sx, sy, lambda x, y: f'{x:g} h: {y:.1f}%')
        for st, s, h in rows:
            if st in (50, 100, 150):
                svg.circle(sx(h), sy(s), 3.6, f'dot s{idx}', 'stroke-width="1.5"')
                if (idx == 1 and st == 100) or (idx == 3 and st == 150):
                    continue
                svg.text(sx(h) + (8 if idx == 3 else -7), sy(s) + (14 if idx == 3 else -6), T(f'step {st}', f'第 {st} 步'), cls='t-faint',
                         anchor='start' if idx == 3 else 'end', size=10.5)
    e4, e1 = four[-1], one[-1]
    if narrow:
        svg.text(sx(e4[2]) - 4, sy(e4[1]) - 9, T(f'step 100 · {e4[1]:.1f}%', f'第 100 步 · {e4[1]:.1f}%'), cls='t-strong', anchor='end', size=FS_TICK)
        svg.text(sx(e1[2]) - 2, sy(e1[1]) - 9, T(f'step 150 · {e1[1]:.1f}%', f'第 150 步 · {e1[1]:.1f}%'), anchor='end', size=FS_TICK)
    else:
        svg.text(sx(e4[2]) + 8, sy(e4[1]) + 4, T(f'step 100 · {e4[1]:.1f}%', f'第 100 步 · {e4[1]:.1f}%'), cls='t-strong', size=FS_TICK)
        svg.text(sx(e1[2]) + 8, sy(e1[1]) + 4, T(f'step 150 · {e1[1]:.1f}%', f'第 150 步 · {e1[1]:.1f}%'), size=FS_TICK)
    if unseen and not narrow:
        for rows, cls in ((four_u, 't-muted'), (one_u, 't-muted')):
            e = rows[-1]
            svg.text(sx(e[2]) + 8, sy(e[1]) + 4, f'{e[1]:.1f}%', cls=cls, size=10.5)
    yb = sy(90)
    svg.path(f'M{sx(e4[2]):.1f},{yb + 5:.1f} V{yb:.1f} H{sx(e1[2]):.1f} V{yb + 5:.1f}', 'leader')
    svg.text((sx(e4[2]) + sx(e1[2])) / 2, yb - 6, T(f'a higher level about {e1[2] - e4[2]:.0f} h sooner', f'约早 {e1[2] - e4[2]:.0f} 小时达到更高水平'),
             cls='t-muted', anchor='middle', size=FS_TICK)
    return svg


# ============================================================================ scr-hotpotqa
def hotpot(W, horiz=False):
    """'aes': round-2 merge with the readings in ink and the bars a little narrower. horiz=True draws panel (c) as two
    horizontal bars (27% vs 4%), which keeps the three panels the same height and reads like a sentence."""
    em, sh = c1._hpq()
    narrow = W < 500
    H = 312 if not narrow else 820
    top = 84
    svg = Svg(W, H, 'HotpotQA: exact match and repeated queries over training, and the share of all-failed groups, under the EM and shaped rewards')
    key_lines(svg, 48, 18, [(1, T('EM reward', 'EM 奖励')), (2, T('shaped reward', '稠密奖励'))])
    pw = (W - 60) / 3
    specs = [('em', T('Exact match', 'EM'), '%', (40, 60), [40, 50, 60], lambda v: f'{v:.0f}'),
             ('repeat_queries', T('Repeated queries', '重复查询'), T('per question', '每题'), (0, 0.2), [0, 0.1, 0.2], lambda v: f'{v:.1f}' if v else '0')]
    p_ = float(PAIRED['hotpotqa_em_vs_shaped:all']['p'])
    verdict = [T(f'no significant change (p = {p_:.2f})', f'无显著差异（p = {p_:.2f}）'), T('−71% at step 200', '第 200 步减少 71%'),
               T('more groups give a learning signal', '更多组有学习信号')]
    for k, (key, title, unit, (lo, hi), ticks, fmt) in enumerate(specs):
        box = (56, 74 + k * 250, W - 70, 74 + k * 250 + 160) if narrow else (52 + k * pw, top, 52 + k * pw + pw - 82, H - 60)
        sx, sy = scale(0, 200, box[0], box[2]), scale(lo, hi, box[3], box[1])
        panel_title(svg, box[0], box[1] - 30, 'ab'[k], title, unit or None)
        svg.text(box[0], box[1] - 13, verdict[k], size=FS_TICK)
        frame(svg, box, sx, sy, [0, 100, 200], ticks, str, fmt, xtitle=T('step', '步'))
        for idx, d in ((2, sh), (1, em)):
            path_line(svg, d[key], sx, sy, idx)
            dots(svg, d[key], sx, sy, idx, r=2.2, ring=False)
            hits(svg, d[key], sx, sy, lambda x, y: f'step {x}: {y}')
        a_, b_ = em[key][-1][1], sh[key][-1][1]
        f = (lambda v: f'{v:.1f}') if key == 'em' else (lambda v: f'{v:.3f}')
        label_stack(svg, box[2] + 7, [(sy(a_), f(a_), 't-strong' if key == 'em' else ''), (sy(b_), f(b_), 't-strong' if key != 'em' else '')], min_gap=13)
        if key != 'em':
            ya, yb = sy(a_), sy(b_)
            xl = sx(200) - 7
            svg.line(xl, ya + 5, xl, yb - 5, 'leader')
    box = (56, 74 + 2 * 250, W - 70, 74 + 2 * 250 + 160) if narrow else (52 + 2 * pw, top, 52 + 2 * pw + pw - 60, H - 60)
    panel_title(svg, box[0], box[1] - 30, 'c', T('All-failed groups', '全错组'), T('during training', '训练中'))
    svg.text(box[0], box[1] - 13, verdict[2], size=FS_TICK)
    if horiz:
        sxh = scale(0, 30, box[0], box[2] - 30)
        frame(svg, box, sxh, None, [0, 10, 20, 30], [], lambda v: f'{v}%', grid='x')
        for j, (idx, v, lab) in enumerate(((1, 27, T('EM reward', 'EM 奖励')), (2, 4, T('shaped', '稠密奖励')))):
            yy = box[1] + 34 + j * 52
            svg.text(box[0], yy - 7, lab, cls='t-muted', size=FS_TICK)
            svg.mark(f'{lab[0]}: about {v}% of the groups had no successful answer', f'<path class="bar s{idx}" d="{hbar(box[0], yy, sxh(v), 14, 3)}"/>')
            svg.text(sxh(v) + 6, yy + 11, f'≈ {v}%', cls='t-strong', size=FS_LABEL)
        return svg
    sy = scale(0, 30, box[3], box[1])
    frame(svg, box, lambda v: v, sy, [], [0, 10, 20, 30], str, lambda v: f'{v}%')
    cw = (box[2] - box[0]) / 2
    for j, (idx, v, lab) in enumerate(((1, 27, T('EM reward', 'EM 奖励')), (2, 4, T('shaped', '稠密奖励')))):
        cx = box[0] + cw * (j + 0.5)
        hw = 11
        svg.mark(f'{lab[0]}: about {v}% of the groups had no successful answer',
                 f'<path class="bar s{idx}" d="M{cx - hw:.1f},{sy(0):.1f} V{sy(v) + 3:.1f} A3,3 0 0 1 {cx - hw + 3:.1f},{sy(v):.1f} H{cx + hw - 3:.1f} A3,3 0 0 1 {cx + hw:.1f},{sy(v) + 3:.1f} V{sy(0):.1f} Z"/>')
        svg.text(cx, sy(v) - 7, f'≈ {v}%', cls='t-strong', anchor='middle', size=FS_LABEL)
        svg.text(cx, box[3] + 16, lab, cls='t-faint', anchor='middle', size=FS_TICK)
    return svg


AES = {'opd-methods': lambda W: methods(W, 'aes'), 'opd-budget': budget, 'opd-training': training, 'opd-compute': compute,
       'scr-sft-rl': sft_rl, 'scr-vs-grpo': vs, 'scr-updates': updates, 'scr-hotpotqa': hotpot}
INNO = {'opd-methods': lambda W: methods(W, 'gain'), 'opd-budget': lambda W: budget(W, callout=True),
        'opd-training': lambda W: training(W, raw=True), 'opd-compute': lambda W: compute(W, spans=True),
        'scr-sft-rl': lambda W: sft_rl(W, same_order=True), 'scr-vs-grpo': lambda W: vs(W, means=True),
        'scr-updates': lambda W: updates(W, unseen=True), 'scr-hotpotqa': lambda W: hotpot(W, horiz=True)}
MERGED = {'opd-methods': lambda W: methods(W, 'aes'),
          'opd-budget': lambda W: budget(W, callout=True),
          'opd-training': lambda W: training(W, raw=True),
          'opd-compute': compute,
          'scr-sft-rl': lambda W: sft_rl(W, same_order=True),
          'scr-vs-grpo': vs,
          'scr-updates': updates,
          'scr-hotpotqa': hotpot}
NOTES = {
    'opd-methods': 'Final: aesthetic (baseline stems lighter so the distillation rows lead). The gain-from-base view reads well but prints derived numbers the page does not cite.',
    'opd-budget': 'Final: innovative, the reading the page text gives (Scaffold-OPD capped at 16k already leads OPD at 32k by 2.7), placed in the empty upper left with a leader.',
    'opd-training': 'Final: innovative: the raw per-step values as faint dots behind the five-step averages, so the smoothing the caption mentions is visible; plus the aesthetic leader ticks.',
    'opd-compute': 'Final: aesthetic (inset in ink, pipeline bars lighter). The stage strip along the axis collided with the base label and repeats the table.',
    'scr-sft-rl': 'Final: innovative (both panels in the seen order, so each family sits on one row across splits) with the aesthetic muting of the non-key gains.',
    'scr-vs-grpo': 'Final: aesthetic (McNemar named, larger squares). The dashed late-stage means sat on top of the blue curve.',
    'scr-updates': 'Final: aesthetic. Adding the unseen split as dashed lines doubled the lines and the labels collided.',
    'scr-hotpotqa': 'Final: aesthetic (readings in ink, slimmer bars). Horizontal bars left panel (c) unbalanced against the two line panels.',
}
