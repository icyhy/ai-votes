"""
FastAPI 主程序入口
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from backend.database import init_db
from backend.routers import admin, signin, host, participant
from backend.routers.websocket import manager
import uvicorn

# 创建 FastAPI 应用
app = FastAPI(title="互动大屏幕投票系统", version="1.0.0")

# 挂载静态文件
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="frontend/templates")

# 注册路由
app.include_router(admin.router)
app.include_router(signin.router)
app.include_router(host.router)
app.include_router(participant.router)

# WebSocket 路由
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, client_type: str = "display"):
    """WebSocket 连接端点"""
    await manager.connect(websocket, client_type)
    try:
        while True:
            # 接收消息(保持连接)
            data = await websocket.receive_text()
            # 可以在这里处理客户端发送的消息
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 页面路由
@app.get("/", response_class=HTMLResponse)
async def display_page(request: Request):
    """大屏页面"""
    return templates.TemplateResponse("display.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    """管理员页面"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/signin", response_class=HTMLResponse)
async def signin_page(request: Request):
    """签到页面"""
    return templates.TemplateResponse("signin.html", {"request": request})

@app.get("/host", response_class=HTMLResponse)
async def host_page(request: Request):
    """主持人页面"""
    return templates.TemplateResponse("host.html", {"request": request})

@app.get("/participant", response_class=HTMLResponse)
async def participant_page(request: Request):
    """参会人页面"""
    return templates.TemplateResponse("participant.html", {"request": request})

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    print("数据库初始化完成")
    print("服务器启动成功")

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理工作"""
    print("服务器关闭")

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
