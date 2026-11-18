"""Home page thumbnail for StepCredit-RL: rollouts that reach the same state; the steps taken from it get opposite credit.

Variants: r1a / r1i / r1m, r2a / r2i / r2m, r3a / r3i / r3m; rounds 4-6 (r4a ... r6m) English only; final: r6m.
"""
from dlib import Fig, INK, LAV, LEAF, MUTED, ROSE, SKY, SLATE, WHITE, label_w, msub

WIDTH = 300
LABEL = 'StepCredit-RL in miniature: three rollouts reach the same state; the steps taken from it get opposite credit'
LABEL_ZH = 'StepCredit-RL 缩略图：三条 rollout 到达同一状态，从该状态出发的各步得到相反的信用'


def T(lang, en, zh):
    return zh if lang == 'zh' else en


ROWS = [(['0', '1', '2', '3'], True), (['0', '5', '1', '2'], False), (['0', '1', '2', '7'], False)]


def state(f, cx, cy, k, shared=False, w=30, h=22, size=14):
    pal = LAV if shared else SLATE
    f.box(cx - w / 2, cy - h / 2, w, h, fill=pal['fill'] if shared else WHITE, stroke=pal['line'], width=1.1, arc=6,
          label=msub('s', k, size), size=13, family='Times New Roman')


def outcome_pill(f, cx, cy, ok, w=34, h=22):
    pal = LEAF if ok else ROSE
    f.box(cx - w / 2, cy - h / 2, w, h, fill=pal['soft'], stroke=pal['line'], width=1.1, arc=11)
    (f.check if ok else f.cross)(cx, cy, s=9 if ok else 8)


def credit(f, cx, cy, sign):
    pal = LEAF if sign > 0 else ROSE
    f.box(cx - 9, cy - 9, 18, 18, fill=pal['line'], stroke='none', width=0, arc=9, label='+' if sign > 0 else '−',
          size=14, color=WHITE, bold=True)


def rows(lang):
    f = Fig(300, 190, LABEL)
    pitch, x0 = 54, 60
    for r, (states, ok) in enumerate(ROWS):
        y = 30 + r * 46
        f.text(14, y, msub('τ', r + 1, 16), size=14)
        shared_c = None
        for c, k in enumerate(states):
            cx = x0 + c * pitch
            state(f, cx, y, k, shared=(k == '2'))
            if c:
                f.edge([(cx - pitch + 16, y), (cx - 16, y)], width=1.1, end=4)
            if k == '2':
                shared_c = cx
        outcome_pill(f, 272, y, ok)
        if shared_c is not None and states.index('2') < len(states) - 1:
            credit(f, shared_c + pitch / 2, y - 16, 1 if ok else -1)
    f.text(150, 172, T(lang, 'Same state, then compare the next steps', '同一状态，比较之后的各步'), size=13, color=MUTED, anchor='c')
    return f


def fan(lang):
    """One shared state, three different next steps, each credited by what followed."""
    f = Fig(300, 190, LABEL)
    cy = 80
    state(f, 40, cy, '2', shared=True, w=40, h=28, size=16)
    acts = [('fridge', True), ('cabinet', False), ('sinkbasin', False)]
    for k, (act, ok) in enumerate(acts):
        y = 34 + k * 46
        f.edge([(61, cy), (88, y)], width=1.2, end=5)
        lab = T(lang, f'go to {act}', f'go to {act}')
        e = f.chip(90, y, lab, SLATE, size=12.5, h=22, pad=6)
        f.edge([(e + 3, y), (206, y)], width=1.1, end=4, dashed=True, dash='2 2')
        outcome_pill(f, 226, y, ok)
        credit(f, 266, y, 1 if ok else -1)
    f.text(150, 172, T(lang, 'Steps from the same state, credited by what followed', '从同一状态出发的各步，按之后的结果给信用'), size=12.5, color=MUTED, anchor='c')
    return f


ALIGNED = [(['0', '1', '2', '3'], True), (['0', '5', '2', '7'], False), (['0', '8', '2', '9'], False)]   # only s0 and s2 shared; s3 / s7 / s9 as in the method figure


def aligned(lang, opts=()):
    """Round-1 merge: the three rollouts with the shared state s2 in one column on a lavender band; each step leaving
    s2 carries its credit; outcomes on the right."""
    f = Fig(300, 190, LABEL)
    pitch, x0 = 56, 58
    col = x0 + 2 * pitch
    f.box(col - 22, 10, 44, 140, fill=LAV['soft'], stroke=LAV['tok'], width=1, arc=10)
    for r, (states, ok) in enumerate(ALIGNED):
        y = 32 + r * 48
        f.text(14, y, msub('τ', r + 1, 16), size=14)
        for c, k in enumerate(states):
            cx = x0 + c * pitch
            state(f, cx, y, k, shared=(k == '2'))
            if c:
                pal = (LEAF if ok else ROSE) if c == 3 else None
                f.edge([(cx - pitch + 16, y), (cx - 16, y)], width=1.6 if pal else 1.1, end=4,
                       color=pal['line'] if pal else '#3A3A3A')
        credit(f, col + pitch / 2, y - 15, 1 if ok else -1)
        outcome_pill(f, 274, y, ok)
    f.text(150, 172, T(lang, 'Same state, then compare the next steps', '同一状态，比较之后的各步'), size=13, color=MUTED, anchor='c')
    return f


def aligned2(lang, legend=False):
    """Round 2: wider band, credit badges centred on the steps that leave s2; with legend, a key replaces the caption."""
    f = Fig(300, 190, LABEL)
    pitch, x0 = 56, 56
    col = x0 + 2 * pitch
    f.box(col - 23, 8, 46, 146, fill=LAV['soft'], stroke=LAV['tok'], width=1, arc=10)
    for r, (states, ok) in enumerate(ALIGNED):
        y = 34 + r * 48
        f.text(12, y, msub('τ', r + 1, 16), size=14)
        for c, k in enumerate(states):
            cx = x0 + c * pitch
            state(f, cx, y, k, shared=(k == '2'))
            if c:
                pal = (LEAF if ok else ROSE) if c == 3 else None
                f.edge([(cx - pitch + 16, y), (cx - 16, y)], width=1.8 if pal else 1.1, end=4,
                       color=pal['line'] if pal else '#3A3A3A')
        credit(f, col + pitch / 2, y - 15, 1 if ok else -1)
        outcome_pill(f, 274, y, ok)
    if legend:
        f.text(150, 174, T(lang, '+ / −: credit for the step after the shared state', '+ / −：离开共享状态那一步的信用'), size=12.5, color=MUTED, anchor='c')
    else:
        f.text(150, 174, T(lang, 'Same state, then compare the next steps', '同一状态，比较之后的各步'), size=13, color=MUTED, anchor='c')
    return f


def aligned3(lang, rvals=False):
    """Round 3: r2a polished; with rvals, the outcome pills read R = 1 / R = 0 as in the method figure."""
    f = Fig(300, 190, LABEL)
    pitch, x0 = 52, 52
    col = x0 + 2 * pitch
    f.box(col - 23, 8, 46, 146, fill=LAV['soft'], stroke=LAV['tok'], width=1, arc=10)
    for r, (states, ok) in enumerate(ALIGNED):
        y = 34 + r * 48
        f.text(10, y, msub('τ', r + 1, 16), size=14)
        for c, k in enumerate(states):
            cx = x0 + c * pitch
            state(f, cx, y, k, shared=(k == '2'))
            if c:
                pal = (LEAF if ok else ROSE) if c == 3 else None
                f.edge([(cx - pitch + 16, y), (cx - 16, y)], width=1.8 if pal else 1.1, end=4,
                       color=pal['line'] if pal else '#3A3A3A')
        credit(f, col + pitch / 2, y - 15, 1 if ok else -1)
        if rvals:
            pal = LEAF if ok else ROSE
            f.box(236, y - 11, 56, 22, fill=pal['soft'], stroke=pal['line'], width=1.1, arc=11,
                  label=f'<span style="font-family:Times New Roman;"><i>R</i></span> = {1 if ok else 0}', size=13)
        else:
            outcome_pill(f, 270, y, ok)
    f.text(150, 174, T(lang, 'Same state, then compare the next steps', '同一状态，比较之后的各步'), size=13, color=MUTED, anchor='c')
    return f


def build(v, lang):
    if v[:2] in ('r4', 'r5', 'r6'):
        return {'r4a': aligned4, 'r4i': bowtie4, 'r4m': lambda: bowtie4(times_signs=True),
                'r5a': bowtie5, 'r5i': lambda: bowtie5(labels=True, rpills=True), 'r5m': bowtie5,
                'r6a': bowtie6, 'r6i': lambda: bowtie6(big=True), 'r6m': lambda: bowtie6(big=True)}[v]()
    if v in ('r3a', 'r3i', 'r3m'):
        return aligned3(lang, rvals=(v == 'r3i'))
    if v == 'r1i':
        return fan(lang)
    if v == 'r1a':
        return rows(lang)
    if v == 'r1m':
        return aligned(lang)
    return aligned2(lang, legend=(v == 'r2i'))


# ------------------------------------------------------------------ rounds 4-6 (English only)
def aligned4(badge_r=10):
    """Round-4 aesthetic: r3m with larger states and credit badges, the band and the rows spread over the card."""
    f = Fig(300, 190, LABEL)
    pitch, x0 = 54, 50
    col = x0 + 2 * pitch
    f.box(col - 24, 8, 48, 146, fill=LAV['soft'], stroke=LAV['tok'], width=1, arc=10)
    for r, (states, ok) in enumerate(ALIGNED):
        y = 34 + r * 48
        f.text(8, y, msub('τ', r + 1, 17), size=14)
        for c, k in enumerate(states):
            cx = x0 + c * pitch
            state(f, cx, y, k, shared=(k == '2'), w=32, h=24, size=15)
            if c:
                pal = (LEAF if ok else ROSE) if c == 3 else None
                f.edge([(cx - pitch + 17, y), (cx - 17, y)], width=1.8 if pal else 1.1, end=4,
                       color=pal['line'] if pal else '#3A3A3A')
        cb = col + pitch / 2
        pal = LEAF if ok else ROSE
        f.box(cb - badge_r, y - 16 - badge_r, 2 * badge_r, 2 * badge_r, fill=pal['line'], stroke='none', width=0, arc=badge_r,
              label='+' if ok else '−', size=15, color=WHITE, bold=True)
        outcome_pill(f, 272, y, ok, w=36, h=24)
    f.text(150, 174, 'Same state, then compare the next steps', size=13, color=MUTED, anchor='c')
    return f


PM = {True: '<span style="font-family:Times New Roman;">+</span>', False: '<span style="font-family:Times New Roman;">−</span>'}


def bowtie4(times_signs=False):
    """Round-4 innovative: the shared state drawn once. Three prefixes from s0 converge on s2; three steps leave it,
    each credited by what followed (+ / -), with the rollout's outcome at the end."""
    f = Fig(300, 190, LABEL)
    ys = [36, 84, 132]
    w, h = 30, 22
    x_s0, x_mid, x_s2, x_nx, x_out = 22, 82, 148, 222, 274
    state(f, x_s0, 84, '0', w=w, h=h)
    state(f, x_s2, 84, '2', shared=True, w=34, h=26, size=15)
    mids, nxts = ['1', '5', '8'], ['3', '7', '9']
    for r, y in enumerate(ys):
        ok = r == 0
        state(f, x_mid, y, mids[r], w=w, h=h)
        f.edge([(x_s0 + w / 2 + 1, 84 + (y - 84) * 0.25), (x_mid - w / 2 - 1, y)], width=1.1, end=4)
        f.edge([(x_mid + w / 2 + 1, y), (x_s2 - 17 - 1, 84 + (y - 84) * 0.3)], width=1.1, end=4)
        pal = LEAF if ok else ROSE
        f.edge([(x_s2 + 17 + 1, 84 + (y - 84) * 0.3), (x_nx - w / 2 - 1, y)], color=pal['line'], width=1.8, end=4)
        state(f, x_nx, y, nxts[r], w=w, h=h)
        mx, my = (x_s2 + 17 + x_nx - w / 2) / 2, (84 + (y - 84) * 0.3 + y) / 2
        f.box(mx - 9, my - 9 - 2, 18, 18, fill=pal['line'], stroke='none', width=0, arc=9,
              label=PM[ok] if times_signs else ('+' if ok else '−'), size=16 if times_signs else 14, color=WHITE, bold=True)
        outcome_pill(f, x_out, y, ok, w=34, h=22)
    f.text(150, 174, 'Same state, then compare the next steps', size=13, color=MUTED, anchor='c')
    return f


# ------------------------------------------------------------------ round 5
def bowtie5(labels=False, rpills=False):
    """Round 5: r4m's bowtie, the three prefixes meeting s2 at one point each side (a clean fan in and out); labels:
    the rollouts named next to their own states; rpills: outcomes read R = 1 / R = 0, as in the method figure."""
    f = Fig(300, 190, LABEL)
    ys = [38, 86, 134]
    yc = 86
    w, h = 30, 22
    x_s0, x_mid, x_s2, x_nx = 26, 88, 152, 224
    x_out = 274 if not rpills else 262
    state(f, x_s0, yc, '0', w=w, h=h)
    state(f, x_s2, yc, '2', shared=True, w=34, h=26, size=15)
    mids, nxts = ['1', '5', '8'], ['3', '7', '9']
    for r, y in enumerate(ys):
        ok = r == 0
        state(f, x_mid, y, mids[r], w=w, h=h)
        f.edge([(x_s0 + w / 2 + 1, yc + (y - yc) * 0.22), (x_mid - w / 2 - 1, y)], width=1.1, end=4)
        f.edge([(x_mid + w / 2 + 1, y), (x_s2 - 17 - 1, yc + (y - yc) * 0.22)], width=1.1, end=4)
        pal = LEAF if ok else ROSE
        f.edge([(x_s2 + 17 + 1, yc + (y - yc) * 0.22), (x_nx - w / 2 - 1, y)], color=pal['line'], width=1.8, end=4)
        state(f, x_nx, y, nxts[r], w=w, h=h)
        mx, my = (x_s2 + 17 + x_nx - w / 2) / 2, (yc + (y - yc) * 0.22 + y) / 2
        f.box(mx - 9, my - 9 - 2, 18, 18, fill=pal['line'], stroke='none', width=0, arc=9, label=PM[ok], size=16, color=WHITE, bold=True)
        if labels:
            f.text(x_mid, y - 19, msub('τ', r + 1, 13), size=12, color=MUTED, anchor='c')
        if rpills:
            f.box(x_out - 26, y - 11, 52, 22, fill=pal['soft'], stroke=pal['line'], width=1.1, arc=11,
                  label=f'<span style="font-family:Times New Roman;"><i>R</i></span> = {1 if ok else 0}', size=13)
        else:
            outcome_pill(f, x_out, y, ok, w=34, h=22)
    f.text(150, 174, 'Same state, then compare the next steps', size=13, color=MUTED, anchor='c')
    return f


# ------------------------------------------------------------------ round 6
def bowtie6(big=False):
    """Round 6: bowtie5 with the fan-in arrows meeting s2 on its border (not short of it) and, with big, every part a
    size larger for the 286 px card."""
    f = Fig(300, 190, LABEL)
    k = 1.08 if big else 1.0
    ys = [38, 86, 134] if not big else [34, 86, 138]
    yc = 86
    w, h = 30 * k, 22 * k
    sw, sh = 34 * k, 26 * k
    x_s0, x_mid, x_s2, x_nx, x_out = (26, 88, 152, 224, 274) if not big else (24, 86, 152, 226, 276)
    fs = 15 if big else 14
    state(f, x_s0, yc, '0', w=w, h=h, size=fs)
    state(f, x_s2, yc, '2', shared=True, w=sw, h=sh, size=fs + 1)
    mids, nxts = ['1', '5', '8'], ['3', '7', '9']
    for r, y in enumerate(ys):
        ok = r == 0
        state(f, x_mid, y, mids[r], w=w, h=h, size=fs)
        f.edge([(x_s0 + w / 2 + 1, yc + (y - yc) * 0.2), (x_mid - w / 2 - 1, y)], width=1.1, end=4)
        f.edge([(x_mid + w / 2 + 1, y), (x_s2 - sw / 2 - 0.5, yc + (y - yc) * 0.2)], width=1.1, end=4)
        pal = LEAF if ok else ROSE
        f.edge([(x_s2 + sw / 2 + 0.5, yc + (y - yc) * 0.2), (x_nx - w / 2 - 1, y)], color=pal['line'], width=1.8, end=4)
        state(f, x_nx, y, nxts[r], w=w, h=h, size=fs)
        mx, my = (x_s2 + sw / 2 + x_nx - w / 2) / 2, (yc + (y - yc) * 0.2 + y) / 2
        r_ = 9.5 if big else 9
        f.box(mx - r_, my - r_ - 2, 2 * r_, 2 * r_, fill=pal['line'], stroke='none', width=0, arc=r_, label=PM[ok],
              size=17 if big else 16, color=WHITE, bold=True)
        outcome_pill(f, x_out, y, ok, w=36 if big else 34, h=24 if big else 22)
    f.text(150, 176, 'Same state, then compare the next steps', size=13.5 if big else 13, color=MUTED, anchor='c')
    return f
