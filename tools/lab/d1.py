"""Chart cycle 2, round 1 (2026-11-17). The pages show every figure in English only, so this cycle judges English.

BASE   = c_final.FINAL (the finals of the first 11-17 cycle).
AES    = polish only: three type sizes (11 / 12 / 13), text in ink tones (no coloured numbers), the same span and bracket
         marks in every chart, titles and keys on one left edge, no letter-spacing, no redundant guides.
INNO   = a new idea per chart (restructuring allowed).
MERGED = what goes on to round 2; NOTES give the reasons.
"""
from d_kit import (FAM_NAMES, FS_LABEL, FS_TICK, OPD, PAIRED, ALF, Svg, T, bracket, dots, frame, hbar, hits,
                   key_lines, label_stack, moving_avg, panel_title, path_line, per_lang, pick, polyline, scale, seg_sign,
                   signed, soft_box, span, text_w, wash_between)
import figures  # noqa: E402,F401  figures -> c_final -> c3 -> c2 -> c1 -> figures: load figures first, or c2 sees a half-built c1
import c1  # noqa: E402
import c_final  # noqa: E402

BASE = dict(c_final.FINAL)


# ============================================================================ opd-methods
def methods(W, table=False, keyband=False):
    """Lollipops of the 4-benchmark average. table=True: each value sits in an aligned column right after its label,
    so name and number read together and the dots stay free of text. keyband=True: a soft band behind the
    Scaffold-OPD row, the same key-row band as in the ALFWorld task-family chart."""
    rows = c1._method_rows()
    d = OPD['eval_avg4']
    narrow = W < 500
    pitch, bh = (42, 11) if narrow else (30, 11)
    if narrow:
        x0, x1 = (44 if table else 12), W - 46
    else:
        x0, x1 = (236 if table else 206), W - (96 if table else 104)
    top = 30
    heads_at = {0: T('Baselines', '基线'), 3: T('On-policy distillation', '在线蒸馏')}
    ys, heads, y = [], [], top
    for i in range(len(rows)):
        if i in heads_at:
            if i:
                y += 14
            heads.append((y - 6, heads_at[i]))
            y += 14
        ys.append(y + (18 if narrow else 0))
        y += pitch
    y_end = y - (pitch - bh) + (18 if narrow else 0) + 8
    H = y_end + 42
    svg = Svg(W, H, '4-benchmark math average by post-training method')
    sx = scale(0, 50, x0, x1)
    i_ours = [k for k, r in enumerate(rows) if r[3] == 'ours'][0]
    if keyband:
        cy = ys[i_ours] + bh / 2
        if narrow:
            svg.rect(4, cy - 30, W - 8, 42, 'band', rx=4)
        else:
            svg.rect(8, cy - pitch / 2 + 2, W - 16, pitch - 4, 'band', rx=4)
    frame(svg, (x0, top - 14, x1, y_end), sx, None, [0, 10, 20, 30, 40, 50], [], grid='x',
          xtitle=T('4-benchmark average (MATH-500, AIME 2024–26)', '4 项平均分（MATH-500、AIME 2024–26）'))
    lab_x = x0 - (52 if table else 12)
    for hy, gl in heads:
        if narrow:
            svg.text(12, hy, gl, cls='t-muted', size=FS_TICK)
        else:
            svg.text(lab_x, hy, gl, cls='t-muted', anchor='end', size=FS_TICK)
    for (lab, v, cls, kind), yb in zip(rows, ys):
        strong = kind == 'ours'
        if kind == 'variant':
            lab = T('↳ ' + lab[0], '↳ ' + lab[1])
        tcls = 't-strong' if strong else ('t-muted' if kind == 'variant' else '')
        cy = yb + bh / 2
        if narrow:
            svg.text(12 + (12 if kind == 'variant' else 0), yb - 6, lab, cls=tcls, size=FS_LABEL)
        else:
            svg.text(lab_x, cy + 4.2, lab, cls=tcls, anchor='end', size=FS_LABEL)
        idx = {'s3': 3, 's2': 2, 's1': 1, 'pn-blue': 1}[cls]
        op = ' opacity=".5"' if kind == 'ref' else (' opacity=".45"' if kind == 'variant' else '')
        svg.line(x0, cy, sx(v), cy, f'line l{idx}', 'stroke-width="2"' + op)
        if kind == 'variant':
            svg.mark(f'{lab[0]}: {v:.2f}', f'<circle cx="{sx(v):.1f}" cy="{cy:.1f}" r="5" class="l1" fill="var(--bg)" stroke-width="2"/>')
        else:
            svg.mark(f'{lab[0]}: {v:.2f}', f'<circle class="dot s{idx}" cx="{sx(v):.1f}" cy="{cy:.1f}" r="{6 if strong else 5}" stroke-width="2"/>')
        if table:
            svg.text(x0 - 12, cy + 4.2, f'{v:.1f}', cls=tcls, anchor='end', size=FS_LABEL)
        else:
            svg.text(sx(v) + 11, cy + 4.2, f'{v:.1f}', cls='t-strong' if strong else '', size=FS_LABEL)
    yo, yt = ys[i_ours - 1] + bh / 2, ys[i_ours] + bh / 2
    xb = sx(d['takeover_conclude_40']) + (18 if table else (38 if narrow else 44))
    bracket(svg, xb, yo, yt, signed(d['takeover_conclude_40'] - d['opd_40']))
    return svg


BENCH_COLS = [(T('MATH-500'), (70, 90), [70, 80, 90]), (T('AIME 2024'), (0, 45), [0, 20, 40]),
              (T('AIME 2025'), (0, 45), [0, 20, 40]), (T('AIME 2026'), (0, 45), [0, 20, 40]), (T('Average', '平均'), (20, 50), [20, 35, 50])]


def methods_bench(W):
    """Innovative: the four benchmarks behind the average, one small dot scale each (MATH-500 70–90, the three AIME
    years on one shared 0–45 scale, the average 20–50). It shows where the gain is: the hard AIME sets, while MATH-500
    is close to its ceiling. Values only in the average column; the table under the figure has the rest."""
    rows = c1._method_rows()
    keys = ['ref0', 'ref1', 'ref2', 'opd', 'ours', 'variant']
    avg = OPD['eval_avg4']
    narrow = W < 500
    if narrow:
        lab_x, c0, widths, gapc, pitch = 12, 12, [50, 50, 50, 50, 64], 6, 40
    else:
        lab_x, c0, widths, gapc, pitch = 178, 194, [78, 78, 78, 78, 112], 14, 28
    xs_cols, x = [], c0
    for w_ in widths:
        xs_cols.append((x, x + w_))
        x += w_ + gapc
    top = 44
    heads_at = {0: T('Baselines', '基线'), 3: T('On-policy distillation', '在线蒸馏')}
    ys, heads, y = [], [], top
    for i in range(len(rows)):
        if i in heads_at:
            if i:
                y += 10
            heads.append((y + 2, heads_at[i]))
            y += 16
        ys.append(y + (14 if narrow else 0))
        y += pitch
    y_end = y - pitch + (14 if narrow else 0) + 14
    H = y_end + 24
    svg = Svg(W, H, 'MATH-500, AIME 2024, 2025, 2026 and their average by post-training method')
    for k, ((ca, cz), (name, (lo, hi), ticks)) in enumerate(zip(xs_cols, BENCH_COLS)):
        nm = name if not narrow else (T(name[0].replace('AIME 20', 'AIME '), name[1]) if k in (1, 2, 3) else name)
        svg.text((ca + cz) / 2, 16, nm, cls='t-strong' if k == 4 else '', anchor='middle', size=FS_TICK if narrow else FS_LABEL)
        sx = scale(lo, hi, ca + 5, cz - (30 if k == 4 else 5))
        svg.line(ca, y_end - 6, cz, y_end - 6, 'axis')
        for tv in (ticks[0], ticks[-1]):
            svg.text(sx(tv), y_end + 8, str(tv), cls='t-faint', anchor='middle', size=FS_TICK)
        for (lab, v_avg, cls, kind), key, yb in zip(rows, keys, ys):
            v = avg[{'ref0': 'base', 'ref1': 'grpo_60', 'ref2': 'sft', 'opd': 'opd_40', 'ours': 'takeover_conclude_40', 'variant': 'takeover_40'}[key]]
            v = v if k == 4 else c1.BENCH[key][k]
            svg.line(ca, yb, cz - (30 if k == 4 else 0), yb, 'grid')
            idx = {'s3': 3, 's2': 2, 's1': 1, 'pn-blue': 1}[cls]
            r = 5 if kind == 'ours' else 4
            title = f'{lab[0]} · {name[0]}: {v:.2f}'
            if kind == 'variant':
                svg.mark(title, f'<circle cx="{sx(v):.1f}" cy="{yb:.1f}" r="{r - 0.5}" class="l1" fill="var(--bg)" stroke-width="1.8"/>')
            else:
                svg.mark(title, f'<circle class="dot s{idx}" cx="{sx(v):.1f}" cy="{yb:.1f}" r="{r}" stroke-width="1.5"' + (' opacity=".75"' if kind == 'ref' else '') + '/>')
            if k == 4:
                svg.text(cz, yb + 4.2, f'{v:.1f}', cls='t-strong' if kind == 'ours' else ('t-muted' if kind == 'variant' else ''), anchor='end', size=FS_LABEL)
    for hy, gl in heads:
        svg.text(lab_x if not narrow else 12, hy, gl, cls='t-muted', anchor='end' if not narrow else 'start', size=FS_TICK)
    for (lab, v, cls, kind), yb in zip(rows, ys):
        if kind == 'variant':
            lab = T('↳ ' + lab[0], '↳ ' + lab[1])
        tcls = 't-strong' if kind == 'ours' else ('t-muted' if kind == 'variant' else '')
        if narrow:
            svg.text(12 + (12 if kind == 'variant' else 0), yb - 9, lab, cls=tcls, size=FS_TICK)
        else:
            svg.text(lab_x, yb + 4.2, lab, cls=tcls, anchor='end', size=FS_LABEL)
    return svg


# ============================================================================ opd-budget
def _band_polys(xs, g, se):
    """The ±SE band split where the paired gap changes sign: [(positive?, polygon points)]."""
    out = []
    pts = list(zip(xs, g, se))
    cur = [pts[0]]
    for (xa, ga, sa), (xb, gb, sb) in zip(pts, pts[1:]):
        if (ga >= 0) != (gb >= 0):
            f = (0 - ga) / (gb - ga)
            mid = (xa + (xb - xa) * f, 0.0, sa + (sb - sa) * f)
            cur.append(mid)
            out.append((ga >= 0, cur))
            cur = [mid]
        cur.append((xb, gb, sb))
    out.append((cur[-1][1] >= 0, cur))
    return out


def budget(W, signgap=False, regions=True):
    """Round-1 polish of the shared-axis budget chart. The callout moves next to the point it describes: right-aligned
    under the curves, with a short vertical leader up to the ring at 16k (the long diagonal leader is gone, and so is
    the dotted guide that lay on top of OPD's own flat line). signgap=True colours panel (b) by who leads (orange
    below zero, blue above), the same blue / orange meaning as the lead strip of the GRPO comparison, and names the
    two sides."""
    b, xs = c1._budget()
    narrow = W < 500
    kfmt = c1.kfmt
    x0, x1 = (44, W - 52) if narrow else (64, W - 150)
    hA, hB, hC, gap = (152, 76, 72, 34) if not narrow else (150, 76, 72, 40)
    yA = 30 if not narrow else 56
    A = (x0, yA, x1, yA + hA)
    B_ = (x0, A[3] + gap, x1, A[3] + gap + hB)
    C = (x0, B_[3] + gap, x1, B_[3] + gap + hC)
    H = C[3] + 46
    svg = Svg(W, H, 'Accuracy, paired gap and finished AIME answers against the evaluation token budget, on a shared axis')
    sx = scale(10, 15, x0, x1)
    if narrow:
        key_lines(svg, x0, 18, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    svg.rect(sx(14), A[1] - 6, sx(15) - sx(14), C[3] - A[1] + 6, 'band')
    svg.text(sx(14.5), A[1] + 8, '16k–32k', cls='t-faint', anchor='middle', size=FS_TICK)
    syA = scale(0, 50, A[3], A[1])
    frame(svg, A, sx, syA, [], [0, 25, 50], kfmt, str)
    wash_between(svg, xs, b['takeover_40'], b['opd_40'], sx, syA)
    for idx, key in ((2, 'opd_40'), (1, 'takeover_40')):
        path_line(svg, list(zip(xs, b[key])), sx, syA, idx)
        dots(svg, [(x, y) for x, y, t in zip(xs, b[key], b['tokens']) if t in c1.DOUBLINGS], sx, syA, idx, r=3)
    if narrow:
        label_stack(svg, x1 + 8, [(syA(b['takeover_40'][-1]), f'{b["takeover_40"][-1]:.1f}', 't-strong'), (syA(b['opd_40'][-1]), f'{b["opd_40"][-1]:.1f}', '')], min_gap=15)
    else:
        label_stack(svg, x1 + 8, [(syA(b['takeover_40'][-1]), f'Scaffold-OPD {b["takeover_40"][-1]:.1f}', 't-strong'),
                                  (syA(b['opd_40'][-1]), f'OPD {b["opd_40"][-1]:.1f}', '')], min_gap=15)
    k16 = b['tokens'].index(16384)
    o32, s16 = b['opd_40'][-1], b['takeover_40'][k16]
    px, py = sx(xs[k16]), syA(s16)
    svg.circle(px, py, 5, 'ring')
    ty = syA(21 if not narrow else 9)
    svg.line(px, py + 6, px, ty - 13, 'leader')
    svg.text(px, ty, T(f'Scaffold-OPD at 16k: {s16:.1f}', f'Scaffold-OPD 在 16k：{s16:.1f}'), cls='t-strong', anchor='end', size=FS_TICK)
    svg.text(px, ty + 14, T(f'already {s16 - o32:.1f} above OPD at 32k ({o32:.1f})', f'已比 OPD 在 32k（{o32:.1f}）高 {s16 - o32:.1f}'), anchor='end', size=FS_TICK)
    panel_title(svg, x0, A[1] - 12, 'a', T('Accuracy', '准确率'), T('4-benchmark average', '4 项平均'))
    syB = scale(-5, 8, B_[3], B_[1])
    frame(svg, B_, sx, syB, [], [-4, 0, 4, 8], kfmt, lambda v: signed(v, 0) if v else '0')
    if signgap:
        for pos, poly in _band_polys(xs, b['gap_40'], b['gap_se_40']):
            up = [(x, g + s) for x, g, s in poly]
            lo = [(x, g - s) for x, g, s in poly]
            svg.path(polyline(up, sx, syB) + ' L' + polyline(list(reversed(lo)), sx, syB)[1:] + ' Z', 'wash1' if pos else 'wash2')
    else:
        up = [(x, g + s) for x, g, s in zip(xs, b['gap_40'], b['gap_se_40'])]
        lo = [(x, g - s) for x, g, s in zip(xs, b['gap_40'], b['gap_se_40'])]
        svg.path(polyline(up, sx, syB) + ' L' + polyline(list(reversed(lo)), sx, syB)[1:] + ' Z', 'wash1')
    svg.line(x0, syB(0), x1, syB(0), 'axis', 'stroke-dasharray="3 3"')
    if signgap:
        for pos, seg in seg_sign(xs, b['gap_40']):
            path_line(svg, seg, sx, syB, 1 if pos else 2)
        if regions:
            svg.text(x0 + 6, syB(5.6), T('Scaffold-OPD ahead', 'Scaffold-OPD 领先'), cls='t-muted', size=FS_TICK)
            svg.text(x1 - 6, syB(-3.9), T('OPD ahead', 'OPD 领先'), cls='t-muted', anchor='end', size=FS_TICK)
    else:
        path_line(svg, list(zip(xs, b['gap_40'])), sx, syB, 1)
    for t_ in (8192, 16384, 32768):
        k = b['tokens'].index(t_)
        g = b['gap_40'][k]
        cls_ = 's1' if (g >= 0 or not signgap) else 's2'
        svg.circle(sx(xs[k]), syB(g), 3, f'dot {cls_}', 'stroke-width="1.5"')
        if t_ == 32768:
            svg.text(x1 + 8, syB(g) + 4, signed(g), cls='t-strong', size=FS_LABEL)
        else:
            svg.text(sx(xs[k]) - 6, syB(g) - 7, signed(g), cls='t-strong', anchor='end', size=FS_TICK)
    panel_title(svg, x0, B_[1] - 12, 'b', T('Paired gap', '配对差'), T('Scaffold-OPD − OPD, ±1 SE', 'Scaffold-OPD − OPD，±1 标准误'))
    syC = scale(0, 100, C[3], C[1])
    frame(svg, C, sx, syC, c1.KT, [0, 50, 100], kfmt, str)
    for idx, key in ((2, 'aime_finished_opd_40'), (1, 'aime_finished_takeover_40')):
        path_line(svg, list(zip(xs, b[key])), sx, syC, idx)
    for idx, key in ((2, 'aime_finished_opd_40'), (1, 'aime_finished_takeover_40')):
        svg.circle(sx(xs[k16]), syC(b[key][k16]), 3, f'dot s{idx}', 'stroke-width="1.5"')
    svg.text(sx(xs[k16]) - 6, syC(b['aime_finished_opd_40'][k16]) - 6, f'{b["aime_finished_opd_40"][k16]:.0f}%', cls='t-strong', anchor='end', size=FS_TICK)
    svg.text(sx(xs[k16]) + 6, syC(b['aime_finished_takeover_40'][k16]) + 12, f'{b["aime_finished_takeover_40"][k16]:.0f}%', cls='t-strong', size=FS_TICK)
    if not narrow:
        label_stack(svg, x1 + 8, [(syC(b['aime_finished_opd_40'][-1]), 'OPD', ''), (syC(b['aime_finished_takeover_40'][-1]), 'Scaffold-OPD', '')], min_gap=14, size=FS_TICK)
    panel_title(svg, x0, C[1] - 12, 'c', T('AIME answers finished', '写完的 AIME 回答'), '%')
    svg.text((x0 + x1) / 2, C[3] + 34, T('evaluation budget, tokens (log scale)', '评测预算，token（对数刻度）'), cls='t-muted', anchor='middle', size=FS_TICK)
    return svg


# ============================================================================ opd-training
def _ratio(t):
    return moving_avg([(s, 100 * v) for s, v in zip(t['step'], t['teacher_token_ratio']) if v is not None and s != 19])


def training(W, rangeband=False, share=False):
    """rangeband=True: panel (b) loses the green area and the two dashed guides; a soft band marks 100–150, the range
    the caption names. share=True (innovative): the right column becomes two small panels on one step axis,
    (b) teacher tokens per answer and (c) their share of all tokens, so both halves of the caption's sentence
    ("stay at 100–150 ... so the share falls from 13% to 3%") are drawn, not written."""
    t, tk, op, teach = c1._train()
    tr = OPD['train']
    narrow = W < 500
    if narrow:
        H = 640 if share else 520
        bA = (48, 62, W - 70, 222)
        bB = (48, 320, W - 70, 470) if not share else (48, 318, W - 70, 408)
        bC = (48, 482, W - 70, 572) if share else None
    else:
        H = 316 if share else 300
        bA = (56, 62, W / 2 - 74, H - 52)
        bB = (W / 2 + 54, 62, W - 64, H - 52) if not share else (W / 2 + 54, 62, W - 64, 140)
        bC = (W / 2 + 54, 194, W - 64, H - 52) if share else None
    svg = Svg(W, H, 'Response length, and the teacher-written tokens per answer in Scaffold-OPD' + (' and their share of all tokens' if share else ''))
    key_lines(svg, bA[0], 18, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    panel_title(svg, bA[0], bA[1] - 16, 'a', T('Response length', '回答长度'), T('tokens', 'token'))
    sxa, sya = scale(0, 60, bA[0], bA[2]), scale(0, 6000, bA[3], bA[1])
    for idx, steps, vals in ((2, tr['opd']['step'], tr['opd']['response_length']), (1, t['step'], t['response_length'])):
        for s_, v in zip(steps, vals):
            if v is not None and not (idx == 1 and s_ == 19):
                svg.circle(sxa(s_), sya(min(v, 6000)), 1.6, f's{idx}', 'opacity=".28"')
    c1._length_panel(svg, bA, tk, op)
    # (b) teacher tokens per answer
    panel_title(svg, bB[0], bB[1] - 16, 'b', T('Teacher tokens per answer', '每条回答的老师 token'), 'Scaffold-OPD')
    sx = scale(0, 60, bB[0], bB[2])
    sy = scale(0, 200, bB[3], bB[1])
    if rangeband or share:
        svg.rect(bB[0], sy(150), bB[2] - bB[0], sy(100) - sy(150), 'band')
    else:
        for v in (100, 150):
            svg.line(bB[0], sy(v), bB[2], sy(v), 'leader', 'stroke-dasharray="3 3"')
    yt = [0, 100, 200] if share else [0, 50, 100, 150, 200]
    frame(svg, bB, sx, sy, [0, 20, 40, 60] if not share else [], yt, xtitle=None if share else T('training step', '训练步'))
    if share:
        for v in (0, 20, 40, 60):
            svg.line(sx(v), bB[3], sx(v), bB[3] + 4, 'axis')
    if not (rangeband or share):
        area = polyline(teach, sx, sy) + f' L{sx(teach[-1][0]):.1f},{sy(0):.1f} L{sx(teach[0][0]):.1f},{sy(0):.1f} Z'
        svg.path(area, 'fl-green', 'opacity=".55"')
    for s_, v in zip(t['step'], t['teacher_tokens_per_answer']):
        if v is not None and s_ != 19:
            svg.circle(sx(s_), sy(min(v, 200)), 1.6, 's5', 'opacity=".35"')
    path_line(svg, teach, sx, sy, 5)
    svg.circle(sx(teach[-1][0]), sy(teach[-1][1]), 3.2, 'dot s5', 'stroke-width="1.5"')
    hits(svg, teach, sx, sy, lambda x, y: f'step {x}: {y:.0f} teacher tokens per answer')
    if not narrow:
        svg.text(bB[2] + 8, sy(teach[-1][1]) + 4, f'{teach[-1][1]:.0f}', cls='t-strong', size=FS_LABEL)
    s0 = 100 * c1._window(t, 1, 5, 'teacher_token_ratio')
    s1 = 100 * c1._window(t, 56, 60, 'teacher_token_ratio')
    if share:
        if narrow:
            svg.text(bB[2] + 8, sy(teach[-1][1]) + 4, f'{teach[-1][1]:.0f}', cls='t-strong', size=FS_LABEL)
        panel_title(svg, bC[0], bC[1] - 16, 'c', T('Teacher share of the tokens', '老师 token 占比'), '%')
        syc = scale(0, 20, bC[3], bC[1])
        frame(svg, bC, sx, syc, [0, 20, 40, 60], [0, 10, 20], xtitle=T('training step', '训练步'))
        ratio = _ratio(t)
        for s_, v in zip(t['step'], t['teacher_token_ratio']):
            if v is not None and s_ != 19:
                svg.circle(sx(s_), syc(min(100 * v, 20)), 1.6, 's5', 'opacity=".35"')
        path_line(svg, ratio, sx, syc, 5)
        svg.circle(sx(ratio[-1][0]), syc(ratio[-1][1]), 3.2, 'dot s5', 'stroke-width="1.5"')
        hits(svg, ratio, sx, syc, lambda x, y: f'step {x}: {y:.1f}% of the tokens written by the teacher')
        svg.text(sx(5) + 4, syc(s0) - 8, f'{s0:.0f}%', cls='t-strong', size=FS_LABEL)
        svg.text(bC[2] + 8, syc(ratio[-1][1]) + 4, f'{s1:.0f}%', cls='t-strong', size=FS_LABEL)
    else:
        y0l, y1l = sy(teach[0][1]) - 22, sy(teach[-1][1]) - 24
        svg.line(sx(teach[0][0]) + 2, y0l + 4, sx(teach[0][0]) + 2, sy(teach[0][1]) - 4, 'leader')
        svg.line(sx(60) - 2, y1l + 4, sx(60) - 2, sy(teach[-1][1]) - 5, 'leader')
        svg.text(sx(teach[0][0]) + 6, y0l + 2, T(f'{s0:.0f}% of the tokens', f'占全部 token {s0:.0f}%'), size=FS_TICK)
        svg.text(sx(60) - 6, y1l + 2, T(f'{s1:.0f}% of the tokens', f'占全部 token {s1:.0f}%'), anchor='end', size=FS_TICK)
    return svg


# ============================================================================ opd-compute
def compute(W, seglabels=False):
    """Polish of the 11-15 drawing the user chose. The 'same score, ≈ 4× the GPU-hours' span uses the shared span
    mark; the y title starts on the plot's left edge like the key; the inset sits on a background box (no grid lines
    through it), and its stage rows carry the same '+ stage' names as the points on the curve, so colour alone says
    'pipeline'. seglabels=True (innovative): no inset; each segment is labelled with what it adds and what it costs
    ('+12.6 in 16.8 h'), the numbers the page text gives, and the slopes do the comparing."""
    pts, alone = c1._compute_data()
    g = OPD['gpu_hours']['pipeline']
    narrow = W < 500
    H = 330 if not narrow else 360
    box = (46, 44, W - (28 if narrow else 118), H - 44)
    svg = Svg(W, H, 'Score against cumulative training GPU-hours: the full pipeline and Scaffold-OPD alone' + ('' if seglabels else ', and the points gained per GPU-hour'))
    key_lines(svg, box[0], 16, [(2, T('full pipeline', '全流程')), (1, T('Scaffold-OPD alone', '只做 Scaffold-OPD'))])
    sx, sy = scale(0, 56, box[0], box[2]), scale(20, 52, box[3], box[1])
    frame(svg, box, sx, sy, [0, 10, 20, 30, 40, 50], [20, 30, 40, 50], xtitle=T('cumulative training GPU-hours (2 × A100)', '累计训练卡时（2 × A100）'))
    svg.text(box[0], box[1] - 10, T('4-benchmark average', '4 项平均分'), cls='t-muted', size=FS_TICK)
    path_line(svg, pts, sx, sy, 2)
    path_line(svg, [pts[0], alone], sx, sy, 1)
    c3x = pts[-1][0]
    span(svg, sx(alone[0]), sx(c3x), sy(50), T(f'same score · ≈ {c3x / alone[0]:.0f}× the GPU-hours', f'分数相同 · 卡时约 {c3x / alone[0]:.0f} 倍'),
         drops=[(sx(alone[0]), sy(alone[1]) - 8), (sx(c3x), sy(pts[-1][1]) - 8)])
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
    if seglabels:
        r1 = lambda v: round(v, 1)  # noqa: E731  (gains from the rounded scores the chart prints, as on the page)
        segs = [(pts[0], pts[1], g['sft_incl_teacher_data'], 2), (pts[1], pts[2], g['takeover_40'], 2), (pts[2], pts[3], g['grpo_30'], 2)]
        offs = [(10, 12), (0, 22), (0, 24)] if not narrow else [(8, 14), (2, 26), (-30, 26)]
        for ((xa, ya), (xb, yb_), hrs, idx), (dx, dy) in zip(segs, offs):
            mx, my = (sx(xa) + sx(xb)) / 2, (sy(ya) + sy(yb_)) / 2
            svg.text(mx + dx, my + dy, T(f'{signed(r1(yb_) - r1(ya))} in {hrs:.1f} h', f'{hrs:.1f} 小时 {signed(r1(yb_) - r1(ya))}'), cls='t-muted', anchor='middle', size=FS_TICK)
        mx, my = (sx(0) + sx(alone[0])) / 2, (sy(pts[0][1]) + sy(alone[1])) / 2
        svg.text(mx - 8, my - 4, T(f'{signed(r1(alone[1]) - r1(pts[0][1]))} in {alone[0]:.1f} h', f'{alone[0]:.1f} 小时 {signed(r1(alone[1]) - r1(pts[0][1]))}'),
                 cls='t-strong', anchor='end', size=FS_TICK)
        return svg
    if not narrow:
        rates = [(T('Scaffold-OPD alone', '只做 Scaffold-OPD'), (alone[1] - pts[0][1]) / alone[0], 's1', ''),
                 (T('+ SFT'), (pts[1][1] - pts[0][1]) / (pts[1][0] - pts[0][0]), 's2', ' opacity=".75"'),
                 (T('+ Scaffold-OPD'), (pts[2][1] - pts[1][1]) / (pts[2][0] - pts[1][0]), 's2', ' opacity=".75"'),
                 (T('+ GRPO on failures', '+ 错题回流 GRPO'), (pts[3][1] - pts[2][1]) / (pts[3][0] - pts[2][0]), 's2', ' opacity=".75"')]
        ix0, ix1 = sx(40), sx(53)
        iy = sy(33.2)
        lx = ix0 - 104
        soft_box(svg, lx - 8, iy - 15, ix1 - lx + 40, 4 * 14 + 30)
        svg.text(lx, iy, T('Points gained per GPU-hour', '每卡时提分'), cls='t-strong', size=FS_TICK)
        sxi = scale(0, 1.7, ix0, ix1)
        for j, (lab, r_, cls, op) in enumerate(rates):
            yy = iy + 9 + j * 14 + (3 if j else 0)
            svg.text(ix0 - 8, yy + 7.5, lab, anchor='end', size=FS_TICK)
            svg.mark(f'{lab[0]}: {r_:.2f} points per GPU-hour', f'<path class="bar {cls}"{op} d="{hbar(ix0, yy, sxi(r_), 8, 2)}"/>')
            svg.text(sxi(r_) + 5, yy + 7.5, f'{r_:.2f}', cls='t-strong' if j == 0 else '', size=FS_TICK)
    return svg


# ============================================================================ scr-sft-rl
def sft_rl(W, shared=False):
    """Progress bars (gray = success after SFT, blue = what 100 RL steps add), both splits in the seen-gain order.
    Polish: the key gain in ink semibold instead of blue text, the other gains muted, the count line at 11 px.
    shared=True (innovative): the two splits share one label column (the families are in the same order anyway), so
    each family is named once and the bars get the space the second label column took."""
    narrow = W < 500
    seen_order = c1._fam('seen')[3]
    svg_label = 'ALFWorld success by task family after SFT and the gain from 100 RL steps, sorted by the gain on seen games'

    def keys(svg):
        def k(i):
            xx = 16 if not narrow else 8
            for cls, s, op in (('s3', pick(T('after SFT', 'SFT 后'), i), ' opacity=".55"'), ('s1', pick(T('gain from 100 RL steps', '100 步 RL 的提升'), i), '')):
                svg.add(f'<rect x="{xx:.1f}" y="9" width="10" height="10" rx="2" class="{cls}"{op}/>')
                svg.text(xx + 15, 18, s, size=FS_LABEL)
                xx += 15 + text_w(s, FS_LABEL) + 18
        per_lang(svg, k)

    def bar(svg, fam, split, a, b, gain, x0b, x1b, y, gx, key, counts=True):
        sx = scale(0, 100, x0b, x1b)
        (sa, n), (sb, _) = a[fam], b[fam]
        pa, pb = 100 * sa / n, 100 * sb / n
        bh_ = 8
        svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sa}/{n} after SFT', f'<path class="bar s3" opacity=".55" d="{hbar(x0b, y - bh_ / 2, max(sx(pa) - 1, x0b + 1), bh_, 2)}"/>')
        svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sb}/{n} after RL', f'<path class="bar s1" d="{hbar(sx(pa) + 1, y - bh_ / 2, max(sx(pb), sx(pa) + 3), bh_, 2)}"/>')
        svg.text(gx, y + 4, f'+{gain[fam]:.0f}', cls='t-strong' if key else 't-muted', anchor='end', size=FS_LABEL)
        if key and counts:
            svg.text((sx(pa) + sx(pb)) / 2, y + 17, f'{sa}/{n} → {sb}/{n}', cls='t-muted', anchor='middle', size=FS_TICK)

    if shared and not narrow:
        H = 290
        svg = Svg(W, H, svg_label)
        keys(svg)
        top, bot = 74, H - 46
        lab_r = 124
        groups = [('seen', 140, 362, 404), ('unseen', 450, 672, 714)]
        pitch = (bot - top) / len(seen_order)
        for i, fam in enumerate(seen_order):
            if fam == 'pick_two_obj_and_place':
                y = top + i * pitch + pitch / 2 - 4
                svg.rect(8, y - pitch / 2 + 2, W - 16, pitch - 4, 'band', rx=4)
        for k, (split, xa, xb, gx) in enumerate(groups):
            a, b, gain, _ = c1._fam(split)
            sx = scale(0, 100, xa, xb)
            panel_title(svg, xa, top - 20, 'ab'[k], T(split, split), T('success, %', '成功率，%'))
            svg.text(gx, top - 20, T('gain', '提升'), cls='t-muted', anchor='end', size=FS_TICK)
            frame(svg, (xa, top - 8, xb, bot), sx, None, [0, 25, 50, 75, 100], [], grid='x')
            for i, fam in enumerate(seen_order):
                y = top + i * pitch + pitch / 2 - 4
                bar(svg, fam, split, a, b, gain, xa, xb, y, gx, fam == 'pick_two_obj_and_place')
        for i, fam in enumerate(seen_order):
            y = top + i * pitch + pitch / 2 - 4
            key = fam == 'pick_two_obj_and_place'
            svg.text(lab_r, y + 4, FAM_NAMES[fam], cls='t-strong' if key else '', anchor='end', size=FS_LABEL)
        return svg
    if shared and narrow:
        # phone: each family on its own line, then the seen and unseen bars side by side
        top = 76
        rowh = 46
        H = top + rowh * len(seen_order) + 34
        svg = Svg(W, H, svg_label)
        keys(svg)
        groups = [('seen', 12, 124, 156), ('unseen', 178, 290, 322 if W > 340 else W - 4)]
        for k, (split, xa, xb, gx) in enumerate(groups):
            panel_title(svg, xa, top - 22, 'ab'[k], T(split, split), None)
            svg.text(gx, top - 22, T('gain', '提升'), cls='t-muted', anchor='end', size=FS_TICK)
        for i, fam in enumerate(seen_order):
            y0 = top + i * rowh
            key = fam == 'pick_two_obj_and_place'
            if key:
                svg.rect(4, y0 - 6, W - 8, rowh - 4, 'band', rx=4)
            svg.text(12, y0 + 8, FAM_NAMES[fam], cls='t-strong' if key else '', size=FS_TICK)
            for split, xa, xb, gx in groups:
                a, b, gain, _ = c1._fam(split)
                bar(svg, fam, split, a, b, gain, xa, xb, y0 + 22, gx, key, counts=False)
        for split, xa, xb, gx in groups:
            sx = scale(0, 100, xa, xb)
            yax = top + rowh * len(seen_order) - 6
            svg.line(xa, yax, xb, yax, 'axis')
            for v in (0, 50, 100):
                svg.text(sx(v), yax + 14, str(v), cls='t-faint', anchor='middle', size=FS_TICK)
        return svg
    if narrow:
        H = 510
        panels = [('seen', (100, 72, W - 56, 232)), ('unseen', (100, 318, W - 56, 478))]
    else:
        H = 296
        panels = [('seen', (128, 70, W / 2 - 56, H - 50)), ('unseen', (W / 2 + 96, 70, W - 52, H - 50))]
    svg = Svg(W, H, svg_label)
    keys(svg)
    for k, (split, box) in enumerate(panels):
        a, b, gain, _ = c1._fam(split)
        sx = scale(0, 100, box[0], box[2])
        panel_title(svg, box[0], box[1] - 20, 'ab'[k], T(split, split), T('success, %', '成功率，%'))
        frame(svg, (box[0], box[1] - 8, box[2], box[3]), sx, None, [0, 25, 50, 75, 100], [], grid='x')
        svg.text(box[2] + 40, box[1] - 20, T('gain', '提升'), cls='t-muted', anchor='end', size=FS_TICK)
        pitch = (box[3] - box[1]) / len(seen_order)
        for i, fam in enumerate(seen_order):
            y = box[1] + i * pitch + pitch / 2 - 4
            key = fam == 'pick_two_obj_and_place'
            if key:
                svg.rect(box[0] - (110 if not narrow else 92), y - pitch / 2 + 2, (box[2] - box[0]) + (152 if not narrow else 132), pitch - 4, 'band', rx=4)
            svg.text(box[0] - 10, y + 4, FAM_NAMES[fam], cls='t-strong' if key else '', anchor='end', size=FS_LABEL if not narrow else FS_TICK)
            bar(svg, fam, split, a, b, gain, box[0], box[2], y, box[2] + 40, key)
    return svg


# ============================================================================ scr-vs-grpo
def vs(W, below=False, gapbars=False):
    """below=True (polish): the late-stage means leave the plot for a second line under the lead strip, written out
    ('mean of the last five: 82.3 vs 61.0'), so the gray band carries no unlabelled numbers. gapbars=True
    (innovative): the lead strip becomes a small bar strip of the gap at each validation (blue up when StepCredit-RL
    leads, orange down when GRPO does), which shows by how much, not only who; the wash between the curves goes,
    since the bars carry the gap."""
    g, r, disc = c1._vs_data()
    narrow = W < 500
    extra = 16 if (below or gapbars) else 0
    if narrow:
        H = 600 + 2 * extra + (30 if gapbars else 0)
        bx = [(44, 64, W - 56, 212), (44, 344 + extra + (15 if gapbars else 0), W - 56, 492 + extra + (15 if gapbars else 0))]
    else:
        H = 318 + extra + (16 if gapbars else 0)
        bx = [(46, 64, W / 2 - 52, 220), (W / 2 + 52, 64, W - 50, 220)]
    svg = Svg(W, H, 'StepCredit-RL vs GRPO: validation success over 200 steps, and which run is ahead at each validation')
    key_lines(svg, bx[0][0], 18, [(1, 'StepCredit-RL'), (2, 'GRPO')])
    for k, (name, A) in enumerate(zip(('seen', 'unseen'), bx)):
        sx, sy = scale(0, 200, A[0], A[2]), scale(0, 100, A[3], A[1])
        panel_title(svg, A[0], A[1] - 16, 'ab'[k], T(name, name), T('success, %', '成功率，%'))
        p_ = float(disc[name]['p'])
        svg.text(A[2], A[1] - 16, f'McNemar p = {c1._pfmt(p_)}', cls='t-strong' if p_ < 0.05 else 't-muted', anchor='end', size=FS_TICK)
        svg.rect(sx(160), A[1], sx(200) - sx(160), A[3] - A[1], 'band')
        frame(svg, A, sx, sy, [0, 50, 100, 150, 200], [0, 25, 50, 75, 100])
        if not gapbars:
            wash_between(svg, [s for s, _ in g[name]], [v for _, v in g[name]], [v for _, v in r[name]], sx, sy)
        lg = sum(v for s, v in g[name] if s >= 160) / 5
        lr = sum(v for s, v in r[name] if s >= 160) / 5
        path_line(svg, r[name], sx, sy, 2)
        path_line(svg, g[name], sx, sy, 1)
        for idx, pts in ((2, r[name]), (1, g[name])):
            svg.circle(sx(200), sy(pts[-1][1]), 3.2, f'dot s{idx}', 'stroke-width="1.5"')
        hits(svg, g[name], sx, sy, lambda x, y: f'StepCredit-RL · step {x}: {y:.1f}%')
        hits(svg, r[name], sx, sy, lambda x, y: f'GRPO · step {x}: {y:.1f}%')
        label_stack(svg, A[2] + 7, [(sy(g[name][-1][1]), f'{g[name][-1][1]:.1f}', 't-strong'), (sy(r[name][-1][1]), f'{r[name][-1][1]:.1f}', '')], min_gap=13)
        if not (below or gapbars):
            svg.text((sx(160) + sx(200)) / 2, A[1] + 13, f'{lg:.1f} / {lr:.1f}', cls='t-muted', anchor='middle', size=FS_TICK)
        ahead = 0
        if gapbars:
            yz = A[3] + 46
            sg = scale(0, 30, 0, 18)
            svg.line(A[0], yz, A[2], yz, 'axis')
            for (s_, a_), (_, b_) in zip(g[name], r[name]):
                d_ = a_ - b_
                ahead += d_ > 0.05
                hgt = max(sg(abs(d_)), 1.2)
                cls = 's1' if d_ > 0.05 else ('s2' if d_ < -0.05 else 's3')
                y_ = yz - hgt if d_ >= 0 else yz
                svg.mark(f'step {s_}: {signed(d_)} points', f'<rect class="{cls}" x="{sx(s_) - 3:.1f}" y="{y_:.1f}" width="6" height="{hgt:.1f}" rx="1"/>')
            ys_text = yz + 34
        else:
            ys = A[3] + 32
            sq = 8
            for (s_, a_), (_, b_) in zip(g[name], r[name]):
                d_ = a_ - b_
                cls = 's1' if d_ > 0.05 else ('s2' if d_ < -0.05 else 's3')
                ahead += d_ > 0.05
                svg.mark(f'step {s_}: {signed(d_)} points', f'<rect class="{cls}" x="{sx(s_) - sq / 2:.1f}" y="{ys:.1f}" width="{sq}" height="{sq}" rx="1.5"/>')
            ys_text = ys + 24
        svg.text(A[0], ys_text, T(f'StepCredit-RL ahead at {ahead} of {len(g[name])} validations', f'{len(g[name])} 次验证中 StepCredit-RL 领先 {ahead} 次'), cls='t-muted', size=FS_TICK)
        if below or gapbars:
            svg.text(A[0], ys_text + 16, T(f'Mean of the last five (gray band): {lg:.1f} vs {lr:.1f}', f'最后 5 次（灰色区）平均：{lg:.1f} 对 {lr:.1f}'), cls='t-muted', size=FS_TICK)
    return svg


# ============================================================================ scr-updates
def _upd_unseen():
    four = [(int(x['step']), float(x['unseen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo_4upd']
    one = [(int(x['step']), float(x['unseen']), float(x['hours'])) for x in ALF if x['run'] == 'gigpo' and int(x['step']) <= 150]
    return four, one


def _hours_panel(svg, box, four, one, narrow, compact=False):
    sx, sy = scale(0, 30, box[0], box[2]), scale(0, 100, box[3], box[1])
    frame(svg, box, sx, sy, [0, 10, 20, 30] if compact else [0, 5, 10, 15, 20, 25, 30], [0, 25, 50, 75, 100], xtitle=T('hours on 2 × A100', '耗时（2 × A100，小时）'))
    for idx, rows in ((3, one), (1, four)):
        pts = [(h, s) for _, s, h in rows]
        path_line(svg, pts, sx, sy, idx)
        hits(svg, pts, sx, sy, lambda x, y: f'{x:g} h: {y:.1f}%')
        for st, s, h in rows:
            if st in (50, 100, 150):
                svg.circle(sx(h), sy(s), 3.6, f'dot s{idx}', 'stroke-width="1.5"')
                if (idx == 1 and st == 100) or (idx == 3 and st == 150):
                    continue
                svg.text(sx(h) + (8 if idx == 3 else -7), sy(s) + (14 if idx == 3 else -6), T(f'step {st}', f'第 {st} 步'), cls='t-muted',
                         anchor='start' if idx == 3 else 'end', size=FS_TICK)
    e4, e1 = four[-1], one[-1]
    if narrow or compact:
        svg.text(sx(e4[2]) - 4, sy(e4[1]) - 9, T(f'step 100 · {e4[1]:.1f}%', f'第 100 步 · {e4[1]:.1f}%'), cls='t-strong', anchor='end', size=FS_TICK)
        svg.text(sx(e1[2]) - 2, sy(e1[1]) - 9, T(f'step 150 · {e1[1]:.1f}%', f'第 150 步 · {e1[1]:.1f}%'), anchor='end', size=FS_TICK)
    else:
        svg.text(sx(e4[2]) + 8, sy(e4[1]) + 4, T(f'step 100 · {e4[1]:.1f}%', f'第 100 步 · {e4[1]:.1f}%'), cls='t-strong', size=FS_TICK)
        svg.text(sx(e1[2]) + 8, sy(e1[1]) + 4, T(f'step 150 · {e1[1]:.1f}%', f'第 150 步 · {e1[1]:.1f}%'), size=FS_TICK)
    yb = sy(92)
    span(svg, sx(e4[2]), sx(e1[2]), yb, T(f'about {e1[2] - e4[2]:.0f} h sooner', f'约早 {e1[2] - e4[2]:.0f} 小时'),
         drops=[(sx(e4[2]), sy(e4[1]) - (22 if (narrow or compact) else 8)), (sx(e1[2]), sy(e1[1]) - (22 if (narrow or compact) else 8))], cls='t-muted', size=FS_TICK)
    return sx, sy


def updates(W, steps=False):
    """Polish: the 'about 13 h sooner' comparison uses the shared span mark, with dotted drops to the two points it
    compares; step labels at 11 px muted; the y title on the plot's left edge. steps=True (innovative): a second panel
    against training steps, the view the page text quotes (at step 100, 76.4% vs 51.4%; four updates lead at every
    validation from 10 to 100), beside the wall-clock view."""
    four, one = c1._upd()
    narrow = W < 500
    if not steps:
        H = 330 if not narrow else 360
        box = (48, 50, W - (92 if not narrow else 64), H - 50)
        svg = Svg(W, H, 'Success against wall-clock hours for four updates per step and for one, with training steps marked')
        key_lines(svg, box[0], 18, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
        svg.text(box[0], box[1] - 14, T('seen success, %', 'seen 成功率，%'), cls='t-muted', size=FS_TICK)
        _hours_panel(svg, box, four, one, narrow)
        return svg
    if narrow:
        H = 640
        bS, bH = (48, 78, W - 40, 250), (48, 360, W - 40, 560)
    else:
        H = 340
        bS, bH = (48, 78, 286, H - 52), (352, 78, W - 92, H - 52)
    svg = Svg(W, H, 'Seen success for four updates per step and for one, against training steps and against wall-clock hours')
    key_lines(svg, bS[0], 18, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
    panel_title(svg, bS[0], bS[1] - 16, 'a', T('Per training step', '按训练步'), T('seen success, %', 'seen 成功率，%'))
    panel_title(svg, bH[0], bH[1] - 16, 'b', T('Per hour', '按耗时'), T('seen success, %', 'seen 成功率，%'))
    sx, sy = scale(0, 150, bS[0], bS[2]), scale(0, 100, bS[3], bS[1])
    frame(svg, bS, sx, sy, [0, 50, 100, 150], [0, 25, 50, 75, 100], xtitle=T('training step', '训练步'))
    for idx, rows in ((3, one), (1, four)):
        pts = [(st, s) for st, s, _ in rows]
        path_line(svg, pts, sx, sy, idx)
        hits(svg, pts, sx, sy, lambda x, y: f'step {x}: {y:.1f}%')
    s4 = [s for st, s, _ in four if st == 100][0]
    s1 = [s for st, s, _ in one if st == 100][0]
    svg.circle(sx(100), sy(s4), 3.6, 'dot s1', 'stroke-width="1.5"')
    svg.circle(sx(100), sy(s1), 3.6, 'dot s3', 'stroke-width="1.5"')
    svg.text(sx(100) - 7, sy(s4) - 8, f'{s4:.1f}%', cls='t-strong', anchor='end', size=FS_TICK)
    svg.text(sx(100) + 7, sy(s1) + 15, f'{s1:.1f}%', size=FS_TICK)
    _hours_panel(svg, bH, four, one, narrow, compact=not narrow)
    return svg


# ============================================================================ scr-hotpotqa
def hotpot(W, story=False):
    """Polish: units the same way in all three panels (the unit in the title, plain tick numbers), the bars named like
    the key ('EM reward', 'shaped reward'), slimmer bars. story=True (innovative): the panels follow the page's
    'Outcome' paragraph — (a) repeated queries, (b) all-failed groups, then (c) exact match, which did not move — so
    the figure reads 'better behaviour, more signal, same accuracy', with the bar panel between the two line panels."""
    em, sh = c1._hpq()
    narrow = W < 500
    H = 312 if not narrow else 820
    top = 84
    svg = Svg(W, H, 'HotpotQA under the EM and shaped rewards: exact match and repeated queries over training, and the share of all-failed groups')
    key_lines(svg, 48, 18, [(1, T('EM reward', 'EM 奖励')), (2, T('shaped reward', '稠密奖励'))])
    pw = (W - 60) / 3
    p_ = float(PAIRED['hotpotqa_em_vs_shaped:all']['p'])
    lines = {'em': (T('Exact match', 'EM'), '%', (40, 60), [40, 50, 60], lambda v: f'{v:.0f}', T(f'no significant change (p = {p_:.2f})', f'无显著差异（p = {p_:.2f}）')),
             'repeat_queries': (T('Repeated queries', '重复查询'), T('per question', '每题'), (0, 0.2), [0, 0.1, 0.2], lambda v: f'{v:.1f}' if v else '0', T('−71% at step 200', '第 200 步减少 71%'))}
    order = ['repeat_queries', 'bars', 'em'] if story else ['em', 'repeat_queries', 'bars']
    for k, key in enumerate(order):
        if narrow:
            box = (56, 74 + k * 250, W - 70, 74 + k * 250 + 160)
        else:
            box = (52 + k * pw, top, 52 + k * pw + pw - (60 if key == 'bars' else 82), H - 60)
        letter = 'abc'[k]
        if key == 'bars':
            panel_title(svg, box[0], box[1] - 30, letter, T('All-failed groups', '全错组'), T('% of training groups', '占训练组 %'))
            svg.text(box[0], box[1] - 13, T('more groups give a learning signal', '更多组有学习信号'), size=FS_TICK)
            sy = scale(0, 30, box[3], box[1])
            frame(svg, box, lambda v: v, sy, [], [0, 10, 20, 30], str, str)
            cw = (box[2] - box[0]) / 2
            for j, (idx, v, lab) in enumerate(((1, 27, T('EM reward', 'EM 奖励')), (2, 4, T('shaped reward', '稠密奖励')))):
                cx = box[0] + cw * (j + 0.5)
                hw = 9
                svg.mark(f'{lab[0]}: about {v}% of the groups had no successful answer',
                         f'<path class="bar s{idx}" d="M{cx - hw:.1f},{sy(0):.1f} V{sy(v) + 3:.1f} A3,3 0 0 1 {cx - hw + 3:.1f},{sy(v):.1f} H{cx + hw - 3:.1f} A3,3 0 0 1 {cx + hw:.1f},{sy(v) + 3:.1f} V{sy(0):.1f} Z"/>')
                svg.text(cx, sy(v) - 7, f'≈ {v}%', cls='t-strong', anchor='middle', size=FS_LABEL)
                svg.text(cx, box[3] + 16, lab, cls='t-muted', anchor='middle', size=FS_TICK)
            continue
        title, unit, (lo, hi), ticks, fmt, verdict = lines[key]
        sx, sy = scale(0, 200, box[0], box[2]), scale(lo, hi, box[3], box[1])
        panel_title(svg, box[0], box[1] - 30, letter, title, unit)
        svg.text(box[0], box[1] - 13, verdict, size=FS_TICK)
        frame(svg, box, sx, sy, [0, 100, 200], ticks, str, fmt, xtitle=T('step', '步'))
        for idx, d in ((2, sh), (1, em)):
            path_line(svg, d[key], sx, sy, idx)
            dots(svg, d[key], sx, sy, idx, r=2.2, ring=False)
            hits(svg, d[key], sx, sy, lambda x, y: f'step {x}: {y}')
        a_, b_ = em[key][-1][1], sh[key][-1][1]
        f = (lambda v: f'{v:.1f}') if key == 'em' else (lambda v: f'{v:.3f}')
        label_stack(svg, box[2] + 7, [(sy(a_), f(a_), 't-strong' if key == 'em' else ''), (sy(b_), f(b_), 't-strong' if key != 'em' else '')], min_gap=13)
        if key != 'em':
            xl = sx(200) - 7
            svg.line(xl, sy(a_) + 5, xl, sy(b_) - 5, 'leader')
    return svg


# ============================================================================ the round
AES = {'opd-methods': lambda W: methods(W, table=True, keyband=True),
       'opd-budget': budget,
       'opd-training': lambda W: training(W, rangeband=True),
       'opd-compute': compute,
       'scr-sft-rl': sft_rl,
       'scr-vs-grpo': lambda W: vs(W, below=True),
       'scr-updates': updates,
       'scr-hotpotqa': hotpot}
INNO = {'opd-methods': methods_bench,
        'opd-budget': lambda W: budget(W, signgap=True),
        'opd-training': lambda W: training(W, share=True),
        'opd-compute': lambda W: compute(W, seglabels=True),
        'scr-sft-rl': lambda W: sft_rl(W, shared=True),
        'scr-vs-grpo': lambda W: vs(W, gapbars=True),
        'scr-updates': lambda W: updates(W, steps=True),
        'scr-hotpotqa': lambda W: hotpot(W, story=True)}
MERGED = {'opd-methods': lambda W: methods(W, table=True, keyband=True),
          'opd-budget': lambda W: budget(W, signgap=True, regions=False),
          'opd-training': lambda W: training(W, share=True),
          'opd-compute': compute,
          'scr-sft-rl': lambda W: sft_rl(W, shared=True),
          'scr-vs-grpo': lambda W: vs(W, below=True),
          'scr-updates': lambda W: updates(W, steps=True),
          'scr-hotpotqa': hotpot}
NOTES = {
    'opd-methods': 'Merged: aesthetic. Values in an aligned column next to the names, a soft band on the Scaffold-OPD row, +6.2 in ink. '
                   'The per-benchmark dot table showed the AIME gains but read as sparse dots on faint tracks, with five scales to learn.',
    'opd-budget': 'Merged: the aesthetic callout (right-aligned under the curves, short vertical leader to the ring at 16k) with the '
                  'innovative sign colours in (b): orange where OPD leads, blue where Scaffold-OPD leads. The two region labels '
                  'were dropped: "Scaffold-OPD ahead" sat next to the orange stretch and read as its label.',
    'opd-training': 'Merged: innovative. The right column becomes (b) teacher tokens per answer (flat inside a soft 100–150 band) and '
                    '(c) their share of all tokens (13% to 3%), so the caption sentence is drawn rather than written into (b).',
    'opd-compute': 'Merged: aesthetic (inset on a background box, "+ stage" names matching the curve, span mark, y title on the left '
                   'edge). Segment labels ("+12.6 in 16.8 h") collided with the point labels and doubled the text.',
    'scr-sft-rl': 'Merged: innovative. Both splits are already in the same order, so they share one label column; each family is '
                  'named once and the bars are longer.',
    'scr-vs-grpo': 'Merged: aesthetic. The late-stage means leave the gray band for a written line under the lead strip. The '
                   'gap-bar strip showed magnitude but duplicated the wash and was harder to count than the squares.',
    'scr-updates': 'Merged: innovative. A per-step panel joins the wall-clock panel: at step 100, 76.4% vs 51.4%, the view the page '
                   'text quotes. Both use the aesthetic span mark.',
    'scr-hotpotqa': 'Merged: aesthetic (units in titles, plain ticks, bars named like the key, slimmer bars). The narrative order '
                    '(repeated queries, all-failed groups, exact match) is kept for round 2; its middle title overran.',
}
