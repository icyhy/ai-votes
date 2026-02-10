"""
签到 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas import SignInRequest, SignInResponse
from backend.services import ActivityService, ParticipantService
from backend.config import settings
from backend.utils import verify_password, get_server_url, generate_qrcode
from backend.routers.websocket import manager

router = APIRouter(prefix="/api/signin", tags=["signin"])

@router.get("/info")
async def get_signin_info(request: Request, db: Session = Depends(get_db)):
    """获取签到页面信息"""
    # 获取当前活动
    activity = ActivityService.get_current_activity(db)
    if not activity:
        return {
            "qrcode_url": "",
            "activity_status": "no_activity",
            "message": "暂无活动"
        }
    
    # 生成二维码 URL
    server_url = get_server_url(settings.manual_ip, settings.port)
    signin_url = f"{server_url}/signin"
    qrcode_data = generate_qrcode(signin_url, size=400)
    
    # 获取签到人数
    participant_count = ParticipantService.get_participants_count(db, activity.id)
    
    return {
        "qrcode_url": qrcode_data,
        "signin_url": signin_url,
        "activity_status": activity.status,
        "activity_name": activity.name,
        "participant_count": participant_count
    }

@router.post("/submit", response_model=SignInResponse)
async def submit_signin(
    signin: SignInRequest,
    db: Session = Depends(get_db)
):
    """提交签到"""
    # 获取当前活动
    activity = ActivityService.get_current_activity(db)
    if not activity:
        raise HTTPException(status_code=400, detail="暂无活动")
    
    # 如果是主持人,验证密码
    if signin.role == 'host':
        if not signin.password or not verify_password(signin.password, settings.host_password):
            raise HTTPException(status_code=401, detail="主持人密码错误")
        
        # 检查是否已有主持人
        existing_host = ParticipantService.get_host(db, activity.id)
        if existing_host:
            # 返回已有主持人的 session_id
            return SignInResponse(
                session_id=existing_host.session_id,
                redirect="/host"
            )
    
    # 创建参会人
    participant = ParticipantService.create_participant(
        db, activity.id, signin.name, signin.department, signin.role
    )
    
    # 广播签到人数更新
    participant_count = ParticipantService.get_participants_count(db, activity.id)
    await manager.broadcast({
        "type": "participant_signed_in",
        "data": {"count": participant_count}
    })
    
    # 返回 session_id 和重定向路径
    redirect = "/host" if signin.role == 'host' else "/participant"
    return SignInResponse(
        session_id=participant.session_id,
        redirect=redirect
    )
