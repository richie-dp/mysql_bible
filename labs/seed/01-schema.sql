-- 实验库 shop：订单 / 明细 / 库存 / 库存流水 / 账户 / 账户流水
-- 与第 49 章同一套字段。金额列叫 pay_amount（第 49 章、附录 D13 都用这个名字），
-- 不要另起 amount，否则附录 D 的诊断 SQL 贴进来会报 1054 列不存在。
CREATE DATABASE IF NOT EXISTS shop
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE shop;

CREATE TABLE order_main (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_no     CHAR(22)        NOT NULL,
  merchant_id  BIGINT UNSIGNED NOT NULL,
  buyer_id     BIGINT UNSIGNED NOT NULL,
  status       TINYINT         NOT NULL DEFAULT 10,
  after_sale   TINYINT         NOT NULL DEFAULT 0,
  pay_amount   DECIMAL(18,2)   NOT NULL DEFAULT 0.00,
  created_at   DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  paid_at      DATETIME(3)     DEFAULT NULL,
  PRIMARY KEY (id),
  -- 挡住"同一笔订单号被重复写入"：支付回调重试、导入脚本跑两遍都靠它
  UNIQUE KEY uk_order_no (order_no),
  -- 挡住"某商户最近 N 天订单"的回表：merchant_id 等值 + created_at 范围，只扫这一段
  KEY idx_merchant_created (merchant_id, created_at),
  -- 挡住运营后台"按状态扫一天"：不加它就得扫全表再过滤 status
  KEY idx_status_created (status, created_at),
  -- 挡住"我的订单"列表：buyer_id 等值 + created_at 倒序，避免 filesort
  KEY idx_buyer_created (buyer_id, created_at)
) ENGINE=InnoDB COMMENT='订单主表';

CREATE TABLE order_item (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  order_id   BIGINT UNSIGNED NOT NULL,
  line_no    INT UNSIGNED    NOT NULL,
  sku_id     BIGINT UNSIGNED NOT NULL,
  sku_name   VARCHAR(64)     NOT NULL,
  unit_price DECIMAL(18,2)   NOT NULL,
  qty        INT UNSIGNED    NOT NULL,
  PRIMARY KEY (id),
  -- 挡住"重试把同一行明细插两遍"：幂等键必须落在唯一索引上，不能靠应用判重
  UNIQUE KEY uk_order_line (order_id, line_no),
  -- 挡住"这个 SKU 卖了多少"：按 sku_id 聚合，不必回主表扫
  KEY idx_sku (sku_id)
) ENGINE=InnoDB COMMENT='订单明细；sku_name/unit_price 是下单时刻的快照';

CREATE TABLE stock (
  sku_id     BIGINT UNSIGNED NOT NULL,
  qty        INT             NOT NULL,
  version    INT UNSIGNED    NOT NULL DEFAULT 0,
  updated_at DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
                             ON UPDATE CURRENT_TIMESTAMP(3),
  -- 单仓模型：主键就是 sku_id，扣减锁退化成一条记录锁（第 19 章）。
  -- 多仓时主键要扩成 (sku_id, warehouse_id)，否则一次扣减会锁住这个 SKU 的所有仓
  PRIMARY KEY (sku_id)
) ENGINE=InnoDB COMMENT='库存；qty >= 1 的判断必须写进 UPDATE 的 WHERE';

CREATE TABLE stock_flow (
  sku_id     BIGINT UNSIGNED NOT NULL,
  biz_no     CHAR(22)        NOT NULL,
  direction  TINYINT         NOT NULL COMMENT '1 扣减 -1 回补',
  qty        INT             NOT NULL,
  status     VARCHAR(16)     NOT NULL,
  created_at DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  -- 故意不建主键：第 41 章案例四要靠它复现"无主键 → 并行回放退化"。
  -- 生产建表必须有 PRIMARY KEY(id)，并补 UNIQUE KEY uk_biz (biz_no, direction)。
  KEY idx_sku_created (sku_id, created_at),
  KEY idx_biz (biz_no)
) ENGINE=InnoDB COMMENT='库存流水；本表刻意无主键，用于复现复制延迟';

CREATE TABLE account (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  merchant_id BIGINT UNSIGNED NOT NULL,
  balance     DECIMAL(18,2)   NOT NULL DEFAULT 0.00,
  frozen      DECIMAL(18,2)   NOT NULL DEFAULT 0.00,
  version     BIGINT UNSIGNED NOT NULL DEFAULT 0,
  updated_at  DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3)
                              ON UPDATE CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  -- 挡住"一个商户开出两个账户"：账户是资金归属，重复即对账不平
  UNIQUE KEY uk_merchant (merchant_id)
) ENGINE=InnoDB COMMENT='商户账户余额';

CREATE TABLE account_flow (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  account_id    BIGINT UNSIGNED NOT NULL,
  biz_no        CHAR(22)        NOT NULL,
  direction     TINYINT         NOT NULL COMMENT '1 入账 -1 出账',
  amount        DECIMAL(18,2)   NOT NULL,
  balance_after DECIMAL(18,2)   NOT NULL,
  created_at    DATETIME(3)     NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  PRIMARY KEY (id),
  -- 挡住"同一笔业务记两次账"：支付回调重放时的最后一道闸
  UNIQUE KEY uk_account_biz (account_id, biz_no, direction),
  -- 挡住"某账户最近流水"：account_id 等值 + created_at 范围
  KEY idx_account_created (account_id, created_at)
) ENGINE=InnoDB COMMENT='账户流水；balance_after 用于对账时逐笔核对';
