-- 第 41 章案例五：一个 Sleep 连接堵住整张表。三个终端，全在主库。
-- 关键点：C 既没改表也没发 DDL，照样被卡住——MDL 队列写优先。
-- ============ 会话 A：开事务读一次，挂着不提交 ============
USE shop;
BEGIN;
SELECT COUNT(*) FROM order_item WHERE order_id = 1;
-- ============ 会话 B：加索引，卡在 MDL 队列 ============
ALTER TABLE order_item ADD INDEX idx_created_probe (sku_id, id);
-- 预期：State = Waiting for table metadata lock，lock_wait_timeout 默认一年
-- ============ 会话 C：普通 SELECT 也被卡住 ============
SELECT * FROM order_item WHERE order_id = 2;
-- ============ 会话 C：找持有者（附录 D3 的定向版） ============
SELECT t.PROCESSLIST_ID AS conn, t.PROCESSLIST_TIME AS idle_s, t.PROCESSLIST_COMMAND AS cmd,
       m.LOCK_TYPE, m.LOCK_STATUS, m.LOCK_DURATION
FROM performance_schema.metadata_locks m
JOIN performance_schema.threads t ON t.THREAD_ID = m.OWNER_THREAD_ID
WHERE m.OBJECT_SCHEMA = 'shop' AND m.OBJECT_NAME = 'order_item'
ORDER BY m.LOCK_STATUS DESC, t.PROCESSLIST_TIME DESC;
-- 预期：SHARED_READ/GRANTED/TRANSACTION 是 A（cmd=Sleep），EXCLUSIVE/PENDING 是 B
-- ============ 会话 C：核实不是大事务，再杀 GRANTED 的那个 ============
SELECT t.PROCESSLIST_ID INTO @holder
FROM performance_schema.metadata_locks m
JOIN performance_schema.threads t ON t.THREAD_ID = m.OWNER_THREAD_ID
WHERE m.OBJECT_SCHEMA = 'shop' AND m.OBJECT_NAME = 'order_item'
  AND m.LOCK_TYPE = 'SHARED_READ' AND m.LOCK_STATUS = 'GRANTED'
  AND m.LOCK_DURATION = 'TRANSACTION' LIMIT 1;
SELECT @holder AS holder_conn, trx_state, trx_rows_modified
FROM information_schema.innodb_trx WHERE trx_mysql_thread_id = @holder;
SELECT CONCAT('KILL ', @holder, ';') AS kill_stmt;
-- 执行生成的那条 KILL；之后 B 的 DDL 继续跑，C 的查询立即返回
