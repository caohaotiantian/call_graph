"""
使用示例：展示如何使用call-graph工具的Python API
"""
from call_graph.analyzer import CallGraphAnalyzer
from call_graph.database import CallGraphDB


def example_1_analyze_project():
    """示例1: 分析整个项目"""
    print("="*60)
    print("示例1: 分析整个项目")
    print("="*60)
    
    analyzer = CallGraphAnalyzer("example.db")
    
    try:
        # 分析项目
        stats = analyzer.analyze_project(
            project_path="./sample_project",
            exclude_dirs=['venv', '__pycache__']
        )
        
        print("\n分析完成！统计信息:")
        print(f"总符号数: {stats['total_symbols']}")
        print(f"总调用关系: {stats['total_relations']}")
        
    finally:
        analyzer.close()


def example_2_query_callers():
    """示例2: 查询谁调用了某个函数"""
    print("\n" + "="*60)
    print("示例2: 查询谁调用了某个函数")
    print("="*60)
    
    db = CallGraphDB("example.db")
    
    try:
        function_name = "process_data"
        callers = db.get_callers(function_name)
        
        print(f"\n调用 '{function_name}' 的函数:")
        for caller in callers:
            print(f"  - {caller['caller_name']} ({caller['caller_file']}:{caller['call_site_line']})")
        
    finally:
        db.close()


def example_3_query_callees():
    """示例3: 查询某个函数调用了哪些函数"""
    print("\n" + "="*60)
    print("示例3: 查询某个函数调用了哪些函数")
    print("="*60)
    
    db = CallGraphDB("example.db")
    
    try:
        function_name = "main"
        callees = db.get_callees(function_name)
        
        print(f"\n'{function_name}' 调用的函数:")
        for callee in callees:
            print(f"  - {callee['callee_name']}")
        
    finally:
        db.close()


def example_4_query_call_chain():
    """示例4: 查询完整的调用链"""
    print("\n" + "="*60)
    print("示例4: 查询完整的调用链")
    print("="*60)
    
    db = CallGraphDB("example.db")
    
    try:
        function_name = "main"
        chains = db.get_call_chain(function_name, depth=3)
        
        print(f"\n'{function_name}' 的调用链:")
        for i, chain in enumerate(chains, 1):
            print(f"{i}. {' -> '.join(chain)}")
        
    finally:
        db.close()


def example_5_search_functions():
    """示例5: 搜索函数"""
    print("\n" + "="*60)
    print("示例5: 搜索函数")
    print("="*60)
    
    db = CallGraphDB("example.db")
    
    try:
        pattern = "process"
        results = db.search_symbols(pattern)
        
        print(f"\n搜索 '{pattern}' 的结果:")
        for symbol in results:
            print(f"  - {symbol['name']} ({symbol['language']}) - {symbol['file']}:{symbol['start_line']}")
        
    finally:
        db.close()


def example_6_analyze_single_file():
    """示例6: 分析单个文件"""
    print("\n" + "="*60)
    print("示例6: 分析单个文件")
    print("="*60)
    
    analyzer = CallGraphAnalyzer("example.db")
    
    try:
        result = analyzer.analyze_file("./sample_project/main.py")
        
        print(f"\n文件: {result['file']}")
        print(f"语言: {result['language']}")
        print(f"找到 {len(result['functions'])} 个函数")
        print(f"找到 {len(result['calls'])} 个调用关系")
        
        print("\n函数列表:")
        for func in result['functions']:
            print(f"  - {func['name']} (行 {func['start_line']}-{func['end_line']})")
        
    finally:
        analyzer.close()


def example_7_export_graph():
    """示例7: 导出调用图"""
    print("\n" + "="*60)
    print("示例7: 导出调用图为Graphviz格式")
    print("="*60)
    
    analyzer = CallGraphAnalyzer("example.db")
    
    try:
        dot_content = analyzer.export_graph('dot')
        
        # 保存到文件
        with open("call_graph.dot", "w", encoding="utf-8") as f:
            f.write(dot_content)
        
        print("\n调用图已导出到 call_graph.dot")
        print("可以使用以下命令生成图片:")
        print("  dot -Tpng call_graph.dot -o call_graph.png")
        
    finally:
        analyzer.close()


def example_8_statistics():
    """示例8: 获取统计信息"""
    print("\n" + "="*60)
    print("示例8: 获取统计信息")
    print("="*60)
    
    db = CallGraphDB("example.db")
    
    try:
        stats = db.get_statistics()
        
        print("\n数据库统计:")
        print(f"总符号数: {stats['total_symbols']}")
        print(f"总调用关系: {stats['total_relations']}")
        
        print("\n按语言统计:")
        for lang, count in stats['by_language'].items():
            print(f"  {lang}: {count} 个符号")
        
        print("\n按类型统计:")
        for kind, count in stats['by_kind'].items():
            print(f"  {kind}: {count} 个")
        
    finally:
        db.close()


if __name__ == "__main__":
    # 运行所有示例
    print("\nCall Graph Analyzer - 使用示例\n")
    
    # 注意: 这些示例需要一个已经分析过的数据库
    # 首先运行 example_1 来创建数据库
    
    try:
        example_1_analyze_project()
        example_2_query_callers()
        example_3_query_callees()
        example_4_query_call_chain()
        example_5_search_functions()
        example_6_analyze_single_file()
        example_7_export_graph()
        example_8_statistics()
    except Exception as e:
        print(f"\n错误: {e}")
        print("\n提示: 请确保已经有一些源代码可供分析")

