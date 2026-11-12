#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 22 章配图：复制原理与事件流"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 22-1
def fig1():
    c = Canvas(960, 660,
               title="图 22-1　一条事务从主库 binlog 到从库数据页的落盘路径",
               subtitle="默认配置下 ①③④ 串在关键路径上，② 被 sync_relay_log 摊薄——延迟下限由此而来")

    # 主库
    c.container(50, 86, 860, 140, "主库 source")
    c.box(70, 118, 240, 60, "binlog cache", "内存 · 事务执行中攒批", accent=SLATE)
    c.box(350, 118, 240, 60, "binlog 文件", "① fsync · sync_binlog=1", accent=PURPLE)
    c.box(630, 118, 240, 60, "dump thread", "按从库要的坐标读文件", accent=BLUE)
    c.arrow(310, 148, 350, 148, color=BLUE)
    c.arrow(590, 148, 630, 148, color=BLUE)

    c.badge(362, 96, "① 落盘", accent=GREEN)

    # 网络
    c.text(52, 262, "网络（TCP）：从库要什么，主库就从哪读，单向推送", size=11, fill=SUB)
    c.arrow([(820, 178), (820, 250), (820, 330)], color=SLATE, dash="5,4",
            label="事件流", label_at=0.55, label_side="left")

    # 从库
    c.container(50, 290, 860, 150, "从库 replica")
    c.box(730, 330, 180, 60, "relay log", "② sync_relay_log=10000", accent=PURPLE,
          size=13, sub_size=10)
    c.box(510, 330, 180, 60, "applier 线程", "③ 写从库 binlog", accent=ORANGE,
          size=13, sub_size=10)
    c.box(290, 330, 180, 60, "redo log", "④ ftc=1 · 每事务", accent=GREEN,
          size=13, sub_size=10)
    c.box(70, 330, 180, 60, "数据页", "脏页异步刷盘", accent=BLUE,
          size=13, sub_size=10)
    c.arrow(730, 360, 690, 360, color=BLUE)
    c.arrow(510, 360, 470, 360, color=BLUE)
    c.arrow(290, 360, 250, 360, color=BLUE)

    c.badge(742, 308, "② 落盘", accent=SLATE)
    c.badge(522, 308, "③ 落盘", accent=GREEN)
    c.badge(302, 308, "④ 落盘", accent=GREEN)

    c.text(52, 466, "①③④ 在关键路径上：客户端、从库的提交都要等它们返回；② 不在——receiver 写完就继续收下一个事件。",
           size=11, fill=INK)
    c.text(52, 488, "relay log 是可丢弃的中间态（崩溃后整段扔掉重拉），所以不必为它付每事务一次的持久化代价。",
           size=11, fill=SUB)

    # 结论条
    c.container(50, 510, 860, 96, "同一条事务在整条链路上的 fsync 次数")
    c.box(70, 546, 250, 48, "默认：3 次", "①③④，②被摊薄", accent=GREEN,
          size=12, sub_size=10)
    c.box(360, 546, 250, 48, "关 log_replica_updates：2 次", "从库不能再当源", accent=ORANGE,
          size=12, sub_size=10)
    c.box(650, 546, 250, 48, "sync_relay_log=1：4 次", "多一次 fdatasync", accent=SLATE,
          size=12, sub_size=10)

    c.legend(52, 626, [(GREEN, "fsync 落盘，在关键路径上", None),
                       (SLATE, "落盘但不在关键路径上", "5,4")])
    return c.save(os.path.join(OUT, "ch22-fig1.svg"))


# ---------------------------------------------------------------- 图 22-2
def fig2():
    c = Canvas(960, 640,
               title="图 22-2　同一个事务：位点是字节偏移，GTID 是事务身份",
               subtitle="主库一换，位点指向别的字节且不报错；GTID 还是那一个，缺什么由集合差决定")

    # 左：位点
    c.container(50, 86, 420, 470, "坐标 A：位点 = 字节偏移")
    chips = [
        (130, "T1　@ 4", SLATE),
        (184, "T2　@ 890", SLATE),
        (238, "T3　@ 1234", GREEN),
        (292, "T4　@ 1560", SLATE),
        (346, "T5　@ 2024", SLATE),
    ]
    for y, label, col in chips:
        c.box(75, y, 370, 40, label, accent=col, size=12, mono=True)

    c.text(52, 412, "pos 只在单个文件内自洽", size=11, fill=SUB)
    c.box(75, 428, 370, 72, "主库切换后：1234 指向别的字节",
          "位点失效，而且不报错", accent=RED, size=12, sub_size=10)

    # 右：GTID
    c.container(490, 86, 420, 470, "坐标 B：GTID = 事务身份")
    chips = [
        (130, "3e11c4a2:1", SLATE),
        (184, "3e11c4a2:2", SLATE),
        (238, "3e11c4a2:3", GREEN),
        (292, "3e11c4a2:4", SLATE),
        (346, "3e11c4a2:5", SLATE),
    ]
    for y, label, col in chips:
        c.box(515, y, 370, 40, label, accent=col, size=12, mono=True)

    c.text(492, 412, "格式：server_uuid:transaction_id", size=11, fill=SUB)
    c.box(515, 428, 370, 72, "主库切换后：集合里有的跳过",
          "缺哪些事务与文件位置无关", accent=GREEN, size=12, sub_size=10)

    c.text(75, 528, "同一个 1234 在另一个文件里是另一个位置", size=10, fill=SUB)
    c.text(515, 528, "差集 = 主库有、从库没有的那些事务", size=10, fill=SUB)

    c.text(52, 588, "位点回答\"从哪接着读\"，GTID 回答\"还缺哪些\"。前者一旦数错就静默跳过一段，后者天然幂等。",
           size=12, fill=INK)
    return c.save(os.path.join(OUT, "ch22-fig2.svg"))


# ---------------------------------------------------------------- 图 22-3
def fig3():
    c = Canvas(960, 540,
               title="图 22-3　relay_log_recovery：丢掉未执行的 relay log，重新拉一遍",
               subtitle="8.0 默认 ON；代价是把\"已收到未应用\"的那段网络传输再付一次")

    c.text(60, 104, "① 崩溃前", size=12, fill=SUB, weight=600)
    c.text(360, 104, "② 崩溃 → 重启", size=12, fill=SUB, weight=600)
    c.text(660, 104, "③ 重新拉取", size=12, fill=SUB, weight=600)

    relay = [
        (130, "T1　已应用", GREEN),
        (176, "T2　已应用", GREEN),
        (222, "T3　已应用", GREEN),
        (268, "T4　已收到", ORANGE),
        (314, "T5　已收到", ORANGE),
    ]
    for y, label, col in relay:
        c.box(60, y, 260, 38, label, accent=col, size=12)
    c.text(60, 372, "应用位点停在 T3", size=11, fill=SUB)

    c.box(360, 150, 260, 70, "从库崩溃", "未提交事务被 InnoDB 回滚",
          accent=RED, size=13, sub_size=10)
    c.arrow(490, 220, 490, 250, color=RED)
    c.box(360, 250, 260, 90, "丢弃 T4、T5", "relay_log_recovery=ON（默认）",
          accent=RED, size=13, sub_size=10)

    c.box(660, 150, 260, 70, "receiver 重连", "把 gtid_executed 发给主库",
          accent=ORANGE, size=13, sub_size=10)
    c.arrow(790, 220, 790, 250, color=ORANGE)
    c.box(660, 250, 260, 90, "只发 T4、T5", "集合里已有的直接跳过",
          accent=GREEN, size=13, sub_size=10)

    c.arrow(320, 287, 358, 287, color=SLATE, dash="5,4", label="重传", label_dy=-8)
    c.arrow(620, 295, 658, 295, color=SLATE, dash="5,4", label="差集", label_dy=-8)

    c.container(60, 396, 860, 120, "两条前提")
    c.text(76, 446, "崩在 T4 应用到一半：InnoDB 回滚这条未提交事务，位点表与数据在同一事务里提交（8.0 默认 TABLE），T4 整条重放，不会半条。",
           size=11, fill=INK)
    c.text(76, 470, "sync_relay_log=10000 意味着 relay log 尾部本来就可能没落盘，所以\"整段丢弃\"比\"原地续放\"更可靠。",
           size=11, fill=SUB)
    c.text(76, 494, "代价是延迟放大：放大的量等于崩溃那一刻积压的传输量，追平后才回到常态。",
           size=11, fill=SUB)
    return c.save(os.path.join(OUT, "ch22-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
