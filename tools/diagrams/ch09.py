#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 9 章配图：索引设计与失效全景"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 9-1
def fig1():
    c = Canvas(960, 640, title="图 9-1　联合索引 (a,b,c)：有序性断在哪一列",
               subtitle="同一个键前缀，条件形态不同，能走到的深度就不同；断点之后只能过滤，不能定位")

    # ① 叶子记录
    c.container(40, 82, 880, 150,
                "① 叶子按 (a,b,c) 字典序：先比 a，a 相同比 b，b 相同比 c")
    recs = ["(1,1,1)", "(1,1,2)", "(1,1,3)", "(1,2,1)",
            "(2,1,1)", "(2,1,2)", "(2,2,1)", "(2,2,2)"]
    xs = [74 + i * 104 for i in range(8)]
    for i, (x, r) in enumerate(zip(xs, recs)):
        accent = BLUE if i < 4 else SLATE
        c.box(x, 140, 84, 48, r, accent=accent, size=12, mono=True)

    c.text(272, 212, "a = 1 段：b、c 在段内有序", size=10.5, fill=BLUE, anchor="middle")
    c.text(688, 212, "a = 2 段：b、c 重新开始", size=10.5, fill=SLATE, anchor="middle")
    c.arrow((480, 134), (480, 204), color=RED, dash="4,3", width=1.4, end=False)
    c.text(490, 216, "a 一变，b、c 的序就重排", size=10, fill=RED)

    # ② 三种条件形态
    c.container(40, 246, 880, 282, "② 同一棵树，三种写法能用到的深度")

    rows = [
        ("① 等值 × 3",
         "a = 1 AND b = 2 AND c = 3",
         "三列都被固定成常量，一次下降落到唯一一段。",
         [(GREEN, "a 定位"), (GREEN, "b 定位"), (GREEN, "c 定位")],
         "三列全部参与定位", GREEN),
        ("② 等值 + 范围 + 等值",
         "a = 1 AND b > 2 AND c = 3",
         "b 是范围，有序性断在 b；c 只能逐条判。",
         [(GREEN, "a 定位"), (ORANGE, "b 范围"), (RED, "c 过滤")],
         "c 只能靠 ICP 过滤，不能定位", ORANGE),
        ("③ 等值 + 排序",
         "a = 1 ORDER BY b, c",
         "a 固定之后 (b,c) 整段有序，流天然是目标顺序。",
         [(GREEN, "a 定位"), (GREEN, "b 有序"), (GREEN, "c 有序")],
         "无 filesort，扫描顺序即结果顺序", GREEN),
    ]
    for i, (title, sql, note, pills, status, col) in enumerate(rows):
        y = 294 + i * 82
        c.text(62, y + 12, title, size=12.5, weight=600)
        c.text(62, y + 34, sql, size=11, fill=INK, mono=True)
        c.text(62, y + 54, note, size=10.5, fill=SUB)
        for j, (pc, label) in enumerate(pills):
            c.pill(548 + j * 100, y, 92, 30, label, accent=pc, size=11)
        c.text(548, y + 50, "→ " + status, size=10.5, fill=col, weight=500)

    # ③ 结语
    c.container(40, 544, 880, 84, None)
    c.text(60, 580,
           "分界线不在「第几列」，在这一列的值还被不被固定成常量：等值按住它，范围放开它，排序只要求别被打断。",
           size=11.5, fill=INK)
    c.text(60, 604,
           "所以 (a,b,c) 上 a=1 AND c=3 只能用到 a；(a,c,b) 上同样的条件能用到两列。顺序是给条件形态排的，不是给列的重要度排的。",
           size=11.5, fill=SUB)
    return c.save(os.path.join(OUT, "ch09-fig1.svg"))


# ---------------------------------------------------------------- 图 9-2
def fig2():
    c = Canvas(960, 640, title="图 9-2　ICP：把能判的先判掉，再决定回不回表",
               subtitle="数量级为示意：候选 1000 条、最终命中 10 条；实际行数由数据分布决定")

    # ① 关闭 ICP
    c.container(40, 84, 880, 200, "① 关闭 ICP：过滤发生在 Server 层")
    boxes_a = [
        ("索引范围扫描", "候选 1000 条", BLUE),
        ("逐条回表", "1000 次下降", RED),
        ("Server 层过滤", "c 条件再判一遍", SLATE),
        ("丢弃 990 条", "过路费已付", RED),
        ("返回 10 条", "结果集", GREEN),
    ]
    for i, (t, s, col) in enumerate(boxes_a):
        x = 60 + i * 176
        c.box(x, 146, 136, 64, t, s, accent=col, size=12, sub_size=10)
        if i < 4:
            c.arrow((x + 136, 178), (x + 176, 178), color=col, width=1.6)
    c.text(60, 252,
           "代价：1000 次回表 —— 每一次都是一遍从根到叶的 B+ 树下降，只为留下 10 行。",
           size=11.5, fill=RED)

    # ② 开启 ICP
    c.container(40, 312, 880, 200, "② 开启 ICP：只依赖索引列的条件，在叶子页上就判完")
    boxes_b = [
        ("索引范围扫描", "候选 1000 条", BLUE),
        ("引擎内过滤", "c 条件就地判", TEAL),
        ("满足者才回表", "10 次下降", GREEN),
        ("Server 层", "条件已判完，直接返回", SLATE),
        ("返回 10 条", "结果集", GREEN),
    ]
    for i, (t, s, col) in enumerate(boxes_b):
        x = 60 + i * 176
        c.box(x, 374, 136, 64, t, s, accent=col, size=12, sub_size=10)
        if i < 4:
            c.arrow((x + 136, 406), (x + 176, 406), color=col, width=1.6)
    c.text(60, 480,
           "代价：1000 次索引项比较 + 10 次回表。回表次数从 1000 降到 10，扫的索引项一条没少。",
           size=11.5, fill=GREEN)

    # ③ 适用边界
    c.container(40, 540, 880, 84, None)
    c.text(60, 574,
           "为什么能省：回表 = 一次 B+ 树下降 + 一次页内定位，比「在索引页里比一个值」贵一到两个数量级。",
           size=11.5, fill=INK)
    c.text(60, 598,
           "什么时候不管用：条件引用了索引之外的列、子查询、存储函数，或对象本来就是聚簇索引（叶子即整行，没有回表可省）。",
           size=11.5, fill=SUB)
    return c.save(os.path.join(OUT, "ch09-fig2.svg"))


# ---------------------------------------------------------------- 图 9-3
def fig3():
    c = Canvas(960, 640, title="图 9-3　索引失效的五个断点：二十种写法归到五类",
               subtitle="先定位断在哪一类，再改 SQL；同一类里的修法往往是同一个")

    c.box(380, 90, 200, 54, "索引失效 20 例", "五个断点，二十种写法",
          accent=RED, size=13, sub_size=10.5)

    cats = [
        ("类型转换", RED, [
            "字符串列传数字",
            "字符串列 = 0",
            "JOIN collation 不一致",
        ]),
        ("函数包裹", ORANGE, [
            "DATE(paid_at)",
            "amount + 100",
            "COALESCE / IFNULL",
            "JSON_EXTRACT",
        ]),
        ("结构不对", PURPLE, [
            "LIKE '%退款%'",
            "OR 一侧无索引",
            "范围列之后的列",
            "缺最左列",
            "排序方向不一致",
        ]),
        ("优化器权衡", TEAL, [
            "!= / <>",
            "NOT IN 子查询",
            "IS NOT NULL 高占比",
            "排序与过滤不同索引",
            "低选择性 IN 列表",
        ]),
        ("统计与参数", SLATE, [
            "统计信息过期",
            "LIMIT 诱导早停",
            "预处理默认选择性",
        ]),
    ]

    for i, (name, col, items) in enumerate(cats):
        x = 40 + i * 181
        cx = x + 78
        c.rect(x, 200, 156, 272, fill=FAINT, stroke="#e5e7eb",
               sw=1.2, r=10, dash="6,4")
        c.box(x + 12, 212, 132, 40, name, accent=col, size=12)
        c.arrow([(480, 144), (480, 174), (cx, 174), (cx, 200)],
                color=SLATE, width=1.2, dash="4,3")
        top = 264 + (5 - len(items)) * 20
        for j, it in enumerate(items):
            c.pill(x + 12, top + j * 40, 132, 34, it, accent=col, size=9.5)

    c.container(40, 486, 880, 134, "这张图怎么用")
    c.text(60, 538,
           "从左往右读，是排查顺序：先看两侧类型（能不能直接比对），再看列有没有被包住，再看索引结构撑不撑得起这条条件，",
           size=11.5, fill=INK)
    c.text(60, 562,
           "最后才怀疑优化器与统计信息——前两类改 SQL 或改表结构，后三类多半要改索引、补 ANALYZE，或者干脆接受全表扫更便宜。",
           size=11.5, fill=INK)
    c.text(60, 592,
           "红线：改完必须用 EXPLAIN 复核 key 与 rows，不能靠「应该走索引了」判断。EXPLAIN ANALYZE [8.0.18+] 能看到实际行数。",
           size=11.5, fill=SUB)
    return c.save(os.path.join(OUT, "ch09-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
