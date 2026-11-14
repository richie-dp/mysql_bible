# labs：附录 G 的实验环境

一台机器起 1 主 2 从（MySQL 8.0），加一个 5.7 单实例做版本对比。复制关系不在 compose 里配——从库要等主库有 GTID 才能自动定位，启动顺序保证不了这件事。

## 三分钟上手

```bash
git clone <本书仓库> mysql_bible && cd mysql_bible

# 1. 起 8.0 一主两从（首次会拉镜像）
docker compose -f labs/docker-compose.yml up -d

# 2. 等三个容器都变成 healthy（约 30~60 秒）
docker compose -f labs/docker-compose.yml ps

# 3. 在主库建复制账号。用默认的 caching_sha2_password，
#    从库靠 GET_SOURCE_PUBLIC_KEY=1 取公钥，不依赖已废弃的 mysql_native_password
docker exec -e MYSQL_PWD=labpass mysql-master mysql -uroot -e "
  CREATE USER 'repl'@'%' IDENTIFIED BY 'replpass';
  GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';"

# 4. 两个从库各配一次（GTID 自动定位，不用记 binlog 位点）
for h in mysql-replica1 mysql-replica2; do
  docker exec -e MYSQL_PWD=labpass "$h" mysql -uroot -e "
    CHANGE REPLICATION SOURCE TO
      SOURCE_HOST='mysql-master', SOURCE_PORT=3306,
      SOURCE_USER='repl', SOURCE_PASSWORD='replpass',
      SOURCE_AUTO_POSITION=1, GET_SOURCE_PUBLIC_KEY=1;
    START REPLICA;
    SET PERSIST read_only=ON, super_read_only=ON;"
done

# 5. 确认两个 Running 都是 Yes
docker exec -e MYSQL_PWD=labpass mysql-replica1 mysql -uroot -e "SHOW REPLICA STATUS\G" \
  | egrep 'Replica_IO_Running|Replica_SQL_Running|Seconds_Behind_Source'

# 6. 建表 + 小数据（2 万单，秒级）
docker exec -i -e MYSQL_PWD=labpass mysql-master mysql -uroot < labs/seed/01-schema.sql
docker exec -i -e MYSQL_PWD=labpass mysql-master mysql -uroot < labs/seed/02-seed-small.sql
```

`SET PERSIST super_read_only=ON` 没有写进 `conf/replica*.cnf`：docker-entrypoint 首次启动要用 root 改 `mysql.user`，`super_read_only` 会让它报 `ERROR 1290` 直接退出（附录 G 的 G.5 有完整解释）。`SET PERSIST` 落在 `mysqld-auto.cnf`，重启后仍在，效果等同写配置文件。

数据导入后等一秒，从库会跟上。验证：

```bash
docker exec -e MYSQL_PWD=labpass mysql-replica1 mysql -uroot -e "SELECT COUNT(*) FROM shop.order_main;"
```

`01-schema.sql` 只跑一次：它没有 `CREATE TABLE IF NOT EXISTS`，重跑会报 1050。要推倒重来：

```bash
docker exec -e MYSQL_PWD=labpass mysql-master mysql -uroot -e "DROP DATABASE shop; CREATE DATABASE shop;"
docker exec -i -e MYSQL_PWD=labpass mysql-master mysql -uroot < labs/seed/01-schema.sql
```

## 章节 → 脚本映射

| 章节 | 实验目的 | 脚本 / SQL 来源 | 预期现象 |
|---|---|---|---|
| Ch1 | 回表次数、提交不等于落盘 | `ch01/seed.sql`，再跑正文 1.6 的 SQL | `Handler_read_key` 在覆盖索引时不随行数增长 |
| Ch2 | buffer pool 命中率、池里是谁 | 附录 D24、D25 | 求差后命中率才有意义 |
| Ch3 | 表空间与文件位置 | 附录 D18、D21 | 独立表空间每表一个 `.ibd` |
| Ch4 | redo 生成速率与 checkpoint | 附录 D27 | 年龄 = LSN − Last checkpoint |
| Ch5 | undo 与长事务 | 附录 D22、D5 | undo 只增不减，先查长事务 |
| Ch6 | binlog 与 XID | 容器内 `mysqlbinlog -vv` | 每个事务以 `Xid = N` 收尾 |
| Ch9 | 索引选择性与回表 | 附录 D16 + `EXPLAIN` | 同一条件换列，`rows` 差一个量级 |
| Ch10 | 统计信息陈旧导致计划突变 | 附录 D39 + `seed/02` 后 `ANALYZE` | `last_update` 早于导入时间 |
| Ch11 | `EXPLAIN ANALYZE` 估算偏差 | 附录 D13 | `actual rows` 与 `estimated` 差一个量级 |
| Ch17 | RR 下快照读与当前读 | 两个会话手写，见正文 1.4 | 同一事务两次 SELECT 结果不同步 |
| Ch18 | 锁类型与锁等待链 | 附录 D1、D2 | `LOCK_MODE` 里有没有 `GAP` |
| Ch19 | 非唯一索引锁三段 | `ch19/lock-demo.sql` | 2 行 `idx_c` + 1 行 `PRIMARY` |
| Ch20 | 死锁现场 | `ch19/lock-demo.sql` 改成交叉顺序 | `LATEST DETECTED DEADLOCK` |
| Ch21 | 长事务与回滚成本 | 附录 D5、D6 | `trx_rows_modified` 决定回滚时长 |
| Ch22 | 复制延迟三段分解 | 附录 D35、D36 | `net_ms` 与 `apply_ms` 分开看 |
| Ch25 | 并行回放退化 | `ch41/case-03-no-pk-lag.sql` | 只有一个 worker 在动 |
| Ch30 | 主键与随机写入 | 附录 D17、D19 | 无主键表清单 |
| Ch38 | 慢查询与 digest | 附录 D8、D9 | 总耗时高 vs 单次高 |
| Ch41 | 三个经典误判 | `ch41/case-01/02/03`，索引见 `ch41/case-md.md` | 见各文件开头的"预期" |
| Ch49 | 超卖与条件更新 | `seed/01-schema.sql` + 正文 SQL | `affected_rows = 0` 就是没货 |
| Ch51 | 千万行容量与造数 | `seed/03-seed-large.py --rows 10000000` | 生成数 GB 的 `.sql` |
| Ch52 | KILL 与回滚 | `ch52/kill-long-trx.sql` | 回滚期间锁不释放 |

其余章节没有专属脚本，用附录 D 的 SQL 直接跑；表结构统一在 `seed/01-schema.sql`。

## 目录与端口

| 路径 | 内容 |
|---|---|
| `docker-compose.yml` | 8.0 一主两从，端口 3306 / 3307 / 3308 |
| `docker-compose-57.yml` | 5.7 单实例，端口 3309，`platform: linux/amd64` |
| `conf/master.cnf` | `server-id=1`、ROW binlog、GTID、慢日志 |
| `conf/replica1.cnf` / `replica2.cnf` | `server-id=2/3`、`log_replica_updates`、并行回放 |
| `conf/57.cnf` | 5.7 对比用，字符集显式写 utf8mb4 |
| `seed/01-schema.sql` | 六张表：订单、明细、库存、库存流水、账户、账户流水 |
| `seed/02-seed-small.sql` | 2 万单 / 4 万明细 / 2000 SKU，秒级 |
| `seed/03-seed-large.py` | 千万行生成器，标准库，输出 INSERT 流 |
| `seed/04-seed-skew.sql` | 10% 订单压到 SKU 8842 与商户 1000 |
| `ch01/` `ch19/` `ch41/` `ch52/` | 对应章节的可执行脚本 |

连接参数统一：用户 `root`，密码 `labpass`，库 `shop`。从库用 `127.0.0.1:3307` / `3308`。

## 5.7 对比实例

```bash
docker compose -f labs/docker-compose-57.yml up -d
docker exec -e MYSQL_PWD=labpass mysql-57 mysql -uroot -e "SELECT VERSION();"
```

Apple Silicon 上这个容器走 Rosetta 模拟，启动比 8.0 慢几倍，只适合跑单条 SQL 对比，不要拿它做性能结论。

## 清理

```bash
docker compose -f labs/docker-compose.yml down       # 停容器，保留数据
docker compose -f labs/docker-compose.yml down -v    # 连数据卷一起删，下次是空库
```

`down -v` 之后要重新走一遍建复制账号与 `CHANGE REPLICATION SOURCE TO`。
