#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《MySQL 圣经》全书体检脚本。

零依赖、只读，不执行任何外部命令。运行：

    python3 tools/verify_book.py

退出码 0 表示全部通过（允许 WARN），1 表示有 ERROR。
检查项分五组：
  S  结构：文件齐全 / 命名规范 / 7 段小节 / 编号与章号一致
  F  图：引用可解析 / SVG 合法 XML / 无孤儿图 / 脚本与图一一对应
  T  文字：禁用词 / user+name 反例 / 代码块语言标注 / 交叉引用章号
  A  附录：条目编号连续 / 标注计数与声称一致
  C  统计：汉字数 / 图数 与 PROGRESS.md 记录对账
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
IMAGES = os.path.join(DOCS, "images")
DIAGRAMS = os.path.join(ROOT, "tools", "diagrams")

ERRORS = []
WARNS = []
NOTES = []


def err(group, msg):
    ERRORS.append(f"[{group}] {msg}")


def warn(group, msg):
    WARNS.append(f"[{group}] {msg}")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def cjk_count(text):
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def md_files():
    return sorted(f for f in os.listdir(DOCS) if f.endswith(".md"))


# ---------------------------------------------------------------- 载入

def load_chapters():
    """返回 OrderedDict{num: {"file","path","text"}}。"""
    out = OrderedDict()
    for f in md_files():
        m = re.match(r"^ch(\d{2})-([a-z0-9-]+)\.md$", f)
        if not m:
            continue
        num = int(m.group(1))
        if num in out:
            err("S", f"章号重复：ch{num:02d} 同时出现在 {out[num]['file']} 与 {f}")
        out[num] = {"file": f, "path": os.path.join(DOCS, f), "text": read(os.path.join(DOCS, f))}
    return out


def load_appendices():
    out = OrderedDict()
    for f in md_files():
        m = re.match(r"^appendix-([a-g])-([a-z0-9-]+)\.md$", f)
        if not m:
            continue
        out[m.group(1).upper()] = {"file": f, "path": os.path.join(DOCS, f), "text": read(os.path.join(DOCS, f))}
    return out


# ---------------------------------------------------------------- S 结构

def check_structure(chapters, appendices):
    expect = set(range(1, 53))
    got = set(chapters)
    for n in sorted(expect - got):
        err("S", f"缺章：第 {n} 章（docs/ch{n:02d}-*.md 不存在）")
    for n in sorted(got - expect):
        err("S", f"多余章节文件：第 {n} 章")

    for n, ch in chapters.items():
        text = ch["text"]
        # 首行标题
        first = text.lstrip().splitlines()[0] if text.strip() else ""
        m = re.match(r"^#\s*第\s*(\d+)\s*章", first)
        if not m:
            err("S", f"ch{n:02d} 首行不是「# 第 N 章」格式：{first[:40]}")
        elif int(m.group(1)) != n:
            err("S", f"ch{n:02d} 首行章号写成 {m.group(1)}")

        # 一句话结论引用块
        if "**一句话结论**" not in text[:800]:
            warn("S", f"ch{n:02d} 开头 800 字内没有「一句话结论」")

        # 小节：## N.x（N.0 场景 + N.1~N.k 机制，后接五个固定段）
        heads = [(int(a), int(b), rest.strip())
                 for a, b, rest in re.findall(r"^##\s+(\d+)\.(\d+)\s*(.*)$", text, re.M)]
        if not heads:
            err("S", f"ch{n:02d} 没有 ## {n}.x 小节")
            continue
        if heads[0][1] != 0:
            err("S", f"ch{n:02d} 首个小节不是 {n}.0（场景）")
        if "场景" not in heads[0][2]:
            warn("S", f"ch{n:02d} 的 {n}.0 标题里没有「场景」字样：{heads[0][2][:20]}")
        seq = [b for _, b, _ in heads]
        if seq != list(range(0, len(seq))):
            err("S", f"ch{n:02d} 小节编号不连续：{['%d.%d' % (n, b) for b in seq]}")
        # 章号一致
        wrong = sorted({a for a, _, _ in heads if a != n})
        if wrong:
            err("S", f"ch{n:02d} 出现其他章号的小节标题：{[f'## {a}.x' for a in wrong]}")

        # 五个固定段，顺序必须正确
        fixed = ["关键结论", "实验验证", "常见误区", "Checklist", "延伸"]
        pos = []
        for name in fixed:
            hit = [i for i, (_, _, t) in enumerate(heads) if name.lower() in t.lower()]
            if not hit:
                err("S", f"ch{n:02d} 缺固定段「{name}」")
                pos.append(-1)
            else:
                pos.append(hit[0])
        if all(p >= 0 for p in pos) and pos != sorted(pos):
            err("S", f"ch{n:02d} 固定段顺序错乱：{list(zip(fixed, pos))}")

        # 必须有图
        refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
        if not refs:
            err("S", f"ch{n:02d} 没有任何配图引用")

    # 附录小节：## X.N
    for letter, ap in appendices.items():
        heads = [(a, b) for a, b in re.findall(r"^##\s+([A-G])\.(\d+)\s", ap["text"], re.M)]
        if not heads:
            err("S", f"附录 {letter} 没有 ## {letter}.N 小节")
        bad = sorted({a for a, _ in heads if a != letter})
        if bad:
            err("S", f"附录 {letter} 出现别的字母编号：{bad}")


# ---------------------------------------------------------------- F 图

def check_figures(chapters, appendices):
    referenced = defaultdict(list)   # svg 文件名 -> [引用者]
    all_docs = dict(chapters)
    all_docs.update({f"附录{letter}": ap for letter, ap in appendices.items()})

    for key, item in all_docs.items():
        text = item["text"]
        for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
            target = target.strip()
            if target.startswith("http"):
                warn("F", f"{item['file']} 引用了外链图片：{target}")
                continue
            path = os.path.normpath(os.path.join(DOCS, target))
            if not os.path.exists(path):
                err("F", f"{item['file']} 图引用断链：{target}")
                continue
            referenced[os.path.basename(path)].append(key)

    # 孤儿图 + XML 合法性
    if os.path.isdir(IMAGES):
        names = sorted(os.listdir(IMAGES))
        for name in names:
            if not name.endswith(".svg"):
                warn("F", f"images 下有非 svg 文件：{name}")
                continue
            if name not in referenced:
                warn("F", f"孤儿图（未被任何正文引用）：{name}")
            try:
                ET.parse(os.path.join(IMAGES, name))
            except ET.ParseError as e:
                err("F", f"SVG 不是合法 XML：{name} -> {e}")
        # 命名规范
        for name in names:
            if name.endswith(".svg") and not re.match(r"^(ch\d{2}|app[A-G])-fig\d+\.svg$", name):
                err("F", f"图文件名不合规：{name}")
    else:
        err("F", "docs/images 目录不存在")

    # 绘图脚本覆盖
    scripts = {f for f in os.listdir(DIAGRAMS) if f.endswith(".py")} if os.path.isdir(DIAGRAMS) else set()
    for n in chapters:
        if f"ch{n:02d}.py" not in scripts:
            err("F", f"缺绘图脚本 tools/diagrams/ch{n:02d}.py")
    for letter in appendices:
        if f"app{letter}.py" not in scripts:
            err("F", f"缺绘图脚本 tools/diagrams/app{letter}.py")
    known = {f"ch{n:02d}.py" for n in chapters} | {f"app{l}.py" for l in appendices}
    for s in sorted(scripts - known):
        warn("F", f"多余绘图脚本：{s}")

    # 脚本 save 的路径 vs 实际引用（脚本用 os.path.join(OUT, "xxx.svg")）
    for s in sorted(scripts):
        src = read(os.path.join(DIAGRAMS, s))
        saves = re.findall(r'["\']([\w.-]+\.svg)["\']', src)
        if not saves:
            err("F", f"{s} 没有生成任何 .svg")
        for base in saves:
            if not os.path.exists(os.path.join(IMAGES, base)):
                err("F", f"{s} 声明输出 {base} 但文件不存在")
            elif base not in referenced:
                warn("F", f"{s} 生成的 {base} 未被正文引用")

    NOTES.append(f"图：{len([n for n in os.listdir(IMAGES) if n.endswith('.svg')])} 张，"
                 f"被引用 {len(referenced)} 张，脚本 {len(scripts)} 个")


# ---------------------------------------------------------------- T 文字

BANNED = ["在本文中", "综上所述", "值得注意的是", "首先，", "其次，"]
BAD_EXAMPLE = [r"\buser\s*表", r"\bname\s*字段", r"CREATE TABLE\s+user\b"]
CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8,
          "九": 9, "十": 10, "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15}
GOOD_TABLES = ("order", "bill", "stock", "merchant", "settle", "account", "sku", "pay")


def check_text(chapters, appendices):
    all_docs = list(chapters.items()) + [(f"附录{l}", a) for l, a in appendices.items()]
    for key, item in all_docs:
        text = item["text"]
        for w in BANNED:
            for m in re.finditer(re.escape(w), text):
                line = text[:m.start()].count("\n") + 1
                err("T", f"{item['file']}:{line} 命中禁用词「{w}」")
        for pat in BAD_EXAMPLE:
            for m in re.finditer(pat, text):
                line = text[:m.start()].count("\n") + 1
                warn("T", f"{item['file']}:{line} 疑似反例表名/字段：{m.group(0)}")

        # 代码块语言标注（配对扫描）
        in_code = False
        for lineno, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            if s.startswith("```"):
                if not in_code:
                    lang = s[3:].strip()
                    if not lang:
                        warn("T", f"{item['file']}:{lineno} 代码块未标语言")
                    in_code = True
                else:
                    in_code = False
        if in_code:
            err("T", f"{item['file']} 代码块围栏未闭合")

        # 交叉引用章号范围（跳过首行标题）
        body = text.split("\n", 1)[1] if "\n" in text else ""
        offset = len(text) - len(body)
        for m in re.finditer(r"第\s*(\d+)\s*章", body):
            n = int(m.group(1))
            if n < 1 or n > 52:
                line = text[:m.start() + offset].count("\n") + 1
                err("T", f"{item['file']}:{line} 交叉引用越界：第 {n} 章")
            elif n not in chapters:
                line = text[:m.start() + offset].count("\n") + 1
                err("T", f"{item['file']}:{line} 引用了不存在的章：第 {n} 章")

        # 自我引用
        m = re.match(r"^ch(\d{2})-", item["file"])
        if m:
            me = int(m.group(1))
            for mm in re.finditer(r"第\s*(\d+)\s*章", body):
                if int(mm.group(1)) == me:
                    line = text[:mm.start() + offset].count("\n") + 1
                    warn("T", f"{item['file']}:{line} 在本章内引用「第 {me} 章」（应为「本章」）")
                    break

    # 每章「延伸」是否至少引一个别章
    for n, ch in chapters.items():
        seg = re.search(r"^##\s+%d\.\d+\s*延伸.*?$(.*?)(?=^##\s|\Z)" % n, ch["text"], re.M | re.S)
        if not seg:
            err("S", f"ch{n:02d} 找不到「延伸」小节")
            continue
        if not re.search(r"第\s*\d+\s*章", seg.group(1)):
            warn("S", f"ch{n:02d} 的「延伸」段没有引用任何其他章节")


# ---------------------------------------------------------------- A 附录

def check_appendix_items(appendices):
    expect = {"A": 85, "B": 12, "C": 28, "D": 40, "E": 100}
    counted = {}

    for letter, total in expect.items():
        if letter not in appendices:
            err("A", f"缺附录 {letter}")
            continue
        text = appendices[letter]["text"]
        if letter == "A":
            # 参数表的行：首列以反引号开头（表头是「参数名」，分隔行是 ---）
            names = re.findall(r"^\|\s*`([^`]+)`", text, re.M)
            counted["A"] = len(names)
            dup = {n for n in names if names.count(n) > 1}
            if dup:
                err("A", f"附录 A 参数重复列出：{sorted(dup)}")
            NOTES.append(f"附录 A：{len(names)} 行参数，其中 {len({n for n in names})} 个不同条目")
        elif letter == "E":
            # ### 1. 标题
            nums = [int(x) for x in re.findall(r"^###\s+(\d+)\.\s", text, re.M)]
            counted["E"] = len(nums)
            if sorted(nums) != list(range(1, total + 1)):
                err("A", f"附录 E 题号不是 1~{total} 连续：实测 {len(nums)} 题，"
                         f"缺 {sorted(set(range(1, total + 1)) - set(nums))[:10]}")
        else:
            nums = [int(x) for x in re.findall(r"^###\s+%s(\d+)" % letter, text, re.M)]
            counted[letter] = len(nums)
            if sorted(nums) != list(range(1, total + 1)):
                err("A", f"附录 {letter} 条目编号不是 1~{total} 连续：实测 {len(nums)} 条，"
                         f"缺 {sorted(set(range(1, total + 1)) - set(nums))[:10]}")

        if counted.get(letter) != total:
            err("A", f"附录 {letter} 条目数 {counted.get(letter)}，应为 {total}")
        NOTES.append(f"附录 {letter}：{counted.get(letter)} 条")

    # 附录 D ⚠️：按条目块切分统计（每个 ### 块到下一个 ## / ### 为止）
    if "D" in appendices:
        d = appendices["D"]["text"]
        starts = [(m.start(), m.group(1)) for m in re.finditer(r"^###\s+(D\d+)", d, re.M)]
        warned = []
        for i, (pos, name) in enumerate(starts):
            end = starts[i + 1][0] if i + 1 < len(starts) else len(d)
            block = d[pos:end]
            block = re.split(r"^##\s", block, maxsplit=1, flags=re.M)[0]
            if "⚠️" in block:
                warned.append(name)
        NOTES.append(f"附录 D：含 ⚠️ 的条目 {len(warned)} 条 -> {'、'.join(warned)}")
        # 正文自报的清单必须与实测一致
        for m in re.finditer(r"标 ⚠️ 的([一二三四五六七八九十百]+)条是([^。]*)", d):
            stated = CN_NUM.get(m.group(1))
            listed = re.findall(r"D\d+", m.group(2))
            if stated != len(listed):
                err("A", f"附录 D「标 ⚠️ 的{m.group(1)}条」但实际列了 {len(listed)} 个")
            if listed and listed != warned:
                err("A", f"附录 D ⚠️ 清单与实测不一致：列了 {listed}，实测含标记的是 {warned}")

    # 附录 E ⭐：按条目标题统计
    if "E" in appendices:
        e = appendices["E"]["text"]
        star_items = re.findall(r"^###\s+\d+\..*⭐", e, re.M)
        NOTES.append(f"附录 E：标题标 ⭐ 的题 {len(star_items)} 道")


# ---------------------------------------------------------------- C 统计

def check_outline(chapters):
    """OUTLINE.md 的 52 个章标题必须与正文首行一致（忽略星级后缀）。"""
    path = os.path.join(DOCS, "OUTLINE.md")
    if not os.path.exists(path):
        err("O", "docs/OUTLINE.md 不存在")
        return
    text = read(path)
    titles = {}
    for m in re.finditer(r"^###\s*第\s*(\d+)\s*章\s*[：: ]?\s*(.+)$", text, re.M):
        titles[int(m.group(1))] = m.group(2).strip()

    def norm(s):
        s = re.sub(r"[（(].*?[)）]", "", s)
        s = re.sub(r"[\s\u3000]+[★☆]+.*$", "", s)
        return s.strip("　 ：:")

    for n in sorted(set(range(1, 53)) - set(titles)):
        err("O", f"OUTLINE 缺第 {n} 章")
    for n, ch in chapters.items():
        if n not in titles:
            continue
        first = ch["text"].splitlines()[0]
        real = re.sub(r"^#\s*第\s*\d+\s*章\s*", "", first).strip()
        if norm(titles[n]) != norm(real):
            err("O", f"第 {n} 章标题不一致：OUTLINE「{norm(titles[n])}」/ 正文「{norm(real)}」")
    NOTES.append(f"大纲：{len(titles)} 个章标题与正文逐条对齐")


def check_stats(chapters, appendices):
    ch_chars = sum(cjk_count(c["text"]) for c in chapters.values())
    ap_chars = sum(cjk_count(a["text"]) for a in appendices.values())
    NOTES.append(f"正文汉字 {ch_chars:,}（{len(chapters)} 章）")
    NOTES.append(f"附录汉字 {ap_chars:,}（{len(appendices)} 份）")
    NOTES.append(f"合计汉字 {ch_chars + ap_chars:,}")

    # 与 PROGRESS.md 表格逐章对账
    prog_path = os.path.join(ROOT, "PROGRESS.md")
    if os.path.exists(prog_path):
        prog = read(prog_path)
        rows = re.findall(r"^\|\s*(\d{1,2})\s*\|\s*`docs/(ch\d{2}-[a-z0-9-]+\.md)`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|$",
                          prog, re.M)
        seen = set()
        for num, path, chars, figs in rows:
            n = int(num)
            seen.add(n)
            if n not in chapters:
                err("C", f"PROGRESS 记录了第 {n} 章，文件不存在")
                continue
            real_chars = cjk_count(chapters[n]["text"])
            real_figs = len(re.findall(r"!\[[^\]]*\]\(", chapters[n]["text"]))
            if abs(real_chars - int(chars)) > 30:
                warn("C", f"PROGRESS 记 ch{n:02d} 为 {chars} 字，实测 {real_chars} 字")
            if real_figs != int(figs):
                err("C", f"PROGRESS 记 ch{n:02d} 为 {figs} 图，实测 {real_figs} 图")
        for n in sorted(set(chapters) - seen):
            warn("C", f"PROGRESS 章节表缺第 {n} 章")
    return ch_chars, ap_chars


# ---------------------------------------------------------------- main

def main():
    chapters = load_chapters()
    appendices = load_appendices()

    check_structure(chapters, appendices)
    check_figures(chapters, appendices)
    check_text(chapters, appendices)
    check_appendix_items(appendices)
    check_outline(chapters)
    check_stats(chapters, appendices)

    print("=" * 68)
    print("《MySQL 圣经》全书体检")
    print("=" * 68)
    for note in NOTES:
        print("  ·", note)
    print("-" * 68)
    if ERRORS:
        print(f"ERROR {len(ERRORS)} 条")
        for e in ERRORS:
            print("  ✗", e)
    if WARNS:
        print(f"WARN  {len(WARNS)} 条")
        for w in WARNS:
            print("  !", w)
    print("-" * 68)
    if not ERRORS and not WARNS:
        print("全部通过：零 ERROR、零 WARN")
    elif not ERRORS:
        print(f"通过（{len(WARNS)} 条 WARN 需人工确认）")
    else:
        print(f"未通过：{len(ERRORS)} 条 ERROR")
    return 0 if not ERRORS else 1


if __name__ == "__main__":
    sys.exit(main())
