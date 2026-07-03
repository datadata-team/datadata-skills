# 查询指南

通过 `execute-adhoc` 执行只读查询时，必须遵循以下 SQL 编写约定。

## 查询引擎

- 默认 `duckdb`；仅当针对 ClickHouse 数据源时切换为 `clickhouse`
- `duckdb` 查询使用 DuckDB SQL；`clickhouse` 查询使用 ClickHouse SQL
- ClickHouse 数据源不支持跨数据源关联

## 数据源绑定

- 在 `execute-adhoc` 请求体中通过 `datasources` 数组绑定：`[{"datasourceId": "ID", "attachAlias": "ALIAS"}]`，可绑定多个
- SQL 中通过别名而非 datasource ID 引用表
- `dataspace` 类型数据源以只读方式挂载为普通 DuckDB 数据库，同样通过别名引用（惯例上用 datasource 的 `name` 作为别名）

## 表命名

在 SQL 中引用表的方式取决于数据源的**类型**。在编写 SQL 前，务必通过 `get-datasource-info` 检查数据源类型，以使用正确的命名模式。

### Dataspace 数据源（类型 `dataspace`）

Datadata 管理的基于 DuckDB 文件的 data-spaces（旧类型名 `ducklake` 已废弃）。在 `execute-adhoc` 中作为普通 DuckDB 数据库以 `READ_ONLY` 方式挂载。catalog 段是挂载别名（`attachAlias`），schema 固定为 DuckDB 的 `main`：

```txt
"{attachAlias}".main."{tableName}"
```

别名由 `datasources` 绑定里指定，惯例上复用 datasource 的 `name`（通过 `GET /datasources/{id}/info` 获取），此时即 `"{datasourceName}".main."{tableName}"`。

> **写入/表管理**（建表、插入、删表）不走 `execute-adhoc`，而是走 `POST /dataspaces/{datasourceId}/execute`，详见 [data-spaces.md](./data-spaces.md)。

### 数据库数据源（MySQL、PostgreSQL、DuckDB、SQLite、ClickHouse 等）

别名变成数据库名。表存放在该数据库中的 schema：

```txt
attachAlias.schemaName.tableName
```

### 文件数据源（CSV、JSON、Parquet 等）

每个附加文件在 DuckDB 内置 `memory` 数据库的 `main` schema 中变成一个表。别名是表名：

```txt
memory.main.attachAlias
```

### 简化名称（仅文件数据源）

文件数据源挂载后表名即为别名，可使用简化名：

- `memory.main.sales` → 仅 `sales`（当所有数据源中没有其他同名表时）
- 用 `*` 从简化名引用所有列：`SELECT * FROM sales`

> 数据库数据源（MySQL、PostgreSQL 等）不支持简化名称，必须使用全限定名 `attachAlias.schemaName.tableName`。

## 标识符引用

始终引用可能与 SQL 关键字冲突的标识符（表名、列名、别名）。标准 SQL 标识符使用双引号，MySQL 兼容语法使用反引号。不确定时，引用所有标识符 — 这是无害的，防止列名恰好为保留字时的微妙崩溃（如 `"from"`、`"order"`、`"group"`、`"select"`、`"user"`、`"status"`、`"key"`）。

```sql
-- 好：引用的标识符
SELECT "id", "name", "status" FROM "sales" WHERE "order" = 'abc'

-- 不好：未引用的 "status" 和 "order" 可能与保留字冲突
SELECT id, name, status FROM sales WHERE order = 'abc'
```

## 安全性

- `execute-adhoc` 是**只读的**。不要用它执行 INSERT、UPDATE、DELETE、DROP、ALTER 或任何修改数据的 SQL
- 写入 dataspace 走 `POST /dataspaces/{datasourceId}/execute`（DDL/DML 均可），详见 [data-spaces.md](./data-spaces.md)
- 未明确要求时不要运行破坏性 SQL
- 不要默默改写业务逻辑 SQL

## 结果处理

`execute-adhoc` 执行后通过 `GET /executions/{id}/result` 获取结果：

- 不要将完整的大数据集发送到 model context — 保存到文件，本地搜索，总结摘要
- 报告文件路径、格式和 execution ID 以便重用
