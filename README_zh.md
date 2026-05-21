# Datadata Skills

Agent skills for the [Datadata](https://www.datadata.com) 数据分析平台。

## 安装

```bash
npx skills add datadata-team/datadata-skills
```

> **提示：** 如果你使用 pnpm，请将 `npx` 替换为 `pnpx`，例如：
>
> ```bash
> pnpx skills add datadata-team/datadata-skills
> ```

## Skills

### datadata-api

通过自然语言与 Datadata 平台交互，围绕两大核心功能：

**查询数据** — 查看数据源元数据、列出表、描述列结构、执行 SQL 查询（DuckDB / ClickHouse，支持跨源 join）、下载 NDJSON/CSV 结果

**录入数据** — 在 Data Spaces（ducklake）中创建表、批量插入数据、删除表，录入后可通过标准查询读取

详细用法见 [skills/datadata-api/SKILL.md](./skills/datadata-api/SKILL.md)。

### datadata-dql

编写 DQL（Datadata Query Language）数据处理脚本 — 基于 Starlark 的扩展脚本语言，支持 DataFrame/Series 操作、SQL 查询、HTTP 请求、2D 绘图等，适用于数据转换、清洗、生成等自定义数据处理场景。

详细用法见 [skills/datadata-dql/SKILL.md](./skills/datadata-dql/SKILL.md)。

### 认证方式

本 skill 支持两种认证方式：

#### 自动授权（推荐）

未配置 API Key 时，首次执行命令 Agent 会自动引导你完成设备授权流程 — 在终端中打开链接登录即可。Key 会在本地缓存 90 天。

#### 手动创建（备用）

在 Datadata 平台中创建 API Key，根据用途勾选所需权限：

| 权限                    | 用途                 |
| ----------------------- | -------------------- |
| `queries:execute-adhoc` | 执行 SQL 查询        |
| `executions:get`        | 获取执行结果         |
| `datasources:read`      | 读取数据源元数据     |
| `datasources:scan`      | 触发异步 Schema 扫描 |
| `data-spaces:write`     | 创建表和插入数据     |

1. 登录 [datadata.com](https://www.datadata.com)
2. 头像 → Settings → 左侧 "API Keys" → 创建新 Key
3. 勾选所需权限后创建
4. 配置到环境变量：

```bash
export DATADATA_API_KEY="ak_..."
```
