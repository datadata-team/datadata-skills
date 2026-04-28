---
name: datadata-api
description: Run SQL or other scripts against Datadata via CLI. Creates adhoc executions and downloads results as NDJSON or CSV.
---

# Datadata API

Query Datadata through `scripts/datadata_query.py`. See [references/cli.md](./references/cli.md) for full argument reference.

## Subcommands

| Subcommand             | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| `get-datasource-info`  | Inspect datasource metadata                |
| `list-tables`          | List tables in a schema                    |
| `describe-table`       | Describe columns of a table                |
| `execute-adhoc`        | Create an execution, returns `executionId` |
| `get-execution-result` | Download result artifact                   |

## Workflow

```bash
# Export credentials
export DATADATA_API_KEY="..."

# Optional metadata discovery
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
  --format ndjson
```

Use `--output-path` on `get-execution-result` to control save location. Defaults to system temp.

Search saved results locally:

```bash
rg 'Acme|United States' /tmp/datadata-<execution-id>.ndjson
```

## Rules

### Parameter scoping

- `--datasource`, `--script`, `--script-type`, `--query-engine` → `execute-adhoc`
- `--execution-id`, `--format`, `--output-path` → `get-execution-result`
- Do not mix parameters between these two subcommands

### Query engine

- Default `duckdb`; switch to `clickhouse` only for ClickHouse datasources
- Use DuckDB SQL for `duckdb` queries; ClickHouse SQL for `clickhouse` queries
- ClickHouse datasources cannot cross-source join

### Datasource binding

- Format: `--datasource "DATASOURCE_ID:ATTACH_ALIAS"`, repeatable
- SQL references `ATTACH_ALIAS`, not the datasource name
- File datasources mount into `memory.main.<alias>` in DuckDB mode

### Result handling

- `--format ndjson` for searchable results; `csv` for exports
- Never send full large datasets into model context — save to file, search locally, summarize
- Report file path, format, and execution ID for reuse

### Safety

- Never run destructive SQL unless explicitly requested
- Never silently rewrite business logic in SQL
- If result fetch fails, return the `executionId` for manual inspection
- On `401`/`403`, verify the API key

### Inputs

- API key: `--api-key` or `DATADATA_API_KEY` env var (required)
- Base URL: defaults to `https://www.datadata.com/api/v1`; override via `DATADATA_BASE_URL` env var or `--base-url` flag (optional, for testing only; do NOT ask user for this)
- If API key missing, tell user how to obtain one: log in to https://www.datadata.com → click avatar → Settings → left sidebar "API Keys" → create a new API Key. Required permissions: `queries:execute-adhoc`, `executions:get`, `datasources:read`
- Inspect datasource/table/column metadata before writing SQL when uncertain

## Resources

- Script: [scripts/datadata_query.py](./scripts/datadata_query.py)
- CLI reference: [references/cli.md](./references/cli.md)
