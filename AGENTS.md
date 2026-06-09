# Agent Customization for Datadata Skills

## What this repo is

Skills repository for the Datadata analytics platform. Three skills:

| Skill               | Capabilities                                                                                                                 | Instructions                             |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| **`datadata-mcp/`** | 通过 MCP Server 进行数据查询与管理 — 搜索、元信息、SQL、Data Spaces 全流程。**有 MCP connector 时优先使用。**                | [SKILL.md](skills/datadata-mcp/SKILL.md) |
| **`datadata-api/`** | 通过 CLI 查询数据 (SQL queries, metadata inspection, result download) · 录入数据 (Data-space table management on `ducklake`) | [SKILL.md](skills/datadata-api/SKILL.md) |
| **`datadata-dql/`** | DQL (Starlark) 脚本编写 — 数据转换、DataFrame/Series 操作、SQL 查询、HTTP 请求、2D 绘图                                      | [SKILL.md](skills/datadata-dql/SKILL.md) |

## Critical agent rules (must-follow)

> **🔴 MCP 优先原则**：当 `datadata-mcp` connector 可用时，交互式操作优先使用 MCP。需要生成独立 Python 脚本（爬虫/ETL）时使用 `datadata-api`。
>
> 以下规则大部分适用于 `datadata-api`。`datadata-mcp` 和 `datadata-dql` 的规则见各自的 SKILL.md。

### 🔐 Authentication（datadata-api）

#### 设备授权是自动流程，绝不能中断询问

命令因"未找到 API Key"退出（exit code 2）时，**在同一轮对话中**立即执行：

```bash
python3 skills/datadata-api/scripts/datadata_query.py device-flow-start        # 发起授权
# 从输出提取 verificationUriComplete → 用浏览器工具打开让用户完成登录
python3 skills/datadata-api/scripts/datadata_query.py device-flow-complete      # 等用户完成
# 成功后立即重跑原始用户命令
```

状态自动保存到 `~/.config/datadata/datadata-api-skills/device-flow-pending.json`，`device-flow-complete` 可省略 `--device-code`。Key 有效期 90 天。**不要问用户要 API Key。**

#### Auth 错误处理

CLI 检测到 401 或 Key 无效的 403（`api key not exists`）且 Key 来自配置文件时自动清除过期配置并返回 exit code 2，重新运行 `device-flow-start` 即可。

**重要区分**：403 `permission denied`（操作他人资源等正常权限拒绝）**不是** Key 失效，不会自动清除配置。Agent 应向用户说明权限不足即可。

### 🛠️ CLI Usage（datadata-api）

#### 全局标志必须在子命令之前

`--base-url` 和 `--api-key` 必须在子命令**之前**出现，否则报"unrecognized arguments"：

```bash
# ✅ 正确
python3 skills/datadata-api/scripts/datadata_query.py --api-key "ak_..." execute-adhoc --script "SELECT 1"

# ❌ 错误（全局标志在子命令后不生效）
python3 skills/datadata-api/scripts/datadata_query.py execute-adhoc --api-key "ak_..." --script "SELECT 1"
```

#### 404 = 立即停止，检查资源 ID 或 DATADATA_BASE_URL

任何 404 错误立即停止，不要重试。先检查 datasource ID / execution ID 是否正确；若多个端点均 404，`DATADATA_BASE_URL` 可能配置错误。

#### 大数据集不进入 context

通过 `get-execution-result` 下载结果到文件（默认 `/tmp/datadata-<id>.ndjson` 或 `.csv`）。报告 `outputPath`、`rowCount`、`format`，不要将完整数据打印到终端或上下文。用 `head`/`tail` 预览，按需用命令行工具本地处理。

### 📊 Data Operations（datadata-api）

#### 查询只读，禁止写操作

`execute-adhoc` **仅支持 SELECT**。INSERT/UPDATE/DELETE/DDL 均被禁止。写入数据只能使用 `insert-rows`（支持批量）。

#### DuckLake 数据源的别名规则特殊

只有 `ducklake` 类型 datasource 在 `--datasource "ID:ALIAS"` 绑定中**忽略 ALIAS**，SQL 中始终使用 `ducklake.{datasourceName}.{tableName}`。编写 SQL 前必须先 `get-datasource-info` 获取 `datasourceName`。

### 🤖 Agent Behavior（通用）

#### 最小操作原则：完成一步即停，禁止猜测意图

Agent 只执行用户明确要求的操作，完成当前步骤后立即停止，等待下一个指令。禁止根据上一步结果自动推断后续操作。用户说"用 xxx 数据源"就是只用，不是用了之后把里面全翻一遍。

#### 搜索数据源后必须让用户选择序号确认

`search-datasource` 返回结果时，Agent **必须**列出结果让用户选序号，**绝不能**自己挑一个 — 即使只有 1 条结果也需确认。选错数据源是危险操作（可能查错数据、写错目标）。

## File structure

```txt
datadata-skills/
├── AGENTS.md                        # This file — agent guidance
├── README.md / README_zh.md         # User-facing intro + API Key setup
├── kilo.json                        # Kilo config (points to AGENTS.md)
├── .vscode/settings.json            # Editor settings (Markdown no-wrap, commit style)
├── .claude/settings.local.json      # Permissions (python3:*, git *; not committed)
├── skills/datadata-mcp/             # MCP Server skill (preferred)
│   ├── SKILL.md
│   └── references/
│       ├── query-guide.md
│       └── data-spaces.md
├── skills/datadata-api/             # CLI + REST skill
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   │   ├── api.md, cli.md, query-guide.md, data-spaces.md
│   └── scripts/
│       └── datadata_query.py
└── skills/datadata-dql/             # DQL (Starlark) scripting skill
    ├── SKILL.md
    └── references/
        ├── __builtins__.pyi, builtins.md, dataframe.md, series.md
        ├── query.md, fetch.md, json.md, math.md, time.md
        ├── canvas_drawing.md, faq_best_practices.md
```

## CLI internals (`datadata_query.py`)

- **Two-pass parsing**: `parse_known_args()` first pass extracts global flags (`--base-url`, `--api-key`), then subcommand parser runs. Global flags **must appear before** the subcommand.
- **Dispatch**: flat `if-elif` chain in `main()`. New subcommands need a subparser in `parse_args()` + a `run_*` branch.
- **HTTP**: `request_json()` / `request_text()` / `request_bytes()` use `urllib.request` with `X-Datadata-Api-key` header.
- **Exit codes**: 0 = success, 1 = fetch error, 2 = invalid args.

## Developer commands

| Command                                                                  | Purpose                            |
| ------------------------------------------------------------------------ | ---------------------------------- |
| `npx skills add ./skills/datadata-mcp --agent claude-code --global`      | 安装 MCP skill 到 Claude Code      |
| `npx skills add ./skills/datadata-mcp --agent codex --global`            | 安装 MCP skill 到 Codex            |
| `npx skills add ./skills/datadata-api --agent claude-code --global`      | 安装 API skill 到 Claude Code      |
| `npx skills add ./skills/datadata-api --agent codex --global`            | 安装 API skill 到 Codex            |
| `python3 skills/datadata-api/scripts/datadata_query.py <subcommand> ...` | 运行 CLI 命令                      |
| `npx skills add ./skills/datadata-dql --agent claude-code --global`      | 安装 DQL skill 到 Claude Code      |
| `npx skills add ./skills/datadata-dql --agent codex --global`            | 安装 DQL skill 到 Codex            |
| `export DATADATA_API_KEY="ak_..."`                                       | Set API key manually               |
| `export DATADATA_BASE_URL="https://www.datadata.com"`                    | Override base URL (local dev only) |

## Conventions

- **Commit messages**: AngularJS style in Chinese — `feat(auth): 新增登录功能`
- **Python (datadata-api)**: stdlib-only, no external deps. Generated scripts must use `urllib.request` directly, not CLI subprocess.
- **DQL**: All built-ins are globals (`query`, `fetch`, `DataFrame`, `Series`, `json`, `math`, etc.) — no `import` needed. `__builtins__.pyi` is the source of truth for signatures.
- **Docs**: Pure Chinese. Markdown files don't word-wrap (`.vscode/settings.json` → `[markdown].editor.wordWrap = off`).
- **Permissions**: `.claude/settings.local.json` allows `python3:*`, `git *`.

## Editing guidance

- Skill docs (`SKILL.md`, `references/`) are the primary artifacts — keep them in sync
- **datadata-mcp**: MCP tool changes require updating `skills/datadata-mcp/SKILL.md`
- **datadata-api**: CLI changes require updating both `skills/datadata-api/scripts/datadata_query.py` and `references/cli.md`; API changes require updating `references/api.md`
- **datadata-dql**: Reference changes must keep `__builtins__.pyi` (source of truth for signatures) and `.md` docs in sync
- New features should provide DQL code samples (datadata-dql), not CLI subprocess calls
