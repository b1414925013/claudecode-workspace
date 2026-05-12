-- 股票收益记录平台 MySQL 初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS stock_platform DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE stock_platform;

-- 1. 账户表
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    account_type VARCHAR(20) DEFAULT 'cash',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_account_type (account_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 持仓表
DROP TABLE IF EXISTS positions;
CREATE TABLE positions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL,
    avg_cost DOUBLE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_account_id (account_id),
    INDEX idx_stock_code (stock_code),
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 交易记录表
DROP TABLE IF EXISTS trades;
CREATE TABLE trades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    trade_type VARCHAR(10) NOT NULL COMMENT 'buy 或 sell',
    quantity INT NOT NULL,
    price DOUBLE NOT NULL,
    commission DOUBLE DEFAULT 0.0,
    trade_date DATETIME NOT NULL,
    profit DOUBLE NULL COMMENT '卖出时计算的盈亏',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_account_id (account_id),
    INDEX idx_stock_code (stock_code),
    INDEX idx_trade_date (trade_date),
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 分红记录表
DROP TABLE IF EXISTS dividends;
CREATE TABLE dividends (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    dividend_amount DOUBLE NOT NULL,
    dividend_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_account_id (account_id),
    INDEX idx_stock_code (stock_code),
    INDEX idx_dividend_date (dividend_date),
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 股票价格表
DROP TABLE IF EXISTS stock_prices;
CREATE TABLE stock_prices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    price DOUBLE NOT NULL,
    change_value DOUBLE NULL,
    change_percent DOUBLE NULL,
    trade_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stock_code (stock_code),
    INDEX idx_trade_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- 初始化测试数据
-- =====================================================

-- 插入账户
INSERT INTO accounts (name, account_type) VALUES
('主账户', 'cash'),
('融资账户', 'margin');

-- 插入持仓
INSERT INTO positions (account_id, stock_code, stock_name, quantity, avg_cost) VALUES
(1, '600519', '贵州茅台', 100, 1800.0),
(1, '000858', '五粮液', 500, 150.0),
(2, '600036', '招商银行', 1000, 35.0);

-- 插入交易记录
INSERT INTO trades (account_id, stock_code, stock_name, trade_type, quantity, price, commission, trade_date) VALUES
(1, '600519', '贵州茅台', 'buy', 100, 1800.0, 5.0, DATE_SUB(NOW(), INTERVAL 60 DAY)),
(1, '000858', '五粮液', 'buy', 300, 145.0, 3.0, DATE_SUB(NOW(), INTERVAL 45 DAY)),
(1, '000858', '五粮液', 'buy', 200, 155.0, 3.0, DATE_SUB(NOW(), INTERVAL 30 DAY)),
(1, '000858', '五粮液', 'sell', 200, 165.0, 3.0, DATE_SUB(NOW(), INTERVAL 15 DAY)),
(2, '600036', '招商银行', 'buy', 1000, 35.0, 5.0, DATE_SUB(NOW(), INTERVAL 20 DAY));

-- 插入分红记录
INSERT INTO dividends (account_id, stock_code, stock_name, dividend_amount, dividend_date) VALUES
(1, '600519', '贵州茅台', 2000.0, DATE_SUB(NOW(), INTERVAL 90 DAY)),
(1, '000858', '五粮液', 1500.0, DATE_SUB(NOW(), INTERVAL 60 DAY)),
(2, '600036', '招商银行', 800.0, DATE_SUB(NOW(), INTERVAL 30 DAY));

-- 插入股票价格（示例）
INSERT INTO stock_prices (stock_code, price, change_value, change_percent, trade_date) VALUES
('600519', 1850.0, 50.0, 2.78, NOW()),
('000858', 160.0, 5.0, 3.23, NOW()),
('600036', 36.5, 1.5, 4.28, NOW());

SELECT '数据库初始化完成！' AS message;
