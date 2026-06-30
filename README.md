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

### datadata-manual (recommended)

Datadata platform operations manual — interact with data through MCP Server, **no API Key required**, OAuth authentication.

**Query data** — Search datasources, inspect metadata, list tables, describe column schemas, run SQL queries (DuckDB / ClickHouse, cross-source joins), set table/column comments, execute DQL scripts.

**Manage Data Spaces** — Create tables, batch-insert rows, describe table structures, drop tables.

See [skills/datadata-manual/SKILL.md](./skills/datadata-manual/SKILL.md) for detailed usage.

### datadata-rest-api

Datadata REST API complete reference — all endpoint documentation with `urllib.request` (zero-dependency) usage examples. Primary use case: generating standalone Python scripts (crawlers, ETL, batch processing). Requires API Key.

See [skills/datadata-rest-api/SKILL.md](./skills/datadata-rest-api/SKILL.md) for detailed usage.

### datadata-memory

Manage AI persistent memories via Datadata MCP Server — add atomic facts, semantic search, update corrections, delete cleanup. Supports merge & compress (auto-dedup similar memories) and conflict merge (keep latest info while preserving change history).

See [skills/datadata-memory/SKILL.md](./skills/datadata-memory/SKILL.md) for detailed usage.

### datadata-dql

Write DQL (Datadata Query Language) scripts — a Starlark-based scripting language for data transformation, cleaning, generation, and custom processing logic. Supports DataFrame/Series operations, SQL queries, HTTP requests, 2D drawing, and more.

See [skills/datadata-dql/SKILL.md](./skills/datadata-dql/SKILL.md) for detailed usage.

### Authentication

**datadata-manual (recommended)**: Uses OAuth — sign in once, no API Key needed.

**datadata-rest-api**: Two ways to authenticate:

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
