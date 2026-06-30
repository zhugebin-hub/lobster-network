-- 学校食堂菜单管理系统 - 数据库结构

-- 用户表（3 级权限）
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    role INTEGER NOT NULL, -- 1:超级管理员，2:食堂管理员，3:审核人员
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 原材料表
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50), -- 蔬菜/肉类/水产/调料/主食等
    unit VARCHAR(20) NOT NULL, -- 克/千克/个/份
    unit_price DECIMAL(10,2), -- 单价（元/单位）
    supplier VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 菜品表
CREATE TABLE IF NOT EXISTS dishes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50), -- 荤菜/素菜/汤/主食等
    description TEXT,
    prep_time INTEGER, -- 切配时间（分钟）
    cook_time INTEGER, -- 烹饪时间（分钟）
    total_time INTEGER, -- 总时间（分钟）
    base_cost DECIMAL(10,2), -- 基础成本
    serving_size INTEGER DEFAULT 1, -- 份量（人份）
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 菜品配料表（多对多关系）
CREATE TABLE IF NOT EXISTS dish_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dish_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    quantity DECIMAL(10,2) NOT NULL, -- 用量
    unit VARCHAR(20), -- 单位（可覆盖原材料默认单位）
    cost DECIMAL(10,2), -- 该项成本
    FOREIGN KEY (dish_id) REFERENCES dishes(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
);

-- 周菜单表
CREATE TABLE IF NOT EXISTS weekly_menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start DATE NOT NULL, -- 周开始日期（周一）
    week_end DATE NOT NULL, -- 周结束日期（周日）
    status INTEGER DEFAULT 1, -- 1:草稿，2:待审核，3:已审核，4:已发布，5:已归档
    created_by INTEGER,
    reviewed_by INTEGER,
    reviewed_at DATETIME,
    review_comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
);

-- 每日菜单表
CREATE TABLE IF NOT EXISTS daily_menus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    weekly_menu_id INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL, -- 1-5（周一到周五）
    meal_type INTEGER NOT NULL, -- 1:中餐，2:晚餐
    dish_id INTEGER NOT NULL,
    sort_order INTEGER DEFAULT 0,
    notes TEXT,
    FOREIGN KEY (weekly_menu_id) REFERENCES weekly_menus(id),
    FOREIGN KEY (dish_id) REFERENCES dishes(id)
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(50) NOT NULL,
    target_type VARCHAR(50),
    target_id INTEGER,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
