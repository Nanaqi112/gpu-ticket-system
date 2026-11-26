# GPU 维修工单系统 API 文档

> 基地址：`http://localhost/api/`
> 适用版本：当前 `main` 分支（提交 `3f60c59` 及之后）
> 最后更新：2026-11-26

本文档描述系统对外提供的全部 HTTP 接口，包含认证方式、请求参数、响应结构、权限矩阵和常见错误。文中示例统一使用 `localhost`，示例数据均为虚构；局域网访问时请把 `localhost` 替换为服务器 IP 或主机名。

---

## 1. 基础信息

| 项目 | 说明 |
|---|---|
| 基地址 | `http://localhost/api/` |
| 协议 | HTTP（内网部署，未启用 HTTPS） |
| 数据格式 | JSON（UTF-8）；创建/更新工单使用 `multipart/form-data` |
| 日期格式 | `YYYY-MM-DD`，例如 `2026-11-26` |
| 时间戳格式 | ISO 8601 带时区，例如 `2026-11-26T17:23:18.098055+08:00` |
| 认证 | Session Cookie（除登录外全部接口需要） |
| 结尾斜杠 | **必须保留**，`/api/tickets` 会触发 Django 重定向，POST 时可能失败 |
| 管理后台 | `/admin/`（需要 `is_staff`），不属于 `/api/` |
| 健康检查 | `/healthz`（nginx 返回 200，无需认证） |

---

## 2. 认证与权限

### 2.1 登录

`POST /api/auth/login/`

支持 `application/json` 或表单 `application/x-www-form-urlencoded`，两种都可用（表单方式在 Windows `cmd` 里更好写）。

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `username` | string | 是 | 用户名 |
| `password` | string | 是 | 密码 |

成功响应 `200` 并下发 `sessionid` Cookie：

```json
{"id": 1, "username": "admin", "is_staff": true}
```

失败响应 `401`：

```json
{"error": "用户名或密码错误"}
```

**Linux / macOS：**

```bash
curl -c ck.txt -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"YOUR_PASSWORD"}' \
     http://localhost/api/auth/login/

# 之后所有请求带上 -b ck.txt
curl -b ck.txt "http://localhost/api/tickets/?status=in_progress"
```

**Windows cmd：**

```bat
curl -c ck.txt -d "username=admin&password=YOUR_PASSWORD" http://localhost/api/auth/login/
curl -b ck.txt "http://localhost/api/tickets/?status=in_progress"
```

> cmd 中要用双引号（不认单引号分组）；`-c` 写 Cookie、`-b` 读 Cookie，不要混用。

**PowerShell（推荐，免手工管理 Cookie 文件）：**

```powershell
$s = New-Object Microsoft.PowerShell.Commands.WebRequestSession

Invoke-RestMethod -Method Post -Uri 'http://localhost/api/auth/login/' `
  -WebSession $s -Body @{ username = 'admin'; password = 'YOUR_PASSWORD' }

Invoke-RestMethod -Uri 'http://localhost/api/tickets/?status=in_progress' -WebSession $s
```

> PowerShell 中 `curl` 是 `Invoke-WebRequest` 的别名，参数与 curl 不同；需要使用 curl 语法时请写 `curl.exe`。

### 2.2 登出

`POST /api/auth/logout/` → `200 {"message":"已登出"}`

### 2.3 当前用户

`GET /api/auth/user/` → `200 {"id":1,"username":"admin","is_staff":true}`

### 2.4 认证机制说明

- 仅支持 Session Cookie，**不支持** Token / JWT / Basic Auth。
- API 层豁免 CSRF（`CsrfExemptSessionAuthentication`），调用时无需 `csrftoken`。
- 未登录访问返回 **403**（不是 401），响应体为 `{"detail":"身份认证信息未提供。"}`。
- Cookie 默认有效期约两周，过期后重新登录即可。
- Cookie 文件等同于登录凭证，不要提交到版本库或共享，建议 `chmod 600 ck.txt`。

### 2.5 权限矩阵

系统只有两种角色：`is_staff=true`（管理员）和普通用户。

| 操作 | 匿名 | 普通用户（如 `test`） | 管理员（如 `admin`） |
|---|---|---|---|
| 登录 | ✅ | ✅ | ✅ |
| 读取列表 / 详情 / 统计 / 导出 | ❌ 403 | ✅ 200 | ✅ 200 |
| 创建 / 更新 / 删除工单 | ❌ 403 | ❌ 403 | ✅ 2xx |
| 删除附件 | ❌ 403 | ❌ 403 | ✅ 204 |
| Django 管理后台 `/admin/` | ❌ | ❌ 登录被拒绝 | ✅ |

注意：普通用户虽然不能写，但**能看到并导出全部工单**（含完整故障描述），当前没有按用户的数据隔离。

---

## 3. 通用约定

### 3.1 分页

列表接口统一返回 DRF 分页结构：

```json
{
  "count": 42,
  "next": "http://localhost/api/tickets/?page=2",
  "previous": null,
  "results": []
}
```

- 每页固定 20 条，用 `?page=N` 翻页，`next` / `previous` 为可直接请求的绝对 URL。
- **`page_size` 参数当前不生效**（未配置 `page_size_query_param`），列表页的“每页条数”选择器实际不起作用。
- 数据超过 20 条时，脚本需循环跟随 `next` 直到为 `null`。

### 3.2 列表筛选参数

`GET /api/tickets/` 支持以下查询参数，可组合使用（AND 关系）：

| 参数 | 说明 |
|---|---|
| `page` | 页码，从 1 开始 |
| `status` | 状态精确匹配：`in_progress` 或 `completed`（传中文“进行中”无效） |
| `search` | 模糊搜索，匹配序列号、来源地、故障描述（不区分大小写） |

当前不支持按型号、日期区间筛选，也不能指定排序（固定 `-created_at`）。

### 3.3 状态码与错误格式

| 状态码 | 含义 |
|---|---|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无响应体） |
| 400 | 参数校验失败 |
| 401 | 登录失败（用户名或密码错误） |
| 403 | 未登录，或权限不足（非管理员执行写操作） |
| 404 | 资源不存在 |
| 405 | 方法不允许（如管理员对 `/stats/` 发 POST） |

> 权限检查先于方法检查：普通用户对只读接口发 POST 会得到 403 而非 405；管理员才会触发 405。

校验失败（400）为字段级字典：

```json
{"serial_number": ["具有 序列号 的 工单 已存在。"]}
{"status": ["“done” 不是合法选项。"]}
```

未登录 / 权限不足（403）：

```json
{"detail": "身份认证信息未提供。"}
{"detail": "您没有执行该操作的权限。"}
```

### 3.4 格式后缀

支持 DRF 的格式后缀：`/api/tickets.json` 或 `/api/tickets/?format=json`。浏览器直接访问会返回可浏览的 HTML 页面（Browsable API），脚本调用默认返回 JSON。

---

## 4. 数据结构

### 4.1 工单列表项（List）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | int | 工单 ID |
| `model_type` | string | 型号代码，见 4.4 |
| `model_display` | string | 型号显示名，如 `H100底板` |
| `serial_number` | string | 序列号，全局唯一，≤100 字符 |
| `source` | string | 来源地，≤200 字符 |
| `status` | string | `in_progress` / `completed` |
| `status_display` | string | `进行中` / `已完成` |
| `created_at` | date | 创建日期 |
| `updated_at` | date | 更新日期 |
| `days_elapsed` | int | 今天与 `updated_at` 相差天数（`updated_at` 在未来时为负） |
| `attachment_count` | int | 附件数量 |

### 4.2 工单详情（Detail）

在列表字段（不含 `attachment_count`）基础上增加：

| 字段 | 类型 | 说明 |
|---|---|---|
| `fault_description` | string | 故障描述，多行文本 |
| `attachments` | array | 附件列表，结构见 4.3；无附件时为空数组 |

### 4.3 附件对象

```json
{
  "id": 1,
  "file": "http://localhost/media/tickets/2026/11/example.txt",
  "file_name": "example.txt",
  "file_type": "document",
  "file_size": 14,
  "uploaded_at": "2026-11-26T17:23:18.098055+08:00",
  "url": "/media/tickets/2026/11/example.txt"
}
```

| 字段 | 说明 |
|---|---|
| `file` | 带主机名的绝对 URL（由请求的 Host 生成） |
| `url` | 相对路径，前端拼接或直接使用 |
| `file_type` | 自动推断：图片 → `image`，pdf/txt/csv → `document`，`.log`/`.txt` → `log`，其他 → `other` |
| `file_size` | 字节数 |

上传限制：单个文件 ≤ **10MB**；未限制 MIME 类型。

### 4.4 枚举值

**型号 `model_type`**

| 代码 | 显示名 |
|---|---|
| `H100` / `H200` / `B200` | H100 / H200 / B200 |
| `H100_BD` / `H200_BD` / `B200_BD` | H100底板 / H200底板 / B200底板 |
| `A100` / `A800` / `L40S` | A100 / A800 / L40S |
| `OTHER` | 其他 |

**状态 `status`**：`in_progress`（进行中）、`completed`（已完成）。新建工单固定为 `in_progress`，需通过 PATCH 修改。

---

## 5. 业务接口

### 5.1 工单列表

`GET /api/tickets/`

- 权限：已登录用户
- 查询参数：见 3.2
- 响应：分页结构，`results` 为 4.1 的列表项

```bash
curl -b ck.txt "http://localhost/api/tickets/?status=in_progress&page=1"
```

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 15,
      "model_type": "H100",
      "model_display": "H100",
      "serial_number": "SN202601001",
      "source": "示例来源地",
      "status": "in_progress",
      "status_display": "进行中",
      "created_at": "2026-11-09",
      "updated_at": "2026-11-09",
      "days_elapsed": 17,
      "attachment_count": 0
    }
  ]
}
```

> 列表**不返回** `fault_description`，需要故障描述请请求详情接口或导出 Excel。

### 5.2 创建工单

`POST /api/tickets/`

- 权限：管理员
- 请求：`multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `model_type` | string | 是 | 型号代码，见 4.4 |
| `serial_number` | string | 是 | 序列号，不可重复 |
| `source` | string | 是 | 来源地 |
| `fault_description` | string | 是 | 故障描述 |
| `created_at` | date | 是 | 创建日期 `YYYY-MM-DD` |
| `updated_at` | date | 是 | 更新日期 `YYYY-MM-DD` |
| `attachments` | file | 否 | 可重复多个，单文件 ≤10MB |

```bash
curl -b ck.txt \
  -F 'model_type=H100' \
  -F 'serial_number=SN202601001' \
  -F 'source=示例来源地' \
  -F 'fault_description=示例故障描述' \
  -F 'created_at=2026-11-26' \
  -F 'updated_at=2026-11-26' \
  -F 'attachments=@/path/to/file.txt' \
  http://localhost/api/tickets/
```

成功响应 `201`：

```json
{
  "model_type": "H100",
  "serial_number": "SN202601001",
  "source": "示例来源地",
  "fault_description": "示例故障描述",
  "created_at": "2026-11-26",
  "updated_at": "2026-11-26"
}
```

> 注意：创建响应**不含 `id` 和 `status`**（序列化器字段限制）。需要 ID 时请再调用列表接口按 `search=SERIAL_NUMBER` 查询，或改用详情/导出流程。

重复序列号返回 `400`：

```json
{"serial_number": ["具有 序列号 的 工单 已存在。"]}
```

### 5.3 工单详情

`GET /api/tickets/{id}/`

- 权限：已登录用户
- 响应：4.2 详情结构，含 `fault_description` 与 `attachments`
- 不存在返回 `404`

```bash
curl -b ck.txt "http://localhost/api/tickets/15/"
```

```json
{
  "id": 15,
  "model_type": "H100",
  "model_display": "H100",
  "serial_number": "SN202601001",
  "source": "示例来源地",
  "fault_description": "示例故障描述\n第二行内容",
  "status": "in_progress",
  "status_display": "进行中",
  "created_at": "2026-11-09",
  "updated_at": "2026-11-09",
  "days_elapsed": 17,
  "attachments": []
}
```

### 5.4 全量更新

`PUT /api/tickets/{id}/`

- 权限：管理员
- 语义为**全量替换**：`model_type`、`serial_number`、`source`、`fault_description`、`updated_at` 均为必填，缺项返回 400
- 一般建议改用 5.5 的 PATCH

```json
{
  "model_type": ["该字段是必填项。"],
  "serial_number": ["该字段是必填项。"]
}
```

### 5.5 部分更新

`PATCH /api/tickets/{id}/`

- 权限：管理员
- 请求体：`application/json` 或 `multipart/form-data`

| 字段 | 说明 |
|---|---|
| `model_type` / `serial_number` / `source` / `fault_description` | 按需修改 |
| `status` | `in_progress` / `completed` |
| `updated_at` | 更新日期 |
| `attachments` | 追加附件（不会删除已有附件） |

```bash
curl -b ck.txt -X PATCH \
  -H "Content-Type: application/json" \
  -d '{"status":"completed","updated_at":"2026-11-26"}' \
  http://localhost/api/tickets/15/
```

成功响应 `200`：

```json
{
  "model_type": "H100",
  "serial_number": "SN202601001",
  "source": "示例来源地",
  "fault_description": "示例故障描述",
  "status": "completed",
  "updated_at": "2026-11-26"
}
```

非法状态 `400`：

```json
{"status": ["“done” 不是合法选项。"]}
```

### 5.6 删除工单

`DELETE /api/tickets/{id}/`

- 权限：管理员
- 成功 `204`，无响应体；关联附件记录与文件一并删除

```bash
curl -b ck.txt -X DELETE http://localhost/api/tickets/15/
```

### 5.7 删除附件

`DELETE /api/tickets/{id}/delete_attachment/`

- 权限：管理员
- 请求体：`{"attachment_id": 1}`
- 成功 `204`；附件不存在返回 `404 {"error":"附件不存在"}`

```bash
curl -b ck.txt -X DELETE \
  -H "Content-Type: application/json" \
  -d '{"attachment_id":1}' \
  http://localhost/api/tickets/15/delete_attachment/
```

### 5.8 统计

`GET /api/tickets/stats/`

- 权限：已登录用户
- 响应：全库统计，无筛选参数

```json
{"total": 10, "completed": 9, "in_progress": 1}
```

### 5.9 导出 Excel

`GET /api/tickets/export/`

- 权限：已登录用户
- 响应头：

```text
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="tickets_20261126_170341.xlsx"
```

- 列：序列号、型号、来源地、故障描述、状态、创建时间、更新时间、已过天数、附件数
- **始终导出全部工单**，`status` / `search` 参数无效
- 同步生成，数据量很大时可能超过前端 axios 的 30s 超时

```bash
curl -b ck.txt -o tickets.xlsx http://localhost/api/tickets/export/
```

### 5.10 API 根

`GET /api/` → `200 {"tickets":"http://localhost/api/tickets/"}`
（仅列出 router 注册的资源，认证接口不在其中。）

---

## 6. 常见场景

### 6.1 拉取进行中工单（含故障描述）

列表不含描述，需列表 + 逐条详情：

```powershell
$s = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-RestMethod -Method Post -Uri 'http://localhost/api/auth/login/' `
  -WebSession $s -Body @{ username = 'admin'; password = 'YOUR_PASSWORD' } | Out-Null

$list = Invoke-RestMethod -Uri 'http://localhost/api/tickets/?status=in_progress' -WebSession $s

$list.results | ForEach-Object {
  Invoke-RestMethod -Uri "http://localhost/api/tickets/$($_.id)/" -WebSession $s
} | Select-Object serial_number, model_display, source, status_display, fault_description |
  Format-List
```

### 6.2 定时导出全部工单

```bash
curl -c ck.txt -d "username=export&password=YOUR_PASSWORD" http://localhost/api/auth/login/
curl -b ck.txt -o "tickets_$(date +%F).xlsx" http://localhost/api/tickets/export/
```

建议为导出创建专用普通用户，避免使用管理员口令。

---

## 7. 非 API 端点

| 路径 | 说明 | 认证 |
|---|---|---|
| `/admin/` | Django 管理后台 | 需要 `is_staff` 登录 |
| `/static/` | Django 静态文件（admin 样式脚本） | 公开 |
| `/media/` | 用户上传的附件文件 | **公开**（nginx 直接读磁盘） |
| `/healthz` | 健康检查 | 公开 |

> `/media/` 目前不校验登录：知道 URL 即可下载附件。若附件内容敏感，需要改为 nginx `auth_request` 或 Django `X-Accel-Redirect` 下发。

---

## 8. 已知限制

1. `page_size` 参数无效，列表固定 20 条/页。
2. 仅支持 Session Cookie，无 Token / API Key，脚本必须携带登录后的 Cookie。
3. 创建接口响应不返回 `id` 与 `status`。
4. `PUT` 为全量更新，字段缺失即 400；建议统一用 `PATCH`。
5. 导出始终为全量，无法按筛选条件导出；且为同步生成。
6. 列表不支持按型号、日期区间筛选，也不支持自定义排序。
7. 无批量导入接口。
8. 媒体文件无鉴权（见第 7 节）。
9. 普通用户可读取、导出全部工单，无数据隔离。
10. 默认账号口令较弱（见 README），部署后应尽快修改。
