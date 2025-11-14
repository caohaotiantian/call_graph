#!/bin/bash
# =============================================================================
# Call Graph 工具快速演示脚本（无需交互）
# 
# 功能：快速展示核心功能，适合 CI/CD 或自动化演示
# =============================================================================

# 颜色定义
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
DB_FILE="demo.db"
PROJECT_DIR="examples/sample_project"

# 确定使用 python 还是 python3
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Call Graph 工具快速演示${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo ""

# 清理
if [ -f "$DB_FILE" ]; then
    rm "$DB_FILE"
    echo -e "${GREEN}✓${NC} 清理旧数据库"
fi

# 1. 分析项目
echo ""
echo -e "${CYAN}▶ 步骤 1/6: 分析多语言项目${NC}"
echo "支持: Python, C, C++, Java, Rust, JavaScript, TypeScript, Go"
$PYTHON_CMD -m call_graph --database "$DB_FILE" analyze "$PROJECT_DIR" --clear 2>&1 | grep -E "分析完成|找到|处理"

# 2. 统计信息
echo ""
echo -e "${CYAN}▶ 步骤 2/6: 查看统计信息${NC}"
$PYTHON_CMD -m call_graph --database "$DB_FILE" stats

# 3. 搜索函数
echo ""
echo -e "${CYAN}▶ 步骤 3/6: 搜索函数${NC}"
$PYTHON_CMD -m call_graph --database "$DB_FILE" search "process" | head -15

# 4. 查询调用关系
echo ""
echo -e "${CYAN}▶ 步骤 4/6: 查询调用关系${NC}"
echo "查询: process_data 函数调用了哪些函数"
$PYTHON_CMD -m call_graph --database "$DB_FILE" query process_data --callees

# 5. 完整路径查询（演示性能优化）
echo ""
echo -e "${CYAN}▶ 步骤 5/6: 完整调用路径查询（含性能优化）${NC}"
echo "查询: calculate 函数的完整调用路径"
$PYTHON_CMD -m call_graph --database "$DB_FILE" query calculate --fullpath --verbose

# 6. 导出调用图
echo ""
echo -e "${CYAN}▶ 步骤 6/6: 导出调用图${NC}"
mkdir -p demo_output
$PYTHON_CMD -m call_graph --database "$DB_FILE" export --output demo_output/call_graph.dot
echo -e "${GREEN}✓${NC} 调用图已导出到: demo_output/call_graph.dot"

# 总结
echo ""
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ 快速演示完成！${NC}"
echo ""
echo "关键特性："
echo "  ✨ 支持 8 种编程语言"
echo "  ✨ 自动路径去重"
echo "  ✨ 5-100倍性能提升"
echo "  ✨ 完整调用路径分析"
echo ""
echo "完整演示: ./demo.sh"
echo "查看文档: cat README.md"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"

