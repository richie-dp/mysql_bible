#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""附录 G 配图：实验环境的拓扑与数据流"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 G-1
def fig1():
    c = Canvas(960, 640,
               title="图 G-1　实验环境：三个容器、一条 binlog 流、一个装脚本的目录",
               subtitle="容器负责把机制跑出来；跑出来的数字不能当容量依据")

    # 宿主机：只有脚本和配置，没有数据
    c.container(48, 84, 320, 264, "宿主机　mysql_bible/labs")
    c.box(64, 120, 288, 52, "labs/",
          "compose · conf · seed · ch01/19/41/52", accent=SLATE,
          size=13, sub_size=9.2)
    c.box(64, 186, 300, 40, "conf/*.cnf　server-id · GTID · 只读",
          accent=SLATE, size=10.4)
    c.box(64, 232, 300, 40, "seed/*.sql　万级 / 千万 / 倾斜",
          accent=SLATE, size=10.4)
    c.box(64, 278, 300, 42, "chXX/*.sql　每章一份",
          "端口：3306 / 3307 / 3308 / 3309", accent=SLATE,
          size=10.4, sub_size=8.8)

    # 三个 8.0 容器
    c.box(520, 92, 392, 92, "mysql-master　宿主 3306",
          "server-id=1 · ROW binlog · GTID · pool 512M",
          accent=BLUE, size=13, sub_size=9.4)
    c.box(520, 236, 392, 78, "mysql-replica1　宿主 3307",
          "read_only · relay log · 4 个回放线程", accent=TEAL,
          size=13, sub_size=9.4)
    c.box(520, 334, 392, 78, "mysql-replica2　宿主 3308",
          "与 replica1 只差 server-id", accent=TEAL,
          size=13, sub_size=9.4)
    c.pill(520, 438, 392, 34,
           "mysql-57（可选）宿主 3309 · 只做版本对比", accent=SLATE, size=10.5)

    # conf 只读挂载：一份源，三处挂载
    c.arrow([(374, 206), (430, 206), (430, 168), (520, 168)],
            color=SLATE, dash="6,4", width=1.2)
    c.arrow([(374, 206), (430, 206), (430, 274), (520, 274)],
            color=SLATE, dash="6,4", width=1.2)
    c.arrow([(374, 206), (430, 206), (430, 372), (520, 372)],
            color=SLATE, dash="6,4", width=1.2)

    # binlog：主库一条流，两个从库各拉一份
    c.arrow(760, 184, 760, 236, color=PURPLE, width=1.8)
    c.arrow([(900, 184), (930, 184), (930, 354), (912, 354)],
            color=PURPLE, width=1.8)

    c.legend(48, 372, [(PURPLE, "binlog 复制流，GTID 自动定位", None),
                       (SLATE, "conf 只读挂载", "6,4")])

    # 能验什么
    c.container(48, 500, 420, 124, "容器里能验")
    c.text(64, 548, "· 页 / redo / undo / 锁 / MDL 的单机机制", size=9.6, fill=INK)
    c.text(64, 570, "· 主从复制、GTID、延迟的三段分解", size=9.6, fill=INK)
    c.text(64, 592, "· DDL 的 INSTANT / INPLACE 行为差异", size=9.6, fill=INK)
    c.text(64, 614, "· 附录 D 的诊断 SQL 与 p_s 视图", size=9.6, fill=INK)

    # 不能验什么
    c.container(492, 500, 420, 124, "容器里不能验")
    c.text(508, 548, "· 真实 IOPS 与 fsync 延迟（共享盘 + 虚拟化）", size=9.6, fill=RED)
    c.text(508, 570, "· 千万级数据的性能结论（CPU 是笔记本的）", size=9.6, fill=RED)
    c.text(508, 592, "· 云上代理、存储层、连接代理的行为", size=9.6, fill=RED)
    c.text(508, 614, "这三件事必须真机或云上验，容器数字不作容量依据",
           size=9.4, fill=SUB)
    return c.save(os.path.join(OUT, "appG-fig1.svg"))


if __name__ == "__main__":
    print(fig1())
