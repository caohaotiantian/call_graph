"""
示例：使用完整调用路径查询功能

展示如何使用新的 --fullpath 功能
"""
import sys
import os

# 添加父目录到路径，以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from call_graph.analyzer import CallGraphAnalyzer
from call_graph.database import CallGraphDB


def example_full_path_query():
    """示例：使用完整调用路径查询"""
    print("="*70)
    print("示例：完整调用路径查询")
    print("="*70)
    
    # 使用已有的数据库（假设已经分析过）
    db_path = "my.db"
    
    if not os.path.exists(db_path):
        print(f"\n错误: 数据库文件 {db_path} 不存在")
        print("请先运行以下命令分析项目：")
        print(f"uv run call-graph --database {db_path} analyze examples/sample_project --clear")
        return
    
    db = CallGraphDB(db_path)
    
    try:
        # 查询中间函数的完整路径
        function_name = "process_data"
        print(f"\n查询函数: {function_name}")
        print("-"*70)
        
        result = db.get_full_call_paths(function_name, max_depth=10)
        
        if result['full_count'] == 0:
            print(f"没有找到包含 '{function_name}' 的调用路径")
            return
        
        # 显示摘要
        print(f"\n📊 摘要:")
        print(f"   目标函数: {result['target_function']}")
        print(f"   从入口到目标的路径: {result['root_count']} 条")
        print(f"   从目标到叶子的路径: {result['leaf_count']} 条")
        print(f"   完整路径: {result['full_count']} 条")
        
        # 显示从入口到目标的路径
        print(f"\n🔼 从入口函数到目标函数的路径:")
        for i, path in enumerate(result['paths_from_root'], 1):
            print(f"   {i}. {' -> '.join(path)}")
        
        # 显示从目标到叶子的路径
        print(f"\n🔽 从目标函数到叶子函数的路径:")
        for i, path in enumerate(result['paths_to_leaf'], 1):
            print(f"   {i}. {' -> '.join(path)}")
        
        # 显示完整路径（高亮目标函数）
        print(f"\n🔗 完整调用路径（入口 -> 目标 -> 叶子）:")
        for i, path in enumerate(result['full_paths'], 1):
            # 高亮显示目标函数
            path_str = ' -> '.join(
                f"[{func}]" if func == function_name else func
                for func in path
            )
            print(f"   {i}. {path_str}")
        
        print("\n" + "="*70)
        
    finally:
        db.close()


def example_compare_chain_vs_fullpath():
    """示例：对比 --chain 和 --fullpath 的区别"""
    print("\n" + "="*70)
    print("对比：--chain vs --fullpath")
    print("="*70)
    
    db_path = "my.db"
    
    if not os.path.exists(db_path):
        print(f"\n错误: 数据库文件 {db_path} 不存在")
        return
    
    db = CallGraphDB(db_path)
    
    try:
        function_name = "process_data"
        
        # 使用 --chain (向下)
        print(f"\n1️⃣  使用 --chain (仅向下查询):")
        print("-"*70)
        chains = db.get_call_chain(function_name, depth=10)
        print(f"从 '{function_name}' 向下的调用链:")
        for i, chain in enumerate(chains, 1):
            print(f"   {i}. {' -> '.join(chain)}")
        
        # 使用 --fullpath (双向)
        print(f"\n2️⃣  使用 --fullpath (双向查询):")
        print("-"*70)
        result = db.get_full_call_paths(function_name, max_depth=10)
        
        print(f"向上追溯到入口:")
        for i, path in enumerate(result['paths_from_root'], 1):
            print(f"   {i}. {' -> '.join(path)}")
        
        print(f"\n向下追溯到叶子:")
        for i, path in enumerate(result['paths_to_leaf'], 1):
            print(f"   {i}. {' -> '.join(path)}")
        
        print(f"\n✨ 结论:")
        print(f"   --chain:    只能看到从 '{function_name}' 向下的调用")
        print(f"   --fullpath: 可以看到 '{function_name}' 的完整上下文")
        print(f"              （谁调用了它 + 它调用了谁）")
        
        print("\n" + "="*70)
        
    finally:
        db.close()


def example_leaf_function():
    """示例：查询叶子函数的完整路径"""
    print("\n" + "="*70)
    print("示例：查询叶子函数")
    print("="*70)
    
    db_path = "my.db"
    
    if not os.path.exists(db_path):
        print(f"\n错误: 数据库文件 {db_path} 不存在")
        return
    
    db = CallGraphDB(db_path)
    
    try:
        function_name = "validate_input"
        print(f"\n查询叶子函数: {function_name}")
        print("-"*70)
        
        result = db.get_full_call_paths(function_name, max_depth=10)
        
        print(f"\n完整调用路径:")
        for i, detailed_path in enumerate(result['full_paths_detailed'], 1):
            # 高亮显示目标函数，显示详细信息
            path_parts = []
            for func_info in detailed_path:
                if func_info['name'] == function_name:
                    path_parts.append(f"[{func_info['display']}]")
                else:
                    path_parts.append(func_info['display'])
            
            path_str = ' -> '.join(path_parts)
            print(f"   {i}. {path_str}")
        
        print(f"\n💡 说明:")
        print(f"   '{function_name}' 是一个叶子函数（或接近叶子）")
        print(f"   可以清楚地看到从入口函数到它的完整路径")
        print(f"   这对于理解错误处理函数或工具函数特别有用")
        
        print("\n" + "="*70)
        
    finally:
        db.close()


def example_entry_function():
    """示例：查询入口函数的完整路径"""
    print("\n" + "="*70)
    print("示例：查询入口函数")
    print("="*70)
    
    db_path = "my.db"
    
    if not os.path.exists(db_path):
        print(f"\n错误: 数据库文件 {db_path} 不存在")
        return
    
    db = CallGraphDB(db_path)
    
    try:
        function_name = "main"
        print(f"\n查询入口函数: {function_name}")
        print("-"*70)
        
        result = db.get_full_call_paths(function_name, max_depth=10)
        
        print(f"\n📊 统计:")
        print(f"   '{function_name}' 调用了 {result['leaf_count']} 条路径")
        
        print(f"\n前 10 条调用路径:")
        for i, detailed_path in enumerate(result['full_paths_detailed'][:10], 1):
            path_str = ' -> '.join(f['display'] for f in detailed_path)
            print(f"   {i}. {path_str}")
        
        if result['full_count'] > 10:
            print(f"\n   ... 还有 {result['full_count'] - 10} 条路径")
        
        print(f"\n💡 说明:")
        print(f"   '{function_name}' 是入口函数")
        print(f"   可以看到整个程序的所有调用路径")
        print(f"   这对于理解程序整体结构非常有用")
        
        print("\n" + "="*70)
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("完整调用路径查询功能演示")
    print("="*70)
    print("\n提示: 请确保已经分析过项目并生成了数据库")
    print("运行命令: uv run call-graph --database my.db analyze examples/sample_project --clear")
    print("\n" + "="*70)
    
    # 运行示例
    example_full_path_query()
    example_compare_chain_vs_fullpath()
    example_leaf_function()
    example_entry_function()
    
    print("\n✅ 所有示例运行完成！")
    print("\n更多信息请查看：新功能说明-完整调用路径.md")

