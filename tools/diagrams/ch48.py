#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 48 章配图：权限格子与三道防护"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 48-1
def _panel(c, x, y, w, h, head, color, lines, hot=None):
    """一格内的半边：标题 + 若干行；hot 指定需要高亮的那一行下标"""
    c.rect(x, y, w, h, fill="#ffffff", stroke=BORDER[color], sw=1.2, r=6)
    c.text(x + 10, y + 20, head, size=10.5, fill=color, weight=600)
    ly = y + 44
    for i, s in enumerate(lines):
        if i == hot:
            c.rect(x + 8, ly - 15, w - 16, 23, fill=RED, stroke=RED, sw=1, r=4)
            c.text(x + 14, ly, s, size=10.5, fill="#ffffff", weight=600)
        else:
            c.text(x + 12, ly, s, size=10.5, fill=SUB)
        ly += 25


def fig1():
    c = Canvas(960, 680,
               title="图 48-1　四级账号的权限格子：每一格都写清「能」与「不能」",
               subtitle="四格里最反直觉的是运维格——能改参数、能 KILL、能做备份，但不该能读业务表")

    cells = [
        (48, 96, "① 应用只读", BLUE,
         ["SELECT 到指定库指定表", "只连只读从库", "通过视图收窄列"],
         ["SELECT 到 mysql 库", "任何 INSERT/UPDATE", "SELECT ... INTO OUTFILE"], None),
        (492, 96, "② 应用读写", BLUE,
         ["SELECT/INSERT/UPDATE", "归档表的 DELETE", "事务内锁行、批量写"],
         ["核心交易表的 DELETE", "DROP / ALTER / TRUNCATE", "FILE、SUPER、GRANT"], None),
        (48, 348, "③ 运维", ORANGE,
         ["改参数、看状态变量", "备份、KILL 会话", "查 p_s 与慢日志"],
         ["读业务表数据", "改业务数据", "把权限授给别人"], 0),
        (492, 348, "④ DBA", RED,
         ["全库全表、恢复实例", "建账号、授权与回收", "主从切换与 DDL"],
         ["无审计的直连操作", "单人执行高危 DDL", "共享账号、长期不收回"], None),
    ]

    for cx, cy, head, col, allow, deny, hot in cells:
        c.container(cx, cy, 420, 232, head, label_color=col)
        _panel(c, cx + 14, cy + 34, 188, 182, "能做什么", GREEN, allow)
        _panel(c, cx + 218, cy + 34, 188, 182, "不能做什么", RED, deny, hot=hot)

    c.rect(48, 594, 864, 38, fill=TINT[SLATE], stroke=BORDER[SLATE], sw=1.2, r=6)
    c.text(480, 618, "权限设计的目标不是防恶意，是把无意的破坏限制在一个格子里",
           size=12.5, fill=INK, anchor="middle", weight=600)
    c.legend(48, 660, [(GREEN, "允许", None)])
    c.legend(150, 660, [(RED, "禁止 / 最常被破坏的一条", None)])
    c.legend(400, 660, [(ORANGE, "运维：权限最容易被「临时需要」撑大", None)])
    return c.save(os.path.join(OUT, "ch48-fig1.svg"))


# ---------------------------------------------------------------- 图 48-2
def fig2():
    c = Canvas(960, 620,
               title="图 48-2　三道屏障各自挡住什么：越往里，越接近明文",
               subtitle="三者不能互相替代；任意一道被当成「我们加密了」，另外两道就会失守")

    # 三道同心屏障
    c.rect(196, 92, 716, 444, fill=TINT[ORANGE], stroke=BORDER[ORANGE], sw=1.6, r=14)
    c.rect(264, 156, 580, 322, fill=TINT[BLUE], stroke=BORDER[BLUE], sw=1.6, r=14)
    c.rect(332, 220, 444, 196, fill=TINT[GREEN], stroke=BORDER[GREEN], sw=1.6, r=14)

    c.text(210, 118, "① TDE 表空间加密", size=12, fill=ORANGE, weight=600)
    c.text(360, 118, "挡住：磁盘、备份文件被整块拷走", size=10.5, fill=GREEN)
    c.text(210, 514, "挡不住：拿着一个合法账号连上来的人", size=10.5, fill=RED)

    c.text(278, 182, "② 账号权限 + 列级加密", size=12, fill=BLUE, weight=600)
    c.text(452, 182, "挡住：越权 SQL，以及读了也不懂的列", size=10.5, fill=GREEN)
    c.text(278, 466, "挡不住：本来就该读这些列的人", size=10.5, fill=RED)

    c.text(346, 246, "③ 脱敏视图", size=12, fill=GREEN, weight=600)
    c.text(432, 246, "挡住：联调与报表看到全量手机号", size=10.5, fill=GREEN)
    c.text(346, 404, "挡不住：基表权限没收回，视图等于白建", size=10.5, fill=RED)

    # 核心：明文数据
    c.box(404, 264, 300, 84, "敏感字段的明文", "卡号 / 手机号 / 身份证号", accent=PURPLE,
          size=13, sub_size=10.5)

    # 左侧：威胁面收窄
    c.arrow((118, 520), (118, 132), color=SLATE, dash="5,4", width=1.4)
    c.text(118, 120, "越往里越窄", size=10.5, fill=SUB, anchor="middle")
    c.text(48, 556, "外层只挡「盘」", size=11, fill=SUB)
    c.text(48, 576, "内层才挡「人」", size=11, fill=INK, weight=600)

    c.legend(48, 600, [(ORANGE, "存储侧", None)])
    c.legend(180, 600, [(BLUE, "权限与密钥", None)])
    c.legend(330, 600, [(GREEN, "展示层", None)])
    c.legend(460, 600, [(RED, "挡不住的部分", None)])
    return c.save(os.path.join(OUT, "ch48-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
