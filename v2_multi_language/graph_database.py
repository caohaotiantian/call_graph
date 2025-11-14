"""
图数据库操作层
支持多语言代码分析的图数据存储和查询
"""
import sqlite3
import json
import hashlib
from typing import List, Dict, Optional, Any, Tuple
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import logging

import config_v2 as config

logger = logging.getLogger(__name__)


class GraphDatabase:
    """图数据库管理器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DB_PATH
        self._init_database()
    
    def _init_database(self):
        """初始化数据库，创建表结构"""
        init_sql_path = Path(__file__).parent / 'init_graph_db.sql'
        
        if not init_sql_path.exists():
            logger.warning(f"init_graph_db.sql not found, skipping initialization")
            return
        
        with open(init_sql_path, 'r', encoding='utf-8') as f:
            init_sql = f.read()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript(init_sql)
            conn.commit()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # 启用外键约束
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()
    
    # ===== 项目操作 =====
    
    def create_project(
        self,
        name: str,
        root_path: str,
        primary_language: str = None,
        languages: List[str] = None
    ) -> str:
        """
        创建项目记录
        
        Args:
            name: 项目名称
            root_path: 项目根路径
            primary_language: 主要语言
            languages: 支持的语言列表
        
        Returns:
            项目ID
        """
        project_id = self._generate_project_id(name, root_path)
        languages_json = json.dumps(languages) if languages else None
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO projects 
                (id, name, root_path, primary_language, languages)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, name, root_path, primary_language, languages_json))
            conn.commit()
        
        logger.info(f"Created project: {name} ({project_id})")
        return project_id
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """获取项目信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                if data.get('languages'):
                    data['languages'] = json.loads(data['languages'])
                return data
            return None
    
    def list_projects(self) -> List[Dict]:
        """列出所有项目"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_project(self, project_id: str):
        """删除项目及其所有数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
        logger.info(f"Deleted project: {project_id}")
    
    # ===== 节点操作 =====
    
    def insert_node(self, node_data: Dict) -> str:
        """
        插入节点
        
        Args:
            node_data: 节点数据
        
        Returns:
            节点ID
        """
        node_id = node_data.get('id') or self._generate_node_id(node_data)
        metadata_json = json.dumps(node_data.get('metadata', {}))
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO nodes 
                (id, project_id, language, node_type, name, qualified_name,
                 file_path, start_line, end_line, start_column, end_column,
                 signature, code_snippet, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                node_id,
                node_data.get('project_id'),
                node_data['language'],
                node_data['node_type'],
                node_data['name'],
                node_data.get('qualified_name'),
                node_data['file_path'],
                node_data.get('start_line'),
                node_data.get('end_line'),
                node_data.get('start_column'),
                node_data.get('end_column'),
                node_data.get('signature'),
                node_data.get('code_snippet'),
                metadata_json
            ))
            conn.commit()
        
        return node_id
    
    def batch_insert_nodes(self, nodes: List[Dict]) -> int:
        """批量插入节点"""
        if not nodes:
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            data = []
            for node in nodes:
                node_id = node.get('id') or self._generate_node_id(node)
                node['id'] = node_id
                metadata_json = json.dumps(node.get('metadata', {}))
                
                data.append((
                    node_id,
                    node.get('project_id'),
                    node['language'],
                    node['node_type'],
                    node['name'],
                    node.get('qualified_name'),
                    node['file_path'],
                    node.get('start_line'),
                    node.get('end_line'),
                    node.get('start_column'),
                    node.get('end_column'),
                    node.get('signature'),
                    node.get('code_snippet'),
                    metadata_json
                ))
            
            cursor.executemany("""
                INSERT OR REPLACE INTO nodes 
                (id, project_id, language, node_type, name, qualified_name,
                 file_path, start_line, end_line, start_column, end_column,
                 signature, code_snippet, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            conn.commit()
        
        return len(nodes)
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """获取节点"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
            row = cursor.fetchone()
            if row:
                data = dict(row)
                if data.get('metadata'):
                    try:
                        data['metadata'] = json.loads(data['metadata'])
                    except:
                        pass
                return data
            return None
    
    def find_nodes(
        self,
        project_id: str = None,
        language: str = None,
        node_type: str = None,
        name: str = None,
        file_path: str = None
    ) -> List[Dict]:
        """查找节点"""
        conditions = []
        params = []
        
        if project_id:
            conditions.append("project_id = ?")
            params.append(project_id)
        if language:
            conditions.append("language = ?")
            params.append(language)
        if node_type:
            conditions.append("node_type = ?")
            params.append(node_type)
        if name:
            conditions.append("name = ?")
            params.append(name)
        if file_path:
            conditions.append("file_path = ?")
            params.append(file_path)
        
        query = "SELECT * FROM nodes"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # ===== 边操作 =====
    
    def insert_edge(self, edge_data: Dict) -> int:
        """插入边"""
        metadata_json = json.dumps(edge_data.get('metadata', {}))
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO edges 
                (project_id, edge_type, source_id, target_id, target_name,
                 file_path, line, column, is_resolved, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                edge_data.get('project_id'),
                edge_data['edge_type'],
                edge_data['source_id'],
                edge_data.get('target_id'),
                edge_data.get('target_name'),
                edge_data.get('file_path'),
                edge_data.get('line'),
                edge_data.get('column'),
                edge_data.get('is_resolved', 1 if edge_data.get('target_id') else 0),
                metadata_json
            ))
            conn.commit()
            return cursor.lastrowid
    
    def batch_insert_edges(self, edges: List[Dict]) -> int:
        """批量插入边"""
        if not edges:
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            data = [(
                edge.get('project_id'),
                edge['edge_type'],
                edge['source_id'],
                edge.get('target_id'),
                edge.get('target_name'),
                edge.get('file_path'),
                edge.get('line'),
                edge.get('column'),
                edge.get('is_resolved', 1 if edge.get('target_id') else 0),
                json.dumps(edge.get('metadata', {}))
            ) for edge in edges]
            
            cursor.executemany("""
                INSERT INTO edges 
                (project_id, edge_type, source_id, target_id, target_name,
                 file_path, line, column, is_resolved, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            conn.commit()
        
        return len(edges)
    
    def get_edges(
        self,
        project_id: str = None,
        edge_type: str = None,
        source_id: str = None,
        target_id: str = None
    ) -> List[Dict]:
        """查询边"""
        conditions = []
        params = []
        
        if project_id:
            conditions.append("project_id = ?")
            params.append(project_id)
        if edge_type:
            conditions.append("edge_type = ?")
            params.append(edge_type)
        if source_id:
            conditions.append("source_id = ?")
            params.append(source_id)
        if target_id:
            conditions.append("target_id = ?")
            params.append(target_id)
        
        query = "SELECT * FROM edges"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # ===== 数据流操作 =====
    
    def insert_dataflow(self, dataflow_data: Dict) -> int:
        """插入数据流记录"""
        metadata_json = json.dumps(dataflow_data.get('metadata', {}))
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dataflow 
                (project_id, variable_id, variable_name, definition_node_id,
                 use_node_id, flow_type, file_path, line, column, scope_node_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dataflow_data.get('project_id'),
                dataflow_data['variable_id'],
                dataflow_data['variable_name'],
                dataflow_data.get('definition_node_id'),
                dataflow_data.get('use_node_id'),
                dataflow_data['flow_type'],
                dataflow_data.get('file_path'),
                dataflow_data.get('line'),
                dataflow_data.get('column'),
                dataflow_data.get('scope_node_id'),
                metadata_json
            ))
            conn.commit()
            return cursor.lastrowid
    
    def batch_insert_dataflows(self, dataflows: List[Dict]) -> int:
        """批量插入数据流记录"""
        if not dataflows:
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            data = [(
                df.get('project_id'),
                df['variable_id'],
                df['variable_name'],
                df.get('definition_node_id'),
                df.get('use_node_id'),
                df['flow_type'],
                df.get('file_path'),
                df.get('line'),
                df.get('column'),
                df.get('scope_node_id'),
                json.dumps(df.get('metadata', {}))
            ) for df in dataflows]
            
            cursor.executemany("""
                INSERT INTO dataflow 
                (project_id, variable_id, variable_name, definition_node_id,
                 use_node_id, flow_type, file_path, line, column, scope_node_id, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            conn.commit()
        
        return len(dataflows)
    
    # ===== 统计操作 =====
    
    def get_project_statistics(self, project_id: str) -> Dict:
        """获取项目统计信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 使用视图
            cursor.execute("""
                SELECT * FROM v_project_summary WHERE id = ?
            """, (project_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            
            return {}
    
    def save_statistics(self, project_id: str, stats: Dict):
        """保存分析统计"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analysis_stats 
                (project_id, language, total_files, total_nodes, total_edges,
                 total_functions, total_classes, total_dataflows, analysis_duration_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                stats.get('language'),
                stats.get('total_files', 0),
                stats.get('total_nodes', 0),
                stats.get('total_edges', 0),
                stats.get('total_functions', 0),
                stats.get('total_classes', 0),
                stats.get('total_dataflows', 0),
                stats.get('analysis_duration_seconds', 0)
            ))
            conn.commit()
    
    # ===== 辅助方法 =====
    
    def _generate_project_id(self, name: str, root_path: str) -> str:
        """生成项目ID"""
        unique_str = f"{name}:{root_path}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:16]
    
    def _generate_node_id(self, node_data: Dict) -> str:
        """生成节点ID"""
        unique_str = f"{node_data['file_path']}:{node_data['node_type']}:{node_data['name']}:{node_data.get('start_line', 0)}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def clear_project_data(self, project_id: str):
        """清空项目数据（保留项目记录）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM dataflow WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM call_chains WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM edges WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM nodes WHERE project_id = ?", (project_id,))
            cursor.execute("DELETE FROM analysis_stats WHERE project_id = ?", (project_id,))
            conn.commit()
        logger.info(f"Cleared data for project: {project_id}")

