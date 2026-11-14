#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""附录 E 配图：面试高频 100 问"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 E-1
def fig1():
    c = Canvas(960, 680,
               title="图 E-1　100 题的七组分布与难度地图",
               subtitle="题数决定复习预算，★ 数量决定优先级，最后一列是面试官真正想区分的东西")

    c.text(56, 92, "组", size=10, fill=SUB, weight=600)
    c.text(168, 92, "题数", size=10, fill=SUB, weight=600)
    c.text(230, 92, "难度（机制深度）", size=10, fill=SUB, weight=600)
    c.text(356, 92, "高频", size=10, fill=SUB, weight=600)
    c.text(420, 92, "占比", size=10, fill=SUB, weight=600)
    c.text(504, 92, "面试官想区分什么", size=10, fill=SUB, weight=600)

    rows = [
        ("引擎与存储", "15", "★★★★", "★ 4", "27%", "分得清日志与页，还是只会背名词", PURPLE),
        ("索引与优化器", "15", "★★★☆", "★ 3", "20%", "会不会用成本模型解释计划", BLUE),
        ("事务与锁", "15", "★★★★★", "★ 3", "20%", "能不能推演一段区间的加锁范围", RED),
        ("复制与高可用", "14", "★★★★", "★ 3", "21%", "分不分得清收到、应用与提交", PURPLE),
        ("建模与 SQL", "14", "★★★", "★ 3", "21%", "设计时想的是错误还是字段", GREEN),
        ("诊断与调优", "14", "★★★★", "★ 2", "14%", "有没有真实排障顺序，不是命令清单", ORANGE),
        ("工程与运维", "13", "★★★★", "★ 2", "15%", "知不知道边界与回退代价", SLATE),
    ]

    for i, (grp, n, diff, star, pct, focus, col) in enumerate(rows):
        y = 100 + i * 74
        c.container(48, y, 864, 64, "")
        c.box(56, y + 10, 104, 44, grp, accent=col, size=11.5)
        c.box(168, y + 10, 54, 44, n, accent=SLATE, size=10.5)
        c.box(230, y + 10, 118, 44, diff, accent=col, size=11)
        c.pill(356, y + 17, 56, 30, star, accent=ORANGE, size=10)
        c.box(420, y + 10, 76, 44, pct, accent=SLATE, size=10.5)
        c.box(504, y + 10, 400, 44, focus, accent=SLATE, size=9.8)

    c.text(56, 634, "标 ★ 的 20 题横跨七组：时间不够时只看它们，剩下的题靠这 20 题的机制往外推。",
           size=11, fill=INK)
    c.text(56, 656, "难度不是知识点多少，是能被追问几层——★ 停在第 2 层，★★★★★ 会一路追到页结构、锁区间与源码分支。",
           size=10.5, fill=SUB)
    return c.save(os.path.join(OUT, "appE-fig1.svg"))


# ---------------------------------------------------------------- 图 E-2
def fig2():
    c = Canvas(960, 720,
               title="图 E-2　六个高频误读：错答与真实机制只差一层",
               subtitle="左列是面试里最常听到的那句话，右列是能继续往下追问的机制")

    c.text(48, 92, "考点", size=10, fill=SUB, weight=600)
    c.text(192, 92, "常见错答（候选人常说的那句）", size=10, fill=RED, weight=600)
    c.text(556, 92, "真实机制（能继续往下推的那层）", size=10, fill=BLUE, weight=600)

    rows = [
        ("Sending data", "在发数据，网络慢", "其实是扫描量在拖",
         "读行 + 处理 + 发送", "扫描时间全算在这一段"),
        ("checkpoint", "用时间戳相减", "系统性低估落后量",
         "两个 LSN 相减", "单位是字节，不是秒"),
        ("Handler_read", "引擎扫过的行数", "拿它和扫描行数对账",
         "Server 向引擎要行", "ICP 与覆盖索引下不相等"),
        ("eq_range 上限", "索引失效了", "以为要重建或强推索引",
         "改用统计估算", "计划仍走索引，估错行数"),
        ("GRANT 之后", "还得再 flush", "不加就担心权限不生效",
         "语句级立即生效", "只有直接改授权表才需要"),
        ("INSTANT 加列", "可以无限加", "以为永远是秒级",
         "每表上限 64 次", "第 65 次整表重建"),
    ]

    for i, (topic, wt, ws, rt, rs) in enumerate(rows):
        y = 100 + i * 100
        c.box(48, y + 10, 128, 64, topic, accent=SLATE, size=10)
        c.box(192, y + 10, 330, 64, wt, ws, accent=RED, size=12, sub_size=9.5)
        c.arrow(526, y + 42, 552, y + 42, color=SLATE, width=1.6)
        c.box(556, y + 10, 356, 64, rt, rs, accent=BLUE, size=12, sub_size=9.5)

    c.text(48, 690, "六条都指向同一个毛病：把「名字」当成「语义」。面试里只要多问一句「那这个数字是怎么算出来的」，就会露底。",
           size=10.5, fill=INK)
    return c.save(os.path.join(OUT, "appE-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
