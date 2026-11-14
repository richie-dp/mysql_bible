-- 第 1 章实验二造数：t_handler 10 万行，user_id 落在 1..1000（每个值约 100 行）
-- 先跑 seed/01-schema.sql；10 万行在本机是秒级
USE shop;
SET SESSION cte_max_recursion_depth = 100000;
DROP TABLE IF EXISTS t_handler;
CREATE TABLE t_handler (
  id      BIGINT       PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT       NOT NULL,
  amount  DECIMAL(10,2) NOT NULL,
  memo    VARCHAR(64)  NOT NULL,
  KEY idx_user (user_id)
) ENGINE=InnoDB;
INSERT INTO t_handler (user_id, amount, memo)
WITH RECURSIVE seq(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM seq WHERE n < 100000)
SELECT 1 + (n % 1000), ROUND(10 + (n % 900) * 0.37, 2), CONCAT('memo-', n) FROM seq;
-- 再放几笔订单：第 1 章讲 UPDATE 的排队点时直接拿 id = 1 用
INSERT IGNORE INTO order_main (order_no, merchant_id, buyer_id, status, pay_amount) VALUES
('SODEMO0000000000000001',1000,100123,20,128.00),('SODEMO0000000000000002',1000,100124,20,256.50),
('SODEMO0000000000000003',1001,100125,10,39.90),('SODEMO0000000000000004',1001,100126,90,899.00);
SELECT COUNT(*) AS t_handler_rows FROM t_handler;
