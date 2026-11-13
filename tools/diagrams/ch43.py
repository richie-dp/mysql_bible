#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 43 章配图：升级与迁移"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 43-1
def fig1():
    c = Canvas(960, 680,
               title="图 43-1　升级路径只有一条，迁移方式有三条",
               subtitle="上半：能走的版本路线与每跳的门槛；下半：三种迁移方式在「跨版本」与「可回滚」上的硬边界")

    # ---------------- 上半：版本路径
    c.container(40, 76, 880, 200, "① 版本路径：唯一受支持的路线是 5.6 → 5.7 → 8.0 → 8.4")

    vers = [
        ("MySQL 5.6", "起点：.frm + MyISAM"),
        ("MySQL 5.7", "过渡：原生 JSON / GTID"),
        ("MySQL 8.0", "换字典：mysql.ibd"),
        ("MySQL 8.4", "同代：8.x 字典不变"),
    ]
    xs = [60, 265, 470, 675]
    for (title, sub), x in zip(vers, xs):
        c.box(x, 128, 150, 58, title, sub, accent=BLUE, size=12.5, sub_size=9.5)

    c.arrow((210, 157), (265, 157), color=BLUE, label="必升")
    c.arrow((415, 157), (470, 157), color=BLUE, label="必升")
    c.arrow((620, 157), (675, 157), color=GREEN, label="可直升")

    c.arrow((135, 214), (545, 214), color=RED, dash="6,4", end=False)
    c.text(340, 206, "✗ 跳过 5.7：8.0 没有 5.6 字典的转换路径",
           size=11, fill=RED, anchor="middle", weight=600)
    c.text(340, 242, "每一跳都能停、能全备、能回退到上一跳", size=11, fill=SUB, anchor="middle")
    c.text(900, 242, "5.7 也不能直接到 8.4", size=11, fill=SUB, anchor="end")

    # ---------------- 下半：三种迁移方式
    c.container(40, 316, 880, 320, "② 三种迁移方式：能不能跨版本、能不能回滚、停多久")

    cols = [
        (60, "逻辑导入", "mysqldump / util.dumpInstance", BLUE),
        (354, "物理拷贝", "xtrabackup / Clone 插件", SLATE),
        (648, "复制滚动", "新版本挂成从库，再切", PURPLE),
    ]
    for x, head, sub, col in cols:
        c.box(x, 356, 252, 46, head, sub, accent=col, size=13, sub_size=9.5)

    rows = [
        [
            ("跨大版本", "可以：导出的 SQL 与版本无关", GREEN),
            ("可回滚", "不行：重来一遍，小时级", RED),
            ("停机量级", "小时级：导入期间不可写", ORANGE),
        ],
        [
            ("跨大版本", "不行：页格式绑定版本", RED),
            ("可回滚", "只能回到备份点，丢增量", RED),
            ("停机量级", "十分钟级：按页拷", ORANGE),
        ],
        [
            ("跨大版本", "可以向上，只进不退", GREEN),
            ("可回滚", "可以：改一次指向", GREEN),
            ("停机量级", "秒级：一次主从切换", ORANGE),
        ],
    ]
    ys = [430, 492, 554]
    for ci, (x, _h, _s, _c) in enumerate(cols):
        for ri, (title, sub, col) in enumerate(rows[ci]):
            c.box(x, ys[ri], 252, 50, title, sub, accent=col, size=12, sub_size=9.5)

    c.text(54, 622, "只有第三列在出错之后还有退路——这是滚动升级成为生产默认的原因，不是速度。",
           size=11.5, fill=INK)

    c.legend(60, 652, [(GREEN, "可回退 / 可跨版本", None)])
    c.legend(280, 652, [(RED, "不可逆 / 不行", None)])
    c.legend(470, 652, [(PURPLE, "复制链路", None)])
    c.legend(620, 652, [(ORANGE, "停机窗口", None)])
    c.legend(760, 652, [(SLATE, "物理拷贝", None)])
    return c.save(os.path.join(OUT, "ch43-fig1.svg"))


# ---------------------------------------------------------------- 图 43-2
def fig2():
    c = Canvas(960, 640,
               title="图 43-2　复制滚动升级的时序：可回退的窗口到切换那一刻为止",
               subtitle="三条泳道自上而下推进；红线以上的每一步出事都能改指向回旧主，红线以下只能恢复备份")

    lanes = [
        (40, "泳道 1｜旧主 5.7", "切换前唯一的写入点", PURPLE, 58),
        (360, "泳道 2｜新从 8.0", "先只读，再提升为主", BLUE, 378),
        (680, "泳道 3｜流量入口", "连接串 / VIP / 中间件", SLATE, 698),
    ]
    for x, label, cap, col, _bx in lanes:
        c.container(x, 80, 240, 516, label, label_color=col)
        c.text(x + 14, 122, cap, size=10.5, fill=SUB)

    W, H = 204, 42

    def bx(lane, y, title, sub, accent):
        c.box(lanes[lane][4], y, W, H, title, sub, accent=accent, size=12, sub_size=9.5)

    # ① 挂新从库
    bx(0, 137, "① 继续对外服务", "5.7 现状不动", PURPLE)
    bx(1, 137, "② 8.0 实例就绪", "Clone 或全备 + binlog", BLUE)
    c.arrow((262, 158), (378, 158), color=PURPLE, label="建链")

    # ② 追平延迟
    bx(0, 201, "binlog 持续写入", "旧主仍是唯一写入点", PURPLE)
    bx(1, 201, "③ 追平延迟", "Seconds_Behind_Source 归零", PURPLE)
    c.arrow((262, 222), (378, 222), color=PURPLE, label="追平")

    c.text(58, 312, "旧主不改配置，", size=10.5, fill=SUB)
    c.text(58, 330, "随时可把流量切回来", size=10.5, fill=SUB)

    # ③ 只读业务切换
    bx(1, 265, "承接只读流量", "先只读，随时可切回", BLUE)
    bx(2, 265, "④ 只读业务切换", "报表 / 导出 / 对账", BLUE)
    c.arrow((698, 286), (582, 286), color=BLUE, label="切读")

    c.text(698, 186, "业务无感：", size=10.5, fill=SUB)
    c.text(698, 204, "新从不接线上流量", size=10.5, fill=SUB)

    # ④ 观察窗口
    bx(1, 329, "只读承载中", "看慢查询与错误日志", ORANGE)
    bx(2, 329, "⑤ 观察窗口", "跨一次日结，比对结果集", ORANGE)

    # 回滚点
    c.arrow((60, 400), (900, 400), color=RED, dash="6,4", end=False)
    c.text(480, 392, "回滚点｜线以上改指向即可，线以下要恢复备份",
           size=11, fill=RED, anchor="middle", weight=600)

    # ⑤ 提升
    bx(0, 415, "置为只读", "冻结数据，不再挂回链路", SLATE)
    bx(1, 415, "⑥ 提升为主库", "read_only = OFF", BLUE)
    bx(2, 415, "⑦ 写流量切换", "停写 → 追平 → 改指向", BLUE)
    c.arrow((698, 436), (582, 436), color=BLUE, label="切写")

    # ⑥ 观察与收尾
    bx(0, 479, "回滚副本保留", "观察期满再下线", GREEN)
    bx(1, 479, "⑧ 重建复制拓扑", "其余从库改挂新主", PURPLE)
    bx(2, 479, "⑨ 观察 24 小时", "延迟 / 慢查询 / 报错", ORANGE)

    bx(1, 535, "⑩ 下一台继续", "一轮只动一台", BLUE)
    c.text(698, 548, "一轮只动一台实例，", size=10.5, fill=SUB)
    c.text(698, 566, "观察满 24 小时再动下一台", size=10.5, fill=SUB)

    c.legend(60, 612, [(RED, "回滚点", "6,4")])
    c.legend(180, 612, [(PURPLE, "复制链路", None)])
    c.legend(320, 612, [(BLUE, "切换到新版本", None)])
    c.legend(490, 612, [(ORANGE, "观察窗口", None)])
    c.legend(640, 612, [(GREEN, "可回退副本", None)])
    return c.save(os.path.join(OUT, "ch43-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
