#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 6 章配图：Binlog 与两阶段提交"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 6-1
def fig1():
    c = Canvas(960, 680,
               title="图 6-1　一个事务在 binlog 里的完整事件序列",
               subtitle="binlog 是追加写的事件流：XID 之前的一切都只是「可能提交」")

    rows = [
        (104, "FORMAT_DESCRIPTION", SLATE,
         "type 15 · 文件头：binlog 版本、事件头长度"),
        (154, "PREVIOUS_GTIDS", SLATE,
         "type 35 · 本文件之前已执行的 GTID 集合"),
        (216, "GTID_LOG_EVENT", PURPLE,
         "type 33 · GTID + last_committed / sequence_number"),
        (266, "QUERY (BEGIN)", BLUE,
         "type 2 · 开事务；DDL 也走 QUERY，但没有 XID"),
        (316, "TABLE_MAP", BLUE,
         "type 19 · table_id → 库.表；row event 只带 table_id"),
        (366, "UPDATE_ROWS", PURPLE,
         "type 31 · 前镜像 + 后镜像，细节看 binlog_row_image"),
        (446, "XID", GREEN,
         "type 16 · InnoDB 事务号；见到它才算「事件组完整」"),
        (516, "ROTATE", SLATE,
         "type 4 · 切文件；只发生在事务之间，不会切开事务"),
    ]

    c.text(80, 96, "① 文件头（每个文件只在开头出现一次）", size=11,
           fill=SUB, weight=600)
    c.text(80, 208, "② 一个事务的事件组（binlog_format = ROW）", size=11,
           fill=SUB, weight=600)
    c.text(80, 502, "③ 事务边界之外", size=11, fill=SUB, weight=600)

    for y, name, col, note in rows:
        c.box(80, y, 320, 40, name, accent=col, size=12, mono=True)
        c.text(470, y + 25, note, size=11, fill=SUB)

    # 事务可见性分界线
    c.arrow((64, 424), (900, 424), color=RED, dash="6,4", end=False)
    c.text(470, 440, "分界线：XID 之前的事件，崩溃恢复时可能被回滚",
           size=11, fill=RED, weight=600)

    c.text(60, 578, "binlog 只能往前读：事件一旦写入就不会再改（被 PURGE 掉是另一回事）。",
           size=11, fill=SUB)
    c.text(60, 598, "row event 里没有库名表名，只有一个 table_id——这也是 CDC 必须缓存 TABLE_MAP 的原因。",
           size=11, fill=SUB)

    c.legend(60, 624, [(PURPLE, "行镜像 / 事务标识", None), (BLUE, "语句与元数据", None)])
    c.legend(330, 624, [(GREEN, "提交点", None), (SLATE, "文件层事件", None)])
    return c.save(os.path.join(OUT, "ch06-fig1.svg"))


# ---------------------------------------------------------------- 图 6-2
def fig2():
    c = Canvas(960, 620,
               title="图 6-2　组提交的三阶段：N 个事务，一次 fsync",
               subtitle="三个阶段各有一条队列，队首线程当 leader，替全组干活；流水线可以重叠推进")

    stages = [
        (60, "① flush 阶段", "write() 进文件即可返回", ["Txn #1", "Txn #2", "Txn #3", "Txn #4"]),
        (365, "② sync 阶段", "一次 fsync，全组共享", ["Txn #1", "Txn #2", "Txn #3", "Txn #4"]),
        (670, "③ commit 阶段", "引擎提交、释放行锁", ["Txn #1", "Txn #2", "Txn #3", "Txn #4"]),
    ]

    for x, head, _, txns in stages:
        c.container(x, 110, 230, 244, head)
        for i, t in enumerate(txns):
            y = 150 + i * 44
            if i == 0:
                c.box(x + 25, y, 180, 36, t, "队首：本阶段 leader", accent=BLUE, size=12, sub_size=10)
            else:
                c.box(x + 25, y, 180, 36, t, "同组：等 leader 完成", accent=SLATE, size=12, sub_size=10)

    c.arrow((290, 168), (365, 168), color=BLUE)
    c.arrow((595, 168), (670, 168), color=BLUE)

    c.text(175, 378, "write() 进 page cache", size=11, fill=SUB, anchor="middle")
    c.text(480, 378, "fsync 落盘，全组只付一次", size=11, fill=SUB, anchor="middle")
    c.text(785, 378, "释放行锁，返回客户端", size=11, fill=SUB, anchor="middle")

    c.text(60, 398, "队首线程成为该阶段的 leader；三个阶段各自独立选 leader，不一定是同一个事务。",
           size=11, fill=SUB)

    c.container(60, 418, 840, 142, "同一个组，两个方向的效果")
    c.box(80, 452, 380, 60,
          "收益：fsync 次数 ÷ 组大小",
          "10 个事务从 10 次 fsync 变成 1 次", accent=GREEN, size=13, sub_size=10)
    c.box(500, 452, 380, 60,
          "代价：最后一个事务多等 ≤ sync_delay",
          "行锁也同步多持有这么久", accent=RED, size=13, sub_size=10)
    c.text(80, 532, "sync_delay = 0 时，组大小由并发自然决定；并发低时组里只有 1 个事务，等于没攒批。",
           size=11, fill=SUB)

    c.legend(60, 572, [(BLUE, "本阶段 leader", None), (SLATE, "同组 follower", None)])
    return c.save(os.path.join(OUT, "ch06-fig2.svg"))


# ---------------------------------------------------------------- 图 6-3
def fig3():
    c = Canvas(960, 600,
               title="图 6-3　sync_binlog × innodb_flush_log_at_trx_commit",
               subtitle="列 = innodb_flush_log_at_trx_commit（ftc），行 = sync_binlog；格内是三种崩溃下会丢什么")

    cols = [
        (220, "ftc = 0", "1 秒一次刷盘"),
        (460, "ftc = 1", "每次提交 fsync"),
        (700, "ftc = 2", "每次提交只 write"),
    ]
    for x, t, s in cols:
        c.box(x, 96, 200, 44, t, s, accent=SLATE, size=13, sub_size=10)

    rows = [
        (160, "sync = 0", "不主动 fsync", [
            (RED, "进程崩就丢", "redo 丢 1s，binlog 却还在"),
            (ORANGE, "只扛进程崩", "OS 崩或掉电丢 1s 的 binlog"),
            (ORANGE, "只扛进程崩", "OS 崩时两边各丢一段"),
        ]),
        (250, "sync = 1", "默认值（8.0）", [
            (RED, "进程崩就丢", "binlog 已落盘，redo 却没落"),
            (GREEN, "三种崩溃都可扛", "双 1：两边的存亡边界对齐"),
            (ORANGE, "只扛进程崩", "掉电后从库比主库多"),
        ]),
        (340, "sync = N", "每 N 组 fsync", [
            (RED, "进程崩就丢", "redo 丢 1s，binlog 丢 N-1 组"),
            (ORANGE, "只扛进程崩", "掉电丢 ≤ N-1 组 binlog"),
            (ORANGE, "只扛进程崩", "两个窗口叠加，丢的不对齐"),
        ]),
    ]

    for y, t, s, cells in rows:
        c.box(60, y, 120, 76, t, s, accent=SLATE, size=12, sub_size=10)
        for i, (col, title, sub) in enumerate(cells):
            c.box(220 + i * 240, y, 200, 76, title, sub, accent=col, size=12, sub_size=10)

    c.text(60, 456, "双 1 的意义不是「少丢几行」，而是让 redo 与 binlog 在同一条时间线上存亡——",
           size=12, fill=INK)
    c.text(60, 478, "只有边界对齐，崩溃恢复才能用「binlog 是否完整」这一个判据决定事务去留。",
           size=12, fill=INK)

    c.legend(60, 508, [(GREEN, "进程崩 / OS 崩 / 掉电都不丢", None),
                       (ORANGE, "只扛进程崩，掉电丢一侧", None),
                       (RED, "进程崩就丢，且两边不对齐", None)])
    return c.save(os.path.join(OUT, "ch06-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
