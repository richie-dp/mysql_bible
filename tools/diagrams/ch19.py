#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 19 章配图：加锁规则推演"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


def band(c, x1, x2, y, h, color, label=None, size=10):
    """加锁区间条：左端开（虚线短竖），右端闭（实线竖）"""
    c.rect(x1, y, x2 - x1, h, fill=color, stroke=color, sw=1, r=4, opacity=0.88)
    c.raw(f'<path d="M {x2} {y - 4} L {x2} {y + h + 4}" '
          f'stroke="{color}" stroke-width="2.4" stroke-linecap="round"/>')
    c.raw(f'<path d="M {x1} {y - 1} L {x1} {y + h + 1}" '
          f'stroke="{color}" stroke-width="1.2" stroke-dasharray="2,2"/>')
    if label:
        c.text((x1 + x2) / 2, y + h / 2 + 3.6, label, size=size,
               fill="#ffffff", anchor="middle", weight=600)


# ---------------------------------------------------------------- 图 19-1
def fig1():
    c = Canvas(960, 660,
               title="图 19-1　等值查询的三种加锁区间：命中 / 未命中 / 边界值",
               subtitle="表 t_lock：idx_c(c)，索引值 5 / 10 / 15 / 20 / 25 / 30；区间条左端开、右端闭")

    c.container(40, 96, 880, 104, "idx_c 叶子记录（按 c 升序；最左是 -∞ 侧，最右是 supremum）")
    xs = [140, 260, 380, 500, 620, 740]
    vals = [5, 10, 15, 20, 25, 30]
    ids = [1, 2, 3, 5, 6, 7]
    for x, v, i in zip(xs, vals, ids):
        c.box(x - 38, 126, 76, 52, f"c={v}", f"id={i}", accent=SLATE,
              size=12, sub_size=10)
    c.box(822, 126, 76, 52, "supremum", "伪记录", accent=SLATE,
          size=10, sub_size=9)

    # ① 命中
    c.text(46, 236, "① WHERE c = 15　命中", size=12, weight=600, fill=RED)
    band(c, 262, 380, 246, 14, GREEN, "(10,15]")
    band(c, 380, 500, 246, 14, RED, "(15,20)")
    c.text(102, 282, "引擎读到 15 后还要读 20 确认没有重复，于是锁住两段：记录 15 + 它右边的间隙；"
                     "回表后 PRIMARY 上再加一条 X,REC_NOT_GAP。", size=11, fill=SUB)

    # ② 未命中
    c.text(46, 326, "② WHERE c = 12　未命中（值域中间）", size=12, weight=600, fill=RED)
    band(c, 262, 380, 336, 14, RED, "(10,15)")
    c.text(102, 372, "没有记录可锁，只剩间隙；LOCK_DATA 记的是间隙右边那条记录 15，"
                     "而不是 12 —— 12 在索引里根本不存在。", size=11, fill=SUB)

    # ③ 边界值
    c.text(46, 416, "③ WHERE c = 30　命中最大值（边界）", size=12, weight=600, fill=RED)
    band(c, 622, 740, 426, 14, GREEN, "(25,30]")
    band(c, 740, 860, 426, 14, RED, "(30,+∞)")
    c.text(102, 462, "右侧邻居不是记录而是 supremum，LOCK_DATA 写成 supremum pseudo-record；"
                     "这一段正是新值插入的落点，冲突概率最高。", size=11, fill=SUB)

    c.legend(102, 492, [(RED, "间隙锁（不可插入）", None),
                        (GREEN, "临键锁里的记录部分", None)])

    c.container(40, 548, 880, 92, "把三种情况并起来看")
    c.text(60, 588, "区间条的空隙 = 还能插入的位置；锁住一段间隙，等于封死这段范围内的所有 INSERT。",
           size=11, fill=INK)
    c.text(60, 610, "等值查询的右边界永远是“第一条不相等（或 supremum）的记录”，所以命中时必然多锁一段。",
           size=11, fill=RED)
    c.text(60, 630, "唯一索引等值命中才例外：唯一性让它不必向右确认，临键锁退化成记录锁。",
           size=11, fill=GREEN)
    return c.save(os.path.join(OUT, "ch19-fig1.svg"))


# ---------------------------------------------------------------- 图 19-2
def fig2():
    c = Canvas(960, 640,
               title="图 19-2　非唯一索引等值命中：为什么是“记录 + 后面的间隙”",
               subtitle="WHERE c = 15；idx_c 的一个索引项 = (c, id)，锁在索引项上，不是锁在行上")

    c.container(40, 90, 880, 210, "① idx_c 叶子：找到 15 之后必须再读一条 20，才能确定没有第二个 15")
    for x, v, i in ((90, 10, 2), (330, 15, 3), (570, 20, 5)):
        accent = RED if v == 15 else SLATE
        c.box(x, 140, 130, 60, f"c={v}", f"id={i}", accent=accent)
    band(c, 155, 395, 226, 14, GREEN, "(10,15]")
    band(c, 395, 635, 226, 14, RED, "(15,20)")
    c.text(120, 262, "临键锁：间隙 + 记录", size=10, fill=GREEN)
    c.text(455, 262, "间隙锁：只锁空隙", size=10, fill=RED)

    # 回表
    c.arrow((395, 202), (395, 388), color=ORANGE, width=2.2,
            label="回表 → 锁行", label_dy=-6, label_at=0.42)
    c.text(410, 322, "X,REC_NOT_GAP", size=10, fill=ORANGE, mono=True)

    c.container(40, 330, 880, 150, "")
    for x, i in ((90, 2), (330, 3), (570, 5)):
        accent = RED if i == 3 else SLATE
        c.box(x, 392, 130, 60, f"id={i}", "整行数据", accent=accent, size=13)
    c.text(60, 474, "② PRIMARY：只有被命中的那一行才回表，未命中的 20 不产生 PK 锁",
           size=12, fill=SUB)

    c.mono_box(40, 500, 880, 116, [
        "INDEX_NAME  LOCK_MODE        LOCK_STATUS  LOCK_DATA",
        "idx_c       X               GRANTED      15, 3      <- 临键锁 (10,15]",
        "idx_c       X,GAP           GRANTED      20, 5      <- 间隙锁 (15,20)",
        "PRIMARY     X,REC_NOT_GAP   GRANTED      3          <- 回表锁住命中的行",
    ], title="performance_schema.data_locks（输出形态，未实跑）")
    return c.save(os.path.join(OUT, "ch19-fig2.svg"))


# ---------------------------------------------------------------- 图 19-3
def fig3():
    c = Canvas(960, 620,
               title="图 19-3　无索引 UPDATE：逐条临键锁 = 事实上的表锁",
               subtitle="同一张 6 行表，UPDATE t_lock SET pad='z' WHERE ...，RR 隔离级别")

    c.container(40, 92, 880, 206, "① WHERE pad = 'x'（pad 无索引）：聚簇索引从头扫到尾")
    xs = [60, 210, 360, 510, 660, 810]
    labels = [("id=1", ""), ("id=2", ""), ("id=3", ""), ("id=5", ""), ("id=6", ""),
              ("supremum", "伪记录")]
    for x, (t, s) in zip(xs, labels):
        if s:
            c.box(x, 140, 110, 56, t, s, accent=RED, size=10, sub_size=9)
        else:
            c.box(x, 140, 110, 56, t, accent=RED, size=12)
    band(c, 60, 920, 208, 14, RED, "(-∞,1] (1,2] (2,3] (3,5] (5,6] (6,supremum]")
    c.text(60, 252, "6 条记录 + supremum 全部加锁：data_locks 里 7 条 RECORD/X。"
                    "LOCK_TYPE 仍是 RECORD，效果却等价于表锁。", size=11, fill=RED)
    c.text(60, 274, "加锁发生在读取路径上：引擎读一条、加一条，它不知道 WHERE 最终会留下谁。",
           size=11, fill=SUB)

    c.container(40, 320, 880, 190, "② WHERE id = 3（主键）：一次定位，退化成记录锁")
    for x, (t, s) in zip(xs, labels):
        if s:
            c.box(x, 368, 110, 56, t, s, accent=SLATE, size=10, sub_size=9)
        elif t == "id=3":
            c.box(x, 368, 110, 56, t, accent=GREEN, size=12)
        else:
            c.box(x, 368, 110, 56, t, accent=SLATE, size=12)
    band(c, 360, 470, 436, 12, GREEN, "(2,3]")
    c.text(60, 474, "只锁 3 这一条，左右两侧的间隙都能继续插入。差的不是“用了索引”，"
                    "差的是“只访问了一条记录”。", size=11, fill=GREEN)

    c.text(40, 552, "锁的规模由访问到的记录条数决定：访问 1 条 = 1 把锁，访问全表 = 全表锁 + supremum。",
           size=12, fill=INK, weight=600)
    c.text(40, 578, "所以“没有索引就不加锁”是反的：没有索引不是不锁，是锁得最狠。", size=12, fill=RED)
    return c.save(os.path.join(OUT, "ch19-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
