# Data Spaces（数据空间）

Data Spaces 是 Datadata 中 `ducklake` 类型 datasource 独有的表管理能力，支持用户创建、写入和删除表。

## 概述

- **Data space** — 特殊的 `ducklake` 类型数据源，支持用户创建表和插入数据
- data-space 名称为 datasource 的 `name`（通过 `GET /datasources/{id}/info` 获取）
- 适合爬虫/ETL 脚本存储结果
- 录入后的数据可通过 `execute-adhoc` 查询，命名约定见 [query-guide.md](./query-guide.md#ducklake-数据源类型-ducklake)

## 限制

- **仅 `ducklake`** 类型的 datasource 支持 data-spaces 操作
- 执行创建表或插入数据前，先通过 `GET /datasources/{id}/info` 确认类型
- `create-table` 和 `insert-rows` 要求 API key 额外拥有 `data-spaces:write` 权限

## 操作

| 操作     | API 端点                                |
| -------- | --------------------------------------- |
| 创建表   | `POST /data-spaces/{id}/create-table`   |
| 描述表   | `POST /data-spaces/{id}/describe-table` |
| 插入数据 | `POST /data-spaces/{id}/insert-rows`    |
| 删除表   | `POST /data-spaces/{id}/drop-table`     |

> 创建表和删除表后会自动触发 schema 扫描，无需手动操作。

### Python 示例

详细的端点参数和 Python 调用示例见 [references/api.md](./api.md#data-spaces-api)。

## 查询录入的数据

录入 data-space 的表后，通过 `execute-adhoc` 查询。表命名约定（`ducklake.{datasourceName}.{tableName}`）详见 [query-guide.md](./query-guide.md)。

## 获取表结构

使用 `POST /data-spaces/{id}/describe-table` 即时获取 data-space 中已创建表的结构。

> `scan-datasource` 是异步 schema 扫描，主要用于非 ducklake 数据源。对于 data-spaces，始终使用 `describe-table`。

## 参考

- REST API 详情：[references/api.md](./api.md#data-spaces-api)
