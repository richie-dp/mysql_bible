#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""附录 A 配图：参数速查表"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 A-1
def fig1():
    c = Canvas(960, 672,
               title="图 A-1　参数的四种生效路径：改在哪里，谁看得见",
               subtitle="同一条参数，走哪条路径决定了「改完要不要重启」和「老连接认不认」")

    lanes = [
        # (行 y, 颜色, 方式, 方式副标, 动作, 动作副标, 结果, 结果副标, 骗你, 适用)
        (86, SLATE, "my.cnf 静态", "写文件，重启才读",
         "重启 mysqld", "停机窗口内完成",
         "全实例生效", "启动时读一次",
         "改了没重启，值根本没变",
         "适用：innodb_page_size、chunk_size、lower_case_table_names"),
        (210, BLUE, "SET GLOBAL", "立即改内存里的值",
         "立即生效", "不用重启",
         "新老会话都变", "读的是全局值",
         "重启后回到 my.cnf 的旧值",
         "适用：innodb_io_capacity、max_connections、sync_binlog"),
        (334, ORANGE, "仅新连接", "SET GLOBAL 的半生效态",
         "只影响新会话", "老连接不重读",
         "老连接仍用旧值", "要重连才拿到",
         "监控变了，跑批连接还是旧值",
         "适用：wait_timeout、sort_buffer_size、sql_mode"),
        (458, GREEN, "SET SESSION", "只改当前连接",
         "仅本会话生效", "别的会话看不见",
         "断开即恢复", "写不进 my.cnf",
         "你试好了，应用连上来还是默认值",
         "适用：optimizer_switch、单条 SQL 的 sort_buffer_size"),
    ]

    for y, col, name, name_sub, act, act_sub, res, res_sub, cheat, scope in lanes:
        c.container(48, y, 864, 112, "")
        c.box(60, y + 12, 144, 50, name, name_sub, accent=col, size=11.5, sub_size=9.5)
        c.arrow(206, y + 37, 246, y + 37, color=col, width=1.4)
        c.box(248, y + 12, 188, 50, act, act_sub, accent=col, size=11, sub_size=9.5)
        c.arrow(438, y + 37, 478, y + 37, color=col, width=1.4)
        c.box(480, y + 12, 196, 50, res, res_sub, accent=col, size=11, sub_size=9.5)
        c.text(700, y + 30, "骗你：" + cheat, size=10.5, fill=RED, weight=500)
        c.text(60, y + 88, scope, size=9.8, fill=SUB)

    c.text(48, 596, "前两条是「改完就生效」，后两条是「改完只对一部分人生效」——值班时的误判全部发生在后两条。",
           size=11, fill=INK)
    c.legend(48, 616, [(SLATE, "重启才生效：要停机窗口", None),
                       (BLUE, "动态生效：立刻可见，重启丢失", None)])
    c.legend(520, 616, [(ORANGE, "仅新连接：老会话保持旧值", None),
                        (GREEN, "仅本会话：断开即失效", None)])
    return c.save(os.path.join(OUT, "appA-fig1.svg"))


# ---------------------------------------------------------------- 图 A-2
def fig2():
    c = Canvas(960, 680,
               title="图 A-2　内存预算的四层分配：只调大第一层，第二层会按并发吃回来",
               subtitle="竖条按示意比例切分，不是精确占比；第二层是唯一随并发线性增长的一层")

    # 竖条
    c.text(110, 100, "物理内存 128G（示例）", size=11, fill=SUB, weight=600)
    bar_x, bar_w = 110, 140
    segs = [
        (110, 235, BLUE, "buffer pool", "64G 预分配"),
        (345, 146, RED, "每连接 × 并发", "峰值 40G"),
        (491, 29, PURPLE, "临时表", "8G"),
        (520, 60, SLATE, "OS 与余量", "16G"),
    ]
    for y, h, col, name, val in segs:
        c.rect(bar_x, y, bar_w, h, fill=col, stroke=col, sw=1, r=0)
        if h >= 100:
            c.text(bar_x + bar_w / 2, y + h / 2 - 8, name, size=11.5,
                   fill="#ffffff", anchor="middle", weight=600)
            c.text(bar_x + bar_w / 2, y + h / 2 + 12, val, size=10.5,
                   fill="#ffffff", anchor="middle")
        else:
            c.text(bar_x + bar_w / 2, y + h / 2 + 4, name + " " + val, size=9.5,
                   fill="#ffffff", anchor="middle", weight=600)

    # 右侧注解
    notes = [
        (150, BLUE, "buffer pool", "预分配，命中率的天花板由它定",
         [(250, 227), (274, 227), (274, 181), (296, 181)]),
        (235, RED, "每连接 buffer", "2M × 200 = 400M；256M × 160 = 40G",
         [(250, 418), (280, 418), (280, 266), (296, 266)]),
        (320, PURPLE, "临时表", "temptable_max_ram 是全局共享上限",
         [(250, 505), (286, 505), (286, 351), (296, 351)]),
        (405, SLATE, "OS 与余量", "page cache、备份顺序读、内核自身",
         [(250, 550), (292, 550), (292, 436), (296, 436)]),
    ]
    for y, col, title, sub, pts in notes:
        c.arrow(pts, color=col, width=1.3, end=False)
        c.box(300, y, 340, 62, title, sub, accent=col, size=11.5, sub_size=9.5)

    # 右侧：只调大第一层会怎样
    c.container(684, 110, 228, 470, "只调大第一层")
    c.box(700, 146, 196, 54, "BP 64G → 96G", "只加第一层", accent=RED, size=11)
    c.arrow(798, 200, 798, 218, color=RED, width=1.3)
    c.box(700, 218, 196, 54, "总需求 160G", "四层相加超 128G", accent=RED, size=11)
    c.arrow(798, 272, 798, 290, color=RED, width=1.3)
    c.box(700, 290, 196, 54, "OOM Killer", "按 anon-rss 排序", accent=RED, size=11)
    c.mono_box(700, 366, 196, 140,
               ["RSS ≈ BP", "+ 固定开销", "+ Σ(buffer×并发)", "+ 临时表"],
               title="预算公式", size=10)
    c.text(700, 540, "顺序不能反：先压第二层，", size=10, fill=RED, weight=500)
    c.text(700, 558, "再加第一层。", size=10, fill=RED, weight=500)

    c.text(110, 606, "四层之和必须小于物理内存。只调大第一层，省下的空间会被第二层按并发吃回去。",
           size=11, fill=INK)
    c.text(110, 628, "第二层平时不出现，只在导出、对账的并发高峰出现——案例八那次 OOM 就是它的形状。",
           size=10.5, fill=SUB)
    return c.save(os.path.join(OUT, "appA-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
