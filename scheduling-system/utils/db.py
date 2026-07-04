"""
数据库操作模块
"""
import sqlite3
from pathlib import Path
from typing import List, Optional, Any


class Database:
    """数据库管理类"""
    
    def __init__(self, db_path: str = "data/school.db"):
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self):
        """连接数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def _create_tables(self):
        """创建数据表"""
        cursor = self.conn.cursor()
        
        # 教师表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                max_weekly_hours INTEGER DEFAULT 16,
                email TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                notes TEXT DEFAULT ''
            )
        """)
        
        # 班级表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grade TEXT NOT NULL,
                student_count INTEGER DEFAULT 45,
                homeroom_teacher_id INTEGER
            )
        """)
        
        # 课程表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                weekly_hours INTEGER DEFAULT 2,
                consecutive INTEGER DEFAULT 1,
                requirements TEXT DEFAULT '',
                FOREIGN KEY (class_id) REFERENCES classes(id),
                FOREIGN KEY (teacher_id) REFERENCES teachers(id)
            )
        """)
        
        # 会议时间表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                day_of_week INTEGER NOT NULL,
                period INTEGER NOT NULL,
                recurring INTEGER DEFAULT 1
            )
        """)
        
        # 课表结果表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                day_of_week INTEGER NOT NULL,
                period INTEGER NOT NULL,
                room TEXT DEFAULT '',
                FOREIGN KEY (class_id) REFERENCES classes(id),
                FOREIGN KEY (teacher_id) REFERENCES teachers(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)
        
        self.conn.commit()
    
    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """执行 SQL"""
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        return cursor
    
    def commit(self):
        """提交事务"""
        self.conn.commit()
    
    def fetch_all(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        """查询所有结果"""
        cursor = self.execute(sql, params)
        return cursor.fetchall()
    
    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """查询单条结果"""
        cursor = self.execute(sql, params)
        return cursor.fetchone()
    
    def insert(self, table: str, data: dict) -> int:
        """插入数据"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = self.execute(sql, tuple(data.values()))
        self.commit()
        return cursor.lastrowid
    
    def update(self, table: str, data: dict, where: str, params: tuple = ()) -> int:
        """更新数据"""
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where}"
        cursor = self.execute(sql, tuple(data.values()) + params)
        self.commit()
        return cursor.rowcount
    
    def delete(self, table: str, where: str, params: tuple = ()) -> int:
        """删除数据"""
        sql = f"DELETE FROM {table} WHERE {where}"
        cursor = self.execute(sql, params)
        self.commit()
        return cursor.rowcount
