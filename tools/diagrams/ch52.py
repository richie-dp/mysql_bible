#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 52 章配图：故障应急与 SOP"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 52-1
def fig1():
    c = Canvas(960, 620,
               title="图 52-1　事故分级与动作权限：级别决定能跳过哪一道审批",
               subtitle="判定标准要能被监控数字直接命中；级别越高，允许的动作越激进，事后追认的要求也越硬")

    cols = [
        (48, RED, "P0", "影响成交或资金",
         ["下单失败率 > 5%", "或资金接口不可用"],
         ["值班 + 业务负责人", "业务方必须在线"],
         ["跳过变更审批", "直接止血、先回滚", "24 小时内补审批"], True),
        (272, ORANGE, "P1", "影响部分用户可用",
         ["某功能整体不可用", "或某地域不可用"],
         ["值班 + 模块 Owner", ""],
         ["快速通道：单人审批", "止血动作必须留记录", "事后仍需复核"], False),
        (496, BLUE, "P2", "性能下降未破 SLA",
         ["P99 抬升", "错误率没有变化"],
         ["值班即可", ""],
         ["不允许跳审批", "只做可回滚的调参", "排到次日窗口"], False),
        (720, SLATE, "P3", "单点异常有兜底",
         ["单实例或单分片异常", "有冗余、用户无感"],
         ["不必叫醒", "记录后进迭代"],
         ["不占用故障窗口", "不做临时变更"], False),
    ]

    for x, col, lv, judge, jl, wl, act, hot in cols:
        c.box(x, 92, 204, 46, lv, judge, accent=col, size=14, sub_size=9.5)
        c.container(x, 146, 204, 274, "")

        c.text(x + 12, 174, "判定标准", size=9, fill=SUB, weight=600)
        yy = 196
        for ln in jl:
            c.text(x + 12, yy, ln, size=9.8, fill=INK)
            yy += 18

        c.text(x + 12, 254, "谁在场", size=9, fill=SUB, weight=600)
        yy = 276
        for ln in wl:
            if ln:
                c.text(x + 12, yy, ln, size=9.8, fill=INK)
                yy += 18

        c.text(x + 12, 332, "允许的动作", size=9, fill=SUB, weight=600)
        yy = 354
        for i, ln in enumerate(act):
            first = (i == 0 and hot)
            c.text(x + 12, yy, ln, size=9.8,
                   fill=col if first else INK, weight=600 if first else 400)
            yy += 18

    c.box(48, 440, 864, 62,
          "P0 可以不等审批就止血",
          "代价是事后追认：动作、依据、审批人，24 小时内补齐",
          accent=RED, size=15, sub_size=11)

    c.text(48, 536, "分级的用途不是决定上报谁，是决定这一次能跳过哪一道审批。",
           size=11.5, fill=INK)

    c.legend(48, 568, [(RED, "P0：跳审批直接止血 / P1：单人审批 / P2、P3：走完整流程", None)])
    return c.save(os.path.join(OUT, "ch52-fig1.svg"))


# ---------------------------------------------------------------- 图 52-2
def fig2():
    c = Canvas(960, 800,
               title="图 52-2　十张卡片的索引：三分钟内认出它，先取证，再止血",
               subtitle="每行对应第 41 章的一个案例；卡片要在故障前读，故障中只来得及看一行")

    rows = [
        ("①", "连接数贴上限，Sleep 上千秒", "Sleep 占比 >90%，Running 个位数", "processlist 按 Command 聚合", "21·37", RED),
        ("②", "QPS 骤降，命中率同步下跌", "计划 ALL，物理读与 rnd_next 齐涨", "EXPLAIN + pages_free", "10·11", RED),
        ("③", "P99 周期性尖刺，无慢 SQL", "checkpoint 年龄贴着 redo 容量", "INNODB STATUS 的 LOG 段", "4·39", ORANGE),
        ("④", "复制延迟成台阶，不是斜坡", "位点长时间不动，然后跳一段", "REPLICA STATUS + 无主键表", "22·25", ORANGE),
        ("⑤", "全站卡在 metadata lock", "GRANTED 挂在 Sleep 会话上", "metadata_locks 的 STATUS", "18·21", ORANGE),
        ("⑥", "死锁激增（1213）", "两个事务 HOLDS/WAITING 对调", "LATEST DETECTED DEADLOCK", "19·20", ORANGE),
        ("⑦", "磁盘满或实例被置只读", "undo 几百 G，history 千万级", "files + BINARY LOGS", "3·5", RED),
        ("⑧", "mysqld 周期性消失", "dmesg 里有 Killed process", "内存按 EVENT_NAME 归因", "14·37", RED),
        ("⑨", "付了钱查不到单", "半同步状态 OFF，延迟却是 0", "Rpl_semi_sync% 三个值", "24·26", PURPLE),
        ("⑩", "误删了一批行", "binlog 里能定位到 BEGIN", "mysqlbinlog 的 # at", "28·48", PURPLE),
    ]

    c.text(104, 88, "症状（一句话）", size=10, fill=SUB, weight=600)
    c.text(306, 88, "认出它：一条命令或一个指标形态", size=10, fill=SUB, weight=600)
    c.text(602, 88, "首选取证", size=10, fill=SUB, weight=600)
    c.text(822, 88, "根因章节", size=10, fill=SUB, weight=600)

    for i, (no, sym, sig, ev, chs, col) in enumerate(rows):
        y = 98 + i * 62
        c.container(48, y, 864, 54, "")
        c.box(56, y + 7, 42, 40, no, accent=col, size=12)
        c.box(104, y + 7, 196, 40, sym, accent=col, size=10)
        c.box(306, y + 7, 290, 40, sig, accent=BLUE, size=9.5)
        c.box(602, y + 7, 214, 40, ev, accent=SLATE, size=9.5)
        c.box(822, y + 7, 88, 40, "第 " + chs + " 章", accent=SLATE, size=9)

    c.legend(60, 738, [(RED, "服务不可用或写入失败：先止血，再定位", None)])
    c.legend(430, 738, [(ORANGE, "等待与延迟：先判断是谁在等", None)])
    c.legend(700, 738, [(PURPLE, "数据正确性：先冻窗口，再补", None)])
    return c.save(os.path.join(OUT, "ch52-fig2.svg"))


# ---------------------------------------------------------------- 图 52-3
def fig3():
    c = Canvas(960, 640,
               title="图 52-3　止血五招的代价坐标：快不等于便宜，慢不等于安全",
               subtitle="横轴是生效速度，纵轴是业务代价；位置是取舍，不是优劣")

    c.arrow((110, 470), (110, 128), color=SLATE, width=1.2)
    c.arrow((110, 470), (900, 470), color=SLATE, width=1.2)

    c.text(102, 136, "代价高", size=10, fill=SUB, anchor="end")
    c.text(102, 470, "代价低", size=10, fill=SUB, anchor="end")
    c.text(112, 492, "慢", size=10, fill=SUB)
    c.text(890, 492, "快 →", size=10, fill=SUB, anchor="end")

    # 速度刻度
    for x, lab in ((760, "秒级"), (520, "一分钟级"), (300, "十分钟级")):
        c.arrow((x, 470), (x, 462), color=SLATE, width=1.0, end=False)
        c.text(x, 458, lab, size=9, fill=SUB, anchor="middle")

    items = [
        (280, 196, "切从库", "丢最近的写入", RED),
        (680, 236, "限流", "部分用户失败", ORANGE),
        (770, 330, "回滚", "丢掉这个版本", GREEN),
        (580, 322, "熔断", "一个功能停掉", ORANGE),
        (470, 392, "降级", "读到旧数据", BLUE),
    ]
    for x, y, name, cost, col in items:
        c.box(x, y, 130, 46, name, cost, accent=col, size=13, sub_size=9.5)

    c.badge(280, 170, "最慢，代价却最高", accent=RED, size=9.5)

    c.text(130, 442, "越慢：窗口越难抢", size=10.5, fill=SUB)
    c.text(900, 150, "越快：伤害越当场兑现", size=10.5, fill=SUB, anchor="end")

    c.container(48, 500, 864, 106, "不能用它的条件（写在卡片背面，比用法更重要）")
    c.text(64, 550, "限流：堵不住已在排队的线程；降级：对写路径无效；熔断：依赖是核心链路时等于全停。",
           size=10.5, fill=INK)
    c.text(64, 572, "切从库：RPO 不为 0 且业务不接受丢单；回滚：已执行不可逆 DDL，或已向外部发出成功回执。",
           size=10.5, fill=INK)
    c.text(64, 594, "五条共同的前提：动作本身可回滚，且动手之前已经抓了现场。",
           size=10.5, fill=RED)
    return c.save(os.path.join(OUT, "ch52-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
