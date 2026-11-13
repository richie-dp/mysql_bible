#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 30 章配图：主键、唯一 ID 与自增"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 30-1
def fig1():
    c = Canvas(960, 560,
               title="图 30-1　自增号的消耗账：连续的从来不是号，是「已提交的行」",
               subtitle="示意：橙色为已分配但没落行的号，比例做了夸张；⑤ 不是浪费，是把旧号重发一遍")

    # 五个原因的标签条
    pills = [
        ("① 批量预分配 ×3", ORANGE),
        ("② ODKU 冲突 ×2", ORANGE),
        ("③ REPLACE ×1", ORANGE),
        ("④ 事务回滚 ×1", ORANGE),
        ("⑤ [5.7] 重启回退", RED),
    ]
    for i, (label, color) in enumerate(pills):
        c.pill(44 + i * 176, 82, 168, 32, label, accent=color, size=11)

    # 图例（横排）
    for x, color, label in ((44, GREEN, "已提交（有行）"),
                            (232, ORANGE, "已消耗（无行）"),
                            (420, RED, "回退后重发")):
        c.rect(x, 138, 13, 13, fill=TINT[color], stroke=BORDER[color], sw=1.2, r=3)
        c.text(x + 20, 150, label, size=11, fill=SUB)

    # 序号轴
    seq = [
        ("101", GREEN, "已提交"), ("102", GREEN, "已提交"),
        ("103", ORANGE, "④×1"), ("104", ORANGE, "②×1"),
        ("105", ORANGE, "②×1"), ("106", GREEN, "已提交"),
        ("107", ORANGE, "③×1"), ("108", GREEN, "已提交"),
        ("109", ORANGE, "①×1"), ("110", ORANGE, "①×1"),
        ("111", ORANGE, "①×1"), ("112", GREEN, "已提交"),
        ("113", GREEN, "已提交"), ("114", GREEN, "已提交"),
    ]
    x0, step, w = 61, 60, 58
    for i, (num, color, tag) in enumerate(seq):
        c.box(x0 + i * step, 176, w, 62, num, tag, accent=color,
              size=13, sub_size=9, r=6)

    # ⑤ 回退箭头：从右往左，指向已被消耗的区间
    c.arrow((906, 268), (452, 268), color=RED, dash="6,4", width=1.8,
            label="⑤ [5.7] 重启后取 MAX(id)+1，已删除的号会被重发", label_dy=-9)

    # 底部说明
    c.container(40, 292, 880, 244, "五个来源，各给一个能复现的动作")
    lines = [
        ("① 批量插入：INSERT ... SELECT / LOAD DATA 拿不到准确行数，mode=2 按倍增的预估值领一段号，领多了直接丢弃。", ORANGE),
        ("② INSERT ... ON DUPLICATE KEY UPDATE：先取号，再判唯一键；冲突时号已经消耗，改走 UPDATE。", ORANGE),
        ("③ REPLACE INTO：本质是 DELETE + INSERT；被删的行不还号，新行再领一个。", ORANGE),
        ("④ 事务回滚：计数器不在事务里，ROLLBACK 只回滚行，不回滚号。", ORANGE),
        ("⑤ 重启：[5.7] 计数器不持久化，取 MAX(id)+1，可能重发已删除的号；[8.0] 计数器进 redo，只前进不回退。", RED),
    ]
    y = 332
    for text, color in lines:
        c.text(60, y, text, size=12, fill=color)
        y += 30
    c.text(60, 496, "自增只保证单调递增，不保证连续。把 id 当业务单号展示，等于把「发号策略」写进了对外契约。",
           size=12, fill=INK, weight=600)
    return c.save(os.path.join(OUT, "ch30-fig1.svg"))


# ---------------------------------------------------------------- 图 30-2
def fig2():
    c = Canvas(960, 590,
               title="图 30-2　五种分布式 ID 方案：四个维度，没有全优解",
               subtitle="绿=优　橙=有代价　红=存在硬伤　灰=取决于实现")

    cols = ["单调性", "长度", "时钟依赖", "分片友好度"]
    col_x = [224, 398, 572, 746]
    col_w = 170

    c.box(40, 96, 180, 40, "方案", accent=SLATE, size=13, r=6)
    for i, name in enumerate(cols):
        c.box(col_x[i], 96, col_w, 40, name, accent=SLATE, size=12, r=6)

    rows = [
        ("号段模式", "Leaf / segment", [
            ("趋势递增", ORANGE), ("8B", GREEN), ("不依赖", GREEN), ("需 biz_tag", ORANGE)]),
        ("雪花算法", "Snowflake", [
            ("单机单调", GREEN), ("8B", GREEN), ("强依赖", RED), ("位内嵌", GREEN)]),
        ("UUIDv7", "RFC 9562", [
            ("近似有序", ORANGE), ("16B", ORANGE), ("弱依赖", ORANGE), ("前缀可路由", GREEN)]),
        ("UUIDv4", "纯随机", [
            ("完全随机", RED), ("16B", ORANGE), ("不依赖", GREEN), ("需映射表", RED)]),
        ("Redis INCR", "单点自增", [
            ("严格递增", GREEN), ("8B", GREEN), ("不依赖", GREEN), ("单点写", RED)]),
    ]
    y = 140
    for name, sub, cells in rows:
        c.box(40, y, 180, 52, name, sub, accent=BLUE, size=13, sub_size=10, r=6)
        for i, (text, color) in enumerate(cells):
            c.box(col_x[i], y, col_w, 52, text, accent=color, size=12, r=6)
        y += 56

    # 图例
    for x, color, label in ((40, GREEN, "优"), (128, ORANGE, "有代价"), (268, RED, "硬伤")):
        c.rect(x, 424, 13, 13, fill=TINT[color], stroke=BORDER[color], sw=1.2, r=3)
        c.text(x + 20, 436, label, size=11, fill=SUB)

    c.container(40, 452, 880, 110, "读法：四个维度问的是四件事")
    c.text(60, 490, "单调性决定写入落点与能否排序；时钟依赖决定机房断电重启后还能不能继续发号。", size=12, fill=INK)
    c.text(60, 514, "号段与 Redis 把唯一性押在中心存储，雪花押在机器 ID 分配，UUID 押在随机数的概率上。", size=12, fill=INK)
    c.text(60, 538, "分片友好度问的是：只拿到 ID，能不能算出它属于哪个分片？算不出，就得再维护一张映射表。", size=12, fill=INK)
    return c.save(os.path.join(OUT, "ch30-fig2.svg"))


# ---------------------------------------------------------------- 图 30-3
def fig3():
    c = Canvas(960, 600,
               title="图 30-3　写入落点：自增打尾页、雪花打时间窗、UUID 打散全树",
               subtitle="每条横条是一个叶子页；箭头是一次插入的落点，越红表示并发争用越强")

    panels = [
        (40, "① 自增主键：写永远落在最后一页", "右分裂只劈一页，代价是同一页的 latch 排队",
         [("94%", GREEN), ("94%", GREEN), ("94%", GREEN), ("94%", GREEN), ("latch 争用", RED)]),
        (348, "② 雪花 / UUIDv7：落在当前时间窗", "窗口内的页仍被并发写，窗口随分片键散开",
         [("94%", GREEN), ("94%", GREEN), ("窗口内", PURPLE), ("窗口边缘", PURPLE), ("94%", GREEN)]),
        (656, "③ UUIDv4：落点随机", "无热点，但每次插入都可能换进一个冷页",
         [("50%", ORANGE), ("50%", ORANGE), ("50%", ORANGE), ("50%", ORANGE), ("50%", ORANGE)]),
    ]

    for px, title, caption, cells in panels:
        c.container(px, 92, 264, 396, title, label_color=SLATE)
        for i, (sub, accent) in enumerate(cells):
            c.box(px + 88, 140 + i * 60, 164, 54, f"叶子页 {i + 1}", sub,
                  accent=accent, size=11, sub_size=10, r=6)
        c.text(px + 14, 468, caption, size=10, fill=SUB)

    # ① 三条并发插入都指向最后一页
    last_y = 140 + 4 * 60 + 27
    for dy, width in ((-14, 1.4), (0, 2.6), (14, 1.4)):
        c.arrow((54, last_y + dy), (126, last_y + dy), color=RED, width=width)

    # ② 落到当前时间窗（第 3、4 页）
    c.arrow((362, 140 + 2 * 60 + 27), (434, 140 + 2 * 60 + 27), color=PURPLE, width=2.4)
    c.arrow((362, 140 + 3 * 60 + 27), (434, 140 + 3 * 60 + 27), color=PURPLE,
            width=1.6, dash="5,3")

    # ③ 五条随机落点
    for i in range(5):
        yy = 140 + i * 60 + 27
        c.arrow((670, yy), (742, yy), color=SLATE, width=1.3, dash="4,3")

    c.text(40, 518, "① 自增的瓶颈不是页分裂：右分裂只影响最后一页，真正的排队点是这页的页 latch 与 index->lock 的 SX 争用。",
           size=12, fill=RED)
    c.text(40, 544, "② 雪花按时间单调，落点同样集中在「当前毫秒」那一段键；序列位用完要等下一毫秒，等于把一个微秒级的锁换成时钟。",
           size=12, fill=ORANGE)
    c.text(40, 570, "③ UUID 把写摊到全树：没有热点，但每插一行都可能把冷页读进 Buffer Pool，把热页挤出去。",
           size=12, fill=SLATE)
    return c.save(os.path.join(OUT, "ch30-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
