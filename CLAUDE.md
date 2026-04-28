# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

Claude Code **skills** repository for the Datadata analytics platform. Each skill lives in its own directory with a `SKILL.md`, optional `agents/` config, `references/` docs, and `scripts/`.

## Deploying changes

```bash
./scripts/sync.sh
```

Rsyncs `datadata-api/` into `~/.claude/skills/`. Run after editing scripts, SKILL.md, references, or agent configs.

## Skill: datadata-api

Run SQL against Datadata via `datadata-api/scripts/datadata_query.py` (stdlib-only Python, zero dependencies). Auth via `DATADATA_API_KEY` env var or `--api-key` flag. Base URL defaults to `https://www.datadata.com/api/v1`, override via `DATADATA_BASE_URL` env var or `--base-url`.

### Architecture of `datadata_query.py`

- `main()` dispatches subcommands via a flat if-elif chain on `args.command`. To add a subcommand, register a subparser in `parse_args()` and add a corresponding `run_*` branch in `main()`.
- Global args (`--base-url`, `--api-key`) must appear **before** the subcommand on the CLI
- `request_json()` / `request_text()` / `request_bytes()` — three HTTP helpers using `urllib.request` with `X-Datadata-Api-key` header. `request_json` auto-detects NDJSON vs JSON responses.
- `create_execution()` POSTs to `/queries/execute-adhoc`, then recursively searches the response for an execution ID via `find_execution_id()`
- `fetch_result_artifact()` GETs `/executions/{id}/result`; saves to temp dir as `datadata-{id}.ndjson` or `.csv`
- `parse_datasource_bindings()` splits `ID:ALIAS` strings into `[{datasourceId, attachAlias}]`
- Exit codes: 0 = success, 1 = result fetch error, 2 = missing/invalid args

### Agent config

`datadata-api/agents/openai.yaml` defines the agent interface (display name, description, default prompt) for OpenAI-compatible agent runners.

### Key conventions

Detailed rules live in `datadata-api/SKILL.md` (parameter scoping, query engine selection, datasource binding syntax, result handling, safety rules). CLI argument reference in `datadata-api/references/cli.md`. Do not duplicate those rules here — the skill system loads SKILL.md directly.
