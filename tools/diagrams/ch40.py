#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 40 章配图：参数与操作系统层调优"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 40-1
def fig1():
    c = Canvas(960, 800,
               title="图 40-1　MySQL 进程的内存：一个大方块，加一个随连接数增长的乘法",
               subtitle="buffer pool 是启动时按 chunk 分配好的固定预算；连接级 buffer 是执行期临时申请的，用完才还")

    # ---- 上半：两条曲线
    c.container(60, 84, 840, 270, "同一实例的内存占用（示意）：两条线，两种斜率")

    c.arrow((150, 318), (150, 140), color=SLATE)
    c.arrow((150, 318), (880, 318), color=SLATE)
    c.text(150, 128, "内存 RSS", size=10.5, fill=SUB, anchor="middle")
    c.text(880, 336, "时间 →", size=10.5, fill=SUB, anchor="end")

    c.arrow((150, 190), (880, 190), color=RED, dash="6,4", width=1.4, end=False)
    c.text(874, 182, "上限：物理内存或 cgroup limit", size=10.5, fill=RED, anchor="end")

    c.arrow([(170, 306), (320, 294), (480, 280), (660, 264), (860, 248)],
            color=GREEN, width=2.5, end=False)
    c.text(858, 238, "BP 调大：缓升", size=11, fill=GREEN, anchor="end")

    c.arrow([(170, 306), (300, 296), (370, 268), (420, 228), (452, 190)],
            color=RED, width=2.5)
    c.text(196, 246, "连接数暴涨", size=11, fill=RED)
    c.text(470, 178, "OOM Killer 在这里动手", size=11, fill=RED)

    c.arrow((150, 340), (176, 340), color=GREEN, end=False)
    c.text(184, 344, "调大 BP", size=10.5, fill=SUB)
    c.arrow((280, 340), (306, 340), color=RED, end=False)
    c.text(314, 344, "连接级 buffer × 活跃连接", size=10.5, fill=SUB)

    # ---- 下半：内存账本
    c.container(60, 394, 840, 250, "同一台 128GB 机器，两种负载下的账本（条宽按比例）")

    c.text(84, 434, "① 日常：20 个活跃连接，sort_buffer_size = 2M", size=11.5, fill=INK)
    c.rect(84, 444, 600, 40, fill=TINT[PURPLE], stroke=BORDER[PURPLE], r=4)
    c.rect(684, 444, 125, 40, fill=TINT[SLATE], stroke=BORDER[SLATE], r=4)
    c.rect(809, 444, 6, 40, fill=RED, stroke=RED, r=0)
    c.rect(815, 444, 69, 40, fill=TINT[SLATE], stroke=BORDER[SLATE], r=4)
    c.text(384, 469, "buffer pool 96GB", size=12, fill=PURPLE, anchor="middle", weight=600)
    c.text(746, 468, "page cache 20GB", size=9.5, fill=SLATE, anchor="middle")
    c.text(849, 468, "其他 11GB", size=9, fill=SUB, anchor="middle")
    c.text(84, 502, "连接级 buffer 合计 1GB，在这张图上几乎看不见 —— 这正是它平时不被怀疑的原因",
           size=11, fill=SUB)

    c.text(84, 534, "② 报表并发：180 个活跃连接，sort_buffer_size = 512M", size=11.5, fill=INK)
    c.rect(84, 544, 600, 40, fill=TINT[PURPLE], stroke=BORDER[PURPLE], r=4)
    c.rect(684, 544, 125, 40, fill=TINT[SLATE], stroke=BORDER[SLATE], r=4)
    c.rect(809, 544, 75, 40, fill=TINT[RED], stroke=BORDER[RED], r=4)
    c.text(384, 569, "buffer pool 96GB（没变）", size=12, fill=PURPLE, anchor="middle", weight=600)
    c.text(746, 568, "page cache 20GB", size=9.5, fill=SLATE, anchor="middle")
    c.text(846, 568, "只剩 12GB", size=9, fill=RED, anchor="middle")

    c.text(84, 604, "实际需要 96 + 20 + 92 = 208GB，超出的 80GB 没有地方放，内核挑最大的进程杀",
           size=11.5, fill=RED)
    c.text(84, 626, "把 BP 从 96GB 调到 64GB，等于把省下的 32GB 交给这个乘法", size=11.5, fill=SUB)

    # ---- 结论条
    c.box(60, 664, 260, 64, "固定块", "BP + log buffer，按 chunk 预分配", accent=PURPLE,
          size=13, sub_size=10)
    c.box(360, 664, 260, 64, "浮动块", "每连接 buffer，按查询需要申请", accent=RED,
          size=13, sub_size=10)
    c.box(660, 664, 260, 64, "OOM 的第一嫌疑", "sort_buffer_size × Threads_running", accent=RED,
          size=13, sub_size=10)

    c.legend(60, 748, [(PURPLE, "固定内存预算", None),
                       (RED, "浮动内存 / 超限风险", None)])
    return c.save(os.path.join(OUT, "ch40-fig1.svg"))


# ---------------------------------------------------------------- 图 40-2
def fig2():
    c = Canvas(960, 920,
               title="图 40-2　每个参数挂在哪一环：改它，动的是这条链路上的哪一段",
               subtitle="同一行里的参数共享一个作用点；跨行改参数等于同时动两个瓶颈，故障时无法归因")

    rows = [
        (96, PURPLE, "内存分配",
         ("innodb_buffer_pool_size", "独占 70~80%；共部署要留余量", 11),
         ("sort_buffer_size", "每连接 × 并发 = OOM 主因", 11.5),
         "改错：加内存追不上并发增长；OOM 先查 sort_buffer_size × Threads_running"),
        (226, BLUE, "刷脏与 IO",
         ("innodb_io_capacity", "默认 200 是 HDD 时代的数", 11.5),
         ("innodb_flush_neighbors", "[8.0] 默认 0，SSD 别开", 11),
         "改错：刷不及时 checkpoint age 涨；设太大把设备 IO 打满，别的查询一起慢"),
        (356, RED, "提交持久性",
         ("innodb_flush_log_at_trx_commit", "默认 1；改成 2 丢掉最近 1 秒事务", 10),
         ("innodb_redo_log_capacity", "[8.0.30+] 取代 log_file_size", 11),
         "改错：拿持久性换吞吐，金融场景就是事故；redo 太小则 checkpoint 频繁"),
        (486, ORANGE, "并发入口",
         ("innodb_thread_concurrency", "默认 0；非 0 就在入口排队", 11.5),
         ("table_open_cache", "Opened_tables 持续涨才该加", 11.5),
         "改错：人为制造排队，queries in queue 飙升，吞吐反而下降"),
        (616, ORANGE, "临时表",
         ("tmp_table_size", "必须 = max_heap_table_size", 11.5),
         ("temptable_max_ram", "[8.0] TempTable 的真实阈值", 11.5),
         "改错：只调大的那个，实际生效的是小的那个；[8.0] 默认下改它根本不生效"),
        (746, SLATE, "优化器决策",
         ("eq_range_index_dive_limit", "默认 200；长 IN 列表计划突变", 11),
         ("range_optimizer_max_mem_size", "默认 8MB；超了退化成全表扫", 11),
         "改错：SET GLOBAL 一改，救一条 SQL 可能坑掉另外一百条"),
    ]

    for y, col, stage, p1, p2, cost in rows:
        c.container(60, y, 840, 116, "")
        c.box(80, y + 30, 130, 50, stage, accent=col, size=13)
        c.box(250, y + 22, 210, 56, p1[0], p1[1], accent=col, size=p1[2], sub_size=9.5)
        c.box(500, y + 22, 210, 56, p2[0], p2[1], accent=col, size=p2[2], sub_size=9.5)
        c.text(250, y + 100, cost, size=11, fill=SUB)

    c.legend(60, 890, [(PURPLE, "内存", None)])
    c.legend(160, 890, [(BLUE, "刷脏 / IO", None)])
    c.legend(300, 890, [(ORANGE, "并发 / 参数阈值", None)])
    c.legend(470, 890, [(RED, "风险 / 误判", None)])
    c.legend(620, 890, [(SLATE, "优化器 / 跨层", None)])
    return c.save(os.path.join(OUT, "ch40-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
