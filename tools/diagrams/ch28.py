#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 28 章配图：XtraBackup prepare 两阶段 / PITR 时间轴 / 四种单表恢复"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 28-1
def fig1():
    c = Canvas(960, 730,
               title="图 28-1　XtraBackup：拷页 + 拷 redo，prepare 要跑两遍恢复",
               subtitle="拷页只保证「每个页是某一时刻的完整版本」；页与页之间的 LSN 差，靠 redo 前滚补齐，靠 undo 撤掉未提交")

    c.container(40, 76, 880, 344, "三个动作，一条时间线：备份集从「能拷」变成「能起」")

    # 列分隔
    for x in (380, 680):
        c.raw(f'<line x1="{x}" y1="112" x2="{x}" y2="406" stroke="#e5e7eb" '
              f'stroke-width="1.2" stroke-dasharray="4,5"/>')

    c.text(60, 126, "① 备份期间：页在变，redo 在记", size=12, fill=BLUE, weight=600)
    c.text(400, 126, "② 前滚：把所有页拉到同一 LSN", size=12, fill=PURPLE, weight=600)
    c.text(700, 126, "③ 回滚：撤掉未提交的事务", size=12, fill=ORANGE, weight=600)

    # ---- 左
    c.box(60, 146, 130, 50, "拷 .ibd 页", "拷的瞬间各不相同",
          accent=BLUE, size=12, sub_size=10)
    c.box(210, 146, 130, 50, "拷 redo", "记录窗口内所有变更",
          accent=PURPLE, size=12, sub_size=10)
    c.box(60, 222, 280, 54, "每个页的 LSN 都不一样",
          "备份集不是一致快照", accent=RED, size=13, sub_size=10)
    c.arrow(125, 196, 125, 222, color=BLUE)
    c.arrow(275, 196, 275, 222, color=PURPLE)

    c.text(60, 302, "拷页与拷日志是两个线程，同时启动。", size=11, fill=SUB)
    c.text(60, 324, "页是快照的原材料，redo 是把它们", size=11, fill=SUB)
    c.text(60, 344, "焊死在同一时刻的焊条。", size=11, fill=SUB)
    c.text(60, 378, "此刻的备份集：能拷，不能起。", size=11, fill=RED, weight=600)

    # ---- 中
    c.text(400, 152, "页 LSN（备份集原样）", size=10, fill=SUB)
    xs = (400, 476, 552)
    for x, v in zip(xs, ("96", "100", "102")):
        c.box(x, 160, 64, 38, v, accent=BLUE, size=13)
        c.arrow(x + 32, 198, x + 32, 230, color=PURPLE)
    for x in xs:
        c.box(x, 230, 64, 38, "104", accent=GREEN, size=13)
    c.pill(400, 280, 216, 24, "所有页到达同一 LSN", accent=GREEN)

    c.text(400, 330, "redo 只做加法：每条记录按页头", size=11, fill=SUB)
    c.text(400, 350, "LSN 幂等，应用到 104 就停。", size=11, fill=SUB)
    c.text(400, 386, "等价于崩溃恢复的「重做」。", size=11, fill=SUB)

    # ---- 右
    c.box(700, 160, 180, 48, "undo 逆序回放", "未提交事务的修改",
          accent=ORANGE, size=12, sub_size=10)
    c.arrow(790, 208, 790, 238, color=ORANGE)
    c.box(700, 238, 180, 48, "这些行消失", "备份集 = 干净关闭",
          accent=GREEN, size=12, sub_size=10)

    c.text(700, 318, "回滚本身也写 redo，否则回滚到", size=11, fill=SUB)
    c.text(700, 338, "一半再崩，就永远回滚不完。", size=11, fill=SUB)
    c.text(700, 386, "等价于崩溃恢复的「回滚」。", size=11, fill=SUB)

    # ---- 底：跳过 prepare
    c.container(40, 440, 880, 190, "跳过 prepare，直接把备份集当 datadir 起", label_color=RED)
    c.mono_box(60, 482, 430, 132, [
        "[ERROR] [InnoDB] Database page corruption on disk",
        "or a failed file read of page [page id: space=42,",
        "page number=118].",
        "[ERROR] [InnoDB] You may have to recover from a backup.",
    ], title="error log（输出形态，未实跑）", size=10)

    c.text(520, 502, "页是一个完整的旧版本，但每页的旧版本", size=11, fill=INK)
    c.text(520, 524, "来自不同时刻；页头 LSN 与日志里的", size=11, fill=INK)
    c.text(520, 546, "checkpoint 对不上，前滚的起点就是错的。", size=11, fill=INK)
    c.text(520, 590, "不是备份坏了，是备份还没被恢复。", size=12, fill=RED, weight=600)

    c.legend(60, 640, [(BLUE, "拷页 / 前滚", None),
                       (PURPLE, "redo 日志流", None),
                       (ORANGE, "undo 回滚", None),
                       (GREEN, "一致状态", None)])
    return c.save(os.path.join(OUT, "ch28-fig1.svg"))


# ---------------------------------------------------------------- 图 28-2
def fig2():
    c = Canvas(960, 690,
               title="图 28-2　PITR 的时间轴：全备之后，binlog 必须连续",
               subtitle="恢复点在误操作前 1 秒；全备位点与 binlog 的衔接点差一个事务，后面全部错位")

    c.container(40, 84, 880, 330, "时间轴：全备 → binlog 连续区间 → 误操作 → 恢复点")

    # 全备节点
    c.box(60, 140, 150, 60, "全备结束", "to_lsn / GTID", accent=ORANGE,
          size=13, sub_size=10)

    # 轴与区间带
    c.arrow(210, 170, 860, 170, color=SLATE, width=1.5)
    c.rect(210, 186, 630, 26, fill=TINT[PURPLE], stroke=BORDER[PURPLE], sw=1.2, r=6)
    c.text(222, 204, "binlog 连续区间：差一个事务就接不上", size=11, fill=PURPLE)

    ticks = [(210, ORANGE), (620, GREEN), (700, RED), (840, SLATE)]
    for x, col in ticks:
        c.raw(f'<line x1="{x}" y1="170" x2="{x}" y2="186" stroke="{col}" stroke-width="1.6"/>')
        c.raw(f'<circle cx="{x}" cy="170" r="5.5" fill="#ffffff" '
              f'stroke="{col}" stroke-width="2.5"/>')

    # 轴上方的两个近点：错开排
    c.text(620, 134, "恢复点", size=10, anchor="middle", fill=SUB)
    c.text(620, 154, "t_bad − 1s", size=12, anchor="middle", fill=GREEN, weight=600)
    c.text(700, 134, "误操作 COMMIT", size=10, anchor="middle", fill=SUB)
    c.text(700, 154, "t_bad", size=12, anchor="middle", fill=RED, weight=600)

    # 轴下方标注
    c.text(210, 244, "t0 全备结束", size=11, anchor="middle", fill=ORANGE, weight=600)
    c.text(210, 264, "位点 = 某个 end_log_pos", size=10, anchor="middle", fill=SUB)
    c.text(700, 244, "20:41:07 DELETE", size=10, anchor="middle", fill=RED, weight=600)
    c.text(840, 244, "binlog 尾", size=10, anchor="middle", fill=SUB)

    # 恢复动作
    c.box(520, 296, 200, 56, "恢复到临时实例", "stop-position = t_bad − 1s",
          accent=GREEN, size=12, sub_size=9)
    c.arrow(620, 296, 620, 214, color=GREEN, width=1.4)

    c.text(60, 320, "原实例不动，binlog 继续写；", size=11, fill=SUB)
    c.text(60, 342, "恢复产物落在一个新的 datadir 上，", size=11, fill=SUB)
    c.text(60, 364, "校验通过再切回。", size=11, fill=SUB)

    # 底部：三种坏法
    c.container(40, 440, 880, 120, "衔接点出问题，只有这三种结局", label_color=RED)
    items = [(60, "① 备份位点已被 purge", "链断在第一步", RED),
             (353, "② 用时间当刀口", "多恢复或少恢复", ORANGE),
             (646, "③ 只恢复全备", "备份之后的写入全丢", RED)]
    for x, t, s, col in items:
        c.box(x, 482, 253, 56, t, s, accent=col, size=12, sub_size=10)

    c.legend(60, 600, [(ORANGE, "全备节点", None),
                       (PURPLE, "binlog 区间", None),
                       (GREEN, "恢复点", None),
                       (RED, "误操作 / 断链", None)])
    return c.save(os.path.join(OUT, "ch28-fig2.svg"))


# ---------------------------------------------------------------- 图 28-3
def fig3():
    c = Canvas(960, 600,
               title="图 28-3　四种单表恢复：按耗时从短到长排，代价同时上升",
               subtitle="同一张表的四种拿法：数字是量级不是实测值；越往右适用面越广、代价越高")

    cards = [
        ("① 表空间导入", "分钟级", "中 · 前提苛刻", "单表 / 结构未变",
         ["同版本", "同页大小", "表结构一致", "无外键", "需 .cfg 文件"], BLUE, ORANGE),
        ("② 闪回工具", "分钟级", "高 · 需人工审核", "误 DELETE / UPDATE",
         ["row_image=FULL", "有主键", "期间无 DDL", "后续无并发改"], ORANGE, RED),
        ("③ 逻辑过滤重放", "十分钟级", "低", "只要一张小表",
         ["binlog 可读", "或 dump 含表段", "表不能太大"], PURPLE, GREEN),
        ("④ 临时实例导回", "小时级", "最低", "任意场景",
         ["有临时实例", "网络带宽", "磁盘空间", "数据量决定耗时"], GREEN, GREEN),
    ]

    for i, (name, cost, risk, scope, prereq, col, rcol) in enumerate(cards):
        x = 40 + i * 230
        c.container(x, 96, 190, 324, "")
        c.box(x + 10, 106, 170, 54, name, cost, accent=col, size=13, sub_size=10)

        c.text(x + 14, 190, "耗时", size=10, fill=SUB)
        c.text(x + 56, 190, cost, size=11, fill=INK, weight=600)
        c.text(x + 14, 214, "风险", size=10, fill=SUB)
        c.text(x + 56, 214, risk, size=10, fill=rcol, weight=600)
        c.text(x + 14, 238, "适用", size=10, fill=SUB)
        c.text(x + 56, 238, scope, size=10, fill=INK)

        c.rect(x + 10, 256, 170, 144, fill=FAINT, stroke="#e5e7eb", sw=1, r=6)
        c.text(x + 20, 276, "前提", size=10, fill=SUB, weight=600)
        yy = 298
        for ln in prereq:
            c.text(x + 20, yy, ln, size=10, fill=INK)
            yy += 22

    c.container(40, 476, 880, 84, "选择顺序")
    c.text(60, 516, "表还在 → 补行（② / ③）；表没了 → 整表替换（① / ④）；拿不准或要留证据 → ④。",
           size=12, fill=INK, weight=600)
    c.text(60, 540, "共同前提：误操作之后这些行不能被再写，否则任何补数都会和现状打架。",
           size=11, fill=SUB)

    return c.save(os.path.join(OUT, "ch28-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
