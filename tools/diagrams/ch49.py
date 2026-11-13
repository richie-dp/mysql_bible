#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 49 章配图：交易与库存的业务模型"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 49-1
def fig1():
    c = Canvas(960, 700,
               title="图 49-1　订单三张表与主表状态机",
               subtitle="拆表的判据是生命周期与访问频率；状态机的判据是能否单向收敛")

    # ---- 左：三张表
    c.container(60, 84, 400, 470, "三张表：行数从千万到十亿，行宽差一个数量级")
    c.box(80, 120, 360, 96, "order_main　订单主表",
          "3.2 亿行，日增 78 万", accent=BLUE, size=13, sub_size=10.5)
    c.box(80, 246, 360, 96, "order_item　订单明细",
          "9 亿行，1 单 1~20 行，存下单快照", accent=BLUE, size=13, sub_size=10.5)
    c.box(80, 372, 360, 96, "order_ext　订单扩展",
          "约 5% 的订单有行，只有详情页读", accent=SLATE, size=13, sub_size=10.5)

    c.arrow((150, 216), (150, 246), color=BLUE)
    c.arrow((150, 342), (150, 372), color=SLATE)
    c.text(160, 238, "1 : N", size=10, fill=SUB)
    c.text(160, 364, "1 : 0..1", size=10, fill=SUB)

    c.text(84, 496, "主表约 350 字节/行，一页放得下四十多行", size=10.5, fill=SUB)
    c.text(84, 518, "多一列 VARCHAR(200)，3.2 亿行就多几十 GB", size=10.5, fill=SUB)
    c.text(84, 540, "明细存快照价，改价不改历史订单", size=10.5, fill=SUB)

    # ---- 右：状态机
    c.container(490, 84, 410, 470, "主表状态：五个值，迁移单向")
    c.box(515, 120, 165, 58, "待支付", "10", accent=BLUE, size=13, sub_size=10)
    c.box(515, 226, 165, 58, "已支付", "20", accent=BLUE, size=13, sub_size=10)
    c.box(515, 332, 165, 58, "已发货", "30", accent=BLUE, size=13, sub_size=10)
    c.box(515, 438, 165, 58, "已完成", "90", accent=GREEN, size=13, sub_size=10)
    c.box(740, 120, 140, 58, "已关闭", "99", accent=RED, size=13, sub_size=10)

    c.arrow((597, 178), (597, 226), color=BLUE, label="支付", label_dy=-10)
    c.arrow((597, 284), (597, 332), color=BLUE, label="发货", label_dy=-10)
    c.arrow((597, 390), (597, 438), color=GREEN, label="确认收货", label_dy=-10)
    c.arrow((680, 149), (740, 149), color=RED, label="超时", label_dy=-10)

    c.text(720, 216, "主表状态每多一个值，", size=10.5, fill=SUB)
    c.text(720, 240, "按状态查询的索引", size=10.5, fill=SUB)
    c.text(720, 264, "选择性就降一档；", size=10.5, fill=SUB)
    c.text(720, 288, "迁移组合数按平方涨", size=10.5, fill=SUB)
    c.text(515, 524, "终态不回退：重开只能新单据", size=10.5, fill=SUB)

    # ---- 底：不该进主表的状态
    c.container(60, 572, 840, 80, "")
    c.text(74, 604, "不该进主表的三个值：", size=11, fill=INK, weight=600)
    c.pill(266, 586, 106, 26, "退款中", accent=RED)
    c.pill(386, 586, 106, 26, "部分退款", accent=RED)
    c.pill(506, 586, 106, 26, "售后中", accent=RED)
    c.text(628, 604, "→ order_event + after_sale 标记", size=10.5, fill=RED)

    c.text(60, 678, "绿色为终态；红色三个值是事件，进事件表，不进状态列", size=10.5, fill=SUB)
    return c.save(os.path.join(OUT, "ch49-fig1.svg"))


# ---------------------------------------------------------------- 图 49-2
def fig2():
    c = Canvas(960, 720,
               title="图 49-2　三种扣减方案：热点分别落在哪一步",
               subtitle="判断与扣减是否在同一条语句里，决定了这把锁能不能挡住超卖")

    rows = [
        (96, GREEN, "方案一", "条件更新", 2,
         [("请求：扣 1 件", "爆款 2400 次/秒", BLUE),
          ("同一条 UPDATE", "判断在 WHERE 里", GREEN),
          ("行 X 锁", "同 SKU 严格串行", RED),
          ("提交等 fsync", "单行几百~两千 TPS", BLUE)],
         "热点：一把行锁。正确，但有天花板；超出上限时排队，不超卖",
         RED),
        (262, ORANGE, "方案二", "乐观锁", 2,
         [("先读 version", "普通快照读，不持锁", BLUE),
          ("带版本号更新", "冲突时影响行数 0", ORANGE),
          ("应用重试", "冲突率越高越糟", RED),
          ("提交", "低冲突不持锁等待", BLUE)],
         "冲突率过约 20% 后重试放大：一次成功要 1/(1-p) 次尝试，吞吐反低于方案一",
         ORANGE),
        (428, PURPLE, "方案三", "预扣 + 流水", 1,
         [("INSERT 流水", "顺序写，无热点行", PURPLE),
          ("可用量靠聚合", "总量 − SUM(占用)", ORANGE),
          ("余量字段异步", "窗口内可超卖", RED),
          ("定期结算", "近实时，不精确", PURPLE)],
         "热点从行锁转移到聚合读与余量字段；形态是预留 + 结算，不是实时精确",
         RED),
    ]

    for y, col, name, tag, hot_idx, steps, verdict, vcol in rows:
        c.container(60, y, 840, 148, "")
        c.box(76, y + 34, 110, 64, name, tag, accent=col, size=13, sub_size=10)
        xs = (208, 384, 560, 736)
        for i, (t, s, sc) in enumerate(steps):
            c.box(xs[i], y + 34, 136, 64, t, s, accent=sc, size=11, sub_size=9.5)
            if i + 1 < len(steps):
                c.arrow((xs[i] + 136, y + 66), (xs[i + 1], y + 66), color=SLATE)
        hx = xs[hot_idx]
        c.rect(hx, y + 34, 136, 64, fill="none", stroke=vcol, sw=1.8, dash="5,3", r=8)
        c.badge(hx + 6, y + 8, "热点", accent=vcol)
        c.text(76, y + 124, verdict, size=11, fill=vcol)

    # ---- 底部判据
    c.container(60, 592, 840, 60, "")
    c.text(74, 616, "数据库能挡住的只有\"余额变负\"：WHERE qty >= 1 是当前读，判断在锁内完成",
           size=10.5, fill=INK)
    c.text(74, 638, "挡不住\"看到有货但下单失败\"（体验问题），也挡不住跨 SKU 的事务（见第 34 章）",
           size=10.5, fill=SUB)

    c.legend(60, 684, [(GREEN, "判断在锁内", None)])
    c.legend(250, 684, [(ORANGE, "等待 / 重试", None)])
    c.legend(440, 684, [(RED, "热点 / 超卖窗口", None)])
    c.legend(650, 684, [(PURPLE, "流水 / 聚合", None)])
    return c.save(os.path.join(OUT, "ch49-fig2.svg"))


# ---------------------------------------------------------------- 图 49-3
def fig3():
    c = Canvas(960, 640,
               title="图 49-3　热点行拆桶之后，多出来的三个问题",
               subtitle="拆桶把一行锁摊成 20 份，也把\"精确可用量\"换成了\"近似可用量\"")

    c.container(60, 84, 840, 250, "一个 SKU 拆成 20 桶：单行并发降到 1/20")
    c.box(400, 112, 160, 56, "stock 总量", "100 件，2400 次/秒", accent=RED, size=12, sub_size=9.5)
    c.arrow((480, 168), (480, 196), color=SLATE)
    c.arrow((168, 196), (824, 196), color=SLATE, end=False)

    xs = (100, 264, 428, 592, 756)
    for i, x in enumerate(xs):
        c.arrow((x + 68, 196), (x + 68, 212), color=SLATE)
        c.box(x, 212, 136, 56, "桶 %d" % i, "qty = 5", accent=GREEN, size=12, sub_size=9.5)

    c.text(80, 292, "请求按 user_id % 20 落桶；单桶约 120 次/秒", size=10.5, fill=SUB)
    c.text(860, 292, "…共 20 桶", size=10.5, fill=SUB, anchor="end")

    cards = [
        ("代价 ① 可用量要 SUM",
         ["实时 SUM 20 行 = 一次聚合读", "要准确还得锁这 20 行", "只给得出“近似可用”", "结算任务定期修正偏差"]),
        ("代价 ② 桶之间不均衡",
         ["热门桶先空，冷桶还有货", "借桶 = 一次跨行事务", "反向借桶就是死锁", "借桶要限频，否则成新热点"]),
        ("代价 ③ 总量调整改 20 行",
         ["运营改库存要动 20 行", "改到第 13 行失败，总量就错", "同事务或版本校验兜底", "异步改则留下不一致窗口"]),
    ]
    for i, (title, lines) in enumerate(cards):
        x = 60 + i * 287
        c.container(x, 350, 266, 150, title)
        for j, ln in enumerate(lines):
            c.text(x + 14, 400 + j * 26, ln, size=10.5, fill=SUB)

    c.container(60, 520, 840, 60, "")
    c.text(74, 544, "拆桶拆的是锁，不是问题：单行热点没了，聚合读、桶倾斜、总量一致性全冒出来",
           size=10.5, fill=INK)
    c.text(74, 566, "秒杀真正的解法是把瞬时并发削成可持续速率；数据库只守最后一道\"不超卖\"",
           size=10.5, fill=SUB)

    c.legend(60, 600, [(RED, "热点行", None)])
    c.legend(200, 600, [(GREEN, "拆出来的桶", None)])
    c.legend(380, 600, [(SLATE, "落桶路由", None)])
    return c.save(os.path.join(OUT, "ch49-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
