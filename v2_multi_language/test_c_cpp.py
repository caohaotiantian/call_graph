"""
测试 C/C++ 项目分析功能
"""
import os
import sys
from pathlib import Path

from unified_analyzer import UnifiedAnalyzer
from graph_database import GraphDatabase
from tsg_engine import check_tsg_installation
from rich.console import Console
from rich.table import Table

console = Console()


def test_c_example():
    """测试 C 示例代码分析"""
    console.print("\n[bold cyan]测试 C 代码分析...[/bold cyan]")
    
    examples_dir = Path(__file__).parent / 'examples'
    c_file = examples_dir / 'example.c'
    
    if not c_file.exists():
        console.print(f"[red]C 示例文件不存在: {c_file}[/red]")
        return False
    
    # 创建分析器
    analyzer = UnifiedAnalyzer('test_c_cpp.db')
    
    # 分析 C 文件
    try:
        project_id = analyzer.analyze_project(
            str(examples_dir),
            project_name='C Example',
            languages=['c']
        )
        
        console.print(f"[green]✓ C 项目分析完成，项目ID: {project_id}[/green]")
        
        # 验证结果
        db = GraphDatabase('test_c_cpp.db')
        
        # 查找函数
        functions = db.find_nodes(
            project_id=project_id,
            node_type='FUNCTION'
        )
        
        console.print(f"\n找到 {len(functions)} 个函数:")
        
        table = Table(title="C 函数列表")
        table.add_column("函数名", style="cyan")
        table.add_column("文件", style="green")
        table.add_column("行号", style="yellow")
        
        for func in functions[:10]:  # 只显示前10个
            table.add_row(
                func['name'],
                Path(func['file_path']).name,
                str(func['start_line'])
            )
        
        console.print(table)
        
        # 查找调用关系
        calls = db.get_edges(
            project_id=project_id,
            edge_type='CALLS'
        )
        
        console.print(f"\n找到 {len(calls)} 个函数调用")
        
        # 显示 main 函数的调用关系
        main_funcs = [f for f in functions if f['name'] == 'main']
        if main_funcs:
            console.print("\n[bold]main 函数调用分析:[/bold]")
            main_func = main_funcs[0]
            
            main_calls = db.get_edges(
                project_id=project_id,
                source_id=main_func['id'],
                edge_type='CALLS'
            )
            
            console.print(f"main 调用了 {len(main_calls)} 个函数:")
            for call in main_calls:
                target = db.get_node(call['target_id'])
                if target:
                    console.print(f"  -> {target['name']} (行 {call['line']})")
        
        return True
    
    except Exception as e:
        console.print(f"[red]✗ C 代码分析失败: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        return False


def test_cpp_example():
    """测试 C++ 示例代码分析"""
    console.print("\n[bold cyan]测试 C++ 代码分析...[/bold cyan]")
    
    examples_dir = Path(__file__).parent / 'examples'
    cpp_file = examples_dir / 'example.cpp'
    
    if not cpp_file.exists():
        console.print(f"[red]C++ 示例文件不存在: {cpp_file}[/red]")
        return False
    
    # 创建分析器
    analyzer = UnifiedAnalyzer('test_c_cpp.db')
    
    # 分析 C++ 文件
    try:
        project_id = analyzer.analyze_project(
            str(examples_dir),
            project_name='C++ Example',
            languages=['cpp']
        )
        
        console.print(f"[green]✓ C++ 项目分析完成，项目ID: {project_id}[/green]")
        
        # 验证结果
        db = GraphDatabase('test_c_cpp.db')
        
        # 查找类
        classes = db.find_nodes(
            project_id=project_id,
            node_type='CLASS'
        )
        
        console.print(f"\n找到 {len(classes)} 个类:")
        
        table = Table(title="C++ 类列表")
        table.add_column("类名", style="cyan")
        table.add_column("文件", style="green")
        table.add_column("行号", style="yellow")
        
        for cls in classes:
            table.add_row(
                cls['name'],
                Path(cls['file_path']).name,
                str(cls['start_line'])
            )
        
        console.print(table)
        
        # 查找函数
        functions = db.find_nodes(
            project_id=project_id,
            node_type='FUNCTION'
        )
        
        console.print(f"\n找到 {len(functions)} 个函数")
        
        # 查找方法
        methods = db.find_nodes(
            project_id=project_id,
            node_type='METHOD'
        )
        
        console.print(f"找到 {len(methods)} 个方法")
        
        # 查找继承关系
        inheritance = db.get_edges(
            project_id=project_id,
            edge_type='INHERITS'
        )
        
        if inheritance:
            console.print(f"\n找到 {len(inheritance)} 个继承关系:")
            for edge in inheritance:
                derived = db.get_node(edge['source_id'])
                base = db.get_node(edge['target_id'])
                if derived and base:
                    console.print(f"  {derived['name']} -> {base['name']}")
        
        # 查找方法调用
        method_calls = db.get_edges(
            project_id=project_id,
            edge_type='METHOD_CALL'
        )
        
        console.print(f"\n找到 {len(method_calls)} 个方法调用")
        
        return True
    
    except Exception as e:
        console.print(f"[red]✗ C++ 代码分析失败: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    console.print("[bold]C/C++ 代码分析功能测试[/bold]")
    console.print("=" * 60)
    
    # 检查环境
    console.print("\n[cyan]检查环境...[/cyan]")
    
    if not check_tsg_installation():
        console.print("[red]✗ tree-sitter-graph 未安装[/red]")
        console.print("\n请先安装:")
        console.print("  cargo install --features cli tree-sitter-graph")
        return 1
    
    console.print("[green]✓ tree-sitter-graph 已安装[/green]")
    
    # 检查 TSG 规则文件
    tsg_rules_dir = Path(__file__).parent / 'tsg_rules'
    c_rules = tsg_rules_dir / 'c.tsg'
    cpp_rules = tsg_rules_dir / 'cpp.tsg'
    
    if not c_rules.exists():
        console.print(f"[red]✗ C 规则文件不存在: {c_rules}[/red]")
        return 1
    
    if not cpp_rules.exists():
        console.print(f"[red]✗ C++ 规则文件不存在: {cpp_rules}[/red]")
        return 1
    
    console.print(f"[green]✓ TSG 规则文件存在[/green]")
    
    # 运行测试
    results = {
        'C 分析': test_c_example(),
        'C++ 分析': test_cpp_example()
    }
    
    # 显示测试结果
    console.print("\n" + "=" * 60)
    console.print("[bold]测试结果汇总[/bold]\n")
    
    table = Table(title="测试结果")
    table.add_column("测试项", style="cyan")
    table.add_column("状态", style="green")
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        style = "green" if result else "red"
        table.add_row(test_name, f"[{style}]{status}[/{style}]")
    
    console.print(table)
    
    # 返回状态
    if all(results.values()):
        console.print("\n[bold green]所有测试通过！[/bold green]")
        return 0
    else:
        console.print("\n[bold red]部分测试失败[/bold red]")
        return 1


if __name__ == '__main__':
    sys.exit(main())

