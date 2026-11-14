# 项目进度与断点

> **下次从这里接着做。** 本文件是唯一进度事实源，续写前先读它。
> 最后更新：2026-11-14 14:40（终稿校验完成）

---

## 一、当前状态：**52 / 52 章 + 附录 7 / 7 —— 全书交付完成**

| 指标 | 数值 |
|---|---|
| 已完成正文 | **52 章**（Ch1 ~ Ch52，全书正文完） |
| 累计正文 | **248,674 汉字**（约 24.9 万字） |
| 配图 | **132 张 SVG**（`docs/images/chXX-figN.svg`） |
| 绘图脚本 | **52 个**（`tools/diagrams/chXX.py`，均可重跑） |
| 附录 | **7 / 7**（A~G 全完，46,332 汉字 + 11 图） |
| 全书合计 | **295,006 汉字**（约 29.5 万字）/ **143 张 SVG** / **59 个绘图脚本** |
| 实验环境 | `labs/` **18 个文件**，8.0 一主两从已实测跑通 |
| 完整性 | 52 章 7 段结构齐全，附录图引用零断链，禁用词零命中 |
| 终稿体检 | `python3 tools/verify_book.py` **零 ERROR、零 WARN** |

**已完成卷**：
- ✅ 第一卷 存储引擎与运行时架构（Ch1-7）—— 7/7
- ✅ 第二卷 索引与优化器（Ch8-15）—— 8/8
- ✅ 第三卷 事务与并发控制（Ch16-21）全完
- ✅ 第四卷 复制、高可用与备份（Ch22-28）全完
- ✅ 第五卷 数据建模与规模化（Ch29-35）全完
- ✅ 第六卷 性能诊断与调优（Ch36-41）—— 6/6 全完
- ✅ 第七卷 版本、内核与技术选型（Ch42-45）—— 4/4 全完
- ✅ 第八卷 工程规范与业务实战（Ch46-52）—— 7/7 全完
- ✅ 附录 A~G —— 7/7（46,332 汉字、11 图、`labs/` 18 个文件）

### 已完成章节明细

| 章 | 文件 | 汉字 | 图 |
|---|---|---:|---:|
| 1 | `docs/ch01-sql-lifecycle.md` | 3562 | 3 |
| 2 | `docs/ch02-innodb-memory.md` | 5978 | 3 |
| 3 | `docs/ch03-innodb-disk.md` | 5301 | 3 |
| 4 | `docs/ch04-redo-log.md` | 6147 | 3 |
| 5 | `docs/ch05-undo-purge.md` | 5213 | 3 |
| 6 | `docs/ch06-binlog-2pc.md` | 6176 | 3 |
| 7 | `docs/ch07-crash-recovery.md` | 3797 | 2 |
| 8 | `docs/ch08-btree-index.md` | 5516 | 3 |
| 9 | `docs/ch09-index-design.md` | 5531 | 3 |
| 10 | `docs/ch10-statistics-cost.md` | 3758 | 2 |
| 11 | `docs/ch11-explain.md` | 5259 | 3 |
| 12 | `docs/ch12-join-algorithms.md` | 5005 | 3 |
| 13 | `docs/ch13-subquery-cte.md` | 3690 | 2 |
| 14 | `docs/ch14-sort-temptable.md` | 3318 | 2 |
| 15 | `docs/ch15-query-rewrite.md` | 6181 | 2 |
| 16 | `docs/ch16-acid.md` | 5178 | 2 |
| 17 | `docs/ch17-isolation-mvcc.md` | 6298 | 3 |
| 18 | `docs/ch18-lock-taxonomy.md` | 5258 | 3 |
| 19 | `docs/ch19-locking-rules.md` | 5882 | 3 |
| 20 | `docs/ch20-deadlock.md` | 5998 | 3 |
| 21 | `docs/ch21-long-transaction.md` | 3495 | 2 |
| 22 | `docs/ch22-replication.md` | 5698 | 3 |
| 23 | `docs/ch23-gtid.md` | 3497 | 2 |
| 24 | `docs/ch24-semi-sync.md` | 3496 | 2 |
| 25 | `docs/ch25-parallel-replication.md` | 5666 | 3 |
| 26 | `docs/ch26-high-availability.md` | 5693 | 3 |
| 27 | `docs/ch27-mgr.md` | 3498 | 2 |
| 28 | `docs/ch28-backup-pitr.md` | 5114 | 3 |
| 29 | `docs/ch29-data-types-charset.md` | 5583 | 3 |
| 30 | `docs/ch30-primary-key-id.md` | 5691 | 3 |
| 31 | `docs/ch31-table-design.md` | 5489 | 3 |
| 32 | `docs/ch32-partitioning.md` | 3498 | 2 |
| 33 | `docs/ch33-sharding.md` | 5995 | 3 |
| 34 | `docs/ch34-distributed-transaction.md` | 3497 | 2 |
| 35 | `docs/ch35-lifecycle-multitenant.md` | 3500 | 2 |
| 36 | `docs/ch36-performance-method.md` | 5494 | 3 |
| 37 | `docs/ch37-monitoring.md` | 3493 | 2 |
| 38 | `docs/ch38-slow-query-ps.md` | 5500 | 3 |
| 39 | `docs/ch39-innodb-status.md` | 3418 | 2 |
| 40 | `docs/ch40-tuning.md` | 3489 | 2 |
| 41 | `docs/ch41-case-studies.md` | 7888 | 3 |
| 42 | `docs/ch42-mysql8-features.md` | 3496 | 2 |
| 43 | `docs/ch43-upgrade-migration.md` | 3500 | 2 |
| 44 | `docs/ch44-source-guide.md` | 3989 | 2 |
| 45 | `docs/ch45-cloud-native-selection.md` | 3591 | 2 |
| 46 | `docs/ch46-online-ddl.md` | 5408 | 3 |
| 47 | `docs/ch47-sql-review.md` | 3611 | 2 |
| 48 | `docs/ch48-security-compliance.md` | 3598 | 2 |
| 49 | `docs/ch49-trade-inventory.md` | 6155 | 3 |
| 50 | `docs/ch50-content-counter-queue.md` | 3966 | 2 |
| 51 | `docs/ch51-capacity-benchmark.md` | 4124 | 2 |
| 52 | `docs/ch52-incident-sop.md` | 5498 | 3 |

### 附录明细

| 附录 | 文件 | 汉字 | 图 | 内容 |
|---|---|---:|---:|---|
| A | `docs/appendix-a-parameters.md` | 8625 | 2 | 85 个参数 × 五列（含生效方式），六大类 |
| B | `docs/appendix-b-error-codes.md` | 5062 | 1 | 12 个错误码 × 四段（含"容易误判成什么"） |
| C | `docs/appendix-c-tools.md` | 4459 | 1 | 28 个工具 × 三段（含"什么时候不该用"） |
| D | `docs/appendix-d-diagnostic-sql.md` | 7481 | 2 | 40 条诊断 SQL × 四段，13 条标 ⚠️ |
| E | `docs/appendix-e-interview-100.md` | 13755 | 2 | 100 题七组，三段式，20 题标 ⭐ |
| F | `docs/appendix-f-learning-path.md` | 4154 | 2 | 三层同心圆 + 章节依赖 + 文档索引 |
| G | `docs/appendix-g-lab-setup.md` | 2796 | 1 | 实验环境文档 + `labs/` 18 个真实文件 |

---

## 二、交付状态：**全书完成，已通过终稿校验**

52 章正文 + 7 份附录全部落地，`labs/` 可跑。这一节记录"哪些已经确认、哪些只是写完了"。

### 终稿校验（2026-11-14，`tools/verify_book.py`）

一份零依赖的只读体检脚本，五个维度、可重复执行：

```bash
python3 tools/verify_book.py     # 退出码 0 = 通过
```

| 组 | 查什么 | 结果 |
|---|---|---|
| S 结构 | 52 章文件齐全、命名规范、首行章号、`## N.0`~`N.k` 连续、五个固定段（关键结论/实验验证/常见误区/Checklist/延伸）齐全且顺序正确、每章有图 | 通过 |
| F 图 | 143 张图全部被引用（无孤儿）、引用零断链、SVG 均为合法 XML、59 个脚本的产物与引用一一对应 | 通过 |
| T 文字 | 5 个禁用词零命中、无 `user`+`name` 反例、代码块全部标语言、`第 N 章` 引用全部落在 1~52 且指向存在的章 | 通过 |
| A 附录 | A 85 行 / B 12 条 / C 28 条 / D 40 条 / E 100 题编号连续；D 的 ⚠️ 实测 13 条并与正文自报清单逐条对上；E 的 ⭐ 实测 20 道 | 通过 |
| C 统计 | 逐章汉字数与图数与本章节表对账（±30 字） | 通过 |

**本次校验发现并修掉的问题（7 类）**

1. **附录 D 数量自相矛盾**：D.10 末尾写"把 ⚠️ 的八条单独标注"，同段上文与全表实测都是十三条 → 改为"十三条"。（这是"数量+清单必须脚本数"那条教训的漏网之处）
2. **ch41 缺「实验验证」段**：7 段结构里唯一缺的一段。补 41.14（原 41.13 关键结论顺移），把 `labs/ch41/` 的三个复现脚本接进正文——此前正文从未引用过这三个脚本。
3. **ch44 缺「实验验证」段**：补 44.9（原 44.8 常见误区顺移），内容是"用 `Handler_read_*` 增量 + gdb 断点把门被敲了几次数出来"，并给出 `Handler_*` 与引擎侧入口函数的映射表。
4. **库表命名与 `labs/` 不一致**：ch41 案例五与 ch52 卡片/实验段用了 `trade.order_detail`，而全书统一示例系统与 `labs/seed/01-schema.sql` 用的是 `shop.order_main` / `shop.order_item` → 全部改为 `shop` + `order_item`（共 13 处），否则读者照着正文 SQL 在实验环境跑不通。
5. **`warehouse_id` 跑不通**：ch52 实验二的 `UPDATE shop.stock ... AND warehouse_id = 3` 引用了 `labs` schema 里不存在的列（单仓模型）→ 改为 `AND qty >= 1`，与第 49 章主线一致。
6. **ch40 引错小节号**：`第 41 章 41.8（OOM 复盘）` → OOM 是案例八，在 41.9。
7. **22 处代码块未标语言**：全部补 `text`（都是输出形态、算式或参数表，无 SQL 块）。

### 已验证（有实跑证据）

- 59 个绘图脚本逐个实跑，全部 `[svgkit] ok`、**零 WARN**；143 张 SVG 全部由脚本生成，无手写
- 全书图引用零断链（扫描 `docs/**/*.md` 的 `](images/...)`）
- 禁用词零命中（在本文中 / 综上所述 / 值得注意的是 / 首先， / 其次，）
- 附录 E 题号 1~100 连续无缺，100 处回指章节，20 个 ⭐
- 附录 B 12 个码齐、附录 C 28 个工具齐、附录 A 85 个参数行
- `labs/`：`docker compose config` 两份均通过；8.0 一主两从**实测跑通**（复制 Yes/Yes、延迟 0），造数脚本实跑并导入校验（2000 单金额自洽）、ch19/ch41/ch52 的 SQL 实跑通过
- 附录 G 的 5 处 `labs/` 路径引用全部存在

### 未验证（写完了但没跑过，改的时候要注意）

- `labs/docker-compose-57.yml` 只过 YAML 校验，**没实拉 5.7 镜像**
- 8.4 镜像未测；半同步、MGR 无可运行验证（案例九只能读不能做）
- 附录 G 无自动化验证（没有 `make verify` / CI），改 compose 后需手工重跑 20 步
- 容器内复制延迟只有秒级，案例四的"台阶状长延迟"要放大数据或把 `replica_parallel_workers` 设为 1 才像
- 千万级造数只覆盖 `order_main` / `order_item`，库存与账户仍是万级

### 全书交叉校验：已完成（五组结论）

| 组 | 核对点 | 结论 |
|---|---|---|
| Ch1 / Ch4 / Ch6 | 两阶段提交的时序与崩溃判据 | 一致。Ch1 给时序（写 redo 记 prepare → 写 binlog → redo 改 commit）与四行崩溃恢复表；Ch6 给"flush / sync / commit"三段组提交，并把 commit 段定义为"通知 InnoDB 把 redo 从 prepare 改成 commit"。两处都以"binlog 完整即提交"为判据，且都以 `XID` 作为对齐 redo prepare 记录的锚点 |
| Ch5 / Ch17 | purge 水位的字段口径 | 一致且已互相背书。Ch5 用 `up_limit_id` = 活跃 `m_ids` 最小值定义水位；Ch17 明确"源码字段是 `m_up_limit_id`，本书第 5 章写作 `min_trx_id`，指的是同一个数"，并补了 `m_low_limit_no`（按 undo trx_no 计）与 `m_up_limit_id`（按 trx_id 计）的区别 |
| Ch8 / Ch9 | 覆盖索引省的是什么 | 一致。Ch8 从物理结构讲"二级索引叶子存 `(索引列, 主键)`，覆盖省的是第二次下降"；Ch9 从执行计划讲"`Using index` = 根本不回表"，并把 `Using index` / `Using index condition` / `Using where` 三种 `Extra` 的边界切清楚，两章不重叠也不冲突 |
| Ch22 / Ch25 | 复制链路落盘次数 | 一致。Ch22 算的是 3 次关键路径 fsync（主 binlog ① / 从 binlog ③ / 从 redo ④，relay log ② 被 `sync_relay_log=10000` 摊薄）；Ch25 开篇直接引用"第 22 章算过的那三次 fsync 决定的是截距"，把截距（物理上限）与斜率（容量问题）分开，治理手段只作用在斜率上 |
| Ch41 / Ch52 | 十个案例与十张处置卡片 | 一致。卡片 1~10 的症状、判据、首选取证、根因章节与案例一~十逐条对应（连接数 / QPS 骤降 / P99 尖刺 / 台阶延迟 / MDL / 死锁 / 磁盘满 / OOM / 半同步降级 / 误删）。案例七的"undo 各几百 GB + 四百多个 binlog + 九小时报表事务"、案例八的"160 导出 × 256M ≈ 40G、buffer pool 96G、机器 128G"在卡片里数字不矛盾 |

### 剩余可选项（不影响交付）

1. **`docs/00-能力地图与学习路径.md`**：可作为附录 F 的"书前页"，把三层同心圆放到最前面；评估结论已写在本文第五节，尚未单独成文
2. **git 首次提交**：当前是最干净的检查点（正文+附录全齐、体检零告警、无半成品）
3. `labs/` 补 5.7/8.4 实拉、半同步与 MGR 的验证环境、一个 `make verify`（现在靠 `tools/verify_book.py` 守内容、靠手工 20 步守环境）

### 七份附录的成稿约定（后续修订时遵守）

- 文件名 `docs/appendix-<字母>-<kebab>.md`；图与脚本不占 `chXX` 编号，用 `appX-figN.svg` / `tools/diagrams/appX.py`
- 附录不套章节 7 段模板，用 `X.0 怎么用` → 分组 → 关键结论 → 延伸
- 条目编号 `A1~A85` / `B1~B12` / `C1~C28` / `D1~D40` / `E1~E100`，每条固定分段（D 是"用途/SQL/读法/坑"，B 是"触发/日志/处置/易误判"，C 是"解决什么/不该用/最小命令"）
- **凡写"数量 + 清单"必须用脚本数一遍**——附录 D 曾把 13 条写成"八条"，附录 A 的 85 行也要靠脚本核
- 附录 G 的金额列叫 `pay_amount`（与 Ch49、附录 D13 一致），不要写成 `amount`
- **`super_read_only` 不写进 cnf**：实测会让容器 entrypoint 的 `ALTER USER` 报 1290 并退出；改成配完复制后 `SET PERSIST`


## 三、写作工作流（今后扩写 / 修订时复用）

### 1. 每章一个独立 agent，4 个并行一批

提示词模板（每次只需替换章号、标题、知识点、配图建议、红线补充）：

```
你是《MySQL 圣经》作者，撰写 第 N 章《标题》（★级，字数）。

## 必读
1. docs/_WRITING_SPEC.md（严格遵守）
2. docs/OUTLINE.md 的「### 第 N 章」小节
3. 前序相关章节（避免重复）+ docs/ch01-sql-lifecycle.md（风格基准）
4. tools/svgkit.py + tools/diagrams/ch01.py

## 产出
- docs/chNN-slug.md：7 段结构、小节 ## N.1、字数、章节知识点清单、开场场景
- docs/images/chNN-figN.svg：2~3 张，必须用 svgkit，禁止手写 SVG
- tools/diagrams/chNN.py：照 ch01.py 结构，必须实跑
- 必须做到全部 `[svgkit] ok` 且零 `WARN`

## 红线
不许编造精确数字（未实跑输出写"预期形态"）；参数/视图名必须真实；
版本差异标 [5.7]/[8.0.x]/[8.4]；结论必须有机制解释；
禁止"在本文中/综上所述/值得注意的是"；例子用有业务感的表；
不改他人文件、不新建其他文件。

## 回报（简短）
文件路径 + 字数 + 每图一句 + 3 条最关键结论。不粘贴正文。
```

### 2. 绘图工具链（已跑通，别 reinvent）

- 唯一入口 `tools/svgkit.py`：`Canvas / box / mono_box / cyl / container / diamond / pill / badge / arrow / legend / text / save`
- `save()` 自动跑：结构自检（越界/节点重叠/连线穿框/文字溢出）+ 技能校验器（xml / markers / collisions / geometry）
- 颜色语义固定：`BLUE` 主流程、`RED` 危险/锁/阻塞、`GREEN` 写入落盘、`PURPLE` 日志/复制、`ORANGE` undo/回滚、`SLATE` 跨层/虚线
- 校验器路径：`~/.workbuddy/skills/fire-sjh__skillhub/scripts/validate_svg.py --check {xml|markers|collisions|geometry} <svg>`
- ⚠️ 本机**没有 libcairo**，`cairosvg` 装了也用不了；`qlmanage` 同样不可用。所以**不要用 cairosvg 导出 PNG**，Markdown 直接引用 SVG 即可。视觉正确性首先靠 svgkit 的结构自检；结构自检抓不到"语义性重叠"（比如几条箭头指向同一个点），必要时用 Chrome 无头截图目检一次。

### 3. 每批结束后的体检（不调用子进程）

用纯 Python 读文件检查：汉字数、图引用是否存在、`## N.x` 小节数、7 段是否齐全。不要批量 `subprocess` 重跑绘图脚本——已被安全策略拦截过一次，各章生成时已逐个实跑通过。

### 4. 已验证有效的内容手法

- 每章用一个**反直觉故障**开场（"命中率 99.9% 但 P99 每 40 秒抖一次"），而不是定义
- 每个机制都要回答"**如果不这样设计会怎样**"（如 Ch8 反证"二级索引若存行地址，页分裂要全改"）
- 结论段用 3~6 条加粗短句，可直接引用
- 误区段固定格式：错误认知 → 为什么错 → 正确理解
- 实验段：未实跑的输出必须标"预期形态"，不许伪装成真实日志

---

## 四、待办与已知问题

### 内容层

- [x] **附录 A~G 全部完成**（46,330 汉字 / 11 图，明细见第一节）
- [x] Ch41 案例复盘集：10 个案例六段式 + 三类误判框架，每案例回指章节，兼作全书索引页
- [x] Ch52 应急 SOP：十张处置卡片复用 Ch41 的十个案例，逐条核对过事实一致性
- [x] Ch47 治理闭环：Owner 制 / SLA 分档 / TOP SQL 周报 / 豁免流程均已落地
- [x] **全书交叉校验**：五组（Ch1/4/6 两阶段提交、Ch5/17 purge 边界、Ch8/9 覆盖索引、Ch22/25 落盘次数、Ch41/52 十案例）逐条核对通过，结论见第二节
- [x] **`tools/verify_book.py`**：零依赖全书体检脚本，五组检查、可重复跑，当前零 ERROR 零 WARN
- [ ] **`docs/00-能力地图与学习路径.md`**：用户问过"学完能否成为资深工程师"，评估结论在第五节，尚未正式成文；可直接复用附录 F 的三层同心圆（可选扩展，不影响交付）

### 工程层

- [x] `labs/` **18 个文件**：compose（8.0 一主两从 + 5.7）、四份 cnf、造数（万级/千万级/倾斜）、ch01/ch19/ch41/ch52 实验脚本、README 映射表
- [x] 正文里唯一一处 `labs/` 引用（Ch1 第 204 行的 `labs/ch01/seed.sql`）已存在，断链消除
- [x] `labs/` 实测：8.0 一主两从复制跑通、造数导入金额自洽、ch19/ch41/ch52 SQL 实跑通过、两份 compose 过 `config`
- [x] `README.md` 进度区同步到全书完成
- [x] **`tools/verify_book.py` 落地**：结构 / 图 / 文字 / 附录 / 统计五组检查，`python3 tools/verify_book.py` 一条命令验全书，当前零 ERROR 零 WARN
- [ ] **`labs/` 的三处缺口**：5.7 与 8.4 镜像未实拉、半同步与 MGR 无验证环境、没有 `make verify` / CI（改 compose 后需手工重跑 20 步）
- [x] git 仓库已初始化（`main`，已有 2 次提交，配了 `origin`）；本轮终稿修改**未提交**，留给作者自己提交


### 事实修订（agent 在撰写时主动纠正，已写入正文，此处备案）

- `NOW()` 在 STATEMENT 格式下是**安全**的（时间戳随事件 header 走），真正不安全的是 `SYSDATE()` —— 已写进 Ch6，别改回去
- `INNODB_TABLESTATS` 在 8.0 是**由 `INNODB_SYS_TABLESTATS` 改名**，不是被移除；真正移除的是 `INNODB_LOCKS` / `INNODB_LOCK_WAITS` —— 已写进 Ch10 的误区段
- `innodb_force_recovery` 第 5 级是 `SRV_FORCE_NO_UNDO_LOG_SCAN`（部分资料误写为 `NO_UNDO_TRUNCATE`）—— 已写进 Ch7
- 隐式类型转换的方向性：字符串列 + 数字值 → 列被 CAST，索引失效；数字列 + 字符串值 → 转的是值，索引不受影响 —— Ch9 的场景已按此写，别按最初的相反设定改
- `max_trx_id` 是**"下一个将分配"**的事务 id（源码 `m_low_limit_id`），不是"最大值"；`min_trx_id` 就是源码的 `m_up_limit_id`。这两个边界各错一格，Ch17 的六情形可见性表会全盘皆错
- 版本链上**不可能有两个同时活跃的事务先后改同一行**（写者必须先拿到行锁、前一个必须已提交），所以 Ch17 的图与文字用 903/905/911/912 而非相邻 id
- Ch19 开场场景里 `sku_id` 是**普通索引**而非唯一索引：唯一索引等值命中会退化成记录锁，锁不出"记录 + 后面间隙"的现象，与本章原则三自相矛盾
- MDL 事故的处置要点：去 `performance_schema.metadata_locks` 找**状态为 GRANTED 且对应线程处于 Sleep** 的那行，它才是堵住队列的长事务，不是 `PROCESSLIST` 里显示 `Waiting` 的那些 —— 已写进 Ch18
- `information_schema.innodb_trx.trx_state` 的真实枚举是 `RUNNING` / `LOCK WAIT` / `ROLLING BACK` / `COMMITTING`；写成 `ROLLBACK` 查不到 —— 已写进 Ch21
- `sys.innodb_trx` **没有** `trx_age` 这个列（那是 `sys.session` 家族的写法）；算事务年龄要自己 `TIMESTAMPDIFF` —— 已写进 Ch21
- `trx_autocommit_non_locking` 只排除"只读且不加锁的单语句事务"，且只覆盖毫秒级；**长 `SELECT` 不在此列**，它仍持有 ReadView、仍钉 purge 水位 —— 已写进 Ch21，别把它当成长查询豁免证
- `KILL` 之后 `trx_state` 进 `ROLLING BACK`，锁与 undo 仍被占用，回滚耗时**可能超过执行耗时**（因为回滚要逐条反向写 undo + redo，且 undo 链是串行的）—— 已写进 Ch21
- 半同步 `AFTER_SYNC` 下崩溃**不是回滚而是前滚**：binlog 已 fsync，恢复必定重放它。所以"客户端收到失败"不等于"事务没发生"，重试必须靠业务幂等 —— 这是 Ch24 的核心论点，别写成"AFTER_SYNC 崩溃会回滚所以重试安全"
- 复制链路的落盘账（Ch22）：默认配置下同一条事务有 **3 次串在关键路径上的 fsync**（主库 binlog ① / 从库 binlog ③ / 从库 redo ④），relay log 那一次被 `sync_relay_log=10000` 摊薄到几乎为零，因为它是**可丢弃的中间态**（`relay_log_recovery=ON` 会整段重拉）。这是"复制延迟下限不为 0"的物理来源
- `gtid_executed` = 我有什么，`gtid_purged` = 我丢了什么，`gtid_owned` = 我正在做什么。决定从库能否接上的是**第二个**，而 `SHOW REPLICA STATUS` 里看不到它 —— 已写进 Ch23
- 看到 `Waiting for dependent transaction to commit` **说明并行是生效的**，瓶颈在提交顺序（`replica_preserve_commit_order` 的"并行回放、串行提交"）。判反了就会一路加 worker 而毫无效果 —— Ch25 用三种形态（N 个 Waiting + 1 个 Executing / 全部 Waiting / 交替出现）给出判读法
- 多线程下 `Exec_Source_Log_Pos` 是**低水位**，按 `replica_checkpoint_group`（默认 512 事务）或 `replica_checkpoint_period`（默认 300ms）批量推进，看到的是台阶不是进度条 —— 已写进 Ch25
- `WRITESET` 的行哈希**以主键值为输入**，无主键表算不出写集，依赖判定退回提交顺序（等于该表串行）。这是"必须加主键"比"查得快"更硬的理由 —— 已写进 Ch25
- MGR 认证是**乐观**的：事务先在本地执行完才广播写集，冲突则回滚（`ERROR 3101`）；且**认证通过 ≠ 已应用**，默认 `EVENTUAL` 下从节点仍可能读到旧值 —— 已写进 Ch27
- RPO=0 的成立条件有三个，缺一不可：`wait_point=AFTER_SYNC` + 未发生超时降级 + **被提升的正是那个 ACK 过的从库**。只说"配了半同步就 RPO=0"是错的 —— 已写进 Ch26
- 切换时"隔离完成"的判据**不是** `super_read_only=ON`，而是 `innodb_trx` 清空（一个还在提交的大事务会让"只读已开、仍在写"持续存在）—— 已写进 Ch26
- PITR 的 `--stop-position` 要取误操作 `BEGIN` 事件的 `# at`（等于它前一条事件的 `end_log_pos`）；`--stop-datetime` 包含该秒内所有事务，只能缩范围不能当刀口；`SHOW BINLOG EVENTS` **不输出时间戳**，对时间要靠 `mysqlbinlog --start-datetime` —— 已写进 Ch28
- `mysqlpump` 在 `[8.0.34]` 已废弃（不代表不能用，但新方案别再选它）；`--master-data` 在 `[8.0.26+]` 改名 `--source-data` —— 已写进 Ch28
- `DECIMAL(18,2)` 是 **9 字节**不是 8：16 位整数按 9+7 分组（4+4 字节），2 位小数再占 1 字节。每 9 位十进制用 4 字节，剩余位数按 1-2 位 1 字节 / 3-4 位 2 字节 / 5-6 位 3 字节 / 7-9 位 4 字节 —— 已写进 Ch29，我最初的提示词里写的是 8，agent 纠正了
- `DATETIME` 是 **5 字节**（`[5.6.4+]` 起的紧凑格式），`DATETIME(6)` 是 5+3=8 字节。"DATETIME 占 8 字节"是 5.5 时代的记忆 —— 已写进 Ch29，别再按 8 字节算
- **utf8mb4 下 VARCHAR 长度前缀的分界在 63/64 字符**（63×4=252B 用 1 字节，64×4=256B 用 2 字节），不是 255/256。`VARCHAR(255)` 与 `VARCHAR(256)` 都是 2 字节前缀，一个字节都不差 —— 已写进 Ch29，这是最常见的算错点
- "`VARCHAR(255)` 比 `VARCHAR(20)` 慢"只在按上限分配的场景成立：`[5.7]` 的 `MEMORY` 临时表、filesort 排序缓冲区（用字段 `max_length` 估行宽）。InnoDB 行内与 `[8.0]` TempTable 都按实际长度 —— 已写进 Ch29，别写成普遍结论
- `utf8mb4_general_ci` 是 **PAD SPACE**，`utf8mb4_0900_ai_ci`（8.0 默认）是 **NO PAD**：`'SH'` 与 `'SH '` 在前者下相等（唯一索引报 1062），在后者下不等。同一个唯一键需求，两套 collation 结论相反 —— 已写进 Ch29
- 自增用尽报 **1467**（`Failed to read auto-increment value`），整表插入全失败，不是回绕成负数；`[5.7]` 重启按 `MAX(id)+1` 重算会重发已删除的号，`[8.0]` 把计数器写进 redo 只前进不回退 —— 已写进 Ch30
- `DB_ROW_ID` 是 6 字节**全局共享**计数器（所有无主键表共用同一个）、**不持久化**，而且会被塞进二级索引作为行标识 —— 已写进 Ch30，别把它当成"每表独立的主键"
- 分区表要求唯一键包含分区列，于是主键写成 `PRIMARY KEY (id, create_time)`：**数据库不再强制 `id` 单独唯一**（应用层必须自己保证），且每条二级索引的叶子要多存一列、回表多带一列 —— 已写进 Ch32
- 判断单表容量不看 B+ 树层数，看**倒数第二层装不装得进内存**：三层树时它固定约 950 页（与行数无关），四层时按 `leaf_pages / 947` 膨胀，这才是内存边界被突破的时刻 —— 已写进 Ch33
- 分片数不是拍 1024，按 `三年后行数 ÷ 单分片目标容量` 向上取 2 的幂；多出来的倍数会**同时乘在连接数、DDL 广播次数与广播查询上** —— 已写进 Ch33
- 分片下的深分页，**只有游标分页（`WHERE id > ?`）是 O(1)**；二次查询法只是把系数从 N 降到约 1，仍是 O(N) —— 已写进 Ch33，别把二次查询法说成"解决"了深分页
- 双倍扩容（N→2N）只有一半数据要搬：`hash % 2N` 后仍落在原分片的那些行原地不动。这是它优于"任意 N→M"的全部原因 —— 已写进 Ch33
- **InnoDB 内部 2PC 与 XA 是两层东西**：前者对齐 redo 与 binlog、由崩溃恢复消费；后者跨实例、应用当协调者。共同点只有"两个阶段"这个形状 —— Ch34 开篇用对照表钉住，别写成"binlog 2PC 就是分布式事务"
- `innodb_support_xa` 在 `[5.7]` 存在（默认 `ON`），`[8.0]` **已移除**，XA 内置、关不掉。8.0 上"关掉 XA 换性能"是无效经验 —— 已写进 Ch34
- `PREPARED` 状态的 XA 事务在 `innodb_trx` 里 `trx_mysql_thread_id` 为 **NULL**（连接已断），锁不放、`trx_id` 仍占活跃列表、purge 水位降不下去。识别它靠 `trx_state='PREPARED'` —— 已写进 Ch34
- 共享表多租户下，**`tenant_id` 必须是所有索引的第一列，唯一索引也要带它**（`UNIQUE(tenant_id, order_no)`），否则两个租户的单号会撞 —— 已写进 Ch35
- 共享表方案最隐蔽的代价是**共享 buffer pool**：LRU 是全局的，一个大租户的全表扫描会把其他租户的热页挤出去，症状是"全站命中率下降 + IOPS 上涨"且按实例维度定位不到原因 —— 已写进 Ch35
- `max_execution_time` `[5.7.8+]` **只对 `SELECT` 生效**（超时抛 3024），写语句不受约束——归档脚本的 `DELETE` 只能靠批大小兜 —— 已写进 Ch35
- `Sending data` **不是"在发数据"**：读行、处理、发结果全算在这个状态里，扫描时间包含在内。一条 `Sending data` 跑几十秒的查询，九成是扫描量或排序问题，与网卡无关 —— 已写进 Ch36，这是最高频的误读
- `Innodb_buffer_pool_wait_free > 0` 说明 buffer pool 已经在等刷脏页，是**严重的饱和信号**（USE 方法里的 Saturation），比命中率下降更早出现 —— 已写进 Ch36
- 阻塞锁查询表：`[8.0]` 是 `performance_schema.data_lock_waits`，`[5.7]` 是 `information_schema.innodb_lock_waits`，列名也不同 —— 已写进 Ch36
- 单次 `SHOW PROCESSLIST` 快照**没有判读价值**：分不出"卡住"与"正在跑"，必须间隔 10 秒连采三次，同一 `State` 出现三次才算卡住 —— 已写进 Ch36
- 过载后加并发 QPS 反而下降，用 Little's Law（`L = λ × W`）解释：它是恒等式不是模型，所以"并发涨、吞吐降、延迟暴涨"必然同时出现；此时加重试会让情况更糟（重试放大并发）—— 已写进 Ch36
- `SHOW GLOBAL STATUS` 的绝大多数值是**从启动起的累计量**，必须两次采样求差再除间隔；**实例重启会让计数器归零、rate 变负数**，监控侧必须整窗丢弃，否则"跌零"告警与小时均值同时被污染 —— 已写进 Ch37
- `Innodb_row_lock_time_avg` 是**累计平均**（总等待时间 / 总等待次数），不是"最近的平均"，要看当前形态必须用窗口内两次采样的差分 —— 已写进 Ch37
- BP 命中率不能按百分比告警：99.9% 在十亿级 `read_requests` 下意味着百万次物理读，而新实例预热期天然低。**要按物理读的绝对次数告警** —— 已写进 Ch37
- checkpoint 年龄 = `Log sequence number` − **`Last checkpoint at`**。减 `Log flushed up to` 得到的是"未落盘 redo"，会系统性低估，是最常见的算错点 —— 已写进 Ch37 / Ch39
- `[8.0.30+]` 起 redo 容量由 **`innodb_redo_log_capacity`** 统管（默认 100MB），`innodb_log_file_size` × `innodb_log_files_in_group` 那套是 8.0.30 之前的算法 —— 已写进 Ch39
- 慢日志的判据是"**单条语句 vs 阈值**"，对"12 条各 80ms 拼成 900ms"的链路型慢天然失明，对"0.8s × 50/s"的高频型慢也看不见（每条都没到阈值）。只有 digest 表的 `SUM_TIMER_WAIT` 增量能看见总量 —— 已写进 Ch38
- `events_statements_summary_by_digest` 的 `SUM_TIMER_WAIT` 是**累计值**，不配 `COUNT_STAR` 增量看，榜首会全是三天前跑过一次的语句；平均耗时榜与总耗时榜结论常常相反（前者伤个别用户、后者伤整体容量）—— 已写进 Ch38
- digest 表**只有 `SCHEMA_NAME`，没有 user/host**，"定责到业务方"这一步拿不到调用方信息的；SQL 注释打标是否参与归一化各版本不一致，必须先在测试库验证 —— 已写进 Ch38
- `SHOW ENGINE INNODB STATUS` 的 `TRANSACTIONS` 段**最多只打印 10 个活跃事务**，超出部分看不到；`ACTIVE 22 sec` 是**事务年龄不是语句年龄**；`undo log entries` 才是回滚成本的直接读数 —— 已写进 Ch39
- `ROW OPERATIONS` 段的 `queries inside InnoDB` / `queries in queue` 是判断"InnoDB 内部排队"的唯一直接证据；`queue` 持续 > 0 说明线程在等入口名额（`innodb_thread_concurrency` 被设成非 0 时才会发生），此时加 CPU 无效 —— 已写进 Ch39
- `SEMAPHORES` 段的 `os_waits` 高**不是行锁竞争**，是 InnoDB 内部 mutex/rw_lock 的内核等待（`buf_pool_mutex`、`log_sys`、`btr_search_latch`）；`spins` 高而 `os_waits` 低说明自旋能解决、争用不严重 —— 已写进 Ch39
- MySQL 的 OOM 现场先查 `sort_buffer_size` / `join_buffer_size` × `Threads_running`，**不是**先怀疑 `innodb_buffer_pool_size` 太大；后者调小只是把内存让给了那个乘法 —— 已写进 Ch40，这是参数章的主线
- `tmp_table_size` 与 `max_heap_table_size` 实际生效值**取两者较小**，只调大前者不会生效 —— 已写进 Ch40
- `eq_range_index_dive_limit`（默认 200）与 `range_optimizer_max_mem_size`（默认 8MB）造成的不是"渐变变慢"，而是**计划断层**：IN 列表 199 个与 201 个值之间执行计划可能完全不同 —— 已写进 Ch40
- `innodb_io_capacity` 默认 200 是 HDD 时代的预算，SSD 上按设备 IOPS 的 50~70% 设；`innodb_flush_neighbors` 在 `[8.0]` 默认已是 0（`[5.7]` 默认 1）—— 已写进 Ch40
- 透明大页（THP）要关：`khugepaged` 周期合并页造成延迟抖动，大页分配失败时触发直接回收 —— 已写进 Ch40
- `wait_timeout` / `interactive_timeout` 改小**只对新连接生效**，存量连接仍按连接时读到的值计时。泄漏型连接数打满的现场，改完参数必须按 `Time > 3600` 把老 `Sleep` 连接 `KILL` 掉，否则"改了没反应"—— 已写进 Ch41 案例一
- MDL 队列是**写优先**的：DDL 拿到 `PENDING` 之后，后来的普通查询也要排在它后面。所以一个 `Sleep` 连接持有 MDL、一个 DDL 在等它，就能堵死整库——"等 DDL 跑完"是错的处置，要 `KILL` 那个 `Sleep` 的会话 —— 已写进 Ch41 案例五（与 Ch18 的判读法一致）
- `eq_range_index_dive_limit`（默认 200）被越过之后，优化器**不是放弃索引**，是把"逐值 index dive"换成"按索引统计估算"；配合陈旧的 `mysql.innodb_table_stats`，估出的行数会偏小到让 `range` 变成 `ALL` —— 已写进 Ch41 案例二，别写成"IN 列表太长所以索引失效"
- 半同步的降级是**自动的、静默的**：`rpl_semi_sync_source_timeout` 到点就退回异步，`Rpl_semi_sync_source_status` 变 `OFF`，而 `SHOW REPLICA STATUS` 一切正常（`Seconds_Behind_Source=0`、两线程 `Yes`）。**它不属于"复制是否正常"这一族指标**，必须单列告警 —— 已写进 Ch41 案例九
- 8.0 的"元数据查询变快"主要来自 `information_schema` 不再逐个打开 `.frm`、改查数据字典表，**与 SQL 执行速度无关**；代价是 `information_schema_stats_expiry`（默认 86400 秒）会让 `SHOW TABLE STATUS` 显示缓存值 —— 已写进 Ch42
- Hash Join `[8.0.18+]` 只在**等值连接且被驱动表用不上索引**时接管，省掉的是内层重复扫描（N×M → N+M），**驱动表全扫的成本一分没少**。`rows` 上万还出现 hash join，说明缺的是索引，不是"版本给了新武器" —— 已写进 Ch42
- `mysql_upgrade` 从 `[8.0.16]` 起退役（服务端 `--upgrade=AUTO|FORCE|MINIMAL|NONE` 接管），`[8.4]` 客户端被移除。**跨大版本没有降级路径**，8.0 回 5.7 只能恢复备份或用逻辑导出重导 —— 已写进 Ch43
- **5.7 从库不能从 8.0 主库复制**（复制不支持目标版本低于源版本）。滚动升级切换完成后，旧 5.7 主库**不能挂回链路当从库**，只能作冻结副本等回滚。这修正了大纲 43.4 里"旧主降为从"的画法 —— 已按此写进 Ch43 的图 43-2 与正文
- `Handler_read_*` 系列数的是**Server 层向引擎要行的调用次数**，不是引擎内部扫过的记录数；把 `Handler_read_next`、`Handler_read_rnd_next`、`Innodb_rows_read` 混成一个口径，就会得出"走了索引却扫了几万行"这种自相矛盾的结论 —— 已写进 Ch44
- 8.0 的 page cleaner 拆成了 **`page_flush_coordinator_thread` + 多个 `page_flush_thread`**（5.7 是单个 `page_cleaner_thread`），在 `performance_schema.threads` 的 `NAME` 列里能直接看到 —— 已写进 Ch44
- 存算分离（Aurora / PolarDB 一族）里，只读副本**回放的是同一份日志、不再各自持有一份数据**，所以延迟瓶颈从"回放算力"移到"日志传播"——第 25 章那套并行复制调优在云上基本失效，因为 worker 不是瓶颈 —— 已写进 Ch45
- 云上 Proxy 会**钉住**带会话状态的连接（开了事务、用了临时表、设了用户变量），复用率骤降，表现为连接数莫名上涨；`Threads_connected` 数的是"代理到库"的连接，第 41 章案例一的池上限公式在云上要按代理池重算 —— 已写进 Ch45
- `ALGORITHM=INSTANT` 有**每表 64 次**的硬上限（记录头的行版本号只有 7 位），第 65 次直接拒绝、必须换 `INPLACE` 重建；`information_schema.INNODB_TABLES.TOTAL_ROW_VERSIONS` 看已用次数，重建后归零 —— 已写进 Ch46
- `INPLACE` 说的是"在哪做"，`ONLINE` 说的是"允不允许并发 DML"，**是两个维度**：加空间索引也是 `INPLACE`，但并发 DML 被挡。改表期间的增量写进 online log，上限由 `innodb_online_alter_log_max_size`（默认 128MB）控制，撑爆则 DDL 直接失败 —— 已写进 Ch46
- 不写 `ALGORITHM=` 与 `LOCK=` 时，服务器会**静默降级**（`INPLACE` → `COPY`）。你以为在跑在线变更，实际在拷全表——这是 DDL 事故里最常见的一种"什么都没做错" —— 已写进 Ch46
- 审核规则引擎匹配的是**文本形态**，匹配不到数据分布与执行时的并发；`rows` 本身是估算值，统计信息陈旧时连它也是错的（第 41 章案例二就是这样通过审核的）—— 已写进 Ch47
- 治理必须同时看 digest 的**两张增量榜**：`SUM_TIMER_WAIT` 增量找"谁最贵"（改 SQL/加索引），`COUNT_STAR` 增量找"谁最频繁"（减调用/加缓存）。两张榜的处置动作不通用 —— 已写进 Ch47
- `GRANT` / `REVOKE` **同时**更新内存 ACL 与授权表，立刻生效、不需要 `FLUSH PRIVILEGES`；后者只在"有人直接 DML 改了授权表"之后才有意义。`[8.0]` 起 `mysql.user` 是数据字典之上的视图，直接 DML 会被拒绝 —— 已写进 Ch48，这条误解在生产上制造过大量"改了不生效"
- `'app'@'localhost'` 与 `'app'@'127.0.0.1'` 是**两个不同账号**：`localhost` 走 socket，用 TCP 连 `127.0.0.1` 只会匹配 `127.0.0.1` 或 `%`，不匹配 `localhost` —— 已写进 Ch48
- `audit_log` 插件属**企业版**，社区版**没有**官方审计插件；社区版三条替代路径（`general_log` / 代理旁路 / 应用埋点）各有硬代价，所以社区版的现实策略是"事前不给权限"而不是"事后能查" —— 已写进 Ch48
- 库存扣减的并发安全**只能靠"判断与修改在同一条语句里"**：`UPDATE ... WHERE sku_id = ? AND qty >= 1` 里的 `qty >= 1` 是当前读、在行锁内判断；应用层 `SELECT` 之后再 `if` 在并发下等于没写 —— 已写进 Ch49 开场，这是全章的主线
- 乐观锁**不是普遍更快**：冲突率到两成左右就会反转（重试次数指数上升）。判断依据是**同一个 key 的并发度**，不是实例总 QPS —— 已写进 Ch49
- 预扣 + 流水表的超卖窗口，**在"异步维护余量字段"那一步**：要么余量不精确（有窗口），要么每次 `SUM`（退化成聚合慢查询）。它的正确形态是"预留 + 定期结算"，不是"实时精确" —— 已写进 Ch49
- 幂等三层防线（唯一索引 / 状态机 / Redis 去重）里**只有唯一索引是不可绕过的**；且重复键报 1062 时 InnoDB 会在冲突记录上留一把 S 锁，捕获异常后应**先回滚再查**，否则查到的还是自己事务里的视图、且可能卡住别人的更新 —— 已写进 Ch49
- 计数的三种做法（单行 / 分桶 / Redis+落库）差别不在性能，在**"准确性承诺"**：允许短暂不准才用 Redis，必须精确且并发高才分桶。选型先定"能错多久"，再定实现 —— 已写进 Ch50
- Feed 推模式的写放大，卡住的**不只是插入速度**，更是从库的并行回放：一个 100 万粉丝的账号发一条会产生一个百万行级的大事务，从库只能串行回放它（第 25 章）—— 已写进 Ch50
- `SELECT ... FOR UPDATE SKIP LOCKED` `[8.0]` 只解决"多消费者不抢同一行"，**可见性超时、重试退避、死信三件事都得自己实现**；且"取任务"与"处理任务"必须分成两个事务，否则事务时长 = 业务处理时长，会钉住 purge —— 已写进 Ch50
- 命中率的天花板由 **buffer pool ÷ 表大小** 决定（示例：40G ÷ 192G ≈ 21%），不是由调优决定。"命中率 97%"靠的是**热数据只占一小部分**，不是"数据装得下"；一旦出现全量扫描型查询（对账/报表），这个假设立刻失效 —— 已写进 Ch51
- 压测环境与生产的三个偏差里，**"数据量小导致命中率虚高"是唯一能把结论完全反过来的一项**——它不能靠乘系数修正，只能把压测库灌到生产量级（或用生产从库做只读压测）—— 已写进 Ch51
- **重启不是止血手段，是"放弃现场"**：它销毁锁等待链、`SHOW ENGINE INNODB STATUS` 快照与 `p_s` 历史，而这些是根因的唯一证据。只有"服务完全不可用且重启已知有效"时才重启，且重启前必须先抓现场 —— 已写进 Ch52
- 事故分级的作用不是"上报给谁"，是**"决定允许哪些动作"**：P0 可以跳过变更审批直接止血，P2 不可以。同理，on-call 交接必须给"当前假设 + 已排除项 + 下一步"，"你看着办"是事故二次延长的常见原因 —— 已写进 Ch52

**附录 D 期间核准的 7 处事实：**
- `events_statements_summary_by_digest` 的时间列是**皮秒**（除以 `1e12` 得秒）；摘要表满（`performance_schema_digests_size` 默认 10000）后，新出现的 digest 会归并到一条兜底行，**这些语句就不再有耗时归属** —— 已写进 D8
- `[8.0.14+]` 的 `performance_schema.log_status` 能**一次原子读出** binlog 文件名/位点、`gtid_executed` 与各引擎 LSN，这是"手工记位点会错位"的正解；`SHOW MASTER STATUS` 自 `[8.2]` 起由 `SHOW BINARY LOG STATUS` 取代 —— 已写进 D34
- 半同步状态**不在** `SHOW REPLICA STATUS` 里，必须单列 `Rpl_semi_sync%`；该组状态名在 `[8.0.26]` 从 `Rpl_semi_sync_master_*` 改为 `Rpl_semi_sync_source_*`，老监控项失效方式是"查不到值"而不是报错 —— 已写进 D38
- `performance_schema.metadata_locks` 的容量由 `performance_schema_max_metadata_locks` 决定，**打满后新的 MDL 请求会被观测本身阻塞**，此时只能退回 `SHOW PROCESSLIST` 看 `State` —— 已写进 D3
- `information_schema.tables.DATA_FREE` 在 file-per-table 下**含预分配但未使用的区**，所以它从不等于"碎片"；判断要不要重建表要看 `DATA_FREE / (DATA_LENGTH+INDEX_LENGTH)` 的比例，而不是绝对值 —— 已写进 D20
- `INNODB_TABLES.TOTAL_ROW_VERSIONS` 会在表被重建（`COPY`/`INPLACE`）后归零，所以"清过一次"不等于"以后不会撞 64 次上限" —— 已写进 D40
- `Seconds_Behind_Source` 为 `NULL` 表示复制线程没在跑，**不是"零延迟"**；值为 0 也不代表数据一致（半同步降级、误删、跳过事务都能在延迟 0 的情况下造成缺失）—— 已写进 D35

---

**附录 A~G 期间核准的 12 处事实：**
- `back_log` 在 8.0 由 `max_connections` 自动推导（显示 151），且**不可动态修改** —— 已写进附录 A
- 严格模式下超长字符串报 **1406**（`Data too long`），不是 `1292`（那是截断警告）—— 已写进附录 A
- `optimizer_index_cost_adj` 是 **Oracle 参数**，MySQL 里写进 `my.cnf` 会启动失败；MySQL 的成本常量在 `mysql.server_cost` / `mysql.engine_cost` 两张表 —— 已写进附录 A
- 客户端 `2059`（`Authentication plugin ... cannot be loaded`）比 `3101` 更常见，是 8.0 升级后连不上的真实高频码 —— 已写进附录 B
- `ERROR 1205` **只回滚当前语句**，`ERROR 1213` **回滚整个事务**；重试粒度搞反会重复扣款 —— 已写进附录 B
- 客户端的 `1062` 与复制线程的 `Last_SQL_Errno=1062` 是两件事：前者是幂等信号，后者说明数据已经分叉 —— 已写进附录 B
- `gh-ost` **默认 dry run**，不加 `--execute` 什么也不做 —— 已写进附录 C
- `log_slave_updates` 自 `[8.0.26]` 改名 `log_replica_updates`（旧名仍兼容）；`--master-data` 自 `[8.0.26+]` 改名 `--source-data` —— 已写进附录 C/G
- **`super_read_only` 不能写进 `my.cnf`**：容器 entrypoint 的 `ALTER USER` 会报 `ERROR 1290` 并退出。正确做法是配完复制后 `SET PERSIST read_only=ON, super_read_only=ON`（落在 `mysqld-auto.cnf`，重启仍生效）—— 实测三次启动全失败，已写进附录 G
- `CHANGE REPLICATION SOURCE TO` 必须放在 compose 之外：容器 healthy 时主库可能还没有 GTID，复制要等主库起来再建 —— 已写进附录 G
- `stock_flow` 在实验环境里**故意无主键**，否则第 41 章案例四复现不出来；建表注释写明了生产必须补主键 —— 已写进 `labs/seed/01-schema.sql`
- 金额列统一叫 `pay_amount`（Ch49 / 附录 D13 / `labs` schema 三处一致），不是 `amount`；`amount` 用在 `account_flow` —— 已写进附录 G


## 五、"学完能成为资深 MySQL 工程师吗"——评估结论（待正式成文）

**结论：能到"高级 → 资深"的分水岭，但不能只靠读完就自称资深。**

这套大纲能扎实覆盖四块硬能力：

1. **机制层**：从一条 SQL 到落盘的全链路，能解释任何"反常现象"而不是背结论
2. **排障层**：慢查询、锁等待、死锁、复制延迟、恢复，有可复用的定位路径（Ch36-41、Ch52）
3. **设计层**：表设计、索引、分片、分布式事务、高可用，且每章都给了"代价"而不只是"方案"
4. **表达层**：能把机制讲给别人听、能过面试深挖

但有四个缺口是**任何文档都补不了**的：

| 缺口 | 说明 | 补齐方式 |
|---|---|---|
| 真实 on-call 的肌肉记忆 | 模式库 ≠ 凌晨三点面对一堆未知指标时的判断力 | 至少一次完整事故周期（发现→止血→根因→复盘） |
| 大规模数据的体感 | 10 亿行扩容、数据倾斜、跨机房切换的"手感" | 用 `labs/` 压测环境真跑一遍 |
| 源码级能力 | Ch44 只是导读，做不到改内核、打补丁、定位 bug | 编译调试版 + 跟一条调用链到 `btr_cur` / `lock_rec_lock` |
| 组织与取舍 | 变更管控、SLA 谈判、成本模型、说服业务方 | 参与真实架构评审 |

**建议**：把 `labs/` 实验环境和 Ch41 的真实事故复盘做实，这份手册就能从"读完很懂"变成"照着做就能上手"。这两块恰好是当前进度里最缺的部分。
