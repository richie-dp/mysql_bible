#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 45 章配图：云原生架构与选型"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *  # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 45-1
def fig1():
    c = Canvas(960, 680,
               title="图 45-1　两种架构的写入路径：网络上运的东西变了",
               subtitle="上半：页在两地各写一次；下半：只有日志记录进网络，页由存储层物化")

    # ---- 上半：自建主从
    c.container(40, 78, 880, 246, "① 自建主从：一次提交，两份完整数据页")

    c.box(64, 118, 170, 72, "主库", "改页 → redo → binlog", accent=BLUE)
    c.cyl(64, 214, 170, 74, "主库数据盘", "整份数据 + redo", accent=GREEN)
    c.box(420, 118, 170, 72, "从库", "收 binlog 再执行一遍", accent=BLUE)
    c.cyl(420, 214, 170, 74, "从库数据盘", "另一份完整数据", accent=GREEN)

    c.arrow((149, 190), (149, 214), color=GREEN)
    c.arrow((505, 190), (505, 214), color=GREEN)
    c.arrow((234, 154), (420, 154), color=PURPLE, label="binlog（逻辑事件）")

    c.box(650, 118, 240, 100, "写放大 = 页", "页 16KB，两地各落一次盘",
          accent=RED, size=13, sub_size=10.5)
    c.text(650, 244, "从库持有第二份完整数据，", size=11, fill=SUB)
    c.text(650, 264, "扩容 = 全量拷贝 + 追增量", size=11, fill=SUB)

    # ---- 下半：存算分离
    c.container(40, 350, 880, 256, "② 存算分离：网络上传的只有 redo 记录，页由存储层物化")

    c.box(64, 394, 180, 76, "主计算节点", "只发 redo，不写页", accent=BLUE)
    c.box(304, 394, 180, 76, "只读计算节点", "回放同一份日志", accent=BLUE)
    c.box(650, 394, 260, 76, "单 AZ 故障不影响写",
          "4/6 与 3/6 的法定人数", accent=GREEN, size=12, sub_size=10)

    c.cyl(64, 528, 560, 66, "共享存储卷 · 6 副本 / 3 个可用区", "写需 4/6 确认 · 读需 3/6 确认",
          accent=PURPLE)

    c.arrow((154, 470), (154, 528), color=PURPLE, label="redo 记录")
    c.arrow((394, 470), (394, 528), color=PURPLE, label="读页并回放")

    c.text(650, 500, "只读副本延迟的组成", size=11.5, fill=INK, weight=600)
    c.text(650, 520, "自建：回放线程追不追得上", size=10.5, fill=SUB)
    c.text(650, 538, "共享存储：日志何时到达", size=10.5, fill=SUB)
    c.text(650, 560, "后者与算力无关（第 25 章失效）", size=10.5, fill=SUB)

    c.legend(64, 620, [(GREEN, "数据页（整份副本）", None)])
    c.legend(300, 620, [(PURPLE, "日志记录 / redo", None)])
    c.legend(520, 620, [(BLUE, "计算节点", None)])

    return c.save(os.path.join(OUT, "ch45-fig1.svg"))


# ---------------------------------------------------------------- 图 45-2
def fig2():
    c = Canvas(960, 640,
               title="图 45-2　选型的四维矩阵与三条硬判断",
               subtitle="先定位自己在哪个象限，再用右侧三句话把自己拉回来")

    # ---- 坐标轴
    c.arrow((100, 512), (590, 512), color=SLATE)
    c.arrow((100, 512), (100, 116), color=SLATE)
    c.text(96, 124, "延迟敏感", size=11, fill=SUB, anchor="end")
    c.text(96, 506, "吞吐密集", size=11, fill=SUB, anchor="end")
    c.text(108, 532, "单机", size=11, fill=SUB)
    c.text(582, 532, "分布式", size=11, fill=SUB, anchor="end")
    c.text(345, 554, "扩展方式：单机 → 分布式", size=11, fill=SUB, anchor="middle")

    # ---- 四个象限
    c.box(140, 150, 200, 118, "单机 · 延迟敏感", "订单、支付、库存扣减",
          accent=BLUE, size=12.5, sub_size=10)
    c.text(240, 290, "默认起点：索引 → 归档 → 读写分离", size=10.5, fill=SUB, anchor="middle")

    c.box(370, 150, 200, 118, "分布式 · 延迟敏感", "每一跳都要跨节点协调",
          accent=RED, size=12.5, sub_size=10)
    c.text(470, 290, "代价最高：扩展性与低延迟互斥", size=10.5, fill=SUB, anchor="middle")

    c.box(140, 350, 200, 118, "单机 · 吞吐密集", "报表、结算批处理",
          accent=ORANGE, size=12.5, sub_size=10)
    c.text(240, 490, "只读副本 + 归档 + 列存通常够用", size=10.5, fill=SUB, anchor="middle")

    c.box(370, 350, 200, 118, "分布式 · 吞吐密集", "写入总量超过单机上限",
          accent=TEAL, size=12.5, sub_size=10)
    c.text(470, 490, "分片键选错，查询退回广播", size=10.5, fill=SUB, anchor="middle")

    # ---- 右侧三条硬判断
    c.box(620, 130, 300, 120, "① 单机装不装得下", "倒数第二层能否常驻内存（第 33 章）",
          accent=BLUE, size=13, sub_size=10)
    c.box(620, 280, 300, 120, "② 钱会不会错", "先看单机 + 半同步能否 RPO = 0",
          accent=GREEN, size=13, sub_size=10)
    c.box(620, 430, 300, 120, "③ 凌晨三点谁上线", "团队能力权重最高，它决定 MTTR",
          accent=RED, size=13, sub_size=10)

    c.box(620, 580, 300, 48, "装不下才分布式，单条慢先加索引",
          accent=SLATE, size=11.5)

    c.legend(60, 600, [(BLUE, "默认路径", None)])
    c.legend(170, 600, [(ORANGE, "需要额外手段", None)])
    c.legend(330, 600, [(RED, "代价最高", None)])
    c.legend(470, 600, [(TEAL, "规模驱动", None)])

    return c.save(os.path.join(OUT, "ch45-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
