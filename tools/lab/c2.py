"""Chart round 2 (2026-11-17). BASE = round 1's merges (c1.MERGED).

Each chart again gets an aesthetic pass (details only) and an innovative one (a new component or reading), and the merge
goes on to round 3. NOTES records the reasons.
"""
import math

from c_kit import (ALF, FAM_NAMES, FS_LABEL, FS_TICK, HPQ, OPD, PAIRED, Svg, T, dots, frame, hbar, hits, key_lines,
                   label_stack, moving_avg, panel_title, path_line, per_lang, pick, polyline, run, scale, signed, text_w,
                   wash_between)
import c1

BASE = dict(c1.MERGED)


# ============================================================================ opd-methods
def methods(W, style='aes'):
    """style 'aes': bars with two small group headers; 'lolli': the same rows as lollipops (thin stem, dot)."""
    rows = c1._method_rows()
    narrow = W < 500
    pitch, bh = (42, 11) if narrow else (30, 11)
    x0, x1 = (12, W - 46) if narrow else (206, W - 104)
    top = 30
    groups = [(0, T('Baselines', '基线')), (3, T('On-policy distillation', '在线蒸馏'))]
    ys, heads = [], []
    y = top
    for i in range(len(rows)):
        for gi, gl in groups:
            if gi == i:
                if i:
                    y += 14
                heads.append((y - 6 + (0 if not narrow else 0), gl))
                y += 14
        ys.append(y + (18 if narrow else 0))
        y += pitch
    y_end = y - (pitch - bh) + (18 if narrow else 0) + 8
    H = y_end + 42
    svg = Svg(W, H, '4-benchmark math average by post-training method')
    sx = scale(0, 50, x0, x1)
    frame(svg, (x0, top - 14, x1, y_end), sx, None, [0, 10, 20, 30, 40, 50], [], grid='x',
          xtitle=T('4-benchmark average (MATH-500, AIME 2024–26)', '4 项平均分（MATH-500、AIME 2024–26）'))
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
        if style == 'lolli':
            svg.line(x0, cy, sx(v), cy, f'line l{idx}', 'stroke-width="2"' + (' opacity=".45"' if kind == 'variant' else ''))
            if kind == 'variant':
                svg.mark(f'{lab[0]}: {v:.2f}', f'<circle cx="{sx(v):.1f}" cy="{cy:.1f}" r="5" class="l1" fill="var(--bg)" stroke-width="2"/>')
            else:
                svg.mark(f'{lab[0]}: {v:.2f}', f'<circle class="dot s{idx}" cx="{sx(v):.1f}" cy="{cy:.1f}" r="{6 if strong else 5}"/>')
            svg.text(sx(v) + 11, cy + 4.2, f'{v:.1f}', cls='t-strong' if strong else '', size=FS_LABEL)
        else:
            d = hbar(x0, yb, sx(v), bh, 3) if kind != 'variant' else hbar(x0, yb + 0.6, sx(v) - 0.6, bh - 1.2, 3)
            svg.mark(f'{lab[0]}: {v:.2f}', f'<path class="{"bar " if kind != "variant" else ""}{cls}" d="{d}"/>')
            svg.text(sx(v) + 6, cy + 4.2, f'{v:.1f}', cls='t-strong' if strong else '', size=FS_LABEL)
    d = OPD['eval_avg4']
    xb = sx(d['takeover_conclude_40']) + (38 if narrow else 44)
    yo, yt = ys[3] + bh / 2, ys[4] + bh / 2
    svg.path(f'M{xb - 5:.1f},{yo:.1f} H{xb:.1f} V{yt:.1f} H{xb - 5:.1f}', 'leader')
    svg.text(xb + 5, (yo + yt) / 2 + 4.3, signed(d['takeover_conclude_40'] - d['opd_40']), cls='tx-blue', size=FS_LABEL, weight=700)
    return svg


# ============================================================================ opd-budget
def budget(W, compare=False):
    """Round-1 merge with the paired-gap values at 8k and 16k back in panel (b). compare=True adds the reading the page
    text gives: Scaffold-OPD capped at 16k already leads OPD's full 32k by 2.7 points."""
    b, xs = c1._budget()
    narrow = W < 500
    short = narrow
    kfmt = c1.kfmt
    x0, x1 = (44, W - 52) if narrow else (64, W - 150)
    hA, hB, hC, gap = (160, 78, 74, 36) if not narrow else (150, 78, 74, 40)
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
    if not narrow:
        svg.text(sx(14.5), A[1] - 12, '16k → 32k', cls='t-faint', anchor='middle', size=FS_TICK)
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
    if compare:
        k16 = b['tokens'].index(16384)
        o32, s16 = b['opd_40'][-1], b['takeover_40'][k16]
        svg.line(sx(xs[k16]) - 2, syA(o32), sx(15), syA(o32), 'leader', 'stroke-dasharray="3 3"')
        xb = sx(xs[k16]) - 8
        svg.path(f'M{xb + 4:.1f},{syA(s16):.1f} H{xb:.1f} V{syA(o32):.1f} H{xb + 4:.1f}', 'leader')
        lab = T(f'+{s16 - o32:.1f} vs OPD at 32k', f'比 OPD 32k 高 {s16 - o32:.1f}')
        svg.text(xb - 5, (syA(s16) + syA(o32)) / 2 + 4, lab, cls='tx-blue', anchor='end', size=FS_TICK, weight=600)
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
def training(W, third=False):
    """Round-1 merge with the 100–150 token level the caption cites drawn as a faint band in (b). third=True adds a
    panel (c): the share of Scaffold-OPD answers that got any takeover at all."""
    t, tk, op, teach = c1._train()
    narrow = W < 500
    if narrow:
        H = 520 if not third else 740
        bA, bB = (48, 62, W - 70, 222), (48, 320, W - 70, 470)
        bC = (48, 560, W - 70, 690)
    elif third:
        H = 300
        pw = (W - 40) / 3
        bA = (48, 62, 48 + pw - 74, H - 52)
        bB = (48 + pw + 14, 62, 48 + 2 * pw - 58, H - 52)
        bC = (48 + 2 * pw + 26, 62, W - 46, H - 52)
    else:
        H = 300
        bA, bB = (56, 62, W / 2 - 74, H - 52), (W / 2 + 54, 62, W - 64, H - 52)
    svg = Svg(W, H, 'Response length, and the teacher-written tokens per answer in Scaffold-OPD')
    key_lines(svg, bA[0], 18, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    panel_title(svg, bA[0], bA[1] - 16, 'a', T('Response length', '回答长度'), T('tokens', 'token'))
    c1._length_panel(svg, bA, tk, op)
    panel_title(svg, bB[0], bB[1] - 16, 'b', T('Teacher tokens per answer', '每条回答的老师 token') if not third else T('Teacher tokens / answer', '老师 token / 条'),
                'Scaffold-OPD' if not third else None)
    sx, sy = scale(0, 60, bB[0], bB[2]), scale(0, 200, bB[3], bB[1])
    svg.rect(bB[0], sy(150), bB[2] - bB[0], sy(100) - sy(150), 'band')
    frame(svg, bB, sx, sy, [0, 20, 40, 60], [0, 50, 100, 150, 200], xtitle=T('training step', '训练步'))
    area = polyline(teach, sx, sy) + f' L{sx(teach[-1][0]):.1f},{sy(0):.1f} L{sx(teach[0][0]):.1f},{sy(0):.1f} Z'
    svg.path(area, 'fl-green', 'opacity=".55"')
    path_line(svg, teach, sx, sy, 5)
    svg.circle(sx(teach[-1][0]), sy(teach[-1][1]), 3.2, 'dot s5', 'stroke-width="1.5"')
    hits(svg, teach, sx, sy, lambda x, y: f'step {x}: {y:.0f} teacher tokens per answer')
    s0 = 100 * c1._window(t, 1, 5, 'teacher_token_ratio')
    s1 = 100 * c1._window(t, 56, 60, 'teacher_token_ratio')
    if not third:
        svg.text(bB[2] - 2, sy(150) - 6, '100–150', cls='t-faint', anchor='end', size=10.5)
    svg.text(sx(1), sy(teach[0][1]) - 12, T(f'{s0:.0f}% of the tokens', f'占全部 token {s0:.0f}%'), size=FS_TICK)
    svg.text(sx(60), sy(teach[-1][1]) - 14, T(f'{s1:.0f}% of the tokens', f'占全部 token {s1:.0f}%'), anchor='end', size=FS_TICK)
    if not narrow and not third:
        svg.text(bB[2] + 8, sy(teach[-1][1]) + 4, f'{teach[-1][1]:.0f}', cls='t-strong', size=FS_LABEL)
    if third:
        aw = moving_avg([(s, 100 * v) for s, v in zip(t['step'], t['answers_with_takeover']) if v is not None and s != 19])
        panel_title(svg, bC[0], bC[1] - 16, 'c', T('Answers with a takeover', '有接管的回答'), '%')
        sxc, syc = scale(0, 60, bC[0], bC[2]), scale(0, 100, bC[3], bC[1])
        frame(svg, bC, sxc, syc, [0, 20, 40, 60], [0, 50, 100], xtitle=T('training step', '训练步'))
        path_line(svg, aw, sxc, syc, 4)
        svg.circle(sxc(aw[-1][0]), syc(aw[-1][1]), 3.2, 'dot s4', 'stroke-width="1.5"')
        hits(svg, aw, sxc, syc, lambda x, y: f'step {x}: {y:.0f}% of answers had a takeover')
        svg.text(sxc(1), syc(aw[0][1]) - 10, f'{aw[0][1]:.0f}%', cls='t-strong', size=FS_TICK)
        svg.text(sxc(60), syc(aw[-1][1]) - 10, f'{aw[-1][1]:.0f}%', cls='t-strong', anchor='end', size=FS_TICK)
    return svg


# ============================================================================ opd-compute
def compute(W, inset=False):
    """Round-1 merge, tightened: shorter dimension label, the stage labels on the side away from the other line, and on
    phones the last label set inside the plot. inset=True adds a small bar chart of points gained per GPU-hour."""
    pts, alone = c1._compute_data()
    narrow = W < 500
    H = 330 if not narrow else 360
    box = (46, 44, W - (28 if narrow else 118), H - 44)
    svg = Svg(W, H, 'Score against cumulative training GPU-hours: the full pipeline and Scaffold-OPD alone')
    key_lines(svg, box[0], 16, [(2, T('full pipeline', '全流程')), (1, T('Scaffold-OPD alone', '只做 Scaffold-OPD'))])
    sx, sy = scale(0, 56, box[0], box[2]), scale(20, 52, box[3], box[1])
    frame(svg, box, sx, sy, [0, 10, 20, 30, 40, 50], [20, 30, 40, 50], xtitle=T('cumulative training GPU-hours (2 × A100)', '累计训练卡时（2 × A100）'))
    svg.text(box[0] - 7, box[1] - 10, T('4-benchmark average', '4 项平均分'), cls='t-muted', size=FS_TICK)
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
    names = [T('base', '基座'), T('+ SFT'), T('+ Scaffold-OPD'), T('+ GRPO on failures', '+ 错题回流 GRPO')]
    for k, ((x, y), lab) in enumerate(zip(pts, names)):
        svg.mark(f'{lab[0]}: {y:.2f} after {x:.1f} GPU-hours', f'<circle class="dot s2" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4"/>')
        text = (f'{lab[0]} {y:.1f}', f'{lab[1]} {y:.1f}')
        if k == 0:
            svg.text(sx(x) + 8, sy(y) + 15, text, cls='t-muted', size=FS_TICK)
        elif k == 3:
            svg.text(sx(x) - 4, sy(y) + 18, text, anchor='end', size=FS_TICK)
        else:
            svg.text(sx(x) + 6, sy(y) + 17, text, size=FS_TICK)
    svg.mark(f'Scaffold-OPD alone: {alone[1]:.2f} after {alone[0]:.1f} GPU-hours',
             f'<circle class="dot s1" cx="{sx(alone[0]):.1f}" cy="{sy(alone[1]):.1f}" r="4.5"/>')
    svg.text(sx(alone[0]) + 9, sy(alone[1]) + 16, T(f'Scaffold-OPD alone {alone[1]:.1f}', f'只做 Scaffold-OPD {alone[1]:.1f}'), cls='t-strong', size=FS_TICK)
    if inset and not narrow:
        rates = [(T('Scaffold-OPD alone', '只做 Scaffold-OPD'), (alone[1] - pts[0][1]) / alone[0], 's1'),
                 (T('pipeline: SFT', '全流程：SFT'), (pts[1][1] - pts[0][1]) / (pts[1][0] - pts[0][0]), 's2'),
                 (T('pipeline: Scaffold-OPD', '全流程：Scaffold-OPD'), (pts[2][1] - pts[1][1]) / (pts[2][0] - pts[1][0]), 's2'),
                 (T('pipeline: GRPO', '全流程：GRPO'), (pts[3][1] - pts[2][1]) / (pts[3][0] - pts[2][0]), 's2')]
        ix0, ix1, iy = sx(31.5), sx(50), sy(35)
        svg.text(sx(18.5), iy - 4, T('points per GPU-hour', '每卡时提分'), cls='t-muted', size=FS_TICK)
        sxi = scale(0, 1.7, ix0, ix1)
        for j, (lab, r_, cls) in enumerate(rates):
            yy = iy + 8 + j * 15
            svg.text(ix0 - 8, yy + 8, lab, cls='', anchor='end', size=10.5)
            svg.mark(f'{lab[0]}: {r_:.2f} points per GPU-hour', f'<path class="bar {cls}" d="{hbar(ix0, yy, sxi(r_), 9, 2)}"{" opacity=.75" if cls == "s2" else ""}/>')
            svg.text(sxi(r_) + 5, yy + 8, f'{r_:.2f}', cls='t-strong' if j == 0 else '', size=10.5)
    return svg


# ============================================================================ scr-sft-rl
def sft_rl(W, combined=False):
    """Progress bars (gray = success after SFT, blue = what 100 RL steps add). combined=True puts seen and unseen in
    one panel, two thin bars per task family, so each family is named once."""
    narrow = W < 500
    if not combined:
        return sft_rl_polish(W)
    a_s, b_s, gain_s, order = c1._fam('seen')
    a_u, b_u, gain_u, _ = c1._fam('unseen')
    rowh = 34 if not narrow else 40
    top = 62
    x0 = 140 if not narrow else 12
    x1 = W - (120 if not narrow else 64)
    H = top + rowh * len(order) + 52 + (len(order) * 14 if narrow else 0)
    svg = Svg(W, H, 'ALFWorld success by task family after SFT and the gain from 100 RL steps, seen and unseen')
    def keys(i):
        xx = 16 if not narrow else 8
        for cls, s, op in (('s3', pick(T('after SFT', 'SFT 后'), i), ' opacity=".55"'), ('s1', pick(T('gain from 100 RL steps', '100 步 RL 的提升'), i), '')):
            svg.add(f'<rect x="{xx:.1f}" y="9" width="10" height="10" rx="2" class="{cls}"{op}/>')
            svg.text(xx + 15, 18, s, size=FS_LABEL)
            xx += 15 + text_w(s, FS_LABEL) + 18
    per_lang(svg, keys)
    sx = scale(0, 100, x0, x1)
    y_end = top + rowh * len(order) + (len(order) * 14 if narrow else 0) - 6
    frame(svg, (x0, top - 14, x1, y_end), sx, None, [0, 25, 50, 75, 100], [], grid='x', xtitle=T('success, %', '成功率，%'))
    svg.text(x1 + 46, top - 20, 'seen', cls='t-faint', anchor='end', size=10.5)
    svg.text(x1 + 88, top - 20, 'unseen', cls='t-faint', anchor='end', size=10.5)
    y = top
    for fam in order:
        key = fam == 'pick_two_obj_and_place'
        if narrow:
            svg.text(x0, y + 1, FAM_NAMES[fam], cls='t-strong' if key else '', size=FS_TICK)
            y += 12
        if key:
            svg.rect(x0 - (130 if not narrow else 6), y - 6, (x1 - x0) + (130 if not narrow else 6) + 96, 26, 'band', rx=4)
        if not narrow:
            svg.text(x0 - 12, y + 11, FAM_NAMES[fam], cls='t-strong' if key else '', anchor='end', size=FS_LABEL)
        for j, (a, b, gain, lab) in enumerate(((a_s, b_s, gain_s, 'seen'), (a_u, b_u, gain_u, 'unseen'))):
            (sa, n), (sb, _) = a[fam], b[fam]
            pa, pb = 100 * sa / n, 100 * sb / n
            yy = y + j * 9
            svg.mark(f'{FAM_NAMES[fam][0]}, {lab}: {sa}/{n} after SFT', f'<path class="bar s3" opacity=".55" d="{hbar(x0, yy, sx(pa), 7, 1.5)}"/>')
            svg.mark(f'{FAM_NAMES[fam][0]}, {lab}: {sb}/{n} after RL',
                     f'<rect class="s1" x="{sx(pa) + 1:.1f}" y="{yy:.1f}" width="{max(sx(pb) - sx(pa) - 1, 1):.1f}" height="7" rx="1.5"{" opacity=.7" if j else ""}/>')
            svg.text(x1 + 46 + 42 * j, y + 11, f'+{gain[fam]:.0f}', cls='tx-blue' if key else '', anchor='end', size=FS_LABEL, weight=700 if key else None)
        y += rowh
    return svg


def sft_rl_polish(W, same_order=False):
    """Progress bars polished: thinner (8 px), a 2 px gap between the SFT part and the RL gain so the two read as two
    quantities, the gain column aligned on the last digit, and the task counts beside the key row's gain.
    same_order=True orders both panels like the seen one, so each family sits on the same row in both."""
    narrow = W < 500
    if narrow:
        H = 510
        panels = [('seen', (100, 72, W - 56, 232)), ('unseen', (100, 318, W - 56, 478))]
    else:
        H = 296
        panels = [('seen', (128, 70, W / 2 - 56, H - 50)), ('unseen', (W / 2 + 96, 70, W - 52, H - 50))]
    svg = Svg(W, H, 'ALFWorld success by task family after SFT and the gain from 100 RL steps, sorted by the gain')
    def keys(i):
        xx = 16 if not narrow else 8
        for cls, s, op in (('s3', pick(T('after SFT', 'SFT 后'), i), ' opacity=".55"'), ('s1', pick(T('gain from 100 RL steps', '100 步 RL 的提升'), i), '')):
            svg.add(f'<rect x="{xx:.1f}" y="9" width="10" height="10" rx="2" class="{cls}"{op}/>')
            svg.text(xx + 15, 18, s, size=FS_LABEL)
            xx += 15 + text_w(s, FS_LABEL) + 18
    per_lang(svg, keys)
    seen_order = c1._fam('seen')[3]
    for k, (split, box) in enumerate(panels):
        a, b, gain, order = c1._fam(split)
        if same_order:
            order = seen_order
        sx = scale(0, 100, box[0], box[2])
        panel_title(svg, box[0], box[1] - 20, 'ab'[k], T(split, split), T('success, %', '成功率，%'))
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
            bh_ = 8
            svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sa}/{n} after SFT', f'<path class="bar s3" opacity=".55" d="{hbar(box[0], y - bh_ / 2, max(sx(pa) - 1, box[0] + 1), bh_, 2)}"/>')
            svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sb}/{n} after RL', f'<path class="bar s1" d="{hbar(sx(pa) + 1, y - bh_ / 2, max(sx(pb), sx(pa) + 3), bh_, 2)}"/>')
            svg.text(box[2] + 40, y + 4, f'+{gain[fam]:.0f}', cls='tx-blue' if key else '', anchor='end', size=FS_LABEL, weight=700 if key else None)
            if key:
                svg.text((sx(pa) + sx(pb)) / 2, y + 16, f'{sa}/{n} → {sb}/{n}', cls='t-muted', anchor='middle', size=10.5)
    return svg


# ============================================================================ scr-vs-grpo
def vs(W, shade=False):
    """Round-1 merge (curves and a win strip) with squares aligned to the steps and the text tightened. shade=True
    grades each square by the size of the lead (under 5, 5–15, over 15 points)."""
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
        svg.text(A[2], A[1] - 16, f'p = {c1._pfmt(p_)}', cls='t-strong' if p_ < 0.05 else 't-faint', anchor='end', size=FS_TICK)
        svg.rect(sx(160), A[1], sx(200) - sx(160), A[3] - A[1], 'band')
        frame(svg, A, sx, sy, [0, 50, 100, 150, 200], [0, 25, 50, 75, 100])
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
        ys = A[3] + 32
        ahead = 0
        sq = 7.5
        for (s_, a_), (_, b_) in zip(g[name], r[name]):
            d_ = a_ - b_
            cls = 's1' if d_ > 0.05 else ('s2' if d_ < -0.05 else 's3')
            ahead += d_ > 0.05
            op = ''
            if shade and cls != 's3':
                op = ' opacity="' + ('.35' if abs(d_) < 5 else ('.65' if abs(d_) < 15 else '1')) + '"'
            svg.mark(f'step {s_}: {signed(d_)} points', f'<rect class="{cls}" x="{sx(s_) - sq / 2:.1f}" y="{ys:.1f}" width="{sq}" height="{sq}" rx="1.5"{op}/>')
        svg.text(A[0], ys + 24, T(f'StepCredit-RL ahead at {ahead} of {len(g[name])} validations', f'{len(g[name])} 次验证中 StepCredit-RL 领先 {ahead} 次'), cls='t-muted', size=FS_TICK)
        if shade and k == 1 and not narrow:
            def lk(i):
                xx = A[2] - 150
                svg.text(xx - 6, ys + 24, pick(T('lead:', '领先：'), i), cls='t-faint', anchor='end', size=10.5)
                for o, s in (('.35', '<5'), ('.65', '5–15'), ('1', '>15')):
                    svg.add(f'<rect x="{xx:.1f}" y="{ys + 16:.1f}" width="8" height="8" rx="1.5" class="s1" opacity="{o}"/>')
                    svg.text(xx + 11, ys + 24, s, cls='t-faint', size=10.5)
                    xx += 11 + text_w(s, 10.5) + 10
            per_lang(svg, lk)
    return svg


# ============================================================================ scr-updates
def updates(W, inset=False):
    """Round-1 merge with the step tags moved off the lines, percentages at the ends, and the comparison bracket labelled
    with both levels. inset=True adds a small by-step view in the empty lower right."""
    four, one = c1._upd()
    narrow = W < 500
    H = 330 if not narrow else 360
    box = (48, 50, W - (92 if not narrow else 64), H - 50)
    svg = Svg(W, H, 'Seen success against wall-clock hours for four updates per step and for one, with training steps marked')
    key_lines(svg, box[0], 18, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
    sx, sy = scale(0, 30, box[0], box[2]), scale(0, 100, box[3], box[1])
    frame(svg, box, sx, sy, [0, 5, 10, 15, 20, 25, 30], [0, 25, 50, 75, 100], xtitle=T('hours on 2 × A100', '耗时（2 × A100，小时）'))
    svg.text(box[0] - 7, box[1] - 12, T('seen success, %', 'seen 成功率，%'), cls='t-muted', size=FS_TICK)
    for idx, rows, dy in ((3, one, 16), (1, four, -9)):
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
    svg.text(sx(e4[2]) + 8, sy(e4[1]) + 4, T(f'step 100 · {e4[1]:.1f}%', f'第 100 步 · {e4[1]:.1f}%'), cls='t-strong', size=FS_TICK)
    svg.text(sx(e1[2]) + 8, sy(e1[1]) + 4, T(f'step 150 · {e1[1]:.1f}%', f'第 150 步 · {e1[1]:.1f}%'), size=FS_TICK) if narrow else \
        svg.text(sx(e1[2]) + 8, sy(e1[1]) + 4, f'{e1[1]:.1f}%', size=FS_LABEL)
    if not narrow:
        svg.text(sx(e1[2]), sy(e1[1]) - 10, T('step 150', '第 150 步'), cls='t-faint', anchor='middle', size=10.5)
    yb = sy(90)
    svg.path(f'M{sx(e4[2]):.1f},{yb + 5:.1f} V{yb:.1f} H{sx(e1[2]):.1f} V{yb + 5:.1f}', 'leader')
    svg.text((sx(e4[2]) + sx(e1[2])) / 2, yb - 6, T(f'a higher level about {e1[2] - e4[2]:.0f} h sooner', f'约早 {e1[2] - e4[2]:.0f} 小时达到更高水平'),
             cls='t-muted', anchor='middle', size=FS_TICK)
    if inset and not narrow:
        ib = (sx(17.5), sy(42), sx(29.5), sy(6))
        svg.rect(ib[0] - 30, ib[1] - 22, ib[2] - ib[0] + 38, ib[3] - ib[1] + 44, 'box', rx=6)
        svg.text(ib[0] - 22, ib[1] - 8, T('by training step', '按训练步'), cls='t-muted', size=10.5)
        sxi, syi = scale(0, 150, ib[0], ib[2]), scale(0, 100, ib[3], ib[1])
        svg.line(ib[0], ib[3], ib[2], ib[3], 'axis')
        for v in (0, 50, 100, 150):
            svg.text(sxi(v), ib[3] + 12, str(v), cls='t-faint', anchor='middle', size=9.5)
        for idx, rows in ((3, one), (1, four)):
            path_line(svg, [(st, s) for st, s, _ in rows], sxi, syi, idx, width=1.6)
    return svg


# ============================================================================ scr-hotpotqa
def hotpot(W, verdicts=False):
    """Round-1 merge with bar labels under the bars and a calmer axis. verdicts=True adds a one-line reading under each
    panel title: no significant change in EM, −71% repeated queries, far fewer groups without a learning signal."""
    em, sh = c1._hpq()
    narrow = W < 500
    H = (296 if not verdicts else 312) if not narrow else 820
    top = 68 if not verdicts else 84
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
        panel_title(svg, box[0], box[1] - (16 if not verdicts else 30), 'ab'[k], title, unit or None)
        if verdicts:
            svg.text(box[0], box[1] - 13, verdict[k], cls='t-muted', size=FS_TICK)
        frame(svg, box, sx, sy, [0, 100, 200], ticks, str, fmt, xtitle=T('step', '步'))
        for idx, d in ((2, sh), (1, em)):
            path_line(svg, d[key], sx, sy, idx)
            dots(svg, d[key], sx, sy, idx, r=2.2, ring=False)
            hits(svg, d[key], sx, sy, lambda x, y: f'step {x}: {y}')
        a_, b_ = em[key][-1][1], sh[key][-1][1]
        f = (lambda v: f'{v:.1f}') if key == 'em' else (lambda v: f'{v:.3f}')
        label_stack(svg, box[2] + 7, [(sy(a_), f(a_), 't-strong' if key == 'em' else ''), (sy(b_), f(b_), 't-strong' if key != 'em' else '')], min_gap=13)
        if key == 'em' and not verdicts:
            svg.text(box[2], sy(lo) - 8, f'McNemar p = {p_:.2f}', cls='t-faint', anchor='end', size=10.5)
        if key != 'em':
            ya, yb = sy(a_), sy(b_)
            xl = sx(200) - 7
            svg.line(xl, ya + 5, xl, yb - 5, 'leader')
            if not verdicts:
                svg.text(xl - 5, ya + (yb - ya) * 0.35 + 4, signed(100 * (b_ - a_) / a_, 0) + '%', cls='t-strong', anchor='end', size=FS_LABEL)
    box = (56, 74 + 2 * 250, W - 70, 74 + 2 * 250 + 160) if narrow else (52 + 2 * pw, top, 52 + 2 * pw + pw - 60, H - 60)
    panel_title(svg, box[0], box[1] - (16 if not verdicts else 30), 'c', T('All-failed groups', '全错组'), T('during training', '训练中'))
    if verdicts:
        svg.text(box[0], box[1] - 13, verdict[2], cls='t-muted', size=FS_TICK)
    sy = scale(0, 30, box[3], box[1])
    frame(svg, box, lambda v: v, sy, [], [0, 10, 20, 30], str, lambda v: f'{v}%')
    cw = (box[2] - box[0]) / 2
    for j, (idx, v, lab) in enumerate(((1, 27, T('EM reward', 'EM 奖励')), (2, 4, T('shaped', '稠密奖励')))):
        cx = box[0] + cw * (j + 0.5)
        hw = 12
        svg.mark(f'{lab[0]}: about {v}% of the groups had no successful answer',
                 f'<path class="bar s{idx}" d="M{cx - hw:.1f},{sy(0):.1f} V{sy(v) + 3:.1f} A3,3 0 0 1 {cx - hw + 3:.1f},{sy(v):.1f} H{cx + hw - 3:.1f} A3,3 0 0 1 {cx + hw:.1f},{sy(v) + 3:.1f} V{sy(0):.1f} Z"/>')
        svg.text(cx, sy(v) - 7, f'≈ {v}%', cls='t-strong', anchor='middle', size=FS_LABEL)
        svg.text(cx, box[3] + 16, lab, cls='t-faint', anchor='middle', size=FS_TICK)
    return svg


AES = {'opd-methods': lambda W: methods(W, 'aes'), 'opd-budget': budget, 'opd-training': training, 'opd-compute': compute,
       'scr-sft-rl': sft_rl, 'scr-vs-grpo': vs, 'scr-updates': updates, 'scr-hotpotqa': hotpot}
INNO = {'opd-methods': lambda W: methods(W, 'lolli'), 'opd-budget': lambda W: budget(W, compare=True),
        'opd-training': lambda W: training(W, third=True), 'opd-compute': lambda W: compute(W, inset=True),
        'scr-sft-rl': lambda W: sft_rl(W, combined=True), 'scr-vs-grpo': lambda W: vs(W, shade=True),
        'scr-updates': lambda W: updates(W, inset=True), 'scr-hotpotqa': lambda W: hotpot(W, verdicts=True)}
def training_merged(W):
    """The aesthetic version with the 100–150 level drawn as two dashed guides instead of a band over the green area."""
    svg = training(W)
    narrow = W < 500
    bB = (48, 320, W - 70, 470) if narrow else (W / 2 + 54, 62, W - 64, 300 - 52)
    sy = scale(0, 200, bB[3], bB[1])
    band = f'<rect x="{bB[0]:.1f}" y="{sy(150):.1f}" width="{bB[2] - bB[0]:.1f}" height="{sy(100) - sy(150):.1f}" rx="0" class="band"/>'
    svg.parts = [p_ for p_ in svg.parts if p_ != band]
    for v in (100, 150):
        svg.parts.insert(1, f'<line x1="{bB[0]:.1f}" y1="{sy(v):.1f}" x2="{bB[2]:.1f}" y2="{sy(v):.1f}" class="leader" stroke-dasharray="3 3"/>')
    return svg


def compute_merged(W):
    """The aesthetic version with the last stage label back on the right on desktop, and the points-per-GPU-hour inset
    placed in the empty lower right, below both lines."""
    pts, alone = c1._compute_data()
    narrow = W < 500
    H = 330 if not narrow else 360
    box = (46, 44, W - (28 if narrow else 118), H - 44)
    svg = Svg(W, H, 'Score against cumulative training GPU-hours: the full pipeline and Scaffold-OPD alone, and the points gained per GPU-hour')
    key_lines(svg, box[0], 16, [(2, T('full pipeline', '全流程')), (1, T('Scaffold-OPD alone', '只做 Scaffold-OPD'))])
    sx, sy = scale(0, 56, box[0], box[2]), scale(20, 52, box[3], box[1])
    frame(svg, box, sx, sy, [0, 10, 20, 30, 40, 50], [20, 30, 40, 50], xtitle=T('cumulative training GPU-hours (2 × A100)', '累计训练卡时（2 × A100）'))
    svg.text(box[0] - 7, box[1] - 10, T('4-benchmark average', '4 项平均分'), cls='t-muted', size=FS_TICK)
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
    names = [T('base', '基座'), T('+ SFT'), T('+ Scaffold-OPD'), T('+ GRPO on failures', '+ 错题回流 GRPO')]
    for k, ((x, y), lab) in enumerate(zip(pts, names)):
        svg.mark(f'{lab[0]}: {y:.2f} after {x:.1f} GPU-hours', f'<circle class="dot s2" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4"/>')
        text = (f'{lab[0]} {y:.1f}', f'{lab[1]} {y:.1f}')
        if k == 0:
            svg.text(sx(x) + 8, sy(y) + 15, text, cls='t-muted', size=FS_TICK)
        elif k == 3:
            if narrow:
                svg.text(sx(x) - 4, sy(y) + 18, text, anchor='end', size=FS_TICK)
            else:
                svg.text(sx(x) + 8, sy(y) + 16, text, size=FS_TICK)
        else:
            svg.text(sx(x) + 6, sy(y) + 17, text, size=FS_TICK)
    svg.mark(f'Scaffold-OPD alone: {alone[1]:.2f} after {alone[0]:.1f} GPU-hours',
             f'<circle class="dot s1" cx="{sx(alone[0]):.1f}" cy="{sy(alone[1]):.1f}" r="4.5"/>')
    svg.text(sx(alone[0]) + 9, sy(alone[1]) + 16, T(f'Scaffold-OPD alone {alone[1]:.1f}', f'只做 Scaffold-OPD {alone[1]:.1f}'), cls='t-strong', size=FS_TICK)
    if not narrow:
        rates = [(T('Scaffold-OPD alone', '只做 Scaffold-OPD'), (alone[1] - pts[0][1]) / alone[0], 's1'),
                 (T('pipeline · SFT', '全流程 · SFT'), (pts[1][1] - pts[0][1]) / (pts[1][0] - pts[0][0]), 's2'),
                 (T('pipeline · Scaffold-OPD', '全流程 · Scaffold-OPD'), (pts[2][1] - pts[1][1]) / (pts[2][0] - pts[1][0]), 's2'),
                 (T('pipeline · GRPO', '全流程 · GRPO'), (pts[3][1] - pts[2][1]) / (pts[3][0] - pts[2][0]), 's2')]
        ix0, ix1 = sx(38.5), sx(53)
        iy = sy(33.5)
        svg.text(ix0 - 132, iy, T('points gained per GPU-hour', '每卡时提分'), cls='t-muted', size=FS_TICK)
        sxi = scale(0, 1.7, ix0, ix1)
        for j, (lab, r_, cls) in enumerate(rates):
            yy = iy + 8 + j * 15
            svg.text(ix0 - 8, yy + 8, lab, anchor='end', size=10.5)
            svg.mark(f'{lab[0]}: {r_:.2f} points per GPU-hour', f'<path class="bar {cls}" d="{hbar(ix0, yy, sxi(r_), 9, 2)}"/>')
            svg.text(sxi(r_) + 5, yy + 8, f'{r_:.2f}', cls='t-strong' if j == 0 else '', size=10.5)
    return svg


MERGED = {'opd-methods': lambda W: methods(W, 'lolli'),
          'opd-budget': budget,
          'opd-training': training_merged,
          'opd-compute': compute_merged,
          'scr-sft-rl': sft_rl_polish,
          'scr-vs-grpo': vs,
          'scr-updates': updates,
          'scr-hotpotqa': lambda W: hotpot(W, verdicts=True)}
NOTES = {
    'opd-methods': 'Merged: innovative lollipops (less ink than bars, same reading) with the aesthetic group headers.',
    'opd-budget': 'Merged: aesthetic (gap values at 8k and 16k back). The 16k-vs-32k callout of the innovative version collided with the lines; it returns in round 3 with a leader into empty space.',
    'opd-training': 'Merged: aesthetic, with the 100–150 level as two dashed guides; the third panel (answers with a takeover) is not cited on the page and shrank the others.',
    'opd-compute': 'Merged: aesthetic plus the innovative points-per-GPU-hour inset, moved to the empty lower right; the last stage label is back on the right on desktop.',
    'scr-sft-rl': 'Merged: aesthetic (2 px gap between SFT and RL parts, thinner bars). The one-panel version with two thin bars per family was harder to read.',
    'scr-vs-grpo': 'Merged: aesthetic (squares aligned with the steps, the overlapping axis note removed). Shading the squares by lead size added a legend and noise.',
    'scr-updates': 'Merged: aesthetic (step tags off the lines, both end levels labelled). The by-step inset covered part of a curve.',
    'scr-hotpotqa': 'Merged: innovative one-line readings under each title (no significant change, −71%, more groups give a signal).',
}
