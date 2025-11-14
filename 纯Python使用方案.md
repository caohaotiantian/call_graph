# Call Graph 工具 - 纯 Python 使用方案

## 🎯 设计目标

提供简单、直接的 Python 使用方式，不依赖任何第三方包管理工具（如 uv）。

## 📦 安装步骤

### 步骤 1: 安装依赖

```bash
cd /path/to/call_graph
pip install -e .
```

**说明**: 
- `-e` 表示可编辑模式安装，方便开发和调试
- 会自动安装 `pyproject.toml` 中定义的所有依赖

**可选：使用虚拟环境（推荐）**

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

### 步骤 2: 验证安装

```bash
# 方式 1: 使用 Python 脚本
python call-graph.py --help

# 方式 2: 使用 Python 模块
python -m call_graph --help

# 方式 3: 如果已安装到系统
call-graph --help
```

## 🚀 使用方法

### 主要方式：使用 Python 脚本

所有命令都使用 `python call-graph.py` 格式：

```bash
# 分析项目
python call-graph.py --database myproject.db analyze /path/to/project --clear

# 查看统计
python call-graph.py --database myproject.db stats

# 搜索函数
python call-graph.py --database myproject.db search "function_name"

# 查询调用关系
python call-graph.py --database myproject.db query function_name --callers
python call-graph.py --database myproject.db query function_name --callees
python call-graph.py --database myproject.db query function_name --fullpath

# 导出图表
python call-graph.py --database myproject.db export --output graph.dot
```

### 备选方式 1：Python 模块方式

```bash
# 使用 -m 标志运行模块
python -m call_graph --database myproject.db stats
python -m call_graph --database myproject.db query main --fullpath
```

### 备选方式 2：系统命令方式

安装后可以直接使用命令：

```bash
# 安装到系统
pip install -e .

# 直接使用
call-graph --database myproject.db stats
call-graph --database myproject.db query main --fullpath
```

## 📝 完整示例

### 示例 1: 分析示例项目

```bash
# 1. 进入项目目录
cd /path/to/call_graph

# 2. 安装依赖（一次性）
pip install -e .

# 3. 分析示例项目
python call-graph.py --database demo.db analyze examples/sample_project --clear

# 4. 查看结果
python call-graph.py --database demo.db stats
```

### 示例 2: 分析自己的项目

```bash
# 分析你的项目
python call-graph.py --database myapp.db analyze /path/to/myapp --clear

# 查看统计
python call-graph.py --database myapp.db stats

# 搜索特定函数
python call-graph.py --database myapp.db search "init"

# 查询函数的完整调用路径
python call-graph.py --database myapp.db query initialize --fullpath --verbose
```

### 示例 3: 导出可视化图表

```bash
# 导出为 DOT 格式
python call-graph.py --database myapp.db export --output myapp.dot

# 使用 Graphviz 生成 PNG（需要先安装 graphviz）
dot -Tpng myapp.dot -o myapp.png
```

## 🎬 运行演示脚本

项目包含多个演示脚本，展示各种功能：

```bash
# 完整交互式演示
./demo.sh

# 快速自动演示
./quick_demo.sh

# 导出图表演示
./export_graph.sh -d demo.db -o output.dot
```

**注意**: 演示脚本会自动检查依赖是否安装，如果未安装会给出明确提示。

## 📚 CLI 命令参考

### 基本格式

```bash
python call-graph.py [全局选项] <子命令> [子命令选项]
```

### 全局选项

- `--database`, `-d` : 数据库文件路径（默认: call_graph.db）

### 子命令

#### 1. analyze - 分析项目

```bash
python call-graph.py --database <db> analyze <项目路径> [选项]

选项:
  --clear              清空现有数据
  --exclude <dirs>     排除的目录（逗号分隔）
```

#### 2. stats - 查看统计

```bash
python call-graph.py --database <db> stats
```

#### 3. search - 搜索函数

```bash
python call-graph.py --database <db> search <关键词> [选项]

选项:
  --verbose, -v        显示详细信息
```

#### 4. query - 查询调用关系

```bash
python call-graph.py --database <db> query <函数名> [选项]

选项:
  --callers            查询谁调用了这个函数
  --callees            查询这个函数调用了谁
  --chain              查询调用链（向下）
  --fullpath           查询完整路径（向上+向下）
  --depth <n>          最大搜索深度
  --verbose, -v        显示详细信息
```

#### 5. export - 导出调用图

```bash
python call-graph.py --database <db> export --output <文件>

选项:
  --output, -o <file>  输出文件路径
```

## 💡 使用技巧

### 技巧 1: 排除不需要的目录

```bash
python call-graph.py --database myapp.db analyze ./myapp \
  --exclude "node_modules,venv,build,dist,.git,__pycache__"
```

### 技巧 2: 多数据库管理

为不同项目使用不同的数据库文件：

```bash
# 项目 A
python call-graph.py --database projectA.db analyze /path/to/projectA

# 项目 B
python call-graph.py --database projectB.db analyze /path/to/projectB
```

### 技巧 3: 查询优化

使用 `--depth` 限制搜索深度，提高大型项目的查询速度：

```bash
python call-graph.py --database large.db query main --fullpath --depth 5
```

### 技巧 4: 批量操作

创建 Shell 脚本批量分析多个项目：

```bash
#!/bin/bash
for project in project1 project2 project3; do
    python call-graph.py --database ${project}.db \
        analyze /path/to/${project} --clear
    python call-graph.py --database ${project}.db \
        export --output ${project}.dot
done
```

## 🔧 开发建议

### 使用虚拟环境（推荐）

```bash
# 创建项目虚拟环境
python -m venv venv

# 激活
source venv/bin/activate

# 安装
pip install -e .

# 使用
python call-graph.py --database dev.db analyze ./src

# 退出
deactivate
```

### Python API 使用

除了 CLI，还可以在 Python 代码中直接使用：

```python
from call_graph.analyzer import CallGraphAnalyzer
from call_graph.database import CallGraphDB

# 创建分析器
analyzer = CallGraphAnalyzer('myproject.db')

# 分析项目
stats = analyzer.analyze_project('/path/to/project')
print(f"找到 {stats['total_symbols']} 个符号")

# 查询
results = analyzer.query_full_call_paths('my_function')
for path in results['full_paths']:
    print(' -> '.join(path))

# 关闭
analyzer.close()
```

## ⚠️ 注意事项

1. **首次使用必须安装依赖**: `pip install -e .`
2. **数据库位置**: 默认在当前目录，建议使用绝对路径或明确指定
3. **大型项目**: 使用 `--exclude` 排除不必要的目录
4. **Python 版本**: 需要 Python 3.10 或更高版本

## 🆘 故障排除

### 问题 1: ModuleNotFoundError

```bash
# 错误
ModuleNotFoundError: No module named 'tree_sitter'

# 解决
pip install -e .
```

### 问题 2: Python 命令找不到

```bash
# 如果 python 命令不存在，使用 python3
python3 call-graph.py --help

# 或创建别名
alias python=python3
```

### 问题 3: 权限错误

```bash
# 使用 --user 参数
pip install --user -e .

# 或使用虚拟环境
python -m venv venv
source venv/bin/activate
pip install -e .
```

### 问题 4: 分析失败

检查：
1. 项目路径是否正确
2. 是否有读取权限
3. 是否排除了正确的目录

```bash
# 使用详细输出
python call-graph.py --database debug.db analyze /path/to/project --clear
```

## 📖 相关文档

- `快速开始.md` - 快速入门指南
- `README.md` - 项目总览
- `使用说明.md` - 详细使用文档
- `examples/` - 示例代码和项目

## 🎯 总结

**推荐使用流程**:

1. **安装**: `pip install -e .`
2. **分析**: `python call-graph.py --database myapp.db analyze /path/to/myapp --clear`
3. **查询**: `python call-graph.py --database myapp.db query function_name --fullpath`
4. **导出**: `python call-graph.py --database myapp.db export --output graph.dot`

简单、直接、高效！🚀

