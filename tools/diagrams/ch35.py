#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 35 章配图：冷热分层与多租户"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 35-1
def fig1():
    c = Canvas(960, 760,
               title="图 35-1　冷热三层：每层三个刻度，两条迁移触发条件",
               subtitle="箭头是数据流，不是查询流；分层判据是访问概率，不是数据年龄")

    # 表头：三个刻度
    for x, lab in ((330, "访问延迟"), (500, "存储成本"), (640, "谁在查它")):
        c.text(x, 104, lab, size=11, fill=SUB, weight=600)

    # ---- 热层
    c.container(40, 120, 760, 118, "")
    c.text(60, 158, "热｜InnoDB 主库", size=15, weight=600)
    c.text(60, 182, "近 7 天，或状态未终态", size=11, fill=SUB)
    c.text(330, 160, "单行 < 1ms", size=11)
    c.text(330, 182, "全在 buffer pool", size=11, fill=SUB)
    c.text(500, 160, "最高", size=11)
    c.text(500, 182, "SSD + 多副本", size=11, fill=SUB)
    c.text(640, 160, "下单、支付、客服查单", size=10.5)
    c.text(640, 182, "高并发、低延迟", size=10.5, fill=SUB)

    # ---- 迁移：热 → 温
    c.arrow((200, 238), (200, 300), color=ORANGE, width=1.8,
            label="行龄 > 90 天 且 30 天零命中", label_side="right")
    c.text(208, 288, "按主键分批，批间看复制延迟", size=10, fill=ORANGE)

    # ---- 温层
    c.container(40, 300, 760, 118, "")
    c.text(60, 338, "温｜order_archive", size=15, weight=600)
    c.text(60, 362, "90 天至 1 年，偶发查", size=11, fill=SUB)
    c.text(330, 340, "百 ms 级", size=11)
    c.text(330, 362, "允许落盘读", size=11, fill=SUB)
    c.text(500, 340, "中", size=11)
    c.text(500, 362, "大容量盘、单副本", size=11, fill=SUB)
    c.text(640, 340, "客诉回溯、日终对账", size=10.5)
    c.text(640, 362, "低频、可排队", size=10.5, fill=SUB)

    # ---- 迁移：温 → 冷
    c.arrow((200, 418), (200, 480), color=ORANGE, width=1.8,
            label="满 1 年无人查，仅合规留存", label_side="right")

    # ---- 冷层
    c.container(40, 480, 760, 118, "")
    c.text(60, 518, "冷｜对象存储 / OLAP", size=15, weight=600)
    c.text(60, 542, "只作留痕，不再承诺查询", size=11, fill=SUB)
    c.text(330, 520, "秒到分钟", size=11)
    c.text(330, 542, "异步导出", size=11, fill=SUB)
    c.text(500, 520, "最低", size=11)
    c.text(500, 542, "按量计费", size=11, fill=SUB)
    c.text(640, 520, "审计、法务、离线分析", size=10.5)
    c.text(640, 542, "几乎不在线", size=10.5, fill=SUB)

    # ---- 冷数据回查：右侧通道，不进任何一层
    c.arrow([(800, 540), (880, 540), (880, 179), (802, 179)],
            color=SLATE, width=1.6, dash="5,4")
    c.text(868, 168, "冷数据回查", size=10, fill=SLATE, anchor="end")

    # ---- 结论带
    c.container(40, 600, 840, 64, "")
    c.text(60, 626, "按「多久以前产生」分层，是用写入节奏去赌查询节奏；按「多久被访问一次」分层，才是容量决策。",
           size=12)
    c.text(60, 650, "冷层不是「不要的数据」，是「不再承诺在线查询的数据」——这句话决定了回查只能异步。",
           size=12, fill=SLATE)

    c.legend(40, 680, [
        (ORANGE, "迁移任务：分批复制 → 校验 → 删除", None),
        (SLATE, "冷数据回查：异步导出，不承诺延迟", "5,4"),
    ])
    return c.save(os.path.join(OUT, "ch35-fig1.svg"))


# ---------------------------------------------------------------- 图 35-2
def fig2():
    c = Canvas(960, 740,
               title="图 35-2　多租户三模型：隔离强度、成本，与那条没人写进合同的隐性代价",
               subtitle="隔离越弱，越省钱，也越容易让一个租户的事故变成所有租户的事故")

    heads = [("独立库", GREEN), ("共享库独立 schema", BLUE), ("共享表 + tenant_id", ORANGE)]
    for i, (lab, color) in enumerate(heads):
        c.box(200 + i * 240, 108, 200, 44, lab, accent=color, size=12.5)

    rows = [
        ("隔离强度", [
            ("最强", "独立实例，故障不扩散"),
            ("中", "同实例，共享 buffer pool"),
            ("最弱", "靠 tenant_id 与代码自觉"),
        ]),
        ("成本", [
            ("最高", "一租户一套实例"),
            ("中", "共享实例，逻辑隔离"),
            ("最低", "一张表装下所有租户"),
        ]),
        ("运维复杂度", [
            ("最高", "N 套备份与升级"),
            ("中", "DDL 广播到每个 schema"),
            ("低", "一次 DDL 全租户生效"),
        ]),
        ("单实例租户上限", [
            ("几十", "受实例成本约束"),
            ("几千到几万", "元数据先变慢"),
            ("十万级", "受单表容量约束"),
        ]),
        ("典型场景", [
            ("金融、政企", "数据驻留要求"),
            ("中大型客户", "需按租户授权"),
            ("SaaS 长尾", "绝大多数"),
        ]),
    ]

    accents = [GREEN, BLUE, ORANGE]
    for r, (label, cells) in enumerate(rows):
        y = 164 + r * 68
        c.text(40, y + 36, label, size=12, fill=INK, weight=600)
        for i, (t, sub) in enumerate(cells):
            c.box(200 + i * 240, y, 200, 60, t, sub, accent=accents[i],
                  size=11.5, sub_size=10)

    # ---- 隐性代价
    c.container(40, 528, 840, 180,
                "共享表方案的隐性代价：一次大租户全表扫描，所有人一起掉命中率")

    # buffer pool 占用条
    c.text(60, 578, "buffer pool 里的页（示意）", size=10.5, fill=SUB)
    c.rect(60, 588, 560, 26, fill="#fee2e2", stroke=RED, sw=1.2, r=4)
    c.rect(60, 588, 336, 26, fill="#fecaca", stroke=RED, sw=1.2, r=4)
    c.rect(396, 588, 112, 26, fill="#bfdbfe", stroke=BLUE, sw=1.2, r=4)
    c.rect(508, 588, 112, 26, fill="#bbf7d0", stroke=GREEN, sw=1.2, r=4)
    c.text(66, 605, "大租户扫描带入的冷页", size=10, fill=RED)
    c.text(402, 605, "其他租户热页", size=10, fill=BLUE)
    c.text(514, 605, "空闲", size=10, fill=GREEN)

    c.text(60, 646, "LRU 是全局的：大租户的扫描把冷页灌进 young 区，别人的热页被推到 old 区并淘汰。",
           size=11.5)
    c.text(60, 668, "症状是所有租户命中率一起掉，监控上只看到 IOPS 上涨——除非按 tenant_id 记录扫描行数，否则查不到是谁干的。",
           size=11.5, fill=RED)
    c.text(60, 690, "治它只有两条：消掉那次全表扫描（补索引、归档），或把大租户搬到独立库。",
           size=11.5, fill=SLATE)
    return c.save(os.path.join(OUT, "ch35-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
