"""Round 1 (2026-11-16), diagrams: two versions of each, starting from the v2 finals in lab/v2.

  aes   the v2 drawing restyled in the paper-like language (tinted panels, semantic tones, icons, numbered steps)
  inno  rebuilt from scratch; the framework figures become full method diagrams
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE / 'v2'))

from figlib import OPD, Svg, T, arrow, chevron, hbar, vbar, width_of  # noqa: E402
from figkit import SOLID, badge, chip, chip_w, curve, icon, math as mtext, panel, tokens, wedge_bracket  # noqa: E402
import figures_v2 as V2  # noqa: E402

pick, per_lang = V2.pick, V2.per_lang


def legend_tokens(svg, x, y, items, size=11.5, gap=18):
    """items: [(tone or 'end', label)]; tone squares like the tokens in the figure."""
    def draw(i):
        xx = x
        for tone, lab in items:
            if tone == 'end':
                svg.rect(xx, y - 10, 11, 11, 'ink', rx=1.5)
            else:
                svg.rect(xx, y - 10, 11, 11, f'pn-{tone}', rx=2.5)
            s = pick(lab, i)
            svg.text(xx + 16, y, s, cls='t-muted', size=size)
            xx += 16 + svg.tw(s, size) + gap
    per_lang(svg, draw)


# ============================================================================ Scaffold-OPD framework
def opd_framework_aes(W):
    """v2 lanes, restyled: student blue, teacher green, takeover points purple, inset as a tinted panel."""
    narrow = W < 500
    lx, ys, yt = (58, 44, 98) if narrow else (74, 46, 104)
    x_end = W - (28 if narrow else 40)
    span = x_end - lx
    segs = [('s', 0.00, 0.25), ('t', 0.28, 0.45), ('s', 0.48, 0.73), ('t', 0.76, 0.90)]
    by = yt + (46 if narrow else 44)
    H = by + (140 if narrow else 70)
    svg = Svg(W, H, 'Illustration: the teacher takes over at a reflection point, writes a short passage and hands back')
    svg.text(12, ys + 4, T('student', '学生'), cls='tx-blue', size=12, weight=700)
    svg.text(12, yt + 4, T('teacher', '老师'), cls='tx-green', size=12, weight=700)
    svg.line(lx, ys, x_end, ys, 'grid', 'stroke-dasharray="3 4"')
    svg.line(lx, yt, x_end, yt, 'grid', 'stroke-dasharray="3 4"')
    for k, (who, a, b) in enumerate(segs):
        y = ys if who == 's' else yt
        n = max(2, int((b - a) * span / 14))
        cw = (b - a) * span / n
        for i in range(n):
            tone = 'blue' if who == 's' else ('purple' if i == 0 else 'green')
            svg.rect(lx + a * span + i * cw, y - 6, cw - 3, 12, f'pn-{tone}', rx=2.5)
    for f0, f1, down in [(0.25, 0.28, True), (0.45, 0.48, False), (0.73, 0.76, True)]:
        x1, x2 = lx + f0 * span - 2, lx + f1 * span
        if down:
            curve(svg, x1, ys + 7, x2, yt - 8, 'line l4')
        else:
            curve(svg, x1, yt - 7, x2, ys + 8, 'line l3', 'stroke-dasharray="3 3"')
    t1, t2, t2e = lx + 0.28 * span, lx + 0.76 * span, lx + 0.90 * span
    svg.text(t1, yt + 25, '“Wait, …”', cls='tx-green', size=12, weight=600)
    svg.text(t2, yt + 25, '“But …”', cls='tx-green', size=12, weight=600)
    svg.rect(t2e + 4, yt - 5.5, 11, 11, 'ink', rx=1.5)

    top5 = ['So', 'Then', 'We', 'The', 'Let']
    if not narrow:
        bw = 450
        svg.rect(16, by, bw, 56, 'pn-purple', rx=10)
        svg.line(t1 + 1, yt + 31, t1 + 1, by, 'leader')

        def inset(i):
            svg.text(30, by + 21, pick(T('teacher’s next token', '老师的下一个 token'), i), cls='t-muted', size=11)
            chip(svg, 30, by + 28, 'Wait', 'green', solid=True)
            svg.text(160, by + 21, pick(T('student’s top-5', '学生的 top-5'), i), cls='t-muted', size=11)
            x = 160
            for wd in top5:
                x = chip(svg, x, by + 28, wd, 'blue') + 4
            svg.text(x + 10, by + 21, pick(T('not in top-5', '不在 top-5'), i), cls='t-muted', size=11)
            svg.text(x + 10, by + 43, pick(T('→ take over', '→ 接管'), i), cls='tx-purple', size=12.5, weight=700)
        per_lang(svg, inset)
        svg.text(16 + bw + 18, by + 22, T('≤ 3 paragraphs per takeover', '每次接管最多写 3 段'), cls='t-muted', size=11.5)
        svg.text(16 + bw + 18, by + 42, T('≤ 2 takeovers per answer', '每条回答最多接管 2 次'), cls='t-muted', size=11.5)
        return svg
    svg.rect(8, by, W - 16, 88, 'pn-purple', rx=10)

    def inset_narrow(i):
        svg.text(20, by + 22, pick(T('teacher’s next token', '老师的下一个 token'), i), cls='t-muted', size=11)
        chip(svg, 148, by + 8, 'Wait', 'green', solid=True)
        svg.text(20, by + 49, pick(T('student’s top-5', '学生的 top-5'), i), cls='t-muted', size=11)
        x = 110 if i == 0 else 100
        for wd in top5:
            x = chip(svg, x, by + 36, wd, 'blue', size=11, pad=5) + 3
        svg.text(20, by + 76, pick(T('not in top-5 → take over', '不在 top-5 → 接管'), i), cls='tx-purple', size=12, weight=700)
    per_lang(svg, inset_narrow)
    svg.text(8, by + 110, T('≤ 3 paragraphs per takeover', '每次接管最多写 3 段'), cls='t-muted', size=11.5)
    svg.text(8, by + 128, T('≤ 2 takeovers per answer', '每条回答最多接管 2 次'), cls='t-muted', size=11.5)
    return svg


def _model_box(svg, x, y, w, h, tone, kind, title, sub):
    svg.rect(x, y, w, h, f'pn-{tone}', rx=9)
    icon(svg, kind, x + 20, y + h / 2, 20, tone)
    svg.text(x + 38, y + h / 2 - 3, title, cls=f'tx-{tone}', size=13, weight=700)
    svg.text(x + 38, y + h / 2 + 13, sub, cls='t-muted', size=11)


def opd_framework_inno(W, hand=True):
    """Full method diagram: (1) relay rollout in speculative decoding, (2) the two triggers, (3) the training signal."""
    if W < 500:
        return _opd_framework_narrow(W, hand)
    H = 486
    svg = Svg(W, H, 'Scaffold-OPD: relay rollout inside speculative decoding, the takeover triggers, and the token-level training signal', hand=hand)
    legend_tokens(svg, 16, 18, [('blue', T('student token', '学生 token')), ('green', T('teacher token', '老师 token')),
                                ('purple', T('takeover point', '接管点')), ('end', T('answer ends', '回答结束'))])
    # ---- panel 1: relay rollout
    panel(svg, 10, 30, W - 20, 206, 'gray', T('Relay rollout inside vLLM speculative decoding', 'vLLM 投机解码中的接力生成'), 1)
    _model_box(svg, 26, 62, 176, 52, 'blue', 'robot', T('Student', '学生'), T('Qwen3-1.7B · drafts', 'Qwen3-1.7B · 写草稿'))
    _model_box(svg, 26, 150, 176, 52, 'green', 'cap', T('Teacher', '老师'), T('Qwen3-4B · verifies', 'Qwen3-4B · 验证'))
    arrow(svg, 98, 116, 98, 147)
    arrow(svg, 130, 147, 130, 117)
    svg.text(91, 136, T('draft', '草稿'), cls='t-faint', anchor='end', size=10.5)
    svg.text(137, 136, T('accept / take over', '接受 / 接管'), cls='t-faint', size=10.5)
    ys, yt, x0 = 88, 176, 232
    svg.line(x0 - 8, ys, W - 26, ys, 'grid', 'stroke-dasharray="2 4"')
    svg.line(x0 - 8, yt, W - 26, yt, 'grid', 'stroke-dasharray="2 4"')
    pitch = 14
    s1 = tokens(svg, x0, ys - 5.5, 12, 'blue')
    t1s = s1 + 18
    svg.rect(t1s, yt - 5.5, 11, 11, 'pn-purple', rx=2.5)
    t1e = tokens(svg, t1s + pitch, yt - 5.5, 8, 'green')
    s2s = t1e + 18
    s2e = tokens(svg, s2s, ys - 5.5, 10, 'blue')
    t2s = s2e + 18
    svg.rect(t2s, yt - 5.5, 11, 11, 'pn-purple', rx=2.5)
    t2e = tokens(svg, t2s + pitch, yt - 5.5, 5, 'green')
    svg.rect(t2e + 8, yt - 5.5, 11, 11, 'ink', rx=1.5)
    curve(svg, s1 + 2, ys + 7, t1s + 5, yt - 8, 'line l4')
    curve(svg, t1e + 2, yt - 7, s2s + 5, ys + 8, 'line l3', 'stroke-dasharray="3 3"')
    curve(svg, s2e + 2, ys + 7, t2s + 5, yt - 8, 'line l4')
    badge(svg, (s1 + t1s) / 2 + 3, (ys + yt) / 2, 1, 'purple', 7.5)
    badge(svg, (s2e + t2s) / 2 + 3, (ys + yt) / 2, 2, 'purple', 7.5)
    svg.text(x0, ys - 13, T('“… so the answer is 47.”', '“……所以答案是 47。”'), cls='t-muted', size=11.5)
    svg.text(s2s, ys - 13, T('“… so the answer is 52.”', '“……所以答案是 52。”'), cls='t-muted', size=11.5)
    svg.text(t1s, yt - 14, T('“Wait, let me check step 2 …”', '“Wait, let me check step 2 …”'), cls='tx-green', size=11.5, weight=600)
    svg.text(t2s, yt - 14, T('“But the question asks …”', '“But the question asks …”'), cls='tx-green', size=11.5, weight=600)
    wedge_bracket(svg, t1s, t1e, yt + 13, 'leader', 5, down=True)
    svg.text((t1s + t1e) / 2, yt + 30, T('≤ 3 paragraphs (≤ 256 tokens), then hand back', '最多写 3 段（≤ 256 token）后交还'), cls='t-muted', anchor='middle', size=11)
    svg.text(W - 30, yt + 30, T('≤ 2 takeovers per answer', '每条回答最多接管 2 次'), cls='t-muted', anchor='end', size=11)
    # ---- panel 2: triggers
    bx, by, bw, bh = 10, 248, 528, 228
    panel(svg, bx, by, bw, bh, 'purple', T('When does the teacher take over?', '老师何时接管？'), 2)

    def triggers(i):
        y = by + 52
        svg.text(bx + 18, y, pick(T('Reflection trigger', '反思触发'), i), cls='t-strong', size=12.5)
        y += 16
        svg.text(bx + 18, y + 2, pick(T('teacher’s top-1', '老师 top-1'), i), cls='t-faint', size=10.5)
        x = chip(svg, bx + 18, y + 7, 'Wait', 'green', solid=True)
        mtext(svg, x + 6, y + 22, '∈ R', 13)
        x += 34
        svg.text(x + 8, y + 22, pick(T('and', '且'), i), cls='t-muted', size=11.5)
        x += 8 + svg.tw(pick(T('and', '且'), i), 11.5) + 10
        svg.text(x, y + 2, pick(T('student’s top-5', '学生 top-5'), i), cls='t-faint', size=10.5)
        for wd in ['So', 'Then', 'We', 'The', 'Let']:
            x = chip(svg, x, y + 7, wd, 'blue', size=11, pad=6) + 3
        mtext(svg, x + 4, y + 22, '∩ R = ∅', 13)
        svg.text(bx + bw - 16, y + 22, pick(T('→ take over', '→ 接管'), i), cls='tx-purple', anchor='end', size=12.5, weight=700)
        svg.text(bx + 18, y + 46, pick(T('R: the 45 reflection words (Wait, But, …)', 'R：45 个反思词（Wait、But 等）'), i), cls='t-faint', size=11)
        y += 86
        svg.text(bx + 18, y, pick(T('Concluding trigger', '收尾触发'), i), cls='t-strong', size=12.5)
        svg.text(bx + 18 + svg.tw(pick(T('Concluding trigger', '收尾触发'), i), 12.5, 600) + 8, y,
                 pick(T('implemented in the verify step', '在验证步中实现'), i), cls='t-faint', size=11)
        y += 16
        svg.text(bx + 18, y + 2, pick(T('teacher wants to conclude', '老师想开始收尾'), i), cls='t-faint', size=10.5)
        x = chip(svg, bx + 18, y + 7, '### ✅ Final Answer', 'green', solid=True)
        svg.text(x + 10, y + 22, pick(T('while', '而'), i), cls='t-muted', size=11.5)
        x += 10 + svg.tw(pick(T('while', '而'), i), 11.5) + 10
        svg.text(x, y + 2, pick(T('student', '学生'), i), cls='t-faint', size=10.5)
        x = chip(svg, x, y + 7, pick(T('keeps reasoning …', '还在往下写……'), i), 'blue', size=11)
        svg.text(bx + bw - 16, y + 22, pick(T('→ take over', '→ 接管'), i), cls='tx-purple', anchor='end', size=12.5, weight=700)
    per_lang(svg, triggers)
    # ---- panel 3: training signal
    cx, cy, cw, ch = 550, 248, W - 560, 228
    panel(svg, cx, cy, cw, ch, 'blue', T('Training on the relayed answer', '在接力回答上训练'), 3)
    _model_box(svg, cx + 14, cy + 40, (cw - 38) / 2, 50, 'green', 'cap', T('Teacher scorer', '老师打分器'), T('all tokens', '整条回答'))
    _model_box(svg, cx + 24 + (cw - 38) / 2, cy + 40, (cw - 38) / 2, 50, 'blue', 'robot', T('Student', '学生'), T('being trained', '正在训练'))
    mtext(svg, cx + 14 + (cw - 38) / 4, cy + 110, 'log πT(yt | y<t)', 12.5, 'middle')
    mtext(svg, cx + 24 + 3 * (cw - 38) / 4, cy + 110, 'log πθ(yt | y<t)', 12.5, 'middle')
    svg.line(cx + 14 + (cw - 38) / 4, cy + 117, cx + cw / 2, cy + 134, 'leader')
    svg.line(cx + 24 + 3 * (cw - 38) / 4, cy + 117, cx + cw / 2, cy + 134, 'leader')
    svg.rect(cx + 18, cy + 136, cw - 36, 40, 'box', rx=8)
    mtext(svg, cx + cw / 2, cy + 161, 'Dt = log πθ(yt | y<t) − log πT(yt | y<t)', 13, 'middle')
    svg.text(cx + cw / 2, cy + 196, T('token-level reverse KL on every token,', '对每个 token 做 token 级反向 KL，'), cls='t-muted', anchor='middle', size=11.5)
    svg.text(cx + cw / 2, cy + 213, T('whoever wrote it', '无论由谁写'), cls='t-muted', anchor='middle', size=11.5)
    return svg


def _opd_framework_narrow(W, hand):
    H = 852
    svg = Svg(W, H, 'Scaffold-OPD: relay rollout, takeover triggers and training signal', hand=hand)
    legend_tokens(svg, 10, 16, [('blue', T('student', '学生')), ('green', T('teacher', '老师')), ('purple', T('takeover', '接管点')), ('end', T('end', '结束'))], size=11, gap=12)
    panel(svg, 6, 28, W - 12, 274, 'gray', T('Relay rollout (vLLM)', '接力生成（vLLM）'), 1, size=12.5)
    _model_box(svg, 18, 60, 158, 48, 'blue', 'robot', T('Student', '学生'), T('1.7B · drafts', '1.7B · 写草稿'))
    _model_box(svg, 184, 60, 158, 48, 'green', 'cap', T('Teacher', '老师'), T('4B · verifies', '4B · 验证'))
    ys, yt, x0 = 148, 214, 74
    svg.text(18, ys + 4, T('student', '学生'), cls='tx-blue', size=11, weight=700)
    svg.text(18, yt + 4, T('teacher', '老师'), cls='tx-green', size=11, weight=700)
    s1 = tokens(svg, x0, ys - 4.5, 5, 'blue', 9, 3)
    t1s = s1 + 12
    svg.rect(t1s, yt - 4.5, 9, 9, 'pn-purple', rx=2)
    t1e = tokens(svg, t1s + 12, yt - 4.5, 4, 'green', 9, 3)
    s2s = t1e + 12
    s2e = tokens(svg, s2s, ys - 4.5, 4, 'blue', 9, 3)
    t2s = s2e + 12
    svg.rect(t2s, yt - 4.5, 9, 9, 'pn-purple', rx=2)
    t2e = tokens(svg, t2s + 12, yt - 4.5, 2, 'green', 9, 3)
    svg.rect(t2e + 6, yt - 4.5, 9, 9, 'ink', rx=1.5)
    curve(svg, s1 + 1, ys + 6, t1s + 4, yt - 7, 'line l4')
    curve(svg, t1e + 1, yt - 6, s2s + 4, ys + 7, 'line l3', 'stroke-dasharray="3 3"')
    curve(svg, s2e + 1, ys + 6, t2s + 4, yt - 7, 'line l4')
    svg.text(t1s, yt + 22, '“Wait, …”', cls='tx-green', size=11, weight=600)
    svg.text(t2s, yt + 22, '“But …”', cls='tx-green', size=11, weight=600)
    svg.text(18, yt + 50, T('≤ 3 paragraphs per takeover, then hand back', '每次最多写 3 段后交还'), cls='t-muted', size=11)
    svg.text(18, yt + 68, T('≤ 2 takeovers; the answer ends after the 2nd', '每条回答最多接管 2 次，第 2 次后结束'), cls='t-muted', size=11)
    by = 314
    panel(svg, 6, by, W - 12, 296, 'purple', T('When does the teacher take over?', '老师何时接管？'), 2, size=12.5)

    def trig(i):
        y = by + 50
        svg.text(18, y, pick(T('Reflection trigger', '反思触发'), i), cls='t-strong', size=12)
        svg.text(18, y + 24, pick(T('teacher’s top-1', '老师 top-1'), i), cls='t-faint', size=11)
        x = chip(svg, 120, y + 10, 'Wait', 'green', solid=True, size=11)
        mtext(svg, x + 6, y + 24, '∈ R', 12.5)
        svg.text(18, y + 52, pick(T('student’s top-5', '学生 top-5'), i), cls='t-faint', size=11)
        x = 120
        for wd in ['So', 'Then', 'We', 'The', 'Let']:
            x = chip(svg, x, y + 38, wd, 'blue', size=10.5, pad=4) + 2
        mtext(svg, 120, y + 80, '∩ R = ∅', 12.5)
        svg.text(W - 18, y + 80, pick(T('→ take over', '→ 接管'), i), cls='tx-purple', anchor='end', size=12, weight=700)
        y += 116
        svg.text(18, y, pick(T('Concluding trigger', '收尾触发'), i), cls='t-strong', size=12)
        svg.text(18, y + 16, pick(T('implemented in the verify step', '在验证步中实现'), i), cls='t-faint', size=10.5)
        chip(svg, 18, y + 26, '### ✅ Final Answer', 'green', solid=True, size=11)
        svg.text(18, y + 64, pick(T('while the student keeps reasoning', '而学生还在往下写'), i), cls='t-muted', size=11)
        svg.text(W - 18, y + 64, pick(T('→ take over', '→ 接管'), i), cls='tx-purple', anchor='end', size=12, weight=700)
    per_lang(svg, trig)
    cy = 622
    panel(svg, 6, cy, W - 12, 222, 'blue', T('Training on the relayed answer', '在接力回答上训练'), 3, size=12.5)
    _model_box(svg, 18, cy + 38, 158, 46, 'green', 'cap', T('Teacher scorer', '老师打分器'), T('all tokens', '整条回答'))
    _model_box(svg, 184, cy + 38, 158, 46, 'blue', 'robot', T('Student', '学生'), T('being trained', '正在训练'))
    mtext(svg, 97, cy + 104, 'log πT(yt | y<t)', 11.5, 'middle')
    mtext(svg, 263, cy + 104, 'log πθ(yt | y<t)', 11.5, 'middle')
    svg.rect(16, cy + 120, W - 32, 38, 'box', rx=8)
    mtext(svg, W / 2, cy + 144, 'Dt = log πθ − log πT', 13, 'middle')
    svg.text(W / 2, cy + 180, T('token-level reverse KL on every token,', '对每个 token 做 token 级反向 KL，'), cls='t-muted', anchor='middle', size=11)
    svg.text(W / 2, cy + 197, T('whoever wrote it', '无论由谁写'), cls='t-muted', anchor='middle', size=11)
    return svg


# ============================================================================ StepCredit-RL framework
def scr_framework_aes(W):
    """v2 state graph, restyled: states as tinted chips, the shared state B in purple, outcomes as green / red chips."""
    narrow = W < 500
    rows = [(['A', 'B', 'C', 'D'], True), (['A', 'E', 'B', 'F'], False), (['A', 'B', 'G'], True)]
    if narrow:
        colx, rowy, H = [40, 100, 160, 220], [36, 90, 144], 300
    else:
        colx, rowy, H = [56, 142, 228, 314], [44, 100, 156], 204
    svg = Svg(W, H, 'Steps that start from the same environment state are compared across rollouts')
    bpos = []
    for r, (states, ok) in enumerate(rows):
        y = rowy[r]
        svg.text(colx[0] - 30, y + 4, f'τ{r + 1}', cls='t-faint', anchor='middle', size=12)
        for c, s in enumerate(states):
            x = colx[c]
            k = s == 'B'
            if c:
                arrow(svg, colx[c - 1] + 17, y, x - 18, y)
            svg.rect(x - 15, y - 13, 30, 26, 'pn-purple' if k else 'pn-gray', rx=7)
            svg.text(x, y + 4.5, s, cls='tx-purple' if k else 't-muted', anchor='middle', size=12.5, weight=700 if k else None)
            if k:
                bpos.append((x, y))
        ex = colx[len(states) - 1] + 28
        svg.rect(ex, y - 11, 70, 22, 'pn-green' if ok else 'pn-red', rx=11)
        svg.text(ex + 35, y + 4.2, T('success', '成功') if ok else T('fail', '失败'), cls='tx-green' if ok else 'tx-red', anchor='middle', size=11.5, weight=600)
    for (xa, ya), (xb, yb) in zip(bpos, bpos[1:]):
        svg.path(f'M{xa:.1f},{ya + 13:.1f} C{xa:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{yb - 13:.1f}', 'line l4', 'stroke-dasharray="4 3" stroke-width="1.4"')
    if narrow:
        ty = 204
        svg.rect(8, ty - 22, W - 16, 112, 'pn-gray', rx=10)

        def text(i):
            tx = 104 if i == 0 else 64
            svg.text(20, ty, pick(T('Episode level', '整局'), i), cls='tx-blue', size=12.5, weight=700)
            svg.text(tx, ty, pick(T('compare the outcomes of τ1–τ3', '比较 τ1–τ3 的最终成败'), i), size=12)
            svg.text(20, ty + 26, pick(T('Step level', '步级'), i), cls='tx-purple', size=12.5, weight=700)
            svg.text(tx, ty + 26, pick(T('compare the steps taken from B', '比较从 B 出发的各步'), i), size=12)
            svg.text(tx, ty + 44, pick(T('by what followed them', '按各自之后的结果'), i), cls='t-muted', size=12)
            svg.text(20, ty + 72, pick(T('No critic, no extra rollouts.', '无需 critic，也无需额外 rollout。'), i), cls='t-faint', size=11.5)
        per_lang(svg, text)
        return svg
    tx = 500
    svg.rect(tx - 18, 22, W - tx + 6, 166, 'pn-gray', rx=12)
    svg.text(tx, 50, T('Episode level', '整局'), cls='tx-blue', size=13, weight=700)
    svg.text(tx, 69, T('compare the outcomes of τ1–τ3', '比较 τ1–τ3 的最终成败'), size=12)
    svg.text(tx, 106, T('Step level', '步级'), cls='tx-purple', size=13, weight=700)
    svg.text(tx, 125, T('compare the steps taken from B', '比较从 B 出发的各步'), size=12)
    svg.text(tx, 142, T('(B→C, B→F, B→G) by what followed', '（B→C、B→F、B→G）之后的结果'), cls='t-muted', size=12)
    svg.text(tx, 174, T('No critic, no extra rollouts.', '无需 critic，也无需额外 rollout。'), cls='t-faint', size=11.5)
    return svg


def _state(svg, x, y, label, tone='gray', w=30, h=24, bold=False):
    svg.rect(x - w / 2, y - h / 2, w, h, f'pn-{tone}', rx=6)
    mtext(svg, x, y + 4.5, label, 12.5, 'middle', f'tx-{tone}' if tone != 'gray' else 'ink')


def scr_framework_inno(W, hand=True):
    """Full method diagram: agent loop, a group of rollouts, episode-level and same-state step-level advantages."""
    if W < 500:
        return _scr_framework_narrow(W, hand)
    H = 474
    svg = Svg(W, H, 'StepCredit-RL: multi-turn agent loop, a group of rollouts, episode-level and step-level advantages', hand=hand)
    # ---- panel 1: agent loop
    panel(svg, 10, 10, 226, H - 20, 'blue', T('Multi-turn agent loop', '多轮 Agent 交互'), 1)
    _model_box(svg, 24, 48, 198, 54, 'blue', 'robot', T('LLM agent', 'LLM Agent'), 'Qwen3-4B')
    _model_box(svg, 24, 238, 198, 54, 'yellow', 'house', T('Environment', '环境'), T('ALFWorld household', 'ALFWorld 家务任务'))
    arrow(svg, 74, 104, 74, 235)
    arrow(svg, 172, 235, 172, 104)
    svg.text(66, 150, T('tool call', '工具调用'), cls='t-faint', anchor='end', size=10.5)
    chip(svg, 30, 158, 'go to fridge 1', 'gray', size=10.5, pad=5)
    svg.text(180, 150, T('observation', '观察'), cls='t-faint', size=10.5)
    svg.text(122, 196, T('“You arrive at', '“You arrive at'), cls='t-muted', size=10.5)
    svg.text(122, 210, T('fridge 1. …”', 'fridge 1. …”'), cls='t-muted', size=10.5)

    def notes(i):
        y = 326
        for line in pick((['One LLM call + one tool call', '= one training sample;', 'the context does not grow.', '',
                           'Reward only at the end:', 'R = 1 if the task succeeds', 'within 20 steps, else 0.'],
                          ['一次 LLM 调用 + 一次工具调用', '= 一条训练样本，', '上下文不随步数增长。', '',
                           '只在最后给奖励：', '20 步内完成任务 R = 1，', '否则 R = 0。']), i):
            if line:
                svg.text(26, y, line, cls='t-muted', size=11.5)
            y += 17
    per_lang(svg, notes)
    # ---- panel 2: a group of rollouts
    gx, gy, gw, gh = 248, 10, W - 258, 214
    panel(svg, gx, gy, gw, gh, 'gray', T('A group of N = 8 rollouts of the same task', '同一任务的一组 N = 8 条 rollout'), 2)
    rows = [(['s₀', 's₁', 's₂', 's₃', 's₄'], True), (['s₀', 's₅', 's₁', 's₂', 's₆'], False), (['s₀', 's₁', 's₂', 's₇'], False)]
    ys = [64, 106, 148]
    pos2 = []
    for r, (states, ok) in enumerate(rows):
        y = ys[r]
        mtext(svg, gx + 26, y + 4.5, f'τ{r + 1}', 13, 'middle')
        x = gx + 66
        for c, s in enumerate(states):
            anchor = s == 's₂'
            _state(svg, x, y, s, 'purple' if anchor else 'gray')
            if anchor:
                pos2.append((x, y))
            if c < len(states) - 1:
                arrow(svg, x + 17, y, x + 47, y)
            x += 64
        tone, mark = ('green', 'check') if ok else ('red', 'cross')
        svg.rect(x - 22, y - 12, 74, 24, f'pn-{tone}', rx=12)
        icon(svg, mark, x - 8, y, 14, tone)
        mtext(svg, x + 22, y + 4.5, 'R = 1' if ok else 'R = 0', 12, 'middle', f'tx-{tone}')
    for (xa, ya), (xb, yb) in zip(pos2, pos2[1:]):
        svg.path(f'M{xa:.1f},{ya + 12:.1f} C{xa:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{yb - 12:.1f}', 'line l4', 'stroke-dasharray="4 3" stroke-width="1.4"')
    mtext(svg, gx + 26, 182, '⋮', 14, 'middle')
    svg.text(gx + 46, 200, T('s₂ appears in τ1, τ2 and τ3 (same observation hash) → one step-level group',
                             's₂ 出现在 τ1、τ2、τ3 中（环境观察的哈希相同）→ 组成一个步级分组'), cls='tx-purple', size=11.5)
    # ---- panel 3: episode level
    ex, ey, ew, eh = 248, 236, 300, H - 246
    panel(svg, ex, ey, ew, eh, 'blue', T('Episode level', '整局'), 3)
    for r, (val, sign) in enumerate([(1, 1), (0, -1), (0, -1)]):
        y = ey + 62 + r * 30
        mtext(svg, ex + 26, y + 4, f'τ{r + 1}', 12.5, 'middle')
        mtext(svg, ex + 66, y + 4, f'R = {val}', 12, 'middle')
        bw = 46
        if sign > 0:
            svg.path(hbar(ex + 140, y - 7, ex + 140 + bw, 14, 4), 's1')
        else:
            svg.path(f'M{ex + 140:.1f},{y - 7:.1f} H{ex + 140 - bw * 0.6 + 4:.1f} A4,4 0 0 0 {ex + 140 - bw * 0.6:.1f},{y - 3:.1f} V{y + 3:.1f} A4,4 0 0 0 {ex + 140 - bw * 0.6 + 4:.1f},{y + 7:.1f} H{ex + 140:.1f} Z', 's2')
        svg.line(ex + 140, y - 11, ex + 140, y + 11, 'axis')
    mtext(svg, ex + 140, ey + 62 + 3 * 30 + 4, '⋮', 13, 'middle')
    svg.rect(ex + 16, ey + eh - 58, ew - 32, 40, 'box', rx=8)
    mtext(svg, ex + ew / 2, ey + eh - 33, 'Aᴱ(τᵢ) = (Rᵢ − mean R) / std R', 13, 'middle')
    # ---- panel 4: step level
    sx, sy, sw, sh = 560, 236, W - 570, H - 246
    panel(svg, sx, sy, sw, sh, 'purple', T('Step level: same-state group', '步级：同状态分组'), 4)
    acts = [('go to fridge 1', 1, 1), ('go to cabinet 1', 0, -1), ('go to sinkbasin 1', 0, -1)]
    for r, (act, g, sign) in enumerate(acts):
        y = sy + 62 + r * 30
        _state(svg, sx + 30, y, 's₂', 'purple', 28, 22)
        chip(svg, sx + 52, y - 10, act, 'gray', size=10.5, pad=5)
        mtext(svg, sx + 196, y + 4, f'G = {g}', 12, 'middle')
        bw = 34
        bx0 = sx + 246
        if sign > 0:
            svg.path(hbar(bx0, y - 7, bx0 + bw, 14, 4), 's4')
        else:
            svg.path(f'M{bx0:.1f},{y - 7:.1f} H{bx0 - bw * 0.6 + 4:.1f} A4,4 0 0 0 {bx0 - bw * 0.6:.1f},{y - 3:.1f} V{y + 3:.1f} A4,4 0 0 0 {bx0 - bw * 0.6 + 4:.1f},{y + 7:.1f} H{bx0:.1f} Z', 's2')
        svg.line(bx0, y - 11, bx0, y + 11, 'axis')
    svg.rect(sx + 14, sy + eh - 58, sw - 28, 40, 'box', rx=8)
    mtext(svg, sx + sw / 2, sy + eh - 33, 'Aₜ = Aᴱ(τ) + Aˢ(sₜ, aₜ)', 13.5, 'middle')
    svg.text(sx + sw / 2, sy + eh - 66, T('no critic · no extra rollouts', '无需 critic · 无需额外 rollout'), cls='t-faint', anchor='middle', size=11)
    return svg


def _scr_framework_narrow(W, hand):
    H = 900
    svg = Svg(W, H, 'StepCredit-RL: agent loop, a group of rollouts, episode-level and step-level advantages', hand=hand)
    panel(svg, 6, 6, W - 12, 164, 'blue', T('Multi-turn agent loop', '多轮 Agent 交互'), 1, size=12.5)
    _model_box(svg, 16, 40, 158, 48, 'blue', 'robot', T('LLM agent', 'LLM Agent'), 'Qwen3-4B')
    _model_box(svg, 186, 40, 158, 48, 'yellow', 'house', T('Environment', '环境'), 'ALFWorld')
    arrow(svg, 176, 56, 184, 56)
    arrow(svg, 184, 72, 176, 72)
    svg.text(18, 112, T('tool call → observation; one sample per step,', '工具调用 → 观察；每步一条样本，'), cls='t-muted', size=11)
    svg.text(18, 129, T('the context does not grow.', '上下文不随步数增长。'), cls='t-muted', size=11)
    svg.text(18, 152, T('Reward only at the end: R = 1 or 0.', '只在最后给奖励：R = 1 或 0。'), cls='t-muted', size=11)
    gy = 182
    panel(svg, 6, gy, W - 12, 230, 'gray', T('A group of N = 8 rollouts', '一组 N = 8 条 rollout'), 2, size=12.5)
    rows = [(['s₀', 's₁', 's₂', 's₃'], True), (['s₀', 's₅', 's₁', 's₂'], False), (['s₀', 's₁', 's₂', 's₇'], False)]
    pos2 = []
    for r, (states, ok) in enumerate(rows):
        y = gy + 56 + r * 44
        mtext(svg, 24, y + 4.5, f'τ{r + 1}', 12.5, 'middle')
        x = 58
        for c, s in enumerate(states):
            a = s == 's₂'
            _state(svg, x, y, s, 'purple' if a else 'gray', 28, 22)
            if a:
                pos2.append((x, y))
            if c < len(states) - 1:
                arrow(svg, x + 16, y, x + 36, y)
            x += 54
        tone, mark = ('green', 'check') if ok else ('red', 'cross')
        svg.rect(x - 20, y - 11, 44, 22, f'pn-{tone}', rx=11)
        icon(svg, mark, x + 2, y, 13, tone)
    for (xa, ya), (xb, yb) in zip(pos2, pos2[1:]):
        svg.path(f'M{xa:.1f},{ya + 11:.1f} C{xa:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{yb - 11:.1f}', 'line l4', 'stroke-dasharray="4 3" stroke-width="1.4"')
    svg.text(18, gy + 200, T('s₂ repeats across rollouts → a step-level group', 's₂ 在多条 rollout 中出现 → 一个步级分组'), cls='tx-purple', size=11)
    ey = 424
    panel(svg, 6, ey, W - 12, 200, 'blue', T('Episode level', '整局'), 3, size=12.5)
    for r, (val, sign) in enumerate([(1, 1), (0, -1), (0, -1)]):
        y = ey + 56 + r * 28
        mtext(svg, 26, y + 4, f'τ{r + 1}', 12, 'middle')
        mtext(svg, 70, y + 4, f'R = {val}', 12, 'middle')
        b0 = 190
        if sign > 0:
            svg.path(hbar(b0, y - 7, b0 + 46, 14, 4), 's1')
        else:
            svg.path(f'M{b0:.1f},{y - 7:.1f} H{b0 - 24:.1f} A4,4 0 0 0 {b0 - 28:.1f},{y - 3:.1f} V{y + 3:.1f} A4,4 0 0 0 {b0 - 24:.1f},{y + 7:.1f} H{b0:.1f} Z', 's2')
        svg.line(b0, y - 11, b0, y + 11, 'axis')
    svg.rect(16, ey + 146, W - 32, 38, 'box', rx=8)
    mtext(svg, W / 2, ey + 170, 'Aᴱ(τᵢ) = (Rᵢ − mean R) / std R', 12.5, 'middle')
    sy = 636
    panel(svg, 6, sy, W - 12, 256, 'purple', T('Step level: same-state group', '步级：同状态分组'), 4, size=12.5)
    for r, (act, g, sign) in enumerate([('go to fridge 1', 1, 1), ('go to cabinet 1', 0, -1), ('go to sinkbasin 1', 0, -1)]):
        y = sy + 56 + r * 30
        _state(svg, 30, y, 's₂', 'purple', 26, 20)
        chip(svg, 50, y - 10, act, 'gray', size=10.5, pad=5)
        mtext(svg, 216, y + 4, f'G = {g}', 11.5, 'middle')
        b0 = 290
        if sign > 0:
            svg.path(hbar(b0, y - 7, b0 + 36, 14, 4), 's4')
        else:
            svg.path(f'M{b0:.1f},{y - 7:.1f} H{b0 - 18:.1f} A4,4 0 0 0 {b0 - 22:.1f},{y - 3:.1f} V{y + 3:.1f} A4,4 0 0 0 {b0 - 18:.1f},{y + 7:.1f} H{b0:.1f} Z', 's2')
        svg.line(b0, y - 11, b0, y + 11, 'axis')
    svg.text(W / 2, sy + 168, T('no critic · no extra rollouts', '无需 critic · 无需额外 rollout'), cls='t-faint', anchor='middle', size=11)
    svg.rect(16, sy + 184, W - 32, 40, 'box', rx=8)
    mtext(svg, W / 2, sy + 209, 'Aₜ = Aᴱ(τ) + Aˢ(sₜ, aₜ)', 13, 'middle')
    return svg


# ============================================================================ pipelines
STAGE_TONES_OPD = ['green', 'gray', 'yellow', 'blue', 'orange']
STAGE_ICONS_OPD = ['cap', 'funnel', 'book', 'relay', 'target']


def opd_pipeline_aes(W):
    """v2 numbered cards, each in its stage's tone with an icon; score pills unchanged."""
    items = [(T('Teacher solutions', '老师解答'), T('14,116 problems', '14,116 道题')),
             (T('Rejection sampling', '拒绝采样'), T('79% kept', '保留 79%')),
             (T('SFT'), T('1 epoch', '1 轮')),
             (T('Scaffold-OPD'), T('40 steps', '40 步')),
             (T('GRPO on failures', '错题回流 GRPO'), T('2,212 problems', '2,212 道题'))]
    p = OPD['pipeline_avg4']
    scores = [T(f'base {p["base"]:.1f}', f'基座 {p["base"]:.1f}'), None, f'{p["sft"]:.1f}', f'{p["takeover_40"]:.1f}', f'{p["grpo_30"]:.1f}']
    if W >= 500:
        w, gap, h = 128, 15, 76
        x0 = (W - (5 * w + 4 * gap)) / 2
        svg = Svg(W, 134, 'Scaffold-OPD pipeline with the 4-benchmark average after each stage')
        for i, ((title, detail), tone, kind) in enumerate(zip(items, STAGE_TONES_OPD, STAGE_ICONS_OPD)):
            bx = x0 + i * (w + gap)
            svg.rect(bx, 6, w, h, f'pn-{tone}', rx=10)
            icon(svg, kind, bx + 20, 28, 20, tone)
            svg.text(bx + w - 10, 24, f'0{i + 1}', cls=f'tx-{tone}', anchor='end', size=10.5, ls='0.08em')
            svg.text(bx + 12, 56, title, cls='t-strong', size=12.5)
            svg.text(bx + 12, 72, detail, cls='t-muted', size=11)
            if i:
                arrow(svg, bx - gap + 2, 6 + h / 2, bx - 2, 6 + h / 2)
            if scores[i]:
                key = i == 3
                V2.score_pill(svg, bx + w / 2, 100, scores[i], 'box-fill' if key else 'box-soft', 't-on' if key else ('t-muted' if i == 0 else 't-strong'), 11.5 if i == 0 else 12)
        return svg
    w, h, gap = W - 16, 52, 12
    svg = Svg(W, 6 + 5 * h + 4 * gap + 6, 'Scaffold-OPD pipeline with the 4-benchmark average after each stage')
    for i, ((title, detail), tone, kind) in enumerate(zip(items, STAGE_TONES_OPD, STAGE_ICONS_OPD)):
        y = 6 + i * (h + gap)
        svg.rect(8, y, w, h, f'pn-{tone}', rx=10)
        icon(svg, kind, 30, y + h / 2, 20, tone)
        svg.text(52, y + 22, title, cls='t-strong', size=12.5)
        svg.text(52, y + 39, detail, cls='t-muted', size=11)
        if scores[i]:
            pw = width_of(scores[i], 12, 600) + 16
            svg.rect(8 + w - 12 - pw, y + 15, pw, 22, 'box-fill' if i == 3 else 'box-soft', rx=11)
            svg.text(8 + w - 12 - pw / 2, y + 30, scores[i], cls='t-on' if i == 3 else ('t-muted' if i == 0 else 't-strong'), anchor='middle', size=12)
        if i:
            chevron(svg, W / 2, y - gap / 2, 3.5)
    return svg


def opd_pipeline_inno(W):
    """Stage cards on top, and under them a score rail: the 4-benchmark average after each training stage."""
    items = [(T('Teacher solutions', '老师解答'), T('14,116 problems', '14,116 道题')),
             (T('Rejection sampling', '拒绝采样'), T('11,158 kept (79%)', '保留 11,158 条（79%）')),
             (T('SFT'), T('1 epoch', '1 轮')),
             (T('Scaffold-OPD'), T('40 steps', '40 步')),
             (T('GRPO on failures', '错题回流 GRPO'), T('2,212 problems · 30 steps', '2,212 道题 · 30 步'))]
    p = OPD['pipeline_avg4']
    vals = [p['base'], None, p['sft'], p['takeover_40'], p['grpo_30']]
    if W < 500:
        return opd_pipeline_aes(W)
    w, gap, h = 132, 12, 82
    x0 = (W - (5 * w + 4 * gap)) / 2
    H = 236
    svg = Svg(W, H, 'Scaffold-OPD pipeline; under it, the 4-benchmark average after each training stage')
    for i, ((title, detail), tone, kind) in enumerate(zip(items, STAGE_TONES_OPD, STAGE_ICONS_OPD)):
        bx = x0 + i * (w + gap)
        svg.rect(bx, 8, w, h, f'pn-{tone}', rx=10)
        icon(svg, kind, bx + 20, 30, 20, tone)
        svg.text(bx + 12, 60, title, cls='t-strong', size=12.5)
        svg.text(bx + 12, 76, detail, cls='t-muted', size=10.5)
        if i:
            arrow(svg, bx - gap + 1, 8 + h / 2, bx - 1, 8 + h / 2)
    # score rail
    top, bot = 118, 206
    sy = lambda v: bot - (v - 20) / 30 * (bot - top)
    for v in (20, 30, 40, 50):
        svg.line(x0, sy(v), x0 + 5 * w + 4 * gap, sy(v), 'grid')
        svg.text(x0 - 6, sy(v) + 4, str(v), cls='t-faint', anchor='end', size=10.5)
    pts = [(x0 + i * (w + gap) + w / 2, v) for i, v in enumerate(vals) if v is not None]
    svg.path(' '.join(f'{"M" if j == 0 else "L"}{x:.1f},{sy(v):.1f}' for j, (x, v) in enumerate(pts)), 'line l1')
    for j, (x, v) in enumerate(pts):
        svg.circle(x, sy(v), 5 if j == 2 else 4, 'dot s1')
        svg.text(x, sy(v) - 10, f'{v:.1f}', cls='t-strong' if j else 't-muted', anchor='middle', size=12)
    svg.text(x0, H - 8, T('4-benchmark average after each stage (base model 25.4)', '每段之后的 4 项平均分（基座 25.4）'), cls='t-faint', size=11)
    return svg


def scr_pipeline_aes(W):
    """v2 cards with micro-bars, in tones: base gray, SFT yellow, RL blue, evaluation green."""
    stages = [(T('Base model', '基座模型'), T('before training', '训练前'), (7.1, 2.2), 'gray', 'robot'),
              (T('Expert SFT', '专家 SFT'), T('22,810 examples · 1 epoch', '22,810 条样本 · 1 轮'), (67.1, 67.2), 'yellow', 'book'),
              (T('Multi-turn RL', '多轮 RL'), T('StepCredit-RL · 100 steps', 'StepCredit-RL · 100 步'), (98.6, 94.0), 'blue', 'target'),
              (T('Paired eval', '配对评测'), T('per-task results', '记录每个任务的结果'), None, 'green', 'scale')]
    if W < 500:
        return V2.scr_pipeline(W)
    w, gap, h, y0 = 164, 18, 104, 32
    x = (W - (4 * w + 3 * gap)) / 2
    svg = Svg(W, y0 + h + 8, 'StepCredit-RL pipeline with ALFWorld success (seen and unseen) after each stage')
    V2.chip_legend(svg, x, 16, [('s1', 'seen'), ('pn-blue', 'unseen')], size=11)
    for i, (title, detail, sc, tone, kind) in enumerate(stages):
        bx = x + i * (w + gap)
        svg.rect(bx, y0, w, h, f'pn-{tone}', rx=10)
        icon(svg, kind, bx + 20, y0 + 22, 18, tone)
        svg.text(bx + 36, y0 + 27, title, cls='t-strong', size=12.5)
        svg.text(bx + 12, y0 + 48, detail, cls='t-muted', size=10.5)
        if sc:
            for j, (v, cls_, nm) in enumerate([(sc[0], 's1', 'seen'), (sc[1], 'pn-blue', 'unseen')]):
                yb = y0 + 62 + j * 18
                tw = w - 24 - 36
                svg.rect(bx + 12, yb, tw, 8, 'band', rx=4)
                svg.mark(f'{title[0]} · {nm}: {v:.1f}%', f'<path class="bar {cls_}" d="{hbar(bx + 12, yb, bx + 12 + tw * v / 100, 8, 4)}"' + '' + '/>')
                svg.text(bx + w - 12, yb + 8, f'{v:.1f}', cls='t-strong' if i == 2 else '', anchor='end', size=11)
        else:
            svg.text(bx + 12, y0 + 72, T('exact McNemar test', '精确 McNemar 检验'), size=11.5)
            svg.text(bx + 12, y0 + 90, T('two runs, same tasks', '两次运行、同一批任务'), cls='t-faint', size=11)
        if i:
            arrow(svg, bx - gap + 2, y0 + h / 2, bx - 2, y0 + h / 2)
    return svg


def scr_pipeline_inno(W):
    """A success staircase: one column pair per stage (seen / unseen) with the stage card under it."""
    if W < 500:
        return scr_pipeline_aes(W)
    stages = [(T('Base model', '基座模型'), (7.1, 2.2), 'gray', 'robot'),
              (T('Expert SFT', '专家 SFT'), (67.1, 67.2), 'yellow', 'book'),
              (T('RL · 20 steps', 'RL · 20 步'), (98.6, 91.0), 'blue', 'target'),
              (T('RL · 100 steps', 'RL · 100 步'), (98.6, 94.0), 'blue', 'target')]
    H = 262
    svg = Svg(W, H, 'ALFWorld success after each stage of the StepCredit-RL pipeline')
    V2.chip_legend(svg, 40, 16, [('s1', 'seen'), ('pn-blue', 'unseen')], size=11)
    x0, x1, top, base = 40, W - 20, 36, 196
    sy = lambda v: base - v / 100 * (base - top)
    for v in (0, 50, 100):
        svg.line(x0, sy(v), x1, sy(v), 'grid' if v else 'axis')
        svg.text(x0 - 6, sy(v) + 4, str(v), cls='t-faint', anchor='end', size=10.5)
    gw = (x1 - x0) / len(stages)
    for i, (title, (s, u), tone, kind) in enumerate(stages):
        cx = x0 + gw * (i + 0.5)
        for j, (v, cls_) in enumerate([(s, 's1'), (u, 'pn-blue')]):
            bx = cx - 24 if j == 0 else cx + 2
            svg.mark(f'{title[0]}: {v:.1f}%', f'<path class="bar {cls_}" d="{vbar(bx, base, sy(v), 22)}"' + '' + '/>')
            svg.text(bx + 11, sy(v) - 6, f'{v:.1f}', cls='t-strong' if i >= 2 else 't-muted', anchor='middle', size=11)
        svg.rect(cx - gw / 2 + 8, 208, gw - 16, 40, f'pn-{tone}', rx=9)
        icon(svg, kind, cx - gw / 2 + 26, 228, 16, tone)
        svg.text(cx - gw / 2 + 42, 233, title, cls='t-strong', size=12)
        if i:
            arrow(svg, cx - gw / 2 + 1, 228, cx - gw / 2 + 7, 228)
    return svg



# ============================================================================ home-page cards
def card_opd_aes(W=380):
    """v2 word-chip paragraph, restyled: student chips blue, teacher runs green, takeover start purple."""
    svg = Svg(W, 126, 'An answer written by the student, with two passages written by the teacher')
    rows = [[34, 18, 46, 26, 40, 22, 30, 38, 20], [28, 44, 20, 32, 48, 36, 26, 30], [40, 24, 30, 52, 22, 34, 28, 26], [30, 46, 22, 38]]
    teacher = {(1, 4), (1, 5), (1, 6), (1, 7), (3, 2), (3, 3)}
    start = {(1, 4), (3, 2)}
    labels = {(1, 4): 'Wait,', (3, 2): 'But'}
    x0, gap, y0, pitch = 26, 5, 14, 24
    for r, row in enumerate(rows):
        x, y = x0, y0 + r * pitch
        for c, w in enumerate(row):
            tone = 'purple' if (r, c) in start else ('green' if (r, c) in teacher else 'blue')
            svg.rect(x, y, w, 10, f'pn-{tone}', rx=5)
            if (r, c) in labels:
                svg.text(x, y - 3.5, labels[(r, c)], cls='tx-green', size=10.5, weight=700)
            x += w + gap
    ly = y0 + 3 * pitch

    def key(i):
        lx = 204
        for tone, lab in [('blue', T('student', '学生')), ('green', T('teacher', '老师'))]:
            svg.rect(lx, ly + 1, 14, 8, f'pn-{tone}', rx=4)
            svg.text(lx + 19, ly + 9, lab[i], cls='t-muted', size=11)
            lx += 19 + svg.tw(lab[i], 11) + 14
    per_lang(svg, key)
    V2.breadcrumb(svg, [T('Teacher data', '老师数据'), T('SFT'), T('Scaffold-OPD'), T('GRPO')], 2, 116)
    return svg


def card_opd_inno(W=380):
    """A miniature of the method figure: student and teacher lanes, two takeovers, the answer ends."""
    svg = Svg(W, 126, 'Miniature: the teacher takes over the student’s answer twice, then the answer ends', hand=True)
    _model_box(svg, 10, 14, 112, 40, 'blue', 'robot', T('Student', '学生'), '1.7B')
    _model_box(svg, 10, 72, 112, 40, 'green', 'cap', T('Teacher', '老师'), '4B')
    ys, yt = 34, 92
    x = 138
    s1 = tokens(svg, x, ys - 5, 5, 'blue', 10, 3)
    t1s = s1 + 12
    svg.rect(t1s, yt - 5, 10, 10, 'pn-purple', rx=2)
    t1e = tokens(svg, t1s + 13, yt - 5, 4, 'green', 10, 3)
    s2s = t1e + 12
    s2e = tokens(svg, s2s, ys - 5, 4, 'blue', 10, 3)
    t2s = s2e + 12
    svg.rect(t2s, yt - 5, 10, 10, 'pn-purple', rx=2)
    t2e = tokens(svg, t2s + 13, yt - 5, 2, 'green', 10, 3)
    svg.rect(t2e + 6, yt - 5, 10, 10, 'ink', rx=1.5)
    curve(svg, s1 + 1, ys + 6, t1s + 4, yt - 7, 'line l4')
    curve(svg, t1e + 1, yt - 6, s2s + 4, ys + 7, 'line l3', 'stroke-dasharray="3 3"')
    curve(svg, s2e + 1, ys + 6, t2s + 4, yt - 7, 'line l4')
    svg.text(t1s, yt + 22, '“Wait, …”', cls='tx-green', size=11, weight=700)
    svg.text(t2s, yt + 22, '“But …”', cls='tx-green', size=11, weight=700)
    return svg


def card_scr_aes(W=380):
    """v2 branching picture, restyled: B purple, outcomes green / red, credit chips on the branches."""
    svg = Svg(W, 126, 'Two rollouts reach the same state B; the steps taken from B get opposite credit')
    A, B = (40, 54), (120, 54)
    up, dn = [(200, 28), (262, 28)], [(200, 80), (262, 80)]
    arrow(svg, A[0] + 12, A[1], B[0] - 15, B[1])
    import math as m
    for path, ok in [(up, True), (dn, False)]:
        (x1, y1), (x2, y2) = path
        ang = m.atan2(y1 - B[1], x1 - B[0])
        arrow(svg, B[0] + 15 * m.cos(ang), B[1] + 15 * m.sin(ang), x1 - 12 * m.cos(ang), y1 - 12 * m.sin(ang))
        arrow(svg, x1 + 12, y1, x2 - 12, y2)
        for (x, y) in path:
            svg.rect(x - 11, y - 10, 22, 20, 'pn-gray', rx=6)
        tone = 'green' if ok else 'red'
        svg.rect(x2 + 20, y2 - 10, 62, 20, f'pn-{tone}', rx=10)
        svg.text(x2 + 51, y2 + 4, T('success', '成功') if ok else T('fail', '失败'), cls=f'tx-{tone}', anchor='middle', size=11, weight=600)
    for (x, y), cls, sign in [(up[0], 's4', '+'), (dn[0], 's2', '−')]:
        mx, my = (B[0] + x) / 2 + 2, (B[1] + y) / 2
        svg.rect(mx - 9, my - 7, 18, 14, cls, rx=7)
        svg.text(mx, my + 4.2, sign, cls='t-on', anchor='middle', size=12)
    svg.rect(A[0] - 11, A[1] - 10, 22, 20, 'pn-gray', rx=6)
    svg.text(A[0], A[1] + 4, 'A', cls='t-muted', anchor='middle', size=11)
    svg.rect(B[0] - 14, B[1] - 12, 28, 24, 'pn-purple', rx=7)
    svg.text(B[0], B[1] + 4.5, 'B', cls='tx-purple', anchor='middle', size=12, weight=700)
    svg.text(B[0], B[1] + 30, T('same state', '同一状态'), cls='t-faint', anchor='middle', size=10.5)
    V2.breadcrumb(svg, [T('Expert demos', '专家示范'), T('SFT'), T('Multi-turn RL', '多轮 RL'), T('Paired eval', '配对评测')], 2, 116)
    return svg


def card_scr_inno(W=380):
    """A miniature of the method figure: three rollouts that meet at the same state, outcomes at the end."""
    svg = Svg(W, 126, 'Miniature: three rollouts reach the same state s₂; their steps from s₂ are compared', hand=True)
    rows = [(['s₀', 's₁', 's₂', 's₃'], True), (['s₀', 's₅', 's₁', 's₂'], False), (['s₀', 's₁', 's₂', 's₇'], False)]
    pos = []
    for r, (states, ok) in enumerate(rows):
        y = 22 + r * 38
        mtext(svg, 22, y + 4.5, f'τ{r + 1}', 12.5, 'middle')
        x = 58
        for c, s in enumerate(states):
            a = s == 's₂'
            _state(svg, x, y, s, 'purple' if a else 'gray', 30, 22)
            if a:
                pos.append((x, y))
            if c < len(states) - 1:
                arrow(svg, x + 17, y, x + 43, y)
            x += 62
        tone, mark = ('green', 'check') if ok else ('red', 'cross')
        svg.rect(x - 24, y - 11, 46, 22, f'pn-{tone}', rx=11)
        icon(svg, mark, x - 1, y, 13, tone)
    for (xa, ya), (xb, yb) in zip(pos, pos[1:]):
        svg.path(f'M{xa:.1f},{ya + 11:.1f} C{xa:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{yb - 11:.1f}', 'line l4', 'stroke-dasharray="4 3" stroke-width="1.4"')
    return svg


AES = {'card-opd': card_opd_aes, 'card-scr': card_scr_aes, 'opd-pipeline': opd_pipeline_aes, 'opd-takeover': opd_framework_aes,
       'scr-pipeline': scr_pipeline_aes, 'scr-steplevel': scr_framework_aes}
INNO = {'card-opd': card_opd_inno, 'card-scr': card_scr_inno, 'opd-pipeline': opd_pipeline_inno, 'opd-takeover': opd_framework_inno,
        'scr-pipeline': scr_pipeline_inno, 'scr-steplevel': scr_framework_inno}
