"""
示例设置脚本
用于演示如何将 Python 代码解析并存储到数据库
这个脚本会解析 example.py 并填充 symbols 表
"""
import os
import hashlib
from tree_sitter import Language, Parser, Node
import tree_sitter_python as tspython
from database import DatabaseManager


class SymbolExtractor:
    """符号提取器"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.parser = Parser()
        PY_LANGUAGE = Language(tspython.language())
        self.parser.set_language(PY_LANGUAGE)
    
    def extract_file(self, file_path):
        """从文件中提取符号"""
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        tree = self.parser.parse(bytes(source_code, 'utf-8'))
        symbols = []
        
        self._traverse_tree(tree.root_node, file_path, source_code, symbols)
        return symbols
    
    def _traverse_tree(self, node, file_path, source_code, symbols, container=None):
        """遍历语法树"""
        # 函数定义
        if node.type in ['function_definition', 'async_function_definition']:
            name_node = node.child_by_field_name('name')
            if name_node:
                name = name_node.text.decode('utf-8')
                
                # 提取签名
                signature = self._extract_signature(node, source_code)
                
                # 提取代码片段
                code_excerpt = self._get_code_excerpt(node, source_code)
                
                # 生成唯一ID
                symbol_id = self._generate_id(file_path, name, node.start_point[0])
                
                symbols.append({
                    'id': symbol_id,
                    'file': file_path,
                    'name': name,
                    'kind': 'method' if container else 'function',
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1,
                    'start_byte': node.start_byte,
                    'end_byte': node.end_byte,
                    'container': container,
                    'signature': signature,
                    'language': 'python',
                    'extras_json': '{}',
                    'code_excerpt': code_excerpt,
                    'is_exported': 1
                })
        
        # 类定义
        elif node.type == 'class_definition':
            name_node = node.child_by_field_name('name')
            if name_node:
                class_name = name_node.text.decode('utf-8')
                
                # 添加类符号
                symbol_id = self._generate_id(file_path, class_name, node.start_point[0])
                code_excerpt = self._get_code_excerpt(node, source_code, max_lines=5)
                
                symbols.append({
                    'id': symbol_id,
                    'file': file_path,
                    'name': class_name,
                    'kind': 'class',
                    'start_line': node.start_point[0] + 1,
                    'end_line': node.end_point[0] + 1,
                    'start_byte': node.start_byte,
                    'end_byte': node.end_byte,
                    'container': container,
                    'signature': f"class {class_name}",
                    'language': 'python',
                    'extras_json': '{}',
                    'code_excerpt': code_excerpt,
                    'is_exported': 1
                })
                
                # 递归处理类的方法
                body = node.child_by_field_name('body')
                if body:
                    self._traverse_tree(body, file_path, source_code, symbols, class_name)
                return
        
        # 递归处理子节点
        for child in node.children:
            self._traverse_tree(child, file_path, source_code, symbols, container)
    
    def _extract_signature(self, node, source_code):
        """提取函数签名"""
        # 找到函数定义的第一行（包含 def 和参数）
        lines = source_code.split('\n')
        start_line = node.start_point[0]
        
        # 查找签名结束位置（找到冒号）
        signature_lines = []
        for i in range(start_line, min(start_line + 5, len(lines))):
            line = lines[i]
            signature_lines.append(line.strip())
            if ':' in line:
                break
        
        return ' '.join(signature_lines)
    
    def _get_code_excerpt(self, node, source_code, max_lines=10):
        """获取代码片段"""
        lines = source_code.split('\n')
        start_line = node.start_point[0]
        end_line = min(node.end_point[0] + 1, start_line + max_lines)
        
        excerpt_lines = lines[start_line:end_line]
        return '\n'.join(excerpt_lines)
    
    def _generate_id(self, file_path, name, line):
        """生成唯一ID"""
        unique_string = f"{file_path}:{name}:{line}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:16]
    
    def save_symbols(self, symbols):
        """保存符号到数据库"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            for symbol in symbols:
                cursor.execute("""
                    INSERT OR REPLACE INTO symbols 
                    (id, file, name, kind, start_line, end_line, start_byte, end_byte,
                     container, signature, language, extras_json, code_excerpt, is_exported)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol['id'], symbol['file'], symbol['name'], symbol['kind'],
                    symbol['start_line'], symbol['end_line'],
                    symbol['start_byte'], symbol['end_byte'],
                    symbol['container'], symbol['signature'],
                    symbol['language'], symbol['extras_json'],
                    symbol['code_excerpt'], symbol['is_exported']
                ))
            
            conn.commit()


def main():
    """主函数"""
    print("=" * 60)
    print("示例设置脚本")
    print("=" * 60)
    
    # 初始化数据库
    db = DatabaseManager('call_graph.db')
    print("✓ 数据库已初始化")
    
    # 创建提取器
    extractor = SymbolExtractor(db)
    
    # 解析示例文件
    example_file = 'example.py'
    if not os.path.exists(example_file):
        print(f"✗ 找不到文件: {example_file}")
        print("请确保 example.py 文件存在")
        return
    
    print(f"\n正在解析: {example_file}")
    symbols = extractor.extract_file(example_file)
    
    print(f"✓ 提取到 {len(symbols)} 个符号:")
    for symbol in symbols:
        print(f"  - {symbol['kind']}: {symbol['name']} (行 {symbol['start_line']}-{symbol['end_line']})")
    
    # 保存到数据库
    print(f"\n保存符号到数据库...")
    extractor.save_symbols(symbols)
    print("✓ 符号已保存")
    
    # 验证
    stats = db.get_statistics()
    print(f"\n数据库统计:")
    print(f"  总符号数: {stats['total_symbols']}")
    
    print("\n" + "=" * 60)
    print("设置完成！现在你可以运行:")
    print("  python main.py all")
    print("来提取和分析调用关系")
    print("=" * 60)


if __name__ == '__main__':
    main()


