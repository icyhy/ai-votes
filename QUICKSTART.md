# 互动大屏幕投票系统 - 快速启动指南

## 环境要求

- Python 3.10+
- pip

## 安装步骤

### 1. 创建虚拟环境(推荐)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 3. 初始化配置

首次运行会自动创建数据库和配置文件。

### 4. 启动服务

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

或者使用快捷命令:

```powershell
python backend/main.py
```

### 5. 访问系统

- **大屏页面**: http://localhost:8000/
- **管理员页面**: http://localhost:8000/admin
- **签到页面**: http://localhost:8000/signin

## Docker 部署

### 构建镜像

```powershell
docker-compose build
```

### 启动服务

```powershell
docker-compose up -d
```

### 停止服务

```powershell
docker-compose down
```

## 默认密码

- **管理员密码**: admin123
- **主持人密码**: host123

> 首次登录后请在管理员页面修改密码!

## 目录说明

- `backend/` - 后端代码
- `frontend/` - 前端代码
- `data/` - 数据库和导出文件
- `config/` - 配置文件

## 注意事项

1. 首次使用需要在管理员页面创建活动和配置投票
2. 如需外网访问,请在管理员页面配置公网 IP 地址
3. 数据库文件位于 `data/database.db`
4. CSV 导出文件位于 `data/exports/`

## 故障排除

### 端口被占用

修改 `.env` 文件中的 `PORT` 配置,或在启动命令中指定其他端口:

```powershell
uvicorn backend.main:app --port 8080
```

### 数据库错误

删除 `data/database.db` 文件,重新启动服务会自动创建新数据库。

## 技术支持

如遇问题,请查看日志输出或联系技术支持。
