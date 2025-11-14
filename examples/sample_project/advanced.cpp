// C++ 示例代码 - 展示更复杂的函数调用关系
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <algorithm>

using namespace std;

// 前向声明
class User;
class UserManager;
class DataProcessor;

/**
 * 用户类
 */
class User {
private:
    string name;
    int age;
    string email;

    bool validateName() const {
        return !name.empty();
    }

    bool validateAge() const {
        return age >= 18 && age <= 150;
    }

    bool validateEmail() const {
        return email.find('@') != string::npos;
    }

    string formatUserInfo() const {
        return name + " (" + to_string(age) + " years old) - " + email;
    }

public:
    User(const string& n, int a, const string& e) 
        : name(n), age(a), email(e) {}

    /**
     * 验证用户信息
     */
    bool validate() const {
        return validateName() && validateAge() && validateEmail();
    }

    /**
     * 获取用户摘要
     */
    string getSummary() const {
        return formatUserInfo();
    }

    /**
     * 检查是否为成人
     */
    bool isAdult() const {
        return age >= 18;
    }

    // Getters
    string getName() const { return name; }
    int getAge() const { return age; }
    string getEmail() const { return email; }

    // Setters
    void setName(const string& n) { name = n; }
    void setAge(int a) { age = a; }
    void setEmail(const string& e) { email = e; }
};

/**
 * 用户管理器类
 */
class UserManager {
private:
    map<string, shared_ptr<User>> users;

    void logError(const string& message) const {
        cerr << "Error: " << message << endl;
    }

    void logInfo(const string& message) const {
        cout << "Info: " << message << endl;
    }

public:
    /**
     * 添加用户
     */
    bool addUser(shared_ptr<User> user) {
        if (!user->validate()) {
            logError("Invalid user data");
            return false;
        }

        if (users.find(user->getEmail()) != users.end()) {
            logError("User already exists");
            return false;
        }

        users[user->getEmail()] = user;
        logInfo("User added successfully");
        return true;
    }

    /**
     * 获取用户
     */
    shared_ptr<User> getUser(const string& email) {
        auto it = users.find(email);
        return (it != users.end()) ? it->second : nullptr;
    }

    /**
     * 获取所有成人用户
     */
    vector<shared_ptr<User>> getAdultUsers() {
        vector<shared_ptr<User>> adults;
        for (const auto& pair : users) {
            if (pair.second->isAdult()) {
                adults.push_back(pair.second);
            }
        }
        return adults;
    }

    /**
     * 统计用户数量
     */
    size_t countUsers() const {
        return users.size();
    }

    /**
     * 打印所有用户
     */
    void printAllUsers() const {
        cout << "\nAll users:" << endl;
        for (const auto& pair : users) {
            cout << "  " << pair.second->getSummary() << endl;
        }
    }

    /**
     * 删除用户
     */
    bool removeUser(const string& email) {
        auto it = users.find(email);
        if (it == users.end()) {
            return false;
        }
        users.erase(it);
        return true;
    }

    /**
     * 清空所有用户
     */
    void clear() {
        users.clear();
    }
};

/**
 * 数据处理器类
 */
class DataProcessor {
public:
    /**
     * 解析用户数据
     */
    static shared_ptr<User> parseUserData(const string& data) {
        // 简单的逗号分隔解析
        size_t pos1 = data.find(',');
        size_t pos2 = data.find(',', pos1 + 1);

        if (pos1 == string::npos || pos2 == string::npos) {
            return nullptr;
        }

        string name = data.substr(0, pos1);
        string ageStr = data.substr(pos1 + 1, pos2 - pos1 - 1);
        string email = data.substr(pos2 + 1);

        // 去除空格
        name = trim(name);
        ageStr = trim(ageStr);
        email = trim(email);

        int age;
        try {
            age = stoi(ageStr);
        } catch (...) {
            return nullptr;
        }

        return make_shared<User>(name, age, email);
    }

    /**
     * 批量处理用户数据
     */
    static vector<shared_ptr<User>> batchProcessUsers(const vector<string>& dataList) {
        vector<shared_ptr<User>> users;

        for (const auto& data : dataList) {
            auto user = parseUserData(data);
            if (user && user->validate()) {
                users.push_back(user);
            }
        }

        return users;
    }

    /**
     * 计算平均年龄
     */
    static double calculateAverageAge(const vector<shared_ptr<User>>& users) {
        if (users.empty()) {
            return 0.0;
        }

        int total = 0;
        for (const auto& user : users) {
            total += user->getAge();
        }

        return static_cast<double>(total) / users.size();
    }

    /**
     * 过滤年龄范围
     */
    static vector<shared_ptr<User>> filterByAgeRange(
        const vector<shared_ptr<User>>& users,
        int minAge,
        int maxAge
    ) {
        vector<shared_ptr<User>> filtered;

        for (const auto& user : users) {
            if (user->getAge() >= minAge && user->getAge() <= maxAge) {
                filtered.push_back(user);
            }
        }

        return filtered;
    }

    /**
     * 按年龄排序
     */
    static void sortByAge(vector<shared_ptr<User>>& users, bool ascending = true) {
        sort(users.begin(), users.end(),
            [ascending](const shared_ptr<User>& a, const shared_ptr<User>& b) {
                return ascending ? a->getAge() < b->getAge() : a->getAge() > b->getAge();
            });
    }

private:
    static string trim(const string& str) {
        size_t first = str.find_first_not_of(' ');
        if (first == string::npos) return "";
        size_t last = str.find_last_not_of(' ');
        return str.substr(first, last - first + 1);
    }
};

/**
 * 主函数
 */
int main() {
    cout << "=== C++ User Management System ===" << endl;

    // 创建用户管理器
    UserManager manager;

    // 添加用户
    auto user1 = make_shared<User>("Alice", 25, "alice@example.com");
    auto user2 = make_shared<User>("Bob", 30, "bob@example.com");
    auto user3 = make_shared<User>("Charlie", 17, "charlie@example.com");

    manager.addUser(user1);
    manager.addUser(user2);
    manager.addUser(user3);

    // 打印所有用户
    manager.printAllUsers();

    // 获取成人用户
    auto adults = manager.getAdultUsers();
    cout << "\nAdult users: " << adults.size() << endl;

    // 计算平均年龄
    double avgAge = DataProcessor::calculateAverageAge(adults);
    cout << "Average age of adults: " << avgAge << endl;

    // 批量处理
    vector<string> data = {
        "David,28,david@example.com",
        "Eve,35,eve@example.com",
        "Frank,22,frank@example.com"
    };

    auto newUsers = DataProcessor::batchProcessUsers(data);
    cout << "\nBatch processing results: " << newUsers.size() << " processed" << endl;

    // 添加新用户到管理器
    for (const auto& user : newUsers) {
        manager.addUser(user);
    }

    cout << "Total users: " << manager.countUsers() << endl;

    // 年龄范围过滤
    auto youngAdults = DataProcessor::filterByAgeRange(
        manager.getAdultUsers(),
        20,
        30
    );
    cout << "Young adults (20-30): " << youngAdults.size() << endl;

    // 排序
    auto sortedUsers = manager.getAdultUsers();
    DataProcessor::sortByAge(sortedUsers);
    cout << "\nUsers sorted by age:" << endl;
    for (const auto& user : sortedUsers) {
        cout << "  " << user->getSummary() << endl;
    }

    return 0;
}

