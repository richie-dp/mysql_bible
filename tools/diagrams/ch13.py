#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 13 章配图：子查询、派生表与 CTE"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


def _card(c, x, y, w, h, name, tag, rows, accent):
    """一张策略卡：表头 + 4 行「标签｜值」"""
    c.container(x, y, w, h, "")
    c.box(x + 12, y + 12, w - 24, 40, name, tag, accent=accent, size=13, sub_size=10)
    yy = y + 72
    for label, val in rows:
        c.text(x + 20, yy, label, size=10, fill=accent, weight=600)
        c.text(x + 78, yy, val, size=10, fill=INK)
        yy += 19


# ---------------------------------------------------------------- 图 13-1
def fig1():
    c = Canvas(960, 756,
               title="图 13-1　同一个 IN，五种执行形态：扫几遍、靠什么去重",
               subtitle="前提是子查询位于 WHERE 顶层、是 AND 的一项，且无 UNION / 聚合 / LIMIT；"
                        "策略由成本在五种里选一种，不是按写法选")

    c.mono_box(40, 76, 880, 50, [
        "SELECT o.order_no FROM order_main o",
        "WHERE o.id IN (SELECT order_id FROM order_item WHERE sku_id = 8842);",
    ], size=10)

    cards = [
        ("Table Pullout", "把子查询表拉进外层", BLUE, [
            ("前提", "连接列是主键或唯一键"),
            ("EXPLAIN", "无标记，select_type 变 SIMPLE"),
            ("扫描", "等同普通 join，外层每行 eq_ref"),
            ("去重", "唯一键保证一行最多匹配一次"),
        ]),
        ("FirstMatch", "命中第一条就收工", GREEN, [
            ("前提", "子查询连接列上有可用索引"),
            ("EXPLAIN", "Extra 出现 FirstMatch(外层别名)"),
            ("扫描", "外层每行一次索引下降，不扫完"),
            ("去重", "短路：一个外层行只输出一次"),
        ]),
        ("LooseScan", "顺着索引跳着扫", TEAL, [
            ("前提", "连接列是索引前缀，值成组有序"),
            ("EXPLAIN", "Extra 出现 LooseScan(m..n)"),
            ("扫描", "子查询表扫一遍，每组只取一行"),
            ("去重", "索引有序性本身就是去重"),
        ]),
        ("Materialization", "先算完，再当表用", PURPLE, [
            ("前提", "拉不出来、内层又没有可用索引"),
            ("EXPLAIN", "多一行 MATERIALIZED + <subquery2>"),
            ("扫描", "子查询算一次 → 临时表 → 外层探测"),
            ("代价", "物化是一次写入，结果大就吃 temptable"),
        ]),
        ("DuplicateWeedout", "先连，再按 rowid 去重", ORANGE, [
            ("前提", "成本选中了子查询侧先驱动的顺序"),
            ("EXPLAIN", "Extra 出现 Start temporary / End temporary"),
            ("扫描", "照普通 join 跑，命中行先落临时表"),
            ("代价", "临时表行数 ≈ 命中的外层行数"),
        ]),
    ]

    pos = [(40, 146), (500, 146), (40, 332), (500, 332), (40, 518)]
    for (x, y), (name, tag, accent, rows) in zip(pos, cards):
        _card(c, x, y, 420, 146, name, tag, rows, accent)

    # 第六格：共同前提
    c.container(500, 518, 420, 146, "")
    c.box(512, 530, 396, 40, "五种都绕不开的门槛", "不满足就退回 DEPENDENT SUBQUERY",
          accent=SLATE, size=13, sub_size=10)
    for i, (label, val) in enumerate([
        ("位置", "WHERE / ON 顶层，且是 AND 的一项"),
        ("排除", "UNION、HAVING、聚合、LIMIT、STRAIGHT_JOIN"),
        ("开关", "optimizer_switch 的 semijoin / firstmatch 等"),
        ("8.0.20+", "半连接也能走 hash join，见第 12 章"),
    ]):
        yy = 590 + i * 19
        c.text(520, yy, label, size=10, fill=SLATE, weight=600)
        c.text(578, yy, val, size=10, fill=INK)

    c.text(40, 706, "读法：先看 Extra 有没有 FirstMatch / LooseScan / Start temporary，"
                    "再看有没有 MATERIALIZED 行。", size=11, fill=SUB)
    c.text(40, 728, "四种标记都没有、子查询又按行重算，就该去找 DEPENDENT SUBQUERY："
                    "不是策略选错，是它没进半连接。", size=11, fill=RED)
    return c.save(os.path.join(OUT, "ch13-fig1.svg"))


# ---------------------------------------------------------------- 图 13-2
def fig2():
    c = Canvas(960, 600,
               title="图 13-2　派生表的两种归宿，以及 8.0.22 把过滤推到物化之前",
               subtitle="同一句 FROM (SELECT ...) d：能不能摊平，取决于派生表里有没有挡住 merge 的构造")

    # A：merge
    c.container(40, 80, 420, 262, "A｜merge：派生表摊平进外层，等于手写 join")
    c.mono_box(56, 112, 388, 76, [
        "SELECT o.order_no, d.sku_id",
        "FROM (SELECT order_id, sku_id",
        "      FROM order_item) d",
        "JOIN order_main o ON o.id = d.order_id;",
    ], size=9)
    for i, (s, col) in enumerate([
        ("EXPLAIN：只有两行，select_type 全是 SIMPLE", INK),
        ("没有 <derived2> —— 派生表不再是一个独立节点", INK),
        ("条件：无聚合、GROUP BY、DISTINCT、LIMIT、UNION、", SUB),
        ("      无窗口函数、无用户变量赋值", SUB),
        ("代价：不额外物化，外层怎么驱动就怎么读", GREEN),
    ]):
        c.text(56, 218 + i * 22, s, size=10, fill=col)

    # B：materialize
    c.container(500, 80, 420, 262, "B｜materialize：先物化成临时表，外层再扫它")
    c.mono_box(516, 112, 388, 76, [
        "SELECT o.order_no, d.cnt",
        "FROM (SELECT order_id, COUNT(*) cnt",
        "      FROM order_item GROUP BY order_id) d",
        "JOIN order_main o ON o.id = d.order_id;",
    ], size=9)
    for i, (s, col) in enumerate([
        ("EXPLAIN：多一行 id=2、select_type=DERIVED", INK),
        ("外层那行 table=<derived2>，可能借用 <auto_key0>", INK),
        ("条件：出现聚合、GROUP BY、DISTINCT、LIMIT、", SUB),
        ("      UNION、窗口函数中的任意一个", SUB),
        ("代价：先算完整个派生表，行宽也照样搬进临时表", RED),
    ]):
        c.text(516, 218 + i * 22, s, size=10, fill=col)

    # 条件下推
    c.container(40, 362, 880, 200, "8.0.22 起：派生条件下推 —— 让过滤发生在物化之前")
    c.box(64, 406, 300, 64, "物化全部派生表行", "WHERE 在物化之后才过滤", accent=RED,
          size=13, sub_size=10)
    c.arrow(368, 438, 448, 438, color=BLUE, label="条件下推", label_dy=-9)
    c.box(452, 406, 300, 64, "只物化通过条件的行", "条件进了派生表的 WHERE / HAVING",
          accent=GREEN, size=13, sub_size=10)

    c.text(60, 498, "触发：外层条件只引用派生表列。GROUP BY 的派生表上，"
                    "分组列的条件推成 WHERE，非分组列的条件推成 HAVING。", size=10, fill=INK)
    c.text(60, 520, "限制：派生表带 LIMIT、带窗口函数、作为外连接内表，"
                    "或 CTE 被引用多次时，都不推。", size=10, fill=RED)
    c.text(60, 542, "开关：optimizer_switch 的 derived_condition_pushdown，默认 on；"
                    "单条语句可用 NO_DERIVED_CONDITION_PUSHDOWN 关掉。", size=10, fill=SUB)
    return c.save(os.path.join(OUT, "ch13-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
