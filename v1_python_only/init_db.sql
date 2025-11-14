-- 符号表：存储从代码中提取的所有符号信息
CREATE TABLE IF NOT EXISTS symbols(
    id TEXT PRIMARY KEY,
    file TEXT,
    name TEXT,
    kind TEXT,
    start_line INTEGER,
    end_line INTEGER,
    start_byte INTEGER,
    end_byte INTEGER,
    container TEXT,
    signature TEXT,
    language TEXT,
    extras_json TEXT,
    code_excerpt TEXT,
    is_exported INTEGER
);

-- 函数调用关系表：存储函数之间的调用关系
CREATE TABLE IF NOT EXISTS function_calls(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_id TEXT NOT NULL,
    caller_name TEXT NOT NULL,
    caller_file TEXT NOT NULL,
    callee_name TEXT NOT NULL,
    callee_id TEXT,
    callee_file TEXT,
    call_line INTEGER,
    call_column INTEGER,
    call_type TEXT,
    is_resolved INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(caller_id) REFERENCES symbols(id),
    FOREIGN KEY(callee_id) REFERENCES symbols(id)
);

-- 调用链表：存储完整的调用链路径
CREATE TABLE IF NOT EXISTS call_chains(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_path TEXT NOT NULL,
    chain_depth INTEGER NOT NULL,
    start_function_id TEXT NOT NULL,
    end_function_id TEXT NOT NULL,
    intermediate_calls TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(start_function_id) REFERENCES symbols(id),
    FOREIGN KEY(end_function_id) REFERENCES symbols(id)
);

-- 索引优化查询性能
CREATE INDEX IF NOT EXISTS idx_function_calls_caller ON function_calls(caller_id);
CREATE INDEX IF NOT EXISTS idx_function_calls_callee ON function_calls(callee_id);
CREATE INDEX IF NOT EXISTS idx_function_calls_caller_name ON function_calls(caller_name);
CREATE INDEX IF NOT EXISTS idx_function_calls_callee_name ON function_calls(callee_name);
CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
CREATE INDEX IF NOT EXISTS idx_symbols_file ON symbols(file);
CREATE INDEX IF NOT EXISTS idx_symbols_kind ON symbols(kind);
CREATE INDEX IF NOT EXISTS idx_call_chains_start ON call_chains(start_function_id);
CREATE INDEX IF NOT EXISTS idx_call_chains_end ON call_chains(end_function_id);