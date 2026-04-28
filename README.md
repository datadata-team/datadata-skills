# Datadata Skills

Claude Code skills for the [Datadata](https://www.datadata.com) analytics platform.

## Skills

### datadata-api

Run SQL or other scripts against Datadata via CLI. Creates adhoc executions and downloads results as NDJSON or CSV.

```bash
export DATADATA_API_KEY="..."
python3 datadata-api/scripts/datadata_query.py execute-adhoc \
  --script-type sql \
  --query-engine duckdb \
  --datasource "ds_123:orders" \
  --script "select * from orders limit 20"
```

See [datadata-api/SKILL.md](./datadata-api/SKILL.md) for full usage, subcommands, and parameter reference.

## Development

```bash
# Deploy skill changes to ~/.claude/skills/
./scripts/sync.sh
```
