#!/usr/bin/env python3
"""
Call Graph 工具启动脚本

使用方法:
    python call-graph.py --database myproject.db analyze /path/to/project
    python call-graph.py --database myproject.db stats
    python call-graph.py --help
"""

import sys
import os

# 将当前目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入并运行主程序
from call_graph.main import main

if __name__ == '__main__':
    main()


