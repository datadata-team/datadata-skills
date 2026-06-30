---
name: datadata-manual
description: |
  本技能包含对 Datadata 平台的详细操作手册，在使用 Datadata 平台相关功能时，**必须先加载本技能**。
  Datadata 平台功能包括:
  1. 数据源管理 - 搜索、查询、元数据增强
  2. 执行 Query 查询 - 对数据源执行 DQL、DQL 查询，并获取结果
  3. Data Spaces 数据空间管理 - 建表、写入数据、删除表
---

## 功能概览

本 skill 通过 **Datadata MCP Server** 直接调用平台能力，在使用之前，请先确认已经连接 Datadata MCP Server。

> **生成独立 Python 脚本（爬虫/ETL/批处理）请使用 `datadata-rest-api` skill。**
> MCP 专为聊天交互设计，不适用于生成独立运行的脚本文件。

### 覆盖能力

- **搜索数据源** — 支持用户名/关键词搜索公开和私有数据源
- **元数据查询** — 检查数据源信息、列出表、描述列结构
- **元数据增强** — 设置表注释和列注释，提升数据可理解性
- **Data Spaces 建表** — 创建表结构，支持 INTEGER、VARCHAR、DOUBLE 等类型
- **Data Spaces 写入** — 批量插入数据行
- **Data Spaces 删除** — 删除表
- **Schema 扫描** — 触发异步扫描，刷新数据源表元数据
- **执行 SQL 查询** — 通过 `execute-adhoc` 执行 SELECT 查询，返回执行 ID 和结果下载链接
- **DQL 脚本执行** — 支持 DQL（Starlark）脚本类型

## 使用场景

| 场景                   | 示例                                                          |
| ---------------------- | ------------------------------------------------------------- |
| 查询 Datadata 中的数据 | "帮我查一下销售数据"、"统计上个月的用户增长"                  |
| 搜索数据源             | "搜索名叫 customers 的数据源"、"看看我有哪些数据源"           |
| 探索数据源结构         | "看看这个 datasource 有哪些表"、"描述一下 customers 表的字段" |
| 设置表和列的注释       | "给 users 表加个注释"、"把 email 列的注释设为'用户邮箱'"      |
| 跨数据源关联分析       | "把 MySQL 的订单表和 CSV 的用户信息 join 一下"                |
| Data Spaces 数据写入   | "把爬虫结果存到 data space 里"、"批量插入这些数据"            |
| 获取查询结果           | "下载上次查询的结果"                                          |
| 定时任务               | "每天早上 8 点帮我查一下销售数据"                             |

## MCP 工具速查

以下工具由 Datadata MCP Server（`https://www.datadata.com/api/mcp/v1`）提供，Agent 直接调用即可：

| 工具                        | 用途                         | 关键参数                                                                                                           |
| --------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `search-datasource`         | 搜索数据源                   | `search` — 用户名或关键词                                                                                          |
| `get-datasource-info`       | 获取数据源元信息             | `datasourceId`                                                                                                     |
| `list-tables`               | 列出表和视图                 | `datasourceId`, `schemaName`（可选）                                                                               |
| `describe-table`            | 获取表列结构（缓存，含注释） | `datasourceId`, `schemaName`, `tableName`                                                                          |
| `describe-data-space-table` | 查看 Data Space 表实时结构   | `datasourceId`, `tableName`                                                                                        |
| `scan-datasource`           | 触发 Schema 扫描             | `datasourceId`                                                                                                     |
| `set-table-comment`         | 设置表/列注释                | `datasourceId`, `schemaName`, `tableName`, `tableComment`（可选）, `columnComments`（可选）                        |
| `create-table`              | 创建 Data Space 表           | `datasourceId`, `tableName`, `columns` — `[{"columnName":"...", "columnType":"..."}]`                              |
| `insert-rows`               | 插入数据行                   | `datasourceId`, `tableName`, `columns`（列名数组）, `rows`（二维数据数组）                                         |
| `drop-table`                | 删除 Data Space 表           | `datasourceId`, `tableName`                                                                                        |
| `execute-adhoc`             | 执行 SQL/DQL 查询            | `name`, `script`, `scriptType`（sql/dql）, `queryEngine`（duckdb/clickhouse）, `datasources`, `parameters`（可选） |

## 概念

- **Datasource** — 查询目标的数据源。不同类型的 datasource（ducklake、MySQL、ClickHouse、CSV 等）有不同的表命名约定。
- **Query**（`execute-adhoc`） — **只读**抽象，包含 SQL/DQL 脚本、datasource 绑定和查询引擎类型。每次调用创建一个 execution 并返回 `executionId`。
- **Execution** — 查询的后台执行实例。执行完成后通过返回的下载链接获取 NDJSON/CSV 结果。

## 工作流

### 基础查询流程

```
搜索数据源 → 用户确认 → 获取元信息 → （可选）列出表/描述列 → 生成查询脚本 → 执行查询 → 下载结果
```

每一步完成后**立即停止**，等待用户明确指令后再进行下一步。详见下方 [规则](#规则) 章节。

### Data Spaces 操作

`create-table` 建表 → `insert-rows` 写入 → `drop-table` 删除，Data Spaces 全流程已 MCP 覆盖。仅限 `ducklake` 类型数据源。详见 [Data Spaces 指南](./references/data-spaces.md)。

### DQL 脚本

如需编写 DQL（Starlark）数据处理脚本，请安装 `datadata-dql` skill。
`execute-adhoc` 的 `scriptType` 设为 `dql` 即可在 MCP 中执行 DQL 脚本，
脚本编写规范和 API 参考以 `datadata-dql` skill 为准。

## 规则

### 🔴 搜索数据源：必须让用户确认，禁止自动选用

`search-datasource` 返回的结果**绝不能**由 Agent 自动选取。选错数据源可能导致查询错误数据等严重后果。

**正确流程：**

1. 调用 `search-datasource` 获取结果
2. 将结果以序号 + 关键信息（`name`、`displayName`、`username`、`visibility`）列表呈现
3. **等待用户明确选择序号**后再使用对应的 `id` 进行后续操作

即使搜索结果只有 1 条，也应让用户确认。

### 🔴 最小操作原则：完成一步即停，禁止猜测意图

Agent 只执行用户**明确要求**的操作，完成当前步骤后**立即停止**。禁止根据上一步结果自动推断下一步。

典型违规：

- 用户："用 customers 数据源" → Agent 确认后又自动 list-tables、describe-table
- 用户："看看有哪些表" → Agent list-tables 后又自动 describe 所有表

### 🔴 execute-adhoc 仅限 SELECT

`execute-adhoc` **只支持 SELECT**，禁止 INSERT/UPDATE/DELETE/DDL。数据写入请使用 Data Spaces 工具（`create-table`、`insert-rows`、`drop-table`）。

### 查询结果处理

`execute-adhoc` 返回执行 ID 和结果下载链接（NDJSON/CSV）。Agent 应自动下载到本地再按需预览，**绝不能将完整数据直接读入上下文**。

**流程：**

1. 调用 `execute-adhoc`，从返回的文本消息中提取下载链接
2. Agent 用 `curl` 将结果下载到 `/tmp/datadata-<executionId>.ndjson`（或 `.csv`）
3. 报告：`outputPath`、行数（`wc -l`）、格式
4. 用 `head`/`tail` 预览前几行，展示数据概览
5. 用户要求时才读取完整内容或做进一步分析
6. 大数据集优先用 `grep`、`awk`、`jq` 等命令行工具本地处理

> **注意**：下载链接从 `execute-adhoc` 返回的文本消息中直接提取，不要自行拼接 URL。

### SQL 编写规范

SQL 编写前必须先通过 `get-datasource-info` 了解数据源类型，不同类型的表命名规则不同。完整的查询引擎、表命名、标识符引用等规范见 [查询指南](./references/query-guide.md)。

### 错误处理

- 任何 **404**：立即停止。检查 datasource ID 或 execution ID 是否正确
- **403** `permission denied`：正常的权限拒绝（如操作他人数据源），向用户说明权限不足
- 查询超时或失败：报告 `executionId`，建议调整查询或稍后重试

## 常见问题

### Q: MCP server 连不上怎么办？

Datadata MCP Server **首选 OAuth 自动授权**（无需手动申请 Key）。
如当前 Agent 不支持 OAuth，可参考 [API Key 申请指南](./references/api-key-setup.md) 通过 Device Flow 自动申请。
如已配置 Key 则检查 MCP server 状态或重启 Agent。

### Q: 查询返回了大量数据怎么办？

不要直接读入上下文。使用返回的下载链接，配合 `curl` + `head`/`tail`/`jq` 等命令行工具在终端中处理。

### Q: 需要写数据（Data Spaces）怎么办？

MCP 已完整支持 Data Spaces：`create-table` 建表 → `insert-rows` 写入 → `drop-table` 删除。

## References

| 文档                                                           | 说明                                           |
| -------------------------------------------------------------- | ---------------------------------------------- |
| [./references/query-guide.md](./references/query-guide.md)     | 查询引擎、表命名、标识符引用、安全性等完整规范 |
| [./references/data-spaces.md](./references/data-spaces.md)     | Data Spaces 表管理完整说明                     |
| [./references/api-key-setup.md](./references/api-key-setup.md) | API Key Device Flow 自动申请指南               |

### 相关 skill（可选安装）

本 skill 可独立使用，以下 skill 提供互补能力：

- **`datadata-rest-api`** — 生成独立 Python 脚本（爬虫/ETL/批处理），含 REST API 参考
- **`datadata-dql`** — DQL（Starlark）脚本编写，含 DataFrame/Series API 参考
