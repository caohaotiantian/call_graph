"""
数据库操作模块
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class CallGraphDB:
    """调用关系数据库管理"""

    def __init__(self, db_path: str = "call_graph.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize()

    def initialize(self):
        """初始化数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # 读取并执行schema
        schema_path = Path(__file__).parent.parent / "init_db.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            self.conn.executescript(f.read())
        self.conn.commit()

    def insert_symbol(self, symbol: Dict[str, Any]):
        """插入符号信息"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO symbols 
            (id, file, name, kind, start_line, end_line, start_byte, end_byte,
             container, signature, language, extras_json, code_excerpt, is_exported)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                symbol["id"],
                symbol["file"],
                symbol["name"],
                symbol["kind"],
                symbol.get("start_line"),
                symbol.get("end_line"),
                symbol.get("start_byte"),
                symbol.get("end_byte"),
                symbol.get("container"),
                symbol.get("signature"),
                symbol["language"],
                json.dumps(symbol.get("extras", {})),
                symbol.get("code_excerpt"),
                symbol.get("is_exported", 0),
            ),
        )
        self.conn.commit()

    def insert_call_relation(self, relation: Dict[str, Any]):
        """插入调用关系"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO call_relations 
            (caller_id, callee_id, caller_name, callee_name, caller_file, 
             callee_file, call_site_line, call_site_column, language)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                relation["caller_id"],
                relation["callee_id"],
                relation["caller_name"],
                relation["callee_name"],
                relation["caller_file"],
                relation.get("callee_file"),
                relation.get("call_site_line"),
                relation.get("call_site_column"),
                relation["language"],
            ),
        )
        self.conn.commit()

    def get_callers(self, function_name: str) -> List[Dict[str, Any]]:
        """查询调用指定函数的所有函数"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM call_relations 
            WHERE callee_name = ?
            ORDER BY caller_file, call_site_line
        """,
            (function_name,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_callees(self, function_name: str) -> List[Dict[str, Any]]:
        """查询指定函数调用的所有函数"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM call_relations 
            WHERE caller_name = ?
            ORDER BY callee_file, call_site_line
        """,
            (function_name,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_call_chain(self, function_name: str, depth: int = 5) -> List[List[str]]:
        """查询函数的调用链（从该函数向下递归查询）"""
        chains = []
        visited = set()

        def dfs(func_name: str, current_chain: List[str], current_depth: int):
            if current_depth > depth or func_name in visited:
                return

            visited.add(func_name)
            current_chain.append(func_name)

            callees = self.get_callees(func_name)
            if not callees:
                chains.append(current_chain.copy())
            else:
                for callee in callees:
                    dfs(callee["callee_name"], current_chain.copy(), current_depth + 1)

            visited.remove(func_name)

        dfs(function_name, [], 0)
        return chains

    def get_function_info(self, func_name: str) -> Optional[Dict[str, Any]]:
        """获取函数的详细信息（文件和行号）"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT file, start_line FROM symbols 
            WHERE name = ? AND kind = 'function'
            LIMIT 1
        """,
            (func_name,),
        )
        row = cursor.fetchone()
        if row:
            return {"file": row["file"], "line": row["start_line"]}
        return None

    def get_full_call_paths(
        self, function_name: str, max_depth: int = 10, max_paths: int = 1000
    ) -> Dict[str, Any]:
        """
        查询函数的完整调用路径（优化版本，支持去重和路径限制）
        返回包含该函数的所有调用链：从入口函数到叶子函数

        Args:
            function_name: 目标函数名称
            max_depth: 最大搜索深度（默认10）
            max_paths: 最大路径数量限制，防止超大项目产生过多路径（默认1000）

        Returns:
            Dict包含：
            - paths_from_root: 从根节点（入口函数）到目标函数的所有路径（已去重）
            - paths_to_leaf: 从目标函数到叶子节点的所有路径（已去重）
            - full_paths: 完整路径（根 -> 目标 -> 叶子）（已去重）
            - full_paths_detailed: 带详细信息的完整路径
            - truncated: 是否因为达到限制而截断
            - performance: 性能统计信息
        """
        import time

        start_time = time.time()

        # 1. 向上追溯：找到所有到达目标函数的路径（从根到目标）
        paths_from_root = []
        visited_up = set()
        seen_paths_up = set()  # 用于去重
        truncated_up = False

        def trace_up(func_name: str, current_path: List[str], depth: int):
            """向上追溯到根节点（优化版）"""
            nonlocal truncated_up

            # 性能优化：限制路径数量
            if len(paths_from_root) >= max_paths:
                truncated_up = True
                return

            if depth > max_depth or func_name in visited_up:
                return

            visited_up.add(func_name)
            current_path.insert(0, func_name)  # 在路径开头插入

            callers = self.get_callers(func_name)
            if not callers:
                # 到达根节点（没有调用者）
                # 使用 tuple 进行去重检查（tuple 可哈希，可以放入 set）
                path_tuple = tuple(current_path)
                if path_tuple not in seen_paths_up:
                    seen_paths_up.add(path_tuple)
                    paths_from_root.append(current_path.copy())
            else:
                for caller in callers:
                    if len(paths_from_root) >= max_paths:
                        truncated_up = True
                        break
                    trace_up(caller["caller_name"], current_path.copy(), depth + 1)

            visited_up.remove(func_name)

        # 2. 向下追溯：找到所有从目标函数出发的路径（目标到叶子）
        paths_to_leaf = []
        visited_down = set()
        seen_paths_down = set()  # 用于去重
        truncated_down = False

        def trace_down(func_name: str, current_path: List[str], depth: int):
            """向下追溯到叶子节点（优化版）"""
            nonlocal truncated_down

            # 性能优化：限制路径数量
            if len(paths_to_leaf) >= max_paths:
                truncated_down = True
                return

            if depth > max_depth or func_name in visited_down:
                return

            visited_down.add(func_name)
            current_path.append(func_name)

            callees = self.get_callees(func_name)
            if not callees:
                # 到达叶子节点（不调用其他函数）
                # 去重检查
                path_tuple = tuple(current_path)
                if path_tuple not in seen_paths_down:
                    seen_paths_down.add(path_tuple)
                    paths_to_leaf.append(current_path.copy())
            else:
                for callee in callees:
                    if len(paths_to_leaf) >= max_paths:
                        truncated_down = True
                        break
                    trace_down(callee["callee_name"], current_path.copy(), depth + 1)

            visited_down.remove(func_name)

        # 执行追溯
        trace_up(function_name, [], 0)
        trace_down(function_name, [], 0)

        # 3. 组合完整路径（使用 set 去重，限制数量）
        full_paths = []
        seen_full_paths = set()  # 用于完整路径去重
        truncated_full = False

        for root_path in paths_from_root:
            if len(full_paths) >= max_paths:
                truncated_full = True
                break

            for leaf_path in paths_to_leaf:
                if len(full_paths) >= max_paths:
                    truncated_full = True
                    break

                # root_path 已经包含目标函数，leaf_path 也包含目标函数
                # 需要去除重复的目标函数
                if len(leaf_path) > 1:
                    # 如果向下有路径，组合时去掉 leaf_path 的第一个元素（目标函数）
                    combined = root_path + leaf_path[1:]
                else:
                    # 如果目标函数就是叶子节点
                    combined = root_path

                # 去重检查
                path_tuple = tuple(combined)
                if path_tuple not in seen_full_paths:
                    seen_full_paths.add(path_tuple)
                    full_paths.append(combined)

        # 如果没有找到根路径（可能目标函数就是根），使用目标函数作为起点
        if not paths_from_root:
            paths_from_root = [[function_name]]
            if paths_to_leaf:
                for leaf_path in paths_to_leaf:
                    if len(leaf_path) > 1:
                        full_paths.append(leaf_path)
                    else:
                        full_paths.append([function_name])

        # 如果没有找到叶子路径（可能目标函数就是叶子），使用目标函数作为终点
        if not paths_to_leaf:
            paths_to_leaf = [[function_name]]
            if not full_paths and paths_from_root:
                full_paths = paths_from_root

        # 4. 为完整路径添加详细信息（文件名和行号）
        # 性能优化：批量获取函数信息，减少数据库查询次数
        time_before_detail = time.time()

        # 收集所有需要查询的函数名
        all_func_names = set()
        for path in full_paths:
            all_func_names.update(path)

        # 批量查询函数信息（一次查询）
        func_info_cache = {}
        if all_func_names:
            placeholders = ",".join("?" * len(all_func_names))
            cursor = self.conn.cursor()
            cursor.execute(
                f"""
                SELECT name, file, start_line FROM symbols 
                WHERE name IN ({placeholders}) AND kind = 'function'
            """,
                tuple(all_func_names),
            )

            for row in cursor.fetchall():
                if row["name"] not in func_info_cache:  # 如果有重名，取第一个
                    func_info_cache[row["name"]] = {
                        "file": row["file"],
                        "line": row["start_line"],
                    }

        # 使用缓存构建详细路径
        full_paths_detailed = []
        for path in full_paths:
            detailed_path = []
            for func_name in path:
                info = func_info_cache.get(func_name)
                if info:
                    # 格式：函数名(文件:行号)
                    file_short = info["file"].split("/")[-1]  # 只取文件名
                    detailed_path.append(
                        {
                            "name": func_name,
                            "file": info["file"],
                            "file_short": file_short,
                            "line": info["line"],
                            "display": f"{func_name}({file_short}:{info['line']})",
                        }
                    )
                else:
                    # 如果找不到信息（可能是外部函数），只显示函数名
                    detailed_path.append(
                        {
                            "name": func_name,
                            "file": None,
                            "file_short": None,
                            "line": None,
                            "display": func_name,
                        }
                    )
            full_paths_detailed.append(detailed_path)

        # 计算性能统计
        end_time = time.time()
        total_time = end_time - start_time
        detail_time = end_time - time_before_detail

        # 检查是否被截断
        is_truncated = truncated_up or truncated_down or truncated_full

        return {
            "target_function": function_name,
            "paths_from_root": paths_from_root,
            "paths_to_leaf": paths_to_leaf,
            "full_paths": full_paths,
            "full_paths_detailed": full_paths_detailed,
            "root_count": len(paths_from_root),
            "leaf_count": len(paths_to_leaf),
            "full_count": len(full_paths),
            "truncated": is_truncated,
            "max_paths": max_paths,
            "performance": {
                "total_time": round(total_time, 3),
                "detail_time": round(detail_time, 3),
                "duplicates_removed": len(seen_full_paths) - len(full_paths)
                if is_truncated
                else 0,
                "unique_functions": len(all_func_names),
            },
        }

    def get_symbols_by_file(self, file_path: str) -> List[Dict[str, Any]]:
        """查询指定文件中的所有符号"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM symbols WHERE file = ?
            ORDER BY start_line
        """,
            (file_path,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_symbols_by_kind(self, kind: str) -> List[Dict[str, Any]]:
        """查询指定类型的所有符号"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM symbols WHERE kind = ?
            ORDER BY file, start_line
        """,
            (kind,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def search_symbols(self, pattern: str) -> List[Dict[str, Any]]:
        """模糊搜索符号名称"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT * FROM symbols 
            WHERE name LIKE ?
            ORDER BY name, file
        """,
            (f"%{pattern}%",),
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        cursor = self.conn.cursor()

        # 符号统计
        cursor.execute("SELECT COUNT(*) as count FROM symbols")
        symbol_count = cursor.fetchone()["count"]

        # 调用关系统计
        cursor.execute("SELECT COUNT(*) as count FROM call_relations")
        relation_count = cursor.fetchone()["count"]

        # 按语言统计
        cursor.execute("""
            SELECT language, COUNT(*) as count 
            FROM symbols 
            GROUP BY language
        """)
        by_language = {row["language"]: row["count"] for row in cursor.fetchall()}

        # 按类型统计
        cursor.execute("""
            SELECT kind, COUNT(*) as count 
            FROM symbols 
            GROUP BY kind
        """)
        by_kind = {row["kind"]: row["count"] for row in cursor.fetchall()}

        return {
            "total_symbols": symbol_count,
            "total_relations": relation_count,
            "by_language": by_language,
            "by_kind": by_kind,
        }

    def clear_all(self):
        """清空所有数据"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM call_relations")
        cursor.execute("DELETE FROM symbols")
        self.conn.commit()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
