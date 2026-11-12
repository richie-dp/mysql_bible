#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 7 章配图：partial write / doublewrite 与崩溃恢复三阶段"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 7-1
def fig1():
    c = Canvas(960, 730,
               title="图 7-1　partial write：为什么 redo 修不好一个坏页",
               subtitle="以 4KB 扇区为例：16KB 的页分四次落地，掉电可能停在第三块；doublewrite 用完整副本兜住，再写回原位")

    # ---- 上半：torn page 现场
    c.container(40, 78, 880, 180, "一次 16KB 的页写入，可能只落地了一半")

    c.rect(64, 118, 424, 112, fill="#ffffff", stroke=LINE, r=6)
    c.box(76, 138, 92, 72, "块 0", "已落盘", accent=GREEN, size=12, sub_size=10)
    c.box(180, 138, 92, 72, "块 1", "已落盘", accent=GREEN, size=12, sub_size=10)
    c.box(284, 138, 92, 72, "块 2", "旧数据", accent=RED, size=12, sub_size=10)
    c.box(388, 138, 92, 72, "块 3", "旧数据", accent=RED, size=12, sub_size=10)

    c.text(520, 136, "一次 write 落在 4 个 4KB 扇区上，不是一个原子动作",
           size=12, weight=600)
    c.text(520, 162, "掉电停在第 3 块之前：前 8KB 是新版本，后 8KB 是旧版本",
           size=11, fill=SUB)
    c.text(520, 184, "页头的 LSN 已经是新的，checksum 却对不上", size=11, fill=SUB)
    c.text(520, 210, "这一页既不是新页，也不是旧页", size=11, fill=RED, weight=600)

    # ---- 中段：两种结局
    c.container(40, 280, 420, 146, "只有 redo：无处下手", label_color=RED)
    c.box(60, 318, 380, 44, "页的结构已经不可信",
          "记录槽 / 页目录 / checksum 全对不上", accent=RED, size=12, sub_size=10)
    c.text(60, 392, "redo 是 physiological：先按页号找到页，", size=11, fill=SUB)
    c.text(60, 412, "再在页内定位记录槽。前提是页还能被解析。", size=11, fill=SUB)

    c.container(500, 280, 420, 146, "有 doublewrite：整页覆盖后再重放", label_color=GREEN)
    c.box(520, 318, 380, 44, "dblwr 里的副本是完整的",
          "写数据文件之前就已经 fsync", accent=GREEN, size=12, sub_size=10)
    c.text(520, 392, "用副本整页覆盖，页结构恢复原状；", size=11, fill=SUB)
    c.text(520, 412, "再从这个页的 LSN 往后重放 redo。", size=11, fill=SUB)

    # ---- 下半：两段式写入
    c.container(40, 452, 880, 190, "正常刷脏的两段式写入：副本先落地，原位后写")

    c.box(60, 500, 240, 64, "① 写 dblwr 区", "连续追加，顺序 IO",
          accent=GREEN, size=13, sub_size=10)
    c.box(360, 500, 240, 64, "② fsync 副本", "副本没落盘就不往下走",
          accent=GREEN, size=13, sub_size=10)
    c.box(660, 500, 240, 64, "③ 写 .ibd 原位", "离散随机，失败也不致命",
          accent=BLUE, size=13, sub_size=10)

    c.arrow(300, 532, 360, 532, color=GREEN)
    c.arrow(600, 532, 660, 532, color=BLUE)

    c.text(60, 600, "恢复时先扫 dblwr：.ibd 里校验失败的页用副本整页覆盖，再交给 redo 前滚。",
           size=11, fill=INK)
    c.text(60, 622, "顺序反了就没意义 —— 副本还没持久化就写原位，崩溃后两份都是坏的。",
           size=10, fill=SUB)

    c.legend(60, 668, [(GREEN, "完整落盘", None),
                       (RED, "页损坏", None),
                       (BLUE, "随机写回原位", None)])
    return c.save(os.path.join(OUT, "ch07-fig1.svg"))


# ---------------------------------------------------------------- 图 7-2
def fig2():
    c = Canvas(960, 680,
               title="图 7-2　恢复三阶段在 LSN 轴上的位置",
               subtitle="分析决定从哪开始，重做把日志前滚到最新 LSN，回滚用 undo 把没提交的事务逆序撤销")

    c.container(40, 78, 880, 340, "三个阶段的起止点都落在 LSN 轴上")

    # ① 分析
    c.rect(180, 116, 620, 34, fill=TINT[BLUE], stroke=BORDER[BLUE], sw=1.2, r=6)
    c.text(196, 138, "① 分析：从 checkpoint 扫到日志尾，重建脏页表与活跃事务表",
           size=12, fill=INK)

    # ② 重做
    c.rect(320, 172, 480, 34, fill=TINT[PURPLE], stroke=BORDER[PURPLE], sw=1.2, r=6)
    c.text(336, 194, "② 重做：从最老脏页 LSN 前滚到日志尾，按 page LSN 幂等",
           size=12, fill=INK)

    # ③ 回滚
    c.rect(320, 228, 480, 34, fill=TINT[ORANGE], stroke=BORDER[ORANGE], sw=1.2, r=6)
    c.text(336, 250, "③ 回滚：用 undo 逆序撤销未提交事务", size=12, fill=INK)
    c.arrow(790, 276, 340, 276, color=ORANGE, width=1.4,
            label="undo 逆序回放，LSN 本身不回退", label_dy=18)

    # LSN 轴
    c.arrow(80, 320, 890, 320, color=SLATE, width=1.5)
    c.text(884, 302, "LSN 单调递增 →", size=10, anchor="end", fill=SUB)

    ticks = [(180, GREEN, "checkpoint", "分析起点"),
             (320, ORANGE, "最老脏页 LSN", "重做起点"),
             (800, SLATE, "日志尾（最新 LSN）", "前滚终点")]
    for x, col, name, note in ticks:
        c.raw(f'<line x1="{x}" y1="310" x2="{x}" y2="330" stroke="{col}" '
              f'stroke-width="1.5"/>')
        c.raw(f'<circle cx="{x}" cy="320" r="5.5" fill="#ffffff" '
              f'stroke="{col}" stroke-width="2.5"/>')
        c.text(x, 350, name, size=11, anchor="middle", fill=col, weight=600)
        c.text(x, 368, note, size=10, anchor="middle", fill=SUB)

    # 三者分工
    c.container(40, 440, 880, 130, "三者分工：页完整 / 改动不丢 / 没提交的不算")
    c.box(60, 486, 250, 64, "doublewrite", "保证「页是完整的」",
          accent=GREEN, size=13, sub_size=11)
    c.box(355, 486, 250, 64, "redo log", "保证「修改不丢」",
          accent=PURPLE, size=13, sub_size=11)
    c.box(650, 486, 250, 64, "undo log", "保证「没提交的不算」",
          accent=ORANGE, size=13, sub_size=11)

    c.legend(60, 592, [(BLUE, "分析", None),
                       (PURPLE, "重做（前滚）", None),
                       (ORANGE, "回滚（undo 逆序）", None),
                       (GREEN, "页的完整性", None)])
    return c.save(os.path.join(OUT, "ch07-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
