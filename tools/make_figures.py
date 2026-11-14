#!/usr/bin/env python3
"""Draw the site's figures as inline SVG and write them into the HTML pages.

Every figure lives between <!-- fig:NAME --> and <!-- /fig:NAME --> in a page; running this script replaces
what is between the markers. Data comes from tools/data/. Colours are CSS classes defined in
assets/css/site.css (.viz ...), so the figures follow the page's light / dark theme, and text that differs by
language is written as two <tspan lang="..."> children that the page's language switch shows or hides.

    python3 tools/make_figures.py          # standard library only
"""
import csv
import html
import json
import math
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'tools' / 'data'
LG, SM = 720, 360          # desktop and phone widths (viewBox units)


# ----------------------------------------------------------------------------- primitives
def esc(s):
    return html.escape(str(s), quote=False)


def T(en, zh=None):
    """Bilingual text; a plain string is used for both languages."""
    return (en, en if zh is None else zh)


def text_w(s, size):
    """Rough rendered width, enough to keep labels apart."""
    return sum(size * (1.0 if ord(ch) > 0x2e80 else 0.56) for ch in s)


class Svg:
    def __init__(self, w, h, label):
        self.w, self.h, self.label, self.parts = w, h, label, []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, t, cls='', anchor='start', size=13, weight=None):
        a = f'x="{x:.1f}" y="{y:.1f}" font-size="{size}"'
        if anchor != 'start':
            a += f' text-anchor="{anchor}"'
        if weight:
            a += f' font-weight="{weight}"'
        if cls:
            a += f' class="{cls}"'
        if isinstance(t, tuple) and t[0] != t[1]:
            inner = f'<tspan lang="en">{esc(t[0])}</tspan><tspan lang="zh-CN">{esc(t[1])}</tspan>'
        else:
            inner = esc(t[0] if isinstance(t, tuple) else t)
        self.add(f'<text {a}>{inner}</text>')

    def line(self, x1, y1, x2, y2, cls):
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" class="{cls}"/>')

    def render(self, variant=''):
        cls = 'viz' + (' ' + variant if variant else '')
        return (f'<svg class="{cls}" viewBox="0 0 {self.w} {self.h:.0f}" width="{self.w}" height="{self.h:.0f}" role="img" '
                f'aria-label="{html.escape(self.label, quote=True)}" xmlns="http://www.w3.org/2000/svg">'
                + ''.join(self.parts) + '</svg>')


def hbar(x0, y, x1, h, r=4):
    """Horizontal bar: square at the baseline (left), rounded data end (right)."""
    r = min(r, max(x1 - x0, 0), h / 2)
    return (f'M{x0:.1f},{y:.1f} H{x1 - r:.1f} A{r},{r} 0 0 1 {x1:.1f},{y + r:.1f} '
            f'V{y + h - r:.1f} A{r},{r} 0 0 1 {x1 - r:.1f},{y + h:.1f} H{x0:.1f} Z')


def scale(d0, d1, r0, r1):
    return lambda v: r0 + (v - d0) * (r1 - r0) / (d1 - d0)


def arrow(svg, x1, y1, x2, y2):
    """Thin connector with a small filled head at (x2, y2)."""
    ang = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 6 * math.cos(ang), y2 - 6 * math.sin(ang)
    svg.line(x1, y1, hx, hy, 'arrow')
    p1 = (x2 - 7 * math.cos(ang - 0.45), y2 - 7 * math.sin(ang - 0.45))
    p2 = (x2 - 7 * math.cos(ang + 0.45), y2 - 7 * math.sin(ang + 0.45))
    svg.add(f'<path class="arrow-head" d="M{x2:.1f},{y2:.1f} L{p1[0]:.1f},{p1[1]:.1f} L{p2[0]:.1f},{p2[1]:.1f} Z"/>')


def legend(svg, x, y, items, size=12.5):
    """items: [(series index, text)]; a short line key beside each name."""
    for idx, label in items:
        svg.add(f'<line x1="{x:.1f}" y1="{y - 4:.1f}" x2="{x + 18:.1f}" y2="{y - 4:.1f}" class="line l{idx}"/>')
        svg.text(x + 24, y, label, size=size)
        lab = label[0] if isinstance(label, tuple) else label
        x += 24 + max(text_w(lab, size), text_w(label[1] if isinstance(label, tuple) else lab, size)) + 22


def fmt(v, nd=1):
    return f'{v:.{nd}f}'


# ----------------------------------------------------------------------------- line panel
def line_panel(svg, box, xdom, ydom, xticks, yticks, series, title=None, end_labels=True,
               xfmt=str, yfmt=str, band=None, notes=(), point_title=None, efmt=None, end_names=True):
    """box = (x0, y0, x1, y1) of the plot area. series = [(idx, label, [(x, y), ...])]."""
    x0, y0, x1, y1 = box
    sx, sy = scale(xdom[0], xdom[1], x0, x1), scale(ydom[0], ydom[1], y1, y0)
    if title:
        svg.text(x0 - 6, y0 - 14, title, cls='t-strong', size=13)
    if band:
        bx0, bx1, blabel = band
        svg.add(f'<rect x="{sx(bx0):.1f}" y="{y0:.1f}" width="{sx(bx1) - sx(bx0):.1f}" height="{y1 - y0:.1f}" class="box-soft" style="stroke:none"/>')
        if blabel:
            svg.text((sx(bx0) + sx(bx1)) / 2, y0 + 14, blabel, cls='t-muted', anchor='middle', size=11.5)
    for v in yticks:
        y = sy(v)
        svg.line(x0, y, x1, y, 'grid' if v != ydom[0] else 'axis')
        svg.text(x0 - 6, y + 4, yfmt(v), cls='t-muted', anchor='end', size=11.5)
    for v in xticks:
        svg.text(sx(v), y1 + 17, xfmt(v), cls='t-muted', anchor='middle', size=11.5)
    for idx, label, pts in series:
        d = ' '.join(f'{"M" if i == 0 else "L"}{sx(x):.1f},{sy(y):.1f}' for i, (x, y) in enumerate(pts))
        svg.add(f'<path class="line l{idx}" d="{d}"/>')
    for idx, label, pts in series:      # hover targets with native tooltips
        for (x, y) in pts:
            tip = point_title(label, x, y) if point_title else f'{x}: {y}'
            svg.add(f'<g class="mark"><title>{esc(tip)}</title><circle class="hit" cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="7"/></g>')
    placed = []
    for idx, label, pts in series:
        xe, ye = pts[-1]
        svg.add(f'<circle class="dot s{idx}" cx="{sx(xe):.1f}" cy="{sy(ye):.1f}" r="4"/>')
        if end_labels:
            ty = sy(ye) + 4
            for py in placed:
                if abs(ty - py) < 14:
                    ty = py + (14 if ty >= py else -14)
            placed.append(ty)
            name = label if isinstance(label, tuple) else (label, label)
            ef = efmt or yfmt
            if end_names:
                svg.text(sx(xe) + 8, ty, (f'{name[0]} {ef(ye)}', f'{name[1]} {ef(ye)}'), size=12)
            else:
                svg.text(sx(xe) + 8, ty, ef(ye), size=12)
    for nx, ny, t, anchor in notes:
        svg.text(sx(nx), sy(ny), t, cls='t-muted', anchor=anchor, size=11.5)
    return sx, sy


def data_table(head, rows, summary=T('Data', '数据')):
    th = ''.join(f'<th>{h}</th>' for h in head)
    body = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    s = f'<span lang="en">{summary[0]}</span><span lang="zh-CN">{summary[1]}</span>'
    return (f'<details class="fig-data"><summary>{s}</summary><div class="table-wrap"><table>'
            f'<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div></details>')


def bi(t):
    return f'<span lang="en">{t[0]}</span><span lang="zh-CN">{t[1]}</span>'


def moving_avg(pts, k=5):
    out = []
    for i in range(len(pts)):
        win = [y for (_, y) in pts[max(0, i - k + 1):i + 1]]
        out.append((pts[i][0], sum(win) / len(win)))
    return out


# ----------------------------------------------------------------------------- Scaffold-OPD
OPD = json.loads((DATA / 'scaffold_opd.json').read_text())


def fig_opd_methods(W):
    d = OPD['eval_avg4']
    rows = [
        (T('Base (Qwen3-1.7B)', '基座（Qwen3-1.7B）'), d['base'], 3, False),
        (T('GRPO, 60 steps', 'GRPO，60 步'), d['grpo_60'], 3, False),
        (T('SFT, 1 epoch', 'SFT，1 轮'), d['sft'], 3, False),
        (T('OPD, 40 steps', 'OPD，40 步'), d['opd_40'], 2, False),
        (T('Takeover OPD, 40 steps', 'Takeover OPD，40 步'), d['takeover_conclude_40'], 1, True),
        (T('without concluding trigger', '关闭收尾触发'), d['takeover_40'], 1, False),
    ]
    narrow = W < 500
    pitch, bh = (46, 16) if narrow else (34, 18)
    x0 = 6 if narrow else 214
    x1 = W - 52
    top = 8
    H = top + pitch * len(rows) + 30
    svg = Svg(W, H, '4-benchmark math average by post-training method')
    sx = scale(0, 50, x0, x1)
    for v in range(0, 51, 10):
        svg.line(sx(v), top, sx(v), top + pitch * len(rows), 'grid' if v else 'axis')
        svg.text(sx(v), top + pitch * len(rows) + 18, str(v), cls='t-muted', anchor='middle', size=11.5)
    for i, (lab, v, idx, strong) in enumerate(rows):
        yb = top + i * pitch + (22 if narrow else (pitch - bh) / 2)
        if narrow:
            svg.text(x0, yb - 6, lab, cls='t-strong' if strong else '', size=12.5)
        else:
            svg.text(x0 - 10, yb + bh / 2 + 4.5, lab, cls='t-strong' if strong else '', anchor='end', size=13)
        svg.add(f'<g class="mark"><title>{esc(lab[0])}: {v:.2f}</title><path class="bar s{idx}" d="{hbar(x0, yb, sx(v), bh)}"/></g>')
        svg.text(sx(v) + 6, yb + bh / 2 + 4.5, fmt(v), cls='t-strong' if strong else '', size=12.5)
    return svg


def fig_opd_budget(W):
    b = OPD['budget']
    toks = b['tokens']
    xs = [math.log2(t) for t in toks]
    narrow = W < 500
    H = 290 if narrow else 300
    box = (40, 40, W - (56 if narrow else 150), H - 34)
    svg = Svg(W, H, 'Accuracy versus evaluation token budget, Takeover OPD vs OPD')
    legend(svg, box[0], 16, [(1, 'Takeover OPD'), (2, 'OPD')])
    tick_tokens = [1024, 2048, 4096, 8192, 16384, 32768]
    series = [(1, 'Takeover OPD', list(zip(xs, b['takeover_40']))), (2, 'OPD', list(zip(xs, b['opd_40'])))]
    def at(name, tk):
        return dict(zip(toks, b[name]))[tk]
    notes = []
    for tk, txt in [(8192, None), (16384, None), (32768, None)]:
        diff = at('takeover_40', tk) - at('opd_40', tk)
        notes.append((math.log2(tk), max(at('takeover_40', tk), at('opd_40', tk)) + 2.2, f'{diff:+.1f}', 'middle'))
    line_panel(svg, box, (10, 15), (0, 50), [math.log2(t) for t in tick_tokens], range(0, 51, 10), series,
               xfmt=lambda v: f'{int(2 ** v / 1024)}k', yfmt=lambda v: f'{v:.0f}' if v == int(v) else f'{v:.1f}',
               notes=notes, end_names=not narrow,
               point_title=lambda lab, x, y: f'{lab} · {int(round(2 ** x))} tokens: {y:.1f}')
    return svg


def opd_budget_table():
    b = OPD['budget']
    rows = [[f'{t:,}', fmt(o), fmt(r), f'{r - o:+.1f}'] for t, o, r in zip(b['tokens'], b['opd_40'], b['takeover_40'])]
    return data_table([bi(T('Budget (tokens)', '预算（token）')), 'OPD', 'Takeover OPD', bi(T('Difference', '差值'))], rows)


def fig_opd_training(W):
    tr = OPD['train']
    tk = [(s, l) for s, l in zip(tr['takeover']['step'], tr['takeover']['response_length']) if s != 19]
    op = list(zip(tr['opd']['step'], tr['opd']['response_length']))
    ratio = [(s, 100 * r) for s, r in zip(tr['takeover']['step'], tr['takeover']['teacher_token_ratio']) if s != 19]
    narrow = W < 500
    if narrow:
        H = 470
        boxA = (46, 60, W - 72, 210)
        boxB = (46, 300, W - 72, 440)
    else:
        H = 280
        boxA = (46, 60, W / 2 - 92, H - 34)
        boxB = (W / 2 + 40, 60, W - 70, H - 34)
    svg = Svg(W, H, 'Training dynamics: response length and teacher-token share')
    legend(svg, boxA[0], 16, [(1, 'Takeover OPD'), (2, 'OPD')])
    line_panel(svg, boxA, (0, 60), (0, 6000), [0, 20, 40, 60], [0, 2000, 4000, 6000],
               [(1, 'Takeover OPD', moving_avg(tk)), (2, 'OPD', moving_avg(op))],
               title=T('Response length (tokens)', '回答长度（token）'),
               yfmt=lambda v: f'{v / 1000:.0f}k' if v else '0', xfmt=lambda v: str(int(v)), efmt=lambda v: f'{v:,.0f}', end_names=not narrow,
               point_title=lambda lab, x, y: f'{lab} · step {x}: {y:,.0f} tokens')
    line_panel(svg, boxB, (0, 60), (0, 20), [0, 20, 40, 60], [0, 5, 10, 15, 20],
               [(1, T('teacher', '老师'), moving_avg(ratio))],
               title=T('Teacher-token share (%)', '老师 token 占比（%）'), end_names=not narrow,
               yfmt=lambda v: f'{v:.0f}' if abs(v - round(v)) < 1e-9 else f'{v:.1f}', xfmt=lambda v: str(int(v)), efmt=lambda v: f'{v:.1f}%',
               point_title=lambda lab, x, y: f'step {x}: {y:.1f}%')
    svg.text(boxA[2], boxA[3] + 30, T('step', '步'), cls='t-muted', anchor='end', size=11.5)
    svg.text(boxB[2], boxB[3] + 30, T('step', '步'), cls='t-muted', anchor='end', size=11.5)
    return svg


def opd_training_table():
    tr = OPD['train']
    t = dict(zip(tr['takeover']['step'], zip(tr['takeover']['response_length'], tr['takeover']['teacher_token_ratio'])))
    o = dict(zip(tr['opd']['step'], tr['opd']['response_length']))
    rows = []
    for s in range(5, 61, 5):
        tl, ratio = t[s]
        rows.append([str(s), f'{tl:,.0f}', f'{o[s]:,.0f}', f'{100 * ratio:.1f}%'])
    return data_table([bi(T('Step', '步')), bi(T('Takeover OPD length', 'Takeover OPD 长度')), bi(T('OPD length', 'OPD 长度')),
                       bi(T('Teacher-token share', '老师 token 占比'))], rows,
                      summary=T('Data (raw values every 5 steps)', '数据（每 5 步的原始值）'))


def pills(svg, x, y, w, h, items, key, gap):
    """A row of stage boxes joined by arrows. items: [(title, detail)]; key = index of the highlighted stage."""
    for i, (title, detail) in enumerate(items):
        bx = x + i * (w + gap)
        cls = 'box-key' if i == key else 'box'
        svg.add(f'<rect x="{bx:.1f}" y="{y:.1f}" width="{w}" height="{h}" rx="8" class="{cls}"/>')
        if detail:
            svg.text(bx + w / 2, y + h / 2 - 3, title, cls='t-strong', anchor='middle', size=12.5)
            svg.text(bx + w / 2, y + h / 2 + 13, detail, cls='t-muted', anchor='middle', size=11)
        else:
            svg.text(bx + w / 2, y + h / 2 + 4.5, title, cls='t-strong', anchor='middle', size=12.5)
        if i:
            arrow(svg, bx - gap + 3, y + h / 2, bx - 3, y + h / 2)


def token_strip(svg, x, y, w, h, segs):
    """segs: [(fraction, 'student'|'teacher', label or None)]; drawn with a 2px surface gap between segments."""
    cx = x
    for frac, who, label in segs:
        sw = w * frac
        cls = 'tok-t' if who == 'teacher' else 'tok-s'
        svg.add(f'<rect x="{cx:.1f}" y="{y:.1f}" width="{max(sw - 2, 1):.1f}" height="{h}" rx="3" class="{cls}"/>')
        if label:
            svg.add(f'<text x="{cx + sw / 2 - 1:.1f}" y="{y + h / 2 + 4:.1f}" font-size="11.5" text-anchor="middle" style="fill:#fff;font-weight:600">{esc(label)}</text>')
        cx += sw
    return cx


def fig_card_opd(W=380):
    svg = Svg(W, 112, 'Scaffold-OPD pipeline: teacher data, SFT, Takeover OPD, GRPO')
    items = [(T('Teacher data', '老师数据'), None), (T('SFT', 'SFT'), None), (T('Takeover OPD', 'Takeover OPD'), None), (T('GRPO', 'GRPO'), None)]
    w, gap = 80, 19
    x = (W - (4 * w + 3 * gap)) / 2
    pills(svg, x, 8, w, 32, items, 2, gap)
    kx = x + 2 * (w + gap)
    sx0, sx1, sy = x + 6, x + 4 * w + 3 * gap - 6, 66
    svg.add(f'<path class="arrow" d="M{kx:.1f},{40:.1f} L{sx0:.1f},{sy - 6:.1f} M{kx + w:.1f},{40:.1f} L{sx1:.1f},{sy - 6:.1f}"/>')
    token_strip(svg, sx0, sy, sx1 - sx0, 18, [(0.30, 'student', None), (0.20, 'teacher', 'Wait, …'), (0.28, 'student', None), (0.22, 'teacher', 'But …')])
    svg.add(f'<rect x="{sx0:.1f}" y="{sy + 30:.1f}" width="10" height="10" rx="2" class="tok-s"/>')
    svg.text(sx0 + 15, sy + 39, T('student writes', '学生写'), size=11.5)
    svg.add(f'<rect x="{sx0 + 120:.1f}" y="{sy + 30:.1f}" width="10" height="10" rx="2" class="tok-t"/>')
    svg.text(sx0 + 135, sy + 39, T('teacher takes over', '老师接管'), size=11.5)
    return svg


def fig_opd_pipeline(W):
    items = [
        (T('Teacher data', '老师轨迹'), T('14,116 problems', '14,116 道题'), None),
        (T('Rejection sampling', '拒绝采样'), T('79% kept', '保留 79%'), None),
        (T('SFT', 'SFT'), T('1 epoch', '1 轮'), '38.0'),
        (T('Takeover OPD', 'Takeover OPD'), T('40 steps', '40 步'), '42.6'),
        (T('GRPO on failures', '错题回流 GRPO'), T('2,212 problems', '2,212 道题'), '46.6'),
    ]
    narrow = W < 500
    if not narrow:
        w, gap, h, y = 124, 20, 62, 10
        x = (W - (5 * w + 4 * gap)) / 2
        svg = Svg(W, 128, 'Scaffold-OPD pipeline with the average after each stage')
        pills(svg, x, y, w, h, [(a, b) for a, b, _ in items], 3, gap)
        for i, (_, _, score) in enumerate(items):
            if score:
                cx = x + i * (w + gap) + w / 2
                svg.text(cx, y + h + 22, (f'avg {score}', f'平均 {score}'), cls='t-strong' if i == 3 or i == 4 else '', anchor='middle', size=12.5)
        svg.text(x, y + h + 46, T('Base model: 25.4 on the same 4-benchmark average.', '基座模型在同一 4 项平均上为 25.4。'), cls='t-muted', size=11.5)
        return svg
    w, h, gap = W - 20, 46, 16
    H = 10 + 5 * h + 4 * gap + 34
    svg = Svg(W, H, 'Scaffold-OPD pipeline with the average after each stage')
    for i, (title, detail, score) in enumerate(items):
        y = 10 + i * (h + gap)
        cls = 'box-key' if i == 3 else 'box'
        svg.add(f'<rect x="10" y="{y}" width="{w}" height="{h}" rx="8" class="{cls}"/>')
        svg.text(24, y + 20, title, cls='t-strong', size=13)
        svg.text(24, y + 37, detail, cls='t-muted', size=11.5)
        if score:
            svg.text(10 + w - 14, y + 28, (f'avg {score}', f'平均 {score}'), cls='t-strong', anchor='end', size=13)
        if i:
            arrow(svg, 10 + w / 2, y - gap + 2, 10 + w / 2, y - 2)
    svg.text(10, H - 10, T('Base model: 25.4.', '基座模型：25.4。'), cls='t-muted', size=11.5)
    return svg


def fig_opd_takeover(W):
    narrow = W < 500
    H = 214 if narrow else 176
    svg = Svg(W, H, 'One relayed answer: student tokens with two teacher takeovers')
    x0, x1 = 12, W - 12
    sy = 84 if narrow else 70
    segs = [(0.27, 'student', None), (0.17, 'teacher', 'Wait, …'), (0.30, 'student', None), (0.14, 'teacher', 'But …'), (0.12, 'end', None)]
    cx = x0
    width = x1 - x0
    marks = []
    for frac, who, label in segs:
        sw = width * frac
        if who == 'end':
            svg.text(cx + 6, sy + 18, T('end', '结束'), cls='t-muted', size=11.5)
            break
        cls = 'tok-t' if who == 'teacher' else 'tok-s'
        svg.add(f'<rect x="{cx:.1f}" y="{sy}" width="{sw - 2:.1f}" height="26" rx="4" class="{cls}"/>')
        if label:
            svg.add(f'<text x="{cx + sw / 2 - 1:.1f}" y="{sy + 17.5}" font-size="12" text-anchor="middle" style="fill:#fff;font-weight:600">{esc(label)}</text>')
        marks.append((cx, cx + sw, who))
        cx += sw
    t1s, t1e, _ = marks[1]
    t2s, t2e, _ = marks[3]
    if narrow:
        svg.text(x0, 16, T('① Teacher’s top next token is a reflection', '① 老师最想写的下一个 token 是反思词，'), size=12)
        svg.text(x0, 32, T('   word not in the student’s top-5 → take over', '   且不在学生 top-5 里 → 老师接管'), size=12)
        svg.text(x0, 50, T('② Teacher writes ≤3 paragraphs, then hands back', '② 老师最多写 3 段（≤256 token）后交还'), size=12)
        svg.line(t1s + 1, 56, t1s + 1, sy - 3, 'arrow')
        svg.text(x0, sy + 46, T('At most 2 takeovers per answer; the answer ends after the second.', '每条回答最多接管 2 次，第 2 次写完回答结束。'), cls='t-muted', size=11.5)
        svg.text(x0, sy + 70, T('③ Every token carries its author → token-level', '③ 每个 token 都带有作者标记 →'), size=12)
        svg.text(x0, sy + 86, T('   reverse KL to the teacher on the whole answer', '   对整条回答做对老师的 token 级反向 KL'), size=12)
        svg.add(f'<rect x="{x0}" y="{H - 20}" width="10" height="10" rx="2" class="tok-s"/>')
        svg.text(x0 + 15, H - 11, T('student', '学生'), size=11.5)
        svg.add(f'<rect x="{x0 + 80}" y="{H - 20}" width="10" height="10" rx="2" class="tok-t"/>')
        svg.text(x0 + 95, H - 11, T('teacher', '老师'), size=11.5)
        return svg
    svg.text(t1s, 22, T('① Teacher’s most likely next token is a reflection word', '① 老师最想写的下一个 token 是反思词（Wait、But 等），'), size=12.5)
    svg.text(t1s, 39, T('   (Wait, But, …) that is not in the student’s top-5', '   且不在学生的 top-5 里'), size=12.5)
    svg.line(t1s + 1, 46, t1s + 1, sy - 3, 'arrow')
    svg.text(t1e + 8, sy + 46, T('② ≤3 paragraphs (≤256 tokens), then hand back', '② 最多 3 段（≤256 token）后交还'), size=12)
    svg.line(t1e - 1, sy + 29, t1e - 1, sy + 36, 'arrow')
    svg.text(t2s, sy + 70, T('at most 2 takeovers per answer', '每条回答最多接管 2 次'), cls='t-muted', size=11.5)
    svg.text(x0, sy + 98, T('③ Every token carries its author → token-level reverse KL to the teacher on the whole answer',
                            '③ 每个 token 都带有作者标记 → 对整条回答做对老师的 token 级反向 KL'), size=12.5)
    lx = x1 - 160
    svg.add(f'<rect x="{lx}" y="12" width="10" height="10" rx="2" class="tok-s"/>')
    svg.text(lx + 15, 21, T('student', '学生'), size=11.5)
    svg.add(f'<rect x="{lx + 80}" y="12" width="10" height="10" rx="2" class="tok-t"/>')
    svg.text(lx + 95, 21, T('teacher', '老师'), size=11.5)
    return svg


# ----------------------------------------------------------------------------- StepCredit-RL
def read_csv(name):
    with open(DATA / name, newline='') as f:
        return list(csv.DictReader(f))


ALF = read_csv('alfworld_val.csv')
HPQ = read_csv('hotpotqa_val.csv')


def run(rows, name, col):
    return [(int(r['step']), float(r[col])) for r in rows if r['run'] == name]


def fig_card_scr(W=380):
    svg = Svg(W, 112, 'StepCredit-RL pipeline: expert demonstrations, SFT, multi-turn RL, paired evaluation')
    items = [(T('Expert demos', '专家示范'), None), (T('SFT', 'SFT'), None), (T('Multi-turn RL', '多轮 RL'), None), (T('Paired eval', '配对评测'), None)]
    w, gap = 80, 19
    x = (W - (4 * w + 3 * gap)) / 2
    pills(svg, x, 8, w, 32, items, 2, gap)
    kx = x + 2 * (w + gap)
    sx0, sx1, sy = x + 6, x + 4 * w + 3 * gap - 6, 74
    svg.add(f'<path class="arrow" d="M{kx:.1f},40 L{sx0:.1f},{sy - 14:.1f} M{kx + w:.1f},40 L{sx1:.1f},{sy - 14:.1f}"/>')
    n = 9
    credit = [0.15, 0.2, 0.9, 0.25, 0.1, 0.2, 0.85, 0.3, 0.6]
    for i in range(n):
        cx = sx0 + 10 + i * (sx1 - sx0 - 20) / (n - 1)
        r = 4 + 4 * credit[i]
        cls = 's1' if credit[i] > 0.5 else 's3'
        svg.add(f'<circle cx="{cx:.1f}" cy="{sy:.1f}" r="{r:.1f}" class="dot {cls}"/>')
        if i:
            px = sx0 + 10 + (i - 1) * (sx1 - sx0 - 20) / (n - 1)
            svg.line(px + 8, sy, cx - 8, sy, 'grid')
    svg.text(sx0, sy + 32, T('one outcome reward → credit for each step, compared within the same state',
                             '一个结局奖励 → 同一状态下比较，给每一步分配信用'), cls='t-muted', size=11.5)
    return svg


def fig_scr_pipeline(W):
    items = [
        (T('Expert demos', '专家示范'), T('22,810 tool-call steps', '2.3 万步工具调用'), T('base 7.1 / 2.2', '基座 7.1 / 2.2')),
        (T('SFT', 'SFT'), T('1 epoch · 356 steps', '1 轮 · 356 步'), T('67.1 / 67.2', '67.1 / 67.2')),
        (T('Multi-turn RL', '多轮 RL'), T('step-level advantage', '步级相对优势'), T('98.6 / 94.0', '98.6 / 94.0')),
        (T('Paired eval', '配对评测'), T('McNemar on the same tasks', '同题 McNemar 检验'), None),
    ]
    narrow = W < 500
    if not narrow:
        w, gap, h, y = 160, 26, 62, 10
        x = (W - (4 * w + 3 * gap)) / 2
        svg = Svg(W, 108, 'StepCredit-RL pipeline with ALFWorld success after each stage')
        pills(svg, x, y, w, h, [(a, b) for a, b, _ in items], 2, gap)
        for i, (_, _, score) in enumerate(items):
            if score:
                svg.text(x + i * (w + gap) + w / 2, y + h + 22, score, cls='t-strong' if i == 2 else '', anchor='middle', size=12.5)
        return svg
    w, h, gap = W - 20, 46, 16
    H = 10 + 4 * h + 3 * gap + 10
    svg = Svg(W, H, 'StepCredit-RL pipeline with ALFWorld success after each stage')
    for i, (title, detail, score) in enumerate(items):
        y = 10 + i * (h + gap)
        svg.add(f'<rect x="10" y="{y}" width="{w}" height="{h}" rx="8" class="{"box-key" if i == 2 else "box"}"/>')
        svg.text(24, y + 20, title, cls='t-strong', size=13)
        svg.text(24, y + 37, detail, cls='t-muted', size=11.5)
        if score:
            svg.text(10 + w - 14, y + 28, score, cls='t-strong', anchor='end', size=12.5)
        if i:
            arrow(svg, 10 + w / 2, y - gap + 2, 10 + w / 2, y - 2)
    return svg


def fig_scr_steplevel(W):
    narrow = W < 500
    rows = [  # (states, outcome)
        (['A', 'B', 'C', 'D'], T('success', '成功')),
        (['A', 'E', 'B', 'F'], T('fail', '失败')),
        (['A', 'B', 'G'], T('success', '成功')),
    ]
    if narrow:
        colx = [30, 100, 170, 240]
        rowy = [40, 96, 152]
        H = 290
    else:
        colx = [44, 134, 224, 314]
        rowy = [44, 104, 164]
        H = 200
    svg = Svg(W, H, 'Step-level grouping: steps from the same environment state are compared across rollouts')
    bpos = []
    for r, (states, outcome) in enumerate(rows):
        y = rowy[r]
        svg.text(colx[0] - 30, y + 4, f'#{r + 1}', cls='t-muted', anchor='middle', size=11.5)
        for c, s in enumerate(states):
            x = colx[c]
            key = s == 'B'
            svg.add(f'<circle cx="{x}" cy="{y}" r="15" class="{"box-key" if key else "box-soft"}"/>')
            svg.text(x, y + 4.5, s, cls='t-strong' if key else '', anchor='middle', size=12.5)
            if key:
                bpos.append((x, y))
            if c:
                arrow(svg, colx[c - 1] + 16, y, x - 17, y)
        lx = colx[len(states) - 1] + 24
        svg.text(lx, y + 4.5, ('→ ' + outcome[0], '→ ' + outcome[1]), size=12)
    for (xa, ya), (xb, yb) in zip(bpos, bpos[1:]):
        svg.add(f'<path d="M{xa:.1f},{ya + 15:.1f} C{xa:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{(ya + yb) / 2:.1f} {xb:.1f},{yb - 15:.1f}" class="line l1" style="opacity:.55"/>')
    if narrow:
        tx, ty = 10, 206
        svg.text(tx, ty, T('Trajectory level: compare the outcomes of #1–#3.', '轨迹级：比较 #1–#3 的最终成败。'), size=12)
        svg.text(tx, ty + 22, T('Step level: compare the actions taken from B', '步级：比较从 B 出发的动作'), size=12)
        svg.text(tx, ty + 40, T('(B→C, B→F, B→G) by what followed them.', '（B→C、B→F、B→G）之后的结果。'), size=12)
        svg.text(tx, ty + 62, T('No critic, no extra rollouts.', '不需要 critic，也不需要额外 rollout。'), cls='t-muted', size=11.5)
        return svg
    tx = 470
    svg.text(tx, 52, T('Trajectory level', '轨迹级'), cls='t-strong', size=13)
    svg.text(tx, 70, T('compare the outcomes of #1–#3', '比较 #1–#3 的最终成败'), size=12)
    svg.text(tx, 106, T('Step level', '步级'), cls='t-strong', size=13)
    svg.text(tx, 124, T('compare actions taken from B', '比较从 B 出发的动作'), size=12)
    svg.text(tx, 141, T('(B→C, B→F, B→G) by what followed', '（B→C、B→F、B→G）之后的结果'), size=12)
    svg.text(tx, 176, T('No critic, no extra rollouts.', '不需要 critic，也不需要额外 rollout。'), cls='t-muted', size=11.5)
    return svg


def fig_scr_sft_rl(W):
    sft = dict(run(ALF, 'sft_gigpo', 'seen'))
    sftu = dict(run(ALF, 'sft_gigpo', 'unseen'))
    stages = [(T('Base', '基座'), 7.1, 2.2), (T('SFT', 'SFT'), sft[0], sftu[0])] + \
             [(T(f'RL {k}', f'RL {k} 步'), sft[k], sftu[k]) for k in (10, 20, 50, 100)]
    narrow = W < 500
    if narrow:   # horizontal grouped bars
        pitch, bh = 46, 12
        x0, x1, top = 64, W - 46, 30
        H = top + pitch * len(stages) + 26
        svg = Svg(W, H, 'ALFWorld success by stage, seen and unseen')
        legend(svg, 8, 16, [(1, 'seen'), (2, 'unseen')])
        sx = scale(0, 100, x0, x1)
        for v in range(0, 101, 25):
            svg.line(sx(v), top, sx(v), top + pitch * len(stages), 'grid' if v else 'axis')
            svg.text(sx(v), top + pitch * len(stages) + 17, str(v), cls='t-muted', anchor='middle', size=11.5)
        for i, (lab, s, u) in enumerate(stages):
            y = top + i * pitch + 8
            svg.text(x0 - 8, y + bh + 4, lab, anchor='end', size=12.5, cls='t-strong' if i == len(stages) - 1 else '')
            for j, (v, idx) in enumerate([(s, 1), (u, 2)]):
                yb = y + j * (bh + 2)
                svg.add(f'<g class="mark"><title>{esc(lab[0])} {("seen", "unseen")[j]}: {v:.1f}%</title><path class="bar s{idx}" d="{hbar(x0, yb, sx(v), bh)}"/></g>')
                svg.text(sx(v) + 5, yb + bh - 1.5, fmt(v), size=11.5)
        return svg
    H = 290
    x0, x1, y0, y1 = 40, W - 12, 40, H - 34
    svg = Svg(W, H, 'ALFWorld success by stage, seen and unseen')
    legend(svg, x0, 16, [(1, 'seen'), (2, 'unseen')])
    sy = scale(0, 100, y1, y0)
    for v in range(0, 101, 25):
        svg.line(x0, sy(v), x1, sy(v), 'grid' if v else 'axis')
        svg.text(x0 - 6, sy(v) + 4, str(v), cls='t-muted', anchor='end', size=11.5)
    gw = (x1 - x0) / len(stages)
    bw = 20
    for i, (lab, s, u) in enumerate(stages):
        cx = x0 + gw * (i + 0.5)
        svg.text(cx, y1 + 18, lab, anchor='middle', size=12.5, cls='t-strong' if i == len(stages) - 1 else '')
        for j, (v, idx) in enumerate([(s, 1), (u, 2)]):
            bx = cx - bw - 1 if j == 0 else cx + 1
            top = sy(v)
            r = min(4, (y1 - top) / 2)
            d = (f'M{bx:.1f},{y1:.1f} V{top + r:.1f} A{r},{r} 0 0 1 {bx + r:.1f},{top:.1f} H{bx + bw - r:.1f} '
                 f'A{r},{r} 0 0 1 {bx + bw:.1f},{top + r:.1f} V{y1:.1f} Z')
            svg.add(f'<g class="mark"><title>{esc(lab[0])} {("seen", "unseen")[j]}: {v:.1f}%</title><path class="bar s{idx}" d="{d}"/></g>')
            svg.text(bx + bw / 2, top - 6, fmt(v), anchor='middle', size=11)
    return svg


def fig_scr_vs_grpo(W):
    narrow = W < 500
    g_s, g_u = run(ALF, 'gigpo', 'seen'), run(ALF, 'gigpo', 'unseen')
    r_s, r_u = run(ALF, 'grpo', 'seen'), run(ALF, 'grpo', 'unseen')
    mean = lambda pts: sum(y for x, y in pts if x >= 160) / len([1 for x, y in pts if x >= 160])
    if narrow:
        H = 520
        boxA, boxB = (40, 66, W - 110, 236), (40, 316, W - 110, 486)
    else:
        H = 300
        boxA, boxB = (40, 66, W / 2 - 74, H - 34), (W / 2 + 40, 66, W - 74, H - 34)
    svg = Svg(W, H, 'ALFWorld validation success over 200 steps, step-level advantage vs GRPO')
    legend(svg, boxA[0], 16, [(1, T('step-level advantage', '步级优势')), (2, 'GRPO')])
    for box, (gs, rs), name in [(boxA, (g_s, r_s), 'seen'), (boxB, (g_u, r_u), 'unseen')]:
        band = (160, 200, (f'mean {mean(gs):.1f} vs {mean(rs):.1f}', f'均值 {mean(gs):.1f} 对 {mean(rs):.1f}'))
        line_panel(svg, box, (0, 200), (0, 100), [0, 50, 100, 150, 200], [0, 25, 50, 75, 100],
                   [(1, T('step-level', '步级'), gs), (2, 'GRPO', rs)], title=(f'valid_{name} (%)', f'valid_{name}（%）'),
                   end_labels=(name == 'seen'), band=band, xfmt=lambda v: str(int(v)),
                   point_title=lambda lab, x, y: f'{lab[0] if isinstance(lab, tuple) else lab} · step {x}: {y:.1f}%')
    return svg


def scr_vs_grpo_table():
    g = {(int(r['step'])): (r['seen'], r['unseen']) for r in ALF if r['run'] == 'gigpo'}
    r_ = {(int(r['step'])): (r['seen'], r['unseen']) for r in ALF if r['run'] == 'grpo'}
    rows = [[str(s), f'{g[s][0]} / {g[s][1]}', f'{r_[s][0]} / {r_[s][1]}'] for s in sorted(g)]
    return data_table([bi(T('Step', '步')), bi(T('Step-level (seen / unseen)', '步级优势（seen / unseen）')), 'GRPO (seen / unseen)'], rows)


def fig_scr_updates(W):
    narrow = W < 500
    four = run(ALF, 'gigpo_4upd', 'seen')
    one = [(s, v) for s, v in run(ALF, 'gigpo', 'seen') if s <= 150]
    H = 290
    box = (40, 40, W - (118 if narrow else 150), H - 34)
    svg = Svg(W, H, 'Seen success with one vs four updates per step')
    legend(svg, box[0], 16, [(1, T('4 updates / step', '每步 4 次更新')), (2, T('1 update / step', '每步 1 次更新'))])
    sx, sy = line_panel(svg, box, (0, 150), (0, 100), [0, 50, 100, 150], [0, 25, 50, 75, 100],
                        [(1, T('4 updates', '4 次'), four), (2, T('1 update', '1 次'), one)], end_labels=True,
                        xfmt=lambda v: str(int(v)), point_title=lambda lab, x, y: f'{lab[0]} · step {x}: {y:.1f}%')
    y100 = dict(one)[100]
    svg.add(f'<circle class="dot s2" cx="{sx(100):.1f}" cy="{sy(y100):.1f}" r="4"/>')
    svg.text(sx(100) + 6, sy(y100) + 16, (f'step 100: {y100:.1f}', f'第 100 步：{y100:.1f}'), cls='t-muted', size=11.5)
    svg.text(box[2], box[3] + 30, T('step', '步'), cls='t-muted', anchor='end', size=11.5)
    return svg


def fig_scr_hotpotqa(W):
    narrow = W < 500
    em_em, em_sh = run(HPQ, 'em', 'em'), run(HPQ, 'shaped', 'em')
    rq_em, rq_sh = run(HPQ, 'em', 'repeat_queries'), run(HPQ, 'shaped', 'repeat_queries')
    if narrow:
        H = 500
        boxA, boxB = (44, 66, W - 112, 226), (44, 306, W - 112, 466)
    else:
        H = 290
        boxA, boxB = (44, 66, W / 2 - 84, H - 34), (W / 2 + 44, 66, W - 84, H - 34)
    svg = Svg(W, H, 'HotpotQA: exact match and repeated queries, EM reward vs shaped reward')
    legend(svg, boxA[0], 16, [(1, T('EM reward', 'EM 奖励')), (2, T('shaped reward', '稠密奖励'))])
    line_panel(svg, boxA, (0, 200), (40, 60), [0, 100, 200], [40, 45, 50, 55, 60],
               [(1, 'EM', em_em), (2, T('shaped', '稠密'), em_sh)], title=T('Exact match (%)', 'EM（%）'),
               xfmt=lambda v: str(int(v)), point_title=lambda lab, x, y: f'step {x}: {y:.1f}%')
    line_panel(svg, boxB, (0, 200), (0, 0.2), [0, 100, 200], [0, 0.05, 0.1, 0.15, 0.2],
               [(1, 'EM', rq_em), (2, T('shaped', '稠密'), rq_sh)], title=T('Repeated queries per question', '每题重复查询次数'),
               xfmt=lambda v: str(int(v)), yfmt=lambda v: f'{v:.2f}' if v else '0',
               efmt=lambda v: f'{v:.3f}', point_title=lambda lab, x, y: f'step {x}: {y:.3f}')
    return svg


def scr_hotpotqa_table():
    em = {int(r['step']): r for r in HPQ if r['run'] == 'em'}
    sh = {int(r['step']): r for r in HPQ if r['run'] == 'shaped'}
    rows = [[str(s), em[s]['em'], sh[s]['em'], em[s]['repeat_queries'], sh[s]['repeat_queries']] for s in sorted(em)]
    return data_table([bi(T('Step', '步')), 'EM (EM reward)', bi(T('EM (shaped)', 'EM（稠密）')),
                       bi(T('Repeats (EM reward)', '重复查询（EM 奖励）')), bi(T('Repeats (shaped)', '重复查询（稠密）'))], rows)


# ----------------------------------------------------------------------------- assemble
def pair(fn, table=None):
    out = fn(LG).render('v-lg') + fn(SM).render('v-sm')
    return out + (table() if table else '')


FIGS = {
    'index.html': {
        'card-opd': lambda: fig_card_opd().render(),
        'card-scr': lambda: fig_card_scr().render(),
    },
    'projects/scaffold-opd.html': {
        'opd-pipeline': lambda: pair(fig_opd_pipeline),
        'opd-takeover': lambda: pair(fig_opd_takeover),
        'opd-methods': lambda: pair(fig_opd_methods),
        'opd-budget': lambda: pair(fig_opd_budget, opd_budget_table),
        'opd-training': lambda: pair(fig_opd_training, opd_training_table),
    },
    'projects/stepcredit-rl.html': {
        'scr-pipeline': lambda: pair(fig_scr_pipeline),
        'scr-steplevel': lambda: pair(fig_scr_steplevel),
        'scr-sft-rl': lambda: pair(fig_scr_sft_rl),
        'scr-vs-grpo': lambda: pair(fig_scr_vs_grpo, scr_vs_grpo_table),
        'scr-updates': lambda: pair(fig_scr_updates),
        'scr-hotpotqa': lambda: pair(fig_scr_hotpotqa, scr_hotpotqa_table),
    },
}


def main():
    for page, figs in FIGS.items():
        path = ROOT / page
        src = path.read_text(encoding='utf-8')
        for name, make in figs.items():
            pat = re.compile(rf'(<!-- fig:{re.escape(name)} -->).*?(<!-- /fig:{re.escape(name)} -->)', re.S)
            if not pat.search(src):
                raise SystemExit(f'{page}: marker for {name} not found')
            src = pat.sub(lambda m: m.group(1) + make() + m.group(2), src)
        path.write_text(src, encoding='utf-8')
        print(f'{page}: {len(figs)} figures')


if __name__ == '__main__':
    main()
