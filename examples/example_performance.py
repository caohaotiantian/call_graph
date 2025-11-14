#!/usr/bin/env python3
"""
性能优化功能示例

演示如何使用去重和路径限制功能来优化查询性能。
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from call_graph.database import CallGraphDB
from call_graph.analyzer import CallGraphAnalyzer


def example_deduplication():
    """示例1: 演示去重功能"""
    print("="*80)
    print("示例 1: 路径去重功能")
    print("="*80)
    
    db_path = "my.db"
    if not os.path.exists(db_path):
        print(f"\n错误: 数据库文件 {db_path} 不存在")
        print("请先运行: uv run call-graph --database my.db analyze <项目路径>")
        return
    
    analyzer = CallGraphAnalyzer(db_path)
    
    function_name = "calculate"
    print(f"\n查询函数: {function_name}")
    print("说明: 自动去除重复的调用路径，只返回唯一路径\n")
    
    result = analyzer.query_full_call_paths(function_name, max_depth=10)
    
    print(f"✅ 找到 {result['full_count']} 条唯一调用路径（已去重）")
    
    # 显示路径详情
    print(f"\n完整调用路径:")
    for i, detailed_path in enumerate(result['full_paths_detailed'], 1):
        path_parts = []
        for func_info in detailed_path:
            if func_info['name'] == function_name:
                path_parts.append(f"[{func_info['display']}]")
            else:
                path_parts.append(func_info['display'])
        print(f"{i}. {' -> '.join(path_parts)}")
    
    # 性能统计
    if 'performance' in result:
        perf = result['performance']
        print(f"\n📊 性能统计:")
        print(f"   查询时间: {perf['total_time']}秒")
        print(f"   涉及函数: {perf['unique_functions']}个")
    
    analyzer.close()


def example_path_limit():
    """示例2: 演示路径数量限制"""
    print("\n" + "="*80)
    print("示例 2: 路径数量限制（性能优化）")
    print("="*80)
    
    db_path = "my.db"
    if not os.path.exists(db_path):
        print(f"\n错误: 数据库文件 {db_path} 不存在")
        return
    
    analyzer = CallGraphAnalyzer(db_path)
    
    function_name = "process_data"
    print(f"\n查询函数: {function_name}")
    print("说明: 对于大型项目，可以限制最大路径数量以提高性能\n")
    
    # 不限制（默认1000）
    print("1️⃣  默认限制 (max_paths=1000):")
    result_default = analyzer.query_full_call_paths(function_name, max_depth=10, max_paths=1000)
    print(f"   找到 {result_default['full_count']} 条路径")
    if result_default.get('truncated'):
        print(f"   ⚠️  已截断（达到限制）")
    else:
        print(f"   ✅ 未截断（在限制范围内）")
    
    # 限制为10条
    print("\n2️⃣  严格限制 (max_paths=10):")
    result_limited = analyzer.query_full_call_paths(function_name, max_depth=10, max_paths=10)
    print(f"   找到 {result_limited['full_count']} 条路径")
    if result_limited.get('truncated'):
        print(f"   ⚠️  已截断（实际可能更多）")
    else:
        print(f"   ✅ 未截断")
    
    # 显示前几条路径
    print(f"\n显示前 3 条路径:")
    for i, detailed_path in enumerate(result_limited['full_paths_detailed'][:3], 1):
        path_parts = [func['display'] for func in detailed_path]
        print(f"{i}. {' -> '.join(path_parts)}")
    
    analyzer.close()


def example_depth_control():
    """示例3: 演示深度控制"""
    print("\n" + "="*80)
    print("示例 3: 搜索深度控制")
    print("="*80)
    
    db_path = "my.db"
    if not os.path.exists(db_path):
        print(f"\n错误: 数据库文件 {db_path} 不存在")
        return
    
    analyzer = CallGraphAnalyzer(db_path)
    
    function_name = "validate_input"
    print(f"\n查询函数: {function_name}")
    print("说明: 通过限制搜索深度可以减少路径数量，提高查询速度\n")
    
    # 不同深度的对比
    for depth in [3, 5, 10]:
        result = analyzer.query_full_call_paths(function_name, max_depth=depth)
        print(f"深度 {depth:2d}: {result['full_count']:3d} 条路径, "
              f"耗时 {result['performance']['total_time']:.3f}秒")
    
    print("\n💡 提示:")
    print("   - 深度越小，查询越快，但可能遗漏深层路径")
    print("   - 深度越大，结果越完整，但路径数量可能爆炸")
    print("   - 建议根据项目规模选择合适的深度（小项目10，大项目3-5）")
    
    analyzer.close()


def example_performance_comparison():
    """示例4: 性能对比（批量查询 vs 单次查询）"""
    print("\n" + "="*80)
    print("示例 4: 批量查询性能对比")
    print("="*80)
    
    db_path = "my.db"
    if not os.path.exists(db_path):
        print(f"\n错误: 数据库文件 {db_path} 不存在")
        return
    
    analyzer = CallGraphAnalyzer(db_path)
    
    print("\n说明: 新版本使用批量查询优化，一次性获取所有函数信息\n")
    
    function_name = "process_data"
    result = analyzer.query_full_call_paths(function_name, max_depth=10)
    
    perf = result['performance']
    print(f"✨ 批量查询优化效果:")
    print(f"   总查询时间: {perf['total_time']:.3f}秒")
    print(f"   详细信息构建时间: {perf['detail_time']:.3f}秒")
    print(f"   涉及函数数量: {perf['unique_functions']}个")
    print(f"   查询次数: 1次（批量查询）")
    
    print(f"\n💭 旧版本（未优化）:")
    print(f"   查询次数: {perf['unique_functions']}次（每个函数一次）")
    print(f"   预计耗时: {perf['detail_time'] * perf['unique_functions']:.3f}秒（估算）")
    
    if perf['unique_functions'] > 1:
        speedup = perf['unique_functions']
        print(f"\n🚀 性能提升: 约 {speedup}倍")
    
    analyzer.close()


def example_large_project_strategy():
    """示例5: 大型项目优化策略"""
    print("\n" + "="*80)
    print("示例 5: 大型项目优化策略")
    print("="*80)
    
    print("\n针对不同规模项目的推荐配置:\n")
    
    strategies = [
        {
            "name": "小型项目 (< 1000 函数)",
            "depth": 10,
            "max_paths": 1000,
            "reason": "默认配置即可，查询快速"
        },
        {
            "name": "中型项目 (1000-10000 函数)",
            "depth": 8,
            "max_paths": 500,
            "reason": "适当限制，平衡性能和完整性"
        },
        {
            "name": "大型项目 (> 10000 函数)",
            "depth": 5,
            "max_paths": 100,
            "reason": "严格限制，关注核心路径"
        },
        {
            "name": "超大项目 (> 100000 函数)",
            "depth": 3,
            "max_paths": 50,
            "reason": "极度优化，快速响应"
        }
    ]
    
    for i, strategy in enumerate(strategies, 1):
        print(f"{i}. {strategy['name']}")
        print(f"   推荐配置: max_depth={strategy['depth']}, max_paths={strategy['max_paths']}")
        print(f"   原因: {strategy['reason']}")
        print()
    
    print("💡 使用建议:")
    print("   1. 先用默认配置尝试，如果太慢再调整")
    print("   2. 深度控制是最有效的优化手段")
    print("   3. 关注核心调用链，不必追求所有路径")
    print("   4. 使用 --verbose 查看性能统计，辅助调优")


def main():
    """运行所有示例"""
    print("\n" + "="*80)
    print("完整调用路径查询 - 性能优化功能演示")
    print("="*80)
    
    # 运行各个示例
    example_deduplication()
    example_path_limit()
    example_depth_control()
    example_performance_comparison()
    example_large_project_strategy()
    
    print("\n" + "="*80)
    print("演示完成！")
    print("="*80)
    
    print("\n💡 关键功能:")
    print("   ✅ 自动去重 - 消除重复路径")
    print("   ✅ 路径限制 - 避免结果爆炸")
    print("   ✅ 批量查询 - 显著提升性能")
    print("   ✅ 性能统计 - 透明展示耗时")
    
    print("\n📖 更多信息:")
    print("   查看 '性能优化说明.md' 了解技术细节")


if __name__ == "__main__":
    main()

