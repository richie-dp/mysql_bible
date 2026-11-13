#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 31 章配图：范式、反范式与表结构演进"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 31-1
def fig1():
    c = Canvas(960, 700,
               title="图 31-1　宽表与窄表：同样的 16KB 页，四种与四十种行密度",
               subtitle="2 亿行、页可用 16256B；buffer pool 128GB 按九成给数据页，行宽 4KB 与 400B 各算一遍")

    # ---------------- ① 宽表
    c.container(40, 82, 430, 322, "① 宽表　行宽 4000B → 每页 4 行")
    c.rect(62, 120, 386, 232, fill="#f8fafc", stroke=LINE, sw=1.2, r=6)
    for i in range(4):
        y = 128 + i * 56
        hot = (i == 1)
        c.rect(72, y, 366, 48, fill="#fef2f2",
               stroke=(ORANGE if hot else "#fecaca"), sw=(2.2 if hot else 1.2), r=5)
        c.rect(72, y, 34, 48, fill=GREEN, stroke=GREEN, sw=1, r=5)
        c.text(116, y + 22, f"第 {i + 1} 行", size=12, fill=INK, weight=600)
        c.text(116, y + 38, "整行 4000B 全部读入", size=10, fill=SUB)
        c.text(428, y + 22, "23B", size=11, fill=GREEN, anchor="end", weight=600)
        c.text(428, y + 38, "有用", size=9, fill=GREEN, anchor="end")
    c.text(62, 372, "16256B ÷ 4000B = 4 行/页", size=11, fill=SUB)
    c.text(62, 390, "绿色 = 要的 3 列（23B，宽度放大）；其余 3977B 白读", size=10, fill=RED)

    # ---------------- ② 窄表
    c.container(490, 82, 430, 322, "② 窄表　行宽 400B → 每页 40 行")
    c.rect(512, 120, 386, 232, fill="#f8fafc", stroke=LINE, sw=1.2, r=6)
    for i in range(40):
        y = 125 + i * 5.6
        c.rect(522, y, 366, 4.4, fill="#f0fdf4", stroke="#bbf7d0", sw=0.8, r=2)
    c.text(512, 372, "16256B ÷ 400B ≈ 40 行/页", size=11, fill=SUB)
    c.text(512, 390, "同样一页，多出 36 行的命中机会", size=10, fill=GREEN)

    # ---------------- ③ 覆盖率
    c.container(40, 424, 880, 178, "③ 同样的 128GB buffer pool，能装下的行数差十倍")
    c.text(62, 486, "宽表 800GB", size=12, fill=INK, weight=600)
    c.badge(62, 496, "3000 万行", accent=RED)
    c.rect(200, 470, 660, 26, fill="#f1f5f9", stroke=LINE, sw=1, r=5)
    c.rect(200, 470, 99, 26, fill=RED, stroke=RED, sw=1, r=5)
    c.text(862, 489, "覆盖 15%", size=12, fill=RED, anchor="end", weight=600)

    c.text(62, 546, "窄表 80GB", size=12, fill=INK, weight=600)
    c.badge(62, 556, "3 亿行", accent=GREEN)
    c.rect(200, 530, 660, 26, fill="#f0fdf4", stroke="#bbf7d0", sw=1, r=5)
    c.rect(200, 530, 660, 26, fill=GREEN, stroke=GREEN, sw=1, r=5)
    c.text(862, 549, "覆盖 100%", size=12, fill="#ffffff", anchor="end", weight=600)

    c.text(62, 590, "差距不在 IO 次数：两种表回表都是 4 次页访问；差距在 IO 落在内存还是磁盘——宽表 85% 的回表落盘。",
           size=11, fill=INK)

    c.text(40, 634, "体积：2 亿 × 4000B ≈ 800GB　｜　2 亿 × 400B ≈ 80GB　　叶页：5000 万　vs　500 万",
           size=11, fill=SUB)
    c.text(40, 656, "同样 2 亿行，树高都是四层；被行宽改变的只有叶子层的页数，以及这些页能有多少留在内存里。",
           size=11, fill=BLUE)
    return c.save(os.path.join(OUT, "ch31-fig1.svg"))


# ---------------------------------------------------------------- 图 31-2
def fig2():
    c = Canvas(960, 650,
               title="图 31-2　反范式三手段：写入路径、不一致窗口与补偿动作",
               subtitle="窗口长度由写入路径决定；补偿动作的幂等性决定重放会不会把旧值写回去")

    cols = [
        (40, "① 冗余字段　receiver_name", [
            ("写入路径", "下单事务内写快照", BLUE),
            ("不一致窗口", "快照 0；当前值=回填延迟", ORANGE),
            ("补偿动作", "变更消息 + 分批回填", GREEN),
        ]),
        (347, "② 汇总表　account_balance", [
            ("写入路径", "流水与余额同事务双写", BLUE),
            ("不一致窗口", "跨库=消息延迟；漏写永久", RED),
            ("补偿动作", "日终对账 + 幂等重算", GREEN),
        ]),
        (654, "③ 宽表　order_wide", [
            ("写入路径", "订单变更 → 异步重建宽表", BLUE),
            ("不一致窗口", "秒级到分钟级", RED),
            ("补偿动作", "版本号比对 + 全量重建", GREEN),
        ]),
    ]

    for x, title, rows in cols:
        c.container(x, 84, 266, 424, title)
        cx = x + 133
        for i, (t, s, color) in enumerate(rows):
            y = 132 + i * 124
            c.box(x + 13, y, 240, 76, t, s, accent=color, size=13, sub_size=11)
            if i < 2:
                c.arrow(cx, y + 76, cx, y + 124,
                        color=(SLATE if i == 0 else GREEN),
                        width=1.8, dash=(None if i == 1 else "5,3"))

    c.container(40, 528, 880, 96, "三条不变式")
    c.text(62, 574, "1　写入路径越长，窗口越长：同事务双写为 0，异步重建以秒计，跨库消息以消息延迟计。",
           size=11, fill=INK)
    c.text(62, 596, "2　窗口内所有读都可能读到旧值，所以「读多写少」是反范式成立的前提。",
           size=11, fill=INK)
    c.text(62, 616, "3　补偿必须幂等：以事实源（流水 / 订单）覆盖派生值，重放多少次结果都一样。",
           size=11, fill=RED)
    return c.save(os.path.join(OUT, "ch31-fig2.svg"))


# ---------------------------------------------------------------- 图 31-3
def fig3():
    c = Canvas(960, 640,
               title="图 31-3　状态字段三种设计：四个维度的对照",
               subtitle="生产形态通常是「主表存当前状态 + 流水表存历史」，两者在同一事务里双写")

    heads = [
        (190, 210, "单列状态机"),
        (440, 210, "状态 + 时间戳列"),
        (690, 230, "状态流水表"),
    ]
    c.box(40, 96, 110, 40, "维度", accent=SLATE, size=12)
    for x, w, t in heads:
        c.box(x, 96, w, 40, t, accent=PURPLE, size=12)

    rows = [
        ("查询当前状态", [
            ("一次主键读", "最直接", GREEN),
            ("一次主键读", "顺带读到时间", GREEN),
            ("取最新一条", "ORDER BY id DESC LIMIT 1", ORANGE),
        ]),
        ("查历史变更", [
            ("查不到", "只有当前值", RED),
            ("只有时间点", "没有操作人", ORANGE),
            ("完整流水", "可审计、可追责", GREEN),
        ]),
        ("索引友好度", [
            ("(status, created_at)", "直接可用", GREEN),
            ("(status, shipped_at)", "按事件精确筛", GREEN),
            ("要按 order_id 回查", "无全局状态索引", ORANGE),
        ]),
        ("存储成本", [
            ("1 字节/行", "2 亿行约 200MB", GREEN),
            ("5~8 字节×状态数", "20 状态约 24GB", ORANGE),
            ("60 字节×变更次数", "12 亿行约 100GB", RED),
        ]),
    ]

    for i, (label, cells) in enumerate(rows):
        y = 152 + i * 80
        c.box(40, y, 110, 66, label, accent=SLATE, size=12)
        for j, (t, s, color) in enumerate(cells):
            x, w, _ = heads[j]
            c.box(x, y, w, 66, t, s, accent=color, size=12, sub_size=10)

    c.container(40, 488, 880, 116, "选型顺序")
    c.text(62, 534, "要审计、要算每个状态的停留时长 → 流水表，同时接受主表那一列只是缓存。",
           size=11, fill=INK)
    c.text(62, 556, "只要「某天发货了多少单」这类筛选 → 时间戳列 + (status, 事件时间) 联合索引。",
           size=11, fill=INK)
    c.text(62, 578, "只要当前状态、且状态数固定 → 单列 TINYINT，别为可能的需求提前付列数与 DDL 的成本。",
           size=11, fill=INK)
    return c.save(os.path.join(OUT, "ch31-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
