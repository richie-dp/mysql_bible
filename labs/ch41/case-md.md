# 第 41 章案例复现索引

三个案例，三份 SQL，都在 `labs/` 起的环境里跑。每个文件开头写了"开几个终端、谁先执行、预期看到什么"，这里只说怎么排、跑完看哪里。

## 先决条件

| 项 | 要求 |
|---|---|
| 环境 | `docker compose up -d` 三个容器 healthy，复制已按 `labs/README.md` 配好 |
| 数据 | `seed/01-schema.sql` 已导入；案例一、二用 02 的小数据就够，案例四建议 02 + 04 |
| 权限 | 用 `root` 连接；`metadata_locks`、`innodb_trx` 需要 `PROCESS` 权限 |
| 端口 | 主库 `127.0.0.1:3306`，从库 `127.0.0.1:3307` / `3308` |

## 三个案例

### 案例一：连接数被打满（`case-01-connections.sql`）

**要复现的误判**：看到 `Threads_connected` 贴顶就扩容。

**脚本做的事**：把 `max_connections` 压到 80，用 bash 循环开 70 个 `SELECT SLEEP(900)` 的连接，再按来源聚合。看三件事——Sleep 连接数、`Threads_running`、`Aborted_clients`。

**判据**：`Sleep` 多 + `running` 个位数 + `Aborted_clients` 几乎不动 = 池子漏了；三者任一不成立，才轮到"量真的涨了"。对应附录 D29、D30、D31。

### 案例五：全站卡在 MDL（`case-02-mdl.sql`）

**要复现的误判**：看到 `Waiting for table metadata lock` 就以为"等 DDL 跑完"。

**脚本做的事**：会话 A 开事务读一次 `order_item` 不提交；B 发 `ALTER TABLE ... ADD INDEX`；C 发普通 `SELECT`。三个会话的状态在 `performance_schema.metadata_locks` 里同时可见。

**判据**：`GRANTED` 挂在一个 `Command = Sleep` 的连接上，`PENDING` 的是 DDL——DDL 自己也在排队，没有任何人在"跑"。杀 `GRANTED` 的那个连接，不是杀 DDL。对应附录 D3、D4。

### 案例四：无主键表的复制延迟（`case-03-no-pk-lag.sql`）

**要复现的误判**：延迟上去就给从库加 CPU。

**脚本做的事**：主库一个事务往无主键的 `stock_flow` 写 20 万行；从库看 `SHOW REPLICA STATUS` 与 `replication_applier_status_by_worker`。

**判据**：`Replica_SQL_Running_State` 出现 `Waiting for dependent transaction to commit`，只有一个 worker 的 `applying_ms` 在涨——瓶颈是依赖判定，不是算力。对应附录 D36、D37，机制见第 25 章。

## 跑完必做

```sql
-- 恢复被改过的全局参数
SET GLOBAL max_connections = 500;
UPDATE shop.stock SET qty = 1000 WHERE sku_id = 8842;
```

```bash
# 案例二加的探针索引，留着会让后面的执行计划实验失真
docker exec -e MYSQL_PWD=labpass mysql-master \
  mysql -uroot -e "ALTER TABLE shop.order_item DROP INDEX idx_created_probe;"
```

`case-03` 的 20 万行流水会一直留在主库并复制到从库，重跑前先 `TRUNCATE shop.stock_flow`（主库执行，从库会跟上）。
