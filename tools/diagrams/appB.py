#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""附录 B 配图：错误码的四个来源与信息流向"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 B-1
def fig1():
    c = Canvas(960, 680,
               title="图 B-1　错误的四个来源：一条语句从左往右走，一个错误码从右往左被包装",
               subtitle="先确认码是谁报的；同一个数字在不同层，可能是两件完全不同的事")

    cols = [
        (48, "① 客户端 / 驱动", "连接与握手", "2059 / 08S01",
         "驱动层改写", "文案由驱动决定", SLATE),
        (272, "② Server 层", "解析、权限、元数据", "1040 · 1290 · 3024",
         "临时表也在这里", "1114 的一种成因", BLUE),
        (496, "③ InnoDB 层", "锁、表空间、日志", "1205 · 1213 · 1467",
         "现场在 data_locks", "和 INNODB STATUS", RED),
        (720, "④ 复制线程", "IO 线程 / SQL 线程", "1032 · 1062 · 1236",
         "码不进客户端", "进 Last_SQL_Errno", PURPLE),
    ]

    for x, head, t1, s1, t2, s2, col in cols:
        c.container(x, 96, 190, 200, head)
        c.box(x + 8, 136, 174, 54, t1, s1, accent=col, size=12, sub_size=9.5)
        c.box(x + 8, 204, 174, 54, t2, s2, accent=col, size=12, sub_size=9.5)

    # 相邻两层之间的调用方向
    c.arrow((244, 190), (272, 190), color=BLUE, width=1.6)
    for x in (462, 686):
        c.arrow((x, 190), (x + 34, 190), color=BLUE, width=1.6)

    # 应用只看到最外层
    c.rect(44, 90, 196, 212, fill="none", stroke=SLATE, sw=1.4, r=12, dash="5,4")
    c.text(143, 84, "应用只看到这一层", size=10, fill=SLATE, anchor="middle")

    c.text(48, 322, "语句向右穿过四层；错误码向左被逐层包装，越往外信息越少、越像「网络问题」。",
           size=11, fill=INK)

    c.pill(300, 336, 360, 34, "同一个数字，在不同层可能是不同的事", accent=SLATE, size=12)

    examples = [
        ("1062", "两个来源",
         "客户端：唯一键冲突，是幂等信号；复制线程：从库已有该行，是数据分叉",
         "同码不同因 —— 一个该重试，一个该补数据", ORANGE),
        ("1205 / 1213", "一对关系",
         "都表现为「等锁」，方向相反：1205 没有环，要缩短持锁；1213 有环，要改加锁顺序",
         "看 LATEST DETECTED DEADLOCK 是空的还是有两段对调的 HOLDS", RED),
        ("1114 / 1878", "同一块盘",
         "1114 是「没地方写」，1878 是「写了一半失败」；同一个磁盘满，报哪个取决于谁先撞上",
         "先 df 数据目录，再 df tmpdir —— 两块盘常常不是同一块", GREEN),
    ]

    for i, (code, tag, line1, line2, col) in enumerate(examples):
        y = 396 + i * 66
        c.container(48, y, 864, 58, "")
        c.box(58, y + 9, 150, 40, code, tag, accent=col, size=13, sub_size=9.5, mono=True)
        c.text(228, y + 27, line1, size=11.5, fill=INK)
        c.text(228, y + 46, line2, size=10.5, fill=SUB)

    c.text(48, 612, "读日志的顺序与因果顺序相反：最晚出现的那个码最不可能是原因。",
           size=11, fill=RED)

    c.legend(56, 642, [(BLUE, "语句下发的方向", None)])
    c.legend(520, 642, [(SLATE, "应用看到的码往往是最外层那个", "5,4")])
    return c.save(os.path.join(OUT, "appB-fig1.svg"))


if __name__ == "__main__":
    print(fig1())
