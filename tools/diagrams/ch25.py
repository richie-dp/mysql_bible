#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 25 章配图：并行复制与延迟治理"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 25-1
def fig1():
    c = Canvas(960, 560,
               title="图 25-1　延迟的本质：进水管比出水管粗，积压只会单调增长",
               subtitle="延迟读数是一个积分量 Q(t)，不是一个状态量；决定它涨不涨的是斜率 λ − μ")

    # 主库：进水管
    c.container(50, 86, 250, 190, "主库 source")
    c.box(70, 134, 210, 52, "M 个事务同时在跑", "并发写入 × 组提交批",
          accent=BLUE, size=13, sub_size=10)
    c.box(70, 196, 210, 52, "λ = M / t_exec", "每秒进队的事务数",
          accent=BLUE, size=13, sub_size=10)

    # 积压
    c.container(340, 86, 280, 190, "relay log 里的积压")
    c.cyl(380, 134, 200, 110, "积压 Q(t)", "λ > μ 时只涨不落", accent=RED)

    # 从库：出水管
    c.container(660, 86, 250, 190, "从库 replica")
    c.box(680, 134, 210, 52, "N 个 worker", "真正并行的 N_eff ≤ N",
          accent=GREEN, size=13, sub_size=10)
    c.box(680, 196, 210, 52, "μ = N_eff / t_apply", "每秒回放完的事务数",
          accent=GREEN, size=13, sub_size=10)

    c.arrow(300, 160, 336, 160, color=BLUE, label="λ", label_dy=-10)
    c.arrow(620, 160, 656, 160, color=GREEN, label="μ", label_dy=-10)

    # 不等式
    c.box(50, 300, 430, 120,
          "M × t_apply > N × t_exec 时积压增长",
          "Q(t) = Q₀ + (λ − μ)·t，延迟读数 L ≈ Q / λ",
          accent=RED, size=14, sub_size=11)

    # 延迟曲线
    c.arrow(520, 470, 520, 290, color=SLATE, end=True)
    c.arrow(520, 470, 892, 470, color=SLATE, end=True)
    c.text(530, 302, "积压 Q", size=10, fill=SUB)
    c.text(884, 492, "时间 t →", size=10, fill=SUB, anchor="end")

    curve = [(524, 462), (570, 452), (620, 438), (670, 418),
             (720, 390), (770, 354), (820, 320), (866, 296)]
    c.arrow(curve, color=RED, width=2.4)
    c.text(530, 336, "斜率 = λ − μ，恒为正", size=11, fill=RED)
    c.text(530, 356, "截距由三次 fsync 决定", size=11, fill=SUB)

    c.text(50, 492, "截距让延迟永远不会是 0；斜率决定它会不会涨到三个小时。前者是物理限制，后者是容量问题。",
           size=11, fill=INK)

    c.legend(52, 520, [(BLUE, "主库产出事务", None),
                       (GREEN, "从库消费事务", None)])
    c.legend(560, 520, [(RED, "积压增长（危险）", None),
                        (SLATE, "坐标轴", None)])
    return c.save(os.path.join(OUT, "ch25-fig1.svg"))


# ---------------------------------------------------------------- 图 25-2
def fig2():
    c = Canvas(960, 700,
               title="图 25-2　同一批 8 个事务，三代策略给出的可并行范围",
               subtitle="判断依据从库名 → 组提交依赖序 → 行级写集哈希；颜色相同即落在同一个 worker")

    W = [BLUE, ORANGE, PURPLE, GREEN]
    TX = ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"]

    # 每行：(容器标签, 左侧三行说明, [(事务下标, 副标题, worker 下标)])
    lanes = [
        ("① DATABASE —— 分发键是库名（5.6）",
         ["全部事件都是 order_db", "哈希只有一个取值", "并行度上限 = 活跃库数"],
         [(i, "order_db", 0) for i in range(8)],
         True),
        ("② LOGICAL_CLOCK —— 分发键是 last_committed（5.7）",
         ["同组的事务同时持锁", "→ 写集必然不重叠", "并行度上限 = 组提交批大小"],
         [(0, "lc=1", 0), (1, "lc=2", 1), (2, "lc=2", 1), (3, "lc=2", 1),
          (4, "lc=5", 2), (5, "lc=5", 2), (6, "lc=7", 3), (7, "lc=7", 3)],
         True),
        ("③ WRITESET —— 分发键是行级写集哈希（8.0）",
         ["写集不重叠即可并行", "不受组提交边界约束", "并行度上限 = 行冲突度"],
         [(0, "r17", 0), (1, "r42", 1), (2, "r88", 0), (3, "r03", 2),
          (4, "r61", 3), (5, "r42", 1), (6, "r77", 3), (7, "r03", 2)],
         False),
    ]

    top = [86, 276, 466]
    for (label, notes, chips, draw_groups), y in zip(lanes, top):
        c.container(50, y, 860, 150, label)
        for k, note in enumerate(notes):
            c.text(64, y + 56 + k * 20, note, size=10, fill=SUB)

        xs = [250 + i * 82 for i in range(len(chips))]
        if draw_groups:
            # 把连续的同一个 worker 画成一个分组底色
            i = 0
            while i < len(chips):
                j = i
                while j + 1 < len(chips) and chips[j + 1][2] == chips[i][2]:
                    j += 1
                col = W[chips[i][2]]
                gx = xs[i] - 6
                gw = xs[j] + 64 + 6 - gx
                c.rect(gx, y + 54, gw, 70, fill=TINT[col], stroke=BORDER[col],
                       sw=1.2, r=8)
                c.text(gx + 8, y + 65, f"worker {chips[i][2] + 1}",
                       size=9, fill=col, weight=600)
                i = j + 1

        for (idx, sub, wk), x in zip(chips, xs):
            col = W[wk]
            if draw_groups:
                c.box(x, y + 68, 64, 48, TX[idx], sub, size=11, sub_size=9)
            else:
                c.box(x, y + 68, 64, 48, TX[idx], sub, accent=col,
                      size=11, sub_size=9)

    c.text(50, 646, "前两行：同色块之间是一条串行的依赖链，worker 再多也只能一段一段往前走。",
           size=11, fill=INK)
    c.text(50, 670, "第三行：颜色的分布不再按事务顺序排列，可并行的边界从\"提交组\"下移到\"行的哈希\"。",
           size=11, fill=INK)
    return c.save(os.path.join(OUT, "ch25-fig2.svg"))


# ---------------------------------------------------------------- 图 25-3
def fig3():
    c = Canvas(960, 590,
               title="图 25-3　replica_preserve_commit_order=ON：并行回放、串行提交",
               subtitle="worker 改完行、拿着锁，却必须等序位在它前面的事务先提交——整体推进由最慢的那个决定")

    c.text(50, 96, "coordinator 按依赖关系分发事务，分发时并不知道哪个 worker 跑得快", size=11, fill=SUB)

    rows = [
        ("worker 1", [(170, 180, "T1 执行", ORANGE), (362, 50, "提交", GREEN)], 120),
        ("worker 2", [(170, 100, "T2 执行", ORANGE), (282, 130, "等 T1 提交", RED),
                      (424, 50, "提交", GREEN)], 206),
        ("worker 3", [(170, 130, "T3 执行", ORANGE), (312, 162, "等 T2 提交", RED),
                      (486, 50, "提交", GREEN)], 292),
    ]
    for name, segs, y in rows:
        c.pill(50, y, 96, 44, name, accent=SLATE, size=11)
        for x, w, label, col in segs:
            c.box(x, y, w, 46, label, accent=col, size=12)

    # 提交顺序的传递：T1 提交 → T2 才能提交 → T3 才能提交
    c.arrow(387, 168, 387, 202, color=RED, width=1.4)
    c.arrow(449, 254, 449, 288, color=RED, width=1.4)

    c.text(556, 322, "Exec_Source_Log_Pos 到这里才前移", size=11, fill=SUB)

    c.text(50, 372, "三个事务的执行时长接近，但提交被串成一条链：落后一个就全体停摆，其余 worker 的执行时间全部沉没。",
           size=11, fill=INK)

    c.mono_box(50, 392, 470, 82, [
        "| 14 | system user | Waiting for dependent |",
        "| 15 | system user | transaction to commit  |",
        "| 16 | system user | Executing event       |",
    ], title="SHOW PROCESSLIST")

    c.box(540, 392, 370, 82, "卡点在提交，不在执行",
          "并行是生效的，吃掉并行度的是提交序", accent=RED, size=13, sub_size=10)

    c.legend(50, 500, [(ORANGE, "执行事务体（真并行）", None),
                       (RED, "等前序提交（并行度被吃掉的地方）", None),
                       (GREEN, "提交并推进低水位", None)])
    return c.save(os.path.join(OUT, "ch25-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
