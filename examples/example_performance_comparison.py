#!/usr/bin/env python3
"""
性能对比示例：标准模式 vs 优化模式
"""
import sys
import os
import time

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from call_graph.analyzer import CallGraphAnalyzer
from call_graph.analyzer_optimized import CallGraphAnalyzerOptimized


def test_standard_mode(project_path: str, db_path: str):
    """
    测试标准模式
    """
    print("="*70)
    print("测试标准模式")
    print("="*70)
    
    start_time = time.time()
    
    analyzer = CallGraphAnalyzer(db_path)
    try:
        analyzer.db.clear_all()
        stats = analyzer.analyze_project(project_path)
    finally:
        analyzer.close()
    
    elapsed = time.time() - start_time
    
    print(f"\n标准模式完成:")
    print(f"  耗时: {elapsed:.2f} 秒")
    print(f"  符号数: {stats['total_symbols']}")
    print(f"  调用关系: {stats['total_relations']}")
    
    return elapsed, stats


def test_optimized_mode(project_path: str, db_path: str, workers: int = None):
    """
    测试优化模式
    """
    print("\n" + "="*70)
    print("测试性能优化模式")
    print("="*70)
    
    start_time = time.time()
    
    analyzer = CallGraphAnalyzerOptimized(db_path, num_workers=workers)
    try:
        analyzer.db.clear_all()
        stats = analyzer.analyze_project(
            project_path,
            batch_size=100,
            show_progress=True
        )
    finally:
        analyzer.close()
    
    elapsed = time.time() - start_time
    
    return elapsed, stats


def main():
    """
    主函数
    """
    # 使用示例项目
    project_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'examples',
        'sample_project'
    )
    
    if not os.path.exists(project_path):
        print(f"错误: 示例项目不存在: {project_path}")
        print("请先创建示例项目")
        return
    
    print("Call Graph 性能对比测试")
    print("="*70)
    print(f"测试项目: {project_path}")
    print()
    
    # 测试标准模式
    db_standard = "test_standard.db"
    time_standard, stats_standard = test_standard_mode(project_path, db_standard)
    
    # 测试优化模式
    db_optimized = "test_optimized.db"
    time_optimized, stats_optimized = test_optimized_mode(project_path, db_optimized)
    
    # 性能对比
    print("\n" + "="*70)
    print("性能对比")
    print("="*70)
    print(f"标准模式耗时:   {time_standard:.2f} 秒")
    print(f"优化模式耗时:   {time_optimized:.2f} 秒")
    print(f"性能提升:      {time_standard / time_optimized:.2f}x")
    print("="*70)
    
    # 清理测试数据库
    for db in [db_standard, db_optimized]:
        if os.path.exists(db):
            os.remove(db)
            print(f"已删除测试数据库: {db}")


if __name__ == '__main__':
    main()

