# CLI Reference

## Conventions

```bash
python3 scripts/datadata_query.py [--base-url URL] [--api-key KEY] <subcommand> [options]
```

Global options (`--base-url`, `--api-key`) must appear **before** the subcommand.
Prefer env vars `DATADATA_BASE_URL` and `DATADATA_API_KEY` to avoid repeating them per command.

## Subcommands

### `get-datasource-info`

| Option            | Required | Description              |
| ----------------- | -------- | ------------------------ |
| `--datasource-id` | Yes      | Datasource ID to inspect |

```bash
python3 scripts/datadata_query.py get-datasource-info --datasource-id "ds_123"
```

### `list-tables`

| Option            | Required | Description                            |
| ----------------- | -------- | -------------------------------------- |
| `--datasource-id` | Yes      | Datasource ID                          |
| `--schema-name`   | No       | Filter by schema; omit for all schemas |

```bash
python3 scripts/datadata_query.py list-tables --datasource-id "ds_123" --schema-name "main"
```

### `describe-table`

| Option            | Required | Description        |
| ----------------- | -------- | ------------------ |
| `--datasource-id` | Yes      | Datasource ID      |
| `--schema-name`   | Yes      | Schema name        |
| `--table-name`    | Yes      | Table or view name |

```bash
python3 scripts/datadata_query.py describe-table --datasource-id "ds_123" --schema-name "main" --table-name "customers"
```

### `create-table`

| Option            | Required | Description                                                                            |
| ----------------- | -------- | -------------------------------------------------------------------------------------- |
| `--datasource-id` | Yes      | Datasource (data space) ID                                                             |
| `--table-name`    | Yes      | New table name                                                                         |
| `--columns`       | Yes      | JSON array of column definitions: `'[{"columnName": "id", "columnType": "INTEGER"}]'` |

```bash
python3 scripts/datadata_query.py create-table \
  --datasource-id "123" \
  --table-name "products" \
  --columns '[{"columnName": "id", "columnType": "INTEGER"}, {"columnName": "name", "columnType": "VARCHAR"}]'
```

Prints `{"status": "ok", "tableName": "..."}` on success.

### `insert-rows`

| Option            | Required | Description                                                    |
| ----------------- | -------- | -------------------------------------------------------------- |
| `--datasource-id` | Yes      | Datasource (data space) ID                                     |
| `--table-name`    | Yes      | Target table name                                              |
| `--columns`       | Yes      | JSON array of column names: `'["col1", "col2"]'`              |
| `--rows`          | Yes      | JSON 2D array of row data: `'[["v1", 1], ["v2", 2]]'`        |

```bash
python3 scripts/datadata_query.py insert-rows \
  --datasource-id "123" \
  --table-name "products" \
  --columns '["id", "name"]' \
  --rows '[[1, "Widget"], [2, "Gadget"]]'
```

Prints `{"status": "ok", "tableName": "...", "inserted": <count>}` on success.

### `scan-datasource`

| Option            | Required | Description          |
| ----------------- | -------- | -------------------- |
| `--datasource-id` | Yes      | Datasource ID to scan |

```bash
python3 scripts/datadata_query.py scan-datasource --datasource-id "CXNGJifvqE48kdzKVC9o5"
```

Prints a JSON object with `taskId`, `taskType`, and `state`. The scan is async — use the data-spaces `describe-table` for real-time table structure on ducklake datasources.

### `execute-adhoc`

| Option           | Required | Default  | Description                    |
| ---------------- | -------- | -------- | ------------------------------ |
| `--script`       | Yes      | —        | SQL or script content          |
| `--script-type`  | No       | `sql`    | Script type                    |
| `--query-engine` | No       | `duckdb` | `duckdb` or `clickhouse`       |
| `--datasource`   | No       | —        | Repeatable, format: `ID:ALIAS` |

```bash
python3 scripts/datadata_query.py execute-adhoc \
  --script-type sql \
  --query-engine duckdb \
  --datasource "ds_123:orders" \
  --datasource "ds_users:users" \
  --script "select * from orders join users on orders.user_id = users.id"
```

Prints a JSON object with `executionId` and the full execution response.

### `get-execution-result`

| Option           | Required | Default     | Description                       |
| ---------------- | -------- | ----------- | --------------------------------- |
| `--execution-id` | Yes      | —           | Execution ID from `execute-adhoc` |
| `--format`       | No       | `ndjson`    | `ndjson` or `csv`                 |
| `--output-path`  | No       | system temp | Output file path                  |
| `--timeout`      | No       | —           | Seconds to wait for execution     |

```bash
python3 scripts/datadata_query.py get-execution-result --execution-id "CaU6DR..." --format ndjson
```

Prints a JSON object with `executionId` and `result` metadata (path, bytes, row count).
