#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 16 章配图：ACID 的分工与事务时间线"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *  # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 16-1
def fig1():
    c = Canvas(960, 600, title="图 16-1　ACID 四个字母，四笔不同的账",
               subtitle="A / D / I 由 InnoDB 的组件兑现；C 的虚线框那一半，只有写代码的人能兑现")

    c.text(60, 92, "字母", size=11, fill=SUB, weight=600)
    c.text(180, 92, "真正买单的组件", size=11, fill=SUB, weight=600)
    c.text(700, 92, "它不成立时，坏在哪", size=11, fill=SUB, weight=600)

    rows = [
        (112, "A", "原子性", ORANGE,
         [("undo log", "记前镜像，回滚时按 undo_no 逆序撤销", None, False)],
         ("撤销本身也要写 redo", "大事务回滚可能比执行更久")),
        (216, "D", "持久性", GREEN,
         [("redo log", "提交时 fsync，组提交摊薄", None, False),
          ("doublewrite", "防 16KB 页被写坏一半", None, False)],
         ("只防页被撕，不防日志没刷", "两层缺一层，D 都不成立")),
        (320, "I", "隔离性", BLUE,
         [("行锁 / Next-Key", "写写互斥，当前读走这条", None, False),
          ("MVCC + ReadView", "读写不互斥，快照读走这条", None, False)],
         ("锁管写写，版本管读写", "两套机制共用一个 trx_id")),
        (424, "C", "一致性", RED,
         [("约束", "PK · UK · FK · CHECK", None, False),
          ("应用逻辑与边界", "跨行、跨表、跨服务", RED, True)],
         ("约束只覆盖它看得见的", "其余不变式靠事务边界")),
    ]

    for y, letter, name, acc, mechs, note in rows:
        c.box(60, y, 84, 64, letter, name, accent=acc, size=22, sub_size=12)
        c.arrow(144, y + 32, 180, y + 32, color=acc)

        if len(mechs) == 1:
            x = 180
            w = 470
        for i, (t, s, macc, dashed) in enumerate(mechs):
            x = 180 if i == 0 else 435
            w = 470 if len(mechs) == 1 else 215
            c.box(x, y, w, 64, t, s, accent=macc)
            if dashed:
                c.rect(x, y, w, 64, fill="none", stroke=RED, sw=1.8, r=8, dash="6,4")
        if len(mechs) == 2:
            c.text(415, y + 38, "+", size=15, fill=SUB, anchor="middle")

        c.text(700, y + 30, note[0], size=11.5, fill="#374151", weight=500)
        c.text(700, y + 50, note[1], size=11.5, fill=SUB)

    # 底部：C 的边界
    c.rect(60, 508, 840, 62, fill="#fef2f2", stroke="#fecaca", sw=1.2, r=10)
    c.text(76, 532, "C 是四个字母里唯一一个「数据库只能提供工具、不能提供结果」的",
           size=12, fill=RED, weight=600)
    c.text(76, 554, "库存不为负、借贷要平衡、跨服务要一致——取决于事务边界和 SQL 的写法，"
                    "不取决于你用了哪个隔离级别。",
           size=11, fill="#7f1d1d")

    return c.save(os.path.join(OUT, "ch16-fig1.svg"))


# ---------------------------------------------------------------- 图 16-2
def fig2():
    c = Canvas(960, 560, title="图 16-2　一个事务的时间线：资源是什么时候被占上的",
               subtitle="BEGIN 只改会话状态；trx_id、undo slot、行锁、ReadView 各有各的出现时机")

    nodes = [
        (60, 140, "BEGIN", "只改会话状态"),
        (243, 160, "第一条写语句", "才分配 trx_id"),
        (446, 160, "写 undo / redo", "数据页变脏，锁在手里"),
        (649, 120, "COMMIT", "redo 落盘，放锁"),
        (809, 90, "purge", "回收 undo"),
    ]
    for i, (x, w, t, s) in enumerate(nodes):
        acc = [SLATE, BLUE, ORANGE, GREEN, PURPLE][i]
        c.box(x, 104, w, 66, t, s, accent=acc)
        if i:
            px, pw = nodes[i - 1][0], nodes[i - 1][1]
            c.arrow(px + pw, 137, x, 137, color=SLATE, width=1.4)

    lanes = [
        (196, BLUE, "trx_id", "只读事务 8.0 不分配", 243, 649,
         "trx_id 从第一条写语句活到 COMMIT", False),
        (266, ORANGE, "undo", "写操作才会产生", 243, 890,
         "undo slot + undo 记录，purge 清完才归还", False),
        (336, RED, "row lock", "X / Next-Key", 243, 649,
         "X 记录锁，持有到事务结束", False),
        (406, PURPLE, "ReadView", "RR 下事务级", 403, 649,
         "首个快照读时才创建", True),
    ]
    for y, acc, name, sub, x1, x2, label, dashed in lanes:
        c.rect(60, y, 840, 56, fill=FAINT, stroke="#e5e7eb", sw=1.2, r=8)
        c.text(74, y + 24, name, size=12, fill=acc, weight=600, mono=True)
        c.text(74, y + 43, sub, size=10.5, fill=SUB)
        c.rect(x1, y + 14, x2 - x1, 28, fill=TINT[acc], stroke=BORDER[acc],
               sw=1.2, r=6, dash="6,4" if dashed else None)
        c.text(x1 + 10, y + 33, label, size=10.5, fill=acc, weight=500)
        if dashed:
            c.text(216, y + 33, "没有快照读就不存在", size=10, fill=SUB)

    c.text(60, 494,
           "BEGIN 之后，连接上只有会话状态；第一条语句才建立引擎侧事务对象，"
           "第一条写语句才换来 trx_id、undo slot 和行锁。",
           size=11.5, fill=INK)
    c.text(60, 518,
           "COMMIT 释放锁和 trx_id，但不释放 undo——undo 的寿命由最老的 ReadView 决定（第 5 章）。",
           size=11.5, fill=SUB)

    return c.save(os.path.join(OUT, "ch16-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
