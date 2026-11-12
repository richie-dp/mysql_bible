#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 12 章配图：连接算法与 Join 优化"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 12-1
def fig1():
    c = Canvas(960, 790,
               title="图 12-1　同一组表，三种连法：扫描次数差三个数量级",
               subtitle="示意规模：orders 过滤后 30 万行作驱动侧，order_item 1200 万行；"
                        "数字用来比较量级，不是实测值")

    # ① NLJ
    c.container(40, 84, 880, 212,
                "① NLJ（Simple Nested Loop）—— 教科书基线，MySQL 里只有关掉 block_nested_loop 才会走到")
    c.box(66, 138, 200, 62, "orders（驱动）", "过滤后 30 万行", accent=BLUE)
    c.box(420, 138, 230, 62, "order_item（被驱动）", "连接列无可用索引", accent=SLATE)
    c.arrow(270, 154, 416, 154, color=RED, label="取 1 行，整表扫一遍")
    c.arrow(416, 186, 270, 186, color=SLATE, label="命中则输出")
    c.text(66, 228, "被驱动表扫描 30 万次 × 1200 万行——这个量级没有讨论价值，所以 MySQL 默认不会走它。",
           size=12, fill=INK)
    c.text(66, 252, "它的唯一用途是作为成本基线：所有「更快」的说法，都是相对它省掉了哪些次数的扫描。",
           size=12, fill=SUB)
    c.text(66, 276, "注意：Extra 里不会出现任何标记，因为没有 join buffer，也没有索引——只剩全表扫。",
           size=12, fill=SLATE)

    # ② INLJ
    c.container(40, 316, 880, 212,
                "② INLJ（Index Nested Loop）—— 被驱动表的连接列有索引，这是 OLTP 唯一想要的路")
    c.box(66, 370, 200, 62, "orders（驱动）", "过滤后 30 万行", accent=BLUE)
    c.box(420, 370, 230, 62, "order_item", "PRIMARY (order_id)", accent=GREEN)
    c.arrow(270, 386, 416, 386, color=BLUE, label="每行一次 B+ 树下降")
    c.arrow(416, 418, 270, 418, color=GREEN, label="回表取整行")
    c.text(66, 460, "代价 ≈ N × 单次查找成本：30 万次索引下降 + 30 万次回表，全部是随机 IO。",
           size=12, fill=INK)
    c.text(66, 484, "把 join 之后要用的列塞进被驱动表的联合索引，回表次数直接归零——这是 join 优化最高性价比的一刀。",
           size=12, fill=GREEN)
    c.text(66, 508, "Extra 里看不出 INLJ；看被驱动表那一行的 type：eq_ref / ref / range 就是它。",
           size=12, fill=SUB)

    # ③ BNL
    c.container(40, 548, 880, 212,
                "③ BNL（Block Nested Loop）—— 无索引时攒批扫，join_buffer_size 决定要扫几轮")
    c.box(66, 602, 190, 62, "orders（驱动）", "30 万行", accent=BLUE)
    c.box(300, 602, 200, 62, "join buffer", "256KB，装 K 行", accent=ORANGE)
    c.box(580, 602, 230, 62, "order_item（被驱动）", "每轮整表扫一遍", accent=RED)
    c.arrow(260, 633, 296, 633, color=ORANGE, label="攒批")
    c.arrow(504, 633, 576, 633, color=RED, label="顺序扫")
    c.text(66, 692, "被驱动表扫描轮数 = ceil(N ÷ K)，K = join_buffer_size ÷ 单行字节数。",
           size=12, fill=INK)
    c.text(66, 716, "N = 30 万、单行约 200B、buffer 256KB → K ≈ 6500，要扫 46 轮；每轮 1200 万行，合计 5 亿行以上。",
           size=12, fill=RED)
    c.text(66, 740, "Extra 写 Using join buffer (Block Nested Loop)，且固定出现在被驱动表那一行——这是定位 BNL 的唯一标记。",
           size=12, fill=SUB)
    return c.save(os.path.join(OUT, "ch12-fig1.svg"))


# ---------------------------------------------------------------- 图 12-2
def fig2():
    c = Canvas(960, 710,
               title="图 12-2　Hash Join 的两阶段，以及装不下时的那条落盘路径",
               subtitle="MySQL 8.0.18+ 支持等值连接；8.0.20+ 起扩展到外连接与半连接，并取代 BNL 成为等值连接的默认算法")

    # ① Build
    c.container(40, 84, 880, 246,
                "① Build：把一侧的行按连接列压成哈希表，这一步是全有或全无的成本")
    c.box(66, 136, 190, 76, "build 侧", "过滤后行数较少的一侧", accent=BLUE, size=13, sub_size=10)
    c.arrow(260, 174, 326, 174, color=BLUE, label="顺序扫一遍")
    c.box(330, 136, 240, 76, "哈希表", "桶数组 + 冲突链，常驻 join buffer", accent=GREEN,
          size=13, sub_size=10)
    c.arrow(574, 174, 656, 174, color=RED, dash="5,3", label="装不下")
    c.cyl(660, 136, 160, 76, "chunk 文件", "磁盘临时文件", accent=RED)

    c.text(66, 246, "内存放得下：build 侧读一遍、probe 侧读一遍，两遍顺序扫，这就是 hash join 的全部成本。",
           size=12, fill=INK)
    c.text(66, 270, "内存放不下：超出部分按 chunk 顺序写盘，probe 阶段再逐块读回，probe 侧因此可能被扫多遍。",
           size=12, fill=RED)
    c.text(66, 294, "默认 join_buffer_size = 256KB，按每行百字节算只装得下几千行——大表 join 的 hash join 其实是「常态溢写」。",
           size=12, fill=ORANGE)
    c.text(66, 318, "这就是为什么把 join_buffer_size 从 256KB 调到 16~64MB，在报表类查询里常常立竿见影。",
           size=12, fill=SUB)

    # ② Probe
    c.container(40, 350, 880, 236,
                "② Probe：另一侧只扫一遍，逐行算 hash、落桶、比对完整连接键")
    c.box(66, 402, 190, 76, "probe 侧", "通常是大表", accent=BLUE, size=13, sub_size=10)
    c.arrow(260, 440, 326, 440, color=BLUE, label="全表扫一遍")
    c.box(330, 402, 240, 76, "定位桶 → 比对键", "hash 相等不算匹配，还要比原值", accent=GREEN,
          size=13, sub_size=10)
    c.arrow(574, 440, 656, 440, color=GREEN, label="命中")
    c.box(660, 402, 190, 76, "输出配对行", "进入下一步 join", accent=GREEN, size=13, sub_size=10)

    c.text(66, 514, "总代价 ≈ 扫 build 侧 + 扫 probe 侧，与两侧谁大谁小基本无关。",
           size=12, fill=INK)
    c.text(66, 538, "「小表驱动大表」在这里失去意义：把小的放 build 侧，理由只剩「省内存、少溢写」。",
           size=12, fill=RED)
    c.text(66, 562, "非等值条件（>, <, BETWEEN, LIKE）用不了 hash join，仍然回落到 BNL。",
           size=12, fill=SUB)

    # 底注
    c.container(40, 606, 880, 80, "一句话判断")
    c.text(60, 646, "EXPLAIN 里被驱动表那行出现 Using join buffer (hash join)，就是它；"
                    "FORMAT=TREE 会直接写成 Inner hash join (a.x = b.x)。", size=12, fill=INK)
    c.text(60, 670, "它省掉的是「被驱动表被扫 N 轮」，换来的是「build 侧的一次性内存 + 可能的磁盘溢写」。",
           size=12, fill=SLATE)
    return c.save(os.path.join(OUT, "ch12-fig2.svg"))


# ---------------------------------------------------------------- 图 12-3
def _result_table(c, x, y, w, header, rows, row_h=32):
    """结果集表格：rows 每项为 (order_no, tier, state)，state ∈ None/keep/drop"""
    c.rect(x, y, w, row_h, fill="#f1f5f9", stroke=LINE, sw=1, r=0)
    c.text(x + 14, y + 21, header[0], size=11, fill=SUB, weight=600)
    c.text(x + 180, y + 21, header[1], size=11, fill=SUB, weight=600)
    for i, (a, b, state) in enumerate(rows):
        ry = y + row_h * (i + 1)
        if state == "keep":
            fill, accent = TINT[GREEN], GREEN
        elif state == "drop":
            fill, accent = TINT[RED], RED
        else:
            fill, accent = BG, SUB
        c.rect(x, ry, w, row_h, fill=fill, stroke=LINE, sw=1, r=0)
        c.text(x + 14, ry + 21, a, size=12, mono=True,
               fill=(SUB if state == "drop" else INK))
        c.text(x + 180, ry + 21, b, size=12, mono=True, fill=accent)
        if state in ("keep", "drop"):
            c.rect(x, ry, 4, row_h, fill=accent, stroke=accent, sw=1, r=0)
        if state == "drop":
            c.rect(x + 10, ry + 17, 44, 1.4, fill=RED, stroke=RED, sw=1, r=0)


def fig3():
    c = Canvas(960, 668,
               title="图 12-3　ON 与 WHERE 之间，隔着一整个「补 NULL」的动作",
               subtitle="同一条 LEFT JOIN，条件放错位置结果就不同；放对位置之后，优化器还会把它改写成内连接")

    # 左：ON
    c.container(40, 76, 430, 392, "A｜条件写在 ON 里：右表先筛，再补 NULL")
    c.mono_box(56, 108, 398, 128, [
        "SELECT o.order_no, p.tier",
        "FROM orders o",
        "LEFT JOIN user_profile p",
        "  ON p.user_id = o.user_id",
        " AND p.tier = 'GOLD';",
    ], title="SQL A｜谓词在 ON", size=10)
    _result_table(c, 56, 246, 398,
                  ("order_no", "p.tier"),
                  [("A1001", "GOLD", "keep"),
                   ("A1002", "NULL", "keep"),
                   ("A1003", "NULL", "keep")])
    c.text(56, 402, "右表没匹配上的行保留下来，补 NULL —— 左表 3 行一行不少。",
           size=12, fill=GREEN)
    c.text(56, 426, "ON 只决定「怎么匹配」，不决定「留不留」，这是外连接的语义地基。",
           size=12, fill=INK)
    c.text(56, 450, "想「只连 GOLD 用户，且没有画像的订单也要」，只能这么写。",
           size=12, fill=SUB)

    # 右：WHERE
    c.container(490, 76, 430, 392, "B｜条件写在 WHERE 里：补完 NULL 再筛，NULL 行被杀掉")
    c.mono_box(506, 108, 398, 128, [
        "SELECT o.order_no, p.tier",
        "FROM orders o",
        "LEFT JOIN user_profile p",
        "  ON p.user_id = o.user_id",
        "WHERE p.tier = 'GOLD';",
    ], title="SQL B｜谓词在 WHERE", size=10)
    _result_table(c, 506, 246, 398,
                  ("order_no", "p.tier"),
                  [("A1001", "GOLD", "keep"),
                   ("A1002", "NULL", "drop"),
                   ("A1003", "NULL", "drop")])
    c.text(506, 402, "NULL = 'GOLD' 的结果是 UNKNOWN，不是 TRUE，两行被吃掉。",
           size=12, fill=RED)
    c.text(506, 426, "结果等价于 INNER JOIN；优化器据此把外连接重写成内连接。",
           size=12, fill=INK)
    c.text(506, 450, "写法是外连接，执行是内连接 —— 最容易骗过 code review 的一种写法。",
           size=12, fill=SUB)

    # 底部规则
    c.container(40, 486, 880, 158, "三句话记住这个差别")
    c.text(60, 526, "1. ON 是匹配条件，在补 NULL 之前生效；WHERE 是结果过滤，在补 NULL 之后生效。",
           size=12, fill=INK)
    c.text(60, 552, "2. WHERE 里对被驱动表列写 =、IN、>、IS NOT NULL，等于声明「这列不能为 NULL」，外连接降级成内连接。",
           size=12, fill=INK)
    c.text(60, 578, "3. 唯一例外是 WHERE p.col IS NULL —— 那是故意找「没匹配上的行」，是反连接，不会被改写。",
           size=12, fill=GREEN)
    c.text(60, 608, "判定口径：EXPLAIN 的 select_type 从 LEFT JOIN 变成 SIMPLE，就说明优化器已经按内连接处理了。",
           size=11, fill=SUB)
    return c.save(os.path.join(OUT, "ch12-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
