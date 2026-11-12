#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 21 章配图：长事务的三维评估与大事务拆分模式"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *  # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 21-1
def fig1():
    c = Canvas(960, 640,
               title="图 21-1　长事务的三维评估：时长、undo/水位、影响面",
               subtitle="任何一维到 2 分都不能按 P2 处理；undo 这一维看的是「是不是最老 ReadView」，不是改了多少行")

    panels = [
        (40, BLUE, "① 持续时长", "trx_started → NOW()", [
            ("0 分 · 秒级", "单语句事务，正常"),
            ("1 分 · 少于 10 分钟", "开始值得看一眼"),
            ("2 分 · 10 分钟及以上", "进入长事务区间"),
        ]),
        (344, ORANGE, "② undo 持有 / 水位", "行数只是估值，水位才是判据", [
            ("0 分 · 无持有", "不写 undo，也不是最老视图"),
            ("1 分 · 有修改 / 持锁", "按行数估，不按字节"),
            ("2 分 · 最老 ReadView", "0 行修改也可能是 2 分"),
        ]),
        (648, RED, "③ 影响面", "锁了谁、挡了谁、拖了谁", [
            ("0 分 · 无人等待", "锁着，但没人排队"),
            ("1 分 · 锁住热点行", "等待在积累"),
            ("2 分 · 已阻塞", "会话 / DDL / 从库回放"),
        ]),
    ]

    for x, accent, head, sub, rows in panels:
        c.rect(x, 84, 264, 286, fill="#ffffff", stroke="#e5e7eb", sw=1.2, r=10)
        c.text(x + 16, 112, head, size=14, fill=accent, weight=700)
        c.text(x + 16, 132, sub, size=10.5, fill=SUB)
        c.rect(x + 16, 142, 232, 1, fill="#e5e7eb", stroke="none", r=0)

        for i, (t, s) in enumerate(rows):
            y = 154 + i * 68
            if i == 2:
                c.box(x + 16, y, 232, 56, t, s, accent=RED, size=12.5, sub_size=10)
            else:
                c.box(x + 16, y, 232, 56, t, s, accent=None, size=12.5, sub_size=10)

    # ---- 判定表
    c.text(40, 404, "三维打分与判定", size=13, fill=INK, weight=700)

    cols = [(40, 310, "典型组合"), (350, 80, "时长"),
            (430, 250, "undo / 水位"), (680, 100, "影响面"),
            (780, 140, "判定")]
    c.rect(40, 414, 880, 32, fill="#f1f5f9", stroke="#e5e7eb", sw=1, r=4)
    for x, w, label in cols:
        c.text(x + 10, 435, label, size=11, fill=SUB, weight=600)

    rows = [
        ("只读对账事务，10 分钟", "2", "2（最老视图，0 行修改）", "0", "P0", RED),
        ("状态回刷，300 万行，40 分钟", "2", "2（自己产生 300 万条 undo）", "2", "P0", RED),
        ("空闲事务，12 分钟，持 MDL 挡 DDL", "2", "1（持锁，但不是水位）", "2", "P0", RED),
        ("普通订单查询，90 秒", "1", "0（不是最老视图）", "0", "P2", GREEN),
    ]
    for i, (combo, t, u, im, verdict, acc) in enumerate(rows):
        y = 446 + i * 34
        bg = "#fef2f2" if verdict == "P0" else "#ffffff"
        c.rect(40, y, 880, 34, fill=bg, stroke="#e5e7eb", sw=1, r=4)
        if verdict == "P0":
            c.rect(40, y, 4, 34, fill=RED, stroke="none", r=2)
        c.text(52, y + 22, combo, size=11, fill=INK, weight=500)
        c.text(360, y + 22, t, size=11, fill=SUB)
        c.text(440, y + 22, u, size=11, fill=SUB)
        c.text(690, y + 22, im, size=11, fill=SUB)
        c.text(790, y + 22, verdict, size=12, fill=acc, weight=700)

    c.text(40, 608,
           "判定：任一维 2 分且总分 ≥ 4 → P0；总分 2~3 → P1；≤ 1 → P2。水位维的 2 分不看修改行数。",
           size=11, fill=SUB)

    return c.save(os.path.join(OUT, "ch21-fig1.svg"))


# ---------------------------------------------------------------- 图 21-2
def fig2():
    c = Canvas(960, 700,
               title="图 21-2　同一份 300 万行，四种切法：时间轴与资源形态",
               subtitle="目标都是 4 小时跑完；差别在「每批是否可独立提交」和「前提条件是否成立」")

    c.text(40, 86, "同一份 300 万行 · 同一个 4 小时窗口 · 同一个主库",
           size=11, fill=SUB, weight=500)

    def lane(y, accent, title, l2, l3, note_color=SUB):
        c.rect(40, y, 880, 1.2, fill="#e5e7eb", stroke="none", r=0)
        c.rect(40, y + 80, 880, 1.2, fill="#e5e7eb", stroke="none", r=0)
        c.rect(40, y + 8, 6, 64, fill=accent, stroke="none", r=3)
        c.text(60, y + 28, title, size=13, fill=INK, weight=700)
        c.text(60, y + 48, l2, size=10.5, fill=SUB)
        c.text(60, y + 66, l3, size=10.5, fill=note_color)
        c.rect(264, y + 50, 640, 1.5, fill="#e5e7eb", stroke="none", r=0)

    # ① 主键区间
    lane(104, BLUE, "① 按主键区间", "WHERE id BETWEEN ? AND ?",
         "前提：主键单调，UUID 失效", RED)
    c.text(280, 120, "id 升序，每批 50 万", size=9.5, fill=SUB)
    for i in range(6):
        c.box(280 + i * 104, 128, 64, 28, "%d/6" % (i + 1),
              accent=BLUE, size=10)

    # ② 时间窗口
    lane(224, BLUE, "② 按时间窗口", "WHERE create_time >= ? AND < ?",
         "前提：有索引，历史不再变")
    c.text(280, 240, "每天行数不同，批次宽度也不同", size=9.5, fill=SUB)
    spans = [(280, 100, "11-01"), (392, 70, "11-02"), (474, 120, "11-03"),
             (606, 80, "11-04"), (698, 100, "11-05"), (810, 80, "11-06")]
    for x, w, label in spans:
        c.box(x, 248, w, 28, label, accent=BLUE, size=9.5)

    # ③ 异步化
    lane(344, SLATE, "③ 异步化", "写任务表 + 消费者分批",
         "代价：最终一致，消费要幂等")
    c.box(272, 364, 110, 36, "task 表", "PENDING", accent=PURPLE,
          size=11, sub_size=9.5)
    c.arrow(382, 382, 444, 382, color=SLATE, dash="5,4", label="消费")
    for i in range(5):
        c.box(450 + i * 80, 368, 56, 28, "批%d" % (i + 1),
              accent=SLATE, size=10)
    c.text(852, 384, "最终一致", size=10, fill=GREEN, weight=600)

    # ④ 状态机
    lane(464, GREEN, "④ 状态机推进", "每批推进一个状态位",
         "天然幂等，适合数据迁移")
    labels = ["0→1", "1→2", "2→3", "3→4", "4→5"]
    for i, label in enumerate(labels):
        c.box(280 + i * 100, 488, 76, 28, label, accent=GREEN, size=10)
    c.pill(800, 486, 110, 24, "失败可重跑", accent=GREEN, size=10)
    c.text(800, 528, "同一状态不重复处理", size=9.5, fill=SUB)

    # ---- 分批大小推导
    c.rect(40, 584, 880, 92, fill="#f8fafc", stroke="#e2e8f0", sw=1.2, r=10)
    c.text(60, 610, "分批大小不是拍 500 或 1000，是从三个上限反推",
           size=12.5, fill=INK, weight=700)
    c.text(60, 634,
           "B = B0 × (t_budget / t0)      "
           "t_budget = min(innodb_lock_wait_timeout × 0.1, 应用超时, T / 批次数 − 批间停顿)",
           size=10.5, fill=INK, mono=True)
    c.text(60, 656,
           "先跑一批 B0 量出 t0；批次数 = ceil(N / B)；批间停顿要让从库回放跟得上。",
           size=10.5, fill=SUB)

    return c.save(os.path.join(OUT, "ch21-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
