#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 32 章配图：分区表"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 32-1
def fig1():
    c = Canvas(960, 668,
               title="图 32-1　分区表在物理上是 N 套独立的 B+ 树",
               subtitle="4 个月分区示意；每个分区自带聚簇索引与全套二级索引，各自一个 .ibd，没有共享的根页")

    # 两条查询
    c.box(40, 92, 380, 40, "Q1｜create_time 落在 2026-03 内",
          accent=GREEN, size=12, r=8)
    c.box(540, 92, 380, 40, "Q2｜buyer_id = 8842（不带分区键）",
          accent=RED, size=12, r=8)

    cols = [("p202601", "2026-01"), ("p202602", "2026-02"),
            ("p202603", "2026-03"), ("p202604", "2026-04")]
    xs = [40, 270, 500, 730]
    for (name, month), x in zip(cols, xs):
        c.container(x, 200, 190, 240, f"{name}（{month}）")
        c.box(x + 15, 234, 160, 66, "聚簇索引", "PRIMARY(id, ct)",
              accent=PURPLE, size=12, sub_size=10)
        c.box(x + 15, 312, 160, 56, "二级索引", "idx_buyer 一份",
              accent=PURPLE, size=12, sub_size=10)
        c.text(x + 15, 392, "独立 .ibd / 独立根页", size=10, fill=SUB)

    # Q2：按非分区键 → 4 个分区全部打开
    c.arrow([(730, 132), (730, 185)], color=RED, width=1.8, end=False)
    c.arrow([(730, 185), (880, 185)], color=RED, width=1.8, end=False)
    c.arrow([(730, 185), (190, 185)], color=RED, width=1.8, end=False)
    for dx in (190, 420, 650, 880):
        c.arrow((dx, 185), (dx, 199), color=RED, width=1.8)
    c.text(760, 178, "4 个分区各下降一次", size=11, fill=RED, weight=600)

    # 绿色裁剪路径在红色总线上「跨线」：先留白，再画箭头
    c.raw('<path d="M 595 176 L 595 201" stroke="#ffffff" stroke-width="7" '
          'fill="none"/>')

    # Q1：按分区键 → 只开 p202603
    c.arrow([(420, 112), (455, 112), (455, 168), (595, 168), (595, 200)],
            color=GREEN, width=2.2)
    c.text(470, 160, "裁剪：只开 1 个分区", size=11, fill=GREEN, weight=600)

    c.legend(40, 466, [
        (GREEN, "按分区键查：裁剪后只打开 1 个分区", None),
        (RED, "按非分区键查：4 个分区全部打开", None),
        (PURPLE, "每个分区：一套聚簇索引 + 一套二级索引", None),
        (SLATE, "分区之间没有共享的根页、也没有全局索引", "4,3"),
    ])

    c.container(40, 552, 880, 96, "代价的方向")
    c.text(60, 594, "分区表不是「一棵更大的树」，是 4 棵互不相通的树：各有根页、各有叶链、各有一份 idx_buyer。",
           size=12, fill=INK)
    c.text(60, 620, "所以按非分区键查的代价 = 单分区代价 × 分区数；执行器是单线程的，这 4 棵不会被并行扫。",
           size=12, fill=RED)
    return c.save(os.path.join(OUT, "ch32-fig1.svg"))


# ---------------------------------------------------------------- 图 32-2
def fig2():
    c = Canvas(960, 640,
               title="图 32-2　DROP PARTITION 与 DELETE：一条元数据命令 vs 一晚上脚本",
               subtitle="同是删掉三个月共 1.2 亿行；红色是随行数线性增长的资源，橙色是一次元数据操作")

    # 时间轴
    c.arrow((240, 140), (900, 140), color=SLATE, width=1.2, dash="4,3",
            label="耗时 →", label_at=0.92, label_dy=-9)
    for tx, lab in ((240, "T0"), (470, "+1h"), (700, "+1 夜"), (866, "第 2 天")):
        c.text(tx, 152, lab, size=10, fill=SLATE, anchor="middle")

    # ① DELETE
    c.box(40, 170, 180, 52, "DELETE", "分批 1000 行", accent=RED,
          size=13, sub_size=10)
    c.box(240, 170, 660, 52, "逐行定位 → delete-mark → 写 undo → 写 redo → 写 binlog row event",
          accent=RED, size=11)
    chips_a = [("undo 每行一份", RED), ("binlog 每行一条", RED),
               ("purge 追不上", RED), ("DATA_FREE 上涨", RED)]
    for i, (lab, color) in enumerate(chips_a):
        c.box(240 + i * 170, 236, 130, 46, lab, accent=color, size=10, r=6)
    c.text(240, 302, "耗时、undo、binlog 量、从库延迟、碎片，全部与行数成正比。",
           size=11, fill=RED)

    # ② DROP PARTITION
    c.box(40, 356, 180, 52, "DROP PARTITION", "元数据操作", accent=ORANGE,
          size=12, sub_size=10)
    c.box(240, 356, 96, 52, "秒级", accent=GREEN, size=12)
    c.text(352, 388, "与分区里装了多少行无关", size=11, fill=GREEN)
    chips_b = [("数据字典更新", ORANGE), ("unlink 对应 .ibd", ORANGE),
               ("binlog 只有一条 DDL", ORANGE)]
    for i, (lab, color) in enumerate(chips_b):
        c.box(240 + i * 172, 422, 150, 46, lab, accent=color, size=10, r=6)
    c.text(240, 492, "不删行、不写 undo、不产生 row event、不留碎片，也不需要 OPTIMIZE。",
           size=11, fill=ORANGE)

    c.container(40, 522, 880, 96, "为什么这两条路径差这么多")
    c.text(60, 564, "DELETE 是 DML：每一行都是一个事务里的修改，要能回滚、要能复制、要在页内留下空洞。",
           size=12, fill=INK)
    c.text(60, 588, "DROP PARTITION 是 DDL：改数据字典 + 摘掉表定义里的一段 + unlink 文件，数据页直接被丢弃。",
           size=12, fill=INK)
    c.text(60, 610, "代价并没有消失，只是被挪到了「拿 MDL」那一刻：要等这张表上没有长事务在跑。",
           size=12, fill=SLATE)
    return c.save(os.path.join(OUT, "ch32-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
