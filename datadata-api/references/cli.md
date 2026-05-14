# CLI 参考

## 约定

```bash
python3 scripts/datadata_query.py [--base-url URL] [--api-key KEY] <subcommand> [options]
```

全局选项（`--base-url`、`--api-key`）必须在子命令**之前**出现。
推荐使用环境变量 `DATADATA_BASE_URL` 和 `DATADATA_API_KEY` 避免重复输入。

## 认证

### API Key 优先级

CLI 按以下顺序查找 API Key（找到即停止）：

1. `--api-key` CLI 标志（最高优先级）
2. `DATADATA_API_KEY` 环境变量
3. `~/.config/datadata/datadata-api-skills/config.json` 配置文件
4. 设备授权流程（自动签发 + 持久化）

> Windows: `%APPDATA%\datadata\datadata-api-skills\config.json`

### 设备授权（推荐）

如果以上来源均未提供 API Key，CLI 将自动发起**设备授权流程**：

1. CLI 调用 `/api/v1/api-keys/device-flow/code`，获取授权链接
2. 终端打印 `verificationUriComplete` —— Agent 应使用浏览器工具自动打开该链接
3. 用户登录 Datadata 并确认授权
4. CLI 后台轮询 `/api/v1/api-keys/device-flow/token`，获取 API Key 后自动继续执行原命令
5. API Key 自动保存到 `~/.config/datadata/datadata-api-skills/config.json`（Unix 权限 0600），后续直接使用，无需重复授权
6. API Key 默认有效期 **90 天**，过期后自动清除并重新签发
7. 若 API 返回 401/403（Key 被撤销或提前失效），CLI 也会自动清除配置并重新签发

授权请求的默认权限覆盖所有 CLI 子命令所需权限。签发的 API Key 默认有效期 **90 天**，过期后删除 `~/.datadata/api-key` 即可重新触发设备授权。

### 手动设置 API Key（备选）

```bash
export DATADATA_API_KEY="ak_..."
export DATADATA_BASE_URL="https://www.datadata.com/api/v1"  # 生产环境，本地开发改为 http://127.0.0.1:9870/api/v1
```

API Key 可在 Datadata 网页端手动创建：登录 → 头像 → Settings → API Keys → 创建新 Key。

## 常见工作流

### 基础查询流程

```bash
# 方式一：设备授权（推荐，无需手动创建 API Key）
# 直接运行命令，CLI 会自动发起设备授权流程
python3 scripts/datadata_query.py get-datasource-info --datasource-id "<id>"

# 方式二：手动设置 API Key
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

### `device-flow-start`

发起设备授权（非阻塞），输出 JSON 后立即退出。供 Agent 使用。

```bash
python3 scripts/datadata_query.py device-flow-start
```

输出含 `verificationUriComplete`、`deviceCode`、`nextStep` 等字段。自动保存状态到 `device-flow-pending.json`。Agent 应提取 URL 用浏览器打开。

### `device-flow-complete`

轮询完成设备授权，获取 API Key 并自动保存。`--device-code` 可省略，自动从状态文件恢复。

| 选项            | 必填 | 默认值         | 说明                                  |
| --------------- | ---- | -------------- | ------------------------------------- |
| `--device-code` | 否   | 从状态文件读取 | `device-flow-start` 返回的 deviceCode |
| `--interval`    | 否   | `3`            | 轮询间隔（秒）                        |

```bash
# 最简单用法：直接运行，自动从状态文件恢复
python3 scripts/datadata_query.py device-flow-complete

# 或显式指定
python3 scripts/datadata_query.py device-flow-complete --device-code "a1b2c3..."
```

输出含 `key`、`permissions`、`expiresAt`、`savedTo`。成功后自动清除状态文件。
