#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 42 章配图：MySQL 8.0 / 8.4 关键特性"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 42-1
def fig1():
    c = Canvas(960, 720,
               title="图 42-1　会让旧结论失效的特性矩阵",
               subtitle="每一格只回答一件事：读完它，你手上哪个“以前这么做是对的”要改")

    groups = [
        # (x, y, 容器标题, 主色, 特性, 备注)
        (40, 84, "① 数据字典：元数据搬了家", BLUE, [
            ("原子 DDL", "[8.0]", "DDL 崩溃留半张表", "结构变更与引擎同生共死"),
            ("I_S 不再读 .frm", "[8.0]", "小表多的库元数据慢", "改查 DD 表，毫秒级"),
            ("ibd2sdi", "替代 .frm", "拷 .frm 就能修表", "只能从 .ibd 抽 SDI"),
        ], "代价：mysql.ibd 成了核心；SHOW TABLE STATUS 带 86400 秒缓存"),
        (500, 84, "② 执行器：算法与语义各变一次", BLUE, [
            ("Hash Join", "[8.0.18+]", "无索引 join 必打满 CPU", "建表 + 探测，O(N+M)"),
            ("GROUP BY", "8.0 起不隐式排序", "GROUP BY 顺带排好序", "顺序不保证，分页错行"),
            ("LATERAL 派生表", "[8.0.14]", "FROM 里不能引用外层", "能写，但按外层行数放大"),
        ], "Hash Join 省的是内层重复扫描，驱动表全扫一分没少"),
        (40, 382, "③ 索引：四件武器，四种代价", GREEN, [
            ("降序索引", "[8.0]", "DESC 只是被忽略的语法", "混向排序才真的有用"),
            ("不可见索引", "[8.0]", "验证能否删只能先删", "INVISIBLE 一周再 DROP"),
            ("函数索引", "[8.0.13+]", "列上套函数必然全扫", "表达式一字不差才命中"),
            ("多值索引", "[8.0.17+]", "JSON 数组包含只能全扫", "一项对多键，写入放大"),
        ], None),
        (500, 382, "④ 认证：升级当天的头号故障", RED, [
            ("caching_sha2", "[8.0] 默认", "建连只有一次往返", "首认证要 RSA 或 TLS"),
            ("老驱动", "Connector/J 5.x", "驱动不动也能连上", "报插件无法加载"),
            ("native 插件", "[8.4] 默认禁用", "应急可改回 native", "要显式开启才能用"),
        ], "先摸清所有连接方的驱动版本，比升级完再逐个报错便宜"),
    ]

    for gx, gy, label, col, items, note in groups:
        c.container(gx, gy, 420, 286, label, label_color=col)
        h = 50 if len(items) == 4 else 54
        pitch = 58 if len(items) == 4 else 66
        for i, (title, ver, old, new) in enumerate(items):
            ry = gy + 40 + i * pitch
            c.box(gx + 14, ry, 148, h, title, ver, accent=col,
                  size=11, sub_size=9.5)
            c.text(gx + 176, ry + 21, "旧 " + old, size=10.5, fill=SLATE)
            c.text(gx + 176, ry + 41, "新 " + new, size=10.5, fill=INK, weight=600)
        if note:
            c.text(gx + 14, gy + 256, note, size=10, fill=SUB)

    c.legend(40, 692, [(BLUE, "主流程 / 新事实", None)])
    c.legend(240, 692, [(GREEN, "索引路径", None)])
    c.legend(400, 692, [(RED, "危险失效点", None)])
    c.legend(560, 692, [(SLATE, "“旧”＝从今天起不再可靠的判断", None)])
    return c.save(os.path.join(OUT, "ch42-fig1.svg"))


# ---------------------------------------------------------------- 图 42-2
def fig2():
    c = Canvas(960, 620,
               title="图 42-2　升级后变慢的三条机制链",
               subtitle="三条链都从“默认值变了”出发，在同一条订单查询上汇合；没有一条来自执行器")

    xs = [40, 347, 654]
    w, h = 266, 62

    cols = [
        (BLUE, ("字符集默认值", "latin1 → utf8mb4"), [
            (BLUE, "VARCHAR(64) 键变宽", "64 字节 → 最多 256 字节"),
            (RED, "索引页键数变少", "非叶页扇出掉到约四分之一"),
            (BLUE, "树高 +1", "每次等值多一次页访问"),
        ]),
        (BLUE, ("排序规则默认值", "general_ci → 0900_ai_ci"), [
            (BLUE, "PAD SPACE 变 NO PAD", "“SH”与“SH ”不再相等"),
            (RED, "唯一键判等松了", "旧数据里冒出“重复”行"),
            (BLUE, "GROUP BY 多一组", "报表按商户拆成两行"),
        ]),
        (BLUE, ("统计口径", "旧快照 + 新增直方图"), [
            (BLUE, "统计还是 5.7 的", "行宽、页数都已变"),
            (RED, "估算行数偏了", "计划从 ref 换成 ALL"),
            (BLUE, "多扫几万行", "回表把热页冲掉"),
        ]),
    ]

    for ci, (accent, head, steps) in enumerate(cols):
        x = xs[ci]
        cx = x + w / 2
        c.box(x, 78, w, 52, head[0], head[1], accent=accent,
              size=12.5, sub_size=9.5)
        for si, (scol, title, sub) in enumerate(steps):
            y = 176 + si * 124
            c.box(x, y, w, h, title, sub, accent=scol, size=12, sub_size=10)
            if si == 0:
                c.arrow((cx, 130), (cx, y), color=SLATE)
            else:
                c.arrow((cx, y - 62), (cx, y), color=scol if si == 1 else BLUE)
        c.arrow((cx, 486), (cx, 536), color=RED, width=1.8)

    c.box(40, 536, 880, 52, "同一条订单查询，P99 涨三成",
          "三条链叠加的结果：不是版本慢，是同一套配置在新版本里含义变了",
          accent=RED, size=13, sub_size=10)

    c.legend(40, 606, [(BLUE, "机制推进", None)])
    c.legend(200, 606, [(RED, "失效点：旧结论在这里不成立", None)])
    return c.save(os.path.join(OUT, "ch42-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
