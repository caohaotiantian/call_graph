"""
tree-sitter-graph 引擎包装器
负责调用 TSG CLI 并处理输出
"""
import subprocess
import json
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

import config_v2 as config

logger = logging.getLogger(__name__)


class TSGEngine:
    """tree-sitter-graph 引擎"""
    
    def __init__(self, tsg_binary: str = None):
        self.tsg_binary = tsg_binary or config.TSG_BINARY
        self._check_tsg_installed()
    
    def _check_tsg_installed(self):
        """检查 tree-sitter-graph 是否已安装"""
        try:
            result = subprocess.run(
                [self.tsg_binary, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"Found tree-sitter-graph: {result.stdout.strip()}")
            else:
                raise RuntimeError("tree-sitter-graph not responding correctly")
        except FileNotFoundError:
            raise RuntimeError(
                f"tree-sitter-graph not found at '{self.tsg_binary}'. "
                "Please install it with: cargo install --features cli tree-sitter-graph"
            )
        except Exception as e:
            raise RuntimeError(f"Error checking tree-sitter-graph: {str(e)}")
    
    def extract_graph(
        self,
        source_file: str,
        rules_file: str,
        language: str = None,
        output_format: str = 'json'
    ) -> Dict[str, Any]:
        """
        使用 TSG 从源文件提取图数据
        
        Args:
            source_file: 源代码文件路径
            rules_file: TSG 规则文件路径
            language: 语言名称（可选，用于查找 tree-sitter 解析器）
            output_format: 输出格式（json, dot, etc.）
        
        Returns:
            提取的图数据（字典格式）
        """
        if not os.path.exists(source_file):
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        if not os.path.exists(rules_file):
            raise FileNotFoundError(f"Rules file not found: {rules_file}")
        
        # 检查文件大小
        file_size_mb = os.path.getsize(source_file) / (1024 * 1024)
        if file_size_mb > config.PERFORMANCE_CONFIG['max_file_size_mb']:
            logger.warning(
                f"File {source_file} is {file_size_mb:.2f}MB, "
                f"exceeds max size {config.PERFORMANCE_CONFIG['max_file_size_mb']}MB. Skipping."
            )
            return {'nodes': [], 'edges': [], 'error': 'file_too_large'}
        
        try:
            # 构建命令
            cmd = [
                self.tsg_binary,
                source_file,
                '--rules', rules_file,
            ]
            
            # 如果指定了语言，添加语言参数
            if language:
                cmd.extend(['--language', language])
            
            logger.debug(f"Running TSG command: {' '.join(cmd)}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=config.TSG_TIMEOUT
            )
            
            if result.returncode != 0:
                logger.error(f"TSG failed for {source_file}: {result.stderr}")
                return {
                    'nodes': [],
                    'edges': [],
                    'error': result.stderr,
                    'source_file': source_file
                }
            
            # 解析输出
            if output_format == 'json':
                try:
                    graph_data = json.loads(result.stdout)
                    return graph_data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse TSG JSON output: {str(e)}")
                    return {
                        'nodes': [],
                        'edges': [],
                        'error': f'json_parse_error: {str(e)}'
                    }
            else:
                return {'output': result.stdout}
        
        except subprocess.TimeoutExpired:
            logger.error(f"TSG timeout for {source_file}")
            return {
                'nodes': [],
                'edges': [],
                'error': 'timeout'
            }
        except Exception as e:
            logger.error(f"Error extracting graph from {source_file}: {str(e)}")
            return {
                'nodes': [],
                'edges': [],
                'error': str(e)
            }
    
    def extract_from_string(
        self,
        source_code: str,
        rules_file: str,
        language: str,
        file_extension: str = None
    ) -> Dict[str, Any]:
        """
        从字符串源代码提取图数据
        
        Args:
            source_code: 源代码字符串
            rules_file: TSG 规则文件路径
            language: 语言名称
            file_extension: 文件扩展名（用于临时文件）
        
        Returns:
            提取的图数据
        """
        # 创建临时文件
        if not file_extension:
            lang_config = config.SUPPORTED_LANGUAGES.get(language, {})
            file_extension = lang_config.get('extensions', ['.txt'])[0]
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=file_extension,
            delete=False
        ) as temp_file:
            temp_file.write(source_code)
            temp_path = temp_file.name
        
        try:
            result = self.extract_graph(temp_path, rules_file, language)
            return result
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def validate_rules(self, rules_file: str) -> bool:
        """
        验证 TSG 规则文件语法
        
        Args:
            rules_file: TSG 规则文件路径
        
        Returns:
            是否有效
        """
        if not os.path.exists(rules_file):
            logger.error(f"Rules file not found: {rules_file}")
            return False
        
        # 创建一个简单的测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.test', delete=False) as f:
            f.write("# test\n")
            test_file = f.name
        
        try:
            result = subprocess.run(
                [self.tsg_binary, test_file, '--rules', rules_file, '--check'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Rules file {rules_file} is valid")
                return True
            else:
                logger.error(f"Rules file {rules_file} validation failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error validating rules file: {str(e)}")
            return False
        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)
    
    def batch_extract(
        self,
        source_files: List[str],
        rules_file: str,
        language: str = None,
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """
        批量提取多个文件的图数据
        
        Args:
            source_files: 源文件列表
            rules_file: TSG 规则文件
            language: 语言名称
            parallel: 是否并行处理
        
        Returns:
            图数据列表
        """
        results = []
        
        if parallel and len(source_files) > 1:
            # 并行处理
            from concurrent.futures import ThreadPoolExecutor, as_completed
            from tqdm import tqdm
            
            max_workers = config.PERFORMANCE_CONFIG['parallel_workers']
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(
                        self.extract_graph,
                        source_file,
                        rules_file,
                        language
                    ): source_file
                    for source_file in source_files
                }
                
                with tqdm(total=len(source_files), desc="Extracting graphs") as pbar:
                    for future in as_completed(futures):
                        source_file = futures[future]
                        try:
                            result = future.result()
                            result['source_file'] = source_file
                            results.append(result)
                        except Exception as e:
                            logger.error(f"Error processing {source_file}: {str(e)}")
                            results.append({
                                'source_file': source_file,
                                'nodes': [],
                                'edges': [],
                                'error': str(e)
                            })
                        finally:
                            pbar.update(1)
        else:
            # 串行处理
            from tqdm import tqdm
            
            for source_file in tqdm(source_files, desc="Extracting graphs"):
                try:
                    result = self.extract_graph(source_file, rules_file, language)
                    result['source_file'] = source_file
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error processing {source_file}: {str(e)}")
                    results.append({
                        'source_file': source_file,
                        'nodes': [],
                        'edges': [],
                        'error': str(e)
                    })
        
        return results
    
    def get_tsg_info(self) -> Dict[str, str]:
        """
        获取 tree-sitter-graph 信息
        
        Returns:
            版本和信息
        """
        try:
            result = subprocess.run(
                [self.tsg_binary, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {
                'binary': self.tsg_binary,
                'version': result.stdout.strip() if result.returncode == 0 else 'unknown',
                'available': result.returncode == 0
            }
        except Exception as e:
            return {
                'binary': self.tsg_binary,
                'version': 'unknown',
                'available': False,
                'error': str(e)
            }


# 工具函数

def check_tsg_installation() -> bool:
    """检查 TSG 是否已安装"""
    try:
        engine = TSGEngine()
        return True
    except RuntimeError:
        return False


def install_instructions() -> str:
    """返回安装说明"""
    return """
tree-sitter-graph is not installed. Please install it with:

1. Install Rust (if not already installed):
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

2. Install tree-sitter-graph:
   cargo install --features cli tree-sitter-graph

3. Verify installation:
   tree-sitter-graph --version

For more information, visit:
https://github.com/tree-sitter/tree-sitter-graph
"""

