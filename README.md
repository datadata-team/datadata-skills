# Datadata Skills

Agent skills for the [Datadata](https://www.datadata.com) analytics platform.

## Skills

### datadata-api

通过自然语言与 Datadata 平台交互，围绕两大核心功能：

**查询数据** — 查看数据源元数据、列出表、描述列结构、执行 SQL 查询（DuckDB / ClickHouse，支持跨源 join）、下载 NDJSON/CSV 结果

**录入数据** — 在 Data Spaces（ducklake）中创建表、批量插入数据、删除表，录入后可通过标准查询读取

```bash
# Codex
npx skills add https://github.com/datadata-team/datadata-skills/datadata-api --agent codex --global

# Claude Code
npx skills add https://github.com/datadata-team/datadata-skills/datadata-api --agent claude-code --global
```

详细用法见 [datadata-api/SKILL.md](./datadata-api/SKILL.md)。

### 获取 API Key

在 Datadata 平台中创建 API Key，根据用途勾选所需权限：

| 权限                    | 用途                 |
| ----------------------- | -------------------- |
| `queries:execute-adhoc` | 执行 SQL 查询        |
| `executions:get`        | 获取执行结果         |
| `datasources:read`      | 读取数据源元数据     |
| `datasources:scan`      | 触发异步 schema 扫描 |
| `data-spaces:write`     | 创建表和插入数据     |

1. 登录 [datadata.com](https://www.datadata.com)
2. 头像 → Settings → 左侧 "API Keys" → 创建新 Key
3. 勾选所需权限后创建
4. 配置到环境变量：

```bash
export DATADATA_API_KEY="ak_..."
```
