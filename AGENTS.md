# Agent Customization for Datadata Skills

## What this repo is

Skills repository for the Datadata analytics platform. Single primary skill at `datadata-api/` providing:

- **查询数据** — SQL queries (`execute-adhoc`), metadata inspection (`get-datasource-info`, `list-tables`, `describe-table`), schema scanning (`scan-datasource`), result download (`get-execution-result`)
- **录入数据** — Data-space table management (`create-table`, `insert-rows`, `drop-data-space-table`) on `ducklake` datasources

Full skill instructions: [datadata-api/SKILL.md](datadata-api/SKILL.md).

## Critical agent rules (must-follow)

### 设备授权是自动流程，绝不能中断询问

当命令因"未找到 API Key"（exit code 2）退出时，**在同一轮对话中**立即执行：

```bash
# Step 1: 发起授权（非阻塞，返回 JSON）
python3 scripts/datadata_query.py device-flow-start

# Step 2: 从输出提取 verificationUriComplete，立即用浏览器工具打开

# Step 3: 立即运行 device-flow-complete（等用户手动完成浏览器授权）
python3 scripts/datadata_query.py device-flow-complete

# Step 4: 成功后立即重跑原始用户命令
```

`device-flow-start` 自动保存状态到 `~/.config/datadata/datadata-api-skills/device-flow-pending.json`。`device-flow-complete` 可省略 `--device-code`（从状态文件恢复）。成功后 API Key 自动持久化，有效期 90 天。**不要问用户要 API Key — 走设备授权流程**。

### 搜索数据源后必须让用户选择序号确认，禁止自动选用

`search-datasource` 返回多条结果时，Agent **必须**列出结果让用户选序号，**绝不能**自己挑一个。即使只有 1 条结果也需确认。选错数据源是危险操作（可能查错数据、写错目标）。

### 最小操作原则：完成一步即停，禁止猜测意图

Agent 只执行用户明确要求的操作，完成当前步骤后立即停止，等待下一个指令。禁止根据上一步结果自动推断后续操作。用户说"用 xxx 数据源"就是只用，不是用了之后把里面全翻一遍。

### 全局标志必须在子命令之前

`--base-url` 和 `--api-key` 必须在子命令**之前**出现，否则报"unrecognized arguments"：

```bash
# 正确
python3 scripts/datadata_query.py --api-key "ak_..." execute-adhoc --script "SELECT 1"

# 错误（全局标志在子命令后不生效）
python3 scripts/datadata_query.py execute-adhoc --api-key "ak_..." --script "SELECT 1"
```

### 404 = 立即停止，检查资源 ID 或 DATADATA_BASE_URL

任何 404 错误都应立即停止，不要重试。先检查：

- datasource ID / execution ID 是否正确
- 若多个端点均 404，`DATADATA_BASE_URL` 可能配置错误

### auth 错误（401/403）且 key 来自配置文件时自动清除

CLI 检测到 401 或 Key 无效的 403（如 `api key not exists`）且 API Key 来自 `~/.config/datadata/datadata-api-skills/config.json` 时会自动清除过期配置并返回 exit code 2。此时重新运行 `device-flow-start` 即可。

**重要区分**：403 `permission denied`（操作他人资源等正常权限拒绝）**不是** Key 失效，不会自动清除配置。Agent 应向用户说明权限不足即可。

### 查询只读，禁止写操作

`execute-adhoc` **仅支持 SELECT**。INSERT/UPDATE/DELETE/DDL 均被禁止。写入数据只能使用 `insert-rows`（支持批量）。

### DuckLake 数据源的别名规则特殊

只有 `ducklake` 类型 datasource 在 `--datasource "ID:ALIAS"` 绑定中**忽略 ALIAS**，SQL 中始终使用 `ducklake.{datasourceName}.{tableName}`。在编写 SQL 前必须先 `get-datasource-info` 获取 `datasourceName`。

### 大数据集不进入 context

通过 `get-execution-result` 下载结果到文件（默认 `/tmp/datadata-<id>.ndjson` 或 `.csv`）。报告 `outputPath`、`rowCount`、`format`，不要将完整数据打印到终端或上下文。先用 `head`/`tail` 预览，按需用命令行工具本地处理。

## File structure

```
datadata-skills/
├── AGENTS.md              # This file — agent guidance
├── CLAUDE.md              # Claude-specific deployment + conventions
├── README.md              # User-facing intro + API Key setup
├── scripts/
│   └── sync.sh            # Deploy to ~/.claude/skills/ or ~/.codex/skills/
└── datadata-api/          # The skill
    ├── SKILL.md           # Skill frontmatter + full instructions
    ├── agents/openai.yaml # Agent interface (OpenAI-compatible)
    ├── references/
    │   ├── api.md         # REST API endpoints + urllib examples
    │   ├── cli.md         # CLI subcommands, params, workflows
    │   ├── query-guide.md # SQL conventions, safety, result handling
    │   └── data-spaces.md # Data-space table management
    └── scripts/
        └── datadata_query.py  # CLI entrypoint (stdlib-only Python)
```

## Developer commands

| Command                                               | Purpose                                      |
| ----------------------------------------------------- | -------------------------------------------- |
| `./scripts/sync.sh claude`                            | Deploy skill to `~/.claude/skills/`          |
| `./scripts/sync.sh codex`                             | Deploy skill to `~/.codex/skills/` (default) |
| `python3 scripts/datadata_query.py <subcommand> ...`  | Run CLI commands                             |
| `export DATADATA_API_KEY="ak_..."`                    | Set API key manually                         |
| `export DATADATA_BASE_URL="https://www.datadata.com"` | Override base URL (local dev only)           |

## Conventions

- **Commit messages**: AngularJS style in Chinese — `feat(auth): 新增登录功能`
- **Python**: stdlib-only, no external deps. All generated scripts must use `urllib.request` directly, not CLI subprocess.
- **Docs**: Pure Chinese. Markdown files don't word-wrap (`.vscode/settings.json` → `[markdown].editor.wordWrap = off`).
- **Permissions**: `.claude/settings.local.json` allows `python3:*`, `git *`, `./scripts/sync.sh *`.

## Editing guidance

- Skill docs (`SKILL.md`, `references/`) are the primary artifacts — keep them in sync
- CLI changes require updating both `scripts/datadata_query.py` (subcommand + handler) and `references/cli.md`
- API changes require updating both `references/api.md` and testing against the live endpoint
- New features should provide `urllib.request` examples, not CLI subprocess calls
