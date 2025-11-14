#!/bin/bash
# Call Graph Analyzer 便捷运行脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到项目目录
cd "$SCRIPT_DIR"

# 使用 uv run 运行工具
uv run call-graph "$@"

