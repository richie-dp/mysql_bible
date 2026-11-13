#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 50 章配图：内容、计数与队列"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 50-1
def fig1():
    c = Canvas(960, 680,
               title="图 50-1　三种计数方案的写入路径与准确性",
               subtitle="三行的差别不在写得多快，在\"允许错多久\"——最后一行决定选型，不是第一行")

    heads = [(141, "方案"), (296, "写并发上限"), (466, "读代价"),
             (636, "准确性承诺"), (806, "何时必须换")]
    for x, s in heads:
        c.text(x, 86, s, size=11, fill=SUB, anchor="middle", weight=600)

    rows = [
        (96, RED, "单行更新", "UPDATE cnt + 1",
         [("每秒几百~两千", "同一行严格串行", RED),
          ("主键点查 1 行", "微秒级，最快", BLUE),
          ("精确", "永不丢，也永不快", GREEN),
          ("并发过两千/秒", "或热内容被刷屏", RED)],
         "没有业务判断就没有保护：库存还有 qty >= 1 兜底，计数只有排队", RED),
        (262, BLUE, "分桶计数", "counter_bucket",
         [("单桶 1/N 并发", "9000/16 → 560/秒", GREEN),
          ("SUM N 行", "1~2 页，读侧要缓存", ORANGE),
          ("精确（聚合后）", "写侧与读侧分开算", GREEN),
          ("桶数要扩容", "或要 WHERE cnt > x", ORANGE)],
         "写并发放大 N 倍，代价是读要 SUM、桶会偏、总量不能直接比较", ORANGE),
        (428, PURPLE, "Redis 落库", "INCR + 定时刷",
         [("单 key 十万量级", "单线程天然串行", GREEN),
          ("内存读", "微秒级，不占 MySQL", BLUE),
          ("近似，会丢", "宕机丢一段增量", RED),
          ("涉及对账 / 审计", "或数字不能有延迟", RED)],
         "拿准确性换吞吐：丢的是一个时间窗内的增量，对账要能把差额找回来", RED),
    ]

    for y, col, name, tag, cells, verdict, vcol in rows:
        c.container(60, y, 840, 152, "")
        c.box(76, y + 26, 130, 76, name, tag, accent=col, size=13, sub_size=9.5)
        xs = (216, 386, 556, 726)
        for i, (t, s, sc) in enumerate(cells):
            c.box(xs[i], y + 26, 158, 76, t, s, accent=sc, size=11.5, sub_size=9.5)
        c.rect(xs[2], y + 26, 158, 76, fill="none", stroke=vcol, sw=1.8, dash="5,3", r=8)
        c.badge(xs[2] + 6, y + 2, "选型的落点", accent=vcol)
        c.text(76, y + 128, verdict, size=10.5, fill=vcol)

    c.text(60, 606, "写并发上限决定你撑不撑得住今晚，准确性承诺决定你三年后要不要重做一次对账",
           size=11.5, fill=INK, weight=600)

    c.legend(60, 636, [(RED, "串行 / 丢数据", None)])
    c.legend(220, 636, [(GREEN, "可接受路径", None)])
    c.legend(380, 636, [(ORANGE, "聚合 / 延迟", None)])
    c.legend(540, 636, [(PURPLE, "外部组件", None)])
    c.legend(700, 636, [(BLUE, "主数据路径", None)])
    return c.save(os.path.join(OUT, "ch50-fig1.svg"))


# ---------------------------------------------------------------- 图 50-2
def fig2():
    c = Canvas(960, 660,
               title="图 50-2　两个\"MySQL 顶不住\"的场景结构：组合爆炸与读写互斥",
               subtitle="上半是\"条件自由组合\"，下半是\"读的便宜与写的便宜互为镜像\"；两者都不靠加索引解决")

    # ---------------- 上半：标签筛选
    c.container(60, 80, 840, 264, "标签筛选：每多一个可筛选标签，查询组合数翻一倍")

    bars = [(1, "2", 22, GREEN), (4, "16", 42, GREEN), (8, "256", 64, ORANGE),
            (12, "4 千", 88, RED), (16, "6.5 万", 110, RED), (20, "105 万", 132, RED)]
    c.arrow((96, 280), (96, 118), color=SLATE)
    c.rect(96, 279, 308, 1.5, fill=LINE, stroke=LINE, sw=0, r=0)

    for i, (n, val, h, col) in enumerate(bars):
        x = 110 + i * 48
        c.rect(x, 280 - h, 34, h, fill=TINT[col], stroke=BORDER[col], sw=1.5, r=4)
        c.text(x + 17, 280 - h - 8, val, size=10.5, fill=col, anchor="middle", weight=600)
        c.text(x + 17, 296, "n=%d" % n, size=10, fill=SUB, anchor="middle")

    c.text(96, 316, "横轴：可筛选标签个数　纵轴：组合数（对数刻度）", size=10, fill=SUB)
    c.text(96, 334, "20 个标签 = 1,048,576 种组合，不可能靠建索引覆盖", size=10.5, fill=RED)

    routes = [
        (108, GREEN, "组合索引", "≤ 2~3 个固定组合，且最左前缀对得上"),
        (154, ORANGE, "位图 BIT", "≤ 64 个标签，位运算不走索引，只能全扫"),
        (200, BLUE, "倒排表", "千万级、条件自由组合，瓶颈是回表次数"),
        (246, PURPLE, "ES 兜底", "再往上，或需要相关性排序"),
    ]
    for y, col, name, desc in routes:
        c.box(430, y, 112, 38, name, accent=col, size=11)
        c.text(556, y + 24, desc, size=10.5, fill=SUB)

    # ---------------- 下半：树形结构
    c.container(60, 356, 840, 228, "树形结构：四种存法，读的代价与写的代价互为镜像")

    cards = [
        (76, BLUE, "邻接表 parent_id",
         ["查子树：递归 N 次查找", "写节点：插入一行", "移动：改一行 parent_id", "适合：层浅、读多写少"]),
        (282, TEAL, "路径枚举 path",
         ["查子树：LIKE 前缀一次扫", "写节点：一行，带 path", "移动：改整棵子树的 path", "适合：频繁查子树"]),
        (488, PURPLE, "闭包表 祖先边",
         ["查子树：一次等值查询", "写节点：写深度条祖先边", "移动：删旧边、插新边", "适合：层级深、模式多"]),
        (694, ORANGE, "嵌套集 lft/rgt",
         ["查子树：一次 BETWEEN", "写节点：平均改半张表", "移动：几乎重建全表", "适合：几乎不变的分类"]),
    ]
    for x, col, name, lines in cards:
        c.box(x, 388, 190, 34, name, accent=col, size=11.5)
        for j, ln in enumerate(lines):
            fill = col if j == 3 else SUB
            c.text(x + 10, 450 + j * 30, ln, size=10, fill=fill)

    c.text(60, 616, "树形结构没有\"最优存法\"：只有\"你的读模式更贵，还是写模式更贵\"",
           size=11.5, fill=INK, weight=600)
    c.legend(60, 642, [(RED, "组合爆炸 / 热点", None)])
    c.legend(250, 642, [(GREEN, "可接受", None)])
    c.legend(370, 642, [(BLUE, "常规路径", None)])
    c.legend(510, 642, [(ORANGE, "写放大", None)])
    c.legend(650, 642, [(PURPLE, "外部组件", None)])
    return c.save(os.path.join(OUT, "ch50-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
