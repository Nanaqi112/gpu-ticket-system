# GPU维修工单系统

GPU维修工单管理系统，用于追踪和管理GPU配件的维修流程。

## 功能特性

### 用户认证
- 登录/登出功能
- 未登录自动跳转登录页
- 权限控制：管理员完全权限，普通用户只读

### 主页仪表盘
- 工单总数、进行中、已完成统计卡片
- 最近工单快速预览

### 工单管理
- 创建工单：填写型号、序列号、来源地、故障描述、时间
- 编辑工单：修改所有字段信息
- 状态流转：进行中 → 已完成
- 搜索筛选：按关键词搜索、按状态筛选
- 附件管理：上传/删除图片和文档

### 详情展示
- 完整配件信息（型号、序列号、来源地）
- 故障描述
- 图片预览（支持放大查看）
- 文件下载
- 已过天数提醒（<21天黄色，≥21天红色）

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Pinia + Axios |
| 后端 | Django + Django REST Framework |
| 数据库 | PostgreSQL |
| 缓存 | Redis (可选) |
| 部署 | Docker + Docker Compose |

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/gpu-ticket-system.git
cd gpu-ticket-system
```

### 2. 配置环境变量

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，修改以下配置：

```env
SECRET_KEY=你的密钥
DB_PASSWORD=数据库密码
```

### 3. 一键启动

```bash
./gpu-tickets.sh start
```

启动脚本会自动：
- 构建Docker镜像
- 启动所有服务
- 初始化数据库
- 创建管理员账号

### 4. 访问系统

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost |
| 后端API | http://localhost:8000/api/ |
| 管理后台 | http://localhost:8000/admin/ |

**默认账号：**

| 用户名 | 密码 | 权限 |
|--------|------|------|
| `admin` | `admin2026` | 管理员（完全权限） |
| `test` | `test` | 普通用户（只读） |

## 管理脚本

```bash
./gpu-tickets.sh start     # 启动服务
./gpu-tickets.sh stop      # 停止服务
./gpu-tickets.sh restart   # 重启服务
./gpu-tickets.sh status    # 查看状态
./gpu-tickets.sh logs      # 查看日志
./gpu-tickets.sh help      # 查看帮助
```

## API接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/login/` | 用户登录 |
| POST | `/api/auth/logout/` | 用户登出 |
| GET | `/api/auth/user/` | 获取当前用户信息 |

### 工单接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tickets/` | 获取工单列表 |
| POST | `/api/tickets/` | 创建工单 |
| GET | `/api/tickets/{id}/` | 获取工单详情 |
| PATCH | `/api/tickets/{id}/` | 更新工单 |
| DELETE | `/api/tickets/{id}/` | 删除工单 |
| GET | `/api/tickets/stats/` | 获取统计数据 |

**查询参数：**
- `page` - 页码
- `page_size` - 每页数量
- `status` - 状态筛选 (`in_progress`, `completed`)
- `search` - 搜索关键词

## 项目结构

```
gpu-ticket-system/
├── backend/                    # Django后端
│   ├── config/                 # 项目配置
│   ├── tickets/                # 工单应用
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example            # 环境变量模板
│   └── Dockerfile
├── frontend/                   # Vue 3前端
│   ├── src/
│   │   ├── api/                # API服务
│   │   ├── router/             # 路由配置
│   │   ├── stores/             # 状态管理 (含user.js)
│   │   └── views/              # 页面组件 (含Login.vue)
│   ├── package.json
│   ├── nginx.conf
│   └── Dockerfile
├── docker-compose.yml          # Docker编排
├── gpu-tickets.sh              # 管理脚本
└── README.md
```

## 数据模型

### 工单 (Ticket)

| 字段 | 类型 | 说明 |
|------|------|------|
| model_type | CharField | 型号 (H100/H200/B200/H100底板/H200底板/B200底板/A100/A800/L40S/OTHER) |
| serial_number | CharField | 序列号（唯一） |
| source | CharField | 来源地 |
| fault_description | TextField | 故障描述 |
| status | CharField | 状态 (in_progress/completed) |
| created_at | DateTimeField | 创建时间 |
| updated_at | DateTimeField | 更新时间 |

### 附件 (Attachment)

| 字段 | 类型 | 说明 |
|------|------|------|
| ticket | ForeignKey | 所属工单 |
| file | FileField | 文件 |
| file_name | CharField | 文件名 |
| file_type | CharField | 类型 (image/document/log/other) |
| file_size | IntegerField | 文件大小 |
| uploaded_at | DateTimeField | 上传时间 |

## 本地开发

### 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 生产部署

1. 修改 `backend/.env`：
   - 设置强密码的 `SECRET_KEY`
   - 设置 `DEBUG=False`
   - 配置 `ALLOWED_HOSTS`
   - 配置数据库连接

2. 配置HTTPS（推荐Nginx + Let's Encrypt）

3. 定期备份数据库

## 许可证

MIT License