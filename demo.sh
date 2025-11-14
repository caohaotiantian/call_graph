#!/bin/bash

# Call Graph Analyzer - 完整功能演示脚本
# 展示所有核心功能

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Python 命令
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# 项目路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SAMPLE_PROJECT="$SCRIPT_DIR/examples/sample_project"
DEMO_DB="$SCRIPT_DIR/demo.db"

# 打印分隔线
print_separator() {
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
}

# 打印标题
print_title() {
    print_separator
    echo -e "${BOLD}${GREEN}$1${NC}"
    print_separator
}

# 打印步骤
print_step() {
    echo -e "\n${YELLOW}▶ $1${NC}\n"
}

# 打印信息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 打印成功
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# 打印命令
print_command() {
    echo -e "${CYAN}$ $1${NC}"
}

# 等待用户按键
wait_for_key() {
    echo ""
    read -p "按 Enter 继续..."
    echo ""
}

# 清屏
clear_screen() {
    clear
}

# 检查依赖
check_dependencies() {
    print_title "检查环境依赖"
    
    print_step "检查 Python..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$($PYTHON_CMD --version)
        print_success "找到 $PYTHON_VERSION"
    else
        echo -e "${RED}错误: 未找到 Python 3${NC}"
        exit 1
    fi
    
    print_step "检查项目依赖..."
    if $PYTHON_CMD -c "import tree_sitter" 2>/dev/null; then
        print_success "依赖已安装"
    else
        echo -e "${YELLOW}警告: 依赖未安装${NC}"
        echo -e "${BLUE}请运行: pip install -e .${NC}"
        echo ""
        read -p "是否继续演示？(y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_step "检查示例项目..."
    if [ -d "$SAMPLE_PROJECT" ]; then
        FILE_COUNT=$(find "$SAMPLE_PROJECT" -type f \( -name "*.py" -o -name "*.js" -o -name "*.java" -o -name "*.go" -o -name "*.rs" -o -name "*.c" -o -name "*.cpp" -o -name "*.ts" \) | wc -l | tr -d ' ')
        print_success "找到示例项目（$FILE_COUNT 个文件）"
    else
        echo -e "${RED}错误: 示例项目不存在${NC}"
        exit 1
    fi
    
    wait_for_key
}

# 演示1: 项目分析（标准模式）
demo_analyze_standard() {
    clear_screen
    print_title "演示 1: 项目分析（标准模式）"
    
    print_info "标准模式适合小型项目（< 500 文件）"
    print_info "串行处理，内存占用少"
    echo ""
    
    print_step "分析示例项目（标准模式）"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB analyze $SAMPLE_PROJECT --clear"
    print_command "$CMD"
    echo ""
    
    $CMD
    
    print_success "标准模式分析完成！"
    wait_for_key
}

# 演示2: 项目分析（性能优化模式）
demo_analyze_optimized() {
    clear_screen
    print_title "演示 2: 项目分析（性能优化模式）⚡"
    
    print_info "优化模式适合大型项目（> 500 文件）"
    print_info "多进程并行处理，速度提升 5-7 倍"
    echo ""
    
    print_step "分析示例项目（性能优化模式）"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB analyze $SAMPLE_PROJECT --clear --fast"
    print_command "$CMD"
    echo ""
    
    $CMD
    
    print_success "性能优化模式分析完成！"
    wait_for_key
}

# 演示3: 查看统计信息
demo_stats() {
    clear_screen
    print_title "演示 3: 查看统计信息"
    
    print_info "查看数据库中的统计数据"
    echo ""
    
    print_step "显示统计信息"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB stats"
    print_command "$CMD"
    echo ""
    
    $CMD
    
    wait_for_key
}

# 演示4: 搜索函数
demo_search() {
    clear_screen
    print_title "演示 4: 搜索函数"
    
    print_info "支持模糊搜索函数名"
    echo ""
    
    # 搜索 "main"
    print_step "搜索包含 'main' 的函数"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB search main"
    print_command "$CMD"
    echo ""
    
    $CMD
    
    echo ""
    echo ""
    
    # 搜索 "process"
    print_step "搜索包含 'process' 的函数（显示详细信息）"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB search process --verbose"
    print_command "$CMD"
    echo ""
    
    $CMD
    
    wait_for_key
}

# 演示5: 查询调用者
demo_query_callers() {
    clear_screen
    print_title "演示 5: 查询调用者"
    
    print_info "查询哪些函数调用了目标函数"
    echo ""
    
    # 先搜索可用的函数
    print_step "搜索可用的函数"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB search '' | head -10"
    print_command "$CMD"
    echo ""
    
    FUNCTIONS=$($PYTHON_CMD call-graph.py --database $DEMO_DB search '' 2>/dev/null | grep -oE '^[0-9]+\. [a-zA-Z_][a-zA-Z0-9_]*' | head -5 | sed 's/^[0-9]*\. //')
    
    if [ -z "$FUNCTIONS" ]; then
        print_info "没有找到函数，跳过此演示"
        wait_for_key
        return
    fi
    
    # 选择第一个函数进行演示
    FIRST_FUNC=$(echo "$FUNCTIONS" | head -1)
    
    print_step "查询谁调用了 '$FIRST_FUNC'"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB query $FIRST_FUNC --callers"
    print_command "$CMD"
    echo ""
    
    $CMD
    
    wait_for_key
}

# 演示6: 查询被调用者
demo_query_callees() {
    clear_screen
    print_title "演示 6: 查询被调用者"
    
    print_info "查询目标函数调用了哪些函数"
    echo ""
    
    # 查询 main 函数
    print_step "查询 'main' 调用了哪些函数"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB query main --callees"
    print_command "$CMD"
    echo ""
    
    $CMD
    
    wait_for_key
}

# 演示7: 查询调用链
demo_query_chain() {
    clear_screen
    print_title "演示 7: 查询调用链"
    
    print_info "查询从目标函数向下的完整调用链"
    echo ""
    
    print_step "查询 'main' 的调用链（深度=5）"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB query main --chain --depth 5"
    print_command "$CMD"
    echo ""
    
    $CMD
    
    wait_for_key
}

# 演示8: 查询完整调用路径
demo_query_fullpath() {
    clear_screen
    print_title "演示 8: 查询完整调用路径"
    
    print_info "查询包含目标函数的完整调用路径（入口 -> 目标 -> 叶子）"
    echo ""
    
    # 先找一个有调用关系的函数
    print_step "搜索有调用关系的函数"
    FUNCTIONS=$($PYTHON_CMD call-graph.py --database $DEMO_DB search '' 2>/dev/null | grep -oE '^[0-9]+\. [a-zA-Z_][a-zA-Z0-9_]*' | sed 's/^[0-9]*\. //' | head -3)
    
    if [ -z "$FUNCTIONS" ]; then
        print_info "没有找到函数，跳过此演示"
        wait_for_key
        return
    fi
    
    TARGET_FUNC=$(echo "$FUNCTIONS" | head -1)
    
    print_step "查询 '$TARGET_FUNC' 的完整调用路径"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB query $TARGET_FUNC --fullpath"
    print_command "$CMD"
    echo ""
    
    $CMD
    
    echo ""
    echo ""
    
    print_step "查询 '$TARGET_FUNC' 的完整调用路径（详细模式）"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB query $TARGET_FUNC --fullpath --verbose"
    print_command "$CMD"
    echo ""
    
    $CMD
    
    wait_for_key
}

# 演示9: 导出调用图
demo_export() {
    clear_screen
    print_title "演示 9: 导出调用图"
    
    print_info "导出为 Graphviz DOT 格式，可生成可视化图表"
    echo ""
    
    OUTPUT_FILE="$SCRIPT_DIR/demo_graph.dot"
    
    print_step "导出调用图"
    CMD="$PYTHON_CMD call-graph.py --database $DEMO_DB export --output $OUTPUT_FILE"
    print_command "$CMD"
    echo ""
    
    $CMD
    
    print_success "调用图已导出到: $OUTPUT_FILE"
    echo ""
    
    print_info "可以使用以下命令生成图片："
    echo -e "${CYAN}  dot -Tpng $OUTPUT_FILE -o demo_graph.png${NC}"
    echo -e "${CYAN}  dot -Tsvg $OUTPUT_FILE -o demo_graph.svg${NC}"
    echo ""
    
    # 如果安装了 graphviz，自动生成图片
    if command -v dot &> /dev/null; then
        print_step "检测到 graphviz，正在生成 PNG 图片..."
        dot -Tpng "$OUTPUT_FILE" -o "$SCRIPT_DIR/demo_graph.png" 2>/dev/null && \
            print_success "PNG 图片已生成: $SCRIPT_DIR/demo_graph.png"
    else
        print_info "提示: 安装 graphviz 可以生成图片"
        echo -e "${BLUE}  Ubuntu/Debian: sudo apt install graphviz${NC}"
        echo -e "${BLUE}  macOS: brew install graphviz${NC}"
    fi
    
    wait_for_key
}

# 演示10: Python API 使用
demo_python_api() {
    clear_screen
    print_title "演示 10: Python API 使用"
    
    print_info "除了 CLI，也可以在 Python 代码中使用"
    echo ""
    
    print_step "创建示例 Python 脚本"
    
    API_DEMO_FILE="$SCRIPT_DIR/api_demo_example.py"
    
    cat > "$API_DEMO_FILE" << 'EOF'
#!/usr/bin/env python3
"""Call Graph Analyzer Python API 演示"""

from call_graph.analyzer import CallGraphAnalyzer

# 创建分析器
print("创建分析器...")
analyzer = CallGraphAnalyzer("demo.db")

try:
    # 获取统计信息
    print("\n获取统计信息:")
    stats = analyzer.get_statistics()
    print(f"  总符号数: {stats['total_symbols']}")
    print(f"  总调用关系: {stats['total_relations']}")
    
    # 搜索函数
    print("\n搜索函数 'main':")
    results = analyzer.search_functions("main")
    for i, result in enumerate(results[:3], 1):
        print(f"  {i}. {result['name']} - {result['file']}:{result['start_line']}")
    
    # 查询调用关系
    if results:
        func_name = results[0]['name']
        print(f"\n查询 '{func_name}' 的调用者:")
        callers = analyzer.query_callers(func_name)
        if callers:
            for i, caller in enumerate(callers[:3], 1):
                print(f"  {i}. {caller['caller_name']}")
        else:
            print("  (无调用者)")
    
    print("\n✓ API 演示完成！")
    
finally:
    analyzer.close()
EOF
    
    chmod +x "$API_DEMO_FILE"
    
    print_command "cat $API_DEMO_FILE"
    echo ""
    cat "$API_DEMO_FILE"
    echo ""
    echo ""
    
    print_step "运行 Python API 演示"
    print_command "$PYTHON_CMD $API_DEMO_FILE"
    echo ""
    
    $PYTHON_CMD "$API_DEMO_FILE"
    
    echo ""
    print_info "示例脚本保存在: $API_DEMO_FILE"
    
    wait_for_key
}

# 清理演示文件
cleanup() {
    print_step "清理演示文件"
    
    if [ -f "$DEMO_DB" ]; then
        rm -f "$DEMO_DB"
        print_success "已删除: $DEMO_DB"
    fi
    
    if [ -f "$SCRIPT_DIR/demo_graph.dot" ]; then
        rm -f "$SCRIPT_DIR/demo_graph.dot"
        print_success "已删除: demo_graph.dot"
    fi
    
    if [ -f "$SCRIPT_DIR/demo_graph.png" ]; then
        rm -f "$SCRIPT_DIR/demo_graph.png"
        print_success "已删除: demo_graph.png"
    fi
    
    if [ -f "$SCRIPT_DIR/api_demo_example.py" ]; then
        rm -f "$SCRIPT_DIR/api_demo_example.py"
        print_success "已删除: api_demo_example.py"
    fi
}

# 主函数
main() {
    clear_screen
    
    print_title "Call Graph Analyzer - 完整功能演示"
    
    echo -e "${BOLD}本演示将展示以下功能：${NC}"
    echo ""
    echo "  1. 项目分析（标准模式）"
    echo "  2. 项目分析（性能优化模式）⚡"
    echo "  3. 查看统计信息"
    echo "  4. 搜索函数"
    echo "  5. 查询调用者"
    echo "  6. 查询被调用者"
    echo "  7. 查询调用链"
    echo "  8. 查询完整调用路径"
    echo "  9. 导出调用图"
    echo "  10. Python API 使用"
    echo ""
    
    read -p "按 Enter 开始演示..."
    
    # 检查依赖
    check_dependencies
    
    # 运行演示
    demo_analyze_standard
    demo_analyze_optimized
    demo_stats
    demo_search
    demo_query_callers
    demo_query_callees
    demo_query_chain
    demo_query_fullpath
    demo_export
    demo_python_api
    
    # 完成
    clear_screen
    print_title "演示完成！🎉"
    
    echo -e "${GREEN}${BOLD}恭喜！你已经了解了 Call Graph Analyzer 的所有核心功能！${NC}"
    echo ""
    echo -e "${BOLD}快速参考：${NC}"
    echo ""
    echo -e "${CYAN}# 分析项目${NC}"
    echo "  python call-graph.py --database myproject.db analyze /path/to/project --clear"
    echo ""
    echo -e "${CYAN}# 性能优化模式（大型项目推荐）⚡${NC}"
    echo "  python call-graph.py --database myproject.db analyze /path/to/project --clear --fast"
    echo ""
    echo -e "${CYAN}# 查询调用关系${NC}"
    echo "  python call-graph.py --database myproject.db query main --callers"
    echo "  python call-graph.py --database myproject.db query main --callees"
    echo "  python call-graph.py --database myproject.db query main --chain"
    echo "  python call-graph.py --database myproject.db query main --fullpath"
    echo ""
    echo -e "${CYAN}# 搜索和统计${NC}"
    echo "  python call-graph.py --database myproject.db search \"keyword\""
    echo "  python call-graph.py --database myproject.db stats"
    echo ""
    echo -e "${CYAN}# 导出调用图${NC}"
    echo "  python call-graph.py --database myproject.db export --output graph.dot"
    echo ""
    echo -e "${BOLD}更多信息：${NC}"
    echo "  📖 README.md - 项目主页"
    echo "  📚 使用指南.md - 详细使用文档"
    echo "  💻 ./quick_demo.sh - 快速演示"
    echo ""
    
    read -p "是否清理演示文件？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cleanup
    fi
    
    echo ""
    print_success "感谢使用 Call Graph Analyzer！"
    echo ""
}

# 运行主函数
main

