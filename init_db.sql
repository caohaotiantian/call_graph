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

-- 调用关系表：存储函数之间的调用关系
CREATE TABLE IF NOT EXISTS call_relations(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caller_id TEXT NOT NULL,
    callee_id TEXT NOT NULL,
    caller_name TEXT,
    callee_name TEXT,
    caller_file TEXT,
    callee_file TEXT,
    call_site_line INTEGER,
    call_site_column INTEGER,
    language TEXT,
    FOREIGN KEY (caller_id) REFERENCES symbols(id),
    FOREIGN KEY (callee_id) REFERENCES symbols(id)
);

-- 为调用关系创建索引，加速查询
CREATE INDEX IF NOT EXISTS idx_caller ON call_relations(caller_id);
CREATE INDEX IF NOT EXISTS idx_callee ON call_relations(callee_id);
CREATE INDEX IF NOT EXISTS idx_caller_name ON call_relations(caller_name);
CREATE INDEX IF NOT EXISTS idx_callee_name ON call_relations(callee_name);
CREATE INDEX IF NOT EXISTS idx_files ON call_relations(caller_file, callee_file);

-- 符号表索引
CREATE INDEX IF NOT EXISTS idx_symbol_name ON symbols(name);
CREATE INDEX IF NOT EXISTS idx_symbol_file ON symbols(file);
CREATE INDEX IF NOT EXISTS idx_symbol_kind ON symbols(kind);
