"""The site's figures: the final version of each, and the data tables shown under some of them.

Every figure went through three rounds in tools/lab/ (r1_*.py, r2_*.py, r3.py). Each round drew an aesthetic and an
innovative version starting from the previous round's pick; tools/lab/rounds.py records the picks and shows every
version side by side. The finals below are the round-3 picks, imported from the round modules so that each drawing
exists in exactly one place. (The previous generation of figures is kept in tools/lab/v2/.)
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
for sub in ('lab', 'lab/v2'):
    p = str(HERE / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

from figlib import ALF, HPQ, OPD, T, bi, data_table  # noqa: E402
import r3  # noqa: E402
import figures_v2 as V2  # noqa: E402

PICKS3 = {'card-opd': 'aes', 'card-scr': 'aes', 'opd-takeover': 'aes', 'scr-steplevel': 'inno',
          'opd-pipeline': 'aes', 'scr-pipeline': 'aes', 'opd-methods': 'aes', 'opd-budget': 'aes', 'opd-training': 'inno',
          'opd-compute': 'aes', 'scr-sft-rl': 'aes', 'scr-vs-grpo': 'aes', 'scr-updates': 'inno', 'scr-hotpotqa': 'aes'}


def final(name):
    return (r3.AES if PICKS3[name] == 'aes' else r3.INNO)[name]


def signed(v, nd=1):
    return f'{v:+.{nd}f}'.replace('-', '−')


# ----------------------------------------------------------------------------- data tables
def opd_budget_table():
    b = OPD['budget']
    rows = [[f'{t:,}', f'{o:.1f}', f'{r:.1f}', f'{signed(g, 2)} ± {s:.2f}', f'{fo:.1f} / {ft:.1f}']
            for t, o, r, g, s, fo, ft in zip(b['tokens'], b['opd_40'], b['takeover_40'], b['gap_40'], b['gap_se_40'],
                                             b['aime_finished_opd_40'], b['aime_finished_takeover_40'])]
    return data_table([bi(T('Budget (tokens)', '预算（token）')), 'OPD', 'Scaffold-OPD', bi(T('Paired gap', '配对差')),
                       bi(T('AIME finished, % (OPD / Scaffold-OPD)', '写完的 AIME 回答，%（OPD / Scaffold-OPD）'))], rows)


def opd_training_table():
    tr = OPD['train']
    t = tr['takeover']
    rec = {s: (l, r, tt) for s, l, r, tt in zip(t['step'], t['response_length'], t['teacher_token_ratio'], t['teacher_tokens_per_answer'])}
    o = dict(zip(tr['opd']['step'], tr['opd']['response_length']))
    rows = []
    for s in range(5, 61, 5):
        l, r, tt = rec[s]
        rows.append([str(s), f'{l:,.0f}', f'{o[s]:,.0f}', f'{tt:,.0f}' if tt is not None else '—', f'{100 * r:.1f}%'])
    return data_table([bi(T('Step', '步')), bi(T('Scaffold-OPD length', 'Scaffold-OPD 长度')), bi(T('OPD length', 'OPD 长度')),
                       bi(T('Teacher tokens per answer', '每条回答的老师 token')), bi(T('Teacher share', '老师占比'))], rows,
                      summary=T('Data (raw values every 5 steps)', '数据（每 5 步的原始值）'))


def opd_compute_table():
    g, p = OPD['gpu_hours']['pipeline'], OPD['pipeline_avg4']
    c1 = g['sft_incl_teacher_data']
    rows = [[bi(T('Base', '基座')), '0', f'{p["base"]:.1f}'],
            [bi(T('+ SFT (incl. teacher solutions)', '+ SFT（含老师解答生成）')), f'{c1:.1f}', f'{p["sft"]:.1f}'],
            [bi(T('+ Scaffold-OPD, 40 steps', '+ Scaffold-OPD，40 步')), f'{c1 + g["takeover_40"]:.1f}', f'{p["takeover_40"]:.1f}'],
            [bi(T('+ GRPO on failures, 30 steps', '+ 错题回流 GRPO，30 步')), f'{c1 + g["takeover_40"] + g["grpo_30"]:.1f}', f'{p["grpo_30"]:.1f}'],
            [bi(T('Scaffold-OPD alone, 40 steps', '只做 Scaffold-OPD，40 步')), f'{OPD["gpu_hours"]["takeover_40"]:.1f}', f'{OPD["eval_avg4"]["takeover_40"]:.1f}']]
    return data_table([bi(T('Route', '路线')), bi(T('Cumulative GPU-h', '累计卡时')), bi(T('Average', '平均'))], rows)


def scr_sft_rl_table():
    rows = []
    for fam in V2.FAM_ORDER:
        cells = [bi(V2.FAM_NAMES[fam])]
        for split in ('seen', 'unseen'):
            (sa, n), (sb, _) = V2.family_counts('sft', split)[fam], V2.family_counts('sft_gigpo_step100', split)[fam]
            cells.append(f'{sa}/{n} → {sb}/{n}')
        rows.append(cells)
    return data_table([bi(T('Task family', '任务类型')), 'seen', 'unseen'], rows)


def scr_vs_grpo_table():
    g = {int(x['step']): (x['seen'], x['unseen']) for x in ALF if x['run'] == 'gigpo'}
    r_ = {int(x['step']): (x['seen'], x['unseen']) for x in ALF if x['run'] == 'grpo'}
    rows = [[str(s), f'{g[s][0]} / {g[s][1]}', f'{r_[s][0]} / {r_[s][1]}'] for s in sorted(g)]
    return data_table([bi(T('Step', '步')), 'StepCredit-RL (seen / unseen)', 'GRPO (seen / unseen)'], rows)


def scr_updates_table():
    f = {int(x['step']): x for x in ALF if x['run'] == 'gigpo_4upd'}
    o = {int(x['step']): x for x in ALF if x['run'] == 'gigpo' and int(x['step']) <= 150}
    rows = []
    for s in sorted(set(f) | set(o)):
        a = f'{f[s]["seen"]} ({f[s]["hours"]} h)' if s in f else '—'
        b = f'{o[s]["seen"]} ({o[s]["hours"]} h)' if s in o else '—'
        rows.append([str(s), a, b])
    return data_table([bi(T('Step', '步')), bi(T('4 updates: seen (hours)', '4 次更新：seen（小时）')), bi(T('1 update: seen (hours)', '1 次更新：seen（小时）'))], rows)


def scr_hotpotqa_table():
    em = {int(x['step']): x for x in HPQ if x['run'] == 'em'}
    sh = {int(x['step']): x for x in HPQ if x['run'] == 'shaped'}
    rows = [[str(s), em[s]['em'], sh[s]['em'], em[s]['f1'], sh[s]['f1'], em[s]['repeat_queries'], sh[s]['repeat_queries']] for s in sorted(em)]
    return data_table([bi(T('Step', '步')), 'EM (EM reward)', bi(T('EM (shaped)', 'EM（稠密）')), 'F1 (EM reward)', bi(T('F1 (shaped)', 'F1（稠密）')),
                       bi(T('Repeats (EM reward)', '重复查询（EM 奖励）')), bi(T('Repeats (shaped)', '重复查询（稠密）'))], rows)


TABLES = {'opd-budget': opd_budget_table, 'opd-training': opd_training_table, 'opd-compute': opd_compute_table,
          'scr-sft-rl': scr_sft_rl_table, 'scr-vs-grpo': scr_vs_grpo_table, 'scr-updates': scr_updates_table,
          'scr-hotpotqa': scr_hotpotqa_table}
FIGS = {name: (final(name), TABLES.get(name)) for name in PICKS3}
# 2026-11-17: the eight data charts went through a new cycle of three rounds (tools/lab/c1.py, c2.py, c3.py; picks in
# tools/lab/c_final.py). Figure 6 (opd-compute) restarted from the 11-15 drawing, which the user preferred.
# 2026-11-17 (second cycle, English only): three more rounds in tools/lab/d1.py, d2.py, d3.py; picks in tools/lab/d_final.py.
import d_final  # noqa: E402
for _name, _fn in d_final.FINAL.items():
    FIGS[_name] = (_fn, TABLES.get(_name))
CARDS = {'card-opd', 'card-scr'}
DRAWIO_FIGS = {'opd-takeover', 'scr-steplevel', 'opd-pipeline', 'scr-pipeline', 'card-opd', 'card-scr'}   # drawn in tools/drawio (2026-11-17)
WIDE = {'opd-takeover': 880, 'scr-steplevel': 880}   # framework figures are drawn wider than the charts
