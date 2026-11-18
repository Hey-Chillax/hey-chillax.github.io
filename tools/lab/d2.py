"""Chart cycle 2, round 2 (2026-11-17). BASE = round 1's merges (d1.MERGED). English is what the pages show.

AES    = polish of the base (see each function's docstring).
INNO   = a new idea per chart.
MERGED = what goes on to round 3; NOTES give the reasons.
"""
from d_kit import (FAM_NAMES, FS_LABEL, FS_TICK, OPD, PAIRED, Svg, T, bracket, dots, frame, hbar, hits, key_lines, ring,
                   label_stack, panel_title, path_line, per_lang, pick, polyline, scale, seg_sign, signed,
                   soft_box, span, text_w, wash_between)
import figures  # noqa: E402,F401  load figures first (see d1)
import c1  # noqa: E402
import d1  # noqa: E402

BASE = dict(d1.MERGED)


# ============================================================================ opd-methods
def methods(W, baseline=False, cost=False, phone_grid=True):
    """Round-1 merge (values beside the names, key-row band). baseline=True (polish): a zero line at the start of the
    stems, so the lollipops stand on something, and the stems of the three baselines a shade lighter.
    cost=True (innovative): the compute context the page gives right under this figure: GRPO's row notes
    '2.6× the GPU-hours, 12× the rollouts', and the bracket adds that OPD and Scaffold-OPD cost about the same.
    phone_grid=False (round 3): on phones the names sit above the stems, so the vertical grid would run through them;
    the values are printed, so the phone version keeps only the axis."""
    rows = c1._method_rows()
    d = OPD['eval_avg4']
    narrow = W < 500
    pitch, bh = (42, 11) if narrow else (30, 11)
    x0, x1 = (44, W - 46) if narrow else (236, W - 96)
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
    cy_o = ys[i_ours] + bh / 2
    if narrow:
        svg.rect(4, cy_o - 30, W - 8, 42, 'band', rx=4)
    else:
        svg.rect(8, cy_o - pitch / 2 + 2, W - 16, pitch - 4, 'band', rx=4)
    frame(svg, (x0, top - 14, x1, y_end), sx, None, [0, 10, 20, 30, 40, 50], [], grid='x' if (phone_grid or not narrow) else '',
          xtitle=T('4-benchmark average (MATH-500, AIME 2024–26)', '4 项平均分（MATH-500、AIME 2024–26）'))
    if baseline and (phone_grid or not narrow):      # on phones the names cross x0, so no vertical line there either
        svg.line(x0, top - 14, x0, y_end, 'axis')
    lab_x = x0 - 52
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
        op = (' opacity=".42"' if baseline else ' opacity=".5"') if kind == 'ref' else (' opacity=".45"' if kind == 'variant' else '')
        svg.line(x0 + (1 if baseline else 0), cy, sx(v), cy, f'line l{idx}', 'stroke-width="2"' + op)
        if kind == 'variant':
            svg.mark(f'{lab[0]}: {v:.2f}', ring(sx(v), cy, 5, 2, 's1'))
        else:
            svg.mark(f'{lab[0]}: {v:.2f}', f'<circle class="dot s{idx}" cx="{sx(v):.1f}" cy="{cy:.1f}" r="{6 if strong else 5}" stroke-width="2"/>')
        svg.text(x0 - 12, cy + 4.2, f'{v:.1f}', cls=tcls, anchor='end', size=FS_LABEL)
        if cost and lab[0].startswith('GRPO'):
            note = T('2.6× the GPU-hours, 12× the rollouts', '2.6 倍卡时、12 倍 rollout')
            if narrow:
                svg.text(sx(v) - 10, cy - 7, note, cls='t-muted', anchor='end', size=FS_TICK)
            else:
                svg.text(sx(v) + 12, cy + 4, note, cls='t-muted', size=FS_TICK)
    yo, yt = ys[i_ours - 1] + bh / 2, ys[i_ours] + bh / 2
    xb = sx(d['takeover_conclude_40']) + 18
    bracket(svg, xb, yo, yt, signed(d['takeover_conclude_40'] - d['opd_40']))
    if cost:
        svg.text(xb + 6, (yo + yt) / 2 + 18, T('≈ same GPU-h', '卡时相近'), cls='t-muted', size=FS_TICK)
    return svg


# ============================================================================ opd-budget
def budget(W, verdict=False):
    """Round-1 merge. Polish: the ring and the leader thinner and lighter, the band label in the band's own gray.
    verdict=True (innovative): the (a) finding moves out of the plot into a one-line reading under the panel title,
    the same device as the HotpotQA chart, and the plot keeps only the ring at 16k and a dotted line carrying its
    43.5 across to 32k, where it can be read against OPD's 40.7."""
    b, xs = c1._budget()
    narrow = W < 500
    kfmt = c1.kfmt
    x0, x1 = (44, W - 52) if narrow else (64, W - 150)
    hA, hB, hC, gap = (152, 76, 72, 34) if not narrow else (150, 76, 72, 40)
    yA = (30 if not narrow else 56) + (14 if verdict else 0)
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
    k16 = b['tokens'].index(16384)
    o32, s16 = b['opd_40'][-1], b['takeover_40'][k16]
    px, py = sx(xs[k16]), syA(s16)
    if verdict:
        svg.line(px + 6, py, x1, py, 'leader', 'stroke-dasharray="2 3"')
    for idx, key in ((2, 'opd_40'), (1, 'takeover_40')):
        path_line(svg, list(zip(xs, b[key])), sx, syA, idx)
        dots(svg, [(x, y) for x, y, t in zip(xs, b[key], b['tokens']) if t in c1.DOUBLINGS], sx, syA, idx, r=3)
    if narrow:
        label_stack(svg, x1 + 8, [(syA(b['takeover_40'][-1]), f'{b["takeover_40"][-1]:.1f}', 't-strong'), (syA(b['opd_40'][-1]), f'{b["opd_40"][-1]:.1f}', '')], min_gap=15)
    else:
        label_stack(svg, x1 + 8, [(syA(b['takeover_40'][-1]), f'Scaffold-OPD {b["takeover_40"][-1]:.1f}', 't-strong'),
                                  (syA(b['opd_40'][-1]), f'OPD {b["opd_40"][-1]:.1f}', '')], min_gap=15)
    svg.add(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" class="ring" stroke-width="1.2"/>')
    if verdict:
        svg.text(x0, A[1] - 12, T(f'Capped at 16k, Scaffold-OPD ({s16:.1f}) is still {s16 - o32:.1f} above OPD at 32k ({o32:.1f})',
                                  f'限到 16k，Scaffold-OPD（{s16:.1f}）仍比 OPD 在 32k（{o32:.1f}）高 {s16 - o32:.1f}'), size=FS_TICK)
        panel_title(svg, x0, A[1] - 28, 'a', T('Accuracy', '准确率'), T('4-benchmark average', '4 项平均'))
    else:
        ty = syA(21 if not narrow else 9)
        svg.line(px, py + 6, px, ty - 13, 'leader')
        svg.text(px, ty, T(f'Scaffold-OPD at 16k: {s16:.1f}', f'Scaffold-OPD 在 16k：{s16:.1f}'), cls='t-strong', anchor='end', size=FS_TICK)
        svg.text(px, ty + 14, T(f'already {s16 - o32:.1f} above OPD at 32k ({o32:.1f})', f'已比 OPD 在 32k（{o32:.1f}）高 {s16 - o32:.1f}'), anchor='end', size=FS_TICK)
        panel_title(svg, x0, A[1] - 12, 'a', T('Accuracy', '准确率'), T('4-benchmark average', '4 项平均'))
    syB = scale(-5, 8, B_[3], B_[1])
    frame(svg, B_, sx, syB, [], [-4, 0, 4, 8], kfmt, lambda v: signed(v, 0) if v else '0')
    for pos, poly in d1._band_polys(xs, b['gap_40'], b['gap_se_40']):
        up = [(x, g + s) for x, g, s in poly]
        lo = [(x, g - s) for x, g, s in poly]
        svg.path(polyline(up, sx, syB) + ' L' + polyline(list(reversed(lo)), sx, syB)[1:] + ' Z', 'wash1' if pos else 'wash2')
    svg.line(x0, syB(0), x1, syB(0), 'axis', 'stroke-dasharray="3 3"')
    for pos, seg in seg_sign(xs, b['gap_40']):
        path_line(svg, seg, sx, syB, 1 if pos else 2)
    for t_ in (8192, 16384, 32768):
        k = b['tokens'].index(t_)
        g = b['gap_40'][k]
        svg.circle(sx(xs[k]), syB(g), 3, f'dot {"s1" if g >= 0 else "s2"}', 'stroke-width="1.5"')
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
        label_stack(svg, x1 + 8, [(syC(b['aime_finished_opd_40'][-1]), 'OPD', 't-muted'), (syC(b['aime_finished_takeover_40'][-1]), 'Scaffold-OPD', 't-muted')], min_gap=14, size=FS_TICK)
    panel_title(svg, x0, C[1] - 12, 'c', T('AIME answers finished', '写完的 AIME 回答'), '%')
    svg.text((x0 + x1) / 2, C[3] + 34, T('evaluation budget, tokens (log scale)', '评测预算，token（对数刻度）'), cls='t-muted', anchor='middle', size=FS_TICK)
    return svg


# ============================================================================ opd-training
def training(W, starts=False, tidy=False):
    """Round-1 merge: (a) response length, (b) teacher tokens per answer, (c) their share. tidy=True (polish): (b) and
    (c) get the same height and a little more of it, and the share axis is labelled in percent. starts=True (innovative): (a) also labels where each line
    starts, so the caption's 'about threefold' can be read off the chart (≈1.0k → 3.4k, ≈1.8k → 5.4k)."""
    t, tk, op, teach = c1._train()
    tr = OPD['train']
    narrow = W < 500
    if narrow:
        H = 650
        bA = (48, 62, W - 70, 222)
        bB, bC = (48, 318, W - 70, 412), (48, 476, W - 70, 570)
    else:
        H = 324 if tidy else 316
        bA = (56, 62, W / 2 - 74, H - 52)
        if tidy:
            bB, bC = (W / 2 + 54, 62, W - 64, 148), (W / 2 + 54, 186, W - 64, H - 52)
        else:
            bB, bC = (W / 2 + 54, 62, W - 64, 140), (W / 2 + 54, 194, W - 64, H - 52)
    svg = Svg(W, H, 'Response length, and the teacher-written tokens per answer in Scaffold-OPD and their share of all tokens')
    key_lines(svg, bA[0], 18, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    panel_title(svg, bA[0], bA[1] - 16, 'a', T('Response length', '回答长度'), T('tokens', 'token'))
    sxa, sya = scale(0, 60, bA[0], bA[2]), scale(0, 6000, bA[3], bA[1])
    for idx, steps, vals in ((2, tr['opd']['step'], tr['opd']['response_length']), (1, t['step'], t['response_length'])):
        for s_, v in zip(steps, vals):
            if v is not None and not (idx == 1 and s_ == 19):
                svg.circle(sxa(s_), sya(min(v, 6000)), 1.6, f's{idx}', 'opacity=".28"')
    c1._length_panel(svg, bA, tk, op)
    if starts:
        for pts, below in ((tk, True), (op, False)):
            x_, y_ = pts[0]
            svg.text(sxa(x_) + 4, sya(y_) + (16 if below else -9), f'≈ {y_ / 1000:.1f}k', cls='t-muted', size=FS_TICK)
    panel_title(svg, bB[0], bB[1] - 16, 'b', T('Teacher tokens per answer', '每条回答的老师 token'), 'Scaffold-OPD')
    sx = scale(0, 60, bB[0], bB[2])
    sy = scale(0, 200, bB[3], bB[1])
    svg.rect(bB[0], sy(150), bB[2] - bB[0], sy(100) - sy(150), 'band')
    frame(svg, bB, sx, sy, [], [0, 100, 200])
    for v in (0, 20, 40, 60):
        svg.line(sx(v), bB[3], sx(v), bB[3] + 4, 'axis')
    for s_, v in zip(t['step'], t['teacher_tokens_per_answer']):
        if v is not None and s_ != 19:
            svg.circle(sx(s_), sy(min(v, 200)), 1.6, 's5', 'opacity=".35"')
    path_line(svg, teach, sx, sy, 5)
    svg.circle(sx(teach[-1][0]), sy(teach[-1][1]), 3.2, 'dot s5', 'stroke-width="1.5"')
    hits(svg, teach, sx, sy, lambda x, y: f'step {x}: {y:.0f} teacher tokens per answer')
    svg.text(bB[2] + 8, sy(teach[-1][1]) + 4, f'{teach[-1][1]:.0f}', cls='t-strong', size=FS_LABEL)
    s0 = 100 * c1._window(t, 1, 5, 'teacher_token_ratio')
    s1 = 100 * c1._window(t, 56, 60, 'teacher_token_ratio')
    panel_title(svg, bC[0], bC[1] - 16, 'c', T('Teacher share of the tokens', '老师 token 占比'), '%' if not tidy else 'Scaffold-OPD')
    syc = scale(0, 20, bC[3], bC[1])
    frame(svg, bC, sx, syc, [0, 20, 40, 60], [0, 10, 20], str, (lambda v: f'{v}%') if tidy else str, xtitle=T('training step', '训练步'))
    ratio = d1._ratio(t)
    for s_, v in zip(t['step'], t['teacher_token_ratio']):
        if v is not None and s_ != 19:
            svg.circle(sx(s_), syc(min(100 * v, 20)), 1.6, 's5', 'opacity=".35"')
    path_line(svg, ratio, sx, syc, 5)
    svg.circle(sx(ratio[-1][0]), syc(ratio[-1][1]), 3.2, 'dot s5', 'stroke-width="1.5"')
    hits(svg, ratio, sx, syc, lambda x, y: f'step {x}: {y:.1f}% of the tokens written by the teacher')
    svg.text(sx(5) + 4, syc(s0) - 8, f'{s0:.0f}%', cls='t-strong', size=FS_LABEL)
    svg.text(bC[2] + 8, syc(ratio[-1][1]) + 4, f'{s1:.0f}%', cls='t-strong', size=FS_LABEL)
    return svg


# ============================================================================ opd-compute
def compute(W, ledger=False, caps=False):
    """Round-1 merge. Polish: the point labels split into the stage name (ink) and its score (semibold), the inset
    title in the panel-title colour, the inset's value column aligned. ledger=True (innovative): the inset gives way
    to a cost ledger under the axis, one bar per run on the same GPU-hour scale (Scaffold-OPD alone 13.2 h; the
    pipeline's three stages 16.8 + 15.4 + 20.0 h), so the ≈ 4× is two lengths you can compare.
    caps=True (the final, 11-17 capitals pass): every standalone label in sentence case — 'Full pipeline', the axis
    title, 'Same score · …', 'Base'; round 2 itself is kept as it was drawn."""
    cap = (lambda t: t[:1].upper() + t[1:]) if caps else (lambda t: t)
    pts, alone = c1._compute_data()
    g = OPD['gpu_hours']['pipeline']
    narrow = W < 500
    H = (330 if not narrow else 360) + (64 if ledger else 0)
    box = (46, 44, W - (28 if narrow else 118), (330 if not narrow else 360) - 44)
    svg = Svg(W, H, 'Score against cumulative training GPU-hours: the full pipeline and Scaffold-OPD alone, and ' + ('the GPU-hours of each run' if ledger else 'the points gained per GPU-hour'))
    key_lines(svg, box[0], 16, [(2, T(cap('full pipeline'), '全流程')), (1, T('Scaffold-OPD alone', '只做 Scaffold-OPD'))])
    sx, sy = scale(0, 56, box[0], box[2]), scale(20, 52, box[3], box[1])
    frame(svg, box, sx, sy, [0, 10, 20, 30, 40, 50], [20, 30, 40, 50], xtitle=None if ledger else T(cap('cumulative training GPU-hours (2 × A100)'), '累计训练卡时（2 × A100）'))
    svg.text(box[0], box[1] - 10, T('4-benchmark average', '4 项平均分'), cls='t-muted', size=FS_TICK)
    path_line(svg, pts, sx, sy, 2)
    path_line(svg, [pts[0], alone], sx, sy, 1)
    c3x = pts[-1][0]
    span(svg, sx(alone[0]), sx(c3x), sy(50), T(cap(f'same score · ≈ {c3x / alone[0]:.0f}× the GPU-hours'), f'分数相同 · 卡时约 {c3x / alone[0]:.0f} 倍'),
         drops=[(sx(alone[0]), sy(alone[1]) - 8), (sx(c3x), sy(pts[-1][1]) - 8)])
    labels = [T(cap('base'), '基座'), T('+ SFT'), T('+ Scaffold-OPD'), T('+ GRPO on failures', '+ 错题回流 GRPO')]

    def two_part(x, y, name, val, anchor='start', cls_name='', cls_val='t-strong'):
        wn = 600 if cls_name == 't-strong' else 400      # measure each part in the weight it is drawn in
        wv = 600 if cls_val == 't-strong' else 400

        def draw(i):
            nm = pick(name, i)
            if anchor == 'end':
                svg.text(x, y, val, cls=cls_val, anchor='end', size=FS_TICK)
                svg.text(x - svg.tw(val, FS_TICK, wv) - 4, y, nm, cls=cls_name, anchor='end', size=FS_TICK)
            else:
                svg.text(x, y, nm, cls=cls_name, size=FS_TICK)
                svg.text(x + svg.tw(nm, FS_TICK, wn) + 4, y, val, cls=cls_val, size=FS_TICK)
        per_lang(svg, draw)

    for k, ((x, y), lab) in enumerate(zip(pts, labels)):
        svg.mark(f'{lab[0]}: {y:.2f} after {x:.1f} GPU-hours', f'<circle class="dot s2" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4"/>')
        if k == 0:
            two_part(sx(x) + 8, sy(y) + 15, lab, f'{y:.1f}', cls_name='t-muted', cls_val='t-muted')
        elif k == 3:
            if narrow:
                two_part(sx(x) - 7, sy(y) - 9, lab, f'{y:.1f}', anchor='end')
            else:
                two_part(sx(x) + 8, sy(y) + 16, lab, f'{y:.1f}')
        else:
            two_part(sx(x) + 6, sy(y) + 17, lab, f'{y:.1f}')
    svg.mark(f'Scaffold-OPD alone: {alone[1]:.2f} after {alone[0]:.1f} GPU-hours',
             f'<circle class="dot s1" cx="{sx(alone[0]):.1f}" cy="{sy(alone[1]):.1f}" r="4.5"/>')
    two_part(sx(alone[0]) + 9, sy(alone[1]) + 16, T('Scaffold-OPD alone', '只做 Scaffold-OPD'), f'{alone[1]:.1f}', cls_name='t-strong')
    if ledger:
        yl = box[3] + 34
        rows_ = [(T('alone', '单独'), [(0, alone[0], 's1', T(f'{alone[0]:.1f} h', f'{alone[0]:.1f} 小时'))]),
                 (T('pipeline', '全流程'), [(0, pts[1][0], 's2', T(f'SFT {g["sft_incl_teacher_data"]:.1f} h', f'SFT {g["sft_incl_teacher_data"]:.1f} 小时')),
                                           (pts[1][0], pts[2][0], 's2', T(f'Scaffold-OPD {g["takeover_40"]:.1f} h', f'Scaffold-OPD {g["takeover_40"]:.1f} 小时')),
                                           (pts[2][0], pts[3][0], 's2', T(f'GRPO {g["grpo_30"]:.1f} h', f'GRPO {g["grpo_30"]:.1f} 小时'))])]
        for j, (name, segs) in enumerate(rows_):
            yy = yl + j * 22
            svg.text(box[0] - 7, yy + 8, name, cls='t-muted', anchor='end', size=FS_TICK)
            for k, (a_, z_, cls, lab) in enumerate(segs):
                op = '' if cls == 's1' else (' opacity=".9"', ' opacity=".6"', ' opacity=".35"')[k]
                svg.add(f'<rect x="{sx(a_) + (1 if k else 0):.1f}" y="{yy:.1f}" width="{sx(z_) - sx(a_) - (1 if k else 0):.1f}" height="11" rx="2" class="{cls}"{op}/>')
                if not narrow or k == 0:
                    svg.text(sx(z_) + 5 if cls == 's1' else (sx(a_) + sx(z_)) / 2, yy - 3 if cls != 's1' else yy + 9, lab,
                             cls='t-muted' if cls != 's1' else '', anchor='start' if cls == 's1' else 'middle', size=FS_TICK)
        svg.text((box[0] + box[2]) / 2, H - 8, T('cumulative training GPU-hours (2 × A100)', '累计训练卡时（2 × A100）'), cls='t-muted', anchor='middle', size=FS_TICK)
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
def sft_rl(W, dumbbell=False, polish=False):
    """Round-1 merge (one label column for both splits). polish=True: the column headers say 'Seen games' /
    'Unseen games' (one table, so the panel letters go), the gain columns get a hairline rule under their header,
    and the zero ends of the bars sit on a baseline. dumbbell=True (innovative): each family is a dumbbell, a hollow
    gray dot after SFT and a blue dot after RL joined by the gain, which drops the heavy gray bars."""
    narrow = W < 500
    seen_order = c1._fam('seen')[3]
    svg_label = 'ALFWorld success by task family after SFT and the gain from 100 RL steps, sorted by the gain on seen games'

    def keys(svg):
        def k(i):
            xx = 16 if not narrow else 8
            if dumbbell:
                for kind, s in (('sft', pick(T('after SFT', 'SFT 后'), i)), ('rl', pick(T('after 100 RL steps', '100 步 RL 后'), i))):
                    if kind == 'sft':
                        svg.add(ring(xx + 5, 14, 4, 1.8, 's3'))
                    else:
                        svg.add(f'<circle cx="{xx + 5:.1f}" cy="14" r="4.5" class="s1"/>')
                    svg.text(xx + 15, 18, s, size=FS_LABEL)
                    xx += 15 + text_w(s, FS_LABEL) + 18
                return
            for cls, s, op in (('s3', pick(T('after SFT', 'SFT 后'), i), ' opacity=".55"'), ('s1', pick(T('gain from 100 RL steps', '100 步 RL 的提升'), i), '')):
                svg.add(f'<rect x="{xx:.1f}" y="9" width="10" height="10" rx="2" class="{cls}"{op}/>')
                svg.text(xx + 15, 18, s, size=FS_LABEL)
                xx += 15 + text_w(s, FS_LABEL) + 18
        per_lang(svg, k)

    def bar(svg, fam, split, a, b, gain, x0b, x1b, y, gx, key, counts=True):
        sx = scale(0, 100, x0b, x1b)
        (sa, n), (sb, _) = a[fam], b[fam]
        pa, pb = 100 * sa / n, 100 * sb / n
        if dumbbell:
            svg.line(sx(pa) + 4, y, sx(pb) - 4, y, 'line l1', 'stroke-width="2.5" opacity=".55"')
            svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sa}/{n} after SFT', ring(sx(pa), y, 4, 1.8, 's3'))
            svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sb}/{n} after RL', f'<circle class="dot s1" cx="{sx(pb):.1f}" cy="{y:.1f}" r="{5 if key else 4.5}" stroke-width="1.5"/>')
        else:
            bh_ = 8
            svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sa}/{n} after SFT', f'<path class="bar s3" opacity=".55" d="{hbar(x0b, y - bh_ / 2, max(sx(pa) - 1, x0b + 1), bh_, 2)}"/>')
            svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sb}/{n} after RL', f'<path class="bar s1" d="{hbar(sx(pa) + 1, y - bh_ / 2, max(sx(pb), sx(pa) + 3), bh_, 2)}"/>')
        svg.text(gx, y + 4, f'+{gain[fam]:.0f}', cls='t-strong' if key else 't-muted', anchor='end', size=FS_LABEL)
        if key and counts:
            svg.text((sx(pa) + sx(pb)) / 2, y + 17, f'{sa}/{n} → {sb}/{n}', cls='t-muted', anchor='middle', size=FS_TICK)

    if not narrow:
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
            if polish:
                svg.text(xa, top - 20, T(f'{split.capitalize()} games', f'{split} 游戏'), cls='t-strong', size=13)
                svg.text(xa + svg.tw(T(f'{split.capitalize()} games', f'{split} 游戏'), 13, 600) + 8, top - 20, T('success, %', '成功率，%'), cls='t-faint', size=FS_TICK)
            else:
                panel_title(svg, xa, top - 20, 'ab'[k], T(split, split), T('success, %', '成功率，%'))
            svg.text(gx, top - 20, T('gain', '提升'), cls='t-muted', anchor='end', size=FS_TICK)
            frame(svg, (xa, top - 8, xb, bot), sx, None, [0, 25, 50, 75, 100], [], grid='x')
            if polish and not dumbbell:
                svg.line(xa, top - 8, xa, bot, 'axis')
            for i, fam in enumerate(seen_order):
                y = top + i * pitch + pitch / 2 - 4
                bar(svg, fam, split, a, b, gain, xa, xb, y, gx, fam == 'pick_two_obj_and_place')
        for i, fam in enumerate(seen_order):
            y = top + i * pitch + pitch / 2 - 4
            key = fam == 'pick_two_obj_and_place'
            svg.text(lab_r, y + 4, FAM_NAMES[fam], cls='t-strong' if key else '', anchor='end', size=FS_LABEL)
        return svg
    top = 76
    rowh = 46
    H = top + rowh * len(seen_order) + 34
    svg = Svg(W, H, svg_label)
    keys(svg)
    groups = [('seen', 12, 124, 156), ('unseen', 178, 290, 322 if W > 340 else W - 4)]
    for k, (split, xa, xb, gx) in enumerate(groups):
        if polish:
            svg.text(xa, top - 22, T(split.capitalize(), split), cls='t-strong', size=13)
        else:
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


# ============================================================================ scr-vs-grpo
def vs(W, keyed=False, oneline=False):
    """Round-1 merge (means written under the lead strip). oneline=True (polish): on desktop the two lines under each
    panel become one ('ahead at 16 of 21 validations · last five 82.3 vs 61.0'), and the McNemar note is muted for
    both splits, bold only on its p when it is significant. keyed=True (innovative): the late-stage means go back into
    the gray band, but keyed: a short blue and orange line before each number, so the band reads on its own and
    nothing is written under the strip except the count."""
    g, r, disc = c1._vs_data()
    narrow = W < 500
    extra = 16 if not (keyed or (oneline and not narrow)) else 0
    if narrow:
        H = 600 + 2 * extra
        bx = [(44, 64, W - 56, 212), (44, 344 + extra, W - 56, 492 + extra)]
    else:
        H = 318 + extra
        bx = [(46, 64, W / 2 - 52, 220), (W / 2 + 52, 64, W - 50, 220)]
    svg = Svg(W, H, 'StepCredit-RL vs GRPO: validation success over 200 steps, and which run is ahead at each validation')
    key_lines(svg, bx[0][0], 18, [(1, 'StepCredit-RL'), (2, 'GRPO')])
    for k, (name, A) in enumerate(zip(('seen', 'unseen'), bx)):
        sx, sy = scale(0, 200, A[0], A[2]), scale(0, 100, A[3], A[1])
        panel_title(svg, A[0], A[1] - 16, 'ab'[k], T(name, name), T('success, %', '成功率，%'))
        p_ = float(disc[name]['p'])
        if oneline:
            pt = f'p = {c1._pfmt(p_)}'
            svg.text(A[2], A[1] - 16, pt, cls='t-strong' if p_ < 0.05 else 't-muted', anchor='end', size=FS_TICK)
            svg.text(A[2] - svg.tw(pt, FS_TICK, 600 if p_ < 0.05 else 400) - 4, A[1] - 16, 'McNemar', cls='t-muted', anchor='end', size=FS_TICK)
        else:
            svg.text(A[2], A[1] - 16, f'McNemar p = {c1._pfmt(p_)}', cls='t-strong' if p_ < 0.05 else 't-muted', anchor='end', size=FS_TICK)
        svg.rect(sx(160), A[1], sx(200) - sx(160), A[3] - A[1], 'band')
        frame(svg, A, sx, sy, [0, 50, 100, 150, 200], [0, 25, 50, 75, 100])
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
        if keyed:
            bxl = sx(160) + 6
            for j, (idx, m) in enumerate(((1, lg), (2, lr))):
                yy = A[1] + 12 + j * 13
                svg.line(bxl, yy - 4, bxl + 9, yy - 4, f'line l{idx}', 'stroke-width="2"')
                svg.text(bxl + 13, yy, f'{m:.1f}', cls='t-strong' if j == 0 else '', size=FS_TICK)
        ys = A[3] + 32
        ahead = 0
        sq = 8
        for (s_, a_), (_, b_) in zip(g[name], r[name]):
            d_ = a_ - b_
            cls = 's1' if d_ > 0.05 else ('s2' if d_ < -0.05 else 's3')
            ahead += d_ > 0.05
            svg.mark(f'step {s_}: {signed(d_)} points', f'<rect class="{cls}" x="{sx(s_) - sq / 2:.1f}" y="{ys:.1f}" width="{sq}" height="{sq}" rx="1.5"/>')
        lead = T(f'StepCredit-RL ahead at {ahead} of {len(g[name])} validations', f'{len(g[name])} 次验证中 StepCredit-RL 领先 {ahead} 次')
        means = T(f'mean of the last five (gray band): {lg:.1f} vs {lr:.1f}', f'最后 5 次（灰色区）平均：{lg:.1f} 对 {lr:.1f}')
        if keyed:
            svg.text(A[0], ys + 24, lead, cls='t-muted', size=FS_TICK)
        elif oneline and not narrow:
            svg.text(A[0], ys + 24, T(f'Ahead at {ahead} of {len(g[name])} validations · last five {lg:.1f} vs {lr:.1f}',
                                      f'{len(g[name])} 次验证领先 {ahead} 次 · 最后 5 次 {lg:.1f} 对 {lr:.1f}'), cls='t-muted', size=FS_TICK)
        else:
            svg.text(A[0], ys + 24, lead, cls='t-muted', size=FS_TICK)
            svg.text(A[0], ys + 40, T(f'Mean of the last five (gray band): {lg:.1f} vs {lr:.1f}', means[1]), cls='t-muted', size=FS_TICK)
    return svg


# ============================================================================ scr-updates
def updates(W, shared_y=False, lead=False, brk=False):
    """Round-1 merge (per step | per hour). shared_y=True (polish): both panels use the same 0–100 scale, so (b) drops
    its tick labels, (b) gets the extra width (it carries the span), and the titles say what the x-axis is.
    lead=True (innovative): panel (a) shades the lead of four updates over one (the same wash as the GRPO chart) and
    brackets the step-100 gap the page quotes (76.4% vs 51.4%); brk=True draws the bracket alone."""
    four, one = c1._upd()
    narrow = W < 500
    if narrow:
        H = 610
        bS, bH = (48, 78, W - 40, 250), (48, 352, W - 40, 552)
    else:
        H = 340
        if shared_y:
            bS, bH = (48, 78, 262, H - 52), (300, 78, W - 92, H - 52)
        else:
            bS, bH = (48, 78, 286, H - 52), (352, 78, W - 92, H - 52)
    svg = Svg(W, H, 'Seen success for four updates per step and for one, against training steps and against wall-clock hours')
    key_lines(svg, bS[0], 18, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
    ta = T('By training step', '按训练步') if shared_y else T('Per training step', '按训练步')
    tb = T('By wall-clock time', '按耗时') if shared_y else T('Per hour', '按耗时')
    panel_title(svg, bS[0], bS[1] - 16, 'a', ta, T('seen success, %', 'seen 成功率，%'))
    panel_title(svg, bH[0], bH[1] - 16, 'b', tb, None if (shared_y and not narrow) else T('seen success, %', 'seen 成功率，%'))
    sx, sy = scale(0, 150, bS[0], bS[2]), scale(0, 100, bS[3], bS[1])
    frame(svg, bS, sx, sy, [0, 50, 100, 150], [0, 25, 50, 75, 100], xtitle=T('training step', '训练步'))
    if lead:
        steps4 = [st for st, _, _ in four]
        wash_between(svg, steps4, [s for _, s, _ in four], [s for st, s, _ in one if st <= 100], sx, sy)
    for idx, rows in ((3, one), (1, four)):
        pts = [(st, s) for st, s, _ in rows]
        path_line(svg, pts, sx, sy, idx)
        hits(svg, pts, sx, sy, lambda x, y: f'step {x}: {y:.1f}%')
    s4 = [s for st, s, _ in four if st == 100][0]
    s1 = [s for st, s, _ in one if st == 100][0]
    svg.circle(sx(100), sy(s4), 3.6, 'dot s1', 'stroke-width="1.5"')
    svg.circle(sx(100), sy(s1), 3.6, 'dot s3', 'stroke-width="1.5"')
    if lead or brk:
        xb = sx(100) + 9
        svg.path(f'M{xb - 4:.1f},{sy(s4):.1f} H{xb:.1f} V{sy(s1):.1f} H{xb - 4:.1f}', 'leader')
        svg.text(xb + 5, sy(s4) + 4, f'{s4:.1f}%', cls='t-strong', size=FS_TICK)
        svg.text(xb + 5, sy(s1) + 4, f'{s1:.1f}%', size=FS_TICK)
    else:
        svg.text(sx(100) - 7, sy(s4) - 8, f'{s4:.1f}%', cls='t-strong', anchor='end', size=FS_TICK)
        svg.text(sx(100) + 7, sy(s1) + 15, f'{s1:.1f}%', size=FS_TICK)
    if shared_y and not narrow:
        sxh, syh = scale(0, 30, bH[0], bH[2]), scale(0, 100, bH[3], bH[1])
        frame(svg, bH, sxh, syh, [0, 5, 10, 15, 20, 25, 30], [0, 25, 50, 75, 100], str, lambda v: '', xtitle=T('hours on 2 × A100', '耗时（2 × A100，小时）'))
        _hours_lines(svg, bH, four, one, sxh, syh)
    else:
        d1._hours_panel(svg, bH, four, one, narrow, compact=not narrow)
    return svg


def _hours_lines(svg, box, four, one, sx, sy):
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
    svg.text(sx(e4[2]) + 8, sy(e4[1]) + 4, T(f'step 100 · {e4[1]:.1f}%', f'第 100 步 · {e4[1]:.1f}%'), cls='t-strong', size=FS_TICK)
    svg.text(sx(e1[2]) + 8, sy(e1[1]) + 4, T(f'step 150 · {e1[1]:.1f}%', f'第 150 步 · {e1[1]:.1f}%'), size=FS_TICK)
    span(svg, sx(e4[2]), sx(e1[2]), sy(92), T(f'about {e1[2] - e4[2]:.0f} h sooner', f'约早 {e1[2] - e4[2]:.0f} 小时'),
         drops=[(sx(e4[2]), sy(e4[1]) - 8), (sx(e1[2]), sy(e1[1]) - 8)], cls='t-muted', size=FS_TICK)


# ============================================================================ scr-hotpotqa
def hotpot(W, lolli=False, polish=False):
    """Round-1 merge. polish=True: the bar panel's subtitle shortened to '% of groups' so the three title rows end
    inside their panels, the verdict lines in ink, the step axis titled once per panel as 'training step'.
    lolli=True (innovative): panel (c) as two lollipops instead of bars, the same weight as the dots of (a) and (b),
    so the big blue block no longer dominates a chart whose main point is that EM did not move."""
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
    for k, key in enumerate(['em', 'repeat_queries', 'bars']):
        if narrow:
            box = (56, 74 + k * 250, W - 70, 74 + k * 250 + 160)
        else:
            box = (52 + k * pw, top, 52 + k * pw + pw - (60 if key == 'bars' else 82), H - 60)
        letter = 'abc'[k]
        if key == 'bars':
            panel_title(svg, box[0], box[1] - 30, letter, T('All-failed groups', '全错组'), T('% of groups', '占比 %') if polish else T('% of training groups', '占训练组 %'))
            svg.text(box[0], box[1] - 13, T('more groups give a learning signal', '更多组有学习信号'), size=FS_TICK)
            sy = scale(0, 30, box[3], box[1])
            frame(svg, box, lambda v: v, sy, [], [0, 10, 20, 30], str, str)
            cw = (box[2] - box[0]) / 2
            for j, (idx, v, lab) in enumerate(((1, 27, T('EM reward', 'EM 奖励')), (2, 4, T('shaped reward', '稠密奖励')))):
                cx = box[0] + cw * (j + 0.5)
                title = f'{lab[0]}: about {v}% of the groups had no successful answer'
                if lolli:
                    svg.line(cx, sy(0), cx, sy(v) + 6, f'line l{idx}', 'stroke-width="2.5"')
                    svg.mark(title, f'<circle class="dot s{idx}" cx="{cx:.1f}" cy="{sy(v):.1f}" r="6" stroke-width="2"/>')
                    svg.text(cx, sy(v) - 12, f'≈ {v}%', cls='t-strong', anchor='middle', size=FS_LABEL)
                else:
                    hw = 9
                    svg.mark(title, f'<path class="bar s{idx}" d="M{cx - hw:.1f},{sy(0):.1f} V{sy(v) + 3:.1f} A3,3 0 0 1 {cx - hw + 3:.1f},{sy(v):.1f} H{cx + hw - 3:.1f} A3,3 0 0 1 {cx + hw:.1f},{sy(v) + 3:.1f} V{sy(0):.1f} Z"/>')
                    svg.text(cx, sy(v) - 7, f'≈ {v}%', cls='t-strong', anchor='middle', size=FS_LABEL)
                svg.text(cx, box[3] + 16, lab, cls='t-muted', anchor='middle', size=FS_TICK)
            continue
        title, unit, (lo, hi), ticks, fmt, verdict = lines[key]
        sx, sy = scale(0, 200, box[0], box[2]), scale(lo, hi, box[3], box[1])
        panel_title(svg, box[0], box[1] - 30, letter, title, unit)
        svg.text(box[0], box[1] - 13, verdict, size=FS_TICK)
        frame(svg, box, sx, sy, [0, 100, 200], ticks, str, fmt, xtitle=T('training step', '训练步') if polish else T('step', '步'))
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
AES = {'opd-methods': lambda W: methods(W, baseline=True),
       'opd-budget': budget,
       'opd-training': lambda W: training(W, tidy=True),
       'opd-compute': compute,
       'scr-sft-rl': lambda W: sft_rl(W, polish=True),
       'scr-vs-grpo': lambda W: vs(W, oneline=True),
       'scr-updates': lambda W: updates(W, shared_y=True),
       'scr-hotpotqa': lambda W: hotpot(W, polish=True)}
INNO = {'opd-methods': lambda W: methods(W, cost=True),
        'opd-budget': lambda W: budget(W, verdict=True),
        'opd-training': lambda W: training(W, starts=True),
        'opd-compute': lambda W: compute(W, ledger=True),
        'scr-sft-rl': lambda W: sft_rl(W, dumbbell=True),
        'scr-vs-grpo': lambda W: vs(W, keyed=True),
        'scr-updates': lambda W: updates(W, lead=True),
        'scr-hotpotqa': lambda W: hotpot(W, lolli=True)}
MERGED = {'opd-methods': lambda W: methods(W, baseline=True),
          'opd-budget': lambda W: budget(W, verdict=True),
          'opd-training': lambda W: training(W, tidy=True),
          'opd-compute': compute,
          'scr-sft-rl': lambda W: sft_rl(W, dumbbell=True, polish=True),
          'scr-vs-grpo': lambda W: vs(W, oneline=True),
          'scr-updates': lambda W: updates(W, shared_y=True, brk=True),
          'scr-hotpotqa': lambda W: hotpot(W, polish=True)}
NOTES = {
    'opd-methods': 'Merged: aesthetic (a zero line under the stems, baseline stems a shade lighter). The cost notes were true but '
                   '"2.6× the GPU-hours" floats without its reference (OPD) inside the chart; the page text says it properly. '
                   'Final: the chart is clear and the data is simple, so it stops here.',
    'opd-budget': 'Merged: innovative. The (a) finding becomes a one-line reading under the title (the HotpotQA device); the plot keeps '
                  'the ring at 16k and a dotted line carrying 43.5 across to 32k, above OPD\'s 40.7. No text block inside the plot.',
    'opd-training': 'Merged: aesthetic ((b) and (c) the same height, share axis in percent, both titled Scaffold-OPD). Start labels '
                    '(≈ 0.9k, ≈ 1.7k) sat on the rising OPD line and did not make "threefold" any easier to see.',
    'opd-compute': 'Merged: aesthetic (stage name in ink, score in semibold). The GPU-hour ledger under the axis repeated the x '
                   'positions of the points and dropped the per-hour comparison. Final: it stops here.',
    'scr-sft-rl': 'Merged: innovative dumbbells (hollow gray = after SFT, blue = after RL, the connector is the gain) with the '
                  'aesthetic headers "Seen games" / "Unseen games". Half the ink of the bars, same reading. Caption needs updating.',
    'scr-vs-grpo': 'Merged: aesthetic (one line under each strip; McNemar muted, only the significant p in semibold). The keyed means '
                   'inside the band collided with the blue curve on seen games.',
    'scr-updates': 'Merged: aesthetic (one y scale, so (b) drops its tick labels and gets the width; titles name the x-axis) with '
                   'the innovative step-100 bracket (76.4% / 51.4%). The lead wash added a large blue area for a lead that never '
                   'changes sides.',
    'scr-hotpotqa': 'Merged: aesthetic (shorter (c) subtitle, "training step" axes). Lollipops made (c) look like two pins; bars '
                    'read as shares.',
}
