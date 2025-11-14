"""
核心分析引擎
协调代码解析和调用关系提取
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# 支持相对导入和直接运行
try:
    from .database import CallGraphDB
    from .parsers import LANGUAGE_CONFIG, detect_language, get_parser
except ImportError:
    from database import CallGraphDB
    from parsers import LANGUAGE_CONFIG, detect_language, get_parser


class CallGraphAnalyzer:
    """调用关系分析器"""

    def __init__(self, db_path: str = "call_graph.db"):
        self.db = CallGraphDB(db_path)
        self.all_functions: List[Dict[str, Any]] = []

    def analyze_project(
        self, project_path: str, exclude_dirs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """分析整个项目"""
        if exclude_dirs is None:
            exclude_dirs = [
                "node_modules",
                ".git",
                "__pycache__",
                "venv",
                "env",
                "build",
                "dist",
                "target",
                ".idea",
                ".vscode",
                "bin",
                "obj",
            ]

        project_path = Path(project_path).resolve()

        print(f"开始分析项目: {project_path}")

        # 收集所有源代码文件
        source_files = self._collect_source_files(project_path, exclude_dirs)

        print(f"找到 {len(source_files)} 个源代码文件")

        # 第一遍：提取所有函数定义
        print("第一遍扫描：提取函数定义...")
        for file_path in source_files:
            self._extract_functions_from_file(file_path)

        print(f"共提取 {len(self.all_functions)} 个函数定义")

        # 保存函数定义到数据库
        print("保存函数定义到数据库...")
        for func in self.all_functions:
            self.db.insert_symbol(func)

        # 第二遍：提取调用关系
        print("第二遍扫描：提取调用关系...")
        total_calls = 0
        for file_path in source_files:
            calls = self._extract_calls_from_file(file_path)
            total_calls += len(calls)

        print(f"共提取 {total_calls} 个调用关系")

        # 生成统计报告
        stats = self.db.get_statistics()

        print("\n分析完成！")
        print(f"总符号数: {stats['total_symbols']}")
        print(f"总调用关系: {stats['total_relations']}")
        print("\n按语言统计:")
        for lang, count in stats["by_language"].items():
            print(f"  {lang}: {count}")

        return stats

    def _collect_source_files(
        self, project_path: Path, exclude_dirs: List[str]
    ) -> List[str]:
        """收集所有源代码文件"""
        source_files = []

        # 收集所有支持的扩展名
        supported_extensions = set()
        for config in LANGUAGE_CONFIG.values():
            supported_extensions.update(config["extensions"])

        for root, dirs, files in os.walk(project_path):
            # 排除指定目录
            dirs[:] = [
                d for d in dirs if d not in exclude_dirs and not d.startswith(".")
            ]

            for file in files:
                if any(file.endswith(ext) for ext in supported_extensions):
                    file_path = os.path.join(root, file)
                    source_files.append(file_path)

        return source_files

    def _extract_functions_from_file(self, file_path: str):
        """从文件中提取函数定义"""
        language = detect_language(file_path)
        if not language:
            return

        try:
            parser = get_parser(language)
            functions = parser.extract_functions(file_path)
            self.all_functions.extend(functions)
        except Exception as e:
            print(f"警告: 提取函数失败 {file_path}: {e}")

    def _extract_calls_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """从文件中提取调用关系"""
        language = detect_language(file_path)
        if not language:
            return []

        try:
            parser = get_parser(language)
            calls = parser.extract_calls(file_path, self.all_functions)

            # 保存到数据库
            for call in calls:
                self.db.insert_call_relation(call)

            return calls
        except Exception as e:
            print(f"警告: 提取调用关系失败 {file_path}: {e}")
            return []

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """分析单个文件"""
        language = detect_language(file_path)
        if not language:
            return {
                "error": f"不支持的文件类型: {file_path}",
                "functions": [],
                "calls": [],
            }

        parser = get_parser(language)

        # 提取函数定义
        functions = parser.extract_functions(file_path)

        # 保存到数据库
        for func in functions:
            self.db.insert_symbol(func)

        # 提取调用关系
        calls = parser.extract_calls(file_path, functions)

        # 保存到数据库
        for call in calls:
            self.db.insert_call_relation(call)

        return {
            "file": file_path,
            "language": language,
            "functions": functions,
            "calls": calls,
        }

    def query_callers(self, function_name: str) -> List[Dict[str, Any]]:
        """查询调用指定函数的所有函数"""
        return self.db.get_callers(function_name)

    def query_callees(self, function_name: str) -> List[Dict[str, Any]]:
        """查询指定函数调用的所有函数"""
        return self.db.get_callees(function_name)

    def query_call_chain(self, function_name: str, depth: int = 5) -> List[List[str]]:
        """查询函数的调用链（向下）"""
        return self.db.get_call_chain(function_name, depth)

    def query_full_call_paths(
        self, function_name: str, max_depth: int = 10, max_paths: int = 1000
    ) -> Dict[str, Any]:
        """
        查询函数的完整调用路径（向上+向下）

        Args:
            function_name: 目标函数名称
            max_depth: 最大搜索深度
            max_paths: 最大路径数量限制（性能优化）
        """
        return self.db.get_full_call_paths(function_name, max_depth, max_paths)

    def search_functions(self, pattern: str) -> List[Dict[str, Any]]:
        """搜索函数"""
        return self.db.search_symbols(pattern)

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.db.get_statistics()

    def export_graph(self, output_format: str = "dot") -> str:
        """导出调用图"""
        if output_format == "dot":
            return self._export_dot()
        else:
            raise ValueError(f"不支持的导出格式: {output_format}")

    def _export_dot(self) -> str:
        """导出为Graphviz DOT格式"""
        lines = ["digraph CallGraph {"]
        lines.append("  rankdir=LR;")
        lines.append("  node [shape=box];")

        # 添加所有函数节点
        symbols = self.db.get_symbols_by_kind("function")
        for symbol in symbols:
            node_id = symbol["id"]
            label = f"{symbol['name']}\\n({symbol['file']})"
            lines.append(f'  "{node_id}" [label="{label}"];')

        # 添加调用边
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM call_relations")
        for row in cursor.fetchall():
            lines.append(f'  "{row["caller_id"]}" -> "{row["callee_id"]}";')

        lines.append("}")
        return "\n".join(lines)

    def close(self):
        """关闭分析器"""
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
