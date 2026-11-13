#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 41 章配图：典型案例复盘集"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 41-1
def fig1():
    c = Canvas(960, 800,
               title="图 41-1　十个案例的导航矩阵：先认类型，再找信号，最后回看章节",
               subtitle="类型 A 把结果当原因 / B 把局部当全局 / C 把配置当银弹；同一类型的处置动作天然不同")

    rows = [
        ("① 连接数被打满", "A", "Sleep 上千秒，Running 个位数", "21·37·40"),
        ("② QPS 骤降 90%", "A", "计划 range→ALL，物理读暴涨", "10·11·40"),
        ("③ RT 周期性抖动", "A", "wait_free 与 checkpoint 年龄", "4·39·40"),
        ("④ 主从延迟 6 小时", "B", "位点成台阶，无主键表回放", "22·25·30"),
        ("⑤ 全站锁死", "A", "GRANTED 挂在 Sleep 线程上", "18·21·36"),
        ("⑥ 死锁风暴", "C", "两个事务加锁顺序刚好相反", "19·20"),
        ("⑦ 磁盘爆满", "B", "undo 几百 G，history 千万级", "3·5·28·35"),
        ("⑧ 内存 OOM", "A", "排序与临时表内存 × 并发数", "14·37·40"),
        ("⑨ 数据不一致", "C", "半同步状态 OFF，延迟却是 0", "24·26·37"),
        ("⑩ 误删 40 万行", "C", "全备 + binlog，stop-position", "28·48"),
    ]
    tone = {"A": RED, "B": ORANGE, "C": TEAL}

    c.text(80, 92, "案例", size=11, fill=SUB, weight=600)
    c.text(336, 92, "类型", size=11, fill=SUB, weight=600)
    c.text(400, 92, "当时唯一有效的信号", size=11, fill=SUB, weight=600)
    c.text(740, 92, "回看章节", size=11, fill=SUB, weight=600)

    for i, (name, typ, sig, chs) in enumerate(rows):
        y = 104 + i * 64
        c.container(56, y, 848, 56, "")
        c.box(66, y + 8, 246, 40, name, accent=SLATE, size=12.5)
        c.pill(322, y + 16, 50, 24, typ, accent=tone[typ], size=12)
        c.box(386, y + 8, 330, 40, sig, accent=tone[typ], size=10.5)
        c.box(726, y + 8, 168, 40, "第 " + chs + " 章", accent=SLATE, size=10,
              sub_size=9)

    c.legend(60, 752, [(RED, "A 把结果当原因：指标动了就修这一层", None)])
    c.legend(60, 774, [(ORANGE, "B 把局部当全局：加一个更大号的同一层", None)])
    c.legend(560, 752, [(TEAL, "C 把配置当银弹：好了就说参数对了", None)])
    c.legend(560, 774, [(SLATE, "导航：类型决定先查什么，章节决定翻哪一页", None)])
    return c.save(os.path.join(OUT, "ch41-fig1.svg"))


# ---------------------------------------------------------------- 图 41-2
def fig2():
    c = Canvas(960, 560,
               title="图 41-2　六段式复盘：前两段是现场，后四段是产物",
               subtitle="每个案例都按同一个骨架写，差别只在第三段——它是唯一有机会改变结论的地方")

    xs = [60, 207, 354, 501, 648, 795]
    y, w, h = 200, 105, 76
    nodes = [
        ("现象", ["现场看到", "什么"], BLUE),
        ("误判", ["当时真的", "相信什么"], RED),
        ("数据", ["拿哪个观测", "去推翻它"], ORANGE),
        ("根因", ["机制上哪", "一层错了"], PURPLE),
        ("处置", ["先做什么", "止住"], GREEN),
        ("长效措施", ["改什么", "才不再来"], SLATE),
    ]

    for x, (title, lines, col) in zip(xs, nodes):
        c.box(x, y, w, h, title, accent=col, size=14)
        c.text(x + w / 2, 300, lines[0], size=10, fill=SUB, anchor="middle")
        c.text(x + w / 2, 318, lines[1], size=10, fill=SUB, anchor="middle")

    for i in range(5):
        c.arrow((xs[i] + w, y + h / 2), (xs[i + 1], y + h / 2), color=BLUE)

    # 唯一的回流：误判 → 数据
    c.arrow([(xs[1] + w / 2, y), (xs[1] + w / 2, 162),
             (xs[2] + w / 2, 162), (xs[2] + w / 2, y)], color=RED, dash="6,4")
    c.text((xs[1] + xs[2] + w) / 2, 152, "唯一能翻盘：这一步换的是假设",
           size=11, fill=RED, anchor="middle", weight=600)

    c.container(60, 350, 840, 130, "六段之间的关系")
    c.text(84, 392, "前两段是现场：现象是别人看到的，误判是你当时真的相信的。写不出“当时相信”，这一段就是假的。",
           size=11, fill=INK)
    c.text(84, 420, "第三段是唯一的翻盘点：数据不是用来支持误判的，是用来淘汰误判的——它必须能区分两种假设。",
           size=11, fill=INK)
    c.text(84, 448, "后三段是产物：根因解释机制，处置止血，长效措施改系统；三者的验收标准互不替代。",
           size=11, fill=INK)
    return c.save(os.path.join(OUT, "ch41-fig2.svg"))


# ---------------------------------------------------------------- 图 41-3
def fig3():
    c = Canvas(960, 620,
               title="图 41-3　案例二的因果链：报警在末端，原因在起点",
               subtitle="从导入到报警跨了 23 小时：报警在第 4 步，原因在第 1 步，中间三步都没有指标")

    xs = [60, 236, 412, 588, 764]
    y, w, h = 180, 136, 80
    steps = [
        ("① 批量导入", "200 万行历史订单", "前一日 22:40", "无人看见",
         ["脚本跑完就退出", "没人算过统计信息"], BLUE),
        ("② 统计陈旧", "基数停在旧分布", "前一日 22:41", "无人看见",
         ["优化器仍按", "旧分布估行数"], BLUE),
        ("③ IN 超阈值", "越过 dive 上限", "当日 21:05", "无人看见",
         ["默认阈值 200", "没人监控长度"], ORANGE),
        ("④ 计划变 ALL", "扫 800 万行", "当日 21:12", "报警在此",
         ["BP 热页被冲掉", "命中率掉到 71%"], RED),
        ("⑤ 全站变慢", "P99 抬到 3s", "当日 21:13", "业务可见",
         ["QPS 掉了 90%", "错误率反而低"], RED),
    ]

    for i, (title, sub, tm, tag, lines, col) in enumerate(steps):
        x = xs[i]
        c.box(x, y, w, h, title, sub, accent=col, size=12.5, sub_size=9.5)
        c.text(x + w / 2, 278, tm, size=9.5, fill=SUB, anchor="middle", mono=True)
        c.pill(x + 13, 292, 110, 22, tag,
               accent=(RED if tag in ("报警在此", "业务可见") else SLATE), size=10)
        c.text(x + w / 2, 344, lines[0], size=9.5, fill=SUB, anchor="middle")
        c.text(x + w / 2, 362, lines[1], size=9.5, fill=SUB, anchor="middle")
        if i:
            c.arrow((xs[i - 1] + w, y + h / 2), (x, y + h / 2), color=SLATE)

    # 从报警回溯到原因
    c.arrow([(xs[3] + w / 2, y), (xs[3] + w / 2, 130),
             (xs[0] + w / 2, 130), (xs[0] + w / 2, y)], color=RED, dash="6,4")
    c.text(480, 120, "报警响在第四步，原因埋在第一步：中间隔了 23 小时",
           size=11, fill=RED, anchor="middle", weight=600)

    c.container(60, 400, 840, 100, "这条链上的观测分布")
    c.text(84, 440, "五个环节里只有最后一个有现成指标。前四个的证据分别是：导入脚本的执行记录、统计信息的时间戳、IN 列表长度、EXPLAIN 输出。",
           size=11, fill=INK)
    c.text(84, 468, "前三个默认没人采集。复盘的任务不是解释第 5 步，是把第 1 步也变成一条曲线。",
           size=11, fill=INK)

    c.legend(60, 540, [(RED, "结果与报警", None)])
    c.legend(200, 540, [(ORANGE, "阈值被越过", None)])
    c.legend(340, 540, [(BLUE, "隐患埋下", None)])
    c.legend(460, 540, [(SLATE, "因果推进", None)])
    return c.save(os.path.join(OUT, "ch41-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
