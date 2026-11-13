#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 33 章配图：分库分表"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 33-1
def fig1():
    c = Canvas(960, 700,
               title="图 33-1　拆与不拆的决策树：四维评估 → 先优化 → 四种成因 → 四种解法",
               subtitle="只有「写入型」现在就通向水平拆分；「单表行数大」不是任何一条路的入口")

    dims = [
        ("① 容量", "倒数第二层多大", BLUE),
        ("② 写入", "占单机峰值比例", BLUE),
        ("③ 热点", "锁等待集中度", BLUE),
        ("④ 运维", "备份 / DDL / 恢复", BLUE),
    ]
    for i, (t, s, col) in enumerate(dims):
        c.box(40 + i * 230, 86, 190, 64, t, s, accent=col, size=13, sub_size=11)

    # 四道闸 → 先优化
    for i in range(4):
        cx = 135 + i * 230
        c.arrow((cx, 150), (cx, 176), color=SLATE, width=1.4, dash="4,3")

    c.container(40, 176, 880, 100, "先优化：五条都做完，才算过闸（每条的「做完」有可读指标）")
    ops = [
        ("索引治理", "top 20 无 filesort"),
        ("归档", "热表行数稳定"),
        ("读写分离", "主库读降到最低"),
        ("分区", "九成查询带键"),
        ("硬件", "BP 装满热数据"),
    ]
    for i, (t, s) in enumerate(ops):
        c.box(54 + i * 174, 214, 156, 48, t, s, accent=GREEN, size=11, sub_size=9)

    # 先优化 → 四种成因
    for i in range(4):
        cx = 135 + i * 230
        c.arrow((cx, 276), (cx, 316), color=SLATE, width=1.4, dash="4,3")

    causes = [
        ("容量型", "数据放不下", BLUE),
        ("写入型", "单机写满", ORANGE),
        ("热点型", "单行争用", RED),
        ("运维型", "窗口不够", PURPLE),
    ]
    for i, (t, s, col) in enumerate(causes):
        c.box(40 + i * 230, 316, 190, 56, t, s, accent=col, size=13, sub_size=11)

    for i in range(4):
        cx = 135 + i * 230
        c.arrow((cx, 372), (cx, 410), color=SLATE, width=1.4)

    fixes = [
        ("归档 → 分区", "水平拆是最后手段", BLUE),
        ("减写 → 垂直分库", "再算分片数", ORANGE),
        ("拆行 · 排队 · 异步", "水平拆分无效", RED),
        ("分区局部维护", "按业务域拆库", PURPLE),
    ]
    for i, (t, s, col) in enumerate(fixes):
        c.box(40 + i * 230, 410, 190, 84, t, s, accent=col, size=12, sub_size=11)

    c.legend(40, 508, [
        (GREEN, "已做过的优化（做完才允许往下走）", None),
        (SLATE, "评估与分流，不代表结论", "4,3"),
    ])

    # 被跳过的闸门
    c.container(40, 560, 880, 112, "被跳过的闸门：33.0 的来路")
    c.box(64, 596, 176, 50, "单表 12 亿行", accent=RED, size=12)
    c.arrow((240, 621), (392, 621), color=RED, width=1.8, dash="5,4")
    c.text(316, 606, "✗", size=18, fill=RED, anchor="middle", weight=700)
    c.box(392, 596, 208, 50, "直接分 1024 张表", accent=RED, size=12)
    c.text(618, 610, "跳过四维评估与五条优化，把行数当成唯一理由", size=11, fill=INK)
    c.text(618, 632, "结果：连接 × 1024、DDL 1024 次、查询广播 1024 次", size=10, fill=RED)
    return c.save(os.path.join(OUT, "ch33-fig1.svg"))


# ---------------------------------------------------------------- 图 33-2
def fig2():
    c = Canvas(960, 620,
               title="图 33-2　跨分片查询的三条路径：带分片键 / 不带分片键 / 绑定表 JOIN",
               subtitle="同一张 4 分片的订单表；绿色是只打开的分片，红色是广播出去的每一条 SQL")

    xs = [40, 360, 680]
    centers = [[x + 26 + i * 60 for i in range(4)] for x in xs]

    heads = [
        ("① 带分片键", "WHERE buyer_id = 8842", GREEN),
        ("② 不带分片键", "WHERE order_no = 'SO...'", RED),
        ("③ 绑定表 JOIN", "order_main ⋈ order_item", GREEN),
    ]
    for i, (t, s, col) in enumerate(heads):
        c.box(xs[i], 96, 240, 56, t, s, accent=col, size=12, sub_size=9)

    routers = ["路由：hash % 4", "无键可算 → 广播", "JOIN 键 = 分片键"]
    for i in range(3):
        cx = xs[i] + 120
        c.arrow((cx, 152), (cx, 184), color=GREEN if i != 1 else RED, width=1.6)
        c.box(cx - 78, 184, 156, 36, routers[i],
              accent=GREEN if i != 1 else RED, size=10)

    # 每个分片的四个小格子
    def shards(i, hot):
        for k in range(4):
            col = GREEN if k in hot else SLATE
            c.box(xs[i] + k * 60, 250, 52, 48, f"0{k}",
                  accent=col, size=12, r=6)
            if k not in hot:
                c.text(xs[i] + k * 60 + 26, 312, "未打开", size=9, fill=SUB,
                       anchor="middle")

    shards(0, {0})
    shards(1, {0, 1, 2, 3})
    shards(2, {2})

    # 路径 ①：只到 00
    cx = xs[0] + 120
    c.arrow([(cx, 220), (cx, 236)], color=GREEN, width=2.2, end=False)
    c.arrow([(cx, 236), (centers[0][0], 236)], color=GREEN, width=2.2, end=False)
    c.arrow((centers[0][0], 236), (centers[0][0], 250), color=GREEN, width=2.2)

    # 路径 ②：四条红色
    cx = xs[1] + 120
    c.arrow([(cx, 220), (cx, 236)], color=RED, width=2.0, end=False)
    c.arrow([(centers[1][0], 236), (centers[1][3], 236)], color=RED, width=2.0,
            end=False)
    for t in centers[1]:
        c.arrow((t, 236), (t, 250), color=RED, width=2.0)

    # 路径 ③：只到 02
    cx = xs[2] + 120
    c.arrow([(cx, 220), (cx, 236)], color=GREEN, width=2.2, end=False)
    c.arrow([(cx, 236), (centers[2][2], 236)], color=GREEN, width=2.2, end=False)
    c.arrow((centers[2][2], 236), (centers[2][2], 250), color=GREEN, width=2.2)

    cost = [
        ("代价：1 次查询", "另外 3 片完全没参与", GREEN),
        ("代价：N 次查询", "延迟 = 最慢的那一片", RED),
        ("代价：1 分片内 2 次查询", "JOIN 不跨网络", GREEN),
    ]
    for i, (t, s, col) in enumerate(cost):
        c.box(xs[i], 330, 240, 58, t, s, accent=col, size=12, sub_size=10)

    c.container(40, 412, 880, 104, "三条路的本质差别")
    c.text(60, 452, "带分片键：路由函数只算一次，SQL 改写成 1 条。它能成立的前提是查询里真的带了这个键。",
           size=11, fill=INK)
    c.text(60, 474, "不带键：SQL 被改写成 N 条并发下发，路由层等最慢的一片，N 越大 P99 越难看；分片数在这里是乘数。",
           size=11, fill=RED)
    c.text(60, 496, "绑定表：两张表同一个分片键、同一台机器，JOIN 回到单库执行——这是唯一不付额外代价的一条。",
           size=11, fill=GREEN)

    c.legend(40, 534, [
        (GREEN, "单分片命中：1 次路由、1 次查询", None),
        (RED, "广播：N 条 SQL、延迟由最慢分片决定", None),
    ])
    return c.save(os.path.join(OUT, "ch33-fig2.svg"))


# ---------------------------------------------------------------- 图 33-3
def fig3():
    c = Canvas(960, 680,
               title="图 33-3　双倍扩容：4 → 8 只有一半数据要动，以及双写迁移的六个闸",
               subtitle="h % 4 = i 的 key，在 h % 8 下只能是 i 或 i + 4；所以每个老分片正好一半留、一半走")

    def panel(x, label, tone, new_names, arrow_color, note):
        c.text(x, 112, label, size=12, fill=arrow_color, weight=600)
        c.raw(f'<path d="M {x} 122 L {x + 420} 122" stroke="{arrow_color}" '
              f'stroke-width="1.2" fill="none" stroke-dasharray="6,4"/>')
        for k in range(4):
            bx = x + 12 + k * 100
            c.box(bx, 138, 88, 54, f"order_0{k}", "老分片", accent=SLATE,
                  size=11, sub_size=9, r=6)
            c.box(bx, 310, 88, 54, new_names[k], "新分片", accent=tone,
                  size=11, sub_size=9, r=6)
            c.arrow((bx + 44, 192), (bx + 44, 310), color=arrow_color, width=1.8)
        c.text(x, 386, note, size=10, fill=arrow_color, weight=600)

    panel(40, "① 原地：h % 8 = i", GREEN,
          ["order_00", "order_01", "order_02", "order_03"], GREEN,
          "这 50% 的 key 不动，不产生任何复制流量")
    panel(500, "② 搬走：h % 8 = i + 4", ORANGE,
          ["order_04", "order_05", "order_06", "order_07"], ORANGE,
          "这 50% 的 key 要搬，双写窗口只覆盖这一半")

    c.text(40, 420, "任意 N → M 不行：模数一换，h % 7 与 h % 4 没有对应关系，几乎每个 key 都要重新落位——要搬的比例从 50% 变成接近 100%。",
           size=11, fill=SLATE)

    # 双写迁移六阶段
    c.text(40, 460, "双写迁移的六个阶段：每一步的校验点，就是进入下一步的闸", size=13,
           fill=INK, weight=600)

    stages = [
        ("① 双写", "新表成功率\n与老表持平"),
        ("② 搬历史", "行数\n分段对齐"),
        ("③ 追增量", "位点差\n归零"),
        ("④ 校验", "不一致\n行数 = 0"),
        ("⑤ 灰度切读", "错误率·P99\n两边一致率"),
        ("⑥ 停老写", "观察期\n后停写"),
    ]
    for i, (t, g) in enumerate(stages):
        bx = 52 + i * 145
        c.box(bx, 478, 128, 44, t, accent=ORANGE if i < 4 else GREEN,
              size=11, r=6)
        if i < 5:
            c.arrow((bx + 128, 500), (bx + 145, 500), color=SLATE, width=1.4)
        for j, line in enumerate(g.split("\n")):
            c.text(bx, 544 + j * 17, line, size=9, fill=SUB)

    c.container(40, 578, 880, 62, "")
    c.text(60, 610, "切读之前必须追平且校验通过：否则读走到新表、新表少一笔，同一个买家刷新两次会看到 3 笔和 4 笔——不报错，只涨工单。",
           size=11, fill=RED)
    return c.save(os.path.join(OUT, "ch33-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
