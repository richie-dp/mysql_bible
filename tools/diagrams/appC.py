#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""附录 C 配图：工具在数据生命周期里的位置"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")

STAGES = ["写入", "变更", "备份", "复制", "诊断", "接入"]
COLS = [48 + i * 152 for i in range(6)]

# (工具名, 它坏了会怎样, 风险色)
TOOLS = {
    0: [],
    1: [("gh-ost", "坏了：变更卡住", ORANGE),
        ("pt-osc", "坏了：写入变慢", ORANGE),
        ("pt-table-checksum", "坏了：差异没发现", SLATE)],
    2: [("XtraBackup", "坏了：恢复不出来", RED),
        ("mysqlbinlog", "坏了：点恢复不对", RED),
        ("Clone", "坏了：加从库失败", ORANGE)],
    3: [("orchestrator", "坏了：不会自动切", ORANGE),
        ("MHA", "坏了：切换靠人", ORANGE),
        ("ProxySQL", "坏了：全部连不上", ORANGE),
        ("pt-heartbeat", "坏了：延迟看不见", SLATE)],
    4: [("pt-query-digest", "坏了：看不出热点", SLATE),
        ("innotop", "坏了：只能敲 SHOW", SLATE),
        ("mysqld_exporter", "坏了：没有趋势", SLATE),
        ("PMM", "坏了：曲线断一截", SLATE)],
    5: [("ShardingSphere", "坏了：SQL 走错片", RED),
        ("Canal", "坏了：下游缺数", RED),
        ("Debezium", "坏了：下游断流", RED),
        ("MaxScale", "坏了：连不上库", ORANGE)],
}


def fig1():
    c = Canvas(960, 720,
               title="图 C-1　工具在数据生命周期里的位置",
               subtitle="主干是数据流经的六个环节；颜色是它坏了以后，伤在哪一层")

    # ---- 环节胶囊 + 主干
    for x, name in zip(COLS, STAGES):
        c.pill(x, 96, 112, 34, name, accent=BLUE, size=11.5)
    c.arrow(48, 150, 912, 150, color=BLUE, width=2)
    for x in COLS:
        c.arrow((x + 56, 132), (x + 56, 148), color=BLUE, width=1.2, end=False)

    # ---- 每一列的地基
    for x in COLS:
        c.rect(x - 4, 160, 120, 230, fill=FAINT, stroke="#eef2f7", sw=1, r=10)

    # ---- 写入：故意留空
    c.rect(48, 172, 112, 44, fill=BG, stroke="#cbd5e1", sw=1.2, r=8, dash="5,4")
    c.text(104, 192, "无第三方组件", size=9.5, anchor="middle", weight=600)
    c.text(104, 208, "写路径上不插组件", size=8.5, anchor="middle", fill=SUB)
    c.text(104, 250, "空着是对的", size=9, anchor="middle", fill=SLATE)

    # ---- 各环节的工具
    for i, items in TOOLS.items():
        for j, (name, risk, col) in enumerate(items):
            c.box(COLS[i], 172 + j * 54, 112, 44, name, risk,
                  accent=col, size=9.5, sub_size=8.5)

    # ---- 底部：三种后果
    c.text(48, 418, "同一句「挂了」，在六个环节里的后果完全不同：",
           size=12, fill=INK, weight=600)

    risks = [
        (RED, "写坏数据 / 回不来", "变更、备份、同步：出事那天才发现"),
        (ORANGE, "暂时不可用", "复制、路由：告警会响，切完就好"),
        (SLATE, "只是看不见", "诊断：不响，等你从业务报错里发现"),
    ]
    for k, (col, title, sub) in enumerate(risks):
        c.box(48 + k * 302, 434, 260, 68, title, sub,
              accent=col, size=12, sub_size=10)

    c.text(48, 534, "颜色往右（SLATE）的可以晚上线、可以少人维护；颜色往左（RED）的必须有人值班、必须有演练。",
           size=11, fill=INK)
    c.text(48, 556, "位置越靠近接入与同步，一次故障波及的请求比例越高 —— 这是 ProxySQL 与一个定时校验脚本的根本差别。",
           size=11, fill=SUB)

    c.container(48, 584, 864, 88, "")
    c.text(68, 616, "越往右，故障面越大：诊断工具挂了，你失去的是视野；接入层挂了，你失去的是全部请求。",
           size=11, fill=INK)
    c.text(68, 640, "所以左边两段可以容忍「用得少」，右边两段必须有人随时知道它现在是什么状态。",
           size=11, fill=INK)
    return c.save(os.path.join(OUT, "appC-fig1.svg"))


if __name__ == "__main__":
    print(fig1())
