#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 39 章配图：InnoDB 状态与等待事件解读"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 39-1
def fig1():
    c = Canvas(960, 760, title="图 39-1　SHOW ENGINE INNODB STATUS 的分段地图",
               subtitle="按排障价值排序，不按输出顺序：四段必看、三段按需、一段可跳过")

    X_L, X_DOC, X_R = 320, 330, 672
    c.text(286, 96, "这里能回答什么", size=11, fill=SLATE, weight=600, anchor="end")
    c.text(X_DOC + 14, 96, "段名（按输出顺序）", size=11, fill=SLATE, weight=600)
    c.text(X_R, 96, "判读次序与入口字段", size=11, fill=SLATE, weight=600)

    # 左侧：输出顺序的纵向提示
    c.els.append(f'<line x1="303" y1="112" x2="303" y2="660" stroke="{LINE}" '
                 f'stroke-width="1.2" stroke-dasharray="5,5"/>')
    c.text(303, 678, "输出从上到下", size=9.5, fill=SUB, anchor="middle")

    rows = [
        ("BACKGROUND THREAD", "主线程在忙什么", SLATE, "跳过",
         "只有 loops 三段计数"),
        ("SEMAPHORES", "内部在争哪把锁", ORANGE, "② 必看",
         "OS waits 在不在涨"),
        ("TRANSACTIONS", "谁在改、改了多久", RED, "① 必看",
         "undo log entries"),
        ("FILE I/O", "IO 是排队还是闲", BLUE, "按需",
         "pending aio / fsync"),
        ("INSERT BUFFER AND ADAPTIVE HASH INDEX", "写放大有多大", BLUE, "按需",
         "merges 与 size 的差"),
        ("LOG", "checkpoint 落后多远", PURPLE, "④ 必看",
         "LSN − Last checkpoint"),
        ("BUFFER POOL AND MEMORY", "脏页与命中率", BLUE, "按需",
         "old 区占比、脏页数"),
        ("ROW OPERATIONS", "入口堵没堵", GREEN, "③ 必看",
         "queries in queue"),
    ]

    y = 112
    for name, question, col, order, note in rows:
        c.box(X_DOC, y, 330, 58, name, accent=col, size=10.5, mono=True)
        c.text(286, y + 34, question, size=10.5, fill=INK, anchor="end")
        bcol = RED if "必看" in order else (BLUE if order == "按需" else SLATE)
        c.badge(X_R, y + 10, order, accent=bcol, size=10)
        c.text(X_R, y + 46, note, size=9.5, fill=SUB, mono=True)
        y += 70

    c.text(60, 706, "读这份输出的次序由「能不能定方向」决定，与打印顺序无关；"
                    "认字段名，不要认行号。", size=11.5, fill=INK)
    c.text(60, 728, "同一份输出里快照值与累计值混着：ACTIVE 22 sec 是此刻，"
                    "Number of rows read 是自启动累计。", size=11.5, fill=SUB)
    return c.save(os.path.join(OUT, "ch39-fig1.svg"))


# ---------------------------------------------------------------- 图 39-2
def fig2():
    c = Canvas(960, 580, title="图 39-2　queries inside InnoDB 与 queries in queue 的四种组合",
               subtitle="两个数是入口的读数；配上看得到的 CPU，才分得清「在算」和「在等名额」")

    cards = [
        ("inside 12, queue 0", "CPU 31%", "正常：有活干，不排队",
         "InnoDB 内部在执行，入口没有积压。",
         "继续看 SQL 与慢日志", GREEN),
        ("inside 64, queue 87", "CPU 28%", "入口排队：名额不够",
         "并发超过 innodb_thread_concurrency 的允许值。",
         "先查这个参数，别加 CPU", RED),
        ("inside 0, queue 0", "CPU 12%", "不在 InnoDB 内部",
         "线程在 Server 层、网络，或者在等行锁。",
         "转 PROCESSLIST 与 data_lock_waits", SLATE),
        ("inside 40, queue 0", "CPU 88%", "真在算：瓶颈在 SQL",
         "没有排队，线程确实在消耗 CPU 干活。",
         "看执行计划与扫描行数", ORANGE),
    ]

    for i, (combo, cpu, verdict, desc, nxt, col) in enumerate(cards):
        x = 60 + (i % 2) * 440
        yy = 110 + (i // 2) * 195
        c.rect(x, yy, 400, 155, fill=TINT[col], stroke=BORDER[col], sw=1.6, r=10)
        c.text(x + 18, yy + 30, combo, size=11.5, fill=col, weight=600, mono=True)
        c.text(x + 382, yy + 30, cpu, size=10, fill=SUB, anchor="end")
        c.text(x + 18, yy + 62, verdict, size=14, fill=INK, weight=600)
        c.text(x + 18, yy + 90, desc, size=10.5, fill=SUB)
        c.text(x + 18, yy + 128, "→ " + nxt, size=10.5, fill=col, weight=500)

    c.text(60, 520, "queue > 0 是入口问题（限流或内部 latch），inside > 0 且 CPU 高是计算问题，"
                    "两个 0 而业务在等是别处的问题。", size=11.5, fill=INK)
    c.text(60, 544, "只看一处数字就会误判：同样 queue 为 0，CPU 88% 和 CPU 12% 是两个完全不同的结论。",
           size=11.5, fill=SUB)
    return c.save(os.path.join(OUT, "ch39-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
