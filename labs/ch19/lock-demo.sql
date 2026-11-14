-- 第 19 章加锁实验：非唯一索引等值命中，为什么会锁三段
-- 开两个终端：A 段执行完不要提交，B 段读锁清单，最后回 A 段 ROLLBACK
CREATE DATABASE IF NOT EXISTS lab19;
USE lab19;
DROP TABLE IF EXISTS t_lock;
CREATE TABLE t_lock (
  id  BIGINT      PRIMARY KEY,
  c   INT         NOT NULL,
  pad VARCHAR(16) NOT NULL,
  KEY idx_c (c)
) ENGINE=InnoDB;
-- id = 4 故意留空：换成 WHERE id = 4 FOR UPDATE 可验证"唯一索引未命中锁间隙"
INSERT INTO t_lock VALUES
  (1, 5, 'a'), (2, 10, 'b'), (3, 15, 'c'),
  (5, 20, 'd'), (6, 25, 'e'), (7, 30, 'f');
-- ============ 会话 A：制造锁，执行到这里停住，不要提交 ============
SET SESSION transaction_isolation = 'REPEATABLE-READ';
BEGIN;
SELECT * FROM t_lock WHERE c = 15 FOR UPDATE;
-- ============ 会话 B：读锁清单 ============
SELECT INDEX_NAME, LOCK_MODE, LOCK_STATUS, LOCK_DATA
FROM performance_schema.data_locks
WHERE OBJECT_SCHEMA = 'lab19' AND OBJECT_NAME = 't_lock'
ORDER BY INDEX_NAME, LOCK_DATA;
-- 预期三行 RECORD（另加一行 TABLE/IX，LOCK_DATA 为 NULL）：
--   idx_c X GRANTED 15, 3 / idx_c X,GAP GRANTED 20, 5 / PRIMARY X,REC_NOT_GAP GRANTED 3
-- 会话 B 再执行 SELECT * FROM t_lock WHERE c = 15 FOR UPDATE; 会一直等到 A 回滚（1205）
-- ============ 会话 A：收尾。回滚后 B 立刻返回 ============
ROLLBACK;
