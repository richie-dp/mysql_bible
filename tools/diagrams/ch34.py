#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 34 章配图：分布式事务与最终一致性"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 34-1
def fig1():
    c = Canvas(960, 640,
               title="图 34-1　XA 的持锁时间轴 vs 本地事务",
               subtitle="本地事务的持锁区间由语句决定；XA 的持锁区间由最慢的那个资源管理器决定")

    # ---- A：本地事务
    c.text(60, 96, "A　本地事务：锁从第一条写语句持有到 COMMIT", size=12,
           fill=SUB, weight=600)
    c.box(60, 110, 110, 46, "BEGIN", accent=SLATE, size=12, mono=True)
    c.box(190, 110, 160, 46, "UPDATE stock", accent=BLUE, size=12, mono=True)
    c.box(370, 110, 120, 46, "COMMIT", accent=GREEN, size=12, mono=True)
    c.arrow((170, 133), (190, 133), color=SLATE)
    c.arrow((350, 133), (370, 133), color=BLUE)

    c.rect(190, 166, 300, 12, fill=TINT[RED], stroke=RED, sw=1.2, r=3)
    c.text(340, 200, "持锁区间 = 语句到 COMMIT，毫秒级", size=11,
           fill=RED, anchor="middle")

    # ---- B：XA
    c.text(60, 240, "B　XA：PREPARE 之后行锁一直不放，协调者慢一步就放大 N 倍",
           size=12, fill=SUB, weight=600)
    c.box(60, 254, 110, 46, "XA START", accent=SLATE, size=12, mono=True)
    c.box(190, 254, 150, 46, "UPDATE stock", accent=BLUE, size=12, mono=True)
    c.box(360, 254, 100, 46, "XA END", accent=SLATE, size=12, mono=True)
    c.box(480, 254, 130, 46, "XA PREPARE", accent=ORANGE, size=12, mono=True)
    c.box(760, 254, 130, 46, "XA COMMIT", accent=GREEN, size=12, mono=True)
    c.arrow((170, 277), (190, 277), color=SLATE)
    c.arrow((340, 277), (360, 277), color=BLUE)
    c.arrow((460, 277), (480, 277), color=SLATE)
    c.arrow((610, 277), (760, 277), color=RED, dash="6,4", label="等协调者")

    c.rect(190, 310, 290, 12, fill=TINT[RED], stroke=RED, sw=1.2, r=3)
    c.rect(480, 310, 280, 12, fill=TINT[ORANGE], stroke=ORANGE, sw=1.2, r=3,
           dash="5,3")
    c.text(470, 344, "锁的持有区间 = 语句到 XA COMMIT，中间是 N 次网络往返",
           size=11, fill=RED, anchor="middle")

    # ---- 串联电路
    c.container(60, 378, 840, 140, "串联电路：三个库的延迟相加，不是取最大")
    c.text(80, 430, "库存库的 XA PREPARE 每慢一个 RTT，订单库 order_main 的行锁就多持有同样长的时间。",
           size=12, fill=INK)
    c.text(80, 456, "本地事务下三个库各自提交、延迟取最大；XA 下三个库都要等同一个协调者，延迟求和、可用性相乘。",
           size=12, fill=INK)
    c.text(80, 482, "放大倍数取决于网络 RTT 与协调者调度，没有固定值——这才是它被弃用的机制原因。",
           size=12, fill=SUB)

    c.text(60, 548, "同样是「两个阶段」，一个是引擎与 binlog 的对齐，一个是多个实例之间的协调。",
           size=12, fill=SUB)

    c.legend(60, 574, [(RED, "行锁被持有", None), (ORANGE, "PREPARED 段：锁不放", "5,3")])
    c.legend(320, 574, [(BLUE, "业务写", None), (SLATE, "协议语句", None)])
    return c.save(os.path.join(OUT, "ch34-fig1.svg"))


# ---------------------------------------------------------------- 图 34-2
def fig2():
    c = Canvas(960, 640,
               title="图 34-2　本地消息表的状态机",
               subtitle="业务写与消息写同一个本地事务；投递可失败可重复，状态迁移靠 affected_rows 判首次")

    c.text(60, 100, "正常链路", size=12, fill=SUB, weight=600)
    c.text(60, 316, "异常分支", size=12, fill=SUB, weight=600)

    c.box(110, 120, 170, 74, "pending", "本地事务已提交", accent=BLUE,
          size=14, sub_size=11, mono=True)
    c.box(360, 120, 170, 74, "sent", "已投进 MQ", accent=PURPLE,
          size=14, sub_size=11, mono=True)
    c.box(620, 120, 170, 74, "done", "下游已回写", accent=GREEN,
          size=14, sub_size=11, mono=True)

    c.arrow((280, 157), (360, 157), color=BLUE, label="扫描投递")
    c.arrow((530, 157), (620, 157), color=GREEN, label="ack 回写")

    # 重试回环
    c.arrow([(145, 194), (145, 250), (265, 250), (265, 194)], color=ORANGE,
            dash="6,4", label="投递失败 → 退避重试", label_dy=-8)

    # 超限转人工
    c.box(110, 330, 200, 74, "failed", "超次数 → 人工队列", accent=RED,
          size=14, sub_size=11, mono=True)
    c.arrow([(280, 180), (330, 180), (330, 367), (310, 367)], color=RED,
            label="retry_count 超限")

    # 卡在 sent：只能靠对账
    c.box(400, 330, 250, 74, "T+1 对账兜底", "总额 / 笔数 / 逐笔", accent=ORANGE,
          size=14, sub_size=11)
    c.arrow((445, 194), (445, 330), color=ORANGE, dash="6,4", label="卡在 sent")

    c.container(60, 430, 840, 118, "这张表看不出来的两件事")
    c.text(80, 472, "① sent 只代表「投递成功」，不代表下游写成功：消费者失败、消息丢失，状态都停在 sent。",
           size=12, fill=INK)
    c.text(80, 496, "② 状态迁移一律写成 UPDATE ... WHERE msg_id = ? AND status = ?，用 affected_rows 判首次，重复投递天然幂等。",
           size=12, fill=INK)
    c.text(80, 520, "没有对账，「最终一致」没有终点，只剩一份「我以为发出去了」的日志。",
           size=12, fill=SUB)

    c.legend(60, 574, [(BLUE, "待投递", None), (PURPLE, "已投递", None)])
    c.legend(300, 574, [(GREEN, "已完成", None), (RED, "终止态", None)])
    c.legend(540, 574, [(ORANGE, "重试 / 兜底", "6,4"), (SLATE, "虚线 = 异常路径", "6,4")])
    return c.save(os.path.join(OUT, "ch34-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
