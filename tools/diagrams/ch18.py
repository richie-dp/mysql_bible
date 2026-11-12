#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 18 章配图：锁体系全景"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


def bracket(c, x1, x2, y, color, up=12, width=2.0, parts=None):
    """区间括线：两端的竖钩 + 底横线。parts 可把横线拆成 [(x1,x2,color,dash)]"""
    c.arrow((x1, y - up), (x1, y), color=color, end=False, width=width)
    c.arrow((x2, y - up), (x2, y), color=color, end=False, width=width)
    if parts:
        for a, b, col, dash in parts:
            c.arrow((a, y), (b, y), color=col, end=False, width=width, dash=dash)
    else:
        c.arrow((x1, y), (x2, y), color=color, end=False, width=width)


# ---------------------------------------------------------------- 图 18-1
def fig1():
    c = Canvas(960, 700, title="图 18-1　锁的分类树：四个正交维度挂在同一批对象上",
               subtitle="一条 UPDATE 拿到的是四个维度的一次取值组合，不是「某一种锁」")

    c.box(380, 84, 200, 54, "InnoDB 锁", "四个维度切同一批对象", accent=BLUE, size=15)

    cols = [
        ("粒度｜锁多大范围", 40, [
            ("全局锁", "对象：整个实例", SLATE),
            ("表锁", "对象：整张表", SLATE),
            ("页锁（历史）", "对象：16KB 数据页", SLATE),
            ("行锁", "对象：索引记录", BLUE),
        ]),
        ("模式｜允许谁同时进", 270, [
            ("S 共享", "读读可并发", GREEN),
            ("X 排他", "读写都互斥", RED),
            ("IS / IX", "表级意向标记", ORANGE),
            ("AUTO-INC", "自增计数器", PURPLE),
        ]),
        ("算法｜覆盖多长一段", 500, [
            ("Record", "锁住那一条记录", BLUE),
            ("Gap", "锁住它前面的空位", RED),
            ("Next-Key", "记录 + 前面空位", ORANGE),
            ("谓词锁", "锁索引区间（空间）", TEAL),
        ]),
        ("用途｜解决别的问题", 730, [
            ("意向锁", "预告：我要锁行", ORANGE),
            ("插入意向", "预告：我要插这里", ORANGE),
            ("MDL", "保护表结构", PURPLE),
            ("备份锁", "保护实例不被 DDL", SLATE),
        ]),
    ]

    for head, x, items in cols:
        cx = x + 95
        c.arrow([(480, 138), (480, 158), (cx, 158), (cx, 178)],
                color=SLATE, width=1.4)
        c.box(x, 178, 190, 44, head, accent=SLATE, size=12)
        c.arrow((cx, 222), (cx, 246), color=SLATE, width=1.2, end=False)
        for i, (t, s, col) in enumerate(items):
            c.box(x, 246 + i * 64, 190, 52, t, s, accent=col, size=12, sub_size=10)

    c.container(40, 516, 880, 146, "四个维度怎么叠在同一条语句上")
    c.text(60, 566, "RR 下 UPDATE order_main SET status = 2 WHERE amount = 1000：行级 + X + Gap + 表级 IX。", size=12, fill=INK)
    c.text(60, 592, "换成 WHERE id = 7 且命中，算法那一维退化成 Record；换成范围条件，又变回 Next-Key——变的只是覆盖范围。", size=12, fill=BLUE)
    c.text(60, 618, "页锁一列是历史：InnoDB 没有页锁，页上的 rw_lock 是 latch，不是事务锁，不进 data_locks。", size=12, fill=SUB)
    c.text(60, 644, "MDL 与备份锁在 Server 层和实例层，引擎根本不知道它们存在，但它们照样让你排队。", size=12, fill=SUB)
    return c.save(os.path.join(OUT, "ch18-fig1.svg"))


# ---------------------------------------------------------------- 图 18-2
def fig2():
    c = Canvas(960, 640, title="图 18-2　意向锁兼容矩阵：表锁如何在不扫一行的情况下判断冲突",
               subtitle="行 = 已持有的锁，列 = 新来的请求；绿色兼容，红色排队")

    names = [("IS", "意向共享"), ("IX", "意向排他"), ("S", "表级共享"), ("X", "表级排他")]
    grid = [
        [1, 1, 0, 0],
        [1, 1, 0, 0],
        [1, 0, 1, 0],
        [0, 0, 0, 0],
    ]

    c.container(40, 108, 164, 200, "假如没有意向锁")
    c.text(52, 152, "给表加锁前必须确认", size=10, fill=SUB)
    c.text(52, 174, "表里没有任何行锁，", size=10, fill=SUB)
    c.text(52, 196, "只能把整张表扫一遍。", size=10, fill=SUB)
    c.text(52, 226, "1000 万行 = 1000 万次", size=10, fill=RED)
    c.text(52, 248, "检查，锁表成了重操作。", size=10, fill=RED)
    c.text(52, 278, "IS / IX 把它变成 O(1)：", size=10, fill=GREEN)
    c.text(52, 296, "只看表上的标记。", size=10, fill=GREEN)

    c.box(246, 108, 104, 48, "持有 ＼ 请求", None, accent=SLATE, size=10)
    for i, (n, full) in enumerate(names):
        c.box(360 + i * 114, 108, 110, 48, n, full, accent=SLATE, size=13, sub_size=10)
        c.box(246, 168 + i * 64, 104, 60, n, full, accent=SLATE, size=13, sub_size=10)
        for j, ok in enumerate(grid[i]):
            c.box(360 + j * 114, 168 + i * 64, 110, 60,
                  "兼容" if ok else "冲突",
                  accent=(GREEN if ok else RED), size=13)

    c.container(40, 440, 880, 176, "矩阵怎么被用：表锁只看这一张，行锁另算")
    c.text(60, 486, "① IS 与 IX 永远兼容。它们是记账不是保护：若 IX 之间互斥，同表两行并发更新就退化成表级串行。",
           size=12, fill=GREEN)
    c.text(60, 514, "② S / X 与 IX 冲突，是因为表级锁要求整表安静；IX 说明「有人正在改行」，两者语义直接打架。",
           size=12, fill=RED)
    c.text(60, 542, "③ 于是加表锁只需读这张矩阵：命中冲突就排队，不必扫描任何一行——这正是意向锁存在的理由。",
           size=12, fill=INK)
    c.text(60, 570, "④ 矩阵只解决「表锁 vs 行锁」。两把行锁是否冲突，要看它们是否落在同一索引记录或同一段间隙上。",
           size=12, fill=BLUE)
    c.text(60, 598, "⑤ 对角线全绿：同模式之间不谈冲突；X 那一行全红，排他锁与任何请求都不共存。",
           size=12, fill=SUB)
    return c.save(os.path.join(OUT, "ch18-fig2.svg"))


# ---------------------------------------------------------------- 图 18-3
def fig3():
    c = Canvas(960, 570, title="图 18-3　一条索引上的三种锁：Record 锁记录，Gap 锁空位，Next-Key 两者相加",
               subtitle="索引 idx_amount 的叶子记录按 amount 升序排列，括线表示加锁覆盖的区间")

    c.text(200, 96, "叶子记录（含伪记录 supremum，值恒为 +∞）", size=11, fill=SUB)

    xs = [260, 400, 540, 680, 820]
    labels = [("amount = 500", "id = 1"), ("amount = 800", "id = 2"),
              ("amount = 1200", "id = 3"), ("amount = 2000", "id = 4"),
              ("SUPREMUM", "+∞")]
    for x, (t, s) in zip(xs, labels):
        acc = SLATE if t == "SUPREMUM" else BLUE
        c.box(x, 112, 100, 64, t, s, accent=acc, size=11, sub_size=10)

    for i in range(4):
        c.arrow((xs[i] + 100, 144), (xs[i + 1], 144), color=SLATE, width=1.2)

    # ① Record
    bracket(c, 400, 500, 232, BLUE)
    c.pill(40, 215, 180, 34, "Record｜只锁 800 这条", accent=BLUE, size=12)
    c.text(200, 262, "锁住这条索引记录本身：别人不能改它、不能删它，但可以在它前后插入新记录。",
           size=12, fill=INK)

    # ② Gap
    bracket(c, 500, 540, 322, RED)
    c.pill(40, 305, 180, 34, "Gap｜空位 (800,1200)", accent=RED, size=12)
    c.text(200, 352, "只锁空位，不含两端记录：amount 落在 800 与 1200 之间的插入全部排队。",
           size=12, fill=INK)
    c.text(200, 374, "两端是开区间——800 和 1200 这两条记录本身没被它锁住。", size=11, fill=SUB)

    # ③ Next-Key
    bracket(c, 500, 640, 412, ORANGE,
            parts=[(500, 540, RED, "5,3"), (540, 640, GREEN, None)])
    c.pill(40, 395, 180, 34, "Next-Key｜(800,1200]", accent=ORANGE, size=12)
    c.text(560, 404, "gap 部分", size=10, fill=RED, anchor="end")
    c.text(600, 404, "记录部分", size=10, fill=GREEN)
    c.text(200, 442, "默认形态就是它：Gap 与 Record 相加，左开右闭。唯一索引等值命中才退化成纯 Record。",
           size=12, fill=INK)

    c.text(200, 486, "锁对象是 (space_id, page_no, heap_no)，heap_no 是页内记录序号，不是行号——所以「不存在的行」也能被锁。",
           size=11, fill=BLUE)
    c.text(200, 510, "800 与 1200 之间没有任何记录，这段空位照样属于索引结构，照样可以挂一把 Gap 锁。",
           size=11, fill=SUB)
    c.text(200, 534, "最后一条记录到 supremum 之间的间隙同样存在，(2000, +∞) 也能被锁——这是范围更新锁到表尾的原因。",
           size=11, fill=SUB)
    return c.save(os.path.join(OUT, "ch18-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
