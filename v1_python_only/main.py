"""
主程序入口
提供命令行接口来执行各种调用图分析操作
"""
import argparse
import json
import sys

from database import DatabaseManager
from call_graph_extractor import CallGraphExtractor
from call_chain_analyzer import CallChainAnalyzer
import config


def extract_calls(db_path: str = None):
    """提取函数调用关系"""
    db = DatabaseManager(db_path)
    extractor = CallGraphExtractor(db)
    extractor.extract_and_save()


def analyze_chains(db_path: str = None, max_depth: int = 5):
    """分析调用链"""
    db = DatabaseManager(db_path)
    analyzer = CallChainAnalyzer(db)
    analyzer.analyze_and_save_all_chains(max_depth)


def show_statistics(db_path: str = None):
    """显示统计信息"""
    db = DatabaseManager(db_path)
    
    print("\n" + "=" * 60)
    print("数据库统计信息")
    print("=" * 60)
    
    stats = db.get_statistics()
    print(f"总符号数: {stats['total_symbols']}")
    print(f"总调用关系: {stats['total_calls']}")
    print(f"已解析调用: {stats['resolved_calls']}")
    print(f"未解析调用: {stats['unresolved_calls']}")
    print(f"总调用链: {stats['total_chains']}")
    
    if stats['total_calls'] > 0:
        print(f"解析率: {stats['resolved_calls']/stats['total_calls']*100:.2f}%")
    
    # 调用统计
    analyzer = CallChainAnalyzer(db)
    call_stats = analyzer.get_call_statistics()
    
    print("\n" + "-" * 60)
    print("调用统计")
    print("-" * 60)
    print(f"有调用关系的函数数: {call_stats['total_functions']}")
    print(f"平均每个函数调用数: {call_stats['average_calls_per_function']:.2f}")
    
    print("\n最常被调用的函数 (Top 10):")
    for idx, (name, count) in enumerate(call_stats['most_called_functions'], 1):
        print(f"  {idx}. {name}: {count} 次")
    
    print("\n调用最多函数的函数 (Top 10):")
    for idx, (name, count) in enumerate(call_stats['most_caller_functions'], 1):
        print(f"  {idx}. {name}: 调用 {count} 个函数")
    
    print("=" * 60)


def query_function_calls(function_name: str, db_path: str = None):
    """查询函数的调用关系"""
    db = DatabaseManager(db_path)
    
    # 查找函数
    symbols = db.find_symbols_by_name(function_name)
    
    if not symbols:
        print(f"未找到函数: {function_name}")
        return
    
    print(f"\n找到 {len(symbols)} 个匹配的函数:\n")
    
    for symbol in symbols:
        print("=" * 60)
        print(f"函数: {symbol['name']}")
        print(f"文件: {symbol['file']}")
        print(f"类型: {symbol['kind']}")
        print(f"位置: {symbol['start_line']}-{symbol['end_line']} 行")
        
        # 查询该函数调用的其他函数
        calls_out = db.get_function_calls(caller_id=symbol['id'])
        print(f"\n该函数调用了 {len(calls_out)} 个函数:")
        for call in calls_out[:10]:  # 只显示前10个
            print(f"  -> {call['callee_name']} (行 {call['call_line']})")
        
        # 查询调用该函数的其他函数
        calls_in = db.get_function_calls(callee_id=symbol['id'])
        print(f"\n该函数被 {len(calls_in)} 个函数调用:")
        for call in calls_in[:10]:  # 只显示前10个
            print(f"  <- {call['caller_name']} (文件: {call['caller_file']}, 行 {call['call_line']})")
        
        # 查询调用链
        chains = db.get_call_chains(start_function_id=symbol['id'])
        print(f"\n从该函数开始的调用链 ({len(chains)} 条):")
        for chain in chains[:10]:  # 只显示前10条
            print(f"  深度 {chain['chain_depth']}: {chain['chain_path']}")
        
        print()


def query_call_chain(start_function: str, end_function: str = None, db_path: str = None, max_depth: int = 5):
    """查询两个函数之间的调用链"""
    db = DatabaseManager(db_path)
    analyzer = CallChainAnalyzer(db)
    
    # 查找起始函数
    start_symbols = db.find_symbols_by_name(start_function)
    if not start_symbols:
        print(f"未找到起始函数: {start_function}")
        return
    
    start_symbol = start_symbols[0]
    print(f"\n查找从 '{start_symbol['name']}' 开始的调用链...\n")
    
    # 查找调用链
    chains = analyzer.find_call_chains(start_symbol['id'], max_depth)
    
    # 如果指定了结束函数，筛选
    if end_function:
        end_symbols = db.find_symbols_by_name(end_function)
        if not end_symbols:
            print(f"未找到结束函数: {end_function}")
            return
        
        end_ids = {s['id'] for s in end_symbols}
        chains = [c for c in chains if c['end_function_id'] in end_ids]
        print(f"找到 {len(chains)} 条从 '{start_function}' 到 '{end_function}' 的调用链:\n")
    else:
        print(f"找到 {len(chains)} 条从 '{start_function}' 开始的调用链:\n")
    
    # 显示调用链
    for idx, chain in enumerate(chains[:20], 1):  # 只显示前20条
        print(f"{idx}. 深度 {chain['chain_depth']}: {chain['chain_path']}")
        
        # 显示详细信息
        intermediate = json.loads(chain['intermediate_calls'])
        for call in intermediate:
            print(f"   {call['caller']} -> {call['callee']} "
                  f"({call['file']}:{call['line']})")
        print()


def find_cycles(db_path: str = None):
    """查找循环依赖"""
    db = DatabaseManager(db_path)
    analyzer = CallChainAnalyzer(db)
    
    print("\n查找循环依赖...\n")
    cycles = analyzer.find_circular_dependencies()
    
    if not cycles:
        print("未发现循环依赖")
        return
    
    print(f"发现 {len(cycles)} 个循环依赖:\n")
    
    for idx, cycle in enumerate(cycles, 1):
        # 获取函数名
        cycle_names = []
        for func_id in cycle:
            symbol = db.get_symbol_by_id(func_id)
            if symbol:
                cycle_names.append(symbol['name'])
        
        print(f"{idx}. {' -> '.join(cycle_names)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Python 函数调用图分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 提取函数调用关系
  python main.py extract
  
  # 分析调用链（最大深度5）
  python main.py analyze --max-depth 5
  
  # 显示统计信息
  python main.py stats
  
  # 查询函数调用关系
  python main.py query --function my_function
  
  # 查询调用链
  python main.py chain --start func1 --end func2
  
  # 查找循环依赖
  python main.py cycles
  
  # 一键执行：提取 + 分析
  python main.py all
        """
    )
    
    parser.add_argument('command', 
                       choices=['extract', 'analyze', 'stats', 'query', 'chain', 'cycles', 'all'],
                       help='要执行的命令')
    parser.add_argument('--db', default=config.DB_PATH, help='数据库文件路径')
    parser.add_argument('--max-depth', type=int, default=5, help='调用链最大深度')
    parser.add_argument('--function', '-f', help='要查询的函数名')
    parser.add_argument('--start', '-s', help='调用链起始函数')
    parser.add_argument('--end', '-e', help='调用链结束函数')
    
    args = parser.parse_args()
    
    try:
        if args.command == 'extract':
            extract_calls(args.db)
        
        elif args.command == 'analyze':
            analyze_chains(args.db, args.max_depth)
        
        elif args.command == 'stats':
            show_statistics(args.db)
        
        elif args.command == 'query':
            if not args.function:
                print("错误: 需要指定 --function 参数")
                sys.exit(1)
            query_function_calls(args.function, args.db)
        
        elif args.command == 'chain':
            if not args.start:
                print("错误: 需要指定 --start 参数")
                sys.exit(1)
            query_call_chain(args.start, args.end, args.db, args.max_depth)
        
        elif args.command == 'cycles':
            find_cycles(args.db)
        
        elif args.command == 'all':
            print("执行完整流程...\n")
            extract_calls(args.db)
            print()
            analyze_chains(args.db, args.max_depth)
            print()
            show_statistics(args.db)
    
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()


