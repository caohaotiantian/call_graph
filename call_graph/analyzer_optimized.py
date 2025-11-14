"""
性能优化版本的分析引擎
支持多进程并行处理和批量数据库操作
"""

import os
import time
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Any, Dict, List, Optional

# 支持相对导入和直接运行
try:
    from .database import CallGraphDB
    from .parsers import LANGUAGE_CONFIG, detect_language, get_parser
except ImportError:
    from database import CallGraphDB
    from parsers import LANGUAGE_CONFIG, detect_language, get_parser


def _process_file_functions(file_path: str) -> List[Dict[str, Any]]:
    """
    工作进程：从单个文件中提取函数定义
    这个函数必须在模块级别，才能被 multiprocessing pickle
    """
    language = detect_language(file_path)
    if not language:
        return []

    try:
        parser = get_parser(language)
        functions = parser.extract_functions(file_path)
        return functions
    except Exception as e:
        print(f"警告: 提取函数失败 {file_path}: {e}")
        return []


def _process_file_calls(args) -> List[Dict[str, Any]]:
    """
    工作进程：从单个文件中提取调用关系
    args: (file_path, all_functions_dict)
    """
    file_path, all_functions_dict = args
    language = detect_language(file_path)
    if not language:
        return []

    try:
        parser = get_parser(language)
        # 将 dict 转换回 list
        all_functions = list(all_functions_dict.values())
        calls = parser.extract_calls(file_path, all_functions)
        return calls
    except Exception as e:
        print(f"警告: 提取调用关系失败 {file_path}: {e}")
        return []


class CallGraphAnalyzerOptimized:
    """
    性能优化版本的调用关系分析器

    优化特性：
    1. 多进程并行处理文件
    2. 批量数据库操作
    3. 进度显示
    4. 事务优化
    """

    def __init__(
        self, db_path: str = "call_graph.db", num_workers: Optional[int] = None
    ):
        self.db = CallGraphDB(db_path)
        self.all_functions: List[Dict[str, Any]] = []
        # 默认使用 CPU 核心数
        self.num_workers = num_workers or max(1, cpu_count() - 1)

    def analyze_project(
        self,
        project_path: str,
        exclude_dirs: Optional[List[str]] = None,
        batch_size: int = 100,
        show_progress: bool = True,
    ) -> Dict[str, Any]:
        """
        分析整个项目（性能优化版本）

        Args:
            project_path: 项目路径
            exclude_dirs: 排除的目录列表
            batch_size: 批量插入数据库的大小
            show_progress: 是否显示进度
        """
        start_time = time.time()

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
        print(f"使用 {self.num_workers} 个工作进程")

        # 收集所有源代码文件
        source_files = self._collect_source_files(project_path, exclude_dirs)
        total_files = len(source_files)

        print(f"找到 {total_files} 个源代码文件")

        # 第一遍：并行提取所有函数定义
        print(f"\n第一遍扫描：提取函数定义（并行处理）...")
        functions_list = self._parallel_extract_functions(source_files, show_progress)

        # 合并结果
        self.all_functions = []
        for functions in functions_list:
            self.all_functions.extend(functions)

        print(f"共提取 {len(self.all_functions)} 个函数定义")

        # 批量保存函数定义到数据库
        print(f"\n保存函数定义到数据库（批量操作，批次大小：{batch_size}）...")
        self._batch_insert_symbols(self.all_functions, batch_size, show_progress)

        # 第二遍：并行提取调用关系
        print(f"\n第二遍扫描：提取调用关系（并行处理）...")
        calls_list = self._parallel_extract_calls(source_files, show_progress)

        # 合并结果
        all_calls = []
        for calls in calls_list:
            all_calls.extend(calls)

        print(f"共提取 {len(all_calls)} 个调用关系")

        # 批量保存调用关系
        print(f"\n保存调用关系到数据库（批量操作，批次大小：{batch_size}）...")
        self._batch_insert_calls(all_calls, batch_size, show_progress)

        # 生成统计报告
        stats = self.db.get_statistics()

        elapsed_time = time.time() - start_time

        print("\n" + "=" * 60)
        print("分析完成！")
        print("=" * 60)
        print(f"总耗时: {elapsed_time:.2f} 秒")
        print(f"处理速度: {total_files / elapsed_time:.1f} 文件/秒")
        print(f"总符号数: {stats['total_symbols']}")
        print(f"总调用关系: {stats['total_relations']}")
        print("\n按语言统计:")
        for lang, count in stats["by_language"].items():
            print(f"  {lang:15s}: {count:6d} 个符号")
        print("=" * 60)

        stats["elapsed_time"] = elapsed_time
        stats["files_per_second"] = total_files / elapsed_time

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

    def _parallel_extract_functions(
        self, source_files: List[str], show_progress: bool = True
    ) -> List[List[Dict]]:
        """
        并行提取函数定义
        """
        total = len(source_files)
        results = []

        with Pool(processes=self.num_workers) as pool:
            if show_progress:
                # 使用 imap 可以显示进度
                processed = 0
                for result in pool.imap_unordered(
                    _process_file_functions, source_files, chunksize=10
                ):
                    results.append(result)
                    processed += 1
                    if processed % 50 == 0 or processed == total:
                        self._print_progress(processed, total, "提取函数")
                print()  # 换行
            else:
                results = pool.map(_process_file_functions, source_files, chunksize=10)

        return results

    def _parallel_extract_calls(
        self, source_files: List[str], show_progress: bool = True
    ) -> List[List[Dict]]:
        """
        并行提取调用关系
        """
        total = len(source_files)
        results = []

        # 创建函数字典（用于传递给工作进程）
        # 使用 dict 减少数据传输量
        functions_dict = {
            f"{func['name']}:{func['file']}": func for func in self.all_functions
        }

        # 准备参数
        args_list = [(file_path, functions_dict) for file_path in source_files]

        with Pool(processes=self.num_workers) as pool:
            if show_progress:
                processed = 0
                for result in pool.imap_unordered(
                    _process_file_calls, args_list, chunksize=10
                ):
                    results.append(result)
                    processed += 1
                    if processed % 50 == 0 or processed == total:
                        self._print_progress(processed, total, "提取调用")
                print()  # 换行
            else:
                results = pool.map(_process_file_calls, args_list, chunksize=10)

        return results

    def _batch_insert_symbols(
        self, symbols: List[Dict], batch_size: int, show_progress: bool = True
    ):
        """
        批量插入符号到数据库
        """
        total = len(symbols)
        inserted = 0

        # 使用事务批量插入
        self.db.conn.execute("BEGIN TRANSACTION")

        try:
            for i in range(0, total, batch_size):
                batch = symbols[i : i + batch_size]
                for symbol in batch:
                    self.db.insert_symbol(symbol)

                inserted += len(batch)

                if show_progress and (inserted % 500 == 0 or inserted == total):
                    self._print_progress(inserted, total, "保存符号")

            self.db.conn.commit()

            if show_progress:
                print()  # 换行
        except Exception as e:
            self.db.conn.rollback()
            raise e

    def _batch_insert_calls(
        self, calls: List[Dict], batch_size: int, show_progress: bool = True
    ):
        """
        批量插入调用关系到数据库
        """
        total = len(calls)
        inserted = 0

        # 使用事务批量插入
        self.db.conn.execute("BEGIN TRANSACTION")

        try:
            for i in range(0, total, batch_size):
                batch = calls[i : i + batch_size]
                for call in batch:
                    self.db.insert_call_relation(call)

                inserted += len(batch)

                if show_progress and (inserted % 1000 == 0 or inserted == total):
                    self._print_progress(inserted, total, "保存调用")

            self.db.conn.commit()

            if show_progress:
                print()  # 换行
        except Exception as e:
            self.db.conn.rollback()
            raise e

    def _print_progress(self, current: int, total: int, task: str):
        """
        打印进度条
        """
        percent = current / total * 100
        bar_length = 40
        filled = int(bar_length * current / total)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(
            f"\r{task}: [{bar}] {current}/{total} ({percent:.1f}%)", end="", flush=True
        )

    # 保留原有的查询方法
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
        """查询函数的完整调用路径（向上+向下）"""
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
