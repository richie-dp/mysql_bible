-- 小数据量：2 万订单 / 4 万明细 / 2000 SKU / 500 商户，秒级导入
-- 先跑 01-schema.sql。本脚本会清空 shop 的五张业务表，只在实验库执行。
SET SESSION cte_max_recursion_depth = 100000;
USE shop;

TRUNCATE TABLE order_item;
TRUNCATE TABLE order_main;
TRUNCATE TABLE stock;
TRUNCATE TABLE stock_flow;
TRUNCATE TABLE account_flow;
TRUNCATE TABLE account;

-- 订单：状态按 10/20/30/90/99 循环，created_at 摊在 40 天里
INSERT INTO order_main (order_no, merchant_id, buyer_id, status, pay_amount, created_at, paid_at)
WITH RECURSIVE seq(n) AS (
  SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 20000
), t AS (
  SELECT n, TIMESTAMP('2026-09-01 00:00:00')
            + INTERVAL (n % 40) DAY
            + INTERVAL (n * 37 % 86400) SECOND AS ts
  FROM seq
)
SELECT CONCAT('SO2026', LPAD(n, 12, '0')),
       1000 + (n % 500),
       100000 + (n * 7 % 50000),
       ELT(1 + (n % 5), 10, 20, 30, 90, 99),
       ROUND(9.9 + (n % 4000) * 1.37, 2),
       ts,
       IF(n % 5 = 0, NULL, ts + INTERVAL 2 MINUTE)
FROM t;

-- 明细：每单两行，两行金额相加严格等于主表 pay_amount（对账时不会对不上）
INSERT INTO order_item (order_id, line_no, sku_id, sku_name, unit_price, qty)
SELECT o.id, 1, 8800 + (o.id % 2000), CONCAT('SKU-', 8800 + (o.id % 2000)),
       ROUND(o.pay_amount * 0.4, 2), 1
FROM order_main o
UNION ALL
SELECT o.id, 2, 9000 + (o.id % 1500), CONCAT('SKU-', 9000 + (o.id % 1500)),
       o.pay_amount - ROUND(o.pay_amount * 0.4, 2), 1
FROM order_main o;

-- 库存：覆盖明细里出现的全部 SKU
INSERT INTO stock (sku_id, qty, version)
WITH RECURSIVE seq(n) AS (
  SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 2000
)
SELECT 8799 + n, 1000 + (n % 50), 0 FROM seq;

-- 账户：商户 1000~1499
INSERT INTO account (merchant_id, balance)
WITH RECURSIVE seq(n) AS (
  SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 500
)
SELECT 999 + n, 100000.00 FROM seq;

-- 账户流水：5000 条，account_id 落在 1~500
INSERT INTO account_flow (account_id, biz_no, direction, amount, balance_after)
WITH RECURSIVE seq(n) AS (
  SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 5000
)
SELECT 1 + (n % 500), CONCAT('AF2026', LPAD(n, 12, '0')),
       IF(n % 2 = 0, 1, -1), ROUND(1 + (n % 900) * 0.31, 2), 100000.00
FROM seq;

SELECT 'order_main' AS tbl, COUNT(*) AS rows_cnt FROM order_main
UNION ALL SELECT 'order_item', COUNT(*) FROM order_item
UNION ALL SELECT 'stock', COUNT(*) FROM stock
UNION ALL SELECT 'account', COUNT(*) FROM account
UNION ALL SELECT 'account_flow', COUNT(*) FROM account_flow;
