#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 36 章配图：性能分析方法论"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 36-1
def fig1():
    c = Canvas(960, 580, title="图 36-1　三层定位法：从业务指标往下收敛",
               subtitle="每一层只排除一类原因；反过来从系统指标往上猜，永远落不到具体 SQL")

    c.text(60, 82, "这一层能排除什么", size=11.5, fill=SLATE, weight=600)

    # 漏斗：三层
    c.box(300, 104, 320, 92, "① 业务指标", "P99 RT ／ 错误率 ／ QPS", accent=BLUE)
    c.box(310, 236, 300, 104, "② DB 指标", "Threads_running ／ 锁等待 ／ 命中率", accent=BLUE)
    c.box(320, 380, 280, 92, "③ 系统指标", "CPU us/sy/wa ／ await ／ swap", accent=BLUE)

    c.arrow(460, 196, 460, 236, color=BLUE, label="还慢，往下走")
    c.arrow(460, 340, 460, 380, color=BLUE, label="还不定位，再往下")

    # 左侧：每层能排除什么
    c.text(60, 128, "排除：不是全局故障", size=11, fill=SUB)
    c.text(60, 148, "定位到接口、商户、时刻", size=11, fill=SUB)
    c.text(60, 262, "排除：SQL 慢 ／ 锁 ／ 容量", size=11, fill=SUB)
    c.text(60, 282, "决定要不要拉 EXPLAIN", size=11, fill=SUB)
    c.text(60, 406, "排除：资源瓶颈", size=11, fill=SUB)
    c.text(60, 426, "但给不出「哪条 SQL」", size=11, fill=SUB)

    # 右侧：反向猜测的代价
    c.container(660, 104, 260, 400, "反向：从系统指标往上猜")
    c.arrow(690, 480, 690, 150, color=RED, dash="5,4")
    c.text(706, 470, "↑ 方向相反", size=10.5, fill=RED, weight=600)
    c.text(706, 185, "CPU 不高 → 结论被误读", size=10.5, fill=INK)
    c.text(706, 203, "成「数据库没问题」", size=10.5, fill=INK)
    c.text(706, 250, "系统指标只证明资源够", size=10.5, fill=INK)
    c.text(706, 268, "给不出下一步查什么", size=10.5, fill=INK)
    c.text(706, 315, "等你看完 iostat", size=10.5, fill=INK)
    c.text(706, 333, "锁等待已积压 20 分钟", size=10.5, fill=INK)

    c.text(60, 545, "三层不是三个仪表盘，而是一条排除链：上层给方向，下层给证据；跳层就是从结论倒推原因。",
           size=11.5, fill=INK)
    return c.save(os.path.join(OUT, "ch36-fig1.svg"))


# ---------------------------------------------------------------- 图 36-2
def fig2():
    c = Canvas(960, 620, title="图 36-2　吞吐-延迟曲线：拐点之后，加并发等于加排队",
               subtitle="L = λ × W；同样的并发增量，在拐点两侧买到的东西完全不同")

    # 三区分隔线
    for x in (400, 580):
        c.els.append(f'<line x1="{x}" y1="150" x2="{x}" y2="500" stroke="{LINE}" '
                     f'stroke-width="1.1" stroke-dasharray="4,5"/>')
    c.rect(150, 158, 200, 3, fill=GREEN, stroke="none", sw=0, r=1)
    c.rect(430, 158, 120, 3, fill=ORANGE, stroke="none", sw=0, r=1)
    c.rect(660, 158, 140, 3, fill=RED, stroke="none", sw=0, r=1)

    # 坐标轴
    c.els.append(f'<line x1="100" y1="500" x2="880" y2="500" stroke="{LINE}" stroke-width="1.4"/>')
    c.els.append(f'<line x1="100" y1="500" x2="100" y2="130" stroke="{LINE}" stroke-width="1.4"/>')
    c.els.append(f'<line x1="880" y1="500" x2="880" y2="130" stroke="{LINE}" stroke-width="1.4"/>')
    c.text(104, 122, "λ  QPS", size=11, fill=BLUE, weight=600)
    c.text(876, 122, "W  ms", size=11, fill=RED, weight=600, anchor="end")
    c.text(880, 528, "并发（Threads_running）", size=11.5, fill=SLATE, anchor="end")

    # 分区标签
    c.text(250, 152, "富余区：加并发直接换成吞吐", size=11, fill=GREEN, anchor="middle", weight=600)
    c.text(490, 152, "饱和区", size=11, fill=ORANGE, anchor="middle", weight=600)
    c.text(730, 152, "过载区：加并发换成排队", size=11, fill=RED, anchor="middle", weight=600)

    # λ 曲线
    c.els.append(
        '<path d="M 100,500 C 150,470 220,430 300,395 '
        'C 360,368 420,352 470,345 C 520,340 560,342 600,350 '
        'C 660,362 750,390 820,420 C 845,431 865,440 878,447" '
        f'fill="none" stroke="{BLUE}" stroke-width="2.6"/>'
    )
    # W 曲线
    c.els.append(
        '<path d="M 100,494 C 250,491 380,487 430,478 '
        'C 470,468 495,446 520,412 C 560,352 620,290 700,225 '
        'C 760,180 820,160 878,150" '
        f'fill="none" stroke="{RED}" stroke-width="2.6"/>'
    )

    # 拐点
    c.els.append(f'<line x1="525" y1="172" x2="525" y2="500" stroke="{PURPLE}" '
                 f'stroke-width="1.3" stroke-dasharray="5,4"/>')
    c.text(533, 196, "拐点", size=11.5, fill=PURPLE, weight=600)
    c.text(533, 214, "λ 增量趋零", size=10.5, fill=PURPLE)

    # 曲线标注
    c.text(300, 372, "λ 见顶", size=11, fill=BLUE)
    c.text(700, 205, "W 陡升", size=11, fill=RED)
    c.arrow(660, 358, 820, 421, color=RED, dash="4,3", width=1.3,
            label="再加并发，λ 反降", label_at=0.55, label_dy=16)

    c.text(100, 555, "横轴向右＝并发加大：线性区的并发是产能，过载区的并发只是排队。",
           size=11.5, fill=INK)
    c.box(560, 540, 320, 56, "L = λ × W", "恒等式：并发 = 吞吐 × 响应时间", accent=PURPLE)
    return c.save(os.path.join(OUT, "ch36-fig2.svg"))


# ---------------------------------------------------------------- 图 36-3
def fig3():
    c = Canvas(960, 790, title="图 36-3　一次排障的真实形态：14:20 → 15:40",
               subtitle="红色是被推翻的判断，橙色是「KILL 之后并没有立刻好」的那 30 分钟")

    c.legend(545, 84, [(RED, "错误判断", None)])
    c.legend(650, 84, [(GREEN, "定位成功", None)])
    c.legend(770, 84, [(ORANGE, "等待 / 回滚", None)])

    # 阶段带
    bands = [
        (90, 146, "试错", "14:20–14:35", SLATE),
        (244, 142, "定位", "14:35–14:50", GREEN),
        (394, 112, "决策", "14:50–15:02", ORANGE),
        (514, 72, "KILL", "15:02", ORANGE),
        (594, 294, "回滚等待 30 分钟", "15:10–15:40 锁未释放", ORANGE),
    ]
    for x, w, t, s, col in bands:
        c.container(x, 150, w, 62, "")
        c.text(x + 12, 174, t, size=12, fill=col, weight=600)
        c.text(x + 12, 194, s, size=10, fill=SUB)

    # 时间轴
    c.els.append(f'<line x1="90" y1="250" x2="890" y2="250" stroke="{SLATE}" stroke-width="1.6"/>')
    for i, lab in enumerate(["14:20", "14:30", "14:40", "14:50", "15:00",
                             "15:10", "15:20", "15:30", "15:40"]):
        x = 90 + i * 100
        c.els.append(f'<line x1="{x}" y1="244" x2="{x}" y2="250" stroke="{SLATE}" stroke-width="1.2"/>')
        c.text(x, 238, lab, size=10, fill=SUB, anchor="middle")

    # 事件针脚
    events = [
        (90, "1", RED), (140, "2", RED), (190, "3", PURPLE), (240, "4", PURPLE),
        (290, "5", GREEN), (340, "6", GREEN), (390, "7", GREEN), (440, "8", ORANGE),
        (510, "9", ORANGE), (590, "10", ORANGE), (890, "11", GREEN),
    ]
    for x, n, col in events:
        c.arrow(x, 250, x, 293, color=col, width=1.2)
        c.pill(x - 15, 294, 30, 22, n, accent=col, size=10)

    # 卡片
    cards = [
        ("① 14:20　告警", "P99 80ms → 2.3s", RED),
        ("② 14:25　查发布", "无变更 → 方向错", RED),
        ("③ 14:30　CPU us 40%", "不是计算密集", PURPLE),
        ("④ 14:35　并发 8 → 90", "CPU 不高 → 在等", PURPLE),
        ("⑤ 14:40　PROCESSLIST", "60+ 线程等行锁", GREEN),
        ("⑥ 14:45　锁等待视图", "指向同一个事务", GREEN),
        ("⑦ 14:50　innodb_trx", "22 分钟｜180 万行", GREEN),
        ("⑧ 14:55　评估回滚", "不立即 KILL", ORANGE),
        ("⑨ 15:02　KILL 会话", "等业务确认后执行", ORANGE),
        ("⑩ 15:10　ROLLING BACK", "锁仍在，等了 30 分钟", ORANGE),
        ("⑪ 15:40　恢复", "P99 回到 80ms", GREEN),
        ("合计 80 分钟", "定位 20 ｜ 回滚 38", SLATE),
    ]
    for i, (t, s, col) in enumerate(cards):
        x = 90 + (i % 3) * 285
        y = 350 + (i // 3) * 92
        c.box(x, y, 255, 76, t, s, accent=col, size=13, sub_size=10.5)

    c.text(90, 742, "两次判断被推翻：② 只查了应用发布、③ 把「CPU 不高」读成「库没问题」；"
                    "真正耗时的是 ⑩ 那 30 分钟。", size=11.5, fill=INK)
    return c.save(os.path.join(OUT, "ch36-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
