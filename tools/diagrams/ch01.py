#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 1 章配图：一条 SQL 的完整生命周期"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 1-1
def fig1():
    c = Canvas(960, 620, title="图 1-1　一条查询穿过 MySQL 的四层",
               subtitle="层次边界比组件名字更重要：跨过 handler 接口，才进入存储引擎")

    # 客户端
    c.box(400, 72, 160, 42, "客户端", accent=None)
    c.arrow(480, 114, 480, 158, color=SLATE, label="SQL 文本")

    # 连接层
    c.container(60, 158, 840, 78, "① 连接层")
    c.box(100, 182, 220, 44, "连接器", "认证 / 权限 / TLS 握手", accent=BLUE)
    c.box(380, 182, 240, 44, "线程 + 会话状态", "one-thread-per-connection", accent=BLUE)
    c.text(650, 208, "max_connections 打满 → 1040 Too many connections",
           size=11, fill=SUB)
    c.arrow(320, 204, 380, 204, color=BLUE)

    # Server 层
    c.container(60, 262, 840, 96, "② Server 层（与存储引擎无关）")
    c.box(80, 292, 130, 46, "解析器", "词法 + 语法 → AST", accent=BLUE, size=13)
    c.box(236, 292, 130, 46, "预处理器", "表/列是否存在", accent=BLUE, size=13)
    c.box(392, 292, 130, 46, "优化器", "选索引 / join 顺序", accent=BLUE, size=13)
    c.box(548, 292, 150, 46, "执行器", "Volcano 迭代器", accent=BLUE, size=13)
    c.arrow(210, 315, 236, 315, color=BLUE)
    c.arrow(366, 315, 392, 315, color=BLUE)
    c.arrow(522, 315, 548, 315, color=BLUE)
    c.arrow(480, 236, 480, 292, color=SLATE)
    c.text(700, 340, "8.0 已移除查询缓存", size=11, fill=SUB)

    # 引擎层
    c.container(60, 386, 840, 96, "③ 存储引擎层（可插拔）")
    c.box(80, 416, 200, 46, "handler 接口", "ha_index_read_map()", accent=GREEN, size=13)
    c.box(320, 416, 180, 46, "InnoDB", "事务 / 行锁 / MVCC", accent=GREEN, size=13)
    c.box(540, 416, 180, 46, "MyISAM · Memory", "无事务（遗留）", accent=None, size=13)
    c.arrow(480, 358, 480, 416, color=SLATE, label="按行回调")
    c.arrow(280, 439, 320, 439, color=GREEN)

    # 磁盘
    c.container(60, 510, 840, 82, "④ 磁盘")
    c.cyl(100, 528, 150, 54, ".ibd", "数据页 16KB", accent=GREEN)
    c.box(290, 532, 190, 46, "redo / undo / binlog", "三类日志各司其职", accent=RED, size=13)
    c.box(520, 532, 170, 46, ".sdi / 数据字典", "8.0 事务性字典", accent=None, size=13)
    c.arrow(480, 482, 480, 528, color=GREEN)

    c.legend(690, 90, [(BLUE, "SQL 层处理", None),
                       (SLATE, "跨层调用", "4,2"),
                       (GREEN, "引擎与落盘", None)])
    return c.save(os.path.join(OUT, "ch01-fig1.svg"))


# ---------------------------------------------------------------- 图 1-2
def fig2():
    c = Canvas(960, 640, title="图 1-2　一条 UPDATE 的时序：redo 与 binlog 如何对齐",
               subtitle="两个日志分属不同层，靠内部 XA 的两阶段提交保证一致")

    lanes = [("执行器\n(Server 层)", 120, BLUE),
             ("InnoDB\nBuffer Pool + undo", 380, GREEN),
             ("redo log\n(log buffer)", 640, RED),
             ("binlog\n(Server 层)", 850, PURPLE)]

    for name, x, col in lanes:
        title = name.split("\n")
        c.box(x - 78, 76, 156, 48, title[0], title[1] if len(title) > 1 else None,
              accent=col, size=13, sub_size=10)
        c.els.append(f'<line x1="{x}" y1="124" x2="{x}" y2="560" '
                     f'stroke="{LINE}" stroke-width="1.2" stroke-dasharray="5,5"/>')

    def msg(y, x1, x2, label, color=BLUE, dash=None, dy=-7):
        c.arrow(x1, y, x2, y, color=color, dash=dash, label=label, label_dy=dy)
        return y

    y = 168
    msg(y, 120, 380, "① 按 id=1 定位，加 X 记录锁")
    y += 46
    msg(y, 380, 640, "② 记 undo：旧值 c=1 写入版本链", color=ORANGE, dy=-7)
    y += 46
    msg(y, 120, 380, "③ 修改数据页（成为脏页，未落盘）")
    y += 46
    msg(y, 380, 640, "④ 写 redo，trx 状态 = prepare", color=RED)
    y += 46

    c.container(60, y - 26, 840, 150, "内部 XA：第二阶段（binlog 落盘后才允许 commit）",
                dash="5,4", fill="#fffdf5", stroke="#fde68a")
    y += 14
    msg(y, 120, 850, "⑤ 写 binlog（ROW 格式）+ fsync", color=PURPLE)
    y += 46
    msg(y, 380, 640, "⑥ redo 状态改为 commit", color=RED)
    y += 46
    c.text(440, y + 4, "⑦ 返回「1 row affected」——此时数据页可能还在内存里",
           size=12, fill=INK)

    c.mono_box(60, 470, 400, 110, [
        "# 崩溃点不同，恢复行为不同：",
        "prepare 前崩溃   → 回滚（redo 无效）",
        "prepare 后、binlog 前崩溃 → 回滚",
        "binlog 完整后崩溃 → 提交（重放 binlog）",
    ], title="恢复判据")
    c.legend(520, 486, [(BLUE, "SQL 层动作", None),
                        (ORANGE, "undo 写入", "4,2"),
                        (RED, "redo 写入", None),
                        (PURPLE, "binlog 写入", None)])
    return c.save(os.path.join(OUT, "ch01-fig2.svg"))


# ---------------------------------------------------------------- 图 1-3
def fig3():
    c = Canvas(960, 560, title="图 1-3　同一张表，两条完全不同的读路径",
               subtitle="快照读不加锁、走 undo 版本链；当前读加锁、读最新已提交版本")

    c.container(60, 96, 400, 380, "快照读　SELECT ... (RR)")
    c.box(100, 140, 170, 48, "一致性读视图", "首条 SELECT 时创建", accent=BLUE, size=13)
    c.arrow(185, 188, 185, 232, color=BLUE)
    c.box(100, 232, 170, 48, "判断可见性", "trx_id < min_trx_id ?", accent=BLUE, size=13)
    c.arrow(185, 280, 185, 324, color=BLUE, label="不可见则回溯", label_side="right")
    c.cyl(100, 324, 170, 56, "undo 版本链", "DB_ROLL_PTR 串联", accent=ORANGE)
    c.arrow(270, 352, 310, 352, color=BLUE)
    c.box(310, 328, 130, 48, "返回历史版本", "不加任何锁", accent=GREEN, size=13)
    c.text(100, 410, "不阻塞写入，也不被写入阻塞（除 DDL）", size=11, fill=SUB)
    c.text(100, 430, "代价：可能读到「旧」数据", size=11, fill=SUB)

    c.container(500, 96, 400, 380, "当前读　UPDATE / FOR UPDATE / DELETE")
    c.box(540, 140, 170, 48, "加锁读", "Next-Key Lock", accent=RED, size=13)
    c.arrow(625, 188, 625, 232, color=RED)
    c.box(540, 232, 170, 48, "读最新已提交版本", "在 Buffer Pool 中", accent=RED, size=13)
    c.arrow(625, 280, 625, 324, color=RED)
    c.box(540, 324, 170, 48, "改写 + undo / redo", "细节见第 4、5 章", accent=GREEN, size=13)
    c.arrow(710, 348, 745, 348, color=RED)
    c.box(745, 324, 130, 48, "阻塞其他写", "等锁 / 死锁", accent=RED, size=13)
    c.text(540, 410, "读到的一定是最新数据（当前读语义）", size=11, fill=SUB)
    c.text(540, 430, "代价：并发下降、可能死锁", size=11, fill=SUB)

    c.text(60, 512, "同一条 SQL 里，UPDATE 的 WHERE 走当前读，而它前面的 SELECT 可能走快照读——"
                    "这就是「同一事务两次查询结果不同」的根源。", size=12, fill=INK)
    return c.save(os.path.join(OUT, "ch01-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
