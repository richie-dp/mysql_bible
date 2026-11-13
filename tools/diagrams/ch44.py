#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 44 章配图：内核源码导读（目录 / 线程 / 调用链）"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 44-1
def fig1():
    c = Canvas(960, 720,
               title="图 44-1　一条 SQL 的两个世界：Server 层不知道 B+ 树，引擎不知道你要干嘛",
               subtitle="左边每一步都在 sql/，右边每一步都在 storage/innobase/；两列之间只隔着 handler 这一道门")

    c.container(40, 100, 400, 556, "Server 层　sql/")
    c.container(520, 100, 400, 556, "InnoDB　storage/innobase/")

    # 竖直分界线 + 接口标签
    c.arrow((480, 104), (480, 652), color=SLATE, dash="6,4", width=1.2, end=False)
    c.pill(410, 74, 140, 24, "handler 接口", accent=SLATE, size=11)

    L = [
        ("mysql_execute_command", "sql/sql_parse.cc", BLUE),
        ("JOIN::optimize", "sql/sql_optimizer.cc　选表 / 选索引 / 算代价", BLUE),
        ("JOIN::exec", "按执行计划驱动算子", BLUE),
        ("do_select", "sql/sql_executor.cc　逐行取、逐行判", BLUE),
        ("handler::ha_index_read_map", "sql/handler.cc　跨层调用点", SLATE),
    ]
    ys = [140, 236, 332, 428, 524]
    for (title, sub, col), y in zip(L, ys):
        c.box(60, y, 360, 64, title, sub, accent=col,
              size=11.5, sub_size=10, mono=True)

    R = [
        ("ha_innobase::index_read", "handler/ha_innodb.cc", PURPLE),
        ("row_search_mvcc", "row/row0sel.cc　判可见性、做回表", PURPLE),
        ("btr_cur_search_to_nth_level", "btr/btr0cur.cc　逐层下降", PURPLE),
        ("mtr_t::commit", "mtr/mtr0mtr.cc　写 redo、放页锁", GREEN),
    ]
    for (title, sub, col), y in zip(R, [236, 332, 428, 524]):
        c.box(540, y, 360, 64, title, sub, accent=col,
              size=11.5, sub_size=10, mono=True)

    # 列内向下
    for y in ys[:-1]:
        c.arrow((240, y + 64), (240, y + 96), color=BLUE)
    for y in [236, 332, 428]:
        c.arrow((720, y + 64), (720, y + 96), color=PURPLE)

    # 跨层：走分界线右侧的竖直通道
    c.arrow([(420, 556), (500, 556), (500, 268), (540, 268)], color=SLATE, width=1.8)

    c.text(60, 626, "这一侧只认识执行计划：读哪个索引、什么方向、给几行", size=11, fill=SUB)
    c.text(540, 626, "这一侧只认识页与记录：在哪个页、加不加锁、算不算可见", size=11, fill=SUB)

    c.text(540, 166, "跨过这道门，引擎只收到三件事：", size=10.5, fill=SLATE, weight=600)
    c.text(540, 190, "① 用哪个索引　② 往哪个方向　③ 要不要加锁", size=10.5, fill=SUB)
    c.text(540, 214, "它不知道这些行是给谁看的、为什么要看", size=10.5, fill=SUB)
    c.legend(40, 686, [(BLUE, "Server 层执行", None)])
    c.legend(220, 686, [(PURPLE, "引擎层读取", None)])
    c.legend(400, 686, [(GREEN, "写入落盘", None)])
    c.legend(560, 686, [(SLATE, "跨层调用的唯一入口", None)])
    return c.save(os.path.join(OUT, "ch44-fig1.svg"))


# ---------------------------------------------------------------- 图 44-2
def fig2():
    c = Canvas(960, 620,
               title="图 44-2　后台线程与它跟不上时你要看的那个指标",
               subtitle="线程名不用背：performance_schema.threads 的 NAME 列就是 thread/innodb/<线程名>")

    c.container(40, 92, 360, 470, "InnoDB 后台线程")
    c.container(560, 92, 360, 470, "它跟不上时，你看到的现象")

    rows = [
        ("srv_master_thread", "srv/srv0srv.cc",
         "周期任务整体滞后", "刷脏检查与 undo 清理都晚一拍", SLATE),
        ("io_ibuf / io_read / io_write", "异步 IO 线程组",
         "IO 队列打满", "Innodb_data_pending_reads 不降", BLUE),
        ("page_flush_coordinator", "page_flush_thread ×N",
         "checkpoint 年龄上涨", "脏页比顶到上限，用户线程代刷", GREEN),
        ("srv_purge_coordinator", "srv_worker_thread ×N",
         "History list length 涨", "undo 表空间膨胀，快照读变慢", ORANGE),
        ("dict_stats_thread", "dict/dict0stats_bg.cc",
         "统计信息陈旧", "执行计划突变，选错索引", TEAL),
    ]

    ys = [110, 196, 282, 368, 454]
    for (lt, ls, rt, rs, col), y in zip(rows, ys):
        c.box(60, y, 320, 66, lt, ls, accent=col, size=11.5, sub_size=9.5, mono=True)
        c.box(580, y, 320, 66, rt, rs, accent=col, size=11.5, sub_size=9.5)
        c.arrow((380, y + 33), (580, y + 33), color=col, width=1.8)

    c.text(60, 546, "这些线程不在 SHOW PROCESSLIST 里：它们没有连接，只跑周期任务", size=10.5, fill=SUB)
    c.text(580, 546, "箭头只是对应关系，不是因果关系", size=10.5, fill=SUB)

    c.legend(40, 588, [(SLATE, "周期调度", None)])
    c.legend(160, 588, [(BLUE, "IO", None)])
    c.legend(260, 588, [(GREEN, "刷脏", None)])
    c.legend(380, 588, [(ORANGE, "purge", None)])
    c.legend(520, 588, [(TEAL, "统计信息", None)])
    return c.save(os.path.join(OUT, "ch44-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
