#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 3 章配图：InnoDB 磁盘体系"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


def fillbar(c, x, y, w, ratio, color=BLUE, hole=False):
    """页内填充率条：底色是空洞，前景是已占用记录"""
    c.rect(x, y, w, 10, fill=("#fef2f2" if hole else "#f1f5f9"),
           stroke=(RED if hole else LINE), sw=1, r=5,
           dash=("3,2" if hole else None))
    if ratio > 0:
        c.rect(x, y, w * ratio, 10, fill=color, stroke=color, sw=1, r=5)


# ---------------------------------------------------------------- 图 3-1
def fig1():
    c = Canvas(960, 640, title="图 3-1　表空间 → 段 → 区 → 页 → 行：五级容器",
               subtitle="分配按区、IO 按页、锁与版本按行——三个单位各自解决一个问题")

    levels = [("① 表空间", 96), ("② 段", 196), ("③ 区", 296),
              ("④ 页", 396), ("⑤ 行", 496)]
    for label, y in levels:
        c.pill(50, y, 110, 34, label, accent=SLATE)
    for i in range(4):
        c.arrow(105, levels[i][1] + 34, 105, levels[i + 1][1],
                color=SLATE, dash="4,3")

    # ① 表空间
    c.cyl(190, 88, 190, 76, "order_item.ibd", "一张表一个文件",
          accent=GREEN)
    c.text(404, 118, "系统表空间 ibdata1 ｜ 通用表空间 ts1.ibd", size=12, fill=SUB)
    c.text(404, 142, "undo 表空间 undo_001 ｜ 临时表空间 ibtmp1", size=12, fill=SUB)

    # ② 段
    c.box(190, 194, 190, 66, "叶子节点段", "存全部行记录", accent=BLUE)
    c.box(420, 194, 200, 66, "非叶子节点段", "存主键 + 子页号", accent=BLUE)
    c.text(660, 222, "每个索引 = 2 个段", size=12, fill=SUB)
    c.text(660, 244, "undo 走回滚段，不在 B+ 树里", size=11, fill=SUB)

    # ③ 区
    c.text(190, 286, "同一段的页尽量落在连续的区里，避免顺序扫描退化成随机 IO",
           size=12, fill=SUB)
    c.rect(190, 296, 624, 52, fill="#ffffff", stroke=BORDER[SLATE], r=0)
    for i in range(16):
        c.rect(190 + i * 39, 296, 39, 52,
               fill=(TINT[BLUE] if i % 2 == 0 else "#ffffff"),
               stroke="none", r=0)
    c.text(502, 327, "64 个页 = 1 个区 = 1MB", size=12, fill=BLUE,
           anchor="middle", weight=600)
    c.badge(832, 308, "分配单位", accent=BLUE)
    c.text(190, 372, "页变小则区内页数变多、字节数不变：8KB → 128 页，4KB → 256 页",
           size=11, fill=SUB)

    # ④ 页
    c.box(190, 392, 190, 66, "1 个数据页", "16384 字节 = 16KB", accent=GREEN)
    c.text(404, 418, "IO 的最小单位；页大小只能在初始化时定", size=12, fill=SUB)
    c.text(404, 442, "改它 = 重建实例，备份与复制两端必须一致", size=11, fill=SUB)

    # ⑤ 行
    c.box(190, 488, 120, 66, "1 行", "主键 + 业务列")
    c.box(350, 488, 160, 66, "DB_TRX_ID 6B", "最近修改事务", accent=PURPLE, size=12)
    c.box(550, 488, 170, 66, "DB_ROLL_PTR 7B", "指向 undo 版本链", accent=ORANGE, size=12)
    c.box(760, 488, 150, 66, "DB_ROW_ID 6B", "仅无主键时存在", size=12)

    c.text(190, 592, "三个隐藏列让每行固定多出 13 字节：1 亿行就是 1.3GB，且与业务字段无关。",
           size=12, fill=INK)
    return c.save(os.path.join(OUT, "ch03-fig1.svg"))


# ---------------------------------------------------------------- 图 3-2
def fig2():
    c = Canvas(960, 640, title="图 3-2　一个 16KB 数据页的内部布局",
               subtitle="横向按功能区划分，不按字节比例；上方数字是页内真实字节偏移")

    blocks = [
        (50, 120, "File Header", "38B · 页号 / LSN", SLATE, "0–37"),
        (170, 118, "Page Header", "56B · 槽数 / 堆顶", SLATE, "38–93"),
        (288, 100, "Inf / Sup", "26B · 两条哨兵", TEAL, "94–119"),
        (388, 176, "User Records", "按键升序的单链表", BLUE, "120 →"),
        (564, 104, "Free Space", "删除留下的空洞", RED, "可变"),
        (668, 122, "Page Directory", "2B/槽 · 4~8 条一组", ORANGE, "← 16375"),
        (790, 100, "File Trailer", "8B · 尾部校验", SLATE, "16376–16383"),
    ]
    for x, w, t, s, col, off in blocks:
        c.text(x + w / 2, 92, off, size=10, fill=SUB, anchor="middle", mono=True)

    for x, w, t, s, col, off in blocks:
        c.box(x, 100, w, 86, t, s, accent=col, size=12, r=3)

    c.text(392, 210, "↑ 记录向高地址生长", size=11, fill=SUB)
    c.text(570, 210, "空洞", size=11, fill=RED)
    c.text(668, 210, "↓ 目录向低地址生长", size=11, fill=SUB)

    # 左：Page Header 字段表
    c.container(50, 240, 430, 210, "Page Header 关键字段（56 字节）")
    rows = [
        ("PAGE_N_DIR_SLOTS", "目录槽数量"),
        ("PAGE_HEAP_TOP", "已分配到哪个偏移"),
        ("PAGE_N_HEAP", "记录数（含 Inf / Sup）"),
        ("PAGE_FREE", "可复用记录链表头"),
        ("PAGE_GARBAGE", "可复用字节数"),
        ("PAGE_LAST_INSERT", "上次插入的记录位置"),
        ("PAGE_DIRECTION", "插入方向：右 / 左 / 随机"),
        ("PAGE_N_RECS", "用户记录数"),
        ("PAGE_LEVEL", "0 = 叶子页"),
    ]
    for i, (k, v) in enumerate(rows):
        y = 282 + i * 20
        c.text(70, y, k, size=10, fill=INK, mono=True, weight=600)
        c.text(258, y, v, size=11, fill=SUB)

    # 右：页内二分
    c.container(500, 240, 400, 210, "页内查找：目录二分 + 组内线性")
    keys = [10, 20, 30, 40, 50, 60, 70, 80]
    for i, k in enumerate(keys):
        x = 512 + i * 46
        hit = (k == 40)
        c.rect(x, 286, 40, 30, fill=(TINT[BLUE] if hit else TINT[SLATE]),
               stroke=(BORDER[BLUE] if hit else BORDER[SLATE]), sw=1.2, r=4)
        c.text(x + 20, 306, str(k), size=11, anchor="middle",
               fill=(BLUE if hit else SUB), weight=600)
    c.text(512, 336, "① 对槽位二分，落到 40 这一组（此处只画了 8 个）", size=11, fill=SUB)

    recs = [("40", False), ("41", False), ("44", False),
            ("47", True), ("48", False), ("50", False)]
    for i, (v, hit) in enumerate(recs):
        x = 512 + i * 60
        c.rect(x, 352, 52, 28, fill=(TINT[ORANGE] if hit else "#ffffff"),
               stroke=(BORDER[ORANGE] if hit else LINE), sw=1.2, r=4)
        c.text(x + 26, 371, v, size=11, anchor="middle",
               fill=(ORANGE if hit else SUB), weight=600)
    c.text(512, 402, "② 进槽后沿 next_record 顺序走，最多 8 条", size=11, fill=SUB)
    c.text(512, 426, "5 次二分 + 最多 8 次组内 ≈ 13 次比较；顺序扫要上百次", size=11, fill=RED)

    # 底部：File Trailer 的用途
    c.container(50, 470, 850, 130, "为什么要留 8 字节的 File Trailer")
    c.text(70, 512, "写一页的顺序：先写页内容，最后写 trailer 里的 checksum 与 LSN 低 32 位。",
           size=12, fill=INK)
    c.text(70, 538, "恢复时比对 trailer 与页头 checksum：对不上说明这页只写了一半，16KB 可能只落了 4KB。",
           size=12, fill=INK)
    c.text(70, 566, "这就是 doublewrite 存在的理由：先把页写进 dblwr，再写回 .ibd（见第 7 章）。",
           size=12, fill=BLUE)
    return c.save(os.path.join(OUT, "ch03-fig2.svg"))


# ---------------------------------------------------------------- 图 3-3
def fig3():
    c = Canvas(960, 660, title="图 3-3　页分裂：顺序插入只追加，随机插入对半劈",
               subtitle="同样 1000 万行，主键顺序决定页的填充率与范围扫描的 IO 形态")

    # 左：顺序插入
    c.container(40, 92, 430, 358, "① 顺序插入（自增主键）：只做右分裂")
    c.arrow(70, 146, 440, 146, color=GREEN, label="插入方向", label_dy=-8)
    for i, name in enumerate(["页 N-2", "页 N-1", "页 N"]):
        x = 70 + i * 140
        c.box(x, 170, 100, 110, name, "15/16 满", accent=BLUE, size=13)
        fillbar(c, x + 8, 254, 84, 0.94, color=BLUE)
    c.text(70, 322, "新页从 free extent 取，追加到链表尾部", size=11, fill=SUB)
    c.text(70, 346, "已有页不搬移，利用率稳定在 15/16 ≈ 93%", size=11, fill=SUB)
    c.text(70, 370, "分裂成本：1 个新页 + 目录重排 + 1 条 redo", size=11, fill=SUB)

    # 右：随机插入
    c.container(490, 92, 430, 358, "② 随机插入（UUID）：50 / 50 分裂")
    c.box(560, 150, 130, 100, "页 A", "8/8 满", accent=RED, size=13)
    fillbar(c, 568, 222, 114, 1.0, color=RED)
    c.arrow(625, 250, 572, 290, color=RED)
    c.arrow(625, 250, 727, 290, color=RED)
    c.badge(786, 214, "对半劈", accent=RED)

    c.box(515, 292, 115, 100, "页 A′", "4/8 满", accent=BLUE, size=13)
    fillbar(c, 523, 364, 99, 0.5, color=BLUE, hole=True)
    c.box(670, 292, 115, 100, "页 B（新）", "4/8 满", accent=GREEN, size=13)
    fillbar(c, 678, 364, 99, 0.5, color=GREEN, hole=True)

    c.text(515, 412, "两页各剩一半空位：页内可复用，不能挪给别人", size=11, fill=SUB)
    c.text(515, 434, "新页与旧页物理不相邻 → 范围扫描退化为随机 IO", size=11, fill=SUB)

    # 底部：代价对照
    c.container(40, 462, 880, 170, "同样的 1000 万行，代价差在哪（按每页 100 行、行宽 150B 估算）")
    c.box(70, 500, 250, 62, "叶页数量", "≈ 10.7 万 vs ≈ 20 万", accent=BLUE)
    c.box(360, 500, 250, 62, "表空间占用", "≈ 1.6GB vs ≈ 3.0GB", accent=GREEN)
    c.box(650, 500, 240, 62, "范围扫描 IO", "顺序 vs 随机", accent=SLATE)
    c.text(70, 592, "10M × 150B ÷ 0.93 ≈ 1.6GB，÷ 0.5 ≈ 3.0GB。填充率不是审美问题，是容量问题。",
           size=11, fill=SUB)
    c.legend(660, 578, [(BLUE, "已占用记录", None), (RED, "空洞（可复用）", "3,2")])
    return c.save(os.path.join(OUT, "ch03-fig3.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2, fig3):
        print(f())
