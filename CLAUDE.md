# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is a Claude Code **skills** repository providing agent skills for the Datadata analytics platform. Each skill lives in its own directory with a `SKILL.md`, optional `agents/` config, `references/` docs, and `scripts/`.

## Skills

### `datadata-api`

Run SQL via the Datadata API using `datadata-api/scripts/datadata_query.py` (stdlib-only Python, no dependencies required).

**Subcommands** (see `datadata-api/references/cli.md` for full arg reference):

| Subcommand             | Purpose                                    |
| ---------------------- | ------------------------------------------ |
| `get-datasource-info`  | Inspect datasource metadata                |
| `list-tables`          | List tables in a schema                    |
| `describe-table`       | Describe columns of a table                |
| `execute-adhoc`        | Create an execution, returns `executionId` |
| `get-execution-result` | Download result artifact (NDJSON/CSV)      |

**Key conventions** (detailed in `datadata-api/SKILL.md`):

- Auth via `--api-key` flag or `DATADATA_API_KEY` env var (required); base URL defaults to `https://www.datadata.com/api/v1`, override via `DATADATA_BASE_URL` env var or `--base-url` flag (optional, for testing only; do NOT ask user)
- `--datasource` uses format `DATASOURCE_ID:ATTACH_ALIAS` (repeatable); SQL references the alias, not the datasource name
- Query engine is `duckdb` by default; use `clickhouse` only for ClickHouse datasources (which cannot cross-source join)
- Results: `--format ndjson` for searchable output, `csv` for exports; defaults to `ndjson`
- Never feed large result sets into model context — save to file, search locally with `rg`, then summarize

**Architecture of `datadata_query.py`**:

- Global args (`--base-url`, `--api-key`) must appear before subcommand
- `request_json()`/`request_text()`/`request_bytes()` handle HTTP via `urllib.request` with `X-Datadata-Api-key` header
- `create_execution()` POSTs to `/queries/execute-adhoc`, then recursively searches response for an execution ID
- `fetch_result_artifact()` GETs `/executions/{id}/result`; saves to temp dir as `datadata-{id}.ndjson` or `.csv`
- `parse_datasource_bindings()` splits `ID:ALIAS` strings into `[{datasourceId, attachAlias}]`
- Exit codes: 0 = success, 1 = result fetch error, 2 = missing/invalid args
