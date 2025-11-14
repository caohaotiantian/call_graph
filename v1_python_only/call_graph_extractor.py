"""
函数调用关系提取器
使用 tree-sitter 从源代码中提取函数调用关系
"""
import os
from typing import List, Dict, Set, Optional
from tree_sitter import Language, Parser, Node
import tree_sitter_python as tspython

import config
from database import DatabaseManager


class CallGraphExtractor:
    """调用图提取器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.parser = Parser()
        
        # 初始化 Python 语言解析器
        PY_LANGUAGE = Language(tspython.language())
        self.parser.set_language(PY_LANGUAGE)
        
        # 缓存：文件 -> 符号映射
        self.symbols_cache = {}
        self._load_symbols_cache()
    
    def _load_symbols_cache(self):
        """加载符号缓存"""
        symbols = self.db_manager.get_all_symbols()
        for symbol in symbols:
            file_path = symbol['file']
            if file_path not in self.symbols_cache:
                self.symbols_cache[file_path] = []
            self.symbols_cache[file_path].append(symbol)
    
    def extract_all_calls(self) -> List[Dict]:
        """
        提取所有函数调用关系
        
        Returns:
            调用关系列表
        """
        all_calls = []
        
        # 获取所有函数和方法符号
        function_symbols = self.db_manager.get_all_symbols(kind='function')
        method_symbols = self.db_manager.get_all_symbols(kind='method')
        
        all_symbols = function_symbols + method_symbols
        
        print(f"开始分析 {len(all_symbols)} 个函数/方法...")
        
        for idx, symbol in enumerate(all_symbols, 1):
            if idx % 10 == 0:
                print(f"进度: {idx}/{len(all_symbols)}")
            
            calls = self._extract_calls_from_symbol(symbol)
            all_calls.extend(calls)
        
        print(f"共提取到 {len(all_calls)} 个调用关系")
        return all_calls
    
    def _extract_calls_from_symbol(self, symbol: Dict) -> List[Dict]:
        """
        从单个符号中提取调用关系
        
        Args:
            symbol: 符号信息
        
        Returns:
            该符号内的所有调用关系
        """
        calls = []
        file_path = symbol['file']
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return calls
        
        try:
            # 读取源代码
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # 解析代码
            tree = self.parser.parse(bytes(source_code, 'utf-8'))
            root_node = tree.root_node
            
            # 找到对应的函数节点
            function_node = self._find_function_node(
                root_node, 
                symbol['name'], 
                symbol['start_line']
            )
            
            if not function_node:
                return calls
            
            # 提取函数内的所有调用
            call_nodes = self._find_all_calls(function_node)
            
            for call_node in call_nodes:
                call_info = self._extract_call_info(
                    call_node, 
                    source_code, 
                    symbol
                )
                if call_info:
                    calls.append(call_info)
        
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
        
        return calls
    
    def _find_function_node(self, root_node: Node, name: str, start_line: int) -> Optional[Node]:
        """
        查找指定的函数节点
        
        Args:
            root_node: 根节点
            name: 函数名
            start_line: 起始行号
        
        Returns:
            函数节点或 None
        """
        def traverse(node):
            if node.type in ['function_definition', 'async_function_definition']:
                # 获取函数名
                name_node = node.child_by_field_name('name')
                if name_node and name_node.text.decode('utf-8') == name:
                    # 检查行号（tree-sitter 行号从0开始，数据库从1开始）
                    if node.start_point[0] + 1 == start_line:
                        return node
            
            for child in node.children:
                result = traverse(child)
                if result:
                    return result
            return None
        
        return traverse(root_node)
    
    def _find_all_calls(self, node: Node) -> List[Node]:
        """
        查找节点内的所有函数调用
        
        Args:
            node: 起始节点
        
        Returns:
            调用节点列表
        """
        calls = []
        
        def traverse(n):
            # 函数调用节点
            if n.type == 'call':
                calls.append(n)
            
            # 递归遍历子节点
            for child in n.children:
                traverse(child)
        
        traverse(node)
        return calls
    
    def _extract_call_info(self, call_node: Node, source_code: str, caller_symbol: Dict) -> Optional[Dict]:
        """
        从调用节点提取调用信息
        
        Args:
            call_node: 调用节点
            source_code: 源代码
            caller_symbol: 调用者符号信息
        
        Returns:
            调用信息字典
        """
        try:
            # 获取被调用函数的名称
            function_node = call_node.child_by_field_name('function')
            if not function_node:
                return None
            
            callee_name = None
            call_type = 'direct_call'
            
            # 处理不同类型的调用
            if function_node.type == 'identifier':
                # 直接调用: func()
                callee_name = function_node.text.decode('utf-8')
                call_type = 'direct_call'
            
            elif function_node.type == 'attribute':
                # 方法调用: obj.method()
                attr_node = function_node.child_by_field_name('attribute')
                if attr_node:
                    callee_name = attr_node.text.decode('utf-8')
                    call_type = 'method_call'
            
            if not callee_name:
                return None
            
            # 获取调用位置
            call_line = call_node.start_point[0] + 1
            call_column = call_node.start_point[1]
            
            # 尝试解析被调用者
            callee_id, callee_file = self._resolve_callee(
                callee_name,
                caller_symbol['file'],
                call_type
            )
            
            return {
                'caller_id': caller_symbol['id'],
                'caller_name': caller_symbol['name'],
                'caller_file': caller_symbol['file'],
                'callee_name': callee_name,
                'callee_id': callee_id,
                'callee_file': callee_file,
                'call_line': call_line,
                'call_column': call_column,
                'call_type': call_type,
                'is_resolved': 1 if callee_id else 0
            }
        
        except Exception as e:
            print(f"提取调用信息时出错: {str(e)}")
            return None
    
    def _resolve_callee(self, callee_name: str, caller_file: str, call_type: str) -> tuple:
        """
        解析被调用者的ID和文件
        
        Args:
            callee_name: 被调用者名称
            caller_file: 调用者文件
            call_type: 调用类型
        
        Returns:
            (callee_id, callee_file) 元组
        """
        # 优先在同一文件中查找
        candidates = self.db_manager.find_symbols_by_name(callee_name, caller_file)
        
        # 如果同文件中没找到，扩大到所有文件
        if not candidates:
            candidates = self.db_manager.find_symbols_by_name(callee_name)
        
        # 如果找到匹配的符号
        if candidates:
            # 如果有多个候选，优先选择同文件的
            for candidate in candidates:
                if candidate['file'] == caller_file:
                    return candidate['id'], candidate['file']
            
            # 否则返回第一个候选
            return candidates[0]['id'], candidates[0]['file']
        
        # 未找到
        return None, None
    
    def extract_and_save(self):
        """提取并保存所有调用关系"""
        print("=" * 60)
        print("开始提取函数调用关系...")
        print("=" * 60)
        
        # 清空旧数据
        self.db_manager.clear_function_calls()
        
        # 提取调用关系
        calls = self.extract_all_calls()
        
        # 批量保存
        if calls:
            print(f"\n保存 {len(calls)} 个调用关系到数据库...")
            self.db_manager.batch_insert_function_calls(calls)
            
            # 统计信息
            resolved_count = sum(1 for c in calls if c['is_resolved'])
            unresolved_count = len(calls) - resolved_count
            
            print("\n" + "=" * 60)
            print("提取完成!")
            print(f"总调用关系: {len(calls)}")
            print(f"已解析: {resolved_count}")
            print(f"未解析: {unresolved_count}")
            print(f"解析率: {resolved_count/len(calls)*100:.2f}%")
            print("=" * 60)
        else:
            print("\n未找到任何调用关系")


