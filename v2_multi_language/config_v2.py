"""
多语言代码分析系统配置
"""
import os
from pathlib import Path

# ===== 路径配置 =====
PROJECT_ROOT = Path(__file__).parent
DB_PATH = os.environ.get('GRAPH_DB_PATH', 'code_graph.db')
TSG_RULES_DIR = PROJECT_ROOT / 'tsg_rules'
CACHE_DIR = PROJECT_ROOT / '.cache'

# ===== tree-sitter-graph 配置 =====
TSG_BINARY = os.environ.get('TSG_BINARY', 'tree-sitter-graph')
TSG_TIMEOUT = int(os.environ.get('TSG_TIMEOUT', '300'))  # 5 minutes default

# ===== 语言配置 =====
SUPPORTED_LANGUAGES = {
    'python': {
        'extensions': ['.py', '.pyi'],
        'tsg_rules': 'python.tsg',
        'parser': 'tree-sitter-python',
    },
    'rust': {
        'extensions': ['.rs'],
        'tsg_rules': 'rust.tsg',
        'parser': 'tree-sitter-rust',
    },
    'c': {
        'extensions': ['.c', '.h'],
        'tsg_rules': 'c.tsg',
        'parser': 'tree-sitter-c',
    },
    'cpp': {
        'extensions': ['.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx'],
        'tsg_rules': 'cpp.tsg',
        'parser': 'tree-sitter-cpp',
    },
    'java': {
        'extensions': ['.java'],
        'tsg_rules': 'java.tsg',
        'parser': 'tree-sitter-java',
    },
    'javascript': {
        'extensions': ['.js', '.jsx', '.mjs'],
        'tsg_rules': 'javascript.tsg',
        'parser': 'tree-sitter-javascript',
    },
    'typescript': {
        'extensions': ['.ts', '.tsx'],
        'tsg_rules': 'typescript.tsg',
        'parser': 'tree-sitter-typescript',
    },
}

# ===== 节点类型定义 =====
NODE_TYPES = {
    'FUNCTION': 'function',
    'METHOD': 'method',
    'CLASS': 'class',
    'INTERFACE': 'interface',
    'STRUCT': 'struct',
    'TRAIT': 'trait',
    'ENUM': 'enum',
    'VARIABLE': 'variable',
    'PARAMETER': 'parameter',
    'MODULE': 'module',
    'NAMESPACE': 'namespace',
    'FIELD': 'field',
}

# ===== 边类型定义 =====
EDGE_TYPES = {
    # 调用关系
    'CALLS': 'calls',
    'METHOD_CALL': 'method_call',
    'CONSTRUCTOR_CALL': 'constructor_call',
    'INDIRECT_CALL': 'indirect_call',
    'STATIC_CALL': 'static_call',
    
    # 数据流
    'DEFINES': 'defines',
    'USES': 'uses',
    'ASSIGNS': 'assigns',
    'RETURNS': 'returns',
    'PARAMETER_PASS': 'parameter_pass',
    'DATA_DEPENDENCY': 'data_dependency',
    
    # 结构关系
    'CONTAINS': 'contains',
    'INHERITS': 'inherits',
    'IMPLEMENTS': 'implements',
    'IMPORTS': 'imports',
    'EXPORTS': 'exports',
    'EXTENDS': 'extends',
    
    # 类型关系
    'TYPE_OF': 'type_of',
    'INSTANTIATES': 'instantiates',
}

# ===== 数据流类型 =====
DATAFLOW_TYPES = {
    'DEF': 'definition',
    'USE': 'use',
    'ASSIGN': 'assignment',
    'RETURN': 'return',
    'PARAM': 'parameter',
    'FIELD_ACCESS': 'field_access',
    'ARRAY_ACCESS': 'array_access',
}

# ===== 分析配置 =====
ANALYSIS_CONFIG = {
    'max_call_chain_depth': int(os.environ.get('MAX_CALL_DEPTH', '10')),
    'max_dataflow_depth': int(os.environ.get('MAX_DATAFLOW_DEPTH', '5')),
    'enable_cross_file_analysis': os.environ.get('ENABLE_CROSS_FILE', 'true').lower() == 'true',
    'enable_dataflow_analysis': os.environ.get('ENABLE_DATAFLOW', 'true').lower() == 'true',
    'resolve_external_calls': os.environ.get('RESOLVE_EXTERNAL', 'false').lower() == 'true',
}

# ===== 性能配置 =====
PERFORMANCE_CONFIG = {
    'parallel_workers': int(os.environ.get('PARALLEL_WORKERS', '4')),
    'batch_size': int(os.environ.get('BATCH_SIZE', '100')),
    'cache_enabled': os.environ.get('CACHE_ENABLED', 'true').lower() == 'true',
    'max_file_size_mb': int(os.environ.get('MAX_FILE_SIZE_MB', '10')),
}

# ===== 排除模式 =====
EXCLUDE_PATTERNS = [
    'node_modules',
    '.git',
    '.svn',
    '__pycache__',
    'venv',
    'env',
    'build',
    'dist',
    'target',  # Rust
    'bin',
    'obj',
    '.idea',
    '.vscode',
    '*.pyc',
    '*.pyo',
    '*.so',
    '*.dylib',
    '*.dll',
]

# ===== 日志配置 =====
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# ===== 输出配置 =====
OUTPUT_FORMATS = ['json', 'csv', 'graphml', 'dot', 'cypher']
DEFAULT_OUTPUT_FORMAT = 'json'

# 创建必要的目录
CACHE_DIR.mkdir(exist_ok=True)
TSG_RULES_DIR.mkdir(exist_ok=True)

