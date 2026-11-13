#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 51 章配图：容量模型的三个乘法 + 压测拐点"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 51-1
def fig1():
    c = Canvas(960, 700,
               title="图 51-1　容量模型的三个乘法：同一组输入，三种撞墙顺序",
               subtitle="输入是一样的三个量（QPS、行数、行宽）；哪个先撞墙，由业务形态决定，不由你最关心的那个指标决定")

    cols = [
        (50, BLUE, "① 内存：装不装得下",
         ["工作集 = 热行数 × 行宽 × 1.2",
          "40GB ÷ (600B × 1.2) ≈ 5960 万行",
          "命中率 = 常驻行数 ÷ 总行数"],
         ("表 192GB / 池 40GB", "只能常驻 20%，其余靠物理读"),
         ("聚合型：全表扫、大结果集", "把叶子层整段换进来又换出去"),
         ("判据不是总行数，是最近 30 天",
          "那 2400 万行装不装得下")),
        (356, TEAL, "② IO：等不等得到盘",
         ["物理读/秒 = QPS × 页数 × 缺失率",
          "32000 × 4 × 3% ≈ 3800 次/秒",
          "缺失率 = 1 − 命中率"],
         ("3800 / 50000 IOPS", "占单盘 7.7%，看着很安全"),
         ("点查型：一次缺页一次随机读", "命中率掉 1 点 = 1280 次/秒"),
         ("平均值的安全感来自长尾之外，",
          "而长尾才决定 P99")),
        (662, PURPLE, "③ 带宽：发不发得出去",
         ["字节/秒 = QPS × 返回行数 × 行宽",
          "32000 × 20 × 600B ≈ 384MB/s",
          "行宽 = 整行字节 + 索引开销"],
         ("10GbE 上限 1.25GB/s", "已用 31%，监控里看不见"),
         ("列表型：一页 20 行、导出", "网卡先满，CPU 还闲着"),
         ("它在 MySQL 里不显眼，",
          "在交换机上一眼就能看到")),
    ]

    for x0, col, head, formula, got, wall, note in cols:
        c.container(x0, 88, 276, 408, "")
        c.box(x0 + 12, 104, 252, 44, head, accent=col, size=13)
        c.mono_box(x0 + 12, 158, 252, 66, formula, size=10)
        c.box(x0 + 12, 236, 252, 84, got[0], got[1], accent=col,
              size=11.5, sub_size=10)
        c.box(x0 + 12, 330, 252, 76, wall[0], wall[1], accent=ORANGE,
              size=11.5, sub_size=10)
        c.text(x0 + 14, 436, "记住这句：", size=10.5, fill=SUB, weight=600)
        c.text(x0 + 14, 456, note[0], size=10, fill=SUB)
        c.text(x0 + 14, 472, note[1], size=10, fill=SUB)

    c.container(50, 520, 888, 140, "三个乘法必须用同一组数字算一遍")
    pills = [("点查型 → 先撞 IO", TEAL), ("列表型 → 先撞带宽", PURPLE),
             ("聚合型 → 先撞内存", BLUE)]
    for i, (label, col) in enumerate(pills):
        c.pill(141 + i * 248, 556, 210, 36, label, accent=col, size=12)
    c.text(64, 622,
           "只算你最关心的那一项，等于只检查最容易过的那一门：内存算下来很宽裕的表，IO 可能早就满了",
           size=11, fill=SUB)

    return c.save(os.path.join(OUT, "ch51-fig1.svg"))


# ---------------------------------------------------------------- 图 51-2
def fig2():
    c = Canvas(960, 640,
               title="图 51-2　阶梯压测上的拐点与三个信号",
               subtitle="同一份数据只改并发：TPS 先饱和、P99 后跳起，所以只看 TPS 曲线会晚一步")

    c.container(50, 78, 860, 388,
                "在 2000 万行的压测库上做阶梯压测（按示例系统设定推算的形态）")

    xs = [130, 235, 340, 445, 550, 655, 760, 865]
    conc = ["8", "16", "32", "64", "96", "128", "192", "256"]

    # ---- 面板 A：TPS
    c.text(72, 120, "TPS", size=11, fill=BLUE, weight=600)
    c.arrow((120, 240), (120, 124), color=SLATE, width=1.2)
    c.arrow((120, 240), (884, 240), color=SLATE, width=1.2)
    for val, yy in (("10k", 132), ("5k", 186), ("0", 244)):
        c.text(112, yy, val, size=9.5, fill=SUB, anchor="end")

    tps = [227, 215, 191, 160, 148, 144, 145, 146]
    c.arrow([(x, y) for x, y in zip(xs, tps)], color=BLUE, width=2.5, end=False)
    c.text(150, 152, "压测库命中率接近 100%：加并发就涨", size=10.5, fill=BLUE)

    # ---- 面板 B：P99
    c.text(72, 300, "P99 (ms)", size=11, fill=RED, weight=600)
    c.arrow((120, 420), (120, 302), color=SLATE, width=1.2)
    c.arrow((120, 420), (884, 420), color=SLATE, width=1.2)
    for val, yy in (("400", 312), ("200", 366), ("0", 424)):
        c.text(112, yy, val, size=9.5, fill=SUB, anchor="end")

    p99 = [418, 418, 416, 413, 407, 396, 359, 308]
    c.arrow([(x, y) for x, y in zip(xs, p99)], color=RED, width=2.5, end=False)
    c.text(300, 404, "拐点之前几乎是一条直线", size=10.5, fill=RED)

    # ---- 拐点
    c.arrow((655, 124), (655, 420), color=RED, dash="6,4", width=1.4, end=False)
    c.text(664, 122, "拐点：TPS 增幅 < 10%，P99 翻倍", size=11, fill=RED, weight=600)
    c.text(683, 200, "再往上加并发", size=10.5, fill=RED)
    c.text(683, 216, "只加排队，不加吞吐", size=10.5, fill=RED)

    for x, lab in zip(xs, conc):
        c.text(x, 442, lab, size=9.5, fill=SUB, anchor="middle")
    c.text(884, 460, "并发 →", size=10.5, fill=SUB, anchor="end")

    # ---- 三个信号灯
    sig = [
        (50, RED, "P99 非线性上升", "每轮加压翻一倍，P50 还稳"),
        (355, ORANGE, "Threads_running 顶住", "贴着压测并发数，撤压也不降"),
        (660, RED, "wait_free / queue 出现", "刷脏跟不上，请求堵在门口"),
    ]
    for x, col, title, sub in sig:
        c.rect(x + 14, 476, 14, 14, fill=col, stroke=col, r=7)
        c.box(x + 12, 494, 253, 78, title, sub, accent=col,
              size=12.5, sub_size=10)

    c.text(50, 604, "三个信号里任何一个亮起，台阶就到底了；三个一起亮，说明瓶颈已经不在 CPU 上",
           size=11, fill=SUB)
    c.text(50, 624, "错误率突变是第四个信号，它出现在拐点之后：先是超时，再是连接拒绝，最后是死锁激增",
           size=11, fill=SUB)

    return c.save(os.path.join(OUT, "ch51-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
