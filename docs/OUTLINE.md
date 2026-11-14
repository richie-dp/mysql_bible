# 《MySQL 圣经》全书大纲

> **副标题**：写给中高级开发者的 MySQL 深度手册
> **版本基线**：MySQL 8.0.x（LTS 8.4 单独标注差异），涉及 5.7 的地方显式标 `[5.7]`
> **写作语言**：中文，术语保留英文原文（Buffer Pool / Next-Key Lock / MVCC）
> **最后更新**：2026-11-11

---

## 〇、这本书的定位

### 写给谁

| 画像 | 典型痛点 | 本书能给什么 |
|---|---|---|
| 3~5 年业务开发 | 会写 SQL、会加索引，但线上慢查询、死锁、锁等待只能靠"猜" | 把「现象 → 原理 → 定位手段 → 解法」的链路打通 |
| 高级开发 / Tech Lead | 要做表设计、分库分表、容灾方案，但缺少可对比的决策依据 | 每个方案给「适用边界 + 代价 + 失败案例」 |
| 面试冲刺者 | 背过八股，一问"为什么 RR 下还有幻读"就答不清 | 所有结论都推到机制层，能自证 |
| DBA / SRE 转型 | 会操作不会解释 | 提供逐段解读的日志、指标、状态输出 |

### 明确不写什么

- ❌ `SELECT` 语法、`JOIN` 是什么、安装部署、客户端工具使用
- ❌ 罗列参数默认值（放附录速查表，正文只讲"为什么是这个值"）
- ❌ 复制粘贴官方文档（官方文档已足够好，本书负责**串联**与**解释冲突**）
- ❌ "加索引就好了"这类结论式建议

### 三条阅读路径

- **路径 A｜面试/原理型**（约 40% 篇幅）：第 2、4、5、8、11、17、18、19、20 章 + 附录 F
- **路径 B｜架构/设计型**：第 3、6、22、26、29~35、42、45、52 章
- **路径 C｜救火/调优型**：第 10、11、19、20、24、25、36~41、47、52 章

### 深度分级

| 标记 | 含义 | 要求 |
|---|---|---|
| ★★★ | 必须吃透 | 能画出结构图、能推演过程、能回答"如果改成这样会怎样" |
| ★★ | 重点掌握 | 知道机制与适用场景，能查文档落地 |
| ★ | 扩展视野 | 了解结论与边界，用到再深入 |

---

## 一、全书结构总览

```text
第一卷  存储引擎与运行时架构   （Ch1-7）    —— 数据到底存在哪、怎么落盘
第二卷  索引与优化器           （Ch8-15）   —— 为什么这条 SQL 慢
第三卷  事务与并发控制         （Ch16-21）  —— 为什么锁住了、为什么数据"不一致"
第四卷  复制、高可用与备份     （Ch22-28）  —— 数据怎么不死、怎么找回
第五卷  数据建模与规模化       （Ch29-35）  —— 表怎么设计、怎么撑住 10 亿行
第六卷  性能诊断与调优         （Ch36-41）  —— 线上慢了怎么定位
第七卷  版本、内核与技术选型   （Ch42-45）  —— 该不该升级、该不该换
第八卷  工程规范与业务实战     （Ch46-52）  —— 落到团队与业务上
附录    A~G
```

**主线叙事**：一条 SQL 从进入 MySQL 到落盘（Ch1）→ 它如何被索引加速（Ch8）→ 并发时如何被事务与锁保护（Ch16）→ 单机撑不住时如何横向扩展（Ch22/Ch33）→ 出问题时如何定位与恢复（Ch36/Ch28）。

---

## 第一卷　存储引擎与运行时架构

### 第 1 章　一条 SQL 的完整生命周期　★★★

> 核心问题：`UPDATE t SET c=c+1 WHERE id=1` 这一句，MySQL 内部到底发生了什么？

- 1.1 三层架构再审视：连接层 / Server 层 / 存储引擎层，以及 `Handler` 接口的分界
- 1.2 连接与线程模型：one-thread-per-connection、线程池插件、连接数打满时的真实表现
- 1.3 解析 → 预处理 → 优化 → 执行：每一步的产物（Parse Tree / Logical Plan / Execution Plan）
- 1.4 一次查询的完整链路：权限校验 → 查询缓存（8.0 已移除）→ 分析器 → 优化器 → 执行器 → 引擎
- 1.5 一次更新的完整链路：Buffer Pool 命中 → undo 写入 → redo 写入 → binlog 写入 → 两阶段提交 → 脏页刷盘
- 1.6 **同一事务内 SELECT 与 UPDATE 的路径差异**（快照读 vs 当前读的物理分叉）
- 1.7 Server 层与引擎层的错误传递：为什么有些错误引擎报了、Server 层却换了错误码
- 🧪 实验：`general_log` + `performance_schema.events_statements_history` 抓一次完整链路
- ⚠️ 常见误区：「查询缓存能加速」——8.0 已删除；「执行器是引擎执行的」——分工常被混淆

### 第 2 章　InnoDB 内存体系　★★★

> 核心问题：为什么 buffer pool 调大后，QPS 反而掉了？

- 2.1 Buffer Pool 组织：chunk / instance / page hash / 三种链表（free、LRU、flush）
- 2.2 改良 LRU：young / old 分区、`innodb_old_blocks_time`、全表扫描为何不冲垮热数据
- 2.3 预读机制：线性预读 vs 随机预读、`innodb_read_ahead_threshold`，以及预读失效的代价
- 2.4 脏页与刷脏：`flush_list`、LRU 刷脏、`innodb_max_dirty_pages_pct`、`innodb_io_capacity` 的自适应算法
- 2.5 **刷脏速度跟不上时的连锁反应**：用户线程被阻塞做 Single Page Flush → RT 抖动
- 2.6 Change Buffer：什么操作会写 CB、为什么唯一索引不适用、`ibuf` 的 merge 时机
- 2.7 Log Buffer：写入时机（`innodb_flush_log_at_trx_commit` 三档的真实语义）
- 2.8 Adaptive Hash Index：命中条件、为何 8.0 之后争议变大
- 2.9 `innodb_buffer_pool_instances` 与热点竞争、buffer pool 在线 resize 的代价
- 🧪 实验：`information_schema.innodb_buffer_page` / `INNODB_BUFFER_POOL_STATS` 观察命中率与脏页比例
- ⚠️ 常见误区：命中率 99.9% 不等于没问题（可能是热数据太小）；`innodb_buffer_pool_dump_at_shutdown` 重启后冷启动

### 第 3 章　InnoDB 磁盘体系：表空间、页与行　★★★

> 核心问题：一行数据在磁盘上长什么样？为什么删了一半数据文件没变小？

- 3.1 表空间体系：系统表空间、独立表空间、通用表空间、undo 表空间、临时表空间
- 3.2 段 / 区 / 页 / 行的层级，extent 大小与 `innodb_page_size` 的影响
- 3.3 数据页内部结构逐字段解析：File Header / Page Header / Infimum & Supremum / User Records / Free List / Page Directory / File Trailer
- 3.4 行格式：COMPACT / REDUNDANT / DYNAMIC / COMPRESSED，隐藏列（`DB_TRX_ID`、`DB_ROLL_PTR`、`DB_ROW_ID`）
- 3.5 行溢出与 off-page 存储：20 字节指针、`innodb_page_size` 与 TEXT/BLOB 的真实开销
- 3.6 页分裂与页合并：随机主键的写放大、`MERGE_THRESHOLD`、碎片率与 `OPTIMIZE TABLE` 的真实效果
- 3.7 表空间回收：`innodb_file_per_table`、`TRUNCATE` vs `DELETE`、`ALTER TABLE ... ENGINE=InnoDB` 重建
- 🧪 实验：`innodb_page_info`（或 `innodb_ruby`）解析 ibd 文件，肉眼看到分裂后的空洞
- ⚠️ 常见误区：`DELETE` 能释放磁盘；`OPTIMIZE TABLE` 随时可做（大表锁 + IO 风暴）

### 第 4 章　Redo Log：WAL 与持久化　★★★

> 核心问题：既然每次都要写磁盘，为什么 redo log 能让 MySQL 快 100 倍？

- 4.1 WAL 的本质：顺序写替换随机写，代价转移给了"恢复"
- 4.2 redo log 物理结构：日志块（512B）、log file header、checkpoint、环形复用
- 4.3 LSN 体系：`log sequence number` / `log flushed up to` / `pages flushed up to` / `last checkpoint at` 四个值的含义与差值诊断
- 4.4 写入时机链路：Log Buffer → OS Page Cache（`write`）→ 磁盘（`fsync`）
- 4.5 `innodb_flush_log_at_trx_commit` = 0/1/2 分别丢多少数据（结合 OS 崩溃 vs 实例崩溃 vs 掉电）
- 4.6 **8.0.30+ 无锁化 redo log**：`innodb_redo_log_capacity`、redo 文件从固定 2 个变为 32 个的原因
- 4.7 Redo 也会写满：checkpoint 被迫推进 → 脏页强制刷盘 → 业务被拖垮的全过程
- 4.8 `innodb_log_writer_threads`、组提交与 redo 写入的并发模型
- 🧪 实验：用 `sysbench` 压测 + `SHOW ENGINE INNODB STATUS` 观察 checkpoint age 增长
- ⚠️ 常见误区：「`=2` 不会丢数据」——主机掉电一样丢；「redo 是逻辑日志」——它是物理逻辑日志（physiological）

### 第 5 章　Undo Log、版本链与 Purge　★★★

> 核心问题：MVCC 的"旧版本"到底存在哪里？长事务为什么能把数据库拖死？

- 5.1 undo 的两种类型：insert undo（提交即弃）vs update undo（进 history list）
- 5.2 undo 表空间、回滚段（rollback segment）、undo slot 的组织
- 5.3 版本链：`DB_ROLL_PTR` 如何串起一行历史，undo record 内部结构
- 5.4 Purge 机制：`purge thread`、`history list length`、为什么它决定 undo 能否回收
- 5.5 **长事务的三重伤害**：undo 膨胀、purge 阻塞、MDL 阻塞 DDL、主从延迟放大
- 5.6 ReadView 需要的最小活跃事务 id（`up_limit_id`）与 purge 的边界关系
- 5.7 undo 表空间膨胀后的处理：`innodb_undo_tablespaces`、`TRUNCATE` undo 的正确姿势
- 🧪 实验：开长事务 + 持续 update，观察 `history list length` 与 undo 表空间大小
- ⚠️ 常见误区：`ROLLBACK` 之后空间立刻回收；`read-only` 事务不产生 undo（会，且照样阻塞 purge）

### 第 6 章　Binlog 与两阶段提交　★★★

> 核心问题：为什么必须有 redo log 还要有 binlog？两者不一致会发生什么？

- 6.1 binlog 的定位：Server 层归档日志，与引擎无关（这是它存在的根本原因）
- 6.2 三种格式：STATEMENT / ROW / MIXED，各自的不一致风险（`NOW()`、`UUID()`、limit 无 order by）
- 6.3 binlog 事件结构：Event Header、`TABLE_MAP`、`WRITE_ROWS` / `UPDATE_ROWS` / `DELETE_ROWS`、`XID`
- 6.4 **内部 XA / 两阶段提交**：prepare → 写 binlog → commit，以及崩溃在中间各点的恢复行为
- 6.5 组提交（Group Commit）：flush / sync / commit 三阶段，`binlog_group_commit_sync_delay` 的收益与代价
- 6.6 `sync_binlog` 取值语义、binlog cache 与 `binlog_cache_size` 溢出到临时文件
- 6.7 `binlog_row_image` = FULL / MINIMAL / NOBLOB 对复制、闪回、CDC 的影响
- 6.8 binlog 的消费方：Canal / Maxwell / Debezium，以及为什么它们必须等事务提交
- 🧪 实验：`mysqlbinlog -vv` 解析一次 UPDATE，逐字段对照
- ⚠️ 常见误区：「binlog 是 InnoDB 的」；「两阶段提交能保证主从强一致」（只能保证主库内部一致）

### 第 7 章　崩溃恢复与 Doublewrite　★★

> 核心问题：断电重启后，MySQL 凭什么敢说数据没丢、也没多？

- 7.1 为什么需要 doublewrite：16KB 页只写了 4KB 的 partial write 问题
- 7.2 doublewrite buffer 的落盘流程与 `innodb_doublewrite` 的关闭风险（8.0.20+ 独立 dblwr 文件）
- 7.3 恢复三阶段：分析（找 checkpoint）→ 重做（redo 前滚）→ 回滚（undo 未提交事务）
- 7.4 恢复时间估算：为什么大事务会让重启从 30 秒变成 30 分钟
- 7.5 `innodb_force_recovery` 六级含义与使用边界
- 🧪 实验：`kill -9` 实例，观察 `mysqld` 启动日志中的恢复输出

---

## 第二卷　索引与优化器

### 第 8 章　B+ 树与索引组织表　★★★

> 核心问题：为什么 InnoDB 选 B+ 树？三层树到底能装多少行？

- 8.1 数据结构横向对比：B 树、B+ 树、LSM、哈希、跳表、倒排，各自解决的瓶颈
- 8.2 B+ 树的两条硬性设计：非叶子只存键、叶子双向链表
- 8.3 扇出计算：主键 BIGINT + 页 16KB → 三层树 ≈ 2000 万行的推导过程
- 8.4 聚簇索引与索引组织表（IOT）：数据即索引，二级索引为何必须回表
- 8.5 二级索引的叶子存什么（主键值），以及**主键过长导致所有二级索引变大**的连锁代价
- 8.6 索引的物理顺序与逻辑顺序、`ORDER BY` 能省掉排序的条件
- 8.7 主键选择：自增 / UUID / 雪花 / 业务主键的性能与运维对比（含页分裂实测思路）
- 🧪 实验：`information_schema.innodb_index_stats` 查看索引页数，验证扇出估算
- ⚠️ 常见误区：「索引越多查询越快」；「联合索引和多个单列索引等价」

### 第 9 章　索引设计与失效全景　★★★

> 核心问题：明明建了索引，为什么执行计划还是全表扫？

- 9.1 联合索引与最左前缀：**真正的规则是"能否用上索引的有序性"**，不是字面匹配
- 9.2 索引下推（ICP）：`Using index condition` 的含义、下推与回表的边界
- 9.3 覆盖索引：`Using index` 的判定、为什么 `SELECT *` 会毁掉覆盖
- 9.4 索引失效 20 例逐条推演：隐式类型转换、函数包裹、`OR` 混合、范围列之后的列、`LIKE '%x'`、排序方向不一致、字符集/collation 不一致、`!=`、`IS NULL`、参数化与非参数化差异
- 9.5 前缀索引：选择性计算、无法覆盖索引、`ORDER BY` 失效
- 9.6 函数索引（8.0.13+）、降序索引（8.0 真实生效）、不可见索引（灰度验证）
- 9.7 索引合并（Index Merge）：`Using intersect/union` 何时出现、为何常常是坏信号
- 9.8 冗余索引与未使用索引的识别：`sys.schema_redundant_indexes` / `schema_unused_indexes`
- 9.9 索引设计方法论：按查询模式反推、三星索引、写入放大与索引数量的平衡
- 🧪 实验：同一条 SQL 加/去函数、改字段类型，对比 `EXPLAIN` 的 `key` 与 `rows`
- ⚠️ 常见误区：「`LIKE 'abc%'` 一定走索引」（取决于选择性与排序需求）；「索引列参与计算仍能走索引」

### 第 10 章　统计信息与成本模型　★★

> 核心问题：为什么昨天还走索引，今天突然全表扫了？

- 10.1 两种统计：表级（行数）与索引级（基数 cardinality、页数）
- 10.2 采样机制：`innodb_stats_persistent`、`innodb_stats_persistent_sample_pages`、采样偏差
- 10.3 统计信息何时更新：`ANALYZE TABLE`、10% 变更触发、重启后、`innodb_stats_on_metadata`
- 10.4 优化器成本模型：`server_cost` / `engine_cost` 两张表、IO 成本与 CPU 成本的默认值
- 10.5 选错索引的四大根因：统计不准、回表成本估算偏差、`ORDER BY` 的排序成本、`LIMIT` 的诱惑
- 10.6 `optimizer_trace` 逐段解读：从 `potential_range_indexes` 到 `best_access_path` 的完整决策链
- 10.7 干预手段的优先级：改写 SQL > 建更合适的索引 > `FORCE INDEX` > 关闭优化器特性
- 🧪 实验：造 100 万行数据，人为制造统计偏差，复现"选错索引"并修复
- ⚠️ 常见误区：「`ANALYZE TABLE` 能解决所有选错索引」（很多是成本模型问题，不是统计问题）

### 第 11 章　执行计划精读　★★★

> 核心问题：`EXPLAIN` 出来的每一列，到底在说什么？

- 11.1 `id` / `select_type` 的真实语义（含 `DEPENDENT SUBQUERY`、`MATERIALIZED`、`UNCACHEABLE`）
- 11.2 `type` 全等级：`system > const > eq_ref > ref > range > index > ALL`，以及 `ref_or_null`、`index_merge`、`unique_subquery`、`index_subquery`、`fulltext`
- 11.3 `possible_keys` vs `key` vs `key_len`：`key_len` 反推用了几列索引（含字符集/可空的影响）
- 11.4 `rows` 与 `filtered` 的乘积为什么经常离谱，`rows_examined` 与 `rows_sent` 的真实差距
- 11.5 `Extra` 关键值逐个拆：`Using filesort`、`Using temporary`、`Using join buffer`、`Backward index scan`、`Using index for group-by`、`Using index for skip scan`
- 11.6 `EXPLAIN FORMAT=JSON` 与 `FORMAT=TREE` 的增量信息（成本、物化、子查询展开）
- 11.7 `EXPLAIN ANALYZE`（8.0.18+）：真实耗时 vs 估算，如何读出"估算 1 行实际 10 万行"
- 11.8 一份"坏的执行计划"体检清单（12 项 checklist）
- 🧪 实验：同一 SQL 的 5 种写法 × 3 种索引，产出一张执行计划对照表
- ⚠️ 常见误区：`type=index` 以为走了索引（是全索引扫描）；`Using filesort` 一定慢（小结果集内存排序很快）

### 第 12 章　连接算法与 Join 优化　★★★

> 核心问题：`LEFT JOIN` 和 `IN` 到底谁快？大表 JOIN 为什么会被 DBA 禁掉？

- 12.1 驱动表与被驱动表的判定规则（含 8.0 优化器对 `LEFT JOIN` 的重写）
- 12.2 NLJ（Simple Nested Loop）与 INLJ（Index Nested Loop）：被驱动表必须有索引
- 12.3 Block Nested Loop（BNL）与 Join Buffer：`Using join buffer (Block Nested Loop)` 的灾难现场
- 12.4 Batched Key Access（BKA）：MRR 的配合、什么时候真的更快、为什么默认关闭
- 12.5 Hash Join（8.0.18+）：等值连接的默认路径、`Using join buffer (hash join)`、内存溢出到磁盘的降级
- 12.6 外连接的语义约束与"谓词下推"的差异（`ON` vs `WHERE` 必须区分清楚）
- 12.7 多表 JOIN 的顺序爆炸与 `optimizer_search_depth`、`optimizer_prune_level`
- 12.8 大表 JOIN 的替代方案：应用层拼接、宽表、异构索引表
- 🧪 实验：同一 JOIN 在三张不同规模表上，对比 NLJ / BNL / Hash Join 的耗时
- ⚠️ 常见误区：「LEFT JOIN 会保留左表全部行」——被 `WHERE` 条件否掉；「小表驱动大表」——真正看的是行数×成本

### 第 13 章　子查询、派生表与 CTE　★★

> 核心问题：`IN (SELECT ...)` 为什么有时比 JOIN 慢 100 倍？

- 13.1 子查询分类：标量 / 行 / 表 / 关联（correlated），执行位置不同结果不同
- 13.2 半连接（Semi-Join）五种策略：`FirstMatch`、`LooseScan`、`Materialization`、`DuplicateWeedout`、`Table Pullout`
- 13.3 `IN` vs `EXISTS` 的真实差异（优化器会重写，不要凭口诀优化）
- 13.4 派生表（derived table）的 merge 与 materialize、8.0 派生表条件下推
- 13.5 CTE（8.0）：`WITH` 的物化行为、递归 CTE 的树形查询实战与深度限制
- 13.6 窗口函数（8.0）：`ROW_NUMBER` / `RANK` / `LAG` 替代自连接，执行代价在哪
- 13.7 "关联子查询被优化成 DEPENDENT SUBQUERY"的识别与改写
- 🧪 实验：`EXPLAIN FORMAT=TREE` 观察半连接策略选择过程

### 第 14 章　排序、临时表与聚合　★★

> 核心问题：`ORDER BY` 为什么突然变慢？磁盘临时表从哪来的？

- 14.1 filesort 两种算法：全字段排序 vs rowid 排序，`max_length_for_sort_data` 的取舍
- 14.2 `sort_buffer_size` 与"用内存还是用磁盘"的判定，`number_of_tmp_files`
- 14.3 内部临时表两种形态：内存临时表（MEMORY/temptable 引擎）与磁盘临时表，溢出时机
- 14.4 8.0 的 TempTable 引擎替换 MEMORY，对 `VARCHAR` 与 BLOB 的改善
- 14.5 `GROUP BY` 的三种实现：索引有序、临时表 + 排序、`Using index for group-by`
- 14.6 `DISTINCT` / `UNION` 的隐式排序与去重代价
- 14.7 大结果集排序的工程解法：游标分页、覆盖索引消除排序、预计算
- 🧪 实验：调小 `sort_buffer_size` 复现磁盘排序，读 `Sort_merge_passes`
- ⚠️ 常见误区：`ORDER BY` 加了索引就一定不排序（要看是否覆盖 + 顺序方向 + 是否用了范围）

### 第 15 章　查询改写实战　★★★

> 核心问题：不能加索引、不能改表结构时，怎么把 SQL 从 3 秒优化到 30 毫秒？

- 15.1 深分页三解法：延迟关联、游标（seek method）、覆盖索引 + 子查询，各自的适用边界
- 15.2 `COUNT(*)` / `COUNT(1)` / `COUNT(col)` 的执行差异，以及"亿级表精确计数"的替代方案
- 15.3 `LIMIT` 与 `ORDER BY` 组合下的优化陷阱
- 15.4 批量更新/删除的分批策略：`WHERE id > ? LIMIT 500` 的循环与主键跳跃
- 15.5 `INSERT ... ON DUPLICATE KEY UPDATE` / `REPLACE INTO` 的隐式行为与自增跳号、触发器副作用
- 15.6 大事务拆分与 `INSERT ... SELECT` 的锁范围
- 15.7 `UNION` vs `UNION ALL`、`OR` 改 `UNION ALL`、`NOT IN` 改 `LEFT JOIN ... IS NULL` 的正确姿势
- 15.8 20 个真实慢 SQL 改写案例（每条给：原写法 / 问题 / 改法 / 前后耗时）
- 🧪 实验：在 1000 万行表上逐条验证 20 个案例

---

## 第三卷　事务与并发控制

### 第 16 章　事务 ACID 的工程实现　★★★

> 核心问题：ACID 四个字母，分别由哪个组件买单？

- 16.1 A（原子性）→ undo log 回滚；C（一致性）→ 约束 + 应用逻辑 + 前两者共同保证
- 16.2 I（隔离性）→ 锁 + MVCC，两套机制如何共存
- 16.3 D（持久性）→ redo log + `innodb_flush_log_at_trx_commit` + doublewrite 的组合拳
- 16.4 事务的生命周期：`BEGIN` 是延迟分配 trx_id 的（这点决定了很多现象）
- 16.5 隐式提交与隐式回滚：DDL、`LOCK TABLES`、`TRUNCATE` 的破坏力
- 16.6 保存点（SAVEPOINT）与嵌套事务的模拟
- 16.7 分布式事务中的本地事务边界（为第 34 章铺垫）
- ⚠️ 常见误区：「事务隔离性靠锁」——快照读根本不加锁；「BEGIN 就开启事务」——一致性读视图到第一条语句才建

### 第 17 章　隔离级别与 MVCC 可见性　★★★

> 核心问题：RR 到底解不解决幻读？为什么同一事务里两次查询结果不同？

- 17.1 四种隔离级别与三类异常的严格定义（含"丢失更新"这个标准外的第五种）
- 17.2 SQL 标准 vs InnoDB 实现的三处关键差异（RR 用 next-key 而非仅 MVCC、RR 也禁止部分幻读、RC 下 binlog 必须 ROW）
- 17.3 ReadView 四个字段：`m_ids`、`min_trx_id`、`max_trx_id`、`creator_trx_id`
- 17.4 **可见性判断算法七步推演**（配一张对照表，把 6 种 trx_id 情形全部走一遍）
- 17.5 快照读 vs 当前读：`SELECT` / `SELECT ... FOR UPDATE` / `UPDATE` / `DELETE` / `INSERT` 分别用哪个
- 17.6 RC 与 RR 的 ReadView 创建时机差异（每条语句 vs 每个事务）及由此产生的现象
- 17.7 **RR 下幻读依然存在的两种场景**：先快照读再当前读、先当前读再快照读（经典面试题的标准答案）
- 17.8 一致性读的边界：为什么从库读到的是"旧的一致视图"
- 🧪 实验：两个会话，16 组操作序列，把每种隔离级别的可见性结果制成表格
- ⚠️ 常见误区：「MVCC 解决幻读」——是 next-key lock 解决的当前读幻读；「RC 没有 gap lock」——外键与唯一性检查仍会加

### 第 18 章　锁体系全景　★★★

> 核心问题：MySQL 一共有多少种锁？它们分别锁什么？

- 18.1 锁的分类树：按粒度（全局/表/页/行）、按模式（S/X）、按算法（Record/Gap/Next-Key）、按用途（意向/插入意向/自增/AI/MDL/谓词）
- 18.2 意向锁（IS/IX）：为什么需要它、它与表锁的兼容矩阵
- 18.3 记录锁 / 间隙锁 / 临键锁：加锁对象是"索引记录"而非"行"，这点是一切困惑的根源
- 18.4 插入意向锁（Insert Intention）：它只是 gap lock 的一种，为什么 INSERT 之间不互斥
- 18.5 自增锁与 `innodb_autoinc_lock_mode` 三档（0/1/2）的并发与连续性权衡
- 18.6 元数据锁（MDL）：`SELECT` 也会加 MDL 读锁，长事务 + DDL = 全表阻塞（经典事故）
- 18.7 全局锁与备份锁：`FLUSH TABLES WITH READ LOCK`、`LOCK INSTANCE FOR BACKUP`
- 18.8 谓词锁与空间索引锁、页锁的历史包袱
- 18.9 锁的内存对象：`lock_sys`、`lock struct` 与 `bitmap`，一条锁信息占多少内存
- 🧪 实验：`performance_schema.data_locks` + `data_lock_waits` 把每种锁"看到"

### 第 19 章　加锁规则推演　★★★

> 核心问题：这条 `UPDATE` 到底锁了哪些行？为什么隔壁那行也被锁了？

- 19.1 两条基本原则 + 两条优化规则（唯一索引等值命中退化为记录锁；等值不存在退化为间隙锁）
- 19.2 唯一索引 / 非唯一索引 / 无索引 三种情况下的加锁差异（**无索引 = 锁全表**的机制解释）
- 19.3 等值查询：命中 / 未命中 / 边界值 三种 case 的逐个推演
- 19.4 范围查询：`>=` / `>` / `<=` / `<` / `BETWEEN` 对 next-key 边界的影响
- 19.5 `LIMIT` 对加锁范围的影响（为什么 `LIMIT 1` 能少锁很多）
- 19.6 `ORDER BY` + 索引顺序导致的加锁范围扩大
- 19.7 插入操作在不同索引上的加锁、唯一键冲突时的 S 锁与死锁
- 19.8 加锁分析五步法（确定索引 → 确定扫描范围 → 确定边界 → 判断退化 → 验证）
- 🧪 实验：12 个经典 SQL × 三种索引结构，用 `data_locks` 输出锁清单并制表
- ⚠️ 常见误区：「只锁 WHERE 命中的行」；「没有索引就不加锁」

### 第 20 章　死锁与锁等待排查　★★★

> 核心问题：线上突然大量超时，怎么在 5 分钟内定位到根因？

- 20.1 死锁四个必要条件在 InnoDB 中的具体映射
- 20.2 死锁检测：wait-for graph、`innodb_deadlock_detect`、检测开销与关闭后的超时兜底
- 20.3 **死锁日志逐行解读**：`LATEST DETECTED DEADLOCK` 的 TRANSACTION / HOLDS / WAITS FOR 该怎么读
- 20.4 六种高频死锁模式：交叉更新、间隙锁互斥、唯一键冲突 + 加锁顺序、`INSERT ... SELECT`、DDL 与事务、批量更新顺序不一致
- 20.5 锁等待（非死锁）：`innodb_lock_wait_timeout`、`sys.innodb_lock_waits` 一条 SQL 找出阻塞链
- 20.6 锁等待的雪崩效应：一个慢事务如何拖垮整个连接池
- 20.7 治理手段：缩小事务、固定加锁顺序、降低隔离级别到 RC 的影响、拆分热点行
- 20.8 `innodb_print_all_deadlocks` 与死锁日志采集、告警策略
- 🧪 实验：手工构造 6 种死锁，逐个抓日志并对号入座

### 第 21 章　长事务与大事务治理　★★

- 21.1 定义与阈值：执行时长、undo 持有量、影响面三个维度
- 21.2 发现手段：`information_schema.innodb_trx`、`sys.innodb_trx`、`performance_schema`、审计插件
- 21.3 长事务的 5 类危害量化（undo、purge、MDL、复制延迟、备份失败）
- 21.4 大事务拆分模式：按主键区间、按时间窗口、异步化、状态机推进
- 21.5 不得已的处置：`KILL` 的风险、`ROLLBACK` 的耗时、如何安全终止
- 21.6 事务模板规范：把事务写在最内层、禁止 RPC/HTTP 调用、控制单次行数

---

## 第四卷　复制、高可用与备份

### 第 22 章　复制原理与事件流　★★★

> 核心问题：一条数据从主库到从库，中间经过了几次落盘？

- 22.1 三个线程 + 两个日志：dump / IO / SQL 线程，binlog → relay log
- 22.2 位点（`binlog_file` + `pos`）与 GTID 两套坐标体系的差异
- 22.3 relay log 结构与 `relay_log_recovery`、`relay_log_purge`
- 22.4 复制的四种模式：异步、半同步、全同步（MGR）、延迟复制
- 22.5 复制过滤规则（`binlog_do_db` / `replicate_wild_do_table`）的坑与替代方案
- 22.6 复制中的会话状态保持：`sql_mode`、字符集、`time_zone`、`auto_increment` 的一致性
- 22.7 从库只读：`super_read_only` 的必要性、`read_only` 为何挡不住 root
- 🧪 实验：搭建一主两从，用 `mysqlbinlog` 观察 relay log 与 binlog 的对应关系

### 第 23 章　GTID 与复制运维　★★

- 23.1 GTID 结构：`server_uuid:transaction_id`，一对一映射到事务
- 23.2 `gtid_executed` / `gtid_purged` / `gtid_owned` 三个变量的区别
- 23.3 GTID 下的搭建、切换、跳过事务（`SET GTID_NEXT` 的正确用法）
- 23.4 errant transaction（多余事务）的识别与修复
- 23.5 GTID 与 `CREATE TABLE ... SELECT`、临时表、`XA` 的限制
- 23.6 复制监控指标体系与"复制中断"的 10 类原因速查

### 第 24 章　半同步与无损复制　★★

- 24.1 半同步的 ACK 时机：`AFTER_COMMIT` vs `AFTER_SYNC`，差一个 ack 就是数据丢失
- 24.2 `rpl_semi_sync_master_timeout` 降级为异步的静默风险与监控
- 24.3 5.7 的 `loss-less semi-sync` 与 8.0 插件化后的行为变化（`wait_for_slave_count`、`wait_point`）
- 24.4 半同步 + 组提交 + 多线程 ACK 的性能损耗量化
- 24.5 何时必须用半同步、何时该改用 MGR

### 第 25 章　并行复制与延迟治理　★★★

> 核心问题：从库延迟 3 小时，日志里全是 `Waiting for dependent transaction to commit`，怎么办？

- 25.1 延迟的本质：单线程回放 vs 主库多线程写入
- 25.2 三种并行策略演进：按库（`DATABASE`）→ 按组提交（`LOGICAL_CLOCK`）→ 按写集（`WRITESET`）
- 25.3 `binlog_transaction_dependency_tracking` 与 `transaction_write_set_extraction` 的配合
- 25.4 `slave_preserve_commit_order` 为什么必须开、开了之后并行度下降
- 25.5 `Seconds_Behind_Master` 为什么不可靠，用 `pt-heartbeat` 或 GTID 差值替代
- 25.6 大事务 / 无主键表 / DDL 造成的延迟放大
- 25.7 延迟的工程解法：读写分离路由、关键读走主、缓存兜底、延迟阈值熔断
- 🧪 实验：主库压测 + 从库 `performance_schema.replication_applier_status_by_worker` 观察并行度

### 第 26 章　高可用架构与故障切换　★★★

> 核心问题：主库挂了，30 秒内切过去，并且一行数据都不能丢，怎么做到？

- 26.1 RPO / RTO 的定义与业务分级（同城双活 vs 两地三中心）
- 26.2 方案全景对比：MHA、Orchestrator、MGR、双主 + Keepalived、ProxySQL / MySQL Router、云 RDS 高可用
- 26.3 传统主从切换的完整流程（选主、补数据、改指向、防脑裂）
- 26.4 **脑裂的产生与防护**：VIP 漂移、网关仲裁、`read_only` 兜底
- 26.5 数据一致性校验与补齐：`pt-table-checksum`、`pt-table-sync`、基于 binlog 的补偿
- 26.6 中间件层：ProxySQL 的健康检查、读写分离规则、连接池与故障时的连接风暴
- 26.7 切换演练 SOP 与常见失败点（DNS 缓存、长连接、应用未重连）
- ⚠️ 常见误区：「有半同步就不会丢数据」；「VIP 切过去业务就好了」（旧连接还在打旧库）

### 第 27 章　MGR 与 InnoDB Cluster　★★

- 27.1 与异步复制/半同步的本质差异：Paxos 变体、多数派提交
- 27.2 认证过程（certification）与冲突检测、`group_replication_consistency` 五个级别
- 27.3 单主模式 vs 多主模式，多主为什么在生产上少见
- 27.4 流控（flow control）与慢节点拖累全组
- 27.5 网络分区下的表现、成员驱逐与 `group_replication_member_expel_timeout`
- 27.6 限制清单：表必须有主键、大事务限制、`SELECT ... FOR UPDATE` 的额外语义
- 27.7 InnoDB Cluster / Router / Shell 的运维闭环

### 第 28 章　备份、恢复与 PITR 演练　★★★

> 核心问题：误删了一张表，怎么在 15 分钟内恢复到删前 1 秒？

- 28.1 备份分类：物理 vs 逻辑、全量 vs 增量、冷/温/热
- 28.2 XtraBackup 原理：拷贝 ibd + 复制 redo、`--prepare` 的两个阶段（前滚 + 回滚）
- 28.3 Clone Plugin（8.0.17+）：本地/远程克隆、与 XtraBackup 的对比
- 28.4 逻辑备份的边界：`mysqldump --single-transaction` 的一致性快照与 `--master-data`
- 28.5 **PITR 完整流程**：全备 + binlog 重放到指定时间点/GTID
- 28.6 单表恢复的四种思路（表空间导入、逻辑过滤、克隆到实例、闪回工具）
- 28.7 延迟从库作为"后悔药"的设计
- 28.8 备份有效性验证：定期恢复演练、校验行数、checksum
- 28.9 备份对线上性能的影响控制：限速、从库备份、`ionice`
- 🧪 实验：完整走一遍"全备 → 删库 → PITR 到误操作前 1 秒"

---

## 第五卷　数据建模与规模化

### 第 29 章　数据类型与字符集　★★★

> 核心问题：为什么 `VARCHAR(255)` 和 `VARCHAR(20)` 性能不一样？`utf8mb4` 让索引变长了多少？

- 29.1 整数类型：显示宽度（8.0.19 已废弃）、`UNSIGNED` 的坑、`INT(11)` 的真实含义
- 29.2 浮点与定点：`FLOAT/DOUBLE` 的精度陷阱、`DECIMAL` 的存储与性能、金额字段的唯一正确选择
- 29.3 字符类型：`CHAR` vs `VARCHAR` 的定长/变长、行内长度前缀（1~2 字节）、`VARCHAR(255)` 跨界的语义
- 29.4 TEXT / BLOB：off-page 阈值、不能有默认值、不能全列索引、临时表与排序的代价
- 29.5 时间类型：`DATETIME` vs `TIMESTAMP`（时区、2038、存储字节）、`DATETIME(6)` 的微秒
- 29.6 `ENUM` / `SET` 的隐性成本（改枚举要 DDL、排序按序号、与字符串比较的开销）
- 29.7 JSON（5.7+）：存储格式、虚拟列 + 索引、`JSON_TABLE`、什么时候不该用 JSON
- 29.8 字符集与 collation：`utf8mb3` / `utf8mb4` / `utf8mb4_0900_ai_ci`、`ci` 与 `cs` 对唯一索引的影响、JOIN 时 collation 不一致导致索引失效
- 29.9 隐含的字符集继承：`character_set_server` / 表 / 列 / 连接四级优先级
- 🧪 实验：同一数据用三种字符集建表，对比索引大小与 JOIN 性能
- ⚠️ 常见误区：「`utf8` 就是 utf8mb4」；「`TIMESTAMP` 更省空间」（要考虑时区转换开销）

### 第 30 章　主键、唯一 ID 与自增　★★★

- 30.1 自增的机制：`AUTO-INC` 锁、批量插入的分配策略、跳号与不连续的原因
- 30.2 自增用尽：`INT UNSIGNED` 的 42 亿上限、溢出后的行为、`ALTER` 扩展的代价
- 30.3 无主键表的代价：隐藏 `DB_ROW_ID`、复制与 MGR 的限制、`DELETE` 无法定位
- 30.4 业务主键 vs 代理主键的取舍（唯一性、长度、变更频率）
- 30.5 分布式 ID 方案对比：号段模式（Leaf/segment）、雪花算法（时钟回拨）、UUIDv7、Redis INCR
- 30.6 分库分表下的全局唯一：`auto_increment_increment` 步长法、基因法（避免跨分片）
- 30.7 主键顺序与写入热点：自增尾部热点 vs 雪花中间热点

### 第 31 章　表设计：范式、反范式与结构演进　★★★

> 核心问题：为什么互联网公司普遍用冗余字段换 JOIN？

- 31.1 三范式在 OLTP 中的适用边界，哪些范式约束应该放到应用层
- 31.2 反范式三种手段：冗余字段、派生表/汇总表、宽表
- 31.3 大宽表的代价：行长度、页密度、`SELECT *` 的 IO 放大、DDL 代价
- 31.4 垂直拆分：冷热字段分离、大字段独立表
- 31.5 水平拆分的前置条件（见第 33 章）
- 31.6 设计评审 checklist：主键、索引、字段类型、可空性、默认值、命名、注释、审计字段、软删除、版本号
- 31.7 状态字段设计：状态机表 vs 位图 vs 多时间戳列
- 31.8 软删除的隐藏成本：唯一索引冲突、索引选择性下降、查询必须带条件
- 🧪 实验：一张 60 列的宽表 vs 拆成三张窄表，对比 QPS 与 buffer pool 占用

### 第 32 章　分区表　★★

- 32.1 分区类型：RANGE / LIST / HASH / KEY，以及分区列必须参与主键的限制
- 32.2 分区裁剪（partition pruning）的发生条件与失效场景
- 32.3 分区表的真实收益：快速删历史数据（`DROP PARTITION`）、局部索引维护
- 32.4 分区表的真实代价：无全局索引、跨分区查询、`ALTER` 元数据锁、分区数上限
- 32.5 与分库分表的边界：什么时候分区够用、什么时候必须上中间件
- 32.6 在线重分区：`EXCHANGE PARTITION` 的用法

### 第 33 章　分库分表　★★★

> 核心问题：单表 10 亿行，是继续优化还是拆？拆了之后 JOIN、分页、事务怎么办？

- 33.1 拆与不拆的判断：容量、QPS、写入热点、运维边界四维评估（含"先优化再拆分"的量化门槛）
- 33.2 垂直拆分：按业务域、按读写、按冷热
- 33.3 水平拆分：分片键选择（用户 ID / 商户 ID / 时间）、均匀性、业务穿透
- 33.4 路由层选型：ShardingSphere-JDBC / Proxy、MyCat、应用层自路由、云原生分布式数据库
- 33.5 跨分片难题逐个破解：JOIN（广播表/绑定表/异构索引）、分页（二次查询法）、排序、聚合、`COUNT`
- 33.6 全局唯一 ID、全局二级索引、分布式事务（引向第 34 章）
- 33.7 扩容方案：双倍扩容、双写迁移、影子表 + 数据校验、灰度切流
- 33.8 数据倾斜与热点分片治理
- 33.9 分片后的运维变化：DDL 广播、备份粒度、监控维度、故障影响面
- ⚠️ 常见误区：「一开始就分 1024 张表」（DDL/连接数灾难）；「用时间做分片键」导致写热点

### 第 34 章　分布式事务与最终一致性　★★

- 34.1 为什么 XA 在互联网场景被弃用（同步阻塞、协调者单点、性能）
- 34.2 2PC / 3PC / XA 的 MySQL 实现与 `innodb_support_xa`
- 34.3 TCC：Try-Confirm-Cancel 的设计要点、空回滚、悬挂、幂等
- 34.4 Saga 与补偿事务、状态机编排
- 34.5 本地消息表 + 定时补偿（最常用的落地方式）
- 34.6 事务消息（RocketMQ）与 binlog 订阅（Canal → MQ）的区别
- 34.7 最大努力通知与对账兜底
- 34.8 选型决策树：一致性强度 × 性能 × 复杂度
- 34.9 幂等设计：唯一索引、去重表、状态机前置校验

### 第 35 章　数据生命周期与多租户　★★

- 35.1 冷热分层：热数据 MySQL、温数据归档表、冷数据对象存储 / OLAP
- 35.2 归档策略：按时间分区 DROP、按主键批量迁移、双写切换
- 35.3 历史表查询的透明化（视图 / 联邦查询）
- 35.4 多租户三种模型：独立库、共享库独立 schema、共享表 + `tenant_id`
- 35.5 `tenant_id` 方案的索引设计（`tenant_id` 必须打头）与租户级资源隔离
- 35.6 数据合规：GDPR 删除权、数据脱敏、审计留痕
- 35.7 缓存与 DB 的一致性：Cache Aside、延迟双删、订阅 binlog 更新缓存、缓存击穿/雪崩的 DB 侧防护

---

## 第六卷　性能诊断与调优

### 第 36 章　性能分析方法论　★★★

> 核心问题：业务说"数据库慢"，你怎么在 10 分钟内给出方向性结论？

- 36.1 三层定位法：业务指标（RT/错误率）→ DB 指标（QPS/TPS/连接/锁）→ 系统指标（CPU/IO/内存/网络）
- 36.2 吞吐 vs 延迟曲线：为什么加并发 QPS 不涨反跌（拐点与排队）
- 36.3 USE 方法（Utilization / Saturation / Errors）在 MySQL 上的落地
- 36.4 从 `SHOW PROCESSLIST` 的 30 秒快照读出真相（哪些 state 说明什么）
- 36.5 火焰图与 `pt-pmp`、`perf` 抓 MySQL 热点函数
- 36.6 一次完整的排障时间线复盘（含错误判断与纠正过程）

### 第 37 章　监控指标体系　★★

- 37.1 必须监控的 20 个指标清单（含阈值建议与告警等级）
- 37.2 连接层：`Threads_connected` / `Threads_running` / `Aborted_connects` / 连接池等待
- 37.3 吞吐层：`Questions` / `Com_select` / `Com_insert` / `Com_update` 的比例异常含义
- 37.4 InnoDB 层：BP 命中率、脏页比例、`LSN` 差值、`history list length`、`row lock waits`
- 37.5 复制层：延迟、`relay_log_space`、applier 线程状态
- 37.6 慢查询趋势、`Table_open_cache` 命中、临时表落盘次数
- 37.7 采集方案：Prometheus + mysqld_exporter、云监控、自建 Agent 的取舍

### 第 38 章　慢查询与 performance_schema 实战　★★★

- 38.1 慢日志配置：`long_query_time`、`log_queries_not_using_indexes` 的噪音、`log_slow_admin_statements`
- 38.2 `pt-query-digest` 输出逐段解读（Response time 分布、Rows examine 比例）
- 38.3 慢查询治理闭环：采集 → 归类 → 定责 → 优化 → 回归验证
- 38.4 `performance_schema` 核心表：`events_statements_summary_by_digest`、`events_waits_summary_global_by_event_name`、`file_summary_by_instance`
- 38.5 `sys` schema 的 20 个高频视图（`statement_analysis`、`innodb_lock_waits`、`schema_table_statistics`）
- 38.6 生产者/消费者配置与内存开销控制
- 38.7 `SHOW PROFILE` 的替代（已废弃）与现代 profiling 手段

### 第 39 章　InnoDB 状态与等待事件解读　★★

- 39.1 `SHOW ENGINE INNODB STATUS` 逐段精读（BACKGROUND THREAD / SEMAPHORES / TRANSACTIONS / FILE I/O / INSERT BUFFER / LOG / BUFFER POOL / ROW OPERATIONS）
- 39.2 `SEMAPHORES` 里的 `os_waits` 高意味着什么
- 39.3 常见等待事件字典：`buf_pool_mutex`、`log_sys`、`dict_table_stats_latch`、`ibuf`、`row_lock`、`trx_sys`
- 39.4 `ROW OPERATIONS` 的 `queries inside InnoDB` 与 `queries in queue` 的差值诊断
- 39.5 `INSERT BUFFER AND ADAPTIVE HASH INDEX` 的异常模式

### 第 40 章　参数与操作系统层调优　★★

- 40.1 内存分配：`innodb_buffer_pool_size`（占物理内存多少）、连接级 buffer 的乘数效应、OOM 的真实来源
- 40.2 IO 相关：`innodb_io_capacity` / `max_io_capacity`、`innodb_flush_neighbors`（SSD 必关）、`innodb_thread_concurrency`
- 40.3 并发相关：`max_connections` / `thread_cache_size` / `table_open_cache` 的联动
- 40.4 临时表与排序：`tmp_table_size` / `max_heap_table_size` 必须一致、`internal_tmp_mem_storage_engine`
- 40.5 优化器相关：`eq_range_index_dive_limit`、`range_optimizer_max_mem_size`、`optimizer_switch` 关键位
- 40.6 OS 层：IO 调度器（noop/none for SSD）、文件系统（XFS vs ext4）、NUMA + `numactl --interleave`、透明大页、swap 倾向
- 40.7 容器化场景：cgroup 内存限制与 `innodb_buffer_pool_size` 的匹配、CPU 限流下的抖动
- 40.8 参数模板：OLTP 在线业务 / 报表分析 / 高写入 / 从库 四套推荐配置及理由

### 第 41 章　典型案例复盘集　★★★

> 每个案例统一格式：现象 → 误判 → 数据 → 根因 → 处置 → 长效措施

- 41.1 连接数被打满：`wait_timeout` 过大 + 连接池泄漏
- 41.2 QPS 骤降 90%：一条 SQL 选错索引引发的雪崩
- 41.3 RT 抖动：脏页刷盘与 checkpoint 年龄过高
- 41.4 主从延迟 6 小时：无主键表 + 大事务 + 单线程回放
- 41.5 全站锁死：长事务持有 MDL，DDL 排队堵住所有查询
- 41.6 死锁风暴：库存扣减的加锁顺序不一致
- 41.7 磁盘爆满：undo 表空间 + binlog 未清理
- 41.8 内存 OOM：`sort_buffer_size` × 高并发
- 41.9 数据不一致：半同步降级为异步未告警
- 41.10 误删事故：PITR 恢复全过程

---

## 第七卷　版本、内核与技术选型

### 第 42 章　MySQL 8.0 / 8.4 关键特性　★★

- 42.1 事务性数据字典：`.frm` 消失、原子 DDL、`information_schema` 性能提升
- 42.2 Hash Join、CTE、窗口函数、`LATERAL` 派生表
- 42.3 降序索引、不可见索引、函数索引、多值索引（JSON 数组）
- 42.4 资源组（`CREATE RESOURCE GROUP`）、`max_execution_time`、连接属性
- 42.5 安全：角色、双密码、`caching_sha2_password`、密码策略
- 42.6 运维：Clone、`innodb_redo_log_capacity`、`innodb_dedicated_server`、`performance_schema` 增强
- 42.7 8.4 LTS 的变化：默认 `caching_sha2_password`、`mysql_native_password` 移除、若干参数废弃清单
- 42.8 5.7 vs 8.0 的性能对比与"升级不一定更快"的真实原因（字符集默认变 utf8mb4、统计信息变化）

### 第 43 章　升级与迁移　★★

- 43.1 升级路径：5.6 → 5.7 → 8.0 → 8.4 的不可跳版本与理由
- 43.2 `mysqlsh -- util checkForServerUpgrade` 检查项逐条解读
- 43.3 in-place 升级的风险点：`undo` 表空间、字符集、废弃参数、保留字
- 43.4 逻辑迁移 vs 物理迁移 vs 复制迁移（滚动升级）
- 43.5 异构迁移：Oracle / PostgreSQL → MySQL 的类型与语义映射
- 43.6 回滚预案：为什么 8.0 降级回 5.7 必须靠备份
- 43.7 升级演练 checklist 与灰度策略

### 第 44 章　内核源码导读（选修）　★

- 44.1 源码目录结构与关键子系统（`sql/`、`storage/innobase/`、`include/`）
- 44.2 线程模型：`master` / `io` / `purge` / `page cleaner` / `dict_stats`
- 44.3 `handler` 接口如何连接 Server 层与引擎层
- 44.4 B+ 树操作核心：`btr_cur_search_to_nth_level`、`mtr`（mini-transaction）
- 44.5 事务子系统：`trx_begin` → `trx_commit`、`lock_rec_lock` 的调用路径
- 44.6 如何读一条 `perf` / `gdb` 栈、如何编译调试版本
- 44.7 读源码的正确顺序与常见误区

### 第 45 章　云原生 MySQL 与技术选型　★★

- 45.1 存算分离架构：Aurora / PolarDB 的共享存储与日志即数据库
- 45.2 云 RDS 的能力边界：Proxy、只读实例、备份、审计、SQL 洞察
- 45.3 Serverless 数据库与冷启动、连接代理
- 45.4 K8s 上的 MySQL：Operator、有状态调度、本地盘 vs 网络盘
- 45.5 横向选型对比：MySQL vs PostgreSQL（MVCC 实现差异、索引能力、扩展性）、TiDB / OceanBase（HTAP、分布式事务）
- 45.6 选型决策矩阵：数据规模、一致性要求、团队能力、成本

---

## 第八卷　工程规范与业务实战

### 第 46 章　DDL 规范与在线变更　★★★

> 核心问题：给 5 亿行的表加一个字段，怎么做到业务无感？

- 46.1 DDL 算法：`COPY` / `INPLACE` / `INSTANT`，8.0 的 `ALGORITHM=INSTANT` 支持范围与限制（8.0.29 支持任意位置加列）
- 46.2 Online DDL 的锁阶段：`EXCLUSIVE` → `SHARED` → `EXCLUSIVE`，为什么还有短暂阻塞
- 46.3 MDL 与 DDL 的致命组合（回指第 18 章）
- 46.4 `gh-ost` 原理：主从切换式拷贝、`_ghc` 表、限流与 `throttle`
- 46.5 `pt-online-schema-change` 原理：触发器 + 分块拷贝 + 原子 `RENAME`
- 46.6 两种工具与原生 Online DDL 的选型
- 46.7 大表 DDL 的窗口选择、前置检查（磁盘、复制延迟、连接数）
- 46.8 DDL 规范清单：必须显式指定算法、禁止无 `WHERE` 的批量变更、字段默认值策略

### 第 47 章　SQL 审核与治理闭环　★★

- 47.1 上线前审核：执行计划预演、`EXPLAIN` 强制走索引、影响行数评估
- 47.2 审核规则引擎设计：禁止项（无索引更新/删除、`SELECT *`、大事务）、警告项、建议项
- 47.3 慢查询治理的组织机制：Owner 制、SLA、周报、TOP SQL 责任制
- 47.4 查询指纹（digest）归一化与同类问题聚合
- 47.5 SQL 防火墙与限流（`MAX_EXECUTION_TIME`、ProxySQL 规则、连接池侧限制）
- 47.6 数据访问层规范：ORM 的 N+1、批量接口、分页强制、禁止动态拼接

### 第 48 章　权限、安全与合规　★★

- 48.1 最小权限模型：账号分级（应用只读/读写、运维、DBA）、库表级授权
- 48.2 权限缓存与 `FLUSH PRIVILEGES` 的真实作用
- 48.3 SQL 注入的真实防线（参数化、`sql_mode`、最小权限兜底）
- 48.4 数据脱敏与加密：TDE、列级加密、脱敏视图、审计日志
- 48.5 审计方案：`audit_log` 插件、general_log 的性能代价、旁路抓包
- 48.6 合规要求：等保、数据出境、删除权实现

### 第 49 章　业务模型实战（上）：交易与库存　★★★

- 49.1 订单表设计：订单主表 + 明细 + 扩展表的拆分逻辑、状态机设计
- 49.2 库存扣减三种方案：`UPDATE ... WHERE stock >= n`、乐观锁版本号、预扣 + 流水表，各自的并发上限与超卖风险
- 49.3 秒杀场景：热点行拆分、库存分桶、异步落库、限流与排队
- 49.4 账户余额与流水：`UPDATE` 加锁 vs 流水驱动、对账机制
- 49.5 幂等与防重：唯一索引 + 状态机 + 请求去重表
- 49.6 分布式事务在交易中的落地（引向第 34 章）
- 49.7 大促前的容量评估与压测

### 第 50 章　业务模型实战（下）：内容、计数与队列　★★

- 50.1 Feed / 时间线：推模式、拉模式、推拉结合，以及 MySQL 在其中的角色
- 50.2 计数系统：`UPDATE count=count+1` 的热点、分桶计数、Redis + 定期落库
- 50.3 排行榜：`ORDER BY score` 的索引设计、窗口函数、离线预计算
- 50.4 标签与多条件筛选：组合索引的爆炸、位图、倒排表、ES 兜底
- 50.5 树形结构：邻接表、路径枚举、闭包表、嵌套集，各自的查询代价
- 50.6 用 MySQL 做队列：`SELECT ... FOR UPDATE SKIP LOCKED`（8.0）、可见性超时、为什么不推荐
- 50.7 消息/任务表设计：状态、重试次数、下次执行时间、索引
- 50.8 报表与聚合：预聚合表、物化视图模拟、读从库 + OLAP 分流

### 第 51 章　容量规划与压测　★★

- 51.1 容量模型：QPS × 平均行数 × 平均行宽 = 带宽与内存需求
- 51.2 数据量增长预测与拆分时间点倒推
- 51.3 压测方法：sysbench（`oltp_read_write` / `oltp_point_select`）、TPCC、真实流量回放
- 51.4 压测指标解读：TPS 拐点、99 线、错误率突变的三个信号
- 51.5 压测环境与生产的差异（数据量、分布、缓存命中率）及修正系数
- 51.6 扩容决策：垂直升配 vs 加从库 vs 分片 vs 上云

### 第 52 章　故障应急与 SOP　★★★

- 52.1 应急分级与响应流程（P0~P3、升级路径、on-call 交接）
- 52.2 十大高频故障的处置卡片（现象 / 3 分钟判断 / 止血动作 / 根因排查）
- 52.3 止血优先原则：限流、熔断、降级、切从库、回滚，各自的代价
- 52.4 高危操作清单与双人复核（`KILL`、`DROP`、`UPDATE` 无 `WHERE`、主从切换）
- 52.5 事故复盘模板：时间线、影响面、根因（5 Why）、改进项与验收
- 52.6 稳定性建设：混沌演练、切换演练、备份演练的排期机制

---

## 附录

### 附录 A　参数速查表　★★
按「内存 / IO / 并发 / 复制 / 优化器 / 日志」分类，给出：参数名、默认值、推荐值区间、改动风险、生效方式（动态/静态）。

### 附录 B　错误码与异常速查　★★
`1062` 唯一键冲突、`1205` 锁等待超时、`1213` 死锁、`1032/1062` 复制错误、`1040` 连接数满、`1114` 表满、`1878` 磁盘不足——每条给：触发条件、典型日志、处置动作。

### 附录 C　工具清单　★
XtraBackup、gh-ost、pt-toolkit 全家桶、sysbench、mysqlbinlog、innotop、orchestrator、ShardingSphere、Canal/Debezium、Prometheus exporter。

### 附录 D　诊断 SQL 手册　★★★
可直接复制的 40 条诊断语句：找锁等待链、找长事务、找慢 SQL、找未使用索引、找碎片表、找连接来源、查 binlog 位点、查复制状态、查表空间占用。

### 附录 E　面试高频 100 问　★★
按卷分组，每题给「一句话结论 + 展开要点 + 常见错误回答」。示例：
- 为什么 InnoDB 用 B+ 树而不是 B 树？
- RR 隔离级别下幻读被解决了吗？
- `UPDATE` 没走索引会锁多少行？
- redo log 和 binlog 为什么需要两阶段提交？
- 主从延迟怎么优化？
- 分库分表后如何做分页？

### 附录 F　学习路径与参考　★
- 入门→进阶→内核 三阶段书单与源码阅读顺序
- 官方文档重点章节索引（InnoDB Locking、Optimizer、Replication）
- 推荐博客/邮件组/会议（Percona Live、MySQL Blog）

### 附录 G　实验环境　★★
`docker-compose.yml` 一键起 1 主 2 从 + 8.0/5.7 双版本；预置 1000 万行测试数据生成脚本；每章实验对应的 SQL 脚本目录。

---

## 二、每章统一写作模板

每章必须包含以下 7 个部分，缺一不可：

```text
## X. 章标题

> 核心问题：<一句话，必须是读者真实会问的问题>

### 1. 场景切入
   一个真实的故障/现象/面试题，制造认知冲突

### 2. 机制原理
   结构图 + 流程图 + 关键数据结构（表 / 字段 / 状态机）
   必须能回答"如果不这样设计会怎样"

### 3. 关键结论（3~5 条）
   加粗，可直接被引用/背诵

### 4. 实验验证
   可复制的 SQL / 脚本 + 预期输出片段 + 解读

### 5. 常见误区与踩坑
   ⚠️ 每条给：错误认知 → 为什么错 → 正确理解 → 真实事故

### 6. 生产建议 / Checklist
   可直接用于 Code Review 与架构评审

### 7. 延伸
   关联章节 + 面试追问 + 官方文档链接
```

**写作硬性要求**

| 项 | 要求 |
|---|---|
| 结论可验证 | 所有"更快/更慢"必须有机制解释或实验数据，禁止"一般来说" |
| 版本标注 | 涉及版本差异必须标 `[5.7]` `[8.0.13+]` `[8.4]` |
| 图示 | 每章至少 1 张图（结构图/流程图/加锁示意图），用 Mermaid 或 ASCII |
| 代码 | SQL 必须可在附录 G 环境直接跑通 |
| 篇幅 | 核心章 4000~6000 字，★★ 章 2500~3500 字，★ 章 1500 字以内 |
| 命名 | 文件名 `docs/ch{两位编号}-{kebab-case}.md`，如 `docs/ch19-locking-rules.md` |

---

## 三、优先级与产出排期

| 优先级 | 章节 | 理由 |
|---|---|---|
| **P0（先写）** | Ch1、2、4、5、8、9、11、17、18、19、20、38 | 覆盖 80% 的线上问题与面试高频，是最小可用版本 |
| **P1** | Ch3、6、7、10、12、13、14、15、16、21、22、25、26、28、29、31、33、36、46、52 | 补齐原理链条与工程能力 |
| **P2** | Ch23、24、27、30、32、34、35、37、39、40、41、42~45、47~51 | 完整性与扩展视野 |
| **附录** | D、E 优先（可直接使用），其余随正文推进 | |

**建议节奏**：P0 完成即为 v0.1 可发布；每完成一卷做一次交叉校验（结论是否与前面章节冲突）。

---

## 四、待确认事项

1. **是否需要配套代码仓库结构**（如 `labs/ch19/` 下放每章实验脚本）？当前大纲已按此预留。
2. **图示工具**：Mermaid（GitHub 友好）/ 手绘 SVG / ASCII，倾向 Mermaid。
3. **是否要中英双语或纯中文**：当前假设纯中文 + 英文术语。
4. **是否包含面试题专题独立成册**：当前放在附录 E，若单独成册可拆出。
