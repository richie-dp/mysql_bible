#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 4 章配图：Redo Log 的物理结构、四个 LSN 与 checkpoint 雪崩链"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 4-1
def fig1():
    c = Canvas(960, 640, title="图 4-1　redo log 是一个环：write pos 追着 checkpoint 跑",
               subtitle="环上的每一段对应一种状态；checkpoint 想前进，必须先把最老的脏页刷下去")

    cx, cy, r, sw = 330, 315, 118, 48
    c.raw(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" '
          f'stroke="#eef2f7" stroke-width="{sw}"/>')

    def pt(deg):
        a = math.radians(deg)
        return (cx + r * math.sin(a), cy - r * math.cos(a))

    def arc(a1, a2, color):
        x1, y1 = pt(a1)
        x2, y2 = pt(a2)
        large = 1 if (a2 - a1) % 360 > 180 else 0
        c.raw(f'<path d="M {x1:.2f} {y1:.2f} A {r} {r} 0 {large} 1 '
              f'{x2:.2f} {y2:.2f}" fill="none" stroke="{color}" '
              f'stroke-width="{sw}"/>')

    # 顺时针：[checkpoint 290 -> pages flushed 370] 已落盘
    #         [pages flushed 10  -> write pos 90]   待刷脏
    #         [write pos 90      -> checkpoint 290]  可写
    arc(90, 290, "#e2e8f0")     # 可写区间（浅灰）
    arc(290, 370, GREEN)        # 已刷盘、可回收
    arc(370, 450, ORANGE)       # 待刷脏，必须保留

    def marker(deg, color):
        x, y = pt(deg)
        c.raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="8" fill="#ffffff" '
              f'stroke="{color}" stroke-width="3"/>')
        return x, y

    xcp, ycp = marker(290, GREEN)
    xpf, ypf = marker(10, ORANGE)
    xwp, ywp = marker(90, SLATE)

    c.text(xcp - 26, ycp + 4, "checkpoint", size=11, anchor="end", weight=600)
    c.text(xpf, ypf - 32, "pages flushed up to", size=11, anchor="middle",
           fill=ORANGE, weight=600)
    c.text(xwp + 30, ywp + 4, "write pos", size=11, fill=SLATE, weight=600)

    # 右侧说明面板
    c.container(540, 170, 380, 250, "三个指针把环切成三段")
    rows = [
        (215, GREEN, "已落盘（可回收）",
         "对应页已刷，checkpoint 越过即可覆盖"),
        (267, ORANGE, "待刷脏（必须保留）",
         "页还在 Buffer Pool 里，覆盖就永久丢"),
        (319, SLATE, "可写区间",
         "capacity − checkpoint age"),
    ]
    for y, col, head, desc in rows:
        c.rect(560, y - 10, 14, 14, fill=col, stroke=col, sw=1, r=3)
        c.text(584, y + 2, head, size=12, weight=600, fill=INK)
        c.text(584, y + 20, desc, size=11, fill=SUB)

    c.raw(f'<line x1="556" y1="352" x2="904" y2="352" stroke="#e5e7eb" '
          f'stroke-width="1" stroke-dasharray="3,3"/>')
    c.text(556, 374, "write pos        = Log sequence number", size=10, fill=SUB, mono=True)
    c.text(556, 394, "checkpoint       = Last checkpoint at", size=10, fill=SUB, mono=True)

    # 底部：32 个文件
    c.text(60, 496, "8.0.30+：容量 = innodb_redo_log_capacity，切成 32 个文件按 LSN 顺时针循环使用",
           size=11, fill=INK)
    for i in range(32):
        x = 60 + i * 24
        fill = TINT[PURPLE] if i >= 24 else "#f3e8ff"
        c.rect(x, 514, 18, 24, fill=fill, stroke=BORDER[PURPLE], sw=1, r=3)
    c.text(60, 558, "#ib_redo0", size=10, fill=SUB)
    c.text(822, 558, "#ib_redo31", size=10, anchor="end", fill=SUB)
    c.text(360, 558, "旧文件被回收后按顺序重新创建，文件名不保证连续",
           size=10, fill=SUB)

    c.legend(60, 582, [(GREEN, "已落盘", None),
                       (ORANGE, "待刷脏", None),
                       (SLATE, "可写 / 指针", None)])
    return c.save(os.path.join(OUT, "ch04-fig1.svg"))


# ---------------------------------------------------------------- 图 4-2
def fig2():
    c = Canvas(960, 620, title="图 4-2　四个 LSN 在同一条时间轴上的位置",
               subtitle="顺序不可颠倒：checkpoint ≤ pages flushed ≤ log flushed ≤ lsn")

    axis_y = 320
    xs = {"cp": 190, "pf": 350, "lf": 640, "lsn": 820}

    c.arrow(100, axis_y, 884, axis_y, color=SLATE, width=1.5)
    c.text(884, axis_y + 22, "LSN 单调递增 →", size=10, anchor="end", fill=SUB)

    # 上方两排标签
    c.box(115, 132, 150, 54, "last checkpoint at", "可覆盖的起点", accent=GREEN, size=12, sub_size=10)
    c.box(565, 132, 150, 54, "log flushed up to", "已 fsync 到磁盘", accent=BLUE, size=12, sub_size=10)
    c.box(275, 210, 150, 54, "pages flushed up to", "脏页刷盘的水位", accent=ORANGE, size=12, sub_size=10)
    c.box(745, 210, 150, 54, "log sequence number", "已写入 log buffer", accent=SLATE, size=12, sub_size=10)

    for key, color, top in (("cp", GREEN, 186), ("lf", BLUE, 186),
                            ("pf", ORANGE, 264), ("lsn", SLATE, 264)):
        c.arrow(xs[key], top, xs[key], axis_y - 8, color=color, dash="4,3", width=1.2)

    for key, color in (("cp", GREEN), ("pf", ORANGE), ("lf", BLUE), ("lsn", SLATE)):
        c.raw(f'<circle cx="{xs[key]}" cy="{axis_y}" r="6" fill="#ffffff" '
              f'stroke="{color}" stroke-width="2.5"/>')

    # 三段差值
    seg = [(196, 344, GREEN, "已落盘，checkpoint 未推进"),
           (356, 634, ORANGE, "刷脏欠账：页还没刷"),
           (646, 814, BLUE, "还没 fsync")]
    for x1, x2, col, label in seg:
        c.arrow(x1, 352, x2, 352, color=col, start=True, end=True, width=1.4)
        c.text((x1 + x2) / 2, 374, label, size=10, anchor="middle", fill=col)

    # 容量条
    c.text(120, 404, "innodb_redo_log_capacity（默认 100MB）", size=10, fill=SUB)
    c.text(840, 404, "剩余可写", size=10, anchor="end", fill=SUB)
    c.rect(120, 410, 720, 26, fill="#f1f5f9", stroke=LINE, sw=1, r=8)
    c.rect(120, 410, 468, 26, fill=ORANGE, stroke=ORANGE, sw=1, r=8, opacity=0.75)
    c.text(130, 428, "checkpoint age：不可覆盖", size=10, fill="#ffffff", weight=600)
    c.raw(f'<line x1="660" y1="402" x2="660" y2="444" stroke="{RED}" '
          f'stroke-width="1.4" stroke-dasharray="4,3"/>')
    c.text(660, 458, "75% 是工程告警线，不是 InnoDB 的硬阈值", size=10,
           anchor="middle", fill=RED)

    c.mono_box(120, 486, 720, 86, [
        "lsn  −  log flushed      -> 还在内存里的 redo   -> 盯 fsync / 组提交",
        "flushed −  pages flushed -> 刷脏欠账             -> 盯 checkpoint age",
        "lsn  −  last checkpoint  -> 不可覆盖量            -> 除以容量 = 年龄",
    ], title="三个差值各自指向一个故障方向")
    return c.save(os.path.join(OUT, "ch04-fig2.svg"))


# ---------------------------------------------------------------- 图 4-3
def fig3():
    c = Canvas(960, 720, title="图 4-3　checkpoint 年龄过高如何演变成 RT 抖动",
               subtitle="这不是一条直线，是一条越转越快的正反馈回路")

    steps = [
        (100, BLUE, "批量任务持续写入", "一次 UPDATE 只写几十到几百字节，但架不住量大"),
        (194, ORANGE, "checkpoint age 上涨", "最老脏页之后的空间被一点点吃掉"),
        (288, RED, "逼近容量：age / capacity > 75%", "剩余可写空间不足以撑过一次批量任务"),
        (382, BLUE, "page cleaner 全力刷脏", "每轮刷多少页，受 innodb_io_capacity 约束"),
        (476, RED, "刷脏跟不上，用户线程接手", "Single Page Flush：同步刷一页才能腾位置"),
        (570, RED, "RT 抖动，连接堆积", "CPU 不高、磁盘 util 不高，P99 却翻十倍"),
    ]
    for y, col, title, sub in steps:
        c.box(330, y, 300, 64, title, sub, accent=col, size=13, sub_size=10)

    for y in (164, 258, 352, 446, 540):
        c.arrow(480, y, 480, y + 30, color=SLATE, width=1.4)

    # 反馈回路
    c.arrow([(630, 602), (700, 602), (700, 132), (632, 132)],
            color=RED, dash="6,4", width=1.5)
    c.text(710, 368, "反馈回路", size=11, fill=RED, weight=600)
    c.text(710, 386, "越慢 → redo 越多", size=10, fill=RED)
    c.text(710, 402, "→ 越慢", size=10, fill=RED)

    # 左侧：观测悖论
    c.text(310, 500, "为什么 CPU 不高？", size=10, anchor="end", fill=SUB, weight=600)
    c.text(310, 518, "线程在等 IO，不在算", size=10, anchor="end", fill=SUB)
    c.text(310, 594, "为什么磁盘也不高？", size=10, anchor="end", fill=SUB, weight=600)
    c.text(310, 612, "同步小 IO，队列深度上不去", size=10, anchor="end", fill=SUB)

    c.legend(760, 96, [(BLUE, "正常推进", None),
                       (ORANGE, "压力积累", None),
                       (RED, "阻塞 / 风险", None),
                       (RED, "反馈回路", "6,4")])

    c.text(60, 662, "稳态条件：刷脏速率 ≥ 脏页产生速率。容量只决定「还有多久爆炸」，不改变这个斜率。",
           size=11, fill=INK)
    c.text(60, 686, "扩容量买到的是处置窗口，不是豁免权。", size=10, fill=SUB)
    return c.save(os.path.join(OUT, "ch04-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
