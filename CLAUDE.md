# CLAUDE.md

Guidance for Claude Code agents working in this repository.

## Repository purpose

Claude Code **skills** repository for the Datadata analytics platform. One primary skill: `datadata-api/`. Organized around two core functions:

- **查询数据** — SQL queries (`execute-adhoc`), metadata inspection, result download
- **录入数据** — Data-space table management (`create-table`, `insert-rows`, `drop-data-space-table`)

Skill details: [datadata-api/SKILL.md](datadata-api/SKILL.md).

## Deploy

```bash
./scripts/sync.sh claude   # deploy to ~/.claude/skills/
./scripts/sync.sh codex    # deploy to ~/.codex/skills/ (default)
```

## Skill structure

```txt
datadata-api/
├── SKILL.md              # Frontmatter + full skill instructions
├── agents/openai.yaml    # Agent interface (OpenAI-compatible)
├── references/
│   ├── api.md            # REST API endpoints + urllib examples
│   ├── cli.md            # CLI commands, params, workflows
│   ├── query-guide.md    # SQL conventions, safety, result handling
│   └── data-spaces.md    # Data-space table management
└── scripts/
    └── datadata_query.py # CLI entrypoint (stdlib-only Python)
```

## CLI internals (`datadata_query.py`)

- **Two-pass parsing**: `parse_known_args()` first pass extracts global flags (`--base-url`, `--api-key`), then subcommand parser runs. Global flags **must appear before** the subcommand.
- **Dispatch**: flat `if-elif` chain in `main()`. New subcommands need a subparser in `parse_args()` + a `run_*` branch.
- **HTTP**: `request_json()` / `request_text()` / `request_bytes()` use `urllib.request` with `X-Datadata-Api-key` header.
- **Exit codes**: 0 = success, 1 = fetch error, 2 = invalid args.

## Conventions

- Commit messages: **AngularJS style in Chinese** — `feat(auth): 新增登录功能`
- Python: stdlib-only, no external deps. Generated scripts should use `urllib.request` directly, not CLI subprocess.
- Docs: Pure Chinese. Markdown files don't word-wrap (`.vscode/settings.json`).
- Permissions: `.claude/settings.local.json` allows `python3:*`, `git *`, `./scripts/sync.sh *`.
