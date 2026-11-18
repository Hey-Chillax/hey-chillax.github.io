"""Chart cycle 2, round 3 (2026-11-17), the last of this cycle. BASE = round 2's merges (d2.MERGED); MERGED is final.

opd-compute stopped after round 2 (simple data, nothing left that made it clearer), so it appears here as BASE and
MERGED only; opd-methods gets a phone-only fix. opd-training and scr-sft-rl get a polish only.

Capitals pass (11-17, the user's diagram rule applied to the charts): every standalone label is in sentence case —
panel titles, legend entries, axis titles, annotations, point labels. Lowercase stays only for the gray unit or
qualifier subtitles after a title ("success, %", "tokens"), text that continues a label ("↳ without …"), identifiers
and maths ("p = 0.16"), and labels that start with a symbol or number ("+6.2", "−71%", "4 updates per step").
"""
from d_kit import (FAM_NAMES, FS_LABEL, FS_TICK, OPD, PAIRED, Svg, T, dots, frame, hits, key_lines, label_stack, ring,
                   panel_title, path_line, per_lang, pick, polyline, scale, seg_sign, signed, span, text_w, wash_between)
import figures  # noqa: E402,F401  load figures first (see d1)
import c1  # noqa: E402
import d1  # noqa: E402
import d2  # noqa: E402

BASE = dict(d2.MERGED)


# ============================================================================ opd-budget
def budget(W, lean=False):
    """Round-2 merge. Polish: the reading under (a)'s title is shorter, so it fits a phone ('Capped at 16k: 43.5, still
    2.7 above OPD at 32k (40.7)'), panel (a) is a little shorter now that it holds no text block, and the three
    readings of this chart all start with a capital like the other charts' readings. lean=True (innovative): (a)
    loses the wash between its curves, since (b) draws that gap with its error band, and the height goes to (b)."""
    b, xs = c1._budget()
    narrow = W < 500
    kfmt = c1.kfmt
    x0, x1 = (44, W - 52) if narrow else (64, W - 150)
    if lean:
        hA, hB, hC, gap = (124, 96, 72, 34) if not narrow else (124, 92, 72, 40)
    else:
        hA, hB, hC, gap = (140, 76, 72, 34) if not narrow else (140, 76, 72, 40)
    yA = (30 if not narrow else 56) + 14
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
    if not lean:
        wash_between(svg, xs, b['takeover_40'], b['opd_40'], sx, syA)
    k16 = b['tokens'].index(16384)
    o32, s16 = b['opd_40'][-1], b['takeover_40'][k16]
    px, py = sx(xs[k16]), syA(s16)
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
    svg.text(x0, A[1] - 12, T(f'Capped at 16k: {s16:.1f}, still {s16 - o32:.1f} above OPD at 32k ({o32:.1f})',
                              f'限到 16k：{s16:.1f}，仍比 OPD 在 32k（{o32:.1f}）高 {s16 - o32:.1f}'), size=FS_TICK)
    panel_title(svg, x0, A[1] - 28, 'a', T('Accuracy', '准确率'), T('4-benchmark average', '4 项平均'))
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
    svg.text((x0 + x1) / 2, C[3] + 34, T('Evaluation budget, tokens (log scale)', '评测预算，token（对数刻度）'), cls='t-muted', anchor='middle', size=FS_TICK)
    return svg


# ============================================================================ opd-training
def _length_panel(svg, box, tk, op, top=7000):
    """Response-length panel on a 0–7k scale: six raw OPD values lie above 6k (up to 6,775 at step 25), and the
    earlier 0–6k panel pinned them to its top edge."""
    sx, sy = scale(0, 60, box[0], box[2]), scale(0, top, box[3], box[1])
    frame(svg, box, sx, sy, [0, 20, 40, 60], [0, 2000, 4000, 6000], str, lambda v: f'{v / 1000:.0f}k' if v else '0',
          xtitle=T('Training step', '训练步'))
    path_line(svg, op, sx, sy, 2)
    path_line(svg, tk, sx, sy, 1)
    for idx, pts in ((2, op), (1, tk)):
        svg.circle(sx(pts[-1][0]), sy(pts[-1][1]), 3.2, f'dot s{idx}', 'stroke-width="1.5"')
    hits(svg, op, sx, sy, lambda x, y: f'OPD · step {x}: {y:,.0f} tokens')
    hits(svg, tk, sx, sy, lambda x, y: f'Scaffold-OPD · step {x}: {y:,.0f} tokens')
    label_stack(svg, box[2] + 8, [(sy(tk[-1][1]), f'{tk[-1][1]:,.0f}', 't-strong'), (sy(op[-1][1]), f'{op[-1][1]:,.0f}', '')])
    return sx, sy


def training(W):
    """Round-2 merge, polished: panel (a) runs to 7k so no raw value is clipped (six OPD steps exceed 6k; the 0–6k
    scale drew them on its top edge), and the right column's two panels share the same left edge, height and end-label
    column as before. No new idea this round: the three panels already draw the caption's three claims."""
    t, tk, op, teach = c1._train()
    tr = OPD['train']
    narrow = W < 500
    if narrow:
        H = 650
        bA = (48, 62, W - 70, 222)
        bB, bC = (48, 318, W - 70, 412), (48, 476, W - 70, 570)
    else:
        H = 324
        bA = (56, 62, W / 2 - 74, H - 52)
        bB, bC = (W / 2 + 54, 62, W - 64, 148), (W / 2 + 54, 186, W - 64, H - 52)
    svg = Svg(W, H, 'Response length, and the teacher-written tokens per answer in Scaffold-OPD and their share of all tokens')
    key_lines(svg, bA[0], 18, [(1, 'Scaffold-OPD'), (2, 'OPD')])
    panel_title(svg, bA[0], bA[1] - 16, 'a', T('Response length', '回答长度'), T('tokens', 'token'))
    sxa, sya = scale(0, 60, bA[0], bA[2]), scale(0, 7000, bA[3], bA[1])
    for idx, steps, vals in ((2, tr['opd']['step'], tr['opd']['response_length']), (1, t['step'], t['response_length'])):
        for s_, v in zip(steps, vals):
            if v is not None and not (idx == 1 and s_ == 19):
                svg.circle(sxa(s_), sya(v), 1.6, f's{idx}', 'opacity=".28"')
    _length_panel(svg, bA, tk, op)
    panel_title(svg, bB[0], bB[1] - 16, 'b', T('Teacher tokens per answer', '每条回答的老师 token'), 'Scaffold-OPD')
    sx = scale(0, 60, bB[0], bB[2])
    sy = scale(0, 200, bB[3], bB[1])
    svg.rect(bB[0], sy(150), bB[2] - bB[0], sy(100) - sy(150), 'band')
    frame(svg, bB, sx, sy, [], [0, 100, 200])
    for v in (0, 20, 40, 60):
        svg.line(sx(v), bB[3], sx(v), bB[3] + 4, 'axis')
    for s_, v in zip(t['step'], t['teacher_tokens_per_answer']):
        if v is not None and s_ != 19:
            svg.circle(sx(s_), sy(v), 1.6, 's5', 'opacity=".35"')
    path_line(svg, teach, sx, sy, 5)
    svg.circle(sx(teach[-1][0]), sy(teach[-1][1]), 3.2, 'dot s5', 'stroke-width="1.5"')
    hits(svg, teach, sx, sy, lambda x, y: f'Step {x}: {y:.0f} teacher tokens per answer')
    svg.text(bB[2] + 8, sy(teach[-1][1]) + 4, f'{teach[-1][1]:.0f}', cls='t-strong', size=FS_LABEL)
    s0 = 100 * c1._window(t, 1, 5, 'teacher_token_ratio')
    s1 = 100 * c1._window(t, 56, 60, 'teacher_token_ratio')
    panel_title(svg, bC[0], bC[1] - 16, 'c', T('Teacher share of the tokens', '老师 token 占比'), 'Scaffold-OPD')
    syc = scale(0, 20, bC[3], bC[1])
    frame(svg, bC, sx, syc, [0, 20, 40, 60], [0, 10, 20], str, lambda v: f'{v}%', xtitle=T('Training step', '训练步'))
    ratio = d1._ratio(t)
    for s_, v in zip(t['step'], t['teacher_token_ratio']):
        if v is not None and s_ != 19:
            svg.circle(sx(s_), syc(100 * v), 1.6, 's5', 'opacity=".35"')
    path_line(svg, ratio, sx, syc, 5)
    svg.circle(sx(ratio[-1][0]), syc(ratio[-1][1]), 3.2, 'dot s5', 'stroke-width="1.5"')
    hits(svg, ratio, sx, syc, lambda x, y: f'Step {x}: {y:.1f}% of the tokens written by the teacher')
    svg.text(sx(5) + 4, syc(s0) - 8, f'{s0:.0f}%', cls='t-strong', size=FS_LABEL)
    svg.text(bC[2] + 8, syc(ratio[-1][1]) + 4, f'{s1:.0f}%', cls='t-strong', size=FS_LABEL)
    return svg


# ============================================================================ scr-sft-rl
def sft_rl(W):
    """Round-2 merge (dumbbells), polished: the connector is a thin solid line in the series' light tone instead of a
    half-transparent thick one (no darker overlap where it meets the dots), the hollow SFT dot sits on a background
    disc so grid lines do not run through it, the key row's two dots are a size larger than the rest, like the key rows
    of the other charts, and the phone version uses the desktop structure (a label column on the left) instead of a
    name line above each row, so no grid line runs through a name."""
    narrow = W < 500
    seen_order = c1._fam('seen')[3]
    svg_label = 'ALFWorld success by task family after SFT and after 100 RL steps, sorted by the gain on seen games'

    def keys(svg):
        def k(i):
            xx = 16 if not narrow else 8
            for kind, s in (('sft', pick(T('After SFT', 'SFT 后'), i)), ('rl', pick(T('After 100 RL steps', '100 步 RL 后'), i))):
                if kind == 'sft':
                    svg.add(ring(xx + 5, 14, 4, 1.8, 's3'))
                else:
                    svg.add(f'<circle cx="{xx + 5:.1f}" cy="14" r="4.5" class="s1"/>')
                svg.text(xx + 15, 18, s, size=FS_LABEL)
                xx += 15 + text_w(s, FS_LABEL) + 18
        per_lang(svg, k)

    def dumbbell(svg, fam, split, a, b, gain, x0b, x1b, y, gx, key, counts=True):
        sx = scale(0, 100, x0b, x1b)
        (sa, n), (sb, _) = a[fam], b[fam]
        pa, pb = 100 * sa / n, 100 * sb / n
        r0, r1 = (4.6, 5.6) if key else (4, 4.6)
        svg.add(f'<line x1="{sx(pa) + r0:.1f}" y1="{y:.1f}" x2="{sx(pb) - r1:.1f}" y2="{y:.1f}" class="ln-blue" stroke-width="{2.4 if key else 2}"/>')
        svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sa}/{n} after SFT', ring(sx(pa), y, r0, 1.8, 's3'))
        svg.mark(f'{FAM_NAMES[fam][0]}, {split}: {sb}/{n} after RL', f'<circle class="dot s1" cx="{sx(pb):.1f}" cy="{y:.1f}" r="{r1}" stroke-width="1.5"/>')
        # round half up: unseen pick & place gains exactly 12.5 points (18/24 → 21/24), which '.0f' would print as +12
        svg.text(gx, y + 4, f'+{int(gain[fam] + 0.5)}', cls='t-strong' if key else 't-muted', anchor='end', size=FS_LABEL)
        if key and counts:
            svg.text((sx(pa) + sx(pb)) / 2, y + 17, f'{sa}/{n} → {sb}/{n}', cls='t-muted', anchor='middle', size=FS_TICK)

    if True:   # desktop and phone share one layout: a label column, then the two groups (phone: narrower, no subtitles)
        H = 278 if not narrow else 290
        svg = Svg(W, H, svg_label)
        keys(svg)
        top, bot = (74, H - 34) if not narrow else (72, H - 36)
        lab_r = 124 if not narrow else 82
        groups = [('seen', 140, 362, 404), ('unseen', 450, 672, 714)] if not narrow else [('seen', 92, 164, 196), ('unseen', 214, 286, W - 16)]
        pitch = (bot - top) / len(seen_order)
        for i, fam in enumerate(seen_order):
            if fam == 'pick_two_obj_and_place':
                y = top + i * pitch + pitch / 2 - 4
                svg.rect(8, y - pitch / 2 + 2, W - 16, pitch - 4, 'band', rx=4)
        for k, (split, xa, xb, gx) in enumerate(groups):
            a, b, gain, _ = c1._fam(split)
            sx = scale(0, 100, xa, xb)
            head = T(f'{split.capitalize()} games', f'{split} 游戏') if not narrow else T(split.capitalize(), split)
            svg.text(xa, top - 20, head, cls='t-strong', size=13)
            if not narrow:
                svg.text(xa + svg.tw(head, 13, 600) + 8, top - 20, T('success, %', '成功率，%'), cls='t-faint', size=FS_TICK)
            svg.text(gx, top - 20, T('Gain', '提升'), cls='t-muted', anchor='end', size=FS_TICK)
            frame(svg, (xa, top - 8, xb, bot), sx, None, [0, 25, 50, 75, 100] if not narrow else [0, 50, 100], [], grid='x')
            for i, fam in enumerate(seen_order):
                y = top + i * pitch + pitch / 2 - 4
                dumbbell(svg, fam, split, a, b, gain, xa, xb, y, gx, fam == 'pick_two_obj_and_place', counts=not narrow)
        for i, fam in enumerate(seen_order):
            y = top + i * pitch + pitch / 2 - 4
            key = fam == 'pick_two_obj_and_place'
            svg.text(lab_r, y + 4, FAM_NAMES[fam], cls='t-strong' if key else '', anchor='end', size=FS_LABEL if not narrow else FS_TICK)
        return svg


# ============================================================================ scr-vs-grpo
def vs(W, floor=False):
    """Round-2 merge. Polish: the one-line reading starts with its subject ('StepCredit-RL ahead at 16 of 21 ·
    last five 82.3 vs 61.0'), the strip squares are a pixel smaller with the same gaps, and on phones the two lines
    keep the same wording. floor=True (innovative): the late-stage means go into the gray band after all, keyed with a
    short blue and orange line, but at the band's floor, where both runs never are, so they label the band itself."""
    g, r, disc = c1._vs_data()
    narrow = W < 500
    if narrow:
        H = 546 if floor else 632       # floor: one text line under the second strip, ends near 522
        top2 = 316 if floor else 360
        bx = [(44, 64, W - 56, 212), (44, top2, W - 56, top2 + 148)]
    else:
        H = 300 if floor else 318
        bx = [(46, 64, W / 2 - 52, 220), (W / 2 + 52, 64, W - 50, 220)]
    svg = Svg(W, H, 'StepCredit-RL vs GRPO: validation success over 200 steps, and which run is ahead at each validation')
    key_lines(svg, bx[0][0], 18, [(1, 'StepCredit-RL'), (2, 'GRPO')])
    for k, (name, A) in enumerate(zip(('seen', 'unseen'), bx)):
        sx, sy = scale(0, 200, A[0], A[2]), scale(0, 100, A[3], A[1])
        panel_title(svg, A[0], A[1] - 16, 'ab'[k], T(f'{name.capitalize()} games', f'{name} 游戏'), T('success, %', '成功率，%'))
        p_ = float(disc[name]['p'])
        pt = f'p = {c1._pfmt(p_)}'
        svg.text(A[2], A[1] - 16, pt, cls='t-strong' if p_ < 0.05 else 't-muted', anchor='end', size=FS_TICK)
        svg.text(A[2] - svg.tw(pt, FS_TICK, 600 if p_ < 0.05 else 400) - 4, A[1] - 16, 'McNemar', cls='t-muted', anchor='end', size=FS_TICK)
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
        if floor:
            bxl = sx(160) + 6
            svg.text(bxl, A[3] - 34, T('Last 5', '最后 5 次'), cls='t-muted', size=FS_TICK)
            for j, (idx, m) in enumerate(((1, lg), (2, lr))):
                yy = A[3] - 20 + j * 13
                svg.line(bxl, yy - 4, bxl + 9, yy - 4, f'line l{idx}', 'stroke-width="2"')
                svg.text(bxl + 13, yy, f'{m:.1f}', cls='t-strong' if j == 0 else '', size=FS_TICK)
        ys = A[3] + 32
        ahead = 0
        sq = 7
        for (s_, a_), (_, b_) in zip(g[name], r[name]):
            d_ = a_ - b_
            cls = 's1' if d_ > 0.05 else ('s2' if d_ < -0.05 else 's3')
            ahead += d_ > 0.05
            svg.mark(f'Step {s_}: {signed(d_)} points', f'<rect class="{cls}" x="{sx(s_) - sq / 2:.1f}" y="{ys:.1f}" width="{sq}" height="{sq}" rx="1.5"/>')
        n = len(g[name])
        if floor:
            svg.text(A[0], ys + 23, T(f'StepCredit-RL ahead at {ahead} of {n} validations', f'{n} 次验证中 StepCredit-RL 领先 {ahead} 次'), cls='t-muted', size=FS_TICK)
        elif narrow:
            svg.text(A[0], ys + 23, T(f'StepCredit-RL ahead at {ahead} of {n} validations', f'{n} 次验证中 StepCredit-RL 领先 {ahead} 次'), cls='t-muted', size=FS_TICK)
            svg.text(A[0], ys + 39, T(f'Last five (gray band): {lg:.1f} vs {lr:.1f}', f'最后 5 次（灰色区）：{lg:.1f} 对 {lr:.1f}'), cls='t-muted', size=FS_TICK)
        else:
            svg.text(A[0], ys + 23, T(f'StepCredit-RL ahead at {ahead} of {n} · last five {lg:.1f} vs {lr:.1f}',
                                      f'StepCredit-RL 领先 {ahead}/{n} 次 · 最后 5 次 {lg:.1f} 对 {lr:.1f}'), cls='t-muted', size=FS_TICK)
    return svg


# ============================================================================ scr-updates
def updates(W, readings=False):
    """Round-2 merge. Polish: the hours axis ticks every 10 h like the step axis ticks every 50 steps (four labels
    each), the step markers in (b) a size smaller than the end points, the span label in ink, and the step-100 gap in (a)
    drawn as a plain line between the two points with 51.4% below-right of its point (the round-2 bracket put it on
    the gray line). readings=True
    (innovative): each panel gets a one-line reading under its title, the device of the budget and HotpotQA charts —
    (a) 'Ahead at every validation from step 10 to 100', (b) 'Step 100 about 13 h before step 150' — and the span
    loses its label."""
    four, one = c1._upd()
    narrow = W < 500
    dy = 14 if readings else 0
    if narrow:
        H = 610 + 2 * dy
        bS, bH = (48, 78 + dy, W - 40, 250 + dy), (48, 352 + 2 * dy, W - 40, 552 + 2 * dy)
    else:
        H = 340 + dy
        bS, bH = (48, 78 + dy, 262, H - 52), (300, 78 + dy, W - 92, H - 52)
    svg = Svg(W, H, 'Seen success for four updates per step and for one, against training steps and against wall-clock hours')
    key_lines(svg, bS[0], 18, [(1, T('4 updates per step', '每步 4 次更新')), (3, T('1 update per step', '每步 1 次更新'))])
    yt = 16 + (16 if readings else 0)
    panel_title(svg, bS[0], bS[1] - yt, 'a', T('By training step', '按训练步'), T('seen success, %', 'seen 成功率，%'))
    panel_title(svg, bH[0], bH[1] - yt, 'b', T('By wall-clock time', '按耗时'), T('seen success, %', 'seen 成功率，%') if narrow else None)
    if readings:
        svg.text(bS[0], bS[1] - 14, T('Ahead at every validation from step 10 to 100', '第 10 到 100 步每次验证都领先'), size=FS_TICK)
        svg.text(bH[0], bH[1] - 14, T('Step 100 about 13 h before step 150, and higher', '第 100 步比第 150 步早约 13 小时，且更高'), size=FS_TICK)
    sx, sy = scale(0, 150, bS[0], bS[2]), scale(0, 100, bS[3], bS[1])
    frame(svg, bS, sx, sy, [0, 50, 100, 150], [0, 25, 50, 75, 100], xtitle=T('Training step', '训练步'))
    for idx, rows in ((3, one), (1, four)):
        pts = [(st, s) for st, s, _ in rows]
        path_line(svg, pts, sx, sy, idx)
        hits(svg, pts, sx, sy, lambda x, y: f'Step {x}: {y:.1f}%')
    s4 = [s for st, s, _ in four if st == 100][0]
    s1 = [s for st, s, _ in one if st == 100][0]
    svg.circle(sx(100), sy(s4), 3.6, 'dot s1', 'stroke-width="1.5"')
    svg.circle(sx(100), sy(s1), 3.6, 'dot s3', 'stroke-width="1.5"')
    # the step-100 gap: a plain line between the two points (as in the HotpotQA chart), each value where its own line
    # leaves room — right of the blue end, below-right of the gray point (the gray line climbs on to the upper right)
    svg.line(sx(100), sy(s4) + 5, sx(100), sy(s1) - 5, 'leader')
    svg.text(sx(100) + 8, sy(s4) + 4, f'{s4:.1f}%', cls='t-strong', size=FS_TICK)
    svg.text(sx(100) + 7, sy(s1) + 15, f'{s1:.1f}%', size=FS_TICK)
    sxh, syh = scale(0, 30, bH[0], bH[2]), scale(0, 100, bH[3], bH[1])
    # phones show (b) under (a), so it keeps its own tick labels; desktop shares (a)'s
    frame(svg, bH, sxh, syh, [0, 10, 20, 30], [0, 25, 50, 75, 100], str, str if narrow else (lambda v: ''), xtitle=T('Hours on 2 × A100', '耗时（2 × A100，小时）'))
    for idx, rows in ((3, one), (1, four)):
        pts = [(h, s) for _, s, h in rows]
        path_line(svg, pts, sxh, syh, idx)
        hits(svg, pts, sxh, syh, lambda x, y: f'{x:g} h: {y:.1f}%')
        for st, s, h in rows:
            if st in (50, 100, 150):
                end = (idx == 1 and st == 100) or (idx == 3 and st == 150)
                svg.circle(sxh(h), syh(s), 3.6 if end else 3, f'dot s{idx}', 'stroke-width="1.5"')
                if end:
                    continue
                svg.text(sxh(h) + (8 if idx == 3 else -7), syh(s) + (14 if idx == 3 else -6), T(f'Step {st}', f'第 {st} 步'), cls='t-muted',
                         anchor='start' if idx == 3 else 'end', size=FS_TICK)
    e4, e1 = four[-1], one[-1]
    l4 = T(f'Step 100 · {e4[1]:.1f}%', f'第 100 步 · {e4[1]:.1f}%')
    l1 = T(f'Step 150 · {e1[1]:.1f}%', f'第 150 步 · {e1[1]:.1f}%')
    if narrow:      # little room right of the points on a phone: the end labels sit above-left of them
        svg.text(sxh(e4[2]) - 4, syh(e4[1]) - 9, l4, cls='t-strong', anchor='end', size=FS_TICK)
        svg.text(sxh(e1[2]) - 2, syh(e1[1]) - 9, l1, anchor='end', size=FS_TICK)
    else:
        svg.text(sxh(e4[2]) + 8, syh(e4[1]) + 4, l4, cls='t-strong', size=FS_TICK)
        svg.text(sxh(e1[2]) + 8, syh(e1[1]) + 4, l1, size=FS_TICK)
    drop = 22 if narrow else 8
    span(svg, sxh(e4[2]), sxh(e1[2]), syh(92), None if readings else T(f'About {e1[2] - e4[2]:.0f} h sooner', f'约早 {e1[2] - e4[2]:.0f} 小时'),
         drops=[(sxh(e4[2]), syh(e4[1]) - drop), (sxh(e1[2]), syh(e1[1]) - drop)], cls='', size=FS_TICK)
    return svg


# ============================================================================ scr-hotpotqa
def hotpot(W, story=False):
    """Round-2 merge. Polish: the three readings start with a capital (as in the other charts' readings), the (c) bars
    one step slimmer with their value labels at 12 px like the line panels' end values. story=True (innovative,
    second try): the order of the page's 'Outcome' paragraph — (a) repeated queries, (b) all-failed groups, (c) exact
    match — with the bar panel in the middle; the titles now fit their panels."""
    em, sh = c1._hpq()
    narrow = W < 500
    H = 312 if not narrow else 820
    top = 84
    svg = Svg(W, H, 'HotpotQA under the EM and shaped rewards: ' + ('repeated queries over training, the share of all-failed groups, and exact match over training'
                                                                    if story else 'exact match and repeated queries over training, and the share of all-failed groups'))
    key_lines(svg, 48, 18, [(1, T('EM reward', 'EM 奖励')), (2, T('Shaped reward', '稠密奖励'))])
    pw = (W - 60) / 3
    p_ = float(PAIRED['hotpotqa_em_vs_shaped:all']['p'])
    lines = {'em': (T('Exact match', 'EM'), '%', (40, 60), [40, 50, 60], lambda v: f'{v:.0f}', T(f'No significant change (p = {p_:.2f})', f'无显著差异（p = {p_:.2f}）')),
             'repeat_queries': (T('Repeated queries', '重复查询'), T('per question', '每题'), (0, 0.2), [0, 0.1, 0.2], lambda v: f'{v:.1f}' if v else '0', T('−71% at step 200', '第 200 步减少 71%'))}
    order = ['repeat_queries', 'bars', 'em'] if story else ['em', 'repeat_queries', 'bars']
    for k, key in enumerate(order):
        if narrow:
            box = (56, 74 + k * 250, W - 70, 74 + k * 250 + 160)
        else:
            box = (52 + k * pw, top, 52 + k * pw + pw - (60 if key == 'bars' else 82), H - 60)
        letter = 'abc'[k]
        if key == 'bars':
            panel_title(svg, box[0], box[1] - 30, letter, T('All-failed groups', '全错组'), T('% of groups', '占比 %'))
            svg.text(box[0], box[1] - 13, T('More groups give a learning signal', '更多组有学习信号'), size=FS_TICK)
            sy = scale(0, 30, box[3], box[1])
            frame(svg, box, lambda v: v, sy, [], [0, 10, 20, 30], str, str)
            cw = (box[2] - box[0]) / 2
            for j, (idx, v, lab) in enumerate(((1, 27, T('EM reward', 'EM 奖励')), (2, 4, T('Shaped reward', '稠密奖励')))):
                cx = box[0] + cw * (j + 0.5)
                hw = 8
                svg.mark(f'{lab[0]}: about {v}% of the groups had no successful answer',
                         f'<path class="bar s{idx}" d="M{cx - hw:.1f},{sy(0):.1f} V{sy(v) + 3:.1f} A3,3 0 0 1 {cx - hw + 3:.1f},{sy(v):.1f} H{cx + hw - 3:.1f} A3,3 0 0 1 {cx + hw:.1f},{sy(v) + 3:.1f} V{sy(0):.1f} Z"/>')
                svg.text(cx, sy(v) - 7, f'≈ {v}%', cls='t-strong', anchor='middle', size=FS_LABEL)
                svg.text(cx, box[3] + 16, lab, cls='t-muted', anchor='middle', size=FS_TICK)
            continue
        title, unit, (lo, hi), ticks, fmt, verdict = lines[key]
        sx, sy = scale(0, 200, box[0], box[2]), scale(lo, hi, box[3], box[1])
        panel_title(svg, box[0], box[1] - 30, letter, title, unit)
        svg.text(box[0], box[1] - 13, verdict, size=FS_TICK)
        frame(svg, box, sx, sy, [0, 100, 200], ticks, str, fmt, xtitle=T('Training step', '训练步'))
        for idx, d in ((2, sh), (1, em)):
            path_line(svg, d[key], sx, sy, idx)
            dots(svg, d[key], sx, sy, idx, r=2.2, ring=False)
            hits(svg, d[key], sx, sy, lambda x, y: f'Step {x}: {y}')
        a_, b_ = em[key][-1][1], sh[key][-1][1]
        f = (lambda v: f'{v:.1f}') if key == 'em' else (lambda v: f'{v:.3f}')
        label_stack(svg, box[2] + 7, [(sy(a_), f(a_), 't-strong' if key == 'em' else ''), (sy(b_), f(b_), 't-strong' if key != 'em' else '')], min_gap=13)
        if key != 'em':
            xl = sx(200) - 7
            svg.line(xl, sy(a_) + 5, xl, sy(b_) - 5, 'leader')
    return svg


# ============================================================================ the round
STOPPED = ('opd-compute',)
AES = {'opd-methods': lambda W: d2.methods(W, baseline=True, phone_grid=False), 'opd-budget': budget, 'opd-training': training, 'scr-sft-rl': sft_rl, 'scr-vs-grpo': vs, 'scr-updates': updates, 'scr-hotpotqa': hotpot}
INNO = {'opd-budget': lambda W: budget(W, lean=True), 'scr-vs-grpo': lambda W: vs(W, floor=True),
        'scr-updates': lambda W: updates(W, readings=True), 'scr-hotpotqa': lambda W: hotpot(W, story=True)}
MERGED = {'opd-methods': AES['opd-methods'],
          'opd-budget': lambda W: budget(W, lean=True),
          'opd-training': training,
          'opd-compute': lambda W: d2.compute(W, caps=True),
          'scr-sft-rl': sft_rl,
          'scr-vs-grpo': lambda W: vs(W, floor=True),
          'scr-updates': updates,
          'scr-hotpotqa': lambda W: hotpot(W, story=True)}
NOTES = {
    'opd-methods': 'Round 3 is a phone fix only: the names sit above the stems there, so the vertical grid ran through them; the '
                   'phone version keeps the axis and drops the grid (values are printed). Otherwise the round-2 merge.',
    'opd-budget': 'Final: innovative. (a) without the wash, since (b) draws the same gap with its error band; the height goes '
                  'to (b), the panel the section title ("the advantage grows with the budget") is about. Plus the shorter '
                  'reading from the aesthetic version, which fits a phone.',
    'opd-training': 'Final: aesthetic. (a) runs to 7k so the six OPD steps above 6k (up to 6,775) are drawn where they are, not '
                    'pinned to the top edge. No new idea: the three panels already draw the caption\'s three claims.',
    'opd-compute': 'Stopped after round 2: final = round-2 merge (the 11-15 drawing with the span mark, stage names in ink and '
                   'scores in semibold, the per-GPU-hour inset on a background box), with the capitals pass (caps=True).',
    'scr-sft-rl': 'Final: aesthetic dumbbells (connector a thin solid light-blue line, hollow SFT dot on a background disc, key row '
                  'a size larger).',
    'scr-vs-grpo': 'Final: innovative. The late-stage means sit at the gray band\'s floor, keyed with short blue and orange lines '
                   'under "Last 5", where neither curve ever goes; the strip keeps its full sentence. The one-line aesthetic '
                   'reading had to cut "validations".',
    'scr-updates': 'Final: aesthetic (hours ticked every 10 h, step markers smaller than the end points, span label in ink). '
                   'Readings under the titles repeated what the span and the bracket already say.',
    'scr-hotpotqa': 'Final: innovative. The order of the page\'s Outcome paragraph: (a) repeated queries −71%, (b) all-failed '
                    'groups ≈27% → ≈4%, (c) exact match, no significant change. The bar panel sits between the two line panels, '
                    'and the chart ends on the result that did not move. Caption needs reordering.',
}
