#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 15 章配图：查询改写实战"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *  # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 15-1
def fig1():
    c = Canvas(960, 540, title="图 15-1　深分页：原写法与三条解法的访问路径",
               subtitle="offset = 1,000,000、LIMIT 20；横条长度按行数对数刻度绘制")

    x0, maxw = 238, 330

    def width(n):
        return maxw * math.log10(max(n, 1)) / 6.0

    # 对数刻度网格（先画，压在条形下面）
    for n, lab in ((10 ** 3, "1e3"), (10 ** 4, "1e4"),
                   (10 ** 5, "1e5"), (10 ** 6, "1e6")):
        gx = x0 + width(n)
        c.raw(f'<line x1="{gx:.1f}" y1="98" x2="{gx:.1f}" y2="392" '
              f'stroke="#e5e7eb" stroke-width="1" stroke-dasharray="3,4"/>')
        c.text(gx, 90, lab, size=9, fill=SUB, anchor="middle")

    rows = [
        ("① 原写法（offset）", "LIMIT 1000000, 20",
         1000020, 1000020, "能跳页", GREEN),
        ("② 延迟关联", "JOIN (SELECT id … LIMIT)",
         1000020, 20, "能跳页", GREEN),
        ("③ 游标 seek", "WHERE id > ? ORDER BY id",
         20, 20, "不能跳页", RED),
        ("④ 覆盖索引 + 子查询", "两次查询，应用拼装 ID",
         1000020, 20, "能跳页", GREEN),
    ]

    for i, (title, sub, scan, back, jump, color) in enumerate(rows):
        y = 112 + i * 74
        c.text(60, y + 14, title, size=13, weight=600)
        c.text(60, y + 32, sub, size=10, fill=SUB)

        c.rect(x0, y, width(scan), 15, fill=BLUE, stroke=BLUE, sw=0, r=3)
        c.rect(x0, y + 21, width(back), 15, fill=ORANGE, stroke=ORANGE, sw=0, r=3)

        c.text(590, y + 12, f"索引 {scan:,} 行", size=10, fill=SUB)
        c.text(590, y + 33, f"回表 {back:,} 次", size=10, fill=SUB)
        c.pill(770, y + 5, 110, 28, jump, accent=color, size=11)

    c.legend(60, 416, [(BLUE, "索引扫描行数", None),
                       (ORANGE, "回表次数", None)])
    c.text(300, 426,
           "offset 越大，前两条越长；只有游标法不随页码增长。",
           size=11, fill=INK)
    c.text(60, 474,
           "延迟关联与“覆盖索引 + 子查询”仍然要扫 offset + limit 行索引，"
           "它们只是把回表压到 limit 次。",
           size=11, fill=SUB)
    return c.save(os.path.join(OUT, "ch15-fig1.svg"))


# ---------------------------------------------------------------- 图 15-2
def fig2():
    c = Canvas(960, 700, title="图 15-2　20 个改写案例的病灶决策树",
               subtitle="先按 EXPLAIN 的信号分四类，再回 15.1.8 查对应案例编号")

    # 根节点
    c.diamond(480, 100, 320, 56, "EXPLAIN 先看哪一列？", accent=SLATE, size=12)

    cols = [
        # (x, 前缀色, 标题, 信号, 叶子列表[(标题, 编号)])
        (60, ORANGE, "A　索引没用上", "type=ALL / key=NULL",
         [("函数 / 运算 / 转换", "案例 1 / 2 / 3"),
          ("OR / 前置通配", "案例 4 / 5")]),
        (285, BLUE, "B　扫得太多", "rows 远大于结果集",
         [("深分页：扫了不用的行", "案例 6 / 7"),
          ("SELECT * / 全表统计", "案例 8 / 9"),
          ("大 IN / JOIN 放大", "案例 10 / 11"),
          ("子查询逐行 / 反连接", "案例 12 / 13")]),
        (510, PURPLE, "C　排了不该排的", "filesort / temporary",
         [("RAND / LIMIT 选错索引", "案例 14 / 17"),
          ("GROUP BY / UNION 去重", "案例 15 / 16")]),
        (735, RED, "D　锁得太久", "Waiting for lock",
         [("批量 DML / 幂等写入", "案例 18 / 19 / 20")]),
    ]

    for x, color, title, signal, leaves in cols:
        c.container(x, 150, 185, 500, "")
        c.box(x + 10, 162, 165, 54, title, signal, accent=color,
              size=12, sub_size=9)

        for j, (leaf, cases) in enumerate(leaves):
            y = 258 + j * 76
            c.box(x + 10, y, 165, 56, leaf, cases, accent=color,
                  size=11, sub_size=10)

    # 根到四个分支
    for x in (60, 285, 510, 735):
        c.arrow((480, 128), (x + 92, 162), color=SLATE, width=1.4)

    # D 列留白处的说明（写路径没有单独的“慢”）
    c.text(745, 380, "写路径的慢，", size=10, fill=SUB)
    c.text(745, 398, "在 processlist 里", size=10, fill=SUB)
    c.text(745, 416, "是 Waiting for lock", size=10, fill=SUB)
    c.text(745, 434, "或 metadata lock。", size=10, fill=SUB)

    c.text(60, 676,
           "四类病灶各自对应一种改法：补索引 / 减行数 / 去排序 / 缩事务。"
           "一条 SQL 可以同时命中两类，但一次只能治一类。",
           size=11, fill=SUB)
    return c.save(os.path.join(OUT, "ch15-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
