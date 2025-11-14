"""
示例 Python 代码文件
用于测试调用图提取功能
"""

def helper_function(data):
    """辅助函数"""
    return data.strip().lower()


def validate_input(text):
    """验证输入"""
    if not text:
        raise ValueError("输入不能为空")
    return helper_function(text)


def process_data(raw_data):
    """处理数据"""
    # 调用验证函数
    validated = validate_input(raw_data)
    
    # 调用转换函数
    transformed = transform_data(validated)
    
    # 保存结果
    save_result(transformed)
    
    return transformed


def transform_data(data):
    """转换数据"""
    # 进行一些转换
    result = data.upper()
    
    # 调用格式化函数
    formatted = format_output(result)
    
    return formatted


def format_output(data):
    """格式化输出"""
    return f"[PROCESSED] {data}"


def save_result(data):
    """保存结果"""
    print(f"保存数据: {data}")
    log_operation("save", data)


def log_operation(operation, data):
    """记录操作"""
    print(f"操作日志: {operation} - {data[:20]}...")


class DataProcessor:
    """数据处理器类"""
    
    def __init__(self, config):
        self.config = config
    
    def run(self, input_data):
        """运行处理流程"""
        # 调用全局函数
        result = process_data(input_data)
        
        # 调用实例方法
        self.finalize(result)
        
        return result
    
    def finalize(self, data):
        """完成处理"""
        print(f"处理完成: {data}")
        self.cleanup()
    
    def cleanup(self):
        """清理资源"""
        print("清理完成")


def batch_process(items):
    """批量处理"""
    processor = DataProcessor({"mode": "batch"})
    results = []
    
    for item in items:
        # 调用处理器
        result = processor.run(item)
        results.append(result)
    
    return results


def main():
    """主函数"""
    # 单个数据处理
    single_result = process_data("  Test Data  ")
    print(f"单个结果: {single_result}")
    
    # 批量处理
    batch_data = ["item1", "item2", "item3"]
    batch_results = batch_process(batch_data)
    print(f"批量结果: {batch_results}")


if __name__ == "__main__":
    main()


