# Data Spaces（数据空间）

Data Spaces 是 Datadata 中 `dataspace` 类型 datasource（旧类型名 `ducklake` 已废弃）独有的能力，通过 MCP 工具**创建数据空间**并**用 SQL 管理表结构与数据**。

## 概述

- **Data space** — 特殊的 `dataspace` 类型数据源，基于 DuckDB 文件存储，支持用户建表、写入数据
- 用 `dataspace-create` 创建数据空间，用 `dataspace-execute-sql` 在其中执行任意 DuckDB SQL
- 适合 AI 生成爬虫/抓取脚本来存储结果
- 录入后的数据通过 `execute-adhoc` 查询，命名约定见 [query-guide.md](./query-guide.md#dataspace-数据源类型-dataspace)

## 读 / 写分离（重要）

| 目的 | 用哪个工具 | 说明 |
| --- | --- | --- |
| **改表结构 / 写数据** | `dataspace-execute-sql` | 单一 dataspace，同步执行，任意 DDL/DML |
| **查询 / 读取数据** | `execute-adhoc` | 查询引擎，把 dataspace 作为只读数据源挂载 |

`execute-adhoc` 把 dataspace 以只读方式挂载，物理上无法写入——写入只能走 `dataspace-execute-sql`。

## 限制

- **仅 `dataspace`** 类型的 datasource 支持 `dataspace-execute-sql`
- 执行前先通过 `get-datasource-info` 确认类型
- 结果超过 **10000 行会被截断**

## 工具

### 创建数据空间

```
dataspace-create(name, displayName, description, visibility, tags?)
```

- `name` — 标识符（用于 SQL/挂载引用）
- `displayName`、`description` — 展示信息
- `visibility` — `public` 或 `private`
- `tags` — 可选标签

### 执行 SQL（建表 / 写入 / 改表 / 删表）

```
dataspace-execute-sql(datasourceId, sql, args?)
```

在 dataspace 内部直接执行，表名用**裸名** `tablename` 或 `main.tablename`。

```sql
-- 建表
CREATE TABLE products (id INTEGER, name VARCHAR, price DOUBLE)

-- 插入（可用 args 传占位符参数）
INSERT INTO products VALUES (?, ?, ?)

-- 查看结构
DESCRIBE products

-- 删表
DROP TABLE IF EXISTS products
```

> 改动 schema 后，可调用 `scan-datasource` 刷新数据源元数据。

## 完整工作流

```
dataspace-create（创建数据空间）
  → dataspace-execute-sql（CREATE TABLE 建表）
  → dataspace-execute-sql（INSERT 写入）
  → execute-adhoc（挂载 dataspace 查询验证）
  → dataspace-execute-sql（DROP TABLE 清理）
```

## 查询录入的数据

录入 dataspace 的表后，通过 `execute-adhoc` 查询（把 dataspace 挂载为数据源），使用 `"{attachAlias}".main."{tableName}"` 命名。详见 [query-guide.md](./query-guide.md)。
