-- 第 41 章案例四：无主键表 + 大事务 → 从库回放退化。主库跑 1~2 段，从库跑 3~4 段。
-- 前提：复制已通，replica_parallel_workers = 4
-- ============ 主库 1：写集依赖追踪（8.0 实测默认 COMMIT_ORDER） ============
SELECT @@binlog_transaction_dependency_tracking AS dep_tracking;
-- ============ 主库 2：一个事务写 20 万行无主键流水 ============
SET SESSION cte_max_recursion_depth = 300000;
USE shop;
BEGIN;
INSERT INTO stock_flow (sku_id, biz_no, direction, qty, status)
WITH RECURSIVE seq(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 200000)
SELECT 8800 + (n % 2000), CONCAT('LAG2026', LPAD(n, 10, '0')), 1, 1, 'OUT' FROM seq;
COMMIT;
-- stock_flow 无主键：并行回放拿不到可用的键，只能按提交顺序来；再叠一个 20 万行的事务，
-- 单个 worker 更搬不动。笔记本上是"延迟跳几秒、Exec pos 停住再跳"，放大十倍才像案例。
-- ============ 从库 1：看回放状态 ============
SHOW REPLICA STATUS\G
-- 看四列：两个 Running=Yes、Seconds_Behind_Source 上升、
--         Replica_SQL_Running_State = Waiting for dependent transaction to commit
-- ============ 从库 2：定位到 worker（附录 D37） ============
SELECT WORKER_ID, SERVICE_STATE,
       TIMESTAMPDIFF(MICROSECOND, APPLYING_TRANSACTION_START_APPLY_TIMESTAMP, NOW(6)) / 1000
         AS applying_ms
FROM performance_schema.replication_applier_status_by_worker
ORDER BY applying_ms DESC;
-- 预期：只有一个 worker 的 applying_ms 在涨，其余闲着等它
-- 收尾（仅实验）：给 stock_flow 补主键后重跑，延迟峰值会低一截
-- ALTER TABLE shop.stock_flow ADD COLUMN id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY FIRST;
