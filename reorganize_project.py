#!/usr/bin/env python3
"""
项目重组脚本
将 V1 和 V2 实现分别放到不同的文件夹中
"""
import os
import shutil
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# V1 文件列表（仅 Python 实现）
V1_FILES = [
    'main.py',
    'database.py',
    'call_graph_extractor.py',
    'call_chain_analyzer.py',
    'config.py',
    'init_db.sql',
    'requirements.txt',
    'example.py',
    'setup_example.py',
    'README.md',
    'QUICKSTART.md',
]

# V2 文件列表（多语言实现）
V2_FILES = [
    'unified_analyzer.py',
    'tsg_engine.py',
    'graph_database.py',
    'config_v2.py',
    'init_graph_db.sql',
    'requirements_v2.txt',
    'test_c_cpp.py',
    'README_V2.md',
    'QUICKSTART_V2.md',
]

# V2 文件夹
V2_DIRS = [
    'tsg_rules',
    'examples',
]

# 共享文档（保留在根目录）
SHARED_DOCS = [
    'ARCHITECTURE_V2.md',
    'INSTALLATION.md',
    'PROJECT_SUMMARY.md',
    'C_CPP_SUPPORT.md',
    'C_CPP_COMPLETION_SUMMARY.md',
    'TREE_SITTER_GRAPH_INTEGRATION.md',
    'FILE_INDEX.md',
    '.gitignore',
]


def create_directories():
    """创建目录结构"""
    print("创建目录结构...")
    
    v1_dir = PROJECT_ROOT / 'v1_python_only'
    v2_dir = PROJECT_ROOT / 'v2_multi_language'
    
    v1_dir.mkdir(exist_ok=True)
    v2_dir.mkdir(exist_ok=True)
    
    print(f"✓ 创建 {v1_dir}")
    print(f"✓ 创建 {v2_dir}")


def move_v1_files():
    """移动 V1 文件"""
    print("\n移动 V1 文件...")
    
    v1_dir = PROJECT_ROOT / 'v1_python_only'
    moved = 0
    
    for filename in V1_FILES:
        src = PROJECT_ROOT / filename
        dst = v1_dir / filename
        
        if src.exists():
            if dst.exists():
                print(f"  跳过 {filename} (已存在)")
            else:
                shutil.copy2(src, dst)
                print(f"  ✓ 复制 {filename}")
                moved += 1
        else:
            print(f"  ✗ 找不到 {filename}")
    
    print(f"移动了 {moved} 个 V1 文件")


def move_v2_files():
    """移动 V2 文件"""
    print("\n移动 V2 文件...")
    
    v2_dir = PROJECT_ROOT / 'v2_multi_language'
    moved = 0
    
    # 移动文件
    for filename in V2_FILES:
        src = PROJECT_ROOT / filename
        dst = v2_dir / filename
        
        if src.exists():
            if dst.exists():
                print(f"  跳过 {filename} (已存在)")
            else:
                shutil.copy2(src, dst)
                print(f"  ✓ 复制 {filename}")
                moved += 1
        else:
            print(f"  ✗ 找不到 {filename}")
    
    # 移动文件夹
    for dirname in V2_DIRS:
        src = PROJECT_ROOT / dirname
        dst = v2_dir / dirname
        
        if src.exists() and src.is_dir():
            if dst.exists():
                print(f"  跳过 {dirname}/ (已存在)")
            else:
                shutil.copytree(src, dst)
                print(f"  ✓ 复制 {dirname}/")
                moved += 1
        else:
            print(f"  ✗ 找不到 {dirname}/")
    
    print(f"移动了 {moved} 个 V2 文件/文件夹")


def create_readme_files():
    """在各个目录创建 README"""
    print("\n创建 README 文件...")
    
    # 根目录 README
    root_readme = PROJECT_ROOT / 'README.md'
    with open(root_readme, 'w', encoding='utf-8') as f:
        f.write("""# 多语言代码分析系统

一个基于 tree-sitter 的多语言代码分析工具，支持函数调用图和数据流图提取。

## 📁 项目结构

本项目包含两个版本的实现：

### V1: Python 专用版本 (v1_python_only/)

- **技术栈**: 纯 Python + tree-sitter-python
- **支持语言**: Python
- **特点**: 简单易用，适合 Python 项目分析
- **文档**: 查看 `v1_python_only/README.md`

### V2: 多语言版本 (v2_multi_language/)

- **技术栈**: Python + tree-sitter-graph (Rust)
- **支持语言**: Python, Rust, C, C++, Java, JavaScript, TypeScript
- **特点**: 高性能，支持多语言，声明式规则
- **文档**: 查看 `v2_multi_language/README_V2.md`

## 🚀 快速选择

### 选择 V1 如果...
- ✅ 只需要分析 Python 代码
- ✅ 想要简单快速的解决方案
- ✅ 不想安装 Rust 工具链

### 选择 V2 如果...
- ✅ 需要分析多种编程语言
- ✅ 需要更高的性能
- ✅ 需要数据流分析
- ✅ 想要可扩展的架构

## 📚 文档

- [安装指南](INSTALLATION.md)
- [架构设计](ARCHITECTURE_V2.md)
- [项目总结](PROJECT_SUMMARY.md)
- [C/C++ 支持](C_CPP_SUPPORT.md)
- [文件索引](FILE_INDEX.md)

## 🎯 快速开始

### V1 版本
```bash
cd v1_python_only
pip install -r requirements.txt
python main.py all
```

### V2 版本
```bash
cd v2_multi_language
pip install -r requirements_v2.txt
python unified_analyzer.py check
python unified_analyzer.py analyze /path/to/project --name MyProject
```

## 📊 对比

| 特性 | V1 | V2 |
|------|----|----|
| 支持语言 | Python | 7+ 种语言 |
| 性能 | 中等 | 高 (3-5x) |
| 数据流分析 | ❌ | ✅ |
| 安装复杂度 | 低 | 中 |
| 扩展性 | 低 | 高 |

## 📄 许可证

MIT License

## 🙏 致谢

- [tree-sitter](https://tree-sitter.github.io/)
- [tree-sitter-graph](https://github.com/tree-sitter/tree-sitter-graph)
""")
    
    print("✓ 创建根目录 README.md")
    
    # V1 目录 README
    v1_readme = PROJECT_ROOT / 'v1_python_only' / 'README.md'
    if not v1_readme.exists():
        # 从原来的 README.md 复制
        src = PROJECT_ROOT / 'README.md'
        if src.exists():
            # README.md 已经在 V1_FILES 中，会被移动
            pass
    
    # V2 目录 README
    v2_readme = PROJECT_ROOT / 'v2_multi_language' / 'README.md'
    if not v2_readme.exists():
        # 从 README_V2.md 复制并重命名
        src = PROJECT_ROOT / 'v2_multi_language' / 'README_V2.md'
        if src.exists():
            shutil.copy2(src, v2_readme)
            print("✓ 创建 v2_multi_language/README.md")


def create_project_structure_doc():
    """创建项目结构说明文档"""
    print("\n创建项目结构说明...")
    
    doc_path = PROJECT_ROOT / 'PROJECT_STRUCTURE.md'
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write("""# 项目结构说明

## 📁 目录结构

```
call_graph/
├── README.md                           # 项目总览
├── PROJECT_STRUCTURE.md                # 本文件
├── reorganize_project.py               # 项目重组脚本
│
├── v1_python_only/                     # V1: Python 专用版本
│   ├── README.md                       # V1 使用文档
│   ├── QUICKSTART.md                   # V1 快速开始
│   ├── main.py                         # V1 主程序
│   ├── database.py                     # V1 数据库层
│   ├── call_graph_extractor.py         # V1 提取器
│   ├── call_chain_analyzer.py          # V1 分析器
│   ├── config.py                       # V1 配置
│   ├── init_db.sql                     # V1 数据库结构
│   ├── requirements.txt                # V1 依赖
│   ├── example.py                      # Python 示例
│   └── setup_example.py                # 示例设置脚本
│
├── v2_multi_language/                  # V2: 多语言版本
│   ├── README.md                       # V2 主文档
│   ├── README_V2.md                    # V2 详细文档
│   ├── QUICKSTART_V2.md                # V2 快速开始
│   ├── unified_analyzer.py             # V2 主程序
│   ├── tsg_engine.py                   # TSG 引擎
│   ├── graph_database.py               # V2 数据库层
│   ├── config_v2.py                    # V2 配置
│   ├── init_graph_db.sql               # V2 数据库结构
│   ├── requirements_v2.txt             # V2 依赖
│   ├── test_c_cpp.py                   # C/C++ 测试
│   │
│   ├── tsg_rules/                      # TSG 规则文件
│   │   ├── python.tsg
│   │   ├── rust.tsg
│   │   ├── c.tsg
│   │   ├── cpp.tsg
│   │   ├── java.tsg
│   │   ├── javascript.tsg
│   │   └── typescript.tsg
│   │
│   └── examples/                       # 示例代码
│       ├── example.c
│       └── example.cpp
│
└── docs/                               # 共享文档
    ├── ARCHITECTURE_V2.md              # 架构设计
    ├── INSTALLATION.md                 # 安装指南
    ├── PROJECT_SUMMARY.md              # 项目总结
    ├── C_CPP_SUPPORT.md                # C/C++ 支持
    ├── C_CPP_COMPLETION_SUMMARY.md     # C/C++ 完成总结
    ├── TREE_SITTER_GRAPH_INTEGRATION.md # TSG 集成
    └── FILE_INDEX.md                   # 文件索引
```

## 📂 目录说明

### v1_python_only/
Python 专用版本，适合只需要分析 Python 代码的场景。

**特点**:
- 简单易用
- 无需 Rust 工具链
- 快速部署

**适用场景**:
- Python 项目分析
- 快速原型验证
- 学习代码分析基础

### v2_multi_language/
多语言版本，基于 tree-sitter-graph 的高性能实现。

**特点**:
- 支持 7 种语言
- 高性能（3-5x 更快）
- 声明式 TSG 规则
- 支持数据流分析

**适用场景**:
- 多语言项目分析
- 大型代码库
- 需要高性能的场景
- 需要扩展新语言

### docs/
共享文档目录，包含架构设计、安装指南等通用文档。

## 🎯 使用指南

### 使用 V1

```bash
cd v1_python_only
pip install -r requirements.txt
python main.py all
```

### 使用 V2

```bash
cd v2_multi_language
pip install -r requirements_v2.txt
python unified_analyzer.py analyze /path/to/project
```

## 🔄 版本迁移

从 V1 迁移到 V2:

1. V2 使用不同的数据库结构，需要重新分析
2. V2 的 API 略有不同，但功能更强大
3. 参考 `docs/INSTALLATION.md` 安装 V2 依赖

## 📚 文档索引

- **快速开始**: `v1_python_only/QUICKSTART.md` 或 `v2_multi_language/QUICKSTART_V2.md`
- **安装指南**: `docs/INSTALLATION.md`
- **架构设计**: `docs/ARCHITECTURE_V2.md`
- **C/C++ 支持**: `docs/C_CPP_SUPPORT.md`
- **完整索引**: `docs/FILE_INDEX.md`

## 🛠️ 开发指南

### 修改 V1
直接编辑 `v1_python_only/` 目录下的文件。

### 修改 V2
直接编辑 `v2_multi_language/` 目录下的文件。

### 添加新语言（V2）
1. 在 `v2_multi_language/tsg_rules/` 创建新的 .tsg 文件
2. 在 `v2_multi_language/config_v2.py` 注册语言
3. 测试和验证

## ⚠️ 注意事项

1. V1 和 V2 使用不同的数据库结构，不兼容
2. V2 需要安装 tree-sitter-graph (Rust)
3. 两个版本可以独立使用，互不影响
4. 共享文档在 `docs/` 目录

## 🔗 相关链接

- V1 文档: `v1_python_only/README.md`
- V2 文档: `v2_multi_language/README.md`
- 项目总览: `README.md`
""")
    
    print("✓ 创建 PROJECT_STRUCTURE.md")


def main():
    """主函数"""
    print("=" * 60)
    print("项目重组脚本")
    print("=" * 60)
    
    # 1. 创建目录
    create_directories()
    
    # 2. 移动 V1 文件
    move_v1_files()
    
    # 3. 移动 V2 文件
    move_v2_files()
    
    # 4. 创建 README
    create_readme_files()
    
    # 5. 创建项目结构说明
    create_project_structure_doc()
    
    print("\n" + "=" * 60)
    print("✓ 项目重组完成！")
    print("=" * 60)
    
    print("\n新的目录结构:")
    print("  call_graph/")
    print("  ├── v1_python_only/      # V1 版本（仅 Python）")
    print("  ├── v2_multi_language/   # V2 版本（多语言）")
    print("  └── docs/                # 共享文档")
    
    print("\n下一步:")
    print("  1. 查看 PROJECT_STRUCTURE.md 了解新结构")
    print("  2. 进入 v1_python_only/ 或 v2_multi_language/ 使用对应版本")
    print("  3. 可以删除根目录下的原始文件（已复制到子目录）")


if __name__ == '__main__':
    main()

