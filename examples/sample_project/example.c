/*
 * 示例C项目
 */
#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

int calculate(int x, int y) {
    int sum = add(x, y);
    int product = multiply(x, y);
    return sum + product;
}

int main() {
    int result = calculate(5, 10);
    printf("Result: %d\n", result);
    return 0;
}

