# Data Spaces（数据空间）

Data Spaces 是 Datadata 中 `ducklake` 类型 datasource 独有的表管理能力，支持用户创建、写入和删除表。MCP 已完整覆盖 Data Spaces 全流程。

## 概述

- **Data space** — 特殊的 `ducklake` 类型数据源，支持用户创建表和插入数据
- data-space 名称为 datasource 的 `name`（通过 `get-datasource-info` 获取）
- 适合 AI 生成爬虫/抓取脚本来存储结果
- 录入后的数据可通过 `execute-adhoc` 查询，命名约定见 [query-guide.md](./query-guide.md#ducklake-数据源类型-ducklake)

## 限制

- **仅 `ducklake`** 类型的 datasource 支持 data-spaces 操作
- 执行创建表或插入数据前，先通过 `get-datasource-info` 确认类型

## 操作

| 操作     | MCP 工具                    | 说明                                       |
| -------- | --------------------------- | ------------------------------------------ |
| 创建表   | `create-table`              | 定义列名和类型，建表后自动触发 schema 扫描 |
| 描述表   | `describe-data-space-table` | 实时查询 information_schema，获取即时结构  |
| 插入数据 | `insert-rows`               | 批量插入，事务性：全部成功或全部回滚       |
| 删除表   | `drop-table`                | 删除后自动触发 schema 扫描                 |

### 创建表

```
create-table(datasourceId, tableName, columns: [{"columnName": "...", "columnType": "..."}])
```

`columnType` 支持 `INTEGER`、`VARCHAR`、`DOUBLE`、`BOOLEAN`、`TIMESTAMP`、`BIGINT`、`FLOAT` 等。

### 插入数据

```
insert-rows(datasourceId, tableName, columns: ["col1", "col2"], rows: [[val1, val2], ...])
```

`columns` 顺序必须与目标表一致，`rows` 为二维数据数组。

### 描述表结构

```
describe-data-space-table(datasourceId, tableName)
```

实时执行 SQL 查询 information_schema，返回即时表结构（含原生注释）。与 `describe-table` 的区别：

| 工具                        | 数据源                  | 注释                                        |
| --------------------------- | ----------------------- | ------------------------------------------- |
| `describe-table`            | 缓存元数据              | 含 `set-table-comment` 设置的 Datadata 注释 |
| `describe-data-space-table` | 实时 information_schema | 仅原生 SQL 注释                             |

### 删除表

```
drop-table(datasourceId, tableName)
```

## 完整工作流

```
create-table → describe-data-space-table（确认结构）→ insert-rows → execute-adhoc（验证数据）→ drop-table（清理）
```

创建表后可立即通过 `describe-data-space-table` 验证，无需等待 schema 扫描。

## 查询录入的数据

录入 data-space 的表后，通过 `execute-adhoc` 查询，使用 `ducklake.{datasourceName}.{tableName}` 命名。详见 [query-guide.md](./query-guide.md)。
