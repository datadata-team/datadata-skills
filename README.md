# Datadata Skills

Agent skills for the [Datadata](https://www.datadata.com) analytics platform.

## Installation

```bash
npx skills add datadata-team/datadata-skills
```

> **Tip:** If you use pnpm, replace `npx` with `pnpx`:
>
> ```bash
> pnpx skills add datadata-team/datadata-skills
> ```

## Skills

### datadata-api

Interact with Datadata through natural language. Two core capabilities:

**Query data** — Inspect datasource metadata, list tables, describe column schemas, run SQL queries (DuckDB / ClickHouse, cross-source joins), download results as NDJSON or CSV.

**Ingest data** — Create tables in Data Spaces (ducklake), batch-insert rows, drop tables. Ingested data is immediately queryable via standard SQL.

See [skills/datadata-api/SKILL.md](./skills/datadata-api/SKILL.md) for detailed usage.

### datadata-dql

Write DQL (Datadata Query Language) scripts — a Starlark-based scripting language for data transformation, cleaning, generation, and custom processing logic. Supports DataFrame/Series operations, SQL queries, HTTP requests, 2D drawing, and more.

See [skills/datadata-dql/SKILL.md](./skills/datadata-dql/SKILL.md) for detailed usage.

### Authentication

The skill supports two ways to authenticate:

#### Automatic (recommended)

If no API Key is configured, the agent will automatically guide you through device authorization when you first run a command — just follow the link displayed in the terminal to complete sign-in. The key is then cached locally for 90 days.

#### Manual (fallback)

Create an API Key in the Datadata platform with the required permissions:

| Permission              | Purpose                       |
| ----------------------- | ----------------------------- |
| `queries:execute-adhoc` | Run SQL queries               |
| `executions:get`        | Retrieve query results        |
| `datasources:read`      | Read datasource metadata      |
| `datasources:scan`      | Trigger async schema scans    |
| `data-spaces:write`     | Create tables and insert data |

1. Sign in to [datadata.com](https://www.datadata.com)
2. Avatar → Settings → "API Keys" (left sidebar) → Create a new key
3. Select the required permissions
4. Set it as an environment variable:

```bash
export DATADATA_API_KEY="ak_..."
```
