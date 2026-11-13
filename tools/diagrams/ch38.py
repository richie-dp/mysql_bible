#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 38 章配图：慢查询与 performance_schema 实战"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 38-1
def fig1():
    c = Canvas(960, 810, title="图 38-1　pt-query-digest 报告的三层结构",
               subtitle="同一份报告，三层回答三个不同的问题；跳过任一层都会得出错误结论")

    blocks = [
        (100, 112, [
            "# Overall: 1.23k total, 12 unique, 0.05 QPS",
            "# Attribute        total    min    max    avg    95%  median",
            "# ==========     ======= ====== ====== ====== ====== =======",
            "# Exec time         523s   10ms     2s  430ms   900ms   400ms",
            "# Rows examined      48M      0    90k    39k    98k     31k",
        ], "① Overall 段", "规模与形状：多少条、多少类、离散度多大", BLUE),

        (232, 112, [
            "# Profile",
            "# Rank Query ID        Response time  Calls  R/Call  V/M",
            "# ==== =============== ============== ====== ======= ====",
            "#    1 0x7f3c2a...       235.4s 45.0%   1200   196ms  0.31",
            "#    2 0x91ab07...       141.2s 27.0%     18   7.8s   0.02",
        ], "② Profile 段", "按「总耗时」排序：先看谁，不等于先优化谁", ORANGE),

        (364, 146, [
            "# Query 1: 0.02 QPS, ID 0x7f3c2a... at byte 88213",
            "# Attribute     pct   total     min     max     avg     95%  median",
            "# Count          10    1200",
            "# Exec time      45    235s    80ms      2s   196ms   420ms   180ms",
            "# Lock time      31     73s       0   900ms    61ms   210ms    40ms",
            "# Rows sent       4    120k       1     900     100     210      96",
            "# Rows examine   82     41M       0     90k     34k     76k     29k",
        ], "③ 单条明细段", "Rows examine : Rows sent —— 诊断重点在这里", RED),

        (530, 112, [
            "# Query_time distribution",
            "#   1ms",
            "#  10ms  ####",
            "# 100ms  ####################",
            "#    1s  ###",
        ], "④ 直方图段", "稳定慢还是长尾；双峰最容易被平均值掩盖", PURPLE),

        (662, 94, [
            "# Tables",
            "#   SHOW CREATE TABLE `shop`.`order_main`\\G",
            "# EXPLAIN /*!50100 PARTITIONS*/",
            "#   SELECT * FROM order_main WHERE merchant_id=? AND status=?",
        ], "⑤ Tables / EXPLAIN", "把这条 SQL 落到具体的表与执行计划", SLATE),
    ]

    for y, h, lines, title, sub, col in blocks:
        c.mono_box(60, y, 520, h, lines)
        cy = y + h / 2
        c.arrow(580, cy, 630, cy, color=SLATE, width=1.2, dash="4,3")
        c.box(630, cy - 42, 280, 84, title, sub, accent=col, size=13, sub_size=10.5)

    c.text(60, 782, "命令：pt-query-digest --explain h=127.0.0.1,u=ro slow.log > report.txt",
           size=11, fill=SUB, mono=True)
    return c.save(os.path.join(OUT, "ch38-fig1.svg"))


# ---------------------------------------------------------------- 图 38-2
def fig2():
    c = Canvas(960, 540, title="图 38-2　慢查询治理闭环：五个环节，缺一环就原地打转",
               subtitle="红色回环是最常见的走法——把「定责」省了，改完的索引三个月后照样失效")

    stages = [
        ("① 采集", "慢日志 / p_s digest", "产出：原始日志", BLUE),
        ("② 归类", "按 DIGEST 合并同类", "产出：Top 20 清单", BLUE),
        ("③ 定责", "落到业务方与接口", "产出：负责人表", RED),
        ("④ 优化", "索引 / 改写 / 拆分", "产出：变更单", GREEN),
        ("⑤ 回归", "比行数、比分位", "产出：对比快照", GREEN),
    ]
    xs = [46, 228, 410, 592, 774]
    for (t, s, p, col), x in zip(stages, xs):
        c.box(x, 150, 140, 104, t, s, accent=col, size=13, sub_size=10.5)
        c.text(x + 70, 242, p, size=10, fill=col, anchor="middle", weight=600)

    for i in range(4):
        c.arrow(xs[i] + 140, 202, xs[i + 1], 202, color=BLUE)

    # 跳过定责的回环：从「优化」底部绕回「采集」
    c.arrow([(714, 254), (714, 430), (178, 430), (178, 254)],
            color=RED, dash="6,5", width=1.6)
    c.text(480, 324, "跳过这一步", size=10.5, fill=RED, anchor="middle", weight=600)
    c.text(446, 460, "跳过定责：改完的 SQL 没有归属，三个月后同一批 digest 重新上榜",
           size=11.5, fill=RED, anchor="middle", weight=500)

    c.text(60, 504, "闭环的判据不是「改了几条 SQL」，而是「下一次同类 SQL 出现时，有人认领」。",
           size=11.5, fill=INK)
    return c.save(os.path.join(OUT, "ch38-fig2.svg"))


# ---------------------------------------------------------------- 图 38-3
def fig3():
    c = Canvas(960, 740, title="图 38-3　performance_schema 的三层：采集、消费、存储",
               subtitle="内存只在第三层；前两层是开关，所以「关掉采集」是唯一能在线降开销的手段")

    # ---- 第一层：生产者
    c.container(60, 104, 560, 150, "① 生产者　setup_instruments：每个采集点一个开关位")
    for x, t, s in [(76, "statement/sql/*", "语句层"),
                    (266, "wait/io/file/*", "文件 IO"),
                    (456, "wait/synch/*", "内部同步")]:
        c.box(x, 148, 150, 62, t, s, accent=PURPLE, size=11, sub_size=10)
    c.badge(478, 112, "内存 ≈ 0", accent=ORANGE)

    # ---- 第二层：消费者
    c.container(60, 290, 560, 160, "② 消费者　setup_consumers：决定写不写明细表")
    for x, t, s in [(76, "*_current", "当前事件"),
                    (266, "*_history", "每线程 N 条"),
                    (456, "*_history_long", "全局环形缓冲")]:
        c.box(x, 336, 150, 62, t, s, accent=PURPLE, size=11, sub_size=10)
    c.badge(406, 298, "内存：条数 × 单条宽度", accent=ORANGE)

    # ---- 第三层：存储
    c.container(60, 490, 560, 160, "③ 存储　performance_schema 表：内存真正花在这里")
    c.box(72, 536, 250, 62, "events_statements_", "summary_by_digest",
          accent=PURPLE, size=11, sub_size=10)
    c.box(362, 536, 250, 62, "file_summary_", "by_instance",
          accent=PURPLE, size=11, sub_size=10)
    c.badge(446, 498, "内存：行数 × 文本长度", accent=ORANGE)

    # ---- 右侧：参数与代价
    cards = [
        (104, 150, 179, [
            (26, "开关：可在线改", 12, INK, True, False),
            (48, "UPDATE setup_instruments", 10, SLATE, False, True),
            (64, "  SET ENABLED='NO'", 10, SLATE, False, True),
            (88, "关掉 = 不采集，但不释放", 10.5, SUB, False, False),
            (106, "已分配的表内存", 10.5, SUB, False, False),
        ]),
        (290, 160, 370, [
            (26, "条数上限（需重启）", 12, INK, True, False),
            (48, "..._events_statements_", 10, SLATE, False, True),
            (64, "   history_long_size", 10, SLATE, False, True),
            (88, "高 QPS 下环形缓冲只够", 10.5, SUB, False, False),
            (106, "存几秒，不是归档", 10.5, SUB, False, False),
        ]),
        (490, 160, 570, [
            (26, "长度 × 行数（需重启）", 12, INK, True, False),
            (48, "performance_schema_digests_size", 9.5, SLATE, False, True),
            (64, "performance_schema_max_digest_length", 9.5, SLATE, False, True),
            (88, "两者相乘：调大一档", 10.5, SUB, False, False),
            (108, "内存按乘法涨", 10.5, SUB, False, False),
        ]),
    ]
    for y, h, ay, lines in cards:
        c.rect(650, y, 270, h, fill="#fff7ed", stroke="#fed7aa", sw=1.4, r=8)
        for dy, txt, size, fill, bold, mono in lines:
            c.text(664, y + dy, txt, size=size, fill=fill,
                   weight=600 if bold else 400, mono=mono)
        c.arrow(620, ay, 650, ay, color=SLATE, width=1.2, dash="4,3")

    # 层间连线
    c.arrow(340, 254, 340, 290, color=BLUE, label="交给消费者")
    c.arrow(340, 450, 340, 490, color=BLUE, label="落到表")

    c.text(60, 700, "最小可用配置：留 global_instrumentation + thread_instrumentation 的 summary 层，"
                    "关掉 stages 与 history_long。", size=11.5, fill=INK)
    return c.save(os.path.join(OUT, "ch38-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
