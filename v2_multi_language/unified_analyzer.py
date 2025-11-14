"""
统一多语言代码分析器
使用 tree-sitter-graph 提取函数调用图和数据流图
"""
import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set
from collections import defaultdict

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

import config_v2 as config
from tsg_engine import TSGEngine, check_tsg_installation, install_instructions
from graph_database import GraphDatabase

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

console = Console()


class UnifiedAnalyzer:
    """统一代码分析器"""
    
    def __init__(self, db_path: str = None):
        self.db = GraphDatabase(db_path)
        self.tsg_engine = TSGEngine()
        self.console = Console()
    
    def analyze_project(
        self,
        project_path: str,
        project_name: str = None,
        languages: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> str:
        """
        分析项目
        
        Args:
            project_path: 项目路径
            project_name: 项目名称
            languages: 要分析的语言列表
            exclude_patterns: 排除模式列表
        
        Returns:
            项目ID
        """
        project_path = Path(project_path).resolve()
        if not project_path.exists():
            raise FileNotFoundError(f"Project path not found: {project_path}")
        
        project_name = project_name or project_path.name
        exclude_patterns = exclude_patterns or config.EXCLUDE_PATTERNS
        
        console.print(f"\n[bold cyan]Analyzing project: {project_name}[/bold cyan]")
        console.print(f"Path: {project_path}")
        
        start_time = time.time()
        
        # 创建项目记录
        project_id = self.db.create_project(
            name=project_name,
            root_path=str(project_path),
            languages=languages
        )
        
        # 清空旧数据
        self.db.clear_project_data(project_id)
        
        # 收集源文件
        source_files = self._collect_source_files(
            project_path,
            languages,
            exclude_patterns
        )
        
        if not source_files:
            console.print("[yellow]No source files found![/yellow]")
            return project_id
        
        console.print(f"Found {len(source_files)} source files")
        
        # 按语言分组
        files_by_language = defaultdict(list)
        for file_path, language in source_files:
            files_by_language[language].append(file_path)
        
        # 分析统计
        total_stats = {
            'total_files': 0,
            'total_nodes': 0,
            'total_edges': 0,
            'total_functions': 0,
            'total_classes': 0,
            'total_dataflows': 0,
        }
        
        # 按语言分析
        for language, files in files_by_language.items():
            console.print(f"\n[bold green]Analyzing {language} files...[/bold green]")
            
            stats = self._analyze_language_files(
                project_id,
                language,
                files
            )
            
            # 累计统计
            for key in total_stats:
                total_stats[key] += stats.get(key, 0)
        
        # 保存统计
        duration = time.time() - start_time
        total_stats['analysis_duration_seconds'] = duration
        self.db.save_statistics(project_id, total_stats)
        
        # 显示结果
        console.print(f"\n[bold green]✓ Analysis complete![/bold green]")
        console.print(f"Duration: {duration:.2f} seconds")
        
        self._display_statistics(total_stats)
        
        return project_id
    
    def _collect_source_files(
        self,
        project_path: Path,
        languages: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> List[tuple]:
        """
        收集源文件
        
        Returns:
            (file_path, language) 元组列表
        """
        source_files = []
        languages = languages or list(config.SUPPORTED_LANGUAGES.keys())
        
        # 构建扩展名到语言的映射
        ext_to_lang = {}
        for lang in languages:
            if lang in config.SUPPORTED_LANGUAGES:
                for ext in config.SUPPORTED_LANGUAGES[lang]['extensions']:
                    ext_to_lang[ext] = lang
        
        # 遍历目录
        for root, dirs, files in os.walk(project_path):
            # 过滤排除的目录
            dirs[:] = [d for d in dirs if not self._should_exclude(d, exclude_patterns)]
            
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix
                
                if ext in ext_to_lang:
                    if not self._should_exclude(str(file_path), exclude_patterns):
                        source_files.append((str(file_path), ext_to_lang[ext]))
        
        return source_files
    
    def _should_exclude(self, path: str, patterns: List[str]) -> bool:
        """检查路径是否应该排除"""
        path_str = str(path)
        for pattern in patterns:
            if pattern in path_str:
                return True
        return False
    
    def _analyze_language_files(
        self,
        project_id: str,
        language: str,
        files: List[str]
    ) -> Dict:
        """分析特定语言的文件"""
        lang_config = config.SUPPORTED_LANGUAGES.get(language)
        if not lang_config:
            logger.warning(f"Unsupported language: {language}")
            return {}
        
        rules_file = config.TSG_RULES_DIR / lang_config['tsg_rules']
        if not rules_file.exists():
            logger.warning(f"TSG rules file not found: {rules_file}")
            return {}
        
        # 批量提取图数据
        graphs = self.tsg_engine.batch_extract(
            files,
            str(rules_file),
            language,
            parallel=True
        )
        
        # 处理和存储图数据
        stats = {
            'total_files': len(files),
            'total_nodes': 0,
            'total_edges': 0,
            'total_functions': 0,
            'total_classes': 0,
        }
        
        all_nodes = []
        all_edges = []
        
        for graph_data in graphs:
            if 'error' in graph_data:
                logger.warning(f"Error in {graph_data.get('source_file')}: {graph_data['error']}")
                continue
            
            # 处理节点
            nodes = graph_data.get('nodes', [])
            for node in nodes:
                node['project_id'] = project_id
                node['language'] = language
                node['file_path'] = graph_data.get('source_file', '')
                all_nodes.append(node)
                
                # 统计
                if node.get('node_type') == 'FUNCTION':
                    stats['total_functions'] += 1
                elif node.get('node_type') == 'CLASS':
                    stats['total_classes'] += 1
            
            # 处理边
            edges = graph_data.get('edges', [])
            for edge in edges:
                edge['project_id'] = project_id
                edge['file_path'] = graph_data.get('source_file', '')
                all_edges.append(edge)
        
        # 批量存储
        if all_nodes:
            stats['total_nodes'] = self.db.batch_insert_nodes(all_nodes)
        
        if all_edges:
            stats['total_edges'] = self.db.batch_insert_edges(all_edges)
        
        return stats
    
    def _display_statistics(self, stats: Dict):
        """显示统计信息"""
        table = Table(title="Analysis Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green", justify="right")
        
        table.add_row("Total Files", str(stats['total_files']))
        table.add_row("Total Nodes", str(stats['total_nodes']))
        table.add_row("Total Edges", str(stats['total_edges']))
        table.add_row("Functions", str(stats['total_functions']))
        table.add_row("Classes", str(stats['total_classes']))
        
        console.print(table)
    
    def query_call_graph(
        self,
        project_id: str,
        function_name: str = None,
        max_depth: int = 5
    ):
        """查询调用图"""
        console.print(f"\n[bold cyan]Call Graph Query[/bold cyan]")
        
        if function_name:
            nodes = self.db.find_nodes(
                project_id=project_id,
                node_type='FUNCTION',
                name=function_name
            )
            
            if not nodes:
                console.print(f"[yellow]Function not found: {function_name}[/yellow]")
                return
            
            node = nodes[0]
            console.print(f"\nFunction: {node['name']}")
            console.print(f"File: {node['file_path']}")
            console.print(f"Line: {node['start_line']}")
            
            # 查询调用关系
            calls_out = self.db.get_edges(
                project_id=project_id,
                source_id=node['id'],
                edge_type='CALLS'
            )
            
            calls_in = self.db.get_edges(
                project_id=project_id,
                target_id=node['id'],
                edge_type='CALLS'
            )
            
            console.print(f"\n[green]Calls {len(calls_out)} functions:[/green]")
            for edge in calls_out[:10]:
                target = self.db.get_node(edge['target_id'])
                if target:
                    console.print(f"  -> {target['name']}")
            
            console.print(f"\n[green]Called by {len(calls_in)} functions:[/green]")
            for edge in calls_in[:10]:
                source = self.db.get_node(edge['source_id'])
                if source:
                    console.print(f"  <- {source['name']}")
    
    def export_graph(
        self,
        project_id: str,
        output_file: str,
        format: str = 'dot'
    ):
        """导出图数据"""
        console.print(f"[cyan]Exporting graph to {output_file}...[/cyan]")
        
        nodes = self.db.find_nodes(project_id=project_id)
        edges = self.db.get_edges(project_id=project_id)
        
        if format == 'dot':
            self._export_dot(nodes, edges, output_file)
        elif format == 'json':
            self._export_json(nodes, edges, output_file)
        else:
            console.print(f"[red]Unsupported format: {format}[/red]")
            return
        
        console.print(f"[green]✓ Graph exported to {output_file}[/green]")
    
    def _export_dot(self, nodes: List[Dict], edges: List[Dict], output_file: str):
        """导出为 GraphViz DOT 格式"""
        with open(output_file, 'w') as f:
            f.write("digraph CallGraph {\n")
            f.write("  rankdir=LR;\n")
            f.write("  node [shape=box];\n\n")
            
            # 写入节点
            for node in nodes:
                if node['node_type'] in ['FUNCTION', 'METHOD']:
                    label = f"{node['name']}\\n{node['file_path'].split('/')[-1]}"
                    f.write(f'  "{node["id"]}" [label="{label}"];\n')
            
            # 写入边
            f.write("\n")
            for edge in edges:
                if edge['edge_type'] in ['CALLS', 'METHOD_CALL']:
                    f.write(f'  "{edge["source_id"]}" -> "{edge["target_id"]}";\n')
            
            f.write("}\n")
    
    def _export_json(self, nodes: List[Dict], edges: List[Dict], output_file: str):
        """导出为 JSON 格式"""
        import json
        
        data = {
            'nodes': nodes,
            'edges': edges
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)


# ===== CLI 命令 =====

@click.group()
def cli():
    """Multi-Language Code Analysis Tool powered by tree-sitter-graph"""
    pass


@cli.command()
def check():
    """检查 tree-sitter-graph 安装"""
    console.print("[cyan]Checking tree-sitter-graph installation...[/cyan]")
    
    if check_tsg_installation():
        console.print("[green]✓ tree-sitter-graph is installed[/green]")
        engine = TSGEngine()
        info = engine.get_tsg_info()
        console.print(f"Version: {info['version']}")
    else:
        console.print("[red]✗ tree-sitter-graph is not installed[/red]")
        console.print(install_instructions())


@cli.command()
@click.argument('project_path')
@click.option('--name', '-n', help='Project name')
@click.option('--languages', '-l', help='Languages to analyze (comma-separated)')
@click.option('--db', default=config.DB_PATH, help='Database path')
def analyze(project_path, name, languages, db):
    """分析项目代码"""
    if not check_tsg_installation():
        console.print("[red]Error: tree-sitter-graph not installed[/red]")
        console.print(install_instructions())
        sys.exit(1)
    
    lang_list = languages.split(',') if languages else None
    
    analyzer = UnifiedAnalyzer(db)
    project_id = analyzer.analyze_project(
        project_path,
        project_name=name,
        languages=lang_list
    )
    
    console.print(f"\n[green]Project ID: {project_id}[/green]")


@cli.command()
@click.option('--project-id', '-p', required=True, help='Project ID')
@click.option('--function', '-f', help='Function name to query')
@click.option('--db', default=config.DB_PATH, help='Database path')
def query(project_id, function, db):
    """查询调用图"""
    analyzer = UnifiedAnalyzer(db)
    analyzer.query_call_graph(project_id, function)


@cli.command()
@click.option('--project-id', '-p', required=True, help='Project ID')
@click.option('--output', '-o', required=True, help='Output file')
@click.option('--format', '-f', default='dot', help='Output format (dot, json)')
@click.option('--db', default=config.DB_PATH, help='Database path')
def export(project_id, output, format, db):
    """导出图数据"""
    analyzer = UnifiedAnalyzer(db)
    analyzer.export_graph(project_id, output, format)


@cli.command()
@click.option('--db', default=config.DB_PATH, help='Database path')
def list_projects(db):
    """列出所有项目"""
    database = GraphDatabase(db)
    projects = database.list_projects()
    
    if not projects:
        console.print("[yellow]No projects found[/yellow]")
        return
    
    table = Table(title="Projects")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Path", style="blue")
    table.add_column("Language", style="magenta")
    
    for project in projects:
        table.add_row(
            project['id'][:8] + "...",
            project['name'],
            project['root_path'][:40] + "..." if len(project['root_path']) > 40 else project['root_path'],
            project.get('primary_language', 'N/A')
        )
    
    console.print(table)


if __name__ == '__main__':
    cli()

