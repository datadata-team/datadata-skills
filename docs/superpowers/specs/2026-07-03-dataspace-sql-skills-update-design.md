# 设计：更新 datadata-skills 以适配基于 SQL 的 dataspace 模型

- 日期：2026-07-03
- 涉及 skill：`datadata-rest-api`、`datadata-manual`
- 触发原因：后端把 dataspace 的 create-table / describe-table / insert-rows / drop-table 专用接口全部删除，改为一个通用 SQL 执行接口；MCP 做了对应调整。

## 1. 背景与动机

后端重构（commit `67f1069`，用 DuckDB 文件存储替换 DuckLake）带来以下变化：

- 数据源类型 `ducklake` → `dataspace`（旧常量 `DatasourceTypeDucklake = "ducklake"` 标记 Deprecated 但仍存在，新值 `DatasourceTypeDataspace = "dataspace"`）。
- 删除了 4 个 dataspace 专用能力（REST 端点 + MCP 工具）：`create-table`、`insert-rows`、`drop-table`、`describe-data-space-table`（`describe-table`）。
- 新增一个通用 SQL 执行接口，上述所有操作都通过 SQL 完成，灵活性更高。

两个 skill 的文档目前仍完整描述已删除的接口/工具，必须更新。

## 2. 核心观念：读 / 写分离

这是本次更新要贯穿到每个文件的关键心智模型，两条路径**用途完全不同、不可混淆**：

| 场景 | 走哪条路 | 特性 |
| --- | --- | --- |
| **查询 / 读取任何数据**（包括读 dataspace 里的数据） | `execute-adhoc`（查询引擎），把 dataspace 作为 `READ_ONLY` 数据源挂载到查询上 | 异步 → `executionId` → `GET /executions/{id}/result` 下载；支持跨数据源关联、DQL |
| **修改某个 dataspace 内的表结构或数据** | `dataspace-execute-sql`（MCP）/ `POST /dataspaces/{id}/execute`（REST） | 同步，直接在单一 dataspace 的 DuckDB 文件上执行；任意 DDL/DML；结果内联返回 |

代码佐证：`execute-adhoc` 把 dataspace 以 `ATTACH ... (TYPE duckdb, READ_ONLY)` 挂载，物理上无法写入；写入只能走 dataspace 的同步 execute 接口。因此"`execute-adhoc` 只读"这一表述继续成立。

## 3. 需写入文档的权威事实（已从后端代码核实）

### 3.1 REST：dataspace SQL 执行

- 方法 + 路径：`POST /api/v1/dataspaces/{datasourceId}/execute`
  - 注意路径段是 `dataspaces`（一个词），路径参数是 `datasourceId`（类型为 `dataspace` 的数据源 ID）。
- 请求体：

  | 字段 | 位置 | 类型 | 必填 | 默认 | 说明 |
  | --- | --- | --- | --- | --- | --- |
  | `datasourceId` | path | string | 是 | — | 必须是 `dataspace` 类型数据源 |
  | `query` | body | string | 是 | — | DuckDB SQL 语句 |
  | `args` | body | array（`[]any`） | 否 | — | 占位符参数（参数化查询） |
  | `format` | body | string | 否 | `json` | `json` \| `ndjson` \| `csv` \| `parquet` |

- 语义：**同步执行**，直接返回结果 dataset（**没有 `executionId`**）。`json` → JSON；`ndjson`/`csv` → 流式文本；`parquet` → 二进制。
- 结果超过 **10000 行会被截断**。
- 权限：**无需特殊权限**，有效 API Key / 登录即可（后端目前仅 `Authenticated()`，有行注释"暂时不做权限控制"）。

### 3.2 MCP 工具

- `dataspace-execute-sql` — 参数 `{datasourceId, sql, args?}`。**注意参数名是 `sql`**（REST 用的是 `query`）。`DestructiveHint: true`。用途：dataspace 内建表/改表/写数据。schema 变更后建议调 `scan-datasource`。
- `dataspace-create` — 参数 `{name, displayName, description, visibility(public|private), tags?}`。创建 dataspace 数据源本身。

### 3.3 表命名（挂载到 execute-adhoc 时）

- 旧：`ducklake.{datasourceName}.{tableName}`
- 新：`"{attachAlias}".main."{tableName}"`
  - `main` 是 DuckDB 固定 schema；`attachAlias` 由调用方在 `datasources` 绑定里指定，惯例上复用数据源 `name`（复用时即 `"{datasourceName}".main."{tableName}"`）。
- 在 `dataspace-execute-sql` / `POST /dataspaces/{id}/execute` 内部（直接在单一文件上执行）：用裸表名 `tablename` 或 `main.tablename`。

### 3.4 未变化

- `execute-adhoc`（`POST /api/v1/queries/execute-adhoc`）不变，仍是异步查询引擎路径，仍只读。
- `/executions/{id}/result` 结果下载流程不变。
- 数据源级 `describe-table`（`GET /api/v1/datasources/{id}/describe-table`，需 `datasources:read`）仍存在——这是数据源 schema 描述，**不是**被删除的 dataspace describe，勿混淆。

## 4. 已确认的范围决策

1. **结构**：保持现有文件布局，就地重写。**不重命名** `data-spaces.md`（两个 skill 均保留此文件名）。
2. **权限写法**：dataspace execute 端点在文档里写成"无需任何特殊权限"。但 `api-key-setup.md` 默认 device-flow 权限集**保留** `data-spaces:write`（前向兼容，无害）。
3. **创建 dataspace 的范围**：`datadata-manual` 覆盖 `dataspace-create`；`datadata-rest-api` **只**处理 execute-sql 接口，不写 dataspace 创建（REST 无干净端点）。
4. `ducklake` 仅作为遗留别名一句带过，主线用 `dataspace`。

## 5. 逐文件改动清单

### 5.1 `datadata-rest-api`

**SKILL.md**
- 功能概览 / 核心能力：把"Data Spaces — 建表、批量写入、删除表"改为"Dataspace SQL 执行 — 通过 execute 端点运行任意 DuckDB SQL（建表/写入/改表/删表）"。
- 概念：更新 "Data space" 描述（`dataspace` 类型；SQL 执行模型）；保留 "Query（execute-adhoc）只读"。
- API Key 权限清单：去掉把 `data-spaces:write` 说成 dataspace 写入必需的表述（execute 无需权限）。
- 规则"查询只读"：写入去向从 "Data Spaces 的 `insert-rows` 端点" 改为 "`POST /dataspaces/{id}/execute`"。
- References 表：`data-spaces.md` 描述改为"Dataspace SQL 执行"。

**references/api.md**
- 端点总览表：删除 3 行（create-table / describe-table / drop-table）data-spaces 端点；新增 `POST /api/v1/dataspaces/{id}/execute`（权限：无 / 需登录）。
- 把整个 "Data Spaces API" 章节替换为 "Dataspace SQL 执行" 章节：请求体结构、4 种 format、同步返回语义、10000 行截断说明；`urllib` 示例覆盖 CREATE TABLE、用 `args` 的参数化 INSERT、DROP TABLE；并注明*读取* dataspace 数据应走 `execute-adhoc`（把 dataspace 挂载到查询）。

**references/query-guide.md**
- "Ducklake 数据源（类型 `ducklake`）" 段落改写为 "Dataspace 数据源（类型 `dataspace`）"，命名从 `ducklake.{name}.{table}` 改为 `"{attachAlias}".main."{table}"`。
- 数据源绑定的"例外"说明（ducklake 忽略别名）更新为 dataspace 的新挂载行为。
- 安全性："仅 `insert-rows` API 端点可以插入数据"改为"写入 dataspace 走 `POST /dataspaces/{id}/execute`"。

**references/data-spaces.md**
- 整体改写为 dataspace SQL 执行模型：删除 create-table / describe / insert-rows / drop-table 工具表；改为描述 `POST /dataspaces/{id}/execute` 的用法（DDL/DML 示例）。
- 概述里的 `ducklake` → `dataspace`。
- 说明查询录入的数据要通过 `execute-adhoc`。
- 范围：仅 execute-sql，不含 dataspace 创建。

### 5.2 `datadata-manual`

**SKILL.md**
- description（顶部 YAML）："Data Spaces 数据空间管理 - 建表、写入数据、删除表"改为"Data Spaces - 创建数据空间、通过 SQL 管理表结构与数据"。
- 覆盖能力：把 create-table / insert-rows / drop-table 三条替换为 `dataspace-create`（创建数据空间）和 `dataspace-execute-sql`（DDL/DML）。
- MCP 工具速查表：删除 `create-table`、`insert-rows`、`drop-table`、`describe-data-space-table` 四行；新增 `dataspace-create`、`dataspace-execute-sql`（参数用 `sql`）；保留数据源级 `describe-table`；`execute-adhoc` 行保留。
- 概念：保留 Query 只读；补充 dataspace SQL 执行是同步、非 execution 的说明。
- 工作流 "Data Spaces 操作"：改写为 `dataspace-create` → `dataspace-execute-sql`（CREATE TABLE / INSERT）→ `execute-adhoc`（挂载 dataspace 查询）→ `dataspace-execute-sql`（DROP 清理）。
- 规则 "execute-adhoc 仅限 SELECT"：保留只读约束，写入去向改为 `dataspace-execute-sql`。
- FAQ "需要写数据（Data Spaces）怎么办"：改写为 `dataspace-execute-sql`。

**references/data-spaces.md**
- 围绕 `dataspace-create` + `dataspace-execute-sql` 改写；删除旧的四工具表和完整工作流；说明查询要回到 `execute-adhoc`。
- `ducklake` → `dataspace`。

**references/query-guide.md**
- 与 rest-api 相同的命名修正（`dataspace` + `"{alias}".main."{table}"`）。
- 安全性说明里"仅 Data Spaces 的 `insert-rows` MCP 工具可以插入数据"改为 `dataspace-execute-sql`。
- "Data Spaces 表管理已通过 MCP 覆盖，使用 create-table..." 提示改为 `dataspace-execute-sql`。

**references/api-key-setup.md**
- 权限表：`data-spaces:write` 那一行的用途描述从"建表/写入"弱化（execute 端点不再需要它），但该权限**保留**在默认 device-flow 申请集合中。

## 6. 非目标（Out of Scope）

- 不改后端 / MCP 代码。
- 不为 `datadata-rest-api` 增加 dataspace 创建文档。
- 不重命名任何 reference 文件。
- 不改动其它 skill（如 `datadata-dql`、`datadata-memory`）。
- 不移除 `data-spaces:write` 权限常量或默认申请集合中的该项。

## 7. 验收标准

- 两个 skill 中不再出现 `create-table`、`insert-rows`、`drop-table`、`describe-data-space-table` 作为可用接口/工具。
- REST 文档准确给出 `POST /api/v1/dataspaces/{datasourceId}/execute` 及 `{query, args?, format?}` 请求体、4 种 format、同步返回、10000 行截断、无需特殊权限。
- MCP 文档准确给出 `dataspace-execute-sql`（参数 `sql`）与 `dataspace-create`。
- 读/写分离在两个 skill 中清晰表达：查询走 `execute-adhoc`（挂载 dataspace），写入走 dataspace execute。
- 表命名统一更新为 `"{attachAlias}".main."{tableName}"`，`ducklake.{name}.{table}` 仅作遗留说明。
- 文件名保持不变，内部链接不失效。
