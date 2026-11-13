#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 27 章配图：MGR 与 InnoDB Cluster"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 27-1
def fig1():
    c = Canvas(960, 700,
               title="图 27-1　认证的四步：提交发生在③之后，数据可见发生在④之后",
               subtitle="事务在①就已经执行完；③才发现冲突，只能靠 undo 撤掉——这是「乐观」的全部含义")

    SX, SW = 50, 520
    steps = [
        (96, "① 本地执行完，尚未提交",
         "redo 已 prepare、binlog 已写未 fsync；其他会话看不到", BLUE),
        (214, "② 广播写集（write set）",
         "表 + 主键值 + 行级哈希；经组通信送到全组", PURPLE),
        (332, "③ 多数派认证（按行并行）",
         "各成员用认证数据库比对「已认证、未应用」的行哈希", GREEN),
        (450, "④ 提交，并广播 apply",
         "发起节点 COMMIT；其他成员收到 apply 才真正改数据", BLUE),
    ]
    for y, t, s, col in steps:
        c.box(SX, y, SW, 76, t, s, accent=col, size=13, sub_size=10)

    for y1, y2 in ((172, 214), (290, 332), (408, 450)):
        c.arrow((SX + SW / 2, y1), (SX + SW / 2, y2), color=SLATE)

    notes = [
        (96, "多数派 = n/2 + 1", "3 节点要 2 票，5 节点要 3 票", PURPLE, False),
        (214, "认证可以并行", "哈希以主键为粒度，不同行互不冲突", SLATE, True),
        (332, "冲突回滚发生在这里", "事务早已执行完，客户端收到 ERROR 3101", RED, True),
        (450, "认证通过 ≠ 已应用", "④ 之后才开始应用；之前 B、C 读到的是旧值", ORANGE, True),
    ]
    for y, t, s, col, link in notes:
        c.box(620, y, 290, 76, t, s, accent=col, size=12, sub_size=10)
        if link:
            c.arrow((SX + SW, y + 38), (620, y + 38), color=col, dash="4,3")

    c.text(50, 566, "认证数据库要保留「已认证、未应用」的写集，直到本节点应用完才能清理。",
           size=12, fill=INK)
    c.text(50, 590, "所以慢成员的认证库会持续膨胀，永远追不上——这就是流控（27.1.5）存在的理由。",
           size=12, fill=SUB)
    c.text(50, 618, "没有主键的表拿不到行标识，写集只能退化为整表范围：两个并发写必然判冲突。",
           size=11, fill=SUB)

    c.legend(50, 652, [(BLUE, "提交路径", None)])
    c.legend(230, 652, [(PURPLE, "组通信", None)])
    c.legend(390, 652, [(GREEN, "认证通过", None)])
    c.legend(560, 652, [(RED, "冲突回滚", None)])
    c.legend(730, 652, [(ORANGE, "等待 / 未应用", None)])
    return c.save(os.path.join(OUT, "ch27-fig1.svg"))


# ---------------------------------------------------------------- 图 27-2
def fig2():
    c = Canvas(960, 560,
               title="图 27-2　一致性五个级别：每个级别在等什么，代价落在读还是写",
               subtitle="越往右保证越强，等待越长；EVENTUAL 之外的四级买的都是「可见性」，不是「提交安全」")

    levels = [
        (45, 130, "EVENTUAL", "默认，不等待", SLATE,
         "不等待", "代价：0", "报表 / 列表页"),
        (215, 190, "BEFORE_ON_PRIMARY_FAILOVER", "切主后先追平", ORANGE,
         "切主后先应用积压", "只在切主后花钱", "所有集群都该开"),
        (445, 130, "BEFORE", "读前等应用", GREEN,
         "等本节点应用完", "代价：读延迟增加", "详情页读己之写"),
        (615, 130, "AFTER", "写后等应用", BLUE,
         "等成员应用完", "代价：写延迟增加", "支付 / 库存扣减"),
        (785, 130, "BEFORE_AND_AFTER", "读写都等", PURPLE,
         "两边都等", "代价：最慢", "账务核对"),
    ]

    for x, w, name, sub, col, wait, cost, scene in levels:
        c.box(x, 130, w, 96, name, sub, accent=col, size=11, sub_size=10, mono=False)
        cx = x + w / 2
        c.arrow((cx, 226), (cx, 288), color=SLATE, dash="3,3")
        c.box(x, 350, w, 78, wait, cost, accent=col, size=11, sub_size=10)
        c.text(cx, 456, scene, size=10, fill=SUB, anchor="middle")

    c.arrow((40, 292), (920, 292), color=SLATE)
    c.text(40, 318, "弱：不等待，可能读到旧值", size=10, fill=SUB)
    c.text(920, 318, "强：读写都等，延迟最高", size=10, fill=SUB, anchor="end")
    c.text(480, 318, "group_replication_consistency", size=10, fill=SLATE,
           anchor="middle", mono=True)

    c.text(45, 500, "同步点只由处在非 EVENTUAL 级别的成员应答：把一台只读成员长期留在 EVENTUAL，它就不在这次等待里。",
           size=11, fill=INK)
    c.text(45, 522, "级别不改变「提交要过多数派认证」，只改变「读/写什么时候返回」。",
           size=11, fill=SUB)

    c.legend(45, 542, [(SLATE, "无等待", None)])
    c.legend(200, 542, [(GREEN, "读同步", None)])
    c.legend(360, 542, [(BLUE, "写同步", None)])
    c.legend(520, 542, [(PURPLE, "读 + 写", None)])
    return c.save(os.path.join(OUT, "ch27-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
