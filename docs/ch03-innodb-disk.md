# 第 3 章　InnoDB 磁盘体系：表空间、页与行

> **一句话结论**：InnoDB 的磁盘空间按页分配，`DELETE` 只把页内的记录槽标成可复用，页本身仍挂在表上——所以行没了、文件不会小；能还盘的只有"重建文件"。

## 3.0 场景：删掉 60% 的账单，磁盘一个字节没退

账单明细表 `bill_detail` 一亿多行，2025 年之前的历史数据占六成，业务只查最近 13 个月。DBA 按 `bill_date` 分批删了三个晚上，每批 5000 行，`Rows_affected` 逐批对得上，第二天的慢查询也少了。

`df -h` 纹丝不动。

```sql
SHOW TABLE STATUS LIKE 'bill_detail'\G
-- Data_length  ≈ 40GB   聚簇索引占的字节
-- Data_free    ≈ 24GB   已空出来、但仍留在文件里的字节
```

`Data_free` 涨上去了，含义是"这部分空间已经不属于任何一行，但物理上还躺在 `bill_detail.ibd` 里"。运维的要求很直接：今晚就释放。

问题在于，这张表要重建，就得有差不多一倍的空闲磁盘；而磁盘只剩不到 10%。于是现场变成一个死局：**不重建，几十小时后写满；重建，现在写满。**

这不是谁操作错了。是"InnoDB 的空间单位是页，不是行"这件事，从来没进过容量规划。

## 3.1 表空间：五种容器，五种账本

一个 `.ibd` 文件不是"一堆行"，是一叠 16KB 的页，外加几张管理这些页的元数据页。表空间就是"页的命名空间"——同一个表空间里的页共用一个 space id，页号在空间内唯一。

| 表空间 | 文件 | 主要装什么 | 会自己变小吗 |
|---|---|---|---|
| 系统表空间 | `ibdata1` | change buffer、双写缓冲（`[8.0.20]` 之前）、`innodb_file_per_table=OFF` 时的用户表 | 不会 |
| 独立表空间 | `表名.ibd` | 一张表的聚簇索引 + 全部二级索引 | `DROP` / `TRUNCATE` 会，`DELETE` 不会 |
| 通用表空间 | `CREATE TABLESPACE` 指定的文件 | 多张表共享，可以放在 datadir 之外 | 不会，需重建 |
| undo 表空间 | `undo_001`、`undo_002` | 回滚段与旧版本 | 8.0 会自动 truncate |
| 临时表空间 | `ibtmp1`、`#innodb_temp/temp_*.ibt` | 临时表数据与其回滚段 | 重启即重建 |

几个容易踩错的点：

- **8.0 的数据字典不在 `ibdata1` 里**，在 `mysql.ibd`。`[5.7]` 的 `.frm` 文件、`INNODB_SYS_TABLES` 这套前缀带 `SYS` 的字典表，在 8.0 全部换成了事务性字典与 `INNODB_TABLES` 这类表名。升级后还去找 `.frm` 的人，会以为表丢了。
- `innodb_file_per_table` 从 5.6.6 起默认 `ON`。"删表能不能还盘"完全由它决定：`OFF` 时所有表挤在 `ibdata1` 里，`DROP TABLE` 也只是把页标成空闲，文件永远不会缩。
- `[5.7]` 允许 `innodb_undo_tablespaces=0`，undo 直接写进 `ibdata1`；8.0 之后 undo 必须独立，默认两个文件，`[8.0.14+]` 起这个参数被废弃，undo 表空间按需自动创建。
- 临时表空间是唯一"重启就清零"的：`ibtmp1` 在实例启动时重建。所以它涨到几百 GB 时，最快的处置不是删表，是挑窗口重启（或者等长事务结束让它自然回落）。
- 通用表空间的价值是"一个文件装多张表"：可以放到 datadir 之外、可以对整个表空间统一加密或压缩、搬迁时只搬一个文件。代价是不能单表回收——想缩，只能把表 `ALTER TABLE ... TABLESPACE=innodb_file_per_table` 搬出去，再重建原文件。

查一个库的真实占用：

```sql
SELECT NAME, SPACE_TYPE, ROW_FORMAT, FILE_SIZE, ALLOCATED_SIZE
FROM information_schema.INNODB_TABLESPACES
WHERE NAME LIKE 'shop/%';
```

`FILE_SIZE` 是按页数算出来的逻辑大小，`ALLOCATED_SIZE` 是文件实际占盘。两者不等，说明文件是稀疏的，或者用了页压缩。

## 3.2 段、区、页、行：五个层级，三种用途

![图 3-1 表空间到行的五级分解](images/ch03-fig1.svg)

从大到小：

- **表空间**：页的集合，一个文件。
- **段（segment）**：一组区，服务一个逻辑对象。每个索引有两个段——叶子节点段、非叶子节点段；undo 用的是回滚段。
- **区（extent）**：64 个连续的页，1MB。
- **页（page）**：16KB，IO 的最小单位。
- **行（row）**：唯一的逻辑单位，也是你唯一能看见的单位。

**为什么按区分，而不是按页分？** 如果一页一页地向文件要空间，一个索引的一万个页会散落在文件各处，范围扫描就从"顺着读"变成"跳着读"。按 1MB 连续分配，同一段的页大概率物理相邻，顺序扫描才能真正变成顺序 IO。

区的页数不固定，字节数固定：

| `innodb_page_size` | 一个区 | 说明 |
|---|---|---|
| 4KB | 256 页 | 1MB |
| 8KB | 128 页 | 1MB |
| 16KB（默认） | 64 页 | 1MB |
| 32KB | 64 页 | 2MB |
| 64KB | 64 页 | 4MB |

页大小只能在初始化实例时设定（`innodb_page_size`），建库之后改不了；备份、复制两端的页大小必须一致，否则物理备份无法恢复。它同时决定了单行上限（见 3.5），所以"把页调大提升性能"这个念头，代价比收益大得多。

段不是一开始就吃满 1MB。新段先按"碎片页"零散地要页，攒到 32 个页之后才转为按区分配。所以一张刚建好的空表，`.ibd` 只有 112KB（7 个页：文件头、inode、SDI、聚簇索引根页等），而不是 1MB 起步。

## 3.3 一个 16KB 的页里到底有什么

![图 3-2 数据页的内部布局](images/ch03-fig2.svg)

在 `innodb_page_size=16K` 下，一页 16384 字节，按功能切成七段：

| 区域 | 字节 | 装什么 |
|---|---|---|
| File Header | 38 | 页号、上一页/下一页、LSN、页类型、space id |
| Page Header | 56 | 槽数、堆顶、记录数、Free 链头、插入方向、页层级 |
| Infimum + Supremum | 26 | 两条伪记录，链表的头尾哨兵 |
| User Records | 可变 | 真实记录，按主键升序串成单链表 |
| Free Space | 可变 | 没分配的空间 + 已释放未复用的空洞 |
| Page Directory | 2 × N | 稀疏目录，一个槽管 4~8 条记录 |
| File Trailer | 8 | 旧 checksum + LSN 低 32 位 |

**File Header 里藏着两个关键指针：`FIL_PAGE_PREV` 和 `FIL_PAGE_NEXT`。** 叶子页之间的双向链表就存在这里，所以 `WHERE id BETWEEN 100 AND 200` 这种范围扫描，沿着链表往右走就行，不需要回到父节点重新路由。页类型字段（`FIL_PAGE_TYPE`，索引页是 17855）则让恢复和诊断工具能一眼区分索引页、undo 页、BLOB 页。

**Page Header 里的 `PAGE_DIRECTION` 是个被低估的字段。** 它记录这一页最近的插入方向：往右、往左、还是无序。这个值直接决定页满时怎么分裂（见 3.6）——所谓"自增主键插入快"，物理根源就在这里，不在优化器。

**Infimum 和 Supremum 是两条假记录**，heap_no 分别是 0 和 1，永远存在、永远最小和最大。有了它们，"找第一条"和"找最后一条"都不用判空，链表操作的边界条件少了一半。

**User Records 从偏移 120 开始，向高地址生长**；Page Directory 从页尾向低地址生长；中间剩下的就是 Free Space。记录之间靠记录头里 2 字节的 `next_record` 串起来，按主键升序，但**物理地址顺序和逻辑顺序无关**——后插入的小主键可能落在物理上更靠前的位置。

**File Trailer 是这七段里唯一"向后看"的结构。** 它固定 8 字节：前 4 字节是页的旧 checksum，后 4 字节是 LSN 的低 32 位。写一页时 InnoDB 先写页内容、最后写 trailer；崩溃恢复时把 trailer 和页头对一遍，对不上就说明这页只写了一半。16KB 的页在掉电时可能只落下去 4KB——这就是 partial write，也是 doublewrite 存在的全部理由（见第 7 章）。

### 页内查找：为什么不能一条条扫

一页能放几十到几百条记录，如果每次查找都从头顺着链表走，B+ 树下降到底层之后的开销就全部白费了。InnoDB 的解法是 Page Directory。

它是一张稀疏索引：把页内记录按每 4~8 条分成一组，每组只记一个 2 字节的槽，槽指向**这一组最后一条记录**的偏移。查找分两步：

1. **对槽做二分**。一个满页约 17 个槽，5 次比较就能定位到目标所在的组。
2. **进组后顺着 `next_record` 线性走**，最多 8 条。

合计十几次比较，而顺序扫是上百次。这就是"页内查找近似常数级"的真正含义，也是 B+ 树只需要三层就能覆盖上亿行的另一半原因（第一半是扇出）。

### 顺带把"单页最多多少行"算清楚

固定开销先扣掉：38 + 56 + 26 + 8 = 128 字节，可用 16256 字节，再扣掉 Page Directory（约 2%）。

一条记录的最小长度 = 5 字节记录头 + 主键 + 隐藏列 13 字节（见 3.4）。取主键 `BIGINT` 8 字节，最小 26 字节，一页上限约 625 条。业务表的行远不止主键，按 150 字节的行宽算，一页约 100 条。

所谓"单页最多一万六千行"，说的是字节天花板：一页就 16384 个字节，一行哪怕只占 1 字节，上限也就是 1.6 万条。它来自页的大小，不是实测容量。**页的大小决定了任何索引的单页容量都在万级以下**，这才是这个数字的意义。

扇出也顺着算：

- 非叶子页的每条记录 = 5（头）+ 8（BIGINT 主键）+ 4（子页号）= 17 字节，16256 / 17 ≈ 956，扇出约 950。
- 叶子页按 150 字节行宽装 100 行。
- 三层树：950 × 950 × 100 ≈ 9000 万行。
- 行宽涨到 1KB（一页 16 行），三层就是 950 × 950 × 16 ≈ 1400 万行，取整就是常说的"两千万"。
- 再加一层，直接到百亿级。

**结论很直接：行宽每翻一倍，树的容量就减半。** 大宽表的代价不只在 IO，它在树的层数上就把你提前送到了四层。

## 3.4 行格式：四种格式与三个隐藏列

| 格式 | 记录头 | 变长列处理 | 溢出方式 | 默认场景 |
|---|---|---|---|---|
| REDUNDANT | 6 字节 | 字段长度偏移列表 | 768 字节前缀 + 20 字节指针 | 5.0 及更早 |
| COMPACT | 5 字节 | 变长长度列表（逆序） | 768 字节前缀 + 20 字节指针 | `[5.6]` 默认 |
| DYNAMIC | 5 字节 | 变长长度列表（逆序） | 整列 off-page，只留 20 字节指针 | 8.0 默认（`[5.7.9+]`） |
| COMPRESSED | 5 字节 | 变长长度列表（逆序） | 同 DYNAMIC，页级 zlib 压缩 | 需显式 `KEY_BLOCK_SIZE` |

COMPACT 及之后的格式，记录头 5 字节里塞了这些：删除标记（1 bit）、最小记录标记（1 bit）、`n_owned`（4 bit，这一组有几条记录）、heap_no（13 bit）、记录类型（3 bit）、`next_record`（2 字节）。`n_owned` 就是 Page Directory 能工作的依据——它是"目录槽"和"记录"之间的粘合剂。

变长长度列表按列逆序排列，NULL 位图按可空列占 1 bit，两者都挤在 5 字节记录头前面。这些布局在 `information_schema` 里一律看不到——它们是页内的二进制约定，不是 SQL 语义的一部分。你要估行宽，只能按"长度列表 + 位图 + 记录头 + 隐藏列 + 各列"逐项加，没有捷径。

三个隐藏列，每行都要付账：

- `DB_TRX_ID`（6 字节）：最后一个修改这行的事务 id。
- `DB_ROLL_PTR`（7 字节）：指向 undo 里的上一个版本，MVCC 版本链的入口（见第 5 章）。
- `DB_ROW_ID`（6 字节）：**只有表既没有主键、也没有唯一非空索引时才存在**。有主键的表没有这一列。

前两个永远存在，所以每行固定多 13 字节。一亿行就是 1.3GB，跟业务字段一点关系没有。第三个是"无主键表"问题的物理起点：InnoDB 得自己造一个 6 字节的全局自增 id，写入全落在树的右端，而且复制和 MGR 都可能因为定位不到唯一行而出问题（见第 30 章）。

## 3.5 行溢出：20 字节指针与"一页至少两行"

InnoDB 有一条硬规则：**一页至少要放得下两行**。16KB 页下，单行上限约 8126 字节。超过这个长度，变长列就得挪出去。

- COMPACT / REDUNDANT：行内保留前 768 字节，剩下放到 off-page 的 BLOB 页，行内留 20 字节指针。
- DYNAMIC：干脆一个字节都不留，整列 off-page，行内只有 20 字节指针。

差别在哪？一张有 `VARCHAR(2000)` 备注列的表，`SELECT id FROM t` 根本不需要备注列。COMPACT 下，主键页里仍然躺着 768 字节的备注前缀，一页能装的记录数被这些前缀吃掉；DYNAMIC 下主键页是干净的，备注页可以完全不读。**同样的表、同样的查询，行格式决定了你要读几个页。**

这正是 5.7.9 起把 `innodb_default_row_format` 改成 DYNAMIC 的实际收益，也是"大字段拆表"这条经验的物理依据：溢出页是独立分配的 BLOB 页，不参与 B+ 树，物理上不和主键页相邻，每读一次就是一次随机 IO。`SELECT *` 在宽表上慢，慢的不是行数，是每行多出来的那几次跳转。

`innodb_strict_mode=ON`（8.0 默认）时，行太大会直接报 `ERROR 1118 (42000): Row size too large`，而不是悄悄截断。

页越小，单行上限也越小：4KB 页时上限只有约 2000 字节。**一张在 16KB 实例上建得好好的宽表，迁到 4KB 页的实例上可能直接建不起来**——这也是 `innodb_page_size` 必须全链路一致的原因之一。

## 3.6 页分裂与页合并：主键顺序的物理代价

![图 3-3 顺序插入与随机插入的分裂差异](images/ch03-fig3.svg)

插入的路径是：定位到目标页 → Free Space 够就直接写 → 不够就分裂。

**顺序插入（自增主键）走的是右分裂。** Page Header 里 `PAGE_DIRECTION` 标记为向右、`PAGE_LAST_INSERT` 指向页尾时，InnoDB 知道"这一页只会往右长"，于是从空闲区取一个新页接在后面，新记录写进新页，原页一条都不动。原页保持在 15/16 左右——分裂的触发条件是"这条记录塞不下"，所以页总是被填到接近满为止，剩下的那一点就是最后一条记录没塞进去的尺寸。

**随机插入（UUID、无序业务键）走的是 50/50 分裂。** 页满了，把一半记录搬到新页，两条链重新串，Page Directory 重建。新页从空闲区取，通常不和原页物理相邻。

后果是三层叠加的：

1. **空间翻倍。** 填充率从 93% 掉到 50%，同样的行数占近两倍页。
2. **写放大。** 一次分裂 = 两个页变脏 + 两条 redo + 目录重建，而不是一条 INSERT 的代价。
3. **扫描退化。** 逻辑上相邻的页物理上不相邻，范围扫描从顺序 IO 变成随机 IO。

但别把话说死：**自增主键也不是免费的**。所有插入都落在最右侧那一个页上，高并发写入时这一页的 latch 就是热点；`innodb_autoinc_lock_mode=2` 解决的是自增值的分配争用，解决不了页内竞争。分库分表之后常见的"步长法"或号段模式，本质就是把这条热点摊开（见第 30 章）。选主键是在"页分裂"和"写热点"之间做取舍，不是在"好"与"坏"之间选。

删除方向的机制对称但更消极：记录被标 `deleted_flag=1`，挂进 `PAGE_FREE` 链，空间记在 `PAGE_GARBAGE`，只能被**同一页**的新记录复用。当页的填充率低于 `MERGE_THRESHOLD`（默认 50%）时，InnoDB 尝试和相邻页合并。但合并是"尝试"：相邻页往往也半满，合起来仍然超过阈值；即使能合，合并本身要改两条链表、动两个页。所以 `index_page_merge_successes` 长期远小于 `index_page_merge_attempts` 是常态，不是故障。

`MERGE_THRESHOLD` 可以按索引设置：

```sql
ALTER TABLE bill_detail
  ADD INDEX idx_bill_date (bill_date) COMMENT 'MERGE_THRESHOLD=40';
```

调低到 40 意味着"更晚才合并"：省 CPU，费空间。这是唯一能在线调的旋钮，但它改变不了已经产生的空洞。

碎片率有两个口径，别混用：

- **页内碎片**：`PAGE_GARBAGE / 页大小`，删除留下的洞。只能靠重建消除。
- **页间碎片**：`Data_free / (Data_length + Index_length + Data_free)`，`SHOW TABLE STATUS` 直接给。它统计的是"整页都空了"的部分。

## 3.7 表空间回收：三条路，三种代价

| 操作 | 机制 | 额外磁盘 | 锁 | 可回滚 |
|---|---|---|---|---|
| `DELETE` | 标记删除，页内复用 | 0 | 行锁 | 是 |
| `TRUNCATE` | 丢弃并重建表空间 | 0 | MDL 排他，等所有事务 | 否（DDL 隐式提交） |
| `ALTER TABLE ... ENGINE=InnoDB` | 重建表 + 重建全部索引 | 约 1 倍 | Online DDL，首尾短锁 | 否 |

`TRUNCATE` 之所以立刻还盘，是因为它根本不是"删行"，是换了一个新文件：旧的丢掉，新的按初始大小（112KB）建。它在文件系统层面立刻可见。它同时会把 `AUTO_INCREMENT` 重置回 1，`DELETE` 不会——这两者在业务上的差别，经常比空间本身更致命。

`DELETE` 之后文件不缩，也没有任何参数能让它自动缩。purge 线程把整页清空后，页会进入表空间的空闲区列表，可以被这张表的新数据复用，但文件本身不变。

`ALTER TABLE ... ENGINE=InnoDB` 是保留数据的重建方式，8.0 里走 `ALGORITHM=INPLACE`，允许并发 DML，但**仍然需要一倍额外磁盘**，而且要重建所有二级索引。`OPTIMIZE TABLE` 对 InnoDB 就是 `ALTER TABLE ... FORCE`，效果一样，顺带刷新统计信息，代价一样大。

所以 3.0 里的死局只有三种破法：

- 先扩盘，再重建（最稳，代价是钱和一次扩容窗口）。
- 用 `gh-ost` / `pt-online-schema-change` 在另一台实例上重建，再切流量（见第 46 章）。
- 如果历史数据本来就要归档，直接 `DROP PARTITION` 或按分区重建，比 `DELETE` 干净得多（见第 32 章）。

## 3.8 关键结论

1. **InnoDB 的空间单位是页，不是行。** `DELETE` 只释放页内槽位（`PAGE_FREE` / `PAGE_GARBAGE`），页仍属于这张表；文件只在重建时缩小。
2. **区管分配、页管 IO、行管语义。** 一个区固定 1MB，一页固定 16KB（可配但不可改），这三个数字决定了容量估算和 IO 形态。
3. **页内查找是"目录二分 + 组内线性"，约十几次比较。** 这让 B+ 树的每一层下降都是常数级，也是三层树能装下千万到上亿行的前提。
4. **扇出约 950，叶子页装的是"行宽决定的条数"。** 150 字节行宽下三层约 9000 万行，1KB 行宽下只剩 1400 万——宽表先用层数惩罚你。
5. **主键顺序决定填充率。** 顺序插入是右分裂、填充率约 93%；随机插入是 50/50、填充率约 50%，同样的数据占近两倍空间，且范围扫描退化为随机 IO。
6. **能还盘的只有重建。** `TRUNCATE`、`ALTER TABLE ... ENGINE=InnoDB`、`DROP`，代价是额外磁盘、IO 与 MDL，没有第四条路。

## 3.9 实验验证

### 实验一：看清一张表的页数与空页

```sql
SELECT NAME, NUM_ROWS, CLUST_INDEX_SIZE, OTHER_INDEX_SIZE
FROM information_schema.INNODB_TABLESTATS
WHERE NAME = 'shop/bill_detail';
```

```text
-- 输出形态（未实跑，字段含义以此为准）
NAME              NUM_ROWS   CLUST_INDEX_SIZE   OTHER_INDEX_SIZE
shop/bill_detail  120000000            1200000             380000
```

`NUM_ROWS` 是采样估算，不是精确值，别拿它对账。`CLUST_INDEX_SIZE` 的单位是页，乘以 16384 就是聚簇索引的逻辑大小。拿它和 `Data_length` 对一下，能判断统计信息是否已经过期。

### 实验二：`DELETE` 不还盘，`TRUNCATE` 还盘

```sql
-- 删除前
SELECT FILE_SIZE, ALLOCATED_SIZE FROM information_schema.INNODB_TABLESPACES
WHERE NAME = 'shop/bill_detail_archive';

DELETE FROM bill_detail_archive WHERE bill_date < '2025-01-01';

-- 删除后再查：两个值大概率不变，Data_free 变大
-- 再执行：
TRUNCATE TABLE bill_detail_archive;
-- 再查：FILE_SIZE 回到 114688（112KB）
```

这条实验比任何解释都直接：同一个文件，`DELETE` 之后一个字节没少，`TRUNCATE` 之后立刻回到初始大小。

### 实验三：数一数页分裂

```sql
SET GLOBAL innodb_monitor_enable = 'index_page_splits';
SET GLOBAL innodb_monitor_enable = 'index_page_merge_attempts';
SET GLOBAL innodb_monitor_enable = 'index_page_merge_successes';

-- 两张结构相同、只有主键不同的表，各插 100 万行后
SELECT NAME, COUNT FROM information_schema.INNODB_METRICS
WHERE NAME IN ('index_page_splits','index_page_merge_attempts',
               'index_page_merge_successes');
```

```text
-- 输出形态（未实跑，字段含义以此为准）
NAME                        COUNT
index_page_splits           自增表约为 UUID 表的 1/2
index_page_merge_attempts   非 0
index_page_merge_successes  长期远小于 attempts
```

第三行是重点：合并经常"尝试了但不成功"，这是设计使然，不是 bug。

### 实验四：肉眼看页内空洞

MySQL 自身没有任何解析 `.ibd` 页面的命令。`innodb_page_info` 是社区工具（`innodb_ruby` / `pyinnodb` 一类），不是内置的；同类的还有 `innodb_ruby` 的 `innodb_space`：

```bash
innodb_space -s ibdata1 -T shop/bill_detail -p 4 page-illustrate
```

```text
-- 输出形态（未实跑）
page 4: INDEX, leaf, 46 records, garbage 1204 bytes
```

`garbage` 就是页内被删除但没复用的字节。连续看几十个页，如果 `garbage` 普遍上千、填充率普遍在 50% 上下，说明这张表该重建了。

## 3.10 常见误区

⚠️ **"`DELETE` 能释放磁盘空间"**
它只释放页内槽位和整页的空闲标记，文件不变。要还盘只有重建。真正该问的是"这张表的数据还要不要"，如果不要，`DROP PARTITION` 比 `DELETE` 快几个数量级，而且立刻还盘。

⚠️ **"`OPTIMIZE TABLE` 随时可以做"**
它等于重建整表：一倍额外磁盘、全表 IO、重建全部二级索引，全程占着 MDL——尾部那次排他会把后面所有查询排在你身后（见第 18 章）。几百 GB 的表在网络盘上做一次，足够把复制延迟推到小时级。上线前先算磁盘余量，线上优先用 gh-ost 或 pt-osc。

⚠️ **"行格式只影响存储，不影响性能"**
COMPACT 的 768 字节前缀会让"只查主键"的查询也把备注前缀读进 Buffer Pool，一页能装的记录数直接少一截。8.0 默认 DYNAMIC 不是随手改的默认值。

⚠️ **"UUID 主键只是多占 16 字节"**
真正的代价在写入路径：随机分布 → 50/50 分裂 → 填充率 50% → 同样行数占两倍页 → 每次分裂多写一个页和一条 redo。二级索引还要额外存这 16 字节的主键值。

⚠️ **"表空间文件大，说明数据多"**
可能全是碎片。`Data_length` 和 `Data_free` 要一起看，`Data_free` 占比超过三成才谈得上"需要重建"；低于这个数，重建的收益还不如扩一块盘。

⚠️ **"把 `innodb_page_size` 调大能提升性能"**
它只能在初始化时设定，改它等于重建实例；而且页越大，单页刷盘的代价越大、崩溃恢复越慢、备份必须同页大小。收益主要在特定的大行宽场景，通用 OLTP 里 16KB 是长期验证过的平衡点。

## 3.11 生产 Checklist

建表与评审时逐条过：

- [ ] 主键是否单调递增？如果是 UUID，有没有做时间有序的变体（UUIDv7 / 雪花）？
- [ ] 行宽估算过吗？是否有可能超过 8126 字节的行（多个 `VARCHAR(2000)`、JSON、长文本）？
- [ ] 大字段是否拆到了独立表？行格式确认是 DYNAMIC 吗？
- [ ] 有没有无主键表？`information_schema.INNODB_INDEXES` 里聚簇索引名是 `GEN_CLUST_INDEX` 的就是（见第 30 章）。
- [ ] 历史数据清理方案是 `DELETE` 还是 `DROP PARTITION`？如果是 `DELETE`，容量规划里有没有把"文件不会缩"算进去？
- [ ] `Data_free` 占比是否超过 30%？超了之后的重建窗口、额外磁盘、回滚方案是什么？
- [ ] `innodb_page_size` 与备份工具、从库、克隆源是否一致？
- [ ] `innodb_file_per_table` 是 `ON` 吗？（`OFF` 时单表无法独立回收）

## 3.12 延伸

- **上一章**：Buffer Pool 管的是这些页在内存里的驻留与淘汰，页的结构决定了它怎么被换入换出。
- **下一章**：redo log 记录的是"哪个页的哪个偏移被改了"，页的物理结构是 redo 能被重放的坐标系。
- **关联章节**：第 5 章（`DB_ROLL_PTR` 与版本链）、第 7 章（File Trailer 与 doublewrite）、第 8 章（扇出与索引组织表）、第 30 章（无主键表的 `DB_ROW_ID`）、第 32 章（分区表的快速回收）、第 46 章（重建与在线 DDL）。
- **面试追问**：
  - "一页 16KB，能存多少行？" → 先问行宽。150 字节约 100 行；只算主键 26 字节，上限 625 行；1.6 万是字节天花板，不是容量。
  - "为什么主键要用自增？" → 右分裂只追加不搬移，填充率 93%；随机主键 50/50 分裂，同样数据占近两倍空间。
  - "`DELETE` 之后磁盘为什么没降？" → 空间以页为单位分配，删除只改页内标记，文件不缩；只有重建才还盘。
- **官方文档**：`InnoDB File Space Management`、`InnoDB Page Structure`、`InnoDB Row Formats`、`innodb_page_size`。
