"""
调用链分析器
分析和构建完整的函数调用链
"""
from typing import List, Dict, Set, Optional
from collections import defaultdict, deque
import json

from database import DatabaseManager


class CallChainAnalyzer:
    """调用链分析器"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.call_graph = defaultdict(list)  # 调用图: caller_id -> [(callee_id, call_info), ...]
        self.reverse_graph = defaultdict(list)  # 反向调用图: callee_id -> [(caller_id, call_info), ...]
        self._build_call_graph()
    
    def _build_call_graph(self):
        """构建调用图"""
        print("构建调用图...")
        calls = self.db_manager.get_function_calls()
        
        for call in calls:
            caller_id = call['caller_id']
            callee_id = call.get('callee_id')
            
            if callee_id:  # 只处理已解析的调用
                self.call_graph[caller_id].append((callee_id, call))
                self.reverse_graph[callee_id].append((caller_id, call))
        
        print(f"调用图节点数: {len(self.call_graph)}")
    
    def find_call_chains(self, start_function_id: str, max_depth: int = 5) -> List[Dict]:
        """
        查找从指定函数开始的所有调用链
        
        Args:
            start_function_id: 起始函数ID
            max_depth: 最大深度
        
        Returns:
            调用链列表
        """
        chains = []
        
        # BFS 搜索调用链
        queue = deque([(start_function_id, [start_function_id], 0)])
        visited = set()
        
        while queue:
            current_id, path, depth = queue.popleft()
            
            # 避免循环调用
            if current_id in visited and depth > 0:
                continue
            
            visited.add(current_id)
            
            # 达到最大深度
            if depth >= max_depth:
                continue
            
            # 获取当前函数调用的所有函数
            callees = self.call_graph.get(current_id, [])
            
            if not callees and depth > 0:
                # 叶子节点，记录调用链
                chain = self._create_chain_record(path, start_function_id)
                if chain:
                    chains.append(chain)
            
            for callee_id, call_info in callees:
                new_path = path + [callee_id]
                queue.append((callee_id, new_path, depth + 1))
                
                # 也记录这条路径
                chain = self._create_chain_record(new_path, start_function_id)
                if chain:
                    chains.append(chain)
        
        return chains
    
    def find_reverse_chains(self, target_function_id: str, max_depth: int = 5) -> List[Dict]:
        """
        查找所有调用到指定函数的调用链（反向查找）
        
        Args:
            target_function_id: 目标函数ID
            max_depth: 最大深度
        
        Returns:
            调用链列表
        """
        chains = []
        
        # BFS 反向搜索
        queue = deque([(target_function_id, [target_function_id], 0)])
        visited = set()
        
        while queue:
            current_id, path, depth = queue.popleft()
            
            if current_id in visited and depth > 0:
                continue
            
            visited.add(current_id)
            
            if depth >= max_depth:
                continue
            
            # 获取调用当前函数的所有函数
            callers = self.reverse_graph.get(current_id, [])
            
            if not callers and depth > 0:
                # 反向链的根节点
                reversed_path = list(reversed(path))
                chain = self._create_chain_record(reversed_path, reversed_path[0])
                if chain:
                    chains.append(chain)
            
            for caller_id, call_info in callers:
                new_path = path + [caller_id]
                queue.append((caller_id, new_path, depth + 1))
                
                # 记录路径
                reversed_path = list(reversed(new_path))
                chain = self._create_chain_record(reversed_path, reversed_path[0])
                if chain:
                    chains.append(chain)
        
        return chains
    
    def _create_chain_record(self, path: List[str], start_function_id: str) -> Optional[Dict]:
        """
        创建调用链记录
        
        Args:
            path: 函数ID路径
            start_function_id: 起始函数ID
        
        Returns:
            调用链记录字典
        """
        if len(path) < 2:
            return None
        
        # 获取函数名称
        function_names = []
        for func_id in path:
            symbol = self.db_manager.get_symbol_by_id(func_id)
            if symbol:
                function_names.append(symbol['name'])
            else:
                function_names.append(f"unknown({func_id})")
        
        # 构建调用链路径字符串
        chain_path = " -> ".join(function_names)
        
        # 中间调用的详细信息
        intermediate_calls = []
        for i in range(len(path) - 1):
            caller_id = path[i]
            callee_id = path[i + 1]
            
            # 查找对应的调用记录
            calls = self.db_manager.get_function_calls(caller_id=caller_id)
            for call in calls:
                if call.get('callee_id') == callee_id:
                    intermediate_calls.append({
                        'caller': function_names[i],
                        'callee': function_names[i + 1],
                        'file': call['caller_file'],
                        'line': call['call_line']
                    })
                    break
        
        return {
            'chain_path': chain_path,
            'chain_depth': len(path) - 1,
            'start_function_id': start_function_id,
            'end_function_id': path[-1],
            'intermediate_calls': json.dumps(intermediate_calls, ensure_ascii=False)
        }
    
    def analyze_and_save_all_chains(self, max_depth: int = 5):
        """
        分析并保存所有函数的调用链
        
        Args:
            max_depth: 最大深度
        """
        print("=" * 60)
        print("开始分析调用链...")
        print("=" * 60)
        
        # 清空旧数据
        self.db_manager.clear_call_chains()
        
        # 获取所有有调用关系的函数
        all_function_ids = set(self.call_graph.keys())
        
        print(f"共有 {len(all_function_ids)} 个函数有调用关系")
        
        all_chains = []
        for idx, func_id in enumerate(all_function_ids, 1):
            if idx % 10 == 0:
                print(f"进度: {idx}/{len(all_function_ids)}")
            
            chains = self.find_call_chains(func_id, max_depth)
            all_chains.extend(chains)
        
        # 去重（基于 chain_path）
        unique_chains = {}
        for chain in all_chains:
            key = f"{chain['start_function_id']}:{chain['chain_path']}"
            if key not in unique_chains:
                unique_chains[key] = chain
        
        # 保存到数据库
        print(f"\n保存 {len(unique_chains)} 条唯一调用链到数据库...")
        for chain in unique_chains.values():
            self.db_manager.insert_call_chain(chain)
        
        print("\n" + "=" * 60)
        print("调用链分析完成!")
        print(f"总调用链: {len(unique_chains)}")
        print("=" * 60)
    
    def get_function_call_depth(self, function_id: str) -> int:
        """
        获取函数的最大调用深度
        
        Args:
            function_id: 函数ID
        
        Returns:
            最大调用深度
        """
        max_depth = 0
        visited = set()
        
        def dfs(current_id, depth):
            nonlocal max_depth
            
            if current_id in visited:
                return
            
            visited.add(current_id)
            max_depth = max(max_depth, depth)
            
            callees = self.call_graph.get(current_id, [])
            for callee_id, _ in callees:
                dfs(callee_id, depth + 1)
        
        dfs(function_id, 0)
        return max_depth
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """
        查找循环依赖
        
        Returns:
            循环依赖列表，每个元素是一个函数ID的循环链
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor, _ in self.call_graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # 找到循环
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            path.pop()
            rec_stack.remove(node)
            return False
        
        for node in self.call_graph.keys():
            if node not in visited:
                dfs(node)
        
        return cycles
    
    def get_call_statistics(self) -> Dict:
        """
        获取调用统计信息
        
        Returns:
            统计信息字典
        """
        # 计算每个函数被调用的次数
        callee_counts = defaultdict(int)
        for callees in self.call_graph.values():
            for callee_id, _ in callees:
                callee_counts[callee_id] += 1
        
        # 找出最常被调用的函数
        most_called = sorted(callee_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 找出调用最多函数的函数
        most_caller = sorted(
            [(caller_id, len(callees)) for caller_id, callees in self.call_graph.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # 获取函数名称
        most_called_with_names = []
        for func_id, count in most_called:
            symbol = self.db_manager.get_symbol_by_id(func_id)
            name = symbol['name'] if symbol else func_id
            most_called_with_names.append((name, count))
        
        most_caller_with_names = []
        for func_id, count in most_caller:
            symbol = self.db_manager.get_symbol_by_id(func_id)
            name = symbol['name'] if symbol else func_id
            most_caller_with_names.append((name, count))
        
        return {
            'total_functions': len(self.call_graph),
            'most_called_functions': most_called_with_names,
            'most_caller_functions': most_caller_with_names,
            'average_calls_per_function': sum(len(v) for v in self.call_graph.values()) / len(self.call_graph) if self.call_graph else 0
        }


