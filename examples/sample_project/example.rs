// Rust 示例代码 - 展示函数调用关系
use std::collections::HashMap;

/// 用户结构体
#[derive(Debug)]
pub struct User {
    pub name: String,
    pub age: u32,
    pub email: String,
}

impl User {
    /// 创建新用户
    pub fn new(name: String, age: u32, email: String) -> Self {
        User { name, age, email }
    }

    /// 验证用户信息
    pub fn validate(&self) -> Result<(), String> {
        if self.name.is_empty() {
            return Err("Name cannot be empty".to_string());
        }
        if self.age < 18 {
            return Err("User must be 18 or older".to_string());
        }
        if !self.email.contains('@') {
            return Err("Invalid email format".to_string());
        }
        Ok(())
    }

    /// 获取用户摘要
    pub fn get_summary(&self) -> String {
        format!("{} ({} years old) - {}", self.name, self.age, self.email)
    }

    /// 检查是否为成人
    pub fn is_adult(&self) -> bool {
        self.age >= 18
    }
}

/// 用户管理器
pub struct UserManager {
    users: HashMap<String, User>,
}

impl UserManager {
    /// 创建新的用户管理器
    pub fn new() -> Self {
        UserManager {
            users: HashMap::new(),
        }
    }

    /// 添加用户
    pub fn add_user(&mut self, user: User) -> Result<(), String> {
        // 验证用户
        user.validate()?;
        
        let email = user.email.clone();
        if self.users.contains_key(&email) {
            return Err("User already exists".to_string());
        }
        
        self.users.insert(email, user);
        Ok(())
    }

    /// 获取用户
    pub fn get_user(&self, email: &str) -> Option<&User> {
        self.users.get(email)
    }

    /// 获取所有成人用户
    pub fn get_adult_users(&self) -> Vec<&User> {
        self.users
            .values()
            .filter(|user| user.is_adult())
            .collect()
    }

    /// 统计用户数量
    pub fn count_users(&self) -> usize {
        self.users.len()
    }

    /// 打印所有用户
    pub fn print_all_users(&self) {
        for user in self.users.values() {
            println!("{}", user.get_summary());
        }
    }
}

/// 数据处理函数
pub fn process_user_data(data: &str) -> Result<User, String> {
    let parts: Vec<&str> = data.split(',').collect();
    
    if parts.len() != 3 {
        return Err("Invalid data format".to_string());
    }
    
    let name = parts[0].trim().to_string();
    let age: u32 = parts[1]
        .trim()
        .parse()
        .map_err(|_| "Invalid age")?;
    let email = parts[2].trim().to_string();
    
    let user = User::new(name, age, email);
    user.validate()?;
    
    Ok(user)
}

/// 批量处理用户数据
pub fn batch_process_users(data_list: Vec<&str>) -> Vec<Result<User, String>> {
    data_list
        .iter()
        .map(|data| process_user_data(data))
        .collect()
}

/// 计算平均年龄
pub fn calculate_average_age(users: &[&User]) -> f64 {
    if users.is_empty() {
        return 0.0;
    }
    
    let total: u32 = users.iter().map(|user| user.age).sum();
    total as f64 / users.len() as f64
}

/// 主函数
pub fn main_rust() {
    println!("=== Rust User Management System ===");
    
    // 创建用户管理器
    let mut manager = UserManager::new();
    
    // 添加用户
    let user1 = User::new("Alice".to_string(), 25, "alice@example.com".to_string());
    let user2 = User::new("Bob".to_string(), 30, "bob@example.com".to_string());
    let user3 = User::new("Charlie".to_string(), 17, "charlie@example.com".to_string());
    
    if let Err(e) = manager.add_user(user1) {
        println!("Error adding user: {}", e);
    }
    if let Err(e) = manager.add_user(user2) {
        println!("Error adding user: {}", e);
    }
    if let Err(e) = manager.add_user(user3) {
        println!("Error adding user: {}", e);
    }
    
    // 打印所有用户
    println!("\nAll users:");
    manager.print_all_users();
    
    // 获取成人用户
    let adults = manager.get_adult_users();
    println!("\nAdult users: {}", adults.len());
    
    // 计算平均年龄
    let avg_age = calculate_average_age(&adults);
    println!("Average age of adults: {:.1}", avg_age);
    
    // 批量处理
    let data = vec![
        "David,28,david@example.com",
        "Eve,35,eve@example.com",
    ];
    
    let results = batch_process_users(data);
    println!("\nBatch processing results: {} processed", results.len());
    
    println!("\nTotal users: {}", manager.count_users());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_user_validation() {
        let user = User::new("Test".to_string(), 20, "test@example.com".to_string());
        assert!(user.validate().is_ok());
    }

    #[test]
    fn test_user_is_adult() {
        let adult = User::new("Adult".to_string(), 25, "adult@example.com".to_string());
        let minor = User::new("Minor".to_string(), 15, "minor@example.com".to_string());
        
        assert!(adult.is_adult());
        assert!(!minor.is_adult());
    }
}

