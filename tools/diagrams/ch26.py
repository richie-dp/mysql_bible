#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 26 章配图：高可用架构与故障切换"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 26-1
def fig1():
    c = Canvas(960, 840,
               title="图 26-1　切换的七个步骤：每一步跳过或换序，都有对应的事故形态",
               subtitle="蓝线是动作顺序；右侧红色框是「这一步没做对」的后果，第 2 步与第 5 步的顺序不能交换")

    c.text(60, 92, "步骤", size=12, fill=SUB, weight=600)
    c.text(250, 92, "检查点 / 关键动作", size=12, fill=SUB, weight=600)
    c.text(620, 92, "跳过或顺序错误的后果", size=12, fill=SUB, weight=600)

    rows = [
        ("① 检测", "谁来判断主库死了",
         "探活 N 次失败 / SELECT 1 超时",
         "先分清「不可达」与「假死」",
         "假死当成宕机", "老主还在写就切了", RED),
        ("② 隔离", "先拿走老主的写权限",
         "super_read_only + KILL + 撤 VIP",
         "顺序：先隔离，再选主",
         "未隔离就提升 = 脑裂", "两台都能写，各写各的", RED),
        ("③ 选主", "选 GTID 最全的那台",
         "GTID_SUBSET 比包含关系",
         "同等完整度再看延迟",
         "选到缺事务的从库", "那段事务永久缺口", RED),
        ("④ 补数据", "老主 binlog 的差集",
         "mysqlbinlog 捞出，重放新主",
         "老主已死则只能接受丢失",
         "跳过补数据", "RPO 兑现成真实缺口", RED),
        ("⑤ 提升", "让新主可写",
         "STOP REPLICA; RESET REPLICA ALL",
         "read_only=OFF 连带清 super_read_only",
         "忘了 RESET REPLICA ALL", "新主还挂着老主的通道", RED),
        ("⑥ 改指向", "从库与应用一起改",
         "CHANGE REPLICATION SOURCE TO",
         "VIP / 连接串 / 中间件三选一",
         "漏一台从库", "它还在追老主，数据分叉", RED),
        ("⑦ 验证", "切完不等于切对",
         "GTID 相等 + 行数抽查 + 探活",
         "全量校验放低峰",
         "不验证就宣布成功", "几天后对账才发现少一批", RED),
    ]

    y = 108
    for i, (step, step_sub, detail, detail_sub, bad, bad_sub, col) in enumerate(rows):
        accent = RED if i == 1 else BLUE
        c.box(60, y, 150, 58, step, step_sub, accent=accent, size=13, sub_size=10)
        c.box(250, y, 330, 58, detail, detail_sub, accent=PURPLE, size=12, sub_size=10)
        c.box(620, y, 280, 58, bad, bad_sub, accent=col, size=12, sub_size=10)
        if i < len(rows) - 1:
            c.arrow((135, y + 58), (135, y + 98), color=BLUE)
        y += 98

    c.text(60, 790, "第 2 步与第 5 步之间没有「等一会儿」：隔离完成后老主只剩只读，提升才有意义。",
           size=12, fill=INK)
    c.legend(60, 812, [(BLUE, "主流程", None)])
    c.legend(220, 812, [(RED, "脑裂 / 丢数据", None)])
    c.legend(430, 812, [(PURPLE, "复制与日志动作", None)])
    return c.save(os.path.join(OUT, "ch26-fig1.svg"))


# ---------------------------------------------------------------- 图 26-2
def fig2():
    c = Canvas(960, 700,
               title="图 26-2　脑裂的三道闸门：每道挡住什么，又从哪漏过去",
               subtitle="三道防线是叠加关系，不是替代关系；任何一道单独用，都有一条现成的绕行路径")

    c.box(60, 88, 840, 54, "前提：老主没有被真正隔离——进程还在、连接还在、VIP 还能收包",
          "此时提升新主，等于给第二个写入点发许可证", accent=RED, size=13, sub_size=10)

    gates = [
        (60, "防线 1｜VIP 漂移", "keepalived / VRRP",
         "新连接落到新主", "客户端按 VIP 连", "ARP 缓存未过期", "应用直连 IP 也绕过"),
        (355, "防线 2｜网关仲裁", "fencing / STONITH",
         "老主被强制断电", "IPMI、交换机端口", "只撤 VIP 不断电", "老主网卡还活着"),
        (650, "防线 3｜super_read_only", "只读围栏 [5.7.8+]",
         "新写入被拒绝", "ERROR 1290", "已建立的事务", "开启前的连接照常 COMMIT"),
    ]

    for x, head, gate_sub, block, block_sub, leak, leak_sub in gates:
        c.pill(x, 170, 250, 28, head, accent=SLATE, size=11)
        c.box(x, 210, 250, 80, "闸门", gate_sub, accent=ORANGE, size=12, sub_size=10)
        c.box(x, 310, 250, 78, block, block_sub, accent=GREEN, size=12, sub_size=10)
        c.box(x, 408, 250, 86, leak, leak_sub, accent=RED, size=12, sub_size=10)
        c.arrow((x + 125, 494), (x + 125, 530), color=RED, dash="5,4")

    c.container(60, 530, 840, 130, "漏网路径：三道闸门都拦不住的三种组合")
    c.text(78, 572, "① 只读开启前已建立的连接：super_read_only 拒绝新语句，但不 kill 会话，未提交事务照常 COMMIT。",
           size=11, fill=INK)
    c.text(78, 600, "② 有 SUPER 权限的账号：read_only 挡不住，super_read_only 才挡；账号权限不收，围栏就是摆设。",
           size=11, fill=INK)
    c.text(78, 628, "③ 没有 fencing 的 VIP 漂移：漂移只是「多了一个入口」，不是「少了旧的」，老主网卡仍在收包。",
           size=11, fill=INK)

    c.legend(60, 668, [(GREEN, "挡得住", None)])
    c.legend(220, 668, [(RED, "漏掉的路径", "5,4")])
    return c.save(os.path.join(OUT, "ch26-fig2.svg"))


# ---------------------------------------------------------------- 图 26-3
def fig3():
    c = Canvas(960, 560,
               title="图 26-3　RTO 的真实构成：切换脚本只是中间一小段",
               subtitle="比例示意，非实测；实际占比取决于探活间隔、应用连接池与业务预热方式")

    X, W, Y, H = 80, 800, 200, 64
    segs = [
        ("检测", "探活间隔 × 失败次数", 170, ORANGE),
        ("决策", "人工 / 工具", 80, SLATE),
        ("切换", "隔离 → 提升", 110, BLUE),
        ("应用重连", "旧连接等 TCP 超时", 330, RED),
        ("预热", "连接池 / 缓存", 110, GREEN),
    ]

    x = X
    for title, sub, w, col in segs:
        c.box(x, Y, w, H, title, sub, accent=col, size=12, sub_size=9)
        x += w

    # 脚本执行时间的范围：决策 + 切换
    c.arrow((X + 170, Y + H + 18), (X + 360, Y + H + 18), color=BLUE, end=False, start=False)
    c.text(X + 265, Y + H + 34, "脚本执行时间", size=11, fill=BLUE, anchor="middle", weight=600)

    # 第二根条：只统计脚本
    c.text(X, 326, "只统计脚本时的口径", size=11, fill=SUB, weight=600)
    c.box(X, 340, 190, 40, "190px 的执行段", None, accent=BLUE, size=11)
    c.rect(X + 190, 340, W - 190, 40, fill="#ffffff", stroke=SLATE, sw=1.3, r=8, dash="6,4")
    c.text(X + 190 + (W - 190) / 2, 365, "检测、重连、预热都不在统计里",
           size=11, fill=SUB, anchor="middle")

    c.text(X, 420, "RTO = 检测 + 决策 + 切换 + 应用重连 + 预热。只优化第三段，等于只改了一小截。",
           size=12, fill=INK)
    c.text(X, 444, "检测的下限由探活间隔决定；应用重连的上限由连接池与 TCP 重传决定。",
           size=11, fill=SUB)

    c.legend(80, 492, [(ORANGE, "检测等待", None)])
    c.legend(210, 492, [(SLATE, "决策", None)])
    c.legend(330, 492, [(BLUE, "切换动作", None)])
    c.legend(470, 492, [(RED, "应用重连", None)])
    c.legend(610, 492, [(GREEN, "预热", None)])
    return c.save(os.path.join(OUT, "ch26-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
