---
name: datadata-api
description: "Query Datadata via CLI — run adhoc SQL, inspect datasource metadata, list and describe tables, and download results as NDJSON/CSV. Use this skill whenever the user mentions Datadata, wants to query data, explore datasources or table schemas, or fetch query results. Triggers on: Datadata, data exploration, SQL queries against datasources, table inspection, execution results."
---

# Datadata API

Query Datadata through `scripts/datadata_query.py`. See [references/cli.md](./references/cli.md) for CLI argument reference and [references/api.md](./references/api.md) for the full REST API reference (including direct `urllib.request` examples for generated scripts).

## Concepts

- **Datasource** — A data source that queries target. Different datasource types (ducklake, MySQL, ClickHouse, CSV, etc.) have different table naming conventions.
- **Data space** — A special datasource of type `ducklake` that supports user-created tables and data insertion. The data-space name is the datasource's `name`. Querying data within a data space uses the exact same flow as any other datasource: bind the datasource in a query, then execute it.
- **Query** (`execute-adhoc`) — An abstraction that bundles a SQL script, datasource bindings, and a query engine type. A query is not executed until you create an execution from it.
- **Execution** (`get-execution-result`) — An abstraction over running a query. Each call to `execute-adhoc` creates an execution and returns an `executionId`. Use that ID to fetch the result asynchronously.

## Subcommands

| Subcommand             | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| `get-datasource-info`  | Inspect datasource metadata                |
| `list-tables`          | List tables in a schema                    |
| `describe-table`       | Describe columns of a table                |
| `create-table`         | Create a table in a data space             |
| `insert-rows`          | Insert rows into a data space table        |
| `scan-datasource`      | Trigger an async schema scan for a datasource |
| `execute-adhoc`        | Create and run a query, returns `executionId` |
| `get-execution-result` | Download execution result artifact         |

## Workflow

```bash
# Export credentials (preferred, avoids arg-ordering issues)
export DATADATA_API_KEY="..."
export DATADATA_BASE_URL="http://127.0.0.1:9870/api/v1/"  # only for local dev

# Optional metadata discovery — only describe tables you actually need
python3 scripts/datadata_query.py get-datasource-info --datasource-id "<id>"
python3 scripts/datadata_query.py list-tables --datasource-id "<id>" --schema-name "main"
python3 scripts/datadata_query.py describe-table --datasource-id "<id>" --schema-name "main" --table-name "customers"

# Create execution
python3 scripts/datadata_query.py execute-adhoc \
  --script-type sql \
  --query-engine duckdb \
  --datasource "<id>:alias" \
  --script "select * from alias limit 20"

# Download result
python3 scripts/datadata_query.py get-execution-result \
  --execution-id "<execution-id>" \
  --format ndjson \
  --timeout 30
```

**CRITICAL: `--base-url` and `--api-key` are GLOBAL flags and must appear BEFORE the subcommand.** Placing them after the subcommand (e.g. `get-datasource-info --datasource-id "..." --base-url "..."`) will fail with "unrecognized arguments".

Use `--output-path` on `get-execution-result` to control save location. Defaults to system temp.

## Data Spaces (Table Management)

Create tables and insert data — useful when AI generates crawler/scraper scripts that need to store results in Datadata. Tables created this way are queryable like any other datasource via `execute-adhoc`.

> **Note:** Only datasources of type `ducklake` support data-spaces operations. Always check the datasource type via `get-datasource-info` before attempting to create a table or insert rows. When querying ducklake tables, use the `ducklake.{datasourceName}.{tableName}` qualified name syntax — see "Table naming" below for details.

**For generated scripts, prefer direct API calls over the CLI** — direct calls use `urllib.request` (stdlib, no dependencies), avoid subprocess overhead, and give cleaner error handling. See [references/api.md](./references/api.md#data-spaces-apis) for request formats and Python examples.

```bash
# Create table
python3 scripts/datadata_query.py create-table \
  --datasource-id "<id>" \
  --table-name "products" \
  --columns '[{"columnName": "id", "columnType": "INTEGER"}, {"columnName": "name", "columnType": "VARCHAR"}]'

# Insert rows (transactional — all-or-nothing)
python3 scripts/datadata_query.py insert-rows \
  --datasource-id "<id>" \
  --table-name "products" \
  --columns '["id", "name"]' \
  --rows '[[1, "Widget"], [2, "Gadget"]]'

# Query with ducklake qualified name (get the datasource name from get-datasource-info)
python3 scripts/datadata_query.py execute-adhoc \
  --script-type sql --query-engine duckdb \
  --datasource "<id>:<datasourceName>" \
  --script "select * from ducklake.<datasourceName>.products limit 10"
```

### Auth note

`create-table` and `insert-rows` require the API key to have the `data-spaces:write` permission (in addition to the existing permissions). `execute-adhoc` queries against these tables work with `queries:execute-adhoc` as usual.

## Scanning Datasource Schema

Trigger an asynchronous schema scan to refresh table metadata for a datasource:

```bash
python3 scripts/datadata_query.py scan-datasource --datasource-id "<id>"
```

Prints a task object like `{"taskId": "...", "taskType": "scan", "state": "active"}`. The scan runs in the background — this command returns immediately.

> **For data-spaces (ducklake):** If you need immediate, real-time table structure, use the data-spaces `describe-table` endpoint instead (CLI: `describe-table`, or direct POST to `/data-spaces/{id}/describe-table`). The scan endpoint is designed for non-ducklake datasources that need background schema discovery; ducklake datasources can always describe tables synchronously.

### Fetching results

`execute-adhoc` returns immediately with an `executionId` — the query runs asynchronously. Pass `--timeout <seconds>` to `get-execution-result` to let the backend wait for completion. If the query isn't done within the timeout, the API returns a timeout error; use a longer timeout or return the `executionId` to the user.

Search saved results locally:

```bash
rg 'Acme|United States' /tmp/datadata-<execution-id>.ndjson
```

## Rules

### Parameter scoping

- `--datasource`, `--script`, `--script-type`, `--query-engine` → `execute-adhoc`
- `--execution-id`, `--format`, `--output-path` → `get-execution-result`
- `--datasource-id` → `get-datasource-info`, `list-tables`, `describe-table` (ID only, no `:alias` binding)
- `--datasource-id`, `--table-name`, `--columns` → `create-table`
- `--datasource-id`, `--table-name`, `--columns`, `--rows` → `insert-rows`
- `--datasource-id` → `scan-datasource`
- Do not mix parameters between subcommands
- API key always starts with `ak_`; datasource IDs look like random strings (e.g. `CXNGJifvqE48kdzKVC9o5`). Never use a non-`ak_` string as `--api-key`

### Query engine

- Default `duckdb`; switch to `clickhouse` only for ClickHouse datasources
- Use DuckDB SQL for `duckdb` queries; ClickHouse SQL for `clickhouse` queries
- ClickHouse datasources cannot cross-source join

### Datasource binding

- Format: `--datasource "DATASOURCE_ID:ATTACH_ALIAS"`, repeatable
- SQL references tables using the alias, not the datasource ID
- **Exception**: `ducklake` type datasources ignore the alias — the datasource's own `name` is always used as the schema. Use `get-datasource-info` to retrieve it.

### Table naming

The way you reference a table in SQL depends on the datasource **type**. Always check the datasource type (via `get-datasource-info`) before writing SQL so you use the correct naming pattern.

**Ducklake datasources** (type `ducklake`): These are Datadata-managed DuckDB-based data spaces. The catalog name is fixed as `ducklake`. The datasource's own `name` (from `get-datasource-info`) is used as the schema — **custom aliases are not supported**. There is no schema nesting beyond the datasource name:

```
ducklake.{datasourceName}.{tableName}
```

Use `get-datasource-info` to find the datasource name, then use it in SQL and `--datasource "ID:NAME"` binding.

**Database datasources** (MySQL, PostgreSQL, DuckDB, SQLite, ClickHouse, etc.): The alias becomes the database name. Tables live inside schemas within that database:

```
attachAlias.schemaName.tableName
```

**File datasources** (CSV, JSON, Parquet, etc.): Each attached file becomes a table in DuckDB's built-in `memory` database under the `main` schema. The alias is the table name:

```
memory.main.attachAlias
```

**Use short names whenever unambiguous:**

- `memory.main.sales` → just `sales` (when no other table named `sales` exists across all attached datasources)
- `mydb.public.users` → just `users` (when `users` is unique across all schemas)
- Use `*` to reference all columns from a short name: `SELECT * FROM sales`
- When joining across datasources, use fully qualified names to avoid ambiguity

### Result handling

- `--format ndjson` for searchable results; `csv` for exports
- Never send full large datasets into model context — save to file, search locally, summarize
- Report file path, format, and execution ID for reuse

### Safety

- Never run destructive SQL unless explicitly requested
- Never silently rewrite business logic in SQL

### Error handling

- On `401`/`403`: verify the API key format (starts with `ak_`) and that it hasn't expired
- On **any 404**: stop immediately. The API endpoint does not exist at this base URL — do NOT retry with different subcommands or parameters. Tell the user the API is unreachable and suggest checking `DATADATA_BASE_URL`
- On `5xx` or network timeout: retry once after 3 seconds. If it fails again, report the error with the `executionId`
- On `--timeout` exceeded (backend returns timeout, query still running): return the `executionId` — suggest a larger `--timeout` or checking later

### Inputs

- API key: `--api-key` or `DATADATA_API_KEY` env var (required)
- Base URL: defaults to `https://www.datadata.com/api/v1`; override via `DATADATA_BASE_URL` env var or `--base-url` flag (optional, for testing only; do NOT ask user for this)
- Inspect datasource/table/column metadata before writing SQL when uncertain
- **Describe only the tables you need**: use `list-tables` to find candidates, then `describe-table` on specific tables. Never blindly dump all columns for every table — large datasources will overflow context

### API Key

If `DATADATA_API_KEY` is not set, print:

```
1. 登录 https://www.datadata.com
2. 头像 → Settings → 左侧 "API Keys" → 创建新 Key
3. 权限勾选: queries:execute-adhoc, executions:get, datasources:read, datasources:scan, data-spaces:write
4. 然后 export DATADATA_API_KEY="<key>" 或直接告诉我。
```

## Resources

- Script: [scripts/datadata_query.py](./scripts/datadata_query.py)
- CLI reference: [references/cli.md](./references/cli.md)
