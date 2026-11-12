#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 11 章配图：执行计划精读"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")

LEVELS = [
    ("system", "唯一 1 行", "1 页", GREEN),
    ("const", "唯一索引等值", "3~4 页", GREEN),
    ("eq_ref", "唯一索引关联", "外层每行 3~4 页", TEAL),
    ("ref", "非唯一等值", "1 次下降 + k 条", BLUE),
    ("range", "索引范围扫", "1 次下降 + 区间", ORANGE),
    ("index", "全索引扫描", "整棵索引", RED),
    ("ALL", "全表扫描", "整张表", RED),
]


# ---------------------------------------------------------------- 图 11-1
def fig1():
    c = Canvas(960, 560, title="图 11-1　type 等级谱系：从精确到粗放，代价沿轴上升",
               subtitle="横轴是访问方式的精确度，不是实测耗时；index_merge 与 fulltext 不在这条主序上")

    c.arrow(46, 104, 892, 104, color=SLATE, width=1.2,
            label="单位行的访问代价递增", label_dy=-8)

    xs = [40, 172, 303, 435, 566, 698, 830]
    for x, (name, way, cost, color) in zip(xs, LEVELS):
        c.box(x, 132, 90, 64, name, way, accent=color, size=12, sub_size=10)
        cx = x + 45
        c.arrow(cx, 198, cx, 224, color=LINE, width=1.2, end=False)
        c.text(cx, 252, cost, size=10, fill=SUB, anchor="middle")

    c.arrow(40, 224, 920, 224, color=SLATE, width=1.6, end=False)

    c.container(40, 300, 880, 180, "旁支：不在这条主序上的 5 个取值")

    side = [
        ("ref_or_null", "ref + IS NULL", "≈ 2 × ref"),
        ("index_merge", "多索引合并", "路数越多越贵"),
        ("unique_subquery", "IN 子查询·唯一", "≈ eq_ref"),
        ("index_subquery", "IN 子查询·非唯一", "≈ ref"),
        ("fulltext", "FULLTEXT 倒排", "与 B+ 树不可比"),
    ]
    for i, (name, desc, cost) in enumerate(side):
        x = 62 + i * 176
        c.pill(x, 340, 132, 38, name, accent=PURPLE, size=11)
        c.text(x + 66, 400, desc, size=10, fill=INK, anchor="middle")
        c.text(x + 66, 420, cost, size=10, fill=SUB, anchor="middle")

    c.text(62, 456, "文档把 index_merge 排在 range 之前，但它可能同时扫两条索引再合并——位置不代表更便宜。",
           size=11, fill=RED)

    return c.save(os.path.join(OUT, "ch11-fig1.svg"))


# ---------------------------------------------------------------- 图 11-2
def fig2():
    c = Canvas(960, 600, title="图 11-2　EXPLAIN 的行序，就是执行树的嵌套顺序",
               subtitle="三表 join：order_main o ⋈ order_item i ⋈ sku s，左深嵌套循环")

    # ---------------- 左：EXPLAIN 表格
    c.container(40, 88, 500, 320, "EXPLAIN 输出（为排版只留 6 列）")

    cols = [52, 84, 184, 250, 406, 452, 528]
    rows_y = [134, 166, 210, 254, 298]

    c.rect(52, 134, 476, 164, fill=BG, stroke=LINE, sw=1.2, r=0)
    c.rect(52, 134, 476, 32, fill=FAINT, stroke="none", sw=1, r=0)
    for y in rows_y:
        c.rect(52, y, 476, 1, fill=LINE, stroke=LINE, sw=1, r=0)
    for x in cols:
        c.rect(x, 134, 1, 164, fill=LINE, stroke=LINE, sw=1, r=0)

    heads = ["id", "table", "type", "key", "rows", "Extra"]
    for x, h in zip(cols[:6], heads):
        c.text(x + 7, 155, h, size=10, fill=SUB, weight=600, mono=True)

    data = [
        ["1", "① o", "range", "idx_status_created", "312", "Using where"],
        ["1", "② i", "ref", "idx_order_id", "3", "NULL"],
        ["1", "③ s", "eq_ref", "PRIMARY", "1", "NULL"],
    ]
    for r, row in enumerate(data):
        y = rows_y[r + 1] + 27
        for x, cell in zip(cols[:6], row):
            c.text(x + 7, y, cell, size=9, fill=INK, mono=True)

    c.text(56, 344, "三行 id 相同 → 同一个 query block；行序 = 嵌套顺序", size=11, fill=INK)
    c.text(56, 366, "第一行是驱动表，后面每行按上一行的每一行执行一次", size=11, fill=SUB)

    # ---------------- 右：执行树
    c.container(580, 88, 340, 320, "执行树（左深嵌套循环）")

    c.box(660, 116, 180, 34, "Limit: 20", accent=SLATE, size=11)
    c.box(635, 176, 230, 34, "Nested loop inner join", accent=SLATE, size=11)
    c.box(645, 236, 210, 34, "Nested loop inner join", accent=SLATE, size=11)
    c.box(616, 290, 112, 46, "① Index range", "o · 312 行 · 1 次",
          accent=GREEN, size=11, sub_size=9)
    c.box(768, 290, 112, 46, "② Index lookup", "i · 3 行 × 312 次",
          accent=BLUE, size=11, sub_size=9)
    c.box(700, 352, 160, 44, "③ Single-row", "s · 1 行 × 936 次",
          accent=BLUE, size=11, sub_size=9)

    c.arrow(750, 150, 750, 176, color=SLATE, width=1.4)
    c.arrow(750, 210, 750, 236, color=SLATE, width=1.4)
    c.arrow([(750, 270), (750, 280), (672, 280), (672, 290)], color=SLATE, width=1.4)
    c.arrow([(750, 270), (750, 280), (824, 280), (824, 290)], color=SLATE, width=1.4)
    c.arrow([(865, 193), (898, 193), (898, 374), (860, 374)], color=SLATE, width=1.4)

    # ---------------- 底：读法
    c.container(40, 424, 880, 150, "怎么读这张对应关系")
    c.text(60, 474, "① 表格的行序就是树的从左到右：o 是驱动表，i 是它的内层，s 是再上一层 join 的内层。",
           size=11, fill=INK)
    c.text(60, 498, "② 三行 id 都是 1，属于同一个 query block；只有派生表、子查询才会出现 id=2、3。",
           size=11, fill=INK)
    c.text(60, 522, "③ rows 是单次循环的行数：i 执行 312 次、每次 3 行；s 执行 312×3=936 次、每次 1 行。",
           size=11, fill=INK)
    c.text(60, 546, "④ 把每层的 rows 乘起来，才是真实的读取量——这也是 EXPLAIN 最容易骗人的地方。",
           size=11, fill=RED)

    return c.save(os.path.join(OUT, "ch11-fig2.svg"))


# ---------------------------------------------------------------- 图 11-3
def fig3():
    c = Canvas(960, 600, title="图 11-3　三个工具能回答的问题，不是同一批",
               subtitle="EXPLAIN 说「打算怎么跑」，EXPLAIN ANALYZE 说「实际怎么跑」，optimizer_trace 说「为什么这么选」")

    cols = [
        (40, "EXPLAIN", "估算，不执行语句", BLUE,
         [("✓", "用哪个索引、什么 type"), ("✓", "估算扫多少行"),
          ("✓", "有没有排序 / 临时表"), ("✗", "实际读了多少行"),
          ("✗", "每个算子花了多久"), ("✗", "为什么放弃另一个索引")],
         "适合：改完 SQL 的第一眼"),
        (348, "EXPLAIN ANALYZE", "真跑，给实测（8.0.18+）", TEAL,
         [("✓", "上面全部"), ("✓", "实际行数 / 循环次数"),
          ("✓", "每个算子的真实耗时"), ("✓", "估算与实际的差距"),
          ("✗", "成本是怎么算出来的"), ("✗", "为什么选 A 不选 B")],
         "适合：怀疑估算、复现慢查询"),
        (656, "optimizer_trace", "给决策过程与成本对比", PURPLE,
         [("✓", "候选索引与各自成本"), ("✓", "各种 join 顺序的成本"),
          ("✓", "哪一步被 prune 掉了"), ("✓", "改写前后的成本差"),
          ("✗", "真实耗时"), ("✗", "实际返回多少行")],
         "适合：计划反直觉、要原因"),
    ]

    for x, name, sub, color, items, fit in cols:
        c.box(x, 92, 264, 58, name, sub, accent=color, size=14, sub_size=10)
        c.container(x, 170, 264, 250, "能回答 / 不能回答")
        for i, (mark, txt) in enumerate(items):
            y = 214 + i * 26
            c.text(x + 18, y, mark, size=12,
                   fill=(GREEN if mark == "✓" else RED), weight=700)
            c.text(x + 38, y, txt, size=11,
                   fill=(INK if mark == "✓" else SUB))
        c.rect(x + 16, 356, 232, 1, fill=LINE, stroke=LINE, sw=1, r=0)
        c.text(x + 18, 382, fit, size=11, fill=color, weight=600)

    c.text(40, 458, "推荐的排查顺序：形状 → 实测 → 原因", size=11, fill=SUB, weight=600)

    pants = [(40, "EXPLAIN 看形状"), (355, "ANALYZE 看真实"), (670, "trace 看决策")]
    for x, label in pants:
        c.pill(x, 476, 250, 44, label, accent=SLATE, size=12)

    c.arrow(290, 498, 353, 498, color=SLATE, width=1.5, label="估算可疑", label_dy=-9)
    c.arrow(605, 498, 668, 498, color=SLATE, width=1.5, label="结果反直觉", label_dy=-9)

    c.text(40, 556, "三者不是替代关系：前两个告诉你「跑成什么样」，最后一个告诉你「为什么」。",
           size=11, fill=SUB)

    return c.save(os.path.join(OUT, "ch11-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
