# Call Graph Analyzer

一个强大的多语言函数调用关系分析工具，使用 tree-sitter 解析源代码并提取函数调用关系。

## 特性

- 🌐 **多语言支持**: 支持 Python、C、C++、Java、Rust、JavaScript、TypeScript、Go
- 📊 **完整的调用关系分析**: 提取函数定义和调用关系
- 💾 **SQLite 持久化**: 将分析结果保存到数据库，支持高效查询
- 🔍 **灵活的查询接口**: 支持查询调用者、被调用者、调用链等
- 🎨 **可视化导出**: 支持导出为 Graphviz DOT 格式
- 🚀 **高性能**: 基于 tree-sitter 的快速语法解析

## 安装

### 前置要求

- Python 3.10 或更高版本
- pip 包管理器

### 安装步骤

```bash
# 克隆仓库
git clone <repository-url>
cd call_graph

# 安装依赖
pip install -e .
```

### 使用虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
```

## 快速开始

### 1. 分析项目

```bash
# 分析整个项目
python call-graph.py --database myproject.db analyze /path/to/your/project --clear

# 排除特定目录
python call-graph.py --database myproject.db analyze /path/to/your/project --exclude "node_modules,build,dist"
```

### 2. 查询调用关系

```bash
# 查询谁调用了某个函数
python call-graph.py --database myproject.db query main --callers

# 查询某个函数调用了哪些函数
python call-graph.py --database myproject.db query process_data --callees

# 查询调用链（向下，默认深度10）
python call-graph.py --database myproject.db query main --chain --depth 3

# 查询完整调用路径（新功能：向上+向下）⭐
python call-graph.py --database myproject.db query process_data --fullpath

# 显示完整路径的详细信息
python call-graph.py --database myproject.db query validate_input --fullpath --verbose
```

### 3. 搜索函数

```bash
# 模糊搜索函数名
python call-graph.py --database myproject.db search "process"

# 显示详细信息
python call-graph.py --database myproject.db search "process" --verbose
```

### 4. 查看统计信息

```bash
# 显示数据库统计信息
python call-graph.py --database myproject.db stats
```

### 5. 导出调用图

```bash
# 导出为 Graphviz DOT 格式
python call-graph.py --database myproject.db export --output call_graph.dot

# 使用 Graphviz 生成图片
dot -Tpng call_graph.dot -o call_graph.png
```

## Python API 使用

### 基本用法

```python
from call_graph.analyzer import CallGraphAnalyzer
from call_graph.database import CallGraphDB

# 创建分析器
analyzer = CallGraphAnalyzer("my_project.db")

# 分析项目
stats = analyzer.analyze_project("/path/to/project")
print(f"找到 {stats['total_symbols']} 个符号")
print(f"找到 {stats['total_relations']} 个调用关系")

analyzer.close()
```

### 查询调用关系

```python
from call_graph.database import CallGraphDB

db = CallGraphDB("my_project.db")

# 查询调用者
callers = db.get_callers("process_data")
for caller in callers:
    print(f"{caller['caller_name']} 调用了 process_data")

# 查询被调用者
callees = db.get_callees("main")
for callee in callees:
    print(f"main 调用了 {callee['callee_name']}")

# 查询调用链
chains = db.get_call_chain("main", depth=3)
for chain in chains:
    print(" -> ".join(chain))

db.close()
```

### 搜索和统计

```python
from call_graph.database import CallGraphDB

db = CallGraphDB("my_project.db")

# 搜索符号
results = db.search_symbols("process")
for symbol in results:
    print(f"{symbol['name']} ({symbol['language']})")

# 获取统计信息
stats = db.get_statistics()
print(f"总符号数: {stats['total_symbols']}")
print(f"按语言统计: {stats['by_language']}")

db.close()
```

### 更多示例

查看 `examples/example_usage.py` 文件获取完整的使用示例。

## 数据库结构

### symbols 表

存储所有提取的符号（函数、方法等）：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | 唯一标识符 |
| file | TEXT | 文件路径 |
| name | TEXT | 符号名称 |
| kind | TEXT | 符号类型（function等） |
| start_line | INTEGER | 起始行号 |
| end_line | INTEGER | 结束行号 |
| start_byte | INTEGER | 起始字节 |
| end_byte | INTEGER | 结束字节 |
| container | TEXT | 所属容器 |
| signature | TEXT | 函数签名 |
| language | TEXT | 编程语言 |
| extras_json | TEXT | 额外信息（JSON格式） |
| code_excerpt | TEXT | 代码摘要 |
| is_exported | INTEGER | 是否导出 |

### call_relations 表

存储函数调用关系：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 自增主键 |
| caller_id | TEXT | 调用者ID |
| callee_id | TEXT | 被调用者ID |
| caller_name | TEXT | 调用者名称 |
| callee_name | TEXT | 被调用者名称 |
| caller_file | TEXT | 调用者文件 |
| callee_file | TEXT | 被调用者文件 |
| call_site_line | INTEGER | 调用位置行号 |
| call_site_column | INTEGER | 调用位置列号 |
| language | TEXT | 编程语言 |

## 支持的语言

| 语言 | 文件扩展名 | 状态 |
|------|-----------|------|
| Python | .py | ✅ |
| C | .c, .h | ✅ |
| C++ | .cpp, .cc, .cxx, .hpp, .hxx, .h | ✅ |
| Java | .java | ✅ |
| Rust | .rs | ✅ |
| JavaScript | .js, .jsx, .mjs | ✅ |
| TypeScript | .ts, .tsx | ✅ |
| Go | .go | ✅ |

## 项目结构

```
call_graph/
├── call_graph/           # 主包
│   ├── __init__.py      # 包初始化
│   ├── analyzer.py      # 核心分析引擎
│   ├── database.py      # 数据库操作
│   ├── parsers.py       # 多语言解析器
│   └── main.py          # CLI 入口
├── examples/            # 使用示例
│   ├── example_usage.py # Python API 示例
│   └── sample_project/  # 示例项目
├── init_db.sql          # 数据库架构
├── pyproject.toml       # 项目配置
└── README.md            # 本文件
```

## 工作原理

1. **代码解析**: 使用 tree-sitter 解析各种语言的源代码，生成抽象语法树（AST）
2. **符号提取**: 遍历 AST，提取所有函数定义和相关信息
3. **调用关系分析**: 分析函数内的调用表达式，建立调用关系
4. **持久化存储**: 将提取的信息保存到 SQLite 数据库
5. **查询和分析**: 提供丰富的查询接口，支持各种分析需求

## 使用场景

- 📖 **代码理解**: 快速了解大型项目的函数调用结构
- 🔄 **重构支持**: 识别函数依赖关系，安全地进行代码重构
- 🐛 **影响分析**: 评估修改某个函数可能影响的范围
- 📈 **代码度量**: 分析代码复杂度和耦合度
- 🗺️ **架构可视化**: 生成调用关系图，理解系统架构
- 🔍 **死代码检测**: 找出未被调用的函数

## 局限性

- 不支持动态调用（如反射、动态import等）
- 对于间接调用（函数指针、回调）的支持有限
- 跨语言调用关系需要额外处理

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 相关项目

- [tree-sitter](https://tree-sitter.github.io/) - 增量解析库
- [tree-sitter-graph](https://github.com/tree-sitter/tree-sitter-graph) - 图构造 DSL（本项目的灵感来源）

## 常见问题

### Q: 分析大型项目需要多长时间？

A: 取决于项目大小。通常，分析速度约为每秒 100-1000 个文件。

### Q: 数据库文件会很大吗？

A: SQLite 数据库大小通常为源代码大小的 10-20%。

### Q: 如何可视化调用关系？

A: 使用 `call-graph export` 导出 DOT 格式，然后用 Graphviz 生成图片：

```bash
call-graph export --output graph.dot
dot -Tpng graph.dot -o graph.png
```

### Q: 支持增量分析吗？

A: 目前不支持增量分析，需要重新分析整个项目。使用 `--clear` 选项清空旧数据。

### Q: 如何分析特定目录？

A: 将目录路径作为参数传递给 `analyze` 命令：

```bash
call-graph analyze /path/to/specific/directory
```

## 更新日志

### v0.1.0 (2024)

- 初始版本
- 支持 7 种编程语言
- 基本的调用关系分析
- SQLite 持久化
- CLI 和 Python API
- DOT 格式导出

## 联系方式

如有问题或建议，请提交 Issue。

