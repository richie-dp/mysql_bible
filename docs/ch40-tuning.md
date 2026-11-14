# 第 40 章　参数与操作系统层调优

> **一句话结论**：参数能解决的问题，几乎都能用一条正确的索引解决得更彻底；动参数之前先证明"这一环就是瓶颈"，动完再证明"它确实好了"，否则就是拿生产环境做实验。

## 40.0 场景：OOM 之后，他们把 buffer pool 调小了

凌晨 3 点 17 分，账单库的 `mysqld` 从监控上消失。`dmesg` 里留着那行记录：

```text
Out of memory: Killed process 28471 (mysqld) total-vm:105209344kB, anon-rss:98746332kB
# 输出形态（未实跑，字段含义以此为准）
```

值班的人看了一眼 `innodb_buffer_pool_size = 96G`，机器 128G，结论很清楚：给多了。改成 64G 重启，一周无事；第八天凌晨，同一个进程又被杀了一次。

他们翻了慢日志，找到一条商户对账报表：

```sql
SELECT merchant_id, SUM(amount) FROM bill_detail
WHERE created_at >= '2026-11-01'
GROUP BY merchant_id ORDER BY 2 DESC;
```

报表平台每个导出任务开一个连接，晚间高峰 180 个并发。`sort_buffer_size` 半年前被改成 512M，理由是"加速大结果集排序"。

512MB × 180 = 92GB。这笔账跟 buffer pool 毫无关系，但两者抢的是同一块物理内存。把 BP 从 96G 调到 64G，只是把省下的 32G 让给了这个乘法，把下一次死亡时间往后推了几天。

![图 40-1 MySQL 进程的内存构成：固定块与浮动块](images/ch40-fig1.svg)

## 40.1 改参数之前，先回答三个问题

**第一，有可观测的症状吗？** 不是"感觉慢"，而是某个计数器或分位数在确定的时间窗内变了：`Threads_running` 从 20 涨到 180、`Innodb_buffer_pool_wait_free` 每秒都在涨。没有这个起点，你分不清"参数生效了"和"高峰过去了"。

**第二，知道它作用于哪条链路吗？** 图 40-2 把本章的参数挂在六个环节上。`sort_buffer_size` 动的是每连接临时内存，`innodb_io_capacity` 动的是每秒刷多少脏页，两者不会互相替代。

**第三，改完能验证吗？** 同一指标、同一压力、同一时间窗，缺一条就不成立。

一条缺失的索引能让某条 SQL 从 80ms 变成 8s，而 buffer pool 在命中率 99% 之后的边际收益接近零——工作集已经装下了。**参数调优的天花板，通常低于补一个联合索引。**

本章只写会出事的十几个参数。不在这里出现的，说明它不该被随手改：要么不影响当前瓶颈，要么改了也说不出好坏。

![图 40-2 每个参数挂在哪一环](images/ch40-fig2.svg)

## 40.2 内存：一个大方块，和一个乘法

**实例独占物理机**时，物理内存的 70~80% 是起点：128G 给 90~100G。前提是工作集确实大于内存，且机器上没有别的服务。

**与其他服务共部署**时，必须给 OS page cache 留空间。留的不是"给 MySQL 的缓存"，是给三件事：binlog 写入（不走 `O_DIRECT`）、数据文件读写（默认 `innodb_flush_method=fsync` 时也过 page cache）、备份的顺序读。BP 顶到 90%，page cache 只剩几个 G，现象会很怪：命中率漂亮，提交延迟和备份耗时却周期性抖动。

BP 的大小会被向上取整到 `innodb_buffer_pool_chunk_size × instances` 的整数倍。在线扩容是加 chunk，基本无痛；缩容要先把 chunk 里的脏页刷出去，等于自造一次 IO 风暴（第 2 章 2.9）。

`innodb_buffer_pool_instances` 分片是为了减少 mutex 争用，代价是每片的 LRU 变薄。热点页按 `page_id % instances` 固定映射，切得太碎就会出现"一个实例先满、其余空着"，而这个实例的 free list 见底会触发用户线程同步刷脏。判据是**每个实例至少 1GB**。官方默认 8，BP 小于 1GB 时实际只有 1 个实例。chunk 的**数量**能跟着 BP 在线变，但 `innodb_buffer_pool_chunk_size` 是只读变量，改它必须重启。

连接级 buffer 是另一回事，它们按需分配：

| 参数 | 什么时候分配 | 一次查询几份 |
|---|---|---|
| `sort_buffer_size` | 需要 filesort 时 | 每个排序步骤各一份，子查询、`UNION`、`GROUP BY` 叠加时多份 |
| `join_buffer_size` | join 用不上索引（BNL）时 | 每个这样的 join 一份 |
| `read_buffer_size` | 顺序扫描一张表 | 每张被扫的表一份 |
| `read_rnd_buffer_size` | 需要按行号回读时 | 每个这样的步骤一份 |
| `binlog_cache_size` | 事务要写 binlog | 每个写事务一份，超了落临时文件 |
| `tmp_table_size` | 需要内存临时表 | 每张临时表一份 |

真实占用不是"这些参数之和 × 连接数"，而是：

```text
RSS ≈ BP + 固定开销 + Σ(单个 buffer × 该 buffer 的并发份数)
```

用 `max_connections` 算是上界，用 `Threads_running` 算更接近真出事的量级，两个都算一遍。

`sort_buffer_size = 256M` × 200 个并发排序 ≈ 51GB。这笔内存跟 buffer pool 无关，但 OOM Killer 不认识参数名，只认 `anon-rss`。

> ⚠️ MySQL 的 OOM 现场，先查 `sort_buffer_size` / `join_buffer_size` × `Threads_running`，而不是先怀疑 `innodb_buffer_pool_size` 太大。

定位要落到线程：

```sql
SELECT t.PROCESSLIST_ID, t.PROCESSLIST_USER, t.PROCESSLIST_INFO,
       ROUND(SUM(m.CURRENT_NUMBER_OF_BYTES_USED)/1024/1024) AS mb
FROM performance_schema.memory_summary_by_thread_by_event_name m
JOIN performance_schema.threads t USING (THREAD_ID)
WHERE t.PROCESSLIST_ID IS NOT NULL
GROUP BY t.PROCESSLIST_ID, t.PROCESSLIST_USER, t.PROCESSLIST_INFO
ORDER BY mb DESC LIMIT 10;
```

`sys.memory_global_by_current_bytes` 按事件名聚合，回答"哪一类 buffer"；这条按线程聚合，回答"哪个连接"。两个一起看，才能从"内存涨了"走到"就是那条报表 SQL"。

`max_connections` 不是设大就安全。每个连接有固定开销：线程栈（`thread_stack` 默认 1MB 量级）加 net buffer（初始 16KB，按需长到 `max_allowed_packet`）。1000 个空闲连接先占 1GB，真正的风险是它们同时开始排序。

## 40.3 IO：刷脏预算与提交语义

**`innodb_io_capacity`。** page cleaner 每轮刷多少页，由脏页比例、redo 水位和它共同决定（第 2 章 2.4）。这里的"一次 IO"约等于一个 16KB 页，默认 200 ≈ 3MB/s，是机械盘时代的数。SSD 上按设备 16KB 随机写 IOPS 的 50~70% 设：设小了 checkpoint age 持续上涨，70% 以上前台写入被拦住（第 7 章）；设大了 page cleaner 吃满设备带宽，binlog 的 `fsync` 和其他实例的读一起抖。`innodb_io_capacity_max` 是突发上限，默认约为它的 2 倍，两个一起动。

**`innodb_flush_neighbors`。** 刷一个脏页时，相邻页也脏就顺带刷。HDD 上一次寻道刷多页，摊薄成本；SSD 上随机写和顺序写成本接近，顺带刷只是让一次 checkpoint 写出更多页——写放大上升，还把本可以晚点刷的页提前写掉。`[8.0]` 默认 `0`，`[5.7]` 默认 `1`。从 5.7 升上来、配置文件里显式写过 `1` 的实例，升级不会帮你改回来。

**`innodb_flush_log_at_trx_commit`。** `1` 每次提交 `fsync` redo；`2` 只写 OS cache 不 `fsync`，`mysqld` 崩溃不丢，操作系统崩溃或掉电丢最近约 1 秒；`0` 每秒一次，连 `mysqld` 崩溃也丢。`[8.0]` 默认 `1`。十年前大量"优化指南"让你改 `2` 换吞吐，代价是小字里的"崩溃丢最近 1 秒事务"。账单、支付、库存这类场景不可接受。要吞吐走组提交（第 6 章），它把多个事务的 `fsync` 合并，持久性不变。

**redo 容量。** `[8.0.30+]` 用 `innodb_redo_log_capacity`（可在线调），更早是 `innodb_log_file_size × innodb_log_files_in_group`。太小，checkpoint 追得紧、写入周期性抖动；太大，崩溃恢复要重放的多，而恢复是单线程（第 7 章）。判读：抓 `Log sequence number - Last checkpoint at` 的日峰值除以总容量，长期超过 70% 说明偏小，低于 20% 说明给多了。

## 40.4 并发入口与临时表

`innodb_thread_concurrency` 默认 `0`，不限制。设成非 `0` 后，超出的线程在入口排队，就是第 39 章 `queries in queue` 那一栏。排队不区分快慢：一条 10ms 的等值查询排在 2s 的报表后面，尾延迟被放大，连接还占着。**绝大多数场景不该设**；只有在 `wait/synch/*` 的 InnoDB 内部锁等待占主导、活跃线程数远大于 CPU 核数时，才从 2 倍核数往下试。

`thread_cache_size` 看 `Threads_created` 的增速：持续增长说明线程复用不足，每次建连都要走内核 clone。`[8.0]` 默认 `-1`，按 `max_connections` 自动 sizing，反而不用手调。

`table_open_cache` 不是越大越好：每个打开的表在缓存里有一个 handler 实例，占内存也占文件描述符。判据是 `Opened_tables`（累计打开次数）是否持续增长；不增长就说明够用，再加只会让 flush 遍历的链表更长。

`tmp_table_size` 与 `max_heap_table_size` 必须一致。MEMORY 引擎下生效值是两者的 `min()`，不一致时大的那个白调。但 `[8.0]` 默认 `internal_tmp_mem_storage_engine=TempTable`，阈值是 `temptable_max_ram`，`tmp_table_size` 根本不参与——这正是"我明明调大了怎么还是落盘"的答案。`[5.7]` 只有 MEMORY 引擎，`VARCHAR` 按最大长度分配，遇到 BLOB/TEXT 直接落盘（第 29 章）。比值 `Created_tmp_disk_tables / Created_tmp_tables` 的读法见第 37 章。

## 40.5 优化器：两个阈值造成的计划断层

`eq_range_index_dive_limit`（默认 200）：等值条件不超过它时，优化器对每个值做一次 index dive，把行数数准；超过就退化成用索引统计信息估算。`IN` 列表从 199 个值变成 201 个，走两条不同的估算路径，计划可能整体翻转。调大的代价是每次优化多几百次 B+ 树探测（第 10 章）。

`range_optimizer_max_mem_size`（默认 8MB）：范围分析要记录每个 range 的边界，值越多内存越大；超限后优化器直接放弃 range 分析，退化成全表扫描。"`IN` 里塞一万个值反而变慢"的根因通常在这里，`EXPLAIN` 之后在 `SHOW WARNINGS` 或 optimizer trace 里能看到 `Memory capacity ... exceeded. Range optimization was not done`。

`optimizer_switch` 三个位值得知道边界：`index_merge` 默认开，只在"多个索引各自选择率都高、交集很小"时划算，其余时候两次索引扫描加交集比单索引回表更贵；`mrr` 默认开，把随机读整理成顺序读，SSD 上收益有限；`batched_key_access` 默认关，打开要求 `mrr` 开启且被驱动表有可用索引。三个都该 `SET SESSION` 改，全局改等于让所有查询一起承担你的假设。

## 40.6 操作系统与容器

**IO 调度器**：NVMe 用 `none`（老内核叫 `noop`），内核再排一层只增加延迟；SATA SSD 用 `mq-deadline` 或 `none`；HDD 用 `mq-deadline`。

**文件系统**：XFS 在大文件、并发写、在线扩容上更稳，ext4 更成熟。差异常常在挂载参数：`noatime` 去掉每次读都要更新 inode 时间的写；`nobarrier` 只在带电池保护的阵列上有讨论空间，普通盘上等于放弃写屏障。

**NUMA**：默认本地分配，buffer pool 启动时由单个线程申请，很容易整块落在 node 0，其他 node 的线程每次访存都走跨片互联。`numactl --interleave=all` 让页交替分配，用单次访存的最坏延迟换"没有哪个 node 先耗尽"。验证看 `numastat -p $(pidof mysqld)` 的 `Numa_Miss` 占比。

**透明大页**：官方建议关闭。`khugepaged` 周期性把 4KB 页合并成 2MB 页，合并要迁移页、拿 mmap 锁，撞上正在申请内存的线程就是一次毫秒级停顿；分配失败时内核走直接回收，把一批不该换出的页扫一遍。

```bash
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

**`vm.swappiness`** 设 1，不是 0。0 会让内核在几乎没内存时仍避免换出匿名页，最后直接触发 OOM Killer；1 保留"实在没办法时换一点"的能力。

**容器**里两件事必须手工算：

- 内存：`[8.0]` 对 cgroup 限制的感知并不可靠（部分版本有改进，不要依赖），`innodb_buffer_pool_size` 写多少就分配多少。推导是 `BP ≤ limit − max_connections × 单连接开销 − 预留`。8G 容器、500 连接、单连接 buffer 合计 4M，先扣 2G，再留 1G 给页缓存与临时文件，BP 最多 5G。超了就是 `oom_kill`。
- CPU：`cpu.cfs_quota_us` 按 100ms 周期结算，一个周期内用完配额，整个 cgroup 被 throttle。表现是"CPU 使用率只有一半，但每秒都有几十毫秒的尖峰"。查 `cpu.stat` 的 `nr_throttled` 与 `throttled_time`。

## 40.7 四套配置模板

以 32 核 / 128GB / NVMe / MySQL 8.0 为例。**这是起点不是终点**，换机器、换盘型都要重算。

| 场景 | 关键设置 | 为什么这样配 |
|---|---|---|
| OLTP 在线业务 | BP 96G；`instances` 8；`sort_buffer_size` 2M；`join_buffer_size` 4M；`io_capacity` = 实测 16K 随机写 IOPS × 0.6；`flush_neighbors` 0；`flush_log_at_trx_commit` 1 | 并发高，任何"每连接"的大值都会被乘成事故；单条查询简单，排序和 join 都小 |
| 报表分析 | BP 80G；`sort_buffer_size` 32M；`join_buffer_size` 32M；`temptable_max_ram` 4G；`tmp_table_size` = `max_heap_table_size` = 256M；`max_connections` 40 | 并发低，乘数效应不成立；内存给单条查询更划算。唯一该调大连接级 buffer 的场景，前提是连接数真的被限住 |
| 高写入 | `flush_log_at_trx_commit` 1；`sync_binlog` 1；redo 容量 8G；`io_capacity` 按设备 70%；`flush_neighbors` 0 | 瓶颈在 `fsync` 与刷脏预算，不在内存；redo 给大是给 checkpoint 留缓冲，代价是恢复变慢（第 7 章） |
| 从库（replica） | `read_only` ON；`super_read_only` ON；`log_replica_updates` ON；BP 与主库（source）同或更大；`flush_log_at_trx_commit` 1 | 回放本质仍是提交，持久性没理由放松；`log_replica_updates` 让回放的事务再写一遍 binlog，写放大近一倍，没有级联和 PITR 需求可以关（第 22 章） |

## 40.8 关键结论

1. **buffer pool 决定"能装多少"，连接级 buffer 决定"会不会 OOM"。** 前者是预分配的固定预算，后者是随并发线性增长的乘法。
2. **OOM 现场的第一嫌疑是 `sort_buffer_size` / `join_buffer_size` × `Threads_running`。** 调小 BP 只是把内存让给这个乘法，症状会推迟，不会消失。
3. **`innodb_io_capacity` 默认 200 属于 HDD 时代，必须和 BP 一起调。** 池子变大而不加预算，脏页积压的绝对量成倍增长。
4. **`innodb_flush_log_at_trx_commit=1` 不可交易。** 改成 0 或 2 换来的吞吐，标价是"崩溃丢最近 N 秒已提交事务"。
5. **优化器那两个阈值造成的不是"慢"，是"计划断层"。** 199 与 201 个值走两条估算路径，索引可能整体换一个。
6. **容器里的 BP 必须手工算。** MySQL 不会可靠地感知 cgroup limit，超限的下场是 `oom_kill`。

## 40.9 实验验证

### 实验一：把最坏情况的内存账算出来

```sql
SELECT ROUND(@@innodb_buffer_pool_size/1024/1024/1024, 1) AS bp_gb,
       @@max_connections AS max_conn,
       ROUND((@@innodb_buffer_pool_size
         + @@max_connections * (@@sort_buffer_size + @@join_buffer_size
         + @@read_buffer_size + @@read_rnd_buffer_size))/1024/1024/1024, 1) AS worst_gb;
```

预期形态（`# 输出形态（未实跑，字段含义以此为准）`）：

```text
bp_gb  max_conn  worst_gb
 96.0       500     142.5
```

`worst_gb` 是上界（并非所有 buffer 同时分配），但它一旦超过物理内存，就存在一条并发路径能打死实例。换成当时的 `Threads_running` 再算一次，两个数之间就是真实风险区。

### 实验二：checkpoint 水位

```sql
SHOW ENGINE INNODB STATUS\G
```

只看 `LOG` 段：`Log sequence number` 减 `Last checkpoint at`，除以 redo 总容量。高峰抓三次，峰值超过 70% 就该动 `io_capacity` 或加 redo。

### 实验三：确认 OS 层配置

```bash
cat /sys/kernel/mm/transparent_hugepage/enabled     # [never]
grep -i AnonHugePages /proc/meminfo                 # 接近 0
cat /sys/block/nvme0n1/queue/scheduler              # [none]
numastat -p $(pidof mysqld) | head -6               # Numa_Miss 占比
```

## 40.10 常见误区

⚠️ **"OOM 就是 buffer pool 太大"**
BP 是唯一"看得见"的大数，所以背锅的总是它。但杀死进程的是 RSS，RSS 里增长最快的是每连接的排序/join buffer。调小 BP 会让 OOM 晚来几天，然后以同样的方式再来一次。

⚠️ **"`sort_buffer_size` 调大，排序就快"**
它只影响内存排序能不能装下，装得下也不会更快；而它是每连接、可多份分配的，账单由并发来付。排序慢的正解通常是让索引给出顺序。

⚠️ **"`innodb_thread_concurrency` 设成 CPU 核数最稳"**
它限制的是"进入 InnoDB 的线程数"，不是"干活的线程数"。设小了，等锁、等 IO 的线程也占名额，能跑的反而更少。

## 40.11 生产 Checklist

- [ ] BP 与实例形态匹配吗？（独占 / 共部署 / 容器）容器里按 `limit − 连接开销 − 预留` 算过吗
- [ ] `max_connections × 单连接 buffer` 的最坏情况算过吗？结果小于物理内存吗
- [ ] `sort_buffer_size`、`join_buffer_size` 超过 8M 的，每一条都有压测依据吗
- [ ] `io_capacity` 按设备实测设的？高峰 checkpoint age 低于 70% 吗
- [ ] `flush_neighbors` 在 SSD 上是 0 吗？（5.7 升 8.0 的重点）
- [ ] `flush_log_at_trx_commit` 与 `sync_binlog` 都是 1 吗？改过的写清丢多少秒了吗
- [ ] `instances × 1GB ≤ BP` 成立吗？
- [ ] 容器 `cpu.stat` 的 `nr_throttled` 在涨吗？
- [ ] THP 是 `never`、`vm.swappiness ≤ 1`、NUMA 开了 interleave 吗

## 40.12 延伸

- **前置**：第 2 章（刷脏预算）、第 7 章（checkpoint 与恢复时间）、第 14 章（临时表与排序）、第 10 章（index dive）。
- **关联**：第 37 章（比值判读）、第 39 章（`queries in queue`）、第 41 章 41.9（OOM 复盘）、第 22 章（从库参数）。
- **面试追问**：
  - "buffer pool 调大后 P99 反而变差？" → 刷脏预算没跟着加，脏页积压的绝对量变大，刷脏从涓流变成周期性爆发。
  - "`sort_buffer_size` 为什么不是越大越好？" → 每连接、可多份分配，账单按并发数乘，超过需求后不再提速。
  - "`innodb_flush_log_at_trx_commit=2` 丢什么？" → 最近约 1 秒已提交事务，触发条件是操作系统崩溃或掉电。
- **官方文档**：`InnoDB Startup Options and System Variables`、`Server System Variables`、`Optimizing InnoDB Disk I/O`。
