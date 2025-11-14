"""
数据库操作层
"""
import sqlite3
import json
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
import config


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DB_PATH
        self._init_database()
    
    def _init_database(self):
        """初始化数据库，创建表结构"""
        with open('init_db.sql', 'r', encoding='utf-8') as f:
            init_sql = f.read()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 执行所有SQL语句
            cursor.executescript(init_sql)
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_all_symbols(self, kind: str = None) -> List[Dict]:
        """
        获取所有符号
        
        Args:
            kind: 符号类型过滤（如 'function', 'method', 'class'）
        
        Returns:
            符号列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if kind:
                cursor.execute("SELECT * FROM symbols WHERE kind = ?", (kind,))
            else:
                cursor.execute("SELECT * FROM symbols")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_symbol_by_id(self, symbol_id: str) -> Optional[Dict]:
        """根据ID获取符号"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM symbols WHERE id = ?", (symbol_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def find_symbols_by_name(self, name: str, file: str = None) -> List[Dict]:
        """
        根据名称查找符号
        
        Args:
            name: 符号名称
            file: 文件路径（可选）
        
        Returns:
            匹配的符号列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if file:
                cursor.execute(
                    "SELECT * FROM symbols WHERE name = ? AND file = ?",
                    (name, file)
                )
            else:
                cursor.execute("SELECT * FROM symbols WHERE name = ?", (name,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def insert_function_call(self, call_data: Dict) -> int:
        """
        插入函数调用记录
        
        Args:
            call_data: 调用数据字典
        
        Returns:
            插入的记录ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO function_calls 
                (caller_id, caller_name, caller_file, callee_name, callee_id, 
                 callee_file, call_line, call_column, call_type, is_resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                call_data['caller_id'],
                call_data['caller_name'],
                call_data['caller_file'],
                call_data['callee_name'],
                call_data.get('callee_id'),
                call_data.get('callee_file'),
                call_data.get('call_line'),
                call_data.get('call_column'),
                call_data.get('call_type', 'direct_call'),
                call_data.get('is_resolved', 0)
            ))
            conn.commit()
            return cursor.lastrowid
    
    def batch_insert_function_calls(self, calls: List[Dict]) -> int:
        """
        批量插入函数调用记录
        
        Args:
            calls: 调用数据列表
        
        Returns:
            插入的记录数
        """
        if not calls:
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO function_calls 
                (caller_id, caller_name, caller_file, callee_name, callee_id, 
                 callee_file, call_line, call_column, call_type, is_resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    call['caller_id'],
                    call['caller_name'],
                    call['caller_file'],
                    call['callee_name'],
                    call.get('callee_id'),
                    call.get('callee_file'),
                    call.get('call_line'),
                    call.get('call_column'),
                    call.get('call_type', 'direct_call'),
                    call.get('is_resolved', 0)
                )
                for call in calls
            ])
            conn.commit()
            return len(calls)
    
    def get_function_calls(self, caller_id: str = None, callee_id: str = None) -> List[Dict]:
        """
        获取函数调用记录
        
        Args:
            caller_id: 调用者ID（可选）
            callee_id: 被调用者ID（可选）
        
        Returns:
            调用记录列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if caller_id:
                cursor.execute("SELECT * FROM function_calls WHERE caller_id = ?", (caller_id,))
            elif callee_id:
                cursor.execute("SELECT * FROM function_calls WHERE callee_id = ?", (callee_id,))
            else:
                cursor.execute("SELECT * FROM function_calls")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def insert_call_chain(self, chain_data: Dict) -> int:
        """
        插入调用链记录
        
        Args:
            chain_data: 调用链数据
        
        Returns:
            插入的记录ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO call_chains 
                (chain_path, chain_depth, start_function_id, end_function_id, intermediate_calls)
                VALUES (?, ?, ?, ?, ?)
            """, (
                chain_data['chain_path'],
                chain_data['chain_depth'],
                chain_data['start_function_id'],
                chain_data['end_function_id'],
                chain_data.get('intermediate_calls')
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_call_chains(self, start_function_id: str = None, max_depth: int = None) -> List[Dict]:
        """
        获取调用链
        
        Args:
            start_function_id: 起始函数ID（可选）
            max_depth: 最大深度（可选）
        
        Returns:
            调用链列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if start_function_id and max_depth:
                cursor.execute("""
                    SELECT * FROM call_chains 
                    WHERE start_function_id = ? AND chain_depth <= ?
                    ORDER BY chain_depth
                """, (start_function_id, max_depth))
            elif start_function_id:
                cursor.execute("""
                    SELECT * FROM call_chains 
                    WHERE start_function_id = ?
                    ORDER BY chain_depth
                """, (start_function_id,))
            else:
                cursor.execute("SELECT * FROM call_chains ORDER BY chain_depth")
            
            return [dict(row) for row in cursor.fetchall()]
    
    def clear_function_calls(self):
        """清空函数调用表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM function_calls")
            conn.commit()
    
    def clear_call_chains(self):
        """清空调用链表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM call_chains")
            conn.commit()
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 统计各类数据
            cursor.execute("SELECT COUNT(*) FROM symbols")
            symbol_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM function_calls")
            call_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM function_calls WHERE is_resolved = 1")
            resolved_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM call_chains")
            chain_count = cursor.fetchone()[0]
            
            return {
                'total_symbols': symbol_count,
                'total_calls': call_count,
                'resolved_calls': resolved_count,
                'unresolved_calls': call_count - resolved_count,
                'total_chains': chain_count
            }


