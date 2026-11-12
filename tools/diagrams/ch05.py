#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 5 章配图：Undo Log、版本链与 Purge"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 5-1
def fig1():
    c = Canvas(960, 580,
               title="图 5-1　一行记录的版本链：当前行 → undo v2 → v1 → v0",
               subtitle="DB_ROLL_PTR 指向 undo 页里的物理位置；undo 只存被改列的前镜像，旧版本是「走一步、拼一次」拼出来的")

    # ---- 数据页里的当前版本
    c.container(40, 84, 880, 116,
                "聚簇索引页 page 3 · 当前版本（磁盘上唯一真实存在的行）")

    cells = [
        (60, 110, "id", "8801"),
        (200, 140, "status", "'已发货'"),
        (370, 140, "amount", "268.00"),
        (540, 140, "DB_TRX_ID", "912"),
        (710, 190, "DB_ROLL_PTR", "rseg 7 / page 5 / off 112"),
    ]
    for x, w, t, s in cells:
        accent = ORANGE if t.startswith("DB_") else BLUE
        c.box(x, 112, w, 64, t, s, accent=accent, size=12, sub_size=10)

    # ---- 指针下探
    c.arrow((805, 176), (805, 298), color=SLATE, dash="5,4",
            label="roll_ptr", label_side="left")

    # ---- undo 表空间里的历史版本
    c.container(40, 250, 880, 190,
                "undo 表空间 undo_001 · 同一行的历史版本（全部是 update undo）")

    cards = [
        (56, "undo 记录 v0", "trx 901 · 链的末端", "roll_ptr = NULL"),
        (356, "undo 记录 v1", "trx 903 · amount 前镜像", "roll_ptr → v0"),
        (656, "undo 记录 v2", "trx 905 · status 前镜像", "roll_ptr → v1"),
    ]
    for x, t, s, ptr in cards:
        c.box(x, 300, 250, 96, t, s, accent=ORANGE, size=12, sub_size=10)
        c.text(x + 125, 383, ptr, size=10, fill=ORANGE, anchor="middle", mono=True)

    c.arrow((656, 348), (606, 348), color=ORANGE, label="回溯")
    c.arrow((356, 348), (306, 348), color=ORANGE, label="回溯")

    c.text(56, 424,
           "记录头里的 trx_id 决定「这个版本能不能给我看」，记录体的前镜像决定「拼出来的旧值是多少」",
           size=11, fill=SUB)

    # ---- 结论行
    c.text(40, 472,
           "链长 = 这行被改过多少次且还没被 purge；走 N 步才能读到第 N 个旧版本——长事务拖慢查询，物理上就是这么发生的。",
           size=12, fill=INK)

    c.legend(60, 508, [(ORANGE, "update undo 记录", None),
                       (BLUE, "当前版本（数据页）", None),
                       (SLATE, "DB_ROLL_PTR 指针", "5,4")])
    return c.save(os.path.join(OUT, "ch05-fig1.svg"))


# ---------------------------------------------------------------- 图 5-2
def fig2():
    c = Canvas(960, 620,
               title="图 5-2　history list 与 purge 边界：谁挡住了回收",
               subtitle="purge 只认最老的那个 ReadView；一个两小时前的只读快照，就能让上千万条 undo 原地罚站")

    c.box(48, 84, 340, 52, "ReadView A：财务报表事务，开了 2 小时",
          "up_limit_id = 903 —— 最老的那个", accent=RED, size=12, sub_size=10)
    c.box(480, 84, 380, 52, "ReadView B：刚刚开始的普通查询",
          "up_limit_id = 906 —— 更年轻，不决定水位", accent=SLATE, size=12, sub_size=10)

    # 水位线：从 A 折下来，穿过 history list
    c.arrow([(218, 136), (218, 152), (331, 152), (331, 302)], color=RED,
            dash="5,4", end=False, label="水位", label_side="left")

    # ---- history list
    c.container(40, 176, 880, 164, "history list（左老右新）")

    c.rect(52, 214, 264, 86, fill=TINT[GREEN], stroke=BORDER[GREEN],
           sw=1.2, r=8, dash="4,3")
    c.rect(344, 214, 558, 86, fill=TINT[RED], stroke=BORDER[RED],
           sw=1.2, r=8, dash="4,3")

    xs = [60, 206, 352, 498, 644, 790]
    for i, x in enumerate(xs):
        c.box(x, 224, 104, 64, "#%d" % (i + 1), "trx %d" % (901 + i),
              accent=ORANGE, size=13, sub_size=10)

    c.text(184, 314, "可回收（trx < 903）", size=11, fill=GREEN, anchor="middle")
    c.text(623, 314, "不可回收：还有人在读", size=11, fill=RED, anchor="middle")

    # ---- 状态输出
    c.mono_box(60, 356, 420, 120, [
        "------------",
        "TRANSACTIONS",
        "------------",
        "History list length  41283902",
        "Purge done for trx's n:o < 4211003",
    ], title="SHOW ENGINE INNODB STATUS")

    c.text(520, 370, "八位数 = 上千万条 undo 在等一个读者", size=11, fill=INK)
    c.text(520, 396, "purge 一直在跑，只是水位一步没动", size=11, fill=INK)
    c.text(520, 422, "同一个回滚段只能串行清，加线程也没用", size=11, fill=INK)
    c.text(520, 448, "积压按小时计才能清完，不会因为停止写入归零", size=11, fill=INK)

    c.text(60, 504,
           "水位由「最老的读者」决定，不由「最新的写入」决定——这是本章唯一需要背下来的因果。",
           size=12, fill=INK)

    c.legend(60, 532, [(ORANGE, "update undo 记录", None),
                       (GREEN, "可被 purge 回收", None),
                       (RED, "被最老视图钉住", None)])
    return c.save(os.path.join(OUT, "ch05-fig2.svg"))


# ---------------------------------------------------------------- 图 5-3
def fig3():
    c = Canvas(960, 640,
               title="图 5-3　insert undo 与 update undo：同一个提交动作，两种归宿",
               subtitle="提交只结束「回滚」这个用途；「让别人看见旧版本」这个用途，要等到没有读者为止")

    # ---- INSERT
    c.container(40, 84, 880, 120, "INSERT —— 回滚需要它，读的人不需要它")
    c.box(60, 124, 190, 56, "INSERT 一行", "新记录只对本事务可见",
          accent=BLUE, size=12, sub_size=10)
    c.box(290, 124, 190, 56, "insert undo", "只存前镜像，不进版本链",
          accent=ORANGE, size=12, sub_size=10)
    c.box(520, 124, 190, 56, "COMMIT", "回滚用途到此为止",
          accent=BLUE, size=12, sub_size=10)
    c.box(750, 124, 160, 56, "立即丢弃", "undo slot 马上复用",
          accent=GREEN, size=12, sub_size=10)

    c.arrow(250, 152, 290, 152, color=BLUE)
    c.arrow(480, 152, 520, 152, color=BLUE)
    c.arrow(710, 152, 750, 152, color=GREEN)

    # ---- UPDATE / DELETE
    c.container(40, 250, 880, 130, "UPDATE / DELETE —— 提交之后还得留着，因为别人还要看")
    c.box(60, 292, 190, 56, "UPDATE 一行", "旧值被替换掉",
          accent=BLUE, size=12, sub_size=10)
    c.box(290, 292, 190, 56, "update undo", "前镜像 + 列位图 + trx_id",
          accent=ORANGE, size=12, sub_size=10)
    c.box(520, 292, 190, 56, "COMMIT 进 history list", "不能丢，读者可能还要",
          accent=ORANGE, size=12, sub_size=10)
    c.box(750, 292, 160, 56, "purge 才释放", "边界见 5.6",
          accent=GREEN, size=12, sub_size=10)

    c.arrow(250, 320, 290, 320, color=BLUE)
    c.arrow(480, 320, 520, 320, color=ORANGE)
    c.arrow(710, 320, 750, 320, color=RED)

    # ---- DELETE 的 delete-mark
    c.container(40, 410, 880, 120, "DELETE 走的是 update undo，动的是删除位")
    c.box(60, 450, 230, 56, "DELETE 一行", "不移动记录、不改数据",
          accent=BLUE, size=12, sub_size=10)
    c.box(330, 450, 250, 56, "打 delete-mark", "info_bits 置删除位，行仍在各索引里",
          accent=ORANGE, size=12, sub_size=10)
    c.box(620, 450, 260, 56, "purge 才物理删除", "先每个二级索引，再聚簇索引",
          accent=GREEN, size=12, sub_size=10)

    c.arrow(290, 478, 330, 478, color=ORANGE)
    c.arrow(580, 478, 620, 478, color=GREEN)

    c.legend(60, 550, [(BLUE, "正常流转", None),
                       (ORANGE, "undo 的生命周期", None),
                       (GREEN, "空间真正释放", None),
                       (RED, "被读者挡住", None)])
    return c.save(os.path.join(OUT, "ch05-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
