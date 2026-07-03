# Dataspace SQL 执行（数据空间）

Data Spaces 是 Datadata 中 `dataspace` 类型 datasource（旧类型名 `ducklake` 已废弃）独有的能力，通过**一个通用 SQL 执行端点**管理表结构与数据。

## 概述

- **Data space** — 特殊的 `dataspace` 类型数据源，基于 DuckDB 文件存储，支持用户建表、写入数据
- 通过 `POST /api/v1/dataspaces/{datasourceId}/execute` 执行任意 DuckDB SQL 完成建表/写入/改表/删表
- 适合爬虫/ETL 脚本存储结果
- 录入后的数据通过 `execute-adhoc` 查询，命名约定见 [query-guide.md](./query-guide.md#dataspace-数据源类型-dataspace)

## 读 / 写分离（重要）

| 目的 | 走哪条路 | 说明 |
| --- | --- | --- |
| **改表结构 / 写数据** | `POST /dataspaces/{id}/execute` | 单一 dataspace，同步执行，任意 DDL/DML |
| **查询 / 读取数据** | `execute-adhoc` | 查询引擎，把 dataspace 作为只读数据源挂载；异步 → 下载结果 |

`execute-adhoc` 把 dataspace 以 `READ_ONLY` 方式挂载，物理上无法写入——写入只能走 execute 端点。

## 限制

- **仅 `dataspace`** 类型的 datasource 支持此接口
- 执行前先通过 `GET /datasources/{id}/info` 确认 `type` 为 `dataspace`
- **无需特殊权限**：有效 API Key（登录）即可，无需 `data-spaces:write`
- 结果超过 **10000 行会被截断**

## SQL 执行端点

`POST /api/v1/dataspaces/{datasourceId}/execute`

请求体：

| 字段     | 类型            | 必填 | 默认   | 说明                                     |
| -------- | --------------- | ---- | ------ | ---------------------------------------- |
| `query`  | string          | 是   | —      | DuckDB SQL 语句                          |
| `args`   | array (`[]any`) | 否   | —      | 占位符参数（参数化查询）                 |
| `format` | string          | 否   | `json` | `json` \| `ndjson` \| `csv` \| `parquet` |

在 dataspace 内部直接执行，表名用**裸名** `tablename` 或 `main.tablename`。

### Python 示例

```python
DS = "CXNGJifvqE48kdzKVC9o5"  # dataspace 类型 datasource ID
EXEC = f"{BASE_URL}/api/v1/dataspaces/{DS}/execute"

# 建表
_request(EXEC, method="POST",
         payload={"query": "CREATE TABLE products (id INTEGER, name VARCHAR, price DOUBLE)"})

# 参数化插入（推荐，防注入）
_request(EXEC, method="POST",
         payload={"query": "INSERT INTO products VALUES (?, ?, ?)", "args": [1, "Widget", 9.99]})

# 查看结构
_request(EXEC, method="POST", payload={"query": "DESCRIBE products"})

# 删表
_request(EXEC, method="POST", payload={"query": "DROP TABLE IF EXISTS products"})
```

批量写入可循环调用，或使用 DuckDB 原生批量语法（如 `INSERT INTO t SELECT * FROM read_csv('...')`）。

详细端点参数见 [references/api.md](./api.md#dataspace-sql-执行-api)。

## 查询录入的数据

录入 dataspace 的表后，通过 `execute-adhoc` 查询（把 dataspace 挂载为数据源）。表命名约定 `"{attachAlias}".main."{tableName}"` 详见 [query-guide.md](./query-guide.md)。

## 参考

- REST API 详情：[references/api.md](./api.md#dataspace-sql-执行-api)
