# Sample Project - 多语言示例项目

## 项目简介

这是一个多语言示例项目，用于演示 Call Graph 工具的功能。项目包含 8 种编程语言的代码示例，展示了函数调用关系的提取和分析。

## 文件列表

### Python 文件
- **main.py** - Python 主程序，包含数据处理流程
- **utils.py** - Python 工具函数（如果存在）

### C 语言文件
- **example.c** - C 语言示例，展示基础函数调用

### C++ 文件
- **advanced.cpp** - C++ 高级示例，展示类、模板、智能指针等特性

### Java 文件
- **Example.java** - Java 示例，展示面向对象编程和 Stream API

### Rust 文件
- **example.rs** - Rust 示例，展示所有权、trait、模式匹配等特性

### JavaScript 文件
- **example.js** - JavaScript 示例，展示异步编程和高阶函数

### TypeScript 文件
- **example.ts** - TypeScript 示例，展示类型系统和泛型

### Go 文件
- **example.go** - Go 语言示例，展示并发和接口

## 代码特点

### 1. 多层次调用关系

每个语言示例都包含多层次的函数调用关系：

```
main/entry_function
  ├── high_level_function
  │   ├── mid_level_function_1
  │   │   └── low_level_function_1
  │   └── mid_level_function_2
  │       └── low_level_function_2
  └── another_high_level_function
```

### 2. 跨语言调用

主程序（C 语言的 main 函数）调用其他语言的函数，展示跨语言调用关系分析。

### 3. 常见模式

- **验证模式**: `validate_*` 函数用于数据验证
- **处理模式**: `process_*` 函数用于数据处理
- **工具模式**: `calculate_*`, `format_*` 等工具函数
- **管理模式**: `UserManager` 等管理类

### 4. 面向对象特性

- **类和方法** (Java, C++, TypeScript, Rust)
- **继承和多态** (Java, C++)
- **接口和 trait** (TypeScript, Rust, Go)
- **静态方法** (Java, TypeScript)

## 分析示例

### 基础分析

```bash
# 分析整个项目
uv run call-graph --database sample.db analyze examples/sample_project --clear

# 查看统计信息
uv run call-graph --database sample.db stats
```

### 函数搜索

```bash
# 搜索用户相关函数
uv run call-graph --database sample.db search "user" --verbose

# 搜索处理函数
uv run call-graph --database sample.db search "process"

# 搜索验证函数
uv run call-graph --database sample.db search "validate"
```

### 调用关系查询

```bash
# 查询谁调用了 validate_input
uv run call-graph --database sample.db query validate_input --callers

# 查询 process_data 调用了哪些函数
uv run call-graph --database sample.db query process_data --callees

# 查询从 main 开始的调用链
uv run call-graph --database sample.db query main --chain --depth 5
```

### 完整路径查询

```bash
# 查询 calculate 函数的完整调用路径
uv run call-graph --database sample.db query calculate --fullpath --verbose

# 查询 addUser 函数的完整路径（跨语言）
uv run call-graph --database sample.db query addUser --fullpath
```

### 可视化导出

```bash
# 导出调用图
uv run call-graph --database sample.db export --output call_graph.dot

# 生成 PNG 图片（需要安装 graphviz）
dot -Tpng call_graph.dot -o call_graph.png
```

## 预期结果

### 统计信息示例

```
数据库统计信息:
  符号总数: 150+
  调用关系数: 200+
  文件数: 8
  
支持的语言:
  - Python: 2 文件
  - C: 1 文件
  - C++: 1 文件
  - Java: 1 文件
  - Rust: 1 文件
  - JavaScript: 1 文件
  - TypeScript: 1 文件
  - Go: 1 文件
```

### 调用路径示例

```
完整调用路径（入口 -> 目标 -> 叶子）:
1. main(example.c:20) -> calculate(example.c:14) -> add(example.c:6)
2. main(example.c:20) -> calculate(example.c:14) -> multiply(example.c:10)
3. main(example.c:20) -> process_data(main.py:13) -> validate_input(main.py:6)
4. main(example.c:20) -> displayUser(example.js:13) -> processUser(example.go:42)
```

## 功能演示

### 快速演示

```bash
# 运行快速演示（3-5分钟）
./quick_demo.sh
```

### 完整演示

```bash
# 运行完整演示（5-10分钟，交互式）
./demo.sh
```

### Python API 演示

```python
from call_graph import CallGraphAnalyzer

# 创建分析器
analyzer = CallGraphAnalyzer('sample.db')

# 分析项目
analyzer.analyze_project('examples/sample_project')

# 查询完整路径
result = analyzer.query_full_call_paths('calculate', max_depth=10)
print(f"找到 {result['full_count']} 条路径")

# 性能统计
perf = result['performance']
print(f"查询时间: {perf['total_time']}秒")
```

## 扩展项目

你可以在这个示例项目的基础上添加更多代码：

### 添加新文件

```bash
# 添加新的 Python 文件
echo "def new_function(): pass" > examples/sample_project/new_module.py

# 重新分析
uv run call-graph --database sample.db analyze examples/sample_project --clear
```

### 添加新语言

目前支持的语言：Python, C, C++, Java, Rust, JavaScript, TypeScript, Go

如果需要支持其他语言，可以在 `call_graph/parsers.py` 中添加相应的解析器。

## 常见查询示例

### 1. 查找入口函数（没有被调用的函数）

```bash
# 统计信息中会显示入口函数数量
uv run call-graph --database sample.db stats
```

### 2. 查找叶子函数（不调用其他函数的函数）

```bash
# 使用 --chain 查询，深度为 1 的就是叶子函数
uv run call-graph --database sample.db query some_function --chain --depth 1
```

### 3. 查找调用最多的函数

```bash
# 搜索常用函数名
uv run call-graph --database sample.db search "print"
uv run call-graph --database sample.db search "log"
```

### 4. 分析特定文件的函数

```bash
# 先搜索该文件的函数
uv run call-graph --database sample.db search "example.c" --verbose
```

## 性能测试

### 小型项目（本示例）

- 文件数: 8
- 函数数: ~150
- 分析时间: < 1 秒
- 查询时间: < 0.01 秒

### 中型项目

- 文件数: 100-500
- 函数数: 1,000-10,000
- 分析时间: 10-60 秒
- 查询时间: < 1 秒

### 大型项目

- 文件数: 1,000+
- 函数数: 10,000-100,000
- 分析时间: 1-10 分钟
- 查询时间: < 5 秒（使用路径限制）

## 故障排查

### 问题1: 某些函数没有被识别

**原因**: 可能是语法特殊或不支持的语言特性

**解决**: 查看分析日志，检查是否有解析错误

### 问题2: 跨语言调用没有显示

**原因**: 跨语言调用依赖函数名匹配，可能名称不一致

**解决**: 确保函数名在不同语言中保持一致

### 问题3: 路径查询很慢

**原因**: 项目规模大，路径过多

**解决**: 
- 使用 `--depth` 限制搜索深度
- 使用 `max_paths` 参数限制路径数量

```bash
uv run call-graph --database sample.db query my_function --fullpath --depth 5
```

## 贡献

欢迎为示例项目添加更多语言的代码示例！

## 许可证

本示例项目仅用于演示目的。

