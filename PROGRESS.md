# 项目进度与断点

> **下次从这里接着做。** 本文件是唯一进度事实源，续写前先读它。
> 最后更新：2026-11-12 11:20

---

## 一、当前状态：24 / 52 章完成

| 指标 | 数值 |
|---|---|
| 已完成正文 | **24 章**（Ch1 ~ Ch24） |
| 累计正文 | **119,232 汉字**（约 11.9 万字） |
| 配图 | **63 张 SVG**（`docs/images/chXX-figN.svg`） |
| 绘图脚本 | **24 个**（`tools/diagrams/chXX.py`，均可重跑） |
| 完整性 | 24 章全部 7 段结构齐全，图引用零断链 |

**已完成卷**：
- ✅ 第一卷 存储引擎与运行时架构（Ch1-7）—— 7/7
- ✅ 第二卷 索引与优化器（Ch8-15）—— 8/8
- ✅ 第三卷 事务与并发控制（Ch16-21）全完
- 🔨 第四卷 复制、高可用与备份（Ch22-28）—— **3/7**
- ⬜ 附录 A~G —— 0/7

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

---

## 二、断点：下一批从 **Ch25** 开始

B6（Ch21~24）已完成并校验通过，**不要重写**。第三卷已收尾，第四卷（复制/高可用/备份）走到 3/7。

### 后续批次计划（4 章/批）

| 批次 | 章节 | 备注 |
|---|---|---|
| ✅ B6（已完成） | Ch21、22、23、24 | 长事务治理 + 复制原理/GTID/半同步 |
| **B7（下一批）** | **Ch25、26、27、28** | 并行复制、高可用切换、MGR、备份与 PITR —— 第四卷收尾 |
| B8 | Ch29、30、31、32 | 类型/字符集、主键 ID、表设计、分区 |
| B9 | Ch33、34、35、36 | 分库分表、分布式事务、数据生命周期、性能方法论 |
| B10 | Ch37、38、39、40 | 监控、慢查询、InnoDB 状态、参数调优 |
| B11 | Ch41、42、43、44 | 案例复盘、8.0/8.4、升级、源码导读 |
| B12 | Ch45、46、47、48 | 选型、在线 DDL、SQL 审核、安全 |
| B13 | Ch49、50、51、52 | 业务实战、容量、应急 SOP |
| B14 | 附录 A~G | 速查表、诊断 SQL 手册、面试 100 问优先 |

### 下一批（B7）四章要点

- **Ch25 并行复制与延迟治理 ★★★**（4500~5500 字，3 图）：延迟的本质（主库 M 并发 vs 从库单线程回放）；三种策略演进 `DATABASE` → `LOGICAL_CLOCK` → `WRITESET`，各自"凭什么判断两个事务可以并行"；`binlog_transaction_dependency_tracking` 与 `transaction_write_set_extraction` 的配合；`replica_preserve_commit_order` 为什么必须开、开了并行度怎么掉；**`Seconds_Behind_Master` 为什么不可靠**（它比的是 relay log 事件时间戳与系统时间，追平瞬间归零、DDL 期间失真、多线程下取最慢 worker），用 `pt-heartbeat` 或 GTID 差值替代；大事务/无主键表/DDL 的放大；工程解法（读写分离路由、关键读走主、缓存兜底、延迟阈值熔断）。**注意：Ch22 已给出延迟下限的"三次 fsync"结论，本章从"并发度"角度接，不要重复数落盘；Ch24 已讲半同步的 RTT，别重复。**
- **Ch26 高可用架构与故障切换 ★★★**（4500~5500 字，3 图）：RPO/RTO 与业务分级；方案全景对比（MHA / Orchestrator / MGR / 双主+Keepalived / ProxySQL·Router / 云 RDS）；传统切换的完整流程（选主→补数据→改指向→防脑裂）；**脑裂**的产生与防护（VIP 漂移、网关仲裁、`read_only` 兜底——`read_only` 挡不住 SUPER，必须 `super_read_only`，指回 Ch22）；一致性校验与补齐（`pt-table-checksum`、`pt-table-sync`、binlog 补偿）；切换 SOP 与常见失败点（DNS 缓存、长连接未断、应用未重连、连接池风暴）。
- **Ch27 MGR 与 InnoDB Cluster ★★**（2500~3500 字，2 图）：与异步/半同步的本质差异（Paxos 变体、多数派认证后才提交）；certification 与冲突检测、`group_replication_consistency` 五个级别（`EVENTUAL`/`BEFORE_ON_PRIMARY_FAILOVER`/`BEFORE`/`AFTER`/`BEFORE_AND_AFTER`）；单主 vs 多主、多主为何生产少见；流控与慢节点拖累；网络分区、成员驱逐 `group_replication_member_expel_timeout`；限制清单（必须主键、大事务上限 `group_replication_transaction_size_limit`、`SELECT ... FOR UPDATE` 的额外语义）；InnoDB Cluster/Router/Shell 的运维闭环。
- **Ch28 备份、恢复与 PITR 演练 ★★★**（4000~5000 字，3 图）：逻辑备份 vs 物理备份的取舍（`mysqldump`/`mysqlpump`/`mydumper` vs XtraBackup/Clone Plugin `[8.0.17+]`）；`--single-transaction` 的一致性快照原理与它对长事务的敏感（指回 Ch21）；XtraBackup 的 `--prepare` 两阶段（redo 前滚 + undo 回滚）为什么必需（指回 Ch7）；**PITR 的完整演练**（全备 + binlog 增量 → 恢复到误操作前一点 → 用 `mysqlbinlog --stop-position` / `--stop-datetime` 卡点 → 跳过误操作 GTID）；备份校验（恢复演练、`checksum`、表级校验）；误删数据的四种恢复路线与各自 RTO；备份的 3-2-1 与异地。

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
- [ ] **Ch41 案例复盘、Ch52 应急 SOP 需要真实事故素材**，目前大纲只有骨架
- [ ] **Ch47 慢查询治理闭环**需要补团队机制（Owner 制 / SLA / 周报）
- [ ] **全书交叉校验**：全部 52 章写完后做一次术语与结论一致性检查（尤其 Ch1/4/6/16 都涉及两阶段提交，Ch5/17 都涉及 purge 边界，Ch8/9 都涉及覆盖索引）
- [ ] **附录 D（40 条诊断 SQL）与附录 E（面试 100 问）优先做**，可直接当工具书用

### 工程层

- [ ] `labs/` 目录已建但**还是空的**：docker-compose（1 主 2 从 + 8.0/5.7）、千万行造数脚本、每章实验 SQL 都还没有
- [ ] 各章正文里引用了 `labs/ch01/seed.sql` 等路径，**需要补齐否则是断链**
- [ ] `README.md` 的进度区已同步更新到 16/52
- [ ] 尚未初始化 git 仓库，建议做一次初始提交便于回滚

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
