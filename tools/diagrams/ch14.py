#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第 14 章配图：排序、临时表与聚合"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from svgkit import *   # noqa

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images")


# ---------------------------------------------------------------- 图 14-1
def fig1():
    c = Canvas(960, 640,
               title="图 14-1　filesort 的两条路径：全字段排序 vs rowid 排序",
               subtitle="同一个 ORDER BY，进 sort buffer 的东西不同，代价的落点也不同")

    # 待排序的输入
    c.box(300, 82, 360, 54, "N 行待排序数据", "排序键 + 需要返回的列",
          accent=SLATE, size=13, sub_size=10)

    c.arrow([(480, 136), (480, 152), (250, 152), (250, 176)],
            color=SLATE, width=1.4)
    c.arrow([(480, 136), (480, 152), (710, 152), (710, 176)],
            color=SLATE, width=1.4)

    # ---------------- 左：全字段排序
    c.container(40, 176, 420, 320, "路径 A｜全字段排序（single-pass）")

    c.box(64, 218, 372, 52,
          "sort buffer：排序键 + 全部返回列",
          "整行投影进缓冲，排完直接输出", accent=BLUE, size=12, sub_size=10)
    c.box(64, 292, 372, 44, "内存快排 / 多路归并", accent=GREEN, size=12)
    c.box(64, 348, 372, 44, "零回表；单行占用大", accent=BLUE, size=12)

    c.text(64, 418, "选它：行窄、返回列少、装得进 sort_buffer", size=11, fill=INK)
    c.text(64, 442, "装不下 → number_of_tmp_files 变大，归并落盘", size=11, fill=SUB)

    # ---------------- 右：rowid 排序
    c.container(500, 176, 420, 320, "路径 B｜rowid 排序（two-pass）")

    c.box(524, 218, 372, 52,
          "sort buffer：排序键 + 主键",
          "只放定位信息，单行小得多", accent=ORANGE, size=12, sub_size=10)
    c.box(524, 292, 372, 44, "按主键逐行回表取列", accent=ORANGE, size=12)
    c.box(524, 348, 372, 44, "两次读；随机 IO 放大", accent=RED, size=12)

    c.text(524, 418, "选它：行宽、含 TEXT/BLOB、返回列多", size=11, fill=INK)
    c.text(524, 442, "回表次数 = 排序结果行数，不是 LIMIT 行数", size=11, fill=SUB)

    # ---------------- 底：判定阈值
    c.container(40, 536, 880, 76, "阈值：谁决定走哪条路")
    c.text(60, 580,
           "< 8.0.20：行长度 > max_length_for_sort_data（8.0 默认 4KB）时走 rowid 排序，拿回表换内存",
           size=11, fill=INK)
    c.text(60, 602,
           "[8.0.20+]：该参数废弃，路径合一——按行的实际长度打包，装不下的行才退回只带主键",
           size=11, fill=RED)

    return c.save(os.path.join(OUT, "ch14-fig1.svg"))


# ---------------------------------------------------------------- 图 14-2
def fig2():
    c = Canvas(960, 620,
               title="图 14-2　GROUP BY 的临时表：从内存到磁盘的降级链",
               subtitle="两条路径两套阈值；tmp_table_size 只卡在下面那条路上")

    # ---------------- 路径 ①：TempTable
    c.container(40, 84, 880, 244,
                "① [8.0] 默认：internal_tmp_mem_storage_engine = TempTable")

    c.box(64, 126, 256, 96, "内存临时表",
          "上限 temptable_max_ram（默认 1GB）", accent=GREEN, size=13, sub_size=10)
    c.box(360, 126, 256, 96, "溢出到 mmap 文件",
          "上限 temptable_max_mmap [8.0.23+]", accent=ORANGE, size=13, sub_size=10)
    c.box(656, 126, 256, 96, "InnoDB 磁盘临时表",
          "ibtmp1 · innodb_temp_data_file_path", accent=RED, size=13, sub_size=10)

    c.arrow(320, 174, 360, 174, color=SLATE, width=1.4)
    c.arrow(616, 174, 656, 174, color=SLATE, width=1.4)

    c.text(64, 262, "RAM 用尽不直接落盘：先申请内存映射的临时文件，两者都超限才把这张表转成 InnoDB 表。",
           size=11, fill=INK)

    # ---------------- 路径 ②：MEMORY
    c.container(40, 368, 880, 150,
                "② [5.7] 或 internal_tmp_mem_storage_engine = MEMORY：MEMORY 引擎临时表")

    c.box(64, 408, 300, 76, "MEMORY 内存临时表",
          "上限 min(tmp_table_size, max_heap_table_size)", accent=BLUE,
          size=13, sub_size=10)
    c.box(464, 408, 300, 76, "InnoDB 磁盘临时表",
          "ibtmp1 · Created_tmp_disk_tables + 1", accent=RED, size=13, sub_size=10)
    c.arrow(364, 446, 464, 446, color=SLATE, width=1.4, label="超出", label_dy=-9)

    c.text(64, 506, "tmp_table_size 卡在这里——它只对 MEMORY 引擎生效，8.0 默认配置下改它没有效果。",
           size=11, fill=RED)

    # ---------------- 底：判断落在哪条路
    c.text(40, 560, "怎么确认自己在哪条路上：SHOW VARIABLES LIKE 'internal_tmp_mem_storage_engine'；",
           size=11, fill=SUB, weight=600)
    c.text(40, 584, "再看 Created_tmp_disk_tables ÷ Created_tmp_tables——比值低说明全在内存，比值高才需要调阈值。",
           size=11, fill=SUB)

    return c.save(os.path.join(OUT, "ch14-fig2.svg"))


if __name__ == "__main__":
    for f in (fig1, fig2):
        print(f())
