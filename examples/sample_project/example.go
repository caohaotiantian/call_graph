// 示例Go项目
package main

import (
	"fmt"
)

// User 用户结构体
type User struct {
	Name string
	Age  int
}

// Greet 用户方法
func (u *User) Greet() string {
	return fmt.Sprintf("Hello, %s!", u.Name)
}

// GetAge 获取年龄
func (u User) GetAge() int {
	return u.Age
}

// add 加法函数
func add(a, b int) int {
	return a + b
}

// multiply 乘法函数
func multiply(a, b int) int {
	return a * b
}

// calculate 计算函数
func calculate(x, y int) int {
	sum := add(x, y)
	product := multiply(x, y)
	return sum + product
}

// processUser 处理用户
func processUser(user *User) {
	greeting := user.Greet()
	age := user.GetAge()
	fmt.Printf("%s, Age: %d\n", greeting, age)
}

// main 主函数
func main() {
	result := calculate(5, 10)
	fmt.Printf("Result: %d\n", result)
	
	user := &User{Name: "Alice", Age: 30}
	processUser(user)
}

