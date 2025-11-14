"""
多语言代码解析器
使用tree-sitter解析源代码，提取函数定义和调用关系
"""
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from tree_sitter import Language, Parser, Node


# 语言配置
LANGUAGE_CONFIG = {
    'python': {
        'extensions': ['.py'],
        'module': 'tree_sitter_python',
        'function_types': ['function_definition', 'async_function_definition'],
        'call_types': ['call'],
    },
    'c': {
        'extensions': ['.c', '.h'],
        'module': 'tree_sitter_c',
        'function_types': ['function_definition'],
        'call_types': ['call_expression'],
    },
    'cpp': {
        'extensions': ['.cpp', '.cc', '.cxx', '.hpp', '.hxx', '.h'],
        'module': 'tree_sitter_cpp',
        'function_types': ['function_definition', 'function_declarator'],
        'call_types': ['call_expression'],
    },
    'java': {
        'extensions': ['.java'],
        'module': 'tree_sitter_java',
        'function_types': ['method_declaration', 'constructor_declaration'],
        'call_types': ['method_invocation'],
    },
    'rust': {
        'extensions': ['.rs'],
        'module': 'tree_sitter_rust',
        'function_types': ['function_item'],
        'call_types': ['call_expression'],
    },
    'javascript': {
        'extensions': ['.js', '.jsx', '.mjs'],
        'module': 'tree_sitter_javascript',
        'function_types': ['function_declaration', 'arrow_function', 'function_expression', 
                          'method_definition'],
        'call_types': ['call_expression'],
    },
    'typescript': {
        'extensions': ['.ts', '.tsx'],
        'module': 'tree_sitter_typescript',
        'submodule': 'typescript',
        'function_types': ['function_declaration', 'arrow_function', 'function_expression',
                          'method_definition', 'method_signature'],
        'call_types': ['call_expression'],
    },
    'go': {
        'extensions': ['.go'],
        'module': 'tree_sitter_go',
        'function_types': ['function_declaration', 'method_declaration'],
        'call_types': ['call_expression'],
    },
}


class LanguageParser:
    """多语言解析器基类"""
    
    def __init__(self, language_name: str):
        self.language_name = language_name
        self.config = LANGUAGE_CONFIG[language_name]
        self.language = self._load_language()
        # tree-sitter >= 0.21 使用 Language 包装器
        self.ts_language = Language(self.language) if not isinstance(self.language, Language) else self.language
        self.parser = Parser(self.ts_language)
    
    def _load_language(self):
        """加载tree-sitter语言"""
        module_name = self.config['module']
        
        try:
            if 'submodule' in self.config:
                # TypeScript需要特殊处理
                module = __import__(module_name, fromlist=[self.config['submodule']])
                lang_func = getattr(module, self.config['submodule'])
                return lang_func.language()
            else:
                module = __import__(module_name, fromlist=['language'])
                return module.language()
        except Exception as e:
            raise ImportError(f"无法加载{self.language_name}语言解析器: {e}")
    
    def parse_file(self, file_path: str) -> Optional[Node]:
        """解析文件"""
        try:
            with open(file_path, 'rb') as f:
                code = f.read()
            tree = self.parser.parse(code)
            return tree.root_node
        except Exception as e:
            print(f"解析文件失败 {file_path}: {e}")
            return None
    
    def get_node_text(self, node: Node, source_code: bytes) -> str:
        """获取节点的文本内容"""
        return source_code[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
    
    def generate_id(self, file_path: str, name: str, start_line: int) -> str:
        """生成唯一ID"""
        unique_str = f"{file_path}:{name}:{start_line}"
        return hashlib.md5(unique_str.encode()).hexdigest()
    
    def extract_function_name(self, node: Node, source_code: bytes) -> Optional[str]:
        """提取函数名称（需要子类实现）"""
        raise NotImplementedError
    
    def extract_functions(self, file_path: str) -> List[Dict[str, Any]]:
        """提取文件中的所有函数定义"""
        root = self.parse_file(file_path)
        if not root:
            return []
        
        with open(file_path, 'rb') as f:
            source_code = f.read()
        
        functions = []
        
        def visit_node(node: Node, container: Optional[str] = None):
            if node.type in self.config['function_types']:
                func_name = self.extract_function_name(node, source_code)
                if func_name:
                    func_id = self.generate_id(file_path, func_name, node.start_point[0])
                    
                    # 提取函数签名
                    signature = self.get_node_text(node, source_code).split('\n')[0]
                    if len(signature) > 200:
                        signature = signature[:200] + "..."
                    
                    functions.append({
                        'id': func_id,
                        'file': file_path,
                        'name': func_name,
                        'kind': 'function',
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1,
                        'start_byte': node.start_byte,
                        'end_byte': node.end_byte,
                        'container': container,
                        'signature': signature,
                        'language': self.language_name,
                        'is_exported': 1
                    })
                    
                    # 更新容器名称
                    new_container = func_name
                    for child in node.children:
                        visit_node(child, new_container)
                    return
            
            for child in node.children:
                visit_node(child, container)
        
        visit_node(root)
        return functions
    
    def extract_calls(self, file_path: str, functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取函数调用关系"""
        root = self.parse_file(file_path)
        if not root:
            return []
        
        with open(file_path, 'rb') as f:
            source_code = f.read()
        
        # 构建函数位置映射
        func_map = {}
        for func in functions:
            if func['file'] == file_path:
                func_map[(func['start_line'], func['end_line'])] = func
        
        calls = []
        
        def find_containing_function(line: int) -> Optional[Dict[str, Any]]:
            """查找包含给定行的函数"""
            for (start, end), func in func_map.items():
                if start <= line <= end:
                    return func
            return None
        
        def visit_node(node: Node):
            if node.type in self.config['call_types']:
                call_name = self.extract_call_name(node, source_code)
                if call_name:
                    line = node.start_point[0] + 1
                    caller = find_containing_function(line)
                    
                    if caller:
                        # 尝试匹配被调用的函数
                        callee_id = None
                        for func in functions:
                            if func['name'] == call_name:
                                callee_id = func['id']
                                break
                        
                        if not callee_id:
                            # 如果找不到定义，创建一个临时ID
                            callee_id = self.generate_id("external", call_name, 0)
                        
                        calls.append({
                            'caller_id': caller['id'],
                            'callee_id': callee_id,
                            'caller_name': caller['name'],
                            'callee_name': call_name,
                            'caller_file': file_path,
                            'callee_file': None,
                            'call_site_line': line,
                            'call_site_column': node.start_point[1],
                            'language': self.language_name
                        })
            
            for child in node.children:
                visit_node(child)
        
        visit_node(root)
        return calls
    
    def extract_call_name(self, node: Node, source_code: bytes) -> Optional[str]:
        """提取被调用函数的名称（需要子类实现）"""
        raise NotImplementedError


class PythonParser(LanguageParser):
    """Python语言解析器"""
    
    def __init__(self):
        super().__init__('python')
    
    def extract_function_name(self, node: Node, source_code: bytes) -> Optional[str]:
        for child in node.children:
            if child.type == 'identifier':
                return self.get_node_text(child, source_code)
        return None
    
    def extract_call_name(self, node: Node, source_code: bytes) -> Optional[str]:
        for child in node.children:
            if child.type == 'identifier':
                return self.get_node_text(child, source_code)
            elif child.type == 'attribute':
                # 处理 obj.method() 形式的调用
                for subchild in child.children:
                    if subchild.type == 'identifier' and subchild.start_byte != child.start_byte:
                        return self.get_node_text(subchild, source_code)
        return None


class CParser(LanguageParser):
    """C语言解析器"""
    
    def __init__(self):
        super().__init__('c')
    
    def extract_function_name(self, node: Node, source_code: bytes) -> Optional[str]:
        declarator = node.child_by_field_name('declarator')
        if declarator:
            if declarator.type == 'function_declarator':
                name_node = declarator.child_by_field_name('declarator')
                if name_node:
                    return self.get_node_text(name_node, source_code)
        return None
    
    def extract_call_name(self, node: Node, source_code: bytes) -> Optional[str]:
        function_node = node.child_by_field_name('function')
        if function_node:
            return self.get_node_text(function_node, source_code)
        return None


class CppParser(LanguageParser):
    """C++语言解析器"""
    
    def __init__(self):
        super().__init__('cpp')
    
    def extract_function_name(self, node: Node, source_code: bytes) -> Optional[str]:
        declarator = node.child_by_field_name('declarator')
        if declarator:
            # 处理各种声明形式
            if declarator.type == 'function_declarator':
                name_node = declarator.child_by_field_name('declarator')
                if name_node:
                    if name_node.type == 'qualified_identifier':
                        return self.get_node_text(name_node, source_code)
                    else:
                        return self.get_node_text(name_node, source_code)
        return None
    
    def extract_call_name(self, node: Node, source_code: bytes) -> Optional[str]:
        function_node = node.child_by_field_name('function')
        if function_node:
            if function_node.type == 'field_expression':
                field = function_node.child_by_field_name('field')
                if field:
                    return self.get_node_text(field, source_code)
            return self.get_node_text(function_node, source_code)
        return None


class JavaParser(LanguageParser):
    """Java语言解析器"""
    
    def __init__(self):
        super().__init__('java')
    
    def extract_function_name(self, node: Node, source_code: bytes) -> Optional[str]:
        name_node = node.child_by_field_name('name')
        if name_node:
            return self.get_node_text(name_node, source_code)
        return None
    
    def extract_call_name(self, node: Node, source_code: bytes) -> Optional[str]:
        name_node = node.child_by_field_name('name')
        if name_node:
            return self.get_node_text(name_node, source_code)
        
        # 处理方法链调用
        object_node = node.child_by_field_name('object')
        if object_node and object_node.type == 'method_invocation':
            return self.extract_call_name(object_node, source_code)
        
        return None


class RustParser(LanguageParser):
    """Rust语言解析器"""
    
    def __init__(self):
        super().__init__('rust')
    
    def extract_function_name(self, node: Node, source_code: bytes) -> Optional[str]:
        name_node = node.child_by_field_name('name')
        if name_node:
            return self.get_node_text(name_node, source_code)
        return None
    
    def extract_call_name(self, node: Node, source_code: bytes) -> Optional[str]:
        function_node = node.child_by_field_name('function')
        if function_node:
            if function_node.type == 'field_expression':
                field = function_node.child_by_field_name('field')
                if field:
                    return self.get_node_text(field, source_code)
            return self.get_node_text(function_node, source_code)
        return None


class JavaScriptParser(LanguageParser):
    """JavaScript语言解析器"""
    
    def __init__(self):
        super().__init__('javascript')
    
    def extract_function_name(self, node: Node, source_code: bytes) -> Optional[str]:
        name_node = node.child_by_field_name('name')
        if name_node:
            return self.get_node_text(name_node, source_code)
        
        # 匿名函数或箭头函数
        if node.type in ['arrow_function', 'function_expression']:
            parent = node.parent
            if parent and parent.type == 'variable_declarator':
                name_node = parent.child_by_field_name('name')
                if name_node:
                    return self.get_node_text(name_node, source_code)
        
        return None
    
    def extract_call_name(self, node: Node, source_code: bytes) -> Optional[str]:
        function_node = node.child_by_field_name('function')
        if function_node:
            if function_node.type == 'member_expression':
                property_node = function_node.child_by_field_name('property')
                if property_node:
                    return self.get_node_text(property_node, source_code)
            return self.get_node_text(function_node, source_code)
        return None


class TypeScriptParser(LanguageParser):
    """TypeScript语言解析器"""
    
    def __init__(self):
        super().__init__('typescript')
    
    def extract_function_name(self, node: Node, source_code: bytes) -> Optional[str]:
        name_node = node.child_by_field_name('name')
        if name_node:
            return self.get_node_text(name_node, source_code)
        
        # 匿名函数或箭头函数
        if node.type in ['arrow_function', 'function_expression']:
            parent = node.parent
            if parent and parent.type == 'variable_declarator':
                name_node = parent.child_by_field_name('name')
                if name_node:
                    return self.get_node_text(name_node, source_code)
        
        return None
    
    def extract_call_name(self, node: Node, source_code: bytes) -> Optional[str]:
        function_node = node.child_by_field_name('function')
        if function_node:
            if function_node.type == 'member_expression':
                property_node = function_node.child_by_field_name('property')
                if property_node:
                    return self.get_node_text(property_node, source_code)
            return self.get_node_text(function_node, source_code)
        return None


class GoParser(LanguageParser):
    """Go语言解析器"""
    
    def __init__(self):
        super().__init__('go')
    
    def extract_function_name(self, node: Node, source_code: bytes) -> Optional[str]:
        name_node = node.child_by_field_name('name')
        if name_node:
            func_name = self.get_node_text(name_node, source_code)
            
            # 对于方法声明，获取接收者类型
            if node.type == 'method_declaration':
                receiver = node.child_by_field_name('receiver')
                if receiver:
                    # 提取接收者类型
                    for child in receiver.children:
                        if child.type == 'parameter_list':
                            for param in child.children:
                                if param.type == 'parameter_declaration':
                                    type_node = param.child_by_field_name('type')
                                    if type_node:
                                        type_name = self.get_node_text(type_node, source_code)
                                        # 去除指针符号
                                        type_name = type_name.lstrip('*')
                                        return f"{type_name}.{func_name}"
            
            return func_name
        return None
    
    def extract_call_name(self, node: Node, source_code: bytes) -> Optional[str]:
        function_node = node.child_by_field_name('function')
        if function_node:
            # 处理选择器表达式（如 obj.Method()）
            if function_node.type == 'selector_expression':
                field_node = function_node.child_by_field_name('field')
                if field_node:
                    return self.get_node_text(field_node, source_code)
            # 处理普通函数调用
            return self.get_node_text(function_node, source_code)
        return None


# 解析器工厂
PARSER_CLASSES = {
    'python': PythonParser,
    'c': CParser,
    'cpp': CppParser,
    'java': JavaParser,
    'rust': RustParser,
    'javascript': JavaScriptParser,
    'typescript': TypeScriptParser,
    'go': GoParser,
}


def get_parser(language: str) -> LanguageParser:
    """获取指定语言的解析器"""
    parser_class = PARSER_CLASSES.get(language)
    if not parser_class:
        raise ValueError(f"不支持的语言: {language}")
    return parser_class()


def detect_language(file_path: str) -> Optional[str]:
    """根据文件扩展名检测语言"""
    ext = Path(file_path).suffix
    for lang, config in LANGUAGE_CONFIG.items():
        if ext in config['extensions']:
            return lang
    return None

