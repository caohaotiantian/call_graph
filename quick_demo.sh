#!/bin/bash

# Call Graph Analyzer - 快速演示脚本
# 非交互式，快速展示核心功能

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Python 命令
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# 项目路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAMPLE_PROJECT="$SCRIPT_DIR/examples/sample_project"
DEMO_DB="$SCRIPT_DIR/quick_demo.db"

echo "════════════════════════════════════════════════════════════════"
echo "  Call Graph Analyzer - 快速演示"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 1. 分析项目（性能优化模式）
echo -e "${YELLOW}▶ 步骤 1: 分析示例项目（性能优化模式）${NC}"
echo -e "${CYAN}$ $PYTHON_CMD call-graph.py --database $DEMO_DB analyze $SAMPLE_PROJECT --clear --fast${NC}"
echo ""
$PYTHON_CMD call-graph.py --database "$DEMO_DB" analyze "$SAMPLE_PROJECT" --clear --fast
echo ""
echo -e "${GREEN}✓ 分析完成${NC}"
echo ""

# 2. 查看统计
echo "────────────────────────────────────────────────────────────────"
echo -e "${YELLOW}▶ 步骤 2: 查看统计信息${NC}"
echo -e "${CYAN}$ $PYTHON_CMD call-graph.py --database $DEMO_DB stats${NC}"
echo ""
$PYTHON_CMD call-graph.py --database "$DEMO_DB" stats
echo ""

# 3. 搜索函数
echo "────────────────────────────────────────────────────────────────"
echo -e "${YELLOW}▶ 步骤 3: 搜索函数${NC}"
echo -e "${CYAN}$ $PYTHON_CMD call-graph.py --database $DEMO_DB search main${NC}"
echo ""
$PYTHON_CMD call-graph.py --database "$DEMO_DB" search "main"
echo ""

# 4. 查询调用关系
echo "────────────────────────────────────────────────────────────────"
echo -e "${YELLOW}▶ 步骤 4: 查询 'main' 的调用关系${NC}"
echo ""

echo -e "${BLUE}4.1 查询被调用者${NC}"
echo -e "${CYAN}$ $PYTHON_CMD call-graph.py --database $DEMO_DB query main --callees${NC}"
echo ""
$PYTHON_CMD call-graph.py --database "$DEMO_DB" query main --callees 2>/dev/null || echo "(无结果)"
echo ""

echo -e "${BLUE}4.2 查询调用链${NC}"
echo -e "${CYAN}$ $PYTHON_CMD call-graph.py --database $DEMO_DB query main --chain --depth 5${NC}"
echo ""
$PYTHON_CMD call-graph.py --database "$DEMO_DB" query main --chain --depth 5 2>/dev/null || echo "(无结果)"
echo ""

# 5. 导出调用图
echo "────────────────────────────────────────────────────────────────"
echo -e "${YELLOW}▶ 步骤 5: 导出调用图${NC}"
OUTPUT_FILE="$SCRIPT_DIR/quick_demo_graph.dot"
echo -e "${CYAN}$ $PYTHON_CMD call-graph.py --database $DEMO_DB export --output $OUTPUT_FILE${NC}"
echo ""
$PYTHON_CMD call-graph.py --database "$DEMO_DB" export --output "$OUTPUT_FILE"
echo ""
echo -e "${GREEN}✓ 导出成功: $OUTPUT_FILE${NC}"
echo ""

# 完成
echo "════════════════════════════════════════════════════════════════"
echo -e "${BOLD}${GREEN}快速演示完成！ 🎉${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BOLD}生成的文件：${NC}"
echo "  📊 $DEMO_DB"
echo "  📈 $OUTPUT_FILE"
echo ""
echo -e "${BOLD}下一步：${NC}"
echo "  • 查看完整演示: ./demo.sh"
echo "  • 阅读文档: README.md 和 使用指南.md"
echo "  • 分析你的项目:"
echo ""
echo -e "${CYAN}    python call-graph.py --database myproject.db analyze /path/to/project --clear --fast${NC}"
echo ""
echo -e "${BOLD}清理演示文件：${NC}"
echo -e "${CYAN}    rm -f $DEMO_DB $OUTPUT_FILE${NC}"
echo ""

