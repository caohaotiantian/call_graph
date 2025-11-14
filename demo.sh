#!/bin/bash
# =============================================================================
# Call Graph 工具完整功能演示脚本
# 
# 功能：
# 1. 分析多语言示例项目
# 2. 展示所有查询功能
# 3. 演示性能优化特性
# 4. 生成可视化调用图
# =============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置
DB_FILE="demo.db"
PROJECT_DIR="examples/sample_project"
OUTPUT_DIR="demo_output"

# 打印带颜色的标题
print_title() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# 打印步骤
print_step() {
    echo -e "${GREEN}▶ $1${NC}"
}

# 打印警告
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# 打印错误
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 打印成功
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# 打印分隔线
print_separator() {
    echo -e "${BLUE}───────────────────────────────────────────────────────────────────────${NC}"
}

# 暂停等待用户
pause() {
    echo ""
    echo -e "${PURPLE}按回车键继续...${NC}"
    read
}

# 检查依赖
check_dependencies() {
    print_title "检查依赖"
    
    print_step "检查 Python 是否安装..."
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        print_error "Python 未安装，请先安装 Python 3.10+"
        exit 1
    fi
    
    # 确定使用 python 还是 python3
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
    
    print_success "Python 已安装 ($PYTHON_CMD)"
    
    print_step "检查依赖..."
    # 尝试导入 tree_sitter 检查依赖是否安装
    if ! $PYTHON_CMD -c "import tree_sitter" 2>/dev/null; then
        print_warning "依赖未安装"
        print_warning "请先安装依赖："
        echo "  pip install -e ."
        echo ""
        echo "  或使用虚拟环境："
        echo "  python -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install -e ."
        echo ""
        read -p "按回车键退出..."
        exit 1
    else
        print_success "依赖已安装"
    fi
    
    print_step "检查示例项目目录..."
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "示例项目目录不存在: $PROJECT_DIR"
        exit 1
    fi
    print_success "示例项目目录存在"
    
    print_step "创建输出目录..."
    mkdir -p "$OUTPUT_DIR"
    print_success "输出目录已创建: $OUTPUT_DIR"
}

# 清理旧数据
cleanup() {
    print_title "清理旧数据"
    
    if [ -f "$DB_FILE" ]; then
        print_step "删除旧数据库文件..."
        rm "$DB_FILE"
        print_success "旧数据库已删除"
    else
        print_step "未找到旧数据库文件，跳过清理"
    fi
}

# 分析项目
analyze_project() {
    print_title "场景 1: 分析多语言项目"
    
    print_step "开始分析示例项目..."
    echo -e "${BLUE}支持的语言: Python, C, C++, Java, Rust, JavaScript, TypeScript, Go${NC}"
    echo ""
    
    $PYTHON_CMD -m call_graph --database "$DB_FILE" analyze "$PROJECT_DIR" --clear
    
    if [ $? -eq 0 ]; then
        print_success "项目分析完成"
    else
        print_error "项目分析失败"
        exit 1
    fi
    
    pause
}

# 查看统计信息
show_statistics() {
    print_title "场景 2: 查看统计信息"
    
    print_step "显示数据库统计信息..."
    echo ""
    
    $PYTHON_CMD -m call_graph --database "$DB_FILE" stats
    
    pause
}

# 搜索函数
search_functions() {
    print_title "场景 3: 搜索函数"
    
    print_step "搜索包含 'user' 的函数..."
    echo ""
    
    $PYTHON_CMD -m call_graph --database "$DB_FILE" search "user" --verbose
    
    print_separator
    
    print_step "搜索包含 'process' 的函数..."
    echo ""
    
    $PYTHON_CMD -m call_graph --database "$DB_FILE" search "process"
    
    pause
}

# 查询调用关系
query_relationships() {
    print_title "场景 4: 查询函数调用关系"
    
    # 查询谁调用了某个函数
    print_step "查询谁调用了 'validate_input' 函数..."
    echo ""
    
    $PYTHON_CMD -m call_graph --database "$DB_FILE" query validate_input --callers
    
    print_separator
    
    # 查询某个函数调用了哪些函数
    print_step "查询 'process_data' 函数调用了哪些函数..."
    echo ""
    
    $PYTHON_CMD -m call_graph --database "$DB_FILE" query process_data --callees
    
    pause
}

# 查询调用链
query_call_chain() {
    print_title "场景 5: 查询调用链（向下）"
    
    print_step "查询从 'main' 函数开始的调用链（深度3）..."
    echo ""
    
    $PYTHON_CMD -m call_graph --database "$DB_FILE" query main --chain --depth 3
    
    pause
}

# 查询完整调用路径（演示去重和性能优化）
query_full_paths() {
    print_title "场景 6: 查询完整调用路径（向上+向下）"
    
    print_step "查询 'calculate' 函数的完整调用路径..."
    echo -e "${BLUE}特性: 自动去重、性能统计${NC}"
    echo ""
    
    $PYTHON_CMD -m call_graph --database "$DB_FILE" query calculate --fullpath --verbose
    
    print_separator
    
    print_step "查询 'process_data' 函数的完整调用路径..."
    echo ""
    
    $PYTHON_CMD -m call_graph --database "$DB_FILE" query process_data --fullpath --verbose
    
    print_separator
    
    print_step "查询 'addUser' 函数的完整调用路径..."
    echo ""
    
    $PYTHON_CMD -m call_graph --database "$DB_FILE" query addUser --fullpath
    
    pause
}

# 演示性能优化
demo_performance() {
    print_title "场景 7: 性能优化演示"
    
    print_step "运行性能优化示例程序..."
    echo -e "${BLUE}展示: 去重、批量查询、路径限制${NC}"
    echo ""
    
    $PYTHON_CMD examples/example_performance.py
    
    pause
}

# 导出调用图
export_graph() {
    print_title "场景 8: 导出调用图"
    
    print_step "导出为 DOT 格式..."
    echo ""
    
    DOT_FILE="$OUTPUT_DIR/call_graph.dot"
    $PYTHON_CMD -m call_graph --database "$DB_FILE" export --output "$DOT_FILE"
    
    if [ $? -eq 0 ]; then
        print_success "调用图已导出到: $DOT_FILE"
        
        # 检查是否安装了 graphviz
        if command -v dot &> /dev/null; then
            print_step "生成 PNG 图片..."
            PNG_FILE="$OUTPUT_DIR/call_graph.png"
            dot -Tpng "$DOT_FILE" -o "$PNG_FILE"
            
            if [ $? -eq 0 ]; then
                print_success "PNG 图片已生成: $PNG_FILE"
            else
                print_warning "PNG 图片生成失败"
            fi
        else
            print_warning "未安装 graphviz，跳过 PNG 生成"
            print_warning "安装方法: brew install graphviz (macOS) 或 apt install graphviz (Linux)"
        fi
    else
        print_error "导出失败"
    fi
    
    pause
}

# Python API 演示
demo_python_api() {
    print_title "场景 9: Python API 使用演示"
    
    print_step "运行 Python API 示例程序..."
    echo ""
    
    $PYTHON_CMD examples/example_usage.py
    
    pause
}

# 完整路径查询 API 演示
demo_fullpath_api() {
    print_title "场景 10: 完整路径查询 API 演示"
    
    print_step "运行完整路径查询示例..."
    echo ""
    
    $PYTHON_CMD examples/example_fullpath.py
    
    pause
}

# 多语言支持展示
demo_multi_language() {
    print_title "场景 11: 多语言支持展示"
    
    print_step "列出示例项目中的所有文件..."
    echo ""
    ls -lh "$PROJECT_DIR"
    echo ""
    
    print_step "支持的语言及特性:"
    echo -e "${GREEN}  ✓ Python   (.py)  - 函数定义、方法、调用${NC}"
    echo -e "${GREEN}  ✓ C        (.c)   - 函数定义、调用${NC}"
    echo -e "${GREEN}  ✓ C++      (.cpp) - 类、方法、模板${NC}"
    echo -e "${GREEN}  ✓ Java     (.java)- 类、方法、静态方法${NC}"
    echo -e "${GREEN}  ✓ Rust     (.rs)  - 函数、impl、trait${NC}"
    echo -e "${GREEN}  ✓ JavaScript (.js) - 函数、箭头函数${NC}"
    echo -e "${GREEN}  ✓ TypeScript (.ts) - 类、接口、泛型${NC}"
    echo -e "${GREEN}  ✓ Go       (.go)  - 函数、方法${NC}"
    
    print_separator
    
    print_step "查询跨语言调用关系..."
    echo ""
    $PYTHON_CMD -m call_graph --database "$DB_FILE" query main --callees
    
    pause
}

# 生成报告
generate_report() {
    print_title "场景 12: 生成演示报告"
    
    REPORT_FILE="$OUTPUT_DIR/demo_report.txt"
    
    print_step "生成演示报告..."
    
    {
        echo "Call Graph 工具演示报告"
        echo "生成时间: $(date)"
        echo ""
        echo "="*70
        echo "1. 数据库统计"
        echo "="*70
        $PYTHON_CMD -m call_graph --database "$DB_FILE" stats
        echo ""
        echo "="*70
        echo "2. 函数搜索示例"
        echo "="*70
        $PYTHON_CMD -m call_graph --database "$DB_FILE" search "process"
        echo ""
        echo "="*70
        echo "3. 完整路径查询示例"
        echo "="*70
        $PYTHON_CMD -m call_graph --database "$DB_FILE" query calculate --fullpath --verbose
    } > "$REPORT_FILE"
    
    print_success "报告已生成: $REPORT_FILE"
    
    pause
}

# 显示总结
show_summary() {
    print_title "演示总结"
    
    echo -e "${GREEN}✓ 已完成所有功能演示！${NC}"
    echo ""
    echo "演示内容："
    echo "  1. ✓ 多语言项目分析"
    echo "  2. ✓ 统计信息查看"
    echo "  3. ✓ 函数搜索"
    echo "  4. ✓ 调用关系查询"
    echo "  5. ✓ 调用链查询"
    echo "  6. ✓ 完整路径查询（含去重和性能优化）"
    echo "  7. ✓ 性能优化演示"
    echo "  8. ✓ 调用图导出"
    echo "  9. ✓ Python API 使用"
    echo " 10. ✓ 完整路径 API"
    echo " 11. ✓ 多语言支持"
    echo " 12. ✓ 报告生成"
    echo ""
    echo "生成的文件："
    echo "  - 数据库文件: $DB_FILE"
    echo "  - 输出目录: $OUTPUT_DIR/"
    if [ -f "$OUTPUT_DIR/call_graph.dot" ]; then
        echo "    - call_graph.dot (调用图)"
    fi
    if [ -f "$OUTPUT_DIR/call_graph.png" ]; then
        echo "    - call_graph.png (可视化图片)"
    fi
    if [ -f "$OUTPUT_DIR/demo_report.txt" ]; then
        echo "    - demo_report.txt (演示报告)"
    fi
    echo ""
    echo "关键特性："
    echo "  ✨ 支持 8 种编程语言"
    echo "  ✨ 自动路径去重"
    echo "  ✨ 批量查询优化（5-100倍性能提升）"
    echo "  ✨ 路径数量可控"
    echo "  ✨ 性能统计透明"
    echo "  ✨ CLI 和 Python API 双接口"
    echo ""
    echo "下一步："
    echo "  - 查看文档: README.md, 使用说明.md"
    echo "  - 运行示例: python examples/example_*.py"
    echo "  - 分析自己的项目: python call-graph.py --database my.db analyze /path/to/project"
    echo ""
    print_success "演示完成！"
}

# 主函数
main() {
    clear
    
    print_title "Call Graph 工具完整功能演示"
    
    echo "本演示将展示 call-graph 工具的所有功能，包括："
    echo ""
    echo "  • 多语言项目分析 (Python, C, C++, Java, Rust, JS, TS, Go)"
    echo "  • 函数调用关系查询"
    echo "  • 完整调用路径分析（含性能优化）"
    echo "  • 调用图可视化"
    echo "  • Python API 使用"
    echo ""
    echo "预计时间: 5-10 分钟"
    echo ""
    
    pause
    
    # 执行各个演示场景
    check_dependencies
    cleanup
    analyze_project
    show_statistics
    search_functions
    query_relationships
    query_call_chain
    query_full_paths
    demo_performance
    export_graph
    demo_python_api
    demo_fullpath_api
    demo_multi_language
    generate_report
    show_summary
}

# 运行主函数
main

