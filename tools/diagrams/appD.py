#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""附录 D 配图：诊断 SQL 手册"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 D-1
def fig1():
    c = Canvas(960, 760,
               title="图 D-1　症状导航：先认出手上的现象属于哪一组，再决定跑哪一条",
               subtitle="八组对应四十条；「首条」是你该先跑的那一条，跑完再决定要不要往下钻")

    c.text(56, 92, "组", size=10, fill=SUB, weight=600)
    c.text(196, 92, "典型症状（值班时你看到的那一句）", size=10, fill=SUB, weight=600)
    c.text(548, 92, "首条：先跑这个", size=10, fill=SUB, weight=600)
    c.text(792, 92, "条目 / 机制章节", size=10, fill=SUB, weight=600)

    rows = [
        ("锁与阻塞", "全站卡住、报 1205、DDL 挂着不动", "D1 锁等待链", "D1–D7 / 18·19", RED),
        ("慢 SQL", "没有慢日志，P99 却在涨", "D8 digest 增量榜", "D8–D13 / 38", ORANGE),
        ("索引", "计划走错、扫描行数突然翻十倍", "D14 从未使用的索引", "D14–D17 / 9·10", BLUE),
        ("表与空间", "磁盘只涨不降、单表越来越慢", "D18 库级空间分布", "D18–D23 / 3·31", GREEN),
        ("内存与 IO", "P99 抖动、物理读同步上涨", "D24 命中率求差", "D24–D28 / 2·39", PURPLE),
        ("连接", "1040、Sleep 一片、连接数贴顶", "D29 按来源聚合", "D29–D32 / 21·45", ORANGE),
        ("日志与复制", "延迟台阶、付了钱查不到单", "D35 复制状态速读", "D33–D38 / 22·24", PURPLE),
        ("统计与元数据", "计划突变、DDL 之后行为变了", "D39 统计信息新旧", "D39–D40 / 10·46", SLATE),
    ]

    for i, (grp, sym, first, ids, col) in enumerate(rows):
        y = 100 + i * 72
        c.container(48, y, 864, 64, "")
        c.box(56, y + 10, 128, 44, grp, accent=col, size=11.5)
        c.box(196, y + 10, 340, 44, sym, accent=SLATE, size=9.8)
        c.box(548, y + 10, 232, 44, first, accent=col, size=10)
        c.box(792, y + 10, 112, 44, ids, accent=SLATE, size=9.2)

    c.text(56, 700, "顺序不能反：先确认「是哪一组」，再选条目。跳过分组直接翻 SQL，最后一定在十几条之间来回试。",
           size=11, fill=INK)
    c.legend(56, 730, [(RED, "服务不可用：先取证再止血", None),
                       (ORANGE, "等待与延迟：先分清楚谁在等谁", None)])
    c.legend(520, 730, [(PURPLE, "数据与复制：先确认一致性", None),
                        (SLATE, "计划与元数据：先怀疑统计", None)])
    return c.save(os.path.join(OUT, "appD-fig1.svg"))


# ---------------------------------------------------------------- 图 D-2
def fig2():
    c = Canvas(960, 600,
               title="图 D-2　锁等待的两种形态：扇出与链式，读法都是倒着找 GRANTED",
               subtitle="data_lock_waits 一行就是一条边；边长什么样，决定你先动谁")

    c.container(48, 96, 424, 340, "形态一：一个持有者，多个等待者（最常见）")
    c.box(186, 140, 148, 52, "txn A", "GRANTED · X", accent=BLUE, size=13, sub_size=9.5)
    waiters = [(72, "txn B", 240), (215, "txn C", 260), (352, "txn D", 280)]
    for x, name, anchor_x in waiters:
        c.box(x, 300, 108, 46, name, "WAITING", accent=RED, size=11, sub_size=9)
        c.arrow((anchor_x, 192), (x + 54, 300), color=RED, width=1.3)
    c.text(64, 400, "杀一个 GRANTED，后面全通；杀 WAITING 只是换个人排队。",
           size=10.5, fill=RED)

    c.container(504, 96, 408, 340, "形态二：链式（A 等 B，B 又等 C）")
    c.box(596, 136, 220, 48, "txn A  WAITING", "等 order_main 的 PK", accent=RED, size=11, sub_size=9)
    c.arrow((706, 184), (706, 232), color=RED, width=1.3)
    c.box(596, 232, 220, 48, "txn B  GRANTED", "自己也卡在别处", accent=ORANGE, size=11, sub_size=9)
    c.arrow((706, 280), (706, 328), color=RED, width=1.3)
    c.box(596, 328, 220, 48, "txn C  GRANTED", "真正握着锁的那个", accent=BLUE, size=11, sub_size=9)
    c.text(520, 400, "链越长，杀错一个只是让链变短，不会解开。", size=10.5, fill=RED)

    c.container(48, 456, 864, 104, "LOCK_DATA 告诉你的三件事")
    c.text(64, 492, "一个值（如 10086）→ 等的是这条索引记录；supremum pseudo-record → 等的是最后一段间隙；",
           size=10.5, fill=INK)
    c.text(64, 514, "NULL → 表级或元数据锁，去看 metadata_locks；LOCK_MODE 里的 GAP 表示只锁间隙，不锁记录。",
           size=10.5, fill=INK)
    c.text(64, 540, "锁的信息只说明「谁在等谁」，不说明「为什么等」——后者要回到事务里看它前面做了什么。",
           size=10.5, fill=SUB)
    return c.save(os.path.join(OUT, "appD-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
