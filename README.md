# Datadata Skills

Claude Code skills for the [Datadata](https://www.datadata.com) analytics platform.

## Skills

### datadata-api

通过自然语言与 Datadata 平台交互。安装后在 Claude Code 中可直接用对话方式完成以下操作：

- **探查数据源** — 查看数据源元数据、列出 schema 中的表、描述表结构
- **执行查询** — 对 DuckDB 或 ClickHouse 数据源运行 SQL，支持跨源 join
- **下载结果** — 获取执行结果，支持 NDJSON 和 CSV 格式
- **结果检索** — 在本地用 `rg` 等工具搜索已保存的结果文件
- **管理 Data Spaces** — 在数据空间中创建表、插入数据，使用标准 SQL 查询

```bash
npx skills add https://github.com/datadata-team/datadata-skills/datadata-api

# 如果您使用 pnpm 和 Claude Code 可以通过下面的命令安装
pnpx skills add https://github.com/datadata-team/datadata-skills/datadata-api --agent claude-code
```

详细用法和命令参考见 [datadata-api/SKILL.md](./datadata-api/SKILL.md)。

更多细节（含 Data Spaces 建表与数据插入）见 [datadata-api/SKILL.md](./datadata-api/SKILL.md) 和 [API 参考](./datadata-api/references/api.md)。

### 获取 API Key

在 Datadata 平台中创建 API Key，根据用途勾选所需权限：

| 权限                    | 用途                 |
| ----------------------- | -------------------- |
| `queries:execute-adhoc` | 执行 SQL 查询        |
| `executions:get`        | 获取执行结果         |
| `datasources:read`      | 读取数据源元数据     |
| `datasource:scan`       | 触发异步 schema 扫描 |
| `data-spaces:write`     | 创建表和插入数据     |

1. 登录 [datadata.com](https://www.datadata.com)
2. 头像 → Settings → 左侧 "API Keys" → 创建新 Key
3. 勾选所需权限后创建
4. 配置到环境变量：

```bash
export DATADATA_API_KEY="ak_..."
```
