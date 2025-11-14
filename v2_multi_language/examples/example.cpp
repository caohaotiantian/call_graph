/**
 * C++ 示例代码
 * 用于测试函数调用图提取
 */

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <functional>

// 命名空间
namespace DataProcessing {

// 基类
class DataProcessor {
protected:
    std::string name;
    int id;

public:
    DataProcessor(const std::string& name, int id) 
        : name(name), id(id) {}
    
    virtual ~DataProcessor() = default;
    
    // 虚函数
    virtual void process() {
        std::cout << "Processing with " << name << std::endl;
    }
    
    // 纯虚函数
    virtual std::string getType() const = 0;
    
    // 普通成员函数
    void setName(const std::string& newName) {
        name = newName;
    }
    
    std::string getName() const {
        return name;
    }
};

// 派生类
class TextProcessor : public DataProcessor {
private:
    std::string text;

public:
    TextProcessor(const std::string& name, int id, const std::string& text)
        : DataProcessor(name, id), text(text) {}
    
    // 重写虚函数
    void process() override {
        std::cout << "Processing text: " << text << std::endl;
        transform();
        validate();
    }
    
    std::string getType() const override {
        return "TextProcessor";
    }
    
    // 成员函数
    void transform() {
        // 转换文本
        for (char& c : text) {
            c = std::toupper(c);
        }
    }
    
    void validate() {
        if (text.empty()) {
            std::cout << "Warning: empty text" << std::endl;
        }
    }
};

// 模板类
template<typename T>
class Container {
private:
    std::vector<T> items;

public:
    void add(const T& item) {
        items.push_back(item);
    }
    
    size_t size() const {
        return items.size();
    }
    
    T get(size_t index) const {
        if (index < items.size()) {
            return items[index];
        }
        throw std::out_of_range("Index out of range");
    }
    
    // 模板成员函数
    template<typename Func>
    void forEach(Func func) {
        for (const auto& item : items) {
            func(item);
        }
    }
};

} // namespace DataProcessing

// 全局函数
void printMessage(const std::string& message) {
    std::cout << "Message: " << message << std::endl;
}

// 函数重载
int calculate(int a, int b) {
    return a + b;
}

double calculate(double a, double b) {
    return a + b;
}

std::string calculate(const std::string& a, const std::string& b) {
    return a + b;
}

// Lambda 表达式示例
void demonstrateLambda() {
    // 简单 lambda
    auto add = [](int a, int b) -> int {
        return a + b;
    };
    
    int result = add(5, 3);
    std::cout << "Lambda result: " << result << std::endl;
    
    // 捕获外部变量的 lambda
    int multiplier = 10;
    auto multiply = [multiplier](int x) {
        return x * multiplier;
    };
    
    std::cout << "Multiply result: " << multiply(5) << std::endl;
}

// 智能指针使用
void useSmartPointers() {
    // unique_ptr
    auto processor1 = std::make_unique<DataProcessing::TextProcessor>(
        "Processor1", 1, "Hello World"
    );
    processor1->process();
    
    // shared_ptr
    auto processor2 = std::make_shared<DataProcessing::TextProcessor>(
        "Processor2", 2, "Shared Processor"
    );
    processor2->process();
}

// 模板函数
template<typename T>
T findMax(T a, T b) {
    return (a > b) ? a : b;
}

// 函数对象
class Comparator {
public:
    bool operator()(int a, int b) const {
        return a < b;
    }
};

// 使用 std::function
void useFunctionObject() {
    std::function<int(int, int)> add = [](int a, int b) {
        return a + b;
    };
    
    int result = add(10, 20);
    std::cout << "Function object result: " << result << std::endl;
}

// 运算符重载示例
class Point {
private:
    int x, y;

public:
    Point(int x = 0, int y = 0) : x(x), y(y) {}
    
    // 运算符重载
    Point operator+(const Point& other) const {
        return Point(x + other.x, y + other.y);
    }
    
    Point operator-(const Point& other) const {
        return Point(x - other.x, y - other.y);
    }
    
    bool operator==(const Point& other) const {
        return x == other.x && y == other.y;
    }
    
    void print() const {
        std::cout << "(" << x << ", " << y << ")" << std::endl;
    }
};

// 主函数
int main() {
    std::cout << "C++ Code Analysis Example" << std::endl;
    
    // 使用派生类
    DataProcessing::TextProcessor textProc("MyProcessor", 1, "test data");
    textProc.process();
    
    // 打印消息
    printMessage("Hello from main");
    
    // 函数重载
    std::cout << "Int calculate: " << calculate(5, 10) << std::endl;
    std::cout << "Double calculate: " << calculate(5.5, 10.5) << std::endl;
    std::cout << "String calculate: " << calculate(std::string("Hello"), std::string(" World")) << std::endl;
    
    // Lambda 表达式
    demonstrateLambda();
    
    // 智能指针
    useSmartPointers();
    
    // 模板函数
    std::cout << "Max int: " << findMax(10, 20) << std::endl;
    std::cout << "Max double: " << findMax(10.5, 20.5) << std::endl;
    
    // 函数对象
    useFunctionObject();
    
    // 运算符重载
    Point p1(10, 20);
    Point p2(5, 15);
    Point p3 = p1 + p2;
    p3.print();
    
    // 模板容器
    DataProcessing::Container<int> intContainer;
    intContainer.add(1);
    intContainer.add(2);
    intContainer.add(3);
    
    intContainer.forEach([](int value) {
        std::cout << "Value: " << value << std::endl;
    });
    
    return 0;
}

