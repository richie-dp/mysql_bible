#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 17 章配图：隔离级别与 MVCC 可见性"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *  # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 17-1
def fig1():
    c = Canvas(960, 720,
               title="图 17-1　ReadView 的四个字段，在 trx_id 数轴和版本链上切出「能看」与「不能看」",
               subtitle="视图由 trx 906 建立，活跃集合 m_ids = {905, 907, 909}；这一行先后被 903 / 905 / 911 / 912 改过")

    # ---- 数轴
    c.container(40, 86, 880, 182, "trx_id 数轴：三个区间，三种默认结论")

    c.rect(80, 184, 220, 22, fill="#ecfdf5", stroke="#a7f3d0", sw=1, r=3)
    c.rect(300, 184, 350, 22, fill="#fffbeb", stroke="#fde68a", sw=1, r=3)
    c.rect(650, 184, 240, 22, fill="#fef2f2", stroke="#fecaca", sw=1, r=3)

    # m_ids 括号
    c.els.append(f'<path d="M 300 172 L 300 158 L 580 158 L 580 172" fill="none" '
                 f'stroke="{ORANGE}" stroke-width="1.4"/>')
    for x in (300, 440, 580):
        c.els.append(f'<line x1="{x}" y1="158" x2="{x}" y2="184" '
                     f'stroke="{ORANGE}" stroke-width="1.4" stroke-dasharray="3,3"/>')
    c.text(300, 148, "m_ids = {905, 907, 909}　建立视图这一刻还活着的事务", size=11,
           fill=ORANGE, weight=600)

    ticks = [(903, 160), (905, 300), (906, 370), (907, 440), (909, 580), (910, 650)]
    for tid, x in ticks:
        c.els.append(f'<line x1="{x}" y1="206" x2="{x}" y2="214" stroke="{SLATE}" stroke-width="1.2"/>')
        c.text(x, 230, str(tid), size=10, fill=SUB, anchor="middle", mono=True)

    c.text(90, 252, "① 已结束 → 直接可见", size=10.5, fill=GREEN)
    c.text(310, 252, "③④ 还活着 → 看在不在 m_ids", size=10.5, fill="#b45309")
    c.text(660, 252, "⑤ 视图之后才出生 → 不可见", size=10.5, fill=RED)

    # ---- 四字段
    fields = [
        (40, "creator_trx_id = 906", "等于它的版本永远可见", BLUE),
        (265, "min_trx_id = 905", "源码字段 m_up_limit_id", GREEN),
        (490, "max_trx_id = 910", "下一个待分配 · m_low_limit_id", RED),
        (715, "m_ids = {905,907,909}", "建视图时的活跃读写事务", ORANGE),
    ]
    for x, t, s, acc in fields:
        c.box(x, 300, 205, 84, t, s, accent=acc, size=12, sub_size=10, mono=True)

    # ---- 版本链
    chain = [
        (50, "当前版本", "DB_TRX_ID = 912", RED, "不可见：912 ≥ max"),
        (270, "undo v2", "由 trx 911 写入", RED, "不可见：911 ≥ max"),
        (490, "undo v1", "由 trx 905 写入", RED, "不可见：905 在 m_ids"),
        (710, "undo v0 链尾", "由 trx 903 写入", GREEN, "可见：903 < min"),
    ]
    for x, t, s, acc, verdict in chain:
        c.box(x, 452, 180, 84, t, s, accent=acc, size=12, sub_size=10)
        c.text(x + 90, 558, verdict, size=10.5, fill=acc, anchor="middle", weight=600)

    for x in (230, 450, 670):
        c.arrow(x, 494, x + 40, 494, color=ORANGE, label="回溯", label_dy=-7)

    c.text(40, 600, "读到的是 v0：这一版在视图建立前就已提交，于是沿链走三步、拼三次，返回它的值。",
           size=11.5, fill=INK)
    c.text(40, 624, "链上每一版都要过一次「六个情形」的判断——判断的是版本头的 trx_id，不是行本身。",
           size=11.5, fill=SUB)

    c.legend(40, 654, [(GREEN, "可见，返回这一版", None),
                       (RED, "不可见，沿 DB_ROLL_PTR 回溯", None),
                       (ORANGE, "建视图时的活跃集合 / 指针", "4,3")])
    return c.save(os.path.join(OUT, "ch17-fig1.svg"))


# ---------------------------------------------------------------- 图 17-2
def fig2():
    c = Canvas(960, 790,
               title="图 17-2　可见性判断的完整决策树：四个判断，六个出口",
               subtitle="顺序不能换：先认「自己」，再认「比我老」，最后才查活跃集合——换成源码以外的顺序，结论会错")

    dx, dw, dh = 290, 340, 90
    dys = [150, 290, 430, 570]
    labels = [
        "DB_TRX_ID = creator ?",
        "DB_TRX_ID < min_trx_id ?",
        "DB_TRX_ID >= max_trx_id ?",
        "DB_TRX_ID 在 m_ids 中 ?",
    ]
    for cy, lb in zip(dys, labels):
        c.diamond(dx, cy, dw, dh, lb, accent=BLUE, size=12)

    for i in range(3):
        y1 = dys[i] + dh / 2
        y2 = dys[i + 1] - dh / 2
        c.arrow(dx, y1, dx, y2, color=SLATE, label="否", label_side="right")

    leaves = [
        (150, "可见　自己写的那一版", "creator 无需查 m_ids，直接放行", GREEN),
        (290, "可见　视图建立前已结束", "比 min 小 = 提交或回滚都已落定", GREEN),
        (430, "不可见 → 回溯", "视图建立后才分配，肯定没提交", RED),
        (555, "不可见 → 回溯", "建立视图时它还活着，可能没提交", RED),
    ]
    for cy, t, s, acc in leaves:
        c.arrow(dx + dw / 2, cy, 520, cy, color=acc, label="是")
        c.box(520, cy - 32, 400, 64, t, s, accent=acc, size=13, sub_size=10)

    # 第四条判断的「否」分支
    c.arrow([(dx, 615), (dx, 660), (520, 660)], color=GREEN, label="否",
            label_side="right")
    c.box(520, 628, 400, 64, "可见　已提交", "在 [min, max) 之间，又不在 m_ids 里",
          accent=GREEN, size=13, sub_size=10)

    c.rect(40, 706, 880, 66, fill="#fef2f2", stroke="#fecaca", sw=1.2, r=8)
    c.text(56, 730, "走「不可见」的两条分支：读 DB_ROLL_PTR 指向的上一段 undo，用它的 trx_id 重跑这棵树。",
           size=11.5, fill=RED, weight=600)
    c.text(56, 754, "走到 roll_ptr = NULL 仍不可见，或取到的版本带 delete-mark → 这行对本视图不存在。",
           size=11, fill="#7f1d1d")
    return c.save(os.path.join(OUT, "ch17-fig2.svg"))


# ---------------------------------------------------------------- 图 17-3
def fig3():
    c = Canvas(960, 780,
               title="图 17-3　RR 下幻读重现：快照读看不见的行，当前读能改，改完就看得见了",
               subtitle="三个会话，同一张 order_charge；A 的两次统计之间只加了一条 UPDATE，总额差了 370,000")

    lanes = [
        (80, 280, 220, "会话 A　业务事务（RR）", BLUE),
        (400, 260, 530, "会话 B　调账写入（自动提交）", TEAL),
        (700, 220, 810, "会话 C　新连接（对照）", PURPLE),
    ]
    for x, w, cx, name, acc in lanes:
        c.box(x, 84, w, 50, name, accent=acc, size=12)
        c.els.append(f'<line x1="{cx}" y1="134" x2="{cx}" y2="660" '
                     f'stroke="{LINE}" stroke-width="1.2" stroke-dasharray="5,5"/>')

    c.arrow(50, 150, 50, 640, color=SLATE)
    c.text(58, 128, "时间", size=11, fill=SUB)

    steps = [
        (160, 80, 280, "BEGIN; SELECT SUM(amount)", "建立 V1：99031 还不在里面", BLUE),
        (245, 400, 260, "INSERT ... (99031, 370000); COMMIT", "一笔调账，业务上完全合法", TEAL),
        (325, 700, 220, "SELECT * WHERE id = 99031", "1 行：数据真的在库里", PURPLE),
        (405, 80, 280, "UPDATE ... SET reconciled = 1", "当前读命中：1 row affected", RED),
        (490, 80, 280, "SELECT SUM(amount)（原样重跑）", "多出 370,000：幻读出现", RED),
        (570, 80, 280, "COMMIT", "释放视图，purge 水位前移", SLATE),
    ]
    for y, x, w, t, s, acc in steps:
        c.box(x, y, w, 60, t, s, accent=acc, size=10.5, sub_size=10.5, mono=acc is not SLATE)

    # B 提交 → C 看得见
    c.arrow([(660, 268), (680, 268), (680, 355), (700, 355)], color=PURPLE)

    # A 的视图存活区间
    c.rect(80, 288, 280, 84, fill=BG, stroke=LINE, sw=1.2, r=8, dash="5,4")
    c.text(100, 314, "V1 存活中", size=11, fill=SUB, weight=600)
    c.text(100, 336, "RR 的视图直到 COMMIT 才释放", size=10.5, fill=SUB)
    c.text(100, 356, "B 的提交正好落在这个窗口里", size=10.5, fill=SUB)

    c.rect(40, 650, 880, 56, fill="#fef2f2", stroke="#fecaca", sw=1.2, r=8)
    c.text(56, 674, "④ 是全章的靶心：这一行在 A 的视图里不存在，A 的当前读却必须改到它；改完它的 DB_TRX_ID 变成 A 自己，",
           size=11, fill=RED, weight=600)
    c.text(56, 694, "可见性判断第 2 条直接放行，于是它在 ⑤ 里凭空出现——两条规则各自都对，接缝上没有不变量。",
           size=11, fill="#7f1d1d")

    c.text(40, 732, "C 全程只做一件事：证明这条记录确实提交了。所以 A 的「看不见」不是数据丢了，是它的视图里没有这一版。",
           size=11, fill=SUB)
    c.text(40, 754, "把 A 的级别改成 RC 重跑，① 和 ⑤ 的差额一样在——RC 连「两次快照读结果相同」都不保证。",
           size=11, fill=SUB)
    return c.save(os.path.join(OUT, "ch17-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
