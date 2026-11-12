#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 23 章配图：GTID 与复制运维"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 23-1
def fig1():
    c = Canvas(960, 680,
               title="图 23-1　gtid_executed / gtid_purged / gtid_owned 的包含关系",
               subtitle="purged 恒为 executed 的子集；从库要的 GTID 落在 purged 区间，就是 1236")

    # 左：executed 与其中的 purged
    c.container(50, 84, 520, 348, "gtid_executed　「我有什么」")
    c.rect(70, 122, 480, 126, fill=TINT[PURPLE], stroke=BORDER[PURPLE], sw=1.5, r=8)
    c.text(86, 148, "gtid_purged　「我丢了什么」", size=13, fill=PURPLE, weight=600)
    c.text(86, 176, "3e11c4a2-…:1 – 3e11c4a2-…:88420", size=12, mono=True)
    c.text(86, 200, "这 88420 个事务的 binlog 已经被删掉", size=11, fill=SUB)
    c.text(86, 224, "集合里还留着名字，内容已经发不出来", size=11, fill=RED)

    c.box(70, 262, 480, 62, "3e11c4a2-…:88421 – :90233",
          "binlog 还在：差集能按事务发给从库", accent=GREEN)

    c.text(70, 352, "purged ⊂ executed，单调增长，不会变小", size=11, fill=INK)
    c.text(70, 376, "PURGE BINARY LOGS、binlog 过期、导入 dump 都会推高它", size=11, fill=SUB)
    c.text(70, 404, "从库要的 GTID 落在上面那一段 → 主库拿不出内容 → 1236", size=11, fill=RED)

    # 右：从库的请求与 1236
    c.box(620, 122, 290, 78, "从库的请求", "缺 :88405 起的 812 个事务", accent=PURPLE, size=13)
    c.arrow(620, 161, 554, 161, color=RED)
    c.text(587, 148, "缺这段", size=10, fill=RED, anchor="middle")

    c.mono_box(620, 250, 290, 132, [
        "ERROR 1236 (HY000):",
        "Got fatal error 1236 from",
        "master when reading data",
        "from binary log:",
        "'... has purged binary logs",
        "containing GTIDs that the",
        "slave requires.'",
    ], size=10)
    c.arrow(765, 200, 765, 250, color=RED)

    # 下：owned
    c.container(50, 470, 860, 108, "gtid_owned　「我正在做什么」——一个还没结算的临时状态")
    c.box(70, 502, 360, 60, "gtid_owned：正在执行的 GTID",
          "提交则并入 executed，回滚则永不并入", accent=BLUE, size=12, sub_size=10)
    c.text(452, 518, "读法：SHOW STATUS LIKE 'gtid_owned'", size=11, fill=INK)
    c.text(452, 540, "SHOW PROCESSLIST 里没有这一列；并行复制下每个 worker 各持一个", size=11, fill=SUB)

    c.legend(52, 610, [(PURPLE, "GTID 集合", None),
                       (GREEN, "binlog 仍在，可发", None)])
    c.legend(300, 610, [(RED, "越界 / 1236", None),
                        (BLUE, "执行中，未结算", None)])
    return c.save(os.path.join(OUT, "ch23-fig1.svg"))


# ---------------------------------------------------------------- 图 23-2
def fig2():
    c = Canvas(960, 660,
               title="图 23-2　用 SET GTID_NEXT 跳过一条事务：五步，缺一步就无限重试",
               subtitle="空事务不是占位，是把 GTID 的所有权结算掉；gtid_executed 里没有它，applier 就重放同一件事")

    c.box(60, 88, 500, 76, "applier 停在 1062",
          "Worker 1 failed executing transaction '3e11c4a2-…:88421'",
          accent=RED, size=13, sub_size=10)

    steps = [
        (190, "① STOP REPLICA;", "8.0.23 之前写作 STOP SLAVE", BLUE),
        (270, "② SET GTID_NEXT='3e11c4a2-…:88421';", "声明下一条要执行的事务身份", ORANGE),
        (350, "③ BEGIN; COMMIT;", "空事务：让这个 GTID 落进 gtid_executed", ORANGE),
        (430, "④ SET GTID_NEXT='AUTOMATIC';", "交回自动分配，否则后面的写入都顶着它", ORANGE),
        (510, "⑤ START REPLICA;", "重读同一个事件，集合里已有 → 整条跳过", GREEN),
    ]
    for y, title, sub, col in steps:
        c.box(60, y, 500, 54, title, sub, accent=col, size=13, sub_size=10, mono=True)

    # 红色回环：不消费 GTID，就一直在"报错—重启—再报错"里转
    c.arrow([(560, 537), (600, 537), (600, 126), (560, 126)], color=RED, dash="6,4")
    c.text(600, 114, "无限重试", size=10, fill=RED, anchor="middle")

    # 右：原因与禁区
    c.container(640, 88, 280, 210, "为什么必须是空事务")
    for i, ln in enumerate([
        "gtid_executed 认的是提交：",
        "只在事务里 SET 一下不算数，",
        "空事务提交之后集合里才有它。",
        "applier 再读到同一个 GTID 事件，",
        "发现已经有 → 整条跳过。",
    ]):
        c.text(656, 140 + i * 26, ln, size=10, fill=INK)
    c.text(656, 270, "不写空事务 → 每次都重放同一条", size=10, fill=RED)

    c.container(640, 332, 280, 214, "三条禁区")
    for i, ln in enumerate([
        "事务中执行：与隐式提交冲突",
        "本会话已持有 GTID：直接报错",
        "gtid_mode=OFF：拒绝设具体 GTID",
        "第四个坑在流程外：忘了改回",
        "AUTOMATIC，后续事务全用同",
        "一个 GTID，从库只能应用第一条",
    ]):
        c.text(656, 384 + i * 26, ln, size=10, fill=INK)

    c.text(60, 600, "空事务也会写进从库自己的 binlog：这台从库将来被提升，这次跳过会跟着传播下去。",
           size=11, fill=INK)
    c.text(60, 624, "跳过只让复制继续，不修数据。跳过之前先确认这条事务在从库上确实不该执行。",
           size=11, fill=SUB)
    return c.save(os.path.join(OUT, "ch23-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
