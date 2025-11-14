"""
示例Python项目 - 主程序
"""


def validate_input(data):
    """验证输入数据"""
    if not data:
        raise ValueError("数据不能为空")
    return True


def process_data(data):
    """处理数据"""
    validate_input(data)
    result = transform_data(data)
    return result


def transform_data(data):
    """转换数据"""
    return [x * 2 for x in data]


def save_results(results):
    """保存结果"""
    print(f"保存结果: {results}")


def main():
    """主函数"""
    data = [1, 2, 3, 4, 5]
    results = process_data(data)
    save_results(results)
    print("处理完成")


if __name__ == "__main__":
    main()

