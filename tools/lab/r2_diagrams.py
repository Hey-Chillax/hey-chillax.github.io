"""Round 2 (2026-11-16), diagrams: each starts from the version kept in round 1.

  aes   round-1 pick polished (math with real subscripts, collisions fixed, stronger tokens, tighter spacing)
  inno  round-1 pick restructured (framework figures composed as a loop: rollout -> training -> weights back)
"""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE / 'v2'))
sys.path.insert(0, str(HERE))

from figlib import OPD, Svg, T, arrow, chevron, hbar, vbar, width_of  # noqa: E402
from figkit import SOLID, badge, chip, curve, icon, mrich, panel, tokens, wedge_bracket  # noqa: E402
import figures_v2 as V2  # noqa: E402
import r1_diagrams as R1  # noqa: E402

pick, per_lang = V2.pick, V2.per_lang
_model_box, legend_tokens, _state = R1._model_box, R1.legend_tokens, R1._state


def _lanes(svg, x0, ys, yt, n1, n2, n3, n4, size=11, gap=3, seg_gap=18):
    """Student / teacher lanes with two takeovers; returns the key x positions."""
    p = size + gap
    s1 = tokens(svg, x0, ys - size / 2, n1, 'blue', size, gap)
    t1s = s1 + seg_gap
    svg.rect(t1s, yt - size / 2, size, size, 'pn-purple', rx=2.5)
    t1e = tokens(svg, t1s + p, yt - size / 2, n2, 'green', size, gap)
    s2s = t1e + seg_gap
    s2e = tokens(svg, s2s, ys - size / 2, n3, 'blue', size, gap)
    t2s = s2e + seg_gap
    svg.rect(t2s, yt - size / 2, size, size, 'pn-purple', rx=2.5)
    t2e = tokens(svg, t2s + p, yt - size / 2, n4, 'green', size, gap)
    svg.rect(t2e + 7, yt - size / 2, size, size, 'ink', rx=1.5)
    curve(svg, s1 + 2, ys + size / 2 + 1, t1s + size / 2, yt - size / 2 - 2, 'line l4')
    curve(svg, t1e + 2, yt - size / 2 - 1, s2s + size / 2, ys + size / 2 + 2, 'line l3', 'stroke-dasharray="3 3"')
    curve(svg, s2e + 2, ys + size / 2 + 1, t2s + size / 2, yt - size / 2 - 2, 'line l4')
    return dict(s1=s1, t1s=t1s, t1e=t1e, s2s=s2s, s2e=s2e, t2s=t2s, t2e=t2e)


def _training_box(svg, x, y, w, compact=False):
    bw = (w - 10) / 2
    _model_box(svg, x, y, bw, 50, 'green', 'cap', T('Teacher scorer', '老师打分器'), T('all tokens', '整条回答'))
    _model_box(svg, x + bw + 10, y, bw, 50, 'blue', 'robot', T('Student', '学生'), T('being trained', '正在训练'))
    mrich(svg, x + bw / 2, y + 70, 'log π_T(y_t | y_{<t})', 12.5, 'middle')
    mrich(svg, x + bw + 10 + bw / 2, y + 70, 'log π_θ(y_t | y_{<t})', 12.5, 'middle')
    svg.line(x + bw / 2, y + 77, x + w / 2, y + 94, 'leader')
    svg.line(x + bw + 10 + bw / 2, y + 77, x + w / 2, y + 94, 'leader')
    svg.rect(x + 4, y + 96, w - 8, 40, 'box', rx=8)
    mrich(svg, x + w / 2, y + 121, 'D_t = log π_θ(y_t | y_{<t}) − log π_T(y_t | y_{<t})', 12.5 if not compact else 11.5, 'middle')
    svg.text(x + w / 2, y + 156, T('reverse KL on every token,', '对每个 token 做反向 KL，'), cls='t-muted', anchor='middle', size=11.5)
    svg.text(x + w / 2, y + 173, T('whoever wrote it', '无论由谁写'), cls='t-muted', anchor='middle', size=11.5)


def _reflection_rule(svg, x, y, i, right):
    svg.text(x, y, pick(T('Reflection trigger', '反思触发'), i), cls='t-strong', size=12.5)
    y += 16
    svg.text(x, y + 2, pick(T('teacher’s top-1', '老师 top-1'), i), cls='t-faint', size=10.5)
    xx = chip(svg, x, y + 7, 'Wait', 'green', solid=True)
    mrich(svg, xx + 6, y + 22, '∈ R', 13)
    xx += 34
    w_and = svg.tw(pick(T('and', '且'), i), 11.5)
    svg.text(xx + 6, y + 22, pick(T('and', '且'), i), cls='t-muted', size=11.5)
    xx += 6 + w_and + 10
    svg.text(xx, y + 2, pick(T('student’s top-5', '学生 top-5'), i), cls='t-faint', size=10.5)
    for wd in ['So', 'Then', 'We', 'The', 'Let']:
        xx = chip(svg, xx, y + 7, wd, 'blue', size=11, pad=6) + 3
    mrich(svg, xx + 4, y + 22, '∩ R = ∅', 13)
    svg.text(right, y + 22, pick(T('→ take over', '→ 接管'), i), cls='tx-purple', anchor='end', size=12.5, weight=700)
    svg.text(x, y + 46, pick(T('R: the 45 reflection words (Wait, But, …)', 'R：45 个反思词（Wait、But 等）'), i), cls='t-faint', size=11)


def _conclude_rule(svg, x, y, i, right):
    t = pick(T('Concluding trigger', '收尾触发'), i)
    svg.text(x, y, t, cls='t-strong', size=12.5)
    svg.text(x + svg.tw(t, 12.5, 600) + 8, y, pick(T('my addition, in the verify step', '我在验证步中实现'), i), cls='t-faint', size=11)
    y += 16
    svg.text(x, y + 2, pick(T('teacher wants to conclude', '老师想开始收尾'), i), cls='t-faint', size=10.5)
    xx = chip(svg, x, y + 7, '### ✅ Final Answer', 'green', solid=True)
    w_while = svg.tw(pick(T('while', '而'), i), 11.5)
    svg.text(xx + 8, y + 22, pick(T('while', '而'), i), cls='t-muted', size=11.5)
    xx += 8 + w_while + 10
    svg.text(xx, y + 2, pick(T('student', '学生'), i), cls='t-faint', size=10.5)
    chip(svg, xx, y + 7, pick(T('keeps reasoning …', '还在往下写……'), i), 'blue', size=11)
    svg.text(right, y + 22, pick(T('→ take over', '→ 接管'), i), cls='tx-purple', anchor='end', size=12.5, weight=700)


# ============================================================================ Scaffold-OPD framework
def opd_framework_aes(W, hand=True):
    """Round-1 layout, polished."""
    if W < 500:
        return _opd_narrow(W, hand)
    H = 494
    svg = Svg(W, H, 'Scaffold-OPD: relay rollout inside speculative decoding, the takeover triggers, and the token-level training signal', hand=hand)
    legend_tokens(svg, 16, 18, [('blue', T('student token', '学生 token')), ('green', T('teacher token', '老师 token')),
                                ('purple', T('takeover point', '接管点')), ('end', T('answer ends', '回答结束'))])
    panel(svg, 10, 30, W - 20, 212, 'gray', T('Relay rollout inside vLLM speculative decoding', 'vLLM 投机解码中的接力生成'), 1)
    _model_box(svg, 26, 62, 178, 52, 'blue', 'robot', T('Student', '学生'), T('Qwen3-1.7B · drafts', 'Qwen3-1.7B · 写草稿'))
    _model_box(svg, 26, 154, 178, 52, 'green', 'cap', T('Teacher', '老师'), T('Qwen3-4B · verifies', 'Qwen3-4B · 验证'))
    arrow(svg, 96, 116, 96, 151)
    arrow(svg, 134, 151, 134, 117)
    svg.text(89, 138, T('draft', '草稿'), cls='t-faint', anchor='end', size=10.5)
    svg.text(141, 138, T('accept / take over', '接受 / 接管'), cls='t-faint', size=10.5)
    ys, yt = 88, 180
    svg.line(226, ys, W - 26, ys, 'grid', 'stroke-dasharray="2 4"')
    svg.line(226, yt, W - 26, yt, 'grid', 'stroke-dasharray="2 4"')
    k = _lanes(svg, 234, ys, yt, 12, 8, 10, 5, size=12, gap=3)
    badge(svg, (k['s1'] + k['t1s']) / 2 + 4, (ys + yt) / 2, 1, 'purple', 7.5)
    badge(svg, (k['s2e'] + k['t2s']) / 2 + 4, (ys + yt) / 2, 2, 'purple', 7.5)
    svg.text(234, ys - 14, T('“… so the answer is 47.”', '“……所以答案是 47。”'), cls='t-muted', size=11.5)
    svg.text(k['s2s'], ys - 14, T('“… so the answer is 52.”', '“……所以答案是 52。”'), cls='t-muted', size=11.5)
    svg.text(k['t1s'] + 16, yt - 16, '“Wait, let me check step 2 …”', cls='tx-green', size=11.5, weight=700)
    svg.text(k['t2s'] + 16, yt - 16, '“But the question asks …”', cls='tx-green', size=11.5, weight=700)
    wedge_bracket(svg, k['t1s'], k['t1e'], yt + 14, 'leader', 5)
    svg.text((k['t1s'] + k['t1e']) / 2, yt + 31, T('≤ 3 paragraphs (≤ 256 tokens), then hand back', '最多写 3 段（≤ 256 token）后交还'), cls='t-muted', anchor='middle', size=11)
    svg.text(W - 30, yt + 31, T('≤ 2 takeovers per answer', '每条回答最多接管 2 次'), cls='t-muted', anchor='end', size=11)
    bx, by, bw, bh = 10, 254, 536, 230
    panel(svg, bx, by, bw, bh, 'purple', T('When does the teacher take over?', '老师何时接管？'), 2)
    per_lang(svg, lambda i: (_reflection_rule(svg, bx + 18, by + 52, i, bx + bw - 16), _conclude_rule(svg, bx + 18, by + 152, i, bx + bw - 16)))
    cx, cy, cw, ch = 556, 254, W - 566, 230
    panel(svg, cx, cy, cw, ch, 'blue', T('Training on the relayed answer', '在接力回答上训练'), 3)
    _training_box(svg, cx + 14, cy + 40, cw - 28)
    return svg


def opd_framework_inno(W, hand=True):
    """Composed as a loop: rollout (1) sends relayed answers to training (3), which sends weights back; the takeover
    rule (2) is a zoom-in on a takeover point."""
    if W < 500:
        return _opd_narrow(W, hand)
    H = 470
    svg = Svg(W, H, 'Scaffold-OPD as a loop: relay rollout, training on the relayed answer, weights back to the drafter; and the takeover rule', hand=hand)
    legend_tokens(svg, 16, 18, [('blue', T('student token', '学生 token')), ('green', T('teacher token', '老师 token')),
                                ('purple', T('takeover point', '接管点')), ('end', T('answer ends', '回答结束'))])
    px, pw = 10, 556
    panel(svg, px, 30, pw, 214, 'gray', T('Relay rollout in vLLM speculative decoding', 'vLLM 投机解码中的接力生成'), 1)
    _model_box(svg, 24, 62, 150, 50, 'blue', 'robot', T('Student', '学生'), T('1.7B · drafts', '1.7B · 写草稿'))
    _model_box(svg, 24, 158, 150, 50, 'green', 'cap', T('Teacher', '老师'), T('4B · verifies', '4B · 验证'))
    arrow(svg, 84, 114, 84, 155)
    arrow(svg, 114, 155, 114, 115)
    svg.text(78, 139, T('draft', '草稿'), cls='t-faint', anchor='end', size=10.5)
    svg.text(120, 139, T('verify', '验证'), cls='t-faint', size=10.5)
    ys, yt = 87, 183
    svg.line(186, ys, px + pw - 12, ys, 'grid', 'stroke-dasharray="2 4"')
    svg.line(186, yt, px + pw - 12, yt, 'grid', 'stroke-dasharray="2 4"')
    k = _lanes(svg, 192, ys, yt, 8, 6, 6, 3, size=11, gap=3, seg_gap=17)
    b1 = ((k['s1'] + k['t1s']) / 2 + 4, (ys + yt) / 2)
    badge(svg, *b1, 1, 'purple', 7.5)
    badge(svg, (k['s2e'] + k['t2s']) / 2 + 4, (ys + yt) / 2, 2, 'purple', 7.5)
    svg.text(192, ys - 14, T('“… the answer is 47.”', '“……答案是 47。”'), cls='t-muted', size=11)
    svg.text(k['s2s'], ys - 14, T('“… the answer is 52.”', '“……答案是 52。”'), cls='t-muted', size=11)
    svg.text(k['t1s'] + 15, yt - 15, '“Wait, let me check …”', cls='tx-green', size=11, weight=700)
    svg.text(k['t2s'] - 6, yt + 30, '“But …”', cls='tx-green', size=11, weight=700)
    wedge_bracket(svg, k['t1s'], k['t1e'], yt + 13, 'leader', 5)
    svg.text((k['t1s'] + k['t1e']) / 2, yt + 30, T('≤ 3 paragraphs', '每次最多 3 段'), cls='t-muted', anchor='middle', size=11)
    svg.text(px + pw - 14, yt + 48, T('≤ 2 takeovers; ends after the 2nd', '最多接管 2 次，第 2 次后结束'), cls='t-muted', anchor='end', size=11)
    # training panel and the loop between the two panels
    tx, tw = 636, W - 646
    panel(svg, tx, 30, tw, 214, 'blue', T('Training', '训练'), 3)
    _training_box(svg, tx + 12, 60, tw - 24, compact=True)
    arrow(svg, px + pw + 6, 96, tx - 6, 96, 'line l1', 7)
    arrow(svg, tx - 6, 178, px + pw + 6, 178, 'line l1', 7)
    def loop_labels(i):
        mid = (px + pw + tx) / 2
        for yy, line in [(80, T('relayed', '接力')), (92, T('answers', '回答'))]:
            svg.text(mid, yy, pick(line, i), cls='tx-blue', anchor='middle', size=10.5, weight=700)
        for yy, line in [(198, T('new', '新的')), (210, T('weights', '权重'))]:
            svg.text(mid, yy, pick(line, i), cls='tx-blue', anchor='middle', size=10.5, weight=700)
    per_lang(svg, loop_labels)
    # takeover rule as a zoom-in on takeover point 1
    zy = 262
    panel(svg, 10, zy, W - 20, H - zy - 10, 'purple', T('What happens at a takeover point: the teacher checks while verifying the draft', '接管点上发生了什么：老师在验证草稿时顺带判断'), 2)
    svg.path(f'M{b1[0]:.1f},{b1[1] + 8:.1f} L{b1[0]:.1f},{zy:.1f}', 'line l4', 'stroke-dasharray="3 3"')
    half = (W - 20) / 2
    svg.line(10 + half, zy + 40, 10 + half, H - 26, 'grid')
    per_lang(svg, lambda i: (_reflection_rule(svg, 28, zy + 58, i, 10 + half - 16), _conclude_rule(svg, 26 + half, zy + 58, i, W - 26)))
    return svg


def _opd_narrow(W, hand):
    H = 872
    svg = Svg(W, H, 'Scaffold-OPD: relay rollout, training, and the takeover rule', hand=hand)
    legend_tokens(svg, 10, 16, [('blue', T('student', '学生')), ('green', T('teacher', '老师')), ('purple', T('takeover', '接管点')), ('end', T('end', '结束'))], size=11, gap=12)
    panel(svg, 6, 28, W - 12, 284, 'gray', T('Relay rollout (vLLM)', '接力生成（vLLM）'), 1, size=12.5)
    _model_box(svg, 16, 60, 160, 48, 'blue', 'robot', T('Student', '学生'), T('1.7B · drafts', '1.7B · 写草稿'))
    _model_box(svg, 184, 60, 160, 48, 'green', 'cap', T('Teacher', '老师'), T('4B · verifies', '4B · 验证'))
    ys, yt = 150, 218
    svg.text(16, ys + 4, T('student', '学生'), cls='tx-blue', size=11, weight=700)
    svg.text(16, yt + 4, T('teacher', '老师'), cls='tx-green', size=11, weight=700)
    k = _lanes(svg, 72, ys, yt, 5, 4, 4, 2, size=9, gap=3, seg_gap=12)
    svg.text(k['t1s'], yt + 22, '“Wait, …”', cls='tx-green', size=11, weight=700)
    svg.text(k['t2s'] - 4, yt + 22, '“But …”', cls='tx-green', size=11, weight=700)
    svg.text(16, yt + 50, T('≤ 3 paragraphs per takeover, then hand back', '每次最多写 3 段后交还'), cls='t-muted', size=11)
    svg.text(16, yt + 68, T('≤ 2 takeovers; the answer ends after the 2nd', '最多接管 2 次，第 2 次后结束'), cls='t-muted', size=11)
    by = 324

    def trig(i):
        panel(svg, 6, by, W - 12, 300, 'purple', pick(T('When does the teacher take over?', '老师何时接管？'), i), 2, size=12.5)
        y = by + 50
        svg.text(18, y, pick(T('Reflection trigger', '反思触发'), i), cls='t-strong', size=12)
        svg.text(18, y + 24, pick(T('teacher’s top-1', '老师 top-1'), i), cls='t-faint', size=11)
        x = chip(svg, 118, y + 10, 'Wait', 'green', solid=True, size=11)
        mrich(svg, x + 6, y + 24, '∈ R', 12.5)
        svg.text(18, y + 52, pick(T('student’s top-5', '学生 top-5'), i), cls='t-faint', size=11)
        x = 118
        for wd in ['So', 'Then', 'We', 'The', 'Let']:
            x = chip(svg, x, y + 38, wd, 'blue', size=10.5, pad=4) + 2
        mrich(svg, 118, y + 80, '∩ R = ∅', 12.5)
        svg.text(W - 18, y + 80, pick(T('→ take over', '→ 接管'), i), cls='tx-purple', anchor='end', size=12, weight=700)
        y += 118
        svg.text(18, y, pick(T('Concluding trigger', '收尾触发'), i), cls='t-strong', size=12)
        svg.text(18, y + 16, pick(T('my addition, in the verify step', '我在验证步中实现'), i), cls='t-faint', size=10.5)
        chip(svg, 18, y + 26, '### ✅ Final Answer', 'green', solid=True, size=11)
        svg.text(18, y + 66, pick(T('while the student keeps reasoning', '而学生还在往下写'), i), cls='t-muted', size=11)
        svg.text(W - 18, y + 66, pick(T('→ take over', '→ 接管'), i), cls='tx-purple', anchor='end', size=12, weight=700)
    per_lang(svg, trig)
    cy = 636
    panel(svg, 6, cy, W - 12, 228, 'blue', T('Training on the relayed answer', '在接力回答上训练'), 3, size=12.5)
    _training_box(svg, 16, cy + 38, W - 32, compact=True)
    return svg


# ============================================================================ StepCredit-RL framework
def _rollout_group(svg, gx, gy, gw, compact=False):
    rows = [(['s₀', 's₁', 's₂', 's₃', 's₄'], True), (['s₀', 's₅', 's₁', 's₂', 's₆'], False), (['s₀', 's₁', 's₂', 's₇'], False)]
    if compact:
        rows = [(r[:4], ok) for r, ok in rows]
    ys = [gy + 54, gy + 96, gy + 138]
    pos2 = []
    step = 60 if compact else 64
    for r, (states, ok) in enumerate(rows):
        y = ys[r]
        mrich(svg, gx + 24, y + 4.5, f'τ_{r + 1}', 13, 'middle')
        x = gx + 62
        for c, s in enumerate(states):
            anchor = s == 's₂'
            _state(svg, x, y, s, 'purple' if anchor else 'gray')
            if anchor:
                pos2.append((x, y))
            if c < len(states) - 1:
                arrow(svg, x + 17, y, x + step - 17, y)
            x += step
        tone, mark = ('green', 'check') if ok else ('red', 'cross')
        svg.rect(x - 22, y - 12, 72, 24, f'pn-{tone}', rx=12)
        icon(svg, mark, x - 8, y, 14, tone)
        mrich(svg, x + 22, y + 4.5, 'R = 1' if ok else 'R = 0', 12, 'middle', f'tx-{tone}')
    for (xa, ya), (xb, yb) in zip(pos2, pos2[1:]):
        svg.path(f'M{xa:.1f},{ya + 12:.1f} C{xa:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{yb - 12:.1f}', 'line l4', 'stroke-dasharray="4 3" stroke-width="1.4"')
    mrich(svg, gx + 24, ys[-1] + 34, '⋮', 14, 'middle')
    return ys


def _bar_pm(svg, x0, y, w, sign, pos_cls='s1'):
    if sign > 0:
        svg.path(hbar(x0, y - 7, x0 + w, 14, 4), pos_cls)
    else:
        svg.path(f'M{x0:.1f},{y - 7:.1f} H{x0 - w + 4:.1f} A4,4 0 0 0 {x0 - w:.1f},{y - 3:.1f} V{y + 3:.1f} A4,4 0 0 0 {x0 - w + 4:.1f},{y + 7:.1f} H{x0:.1f} Z', 's2')
    svg.line(x0, y - 11, x0, y + 11, 'axis')


def _agent_panel(svg, x, y, w, h):
    panel(svg, x, y, w, h, 'blue', T('Multi-turn agent loop', '多轮 Agent 交互'), 1)
    _model_box(svg, x + 14, y + 38, w - 28, 54, 'blue', 'robot', T('LLM agent', 'LLM Agent'), 'Qwen3-4B')
    _model_box(svg, x + 14, y + 226, w - 28, 54, 'yellow', 'house', T('Environment', '环境'), T('ALFWorld household', 'ALFWorld 家务任务'))
    arrow(svg, x + 52, y + 94, x + 52, y + 223)
    arrow(svg, x + w - 52, y + 223, x + w - 52, y + 94)
    svg.text(x + 46, y + 128, T('tool call', '工具调用'), cls='t-faint', anchor='end', size=10.5)
    chip(svg, x + 18, y + 138, 'go to fridge 1', 'gray', size=10.5, pad=5)
    svg.text(x + w - 46, y + 128, T('observation', '观察'), cls='t-faint', size=10.5)
    chip(svg, x + w - 136, y + 176, '“You arrive at fridge 1.”', 'gray', size=10, pad=4)

    def notes(i):
        yy = y + 316
        for line in pick((['One LLM call + one tool call', '= one training sample;', 'the context does not grow.', '',
                           'Reward only at the end:', 'R = 1 if the task succeeds', 'within 20 steps, else 0.'],
                          ['一次 LLM 调用 + 一次工具调用', '= 一条训练样本，', '上下文不随步数增长。', '',
                           '只在最后给奖励：', '20 步内完成任务 R = 1，', '否则 R = 0。']), i):
            if line:
                svg.text(x + 16, yy, line, cls='t-muted', size=11.5)
            yy += 17
    per_lang(svg, notes)


def scr_framework_aes(W, hand=True):
    """Round-1 layout, polished: observation moved off the arrow, one diverging pair (blue + / orange −) in both
    advantage panels, real subscripts."""
    if W < 500:
        return R1._scr_framework_narrow(W, hand)
    H = 478
    svg = Svg(W, H, 'StepCredit-RL: multi-turn agent loop, a group of rollouts, episode-level and step-level advantages', hand=hand)
    _agent_panel(svg, 10, 10, 230, H - 20)
    gx, gy, gw, gh = 252, 10, W - 262, 214
    panel(svg, gx, gy, gw, gh, 'gray', T('A group of N = 8 rollouts of the same task', '同一任务的一组 N = 8 条 rollout'), 2)
    _rollout_group(svg, gx, gy, gw)
    svg.text(gx + 46, gy + 200, T('s₂ appears in τ1, τ2 and τ3 (same observation hash) → one step-level group',
                                  's₂ 出现在 τ1、τ2、τ3 中（环境观察的哈希相同）→ 组成一个步级分组'), cls='tx-purple', size=11.5)
    ex, ey, ew, eh = 252, 236, 300, H - 246
    panel(svg, ex, ey, ew, eh, 'blue', T('Episode level', '整局'), 3)
    for r, (val, sign) in enumerate([(1, 1), (0, -1), (0, -1)]):
        y = ey + 62 + r * 30
        mrich(svg, ex + 26, y + 4, f'τ_{r + 1}', 12.5, 'middle')
        mrich(svg, ex + 70, y + 4, f'R = {val}', 12, 'middle')
        _bar_pm(svg, ex + 170, y, 46 if sign > 0 else 28, sign)
    svg.rect(ex + 16, ey + eh - 58, ew - 32, 40, 'box', rx=8)
    mrich(svg, ex + ew / 2, ey + eh - 33, 'A^E(τ_i) = (R_i − mean R) / std R', 13, 'middle')
    sx, sy, sw, sh = 564, 236, W - 574, H - 246
    panel(svg, sx, sy, sw, sh, 'purple', T('Step level: same-state group', '步级：同状态分组'), 4)
    for r, (act, g, sign) in enumerate([('go to fridge 1', 1, 1), ('go to cabinet 1', 0, -1), ('go to sinkbasin 1', 0, -1)]):
        y = sy + 62 + r * 30
        _state(svg, sx + 30, y, 's₂', 'purple', 28, 22)
        chip(svg, sx + 52, y - 10, act, 'gray', size=10.5, pad=5)
        mrich(svg, sx + 198, y + 4, f'G = {g}', 12, 'middle')
        _bar_pm(svg, sx + 254, y, 36 if sign > 0 else 22, sign)
    svg.text(sx + sw / 2, sy + eh - 68, T('no critic · no extra rollouts', '无需 critic · 无需额外 rollout'), cls='t-faint', anchor='middle', size=11)
    svg.rect(sx + 14, sy + eh - 58, sw - 28, 40, 'box', rx=8)
    mrich(svg, sx + sw / 2, sy + eh - 33, 'A_t = A^E(τ) + A^S(s_t, a_t)', 13.5, 'middle')
    return svg


def scr_framework_inno(W, hand=True):
    """Composed as a loop: the agent loop produces a group of rollouts (2); the two advantages (3, 4) are added and
    the update goes back to the agent (5)."""
    if W < 500:
        return R1._scr_framework_narrow(W, hand)
    H = 486
    svg = Svg(W, H, 'StepCredit-RL as a loop: rollouts, episode-level and step-level advantages, update back to the agent', hand=hand)
    _agent_panel(svg, 10, 10, 230, H - 20)
    gx, gy, gw, gh = 274, 10, W - 284, 200
    panel(svg, gx, gy, gw, gh, 'gray', T('A group of N = 8 rollouts of the same task', '同一任务的一组 N = 8 条 rollout'), 2)
    _rollout_group(svg, gx, gy, gw)
    svg.text(gx + gw - 16, gy + 24, T('s₂ = same observation hash', 's₂：环境观察的哈希相同'), cls='tx-purple', anchor='end', size=11, weight=600)
    arrow(svg, 242, 110, gx - 4, 110, 'line l1', 7)
    svg.text(258, 100, T('8 ×', '8 ×'), cls='tx-blue', anchor='middle', size=11, weight=700)
    ex, ey, ew = 274, 222, 300
    eh = 168
    panel(svg, ex, ey, ew, eh, 'blue', T('Episode level', '整局'), 3)
    for r, (val, sign) in enumerate([(1, 1), (0, -1), (0, -1)]):
        y = ey + 56 + r * 26
        mrich(svg, ex + 26, y + 4, f'τ_{r + 1}', 12.5, 'middle')
        mrich(svg, ex + 70, y + 4, f'R = {val}', 12, 'middle')
        _bar_pm(svg, ex + 170, y, 46 if sign > 0 else 28, sign)
    mrich(svg, ex + ew / 2, ey + eh - 14, 'A^E(τ_i) = (R_i − mean R) / std R', 12.5, 'middle')
    sx, sw = 586, W - 596
    panel(svg, sx, ey, sw, eh, 'purple', T('Step level: same-state group', '步级：同状态分组'), 4)
    for r, (act, g, sign) in enumerate([('go to fridge 1', 1, 1), ('go to cabinet 1', 0, -1), ('go to sinkbasin 1', 0, -1)]):
        y = ey + 56 + r * 26
        _state(svg, sx + 28, y, 's₂', 'purple', 26, 20)
        chip(svg, sx + 48, y - 10, act, 'gray', size=10, pad=4)
        mrich(svg, sx + 186, y + 4, f'G = {g}', 11.5, 'middle')
        _bar_pm(svg, sx + 238, y, 30 if sign > 0 else 18, sign)
    mrich(svg, sx + sw / 2, ey + eh - 14, 'A^S(s, a) = (G − mean G) / std G', 12.5, 'middle')
    uy = ey + eh + 12
    panel(svg, 274, uy, W - 284, H - uy - 10, 'green', T('Combine and update', '相加并更新'), 5)
    mrich(svg, 274 + (W - 284) / 2, uy + 50, 'A_t = A^E(τ) + A^S(s_t, a_t)', 14.5, 'middle')
    svg.text(274 + (W - 284) / 2, uy + 70, T('no critic · no extra rollouts · policy-gradient update', '无需 critic · 无需额外 rollout · 策略梯度更新'), cls='t-muted', anchor='middle', size=11)
    svg.path(f'M274,{uy + 42:.1f} H250', 'line l5', 'stroke-width="1.6"')
    arrow(svg, 250, uy + 42, 250, 64, 'line l5', 7)
    svg.text(256, (uy + 42 + 64) / 2 + 60, T('update', '更新'), cls='tx-green', size=10.5, weight=700, extra=f'transform="rotate(-90 256 {(uy + 42 + 64) / 2 + 60:.1f})"')
    return svg


# ============================================================================ pipelines
def opd_pipeline_aes(W):
    """Round-1 cards, polished: equal heights, aligned icons and numbers, the gain over the previous stage under each score."""
    if W < 500:
        return R1.opd_pipeline_aes(W)
    items = [(T('Teacher solutions', '老师解答'), T('14,116 problems', '14,116 道题')),
             (T('Rejection sampling', '拒绝采样'), T('11,158 kept (79%)', '保留 11,158 条（79%）')),
             (T('SFT'), T('1 epoch', '1 轮')),
             (T('Scaffold-OPD'), T('40 steps', '40 步')),
             (T('GRPO on failures', '错题回流 GRPO'), T('2,212 problems', '2,212 道题'))]
    p = OPD['pipeline_avg4']
    vals = [p['base'], None, p['sft'], p['takeover_40'], p['grpo_30']]
    w, gap, h = 130, 14, 84
    x0 = (W - (5 * w + 4 * gap)) / 2
    svg = Svg(W, 160, 'Scaffold-OPD pipeline with the 4-benchmark average after each stage')
    prev = None
    for i, ((title, detail), tone, kind) in enumerate(zip(items, R1.STAGE_TONES_OPD, R1.STAGE_ICONS_OPD)):
        bx = x0 + i * (w + gap)
        svg.rect(bx, 8, w, h, f'pn-{tone}', rx=10)
        icon(svg, kind, bx + 21, 30, 20, tone)
        svg.text(bx + w - 12, 34, f'0{i + 1}', cls=f'tx-{tone}', anchor='end', size=11, weight=700)
        svg.text(bx + 12, 62, title, cls='t-strong', size=12.5)
        svg.text(bx + 12, 79, detail, cls='t-muted', size=10.5)
        if i:
            arrow(svg, bx - gap + 2, 8 + h / 2, bx - 2, 8 + h / 2)
        v = vals[i]
        if v is not None:
            key = i == 3
            lab = T(f'base {v:.1f}', f'基座 {v:.1f}') if i == 0 else f'{v:.1f}'
            V2.score_pill(svg, bx + w / 2, 106, lab, 'box-fill' if key else 'box-soft', 't-on' if key else ('t-muted' if i == 0 else 't-strong'), 11.5 if i == 0 else 12.5)
            if prev is not None:
                svg.text(bx + w / 2, 146, V2.signed(v - prev), cls='tx-blue' if key else 't-muted', anchor='middle', size=11.5, weight=700 if key else None)
            prev = v
    return svg


def opd_pipeline_inno(W):
    """The pipeline drawn as a funnel of data (14,116 → 11,158 → 2,212 problems) feeding three training stages."""
    if W < 500:
        return R1.opd_pipeline_aes(W)
    p = OPD['pipeline_avg4']
    svg = Svg(W, 214, 'Scaffold-OPD pipeline: data flow and the 4-benchmark average after each training stage')
    # data lane
    svg.text(16, 30, T('data', '数据'), cls='t-faint', size=11, weight=700)
    svg.text(16, 132, T('training', '训练'), cls='t-faint', size=11, weight=700)
    d = [(84, 'green', 'cap', T('Teacher solutions', '老师解答'), T('14,116 problems', '14,116 道题')),
         (264, 'gray', 'funnel', T('Rejection sampling', '拒绝采样'), T('11,158 kept (79%)', '保留 11,158 条（79%）')),
         (622, 'orange', 'doc', T('Failures', '错题'), T('2,212 problems', '2,212 道题'))]
    for x, tone, kind, title, sub in d:
        svg.rect(x, 12, 156, 52, f'pn-{tone}', rx=9)
        icon(svg, kind, x + 20, 38, 18, tone)
        svg.text(x + 36, 34, title, cls='t-strong', size=12)
        svg.text(x + 36, 51, sub, cls='t-muted', size=10.5)
    arrow(svg, 240, 38, 262, 38)
    t = [(264, 'yellow', 'book', T('SFT', 'SFT'), T('1 epoch', '1 轮'), p['sft']),
         (444, 'blue', 'relay', T('Scaffold-OPD', 'Scaffold-OPD'), T('40 steps', '40 步'), p['takeover_40']),
         (622, 'orange', 'target', T('GRPO on failures', '错题回流 GRPO'), T('30 steps', '30 步'), p['grpo_30'])]
    for j, (x, tone, kind, title, sub, v) in enumerate(t):
        svg.rect(x, 104, 156, 56, f'pn-{tone}', rx=9)
        icon(svg, kind, x + 20, 132, 18, tone)
        svg.text(x + 36, 128, title, cls='t-strong', size=12)
        svg.text(x + 36, 145, sub, cls='t-muted', size=10.5)
        key = j == 1
        V2.score_pill(svg, x + 78, 172, f'{v:.1f}', 'box-fill' if key else 'box-soft', 't-on' if key else 't-strong', 12.5)
        if j:
            arrow(svg, x - 22, 132, x - 2, 132)
    arrow(svg, 342, 66, 342, 101)
    arrow(svg, 522, 132, 532, 132)
    arrow(svg, 700, 101, 700, 68)
    svg.path('M600,132 C610,132 612,80 622,64', 'line l2', 'fill="none" stroke-dasharray="3 3" stroke-width="1.4"')
    svg.text(84, 118, T('base model', '基座'), cls='t-muted', size=11)
    V2.score_pill(svg, 130, 138, '25.4', 'box-soft', 't-muted', 12)
    arrow(svg, 176, 149, 262, 132)
    svg.text(W - 16, 206, T('scores: 4-benchmark average after each stage', '分数：每段之后的 4 项平均'), cls='t-faint', anchor='end', size=11)
    return svg


def scr_pipeline_aes(W):
    """Round-1 cards, polished; the RL card marks where RL saturates (step 20) on its bars."""
    if W < 500:
        return V2.scr_pipeline(W)
    stages = [(T('Base model', '基座模型'), T('before training', '训练前'), (7.1, 2.2), 'gray', 'robot'),
              (T('Expert SFT', '专家 SFT'), T('22,810 examples · 1 epoch', '22,810 条样本 · 1 轮'), (67.1, 67.2), 'yellow', 'book'),
              (T('Multi-turn RL', '多轮 RL'), T('StepCredit-RL · 100 steps', 'StepCredit-RL · 100 步'), (98.6, 94.0), 'blue', 'target'),
              (T('Paired eval', '配对评测'), T('per-task results', '记录每个任务的结果'), None, 'green', 'scale')]
    w, gap, h, y0 = 166, 16, 108, 34
    x = (W - (4 * w + 3 * gap)) / 2
    svg = Svg(W, y0 + h + 10, 'StepCredit-RL pipeline with ALFWorld success (seen and unseen) after each stage')
    V2.chip_legend(svg, x, 18, [('s1', 'seen'), ('pn-blue', 'unseen')], size=11)
    for i, (title, detail, sc, tone, kind) in enumerate(stages):
        bx = x + i * (w + gap)
        svg.rect(bx, y0, w, h, f'pn-{tone}', rx=10)
        icon(svg, kind, bx + 21, y0 + 23, 18, tone)
        svg.text(bx + 38, y0 + 28, title, cls='t-strong', size=12.5)
        svg.text(bx + 12, y0 + 50, detail, cls='t-muted', size=10.5)
        if sc:
            tw = w - 24 - 36
            for j, (v, cls_, nm) in enumerate([(sc[0], 's1', 'seen'), (sc[1], 'pn-blue', 'unseen')]):
                yb = y0 + 66 + j * 18
                svg.rect(bx + 12, yb, tw, 8, 'band', rx=4)
                svg.mark(f'{title[0]} · {nm}: {v:.1f}%', f'<path class="bar {cls_}" d="{hbar(bx + 12, yb, bx + 12 + tw * v / 100, 8, 4)}"/>')
                svg.text(bx + w - 12, yb + 8, f'{v:.1f}', cls='t-strong' if i == 2 else '', anchor='end', size=11)
            if i == 2:
                svg.text(bx + 12, y0 + h - 6, T('98.6 / 91.0 already at step 20', '第 20 步已达 98.6 / 91.0'), cls='t-faint', size=10)
        else:
            svg.text(bx + 12, y0 + 74, T('exact McNemar test', '精确 McNemar 检验'), size=11.5)
            svg.text(bx + 12, y0 + 92, T('two runs, same tasks', '两次运行、同一批任务'), cls='t-faint', size=11)
        if i:
            arrow(svg, bx - gap + 2, y0 + h / 2, bx - 2, y0 + h / 2)
    return svg


def scr_pipeline_inno(W):
    """Cards on a time axis: wall-clock hours of each stage (data + SFT ≈ 2 h, RL to step 20 ≈ 3.5 h, to step 100 ≈ 14 h)."""
    if W < 500:
        return scr_pipeline_aes(W)
    from figlib import ALF
    rl = {int(r['step']): float(r['hours']) for r in ALF if r['run'] == 'sft_gigpo'}
    svg = Svg(W, 196, 'StepCredit-RL pipeline on a time axis, with ALFWorld success at each milestone')
    x0, x1 = 40, W - 30
    tmax = 2.1 + rl[100] + 0.5
    sx = lambda h: x0 + h / tmax * (x1 - x0)
    y = 120
    svg.line(x0, y, x1, y, 'axis')
    for h in range(0, int(tmax) + 1, 2):
        svg.line(sx(h), y, sx(h), y + 4, 'axis')
        svg.text(sx(h), y + 17, f'{h} h', cls='t-faint', anchor='middle', size=10.5)
    segs = [(0, 2.1, 'yellow', T('expert data + SFT ≈ 2 h', '专家数据 + SFT 约 2 小时')), (2.1, 2.1 + rl[100], 'blue', T('multi-turn RL, 100 steps', '多轮 RL，100 步'))]
    for a, b, tone, lab in segs:
        svg.rect(sx(a) + 1, y - 26, sx(b) - sx(a) - 2, 22, f'pn-{tone}', rx=6)
        svg.text(sx(a) + 8, y - 11, lab, cls='t-strong', size=11)
    marks = [(0, T('base', '基座'), '7.1 / 2.2', 't-muted'), (2.1, T('after SFT', 'SFT 后'), '67.1 / 67.2', ''),
             (2.1 + rl[20], T('RL 20 steps', 'RL 20 步'), '98.6 / 91.0', 't-strong'), (2.1 + rl[100], T('RL 100 steps', 'RL 100 步'), '98.6 / 94.0', 't-strong')]
    for k, (h, lab, val, cls) in enumerate(marks):
        yy = 34 if k % 2 == 0 else 62
        svg.line(sx(h), yy + 8, sx(h), y - 28, 'leader', 'stroke-dasharray="2 3"')
        svg.circle(sx(h), y - 15, 4, 'dot s1')
        svg.text(sx(h), yy - 6, lab, cls='t-muted', anchor='middle' if k else 'start', size=11)
        svg.text(sx(h), yy + 8, val, cls=cls, anchor='middle' if k else 'start', size=12.5)
    svg.text(x0, 176, T('ALFWorld success seen / unseen at each milestone; GRPO from the base model needs 38 h for 200 steps (70.7 / 71.6)',
                        '各节点的 ALFWorld 成功率（seen / unseen）；从基座训练的 GRPO 200 步需 38 小时（70.7 / 71.6）'), cls='t-faint', size=11)
    return svg


# ============================================================================ cards
def card_opd_aes(W=380):
    """Round-1 miniature, polished: fits the card, smaller model boxes, the second takeover fully visible."""
    svg = Svg(W, 124, 'Miniature: the teacher takes over the student’s answer twice, then the answer ends', hand=True)
    _model_box(svg, 8, 12, 100, 42, 'blue', 'robot', T('Student', '学生'), '1.7B')
    _model_box(svg, 8, 70, 100, 42, 'green', 'cap', T('Teacher', '老师'), '4B')
    k = _lanes(svg, 124, 33, 91, 4, 4, 3, 2, size=10, gap=3, seg_gap=12)
    svg.text(k['t1s'], 91 + 22, '“Wait, …”', cls='tx-green', size=11, weight=700)
    svg.text(k['t2s'] - 2, 91 + 22, '“But …”', cls='tx-green', size=11, weight=700)
    return svg


def card_opd_inno(W=380):
    """One lane: the answer as a single line of tokens, coloured by who wrote it, under the two models."""
    svg = Svg(W, 124, 'Miniature: one answer, written mostly by the student with two short passages by the teacher', hand=True)
    _model_box(svg, 14, 10, 166, 40, 'blue', 'robot', T('Student · 1.7B', '学生 · 1.7B'), T('writes', '写'))
    _model_box(svg, 200, 10, 166, 40, 'green', 'cap', T('Teacher · 4B', '老师 · 4B'), T('steps in', '接管'))
    x, y = 14, 72
    seq = [('blue', 6), ('purple', 1), ('green', 4), ('blue', 6), ('purple', 1), ('green', 2), ('end', 1)]
    for tone, n in seq:
        for _ in range(n):
            svg.rect(x, y, 11, 11, 'ink' if tone == 'end' else f'pn-{tone}', rx=2.5)
            x += 14
    svg.text(14 + 7 * 14, y + 34, '“Wait, …”', cls='tx-green', size=11, weight=700)
    svg.text(14 + 18 * 14, y + 34, '“But …”', cls='tx-green', size=11, weight=700)
    return svg


def card_scr_aes(W=380):
    """Round-1 miniature, polished: aligned rows, the shared state labelled once, outcome chips aligned."""
    svg = Svg(W, 124, 'Miniature: three rollouts reach the same state s₂; their steps from s₂ are compared', hand=True)
    rows = [(['s₀', 's₁', 's₂', 's₃'], True), (['s₀', 's₅', 's₁', 's₂'], False), (['s₀', 's₁', 's₂', 's₇'], False)]
    pos = []
    for r, (states, ok) in enumerate(rows):
        y = 20 + r * 38
        mrich(svg, 20, y + 4.5, f'τ_{r + 1}', 12.5, 'middle')
        x = 54
        for c, s in enumerate(states):
            a = s == 's₂'
            _state(svg, x, y, s, 'purple' if a else 'gray', 30, 22)
            if a:
                pos.append((x, y))
            if c < len(states) - 1:
                arrow(svg, x + 17, y, x + 41, y)
            x += 60
        tone, mark = ('green', 'check') if ok else ('red', 'cross')
        svg.rect(304, y - 11, 52, 22, f'pn-{tone}', rx=11)
        icon(svg, mark, 330, y, 13, tone)
    for (xa, ya), (xb, yb) in zip(pos, pos[1:]):
        svg.path(f'M{xa:.1f},{ya + 11:.1f} C{xa:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{yb - 11:.1f}', 'line l4', 'stroke-dasharray="4 3" stroke-width="1.4"')
    return svg


def card_scr_inno(W=380):
    """The same three rollouts, plus the credit each step from s₂ receives (+ for the success, − for the failures)."""
    svg = card_scr_aes(W)
    xs = {0: 54 + 2 * 60, 1: 54 + 3 * 60, 2: 54 + 2 * 60}
    for r, sign in [(0, '+'), (1, '−'), (2, '−')]:
        x, y = xs[r] + 30, 20 + r * 38 - 12
        cls = 's1' if sign == '+' else 's2'
        svg.rect(x - 8, y - 6, 16, 12, cls, rx=6)
        svg.text(x, y + 4, sign, cls='t-on', anchor='middle', size=11)
    return svg


AES = {'card-opd': card_opd_aes, 'card-scr': card_scr_aes, 'opd-pipeline': opd_pipeline_aes, 'opd-takeover': opd_framework_aes,
       'scr-pipeline': scr_pipeline_aes, 'scr-steplevel': scr_framework_aes}
INNO = {'card-opd': card_opd_inno, 'card-scr': card_scr_inno, 'opd-pipeline': opd_pipeline_inno, 'opd-takeover': opd_framework_inno,
        'scr-pipeline': scr_pipeline_inno, 'scr-steplevel': scr_framework_inno}
