"""
示例Python项目 - 工具函数
"""


def helper_function():
    """辅助函数"""
    return "helper"


def calculate_sum(numbers):
    """计算总和"""
    return sum(numbers)


def calculate_average(numbers):
    """计算平均值"""
    total = calculate_sum(numbers)
    return total / len(numbers) if numbers else 0


class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        self.data = []
    
    def add_data(self, item):
        """添加数据"""
        self.data.append(item)
    
    def process(self):
        """处理数据"""
        avg = calculate_average(self.data)
        return avg

