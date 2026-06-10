---
name: datadata-memory
description: 通过 Datadata MCP Server 管理AI持久化记忆——添加、搜索、更新、删除记忆，支持语义搜索和多维度过滤。当用户想让AI记住某些信息、回忆之前的对话内容、管理持久化知识时使用此skill。触发：记住、记忆、回忆、别忘了、帮我记下、之前说过、搜索记忆、删除记忆。
---

## 功能概览

本 skill 通过 **Datadata MCP Server** 的记忆工具管理 AI 持久化记忆。记忆是跨会话保留的原子事实、偏好或知识点，Agent 可在后续对话中检索使用。

- **添加记忆** — 存储原子事实，支持标签、分类、元数据（异步索引）
- **搜索记忆** — 关键词或语义搜索，支持按时间、分类、Agent、会话等多维度过滤
- **更新记忆** — 修正或补充已有记忆内容
- **合并压缩** — 检测相似记忆并合并为一条，消除冗余
- **冲突合并** — 发现信息冲突时保留最新、记录历史
- **删除记忆** — 按 ID 移除过时或错误的记忆

### 与其他 skill 的分工

| 场景                         | 使用 skill                    |
| ---------------------------- | ----------------------------- |
| 查询数据源、执行 SQL         | `datadata-mcp`                |
| 生成 Python 脚本（爬虫/ETL） | `datadata-api`                |
| DQL 数据处理脚本             | `datadata-dql`                |
| AI 持久化记忆管理            | `datadata-memory`（本 skill） |

## MCP 工具速查

| 工具               | 用途                 | 关键参数                                                                                        |
| ------------------ | -------------------- | ----------------------------------------------------------------------------------------------- |
| `memory_add`       | 添加新记忆（异步）   | `content`（必填）, `category`, `tags`, `agentId`, `metadata`                                    |
| `memory_search`    | 搜索记忆             | `search`（必填）, `limit`, `offset`, `agentId`, `category`, `sessionId`, `startTime`, `endTime` |
| `memory_update`    | 更新已有记忆（异步） | `id`（必填）, `content`（必填）, `tags`, `category`, `agentId`, `metadata`                      |
| `memory_delete`    | 删除记忆             | `id`（必填）                                                                                    |
| `memory_task_wait` | 等待异步任务完成     | `taskId`（必填）, `timeout`（秒，默认 60）                                                      |

> **注意**：所有工具名前缀为 `mcp_datadata_`，如 `mcp_datadata_memory_add`。文档中省略前缀以保持简洁。

## 概念

### 记忆范围（Scope）

| 范围       | 说明                                | 使用场景                     |
| ---------- | ----------------------------------- | ---------------------------- |
| 用户全局   | 不指定 `agentId`，跨所有 Agent 可见 | 用户偏好、通用知识、项目约定 |
| Agent 专属 | 指定 `agentId`，仅特定 Agent 可检索 | Agent 专属上下文、任务状态   |

### 记忆属性

| 属性       | 说明                         | 示例                               |
| ---------- | ---------------------------- | ---------------------------------- |
| `content`  | 原子事实或偏好，一句话说清楚 | "用户偏好使用中文提交信息"         |
| `category` | 自定义分类，用于组织和过滤   | `"preferences"`, `"project-notes"` |
| `tags`     | 可搜索标签数组               | `["git", "convention"]`            |
| `metadata` | 键值对附加信息               | `{"project": "datadata-skills"}`   |

### 异步索引

`memory_add` 和 `memory_update` 是**异步操作**。调用后返回 `taskId`，记忆进入索引队列。在索引完成前，新添加的记忆**不会出现在搜索结果中**。

**正确流程**：`add` → `task_wait`（等待索引完成）→ `search`（验证可检索）

## 工作流

### 添加记忆

```
用户要求记住某事 → memory_add → memory_task_wait（等待索引）→ 确认完成
```

**示例**：

```
用户："记住我喜欢用中文写 commit message"
→ memory_add(content="用户偏好使用中文编写 Git 提交信息", category="preferences", tags=["git", "commit", "chinese"])
→ memory_task_wait(taskId=<返回的ID>)
→ 确认："已记住。"
```

**原则**：

- 每条记忆应为**单一原子事实**，不要塞多个不相关信息
- 添加前先 `memory_search` 检查是否已有类似记忆，避免重复
- 选择合适的 `category` 便于后续过滤

### 搜索记忆

```
用户询问过去信息 → memory_search → 返回相关记忆
```

**搜索策略**：

| 场景             | 方法                                               |
| ---------------- | -------------------------------------------------- |
| 关键词精确匹配   | `search="关键词"`                                  |
| 语义相关         | 使用自然语言描述，如 `search="用户的编码偏好"`     |
| 限定分类         | 加 `category="preferences"`                        |
| 限定时间范围     | 加 `startTime` / `endTime`（RFC3339 格式）         |
| 首次对话了解用户 | `memory_search(search="用户偏好和习惯", limit=10)` |

**优先级**：搜索记忆应在新对话开始时进行，以获取用户上下文。Agent 应在处理用户请求前检查相关记忆。

### 更新记忆

```
用户纠正或补充信息 → memory_update(id=<记忆ID>, content="修正后的内容") → memory_task_wait
```

**何时更新**：

- 用户明确纠正之前的说法："不对，我之前说的..."
- 信息已过时需要刷新
- 补充更多细节

**注意**：`memory_update` 同样异步，需要 `task_wait`。

### 合并压缩

当添加新记忆时，搜索发现存在**语义相似**的已有记忆，应将两者合并为一条，避免信息碎片化。

**触发条件**：`memory_add` 前的 `memory_search` 返回高度相关的结果（语义相似度 > 80%）

**流程**：

```
memory_search(新内容摘要) → 发现相似记忆
    ↓
合并内容（保留所有不重复信息）→ memory_update(已有记忆ID, 合并后内容)
    ↓
memory_task_wait → 确认合并完成
```

**合并原则**：

| 场景                   | 处理方式                           |
| ---------------------- | ---------------------------------- |
| 新信息是已有信息的子集 | 不操作，已有记忆已覆盖             |
| 新信息是已有信息的超集 | `memory_update` 替换为更完整的版本 |
| 新信息与已有信息互补   | 合并为一条，用分号或编号整合       |
| 新信息与已有信息重复   | 不操作，跳过添加                   |

**示例**：

```
已有："用户偏好使用中文编写 Git 提交信息"
新增："用户用 AngularJS 风格写 commit，类型有 feat/fix/docs 等"
→ 合并为："用户偏好使用中文编写 Git 提交信息，遵循 AngularJS 风格（feat/fix/docs/chore 等）"
```

### 冲突合并

当新信息与已有记忆**矛盾**（如用户先说电话是 1111，后又说电话是 2222），应以最新信息为准，同时保留变更历史。

**触发条件**：`memory_add` 前搜索发现语义相似但**内容矛盾**的记忆

**流程**：

```
memory_search → 发现冲突记忆
    ↓
将旧值写入 metadata.history，用新值更新 content
    ↓
memory_update(id, content="最新值", metadata={..., "history": [{"value": "旧值", "updatedAt": "..."}]})
    ↓
memory_task_wait → 确认
```

**metadata.history 格式**：

```json
{
  "history": [
    { "value": "电话: 1111", "updatedAt": "2026-06-01T10:00:00Z" },
    { "value": "电话: 2222", "updatedAt": "2026-06-10T14:00:00Z" }
  ]
}
```

> `history` 数组按时间倒序，最新在前。每次冲突合并时追加一条记录。

**判定冲突的标准**：

- 同一主题下的事实性信息不一致（电话号码、地址、版本号等）
- 用户明确说"不对，我之前说的..."或"改一下，应该是..."
- 偏好或习惯发生明确变化（"我现在不用 VS Code 了，改用 Fleet"）

**不是冲突的情况**（应合并压缩而非冲突合并）：

- 对同一主题的补充说明（不矛盾）
- 不同上下文的不同选择（"项目 A 用 pnpm，项目 B 用 yarn"）

### 删除记忆

```
用户要求忘记某事 / 记忆明显错误 → memory_delete(id=<记忆ID>)
```

删除是**同步操作**，无需等待索引。不可逆，执行前应确认。

## 规则

### 🟡 添加前先搜索，避免重复

调用 `memory_add` 前应先 `memory_search` 检查是否已有相似记忆。若存在相关记忆，优先 `memory_update` 更新而非重复添加。

### 🟡 添加/更新后必须等待索引

`memory_add` 和 `memory_update` 返回后，**必须**调用 `memory_task_wait` 等待索引完成，否则后续搜索可能遗漏。

### 🟡 记忆内容应原子化

每条记忆只包含一个独立事实。反面示例：

```
❌ "用户偏好中文 commit、喜欢用 VS Code、项目使用 TypeScript"
✅ "用户偏好使用中文编写 Git 提交信息"
✅ "用户使用 VS Code 作为主力编辑器"
✅ "项目 datadata-skills 使用 TypeScript"
```

### 🟡 搜索优先于猜测

当用户问"我之前说过..."或需要上下文时，**必须先搜索记忆**，不要凭当前对话猜测。

### 🟡 删除需确认

在 `memory_delete` 前，向用户展示要删除的记忆内容并请求确认。记忆删除不可逆。

## 常见问题

### Q: 添加记忆后搜索不到？

检查是否调用了 `memory_task_wait` 等待索引完成。异步索引可能需要几秒钟。

### Q: 搜索返回太多结果？

使用过滤参数缩小范围：`category`、`agentId`、`startTime`/`endTime`、或减小 `limit`。

### Q: 如何区分 tags 和 metadata？

- `tags`：用于搜索过滤的简短标签，会建立索引
- `metadata`：附加键值对，用于存储不参与搜索过滤的补充信息

### Q: 记忆和 session memory 有什么区别？

- **Datadata 记忆**（本 skill）：持久化存储，跨会话、跨 Agent 保留
- **Session memory**（`/memories/session/`）：仅当前会话有效，会话结束后清除

## References

| 文档                                                         | 说明                             |
| ------------------------------------------------------------ | -------------------------------- |
| [./references/memory-guide.md](./references/memory-guide.md) | 搜索策略、索引机制、最佳实践详解 |
