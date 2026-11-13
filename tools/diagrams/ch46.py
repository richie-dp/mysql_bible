#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 46 章配图：DDL 规范与在线变更"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 46-1
def fig1():
    c = Canvas(960, 700,
               title="图 46-1　三档算法：差别只在「碰不碰行数据」",
               subtitle="COPY 重写全部行；INPLACE 按操作决定要不要重写；INSTANT 只改数据字典，给表加一个行版本号")

    cols = [
        ("COPY", RED, 40, [
            ("原表 order_main", "全程被 MDL X 独占"),
            ("新表 #sql-xxx", "按目标结构建一张"),
            ("拷贝行数据", "是，全表逐行重写"),
            ("并发 DML", "不允许，读写都停"),
            ("耗时量级", "与表大小成正比"),
            ("一句话", "最慢，却最常被静默选中"),
        ]),
        ("INPLACE", BLUE, 340, [
            ("原表 order_main", "原地改，或原地重建"),
            ("新表 #sql-xxx", "只有重建时才有"),
            ("拷贝行数据", "重建类要，加索引不要"),
            ("并发 DML", "允许，增量进 online log"),
            ("耗时量级", "重建类与表大小成正比"),
            ("一句话", "不重建的那部分才叫真在线"),
        ]),
        ("INSTANT", GREEN, 640, [
            ("原表 order_main", "只改数据字典"),
            ("新表", "不建，没有临时表"),
            ("拷贝行数据", "一行都不碰"),
            ("并发 DML", "允许"),
            ("耗时量级", "与表大小无关"),
            ("一句话", "代价挪到了每一次读老行"),
        ]),
    ]

    for head, col, x, rows in cols:
        c.container(x, 92, 280, 500, "")
        c.box(x + 16, 104, 248, 44, head,
              {"COPY": "建新表 → 逐行拷 → 换名",
               "INPLACE": "在原表上做，增量回放",
               "INSTANT": "只改元数据，不碰行"}[head],
              accent=col, size=16, sub_size=10)
        for i, (t, s) in enumerate(rows):
            accent = col if i in (3, 4) else None
            c.box(x + 16, 166 + i * 70, 248, 54, t, s,
                  accent=accent, size=12, sub_size=10)

    c.box(40, 612, 880, 56,
          "分界不是新旧，是「碰不碰行数据」",
          "COPY 重写每一行 · INPLACE 按操作决定 · INSTANT 一行不碰，只加一个 7 位行版本号",
          accent=SLATE, size=14, sub_size=11)
    return c.save(os.path.join(OUT, "ch46-fig1.svg"))


# ---------------------------------------------------------------- 图 46-2
def fig2():
    c = Canvas(960, 620,
               title="图 46-2　三个锁阶段：Online 仍然会卡，卡在两端",
               subtitle="首尾两段 EXCLUSIVE 各自都是毫秒级——前提是表上没有未提交的事务")

    # 时间轴标记
    c.text(900, 104, "时间 →", size=10.5, fill=SUB, anchor="end")

    # ---- 泳道标签
    c.text(40, 162, "DDL 线程", size=12, fill=INK, weight=600)
    c.text(40, 272, "长事务", size=12, fill=INK, weight=600)
    c.text(40, 382, "业务查询", size=12, fill=INK, weight=600)

    # ---- 泳道 1：DDL 自身
    c.rect(140, 136, 180, 44, fill=TINT[RED], stroke=BORDER[RED],
           sw=1.2, r=6, dash="5,3")
    c.text(230, 163, "等 MDL X", size=11, fill=RED, anchor="middle", weight=600)
    c.text(230, 178, "被下面的报表事务拖住", size=9.5, fill=RED, anchor="middle")

    c.rect(320, 136, 42, 44, fill=RED, stroke=RED, sw=1.2, r=4)
    c.text(341, 126, "PREPARE", size=9.5, fill=RED, anchor="middle", weight=600)

    c.rect(362, 136, 450, 44, fill=TINT[GREEN], stroke=GREEN, sw=1.4, r=5)
    c.text(587, 157, "EXECUTE｜SHARED｜允许 DML", size=12, fill=GREEN,
           anchor="middle", weight=600)
    c.text(587, 175, "拷贝数据 + 记录增量，业务照常读写", size=10, fill=SUB,
           anchor="middle")

    c.rect(812, 136, 42, 44, fill=RED, stroke=RED, sw=1.2, r=4)
    c.text(833, 126, "COMMIT", size=9.5, fill=RED, anchor="middle", weight=600)
    c.text(890, 163, "放行", size=10, fill=SUB, anchor="end")

    # ---- 泳道 2：长事务
    c.box(100, 246, 240, 44, "报表事务 23:50 起",
          "持有 MDL_SHARED_READ 不提交", accent=RED, size=12, sub_size=10)
    c.arrow((300, 246), (300, 190), color=RED, dash="5,4", width=1.5,
            label="它不放手，X 就来不了", label_side="left")

    # ---- 泳道 3：排队
    c.box(340, 356, 580, 44, "业务查询：全部排在 PENDING 的 X 后面",
          "MDL 写优先：后来的 S 不许插到 X 前面", accent=RED, size=13, sub_size=10)
    c.arrow((361, 180), (361, 356), color=SLATE, dash="4,4", width=1.3,
            label="队列写优先", label_side="right")

    # ---- 两处阻塞点
    c.box(40, 466, 430, 76, "① 首端：等 MDL X",
          "长度 = 表上最老那个未提交事务的年龄", accent=RED, size=13, sub_size=10)
    c.box(490, 466, 430, 76, "② 尾端：等活跃事务退出",
          "长度 = 它们还剩多久提交", accent=ORANGE, size=13, sub_size=10)

    c.box(40, 560, 880, 44,
          "等待时间与表大小无关，只与表上还有几个没提交的事务有关",
          accent=SLATE, size=13)
    return c.save(os.path.join(OUT, "ch46-fig2.svg"))


# ---------------------------------------------------------------- 图 46-3
def fig3():
    c = Canvas(960, 720,
               title="图 46-3　gh-ost 与 pt-osc：两条增量路径，同一个结尾",
               subtitle="左边从复制流里读增量，右边从触发器里拿增量；最后都靠一次原子 RENAME 换名")

    c.arrow((480, 100), (480, 570), color=SLATE, dash="4,6", width=1, end=False)

    left = [
        ("主库 order_main", "业务照常读写", BLUE),
        ("伪装成从库拉 binlog", "ROW 格式 + 复制权限", PURPLE),
        ("_order_main_gho 影子表", "同结构，按主键分块拷", BLUE),
        ("_order_main_ghc 状态表", "断点续传 + 限流记录", TEAL),
        ("限流开关 max-load", "超 --max-lag 就暂停拷贝", ORANGE),
        ("cut-over：写锁 + RENAME", "原表改名 _del，确认后删", RED),
    ]
    right = [
        ("主库 order_main", "业务照常读写", BLUE),
        ("3 个触发器 INS/UPD/DEL", "增量同事务写进新表", ORANGE),
        ("_order_main_new 新表", "同结构，按主键分块拷", BLUE),
        ("存量分块拷贝", "chunk-time 控制每块时长", BLUE),
        ("触发器自身的代价", "每次写入多一次执行", RED),
        ("RENAME TABLE 原子替换", "再删旧表与 3 个触发器", RED),
    ]

    for col, (x, items) in enumerate([(56, left), (536, right)]):
        for i, (t, s, a) in enumerate(items):
            y = 124 + i * 72
            c.box(x, y, 368, 48, t, s, accent=a, size=13, sub_size=10)
            if i < len(items) - 1:
                c.arrow((x + 184, y + 48), (x + 184, y + 72),
                        color=PURPLE if (col == 0 and i == 0) else
                        (ORANGE if (col == 1 and i == 0) else SLATE),
                        width=1.4)

    c.text(56, 100, "gh-ost：增量来自复制流", size=12, fill=PURPLE, weight=600)
    c.text(536, 100, "pt-osc：增量来自触发器", size=12, fill=ORANGE, weight=600)

    c.box(40, 596, 880, 56,
          "共同点：最后都靠一次原子 RENAME",
          "cut-over 那一瞬仍要拿排它锁；表上只要有长事务，这一段照样等",
          accent=SLATE, size=14, sub_size=11)

    c.text(40, 690,
           "区别在增量从哪来：一个读日志，碰不到写路径；一个挂触发器，与业务写同生共死。",
           size=11, fill=SUB)
    return c.save(os.path.join(OUT, "ch46-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
