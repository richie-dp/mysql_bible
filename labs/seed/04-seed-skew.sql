-- 倾斜数据：在 02 之上追加，制造"热 SKU + 热商户 + 热账户"
-- 均匀分布下，行锁永远不冲突、执行计划永远不变——第 41 章的案例二和案例六都复现不出来。
SET SESSION cte_max_recursion_depth = 100000;
USE shop;

-- 1) 2000 笔订单（占 2 万单的 10%）全部落在商户 1000 与 SKU 8842 上
INSERT IGNORE INTO order_main
  (order_no, merchant_id, buyer_id, status, pay_amount, created_at, paid_at)
WITH RECURSIVE seq(n) AS (
  SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 2000
)
SELECT CONCAT('HOT2026', LPAD(n, 11, '0')), 1000, 100000 + (n % 5000), 20, 29.90,
       TIMESTAMP('2026-10-01 00:00:00') + INTERVAL (n % 3) DAY
         + INTERVAL (n * 13 % 3600) SECOND,
       TIMESTAMP('2026-10-01 00:00:00') + INTERVAL (n % 3) DAY
         + INTERVAL (n * 13 % 3600) SECOND + INTERVAL 1 MINUTE
FROM seq;

-- 2) 这批订单的明细全部指向爆款 SKU；uk_order_line 保证重复执行不会插两遍
INSERT IGNORE INTO order_item (order_id, line_no, sku_id, sku_name, unit_price, qty)
SELECT id, 1, 8842, 'SKU-8842', 29.90, 1
FROM order_main WHERE order_no LIKE 'HOT2026%';

-- 3) 爆款库存只剩 50 件：第 49 章的"条件更新"实验要靠这个数制造竞争
UPDATE stock SET qty = 50 WHERE sku_id = 8842;

-- 4) 账户 1（商户 1000）吃下 2 万条流水：单账户热点，索引选择性极差
INSERT IGNORE INTO account_flow (account_id, biz_no, direction, amount, balance_after)
WITH RECURSIVE seq(n) AS (
  SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 20000
)
SELECT 1, CONCAT('HF2026', LPAD(n, 11, '0')), 1, 1.00, 100000.00 FROM seq;

-- 5) 确认倾斜生效：第一行应该是 8842，且远高于第二行
SELECT sku_id, COUNT(*) AS items
FROM order_item GROUP BY sku_id ORDER BY items DESC LIMIT 5;
