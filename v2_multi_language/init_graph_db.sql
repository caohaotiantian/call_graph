-- 多语言代码分析系统数据库表结构
-- 支持函数调用图和数据流图分析

-- 项目表：支持多项目分析
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    root_path TEXT NOT NULL,
    primary_language TEXT,
    languages TEXT,  -- JSON array of supported languages
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 节点表：存储所有代码元素
CREATE TABLE IF NOT EXISTS nodes (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    language TEXT NOT NULL,
    node_type TEXT NOT NULL,  -- FUNCTION, CLASS, VARIABLE, PARAMETER, MODULE, etc.
    name TEXT NOT NULL,
    qualified_name TEXT,  -- 完全限定名（如 pkg.module.Class.method）
    file_path TEXT NOT NULL,
    start_line INTEGER,
    end_line INTEGER,
    start_column INTEGER,
    end_column INTEGER,
    signature TEXT,
    code_snippet TEXT,
    metadata TEXT,  -- JSON string for additional language-specific data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 边表：存储所有关系
CREATE TABLE IF NOT EXISTS edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
    edge_type TEXT NOT NULL,  -- CALLS, METHOD_CALL, DEFINES, USES, INHERITS, etc.
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    target_name TEXT,  -- 目标名称（用于未解析的外部引用）
    file_path TEXT,
    line INTEGER,
    column INTEGER,
    is_resolved INTEGER DEFAULT 1,  -- 是否成功解析目标节点
    metadata TEXT,  -- JSON string for additional edge data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(source_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY(target_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- 数据流表：存储数据流分析信息
CREATE TABLE IF NOT EXISTS dataflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
    variable_id TEXT NOT NULL,
    variable_name TEXT NOT NULL,
    definition_node_id TEXT,  -- 定义该变量的节点
    use_node_id TEXT,  -- 使用该变量的节点
    flow_type TEXT NOT NULL,  -- DEFINES, USES, ASSIGNS, RETURNS, PARAMETER_PASS, etc.
    file_path TEXT,
    line INTEGER,
    column INTEGER,
    scope_node_id TEXT,  -- 作用域节点（通常是函数或类）
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(variable_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY(definition_node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY(use_node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY(scope_node_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- 调用链表：存储完整的调用链（优化查询性能）
CREATE TABLE IF NOT EXISTS call_chains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
    chain_path TEXT NOT NULL,  -- 调用链路径（可读格式）
    chain_ids TEXT NOT NULL,  -- 调用链节点ID列表（JSON）
    chain_depth INTEGER NOT NULL,
    start_function_id TEXT NOT NULL,
    end_function_id TEXT NOT NULL,
    intermediate_calls TEXT,  -- 中间调用详情（JSON）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY(start_function_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY(end_function_id) REFERENCES nodes(id) ON DELETE CASCADE
);

-- 分析统计表：存储分析统计信息
CREATE TABLE IF NOT EXISTS analysis_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    language TEXT,
    total_files INTEGER DEFAULT 0,
    total_nodes INTEGER DEFAULT 0,
    total_edges INTEGER DEFAULT 0,
    total_functions INTEGER DEFAULT 0,
    total_classes INTEGER DEFAULT 0,
    total_dataflows INTEGER DEFAULT 0,
    analysis_duration_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- ===== 索引优化 =====

-- 项目索引
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);

-- 节点索引
CREATE INDEX IF NOT EXISTS idx_nodes_project ON nodes(project_id);
CREATE INDEX IF NOT EXISTS idx_nodes_language ON nodes(language);
CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_name ON nodes(name);
CREATE INDEX IF NOT EXISTS idx_nodes_qualified_name ON nodes(qualified_name);
CREATE INDEX IF NOT EXISTS idx_nodes_file ON nodes(file_path);
CREATE INDEX IF NOT EXISTS idx_nodes_project_type ON nodes(project_id, node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_project_name ON nodes(project_id, name);

-- 边索引
CREATE INDEX IF NOT EXISTS idx_edges_project ON edges(project_id);
CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
CREATE INDEX IF NOT EXISTS idx_edges_target_name ON edges(target_name);
CREATE INDEX IF NOT EXISTS idx_edges_source_type ON edges(source_id, edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_target_type ON edges(target_id, edge_type);
CREATE INDEX IF NOT EXISTS idx_edges_resolved ON edges(is_resolved);

-- 数据流索引
CREATE INDEX IF NOT EXISTS idx_dataflow_project ON dataflow(project_id);
CREATE INDEX IF NOT EXISTS idx_dataflow_variable ON dataflow(variable_id);
CREATE INDEX IF NOT EXISTS idx_dataflow_variable_name ON dataflow(variable_name);
CREATE INDEX IF NOT EXISTS idx_dataflow_definition ON dataflow(definition_node_id);
CREATE INDEX IF NOT EXISTS idx_dataflow_use ON dataflow(use_node_id);
CREATE INDEX IF NOT EXISTS idx_dataflow_type ON dataflow(flow_type);
CREATE INDEX IF NOT EXISTS idx_dataflow_scope ON dataflow(scope_node_id);

-- 调用链索引
CREATE INDEX IF NOT EXISTS idx_call_chains_project ON call_chains(project_id);
CREATE INDEX IF NOT EXISTS idx_call_chains_start ON call_chains(start_function_id);
CREATE INDEX IF NOT EXISTS idx_call_chains_end ON call_chains(end_function_id);
CREATE INDEX IF NOT EXISTS idx_call_chains_depth ON call_chains(chain_depth);

-- 统计索引
CREATE INDEX IF NOT EXISTS idx_stats_project ON analysis_stats(project_id);
CREATE INDEX IF NOT EXISTS idx_stats_language ON analysis_stats(language);

-- ===== 视图：便捷查询 =====

-- 函数调用关系视图
CREATE VIEW IF NOT EXISTS v_function_calls AS
SELECT 
    e.id,
    e.project_id,
    e.edge_type,
    n1.id as caller_id,
    n1.name as caller_name,
    n1.qualified_name as caller_qualified_name,
    n1.file_path as caller_file,
    n2.id as callee_id,
    n2.name as callee_name,
    n2.qualified_name as callee_qualified_name,
    n2.file_path as callee_file,
    e.line as call_line,
    e.is_resolved
FROM edges e
JOIN nodes n1 ON e.source_id = n1.id
LEFT JOIN nodes n2 ON e.target_id = n2.id
WHERE e.edge_type IN ('CALLS', 'METHOD_CALL', 'CONSTRUCTOR_CALL', 'INDIRECT_CALL');

-- 数据流关系视图
CREATE VIEW IF NOT EXISTS v_dataflow_relations AS
SELECT 
    df.id,
    df.project_id,
    df.variable_name,
    df.flow_type,
    n1.name as scope_function,
    n1.file_path as file_path,
    df.line,
    n2.name as definition_context,
    n3.name as use_context
FROM dataflow df
LEFT JOIN nodes n1 ON df.scope_node_id = n1.id
LEFT JOIN nodes n2 ON df.definition_node_id = n2.id
LEFT JOIN nodes n3 ON df.use_node_id = n3.id;

-- 项目统计视图
CREATE VIEW IF NOT EXISTS v_project_summary AS
SELECT 
    p.id,
    p.name,
    p.root_path,
    p.primary_language,
    COUNT(DISTINCT n.id) as total_nodes,
    COUNT(DISTINCT CASE WHEN n.node_type = 'FUNCTION' THEN n.id END) as total_functions,
    COUNT(DISTINCT CASE WHEN n.node_type = 'CLASS' THEN n.id END) as total_classes,
    COUNT(DISTINCT e.id) as total_edges,
    COUNT(DISTINCT df.id) as total_dataflows
FROM projects p
LEFT JOIN nodes n ON p.id = n.project_id
LEFT JOIN edges e ON p.id = e.project_id
LEFT JOIN dataflow df ON p.id = df.project_id
GROUP BY p.id;

