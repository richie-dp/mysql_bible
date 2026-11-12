#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
svgkit — 《MySQL 圣经》配套 SVG 绘图工具包

设计目标：
1. 统一所有章节插图视觉规范（Style 1: Flat Icon 的浅色变体，适配文档阅读）
2. 用 Python 函数代替手写 XML，杜绝标签/属性语法错误
3. 内置正交路由、文本宽度估算、自动图例，避免箭头穿框、文字溢出

用法：
    from svgkit import Canvas
    c = Canvas(960, 600, title="InnoDB 内存结构")
    c.container(40, 80, 560, 300, "Buffer Pool")
    c.box("bp", 80, 140, 160, 64, "数据页", "16KB / page")
    c.arrow((240, 172), (400, 172), label="读取")
    c.save("docs/images/ch02-fig1.svg")
"""

from __future__ import annotations

import html
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------- 设计令牌
BG = "#ffffff"
INK = "#111827"        # 主文字
SUB = "#6b7280"        # 次级文字
LINE = "#d1d5db"       # 默认描边
FAINT = "#f9fafb"      # 容器底色

BLUE = "#2563eb"
RED = "#dc2626"
GREEN = "#16a34a"
PURPLE = "#9333ea"
ORANGE = "#ea580c"
TEAL = "#0d9488"
SLATE = "#475569"

TINT = {
    BLUE: "#eff6ff",
    RED: "#fef2f2",
    GREEN: "#f0fdf4",
    PURPLE: "#faf5ff",
    ORANGE: "#fff7ed",
    TEAL: "#f0fdfa",
    SLATE: "#f8fafc",
}

BORDER = {
    BLUE: "#bfdbfe",
    RED: "#fecaca",
    GREEN: "#bbf7d0",
    PURPLE: "#e9d5ff",
    ORANGE: "#fed7aa",
    TEAL: "#99f6e4",
    SLATE: "#e2e8f0",
}

FONT = ("'Helvetica Neue', Helvetica, Arial, 'PingFang SC', "
        "'Microsoft YaHei', 'Hiragino Sans GB', 'SimHei', sans-serif")
MONO = "'SF Mono', Menlo, Consolas, 'Courier New', monospace"


def text_width(s: str, size: float) -> float:
    """估算文本像素宽度：CJK 记 1.0em，其余 0.56em"""
    w = 0.0
    for ch in s:
        w += size if ord(ch) > 0x2E80 else size * 0.56
    return w


class Canvas:
    def __init__(self, w: int = 960, h: int = 600, title: str | None = None,
                 subtitle: str | None = None):
        self.w, self.h = w, h
        self.title = title
        self.subtitle = subtitle
        self.els: list[str] = []
        self._markers: dict[str, str] = {}
        self._clip_n = 0
        self._nodes: list[tuple[float, float, float, float, str]] = []
        self._edges: list[tuple[list, str]] = []
        self._warn: list[str] = []

    # ------------------------------------------------------------ 基础图元
    def _marker(self, color: str, start: bool = False) -> str:
        key = f"{'s' if start else 'e'}_{color.lstrip('#')}"
        mid = f"m_{key}"
        if key in self._markers:
            return mid
        if start:
            pts = "10 0, 0 3.5, 10 7"
            refx = 1
        else:
            pts = "0 0, 10 3.5, 0 7"
            refx = 9
        self._markers[key] = (
            f'<marker id="{mid}" markerWidth="10" markerHeight="7" '
            f'refX="{refx}" refY="3.5" orient="auto">'
            f'<polygon points="{pts}" fill="{color}"/></marker>'
        )
        return mid

    def raw(self, s: str) -> "Canvas":
        self.els.append(s)
        return self

    def text(self, x, y, s, size=14, fill=None, anchor="start",
             weight=400, mono=False, opacity=None) -> "Canvas":
        fill = fill or INK
        fam = f'font-family="{MONO}"' if mono else ""
        op = f' opacity="{opacity}"' if opacity else ""
        self.els.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}"{op} {fam}>'
            f'{html.escape(s)}</text>'
        )
        return self

    def rect(self, x, y, w, h, fill=BG, stroke=LINE, sw=1.5, r=8,
             dash=None, opacity=None) -> "Canvas":
        d = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity else ""
        self.els.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{op}/>'
        )
        return self

    def container(self, x, y, w, h, label, dash="6,4", fill=FAINT,
                  stroke="#e5e7eb", label_color=None) -> "Canvas":
        """虚线分组容器 + 左上角标签"""
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.2, r=10, dash=dash)
        if label:
            self.text(x + 14, y + 22, label, size=13,
                      fill=label_color or SUB, weight=600)
        return self

    def box(self, x, y, w, h, title, sub=None, accent=None, fill=None,
            stroke=None, size=14, sub_size=11, r=8, mono=False,
            align="center", sw=1.5) -> "Canvas":
        f = fill or (TINT.get(accent, BG) if accent else BG)
        s = stroke or (BORDER.get(accent, LINE) if accent else LINE)
        self.rect(x, y, w, h, fill=f, stroke=s, sw=sw, r=r)
        self._nodes.append((x, y, w, h, title))
        inner = w - 16
        if text_width(title, size) > inner:
            self._warn.append(f"文字溢出 [{title}] 需要 {text_width(title,size):.0f}px / 可用 {inner:.0f}px")
        if sub and text_width(sub, sub_size) > inner:
            self._warn.append(f"副标题溢出 [{sub}] 需要 {text_width(sub,sub_size):.0f}px / 可用 {inner:.0f}px")
        cx = x + w / 2
        anchor = "middle" if align == "center" else "start"
        tx = cx if align == "center" else x + 12
        if sub:
            self.text(tx, y + h / 2 - 5, title, size=size, anchor=anchor,
                      weight=600, mono=mono)
            self.text(tx, y + h / 2 + 15, sub, size=sub_size, anchor=anchor,
                      fill=SUB)
        else:
            self.text(tx, y + h / 2 + size * 0.35, title, size=size,
                      anchor=anchor, weight=600, mono=mono)
        return self

    def mono_box(self, x, y, w, h, lines, fill="#0f172a", fg="#e2e8f0",
                 size=11, title=None) -> "Canvas":
        """深色代码块（用于展示 SQL / 日志片段）"""
        self.rect(x, y, w, h, fill=fill, stroke="#334155", sw=1.2, r=6)
        self._nodes.append((x, y, w, h, "code"))
        yy = y + (26 if title else 18)
        if title:
            self.text(x + 12, y + 17, title, size=11, fill="#94a3b8")
            yy = y + 38
        for ln in lines:
            self.text(x + 12, yy, ln, size=size, fill=fg, mono=True)
            yy += size + 6
        return self

    def cyl(self, x, y, w, h, title, sub=None, accent=None) -> "Canvas":
        """数据库圆柱体"""
        f = TINT.get(accent, "#f8fafc") if accent else "#f8fafc"
        s = BORDER.get(accent, LINE) if accent else LINE
        ry = 11
        d = (f"M {x} {y+ry} A {w/2} {ry} 0 0 1 {x+w} {y+ry} "
             f"L {x+w} {y+h-ry} A {w/2} {ry} 0 0 1 {x} {y+h-ry} Z")
        self.els.append(f'<path d="{d}" fill="{f}" stroke="{s}" stroke-width="1.5"/>')
        self.els.append(
            f'<path d="M {x} {y+ry} A {w/2} {ry} 0 0 0 {x+w} {y+ry}" '
            f'fill="none" stroke="{s}" stroke-width="1.5"/>'
        )
        self._nodes.append((x, y, w, h, title))
        if text_width(title, 13) > w - 14:
            self._warn.append(f"圆柱文字溢出 [{title}]")
        cx = x + w / 2
        if sub:
            self.text(cx, y + h / 2 - 2, title, size=13, anchor="middle", weight=600)
            self.text(cx, y + h / 2 + 16, sub, size=11, anchor="middle", fill=SUB)
        else:
            self.text(cx, y + h / 2 + 8, title, size=13, anchor="middle", weight=600)
        return self

    def diamond(self, cx, cy, w, h, label, accent=None, size=12) -> "Canvas":
        f = TINT.get(accent, "#ffffff") if accent else "#ffffff"
        s = BORDER.get(accent, LINE) if accent else LINE
        pts = f"{cx},{cy-h/2} {cx+w/2},{cy} {cx},{cy+h/2} {cx-w/2},{cy}"
        self.els.append(
            f'<polygon points="{pts}" fill="{f}" stroke="{s}" stroke-width="1.5"/>'
        )
        self.text(cx, cy + size * 0.35, label, size=size, anchor="middle", weight=600)
        return self

    def pill(self, x, y, w, h, label, accent=None, size=12) -> "Canvas":
        self.box(x, y, w, h, label, accent=accent, size=size, r=h / 2)
        return self

    def badge(self, x, y, label, accent=BLUE, size=11) -> "Canvas":
        w = text_width(label, size) + 16
        self.rect(x, y, w, 20, fill=TINT.get(accent, "#f1f5f9"),
                  stroke=BORDER.get(accent, LINE), sw=1, r=10)
        self.text(x + w / 2, y + 14, label, size=size, anchor="middle",
                  fill=accent, weight=600)
        return self

    # ------------------------------------------------------------ 连线
    def arrow(self, *args, color=BLUE, label=None, dash=None, width=1.5,
              start=False, end=True, label_at=0.5, label_dy=-8,
              label_side="auto", bg=True) -> "Canvas":
        """支持三种写法：
        arrow((x1, y1, x2, y2))
        arrow((x1, y1), (x2, y2))
        arrow([(x1, y1), (mx, my), (x2, y2)])   # 显式折线
        """
        if len(args) == 1:
            pts = args[0]
            if isinstance(pts, tuple) and len(pts) == 4 and not isinstance(pts[0], (tuple, list)):
                pts = [(pts[0], pts[1]), (pts[2], pts[3])]
        elif len(args) == 2:
            pts = [args[0], args[1]]
        elif len(args) == 4:
            pts = [(args[0], args[1]), (args[2], args[3])]
        else:
            raise TypeError("arrow() 需要 1/2/4 个坐标参数")
        pts = [tuple(map(float, p)) for p in pts]
        self._edges.append((pts, color))
        d = f"M {pts[0][0]},{pts[0][1]} " + " ".join(
            f"L {x},{y}" for x, y in pts[1:]
        )
        mk_end = f' marker-end="url(#{self._marker(color)})"' if end else ""
        mk_start = f' marker-start="url(#{self._marker(color, True)})"' if start else ""
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.els.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linejoin="round"{dash_attr}{mk_start}{mk_end}/>'
        )
        if label:
            self._arrow_label(pts, label, color, label_at, label_dy,
                              label_side, bg)
        return self

    def _arrow_label(self, pts, label, color, at, dy, side, bg):
        # 取第 at 比例处的线段
        total = sum(((pts[i + 1][0] - pts[i][0]) ** 2 +
                     (pts[i + 1][1] - pts[i][1]) ** 2) ** 0.5
                    for i in range(len(pts) - 1))
        target = total * at
        acc = 0.0
        for i in range(len(pts) - 1):
            seg = ((pts[i + 1][0] - pts[i][0]) ** 2 +
                   (pts[i + 1][1] - pts[i][1]) ** 2) ** 0.5
            if acc + seg >= target or i == len(pts) - 2:
                t = (target - acc) / seg if seg else 0
                x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t
                y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t
                horizontal = abs(pts[i + 1][0] - pts[i][0]) >= abs(pts[i + 1][1] - pts[i][1])
                size = 11
                w = text_width(label, size)
                if horizontal:
                    tx, ty, anchor = x, y + dy, "middle"
                else:
                    if side == "left":
                        tx, ty, anchor = x - 8, y + 4, "end"
                    else:
                        tx, ty, anchor = x + 8, y + 4, "start"
                if bg:
                    bx = tx - (w / 2 if anchor == "middle" else (w if anchor == "end" else 0)) - 3
                    self.els.append(
                        f'<rect x="{bx:.1f}" y="{ty-size+1:.1f}" '
                        f'width="{w+6:.1f}" height="{size+5}" fill="{BG}" '
                        f'opacity="0.92" rx="3"/>'
                    )
                self.text(tx, ty, label, size=size, fill=color, anchor=anchor,
                          weight=500)
                return
            acc += seg

    def legend(self, x, y, items, size=11) -> "Canvas":
        """items: [(color, label, dash_or_None), ...]"""
        yy = y
        for color, label, dash in items:
            self.els.append(
                f'<path d="M {x} {yy} L {x+26} {yy}" stroke="{color}" '
                f'stroke-width="1.5" fill="none"'
                + (f' stroke-dasharray="{dash}"' if dash else "")
                + f' marker-end="url(#{self._marker(color)})"/>'
            )
            self.text(x + 33, yy + 4, label, size=size, fill=SUB)
            yy += 20
        return self

    # ------------------------------------------------------------ 输出
    def svg(self) -> str:
        out = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}">',
            f'<style>text {{ font-family: {FONT}; }}</style>',
            "<defs>" + "".join(self._markers.values()) + "</defs>",
            f'<rect width="{self.w}" height="{self.h}" fill="{BG}"/>',
        ]
        if self.title:
            out.append(f'<text x="24" y="38" font-size="17" font-weight="600" '
                       f'fill="{INK}">{html.escape(self.title)}</text>')
        if self.subtitle:
            out.append(f'<text x="24" y="60" font-size="12" fill="{SUB}">'
                       f'{html.escape(self.subtitle)}</text>')
        out.extend(self.els)
        out.append("</svg>")
        return "\n".join(out)

    def _self_check(self) -> None:
        """结构性自检：越界 / 节点重叠 / 连线穿框。比 XML 校验更接近"看起来对不对"。"""
        for (x, y, w, h, name) in self._nodes:
            if x < 8 or y < 8 or x + w > self.w - 8 or y + h > self.h - 8:
                self._warn.append(f"元素越界 [{name}]")
        for i in range(len(self._nodes)):
            ax, ay, aw, ah, an = self._nodes[i]
            for j in range(i + 1, len(self._nodes)):
                bx, by, bw, bh, bn = self._nodes[j]
                if ax < bx + bw - 2 and bx < ax + aw - 2 and \
                   ay < by + bh - 2 and by < ay + ah - 2:
                    self._warn.append(f"节点重叠 [{an}] × [{bn}]")
        for pts, _color in self._edges:
            for k in range(len(pts) - 1):
                (x1, y1), (x2, y2) = pts[k], pts[k + 1]
                steps = max(int(max(abs(x2 - x1), abs(y2 - y1)) // 6), 1)
                for s in range(steps + 1):
                    t = s / steps
                    px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                    # 端点附近是正常接触，跳过
                    if (px, py) in (pts[0], pts[-1]) or t < 0.06 or t > 0.94:
                        continue
                    for (nx, ny, nw, nh, name) in self._nodes:
                        if nx + 3 < px < nx + nw - 3 and ny + 3 < py < ny + nh - 3:
                            self._warn.append(
                                f"连线穿过 [{name}] @({px:.0f},{py:.0f})")
                            break

    def save(self, path: str, validate: bool = True) -> str:
        self._self_check()
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.svg())
        if self._warn:
            for w in sorted(set(self._warn)):
                print(f"[svgkit] WARN {os.path.basename(path)}: {w}")
        if validate:
            _validate(path)
        return path


_SKILL_SCRIPTS = os.path.expanduser(
    "~/.workbuddy/skills/fire-sjh__skillhub/scripts/validate_svg.py"
)


def _validate(path: str) -> None:
    """调用技能自带校验器：XML / marker / 碰撞 / 几何 / 构图预算"""
    if not os.path.exists(_SKILL_SCRIPTS):
        print(f"[svgkit] validator not found, skip: {path}")
        return
    ok = True
    for chk in ("xml", "markers", "collisions", "geometry"):
        r = subprocess.run(
            [sys.executable, _SKILL_SCRIPTS, "--check", chk, path],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            ok = False
            print(f"[svgkit] {chk} FAILED {os.path.basename(path)}")
            print((r.stdout or "") + (r.stderr or ""))
    if ok:
        print(f"[svgkit] ok {os.path.basename(path)}")
