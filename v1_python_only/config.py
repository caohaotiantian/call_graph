"""
配置文件
"""
import os

# 数据库配置
DB_PATH = os.environ.get('DB_PATH', 'call_graph.db')

# 源代码路径配置
SOURCE_CODE_ROOT = os.environ.get('SOURCE_CODE_ROOT', '.')

# Tree-sitter 配置
SUPPORTED_LANGUAGES = ['python']

# 调用类型定义
CALL_TYPES = {
    'call': 'direct_call',          # 直接函数调用
    'attribute': 'method_call',     # 方法调用
    'decorator': 'decorator_call',  # 装饰器调用
}

# 需要分析的符号类型
ANALYZABLE_SYMBOL_KINDS = ['function', 'method', 'class']


