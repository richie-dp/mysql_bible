# 项目进度与断点

> **下次从这里接着做。** 本文件是唯一进度事实源，续写前先读它。
> 最后更新：2026-11-13 17:40

---

## 一、当前状态：52 / 52 章完成 —— **正文收官**

| 指标 | 数值 |
|---|---|
| 已完成正文 | **52 章**（Ch1 ~ Ch52，全书正文完） |
| 累计正文 | **247,544 汉字**（约 24.8 万字） |
| 配图 | **132 张 SVG**（`docs/images/chXX-figN.svg`） |
| 绘图脚本 | **52 个**（`tools/diagrams/chXX.py`，均可重跑） |
| 完整性 | 52 章全部 7 段结构齐全，图引用零断链 |

**已完成卷**：
- ✅ 第一卷 存储引擎与运行时架构（Ch1-7）—— 7/7
- ✅ 第二卷 索引与优化器（Ch8-15）—— 8/8
- ✅ 第三卷 事务与并发控制（Ch16-21）全完
- ✅ 第四卷 复制、高可用与备份（Ch22-28）全完
- ✅ 第五卷 数据建模与规模化（Ch29-35）全完
- ✅ 第六卷 性能诊断与调优（Ch36-41）—— 6/6 全完
- ✅ 第七卷 版本、内核与技术选型（Ch42-45）—— 4/4 全完
- ✅ 第八卷 工程规范与业务实战（Ch46-52）—— 7/7 全完
- ⬜ 附录 A~G —— 0/7（**下一批 B14**）

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
| 41 | `docs/ch41-case-studies.md` | 7250 | 3 |
| 42 | `docs/ch42-mysql8-features.md` | 3496 | 2 |
| 43 | `docs/ch43-upgrade-migration.md` | 3500 | 2 |
| 44 | `docs/ch44-source-guide.md` | 3497 | 2 |
| 45 | `docs/ch45-cloud-native-selection.md` | 3591 | 2 |
| 46 | `docs/ch46-online-ddl.md` | 5408 | 3 |
| 47 | `docs/ch47-sql-review.md` | 3611 | 2 |
| 48 | `docs/ch48-security-compliance.md` | 3598 | 2 |
| 49 | `docs/ch49-trade-inventory.md` | 6155 | 3 |
| 50 | `docs/ch50-content-counter-queue.md` | 3966 | 2 |
| 51 | `docs/ch51-capacity-benchmark.md` | 4124 | 2 |
| 52 | `docs/ch52-incident-sop.md` | 5498 | 3 |

---

## 二、断点：**正文 52 章已收官**，下一批做 **附录 A~G（B14）**

B13（Ch49~52）已完成并校验通过，**不要重写**。第八卷 7/7，全书正文完。

### 后续批次计划

| 批次 | 内容 | 备注 |
|---|---|---|
| ✅ B10~B13 | Ch37 ~ Ch52 | 正文全部完成，共 52 章 / 247,544 汉字 / 132 图 |
| **B14（下一批）** | **附录 A~G** | 按 D → E → A → B → G → C → F 的顺序写（D/E 可直接当工具用，优先） |
| B15 | `docs/00-能力地图与学习路径.md` + `labs/` 实验环境 | 见第四、五节 |

### 下一批（B14）附录要点

- **附录 D 诊断 SQL 手册 ★★★（最高优先级）**：40 条可直接复制的语句，按"我要解决什么问题"分组，不按语法分组。九组：找锁等待链（`data_lock_waits` + `data_locks` 自连接，`[5.7]` 用 `innodb_lock_waits`）、找长事务（`innodb_trx` 按 `trx_started` 排，含 `trx_rows_modified` 判回滚成本）、找慢 SQL（digest 增量双榜）、找未使用/冗余索引（`sys.schema_unused_indexes`、`sys.schema_redundant_indexes`）、找碎片表（`information_schema.tables` 的 `data_free`，**注意 `data_free` 含预分配空间，不能直接当碎片**）、找连接来源（`processlist` 按 Host/User 聚合）、查 binlog 位点与 GTID、查复制状态与延迟组成、查表空间与 undo 占用。**每条给：用途一句话 + SQL + 读法一句 + 坑一句**。40 条里至少有 8 条要写"这条会扫 p_s 全表，别在高负载时跑"。
- **附录 E 面试高频 100 问 ★★**：按卷分七组（引擎/索引/事务/复制/建模/诊断/工程），每题三段：**一句话结论**（能被直接背下来）+ **展开要点**（3 条，指向机制）+ **常见错误回答**（这是最有价值的一段，写"候选人常说的那句错话，以及它错在哪"）。100 题里必须包含系列里已有的"高频误读"：`Sending data` 不是发数据、checkpoint 年龄减 `Last checkpoint at`、`Handler_read_*` 是调用次数、`eq_range_index_dive_limit` 越过之后不是索引失效、`GRANT` 不需要 `FLUSH PRIVILEGES`、`INSTANT` 每表 64 次。**每题末尾标回指章节**。
- **附录 A 参数速查表 ★★**：六类（内存/IO/并发/复制/优化器/日志）× 五列（参数名、默认值、推荐区间、改动风险、生效方式）。**"生效方式"这一列是重点**——静态参数改完要重启，这是值班时最容易踩的坑。只收正文出现过的参数，保持与各章一致；`[8.0]` 与 `[5.7]` 默认值不同的要并列标。
- **附录 B 错误码速查 ★★**：`1062` `1205` `1213` `1032` `1040` `1114` `1878` `1467` `3024` `3101`，每条四段：触发条件 / 典型日志（含错误码原文） / 处置动作 / 容易误判成什么。
- **附录 G 实验环境 ★★**：`labs/docker-compose.yml` 起 1 主 2 从（8.0），另一份 5.7 用于版本对比；**必须真的能跑**——这一项会顺带补上正文里所有 `labs/` 断链。内容：compose 文件、`my.cnf` 片段、造数脚本（千万行订单 + 明细 + 库存，带倾斜）、每章实验脚本目录映射表。**写完要实跑 `docker compose config` 校验语法**。
- **附录 C 工具清单 ★**：每个工具一行：它解决什么问题 / 什么时候不该用它 / 一条最小可用命令。不写安装步骤。
- **附录 F 学习路径与参考 ★**：三阶段路径（入门→进阶→内核）+ 每阶段对应的本书章节 + 官方文档重点页索引。

---
## 三、续写时必须复用的工作流

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
- ⚠️ 本机**没有 libcairo**，`cairosvg` 装了也用不了；`qlmanage` 同样不可用。所以**不要尝试导出 PNG**，Markdown 直接引用 SVG 即可。视觉正确性靠 svgkit 的结构自检保证。

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

- [ ] **补写 `docs/00-能力地图与学习路径.md`**：用户问过"学完能否成为资深 MySQL 工程师"，尚未正式回答（评估见下节）
- [x] ~~**Ch41 案例复盘**需要真实事故素材~~：已按"六段式 + 三类误判"落地 10 个案例，每个案例末尾回指章节，Ch41 现在同时是全书索引页
- [ ] **Ch52 应急 SOP 需要真实事故素材**，目前大纲只有骨架；可直接复用 Ch41 的十个案例做"按症状索引"的分支
- [ ] **Ch47 SQL 审核治理闭环**的团队机制部分（Owner 制 / SLA / 周报 / 豁免流程）已写进 B12 要点，别写成工具介绍
- [ ] **全书交叉校验**：全部 52 章写完后做一次术语与结论一致性检查（尤其 Ch1/4/6/16 都涉及两阶段提交，Ch5/17 都涉及 purge 边界，Ch8/9 都涉及覆盖索引）
- [ ] **附录 D（40 条诊断 SQL）与附录 E（面试 100 问）优先做**，可直接当工具书用

### 工程层

- [ ] `labs/` 目录已建但**还是空的**：docker-compose（1 主 2 从 + 8.0/5.7）、千万行造数脚本、每章实验 SQL 都还没有。**这一项与附录 G 是同一件事，应合并到 B14 一起做**
- [ ] 各章正文里引用了 `labs/ch01/seed.sql` 等路径，**需要补齐否则是断链**（同上，随附录 G 解决）
- [x] `README.md` 进度区已同步到 52/52
- [ ] **全书交叉校验**：52 章已齐，现在可以做一次术语与结论一致性检查（重点：Ch1/4/6 都讲两阶段提交、Ch5/17 都讲 purge 边界、Ch8/9 都讲覆盖索引、Ch22/25 都讲落盘次数、Ch41/52 的十个案例必须逐字对齐）
- [ ] **`docs/00-能力地图与学习路径.md`** 仍未写（第五节的评估结论可以正式成文了）
- [ ] 尚未初始化 git 仓库，**52 章正文已齐，现在正是做首次提交的时机**

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

---

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
