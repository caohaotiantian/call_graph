/**
 * C 语言示例代码
 * 用于测试函数调用图提取
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// 全局变量
int global_counter = 0;

// 函数声明
int calculate_sum(int a, int b);
void process_data(const char* data);
char* transform_string(const char* input);

// 结构体定义
struct DataProcessor {
    char* buffer;
    int size;
    int (*callback)(void*);
};

// 枚举定义
enum Status {
    STATUS_OK,
    STATUS_ERROR,
    STATUS_PENDING
};

// 辅助函数
int validate_input(int value) {
    if (value < 0) {
        return 0;
    }
    return 1;
}

// 计算和
int calculate_sum(int a, int b) {
    int result = a + b;
    
    // 调用验证函数
    if (validate_input(result)) {
        global_counter++;
        return result;
    }
    
    return -1;
}

// 字符串转换
char* transform_string(const char* input) {
    if (input == NULL) {
        return NULL;
    }
    
    size_t len = strlen(input);
    char* output = (char*)malloc(len + 1);
    
    if (output == NULL) {
        return NULL;
    }
    
    // 复制字符串
    strcpy(output, input);
    
    return output;
}

// 数据处理
void process_data(const char* data) {
    printf("Processing: %s\n", data);
    
    // 转换数据
    char* transformed = transform_string(data);
    
    if (transformed != NULL) {
        printf("Transformed: %s\n", transformed);
        free(transformed);
    }
}

// 回调函数示例
int callback_handler(void* context) {
    printf("Callback executed\n");
    return 0;
}

// 使用结构体和函数指针
void use_data_processor(struct DataProcessor* processor) {
    if (processor == NULL) {
        return;
    }
    
    // 调用回调
    if (processor->callback != NULL) {
        processor->callback(NULL);
    }
    
    // 处理缓冲区
    if (processor->buffer != NULL) {
        process_data(processor->buffer);
    }
}

// 递归函数示例
int fibonacci(int n) {
    if (n <= 1) {
        return n;
    }
    
    // 递归调用
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// 主函数
int main(int argc, char* argv[]) {
    printf("C Code Analysis Example\n");
    
    // 调用计算函数
    int sum = calculate_sum(10, 20);
    printf("Sum: %d\n", sum);
    
    // 调用数据处理
    process_data("Hello, World!");
    
    // 创建处理器
    struct DataProcessor processor;
    processor.buffer = "Test Data";
    processor.size = 9;
    processor.callback = callback_handler;
    
    // 使用处理器
    use_data_processor(&processor);
    
    // 计算斐波那契数
    int fib = fibonacci(10);
    printf("Fibonacci(10): %d\n", fib);
    
    printf("Global counter: %d\n", global_counter);
    
    return 0;
}

