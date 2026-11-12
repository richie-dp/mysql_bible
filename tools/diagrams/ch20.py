#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 20 章配图：wait-for graph / 交叉更新时序 / 锁等待雪崩"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *  # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 20-1
def fig1():
    c = Canvas(960, 560, title="图 20-1　wait-for graph 与环检测",
               subtitle="节点是事务，边是「我在等你的锁」；检测从刚进入等待的那个事务出发，走回自己就是环")

    c.container(40, 84, 880, 380,
                "wait-for graph：T1 → T2 → T3 → T1 构成环，T4 只是环外排队")

    # 环上的三个事务
    c.box(70, 130, 130, 50, "T1 订单扣减", "持有 A 的 X 锁", accent=RED, size=13)
    c.box(390, 130, 130, 50, "T2 库存回补", "持有 B 的 X 锁", accent=RED, size=13)
    c.box(710, 130, 130, 50, "T3 账单核销", "持有 C 的 X 锁", accent=RED, size=13)

    # 环上的边
    c.arrow(200, 155, 390, 155, color=RED, label="等 B")
    c.arrow(520, 155, 710, 155, color=RED, label="等 C")
    c.arrow([(775, 180), (775, 310), (135, 310), (135, 180)],
            color=RED, label="等 A：环闭合", label_at=0.62, label_dy=16)

    # 环外排队的事务
    c.box(390, 240, 130, 50, "T4 对账任务", "只想读 B", accent=SLATE, size=13)
    c.arrow(455, 240, 455, 180, color=SLATE, dash="5,4", label="也在等 B")

    c.text(70, 378, "T4 不在环上：它只是在排队，不会被选为牺牲者。",
           size=12, fill=SUB)
    c.text(70, 402, "环上的事务才是死锁的当事人。", size=12, fill=SUB)

    c.legend(745, 350, [(RED, "环上的等待", None), (SLATE, "环外排队", "5,4")])

    c.text(60, 512,
           "牺牲者怎么选：只在环上挑 → 比较已产生的 undo 记录数，选干活少的 → 整事务回滚，返回 1213",
           size=12, fill=INK)
    return c.save(os.path.join(OUT, "ch20-fig1.svg"))


# ---------------------------------------------------------------- 图 20-2
def fig2():
    c = Canvas(960, 600, title="图 20-2　交叉更新死锁：环形成的那一刻",
               subtitle="两个事务对 A、B 两行用了相反的加锁顺序，各自的等待在第四步闭合成环")

    lanes = [("事务 T1", "先锁 A（sku 1001）", 300, BLUE),
             ("事务 T2", "先锁 B（sku 2002）", 660, BLUE)]
    for name, sub, x, col in lanes:
        c.box(x - 110, 76, 220, 48, name, sub, accent=col, size=13, sub_size=10)

    # 生命线（先画，后画的方块盖住它）
    for _, _, x, _ in lanes:
        c.els.append(f'<line x1="{x}" y1="124" x2="{x}" y2="470" '
                     f'stroke="{LINE}" stroke-width="1.2" stroke-dasharray="5,5"/>')

    c.box(190, 148, 220, 36, "① 持有 A 的 X 锁", accent=GREEN, size=12)
    c.box(550, 200, 220, 36, "② 持有 B 的 X 锁", accent=GREEN, size=12)

    c.arrow(300, 280, 660, 280, color=SLATE,
            label="③ 请求 B：进入等待")
    c.arrow(660, 350, 300, 350, color=RED,
            label="④ 请求 A：环闭合")

    c.text(480, 320, "环形成", size=12, fill=RED, anchor="middle", weight=600)

    c.arrow(300, 380, 300, 414, color=ORANGE)
    c.arrow(660, 380, 660, 414, color=GREEN)
    c.box(190, 414, 220, 44, "⑤ T1 被回滚", "1213 → 整个事务重做",
          accent=ORANGE, size=12, sub_size=10)
    c.box(550, 414, 220, 44, "⑥ T2 拿到锁，继续", "提交成功",
          accent=GREEN, size=12, sub_size=10)

    c.mono_box(60, 486, 840, 76, [
        "HOLDS: lock_mode X locks rec but not gap        ← 双方各持一把",
        "WAITING FOR THIS LOCK TO BE GRANTED: ... waiting  ← heap no 互相指向",
        "WE ROLL BACK TRANSACTION (1)                     ← 括号是编号，不是顺序",
    ], title="LATEST DETECTED DEADLOCK 里能直接对照的三行", size=10)
    return c.save(os.path.join(OUT, "ch20-fig2.svg"))


# ---------------------------------------------------------------- 图 20-3
def fig3():
    c = Canvas(960, 720, title="图 20-3　锁等待的雪崩链：一条慢事务如何拖垮服务",
               subtitle="数据库只坏了一点点，应用层把「等待」放大成了「不可用」")

    c.container(120, 90, 720, 240, "MySQL 内部：这一侧几乎没有报警")
    c.container(120, 330, 720, 340, "应用与编排层")

    steps = [
        (120, "① 慢事务", "持锁 8 秒，事务里有 RPC", ORANGE, "唯一的异常在这里"),
        (230, "② 行锁等待堆积", "同一热点行排队", RED, "不在慢日志里"),
        (340, "③ 连接池耗尽", "等待期间连接不归还", RED, "池一满，全都慢"),
        (450, "④ 健康检查失败", "探针也要拿连接", PURPLE, "readiness 探针超时"),
        (560, "⑤ 服务不可用", "摘流，剩余实例更挤", SLATE, "故障开始扩散"),
    ]
    for y, title, sub, col, note in steps:
        c.box(320, y, 320, 64, title, sub, accent=col, size=13, sub_size=11)
        c.text(660, y + 36, note, size=11, fill=SUB)

    for y in (184, 294, 404, 514):
        c.arrow(480, y, 480, y + 46, color=RED, width=1.8)

    c.arrow([(320, 592), (210, 592), (210, 152), (320, 152)],
            color=RED, dash="5,4", width=1.8, label="重试风暴")

    c.text(140, 690,
           "反馈回路：越不可用 → 重试越多 → 热点行越挤 → 越不可用",
           size=12, fill=RED)
    return c.save(os.path.join(OUT, "ch20-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
