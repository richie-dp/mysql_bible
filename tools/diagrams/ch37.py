#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 37 章配图：监控指标体系"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 37-1
def fig1():
    c = Canvas(960, 720, title="图 37-1　四层指标的判读卡：正常长什么样，异常长什么样",
               subtitle="红色是本章点名的最高频误读——把命中率当健康度，把延迟归零当追平")

    c.legend(690, 70, [(GREEN, "正常形态", None), (RED, "异常 / 误读", None)])

    cards = [
        (40, 96, "连接层", "占用的坑 vs 正在干活的人", PURPLE, [
            ("Threads_connected", "日周期波动，峰谷比稳定", "阶梯上涨不回落 = 池泄漏", False),
            ("Threads_running", "峰值 ≤ 核数 × 2~3", "高位平台而 QPS 不涨 = 排队", False),
            ("Aborted_connects / Aborted_clients", "仅发布窗口尖峰", "持续 > 0，且要分因排查", False),
        ]),
        (500, 96, "吞吐层", "比例变了才有信息量", BLUE, [
            ("Questions 增速", "与业务 QPS 同步", "平台期突变 = 上游重试", False),
            ("Com_select 占比", "日内稳定", "骤降 = 缓存生效或切流", False),
            ("Innodb_rows_read / Com_select", "接近基线（OLTP 个位数）", "翻倍 = 索引退化", False),
        ]),
        (40, 386, "InnoDB 层", "三个容易算错的公式", GREEN, [
            ("BP 命中率（百分比）", "不用百分比判断", "99.9% 仍可能是百万次物理读", True),
            ("pages_dirty / pages_total", "在 lwm 与 max 之间", "逼近 max = 强制刷脏", False),
            ("checkpoint age / 容量", "< 60%，按刷脏能力推", "> 75% 出现周期性抖动", False),
        ]),
        (500, 386, "复制层", "延迟是最不可靠的那个数", SLATE, [
            ("Seconds_Behind_Source", "只作参考值", "归零 ≠ 追平", True),
            ("GTID 差值 received − executed", "收敛到 0", "双停不动 = 复制断了", False),
            ("Relay_Log_Space", "锯齿，不贴上限", "贴顶锯齿 = applier 落后", False),
        ]),
    ]

    for x, y, name, tag, color, items in cards:
        c.container(x, y, 420, 250, "")
        c.text(x + 16, y + 26, name, size=13.5, fill=color, weight=600)
        c.text(x + 92, y + 26, tag, size=10.5, fill=SUB)
        for i, (var, ok, bad, hot) in enumerate(items):
            ry = y + 42 + i * 64
            if hot:
                c.rect(x + 8, ry - 2, 3, 44, fill=RED, stroke="none", sw=0, r=1.5)
            c.text(x + 18, ry + 14, var, size=11, fill=RED if hot else INK,
                   weight=600, mono=True)
            c.text(x + 18, ry + 33, "正常　" + ok, size=9.5, fill=GREEN)
            c.text(x + 18, ry + 49, "异常　" + bad, size=9.5, fill=RED)

    c.text(40, 682, "四层不是四个仪表盘：先看连接与占比，再看 InnoDB 的机制量，最后才轮到复制。",
           size=11.5, fill=INK)
    return c.save(os.path.join(OUT, "ch37-fig1.svg"))


# ---------------------------------------------------------------- 图 37-2
def fig2():
    c = Canvas(960, 560, title="图 37-2　Threads_connected 与 Threads_running：三种形态",
               subtitle="同一组坐标轴上，两条线的相对走势比各自的绝对值更能定性")

    c.legend(40, 84, [(BLUE, "Threads_connected　资源占用", None),
                      (PURPLE, "Threads_running　并发压力", None),
                      (RED, "异常段标注", "5,3")])

    panels = [
        (40, "① 连接池泄漏", ["connected 阶梯上行，running 平稳", "→ 连接只增不减，池子永不回收"]),
        (345, "② 突发流量", ["两条线同向陡升陡降", "→ 请求真的多了，连接与并发一起涨"]),
        (650, "③ 锁等待积压", ["connected 不变，running 冲高不降", "→ 连接都卡在同一把锁上"]),
    ]

    for px, title, notes in panels:
        c.container(px, 110, 265, 340, "")
        c.text(px + 14, 132, title, size=12.5, fill=INK, weight=600)

        x0, x1 = px + 32, px + 240
        y0, y1 = 400, 180
        c.raw(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{LINE}" stroke-width="1.2"/>')
        c.raw(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{LINE}" stroke-width="1.2"/>')
        c.text(x0 - 6, y1 + 4, "高", size=9, fill=SLATE, anchor="end")
        c.text(x0 - 6, y0, "低", size=9, fill=SLATE, anchor="end")
        c.text(x1, y0 + 16, "时间 →", size=9, fill=SLATE, anchor="end")

        if title.startswith("①"):
            # connected：阶梯上行；running：低位平稳
            d = (f"M {x0},{y0 - 12} L {x0 + 45},{y0 - 12} L {x0 + 45},{y0 - 44} "
                 f"L {x0 + 88},{y0 - 44} L {x0 + 88},{y0 - 78} L {x0 + 130},{y0 - 78} "
                 f"L {x0 + 130},{y0 - 112} L {x0 + 175},{y0 - 112} L {x0 + 175},{y0 - 148} "
                 f"L {x1 - 6},{y0 - 148}")
            c.raw(f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
            c.raw(f'<path d="M {x0},{y0 - 18} L {x0 + 60},{y0 - 16} L {x0 + 120},{y0 - 19} '
                  f'L {x1 - 6},{y0 - 17}" fill="none" stroke="{PURPLE}" stroke-width="2.2"/>')
            c.text(x1 - 8, y0 - 158, "connected ↑", size=9.5, fill=BLUE, anchor="end", weight=600)
            c.text(x1 - 8, y0 - 30, "running →", size=9.5, fill=PURPLE, anchor="end", weight=600)
            c.arrow(x0 + 62, y0 - 178, x0 + 134, y0 - 178, color=RED, dash="5,3", width=1.2,
                    label="持续上行", label_dy=-7)
        elif title.startswith("②"):
            c.raw(f'<path d="M {x0},{y0 - 10} C {x0 + 40},{y0 - 14} {x0 + 62},{y0 - 60} '
                  f'{x0 + 96},{y0 - 128} C {x0 + 118},{y0 - 172} {x0 + 140},{y0 - 150} '
                  f'{x1 - 6},{y0 - 24}" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
            c.raw(f'<path d="M {x0},{y0 - 24} C {x0 + 44},{y0 - 26} {x0 + 70},{y0 - 70} '
                  f'{x0 + 102},{y0 - 112} C {x0 + 124},{y0 - 142} {x0 + 146},{y0 - 120} '
                  f'{x1 - 6},{y0 - 40}" fill="none" stroke="{PURPLE}" stroke-width="2.2"/>')
            c.text(x1 - 8, y0 - 158, "connected", size=9.5, fill=BLUE, anchor="end", weight=600)
            c.text(x1 - 10, y0 - 14, "running", size=9.5, fill=PURPLE, anchor="end", weight=600)
        else:
            c.raw(f'<path d="M {x0},{y0 - 34} L {x0 + 70},{y0 - 34} L {x1 - 6},{y0 - 33}'
                  f'" fill="none" stroke="{BLUE}" stroke-width="2.4"/>')
            c.raw(f'<path d="M {x0},{y0 - 18} L {x0 + 52},{y0 - 18} L {x0 + 52},{y0 - 150} '
                  f'L {x1 - 6},{y0 - 148}" fill="none" stroke="{PURPLE}" stroke-width="2.2"/>')
            c.text(x1 - 8, y0 - 44, "connected →", size=9.5, fill=BLUE, anchor="end", weight=600)
            c.text(x1 - 8, y0 - 160, "running ↑", size=9.5, fill=PURPLE, anchor="end", weight=600)
            c.arrow(x0 + 96, y0 - 120, x0 + 172, y0 - 120, color=RED, dash="5,3", width=1.2,
                    label="持续不降", label_dy=-7)

        c.text(px + 14, 472, notes[0], size=9.8, fill=INK, weight=600)
        c.text(px + 14, 491, notes[1], size=9.8, fill=SUB)

    c.text(40, 528, "判据不是单点读数，而是两条线的相对走势；同一时刻的绝对连接数说明不了谁在等谁。",
           size=11.5, fill=INK)
    return c.save(os.path.join(OUT, "ch37-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
