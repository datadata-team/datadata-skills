# API Key 申请

连接 Datadata MCP Server **首选 OAuth 自动授权**，无需手动申请 Key。
但部分 Agent 不支持 OAuth，此时可切换到 API Key 授权。

本章节介绍如何通过 Device Flow 自动申请 API Key。

## 自动申请流程

**Step 1 — 发起授权请求**

使用 curl 请求 `device-flow/code` 接口，必须包含 `name`、`description` 和 `permissions`：

```shell
curl -X POST "https://www.datadata.com/api/v1/api-keys/device-flow/code" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "{Agent Name}",
    "description": "{Agent Description}",
    "permissions": [
      "datasources:read",
      "datasources:scan",
      "datasources:replace-file",
      "data-spaces:write",
      "executions:get",
      "queries:execute",
      "queries:execute-adhoc"
    ]
  }'
```

响应中包含 `deviceCode`、`userCode`、`verificationUriComplete` 等字段。

**Step 2 — 引导用户授权**

将 `verificationUriComplete` 和 `userCode` 原样展示给用户，提示用户在浏览器中打开链接完成授权：

```txt
请点击或复制以下链接在浏览器中完成授权，您的授权码是：**{userCode}**

{verificationUriComplete}
```

**Step 3 — 轮询换取 API Key**

用户确认授权后，用 `deviceCode` 换取 API Key：

```shell
curl -X POST "https://www.datadata.com/api/v1/api-keys/device-flow/token" \
  -H "Content-Type: application/json" \
  -d '{
    "deviceCode": "{deviceCode}"
  }'
```

成功响应示例：

```json
{
  "key": "ak_xxx...xxx",
  "name": "{Agent Name}",
  "permissions": ["..."]
}
```

其中 `key` 字段即为 API Key。

## 错误处理

| HTTP 状态码 | code                    | 处理方式                                        |
| ----------- | ----------------------- | ----------------------------------------------- |
| `400`       | `authorization_pending` | 用户尚未确认，继续轮询                          |
| `400`       | `invalid_device_code`   | deviceCode 已过期或不存在，反馈用户重新发起申请 |

## 权限说明

Agent 申请的默认权限集如下，可根据实际需要调整：

| 权限                       | 用途                   |
| -------------------------- | ---------------------- |
| `datasources:read`         | 读取数据源信息和元数据 |
| `datasources:scan`         | 触发 Schema 扫描       |
| `datasources:replace-file` | 替换数据源文件         |
| `data-spaces:write`        | Data Spaces 建表/写入  |
| `executions:get`           | 获取执行结果           |
| `queries:execute`          | 执行已保存的查询       |
| `queries:execute-adhoc`    | 执行临时查询           |
