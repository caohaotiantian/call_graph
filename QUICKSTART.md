# 快速开始指南

## 安装

```bash
# 进入项目目录
cd /Users/caohaotian/Documents/Projects/call_graph

# 安装依赖
uv sync

# 或使用 pip
pip install -e .
```

## 基本使用

### 1. 分析项目

```bash
# 使用 uv run（推荐）
uv run call-graph --database my_project.db analyze /path/to/your/project --clear

# 或直接使用（如果已安装到系统）
call-graph --database my_project.db analyze /path/to/your/project --clear
```

### 2. 查看统计信息

```bash
uv run call-graph --database my_project.db stats
```

输出示例：
```
==================================================
数据库统计信息
==================================================

总符号数: 19
总调用关系: 20

按语言统计:
  c              :      4 个符号
  javascript     :      4 个符号
  python         :     11 个符号

按类型统计:
  function       :     19 个
```

### 3. 查询函数调用关系

#### 查询谁调用了某个函数

```bash
uv run call-graph --database my_project.db query process_data --callers
```

输出示例：
```
查询调用 'process_data' 的所有函数:

1. main (/path/to/main.py:33)
```

#### 查询某个函数调用了哪些函数

```bash
uv run call-graph --database my_project.db query main --callees
```

输出示例：
```
'main' 调用的所有函数:

1. process_data (external)
2. save_results (external)
3. print (external)
```

#### 查询完整调用链

```bash
uv run call-graph --database my_project.db query main --chain --depth 3
```

### 4. 搜索函数

```bash
# 模糊搜索
uv run call-graph --database my_project.db search "calculate"

# 显示详细信息
uv run call-graph --database my_project.db search "process" --verbose
```

输出示例：
```
搜索符号 'calculate':

1. calculate (function) - /path/to/example.c:14
2. calculate_average (function) - /path/to/utils.py:16
3. calculate_sum (function) - /path/to/utils.py:11
```

### 5. 导出调用图

```bash
# 导出为 DOT 格式
uv run call-graph --database my_project.db export --output call_graph.dot

# 使用 Graphviz 生成图片（需要安装 graphviz）
dot -Tpng call_graph.dot -o call_graph.png
dot -Tsvg call_graph.dot -o call_graph.svg
```

## Python API 使用

### 分析项目

```python
from call_graph.analyzer import CallGraphAnalyzer

# 创建分析器
analyzer = CallGraphAnalyzer("my_project.db")

try:
    # 分析项目
    stats = analyzer.analyze_project("/path/to/your/project")
    print(f"找到 {stats['total_symbols']} 个符号")
    print(f"找到 {stats['total_relations']} 个调用关系")
finally:
    analyzer.close()
```

### 查询调用关系

```python
from call_graph.database import CallGraphDB

db = CallGraphDB("my_project.db")

try:
    # 查询调用者
    callers = db.get_callers("process_data")
    for caller in callers:
        print(f"{caller['caller_name']} -> process_data")
    
    # 查询被调用者
    callees = db.get_callees("main")
    for callee in callees:
        print(f"main -> {callee['callee_name']}")
    
    # 查询调用链
    chains = db.get_call_chain("main", depth=3)
    for chain in chains:
        print(" -> ".join(chain))
    
    # 搜索函数
    results = db.search_symbols("process")
    for symbol in results:
        print(f"{symbol['name']} ({symbol['language']})")
    
    # 获取统计信息
    stats = db.get_statistics()
    print(stats)
    
finally:
    db.close()
```

### 使用上下文管理器

```python
from call_graph.analyzer import CallGraphAnalyzer
from call_graph.database import CallGraphDB

# 自动管理资源
with CallGraphAnalyzer("my_project.db") as analyzer:
    stats = analyzer.analyze_project("/path/to/your/project")
    print(stats)

with CallGraphDB("my_project.db") as db:
    results = db.search_symbols("main")
    print(results)
```

## 测试示例项目

项目包含了一个示例项目用于测试：

```bash
# 分析示例项目
uv run call-graph --database example.db analyze examples/sample_project --clear

# 查看统计
uv run call-graph --database example.db stats

# 查询 main 函数
uv run call-graph --database example.db query main --callees

# 搜索函数
uv run call-graph --database example.db search "process"

# 导出调用图
uv run call-graph --database example.db export --output example_graph.dot
```

## 支持的语言

- ✅ Python (.py)
- ✅ C (.c, .h)
- ✅ C++ (.cpp, .cc, .cxx, .hpp, .hxx, .h)
- ✅ Java (.java)
- ✅ Rust (.rs)
- ✅ JavaScript (.js, .jsx, .mjs)
- ✅ TypeScript (.ts, .tsx)
- ✅ Go (.go)

## 常用选项

### analyze 命令

```bash
# 清空现有数据重新分析
--clear, -c

# 排除特定目录
--exclude "node_modules,build,dist"
```

### query 命令

```bash
# 查询调用者
--callers

# 查询被调用者
--callees

# 查询调用链
--chain

# 设置调用链深度
--depth 5
```

### search 命令

```bash
# 显示详细信息
--verbose, -v
```

### export 命令

```bash
# 指定输出文件
--output, -o call_graph.dot

# 指定格式（目前仅支持 dot）
--format dot
```

## 高级用法

### 分析特定目录

```bash
uv run call-graph --database backend.db analyze /path/to/project/backend --clear
uv run call-graph --database frontend.db analyze /path/to/project/frontend --clear
```

### 组合查询

```python
from call_graph.database import CallGraphDB

db = CallGraphDB("my_project.db")

# 查找最常被调用的函数
cursor = db.conn.cursor()
cursor.execute("""
    SELECT callee_name, COUNT(*) as call_count
    FROM call_relations
    GROUP BY callee_name
    ORDER BY call_count DESC
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"{row['callee_name']}: {row['call_count']} 次调用")

db.close()
```

### 分析特定文件

```python
from call_graph.analyzer import CallGraphAnalyzer

analyzer = CallGraphAnalyzer("my_project.db")

result = analyzer.analyze_file("/path/to/file.py")
print(f"文件: {result['file']}")
print(f"语言: {result['language']}")
print(f"函数数量: {len(result['functions'])}")
print(f"调用关系: {len(result['calls'])}")

analyzer.close()
```

## 故障排除

### 问题：找不到 call-graph 命令

**解决方案**：使用 `uv run call-graph` 或先激活虚拟环境

```bash
# 使用 uv run
uv run call-graph --help

# 或激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
call-graph --help
```

### 问题：解析特定语言失败

**解决方案**：检查是否安装了对应的 tree-sitter 解析器

```bash
uv sync
```

### 问题：数据库过大

**解决方案**：使用 `--clear` 选项清空旧数据，或定期清理

```bash
# 清空数据库重新分析
uv run call-graph --database my_project.db analyze /path/to/project --clear
```

```python
# 或使用 Python API
from call_graph.database import CallGraphDB

db = CallGraphDB("my_project.db")
db.clear_all()
db.close()
```

## 下一步

- 查看完整的 [README.md](README.md) 了解更多信息
- 查看 [examples/example_usage.py](examples/example_usage.py) 获取完整示例
- 查看数据库结构了解如何编写自定义查询

## 反馈和贡献

如有问题或建议，欢迎提交 Issue！

