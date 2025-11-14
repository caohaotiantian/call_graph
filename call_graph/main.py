"""
主程序和CLI接口
"""

import argparse
import json
import sys

# 支持相对导入和直接运行
try:
    from .analyzer import CallGraphAnalyzer
    from .analyzer_optimized import CallGraphAnalyzerOptimized
    from .database import CallGraphDB
except ImportError:
    from analyzer import CallGraphAnalyzer
    from analyzer_optimized import CallGraphAnalyzerOptimized
    from database import CallGraphDB


def cmd_analyze(args):
    """分析项目命令"""
    # 根据参数选择分析器
    if hasattr(args, "fast") and args.fast:
        workers = args.workers if hasattr(args, "workers") else None
        analyzer = CallGraphAnalyzerOptimized(args.database, num_workers=workers)
        print(f"使用性能优化模式（多进程并行处理）")
    else:
        analyzer = CallGraphAnalyzer(args.database)

    try:
        if args.clear:
            print("清空现有数据...")
            analyzer.db.clear_all()

        if hasattr(args, "fast") and args.fast:
            batch_size = args.batch_size if hasattr(args, "batch_size") else 100
            stats = analyzer.analyze_project(
                args.project_path,
                exclude_dirs=args.exclude.split(",") if args.exclude else None,
                batch_size=batch_size,
                show_progress=True,
            )
        else:
            stats = analyzer.analyze_project(
                args.project_path,
                exclude_dirs=args.exclude.split(",") if args.exclude else None,
            )

        if not (hasattr(args, "fast") and args.fast):
            # 优化版本已经打印了详细统计，这里只打印普通版本的
            print("\n" + "=" * 50)
            print("分析统计:")
            print("=" * 50)
            print(json.dumps(stats, indent=2, ensure_ascii=False))

    finally:
        analyzer.close()


def cmd_query(args):
    """查询命令"""
    db = CallGraphDB(args.database)

    try:
        if args.callers:
            # 查询调用者
            print(f"\n查询调用 '{args.function}' 的所有函数:\n")
            results = db.get_callers(args.function)

            if not results:
                print(f"没有找到调用 '{args.function}' 的函数")
            else:
                # 按调用者分组（去重）
                caller_groups = {}
                for rel in results:
                    caller_name = rel["caller_name"]
                    if caller_name not in caller_groups:
                        caller_groups[caller_name] = []
                    caller_groups[caller_name].append(rel)

                # 批量获取所有调用者的函数信息
                caller_info_map = {}
                for caller_name in caller_groups.keys():
                    info = db.get_function_info(caller_name)
                    if info:
                        caller_info_map[caller_name] = info

                # 显示结果（已去重）
                for i, (caller_name, rels) in enumerate(
                    sorted(caller_groups.items()), 1
                ):
                    if caller_name in caller_info_map:
                        info = caller_info_map[caller_name]
                        func_display = f"{caller_name}({info['file']}:{info['line']})"
                    else:
                        func_display = f"{caller_name}({rels[0]['caller_file'] or 'unknown'})"

                    # 在 verbose 模式下显示所有调用点
                    if args.verbose and len(rels) > 0:
                        print(f"{i}. {func_display}")
                        for j, rel in enumerate(rels, 1):
                            print(
                                f"   调用点 {j}: {rel['caller_file']}:{rel['call_site_line']}"
                            )
                    else:
                        # 非 verbose 模式，只显示函数定义位置
                        if len(rels) > 1:
                            print(f"{i}. {func_display} (共 {len(rels)} 处调用)")
                        else:
                            print(f"{i}. {func_display}")

        elif args.callees:
            # 查询被调用者
            print(f"\n'{args.function}' 调用的所有函数:\n")
            results = db.get_callees(args.function)

            if not results:
                print(f"'{args.function}' 没有调用其他函数")
            else:
                # 按被调用者分组（去重）
                callee_groups = {}
                for rel in results:
                    callee_name = rel["callee_name"]
                    if callee_name not in callee_groups:
                        callee_groups[callee_name] = []
                    callee_groups[callee_name].append(rel)

                # 批量获取所有被调用者的函数信息
                callee_info_map = {}
                for callee_name in callee_groups.keys():
                    info = db.get_function_info(callee_name)
                    if info:
                        callee_info_map[callee_name] = info

                # 显示结果（已去重）
                for i, (callee_name, rels) in enumerate(
                    sorted(callee_groups.items()), 1
                ):
                    if callee_name in callee_info_map:
                        info = callee_info_map[callee_name]
                        func_display = f"{callee_name}({info['file']}:{info['line']})"
                    else:
                        # 外部函数或未找到定义
                        func_display = (
                            f"{callee_name}({rels[0]['callee_file']})"
                            if rels[0]["callee_file"]
                            else f"{callee_name}(external)"
                        )

                    # 在 verbose 模式下显示所有调用点
                    if args.verbose and len(rels) > 0:
                        print(f"{i}. {func_display}")
                        for j, rel in enumerate(rels, 1):
                            print(
                                f"   调用点 {j}: {rel['caller_file']}:{rel['call_site_line']}"
                            )
                    else:
                        # 非 verbose 模式，只显示函数定义位置
                        if len(rels) > 1:
                            print(f"{i}. {func_display} (共 {len(rels)} 处调用)")
                        else:
                            print(f"{i}. {func_display}")

        elif args.chain:
            # 查询调用链
            print(f"\n'{args.function}' 的调用链 (深度={args.depth}):\n")
            chains = db.get_call_chain(args.function, args.depth)

            if not chains:
                print(f"没有找到 '{args.function}' 的调用链")
            else:
                # 去重：使用 tuple 作为 key
                unique_chains = []
                seen_chains = set()
                for chain in chains:
                    chain_tuple = tuple(chain)
                    if chain_tuple not in seen_chains:
                        seen_chains.add(chain_tuple)
                        unique_chains.append(chain)

                # 收集所有需要查询的函数名
                all_func_names = set()
                for chain in unique_chains:
                    all_func_names.update(chain)

                # 批量获取所有函数的详细信息
                func_info_map = {}
                for func_name in all_func_names:
                    info = db.get_function_info(func_name)
                    if info:
                        func_info_map[func_name] = info

                # 显示去重后的调用链（带详细信息）
                print(f"找到 {len(unique_chains)} 条唯一调用链")
                if len(chains) > len(unique_chains):
                    print(f"(已去除 {len(chains) - len(unique_chains)} 条重复)\n")
                else:
                    print()

                for i, chain in enumerate(unique_chains, 1):
                    chain_display = []
                    for func_name in chain:
                        if func_name in func_info_map:
                            info = func_info_map[func_name]
                            chain_display.append(
                                f"{func_name}({info['file']}:{info['line']})"
                            )
                        else:
                            chain_display.append(f"{func_name}(unknown)")

                    print(f"{i}. {' -> '.join(chain_display)}")

        elif args.fullpath:
            # 查询完整调用路径
            print(f"\n查询 '{args.function}' 的完整调用路径 (最大深度={args.depth}):\n")
            result = db.get_full_call_paths(args.function, args.depth)

            if result["full_count"] == 0:
                print(f"没有找到包含 '{args.function}' 的调用路径")
            else:
                print(f"目标函数: {result['target_function']}")
                print(f"找到 {result['full_count']} 条完整调用路径\n")

                # 直接显示完整路径（带详细信息）
                print("=" * 80)
                print("完整调用路径（入口 -> 目标 -> 叶子）:")
                print("=" * 80)

                for i, detailed_path in enumerate(result["full_paths_detailed"], 1):
                    # 构建路径字符串
                    path_parts = []
                    for func_info in detailed_path:
                        # 高亮目标函数
                        if func_info["name"] == args.function:
                            path_parts.append(f"[{func_info['display']}]")
                        else:
                            path_parts.append(func_info["display"])

                    path_str = " -> ".join(path_parts)
                    print(f"{i}. {path_str}")

                # 显示截断警告（如果有）
                if result.get("truncated", False):
                    print(f"\n⚠️  警告: 路径数量过多，已限制为 {result['max_paths']} 条")
                    print(
                        "   提示: 可以使用 --depth 参数增加搜索深度限制来减少路径数量"
                    )

                # 如果是 verbose 模式，显示额外的统计信息
                if args.verbose:
                    print("\n" + "=" * 80)
                    print("统计信息:")
                    print("=" * 80)
                    print(f"从入口到目标的不同路径: {result['root_count']} 条")
                    print(f"从目标到叶子的不同路径: {result['leaf_count']} 条")
                    print(f"完整路径总数: {result['full_count']} 条")

                    if "performance" in result:
                        perf = result["performance"]
                        print("\n性能信息:")
                        print(f"  总查询时间: {perf['total_time']}秒")
                        print(f"  详细信息构建时间: {perf['detail_time']}秒")
                        print(f"  涉及的唯一函数数: {perf['unique_functions']}")
                        if result.get("truncated", False):
                            print(f"  已截断: 是（达到 {result['max_paths']} 条限制）")

        else:
            print("请指定查询类型: --callers, --callees, --chain, 或 --fullpath")
            sys.exit(1)

    finally:
        db.close()


def cmd_search(args):
    """搜索命令"""
    db = CallGraphDB(args.database)

    try:
        print(f"\n搜索符号 '{args.pattern}':\n")
        results = db.search_symbols(args.pattern)

        if not results:
            print(f"没有找到匹配 '{args.pattern}' 的符号")
        else:
            for i, symbol in enumerate(results, 1):
                print(
                    f"{i}. {symbol['name']} ({symbol['kind']}) - {symbol['file']}:{symbol['start_line']}"
                )
                if args.verbose:
                    print(f"   签名: {symbol['signature']}")
                    print()

    finally:
        db.close()


def cmd_stats(args):
    """统计命令"""
    db = CallGraphDB(args.database)

    try:
        stats = db.get_statistics()

        print("\n" + "=" * 50)
        print("数据库统计信息")
        print("=" * 50)
        print(f"\n总符号数: {stats['total_symbols']}")
        print(f"总调用关系: {stats['total_relations']}")

        print("\n按语言统计:")
        for lang, count in sorted(stats["by_language"].items()):
            print(f"  {lang:15s}: {count:6d} 个符号")

        print("\n按类型统计:")
        for kind, count in sorted(stats["by_kind"].items()):
            print(f"  {kind:15s}: {count:6d} 个")

    finally:
        db.close()


def cmd_export(args):
    """导出命令"""
    analyzer = CallGraphAnalyzer(args.database)

    try:
        print(f"导出调用图为 {args.format} 格式...")

        content = analyzer.export_graph(args.format)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"已保存到: {args.output}")
        else:
            print(content)

    finally:
        analyzer.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="多语言函数调用关系分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:

  # 分析项目（清空旧数据）
  python call-graph.py --database myproject.db analyze /path/to/project --clear
  
  # 分析项目（使用性能优化模式，适合大型项目）⚡
  python call-graph.py --database myproject.db analyze /path/to/project --clear --fast
  
  # 性能优化模式（自定义参数）
  python call-graph.py --database myproject.db analyze /path/to/project --clear --fast --workers 8 --batch-size 200
  
  # 分析项目（排除特定目录）
  python call-graph.py --database myproject.db analyze /path/to/project --exclude "node_modules,build"
  
  # 查看统计信息
  python call-graph.py --database myproject.db stats
  
  # 查询谁调用了某个函数
  python call-graph.py --database myproject.db query main --callers
  
  # 查询某个函数调用了哪些函数
  python call-graph.py --database myproject.db query process_data --callees
  
  # 查询调用链（向下）
  python call-graph.py --database myproject.db query main --chain --depth 3
  
  # 查询完整调用路径（向上+向下）
  python call-graph.py --database myproject.db query process_data --fullpath
  
  # 查询完整路径并显示详细信息
  python call-graph.py --database myproject.db query validate_input --fullpath --verbose
  
  # 搜索函数（模糊匹配）
  python call-graph.py --database myproject.db search "process"
  
  # 搜索函数（显示详细信息）
  python call-graph.py --database myproject.db search "calculate" --verbose
  
  # 导出调用图为 DOT 格式
  python call-graph.py --database myproject.db export --output graph.dot
  
  # 使用 Graphviz 生成可视化图片
  dot -Tpng graph.dot -o graph.png

安装依赖:
  pip install -e .

注意：
  1. --database 参数必须放在子命令之前
  2. 首次使用需要先安装依赖（见上方）
  3. 首次分析建议使用 --clear 清空旧数据
  4. 默认排除 node_modules, .git, __pycache__ 等目录
  
其他运行方式：
  # 使用 Python 模块方式
  python -m call_graph --database myproject.db stats
  
  # 如果已安装到系统（推荐日常使用）
  call-graph --database myproject.db stats
        """,
    )

    parser.add_argument(
        "--database",
        "-d",
        default="call_graph.db",
        help="数据库文件路径 (默认: call_graph.db)",
    )

    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # analyze命令
    analyze_parser = subparsers.add_parser("analyze", help="分析项目")
    analyze_parser.add_argument("project_path", help="项目路径")
    analyze_parser.add_argument("--exclude", "-e", help="要排除的目录，用逗号分隔")
    analyze_parser.add_argument(
        "--clear", "-c", action="store_true", help="清空现有数据"
    )
    analyze_parser.add_argument(
        "--fast", "-f", action="store_true", help="使用性能优化模式（多进程+批量操作）"
    )
    analyze_parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=None,
        help="工作进程数（默认：CPU核心数-1）",
    )
    analyze_parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=100,
        help="批量插入数据库的大小（默认：100）",
    )

    # query命令
    query_parser = subparsers.add_parser("query", help="查询调用关系")
    query_parser.add_argument("function", help="函数名称")
    query_parser.add_argument(
        "--callers", action="store_true", help="查询谁调用了这个函数"
    )
    query_parser.add_argument(
        "--callees", action="store_true", help="查询这个函数调用了谁"
    )
    query_parser.add_argument("--chain", action="store_true", help="查询调用链（向下）")
    query_parser.add_argument(
        "--fullpath",
        action="store_true",
        help="查询完整调用路径（向上追溯到入口，向下追溯到叶子）",
    )
    query_parser.add_argument(
        "--depth", type=int, default=10, help="最大搜索深度 (默认: 10)"
    )
    query_parser.add_argument(
        "--verbose", "-v", action="store_true", help="显示详细信息（包括完整路径）"
    )

    # search命令
    search_parser = subparsers.add_parser("search", help="搜索符号")
    search_parser.add_argument("pattern", help="搜索模式")
    search_parser.add_argument(
        "--verbose", "-v", action="store_true", help="显示详细信息"
    )

    # stats命令
    subparsers.add_parser("stats", help="显示统计信息")

    # export命令
    export_parser = subparsers.add_parser("export", help="导出调用图")
    export_parser.add_argument(
        "--format", "-f", default="dot", choices=["dot"], help="导出格式 (默认: dot)"
    )
    export_parser.add_argument("--output", "-o", help="输出文件路径")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # 执行对应的命令
    if args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "export":
        cmd_export(args)


if __name__ == "__main__":
    main()
