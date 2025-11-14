// TypeScript 示例代码 - 展示函数调用关系

/**
 * 用户接口
 */
interface IUser {
    name: string;
    age: number;
    email: string;
}

/**
 * 验证结果接口
 */
interface ValidationResult {
    valid: boolean;
    errors: string[];
}

/**
 * 用户类
 */
class User implements IUser {
    constructor(
        public name: string,
        public age: number,
        public email: string
    ) {}

    /**
     * 验证用户信息
     */
    validate(): ValidationResult {
        const errors: string[] = [];

        if (!this.validateName()) {
            errors.push('Invalid name');
        }
        if (!this.validateAge()) {
            errors.push('Invalid age');
        }
        if (!this.validateEmail()) {
            errors.push('Invalid email');
        }

        return {
            valid: errors.length === 0,
            errors
        };
    }

    private validateName(): boolean {
        return this.name !== null && this.name.trim().length > 0;
    }

    private validateAge(): boolean {
        return this.age >= 18 && this.age <= 150;
    }

    private validateEmail(): boolean {
        return this.email !== null && this.email.includes('@');
    }

    /**
     * 获取用户摘要
     */
    getSummary(): string {
        return this.formatUserInfo();
    }

    private formatUserInfo(): string {
        return `${this.name} (${this.age} years old) - ${this.email}`;
    }

    /**
     * 检查是否为成人
     */
    isAdult(): boolean {
        return this.age >= 18;
    }

    /**
     * 转换为 JSON
     */
    toJSON(): IUser {
        return {
            name: this.name,
            age: this.age,
            email: this.email
        };
    }
}

/**
 * 用户管理器类
 */
class UserManager {
    private users: Map<string, User>;

    constructor() {
        this.users = new Map();
    }

    /**
     * 添加用户
     */
    addUser(user: User): boolean {
        const validation = user.validate();
        
        if (!validation.valid) {
            console.error('Invalid user:', validation.errors);
            return false;
        }

        if (this.users.has(user.email)) {
            console.error('User already exists');
            return false;
        }

        this.users.set(user.email, user);
        return true;
    }

    /**
     * 获取用户
     */
    getUser(email: string): User | undefined {
        return this.users.get(email);
    }

    /**
     * 获取所有成人用户
     */
    getAdultUsers(): User[] {
        return Array.from(this.users.values())
            .filter(user => user.isAdult());
    }

    /**
     * 统计用户数量
     */
    countUsers(): number {
        return this.users.size;
    }

    /**
     * 打印所有用户
     */
    printAllUsers(): void {
        this.users.forEach(user => {
            console.log(user.getSummary());
        });
    }

    /**
     * 删除用户
     */
    removeUser(email: string): boolean {
        return this.users.delete(email);
    }

    /**
     * 清空所有用户
     */
    clear(): void {
        this.users.clear();
    }

    /**
     * 导出为 JSON
     */
    exportToJSON(): IUser[] {
        return Array.from(this.users.values()).map(user => user.toJSON());
    }
}

/**
 * 用户数据处理工具
 */
class UserDataProcessor {
    /**
     * 解析用户数据
     */
    static parseUserData(data: string): User | null {
        try {
            const parts = data.split(',');

            if (parts.length !== 3) {
                throw new Error('Invalid data format');
            }

            const name = parts[0].trim();
            const age = parseInt(parts[1].trim(), 10);
            const email = parts[2].trim();

            if (isNaN(age)) {
                throw new Error('Invalid age');
            }

            return new User(name, age, email);
        } catch (error) {
            console.error('Parse error:', error);
            return null;
        }
    }

    /**
     * 批量处理用户数据
     */
    static batchProcessUsers(dataList: string[]): User[] {
        const users: User[] = [];

        for (const data of dataList) {
            const user = this.parseUserData(data);
            if (user && user.validate().valid) {
                users.push(user);
            }
        }

        return users;
    }

    /**
     * 计算平均年龄
     */
    static calculateAverageAge(users: User[]): number {
        if (users.length === 0) {
            return 0;
        }

        const total = users.reduce((sum, user) => sum + user.age, 0);
        return total / users.length;
    }

    /**
     * 过滤年龄范围
     */
    static filterByAgeRange(users: User[], minAge: number, maxAge: number): User[] {
        return users.filter(user => 
            user.age >= minAge && user.age <= maxAge
        );
    }

    /**
     * 按年龄排序
     */
    static sortByAge(users: User[], ascending: boolean = true): User[] {
        return [...users].sort((a, b) => 
            ascending ? a.age - b.age : b.age - a.age
        );
    }

    /**
     * 分组统计
     */
    static groupByAgeRange(users: User[]): Map<string, User[]> {
        const groups = new Map<string, User[]>();
        
        for (const user of users) {
            const range = this.getAgeRange(user.age);
            if (!groups.has(range)) {
                groups.set(range, []);
            }
            groups.get(range)!.push(user);
        }
        
        return groups;
    }

    private static getAgeRange(age: number): string {
        if (age < 20) return '18-19';
        if (age < 30) return '20-29';
        if (age < 40) return '30-39';
        if (age < 50) return '40-49';
        return '50+';
    }
}

/**
 * 主函数
 */
function mainTypeScript(): void {
    console.log('=== TypeScript User Management System ===');

    // 创建用户管理器
    const manager = new UserManager();

    // 添加用户
    const user1 = new User('Alice', 25, 'alice@example.com');
    const user2 = new User('Bob', 30, 'bob@example.com');
    const user3 = new User('Charlie', 17, 'charlie@example.com');

    manager.addUser(user1);
    manager.addUser(user2);
    manager.addUser(user3);

    // 打印所有用户
    console.log('\nAll users:');
    manager.printAllUsers();

    // 获取成人用户
    const adults = manager.getAdultUsers();
    console.log(`\nAdult users: ${adults.length}`);

    // 计算平均年龄
    const avgAge = UserDataProcessor.calculateAverageAge(adults);
    console.log(`Average age of adults: ${avgAge.toFixed(1)}`);

    // 批量处理
    const data = [
        'David,28,david@example.com',
        'Eve,35,eve@example.com',
        'Frank,22,frank@example.com'
    ];

    const newUsers = UserDataProcessor.batchProcessUsers(data);
    console.log(`\nBatch processing results: ${newUsers.length} processed`);

    // 添加新用户到管理器
    newUsers.forEach(user => manager.addUser(user));

    console.log(`Total users: ${manager.countUsers()}`);

    // 年龄范围过滤
    const youngAdults = UserDataProcessor.filterByAgeRange(
        manager.getAdultUsers(),
        20,
        30
    );
    console.log(`Young adults (20-30): ${youngAdults.length}`);

    // 排序
    const sortedUsers = UserDataProcessor.sortByAge(manager.getAdultUsers());
    console.log('\nUsers sorted by age:');
    sortedUsers.forEach(user => console.log(`  ${user.getSummary()}`));

    // 分组统计
    const groups = UserDataProcessor.groupByAgeRange(manager.getAdultUsers());
    console.log('\nAge groups:');
    groups.forEach((users, range) => {
        console.log(`  ${range}: ${users.length} users`);
    });

    // 导出 JSON
    const jsonData = manager.exportToJSON();
    console.log(`\nExported ${jsonData.length} users to JSON`);
}

// 如果作为主模块运行
if (require.main === module) {
    mainTypeScript();
}

// 导出类和函数
export { User, UserManager, UserDataProcessor, mainTypeScript };

