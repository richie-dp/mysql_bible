#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 8 章配图：B+ 树与索引组织表"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


def fillbar(c, x, y, w, ratio, color=GREEN, hole=False, h=10):
    """页内填充条：底色是空洞，前景是已占用记录"""
    c.rect(x, y, w, h, fill=("#fef2f2" if hole else "#f1f5f9"),
           stroke=(RED if hole else LINE), sw=1, r=5,
           dash=("3,2" if hole else None))
    if ratio > 0:
        c.rect(x, y, w * ratio, h, fill=color, stroke=color, sw=1, r=5)


# ---------------------------------------------------------------- 图 8-1
def fig1():
    c = Canvas(960, 680, title="图 8-1　三层 B+ 树：非叶子只做路由，叶子才放数据",
               subtitle="按扇出 1000、叶页 75 行估算；真实值由主键长度与行宽决定，可用 innodb_index_stats 反推")

    c.text(46, 152, "层 3", size=12, fill=SLATE, weight=600)
    c.text(46, 320, "层 2", size=12, fill=SLATE, weight=600)
    c.text(46, 466, "层 1", size=12, fill=SLATE, weight=600)

    # 根页
    c.box(390, 112, 220, 68, "根页（1 个页）", "≈ 1000 个键 + 子页号", accent=BLUE)

    # 非叶子页
    for i, x in enumerate((124, 328, 532, 736)):
        c.box(x, 282, 140, 64, f"非叶子页 {i + 1}", "≈ 1000 个子页",
              accent=SLATE, size=12, sub_size=10)

    # 叶子页
    leaf_x = [110 + i * 102 for i in range(8)]
    for i, x in enumerate(leaf_x):
        c.box(x, 422, 66, 84, f"页 {i + 1}", "75 行",
              accent=GREEN, size=11, sub_size=10)

    # 结构连线（灰）：根 → 非叶子
    for cx in (194, 398, 602, 806):
        c.arrow([(500, 180), (500, 232), (cx, 232), (cx, 282)],
                color=SLATE, width=1.2, dash="4,3")
    # 非叶子 → 叶子（只画每页两个）
    for cx in (194, 398, 602, 806):
        for lx in (cx - 51, cx + 51):
            c.arrow([(cx, 346), (cx, 386), (lx, 386), (lx, 422)],
                    color=SLATE, width=1.2, dash="4,3")

    # 高亮一次点查：根 → 非叶子 3 → 页 5
    c.arrow([(500, 180), (500, 232), (602, 232), (602, 282)],
            color=BLUE, width=2.2)
    c.arrow([(602, 346), (602, 386), (551, 386), (551, 422)],
            color=BLUE, width=2.2)
    c.text(612, 260, "点查路径", size=11, fill=BLUE, weight=600)

    # 叶子双向链表
    for i in range(7):
        c.arrow((leaf_x[i] + 68, 464), (leaf_x[i + 1] - 2, 464),
                color=GREEN, width=1.3, start=True)

    c.text(110, 528, "叶子页之间是双向链表（FIL_PAGE_PREV / FIL_PAGE_NEXT）", size=11, fill=SUB)

    # 每层定位能力
    c.container(40, 546, 880, 114, "每层能定位的范围（扇出 1000、每叶 75 行）")
    c.text(60, 598, "层 3：1 个根页把全部键切成 ≈1000 段；整层只有 1 页，常驻 Buffer Pool。",
           size=12, fill=INK)
    c.text(60, 620, "层 2：≈1000 个非叶子页切成 ≈100 万段，合计约 15MB，基本可以整层缓存。",
           size=12, fill=INK)
    c.text(60, 642, "层 1：≈100 万个叶子页 × 75 行 ≈ 7500 万行——点查真正读盘的只有这一层。",
           size=12, fill=GREEN)
    return c.save(os.path.join(OUT, "ch08-fig1.svg"))


# ---------------------------------------------------------------- 图 8-2
def fig2():
    c = Canvas(960, 640, title="图 8-2　聚簇索引与二级索引：叶子存主键，所以要回表",
               subtitle="两条路径共用一次「根 → 叶」下降；差别在拿到二级索引叶子之后")

    c.pill(85, 96, 280, 34, "二级索引 idx_buyer_id", accent=PURPLE, size=12)
    c.pill(595, 96, 280, 34, "聚簇索引 PRIMARY（表本身）", accent=BLUE, size=12)

    c.box(125, 150, 200, 54, "根页", "buyer_id 区间路由", accent=PURPLE)
    c.box(635, 150, 200, 54, "根页", "id 区间路由", accent=BLUE)

    c.box(55, 240, 150, 90, "8842 → 1024", "索引列 → 主键值",
          accent=PURPLE, size=13, sub_size=10)
    c.box(245, 240, 150, 90, "8843 → 1030", "索引列 → 主键值",
          accent=PURPLE, size=13, sub_size=10)
    c.box(565, 240, 150, 90, "id = 1024", "整行：买家 / 金额 / 状态",
          accent=GREEN, size=13, sub_size=10)
    c.box(755, 240, 150, 90, "id = 1030", "整行：买家 / 金额 / 状态",
          accent=GREEN, size=13, sub_size=10)

    for lx in (130, 320):
        c.arrow([(225, 204), (225, 222), (lx, 222), (lx, 240)], color=PURPLE, width=1.4)
    for lx in (640, 830):
        c.arrow([(735, 204), (735, 222), (lx, 222), (lx, 240)], color=BLUE, width=1.4)

    # 回表：二级索引叶 → 聚簇索引根
    c.arrow([(395, 286), (480, 286), (480, 177), (635, 177)],
            color=ORANGE, width=2.2)
    c.text(505, 204, "回表", size=12, fill=ORANGE, weight=600)
    c.text(505, 222, "拿 1024 再下降一次", size=10, fill=ORANGE)

    # 两条路径的终点
    c.box(40, 380, 370, 56, "路径 A｜覆盖索引，到这里结束",
          "需要的列已经在叶子里，不再下降", accent=GREEN, size=12, sub_size=10)
    c.box(550, 380, 370, 56, "路径 B｜非覆盖，必须回表",
          "二级索引 → 主键 → 聚簇索引 → 整行", accent=ORANGE, size=12, sub_size=10)
    c.arrow((130, 330), (130, 380), color=GREEN, width=1.6, dash="5,3")
    c.arrow((640, 330), (640, 380), color=ORANGE, width=1.6, dash="5,3")

    c.container(40, 452, 880, 168, "为什么叶子存主键，而不是存行地址")
    c.text(60, 502, "二级索引叶子存的是 (索引列, 主键值)。拿到主键后必须回聚簇索引再下降一次，这一次就是回表。",
           size=12, fill=INK)
    c.text(60, 528, "反过来，如果叶子存的是行地址：页分裂时一半的行会搬到新页，指向它们的每一个二级索引项都得跟着改。",
           size=12, fill=RED)
    c.text(60, 554, "存主键把「行搬家」变成「键不变」，二级索引零维护；代价是每次非覆盖查询多一次随机 IO。",
           size=12, fill=BLUE)
    c.text(60, 580, "覆盖索引之所以快，是它把这次下降整个省掉了，而不是因为「索引更小」。",
           size=12, fill=GREEN)
    return c.save(os.path.join(OUT, "ch08-fig2.svg"))


# ---------------------------------------------------------------- 图 8-3
def fig3():
    c = Canvas(960, 632, title="图 8-3　自增主键与 UUID 主键：同一批数据，两种页形态",
               subtitle="行宽按 200B、叶页可用 16256B 估算，一页满装约 81 行")

    # ① 自增
    c.container(40, 88, 880, 242, "① 自增主键：插入永远落在最右页，新页追加到链表尾部")
    c.badge(700, 98, "热点：最右一页的 latch", accent=RED)
    c.arrow(60, 136, 890, 136, color=BLUE, label="插入方向", label_dy=-9)
    for i, x in enumerate((55, 230, 405, 580, 755)):
        last = (i == 4)
        c.box(x, 152, 150, 96, f"页 N-{4 - i}" if not last else "页 N（正在写）",
              "填充 94%", accent=(ORANGE if last else BLUE), size=12, sub_size=10)
        fillbar(c, x + 10, 226, 130, 0.94, color=(ORANGE if last else GREEN))
    c.text(55, 278, "已有页一条都不搬：新记录塞不下时，从空闲区取一个新页接在后面，原页保持 15/16 满。",
           size=12, fill=INK)
    c.text(55, 302, "填充率长期稳定在 93% 左右；一页 81 行 → 实际约 76 行/页。",
           size=12, fill=SUB)
    c.text(55, 324, "代价写在另一头：所有并发写都打在最右一页的 latch 上（第 3.6 节）。",
           size=11, fill=RED)

    # ② UUID
    c.container(40, 370, 880, 242, "② UUID 主键：落点随机，满页对半劈，空洞只能在页内复用")
    c.badge(690, 380, "无热点，但随机 IO 翻倍", accent=SLATE)
    c.arrow(890, 418, 60, 418, color=SLATE, dash="5,3", label="插入方向不再单调", label_dy=-9)
    for i, x in enumerate((55, 230, 405, 580, 755)):
        c.box(x, 434, 150, 96, f"页 {i + 1}", "填充 50%", accent=RED, size=12, sub_size=10)
        fillbar(c, x + 10, 508, 130, 0.50, color=GREEN, hole=True)
    c.text(55, 556, "满页后把一半记录搬到新页：两页各剩一半空位，这部分空间谁也借不到。",
           size=12, fill=INK)
    c.text(55, 580, "新页从 free extent 取，物理上不和原页相邻 → 范围扫描从顺序 IO 退化成随机 IO。",
           size=12, fill=RED)
    c.text(55, 604, "1 亿行 × 200B：填充 94% ≈ 130 万叶页 / 21GB；填充 50% ≈ 250 万叶页 / 41GB。",
           size=12, fill=SUB)
    return c.save(os.path.join(OUT, "ch08-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
