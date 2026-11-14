-- 第 52 章实验二：KILL 之后锁不会立刻释放。三个终端，全在主库（3306）。
-- B 的等待上限调大，否则默认 50 秒就自己报 1205 了。
USE shop;
UPDATE stock SET qty = 1000 WHERE sku_id = 8842;
-- ============ 会话 A：改 2 万行，制造"回滚也要花时间"的事务 ============
BEGIN;
UPDATE order_main SET after_sale = 1 - after_sale WHERE id <= 20000;
-- 不要提交，也不要断开
-- ============ 会话 B：同一行，开始等锁 ============
SET SESSION innodb_lock_wait_timeout = 300;
BEGIN;
UPDATE order_main SET after_sale = 1 - after_sale WHERE id = 1;
-- 预期：State = updating，一直等到 A 结束
-- ============ 会话 C：先取证，再决定杀谁 ============
SELECT trx_id, trx_state, trx_rows_modified, trx_started,
       trx_mysql_thread_id AS conn, LEFT(trx_query, 40) AS query
FROM information_schema.innodb_trx ORDER BY trx_started;
-- A：trx_rows_modified 约 2 万、RUNNING；B：LOCK WAIT
SET @a = (SELECT trx_mysql_thread_id FROM information_schema.innodb_trx
          WHERE trx_rows_modified > 10000 ORDER BY trx_started LIMIT 1);
SELECT @a AS victim_conn, CONCAT('KILL ', @a, ';') AS stmt;
-- ============ 会话 C：两种 KILL 的区别，按顺序各做一次 ============
-- 1) KILL QUERY：只中断当前语句，事务还在，锁不放，B 继续等
-- 2) KILL：断开连接并触发回滚，回滚期间 trx_state = ROLLBACK
SELECT trx_state, trx_rows_modified FROM information_schema.innodb_trx;
-- 预期：ROLLBACK 期间锁不释放；2 万行回滚结束后 B 才拿到锁
-- 收尾：B 执行 ROLLBACK;
