# CLI 参考

## 约定

```bash
python3 scripts/datadata_query.py [--base-url URL] [--api-key KEY] <subcommand> [options]
```

全局选项（`--base-url`、`--api-key`）必须在子命令**之前**出现。
推荐使用环境变量 `DATADATA_BASE_URL` 和 `DATADATA_API_KEY` 避免重复输入。

## 常见工作流

### 基础查询流程

```bash
# 1. 设置认证（推荐方式）
export DATADATA_API_KEY="ak_..."
export DATADATA_BASE_URL="https://www.datadata.com/api/v1"  # 生产环境，本地开发改为 http://127.0.0.1:9870/api/v1

# 2. 查询数据源元信息（可选）
python3 scripts/datadata_query.py get-datasource-info --datasource-id "<id>"
python3 scripts/datadata_query.py list-tables --datasource-id "<id>" --schema-name "main"
python3 scripts/datadata_query.py describe-table --datasource-id "<id>" --schema-name "main" --table-name "customers"

# 3. 执行查询
python3 scripts/datadata_query.py execute-adhoc \
  --script-type sql \
  --query-engine duckdb \
  --datasource "<id>:alias" \
  --script "select * from alias limit 20"

# 4. 获取结果
python3 scripts/datadata_query.py get-execution-result \
  --execution-id "<execution-id>" \
  --format ndjson \
  --timeout 30
```

### Data Spaces 工作流（创建和管理表）

```bash
# 1. 创建表
python3 scripts/datadata_query.py create-table \
  --datasource-id "<id>" \
  --table-name "products" \
  --columns '[{"columnName": "id", "columnType": "INTEGER"}, {"columnName": "name", "columnType": "VARCHAR"}]'

# 2. 查看表结构
python3 scripts/datadata_query.py describe-data-space-table \
  --datasource-id "<id>" \
  --table-name "products"

# 3. 插入数据
python3 scripts/datadata_query.py insert-rows \
  --datasource-id "<id>" \
  --table-name "products" \
  --columns '["id", "name"]' \
  --rows '[[1, "Widget"], [2, "Gadget"]]'

# 4. 查询数据（使用 ducklake 限定名）
python3 scripts/datadata_query.py execute-adhoc \
  --script-type sql --query-engine duckdb \
  --datasource "<id>:<datasourceName>" \
  --script "select * from ducklake.<datasourceName>.products limit 10"

# 5. 删除表
python3 scripts/datadata_query.py drop-data-space-table \
  --datasource-id "<id>" \
  --table-name "products"
```

## 子命令

### `get-datasource-info`

| 选项              | 必填 | 描述              |
| ----------------- | ---- | ----------------- |
| `--datasource-id` | 是   | 待查询的数据源 ID |

```bash
python3 scripts/datadata_query.py get-datasource-info --datasource-id "ds_123"
```

### `list-tables`

| 选项              | 必填 | 描述                           |
| ----------------- | ---- | ------------------------------ |
| `--datasource-id` | 是   | 数据源 ID                      |
| `--schema-name`   | 否   | 按 schema 过滤；省略时返回全部 |

```bash
python3 scripts/datadata_query.py list-tables --datasource-id "ds_123" --schema-name "main"
```

### `describe-table`

| 选项              | 必填 | 描述       |
| ----------------- | ---- | ---------- |
| `--datasource-id` | 是   | 数据源 ID  |
| `--schema-name`   | 是   | Schema 名  |
| `--table-name`    | 是   | 表或视图名 |

```bash
python3 scripts/datadata_query.py describe-table --datasource-id "ds_123" --schema-name "main" --table-name "customers"
```

### `create-table`

| 选项              | 必填 | 描述                                                                  |
| ----------------- | ---- | --------------------------------------------------------------------- |
| `--datasource-id` | 是   | 数据空间 ID                                                           |
| `--table-name`    | 是   | 新表名                                                                |
| `--columns`       | 是   | 列定义 JSON 数组：`'[{"columnName": "id", "columnType": "INTEGER"}]'` |

```bash
python3 scripts/datadata_query.py create-table \
  --datasource-id "123" \
  --table-name "products" \
  --columns '[{"columnName": "id", "columnType": "INTEGER"}, {"columnName": "name", "columnType": "VARCHAR"}]'
```

成功时打印 `{"status": "ok", "tableName": "..."}`.

### `describe-data-space-table`

| 选项              | 必填 | 描述        |
| ----------------- | ---- | ----------- |
| `--datasource-id` | 是   | 数据空间 ID |
| `--table-name`    | 是   | 表名        |

```bash
python3 scripts/datadata_query.py describe-data-space-table --datasource-id "123" --table-name "products"
```

打印表结构的 JSON 响应。

### `drop-data-space-table`

| 选项              | 必填 | 描述        |
| ----------------- | ---- | ----------- |
| `--datasource-id` | 是   | 数据空间 ID |
| `--table-name`    | 是   | 表名        |

```bash
python3 scripts/datadata_query.py drop-data-space-table --datasource-id "123" --table-name "products"
```

成功时打印 `{"status": "ok", "tableName": "...", "response": ...}`.

### `insert-rows`

| 选项              | 必填 | 描述                                             |
| ----------------- | ---- | ------------------------------------------------ |
| `--datasource-id` | 是   | 数据空间 ID                                      |
| `--table-name`    | 是   | 目标表名                                         |
| `--columns`       | 是   | 列名 JSON 数组：`'["col1", "col2"]'`             |
| `--rows`          | 是   | 行数据二维 JSON 数组：`'[["v1", 1], ["v2", 2]]'` |

```bash
python3 scripts/datadata_query.py insert-rows \
  --datasource-id "123" \
  --table-name "products" \
  --columns '["id", "name"]' \
  --rows '[[1, "Widget"], [2, "Gadget"]]'
```

成功时打印 `{"status": "ok", "tableName": "...", "inserted": <count>}`.

### `scan-datasource`

| 选项              | 必填 | 描述              |
| ----------------- | ---- | ----------------- |
| `--datasource-id` | 是   | 待扫描的数据源 ID |

```bash
python3 scripts/datadata_query.py scan-datasource --datasource-id "CXNGJifvqE48kdzKVC9o5"
```

打印 `{"taskId": "...", "taskType": "scan", "state": "active"}` 形式的 JSON。扫描为异步执行 — 对于 ducklake 数据源上需要实时表结构查询的场景，使用 `describe-data-space-table`。

### `execute-adhoc`

| 选项             | 必填 | 默认值   | 描述                     |
| ---------------- | ---- | -------- | ------------------------ |
| `--script`       | 是   | —        | SQL 或脚本内容           |
| `--script-type`  | 否   | `sql`    | 脚本类型                 |
| `--query-engine` | 否   | `duckdb` | `duckdb` 或 `clickhouse` |
| `--datasource`   | 否   | —        | 可重复；格式：`ID:ALIAS` |

```bash
python3 scripts/datadata_query.py execute-adhoc \
  --script-type sql \
  --query-engine duckdb \
  --datasource "ds_123:orders" \
  --datasource "ds_users:users" \
  --script "select * from orders join users on orders.user_id = users.id"
```

打印包含 `executionId` 和完整执行响应的 JSON 对象。

### `get-execution-result`

| 选项             | 必填 | 默认值    | 描述                           |
| ---------------- | ---- | --------- | ------------------------------ |
| `--execution-id` | 是   | —         | 来自 `execute-adhoc` 的执行 ID |
| `--format`       | 否   | `ndjson`  | `ndjson` 或 `csv`              |
| `--output-path`  | 否   | 系统 /tmp | 输出文件路径                   |
| `--timeout`      | 否   | —         | 等待执行完成的秒数             |

```bash
python3 scripts/datadata_query.py get-execution-result --execution-id "CaU6DR..." --format ndjson
```

打印包含 `executionId` 和 `result` 元数据（路径、字节数、行数）的 JSON 对象。
