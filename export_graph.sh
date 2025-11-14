#!/bin/bash
# =============================================================================
# 导出调用图辅助脚本
# 
# 功能：
# 1. 正确导出调用图为 DOT 格式
# 2. 自动验证导出结果
# 3. 可选生成 PNG 图片
# =============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 默认值
DB_FILE="call_graph.db"
OUTPUT_FILE="call_graph.dot"
GENERATE_PNG=false

# 帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -d, --database FILE    数据库文件路径 (默认: call_graph.db)"
    echo "  -o, --output FILE      输出 DOT 文件路径 (默认: call_graph.dot)"
    echo "  -p, --png              同时生成 PNG 图片"
    echo "  -h, --help             显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                                     # 使用默认值"
    echo "  $0 -d myproject.db -o output.dot      # 指定数据库和输出"
    echo "  $0 -d demo.db -o graph.dot -p         # 同时生成 PNG"
    echo ""
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--database)
            DB_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -p|--png)
            GENERATE_PNG=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}错误: 未知参数 '$1'${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
done

# 打印配置
echo -e "${CYAN}================================${NC}"
echo -e "${CYAN}导出调用图${NC}"
echo -e "${CYAN}================================${NC}"
echo ""
echo "配置:"
echo "  数据库: $DB_FILE"
echo "  输出文件: $OUTPUT_FILE"
echo "  生成PNG: $GENERATE_PNG"
echo ""

# 检查数据库文件
if [ ! -f "$DB_FILE" ]; then
    echo -e "${RED}✗ 错误: 数据库文件不存在: $DB_FILE${NC}"
    echo ""
    echo "提示: 请先分析项目"
    echo "  uv run call-graph --database $DB_FILE analyze /path/to/project --clear"
    exit 1
fi

echo -e "${GREEN}✓${NC} 数据库文件存在"

# 检查 Python 命令
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ 错误: Python 未安装${NC}"
    echo "安装方法: 请安装 Python 3.10+"
    exit 1
fi

# 确定使用 python 还是 python3
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

echo -e "${GREEN}✓${NC} Python 已安装 ($PYTHON_CMD)"

# 创建输出目录
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
if [ "$OUTPUT_DIR" != "." ] && [ ! -d "$OUTPUT_DIR" ]; then
    mkdir -p "$OUTPUT_DIR"
    echo -e "${GREEN}✓${NC} 创建输出目录: $OUTPUT_DIR"
fi

# 执行导出（使用正确的参数顺序）
echo ""
echo -e "${CYAN}正在导出...${NC}"
echo ""

# 注意：--database 必须在 export 之前
$PYTHON_CMD -m call_graph --database "$DB_FILE" export --output "$OUTPUT_FILE"

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}✗ 导出失败${NC}"
    exit 1
fi

# 验证导出结果
echo ""
echo -e "${CYAN}验证导出结果...${NC}"

# 检查文件是否存在
if [ ! -f "$OUTPUT_FILE" ]; then
    echo -e "${RED}✗ 输出文件未生成${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} 文件已生成"

# 检查文件大小
FILE_SIZE=$(wc -c < "$OUTPUT_FILE")
if [ "$FILE_SIZE" -lt 50 ]; then
    echo -e "${YELLOW}⚠ 警告: 文件太小 ($FILE_SIZE 字节)，可能数据库为空${NC}"
    echo ""
    echo "提示: 请检查数据库是否有数据"
    echo "  uv run call-graph --database $DB_FILE stats"
else
    echo -e "${GREEN}✓${NC} 文件大小: $FILE_SIZE 字节"
fi

# 检查 DOT 格式
if head -1 "$OUTPUT_FILE" | grep -q "digraph"; then
    echo -e "${GREEN}✓${NC} DOT 格式正确"
else
    echo -e "${RED}✗ 错误: 文件格式不正确${NC}"
    echo ""
    echo "文件内容:"
    head -5 "$OUTPUT_FILE"
    exit 1
fi

# 统计节点和边
NODE_COUNT=$(grep -c '\[label=' "$OUTPUT_FILE" || echo 0)
EDGE_COUNT=$(grep -c ' -> ' "$OUTPUT_FILE" || echo 0)

echo ""
echo "统计信息:"
echo "  节点数: $NODE_COUNT"
echo "  边数: $EDGE_COUNT"

# 生成 PNG（如果需要）
if [ "$GENERATE_PNG" = true ]; then
    echo ""
    echo -e "${CYAN}生成 PNG 图片...${NC}"
    
    if ! command -v dot &> /dev/null; then
        echo -e "${YELLOW}⚠ 警告: graphviz 未安装，无法生成 PNG${NC}"
        echo "安装方法:"
        echo "  macOS: brew install graphviz"
        echo "  Linux: apt install graphviz 或 yum install graphviz"
    else
        PNG_FILE="${OUTPUT_FILE%.dot}.png"
        
        dot -Tpng "$OUTPUT_FILE" -o "$PNG_FILE"
        
        if [ $? -eq 0 ]; then
            PNG_SIZE=$(wc -c < "$PNG_FILE")
            echo -e "${GREEN}✓${NC} PNG 图片已生成"
            echo "  文件: $PNG_FILE"
            echo "  大小: $PNG_SIZE 字节"
            
            # 在 macOS 上尝试打开图片
            if [[ "$OSTYPE" == "darwin"* ]] && command -v open &> /dev/null; then
                echo ""
                echo "尝试打开图片..."
                open "$PNG_FILE" 2>/dev/null
            fi
        else
            echo -e "${RED}✗ PNG 生成失败${NC}"
        fi
    fi
fi

# 总结
echo ""
echo -e "${CYAN}================================${NC}"
echo -e "${GREEN}✓ 导出成功！${NC}"
echo -e "${CYAN}================================${NC}"
echo ""
echo "输出文件:"
echo "  DOT: $OUTPUT_FILE"
if [ "$GENERATE_PNG" = true ] && [ -f "${OUTPUT_FILE%.dot}.png" ]; then
    echo "  PNG: ${OUTPUT_FILE%.dot}.png"
fi
echo ""
echo "查看内容:"
echo "  head -20 $OUTPUT_FILE"
echo ""
echo "生成其他格式:"
echo "  dot -Tpng $OUTPUT_FILE -o graph.png     # PNG 图片"
echo "  dot -Tsvg $OUTPUT_FILE -o graph.svg     # SVG 矢量图"
echo "  dot -Tpdf $OUTPUT_FILE -o graph.pdf     # PDF 文档"
echo ""

