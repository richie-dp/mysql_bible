#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 29 章配图：数据类型与字符集"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 29-1
def fig1():
    c = Canvas(960, 480,
               title="图 29-1　一行订单记录的字节布局：行内 83 字节，TEXT 只剩指针",
               subtitle="DYNAMIC 行格式、utf8mb4、所有列 NOT NULL（NULL 位图 0 字节）；取 order_no 为 14 字节 ASCII")

    c.container(40, 82, 880, 150,
                "主键页内的一条记录（记录头 → 长度列表 → 列数据 → 隐藏列）")

    widths = [72, 84, 74, 100, 104, 84, 92, 104]
    labels = ["记录头", "变长长度列表", "id", "amount", "order_no",
              "remark", "created_at", "隐藏列"]
    types = ["5 B", "4 B", "BIGINT", "DECIMAL(18,2)", "VARCHAR(64)",
             "TEXT", "DATETIME(6)", "DB_TRX_ID"]
    subs = ["状态位", "2 + 2", "8 B", "9 B", "2 + 14 B",
            "20 B 指针", "8 B", "+ ROLL_PTR 13B"]

    x = 58
    for i, w in enumerate(widths):
        c.text(x + w / 2, 118, labels[i], size=10, fill=SUB, anchor="middle")
        c.box(x, 126, w, 80, types[i], subs[i], accent=PURPLE,
              size=9, sub_size=9)
        x += w + 18

    # 20 字节指针 → 溢出页
    c.arrow([(624, 206), (624, 300), (760, 300), (760, 330)],
            color=PURPLE, width=2.0)
    c.text(632, 292, "20 字节指针", size=11, fill=PURPLE, weight=600)

    c.container(40, 262, 500, 170, "行内长度与\"会不会读溢出页\"是两件事")
    c.text(56, 310, "行内合计 83 字节：5 + 4 + 8 + 9 + 16 + 20 + 8 + 13。",
           size=12, fill=INK)
    c.text(56, 336, "16KB 页可用约 16256 字节，一页装得下约 195 行。",
           size=12, fill=INK)
    c.text(56, 362, "remark 写多长，行内都是 20 字节——溢出页独立分配。",
           size=12, fill=INK)
    c.text(56, 388, "SELECT * 每行多一次随机 IO，慢在跳转不在行数。",
           size=12, fill=INK)
    c.text(56, 414, "退回 COMPACT + VARCHAR(8000)：行宽 851 字节，一页 19 行。",
           size=12, fill=RED)

    c.box(620, 330, 280, 96, "remark 的溢出页",
          "独立 BLOB 页，物理上不与主键页相邻", accent=PURPLE, size=13, sub_size=11)
    return c.save(os.path.join(OUT, "ch29-fig1.svg"))


# ---------------------------------------------------------------- 图 29-2
def fig2():
    c = Canvas(960, 560,
               title="图 29-2　DATETIME 存字面量，TIMESTAMP 存 UTC 再按会话还原",
               subtitle="同一行数据、同一条 SELECT，两个 time_zone 会话看到的字符串不同")

    # 左：DATETIME
    c.container(40, 88, 420, 380, "DATETIME：存什么读什么（5 字节）")
    c.box(80, 130, 340, 62, "会话 A  time_zone = '+08:00'",
          "INSERT '2026-11-12 10:00:00'", accent=BLUE, size=12, sub_size=10)
    c.box(80, 232, 340, 62, "列值 '2026-11-12 10:00:00'",
          "5 字节，不带任何时区信息", accent=PURPLE, size=12, sub_size=10)
    c.box(80, 334, 340, 62, "会话 B  time_zone = '+00:00' 读",
          "还是 '2026-11-12 10:00:00'", accent=BLUE, size=12, sub_size=10)
    c.arrow((250, 192), (250, 232), color=BLUE, width=1.6)
    c.arrow((250, 294), (250, 334), color=BLUE, width=1.6)
    c.text(80, 428, "两个会话读到同一个字符串，但它对应的绝对时刻相差 8 小时。",
           size=12, fill=RED)
    c.text(80, 450, "跨时区协作时，\"10 点\"到底是哪儿的 10 点，只能靠人约定。",
           size=12, fill=SUB)

    # 右：TIMESTAMP
    c.container(480, 88, 440, 380, "TIMESTAMP：写时转 UTC，读时按会话还原（4 字节）")
    c.box(520, 122, 360, 56, "会话 A（+08:00）写入",
          "'2026-11-12 10:00:00'", accent=BLUE, size=12, sub_size=10)
    c.box(520, 202, 360, 56, "转成 UTC：2026-11-12 02:00:00",
          "按会话时区减 8 小时", accent=ORANGE, size=12, sub_size=10)
    c.box(520, 282, 360, 56, "存 4 字节 epoch",
          "内部是 UTC 秒，与任何时区无关", accent=PURPLE, size=12, sub_size=10)
    c.box(520, 362, 360, 56, "会话 B（+00:00）读出",
          "'2026-11-12 02:00:00'", accent=BLUE, size=12, sub_size=10)
    c.arrow((700, 178), (700, 202), color=ORANGE, width=1.8)
    c.arrow((700, 258), (700, 282), color=ORANGE, width=1.8)
    c.arrow((700, 338), (700, 362), color=ORANGE, width=1.8)
    c.text(520, 444, "同一条记录看到不同值，是设计意图，不是 bug。",
           size=12, fill=GREEN)

    c.text(40, 504,
           "反过来才危险：两个会话写入同一个字面量，TIMESTAMP 落成两个绝对时刻，DATETIME 落成同一个字符串。",
           size=12, fill=INK)
    c.text(40, 528,
           "选哪个不取决于谁更省 1 字节，取决于这一列的语义是\"绝对时刻\"还是\"墙上时间\"，以及 2038 年要不要迁移。",
           size=12, fill=SUB)
    return c.save(os.path.join(OUT, "ch29-fig2.svg"))


# ---------------------------------------------------------------- 图 29-3
def fig3():
    c = Canvas(960, 620,
               title="图 29-3　字符集的四级继承与连接三级：哪一级没对齐，坏在哪",
               subtitle="建库建表不写字符集，就一路继承；列上写死，继承链在这里断掉")

    # 左：四级继承
    c.container(40, 88, 400, 350, "四级继承：不写就往下继承")
    levels = [
        ("character_set_server", "utf8mb4 —— 新库的默认值"),
        ("database", "建库没写 → 继承 server"),
        ("table", "建表没写 → 继承库"),
        ("column", "列上写死 utf8mb3 → 链在这里断"),
    ]
    y = 126
    for i, (name, note) in enumerate(levels):
        accent = RED if i == 3 else BLUE
        c.box(64, y, 352, 58, name, note, accent=accent, size=12, sub_size=10)
        if i < 3:
            c.arrow((240, y + 58), (240, y + 82), color=SLATE, width=1.4, dash="4,3")
        y += 82

    # 右：连接三级
    c.container(480, 88, 440, 350, "连接三级：SET NAMES 一次改三个")
    conns = [
        ("character_set_client", "服务端按它解释客户端发来的字节"),
        ("character_set_connection", "字面量按它解析，比较前按它转换"),
        ("character_set_results", "返回给客户端的字节按它编码"),
    ]
    y = 126
    for i, (name, note) in enumerate(conns):
        c.box(510, y, 380, 58, name, note, accent=BLUE, size=12, sub_size=10)
        if i < 2:
            c.arrow((700, y + 58), (700, y + 80), color=SLATE, width=1.4, dash="4,3")
        y += 80
    c.text(510, 392, "SET NAMES utf8mb4 等价于同时设这三个变量。",
           size=12, fill=GREEN)
    c.text(510, 416, "写死其中任何一个，乱码就挪到另一个环节去。",
           size=12, fill=SUB)

    # 底部：三种坏法与一条对齐
    c.container(40, 462, 880, 128, "对不齐的三种后果，以及唯一的安全姿势")
    c.text(56, 502, "乱码 A：character_set_client 与真实字节不符 → 双重编码，存进去的数据本身就是错的。",
           size=12, fill=RED)
    c.text(56, 526, "乱码 B：character_set_results 与客户端期望不符 → 数据是对的，显示是坏的（用 HEX() 区分）。",
           size=12, fill=RED)
    c.text(56, 550, "索引失效：JOIN 两侧列的字符集或 collation 不同，转换落在被驱动列上，B+ 树给不出序（第 9 章）。",
           size=12, fill=RED)
    c.text(56, 574, "对齐：server → 库 → 表 → 列 全用 utf8mb4；连接三件套用 SET NAMES utf8mb4 一次设齐。",
           size=12, fill=GREEN)
    return c.save(os.path.join(OUT, "ch29-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
