#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 47 章配图：SQL 审核与治理闭环"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 47-1
def fig1():
    c = Canvas(960, 640,
               title="图 47-1　门禁的天花板：上线这一刻，能看见的到这里为止",
               subtitle="左边查的是文本形态与估算值，右边只有跑起来才有；中间那条竖线不是流程节点，是信息断点")

    # ---- 两栏标题
    c.text(56, 96, "能挡住的：静态文本 + 优化器估算", size=12, fill=GREEN, weight=600)
    c.text(528, 96, "挡不住的：只有运行时才有", size=12, fill=RED, weight=600)

    # ---- 中间的分界线
    c.pill(408, 104, 144, 24, "上线这一刻", accent=SLATE, size=11.5)
    c.arrow((480, 130), (480, 530), color=SLATE, dash="5,6", width=1.5, end=False)

    # ---- 左栏：门禁能做的三件
    c.container(56, 140, 376, 390, "进入系统之前：审的是 SQL 文本")
    left = [
        ("语法与形态检查", "禁 SELECT *、无 WHERE 更新", BLUE),
        ("影响行数估算", "EXPLAIN 的 rows 乘过滤率", BLUE),
        ("DDL 的算法与锁", "ALGORITHM 与 LOCK 必须写明", BLUE),
    ]
    for i, (t, s, a) in enumerate(left):
        c.box(76, 178 + i * 108, 336, 88, t, s, accent=a, size=14, sub_size=10.5)

    # ---- 右栏：门禁看不见的三件
    c.container(528, 140, 376, 390, "跑起来之后：看的是真实数据")
    right = [
        ("真实扫描行数", "估算值；统计信息旧了它也错", RED),
        ("并发下的等待", "80ms × 50 QPS，等于 4 条在跑", ORANGE),
        ("链路总耗时", "12 条各 80ms，接口就是 960ms", PURPLE),
    ]
    for i, (t, s, a) in enumerate(right):
        c.box(548, 178 + i * 108, 336, 88, t, s, accent=a, size=14, sub_size=10.5)

    # ---- 跨线：SQL 进入运行时
    c.arrow((432, 330), (524, 330), color=SLATE, width=1.6, label="SQL 上线")

    # ---- 结论条
    c.box(56, 552, 848, 62,
          "门禁的价值：把低级错误挡在门外",
          "它不保证线上不出问题；当成保险，出事时第一句话就是「不是审核过了吗」",
          accent=SLATE, size=14, sub_size=10.5)
    return c.save(os.path.join(OUT, "ch47-fig1.svg"))


# ---------------------------------------------------------------- 图 47-2
def fig2():
    c = Canvas(960, 660,
               title="图 47-2　治理闭环四步：每一步都要有名字、有期限、有归因",
               subtitle="缺任何一步，整条链都退化成「每周筛一遍，再倒回同一个池子」")

    cards = [
        (56, 104, BLUE, "① 聚合", "按 DIGEST 合并，不看单条", [
            ("输入", "两份间隔快照（周初 / 周末）"),
            ("产出", "增量 TOP 10，带 COUNT_STAR 增量"),
            ("缺了它", "榜单被历史累计值占满"),
            ("读法", "先看增量，再看次数"),
        ]),
        (508, 104, RED, "② 定责", "唯一一步工具替不了", [
            ("输入", "DIGEST + SCHEMA_NAME"),
            ("产出", "业务名 + 具名 Owner"),
            ("缺了它", "优化项烂在别人的待办里"),
            ("断点", "表里没有 user / host"),
        ]),
        (508, 362, GREEN, "③ 分派", "挂到人，带上期限", [
            ("输入", "TOP N + 已认领的 Owner"),
            ("产出", "SLA 与到期日"),
            ("缺了它", "排期永远排在需求后面"),
            ("期限", "P0 24h · P1 一周 · P2 季度"),
        ]),
        (56, 362, PURPLE, "④ 复盘", "看新增的从哪来", [
            ("输入", "上月 TOP 与本月新增"),
            ("产出", "归因：门禁失效 / 容量失效"),
            ("缺了它", "同一个问题每季度复发"),
            ("判据", "新功能查门禁，老功能查容量"),
        ]),
    ]

    for x, y, col, title, sub, lines in cards:
        stroke = BORDER[RED] if col == RED else "#e5e7eb"
        c.container(x, y, 396, 214, "", stroke=stroke)
        c.box(x + 14, y + 12, 368, 46, title, sub, accent=col, size=13.5,
              sub_size=9.5)
        for i, (k, v) in enumerate(lines):
            yy = y + 86 + i * 28
            key_col = RED if (col == RED and k == "断点") else col
            c.text(x + 20, yy, k + "｜", size=10.5, fill=key_col, weight=600)
            c.text(x + 66, yy, v, size=10.5,
                   fill=RED if (col == RED and k == "断点") else INK)

    # ---- 闭环箭头（顺时针）
    c.arrow((452, 211), (504, 211), color=SLATE, width=1.6)
    c.arrow((706, 318), (706, 358), color=SLATE, width=1.6)
    c.arrow((508, 469), (456, 469), color=SLATE, width=1.6)
    c.arrow((254, 362), (254, 322), color=SLATE, width=1.6)

    c.box(56, 596, 848, 52,
          "断点在「定责」：digest 表只有 SCHEMA_NAME",
          "没有 user / host，只能靠库名前缀或注释打标补上；注释是否参与归一化，先在测试库验证",
          accent=RED, size=13, sub_size=10)
    return c.save(os.path.join(OUT, "ch47-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
