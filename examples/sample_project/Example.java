// Java 示例代码 - 展示函数调用关系
import java.util.*;
import java.util.stream.*;

/**
 * 用户类
 */
class User {
    private String name;
    private int age;
    private String email;
    
    public User(String name, int age, String email) {
        this.name = name;
        this.age = age;
        this.email = email;
    }
    
    public String getName() {
        return name;
    }
    
    public int getAge() {
        return age;
    }
    
    public String getEmail() {
        return email;
    }
    
    /**
     * 验证用户信息
     */
    public boolean validate() {
        if (!validateName()) {
            return false;
        }
        if (!validateAge()) {
            return false;
        }
        if (!validateEmail()) {
            return false;
        }
        return true;
    }
    
    private boolean validateName() {
        return name != null && !name.isEmpty();
    }
    
    private boolean validateAge() {
        return age >= 18 && age <= 150;
    }
    
    private boolean validateEmail() {
        return email != null && email.contains("@");
    }
    
    /**
     * 获取用户摘要
     */
    public String getSummary() {
        return formatUserInfo(name, age, email);
    }
    
    private String formatUserInfo(String name, int age, String email) {
        return String.format("%s (%d years old) - %s", name, age, email);
    }
    
    /**
     * 检查是否为成人
     */
    public boolean isAdult() {
        return age >= 18;
    }
    
    @Override
    public String toString() {
        return getSummary();
    }
}

/**
 * 用户管理器
 */
class UserManager {
    private Map<String, User> users;
    
    public UserManager() {
        this.users = new HashMap<>();
    }
    
    /**
     * 添加用户
     */
    public boolean addUser(User user) {
        if (!user.validate()) {
            System.err.println("Invalid user data");
            return false;
        }
        
        if (users.containsKey(user.getEmail())) {
            System.err.println("User already exists");
            return false;
        }
        
        users.put(user.getEmail(), user);
        return true;
    }
    
    /**
     * 获取用户
     */
    public User getUser(String email) {
        return users.get(email);
    }
    
    /**
     * 获取所有成人用户
     */
    public List<User> getAdultUsers() {
        return users.values().stream()
            .filter(User::isAdult)
            .collect(Collectors.toList());
    }
    
    /**
     * 统计用户数量
     */
    public int countUsers() {
        return users.size();
    }
    
    /**
     * 打印所有用户
     */
    public void printAllUsers() {
        users.values().forEach(user -> {
            System.out.println(user.getSummary());
        });
    }
    
    /**
     * 删除用户
     */
    public boolean removeUser(String email) {
        if (!users.containsKey(email)) {
            return false;
        }
        users.remove(email);
        return true;
    }
    
    /**
     * 清空所有用户
     */
    public void clear() {
        users.clear();
    }
}

/**
 * 用户数据处理工具
 */
class UserDataProcessor {
    /**
     * 解析用户数据
     */
    public static User parseUserData(String data) throws Exception {
        String[] parts = data.split(",");
        
        if (parts.length != 3) {
            throw new Exception("Invalid data format");
        }
        
        String name = parts[0].trim();
        int age = Integer.parseInt(parts[1].trim());
        String email = parts[2].trim();
        
        return new User(name, age, email);
    }
    
    /**
     * 批量处理用户数据
     */
    public static List<User> batchProcessUsers(List<String> dataList) {
        List<User> users = new ArrayList<>();
        
        for (String data : dataList) {
            try {
                User user = parseUserData(data);
                if (user.validate()) {
                    users.add(user);
                }
            } catch (Exception e) {
                System.err.println("Error processing data: " + e.getMessage());
            }
        }
        
        return users;
    }
    
    /**
     * 计算平均年龄
     */
    public static double calculateAverageAge(List<User> users) {
        if (users.isEmpty()) {
            return 0.0;
        }
        
        return users.stream()
            .mapToInt(User::getAge)
            .average()
            .orElse(0.0);
    }
    
    /**
     * 过滤年龄范围
     */
    public static List<User> filterByAgeRange(List<User> users, int minAge, int maxAge) {
        return users.stream()
            .filter(user -> user.getAge() >= minAge && user.getAge() <= maxAge)
            .collect(Collectors.toList());
    }
}

/**
 * 主类
 */
public class Example {
    /**
     * 主函数
     */
    public static void main(String[] args) {
        System.out.println("=== Java User Management System ===");
        
        // 创建用户管理器
        UserManager manager = new UserManager();
        
        // 添加用户
        User user1 = new User("Alice", 25, "alice@example.com");
        User user2 = new User("Bob", 30, "bob@example.com");
        User user3 = new User("Charlie", 17, "charlie@example.com");
        
        manager.addUser(user1);
        manager.addUser(user2);
        manager.addUser(user3);
        
        // 打印所有用户
        System.out.println("\nAll users:");
        manager.printAllUsers();
        
        // 获取成人用户
        List<User> adults = manager.getAdultUsers();
        System.out.println("\nAdult users: " + adults.size());
        
        // 计算平均年龄
        double avgAge = UserDataProcessor.calculateAverageAge(adults);
        System.out.println("Average age of adults: " + avgAge);
        
        // 批量处理
        List<String> data = Arrays.asList(
            "David,28,david@example.com",
            "Eve,35,eve@example.com"
        );
        
        List<User> newUsers = UserDataProcessor.batchProcessUsers(data);
        System.out.println("\nBatch processing results: " + newUsers.size() + " processed");
        
        // 添加新用户到管理器
        for (User user : newUsers) {
            manager.addUser(user);
        }
        
        System.out.println("Total users: " + manager.countUsers());
        
        // 年龄范围过滤
        List<User> youngAdults = UserDataProcessor.filterByAgeRange(
            manager.getAdultUsers(), 20, 30
        );
        System.out.println("Young adults (20-30): " + youngAdults.size());
    }
}

