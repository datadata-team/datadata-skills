# Agent Customization for Datadata Skills

## What this repo is

Skills repository for the Datadata analytics platform. Four skills:

| Skill                  | Capabilities                                                                                           | Instructions                                |
| ---------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------- |
| **`datadata-mcp/`**    | 通过 MCP Server 进行数据查询与管理 — 搜索、元信息、SQL、Data Spaces 全流程。**交互式操作的首选方式。** | [SKILL.md](skills/datadata-mcp/SKILL.md)    |
| **`datadata-api/`**    | Datadata REST API 参考 — 完整端点文档和 `urllib.request` 调用示例。首要用例：生成爬虫/ETL/批处理脚本。 | [SKILL.md](skills/datadata-api/SKILL.md)    |
| **`datadata-dql/`**    | DQL (Starlark) 脚本编写 — 数据转换、DataFrame/Series 操作、SQL 查询、HTTP 请求、2D 绘图                | [SKILL.md](skills/datadata-dql/SKILL.md)    |
| **`datadata-memory/`** | AI 持久化记忆管理 — 添加、搜索、更新、删除记忆，支持语义搜索和多维度过滤                               | [SKILL.md](skills/datadata-memory/SKILL.md) |

## Critical agent rules (must-follow)

> **🔴 MCP 优先原则**：交互式操作（聊天中查询、探索数据、管理 Data Spaces、定时任务等）一律使用 `datadata-mcp`。`datadata-api` 用于需要直接参考 REST API 文档的场景，首要用例是生成独立 Python 脚本（爬虫/ETL/批处理）。
>
> `datadata-mcp`、`datadata-dql` 和 `datadata-memory` 的规则见各自的 SKILL.md。

### 🤖 Agent Behavior（通用）

#### 最小操作原则：完成一步即停，禁止猜测意图

Agent 只执行用户明确要求的操作，完成当前步骤后立即停止，等待下一个指令。禁止根据上一步结果自动推断后续操作。用户说"用 xxx 数据源"就是只用，不是用了之后把里面全翻一遍。

#### 搜索数据源后必须让用户选择序号确认

`search-datasource` 返回结果时，Agent **必须**列出结果让用户选序号，**绝不能**自己挑一个 — 即使只有 1 条结果也需确认。选错数据源是危险操作（可能查错数据、写错目标）。

#### 生成的脚本必须零依赖

使用 `datadata-api` 生成的 Python 脚本只能使用标准库（`urllib.request`、`json`、`os` 等），不依赖 `requests`、`pandas` 等第三方库。

## File structure

```txt
datadata-skills/
├── AGENTS.md                        # This file — agent guidance
├── README.md / README_zh.md         # User-facing intro + API Key setup
├── kilo.json                        # Kilo config (points to AGENTS.md)
├── .vscode/settings.json            # Editor settings (Markdown no-wrap, commit style)
├── .claude/settings.local.json      # Permissions (python3:*, git *; not committed)
├── skills/datadata-mcp/             # MCP Server skill (interactive use — preferred)
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── query-guide.md
│       └── data-spaces.md
├── skills/datadata-api/             # REST API skill (script generation)
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── api.md, query-guide.md, data-spaces.md
├── skills/datadata-memory/          # Persistent memory management skill
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       └── memory-guide.md
└── skills/datadata-dql/             # DQL (Starlark) scripting skill
    ├── SKILL.md
    └── references/
        ├── __builtins__.pyi, builtins.md, dataframe.md, series.md
        ├── query.md, fetch.md, json.md, math.md, time.md
        ├── canvas_drawing.md, faq_best_practices.md
```

## Developer commands

| Command                                                                | Purpose                            |
| ---------------------------------------------------------------------- | ---------------------------------- |
| `npx skills add ./skills/datadata-mcp --agent claude-code --global`    | 安装 MCP skill 到 Claude Code      |
| `npx skills add ./skills/datadata-mcp --agent codex --global`          | 安装 MCP skill 到 Codex            |
| `npx skills add ./skills/datadata-api --agent claude-code --global`    | 安装 API skill 到 Claude Code      |
| `npx skills add ./skills/datadata-api --agent codex --global`          | 安装 API skill 到 Codex            |
| `npx skills add ./skills/datadata-memory --agent claude-code --global` | 安装 Memory skill 到 Claude Code   |
| `npx skills add ./skills/datadata-memory --agent codex --global`       | 安装 Memory skill 到 Codex         |
| `npx skills add ./skills/datadata-dql --agent claude-code --global`    | 安装 DQL skill 到 Claude Code      |
| `npx skills add ./skills/datadata-dql --agent codex --global`          | 安装 DQL skill 到 Codex            |
| `export DATADATA_API_KEY="ak_..."`                                     | Set API key manually               |
| `export DATADATA_BASE_URL="https://www.datadata.com"`                  | Override base URL (local dev only) |

## Conventions

- **Commit messages**: AngularJS style in Chinese — `feat(auth): 新增登录功能`
- **Python (datadata-api)**: stdlib-only, no external deps. Generated scripts must use `urllib.request` directly.
- **DQL**: All built-ins are globals (`query`, `fetch`, `DataFrame`, `Series`, `json`, `math`, etc.) — no `import` needed. `__builtins__.pyi` is the source of truth for signatures.
- **Docs**: Pure Chinese. Markdown files don't word-wrap (`.vscode/settings.json` → `[markdown].editor.wordWrap = off`).
- **Permissions**: `.claude/settings.local.json` allows `python3:*`, `git *`.

## Editing guidance

- Skill docs (`SKILL.md`, `references/`) are the primary artifacts — keep them in sync
- **datadata-mcp**: MCP tool changes require updating `skills/datadata-mcp/SKILL.md`
- **datadata-api**: API endpoint changes require updating `references/api.md`
- **datadata-dql**: Reference changes must keep `__builtins__.pyi` (source of truth for signatures) and `.md` docs in sync
- New features should provide DQL code samples (datadata-dql), not CLI subprocess calls
