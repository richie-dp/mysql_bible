#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 24 章配图：半同步与无损复制"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


def band(c, x, y, w, h, label, color, size=10):
    """虚线带：标出崩溃窗口的落点（不进 _nodes，不参与重叠判定）"""
    c.rect(x, y, w, h, fill=TINT[color], stroke=BORDER[color], sw=1.4, r=6, dash="5,3")
    c.text(x + w / 2, y + h / 2 + size * 0.35, label, size=size,
           fill=color, anchor="middle", weight=600)


# ---------------------------------------------------------------- 图 24-1
def fig1():
    c = Canvas(960, 690,
               title="图 24-1　等待点差一步：AFTER_COMMIT 与 AFTER_SYNC",
               subtitle="两条时序都从 binlog fsync 开始；区别只有一个：ACK 等待插在引擎 COMMIT 之前还是之后")

    LX, RX, W = 70, 510, 380

    c.box(LX, 100, W, 44, "AFTER_COMMIT", "5.5 / 5.6 的唯一行为，8.0 仍可切回",
          accent=RED, size=13, sub_size=10)
    c.box(RX, 100, W, 44, "AFTER_SYNC", "5.7 起的 loss-less，8.0 默认",
          accent=GREEN, size=13, sub_size=10)

    left = [
        (160, "① binlog 写入 + fsync", "sync_binlog=1，组提交共享一次", PURPLE),
        (228, "② 引擎 COMMIT", "事务已对其他会话可见", RED),
    ]
    right = [
        (160, "① binlog 写入 + fsync", "同上，此时事务还是 prepare", PURPLE),
        (228, "② 等从库 ACK", "引擎层没提交，别人看不到", ORANGE),
    ]
    for y, t, s, col in left:
        c.box(LX, y, W, 44, t, s, accent=col, size=12, sub_size=10)
    for y, t, s, col in right:
        c.box(RX, y, W, 44, t, s, accent=col, size=12, sub_size=10)

    band(c, LX, 296, W, 34, "崩溃窗口：已提交、未应答", RED)
    band(c, RX, 296, W, 34, "崩溃窗口：已 fsync、未提交", GREEN)

    c.box(LX, 354, W, 44, "③ 等从库 ACK", "等的是 RTT + 从库 relay log",
          accent=ORANGE, size=12, sub_size=10)
    c.box(LX, 422, W, 44, "④ 返回客户端", "客户端拿到「成功」",
          accent=BLUE, size=12, sub_size=10)
    c.box(RX, 354, W, 44, "③ 引擎 COMMIT", "等到了才提交",
          accent=GREEN, size=12, sub_size=10)
    c.box(RX, 422, W, 44, "④ 返回客户端", "客户端拿到「成功」",
          accent=BLUE, size=12, sub_size=10)

    for x in (LX + W / 2, RX + W / 2):
        for y1, y2 in ((204, 228), (272, 296), (330, 354), (398, 422)):
            c.arrow((x, y1), (x, y2), color=SLATE)

    c.box(LX, 490, W, 86, "主库已提交，从库可能没有",
          "切换后这笔账消失；客户端重试还会重复", accent=RED, size=12, sub_size=10)
    c.box(RX, 490, W, 86, "主库未提交，binlog 已完整",
          "恢复时照样前滚：不丢，重试才会重复", accent=GREEN, size=12, sub_size=10)

    c.text(70, 610, "等待在前，崩溃最多产生重复；等待在后，崩溃可能产生缺口。",
           size=12, fill=INK)
    c.text(70, 632, "所以 AFTER_SYNC 叫 loss-less，不叫 exactly-once：不丢它管，重复要靠业务幂等。",
           size=11, fill=SUB)

    c.legend(70, 654, [(PURPLE, "binlog 落盘", None)])
    c.legend(250, 654, [(ORANGE, "等 ACK", None)])
    c.legend(400, 654, [(RED, "危险：已提交", None)])
    c.legend(580, 654, [(GREEN, "安全：未提交", None)])
    return c.save(os.path.join(OUT, "ch24-fig1.svg"))


# ---------------------------------------------------------------- 图 24-2
def fig2():
    c = Canvas(960, 620,
               title="图 24-2　超时降级：从 ON 掉到 OFF，只需要一次沉默",
               subtitle="降级不报错、不断连接，只在 error log 留一条 warning；监控上唯一的变化是一个状态变量")

    c.text(300, 112,
           "回到 ON 的前提：某个从库的 ACK 重新落回超时窗口内（网络恢复 / 复制重建 / 手工重置 enabled）",
           size=10, fill=SUB)

    c.box(70, 250, 210, 86, "ON 半同步生效", "每个提交都等 ACK",
          accent=GREEN, size=13, sub_size=10)
    c.box(400, 250, 200, 86, "等 ACK", "最多等 10 秒",
          accent=ORANGE, size=13, sub_size=10)
    c.box(730, 250, 190, 86, "OFF 已降级", "不再等待，异步复制",
          accent=RED, size=13, sub_size=10)

    c.arrow((280, 293), (400, 293), color=BLUE)
    c.arrow((600, 293), (730, 293), color=RED, label="超时")

    c.arrow([(825, 250), (825, 150), (175, 150), (175, 250)], color=GREEN,
            label="ACK 重新落回窗口内")

    c.arrow((825, 336), (825, 392), color=RED, label="期间所有提交")

    c.box(710, 392, 210, 96, "降级窗口", "主从不一致无上限",
          accent=RED, size=13, sub_size=10)
    c.text(710, 512, "窗口本身不丢数据，只把风险押给下一次故障", size=10, fill=SUB)

    c.text(70, 380, "唯一的状态信号", size=11, fill=SUB, weight=600)
    c.text(70, 400, "Rpl_semi_sync_source_status", size=11, mono=True, fill=INK)
    c.text(70, 420, "ON → OFF，就是降级的全部痕迹", size=10, fill=SUB)

    c.mono_box(70, 440, 470, 74, [
        "[Warning] Timeout waiting for reply of binlog",
        "(file: mysql-bin.000021, pos: ...), semi-sync up to ...",
        "-- 整条链路上只有这一行，没有第二次提醒",
    ], size=9, title="error log")

    c.legend(600, 540, [(GREEN, "半同步生效", None),
                        (RED, "已降级为异步", None),
                        (ORANGE, "等 ACK 的提交", None)])
    return c.save(os.path.join(OUT, "ch24-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
