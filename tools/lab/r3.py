"""Round 3 (2026-11-16): the last round. Each figure starts from the version kept in round 2; the picks here are the
finals (tools/figures.py). Cards are redrawn for the home page's project rows (thumbnail about 270 px wide)."""
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE / 'v2'))
sys.path.insert(0, str(HERE))

from figlib import ALF, HPQ, OPD, PAIRED, Svg, T, arrow, chevron, hbar, hit_points, moving_avg, polyline, run, scale, width_of  # noqa: E402
from figkit import badge, chip, curve, icon, mrich, panel, tokens, wedge_bracket  # noqa: E402
import figures_v2 as V2  # noqa: E402
import r1_charts as R1C  # noqa: E402
import r1_diagrams as R1D  # noqa: E402
import r2_charts as R2C  # noqa: E402
import r2_diagrams as R2D  # noqa: E402

pick, per_lang, legend, chip_legend, gap_wash, signed = V2.pick, V2.per_lang, V2.legend, V2.chip_legend, V2.gap_wash, V2.signed
axes, ptitle, lines, end_label = R1C.axes, R1C.ptitle, R1C.lines, R1C.end_label
_model_box, _state, legend_tokens = R1D._model_box, R1D._state, R1D.legend_tokens
CARD_W, CARD_H = 300, 190


# ============================================================================ cards (thumbnails)
def _card_lanes(svg, y_s, y_t, x0):
    k = R2D._lanes(svg, x0, y_s, y_t, 3, 3, 2, 1, size=11, gap=3, seg_gap=12)
    svg.text(k['t1s'] - 2, y_t + 24, '“Wait, …”', cls='tx-green', size=13, weight=700)
    svg.text(k['t2s'] - 4, y_t + 24, '“But …”', cls='tx-green', size=13, weight=700)
    return k


def card_opd_aes(W=CARD_W):
    """R2 miniature redrawn for the thumbnail: two model chips, the two lanes, two takeovers, larger type."""
    svg = Svg(W, CARD_H, 'Miniature: the teacher takes over the student’s answer twice, then the answer ends', hand=True)
    for y, tone, kind, name in [(30, 'blue', 'robot', T('Student', '学生')), (112, 'green', 'cap', T('Teacher', '老师'))]:
        svg.rect(6, y - 18, 86, 36, f'pn-{tone}', rx=8)
        icon(svg, kind, 24, y, 18, tone)
        svg.text(38, y + 5, name, cls=f'tx-{tone}', size=13, weight=700)
    _card_lanes(svg, 30, 112, 100)
    svg.text(W / 2, CARD_H - 10, T('teacher steps in, then hands back', '老师接管一小段，再交还'), cls='t-muted', anchor='middle', size=12.5)
    return svg


def card_opd_inno(W=CARD_W):
    """A miniature of the three-part method figure: (1) relay lanes, (2) the rule, (3) the loss."""
    svg = Svg(W, CARD_H, 'Miniature of the method figure: relay rollout, takeover rule, token-level loss', hand=True)
    svg.rect(4, 4, W - 8, 92, 'pn-gray', rx=9)
    badge(svg, 18, 18, 1, 'gray', 7)
    k = R2D._lanes(svg, 36, 34, 74, 4, 4, 3, 2, size=10, gap=3, seg_gap=11)
    svg.rect(4, 102, 146, 84, 'pn-purple', rx=9)
    badge(svg, 18, 116, 2, 'purple', 7)
    chip(svg, 14, 128, 'Wait', 'green', solid=True, size=12)
    mrich(svg, 68, 143, '∉ top-5', 12.5)
    svg.text(14, 172, T('→ take over', '→ 接管'), cls='tx-purple', size=12.5, weight=700)
    svg.rect(156, 102, W - 160, 84, 'pn-blue', rx=9)
    badge(svg, 170, 116, 3, 'blue', 7)
    mrich(svg, 156 + (W - 160) / 2 + 6, 148, 'log π_θ − log π_T', 13, 'middle')
    svg.text(156 + (W - 160) / 2 + 6, 172, T('every token', '每个 token'), cls='t-muted', anchor='middle', size=12)
    return svg


def _card_rows(svg, x0, step, y0, pitch, credit=True):
    rows = [(['s₀', 's₁', 's₂', 's₃'], True), (['s₀', 's₅', 's₁', 's₂'], False), (['s₀', 's₁', 's₂', 's₇'], False)]
    pos = []
    for r, (states, ok) in enumerate(rows):
        y = y0 + r * pitch
        mrich(svg, 14, y + 5, f'τ_{r + 1}', 13, 'middle')
        x = x0
        for c, s in enumerate(states):
            a = s == 's₂'
            _state(svg, x, y, s, 'purple' if a else 'gray', 32, 24)
            if a:
                pos.append((x, y))
            if c < len(states) - 1:
                arrow(svg, x + 17, y, x + step - 17, y)
            x += step
        tone, mark = ('green', 'check') if ok else ('red', 'cross')
        svg.rect(W_OUT - 40, y - 12, 36, 24, f'pn-{tone}', rx=12)
        icon(svg, mark, W_OUT - 22, y, 13, tone)
    for (xa, ya), (xb, yb) in zip(pos, pos[1:]):
        svg.path(f'M{xa:.1f},{ya + 12:.1f} C{xa:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{yb - 12:.1f}', 'line l4', 'stroke-dasharray="4 3" stroke-width="1.5"')
    if credit:
        for (x, y), sign in zip(pos, ['+', '−', '−']):
            cls = 's1' if sign == '+' else 's2'
            svg.rect(x + 14, y - 22, 16, 13, cls, rx=6.5)
            svg.text(x + 22, y - 12, sign, cls='t-on', anchor='middle', size=11)
    return pos


W_OUT = CARD_W


def card_scr_aes(W=CARD_W):
    """R2 miniature redrawn for the thumbnail: three rollouts, the shared state s₂, + / − credit on its steps."""
    svg = Svg(W, CARD_H, 'Miniature: three rollouts reach the same state s₂; the steps taken from it get opposite credit', hand=True)
    _card_rows(svg, 46, 56, 32, 48)
    svg.text(W / 2, CARD_H - 10, T('same state → compare the next steps', '同一状态 → 比较之后的各步'), cls='t-muted', anchor='middle', size=12.5)
    return svg


def card_scr_inno(W=CARD_W):
    """The three rollouts plus the formula the figure ends with."""
    svg = Svg(W, CARD_H, 'Miniature: three rollouts reach the same state s₂; the advantage is the sum of episode and step terms', hand=True)
    _card_rows(svg, 46, 56, 28, 44)
    svg.rect(6, 150, W - 12, 34, 'pn-green', rx=8)
    mrich(svg, W / 2, 172, 'A = A^E + A^S', 14, 'middle')
    return svg


# ============================================================================ Scaffold-OPD framework (from R2 aes)
def opd_framework_aes(W, hand=True, loop=False):
    """R2 polish: example text under the teacher lane (no collisions with the curves), right edge respected."""
    if W < 500:
        return R2D._opd_narrow(W, hand)
    H = 514
    svg = Svg(W, H, 'Scaffold-OPD: relay rollout inside speculative decoding, the takeover triggers, and the token-level training signal', hand=hand)
    legend_tokens(svg, 16, 18, [('blue', T('student token', '学生 token')), ('green', T('teacher token', '老师 token')),
                                ('purple', T('takeover point', '接管点')), ('end', T('answer ends', '回答结束'))])
    panel(svg, 10, 30, W - 20, 232, 'gray', T('Relay rollout inside vLLM speculative decoding', 'vLLM 投机解码中的接力生成'), 1)
    _model_box(svg, 26, 62, 178, 52, 'blue', 'robot', T('Student', '学生'), T('Qwen3-1.7B · drafts', 'Qwen3-1.7B · 写草稿'))
    _model_box(svg, 26, 150, 178, 52, 'green', 'cap', T('Teacher', '老师'), T('Qwen3-4B · verifies', 'Qwen3-4B · 验证'))
    arrow(svg, 96, 116, 96, 147)
    arrow(svg, 134, 147, 134, 117)
    svg.text(89, 136, T('draft', '草稿'), cls='t-faint', anchor='end', size=10.5)
    svg.text(141, 136, T('accept / take over', '接受 / 接管'), cls='t-faint', size=10.5)
    ys, yt = 88, 176
    svg.line(226, ys, W - 26, ys, 'grid', 'stroke-dasharray="2 4"')
    svg.line(226, yt, W - 26, yt, 'grid', 'stroke-dasharray="2 4"')
    k = R2D._lanes(svg, 234, ys, yt, 12, 8, 10, 5, size=12, gap=3)
    badge(svg, (k['s1'] + k['t1s']) / 2 + 4, (ys + yt) / 2, 1, 'purple', 7.5)
    badge(svg, (k['s2e'] + k['t2s']) / 2 + 4, (ys + yt) / 2, 2, 'purple', 7.5)
    svg.text(234, ys - 14, T('“… so the answer is 47.”', '“……所以答案是 47。”'), cls='t-muted', size=11.5)
    svg.text(k['s2s'], ys - 14, T('“… so the answer is 52.”', '“……所以答案是 52。”'), cls='t-muted', size=11.5)
    svg.text(k['t1s'], yt + 26, '“Wait, let me check step 2 …”', cls='tx-green', size=11.5, weight=700)
    svg.text(W - 28, yt + 26, '“But the question asks …”', cls='tx-green', anchor='end', size=11.5, weight=700)
    wedge_bracket(svg, k['t1s'], k['t1e'], yt + 38, 'leader', 5)
    svg.text((k['t1s'] + k['t1e']) / 2, yt + 55, T('≤ 3 paragraphs (≤ 256 tokens), then hand back', '最多写 3 段（≤ 256 token）后交还'), cls='t-muted', anchor='middle', size=11)
    svg.text(W - 28, yt + 55, T('≤ 2 takeovers; the answer then ends', '最多接管 2 次，之后回答结束'), cls='t-muted', anchor='end', size=11)
    bx, by, bw, bh = 10, 274, 536, 230
    panel(svg, bx, by, bw, bh, 'purple', T('When does the teacher take over?', '老师何时接管？'), 2)
    per_lang(svg, lambda i: (R2D._reflection_rule(svg, bx + 18, by + 52, i, bx + bw - 16), R2D._conclude_rule(svg, bx + 18, by + 152, i, bx + bw - 16)))
    cx, cy, cw, ch = 556, 274, W - 566, 230
    panel(svg, cx, cy, cw, ch, 'blue', T('Training on the relayed answer', '在接力回答上训练'), 3)
    R2D._training_box(svg, cx + 14, cy + 40, cw - 28)
    if loop:
        icon(svg, 'relay', cx + cw - 26, cy + 19, 16, 'blue')
        svg.text(cx + cw - 40, cy + 23.5, T('weights back to the drafter', '新权重回到草稿模型'), cls='tx-blue', anchor='end', size=10.5, weight=700)
    return svg


def opd_framework_inno(W, hand=True):
    """As the aesthetic version, plus the on-policy loop: after each update the student's weights go back to vLLM."""
    return opd_framework_aes(W, hand, loop=True)


# ============================================================================ StepCredit-RL framework (from R2 inno)
def scr_framework_aes(W, hand=True, legend_states=False):
    """R2 loop layout, polished: a clean elbow arrow for the update, no overlapping labels, a phone layout with all five parts."""
    if W < 500:
        return _scr_narrow(W, hand)
    H = 492
    svg = Svg(W, H, 'StepCredit-RL as a loop: rollouts, episode-level and step-level advantages, update back to the agent', hand=hand)
    R2D._agent_panel(svg, 10, 10, 230, H - 20)
    gx, gy, gw, gh = 274, 10, W - 284, 204
    panel(svg, gx, gy, gw, gh, 'gray', T('A group of N = 8 rollouts of the same task', '同一任务的一组 N = 8 条 rollout'), 2)
    R2D._rollout_group(svg, gx, gy, gw)
    if legend_states:
        svg.text(gx + gw - 14, gy + 24, T('s₂: holding the mug (same observation hash)', 's₂：手里拿着杯子（环境观察的哈希相同）'), cls='tx-purple', anchor='end', size=11, weight=600)
    else:
        svg.text(gx + gw - 14, gy + 24, T('s₂ = same observation hash', 's₂：环境观察的哈希相同'), cls='tx-purple', anchor='end', size=11, weight=600)
    arrow(svg, 242, 112, gx - 4, 112, 'line l1', 7)
    ey, eh = 226, 170
    ex, ew = 274, 300
    panel(svg, ex, ey, ew, eh, 'blue', T('Episode level', '整局'), 3)
    for r, (val, sign) in enumerate([(1, 1), (0, -1), (0, -1)]):
        y = ey + 56 + r * 26
        mrich(svg, ex + 26, y + 4, f'τ_{r + 1}', 12.5, 'middle')
        mrich(svg, ex + 70, y + 4, f'R = {val}', 12, 'middle')
        R2D._bar_pm(svg, ex + 170, y, 46 if sign > 0 else 28, sign)
    mrich(svg, ex + ew / 2, ey + eh - 16, 'A^E(τ_i) = (R_i − mean R) / std R', 12.5, 'middle')
    sx, sw = 586, W - 596
    panel(svg, sx, ey, sw, eh, 'purple', T('Step level: same-state group', '步级：同状态分组'), 4)
    for r, (act, g, sign) in enumerate([('go to fridge 1', 1, 1), ('go to cabinet 1', 0, -1), ('go to sinkbasin 1', 0, -1)]):
        y = ey + 56 + r * 26
        _state(svg, sx + 28, y, 's₂', 'purple', 26, 20)
        chip(svg, sx + 48, y - 10, act, 'gray', size=10, pad=4)
        mrich(svg, sx + 186, y + 4, f'G = {g}', 11.5, 'middle')
        R2D._bar_pm(svg, sx + 238, y, 30 if sign > 0 else 18, sign)
    mrich(svg, sx + sw / 2, ey + eh - 16, 'A^S(s, a) = (G − mean G) / std G', 12.5, 'middle')
    uy = ey + eh + 12
    panel(svg, 274, uy, W - 284, H - uy - 10, 'green', T('Combine and update', '相加并更新'), 5)
    mrich(svg, 274 + (W - 284) / 2, uy + 44, 'A_t = A^E(τ) + A^S(s_t, a_t)', 14.5, 'middle')
    svg.text(274 + (W - 284) / 2, uy + 64, T('no critic · no extra rollouts · policy-gradient update', '无需 critic · 无需额外 rollout · 策略梯度更新'), cls='t-muted', anchor='middle', size=11)
    # elbow arrow from the update panel back into the agent panel, below the rollout arrow so the two never cross
    yy, ye = uy + 36, 172
    svg.path(f'M274,{yy:.1f} H257 V{ye} H250', 'line l5', 'stroke-width="1.6" stroke-dasharray="5 3" fill="none"')
    svg.path(f'M242.5,{ye} L251.5,{ye - 4.5} L251.5,{ye + 4.5} Z', 's5')
    svg.rect(244, (yy + ye) / 2 - 9, 26, 18, 'pn-green', rx=4)
    icon(svg, 'relay', 257, (yy + ye) / 2, 13, 'green')
    return svg


def scr_framework_inno(W, hand=True):
    """As the aesthetic version, with the shared state named (holding the mug) to make the example concrete."""
    return scr_framework_aes(W, hand, legend_states=True)


def _scr_narrow(W, hand):
    """Phone layout with the same five parts as the desktop figure."""
    H = 1010
    svg = Svg(W, H, 'StepCredit-RL: agent loop, a group of rollouts, episode-level and step-level advantages, update', hand=hand)
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
        mrich(svg, 24, y + 4.5, f'τ_{r + 1}', 12.5, 'middle')
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
    panel(svg, 6, ey, W - 12, 168, 'blue', T('Episode level', '整局'), 3, size=12.5)
    for r, (val, sign) in enumerate([(1, 1), (0, -1), (0, -1)]):
        y = ey + 52 + r * 26
        mrich(svg, 26, y + 4, f'τ_{r + 1}', 12, 'middle')
        mrich(svg, 70, y + 4, f'R = {val}', 12, 'middle')
        R2D._bar_pm(svg, 190, y, 46 if sign > 0 else 28, sign)
    mrich(svg, W / 2, ey + 150, 'A^E(τ_i) = (R_i − mean R) / std R', 12, 'middle')
    sy = 604
    panel(svg, 6, sy, W - 12, 200, 'purple', T('Step level: same-state group', '步级：同状态分组'), 4, size=12.5)
    for r, (act, g, sign) in enumerate([('go to fridge 1', 1, 1), ('go to cabinet 1', 0, -1), ('go to sinkbasin 1', 0, -1)]):
        y = sy + 52 + r * 28
        _state(svg, 30, y, 's₂', 'purple', 26, 20)
        chip(svg, 50, y - 10, act, 'gray', size=10.5, pad=5)
        mrich(svg, 216, y + 4, f'G = {g}', 11.5, 'middle')
        R2D._bar_pm(svg, 292, y, 36 if sign > 0 else 22, sign)
    mrich(svg, W / 2, sy + 182, 'A^S(s, a) = (G − mean G) / std G', 12, 'middle')
    uy = 816
    panel(svg, 6, uy, W - 12, 186, 'green', T('Combine and update', '相加并更新'), 5, size=12.5)
    mrich(svg, W / 2, uy + 72, 'A_t = A^E(τ) + A^S(s_t, a_t)', 14, 'middle')
    svg.text(W / 2, uy + 100, T('no critic · no extra rollouts', '无需 critic · 无需额外 rollout'), cls='t-muted', anchor='middle', size=11)
    svg.text(W / 2, uy + 118, T('→ policy-gradient update of the agent', '→ 对 Agent 做策略梯度更新'), cls='t-muted', anchor='middle', size=11)
    return svg


# ============================================================================ pipelines
def opd_pipeline_aes(W):
    """R2 cards, polished: the scores get row labels instead of a 'base' pill under a data stage; the base score
    moves into the row label, so every pill sits under the training stage it belongs to."""
    if W < 500:
        return _opd_pipeline_narrow(W)
    items = [(T('Teacher solutions', '老师解答'), T('14,116 problems', '14,116 道题')),
             (T('Rejection sampling', '拒绝采样'), T('11,158 kept (79%)', '保留 11,158 条（79%）')),
             (T('SFT'), T('1 epoch', '1 轮')),
             (T('Scaffold-OPD'), T('40 steps', '40 步')),
             (T('GRPO on failures', '错题回流 GRPO'), T('2,212 problems', '2,212 道题'))]
    p = OPD['pipeline_avg4']
    vals = [None, None, p['sft'], p['takeover_40'], p['grpo_30']]
    w, gap, h = 130, 14, 84
    x0 = (W - (5 * w + 4 * gap)) / 2
    svg = Svg(W, 160, 'Scaffold-OPD pipeline with the 4-benchmark average after each training stage and the gain over the previous one')
    xl = x0 + 2 * (w + gap) - 14
    svg.text(xl, 110, T(f'4-benchmark average (base {p["base"]:.1f})', f'4 项平均分（基座 {p["base"]:.1f}）'), cls='t-muted', anchor='end', size=11.5)
    svg.text(xl, 150, T('gain over the previous stage', '相对上一阶段'), cls='t-faint', anchor='end', size=11)
    prev = p['base']
    for i, ((title, detail), tone, kind) in enumerate(zip(items, R1D.STAGE_TONES_OPD, R1D.STAGE_ICONS_OPD)):
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
            V2.score_pill(svg, bx + w / 2, 106, f'{v:.1f}', 'box-fill' if key else 'box-soft', 't-on' if key else 't-strong', 12.5)
            svg.text(bx + w / 2, 150, signed(v - prev), cls='tx-blue' if key else 't-muted', anchor='middle', size=11.5, weight=700 if key else None)
            prev = v
    return svg


def _opd_pipeline_narrow(W):
    """Phone layout of the aesthetic version: stacked cards; the base score in the header, a pill and the gain only on
    training stages."""
    items = [(T('Teacher solutions', '老师解答'), T('14,116 problems', '14,116 道题')),
             (T('Rejection sampling', '拒绝采样'), T('79% kept', '保留 79%')),
             (T('SFT'), T('1 epoch', '1 轮')),
             (T('Scaffold-OPD'), T('40 steps', '40 步')),
             (T('GRPO on failures', '错题回流 GRPO'), T('2,212 problems', '2,212 道题'))]
    p = OPD['pipeline_avg4']
    vals = [None, None, p['sft'], p['takeover_40'], p['grpo_30']]
    w, h, gap, top = W - 16, 52, 12, 30
    svg = Svg(W, top + 5 * h + 4 * gap + 6, 'Scaffold-OPD pipeline with the 4-benchmark average after each training stage')
    svg.text(8, 18, T(f'4-benchmark average after each training stage (base {p["base"]:.1f})', f'每个训练阶段之后的 4 项平均分（基座 {p["base"]:.1f}）'), cls='t-muted', size=11)
    prev = p['base']
    for i, ((title, detail), tone, kind) in enumerate(zip(items, R1D.STAGE_TONES_OPD, R1D.STAGE_ICONS_OPD)):
        y = top + i * (h + gap)
        svg.rect(8, y, w, h, f'pn-{tone}', rx=10)
        icon(svg, kind, 30, y + h / 2, 20, tone)
        svg.text(52, y + 22, title, cls='t-strong', size=12.5)
        svg.text(52, y + 39, detail, cls='t-muted', size=11)
        v = vals[i]
        if v is not None:
            key = i == 3
            s = f'{v:.1f}'
            pw = width_of(s, 12, 600) + 16
            px = 8 + w - 12 - pw
            svg.rect(px, y + 15, pw, 22, 'box-fill' if key else 'box-soft', rx=11)
            svg.text(px + pw / 2, y + 30, s, cls='t-on' if key else 't-strong', anchor='middle', size=12)
            svg.text(px - 8, y + 30, signed(v - prev), cls='tx-blue' if key else 't-muted', anchor='end', size=11, weight=700 if key else None)
            prev = v
        if i:
            chevron(svg, W / 2, y - gap / 2, 3.5)
    return svg


def opd_pipeline_inno(W):
    """The base model as its own starting point on the left, so no score sits under the data-only stages."""
    if W < 500:
        return R1D.opd_pipeline_aes(W)
    items = [(T('Teacher solutions', '老师解答'), T('14,116 problems', '14,116 道题')),
             (T('Rejection sampling', '拒绝采样'), T('11,158 kept (79%)', '保留 11,158 条')),
             (T('SFT'), T('1 epoch', '1 轮')),
             (T('Scaffold-OPD'), T('40 steps', '40 步')),
             (T('GRPO on failures', '错题回流 GRPO'), T('2,212 problems', '2,212 道题'))]
    p = OPD['pipeline_avg4']
    vals = [None, None, p['sft'], p['takeover_40'], p['grpo_30']]
    w, gap, h = 120, 12, 84
    x0 = W - (5 * w + 4 * gap) - 8
    svg = Svg(W, 160, 'Scaffold-OPD pipeline with the 4-benchmark average after each training stage, starting from the base model')
    svg.rect(6, 8 + h / 2 - 26, x0 - 26, 52, 'pn-gray', rx=10)
    icon(svg, 'robot', 26, 8 + h / 2 - 8, 18, 'gray')
    svg.text(42, 8 + h / 2 - 3, T('Base', '基座'), cls='t-strong', size=12.5)
    svg.text(18, 8 + h / 2 + 16, '25.4', cls='t-muted', size=12)
    arrow(svg, x0 - 18, 8 + h / 2, x0 - 3, 8 + h / 2)
    prev = p['base']
    for i, ((title, detail), tone, kind) in enumerate(zip(items, R1D.STAGE_TONES_OPD, R1D.STAGE_ICONS_OPD)):
        bx = x0 + i * (w + gap)
        svg.rect(bx, 8, w, h, f'pn-{tone}', rx=10)
        icon(svg, kind, bx + 20, 30, 19, tone)
        svg.text(bx + w - 11, 34, f'0{i + 1}', cls=f'tx-{tone}', anchor='end', size=11, weight=700)
        svg.text(bx + 11, 62, title, cls='t-strong', size=12)
        svg.text(bx + 11, 79, detail, cls='t-muted', size=10.5)
        if i:
            arrow(svg, bx - gap + 2, 8 + h / 2, bx - 2, 8 + h / 2)
        v = vals[i]
        if v is not None:
            key = i == 3
            V2.score_pill(svg, bx + w / 2, 106, f'{v:.1f}', 'box-fill' if key else 'box-soft', 't-on' if key else 't-strong', 12.5)
            svg.text(bx + w / 2, 146, signed(v - prev), cls='tx-blue' if key else 't-muted', anchor='middle', size=11.5, weight=700 if key else None)
            prev = v
    return svg


def scr_pipeline_aes(W):
    """R2 cards, polished: the legend names the unit, the RL card marks step 20 on its unseen bar (seen is already at
    98.6 there), and the evaluation card states what is compared."""
    if W < 500:
        return _scr_pipeline_narrow(W)
    stages = [(T('Base model', '基座模型'), T('before training', '训练前'), (7.1, 2.2), 'gray', 'robot'),
              (T('Expert SFT', '专家 SFT'), T('22,810 examples · 1 epoch', '22,810 条样本 · 1 轮'), (67.1, 67.2), 'yellow', 'book'),
              (T('Multi-turn RL', '多轮 RL'), T('StepCredit-RL · 100 steps', 'StepCredit-RL · 100 步'), (98.6, 94.0), 'blue', 'target'),
              (T('Paired eval', '配对评测'), T('per-task results', '逐任务记录结果'), None, 'green', 'scale')]
    w, gap, h, y0 = 166, 16, 112, 34
    x = (W - (4 * w + 3 * gap)) / 2
    svg = Svg(W, y0 + h + 10, 'StepCredit-RL pipeline with ALFWorld success (seen and unseen, %) after each stage')
    svg.text(x, 22, T('ALFWorld success, %', 'ALFWorld 成功率，%'), cls='t-muted', size=11)
    V2.chip_legend(svg, x + (118 if True else 0), 18, [('s1', 'seen'), ('pn-blue', 'unseen')], size=11)
    for i, (title, detail, sc, tone, kind) in enumerate(stages):
        bx = x + i * (w + gap)
        svg.rect(bx, y0, w, h, f'pn-{tone}', rx=10)
        icon(svg, kind, bx + 21, y0 + 23, 18, tone)
        svg.text(bx + 38, y0 + 28, title, cls='t-strong', size=12.5)
        svg.text(bx + 12, y0 + 50, detail, cls='t-muted', size=11)
        if sc:
            tw = w - 24 - 36
            for j, (v, cls_, nm) in enumerate([(sc[0], 's1', 'seen'), (sc[1], 'pn-blue', 'unseen')]):
                yb = y0 + 66 + j * 18
                svg.rect(bx + 12, yb, tw, 8, 'band', rx=4)
                svg.mark(f'{title[0]} · {nm}: {v:.1f}%', f'<path class="bar {cls_}" d="{hbar(bx + 12, yb, bx + 12 + tw * v / 100, 8, 4)}"/>')
                svg.text(bx + w - 12, yb + 8, f'{v:.1f}', cls='t-strong' if i == 2 else '', anchor='end', size=11.5)
            if i == 2:
                xm = bx + 12 + tw * 91.0 / 100
                svg.line(xm, y0 + 82, xm, y0 + 94, 'ink-line', 'stroke-width="1.6"')
                svg.text(bx + 12, y0 + h - 6, T('| step 20: 98.6 / 91.0', '| 第 20 步：98.6 / 91.0'), cls='t-faint', size=10.5)
        else:
            svg.text(bx + 12, y0 + 74, T('exact McNemar test', '精确 McNemar 检验'), size=11.5)
            svg.text(bx + 12, y0 + 92, T('two runs, same tasks', '两次运行、同一批任务'), cls='t-faint', size=11)
        if i:
            arrow(svg, bx - gap + 2, y0 + h / 2, bx - 2, y0 + h / 2)
    return svg


def _scr_pipeline_narrow(W):
    """Phone layout of the aesthetic version, with the same encoding as the desktop one (seen solid, unseen outlined)."""
    stages = [(T('Base model', '基座模型'), T('before training', '训练前'), (7.1, 2.2), 'gray', 'robot'),
              (T('Expert SFT', '专家 SFT'), T('22,810 examples · 1 epoch', '22,810 条样本 · 1 轮'), (67.1, 67.2), 'yellow', 'book'),
              (T('Multi-turn RL', '多轮 RL'), T('StepCredit-RL · 100 steps · step 20: 98.6 / 91.0', 'StepCredit-RL · 100 步 · 第 20 步：98.6 / 91.0'), (98.6, 94.0), 'blue', 'target'),
              (T('Paired eval', '配对评测'), T('per-task results', '逐任务记录结果'), None, 'green', 'scale')]
    top, h, gap = 34, 78, 10
    svg = Svg(W, top + 4 * h + 3 * gap + 6, 'StepCredit-RL pipeline with ALFWorld success (seen and unseen, %) after each stage')
    svg.text(8, 20, T('ALFWorld success, %', 'ALFWorld 成功率，%'), cls='t-muted', size=11)
    V2.chip_legend(svg, 126, 16, [('s1', 'seen'), ('pn-blue', 'unseen')], size=11)
    for i, (title, detail, sc, tone, kind) in enumerate(stages):
        y = top + i * (h + gap)
        svg.rect(8, y, W - 16, h, f'pn-{tone}', rx=10)
        icon(svg, kind, 28, y + 20, 17, tone)
        svg.text(44, y + 25, title, cls='t-strong', size=12.5)
        svg.text(20, y + 44, detail, cls='t-muted', size=11)
        if sc:
            tw = W - 80
            for j, (v, cls_, nm) in enumerate([(sc[0], 's1', 'seen'), (sc[1], 'pn-blue', 'unseen')]):
                yb = y + 54 + j * 12
                svg.rect(20, yb, tw, 7, 'band', rx=3.5)
                svg.mark(f'{title[0]} · {nm}: {v:.1f}%', f'<path class="bar {cls_}" d="{hbar(20, yb, 20 + tw * v / 100, 7, 3.5)}"/>')
                svg.text(W - 20, yb + 7, f'{v:.1f}', anchor='end', size=11, cls='t-strong' if i == 2 else '')
            if i == 2:
                xm = 20 + tw * 91.0 / 100
                svg.line(xm, y + 64, xm, y + 75, 'ink-line', 'stroke-width="1.5"')
        else:
            svg.text(20, y + 62, T('exact McNemar test · two runs, same tasks', '精确 McNemar 检验 · 两次运行、同一批任务'), size=11.5)
        if i:
            chevron(svg, W / 2, y - gap / 2, 3.5)
    return svg


def scr_pipeline_inno(W):
    """R2's time axis, cleaned: labels alternate above the track, the GRPO comparison as a ghost bar."""
    if W < 500:
        return R2D.scr_pipeline_aes(W)
    rl = {int(r['step']): float(r['hours']) for r in ALF if r['run'] == 'sft_gigpo'}
    svg = Svg(W, 214, 'StepCredit-RL pipeline on a time axis, with ALFWorld success at each milestone, and GRPO for comparison')
    x0, x1 = 40, W - 30
    tmax = 40
    sx = lambda hh: x0 + hh / tmax * (x1 - x0)
    y = 116
    svg.line(x0, y + 44, x1, y + 44, 'axis')
    for hh in range(0, 41, 10):
        svg.line(sx(hh), y + 44, sx(hh), y + 48, 'axis')
        svg.text(sx(hh), y + 62, f'{hh} h', cls='t-faint', anchor='middle', size=10.5)
    sft_end = 2.1
    svg.rect(sx(0) + 1, y - 22, sx(sft_end) - sx(0) - 1, 20, 'pn-yellow', rx=5)
    svg.rect(sx(sft_end) + 1, y - 22, sx(sft_end + rl[100]) - sx(sft_end) - 2, 20, 'pn-blue', rx=5)
    svg.text(sx(sft_end) + 8, y - 8, T('SFT → StepCredit-RL, 100 steps', 'SFT → StepCredit-RL，100 步'), cls='t-strong', size=11)
    svg.rect(sx(0) + 1, y + 10, sx(38.1) - sx(0) - 2, 20, 'pn-orange', rx=5)
    svg.text(sx(0) + 8, y + 24, T('GRPO from the base model, 200 steps', '从基座训练 GRPO，200 步'), cls='t-strong', size=11)
    marks = [(sft_end, T('after SFT', 'SFT 后'), '67.1 / 67.2', '', 40), (sft_end + rl[20], T('RL step 20', 'RL 第 20 步'), '98.6 / 91.0', 't-strong', 64),
             (sft_end + rl[100], T('RL step 100', 'RL 第 100 步'), '98.6 / 94.0', 't-strong', 40), (38.1, T('GRPO step 200', 'GRPO 第 200 步'), '70.7 / 71.6', '', 64)]
    for hh, lab, val, cls, yy in marks:
        svg.line(sx(hh), yy + 6, sx(hh), y - 24 if hh < 30 else y + 8, 'leader', 'stroke-dasharray="2 3"')
        svg.text(sx(hh), yy - 14, lab, cls='t-muted', anchor='middle', size=10.5)
        svg.text(sx(hh), yy + 1, val, cls=cls, anchor='middle', size=12)
    svg.text(x0, 206, T('ALFWorld success, seen / unseen; time on 2 × A100', 'ALFWorld 成功率（seen / unseen）；时间为 2 张 A100 上的耗时'), cls='t-faint', size=11)
    return svg


# ============================================================================ charts
def opd_methods_aes(W):
    """R2 bars, polished: the run without the concluding trigger is marked as a variant of Scaffold-OPD (↳, outlined
    bar) instead of a faded one, and the base line is labelled once at the top."""
    rows = R2C._method_rows()
    d = OPD['eval_avg4']
    narrow = W < 500
    pitch, bh = (46, 13) if narrow else (36, 14)
    x0 = 10 if narrow else 220
    x1 = W - (60 if narrow else 100)
    top = 26
    y_end = top + pitch * len(rows) - 6
    H = y_end + 46
    svg = Svg(W, H, '4-benchmark math average by post-training method')
    sx = scale(0, 50, x0, x1)
    for v in range(10, 51, 10):
        svg.line(sx(v), top - 8, sx(v), y_end, 'grid')
    axes(svg, (x0, top - 8, x1, y_end), sx, lambda v: v, [0, 10, 20, 30, 40, 50], [], grid=False)
    svg.text((x0 + x1) / 2, y_end + 33, T('4-benchmark average (MATH-500, AIME 2024–26)', '4 项平均（MATH-500、AIME 2024–26）'), cls='t-muted', anchor='middle', size=11.5)
    svg.line(sx(d['base']), top - 8, sx(d['base']), y_end, 'leader', 'stroke-dasharray="3 3"')
    svg.text(sx(d['base']) + 4, top - 12, T('base', '基座'), cls='t-faint', size=10.5)
    ys = []
    for i, (lab, v, idx, strong) in enumerate(rows):
        yb = top + i * pitch + (22 if narrow else (pitch - bh) / 2 - 2)
        ys.append(yb)
        variant = i == 5
        if variant:
            lab = T('↳ ' + lab[0], '↳ ' + lab[1])
        cls = 't-strong' if strong else ('t-muted' if variant else '')
        if narrow:
            svg.text(x0 + (14 if variant else 0), yb - 6, lab, cls=cls, size=12)
        else:
            svg.text(x0 - 12, yb + bh / 2 + 4.2, lab, cls=cls, anchor='end', size=12.5)
        if variant:
            svg.mark(f'{lab[0]}: {v:.2f}', f'<path class="pn-blue" d="{hbar(x0, yb + 0.6, sx(v) - 0.6, bh - 1.2)}"/>')
        else:
            svg.mark(f'{lab[0]}: {v:.2f}', f'<path class="bar s{idx}" d="{hbar(x0, yb, sx(v), bh)}"/>')
        svg.text(sx(v) + 7, yb + bh / 2 + 4.2, f'{v:.1f}', cls='t-strong' if strong else 't-muted', size=12)
    xb = sx(d['takeover_conclude_40']) + (36 if narrow else 42)
    yo, yt = ys[3] + bh / 2, ys[4] + bh / 2
    svg.path(f'M{xb - 5:.1f},{yo:.1f} H{xb:.1f} V{yt:.1f} H{xb - 5:.1f}', 'leader')
    svg.text(xb + 6, (yo + yt) / 2 + 4.5, signed(d['takeover_conclude_40'] - d['opd_40']), cls='tx-blue', size=13, weight=700)
    return svg


def opd_methods_inno(W):
    """R2 bars, each split at the base model's 25.4: the light part is where every method starts, the solid part is the gain."""
    rows = R2C._method_rows()
    d = OPD['eval_avg4']
    base = d['base']
    narrow = W < 500
    pitch, bh = (46, 13) if narrow else (36, 14)
    x0 = 10 if narrow else 220
    x1 = W - (60 if narrow else 100)
    top = 26
    y_end = top + pitch * len(rows) - 6
    H = y_end + 46
    svg = Svg(W, H, '4-benchmark math average by post-training method, split into the base score and the gain over it')
    sx = scale(0, 50, x0, x1)
    for v in range(10, 51, 10):
        svg.line(sx(v), top - 8, sx(v), y_end, 'grid')
    axes(svg, (x0, top - 8, x1, y_end), sx, lambda v: v, [0, 10, 20, 30, 40, 50], [], grid=False)
    svg.text((x0 + x1) / 2, y_end + 33, T('4-benchmark average (MATH-500, AIME 2024–26)', '4 项平均（MATH-500、AIME 2024–26）'), cls='t-muted', anchor='middle', size=11.5)
    svg.text(sx(base) + 4, top - 12, T('base', '基座'), cls='t-faint', size=10.5)
    ys = []
    for i, (lab, v, idx, strong) in enumerate(rows):
        yb = top + i * pitch + (22 if narrow else (pitch - bh) / 2 - 2)
        ys.append(yb)
        cls = 't-strong' if strong else ('t-muted' if i == 5 else '')
        if narrow:
            svg.text(x0, yb - 6, lab, cls=cls, size=12)
        else:
            svg.text(x0 - 12, yb + bh / 2 + 4.2, lab, cls=cls, anchor='end', size=12.5)
        op = ' opacity=".45"' if i == 5 else ''
        svg.rect(x0, yb, sx(base) - x0, bh, 'fl-gray')
        if i:
            svg.mark(f'{lab[0]}: {v:.2f} ({signed(v - base)} over base)', f'<path class="bar s{idx}" d="{hbar(sx(base) + 1.5, yb, sx(v), bh)}"{op}/>')
        svg.text(sx(v) + 7, yb + bh / 2 + 4.2, f'{v:.1f}', cls='t-strong' if strong else 't-muted', size=12)
    xb = sx(d['takeover_conclude_40']) + (36 if narrow else 42)
    yo, yt = ys[3] + bh / 2, ys[4] + bh / 2
    svg.path(f'M{xb - 5:.1f},{yo:.1f} H{xb:.1f} V{yt:.1f} H{xb - 5:.1f}', 'leader')
    svg.text(xb + 6, (yo + yt) / 2 + 4.5, signed(d['takeover_conclude_40'] - d['opd_40']), cls='tx-blue', size=13, weight=700)
    return svg


def opd_budget_aes(W):
    """R2, polished: the three-line note in panel (a) becomes one line above the 16k–32k band."""
    svg = R2C.opd_budget_inno(W)
    if W < 500:
        return svg
    svg.parts = [p_ for p_ in svg.parts if not any(k in p_ for k in ('OPD has finished', 'its answers and stops', 'keeps reasoning'))]
    A = (52, 54, W - 150, 232)
    sxA, syA = scale(10, 15, A[0], A[2]), scale(0, 50, A[3], A[1])
    svg.text(sxA(14) - 8, syA(47.5), T('16k → 32k: OPD stops rising, Scaffold-OPD keeps reasoning', '16k → 32k：OPD 不再提升，Scaffold-OPD 还在推理'), cls='t-muted', anchor='end', size=11)
    return svg


def opd_budget_inno(W):
    """R2, with the 8k / 16k / 32k guides carried through all three panels."""
    svg = R2C.opd_budget_inno(W)
    if W < 500:
        return svg
    B = (52, 306, W / 2 - 44, 480 - 54)
    C = (W / 2 + 56, 306, W - 150, 480 - 54)
    for box in (B, C):
        sx = scale(10, 15, box[0], box[2])
        for t in (13, 14):
            svg.parts.insert(0, f'<line x1="{sx(t):.1f}" y1="{box[1]:.1f}" x2="{sx(t):.1f}" y2="{box[3]:.1f}" class="grid" stroke-dasharray="3 3"/>')
    return svg


def opd_training_aes(W):
    """R2, polished: a dashed guide at step 40, the step every main result is reported at, through both panels."""
    svg = R2C.opd_training_inno(W)
    narrow = W < 500
    boxes = [(52, 62, W - 64, 212), (52, 316, W - 64, 460)] if narrow else [(56, 62, W / 2 - 70, 300 - 52), (W / 2 + 54, 62, W - 60, 300 - 52)]
    for k, box in enumerate(boxes):
        x = scale(0, 60, box[0], box[2])(40)
        svg.parts.insert(0, f'<line x1="{x:.1f}" y1="{box[1]:.1f}" x2="{x:.1f}" y2="{box[3]:.1f}" class="leader" stroke-dasharray="3 3"/>')
        if k == 0:
            svg.text(x + 4, box[1] + 10, T('step 40: main result', '第 40 步：主结果'), cls='t-faint', size=10.5)
    return svg


def opd_training_inno(W):
    """R2, with the teacher's share written next to the curve at both ends instead of in a corner note."""
    svg = R2C.opd_training_inno(W)
    svg.parts = [p_ for p_ in svg.parts if 'share of all tokens' not in p_ and 'answers get' not in p_]
    narrow = W < 500
    bB = (52, 316, W - 64, 460) if narrow else (W / 2 + 54, 62, W - 60, 300 - 52)
    t = OPD['train']['takeover']
    teach = moving_avg([(s_, v) for s_, v in zip(t['step'], t['teacher_tokens_per_answer']) if v is not None and s_ != 19])
    ratio = {s_: 100 * r_ for s_, r_ in zip(t['step'], t['teacher_token_ratio'])}
    sxB, syB = scale(0, 60, bB[0], bB[2]), scale(0, 200, bB[3], bB[1])
    s0 = sum(ratio[s_] for s_ in range(1, 6)) / 5
    s1 = sum(ratio[s_] for s_ in range(56, 61)) / 5
    svg.text(sxB(teach[0][0]) + 6, syB(teach[0][1]) - 10, T(f'{s0:.0f}% of the answer', f'占回答 {s0:.0f}%'), cls='tx-green', size=11.5, weight=700)
    svg.text(sxB(60) - 4, syB(teach[-1][1]) - 12, T(f'{s1:.0f}% of the answer', f'占回答 {s1:.0f}%'), cls='tx-green', anchor='end', size=11.5, weight=700)
    return svg


def opd_compute_aes(W):
    """R2: stage scores above the segments, the final score once at the end, the base score at zero."""
    narrow = W < 500
    svg = Svg(W, 236 if not narrow else 294, 'Training GPU-hours of the full pipeline (with the average after each stage) and of Scaffold-OPD alone')
    g, p = OPD['gpu_hours']['pipeline'], OPD['pipeline_avg4']
    alone_h, alone_s = OPD['gpu_hours']['takeover_40'], OPD['eval_avg4']['takeover_40']
    x0 = 150 if not narrow else 16
    x1 = W - (126 if not narrow else 22)
    sx = scale(0, 56, x0, x1)
    rows_y = (74, 154) if not narrow else (100, 200)
    segs = [(g['sft_incl_teacher_data'], 'pn-yellow', T('data + SFT', '数据 + SFT'), p['sft']),
            (g['takeover_40'], 'pn-blue', T('Scaffold-OPD', 'Scaffold-OPD'), p['takeover_40']),
            (g['grpo_30'], 'pn-orange', T('GRPO', 'GRPO'), p['grpo_30'])]
    for v in (0, 10, 20, 30, 40, 50):
        svg.line(sx(v), 44, sx(v), rows_y[1] + 34, 'grid')
        svg.line(sx(v), rows_y[1] + 34, sx(v), rows_y[1] + 38, 'axis')
        svg.text(sx(v), rows_y[1] + 52, str(v), cls='t-faint', anchor='middle', size=11)
    svg.line(x0, rows_y[1] + 34, sx(56), rows_y[1] + 34, 'axis')
    svg.text((x0 + x1) / 2, rows_y[1] + 70, T('training GPU-hours (2 × A100)', '训练卡时（2 × A100）'), cls='t-muted', anchor='middle', size=11.5)
    y = rows_y[0]
    if narrow:
        svg.text(x0, y - 24, T('Full pipeline', '全流程'), cls='t-strong', size=12.5)
    else:
        svg.text(x0 - 12, y + 20, T('Full pipeline', '全流程'), cls='t-strong', anchor='end', size=12.5)
    svg.text(sx(0), y - 8, f'{p["base"]:.1f}', cls='t-faint', anchor='middle', size=10.5)
    x = 0
    for k, (hrs, cls, lab, score) in enumerate(segs):
        svg.mark(f'{lab[0]}: {hrs:.1f} GPU-hours, average {score:.1f} after it',
                 f'<rect class="{cls}" x="{sx(x) + 1:.1f}" y="{y:.1f}" width="{sx(x + hrs) - sx(x) - 2:.1f}" height="30" rx="6"/>')
        svg.text((sx(x) + sx(x + hrs)) / 2, y + 14, lab, cls='t-strong', anchor='middle', size=11 if not narrow else 9.5)
        svg.text((sx(x) + sx(x + hrs)) / 2, y + 26, f'{hrs:.1f} h', cls='t-muted', anchor='middle', size=10)
        x += hrs
        if k < 2:
            svg.text(sx(x), y - 8, f'{score:.1f}', cls='t-muted', anchor='middle', size=10.5)
    svg.text(sx(x) + 10, y + 20, f'→ {p["grpo_30"]:.1f}', cls='t-strong', size=13.5)
    y = rows_y[1]
    if narrow:
        svg.text(x0, y - 24, T('Scaffold-OPD alone', '只做 Scaffold-OPD'), cls='t-strong', size=12.5)
    else:
        svg.text(x0 - 12, y + 20, T('Scaffold-OPD alone', '只做 Scaffold-OPD'), cls='t-strong', anchor='end', size=12.5)
    svg.mark(f'Scaffold-OPD alone: {alone_h:.1f} GPU-hours', f'<rect class="pn-blue" x="{sx(0) + 1:.1f}" y="{y:.1f}" width="{sx(alone_h) - sx(0) - 2:.1f}" height="30" rx="6"/>')
    svg.text((sx(0) + sx(alone_h)) / 2, y + 20, f'{alone_h:.1f} h', cls='t-muted', anchor='middle', size=10.5)
    svg.text(sx(alone_h) + 10, y + 20, f'→ {alone_s:.1f}', cls='t-strong', size=13.5)
    svg.path(f'M{sx(alone_h):.1f},{y - 8:.1f} V{y - 14:.1f} H{sx(x):.1f} V{y - 8:.1f}', 'leader')
    svg.text((sx(alone_h) + sx(x)) / 2, y - 18, T(f'{x / alone_h:.1f}× the GPU-hours for the same score', f'分数相同，卡时多 {x / alone_h:.1f} 倍'), cls='tx-blue', anchor='middle', size=11.5, weight=700)
    return svg


def opd_compute_inno(W):
    """A different reading of the same numbers: training GPU-hours per point of 4-benchmark average gained over the
    base model. Both routes end at the same score, so the ratio is the whole story."""
    narrow = W < 500
    g, p = OPD['gpu_hours']['pipeline'], OPD['pipeline_avg4']
    pipe_h = g['total']   # 52.4: the sum before the per-stage values were rounded
    alone_h, alone_s = OPD['gpu_hours']['takeover_40'], OPD['eval_avg4']['takeover_40']
    rows = [(T('Full pipeline', '全流程'), pipe_h, p['grpo_30'] - p['base'], 'pn-orange', p['grpo_30']),
            (T('Scaffold-OPD alone', '只做 Scaffold-OPD'), alone_h, alone_s - p['base'], 'pn-blue', alone_s)]
    H = 200 if not narrow else 250
    svg = Svg(W, H, 'Training GPU-hours per point gained over the base model: full pipeline vs Scaffold-OPD alone')
    x0 = 160 if not narrow else 16
    x1 = W - (150 if not narrow else 30)
    sx = scale(0, 3, x0, x1)
    top = 40 if not narrow else 56
    svg.text(x0 if narrow else 16, 20, T('GPU-hours per point gained over the base model (25.4)', '每提升 1 分所需的训练卡时（相对基座 25.4）'), cls='t-strong', size=12.5)
    for v in (0, 1, 2, 3):
        svg.line(sx(v), top - 6, sx(v), top + 104, 'grid')
        svg.text(sx(v), top + 122, f'{v}', cls='t-faint', anchor='middle', size=11)
    for i, (lab, hrs, gain, cls, score) in enumerate(rows):
        y = top + i * 56 + (18 if narrow else 0)
        per = hrs / gain
        if narrow:
            svg.text(x0, y - 6, lab, cls='t-strong', size=12)
        else:
            svg.text(x0 - 12, y + 20, lab, cls='t-strong', anchor='end', size=12.5)
        svg.mark(f'{lab[0]}: {hrs:.1f} GPU-hours for +{gain:.1f} points = {per:.2f} per point',
                 f'<rect class="{cls}" x="{sx(0):.1f}" y="{y:.1f}" width="{sx(per) - sx(0):.1f}" height="28" rx="6"/>')
        svg.text(sx(per) + 10, y + 13, f'{per:.2f}', cls='t-strong', size=13)
        svg.text(sx(per) + 10, y + 27, T(f'{hrs:.1f} h for +{gain:.1f} → {score:.1f}', f'{hrs:.1f} 小时，+{gain:.1f} → {score:.1f}'), cls='t-muted', size=10.5)
    return svg


def scr_sft_rl_aes(W):
    """R2, polished: the two-object rows, which carry the point of the figure, show their task counts under the line."""
    svg = R2C.scr_sft_rl_inno(W)
    narrow = W < 500
    panels = [('seen', (100, 70, W - 60, 228)), ('unseen', (100, 310, W - 60, 468))] if narrow else \
             [('seen', (130, 66, W / 2 - 60, 290 - 50)), ('unseen', (W / 2 + 96, 66, W - 60, 290 - 50))]
    for split, box in panels:
        a, b = V2.family_counts('sft', split), V2.family_counts('sft_gigpo_step100', split)
        gain = {f: 100 * (b[f][0] - a[f][0]) / a[f][1] for f in V2.FAM_ORDER}
        order = sorted(V2.FAM_ORDER, key=lambda f: -gain[f])
        sx = scale(0, 100, box[0], box[2])
        pitch = (box[3] - box[1]) / len(order)
        i = order.index('pick_two_obj_and_place')
        y = box[1] + i * pitch + pitch / 2 - 4
        (sa, n), (sb, _) = a['pick_two_obj_and_place'], b['pick_two_obj_and_place']
        svg.text((sx(100 * sa / n) + sx(100 * sb / n)) / 2, y + 16, f'{sa}/{n} → {sb}/{n}', cls='tx-blue', anchor='middle', size=10.5)
    return svg


def scr_sft_rl_inno(W):
    """One panel: each family has a seen (solid) and an unseen (hollow) dumbbell, sorted by the seen gain."""
    narrow = W < 500
    a_s, b_s = V2.family_counts('sft', 'seen'), V2.family_counts('sft_gigpo_step100', 'seen')
    a_u, b_u = V2.family_counts('sft', 'unseen'), V2.family_counts('sft_gigpo_step100', 'unseen')
    gain = {f: 100 * (b_s[f][0] - a_s[f][0]) / a_s[f][1] for f in V2.FAM_ORDER}
    order = sorted(V2.FAM_ORDER, key=lambda f: -gain[f])
    H = 330 if not narrow else 380
    box = (140 if not narrow else 104, 56, W - (40 if not narrow else 20), H - 46)
    svg = Svg(W, H, 'ALFWorld success by task family after SFT and after 100 RL steps, seen and unseen')
    chip_legend(svg, 14, 18, [('s3', T('after SFT', 'SFT 后')), ('s1', T('after +100 RL steps', '再训练 100 步 RL 后'))], size=11.5)
    sx = scale(0, 100, box[0], box[2])
    for v in (25, 50, 75, 100):
        svg.line(sx(v), box[1] - 6, sx(v), box[3], 'grid')
    axes(svg, (box[0], box[1] - 6, box[2], box[3]), sx, lambda v: v, [0, 25, 50, 75, 100], [], grid=False, xtitle=T('success, %  (● seen  ○ unseen)', '成功率，%（● seen  ○ unseen）'))
    pitch = (box[3] - box[1]) / len(order)
    for i, fam in enumerate(order):
        y = box[1] + i * pitch + pitch / 2 - 6
        key = fam == 'pick_two_obj_and_place'
        svg.text(box[0] - 10, y + 9, V2.FAM_NAMES[fam], cls='t-strong' if key else '', anchor='end', size=11.5)
        for j, (a, b, yy, hollow) in enumerate([(a_s, b_s, y, False), (a_u, b_u, y + 13, True)]):
            pa, pb = 100 * a[fam][0] / a[fam][1], 100 * b[fam][0] / b[fam][1]
            svg.line(sx(pa), yy, sx(pb), yy, 'line l1' if key else 'line l3', 'stroke-width="2"' + ('' if key else ' opacity=".55"'))
            dot = 'fill="var(--bg)" stroke-width="2"' if hollow else ''
            svg.mark(f'{V2.FAM_NAMES[fam][0]} ({"unseen" if hollow else "seen"}): {a[fam][0]}/{a[fam][1]} → {b[fam][0]}/{b[fam][1]}',
                     f'<circle class="dot s3" cx="{sx(pa):.1f}" cy="{yy:.1f}" r="3.8"/>'
                     + (f'<circle cx="{sx(pb):.1f}" cy="{yy:.1f}" r="4" class="l1" fill="none" stroke-width="2"/>' if hollow else f'<circle class="dot s1" cx="{sx(pb):.1f}" cy="{yy:.1f}" r="4.5"/>'))
    return svg


def scr_vs_grpo_aes(W):
    """R2, with each panel's McNemar result at step 200 in its title line."""
    return R2C._vs(W, p_in_title=True)


def scr_vs_grpo_inno(W):
    """The aesthetic version plus, under each split, the tasks only one run solved at step 200 drawn as two short bars
    (what the McNemar test compares), instead of R2's sentence that collided."""
    if W < 500:
        return R2C._vs(W, p_in_title=True)
    svg = R2C._vs(W)
    svg.h += 52
    disc = {k: PAIRED[f'alfworld_steplevel_vs_grpo:valid_{k}'] for k in ('seen', 'unseen')}
    for k, (name, x0, x1) in enumerate([('seen', 48, W / 2 - 52), ('unseen', W / 2 + 54, W - 46)]):
        d = disc[name]
        y = 408
        unit = 3.6
        for j, (lab, n, cls) in enumerate([(T('only StepCredit-RL', '只有 StepCredit-RL'), int(d['only_a']), 's1'), (T('only GRPO', '只有 GRPO'), int(d['only_b']), 's2')]):
            yy = y + j * 18
            svg.text(x0, yy + 9, lab, cls='t-muted', size=10.5)
            bx = x0 + 104
            svg.rect(bx, yy, n * unit, 11, cls, rx=3)
            svg.text(bx + n * unit + 5, yy + 9.5, str(n), cls='t-strong', size=11)
        pv = float(d['p'])
        svg.text(x1, y + 27, f'p = {pv:.3f}' if pv < 0.1 else f'p = {pv:.2f}', cls='tx-blue' if pv < 0.05 else 't-muted', anchor='end', size=11.5, weight=700 if pv < 0.05 else None)
        svg.text(x0, y - 8, T('step 200, tasks solved by only one run', '第 200 步，只有一方解出的任务'), cls='t-faint', size=10.5)
    return svg


def scr_updates_aes(W):
    """R2 bars without ratio labels: the reader reads the steps and hours directly."""
    svg = R2C.scr_updates_aes(W)
    svg.parts = [p_ for p_ in svg.parts if not ('class="tx-blue"' in p_ and '×' in p_)]
    return svg


def scr_updates_inno(W):
    """Back to curves, tied to the text: by step (same level at step 100 vs 150) and by wall-clock hours."""
    return R1C.scr_updates_aes(W)


def scr_hotpotqa_aes(W):
    """R2, with the −71% moved up next to the bracket, off the shaped-reward line."""
    return R2C.scr_hotpotqa_aes(W, label_frac=0.65)


def scr_hotpotqa_inno(W):
    """R2 small multiples plus a one-line reading of the result at step 200 under them."""
    svg = R2C.scr_hotpotqa_aes(W)
    narrow = W < 500
    em = {k: run(HPQ, 'em', k)[-1][1] for k in ('em', 'f1', 'repeat_queries')}
    sh = {k: run(HPQ, 'shaped', k)[-1][1] for k in ('em', 'f1', 'repeat_queries')}
    pv = float(PAIRED['hotpotqa_em_vs_shaped:all']['p'])
    svg.h += 30
    y = svg.h - 10
    if narrow:
        svg.text(8, y, T(f'Step 200, shaped vs EM reward: repeats −71%, EM −{em["em"] - sh["em"]:.1f} (p = {pv:.2f})', f'第 200 步，稠密对 EM 奖励：重复查询 −71%，EM −{em["em"] - sh["em"]:.1f}（p = {pv:.2f}）'), cls='t-muted', size=11)
    else:
        svg.text(56, y, T(f'Step 200, shaped vs EM reward: repeated queries {sh["repeat_queries"]:.3f} vs {em["repeat_queries"]:.3f} (−71%); EM {sh["em"]:.1f} vs {em["em"]:.1f} (McNemar p = {pv:.2f}); F1 {sh["f1"]:.3f} vs {em["f1"]:.3f}',
                         f'第 200 步，稠密奖励对 EM 奖励：重复查询 {sh["repeat_queries"]:.3f} 对 {em["repeat_queries"]:.3f}（−71%）；EM {sh["em"]:.1f} 对 {em["em"]:.1f}（McNemar p = {pv:.2f}）；F1 {sh["f1"]:.3f} 对 {em["f1"]:.3f}'), cls='t-muted', size=11.5)
    return svg


AES = {'card-opd': card_opd_aes, 'card-scr': card_scr_aes, 'opd-takeover': opd_framework_aes, 'scr-steplevel': scr_framework_aes,
       'opd-pipeline': opd_pipeline_aes, 'scr-pipeline': scr_pipeline_aes, 'opd-methods': opd_methods_aes, 'opd-budget': opd_budget_aes,
       'opd-training': opd_training_aes, 'opd-compute': opd_compute_aes, 'scr-sft-rl': scr_sft_rl_aes, 'scr-vs-grpo': scr_vs_grpo_aes,
       'scr-updates': scr_updates_aes, 'scr-hotpotqa': scr_hotpotqa_aes}
INNO = {'card-opd': card_opd_inno, 'card-scr': card_scr_inno, 'opd-takeover': opd_framework_inno, 'scr-steplevel': scr_framework_inno,
        'opd-pipeline': opd_pipeline_inno, 'scr-pipeline': scr_pipeline_inno, 'opd-methods': opd_methods_inno, 'opd-budget': opd_budget_inno,
        'opd-training': opd_training_inno, 'opd-compute': opd_compute_inno, 'scr-sft-rl': scr_sft_rl_inno, 'scr-vs-grpo': scr_vs_grpo_inno,
        'scr-updates': scr_updates_inno, 'scr-hotpotqa': scr_hotpotqa_inno}
