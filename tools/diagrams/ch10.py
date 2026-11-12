#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 10 章配图：统计信息与成本模型"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 10-1
def fig1():
    c = Canvas(960, 720,
               title="图 10-1　优化器的决策链：五步，每步只依赖有限的几个数",
               subtitle="左边是它做的事，右边是它做这件事时唯一能看到的信息；看不到的，只能靠假设")

    c.container(40, 84, 536, 556, "决策链（自上而下，逐层收窄）")
    c.container(596, 84, 324, 556, "这一步依赖的统计值", fill="#ffffff", stroke="#e5e7eb")

    steps = [
        ("① 枚举候选索引", "potential_range_indexes",
         "索引定义 + WHERE 的列", "只看「能不能用」，不看数据长什么样"),
        ("② 每个候选估行数", "range_analysis / analyze_range",
         "n_diff 与表行数", "估计值 = n_rows ÷ n_diff × 过滤率"),
        ("③ 叠加回表、排序、LIMIT", "best_access_path",
         "rows × io_block_read_cost", "回表按「每行一次块读」计价"),
        ("④ 逐个比总成本", "considered_execution_plans",
         "server_cost / engine_cost", "8 个常数决定「谁更贵」"),
        ("⑤ 选定并产出计划", "chosen = 1",
         "到此为止，没有别的输入了", "选错了只能靠 trace 回放它的推理"),
    ]

    ys = [116, 222, 328, 434, 540]
    for i, (t, sub, dep, note) in enumerate(steps):
        y = ys[i]
        c.box(64, y, 488, 62, t, sub, accent=(RED if i == 4 else BLUE),
              size=14, sub_size=10, mono=False)
        c.box(612, y, 292, 62, dep, note, accent=SLATE, size=11, sub_size=9.5)

        # 决策链：竖向主流程
        if i < 4:
            c.arrow((308, y + 62), (308, ys[i + 1]), color=BLUE, width=1.8)
        # 依赖关系：横向虚线，只表示「读了这个数」
        c.arrow((552, y + 31), (612, y + 31), color=SLATE, width=1.2, dash="4,3")

    c.legend(40, 668, [(BLUE, "决策流程", None), (SLATE, "读取某个统计值 / 成本常数", "4,3")])
    c.text(560, 668, "成本单位无量纲：1.0 只表示「一个磁盘块读」，不等于 1 毫秒",
           size=11, fill=SUB)
    return c.save(os.path.join(OUT, "ch10-fig1.svg"))


# ---------------------------------------------------------------- 图 10-2
def fig2():
    c = Canvas(960, 700,
               title="图 10-2　倾斜数据下，基数与真实分布是两回事",
               subtitle="示例：480 万行的订单表 / 2050 个商户；数值只表达量级，不是实测")

    # ① 真实分布
    c.container(40, 84, 880, 266, "① 真实分布：一根尖刺 + 一条长尾（月底结算的连锁商户）")
    base = 314
    c.rect(88, base, 796, 1.2, fill=LINE, stroke=LINE, sw=0, r=0)
    c.text(48, 132, "行数", size=11, fill=SUB)
    c.text(48, 150, "（示意）", size=9, fill=SUB)

    heights = [14, 10, 168, 18, 9, 12, 8, 16, 20, 10, 13, 11, 8, 12]
    hot = 2
    for i, h in enumerate(heights):
        x = 100 + i * 54
        is_hot = (i == hot)
        c.rect(x, base - h, 34, h,
               fill=("#fee2e2" if is_hot else "#dbeafe"),
               stroke=(RED if is_hot else "#93c5fd"), sw=1.2, r=3)
    c.text(100 + hot * 54 + 17, base + 18, "8842", size=11, fill=RED,
           anchor="middle", weight=600)
    c.text(100 + hot * 54 + 17, base - 168 - 10, "60%", size=11, fill=RED,
           anchor="middle", weight=600)

    c.text(600, 146, "其余 2049 个商户合计 40%", size=12, fill=INK)
    c.text(600, 170, "单商户平均不到 0.05%（约 900 行）", size=11, fill=SUB)
    c.text(600, 194, "「平均每个商户 2340 行」这句话", size=11, fill=RED)
    c.text(600, 214, "对这张表不成立", size=11, fill=RED)

    # ② 优化器脑中的分布
    c.container(40, 366, 420, 238, "② 优化器脑中的分布（dive 退场后）")
    c.rect(62, 480, 370, 1.2, fill=LINE, stroke=LINE, sw=0, r=0)
    for i in range(14):
        c.rect(62 + i * 26, 480 - 28, 20, 28, fill="#e2e8f0",
               stroke="#94a3b8", sw=1.1, r=3)
    c.text(62, 508, "480 万 ÷ 2050 ≈ 2340 行 / 商户", size=11, fill=INK)
    c.text(62, 532, "对 8842：低估约 1200 倍", size=11, fill=RED)
    c.text(62, 556, "对小商户：高估 2~3 倍", size=11, fill=RED)
    c.text(62, 580, "等值单查会走 index dive，那时用不上这一步", size=10, fill=SUB)

    # ③ 20 页采样
    c.container(500, 366, 420, 238, "③ n_diff 从哪来：20 个叶子页")
    for i in range(20):
        row, col = divmod(i, 10)
        x, y = 520 + col * 37, 410 + row * 34
        hot_page = i < 12
        c.rect(x, y, 28, 22,
               fill=("#fee2e2" if hot_page else "#dbeafe"),
               stroke=(RED if hot_page else "#93c5fd"), sw=1.1, r=3)
    c.text(520, 490, "20 页 × 80 行 = 1600 行，要估 480 万行", size=11, fill=INK)
    c.text(520, 513, "两次 ANALYZE：1800 / 2600（示例）", size=11, fill=INK)
    c.text(520, 536, "真实 2050 —— 误差两三成", size=11, fill=INK)
    c.text(520, 559, "这点误差，解释不了 1200 倍", size=11, fill=RED)
    c.text(520, 582, "真正的错在下一步：拿它做除法", size=11, fill=RED)

    c.text(40, 654, "n_diff 只差两三成，但用它做除法，把 60% 的行摊成了 0.05%——"
                    "选错计划的地方在这里，不在采样精度。", size=12, fill=INK)
    return c.save(os.path.join(OUT, "ch10-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
