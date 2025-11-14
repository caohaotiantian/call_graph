/**
 * 示例JavaScript项目
 */

function fetchData() {
    return { name: "John", age: 30 };
}

function processUser(user) {
    return `User: ${user.name}, Age: ${user.age}`;
}

function displayUser(userId) {
    const user = fetchData(userId);
    const message = processUser(user);
    console.log(message);
}

function main() {
    displayUser(123);
}

main();

