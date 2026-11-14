#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""附录 F 配图：学习路径与参考"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


def skip_box(c, x, y, w, h, title, sub, size=12.5, sub_size=10.2):
    """虚线边框节点：可跳章。svgkit 的 box() 不带 dash，这里自己组一次。"""
    c.rect(x, y, w, h, fill=TINT[SLATE], stroke=SLATE, sw=1.4, r=8, dash="6,4")
    c._nodes.append((x, y, w, h, title))
    if text_width(title, size) > w - 16:
        c._warn.append(f"文字溢出 [{title}]")
    if text_width(sub, sub_size) > w - 16:
        c._warn.append(f"副标题溢出 [{sub}]")
    c.text(x + w / 2, y + h / 2 - 5, title, size=size, anchor="middle",
           weight=600, fill=SLATE)
    c.text(x + w / 2, y + h / 2 + 15, sub, size=sub_size, anchor="middle", fill=SUB)


def hlegend(c, x, y, items, size=11):
    """横排图例：小色块 + 文字。"""
    for color, label, dash in items:
        c.rect(x, y - 9, 14, 12, fill=TINT.get(color, "#ffffff"), stroke=color,
               sw=1.4, r=3, dash=dash)
        c.text(x + 20, y + 1, label, size=size, fill=SUB)
        x += 20 + text_width(label, size) + 30


# ---------------------------------------------------------------- 图 F-1
def fig1():
    c = Canvas(960, 720,
               title="图 F-1　三层同心圆：知识的结构与章节归属",
               subtitle="画成环，是因为三层共享同一套机制；读的顺序不等于画的顺序")

    # 三个环（同心方环，只为表达"层"，不表达包含）
    c.rect(40, 88, 880, 608, fill="none", stroke=BLUE, sw=2, r=26)
    c.rect(148, 186, 664, 422, fill="none", stroke=PURPLE, sw=2, r=22)
    c.rect(256, 284, 448, 236, fill=TINT[GREEN], stroke=GREEN, sw=2, r=18)

    # 第一层
    c.pill(64, 104, 178, 30, "第一层 · 能用对", accent=BLUE)
    c.text(262, 118, "Ch1 → Ch2/3 → Ch8/9 → Ch10~12", size=13,
           fill=BLUE, weight=600)
    c.text(262, 142, "一条 SQL 从文本到一行数据，经过哪些排队点", size=11.5, fill=SUB)
    c.text(262, 164, "产出：写对 SQL、看懂 EXPLAIN、说清慢在哪一层", size=11.5, fill=SUB)

    # 第二层
    c.pill(172, 202, 178, 30, "第二层 · 能诊断", accent=PURPLE)
    c.text(370, 216, "Ch4/5 → Ch17~20 → Ch6/7", size=13, fill=PURPLE, weight=600)
    c.text(370, 240, "数据怎么落到盘、怎么保证不丢不错", size=11.5, fill=SUB)
    c.text(370, 262, "产出：定位到层、改对参数、做一次在线 DDL", size=11.5, fill=SUB)

    # 第三层（内核）
    c.text(480, 334, "第三层 · 能读源码", size=13.5, fill=GREEN, anchor="middle",
           weight=600)
    c.text(480, 362, "Ch22~28 → Ch33/34　＋　Ch44", size=12.5, anchor="middle",
           weight=600)
    c.text(480, 390, "多个实例怎么协同：复制、切换、分片、分布式事务", size=11.5,
           fill=SUB, anchor="middle")
    c.text(480, 414, "这一层的问题，单机的答案常常不够用", size=11.5,
           fill=SUB, anchor="middle")
    c.text(480, 446, "从库回放慢、切换丢事务、跨分片不一致——", size=11,
           fill=SUB, anchor="middle")
    c.text(480, 468, "都要回到第 4、6 章的日志格式里找根因", size=11,
           fill=SUB, anchor="middle")

    # 第二层底部：两条链
    c.text(172, 548, "第二层的两条链：第 4→5→6→7 章（数据怎么落盘、怎么恢复），"
                     "第 17→18→19→20 章（并发时谁挡住谁）。", size=11, fill=INK)
    c.text(172, 572, "两条链的交汇点是 redo 与 undo 同时参与一次提交——"
                     "这也是第 6 章读起来最费力的原因。", size=11, fill=SUB)
    c.text(172, 596, "两个最常见的错觉：以为 redo 是写缓存，以为 undo 是备份。",
           size=11, fill=SUB)

    # 第一层底部：三句判断
    c.text(64, 636, "第 1 章是全书的索引：读不懂它，后面每一章都会吃力。",
           size=12, fill=RED, weight=600)
    c.text(64, 662, "三层不是能力等级，是问题域的扩张；跨层学习是大多数人的卡点。",
           size=11.5, fill=INK)
    c.text(64, 686, "画成同心圆，是因为三层共享同一套机制，不是因为外层包含内层。",
           size=11.5, fill=SUB)
    return c.save(os.path.join(OUT, "appF-fig1.svg"))


# ---------------------------------------------------------------- 图 F-2
COLS = [40, 270, 500, 730]
ROWS = [96, 206, 316, 426, 536, 646]
W, H = 190, 54


def node(c, col, row, title, sub, accent=None, hub=False, skip=False):
    x, y = COLS[col], ROWS[row]
    if skip:
        skip_box(c, x, y, W, H, title, sub)
        return x, y
    c.box(x, y, W, H, title, sub, accent=accent, size=12.5, sub_size=10.2,
          sw=2.4 if hub else 1.5)
    return x, y


def fig2():
    c = Canvas(960, 760,
               title="图 F-2　章节依赖图：哪些必须先读，哪些可以按需跳",
               subtitle="只画枢纽与关键依赖；红色是断了会连带一片的章，灰色虚线是不在主依赖链上的章")

    # 第 0 行：根
    c.box(270, 96, 420, H, "Ch1　一条 SQL 的生命周期",
          "全书的索引：四层结构与 handler 边界", accent=RED, size=14,
          sub_size=11, sw=2.6)

    # 第 1 行：两条主干
    node(c, 0, 1, "Ch4　Redo Log", "WAL：先写日志，再刷页", accent=RED, hub=True)
    node(c, 1, 1, "Ch2/3　内存与磁盘", "页、表空间、Buffer Pool", accent=BLUE)
    node(c, 2, 1, "Ch8/9　B+ 树与索引", "索引组织表与失效边界", accent=BLUE)
    node(c, 3, 1, "Ch10~12　统计与计划", "成本模型、EXPLAIN、Join", accent=BLUE)

    # 第 2 行
    node(c, 0, 2, "Ch5　Undo 与 Purge", "版本链、回滚与 purge", accent=PURPLE)
    node(c, 1, 2, "Ch16/17　事务与 MVCC", "ACID 与可见性判定", accent=PURPLE)
    node(c, 3, 2, "Ch13~15　改写与临时表", "可跳：用到再读", skip=True)

    # 第 3 行
    node(c, 0, 3, "Ch6　Binlog 与 2PC", "两份日志如何一致", accent=PURPLE)
    node(c, 1, 3, "Ch18　锁体系", "四个正交维度", accent=RED, hub=True)
    node(c, 2, 3, "Ch19/20　加锁与死锁", "规则推演与现场取证", accent=PURPLE)
    node(c, 3, 3, "Ch21　长事务治理", "回滚多久、锁多久", accent=PURPLE)

    # 第 4 行
    node(c, 0, 4, "Ch7　崩溃恢复", "崩溃后凭什么能起来", accent=PURPLE)
    node(c, 1, 4, "Ch44　源码导读", "按需：有具体问题再进", skip=True)
    node(c, 2, 4, "Ch22　复制原理", "事件流：搬一次、放一次", accent=RED, hub=True)
    node(c, 3, 4, "Ch23~25　GTID 与延迟", "位点、半同步、回放", accent=GREEN)

    # 第 5 行
    node(c, 0, 5, "Ch33/34　分片与分布式", "跨实例的一致性与事务", accent=GREEN)
    node(c, 1, 5, "Ch27　MGR（可跳）", "可跳：集群选型时读", skip=True)
    node(c, 2, 5, "Ch26/28　高可用与备份", "切换与 PITR", accent=GREEN)
    node(c, 3, 5, "Ch32　分区表（可跳）", "可跳：不在主依赖链", skip=True)

    # 连线
    # 根到两条主干
    c.arrow((330, 150), (135, 206), color=RED, width=2)     # Ch1 → Ch4
    c.arrow((430, 150), (365, 206), color=BLUE)             # Ch1 → Ch2/3
    # SQL 主干：横向
    c.arrow((460, 233), (500, 233), color=BLUE)             # 2/3 → 8/9
    c.arrow((690, 233), (730, 233), color=BLUE)             # 8/9 → 10~12
    c.arrow((825, 260), (825, 316), color=SLATE, dash="5,4")  # 10~12 → 13~15
    # 落盘主干：纵向
    c.arrow((135, 260), (135, 316), color=PURPLE)           # 4 → 5
    c.arrow((135, 370), (135, 426), color=PURPLE)           # 5 → 6
    c.arrow((135, 480), (135, 536), color=PURPLE)           # 6 → 7
    # 事务与锁
    c.arrow((230, 343), (270, 343), color=PURPLE)           # 5 → 16/17
    c.arrow((365, 370), (365, 426), color=PURPLE)           # 16/17 → 18
    c.arrow((460, 453), (500, 453), color=RED)              # 18 → 19/20
    c.arrow((690, 453), (730, 453), color=PURPLE)           # 19/20 → 21
    c.arrow((365, 480), (365, 536), color=SLATE, dash="5,4")  # 18 → 44（按需）
    # binlog 到复制：走两行之间的空档
    c.arrow([(230, 453), (250, 453), (250, 508), (595, 508), (595, 536)],
            color=RED, width=2)
    # 多实例
    c.arrow((690, 563), (730, 563), color=GREEN)            # 22 → 23~25
    c.arrow((595, 590), (135, 646), color=GREEN)            # 22 → 33/34
    c.arrow((825, 590), (595, 646), color=GREEN)            # 23~25 → 26/28
    c.arrow((500, 673), (460, 673), color=SLATE, dash="5,4")  # 26/28 → 27

    hlegend(c, 40, 728, [
        (BLUE, "第一层：能用对", None),
        (PURPLE, "第二层：能诊断", None),
        (GREEN, "第三层：能读源码", None),
        (RED, "枢纽章：跳过后多处读不懂", None),
        (SLATE, "可跳章：虚线框", "4,3"),
    ], size=10.6)

    return c.save(os.path.join(OUT, "appF-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
