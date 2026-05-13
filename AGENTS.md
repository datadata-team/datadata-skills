# Agent Customization for Datadata Skills

## What this repo is

A skills repository for the Datadata analytics platform, organized around two core functions:

- **查询数据** (Query) — SQL queries, metadata inspection, schema scanning
- **录入数据** (Data Entry) — Data-space table management (create, insert, drop)

Detailed skill documentation lives in [datadata-api/SKILL.md](datadata-api/SKILL.md).

## Key files

| File                                                                             | Purpose                                        |
| -------------------------------------------------------------------------------- | ---------------------------------------------- |
| [datadata-api/SKILL.md](datadata-api/SKILL.md)                                   | Skill instructions, concepts, rules            |
| [datadata-api/references/api.md](datadata-api/references/api.md)                 | REST API reference + `urllib.request` examples |
| [datadata-api/references/cli.md](datadata-api/references/cli.md)                 | CLI commands, parameters, workflows            |
| [datadata-api/references/query-guide.md](datadata-api/references/query-guide.md) | SQL conventions, safety, result handling       |
| [datadata-api/references/data-spaces.md](datadata-api/references/data-spaces.md) | Data-space table management                    |
| [datadata-api/scripts/datadata_query.py](datadata-api/scripts/datadata_query.py) | CLI entrypoint (stdlib-only Python)            |
| [datadata-api/agents/openai.yaml](datadata-api/agents/openai.yaml)               | OpenAI-compatible agent interface              |

## Conventions

- **Commit messages**: AngularJS style in **Chinese** — `feat(auth): 新增登录功能`
- **Python**: stdlib-only, no external dependencies
- **Docs**: Pure Chinese, Markdown files don't word-wrap
- **Deploy**: `./scripts/sync.sh [claude|codex]` rsyncs `datadata-api/` into skills directory (default: codex)

## Editing guidance

- Skill docs (SKILL.md, references/) are the primary artifacts — keep them in sync
- CLI changes require updating both `datadata_query.py` (subcommand + handler) and `cli.md`
- API changes require updating both `api.md` and testing against the live endpoint
- When adding new features, prefer direct REST API calls (`urllib.request`) over CLI subprocess for generated scripts
