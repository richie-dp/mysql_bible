#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 2 章配图：InnoDB 内存体系"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 2-1
def fig1():
    c = Canvas(960, 700,
               title="图 2-1　Buffer Pool：一个池子，N 份独立结构，三条链表",
               subtitle="page hash 保证「一页只有一份」；三条链表分别回答「哪能分配 / 谁该淘汰 / 谁还没落盘」")

    # ---- 定位路径
    c.box(60, 78, 160, 44, "页请求", "space_id + page_no", accent=SLATE, size=13)
    c.arrow(220, 100, 268, 100, color=SLATE)
    c.box(268, 78, 210, 44, "page hash", "O(1) 定位到 frame", accent=SLATE, size=13)
    c.arrow(478, 100, 526, 100, color=SLATE)
    c.box(526, 78, 170, 44, "命中？", "命中直接用", accent=SLATE, size=13)
    c.arrow(696, 100, 744, 100, color=BLUE, label="否")
    c.box(744, 78, 156, 44, "未命中", "读磁盘 16KB 页", accent=BLUE, size=13)

    c.arrow(350, 122, 350, 158, color=SLATE)

    # ---- 实例内部
    c.container(60, 158, 840, 202,
                "Buffer Pool Instance #k —— 每个实例有独立的 mutex、page hash 和三条链表")

    c.box(80, 192, 180, 44, "chunk 0", "128MB / 8192 页", accent=BLUE, size=13)
    c.box(280, 192, 180, 44, "chunk 1", "扩缩容的最小单位", accent=BLUE, size=13)
    c.text(484, 219, "… 每个 chunk 切成 8192 个 16KB 的 frame", size=11, fill=SUB)

    c.box(80, 272, 250, 46, "free list", "还有多少 frame 可分配", accent=GREEN, size=13)
    c.box(350, 272, 250, 46, "LRU list", "young 5/8 · old 3/8", accent=BLUE, size=13)
    c.box(620, 272, 260, 46, "flush_list", "按 oldest_modification 升序", accent=ORANGE, size=13)

    c.text(80, 344, "一个页可以同时在 LRU 和 flush_list 上：前者管淘汰，后者管落盘",
           size=11, fill=SUB)

    # ---- 页的身份变化
    c.container(60, 380, 840, 210, "同一个页的身份变化（从左到右）")

    c.box(80, 440, 155, 56, "free list", "空闲 frame，可分配", accent=GREEN, size=13)
    c.box(295, 440, 155, 56, "LRU old 区", "新页统一从这里进入", accent=BLUE, size=13)
    c.box(510, 440, 155, 56, "LRU young 区", "停留 >1s 才晋升", accent=BLUE, size=13)
    c.box(725, 440, 155, 56, "flush_list", "脏页：待刷但仍在 LRU", accent=ORANGE, size=13)

    c.arrow(235, 468, 295, 468, color=BLUE, label="读入")
    c.arrow(450, 468, 510, 468, color=BLUE, label="再命中")
    c.arrow(665, 468, 725, 468, color=ORANGE, label="UPDATE")

    c.text(80, 545, "刷盘后页不会离开 LRU，只是从 flush_list 摘除——「脏页比例下降」不等于「页被释放」",
           size=11, fill=SUB)

    c.legend(60, 620, [(GREEN, "分配与落盘", None),
                       (BLUE, "读路径 / 链表归属", None),
                       (ORANGE, "脏页", None)])
    return c.save(os.path.join(OUT, "ch02-fig1.svg"))


# ---------------------------------------------------------------- 图 2-2
def fig2():
    c = Canvas(960, 600,
               title="图 2-2　改良 LRU：新页只进 old 区，全表扫描冲不垮热数据",
               subtitle="innodb_old_blocks_pct=37 划边界，innodb_old_blocks_time=1000 决定能否晋升")

    c.container(60, 96, 840, 150, "LRU 链表（左 head → 右 tail，越靠右越先被淘汰）")

    c.box(80, 140, 475, 62, "young 区（约 5/8）", "二次访问且停留超 1s 才晋升到头部",
          accent=BLUE, size=13, sub_size=10)
    c.box(595, 140, 285, 62, "old 区（约 3/8）", "新页一律插到 old 区头部",
          accent=SLATE, size=13, sub_size=10)

    c.arrow((575, 132), (575, 212), color=SLATE, dash="4,3", end=False)
    c.text(575, 228, "midpoint（新旧页的分界）", size=10, fill=SUB, anchor="middle")
    c.text(80, 228, "head：最近访问", size=10, fill=SUB)
    c.text(880, 228, "tail：最先淘汰", size=10, fill=SUB, anchor="end")

    # ---- 扫描推演
    c.container(60, 276, 840, 130, "一次全表扫描，为什么只脏了 old 区")

    c.box(80, 316, 240, 56, "① 预读整个 extent", "64 个页全插到 old 头", accent=TEAL, size=13, sub_size=10)
    c.box(360, 316, 240, 56, "② 1 秒内再次访问", "old 区的页不晋升", accent=BLUE, size=13, sub_size=10)
    c.box(640, 316, 240, 56, "③ 扫描继续推进", "从 old 尾部把自己挤掉", accent=GREEN, size=13, sub_size=10)

    c.arrow(320, 344, 360, 344, color=BLUE)
    c.arrow(600, 344, 640, 344, color=BLUE)

    # ---- 两种参数值
    c.container(60, 420, 840, 116, "同一个全表扫描，两个参数值的结局")

    c.box(80, 452, 380, 60, "innodb_old_blocks_time = 0", "每次命中都晋升，扫描把热页顶走",
          accent=RED, size=13, sub_size=10)
    c.box(500, 452, 380, 60, "innodb_old_blocks_time = 1000", "1 秒内不晋升，扫描退化为顺序 IO",
          accent=GREEN, size=13, sub_size=10)

    c.text(60, 566, "代价：真正的新热点要等 1 秒才能进 young 区——冷启动后的第一秒，命中率是失真的。",
           size=12, fill=INK)
    return c.save(os.path.join(OUT, "ch02-fig2.svg"))


# ---------------------------------------------------------------- 图 2-3
def fig3():
    c = Canvas(960, 740,
               title="图 2-3　一次脏页刷新的完整链路，以及用户线程被拖下水的位置",
               subtitle="后台有预算地刷；预算不够时，三条路径会把同步 IO 压到用户线程身上")

    c.box(350, 84, 260, 48, "UPDATE 修改数据页", "redo 已写，页变成脏页", accent=ORANGE, size=13, sub_size=10)
    c.arrow(480, 132, 480, 158, color=ORANGE)

    c.box(280, 158, 400, 48, "脏页：LRU 与 flush_list 各挂一次", "两条链表各管一件事，互不替代",
          accent=ORANGE, size=13, sub_size=10)

    # 分支总线
    c.arrow((480, 206), (480, 220), color=ORANGE, end=False)
    c.arrow((200, 220), (760, 220), color=ORANGE, end=False)

    c.arrow((200, 220), (200, 240), color=BLUE)
    c.arrow((480, 220), (480, 240), color=BLUE)
    c.arrow((760, 220), (760, 240), color=RED)

    c.box(80, 240, 240, 52, "① LRU 尾部刷脏", "腾 free frame，不保证顺序", accent=BLUE, size=13, sub_size=10)
    c.box(360, 240, 240, 52, "② flush_list 刷脏", "按 LSN 升序，推进 checkpoint", accent=BLUE, size=13, sub_size=10)
    c.box(640, 240, 240, 52, "③ 用户线程同步刷脏", "free 见底 / redo 将满", accent=RED, size=13, sub_size=10)

    c.arrow((200, 292), (200, 312), color=BLUE)
    c.arrow((480, 292), (480, 312), color=BLUE)
    c.arrow((760, 292), (760, 312), color=RED)

    c.box(80, 312, 520, 52, "page cleaner 后台线程",
          "每秒重算目标页数 = f(脏页比例, redo 水位) × io_capacity", accent=BLUE, size=13, sub_size=10)
    c.box(640, 312, 240, 52, "用户 SQL 线程", "在同步刷脏里等 IO", accent=RED, size=13, sub_size=10)

    c.arrow((340, 364), (340, 404), color=BLUE, label="异步批量")
    c.arrow((760, 364), (760, 404), color=RED, label="同步，SQL 停在这里")

    c.box(80, 404, 800, 52, "doublewrite buffer → .ibd 数据文件",
          "先顺序写双写区，再随机写数据文件", accent=GREEN, size=13, sub_size=10)

    c.arrow(480, 456, 480, 494, color=GREEN)
    c.box(80, 494, 800, 52, "页变干净：移出 flush_list，仍然是 LRU 成员",
          "oldest_modification 前移到下一个脏页", accent=GREEN, size=13, sub_size=10)

    c.arrow(480, 546, 480, 584, color=PURPLE)
    c.box(80, 584, 800, 52, "checkpoint 前进 → redo 可复用空间变大 → log_free_check 不再阻塞",
          "用户线程回到正常路径", accent=PURPLE, size=13, sub_size=10)

    c.legend(60, 664, [(BLUE, "后台刷脏（有预算）", None),
                       (RED, "用户线程被迫同步刷脏", None),
                       (GREEN, "落盘写入", None),
                       (PURPLE, "checkpoint / redo 空间", None)])
    return c.save(os.path.join(OUT, "ch02-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
