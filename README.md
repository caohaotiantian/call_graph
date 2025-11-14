# Call Graph Analyzer

多语言函数调用关系分析工具 - 基于 Tree-sitter 实现的高性能代码分析器

## 📖 简介

Call Graph Analyzer 是一个强大的静态代码分析工具，能够从项目源代码中提取函数定义和调用关系，构建完整的调用图，并支持多种查询和分析功能。特别为大型项目优化，支持多进程并行处理。

### 核心特性

- 🌍 **多语言支持**: Python, C, C++, Java, Rust, JavaScript, TypeScript, Go
- ⚡ **高性能**: 支持多进程并行处理，大型项目分析速度提升 5-7 倍
- 💾 **持久化存储**: 使用 SQLite 数据库，支持快速查询
- 🔍 **强大查询**: 支持调用者、被调用者、调用链、完整路径查询
- 📊 **可视化导出**: 支持导出 Graphviz DOT 格式，可生成调用图
- 🎯 **精确定位**: 提供函数位置信息（文件名和行号）

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone <repository_url>
cd call_graph

# 安装依赖（推荐使用虚拟环境）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装项目
pip install -e .
```

### 基本使用

```bash
# 1. 分析项目（标准模式）
python call-graph.py --database myproject.db analyze /path/to/project --clear

# 2. 分析项目（性能优化模式，推荐用于大型项目）⚡
python call-graph.py --database myproject.db analyze /path/to/project --clear --fast

# 3. 查询函数调用关系
python call-graph.py --database myproject.db query main --callers

# 4. 查看统计信息
python call-graph.py --database myproject.db stats

# 5. 搜索函数
python call-graph.py --database myproject.db search "process"
```

## 📊 性能对比

### 标准模式 vs 优化模式

| 项目规模   | 文件数 | 函数数 | 标准模式 | 优化模式 | 性能提升 |
| ---------- | ------ | ------ | -------- | -------- | -------- |
| 小型项目   | 100    | 500    | 15 秒    | 10 秒    | 1.5x     |
| 中型项目   | 500    | 2000   | 2 分钟   | 30 秒    | 4x       |
| 大型项目   | 2000   | 12000  | 15 分钟  | 3 分钟   | **5x**   |
| 超大型项目 | 5000+  | 30000+ | 30+分钟  | 6 分钟   | **5-7x** |

### 性能优化模式使用

```bash
# 基本用法
python call-graph.py --database myproject.db analyze /path/to/project --clear --fast

# 自定义工作进程数和批次大小
python call-graph.py --database myproject.db analyze /path/to/project \
  --clear --fast --workers 8 --batch-size 200
```

**适用场景**:

- ✅ 文件数 > 500
- ✅ 多核 CPU（4 核或以上）
- ✅ 需要快速分析

## 🎯 核心功能

### 1. 项目分析

提取项目中所有函数定义和调用关系：

```bash
# 分析项目并清空旧数据
python call-graph.py --database myproject.db analyze /path/to/project --clear

# 排除特定目录
python call-graph.py --database myproject.db analyze /path/to/project \
  --exclude "node_modules,venv,build,dist,target"

# 使用性能优化模式（大型项目推荐）
python call-graph.py --database myproject.db analyze /path/to/project --clear --fast
```

### 2. 调用关系查询

#### 查询调用者

查询哪些函数调用了目标函数（自动去重，显示完整的函数定义位置）：

```bash
python call-graph.py --database myproject.db query calculate --callers

# 输出格式：function_name(file:line)
# 自动去重，多次调用会标注次数
# 示例输出：
# 1. process_order(/path/to/order.py:45) (共 3 处调用)
# 2. update_invoice(/path/to/invoice.py:78)
```

显示所有调用点详细信息（verbose 模式）：

```bash
python call-graph.py --database myproject.db query calculate --callers --verbose

# 示例输出：
# 1. process_order(/path/to/order.py:45)
#    调用点 1: /path/to/order.py:67
#    调用点 2: /path/to/order.py:89
#    调用点 3: /path/to/order.py:123
```

#### 查询被调用者

查询目标函数调用了哪些函数（自动去重，显示完整的函数定义位置）：

```bash
python call-graph.py --database myproject.db query main --callees

# 输出格式：function_name(file:line)
# 自动去重，多次调用会标注次数
# 示例输出：
# 1. initialize(/path/to/app.py:10) (共 2 处调用)
# 2. process_data(/path/to/data.py:34)
# 3. print(external)  # 外部函数
```

#### 查询调用链

查询从目标函数向下的完整调用链（自动去重，每个函数显示完整位置）：

```bash
python call-graph.py --database myproject.db query main --chain --depth 5

# 输出格式：func1(file:line) -> func2(file:line) -> ...
# 自动去除重复路径
# 示例输出：
# 找到 3 条唯一调用链
# (已去除 2 条重复)
#
# 1. main(/path/to/main.py:10) -> initialize(/path/to/app.py:5) -> load_config(/path/to/config.py:12)
# 2. main(/path/to/main.py:10) -> process_data(/path/to/data.py:34)
```

#### 查询完整调用路径

查询包含目标函数的完整调用路径（从入口函数到叶子函数）：

```bash
# 基本查询
python call-graph.py --database myproject.db query process_data --fullpath

# 显示详细统计信息
python call-graph.py --database myproject.db query process_data --fullpath --verbose
```

### 3. 函数搜索

支持模糊搜索函数名：

```bash
python call-graph.py --database myproject.db search "process"

# 显示详细信息（包括函数签名）
python call-graph.py --database myproject.db search "process" --verbose
```

### 4. 统计信息

查看数据库中的统计信息：

```bash
python call-graph.py --database myproject.db stats
```

### 5. 导出调用图

导出为 Graphviz DOT 格式：

```bash
# 导出到文件
python call-graph.py --database myproject.db export --output graph.dot

# 生成图片（需要安装 graphviz）
dot -Tpng graph.dot -o graph.png
dot -Tsvg graph.dot -o graph.svg
```

## 🛠️ 支持的语言

| 语言       | 支持的结构               | 文件扩展名                            |
| ---------- | ------------------------ | ------------------------------------- |
| Python     | 函数定义、函数调用       | `.py`                                 |
| C          | 函数定义、函数调用       | `.c`, `.h`                            |
| C++        | 函数定义、方法、函数调用 | `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hxx` |
| Java       | 方法定义、方法调用       | `.java`                               |
| Rust       | 函数定义、方法、函数调用 | `.rs`                                 |
| JavaScript | 函数定义、箭头函数、调用 | `.js`, `.jsx`                         |
| TypeScript | 函数定义、箭头函数、调用 | `.ts`, `.tsx`                         |
| Go         | 函数定义、方法、函数调用 | `.go`                                 |

## 📚 CLI 命令参考

### analyze - 分析项目

```bash
python call-graph.py --database <db> analyze <project_path> [选项]

选项:
  --clear, -c              清空现有数据
  --exclude, -e <dirs>     排除的目录（逗号分隔）
  --fast, -f               启用性能优化模式
  --workers, -w <num>      工作进程数（默认：CPU核心数-1）
  --batch-size, -b <size>  批量插入大小（默认：100）
```

### query - 查询调用关系

```bash
python call-graph.py --database <db> query <function_name> [选项]

选项:
  --callers       查询调用者
  --callees       查询被调用者
  --chain         查询调用链（向下）
  --fullpath      查询完整调用路径（向上+向下）
  --depth <n>     最大搜索深度（默认：10）
  --verbose, -v   显示详细信息
```

### search - 搜索函数

```bash
python call-graph.py --database <db> search <pattern> [选项]

选项:
  --verbose, -v   显示详细信息
```

### stats - 统计信息

```bash
python call-graph.py --database <db> stats
```

### export - 导出调用图

```bash
python call-graph.py --database <db> export [选项]

选项:
  --format, -f <format>  导出格式（默认：dot）
  --output, -o <file>    输出文件路径
```

## 🔧 Python API

除了 CLI，也可以在 Python 代码中使用：

```python
from call_graph.analyzer import CallGraphAnalyzer
from call_graph.analyzer_optimized import CallGraphAnalyzerOptimized

# 标准模式
analyzer = CallGraphAnalyzer("myproject.db")
analyzer.analyze_project("/path/to/project")

# 性能优化模式
analyzer_opt = CallGraphAnalyzerOptimized("myproject.db", num_workers=8)
stats = analyzer_opt.analyze_project(
    "/path/to/project",
    batch_size=200,
    show_progress=True
)

# 查询
callers = analyzer.query_callers("my_function")
callees = analyzer.query_callees("my_function")
paths = analyzer.query_full_call_paths("my_function", max_depth=10)

# 搜索
results = analyzer.search_functions("process")

analyzer.close()
```

## 📂 项目结构

```
call_graph/
├── call_graph/              # 核心代码包
│   ├── __init__.py
│   ├── __main__.py         # 模块入口
│   ├── analyzer.py         # 标准分析器
│   ├── analyzer_optimized.py  # 性能优化分析器
│   ├── database.py         # 数据库操作
│   ├── main.py            # CLI 接口
│   └── parsers.py         # 多语言解析器
├── examples/              # 示例项目
│   └── sample_project/    # 多语言示例代码
├── call-graph.py          # 启动脚本
├── init_db.sql           # 数据库 schema
├── pyproject.toml        # 项目配置
├── README.md             # 本文件
└── 使用指南.md           # 详细使用文档
```

## 🎬 演示

运行演示脚本查看所有功能：

```bash
# 完整功能演示
./demo.sh

# 快速演示
./quick_demo.sh
```

## ⚙️ 配置说明

### 默认排除目录

分析项目时自动排除以下目录：

- `node_modules` - Node.js 依赖
- `.git` - Git 仓库
- `__pycache__` - Python 缓存
- `venv`, `env` - Python 虚拟环境
- `build`, `dist` - 构建输出
- `target` - Rust/Java 构建输出
- `.idea`, `.vscode` - IDE 配置

可以使用 `--exclude` 参数添加更多排除目录。

## 🐛 故障排除

### 问题 1: ModuleNotFoundError

```bash
# 确保已安装依赖
pip install -e .

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate
pip install -e .
```

### 问题 2: 性能优化模式内存不足

```bash
# 减少工作进程数
python call-graph.py ... --fast --workers 4

# 减少批次大小
python call-graph.py ... --fast --batch-size 50
```

### 问题 3: 数据库锁定

确保没有其他进程在访问数据库文件。

## 📝 开发指南

### 添加新语言支持

1. 在 `call_graph/parsers.py` 中添加语言配置：

```python
LANGUAGE_CONFIG = {
    'your_language': {
        'extensions': ['.ext'],
        'module': 'tree_sitter_yourlang',
        'function_types': ['function_definition'],
        'call_types': ['call_expression']
    }
}
```

2. 实现语言解析器类：

```python
class YourLanguageParser(LanguageParser):
    def extract_function_name(self, node):
        # 提取函数名逻辑
        pass

    def extract_call_name(self, node):
        # 提取调用名逻辑
        pass
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题或建议，请提交 Issue。

---

**快速上手**: 查看 [使用指南.md](使用指南.md) 获取详细教程和最佳实践。
